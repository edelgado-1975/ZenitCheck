"""
ZenitCheck — Vistas de Gestión y Flujo de Inspección en Alturas.
"""

from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Inspection, InspectionPhoto, DefectFinding, VerdictAuditLog
from .forms import InspectionCreateForm, VerdictConfirmationForm, PhotoUploadForm
from .image_utils import compress_image, validate_image_file
from equipment.models import Equipment
from ai_engine.service import process_inspection_photo, recalculate_inspection_verdict
from accounts.permissions import inspector_required


@login_required
def dashboard_view(request):
    """Panel principal con métricas, alertas de vencimiento y equipos recientes."""
    equipments = Equipment.objects.all()
    total = equipments.count()
    operational = equipments.filter(status=Equipment.Status.OPERATIONAL).count()
    observation = equipments.filter(status=Equipment.Status.OBSERVATION).count()
    out_of_service = equipments.filter(status=Equipment.Status.OUT_OF_SERVICE).count()

    # Alertas de vencimiento
    today = date.today()
    expiring_soon = equipments.filter(
        certification_expiry_date__gte=today,
        certification_expiry_date__lte=today + timedelta(days=30)
    ).count()
    expired = equipments.filter(certification_expiry_date__lt=today).count()

    recent_inspections = Inspection.objects.select_related('equipment', 'inspector').all()[:8]

    context = {
        'total_equipments': total,
        'operational': operational,
        'observation': observation,
        'out_of_service': out_of_service,
        'expiring_soon': expiring_soon,
        'expired': expired,
        'recent_inspections': recent_inspections,
        'recent_equipments': equipments[:6],
    }
    return render(request, 'inspections/dashboard.html', context)


@login_required
def inspection_list_view(request):
    """Listado completo de inspecciones con filtro por veredicto."""
    verdict_filter = request.GET.get('verdict')
    inspections = Inspection.objects.select_related('equipment', 'inspector').all()

    if verdict_filter in ['APPROVED', 'OBSERVATION', 'REJECTED']:
        inspections = inspections.filter(final_verdict=verdict_filter)

    return render(request, 'inspections/inspection_list.html', {
        'inspections': inspections,
        'current_filter': verdict_filter
    })


@inspector_required
def inspection_create_view(request):
    """
    Registro de nueva inspección en campo.
    Diseñado para móvil con una mano: captura con cámara trasera o subida de archivos.
    """
    if request.method == 'POST':
        form = InspectionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.inspector = request.user
            inspection.save()

            # Procesar fotos adjuntas
            files = request.FILES.getlist('photos')
            for uploaded_file in files:
                try:
                    validate_image_file(uploaded_file)
                    compressed = compress_image(uploaded_file)
                    InspectionPhoto.objects.create(
                        inspection=inspection,
                        image=compressed,
                        original_filename=uploaded_file.name,
                        photo_type=InspectionPhoto.PhotoType.OVERALL
                    )
                except Exception as e:
                    messages.warning(request, f"No se pudo cargar la imagen {uploaded_file.name}: {str(e)}")

            messages.success(request, f"Inspección para {inspection.equipment.serial_number} iniciada con éxito.")
            return redirect('inspections:detail', inspection_id=inspection.id)
    else:
        initial_eq = request.GET.get('equipment')
        form = InspectionCreateForm(initial={'equipment': initial_eq} if initial_eq else None)

    return render(request, 'inspections/inspection_form.html', {'form': form})


@login_required
def inspection_detail_view(request, inspection_id):
    """
    Ficha técnica de la inspección: fotos, análisis IA, hallazgos y emisión/confirmación de veredicto.
    """
    inspection = get_object_or_404(
        Inspection.objects.select_related('equipment', 'equipment__brand', 'equipment__equipment_type', 'inspector'),
        id=inspection_id
    )

    if request.method == 'POST':
        form = VerdictConfirmationForm(request.POST, instance=inspection)
        if form.is_valid():
            previous_verdict = inspection.final_verdict
            updated_inspection = form.save(commit=False)

            is_override = updated_inspection.final_verdict != inspection.suggested_verdict

            # Actualizar estado de equipo según veredicto
            if updated_inspection.final_verdict == Inspection.Verdict.APPROVED:
                inspection.equipment.status = Equipment.Status.OPERATIONAL
                inspection.equipment.last_inspection_date = inspection.inspection_date.date()
                inspection.equipment.certification_expiry_date = inspection.next_inspection_due
            elif updated_inspection.final_verdict == Inspection.Verdict.OBSERVATION:
                inspection.equipment.status = Equipment.Status.OBSERVATION
            else:
                inspection.equipment.status = Equipment.Status.OUT_OF_SERVICE

            inspection.equipment.save()
            updated_inspection.is_certified = True
            updated_inspection.status = Inspection.Status.CERTIFIED
            updated_inspection.save()

            # Registrar auditoría
            action = VerdictAuditLog.Action.OVERRIDDEN if is_override else VerdictAuditLog.Action.CONFIRMED
            justification = updated_inspection.verdict_override_justification if is_override else "Veredicto de IA confirmado por el inspector."
            VerdictAuditLog.objects.create(
                inspection=updated_inspection,
                user=request.user,
                action=action,
                previous_verdict=previous_verdict,
                new_verdict=updated_inspection.final_verdict,
                justification=justification,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, f"Veredicto {updated_inspection.get_final_verdict_display()} emitido y certificado generado.")
            return redirect('inspections:detail', inspection_id=inspection.id)
    else:
        form = VerdictConfirmationForm(instance=inspection)

    photos = inspection.photos.prefetch_related('findings').all()
    audits = inspection.verdict_audits.select_related('user').all()

    context = {
        'inspection': inspection,
        'photos': photos,
        'audits': audits,
        'form': form,
    }
    return render(request, 'inspections/inspection_detail.html', context)


@inspector_required
def trigger_ai_analysis_view(request, inspection_id):
    """Ejecuta el análisis de IA sobre todas las fotos de la inspección."""
    inspection = get_object_or_404(Inspection, id=inspection_id)
    photos = inspection.photos.filter(ai_status__in=[InspectionPhoto.AIStatus.PENDING, InspectionPhoto.AIStatus.FAILED])

    count = 0
    for p in photos:
        process_inspection_photo(p.id)
        count += 1

    recalculate_inspection_verdict(inspection)
    messages.success(request, f"Se analizaron {count} fotografías con el motor de visión artificial.")
    return redirect('inspections:detail', inspection_id=inspection.id)


@login_required
def equipment_history_view(request, serial_number):
    """Línea de tiempo histórica de todas las inspecciones y veredictos de un equipo."""
    equipment = get_object_or_404(
        Equipment.objects.select_related('brand', 'equipment_type'),
        serial_number=serial_number
    )
    inspections = equipment.inspections.select_related('inspector').prefetch_related('photos').order_by('-inspection_date')

    return render(request, 'inspections/equipment_history.html', {
        'equipment': equipment,
        'inspections': inspections
    })


@login_required
def alerts_view(request):
    """Módulo de alertas técnicas y equipos que requieren atención inmediata."""
    today = date.today()
    expired_equipments = Equipment.objects.filter(certification_expiry_date__lt=today).select_related('brand', 'equipment_type')
    expiring_soon_equipments = Equipment.objects.filter(
        certification_expiry_date__gte=today,
        certification_expiry_date__lte=today + timedelta(days=30)
    ).select_related('brand', 'equipment_type')

    return render(request, 'inspections/alerts.html', {
        'expired_equipments': expired_equipments,
        'expiring_soon_equipments': expiring_soon_equipments,
        'today': today
    })

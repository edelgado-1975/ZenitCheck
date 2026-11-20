"""
ZenitCheck — Vistas de Generación y Descarga de Certificados PDF.
"""

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from inspections.models import Inspection
from .generator import generate_inspection_certificate_pdf


@login_required
def download_certificate_pdf(request, inspection_id):
    """Genera y descarga el certificado PDF firmado digitalmente."""
    inspection = get_object_or_404(
        Inspection.objects.select_related('equipment', 'equipment__brand', 'equipment__equipment_type', 'inspector'),
        id=inspection_id
    )

    pdf_bytes, signature_info = generate_inspection_certificate_pdf(inspection)

    filename = f"Certificado_{inspection.equipment.serial_number}_{inspection.inspection_date.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    response['X-Certificate-Signature'] = signature_info['signature_hex'][:64]
    response['X-Certificate-SHA256'] = signature_info['sha256_hash']

    return response


@login_required
def certificate_view(request, inspection_id):
    """Vista previa y detalles de verificación criptográfica del certificado."""
    inspection = get_object_or_404(Inspection, id=inspection_id)
    return render(request, 'reports/certificate_detail.html', {'inspection': inspection})

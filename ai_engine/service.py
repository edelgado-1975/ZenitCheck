"""
ZenitCheck — Servicio Integrador de Análisis de Fotos con IA.
Ejecuta el detector, guarda los hallazgos en la BD, genera la superposición gráfica
y recalcula el veredicto sugerido para la inspección.
"""

import os
from django.conf import settings
from django.core.files import File
from .detector import get_defect_detector
from .overlay import draw_defect_overlays
from inspections.models import InspectionPhoto, DefectFinding, Inspection, VerdictAuditLog
from inspections.verdict import calculate_inspection_verdict


def process_inspection_photo(photo_id, detector=None):
    """
    Procesa una fotografía de inspección:
    1. Ejecuta el detector de anomalías por visión artificial.
    2. Registra los DefectFinding en la base de datos.
    3. Genera la imagen procesada con cajas superpuestas.
    4. Actualiza el veredicto sugerido en la inspección matriz.
    """
    photo = InspectionPhoto.objects.select_related('inspection', 'inspection__equipment').get(id=photo_id)
    photo.ai_status = InspectionPhoto.AIStatus.PROCESSING
    photo.save(update_fields=['ai_status'])

    if detector is None:
        detector = get_defect_detector()

    try:
        image_path = photo.image.path
        raw_findings = detector.detect_anomalies(image_path, photo_type=photo.photo_type)

        # Guardar hallazgos en la BD
        created_findings = []
        max_conf = 0.0
        for f_data in raw_findings:
            finding = DefectFinding.objects.create(
                photo=photo,
                defect_type=f_data['defect_type'],
                severity=f_data['severity'],
                confidence=f_data['confidence'],
                box_x=f_data.get('box_x', 0.0),
                box_y=f_data.get('box_y', 0.0),
                box_width=f_data.get('box_width', 0.2),
                box_height=f_data.get('box_height', 0.2),
                description=f_data.get('description', ''),
                confirmed_by_inspector=True
            )
            created_findings.append(finding)
            if f_data['confidence'] > max_conf:
                max_conf = f_data['confidence']

        # Superposición gráfica si hay hallazgos
        if created_findings:
            processed_temp_path = draw_defect_overlays(image_path, raw_findings)
            with open(processed_temp_path, 'rb') as pf:
                filename = os.path.basename(processed_temp_path)
                photo.processed_image.save(filename, File(pf), save=False)

        photo.ai_status = InspectionPhoto.AIStatus.COMPLETED
        photo.ai_confidence_score = max_conf
        photo.save()

        # Recalcular veredicto sugerido de la inspección
        recalculate_inspection_verdict(photo.inspection)

        return created_findings

    except Exception as exc:
        photo.ai_status = InspectionPhoto.AIStatus.FAILED
        photo.save(update_fields=['ai_status'])
        raise exc


def recalculate_inspection_verdict(inspection):
    """
    Recalcula el veredicto sugerido para una inspección agrupando todos los hallazgos de sus fotos.
    """
    all_findings = DefectFinding.objects.filter(photo__inspection=inspection)
    suggested, color, reasons, is_critical = calculate_inspection_verdict(
        equipment=inspection.equipment,
        findings=list(all_findings)
    )

    prev_suggested = inspection.suggested_verdict
    inspection.suggested_verdict = suggested

    # Si aún está en borrador o no ha sido modificado manualmente, alinear el final al sugerido
    if inspection.status == Inspection.Status.DRAFT:
        inspection.final_verdict = suggested

    inspection.save(update_fields=['suggested_verdict', 'final_verdict'])

    # Si cambió el veredicto sugerido, auditar
    if prev_suggested != suggested:
        VerdictAuditLog.objects.create(
            inspection=inspection,
            user=inspection.inspector,
            action=VerdictAuditLog.Action.SUGGESTED_BY_AI,
            previous_verdict=prev_suggested,
            new_verdict=suggested,
            justification=f"Recalculado automáticamente por IA: {'; '.join(reasons)}"
        )

    return suggested

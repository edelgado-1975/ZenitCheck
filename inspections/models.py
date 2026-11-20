"""
ZenitCheck — Modelos de Inspección, Fotos, Hallazgos y Auditoría de Veredicto.
"""

import uuid
from datetime import date, timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings
from equipment.models import Equipment
from accounts.models import User


class Inspection(models.Model):
    """
    Inspección técnica de un equipo de trabajo en alturas.
    """
    class Verdict(models.TextChoices):
        APPROVED = 'APPROVED', 'Apto / Aprobado para Operar'
        OBSERVATION = 'OBSERVATION', 'En Observación / Próximo a Vencer'
        REJECTED = 'REJECTED', 'Rechazado / Fuera de Servicio (Bloqueo Inmediato)'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador en Campo'
        ANALYZED = 'ANALYZED', 'Analizado con IA'
        CERTIFIED = 'CERTIFIED', 'Certificado y Firmado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name='inspections', verbose_name='Equipo Inspeccionado')
    inspector = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inspections_performed', verbose_name='Inspector Técnico')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspections_supervised', verbose_name='Supervisor Auditor')
    inspection_date = models.DateTimeField(default=timezone.now, verbose_name='Fecha y Hora de Inspección')
    location = models.CharField(max_length=200, blank=True, verbose_name='Ubicación / Sitio de Inspección')
    suggested_verdict = models.CharField(
        max_length=20,
        choices=Verdict.choices,
        default=Verdict.APPROVED,
        verbose_name='Veredicto Sugerido por IA'
    )
    final_verdict = models.CharField(
        max_length=20,
        choices=Verdict.choices,
        default=Verdict.APPROVED,
        verbose_name='Veredicto Final Emitido'
    )
    verdict_override_justification = models.TextField(
        blank=True,
        verbose_name='Justificación Obligatoria de Modificación',
        help_text='Requerido obligatoriamente si el veredicto final difiere del sugerido por la IA.'
    )
    general_observations = models.TextField(blank=True, verbose_name='Observaciones Generales del Inspector')
    next_inspection_due = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Límite Próxima Inspección'
    )
    is_certified = models.BooleanField(default=False, verbose_name='Certificado Emitido')
    certificate_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Estado del Registro')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inspección'
        verbose_name_plural = 'Inspecciones'
        ordering = ['-inspection_date']

    def __str__(self):
        return f"Inspección {self.equipment.serial_number} — {self.inspection_date.strftime('%Y-%m-%d')} [{self.get_final_verdict_display()}]"

    @property
    def verdict_color(self):
        colors = {
            self.Verdict.APPROVED: settings.VERDICT_COLORS['APPROVED'],
            self.Verdict.OBSERVATION: settings.VERDICT_COLORS['OBSERVATION'],
            self.Verdict.REJECTED: settings.VERDICT_COLORS['REJECTED'],
        }
        return colors.get(self.final_verdict, '#6B7280')

    def save(self, *args, **kwargs):
        # Si se aprueba la inspección, calcular próxima inspección a 12 meses
        if not self.next_inspection_due:
            base_date = self.inspection_date.date() if isinstance(self.inspection_date, timezone.datetime) else date.today()
            self.next_inspection_due = base_date + timedelta(days=365)
        super().save(*args, **kwargs)


class InspectionPhoto(models.Model):
    """
    Fotografía técnica del equipo tomada en campo o subida manualmente.
    Se comprime automáticamente antes de persistir.
    """
    class PhotoType(models.TextChoices):
        OVERALL = 'OVERALL', 'Vista General del Equipo'
        LABEL = 'LABEL', 'Etiqueta de Fabricación y Trazabilidad'
        SEAMS = 'SEAMS', 'Costuras Principales de Carga'
        D_RING = 'D_RING', 'Argolla Dorsal / Pectoral en D'
        WEBBING = 'WEBBING', 'Cintas Textiles y Fibras'
        BUCKLES = 'BUCKLES', 'Hebillas y Ajustes Metálicos'
        HOOKS = 'HOOKS', 'Ganchos / Mosquetones Acoplados'
        ROPE_BODY = 'ROPE_BODY', 'Cuerpo de Cuerda / Cable'
        OTHER = 'OTHER', 'Detalle Específico / Otro'

    class AIStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente de Análisis'
        PROCESSING = 'PROCESSING', 'Procesando con IA...'
        COMPLETED = 'COMPLETED', 'Análisis Completado'
        FAILED = 'FAILED', 'Error en Análisis'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='photos', verbose_name='Inspección')
    image = models.ImageField(upload_to='inspections/%Y/%m/', verbose_name='Fotografía Original Comprimida')
    processed_image = models.ImageField(
        upload_to='inspections/processed/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Imagen con Hallazgos de IA Superpuestos'
    )
    photo_type = models.CharField(max_length=30, choices=PhotoType.choices, default=PhotoType.OVERALL, verbose_name='Parte / Zona Fotografiada')
    original_filename = models.CharField(max_length=255, blank=True)
    ai_status = models.CharField(max_length=20, choices=AIStatus.choices, default=AIStatus.PENDING, verbose_name='Estado Análisis IA')
    ai_confidence_score = models.FloatField(default=0.0, verbose_name='Puntaje Máximo de Confianza IA')
    notes = models.TextField(blank=True, verbose_name='Notas del Inspector sobre la Foto')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fotografía de Inspección'
        verbose_name_plural = 'Fotografías de Inspección'
        ordering = ['created_at']

    def __str__(self):
        return f"Foto {self.get_photo_type_display()} ({self.inspection.equipment.serial_number})"


class DefectFinding(models.Model):
    """
    Hallazgo técnico o anomalía detectada por el motor de visión artificial o señalada por el inspector.
    """
    class DefectType(models.TextChoices):
        STITCH_FAILURE = 'STITCH_FAILURE', 'Falla / Rotura en Costura de Carga'
        DISCOLORATION = 'DISCOLORATION', 'Decoloración / Daño Químico o UV'
        CORROSION = 'CORROSION', 'Corrosión / Oxidación en Metal'
        WEAR_ABRASION = 'WEAR_ABRASION', 'Desgaste / Abrasión Severa de Cinta'
        CUT = 'CUT', 'Corte Transversal / Pérdida de Fibras'
        FRAYING = 'FRAYING', 'Deshilachado Superficial o Profundo'
        DEFORMATION = 'DEFORMATION', 'Deformación Mecánica en Conector / Argolla'
        LABEL_UNREADABLE = 'LABEL_UNREADABLE', 'Etiqueta Ilegible, Faltante o Adulterada'

    class Severity(models.TextChoices):
        CRITICAL = 'CRITICAL', 'Crítico (Rechazo Inmediato)'
        MAJOR = 'MAJOR', 'Mayor (Requiere Evaluación Detallada)'
        MINOR = 'MINOR', 'Menor (Observación Preventiva)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ForeignKey(InspectionPhoto, on_delete=models.CASCADE, related_name='findings', verbose_name='Foto')
    defect_type = models.CharField(max_length=40, choices=DefectType.choices, verbose_name='Tipo de Anomalía')
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.CRITICAL, verbose_name='Severidad')
    confidence = models.FloatField(default=0.0, verbose_name='Nivel de Confianza IA (0.0 a 1.0)')
    # Bounding Box normalizado (0.0 a 1.0)
    box_x = models.FloatField(default=0.0, verbose_name='Posición X Relativa')
    box_y = models.FloatField(default=0.0, verbose_name='Posición Y Relativa')
    box_width = models.FloatField(default=0.0, verbose_name='Ancho Relativo')
    box_height = models.FloatField(default=0.0, verbose_name='Alto Relativo')
    description = models.TextField(blank=True, verbose_name='Descripción del Hallazgo')
    confirmed_by_inspector = models.BooleanField(default=True, verbose_name='Confirmado por el Inspector')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hallazgo de Anomalía'
        verbose_name_plural = 'Hallazgos de Anomalía'
        ordering = ['-severity', '-confidence']

    def __str__(self):
        return f"{self.get_defect_type_display()} ({self.confidence:.0%}) — {self.get_severity_display()}"


class VerdictAuditLog(models.Model):
    """
    Registro inmutable de auditoría para cada emisión o modificación de veredicto.
    """
    class Action(models.TextChoices):
        SUGGESTED_BY_AI = 'SUGGESTED_BY_AI', 'Sugerido por Análisis de IA'
        CONFIRMED = 'CONFIRMED', 'Confirmado por Inspector'
        OVERRIDDEN = 'OVERRIDDEN', 'Modificado con Justificación'
        SUPERVISOR_AUDIT = 'SUPERVISOR_AUDIT', 'Auditado por Supervisor'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='verdict_audits', verbose_name='Inspección')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuario Responsable')
    action = models.CharField(max_length=30, choices=Action.choices, verbose_name='Acción Realizada')
    previous_verdict = models.CharField(max_length=20, blank=True, verbose_name='Veredicto Anterior')
    new_verdict = models.CharField(max_length=20, verbose_name='Veredicto Asignado')
    justification = models.TextField(blank=True, verbose_name='Justificación Técnica Obligatoria')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dirección IP')

    class Meta:
        verbose_name = 'Registro de Auditoría de Veredicto'
        verbose_name_plural = 'Registros de Auditoría de Veredictos'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Auditoría {self.inspection.id} por {self.user.username} a las {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

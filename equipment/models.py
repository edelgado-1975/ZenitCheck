"""
ZenitCheck — Catálogo y Registro de Equipos de Trabajo en Alturas.
Alineado con normas EN (Europa) y ANSI (USA).
"""

import uuid
from datetime import date
from django.db import models


class Brand(models.Model):
    """
    Marca fabricante de equipos de protección contra caídas.
    Incluye estado de verificación para garantizar rigor técnico sin datos inventados.
    """
    class Origin(models.TextChoices):
        INTERNATIONAL = 'INTERNATIONAL', 'Internacional'
        NATIONAL = 'NATIONAL', 'Nacional (Colombia / Regional)'

    class VerificationStatus(models.TextChoices):
        VERIFIED = 'VERIFIED', 'Verificada con documentación oficial'
        PENDING = 'PENDING', 'Pendiente de confirmación documental'

    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre de la Marca')
    origin = models.CharField(max_length=20, choices=Origin.choices, default=Origin.INTERNATIONAL, verbose_name='Origen')
    country = models.CharField(max_length=80, verbose_name='País de Origen / Sede')
    website = models.URLField(blank=True, verbose_name='Sitio Web Oficial')
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.VERIFIED,
        verbose_name='Estado de Verificación'
    )
    verification_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Verificación / Soporte Documental',
        help_text='Indicar fuente pública o marcar pendiente de confirmación si no hay catálogo técnico oficial disponible.'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activa en Catálogo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['name']

    def __str__(self):
        status_suffix = "" if self.verification_status == self.VerificationStatus.VERIFIED else " ⚠️ [Pendiente confirmación]"
        return f"{self.name} ({self.get_origin_display()}){status_suffix}"


class EquipmentType(models.Model):
    """
    Tipo de equipo o accesorio de altura, con sus normas industriales obligatorias asociadas.
    """
    code = models.CharField(max_length=50, unique=True, verbose_name='Código Técnico')
    name = models.CharField(max_length=120, verbose_name='Nombre del Tipo de Equipo')
    standard_international = models.CharField(
        max_length=100,
        verbose_name='Norma Europea / Internacional (EN/ISO)',
        help_text='Ej: EN 361, EN 360, EN 362, EN 355, EN 358'
    )
    standard_us = models.CharField(
        max_length=100,
        verbose_name='Norma Estadounidense (ANSI / NFPA)',
        help_text='Ej: ANSI Z359.11, ANSI Z359.14, ANSI Z359.12, ANSI Z359.13'
    )
    inspection_interval_months = models.PositiveIntegerField(
        default=12,
        verbose_name='Frecuencia Máxima de Inspección Periódica (Meses)',
        help_text='Estándar ANSI/OSHA exige inspección competente al menos cada 12 meses.'
    )
    max_lifespan_years = models.PositiveIntegerField(
        default=10,
        verbose_name='Vida Útil Máxima del Fabricante (Años)',
        help_text='Típicamente 5-10 años para materiales textiles; indefinido/condicional para metálicos.'
    )
    description = models.TextField(blank=True, verbose_name='Descripción y Criterios de Rechazo')
    critical_points = models.TextField(
        blank=True,
        verbose_name='Puntos Críticos de Inspección',
        help_text='Costuras de carga, argollas D, hebillas, etiqueta de trazabilidad, etc.'
    )

    class Meta:
        verbose_name = 'Tipo de Equipo'
        verbose_name_plural = 'Tipos de Equipo'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} [{self.standard_international} / {self.standard_us}]"


class Equipment(models.Model):
    """
    Equipo individual registrado con número de serie único y ciclo de vida de certificación.
    Centrado en equipos fabricados en los últimos 3 años o menos.
    """
    class Status(models.TextChoices):
        OPERATIONAL = 'OPERATIONAL', 'Apto / Operativo'
        OBSERVATION = 'OBSERVATION', 'En Observación / Próximo a Vencer'
        OUT_OF_SERVICE = 'OUT_OF_SERVICE', 'Fuera de Servicio / Rechazado'
        IN_INSPECTION = 'IN_INSPECTION', 'En Proceso de Inspección'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='equipments', verbose_name='Marca')
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.PROTECT, related_name='equipments', verbose_name='Tipo de Equipo')
    model_name = models.CharField(max_length=120, verbose_name='Modelo / Referencia Comercial')
    serial_number = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Número de Serie / Lote')
    manufacturing_date = models.DateField(
        verbose_name='Fecha de Fabricación',
        help_text='Fecha impresa en la etiqueta de trazabilidad del fabricante.'
    )
    first_use_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Puesta en Servicio'
    )
    last_inspection_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Última Inspección Formal'
    )
    certification_expiry_date = models.DateField(
        db_index=True,
        verbose_name='Fecha de Vencimiento de Certificación',
        help_text='Límite de validez del certificado vigente (máximo 12 meses desde la última inspección).'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPERATIONAL,
        verbose_name='Estado Operativo'
    )
    client_name = models.CharField(max_length=150, blank=True, verbose_name='Empresa Cliente / Propietario')
    location_assigned = models.CharField(max_length=150, blank=True, verbose_name='Ubicación / Proyecto Asignado')
    notes = models.TextField(blank=True, verbose_name='Observaciones Técnicas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Equipo de Altura'
        verbose_name_plural = 'Equipos de Altura'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.brand.name} {self.model_name} (S/N: {self.serial_number})"

    @property
    def days_until_expiry(self):
        if not self.certification_expiry_date:
            return 0
        delta = (self.certification_expiry_date - date.today()).days
        return delta

    @property
    def is_expired(self):
        return self.days_until_expiry < 0

    @property
    def is_expiring_soon(self):
        """Retorna True si vence en 30 días o menos y aún no ha vencido."""
        return 0 <= self.days_until_expiry <= 30

    @property
    def age_in_years(self):
        """Edad del equipo calculada desde la fecha de fabricación."""
        if not self.manufacturing_date:
            return 0.0
        delta = (date.today() - self.manufacturing_date).days
        return round(delta / 365.25, 1)


class Accessory(models.Model):
    """
    Accesorio acoplado a un equipo principal (mosquetón adicional, absorbedor integrado, pad confort, etc.).
    """
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='accessories', verbose_name='Equipo Principal')
    name = models.CharField(max_length=120, verbose_name='Nombre del Accesorio')
    serial_number = models.CharField(max_length=100, blank=True, verbose_name='Serial / Lote del Accesorio')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Marca del Accesorio')
    is_critical = models.BooleanField(
        default=False,
        verbose_name='Elemento Crítico de Retención',
        help_text='Si falla este accesorio, compromete directamente la seguridad del usuario.'
    )
    notes = models.TextField(blank=True, verbose_name='Descripción y Estado')

    class Meta:
        verbose_name = 'Accesorio'
        verbose_name_plural = 'Accesorios'

    def __str__(self):
        return f"{self.name} - Acoplado a: {self.equipment.serial_number}"

"""
ZenitCheck — Modelos de Sincronización Offline (SQLite Local) ↔ Online (PostgreSQL Central).
Permite operar en sitio sin conectividad y sincronizar con trazabilidad completa.
"""

import uuid
from django.db import models
from django.utils import timezone


class SyncQueueItem(models.Model):
    """
    Elemento en la cola de sincronización.
    Registra operaciones generadas offline para su replicación al servidor central.
    """
    class EntityType(models.TextChoices):
        EQUIPMENT = 'EQUIPMENT', 'Equipo de Altura'
        INSPECTION = 'INSPECTION', 'Inspección'
        PHOTO = 'PHOTO', 'Fotografía de Inspección'
        FINDING = 'FINDING', 'Hallazgo de Anomalía'
        AUDIT = 'AUDIT', 'Auditoría de Veredicto'

    class Operation(models.TextChoices):
        CREATE = 'CREATE', 'Creación'
        UPDATE = 'UPDATE', 'Actualización'
        DELETE = 'DELETE', 'Eliminación'

    class SyncStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente de Sincronización'
        SYNCED = 'SYNCED', 'Sincronizado Exitosamente'
        CONFLICT = 'CONFLICT', 'Conflicto Resuelto (Last-Write-Wins)'
        FAILED = 'FAILED', 'Error de Transmisión'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=30, choices=EntityType.choices, verbose_name='Tipo de Entidad')
    entity_id = models.CharField(max_length=100, db_index=True, verbose_name='ID de la Entidad')
    operation = models.CharField(max_length=20, choices=Operation.choices, default=Operation.CREATE, verbose_name='Operación')
    payload = models.JSONField(default=dict, verbose_name='Datos serializados de la entidad')
    client_timestamp = models.DateTimeField(default=timezone.now, verbose_name='Timestamp del Dispositivo Local')
    server_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Timestamp de Confirmación Central')
    status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING, verbose_name='Estado de Sincronización')
    conflict_notes = models.TextField(blank=True, verbose_name='Notas de Resolución de Conflictos')
    retry_count = models.PositiveIntegerField(default=0, verbose_name='Reintentos')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Elemento de Cola de Sincronización'
        verbose_name_plural = 'Cola de Sincronización'
        ordering = ['client_timestamp']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.entity_type} {self.entity_id} ({self.operation})"

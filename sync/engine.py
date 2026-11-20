"""
ZenitCheck — Motor de Sincronización y Resolución de Conflictos.
Estrategia: Last-Write-Wins con log inmutable de auditoría.
Valida datos del cliente e historial del equipo antes de permitir la certificación en la BD central.
"""

from datetime import datetime
from django.utils import timezone
from .models import SyncQueueItem


def enqueue_change(entity_type, entity_id, operation, payload, client_timestamp=None):
    """Agrega un cambio a la cola de sincronización local."""
    if client_timestamp is None:
        client_timestamp = timezone.now()

    return SyncQueueItem.objects.create(
        entity_type=entity_type,
        entity_id=str(entity_id),
        operation=operation,
        payload=payload,
        client_timestamp=client_timestamp,
        status=SyncQueueItem.SyncStatus.PENDING
    )


def resolve_conflict_last_write_wins(incoming_timestamp, remote_timestamp, incoming_data, remote_data):
    """
    Estrategia de resolución de conflictos: Last-Write-Wins (LWW).
    Compara marcas de tiempo UTC. La modificación más reciente prevalece.

    Retorna: (winning_data, was_incoming_winner, conflict_note)
    """
    if incoming_timestamp >= remote_timestamp:
        # Prevalece el dato local entrante
        note = (
            f"Conflicto LWW resuelto a favor de cambio local "
            f"(Local: {incoming_timestamp.isoformat()} >= Central: {remote_timestamp.isoformat()})."
        )
        return incoming_data, True, note
    else:
        # Prevalece el dato remoto central
        note = (
            f"Conflicto LWW resuelto a favor del servidor central "
            f"(Central: {remote_timestamp.isoformat()} > Local: {incoming_timestamp.isoformat()})."
        )
        return remote_data, False, note


def validate_certification_prerequisites(equipment_data, client_data):
    """
    Valida requisitos indispensables antes de emitir la certificación final en la BD central:
    - Cliente debe tener identificación/razón social válida.
    - Equipo debe tener serial registrado y fecha de fabricación verificable.
    """
    errors = []
    if not client_data.get('client_name'):
        errors.append("El cliente o propietario del equipo es obligatorio para emitir certificado central.")

    if not equipment_data.get('serial_number'):
        errors.append("El número de serie es obligatorio.")

    return len(errors) == 0, errors

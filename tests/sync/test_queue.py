"""
Pruebas de la cola de sincronización offline.
"""

import pytest
from django.utils import timezone
from sync.models import SyncQueueItem
from sync.engine import enqueue_change


@pytest.mark.django_db
class TestSyncQueue:
    def test_enqueue_change_creates_pending_item(self):
        item = enqueue_change(
            entity_type=SyncQueueItem.EntityType.EQUIPMENT,
            entity_id="EQ-1002",
            operation=SyncQueueItem.Operation.CREATE,
            payload={"serial_number": "EQ-1002", "model": "ExoFit"}
        )

        assert item.pk is not None
        assert item.status == SyncQueueItem.SyncStatus.PENDING
        assert item.payload['serial_number'] == "EQ-1002"
        assert item.retry_count == 0

    def test_queue_ordering_by_client_timestamp(self):
        t1 = timezone.now()
        t2 = t1 + timezone.timedelta(seconds=10)

        enqueue_change('INSPECTION', 'INS-2', 'UPDATE', {}, client_timestamp=t2)
        enqueue_change('INSPECTION', 'INS-1', 'CREATE', {}, client_timestamp=t1)

        items = list(SyncQueueItem.objects.all())
        assert items[0].entity_id == 'INS-1'
        assert items[1].entity_id == 'INS-2'

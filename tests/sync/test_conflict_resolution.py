"""
Pruebas de resolución de conflictos (Last-Write-Wins).
"""

from datetime import datetime, timezone, timedelta
from sync.engine import resolve_conflict_last_write_wins


class TestConflictResolution:
    def test_incoming_newer_wins(self):
        t_remote = datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
        t_local = t_remote + timedelta(minutes=15)  # Local es más reciente

        local_data = {"status": "OPERATIONAL", "notes": "Inspeccionado en campo"}
        remote_data = {"status": "OBSERVATION", "notes": "Registro previo central"}

        winner, was_local, note = resolve_conflict_last_write_wins(
            incoming_timestamp=t_local,
            remote_timestamp=t_remote,
            incoming_data=local_data,
            remote_data=remote_data
        )

        assert was_local is True
        assert winner["status"] == "OPERATIONAL"
        assert "a favor de cambio local" in note

    def test_remote_newer_wins(self):
        t_local = datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
        t_remote = t_local + timedelta(hours=1)  # Central fue actualizado después

        local_data = {"status": "OBSERVATION"}
        remote_data = {"status": "REJECTED"}

        winner, was_local, note = resolve_conflict_last_write_wins(
            incoming_timestamp=t_local,
            remote_timestamp=t_remote,
            incoming_data=local_data,
            remote_data=remote_data
        )

        assert was_local is False
        assert winner["status"] == "REJECTED"
        assert "a favor del servidor central" in note

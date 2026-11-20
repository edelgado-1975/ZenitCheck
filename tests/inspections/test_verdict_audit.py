"""
Pruebas de auditoría inmutable de veredictos.
"""

import pytest
from inspections.models import Inspection, VerdictAuditLog
from tests.inspections.conftest import InspectionFactory
from tests.accounts.conftest import UserFactory


@pytest.mark.django_db
class TestVerdictAudit:
    def test_audit_log_creation_on_override(self):
        inspector = UserFactory(username="inspector_audit")
        inspection = InspectionFactory(
            inspector=inspector,
            suggested_verdict=Inspection.Verdict.APPROVED,
            final_verdict=Inspection.Verdict.APPROVED
        )

        # Inspector decide modificar veredicto a RECHAZADO con justificación
        inspection.final_verdict = Inspection.Verdict.REJECTED
        inspection.verdict_override_justification = "Se detectó corte no visible en fotos en cinta dorsal."
        inspection.save()

        log = VerdictAuditLog.objects.create(
            inspection=inspection,
            user=inspector,
            action=VerdictAuditLog.Action.OVERRIDDEN,
            previous_verdict='APPROVED',
            new_verdict='REJECTED',
            justification=inspection.verdict_override_justification,
            ip_address="192.168.1.50"
        )

        assert log.pk is not None
        assert inspection.verdict_audits.count() == 1
        assert "corte no visible" in log.justification
        assert log.action == VerdictAuditLog.Action.OVERRIDDEN

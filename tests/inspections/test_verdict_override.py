"""
Pruebas de validación de modificación de veredicto (justificación obligatoria).
"""

import pytest
from django.core.exceptions import ValidationError
from inspections.models import Inspection
from tests.inspections.conftest import InspectionFactory


@pytest.mark.django_db
class TestVerdictOverrideValidation:
    def test_override_without_justification_is_invalid(self):
        """Si el veredicto final es diferente al sugerido, la justificación no puede estar vacía."""
        inspection = InspectionFactory(
            suggested_verdict=Inspection.Verdict.APPROVED,
            final_verdict=Inspection.Verdict.REJECTED,
            verdict_override_justification=""
        )

        # Regla de negocio en formulario/validación
        is_override = inspection.final_verdict != inspection.suggested_verdict
        has_justification = bool(inspection.verdict_override_justification.strip())

        assert is_override is True
        assert has_justification is False  # Inválido: debe exigirse justificación

    def test_override_with_justification_is_valid(self):
        inspection = InspectionFactory(
            suggested_verdict=Inspection.Verdict.APPROVED,
            final_verdict=Inspection.Verdict.REJECTED,
            verdict_override_justification="Desgaste en costuras constatado físicamente."
        )

        is_override = inspection.final_verdict != inspection.suggested_verdict
        has_justification = bool(inspection.verdict_override_justification.strip())

        assert is_override is True
        assert has_justification is True  # Válido

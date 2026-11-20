"""
Pruebas de validación de formularios de UI.
"""

import pytest
from inspections.forms import VerdictConfirmationForm, InspectionCreateForm
from inspections.models import Inspection
from tests.inspections.conftest import InspectionFactory
from tests.equipment.conftest import EquipmentFactory


@pytest.mark.django_db
class TestUIForms:
    def test_verdict_form_validates_mandatory_override_justification(self):
        ins = InspectionFactory(suggested_verdict='APPROVED', final_verdict='APPROVED')
        # Intentar modificar a REJECTED sin justificación
        form = VerdictConfirmationForm(
            data={'final_verdict': 'REJECTED', 'verdict_override_justification': ''},
            instance=ins
        )
        assert not form.is_valid()
        assert 'verdict_override_justification' in form.errors

    def test_inspection_create_form_valid(self):
        eq = EquipmentFactory()
        form = InspectionCreateForm(data={
            'equipment': eq.id,
            'location': 'Frente 1',
            'general_observations': 'Buen estado'
        })
        assert form.is_valid()

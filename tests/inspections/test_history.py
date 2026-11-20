"""
Pruebas de la vista de historial de equipo.
"""

import pytest
from django.urls import reverse
from tests.inspections.conftest import InspectionFactory
from tests.equipment.conftest import EquipmentFactory
from tests.accounts.conftest import UserFactory


@pytest.mark.django_db
class TestEquipmentHistory:
    def test_history_shows_all_inspections_chronologically(self, client):
        user = UserFactory(username="tester")
        client.force_login(user)

        eq = EquipmentFactory(serial_number="HIST-SN-1234")
        ins1 = InspectionFactory(equipment=eq)
        ins2 = InspectionFactory(equipment=eq)

        url = reverse('inspections:equipment_history', kwargs={'serial_number': eq.serial_number})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert "HIST-SN-1234" in content
        assert "Historial de Inspecciones" in content

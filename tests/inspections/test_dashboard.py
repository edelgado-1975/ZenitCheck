"""
Pruebas del Dashboard de inspección y métricas.
"""

import pytest
from django.urls import reverse
from tests.accounts.conftest import UserFactory
from tests.equipment.conftest import EquipmentFactory
from equipment.models import Equipment


@pytest.mark.django_db
class TestDashboard:
    def test_dashboard_metrics_counts(self, client):
        user = UserFactory(username="dash_user")
        client.force_login(user)

        EquipmentFactory(status=Equipment.Status.OPERATIONAL)
        EquipmentFactory(status=Equipment.Status.OBSERVATION)
        EquipmentFactory(status=Equipment.Status.OUT_OF_SERVICE)

        url = reverse('inspections:dashboard')
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['total_equipments'] >= 3
        assert response.context['operational'] >= 1
        assert response.context['observation'] >= 1
        assert response.context['out_of_service'] >= 1

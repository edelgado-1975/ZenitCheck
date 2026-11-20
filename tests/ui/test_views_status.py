"""
Pruebas de código HTTP 200 para todas las vistas principales.
"""

import pytest
from django.urls import reverse
from tests.accounts.conftest import UserFactory
from tests.equipment.conftest import EquipmentFactory
from tests.inspections.conftest import InspectionFactory


@pytest.mark.django_db
class TestViewsStatus:
    def test_all_views_return_200_for_authenticated_user(self, client):
        user = UserFactory(username="ui_tester", is_staff=True)
        client.force_login(user)

        eq = EquipmentFactory()
        ins = InspectionFactory(equipment=eq)

        urls = [
            reverse('inspections:dashboard'),
            reverse('inspections:list'),
            reverse('inspections:create'),
            reverse('inspections:detail', kwargs={'inspection_id': ins.id}),
            reverse('inspections:equipment_history', kwargs={'serial_number': eq.serial_number}),
            reverse('inspections:alerts'),
            reverse('equipment:list'),
            reverse('accounts:profile'),
        ]

        for url in urls:
            resp = client.get(url)
            assert resp.status_code == 200, f"Fallo en URL: {url}"

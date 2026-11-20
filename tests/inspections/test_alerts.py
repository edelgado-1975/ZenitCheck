"""
Pruebas de alertas de vencimiento de certificación.
"""

from datetime import date, timedelta
import pytest
from django.urls import reverse
from tests.equipment.conftest import EquipmentFactory
from tests.accounts.conftest import UserFactory


@pytest.mark.django_db
class TestAlerts:
    def test_alerts_view_classifies_expired_and_expiring_soon(self, client):
        user = UserFactory(username="alert_tester")
        client.force_login(user)

        today = date.today()
        # Vencido
        eq_expired = EquipmentFactory(
            serial_number="ALERT-EXP-01",
            certification_expiry_date=today - timedelta(days=5)
        )
        # Próximo a vencer (15 días)
        eq_soon = EquipmentFactory(
            serial_number="ALERT-SOON-02",
            certification_expiry_date=today + timedelta(days=15)
        )

        url = reverse('inspections:alerts')
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert "ALERT-EXP-01" in content
        assert "ALERT-SOON-02" in content

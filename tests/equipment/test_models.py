"""
Pruebas de modelos para equipment.
"""

from datetime import date, timedelta
import pytest
from django.db import IntegrityError
from equipment.models import Brand, EquipmentType, Equipment, Accessory
from tests.equipment.conftest import BrandFactory, EquipmentTypeFactory, EquipmentFactory, AccessoryFactory


@pytest.mark.django_db
class TestBrandModel:
    def test_create_brand(self):
        brand = BrandFactory(name="Petzl", origin=Brand.Origin.INTERNATIONAL)
        assert brand.pk is not None
        assert str(brand) == "Petzl (Internacional)"

    def test_brand_unique_name(self):
        BrandFactory(name="3M")
        with pytest.raises(IntegrityError):
            BrandFactory(name="3M")

    def test_unverified_brand_representation(self):
        brand = BrandFactory(
            name="XP Safety",
            verification_status=Brand.VerificationStatus.PENDING
        )
        assert "[Pendiente confirmación]" in str(brand)


@pytest.mark.django_db
class TestEquipmentTypeModel:
    def test_create_equipment_type(self):
        eq_type = EquipmentTypeFactory(
            code="HARNESS",
            name="Arnés",
            standard_international="EN 361",
            standard_us="ANSI Z359.11"
        )
        assert str(eq_type) == "Arnés [EN 361 / ANSI Z359.11]"

    def test_unique_code(self):
        EquipmentTypeFactory(code="SRL")
        with pytest.raises(IntegrityError):
            EquipmentTypeFactory(code="SRL")


@pytest.mark.django_db
class TestEquipmentModel:
    def test_create_equipment(self):
        eq = EquipmentFactory(serial_number="TEST-SN-001")
        assert eq.pk is not None
        assert "TEST-SN-001" in str(eq)

    def test_unique_serial_number(self):
        EquipmentFactory(serial_number="SERIAL-DUPLICATE")
        with pytest.raises(IntegrityError):
            EquipmentFactory(serial_number="SERIAL-DUPLICATE")

    def test_days_until_expiry_positive(self):
        today = date.today()
        eq = EquipmentFactory(certification_expiry_date=today + timedelta(days=45))
        assert eq.days_until_expiry == 45
        assert not eq.is_expired
        assert not eq.is_expiring_soon

    def test_days_until_expiry_expiring_soon(self):
        today = date.today()
        eq = EquipmentFactory(certification_expiry_date=today + timedelta(days=15))
        assert eq.days_until_expiry == 15
        assert not eq.is_expired
        assert eq.is_expiring_soon

    def test_days_until_expiry_expired(self):
        today = date.today()
        eq = EquipmentFactory(certification_expiry_date=today - timedelta(days=10))
        assert eq.days_until_expiry == -10
        assert eq.is_expired
        assert not eq.is_expiring_soon

    def test_age_in_years_calculation(self):
        today = date.today()
        eq = EquipmentFactory(manufacturing_date=today - timedelta(days=730))
        assert 1.9 <= eq.age_in_years <= 2.1


@pytest.mark.django_db
class TestAccessoryModel:
    def test_accessory_creation(self):
        acc = AccessoryFactory(name="Pad lumbar", is_critical=False)
        assert acc.pk is not None
        assert "Pad lumbar" in str(acc)
        assert not acc.is_critical

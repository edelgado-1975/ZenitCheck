"""
Fixtures y Factories para tests de equipment.
"""

from datetime import date, timedelta
import factory
import pytest
from equipment.models import Brand, EquipmentType, Equipment, Accessory


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f"Marca-{n}")
    origin = Brand.Origin.INTERNATIONAL
    country = "Francia"
    website = "https://example.com"
    verification_status = Brand.VerificationStatus.VERIFIED
    verification_notes = "Documentación técnica oficial verificada."


class EquipmentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentType

    code = factory.Sequence(lambda n: f"TYPE_{n}")
    name = factory.Sequence(lambda n: f"Tipo de Equipo {n}")
    standard_international = "EN 361:2002"
    standard_us = "ANSI/ASSP Z359.11-2021"
    inspection_interval_months = 12
    max_lifespan_years = 10
    critical_points = "Costuras de carga, argolla D, hebillas."


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment

    brand = factory.SubFactory(BrandFactory)
    equipment_type = factory.SubFactory(EquipmentTypeFactory)
    model_name = "Arnés Pro-Fit X"
    serial_number = factory.Sequence(lambda n: f"SN-2024-{n:05d}")
    manufacturing_date = factory.LazyFunction(lambda: date.today() - timedelta(days=180))
    first_use_date = factory.LazyFunction(lambda: date.today() - timedelta(days=150))
    last_inspection_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    certification_expiry_date = factory.LazyFunction(lambda: date.today() + timedelta(days=335))
    status = Equipment.Status.OPERATIONAL
    client_name = "Constructora Nacional"
    location_assigned = "Edificio Torre 1"


class AccessoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Accessory

    equipment = factory.SubFactory(EquipmentFactory)
    name = "Mosquetón de anclaje"
    serial_number = factory.Sequence(lambda n: f"ACC-{n:04d}")
    is_critical = True


@pytest.fixture
def brand(db):
    return BrandFactory()


@pytest.fixture
def equipment_type(db):
    return EquipmentTypeFactory()


@pytest.fixture
def equipment(db):
    return EquipmentFactory()

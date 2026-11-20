"""
Pruebas de factories para equipment.
"""

import pytest
from tests.equipment.conftest import BrandFactory, EquipmentTypeFactory, EquipmentFactory, AccessoryFactory


@pytest.mark.django_db
class TestEquipmentFactories:
    def test_brand_factory_batch(self):
        brands = BrandFactory.create_batch(5)
        assert len(brands) == 5
        names = [b.name for b in brands]
        assert len(set(names)) == 5  # Todos únicos

    def test_equipment_factory_defaults(self):
        eq = EquipmentFactory()
        assert eq.brand is not None
        assert eq.equipment_type is not None
        assert eq.serial_number.startswith("SN-")

    def test_accessory_factory_relation(self):
        acc = AccessoryFactory()
        assert acc.equipment is not None
        assert acc.equipment.accessories.count() == 1

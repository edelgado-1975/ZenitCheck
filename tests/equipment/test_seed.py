"""
Prueba del comando de seed catalog.
Verifica que se carguen las 10+ marcas (con verificabilidad) y normas EN/ANSI.
"""

import pytest
from django.core.management import call_command
from equipment.models import Brand, EquipmentType, Equipment


@pytest.mark.django_db
class TestSeedCatalogCommand:
    def test_seed_catalog_execution(self):
        # Ejecutar comando
        call_command('seed_catalog')

        # Verificar tipos de equipo cargados con normas
        types = EquipmentType.objects.all()
        assert types.count() >= 8
        harness = EquipmentType.objects.get(code='HARNESS_FULL_BODY')
        assert 'EN 361' in harness.standard_international
        assert 'ANSI' in harness.standard_us

        # Verificar marcas cargadas (10+ marcas requeridas)
        brands = Brand.objects.all()
        assert brands.count() >= 10

        # Verificar marcas internacionales verificadas
        assert Brand.objects.filter(name__icontains='3M', verification_status=Brand.VerificationStatus.VERIFIED).exists()
        assert Brand.objects.filter(name__icontains='Petzl', verification_status=Brand.VerificationStatus.VERIFIED).exists()
        assert Brand.objects.filter(name__icontains='MSA', verification_status=Brand.VerificationStatus.VERIFIED).exists()
        assert Brand.objects.filter(name__icontains='Honeywell', verification_status=Brand.VerificationStatus.VERIFIED).exists()

        # Verificar marcas nacionales marcadas como pendientes de confirmación
        assert Brand.objects.filter(name__icontains='XP Safety', verification_status=Brand.VerificationStatus.PENDING).exists()
        assert Brand.objects.filter(name__icontains='Armadura', verification_status=Brand.VerificationStatus.PENDING).exists()

        # Verificar que se crearon equipos de demostración (2023-2026)
        equipments = Equipment.objects.all()
        assert equipments.count() >= 5
        for eq in equipments:
            assert eq.manufacturing_date.year >= 2023

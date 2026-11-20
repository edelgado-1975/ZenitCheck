"""
Pruebas de contenido exhaustivo del certificado PDF.
"""

import pytest
from reports.generator import generate_inspection_certificate_pdf
from tests.inspections.conftest import InspectionFactory
from tests.equipment.conftest import EquipmentFactory


@pytest.mark.django_db
class TestPDFContent:
    def test_pdf_contains_equipment_and_standards(self):
        eq = EquipmentFactory(serial_number="CERT-SERIAL-9988")
        inspection = InspectionFactory(equipment=eq)

        pdf_bytes, _ = generate_inspection_certificate_pdf(inspection)

        # En ReportLab, las cadenas de texto quedan codificadas en el flujo PDF
        assert b"CERT-SERIAL-9988" in pdf_bytes
        assert eq.equipment_type.standard_international.encode('utf-8') in pdf_bytes
        assert eq.equipment_type.standard_us.encode('utf-8') in pdf_bytes

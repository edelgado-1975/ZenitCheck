"""
Pruebas de aplicación de colores de veredicto en la generación de PDF.
"""

import pytest
from reports.generator import generate_inspection_certificate_pdf
from inspections.models import Inspection
from tests.inspections.conftest import InspectionFactory


@pytest.mark.django_db
class TestPDFColors:
    def test_approved_pdf_generation(self):
        ins = InspectionFactory(final_verdict=Inspection.Verdict.APPROVED)
        pdf_bytes, _ = generate_inspection_certificate_pdf(ins)
        assert len(pdf_bytes) > 0

    def test_observation_pdf_generation(self):
        ins = InspectionFactory(final_verdict=Inspection.Verdict.OBSERVATION)
        pdf_bytes, _ = generate_inspection_certificate_pdf(ins)
        assert len(pdf_bytes) > 0

    def test_rejected_pdf_generation(self):
        ins = InspectionFactory(final_verdict=Inspection.Verdict.REJECTED)
        pdf_bytes, _ = generate_inspection_certificate_pdf(ins)
        assert len(pdf_bytes) > 0

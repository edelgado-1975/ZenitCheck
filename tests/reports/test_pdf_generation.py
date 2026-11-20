"""
Pruebas de generación del archivo PDF de certificado.
"""

import pytest
from reports.generator import generate_inspection_certificate_pdf
from tests.inspections.conftest import InspectionFactory


@pytest.mark.django_db
class TestPDFGeneration:
    def test_pdf_is_generated_as_valid_bytes(self):
        inspection = InspectionFactory()
        pdf_bytes, sig_info = generate_inspection_certificate_pdf(inspection)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        # Cabecera estándar de archivo PDF
        assert pdf_bytes.startswith(b"%PDF-")

    def test_pdf_signature_info_structure(self):
        inspection = InspectionFactory()
        _, sig_info = generate_inspection_certificate_pdf(inspection)

        assert 'sha256_hash' in sig_info
        assert len(sig_info['sha256_hash']) == 64  # Hexadecimal SHA-256
        assert 'signature_hex' in sig_info
        assert len(sig_info['signature_hex']) > 100
        assert 'signed_at' in sig_info

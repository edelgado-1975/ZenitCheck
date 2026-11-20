"""
Pruebas de firma digital X.509 y verificación criptográfica.
"""

import pytest
from cryptography import x509
from reports.signer import ensure_certificate_authority, sign_pdf_data, compute_pdf_digest


class TestDigitalSignature:
    def test_ca_creation_and_certificate_validity(self):
        key_path, cert_path = ensure_certificate_authority()
        with open(cert_path, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())

        assert "ZenitCheck" in str(cert.subject)
        # Compatible con versiones recientes de cryptography
        assert cert.not_valid_after_utc is not None

    def test_sign_pdf_digest_consistency(self):
        data = b"%PDF-1.4 Fake test content for crypto validation"
        digest = compute_pdf_digest(data)
        assert len(digest) == 64

        sig_info = sign_pdf_data(data)
        assert sig_info['sha256_hash'] == digest

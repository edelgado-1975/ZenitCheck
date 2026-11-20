"""
ZenitCheck — Generación de Claves X.509 y Firma Digital Criptográfica de Certificados.
Cumple estándares de seguridad e inalterabilidad de documentos técnicos.
"""

import os
from datetime import datetime, timezone, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings


def ensure_certificate_authority():
    """
    Verifica o genera el par de claves RSA y el certificado X.509 autofirmado
    para la entidad certificadora de ZenitCheck.
    """
    certs_dir = settings.BASE_DIR / 'certs'
    os.makedirs(certs_dir, exist_ok=True)

    key_path = certs_dir / 'private_key.pem'
    cert_path = certs_dir / 'certificate.pem'

    if os.path.exists(key_path) and os.path.exists(cert_path):
        return str(key_path), str(cert_path)

    # Generar clave privada RSA de 2048 bits
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Crear certificado X.509
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CO"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Bogota DC"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Bogota"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ZenitCheck Certificaciones de Altura"),
        x509.NameAttribute(NameOID.COMMON_NAME, "ZenitCheck CA - Certificados de Seguridad en Alturas"),
    ])

    now = datetime.now(timezone.utc)
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        now
    ).not_valid_after(
        now + timedelta(days=3650)  # Válido por 10 años
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    ).sign(private_key, hashes.SHA256())

    # Guardar clave privada
    with open(key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Guardar certificado
    with open(cert_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return str(key_path), str(cert_path)


def compute_pdf_digest(pdf_bytes):
    """Calcula el hash criptográfico SHA-256 del contenido del PDF."""
    digest = hashes.Hash(hashes.SHA256())
    digest.update(pdf_bytes)
    return digest.finalize().hex()


def sign_pdf_data(pdf_bytes):
    """
    Firma digitalmente el contenido binario del certificado PDF.
    Retorna el hash SHA-256 y la firma digital RSA PKCS#1 v1.5 en formato hexadecimal.
    """
    key_path, cert_path = ensure_certificate_authority()

    with open(key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Hashear y firmar
    from cryptography.hazmat.primitives.asymmetric import padding
    signature = private_key.sign(
        pdf_bytes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return {
        'sha256_hash': compute_pdf_digest(pdf_bytes),
        'signature_hex': signature.hex(),
        'certificate_path': cert_path,
        'signed_at': datetime.now(timezone.utc).isoformat(),
    }

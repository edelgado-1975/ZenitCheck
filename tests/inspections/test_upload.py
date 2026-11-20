"""
Pruebas de validación de carga y tamaño de imágenes.
"""

import io
import pytest
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from inspections.image_utils import validate_image_file, MAX_FILE_SIZE_BYTES


class TestImageUploadValidation:
    def test_valid_jpeg_passes(self):
        f = io.BytesIO()
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img.save(f, format='JPEG')
        f.seek(0)
        uploaded = SimpleUploadedFile("foto.jpg", f.read(), content_type="image/jpeg")
        # No debe lanzar excepción
        validate_image_file(uploaded)

    def test_valid_png_passes(self):
        f = io.BytesIO()
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        img.save(f, format='PNG')
        f.seek(0)
        uploaded = SimpleUploadedFile("foto.png", f.read(), content_type="image/png")
        validate_image_file(uploaded)

    def test_invalid_extension_raises_validation_error(self):
        f = io.BytesIO(b"fake executable content")
        uploaded = SimpleUploadedFile("malware.exe", f.read(), content_type="application/octet-stream")
        with pytest.raises(ValidationError):
            validate_image_file(uploaded)

    def test_corrupted_image_raises_validation_error(self):
        f = io.BytesIO(b"not an image at all but renamed to .jpg")
        uploaded = SimpleUploadedFile("corrupto.jpg", f.read(), content_type="image/jpeg")
        with pytest.raises(ValidationError):
            validate_image_file(uploaded)

    def test_file_exceeding_max_size_raises_validation_error(self):
        f = io.BytesIO()
        img = Image.new('RGB', (50, 50))
        img.save(f, format='JPEG')
        f.seek(0)
        uploaded = SimpleUploadedFile("grande.jpg", f.read(), content_type="image/jpeg")
        uploaded.size = MAX_FILE_SIZE_BYTES + 1024  # Forzar tamaño mayor a 10MB
        with pytest.raises(ValidationError):
            validate_image_file(uploaded)

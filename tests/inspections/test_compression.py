"""
Pruebas de compresión y redimensionamiento con Pillow.
"""

import io
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from inspections.image_utils import compress_image


class TestImageCompression:
    def test_image_is_compressed_and_resized(self):
        # Crear imagen grande (3000 x 2000 px)
        large_buf = io.BytesIO()
        large_img = Image.new('RGB', (3000, 2000), color=(120, 200, 150))
        large_img.save(large_buf, format='JPEG', quality=95)
        large_buf.seek(0)

        uploaded = SimpleUploadedFile("gran_foto.jpg", large_buf.read(), content_type="image/jpeg")

        compressed = compress_image(uploaded, max_dimension=1920, quality=80)

        assert compressed is not None
        assert compressed.name.endswith(".jpg")

        # Verificar dimensiones del resultado
        result_img = Image.open(compressed)
        w, h = result_img.size
        assert max(w, h) <= 1920
        # Mantiene aspect ratio 3:2
        assert abs((w / h) - (3000 / 2000)) < 0.05

    def test_rgba_converted_to_rgb_cleanly(self):
        rgba_buf = io.BytesIO()
        rgba_img = Image.new('RGBA', (200, 200), color=(255, 0, 0, 128))
        rgba_img.save(rgba_buf, format='PNG')
        rgba_buf.seek(0)

        uploaded = SimpleUploadedFile("transparente.png", rgba_buf.read(), content_type="image/png")
        compressed = compress_image(uploaded)

        result_img = Image.open(compressed)
        assert result_img.mode == 'RGB'

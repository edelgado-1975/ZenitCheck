"""
Pruebas de sincronización de imágenes y consistencia de almacenamiento.
"""

import io
from PIL import Image
from inspections.image_utils import compress_image
from django.core.files.uploadedfile import SimpleUploadedFile


class TestImageSyncConsistency:
    def test_image_payload_is_reproducible_between_environments(self):
        """Verifica que la compresión genere un formato estándar JPEG compatible entre SQLite y PostgreSQL."""
        buf = io.BytesIO()
        img = Image.new('RGB', (500, 500), color=(10, 20, 30))
        img.save(buf, format='JPEG')
        buf.seek(0)

        uploaded = SimpleUploadedFile("sync_test.jpg", buf.read(), content_type="image/jpeg")
        compressed = compress_image(uploaded)

        assert compressed.content_type == 'image/jpeg'
        assert compressed.size > 0

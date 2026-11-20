"""
Pruebas de superposición gráfica de hallazgos sobre la imagen (Overlay).
"""

import os
import tempfile
import pytest
from PIL import Image
from ai_engine.overlay import draw_defect_overlays


@pytest.fixture
def base_test_image():
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img = Image.new('RGB', (600, 400), color=(200, 200, 200))
    img.save(tmp.name, format='JPEG')
    tmp.close()
    yield tmp.name
    if os.path.exists(tmp.name):
        try:
            os.remove(tmp.name)
        except OSError:
            pass


class TestOverlayGraphics:
    def test_draw_overlay_creates_valid_image(self, base_test_image):
        findings = [
            {
                'defect_type': 'CUT',
                'severity': 'CRITICAL',
                'confidence': 0.92,
                'box_x': 0.2,
                'box_y': 0.2,
                'box_width': 0.3,
                'box_height': 0.3,
            }
        ]

        out_path = draw_defect_overlays(base_test_image, findings)
        assert os.path.exists(out_path)

        # Usar context manager para cerrar el descriptor de archivo en Windows
        with Image.open(out_path) as out_img:
            assert out_img.size == (600, 400)
            assert out_img.mode == 'RGB'

        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass

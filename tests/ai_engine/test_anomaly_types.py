"""
Pruebas de detección de tipos de anomalía con imágenes sintéticas.
"""

import os
import tempfile
import pytest
from PIL import Image, ImageDraw
from ai_engine.detector import ComputerVisionDefectDetector


@pytest.fixture
def rust_image():
    """Genera imagen con mancha de óxido (tonos naranjas/rojizos oscuros)."""
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img = Image.new('RGB', (400, 400), color=(180, 180, 180))
    draw = ImageDraw.Draw(img)
    # Mancha de óxido color herrumbre (H ~ 15 en HSV, R alto, G medio, B bajo)
    draw.rectangle([100, 100, 300, 300], fill=(160, 60, 10))
    img.save(tmp.name, format='JPEG')
    tmp.close()
    yield tmp.name
    if os.path.exists(tmp.name):
        os.remove(tmp.name)


class TestAnomalyTypes:
    def test_rust_corrosion_detection(self, rust_image):
        detector = ComputerVisionDefectDetector()
        findings = detector.detect_anomalies(rust_image, photo_type='HOOKS')
        rust_findings = [f for f in findings if f['defect_type'] == 'CORROSION']
        assert len(rust_findings) >= 1
        assert rust_findings[0]['confidence'] >= 0.50
        assert rust_findings[0]['box_width'] > 0
        assert rust_findings[0]['box_height'] > 0

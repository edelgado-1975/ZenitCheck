"""
Pruebas de interfaz desacoplada y analizador de visión artificial.
"""

import os
import tempfile
import pytest
from PIL import Image
from ai_engine.detector import ComputerVisionDefectDetector, MockDefectDetector, BaseDefectDetector


@pytest.fixture
def sample_clean_image():
    """Genera una imagen sintética limpia."""
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img = Image.new('RGB', (400, 400), color=(80, 80, 80))
    img.save(tmp.name, format='JPEG')
    tmp.close()
    yield tmp.name
    if os.path.exists(tmp.name):
        os.remove(tmp.name)


class TestDefectAnalyzer:
    def test_detector_inherits_base_interface(self):
        detector = ComputerVisionDefectDetector()
        assert isinstance(detector, BaseDefectDetector)

    def test_analyze_clean_image_returns_list(self, sample_clean_image):
        detector = ComputerVisionDefectDetector()
        findings = detector.detect_anomalies(sample_clean_image, photo_type='OVERALL')
        assert isinstance(findings, list)

    def test_missing_image_raises_file_not_found(self):
        detector = ComputerVisionDefectDetector()
        with pytest.raises(FileNotFoundError):
            detector.detect_anomalies("ruta_inexistente_12345.jpg")

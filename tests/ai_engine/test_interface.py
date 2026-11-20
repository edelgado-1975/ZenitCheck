"""
Pruebas de reemplazabilidad de la interfaz del motor de IA.
"""

from ai_engine.detector import BaseDefectDetector, MockDefectDetector


class CustomCompanyDetector(BaseDefectDetector):
    """Demuestra que cualquier clase externa que implemente BaseDefectDetector es compatible."""
    def detect_anomalies(self, image_path, photo_type='OVERALL'):
        return [{
            'defect_type': 'WEAR_ABRASION',
            'severity': 'MINOR',
            'confidence': 0.40,
            'box_x': 0.1,
            'box_y': 0.1,
            'box_width': 0.5,
            'box_height': 0.5,
            'description': 'Detector externo personalizado'
        }]


class TestInterfaceReplaceability:
    def test_custom_detector_can_be_used_transparently(self):
        detector = CustomCompanyDetector()
        res = detector.detect_anomalies("any_path.jpg")
        assert len(res) == 1
        assert res[0]['defect_type'] == 'WEAR_ABRASION'
        assert res[0]['confidence'] == 0.40

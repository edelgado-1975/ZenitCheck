"""
Pruebas de niveles de confianza de la IA.
"""

import pytest
from ai_engine.detector import MockDefectDetector


class TestConfidenceScores:
    def test_confidence_values_are_bounded_0_to_1(self):
        mock_findings = [
            {'defect_type': 'STITCH_FAILURE', 'severity': 'CRITICAL', 'confidence': 0.88, 'box_x': 0.1, 'box_y': 0.1, 'box_width': 0.2, 'box_height': 0.2},
            {'defect_type': 'DISCOLORATION', 'severity': 'MINOR', 'confidence': 0.35, 'box_x': 0.1, 'box_y': 0.1, 'box_width': 0.2, 'box_height': 0.2},
        ]
        detector = MockDefectDetector(mock_findings)
        results = detector.detect_anomalies("dummy.jpg")

        for item in results:
            assert 0.0 <= item['confidence'] <= 1.0

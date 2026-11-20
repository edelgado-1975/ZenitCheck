"""
Pruebas exhaustivas y parametrizadas de umbrales de veredicto.
CRÍTICO: Valida los criterios normativos exactos:
- Verde Esmeralda (#16A34A): 0 hallazgos críticos, certificación vigente.
- Ámbar (#EAB308): Hallazgos menores o certificación vence en ≤ 30 días.
- Rojo Carmesí (#DC2626): Hallazgo crítico ≥ 70% o certificación vencida (bloqueo inmediato).
"""

from datetime import date, timedelta
from types import SimpleNamespace
import pytest
from inspections.verdict import (
    calculate_inspection_verdict,
    HEX_APPROVED, HEX_OBSERVATION, HEX_REJECTED
)


class TestVerdictThresholds:
    @pytest.mark.parametrize(
        "days_to_expiry, findings, expected_verdict, expected_color, expected_lock",
        [
            # 1. Caso perfecto: sin hallazgos y vence en 200 días → VERDE
            (200, [], 'APPROVED', HEX_APPROVED, False),

            # 2. Vence en 31 días (> 30) sin hallazgos → VERDE
            (31, [], 'APPROVED', HEX_APPROVED, False),

            # 3. Próximo a vencer exactamente en 30 días → ÁMBAR
            (30, [], 'OBSERVATION', HEX_OBSERVATION, False),

            # 4. Próximo a vencer en 1 día → ÁMBAR
            (1, [], 'OBSERVATION', HEX_OBSERVATION, False),

            # 5. Vence hoy mismo (0 días) → ÁMBAR
            (0, [], 'OBSERVATION', HEX_OBSERVATION, False),

            # 6. Certificación VENCIDA (-1 día) sin hallazgos → ROJO (Bloqueo inmediato)
            (-1, [], 'REJECTED', HEX_REJECTED, True),

            # 7. Certificación VENCIDA hace 100 días → ROJO
            (-100, [], 'REJECTED', HEX_REJECTED, True),

            # 8. Hallazgo menor con baja confianza (20%) → VERDE
            (200, [{'defect_type': 'DISCOLORATION', 'severity': 'MINOR', 'confidence': 0.20}], 'APPROVED', HEX_APPROVED, False),

            # 9. Hallazgo menor con confianza moderada (45%) → ÁMBAR
            (200, [{'defect_type': 'DISCOLORATION', 'severity': 'MINOR', 'confidence': 0.45}], 'OBSERVATION', HEX_OBSERVATION, False),

            # 10. Hallazgo crítico (Rotura de costura) con confianza ALTA (85%) → ROJO
            (200, [{'defect_type': 'STITCH_FAILURE', 'severity': 'CRITICAL', 'confidence': 0.85}], 'REJECTED', HEX_REJECTED, True),

            # 11. Hallazgo crítico en umbral exacto (70%) → ROJO
            (200, [{'defect_type': 'CUT', 'severity': 'CRITICAL', 'confidence': 0.70}], 'REJECTED', HEX_REJECTED, True),

            # 12. Hallazgo crítico con confianza baja (50% < 70%) → ÁMBAR (No descarta pero observa)
            (200, [{'defect_type': 'STITCH_FAILURE', 'severity': 'CRITICAL', 'confidence': 0.50}], 'OBSERVATION', HEX_OBSERVATION, False),

            # 13. Deformación mecánica de conector con confianza 75% → ROJO
            (200, [{'defect_type': 'DEFORMATION', 'severity': 'CRITICAL', 'confidence': 0.75}], 'REJECTED', HEX_REJECTED, True),

            # 14. Combinación: vence en 15 días (Ámbar) pero tiene corte crítico 80% (Rojo) → Gana el ROJO
            (15, [{'defect_type': 'CUT', 'severity': 'CRITICAL', 'confidence': 0.80}], 'REJECTED', HEX_REJECTED, True),

            # 15. Combinación: equipo vencido (-5 días) pero fotos limpias → ROJO por norma
            (-5, [], 'REJECTED', HEX_REJECTED, True),
        ]
    )
    def test_verdict_matrix(self, days_to_expiry, findings, expected_verdict, expected_color, expected_lock):
        today = date(2026, 6, 1)
        mock_eq = SimpleNamespace(certification_expiry_date=today + timedelta(days=days_to_expiry))

        verdict, color, reasons, is_locked = calculate_inspection_verdict(
            equipment=mock_eq,
            findings=findings,
            today=today
        )

        assert verdict == expected_verdict
        assert color == expected_color
        assert is_locked == expected_lock
        assert len(reasons) > 0

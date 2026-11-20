"""
Pruebas de colores de veredicto oficiales y contrastes.
"""

import pytest
from inspections.verdict import HEX_APPROVED, HEX_OBSERVATION, HEX_REJECTED
from inspections.models import Inspection
from tests.inspections.conftest import InspectionFactory


class TestVerdictColors:
    def test_exact_hex_colors(self):
        assert HEX_APPROVED == '#16A34A'
        assert HEX_OBSERVATION == '#EAB308'
        assert HEX_REJECTED == '#DC2626'

    @pytest.mark.django_db
    def test_inspection_model_verdict_color_property(self):
        ins_approved = InspectionFactory(final_verdict=Inspection.Verdict.APPROVED)
        assert ins_approved.verdict_color == '#16A34A'

        ins_obs = InspectionFactory(final_verdict=Inspection.Verdict.OBSERVATION)
        assert ins_obs.verdict_color == '#EAB308'

        ins_rej = InspectionFactory(final_verdict=Inspection.Verdict.REJECTED)
        assert ins_rej.verdict_color == '#DC2626'

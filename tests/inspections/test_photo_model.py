"""
Pruebas de modelos de foto y relaciones.
"""

import pytest
from inspections.models import InspectionPhoto, DefectFinding
from tests.inspections.conftest import InspectionFactory, InspectionPhotoFactory, create_test_image


@pytest.mark.django_db
class TestInspectionPhotoModel:
    def test_create_inspection_photo(self):
        inspection = InspectionFactory()
        photo = InspectionPhotoFactory(inspection=inspection)
        assert photo.pk is not None
        assert photo.inspection == inspection
        assert photo.ai_status == InspectionPhoto.AIStatus.PENDING

    def test_photo_relation_to_findings(self):
        photo = InspectionPhotoFactory()
        finding = DefectFinding.objects.create(
            photo=photo,
            defect_type=DefectFinding.DefectType.STITCH_FAILURE,
            severity=DefectFinding.Severity.CRITICAL,
            confidence=0.85,
            box_x=0.1,
            box_y=0.1,
            box_width=0.3,
            box_height=0.3,
            description="Costura descosida"
        )
        assert photo.findings.count() == 1
        assert photo.findings.first() == finding

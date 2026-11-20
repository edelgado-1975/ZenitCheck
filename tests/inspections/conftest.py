"""
Fixtures y Factories para tests de inspections y fotos.
"""

from datetime import date, timedelta
import io
from PIL import Image
import factory
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from inspections.models import Inspection, InspectionPhoto, DefectFinding, VerdictAuditLog
from tests.equipment.conftest import EquipmentFactory
from tests.accounts.conftest import UserFactory


def create_test_image(width=400, height=300, color=(100, 150, 200), name='test.jpg'):
    """Genera una imagen en memoria para tests."""
    file_obj = io.BytesIO()
    img = Image.new('RGB', (width, height), color=color)
    img.save(file_obj, format='JPEG')
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type='image/jpeg')


class InspectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inspection

    equipment = factory.SubFactory(EquipmentFactory)
    inspector = factory.SubFactory(UserFactory)
    suggested_verdict = Inspection.Verdict.APPROVED
    final_verdict = Inspection.Verdict.APPROVED
    status = Inspection.Status.DRAFT


class InspectionPhotoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InspectionPhoto

    inspection = factory.SubFactory(InspectionFactory)
    photo_type = InspectionPhoto.PhotoType.SEAMS
    original_filename = "arnes_costura.jpg"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if 'image' not in kwargs:
            kwargs['image'] = create_test_image()
        return super()._create(model_class, *args, **kwargs)


@pytest.fixture
def inspection(db):
    return InspectionFactory()


@pytest.fixture
def inspection_photo(db):
    return InspectionPhotoFactory()

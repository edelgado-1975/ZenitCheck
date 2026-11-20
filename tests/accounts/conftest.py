"""
Fixtures y Factories para tests de accounts.
"""

import factory
import pytest
from accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = "Inspector"
    last_name = "Test"
    role = User.Role.INSPECTOR
    license_number = "LIC-TEST-12345"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Asegura que la contraseña sea hasheada correctamente."""
        password = kwargs.pop('password', 'ValidPass123!')
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user


@pytest.fixture
def inspector_user(db):
    return UserFactory(role=User.Role.INSPECTOR, username="test_inspector")


@pytest.fixture
def supervisor_user(db):
    return UserFactory(role=User.Role.SUPERVISOR, username="test_supervisor")


@pytest.fixture
def admin_user(db):
    return UserFactory(role=User.Role.ADMIN, username="test_admin", is_staff=True)

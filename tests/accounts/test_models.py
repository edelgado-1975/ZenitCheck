"""
Pruebas del modelo User y roles.
"""

import pytest
from accounts.models import User
from tests.accounts.conftest import UserFactory


@pytest.mark.django_db
class TestUserModel:
    def test_create_inspector(self):
        user = UserFactory(role=User.Role.INSPECTOR)
        assert user.is_inspector is True
        assert user.is_supervisor is False
        assert user.is_admin_user is False
        assert "(Inspector Técnico)" in str(user)

    def test_create_supervisor(self):
        user = UserFactory(role=User.Role.SUPERVISOR)
        assert user.is_inspector is False
        assert user.is_supervisor is True
        assert user.is_admin_user is False
        assert "(Supervisor de Seguridad)" in str(user)

    def test_create_admin(self):
        user = UserFactory(role=User.Role.ADMIN)
        assert user.is_inspector is False
        assert user.is_supervisor is False
        assert user.is_admin_user is True
        assert "(Administrador del Sistema)" in str(user)

    def test_superuser_has_all_roles(self):
        super_user = UserFactory(is_superuser=True, role=User.Role.ADMIN)
        assert super_user.is_inspector is True
        assert super_user.is_supervisor is True
        assert super_user.is_admin_user is True

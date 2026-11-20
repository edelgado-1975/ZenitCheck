"""
Pruebas de control de acceso por roles (RBAC).
"""

import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory
from accounts.permissions import (
    inspector_required, supervisor_required, admin_required,
    role_required
)
from tests.accounts.conftest import UserFactory


def dummy_view(request):
    return HttpResponse("Access Granted")


@pytest.mark.django_db
class TestRolePermissions:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_unauthenticated_user_redirected_to_login(self):
        request = self.factory.get('/dummy/')
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        decorated = inspector_required(dummy_view)
        response = decorated(request)
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_inspector_can_access_inspector_view(self, inspector_user):
        request = self.factory.get('/dummy/')
        request.user = inspector_user
        decorated = inspector_required(dummy_view)
        response = decorated(request)
        assert response.status_code == 200
        assert response.content == b"Access Granted"

    def test_inspector_cannot_access_supervisor_view(self, inspector_user):
        request = self.factory.get('/dummy/')
        request.user = inspector_user
        decorated = supervisor_required(dummy_view)
        with pytest.raises(PermissionDenied):
            decorated(request)

    def test_inspector_cannot_access_admin_view(self, inspector_user):
        request = self.factory.get('/dummy/')
        request.user = inspector_user
        decorated = admin_required(dummy_view)
        with pytest.raises(PermissionDenied):
            decorated(request)

    def test_supervisor_can_access_supervisor_view(self, supervisor_user):
        request = self.factory.get('/dummy/')
        request.user = supervisor_user
        decorated = supervisor_required(dummy_view)
        response = decorated(request)
        assert response.status_code == 200

    def test_supervisor_cannot_access_admin_view(self, supervisor_user):
        request = self.factory.get('/dummy/')
        request.user = supervisor_user
        decorated = admin_required(dummy_view)
        with pytest.raises(PermissionDenied):
            decorated(request)

    def test_admin_can_access_all_views(self, admin_user):
        request = self.factory.get('/dummy/')
        request.user = admin_user
        for dec in [inspector_required, supervisor_required, admin_required]:
            res = dec(dummy_view)(request)
            assert res.status_code == 200

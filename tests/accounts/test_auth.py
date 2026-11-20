"""
Pruebas de autenticación (Login / Logout).
"""

import pytest
from django.urls import reverse
from tests.accounts.conftest import UserFactory


@pytest.mark.django_db
class TestAuthViews:
    def test_login_page_renders(self, client):
        url = reverse('accounts:login')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ZenitCheck' in response.content.decode('utf-8')

    def test_login_valid_credentials(self, client):
        UserFactory(username="carlos", password="SecretPassword123!")
        url = reverse('accounts:login')
        response = client.post(url, {
            'username': 'carlos',
            'password': 'SecretPassword123!'
        })
        assert response.status_code == 302
        assert response.url == reverse('inspections:dashboard')

    def test_login_invalid_credentials(self, client):
        UserFactory(username="carlos", password="SecretPassword123!")
        url = reverse('accounts:login')
        response = client.post(url, {
            'username': 'carlos',
            'password': 'WrongPassword!'
        })
        assert response.status_code == 200
        assert 'Usuario o contraseña incorrectos' in response.content.decode('utf-8')

    def test_logout(self, client, inspector_user):
        client.force_login(inspector_user)
        url = reverse('accounts:logout')
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse('accounts:login')

"""
ZenitCheck — Fixtures globales para pytest.
"""
import pytest


@pytest.fixture
def api_client(client):
    """Cliente HTTP de Django para tests."""
    return client

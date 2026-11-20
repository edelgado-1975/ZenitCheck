"""
ZenitCheck — Configuración de TESTING (pytest).
Extiende base.py con SQLite en memoria para velocidad.
"""

from .base import *  # noqa: F401, F403

# ============================================
# Debug ON para tests (mejores mensajes de error)
# ============================================
DEBUG = True

# ============================================
# Base de datos — SQLite en memoria (rápida)
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# ============================================
# Password hashers rápidos para tests
# ============================================
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ============================================
# Email — En memoria
# ============================================
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ============================================
# Media — Directorio temporal para tests
# ============================================
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# ============================================
# IA — Desactivar modelo pesado en tests
# ============================================
AI_USE_MOCK_ENGINE = True

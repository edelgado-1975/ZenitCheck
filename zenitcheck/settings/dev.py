"""
ZenitCheck — Configuración de DESARROLLO.
Extiende base.py con SQLite y herramientas de debug.
"""

from .base import *  # noqa: F401, F403

# ============================================
# Debug
# ============================================
DEBUG = True

# ============================================
# Base de datos — SQLite (desarrollo y campo)
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================
# Email — Console backend para desarrollo
# ============================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================
# Logging
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'ai_engine': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

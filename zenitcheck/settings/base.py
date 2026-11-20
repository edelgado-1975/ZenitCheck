"""
ZenitCheck — Configuración base de Django.
Configuraciones comunes a todos los entornos (dev, prod, test).
"""

from pathlib import Path
from decouple import config, Csv

# ============================================
# Rutas del proyecto
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================
# Seguridad
# ============================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

# ============================================
# Aplicaciones instaladas
# ============================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

PROJECT_APPS = [
    'accounts',
    'equipment',
    'inspections',
    'reports',
    'ai_engine',
    'sync',
]

THIRD_PARTY_APPS = [
    'django_cleanup.apps.CleanupConfig',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

# ============================================
# Middleware
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================
# URLs y WSGI
# ============================================
ROOT_URLCONF = 'zenitcheck.urls'
WSGI_APPLICATION = 'zenitcheck.wsgi.application'

# ============================================
# Templates
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================
# Autenticación
# ============================================
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================
# Internacionalización
# ============================================
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ============================================
# Archivos estáticos y media
# ============================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / config('MEDIA_ROOT', default='media')

# ============================================
# Carga de archivos
# ============================================
MAX_UPLOAD_SIZE_MB = config('MAX_UPLOAD_SIZE_MB', default=10, cast=int)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_BYTES
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_BYTES

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# ============================================
# ID por defecto
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# IA / Visión Artificial
# ============================================
AI_CONFIDENCE_THRESHOLD = config('AI_CONFIDENCE_THRESHOLD', default=0.5, cast=float)
AI_MODEL_PATH = BASE_DIR / config('AI_MODEL_PATH', default='ai_engine/models/weights/')

# ============================================
# Veredictos — Umbrales y colores
# ============================================
VERDICT_COLORS = {
    'APPROVED': '#16A34A',       # Verde Esmeralda — apto para operar
    'OBSERVATION': '#EAB308',    # Ámbar — en observación
    'REJECTED': '#DC2626',       # Rojo Carmesí — fuera de servicio
}

VERDICT_THRESHOLDS = {
    # Hallazgos críticos con confianza >= este valor → RECHAZADO
    'CRITICAL_CONFIDENCE_MIN': 0.70,
    # Confianza media de hallazgos para observación
    'OBSERVATION_CONFIDENCE_MAX': 0.70,
    # Días antes de vencimiento para alertar → OBSERVACIÓN
    'DAYS_BEFORE_EXPIRY_WARNING': 30,
}

# ============================================
# Firma digital de certificados
# ============================================
CERT_KEY_PATH = config('CERT_KEY_PATH', default='certs/private_key.pem')
CERT_CHAIN_PATH = config('CERT_CHAIN_PATH', default='certs/certificate.pem')

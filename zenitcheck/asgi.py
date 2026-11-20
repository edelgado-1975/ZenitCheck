"""ASGI config for ZenitCheck."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zenitcheck.settings.dev')
application = get_asgi_application()

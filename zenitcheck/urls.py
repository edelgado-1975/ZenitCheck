"""
ZenitCheck — Configuración de URLs raíz.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('equipment/', include('equipment.urls')),
    path('inspections/', include('inspections.urls')),
    path('reports/', include('reports.urls')),
    path('sync/', include('sync.urls')),
    # Redirección de raíz al listado o dashboard de inspecciones
    path('', include(('inspections.urls', 'inspections'), namespace='home')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

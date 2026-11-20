from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('certificate/<uuid:inspection_id>/pdf/', views.download_certificate_pdf, name='download_pdf'),
    path('certificate/<uuid:inspection_id>/', views.certificate_view, name='certificate_detail'),
]

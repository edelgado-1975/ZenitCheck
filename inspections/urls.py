from django.urls import path
from . import views

app_name = 'inspections'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('list/', views.inspection_list_view, name='list'),
    path('new/', views.inspection_create_view, name='create'),
    path('<uuid:inspection_id>/', views.inspection_detail_view, name='detail'),
    path('<uuid:inspection_id>/analyze/', views.trigger_ai_analysis_view, name='analyze_ai'),
    path('equipment/<str:serial_number>/history/', views.equipment_history_view, name='equipment_history'),
    path('alerts/', views.alerts_view, name='alerts'),
]

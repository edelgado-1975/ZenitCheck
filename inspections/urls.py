from django.urls import path
from . import views

app_name = 'inspections'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('list/', views.inspection_list_view, name='list'),
]

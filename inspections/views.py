"""
Vistas principales de Inspecciones y Dashboard.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from equipment.models import Equipment


@login_required
def dashboard_view(request):
    """Dashboard general con métricas de inspección y estado de equipos."""
    equipments = Equipment.objects.all()
    total_equipments = equipments.count()
    operational = equipments.filter(status=Equipment.Status.OPERATIONAL).count()
    observation = equipments.filter(status=Equipment.Status.OBSERVATION).count()
    out_of_service = equipments.filter(status=Equipment.Status.OUT_OF_SERVICE).count()

    context = {
        'total_equipments': total_equipments,
        'operational': operational,
        'observation': observation,
        'out_of_service': out_of_service,
        'recent_equipments': equipments[:6],
    }
    return render(request, 'inspections/dashboard.html', context)


@login_required
def inspection_list_view(request):
    return render(request, 'inspections/inspection_list.html', {})

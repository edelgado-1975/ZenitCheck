from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Equipment


@login_required
def equipment_list_view(request):
    equipments = Equipment.objects.select_related('brand', 'equipment_type').all()
    return render(request, 'equipment/equipment_list.html', {'equipments': equipments})

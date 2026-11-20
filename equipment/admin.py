from django.contrib import admin
from .models import Brand, EquipmentType, Equipment, Accessory


class AccessoryInline(admin.TabularInline):
    model = Accessory
    extra = 1
    fields = ('name', 'brand', 'serial_number', 'is_critical', 'notes')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'country', 'verification_status', 'is_active', 'updated_at')
    list_filter = ('origin', 'verification_status', 'is_active')
    search_fields = ('name', 'country', 'verification_notes')
    ordering = ('name',)


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'standard_international', 'standard_us', 'inspection_interval_months', 'max_lifespan_years')
    search_fields = ('code', 'name', 'standard_international', 'standard_us')
    ordering = ('name',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'brand', 'model_name', 'equipment_type',
        'manufacturing_date', 'certification_expiry_date', 'status', 'client_name'
    )
    list_filter = ('status', 'brand', 'equipment_type', 'certification_expiry_date')
    search_fields = ('serial_number', 'model_name', 'client_name', 'location_assigned')
    inlines = [AccessoryInline]
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'certification_expiry_date'


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment', 'brand', 'serial_number', 'is_critical')
    list_filter = ('is_critical', 'brand')
    search_fields = ('name', 'serial_number', 'equipment__serial_number')

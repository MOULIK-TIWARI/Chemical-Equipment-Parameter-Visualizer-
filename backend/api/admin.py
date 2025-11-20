from django.contrib import admin
from .models import Dataset, EquipmentRecord


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'uploaded_by', 'uploaded_at', 'total_records']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['name']
    readonly_fields = ['uploaded_at']


@admin.register(EquipmentRecord)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'dataset', 'flowrate', 'pressure', 'temperature']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['equipment_name', 'equipment_type']

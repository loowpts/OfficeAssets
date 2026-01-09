from django.contrib import admin
from apps.assets.models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'inventory_number',
        'product',
        'serial_number',
        'status',
        'current_location',
        'created_at'
    ]
    list_filter = ['status', 'product', 'current_location', 'created_at']
    search_fields = ['inventory_number', 'serial_number', 'product__name']
    readonly_fields = ['created_at', 'updated_at']

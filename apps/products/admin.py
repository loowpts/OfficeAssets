from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category',
        'unit', 'is_consumable',
        'min_stock', 'created_at'
    ]
    list_filter = ['category', 'is_consumable', 'unit', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'sku', 'category', 'unit')
        }),
        ('Характеристики', {
            'fields': ('is_consumable', 'min_stock', 'description')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes':('collapse')
        })
    )

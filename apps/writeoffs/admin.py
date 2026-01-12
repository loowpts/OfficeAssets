from django.contrib import admin
from .models import WriteOff

@admin.register(WriteOff)
class WriteoffAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_item', 'quantity',
        'location', 'date', 'reason_short'
    ]
    list_filter = ['date', 'location']
    search_fields = [
        'reason', 'product__name',
        'inventory_item__inventory_number'
    ]
    readonly_fields = ['date', 'created_at', 'updated_at']

    def get_item(self, obj):
        """Возвращает название списанного объекта"""
        if obj.product:
            return f'{obj.product.name} x{obj.quantity}'
        return f'{obj.inventory_item.inventory_number}'
    get_item.short_description = 'Списанный объект'

    def reason_short(self, obj):
        """Возвращает первые 50 символов причины"""
        if len(obj.reason) > 50:
            return f'{obj.reason[:50]}...'
        return obj.reason
    reason_short.short_description = 'Причина'

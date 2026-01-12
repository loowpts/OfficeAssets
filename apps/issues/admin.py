from django.contrib import admin
from .models import Issuance


@admin.register(Issuance)
class IssuanceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'inventory_item',
        'recipient',
        'issue_date',
        'return_date',
        'is_returned_display'
    ]
    list_filter = ['issue_date', 'return_date']
    search_fields = [
        'recipient',
        'inventory_item__inventory_number',
        'inventory_item__product__name'
    ]
    readonly_fields = ['issue_date', 'created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('inventory_item', 'recipient')
        }),
        ('Даты', {
            'fields': ('issue_date', 'return_date', 'created_at', 'updated_at')
        }),
        ('Комментарии', {
            'fields': ('issue_comment', 'return_comment')
        }),
    )

    def is_returned_display(self, obj):
        """Отображение статуса возврата"""
        return obj.is_returned
    is_returned_display.boolean = True
    is_returned_display.short_description = 'Возвращена'

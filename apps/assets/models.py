from django.db import models
from django.core.exceptions import ValidationError

class Asset(models.Model):
    
    class StatusChoices(models.TextChoices):
        IN_STOCK = 'in_stock', 'На складе'
        ISSUED = 'issued', 'Выдано'
        IN_REPAIR = 'in_repair', 'В ремонте'
        WRITTEN_OFF = 'written_off', 'Списано'
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='assets'
    )
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    inventory_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_STOCK
    )
    current_location = models.ForeignKey(
        'references.Location',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assets'
        verbose_name = 'Товар на складе'
        verbose_name_plural = 'Товары на складе'
        
    def clean(self):
        if self.product.is_consumable:
            raise ValidationError(
                'Расходные материалы не могут иметь инвентарные единицы'
            )
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'({self.product}) - {self.serial_number} - {self.status}: {self.current_location}'

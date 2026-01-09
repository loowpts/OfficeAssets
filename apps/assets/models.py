from django.db import models
from django.core.exceptions import ValidationError

class Asset(models.Model):
    
    class StatusChoices(models.TextChoices):
        IN_STOCK = 'in_stock', 'В наличии'
        ISSUED = 'issued', 'Выдана'
        MAINTENANCE = 'maintenance', 'На обслуживании'
        WRITTEN_OFF = 'written_off', 'Списана'

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='assets'
    )
    
    serial_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    inventory_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )
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
        indexes = [
            models.Index(fields=['inventory_number']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['status'])
        ]
        
    def clean(self):
        if self.product and self.product.is_consumable:
           raise ValidationError(
                'Asset можно создать только для техники (is_consumable=False). '
                'Для расходных материалов используйте Stock.'
            )
        
        if not self.inventory_number or not self.inventory_number.strip():
            raise ValidationError('Инвентарный номер обязателен')         
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        return self.status == self.StatusChoices.IN_STOCK
    
    def mark_as_issued(self):
        if not self.is_available:
            raise ValidationError(
                f'Инвентарная единица: {self.inventory_number} недоступна для выдачи.'
                f'Текущий статус: {self.get_status_display()}'
            )
        self.status = self.StatusChoices.ISSUED
        self.save()
        
    def mark_as_returned(self):
        if self.status != self.StatusChoices.ISSUED:
            raise ValidationError(
                f'Невозможно вернуть единицу со статусом: {self.get_status_display()}'
            )
        self.status = self.StatusChoices.IN_STOCK
        self.save()
    
    def mark_as_written(self):
        self.status = self.StatusChoices.WRITTEN_OFF
        self.save()
        
    def __str__(self):
        return f'({self.product}) - {self.serial_number} - {self.status}: {self.current_location}'

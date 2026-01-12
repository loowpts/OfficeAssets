from django.db import models
from django.core.exceptions import ValidationError


class WriteOff(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='writeoffs'
    )
    inventory_item = models.ForeignKey(
        'assets.Asset',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='writeoffs'
    )
    quantity = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(
        'references.Location',
        on_delete=models.PROTECT,
        related_name='writeoffs'
    )
    reason = models.TextField(verbose_name='Причина списания')
    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Списание'
        verbose_name_plural = 'Списания'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['product']),
            models.Index(fields=['inventory_item'])
        ]
        
    def __str__(self):
        if self.inventory_item:
            return f"Списание: {self.inventory_item.inventory_number} ({self.date.strftime('%Y-%m-%d %H:%M')})"
        elif self.product:
            return f"Списание: {self.product.name} x{self.quantity} ({self.date.strftime('%Y-%m-%d %H:%M')})"
        return f"Списание #{self.id}"

    def clean(self):
        # Проверка: должен быть указан либо product, либо inventory_item
        if not self.product and not self.inventory_item:
            raise ValidationError(
                'Должен быть указан либо товар (product), либо техника (inventory_item)'
            )

        if self.product and self.inventory_item:
            raise ValidationError(
                'Нельзя указывать одновременно и товар, и технику. Укажите что-то одно.'
            )

        # Валидация для расходников (product)
        if self.product:
            if not self.product.is_consumable:
                raise ValidationError(
                    f'Товар "{self.product.name}" не является расходником (is_consumable=False). '
                    'Для техники используйте поле inventory_item.'
                )
            if not self.quantity or self.quantity <= 0:
                raise ValidationError(
                    'Для расходников должно быть указано количество (quantity > 0)'
                )

        # Валидация для техники (inventory_item)
        if self.inventory_item:
            if self.inventory_item.product.is_consumable:
                raise ValidationError(
                    f'Актив "{self.inventory_item.inventory_number}" является расходником. '
                    'Для расходников используйте поле product.'
                )
            if self.quantity is not None:
                raise ValidationError(
                    'Для техники поле quantity должно быть пустым'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
            
        

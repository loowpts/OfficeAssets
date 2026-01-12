from django.db import models
from django.core.exceptions import ValidationError


class Stock(models.Model):
    """
    Остатки расходных материалов на складе.
    ВАЖНО: Только для продуктов с is_consumable=True
    """
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='stock_balances'
    )
    location = models.ForeignKey(
        'references.Location',
        on_delete=models.PROTECT,
        related_name='stock_balances'
    )
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'location')
        db_table = 'stock'
        verbose_name = 'Остаток'
        verbose_name_plural = 'Остатки'
        indexes = [
            models.Index(fields=['product', 'location']),
        ]

    def clean(self):
        if self.product and not self.product.is_consumable:
            raise ValidationError(
                'StockBalance может быть создан только для расходных материалов (is_consumable=True)'
            )

        if self.quantity < 0:
            raise ValidationError('Количество не может быть отрицательным')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_low_stock(self):
        """Проверка низкого остатка"""
        return self.quantity < self.product.min_stock
    
    def __str__(self):
        return f'{self.product.name} - {self.location.name}: {self.quantity}'


class StockOperations(models.Model):
    """
    История складских операций.
    ВАЖНО: Записи immutable - нельзя изменять после создания.
    """

    class OperationChoices(models.TextChoices):
        RECEIPT = 'receipt', 'Приход'
        EXPENSE = 'expense', 'Расход'
        TRANSFER = 'transfer', 'Перемещение'
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='operations'
    )

    operation_type = models.CharField(
        max_length=50,
        choices=OperationChoices.choices,
    )
    
    quantity = models.IntegerField()
    to_location = models.ForeignKey(
        'references.Location',
        on_delete=models.PROTECT,
        related_name='incoming_stock_operations',
        null=True,
        blank=True
    )
    
    from_location = models.ForeignKey(
        'references.Location',
        on_delete=models.PROTECT,
        related_name='outgoing_stock_operations',
        null=True,
        blank=True
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['product', 'timestamp']),
            models.Index(fields=['operation_type', 'timestamp']),
        ]
    
    def clean(self):
        """Валидация операции"""
        # Количество должно быть положительным
        if self.quantity <= 0:
            raise ValidationError('Количество должно быть больше 0')

        # Только для расходников
        if self.product and not self.product.is_consumable:
            raise ValidationError('StockOperations только для расходных материалов')

        # Приход: нужен to_location
        if self.operation_type == self.OperationChoices.RECEIPT:
            if not self.to_location:
                raise ValidationError('Для прихода необходимо указать локацию назначения')

        # Расход: нужен from_location
        elif self.operation_type == self.OperationChoices.EXPENSE:
            if not self.from_location:
                raise ValidationError('Для расхода необходимо указать локацию отправления')

        # Перемещение: нужны оба
        elif self.operation_type == self.OperationChoices.TRANSFER:
            if not self.from_location or not self.to_location:
                raise ValidationError('Для перемещения необходимы обе локации')
            if self.from_location == self.to_location:
                raise ValidationError('Локации отправления и назначения должны различаться')

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # Запрет на изменение существующих записей
        if self.pk is not None and not force_insert:
            raise ValidationError('Операции нельзя изменять после создания')

        self.full_clean()
        super().save(force_insert=force_insert, force_update=force_update, *args, **kwargs)

    def __str__(self):
        return f"{self.get_operation_type_display()} - {self.product.name} ({self.quantity})"

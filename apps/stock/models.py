from django.db import models
from django.core.exceptions import ValidationError


class Stock(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    location = models.ForeignKey(
        'references.Location',
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'location')
        db_table = 'stock'
        verbose_name = 'Остаток'
        verbose_name_plural = 'Остатки'

    def clean(self):
        if not self.product.is_consumable:
            raise ValidationError('StockBalance только для расходных материалов')
        if self.quantity < 0:
            raise ValidationError('Количество не может быть отрицательным')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} - {self.location.name}: {self.quantity}'


class StockOperations(models.Model):
    
    class OperationChoices(models.TextChoices):
        RECEIPT = 'receipt', 'Приход'
        EXPENSE = 'expense', 'Расход'
        TRANSFER = 'transfer', 'Перемещение'
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='stock_operations'
    )
    
    inventory_item = models.ForeignKey(
        'assets.Asset',
        on_delete=models.PROTECT,
        related_name='stock_operations',
        blank=True,
        null=True
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
    
    def clean(self):
        if self.quantity <= 0:
            raise ValidationError('Количество должно быть больше 0')

        if self.operation_type == self.OperationChoices.RECEIPT:
            if self.from_location:
                raise ValidationError('При приходе не указывается склад-источник')
            if not self.to_location:
                raise ValidationError('При приходе нужен склад-получатель')

        if self.operation_type == self.OperationChoices.EXPENSE:
            if not self.from_location:
                raise ValidationError('При расходе обязателен склад-источник')
            if self.to_location:
                raise ValidationError('При расходе склад-получатель не указывается')

        if self.operation_type == self.OperationChoices.TRANSFER:
            if not self.from_location or not self.to_location:
                raise ValidationError('Для перемещения нужны оба склада')
            if self.from_location == self.to_location:
                raise ValidationError('Склады должны отличаться')

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('Операции со складом нельзя изменять')
        self.full_clean()
        super().save(*args, **kwargs)

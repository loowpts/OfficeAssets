from django.db import models
from apps.references.models import Category


class Product(models.Model):
    name = models.CharField(max_length=250)
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    
    sku = models.CharField(
        max_length=100,
        unique=True
    )
    
    is_consumable = models.BooleanField(
        default=False,
        verbose_name='Расходный материал'
    )
    
    unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения'
    )
    
    min_stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Минимальный остаток'
    )
    
    description = models.TextField(
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.sku})'

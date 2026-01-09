from django.db import models
from apps.references.models import Category
from .validators import (
    validate_sku_format,
    validate_product_name,
    validate_min_stock
)

class Product(models.Model):
    name = models.CharField(
        max_length=250,
        validators=[validate_product_name]
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_sku_format]
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
        verbose_name='Минимальный остаток',
        validators=[validate_min_stock]
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
        
    def is_low_stock(self, current_quantity):
        return current_quantity < self.min_stock

    def __str__(self):
        return f'{self.name} ({self.sku})'

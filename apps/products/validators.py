from django.core.exceptions import ValidationError
import re


def validate_sku_format(value):
    if not re.match(r'^[A-Z0-9-]+$', value):
        raise ValidationError(
            'SKU должен содержать только заглавные буквы, цифры и дефисы'
        )

def validate_min_stock(value):
    if value < 0:
        raise ValidationError(
            'Минимальный остаток не может быть отрицательным'
        )

def validate_product_name(value):
    if len(value.strip()) < 3:
        raise ValidationError(
            'Название продукта должно содержать минимум 3 символа'
        )
    

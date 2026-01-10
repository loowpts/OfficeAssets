import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from typing import Dict, Any, Optional

from .models import Stock, StockOperations
from apps.products.models import Product
from apps.references.models import Location


logger = logging.getLogger(__name__)


class StockService:
    
    @staticmethod
    @transaction.atomic
    def create_receipt(product: Product, location: Location, quantity: int, comment: str):
        
        if not product.is_consumable:
            raise ValidationError(
                f'Операция прихода возможна только для расходных материалов. '
                f'Продукт "{product.name}" не является расходником.'
            )
        
        operation = StockOperations.objects.create(
            product=product,
            operation_type=StockOperations.OperationChoices.RECEIPT,
            quantity=quantity,
            to_location=location,
            comment=comment
        )
        
        stock, created = Stock.objects.get_or_create(
            product=product,
            location=location,
            defaults={'quantity': 0}
        )
        
        stock.quantity += quantity
        
        stock.save()
        
        logger.info(
            f'Приход: {product.name} ({product.sku}) - {quantity} {product.unit} '
            f'на склад {location.name}. Новый остаток: {stock.quantity}. '
            f'Операция ID: {operation.id}'
        )
        
        return operation
        

        
                
        

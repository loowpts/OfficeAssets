import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from typing import Dict, Any, Optional

from .models import WriteOff
from apps.assets.models import Asset
from apps.products.models import Product
from apps.stock.models import Stock
from apps.references.models import Location
from apps.core.exceptions import InsufficientStockError


logger = logging.getLogger(__name__)


class WriteOffService:
    
    @staticmethod
    @transaction.atomic
    def create_writeoff_consumable(product: Product, location: Location, quantity: int, reason: str=''):
        if not product.is_consumable:
            raise ValidationError(
                f'Товар "{product.name}" не является расходником (is_consumable=False). '
                'Для списания техники используйте create_writeoff_asset()'
            )
        
        try:
            stock = Stock.objects.get(
                product=product,
                location=location
            )
        except Stock.DoesNotExist:
            raise InsufficientStockError(
                f'Товар "{product.name}" отсутствует в локации "{location}". '
                f'Доступное количество: 0'
            )
        
        if stock.quantity < quantity:
            raise InsufficientStockError(
                f'Недостаточное количество товара "{product.name}" в локации "{location}". '
                f'Доступно: {stock.quantity}, запрошено: {quantity}'
            )
            
        write_off = WriteOff.objects.create(
            product=product,
            location=location,
            quantity=quantity,
            reason=reason
        )
        
        stock.quantity -= quantity
        stock.save()

        logger.info(
            f'Списан расходник: {product.name} x{quantity} '
            f'со склада {location.name}. ID списания: {write_off.id}'
        )

        return write_off
    
    @staticmethod
    @transaction.atomic
    def create_writeoff_asset(inventory_item: Asset, reason: str=''):
        if inventory_item.product.is_consumable:
            raise ValidationError(
                f'Актив "{inventory_item.inventory_number}" является расходником. '
                'Для списания расходников используйте create_writeoff_consumable()'
            )

        write_off = WriteOff.objects.create(
            inventory_item=inventory_item,
            location=inventory_item.current_location,
            reason=reason
        )

        inventory_item.mark_as_written()

        logger.info(
            f'Списана техника: {inventory_item.inventory_number} '
            f'({inventory_item.product.name}). ID списания: {write_off.id}'
        )

        return write_off
    
    @staticmethod
    def get_writeoffs_by_date_range(start_date, end_date):
        return WriteOff.objects.filter(
            date__range=(start_date, end_date)
        ).select_related('product', 'inventory_item', 'location')
    
            

import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from typing import Dict, Any, Optional

from .models import Stock, StockOperations
from apps.products.models import Product
from apps.references.models import Location
from django.db.models import F


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
        


    @staticmethod
    @transaction.atomic
    def create_expense(product: Product, location: Location, quantity: int, comment: str):
        if not product.is_consumable:
            raise ValidationError(
                f'Операция расхода возможна только для расходных материалов. '
                f'Продукт "{product.name}" не является расходником.'
            )
        
        try:
            stock = Stock.objects.get(
                product=product,
                location=location
            )
        except Stock.DoesNotExist:
            raise ValidationError(
                f'Товар "{product.name}" отсутствует в локации "{location}". '
                f'Доступное количество: 0'
            )
        
        if stock.quantity < quantity:
            raise ValidationError(
                f'Недостаточное количество товара "{product.name}" в локации "{location}". '
                f'Доступно: {stock.quantity}, запрошено: {quantity}'
            )
        
        operation = StockOperations.objects.create(
            product=product,
            operation_type=StockOperations.OperationChoices.EXPENSE,
            quantity=quantity,
            from_location=location,
            comment=comment
        )
        
        stock.quantity -= quantity
        
        stock.save(update_fields=['quantity'])
        
        logger.info(
            f'Expense operation created: {quantity} units of "{product.name}" '
            f'from location "{location}". '
            f'Remaining stock: {stock.quantity}. '
            f'Operation ID: {operation.id}'
        )
        
        return operation
        
    @staticmethod
    @transaction.atomic
    def create_transfer(
        product: Product,
        from_location: Location,
        to_location: Location,
        quantity: int,
        comment: str) -> StockOperations:
        
        if not product.is_consumable:
            raise ValidationError(
                f'Операция прихода возможна только для расходных материалов. '
                f'Продукт "{product.name}" не является расходником.'
            )
        
        if from_location == to_location:
            raise ValidationError('Локации не должны совпадать при перемещении')
        


        try:
            from_stock = Stock.objects.get(
                product=product,
                location=from_location
            )
        except Stock.DoesNotExist:
            raise ValidationError(
                f'Товар "{product.name}" отсутствует в локации "{from_location}"'
            )
            
        if from_stock.quantity < quantity:
            raise ValidationError(
                f'Недостаточное количество товара. '
                f'Доступно: {from_stock.quantity}, запрошено: {quantity}'
            )
            
        operation = StockOperations.objects.create(
            product=product,
            operation_type=StockOperations.OperationChoices.TRANSFER,
            quantity=quantity,
            from_location=from_location,
            to_location=to_location,
            comment=comment
        )
        
        from_stock.quantity -= quantity
        from_stock.save()
        
        to_stock, created = Stock.objects.get_or_create(
            product=product,
            location=to_location,
            defaults={'quantity': 0}
        )
        
        to_stock.quantity += quantity
        
        to_stock.save()
        
        logger.info(
            f'Transfer created: {quantity} units of {product.name} '
            f'from {from_location} to {to_location}. Operation ID: {operation.id}'
        )
        
        return operation
        
    @staticmethod
    def get_current_stock(product: Product, location: Location) -> int:
        try:
            stock = Stock.objects.get(
                product=product,
                location=location
            )
            return stock.quantity
        except Stock.DoesNotExist:
            return 0


    @staticmethod
    def get_low_stock_items():
        return Stock.objects.filter(
            quantity__lt=F('product__min_stock')
        ).select_related('product', 'location')
        


            
                
           


        


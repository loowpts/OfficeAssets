import pytest
from django.core.exceptions import ValidationError
from apps.stock.services import StockService
from apps.stock.models import Stock, StockOperations
from apps.products.models import Product
from apps.references.models import Category, Location


@pytest.mark.django_db
class TestStockService:

    def test_create_receipt_success(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Картридж HP',
            category=category,
            sku='HP-CART-001',
            is_consumable=True,
            unit='шт',
            min_stock=10
        )

        operation = StockService.create_receipt(
            product=product,
            location=location,
            quantity=50,
            comment='Поступление со склада поставщика'
        )

        assert operation is not None
        assert operation.operation_type == StockOperations.OperationChoices.RECEIPT
        assert operation.quantity == 50
        assert operation.to_location == location

        stock = Stock.objects.get(product=product, location=location)
        assert stock.quantity == 50

    def test_create_receipt_non_consumable_product(self):
        category = Category.objects.create(name='Техника')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Принтер HP',
            category=category,
            sku='HP-PRINTER-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )

        with pytest.raises(ValidationError) as excinfo:
            StockService.create_receipt(
                product=product,
                location=location,
                quantity=5,
                comment='Тестовый приход'
            )

        assert 'расходных материалов' in str(excinfo.value)

    def test_create_receipt_updates_existing_stock(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Картридж HP',
            category=category,
            sku='HP-CART-001',
            is_consumable=True,
            unit='шт',
            min_stock=10
        )

        Stock.objects.create(
            product=product,
            location=location,
            quantity=30
        )

        StockService.create_receipt(
            product=product,
            location=location,
            quantity=20,
            comment='Дополнительный приход'
        )

        stock = Stock.objects.get(product=product, location=location)
        assert stock.quantity == 50

    def test_create_receipt_creates_operation_record(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Картридж HP',
            category=category,
            sku='HP-CART-001',
            is_consumable=True,
            unit='шт',
            min_stock=10
        )

        operation = StockService.create_receipt(
            product=product,
            location=location,
            quantity=100,
            comment='Большая поставка'
        )

        assert StockOperations.objects.filter(id=operation.id).exists()
        assert operation.comment == 'Большая поставка'
        assert operation.product == product

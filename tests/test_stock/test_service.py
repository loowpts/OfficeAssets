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

    def test_create_expense_success(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Бумага A4',
            category=category,
            sku='PAPER-A4-001',
            is_consumable=True,
            unit='пачка',
            min_stock=5
        )

        # Создаем остаток на складе
        Stock.objects.create(
            product=product,
            location=location,
            quantity=100
        )

        operation = StockService.create_expense(
            product=product,
            location=location,
            quantity=30,
            comment='Выдано в отдел продаж'
        )

        assert operation is not None
        assert operation.operation_type == StockOperations.OperationChoices.EXPENSE
        assert operation.quantity == 30
        assert operation.from_location == location

        stock = Stock.objects.get(product=product, location=location)
        assert stock.quantity == 70

    def test_create_expense_insufficient_stock(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Бумага A4',
            category=category,
            sku='PAPER-A4-001',
            is_consumable=True,
            unit='пачка',
            min_stock=5
        )

        # Создаем остаток всего 10 штук
        Stock.objects.create(
            product=product,
            location=location,
            quantity=10
        )

        # Пытаемся списать 20
        with pytest.raises(ValidationError) as excinfo:
            StockService.create_expense(
                product=product,
                location=location,
                quantity=20,
                comment='Попытка списать больше чем есть'
            )

        assert 'Недостаточное количество' in str(excinfo.value)
        assert 'Доступно: 10' in str(excinfo.value)

        # Проверяем что остаток не изменился
        stock = Stock.objects.get(product=product, location=location)
        assert stock.quantity == 10

    def test_create_expense_no_stock(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Бумага A4',
            category=category,
            sku='PAPER-A4-001',
            is_consumable=True,
            unit='пачка',
            min_stock=5
        )

        # НЕ создаем остаток на складе
        with pytest.raises(ValidationError) as excinfo:
            StockService.create_expense(
                product=product,
                location=location,
                quantity=5,
                comment='Попытка списать с пустого склада'
            )

        assert 'отсутствует в локации' in str(excinfo.value)

    def test_create_expense_non_consumable_product(self):
        category = Category.objects.create(name='Техника')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Ноутбук Dell',
            category=category,
            sku='DELL-LAPTOP-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )

        with pytest.raises(ValidationError) as excinfo:
            StockService.create_expense(
                product=product,
                location=location,
                quantity=1,
                comment='Попытка расхода техники'
            )

        assert 'расходных материалов' in str(excinfo.value)

    def test_create_transfer_success(self):
        category = Category.objects.create(name='Расходники')
        location1 = Location.objects.create(name='Склад 1')
        location2 = Location.objects.create(name='Склад 2')
        product = Product.objects.create(
            name='Картридж',
            category=category,
            sku='CART-001',
            is_consumable=True,
            unit='шт',
            min_stock=5
        )

        # Создаем остаток на первом складе
        Stock.objects.create(
            product=product,
            location=location1,
            quantity=50
        )

        operation = StockService.create_transfer(
            product=product,
            from_location=location1,
            to_location=location2,
            quantity=20,
            comment='Перемещение между складами'
        )

        assert operation is not None
        assert operation.operation_type == StockOperations.OperationChoices.TRANSFER
        assert operation.quantity == 20
        assert operation.from_location == location1
        assert operation.to_location == location2

        # Проверяем остатки
        stock1 = Stock.objects.get(product=product, location=location1)
        assert stock1.quantity == 30

        stock2 = Stock.objects.get(product=product, location=location2)
        assert stock2.quantity == 20

    def test_create_transfer_same_location_fails(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Картридж',
            category=category,
            sku='CART-001',
            is_consumable=True,
            unit='шт',
            min_stock=5
        )

        Stock.objects.create(
            product=product,
            location=location,
            quantity=50
        )

        with pytest.raises(ValidationError) as excinfo:
            StockService.create_transfer(
                product=product,
                from_location=location,
                to_location=location,
                quantity=10,
                comment='Попытка переместить в ту же локацию'
            )

        assert 'Локации не должны совпадать' in str(excinfo.value)

    def test_create_transfer_insufficient_stock(self):
        category = Category.objects.create(name='Расходники')
        location1 = Location.objects.create(name='Склад 1')
        location2 = Location.objects.create(name='Склад 2')
        product = Product.objects.create(
            name='Картридж',
            category=category,
            sku='CART-001',
            is_consumable=True,
            unit='шт',
            min_stock=5
        )

        Stock.objects.create(
            product=product,
            location=location1,
            quantity=10
        )

        with pytest.raises(ValidationError) as excinfo:
            StockService.create_transfer(
                product=product,
                from_location=location1,
                to_location=location2,
                quantity=20,
                comment='Попытка переместить больше чем есть'
            )

        assert 'Недостаточное количество' in str(excinfo.value)

    def test_create_transfer_non_consumable_product(self):
        category = Category.objects.create(name='Техника')
        location1 = Location.objects.create(name='Склад 1')
        location2 = Location.objects.create(name='Склад 2')
        product = Product.objects.create(
            name='Монитор',
            category=category,
            sku='MONITOR-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )

        with pytest.raises(ValidationError) as excinfo:
            StockService.create_transfer(
                product=product,
                from_location=location1,
                to_location=location2,
                quantity=1,
                comment='Попытка переместить технику'
            )

        assert 'расходных материалов' in str(excinfo.value)

    def test_get_current_stock_exists(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Бумага',
            category=category,
            sku='PAPER-001',
            is_consumable=True,
            unit='пачка',
            min_stock=5
        )

        Stock.objects.create(
            product=product,
            location=location,
            quantity=75
        )

        current_stock = StockService.get_current_stock(product, location)
        assert current_stock == 75

    def test_get_current_stock_not_exists(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Бумага',
            category=category,
            sku='PAPER-001',
            is_consumable=True,
            unit='пачка',
            min_stock=5
        )

        # Не создаем Stock - метод должен вернуть 0
        current_stock = StockService.get_current_stock(product, location)
        assert current_stock == 0

    def test_get_low_stock_items(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')

        product1 = Product.objects.create(
            name='Бумага A4',
            category=category,
            sku='PAPER-001',
            is_consumable=True,
            unit='пачка',
            min_stock=50
        )

        product2 = Product.objects.create(
            name='Картридж HP',
            category=category,
            sku='CART-001',
            is_consumable=True,
            unit='шт',
            min_stock=10
        )

        product3 = Product.objects.create(
            name='Ручки',
            category=category,
            sku='PEN-001',
            is_consumable=True,
            unit='шт',
            min_stock=20
        )

        # Создаем остатки: product1 - низкий, product2 - достаточный, product3 - низкий
        Stock.objects.create(product=product1, location=location, quantity=30)  # min_stock=50, низкий
        Stock.objects.create(product=product2, location=location, quantity=15)  # min_stock=10, достаточный
        Stock.objects.create(product=product3, location=location, quantity=5)   # min_stock=20, низкий

        low_stock_items = StockService.get_low_stock_items()

        assert low_stock_items.count() == 2
        low_stock_products = [item.product for item in low_stock_items]
        assert product1 in low_stock_products
        assert product3 in low_stock_products
        assert product2 not in low_stock_products

    def test_transaction_rollback_on_error(self):
        category = Category.objects.create(name='Расходники')
        location = Location.objects.create(name='Склад 1')
        product = Product.objects.create(
            name='Бумага',
            category=category,
            sku='PAPER-001',
            is_consumable=True,
            unit='пачка',
            min_stock=5
        )

        Stock.objects.create(
            product=product,
            location=location,
            quantity=10
        )

        initial_operations_count = StockOperations.objects.count()

        # Пытаемся списать больше чем есть - транзакция должна откатиться
        with pytest.raises(ValidationError):
            StockService.create_expense(
                product=product,
                location=location,
                quantity=20,
                comment='Попытка списать слишком много'
            )

        # Проверяем что операция не создалась (транзакция откатилась)
        assert StockOperations.objects.count() == initial_operations_count

        # Проверяем что остаток не изменился
        stock = Stock.objects.get(product=product, location=location)
        assert stock.quantity == 10

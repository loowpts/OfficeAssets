import pytest
from django.core.exceptions import ValidationError
from apps.stock.services import StockService
from apps.stock.models import Stock, StockOperations
from apps.products.models import Product
from apps.references.models import Category, Location


@pytest.mark.django_db
class TestStockSignals:

    def test_low_stock_signal(self, caplog):
        """Проверка что при создании Stock с низким остатком логируется WARNING"""
        # Arrange - подготовка данных
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

        # Act - создаём Stock с количеством меньше минимума
        with caplog.at_level('WARNING', logger='apps.stock.signals'):
            Stock.objects.create(
                product=product,
                location=location,
                quantity=5  # Меньше min_stock=10
            )

        # Assert - проверяем что залогировано предупреждение
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'WARNING'
        assert 'LOW STOCK WARNING' in caplog.text
        assert 'Картридж HP' in caplog.text
        assert 'Склад 1' in caplog.text
        assert 'Остаток: 5' in caplog.text
        assert 'минимум: 10' in caplog.text

    def test_no_warning_for_sufficient_stock(self, caplog):
        """Проверка что при достаточном остатке WARNING не логируется"""
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

        with caplog.at_level('WARNING', logger='apps.stock.signals'):
            Stock.objects.create(
                product=product,
                location=location,
                quantity=15  # Больше min_stock=10
            )

        # Не должно быть WARNING
        assert len(caplog.records) == 0



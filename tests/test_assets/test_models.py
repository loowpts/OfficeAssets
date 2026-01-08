import pytest
from django.core.exceptions import ValidationError

from apps.assets.models import Asset
from apps.references.models import Category
from apps.products.models import Product
from apps.references.models import Location


@pytest.mark.django_db
class TestAssetModel:

    def test_create_inventory_item_for_non_consumable_product(self):
        category = Category.objects.create(name='TestCategory')

        product = Product.objects.create(
            name='Принтер HP',
            category=category,
            sku='HP-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )

        location = Location.objects.create(name='Склад')

        item = Asset(
            product=product,
            serial_number='SN123',
            inventory_number='INV123',
            current_location=location
        )

        item.save()

        assert Asset.objects.count() == 1
        assert item.status == Asset.StatusChoices.IN_STOCK

    def test_cannot_create_inventory_item_for_consumable_product(self):
        category = Category.objects.create(name='TestCategory')

        product = Product.objects.create(
            name='Картридж HP',
            category=category,
            sku='HP-CARTRIDGE',
            is_consumable=True,
            unit='шт',
            min_stock=10
        )

        item = Asset(
            product=product,
            inventory_number='INV999'
        )

        with pytest.raises(ValidationError):
            item.save()

    def test_inventory_number_must_be_unique(self):
        category = Category.objects.create(name='TestCategory')

        product = Product.objects.create(
            name='Монитор',
            category=category,
            sku='MON-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )

        Asset.objects.create(
            product=product,
            inventory_number='INV001'
        )

        duplicate = Asset(
            product=product,
            inventory_number='INV001'
        )

        with pytest.raises(ValidationError):
            duplicate.save()

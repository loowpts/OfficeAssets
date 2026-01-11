import pytest
from apps.references.models import Category, Location
from apps.products.models import Product
from apps.assets.models import Asset
from apps.assets.serializers import AssetCreateUpdateSerializer


@pytest.mark.django_db
class TestAssetsSerializer:

    def test_valid_data(self):
        category = Category.objects.create(name='TestCategory')
        location = Location.objects.create(name='SKLAD')
        product = Product.objects.create(
            name='Принтер HP',
            category=category,
            sku='HP-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )

        data = {
            'product': product.id,
            'serial_number': '332323dsdsffs',
            'inventory_number': '3dsfsaasd',
            'current_location': location.id,
        }

        serializer = AssetCreateUpdateSerializer(data=data)

        assert serializer.is_valid(), serializer.errors

        asset = serializer.save()

        assert Asset.objects.filter(serial_number='332323dsdsffs').exists()
        assert asset.status == Asset.StatusChoices.IN_STOCK

    def test_valid_update(self):
        category = Category.objects.create(name='TestCategory')
        location = Location.objects.create(name='Склад')
        product = Product.objects.create(
            name='Принтер HP',
            category=category,
            sku='HP-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )
        items = Asset.objects.create(
            product=product,
            serial_number='332323dsdsffs',
            inventory_number='3dsfsaasd',
            status=Asset.StatusChoices.IN_STOCK,
            current_location=location,
        )

        update_data = {
            'product': product.id,
            'serial_number': 'New32233',
            'inventory_number': 'NEW3DSFSAASD',
            'current_location': location.id
        }

        serializer = AssetCreateUpdateSerializer(instance=items, data=update_data)

        assert serializer.is_valid(), serializer.errors

        updated_asset = serializer.save()
        assert updated_asset.serial_number == 'New32233'
        assert updated_asset.inventory_number == 'NEW3DSFSAASD'

    def test_validation_check_consumable_product(self):
        category = Category.objects.create(name='TestCategory')
        location = Location.objects.create(name='SKLAD')
        product = Product.objects.create(
            name='Картридж HP',
            category=category,
            sku='HP-001',
            is_consumable=True,
            unit='шт',
            min_stock=1
        )

        data = {
            'product': product.id,
            'serial_number': '332323dsdsffs',
            'inventory_number': '3dsfsaasd',
            'current_location': location.id,
        }

        serializer = AssetCreateUpdateSerializer(data=data)

        assert not serializer.is_valid()
        assert 'product' in serializer.errors

    def test_inventory_number_uppercase_strip(self):
        category = Category.objects.create(name='TestCategory')
        location = Location.objects.create(name='SKLAD')
        product = Product.objects.create(
            name='Принтер HP',
            category=category,
            sku='HP-001',
            is_consumable=False,
            unit='шт',
            min_stock=1
        )

        data = {
            'product': product.id,
            'serial_number': 'SN123',
            'inventory_number': '  inv123  ',
            'current_location': location.id,
        }

        serializer = AssetCreateUpdateSerializer(data=data)

        assert serializer.is_valid(), serializer.errors

        asset = serializer.save()
        assert asset.inventory_number == 'INV123'

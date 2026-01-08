import pytest
from apps.references.models import Category, Location
from apps.products.models import Product
from apps.assets.models import Asset
from apps.assets.serializers import AssetCreateSerializer


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
            'status': Asset.StatusChoices.IN_STOCK,
            'location': location,
        }
        
        serializer = AssetCreateSerializer(data=data)
        
        assert serializer.is_valid(), serializer.errors
        
        serializer.save()
        
        assert Asset.objects.filter(serial_number='332323dsdsffs')
        
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
            'inventory_number': 'New3dsfsaasd',
            'current_location': location.id
        }
        
        serializer = AssetCreateSerializer(instance=items, data=update_data)
        
        assert serializer.is_valid(), serializer.errors
        
    def test_validation_check(self):
        category = Category.objects.create(name='TestCategory')
        location = Location.objects.create(name='SKLAD')
        product = Product.objects.create(
            name='Принтер HP',
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
            'status': Asset.StatusChoices.IN_STOCK,
            'location': location,
        }
        
        serializer = AssetCreateSerializer(data=data)
        
        assert not serializer.is_valid()

           
            

import pytest
from apps.references.models import Category
from apps.products.models import Product
from apps.products.serializers import ProductCreateUpdateSerializer


@pytest.mark.django_db
class TestProductSerializer:
    
    def test_valid_data(self):
        category = Category.objects.create(name='Тест1')

        data = {
            'name': 'Тестовый продукт',
            'category': category.id,
            'sku': 'HP-003-MFP',
            'is_consumable': False,
            'unit': 'шт',
            'min_stock': 5,
            'description': 'Тестовое описание'
        }

        serializer = ProductCreateUpdateSerializer(data=data)

        assert serializer.is_valid(), serializer.errors
        product = serializer.save()

        assert product.name == data['name']
        assert product.unit == data['unit']
        assert product.min_stock == data['min_stock']
        
    def test_valid_update(self):
        category = Category.objects.create(name='Тест1')

        product = Product.objects.create(
            name='Тестовый продукт',
            category=category,
            sku='HP-003-MFP',
            is_consumable=False,
            unit='шт',
            min_stock=10
        )

        product.save()

        update_data = {
            'name': 'Тестовый',
            'category': category.id,
            'sku': 'HP-003-MFP',
            'is_consumable': False,
            'unit': 'шт',
            'min_stock': 15,
        }

        serializer = ProductCreateUpdateSerializer(instance=product, data=update_data)

        assert serializer.is_valid(), serializer.errors

        serializer.save()
        product.refresh_from_db()

        assert product.name == update_data['name']
        assert product.min_stock == update_data['min_stock']
        
    def test_validation_check(self):

        category = Category.objects.create(name='Тест1')

        product = Product.objects.create(
            name='Тестовый продукт',
            category=category,
            sku='HP-003-MFP',
            is_consumable=False,
            unit='шт',
            min_stock=10
        )

        product.save()

        update_data = {
            'name': '',
            'category': category.id,
            'sku': 'HP-003-MFP',
            'is_consumable': False,
            'unit': 'шт',
            'min_stock': 10,
        }

        serializer = ProductCreateUpdateSerializer(instance=product, data=update_data)

        assert not serializer.is_valid(), serializer.errors
        assert product.name == 'Тестовый продукт'    

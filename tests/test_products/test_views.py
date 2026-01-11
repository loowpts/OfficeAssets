import pytest
from rest_framework.test import APIClient

from apps.references.models import Category
from apps.products.models import Product
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestProductView:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Тестовая')

    def test_products_list(self):
        Product.objects.create(
            name='Тестовая1',
            category=self.category,
            sku='HP-003MFP',
            is_consumable=True,
            unit='шт',
            min_stock=5
        )
        Product.objects.create(
            name='Тестовая2',
            category=self.category,
            is_consumable=True,
            sku='HP-004MFP',
            unit='шт',
            min_stock=5
        )
        Product.objects.create(
            name='Тестовая3',
            category=self.category,
            is_consumable=True,
            sku='HP-005MFP',
            unit='шт',
            min_stock=5
        )
        Product.objects.create(
            name='Тестовая4',
            category=self.category,
            is_consumable=True,
            sku='HP-006MFP',
            unit='шт',
            min_stock=5
        )

        response = self.client.get('/api/v1/products/')

        data = response.json()

        assert response.status_code == 200
        assert data['count'] == 4

    def test_product_create(self):
        create_data = {
            'name': 'Новый продукт',
            'category': self.category.id,
            'sku': 'NEW-001',
            'is_consumable': False,
            'unit': 'шт',
            'min_stock': 10,
            'description': 'Описание'
        }

        response = self.client.post('/api/v1/products/', create_data, format='json')

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == create_data['name']
        assert data['sku'] == create_data['sku']

    def test_product_retrieve(self):
        product = Product.objects.create(
            name='Тестовый продукт',
            category=self.category,
            sku='HP-001',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )

        response = self.client.get(f'/api/v1/products/{product.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Тестовый продукт'
        assert data['sku'] == 'HP-001'

    def test_product_update(self):
        product = Product.objects.create(
            name='Старое название',
            category=self.category,
            sku='OLD-001',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )

        update_data = {
            'name': 'Новое название',
            'category': self.category.id,
            'sku': 'OLD-001',
            'is_consumable': False,
            'unit': 'шт',
            'min_stock': 10
        }

        response = self.client.put(f'/api/v1/products/{product.id}/', update_data, format='json')

        assert response.status_code == 200
        product.refresh_from_db()
        assert product.name == 'Новое название'
        assert product.min_stock == 10

    def test_product_partial_update(self):
        product = Product.objects.create(
            name='Продукт',
            category=self.category,
            sku='PROD-001',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )

        update_data = {'min_stock': 20}

        response = self.client.patch(f'/api/v1/products/{product.id}/', update_data, format='json')

        assert response.status_code == 200
        product.refresh_from_db()
        assert product.min_stock == 20
        assert product.name == 'Продукт'

    def test_product_delete(self):
        product = Product.objects.create(
            name='Удаляемый продукт',
            category=self.category,
            sku='DEL-001',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )

        response = self.client.delete(f'/api/v1/products/{product.id}/')

        assert response.status_code == 204
        assert not Product.objects.filter(id=product.id).exists()

    def test_consumables_action(self):
        Product.objects.create(
            name='Расходник 1',
            category=self.category,
            sku='CONS-001',
            is_consumable=True,
            unit='шт',
            min_stock=10
        )
        Product.objects.create(
            name='Техника 1',
            category=self.category,
            sku='TECH-001',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )

        response = self.client.get('/api/v1/products/consumables/')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['is_consumable'] is True

    def test_assets_action(self):
        Product.objects.create(
            name='Расходник 1',
            category=self.category,
            sku='CONS-001',
            is_consumable=True,
            unit='шт',
            min_stock=10
        )
        Product.objects.create(
            name='Техника 1',
            category=self.category,
            sku='TECH-001',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )

        response = self.client.get('/api/v1/products/assets/')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['is_consumable'] is False

    def test_filter_by_category(self):
        category2 = Category.objects.create(name='Категория 2')

        Product.objects.create(
            name='Продукт 1',
            category=self.category,
            sku='PROD-001',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )
        Product.objects.create(
            name='Продукт 2',
            category=category2,
            sku='PROD-002',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )

        response = self.client.get(f'/api/v1/products/?category={self.category.id}')
        data = response.json()

        assert response.status_code == 200
        assert data['count'] == 1

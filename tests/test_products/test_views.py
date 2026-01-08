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

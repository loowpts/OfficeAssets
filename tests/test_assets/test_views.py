import pytest
from rest_framework.test import APIClient

from apps.references.models import Category
from apps.products.models import Product
from apps.assets.models import Asset
from apps.references.models import Location
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAssetView:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Тестовая')
        self.product = Product.objects.create(
            name='Тестовая1',
            category=self.category,
            sku='HP-003MFP',
            is_consumable=False,
            unit='шт',
            min_stock=5
        )
        self.location = Location.objects.create(name='Склад')
        
    def test_assets_list(self):
        item = Asset(
            product=self.product,
            serial_number='SN123',
            inventory_number='INV123',
            current_location=self.location
        )
        item2 = Asset(
            product=self.product,
            serial_number='SN12332',
            inventory_number='INV12311',
            current_location=self.location
        )
        
        item3 = Asset(
            product=self.product,
            serial_number='SN12332',
            inventory_number='INV12323',
            current_location=self.location
        )
        
        item.save()
        item2.save()
        item3.save()
        
        response = self.client.get('/api/v1/assets/')
        
        data = response.json()
        
        assert response.status_code == 200
        assert data['count'] == 3
        
    def test_assets_detail(self):
        item = Asset(
            product=self.product,
            serial_number='SN123',
            inventory_number='INV123',
            current_location=self.location
        )
        
        item.save()
        
        response = self.client.get(f'/api/v1/assets/{item.id}/')
        
        data = response.json()
        
        assert response.status_code == 200
        assert data['serial_number'] == 'SN123'
        assert Asset.objects.filter(inventory_number='INV123').exists()
        
    def tests_assets_update(self):
        item = Asset(
            product=self.product,
            serial_number='SN123',
            inventory_number='INV123',
            current_location=self.location
        )
        
        item.save()

        update_data = {
            "serial_number": "SN999",
            "inventory_number": "INV999"
        }
        
        response = self.client.patch(
            f'/api/v1/assets/{item.id}/',
            data=update_data,
            format='json'
        )
        
        assert response.status_code == 200

        item.refresh_from_db()
        assert item.serial_number == "SN999"
        assert item.inventory_number == "INV999"

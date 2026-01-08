import pytest
from rest_framework.test import APIClient
from apps.references.models import Category, Location
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestCategoryView:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.force_authenticate(user=self.user)
    
    def test_category_list(self):
        Category.objects.create(name='Категория 1')
        Category.objects.create(name='Категория 2')
        Category.objects.create(name='Категория 3')
        Category.objects.create(name='Категория 4')
        Category.objects.create(name='Категория 5')
        Category.objects.create(name='Категория 6')
        
        response = self.client.get('/api/v1/categories/')
        
        data = response.json()
                
        assert response.status_code == 200
        assert data['count'] == 6
        
    def test_update_category(self):
        category = Category.objects.create(name='Name 1')
        
        update_data = {'name': 'Новое название'}
        
        response = self.client.put(f'/api/v1/categories/{category.id}/', update_data, format='json')
        
        data = response.json()
        
        assert response.status_code == 200
        assert data['name'] == update_data['name']
        
        category.refresh_from_db()
        assert category.name == update_data['name']
        
    def test_delete_category(self):
        category = Category.objects.create(name='Name 1')
        
        response = self.client.delete(f'/api/v1/categories/{category.id}/')
        assert response.status_code == 204
        assert not Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db      
class TestLocationView:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.force_authenticate(user=self.user)
    
    def test_locations_list(self):
        Location.objects.create(name='Location 1')
        Location.objects.create(name='Location 2')
        Location.objects.create(name='Location 3')
        Location.objects.create(name='Location 4')
        Location.objects.create(name='Location 5')
        Location.objects.create(name='Location 6')

        response = self.client.get('/api/v1/locations/')

        data = response.json()

        assert response.status_code == 200
        assert data['count'] == 6

    def test_update_location(self):
        location = Location.objects.create(name='Location 1')

        update_location = {'name': 'New New'}

        response = self.client.put(f'/api/v1/locations/{location.id}/', update_location, format='json')

        assert response.status_code == 200
        data = response.json()

        assert data['name'] == update_location['name']

        location.refresh_from_db()
        assert location.name == update_location['name']

    def test_delete_location(self):
        location = Location.objects.create(name='Location 1')

        response = self.client.delete(f'/api/v1/locations/{location.id}/')

        assert response.status_code == 204
        assert not Location.objects.filter(id=location.id).exists()
        

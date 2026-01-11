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

    def test_category_create(self):
        create_data = {'name': 'Новая категория'}

        response = self.client.post('/api/v1/categories/', create_data, format='json')

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == create_data['name']
        assert data['is_active'] is True
        assert 'slug' in data

    def test_category_retrieve(self):
        category = Category.objects.create(name='Тестовая категория')

        response = self.client.get(f'/api/v1/categories/{category.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Тестовая категория'
        assert data['is_active'] is True

    def test_update_category(self):
        category = Category.objects.create(name='Name 1')

        update_data = {'name': 'Новое название', 'is_active': True}

        response = self.client.put(f'/api/v1/categories/{category.id}/', update_data, format='json')

        data = response.json()

        assert response.status_code == 200
        assert data['name'] == update_data['name']

        category.refresh_from_db()
        assert category.name == update_data['name']

    def test_partial_update_category(self):
        category = Category.objects.create(name='Старое название')

        update_data = {'is_active': False}

        response = self.client.patch(f'/api/v1/categories/{category.id}/', update_data, format='json')

        assert response.status_code == 200
        category.refresh_from_db()
        assert category.is_active is False
        assert category.name == 'Старое название'

    def test_delete_category(self):
        category = Category.objects.create(name='Name 1')

        response = self.client.delete(f'/api/v1/categories/{category.id}/')
        assert response.status_code == 204
        assert not Category.objects.filter(id=category.id).exists()

    def test_filter_by_is_active(self):
        Category.objects.create(name='Активная 1', is_active=True)
        Category.objects.create(name='Активная 2', is_active=True)
        Category.objects.create(name='Неактивная', is_active=False)

        response = self.client.get('/api/v1/categories/?is_active=true')
        data = response.json()

        assert response.status_code == 200
        assert data['count'] == 2


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

    def test_location_create(self):
        create_data = {'name': 'Новая локация'}

        response = self.client.post('/api/v1/locations/', create_data, format='json')

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == create_data['name']
        assert data['is_active'] is True

    def test_location_retrieve(self):
        location = Location.objects.create(name='Склад 1')

        response = self.client.get(f'/api/v1/locations/{location.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Склад 1'
        assert data['is_active'] is True

    def test_update_location(self):
        location = Location.objects.create(name='Location 1')

        update_location = {'name': 'New New', 'is_active': True}

        response = self.client.put(f'/api/v1/locations/{location.id}/', update_location, format='json')

        assert response.status_code == 200
        data = response.json()

        assert data['name'] == update_location['name']

        location.refresh_from_db()
        assert location.name == update_location['name']

    def test_partial_update_location(self):
        location = Location.objects.create(name='Старая локация')

        update_data = {'is_active': False}

        response = self.client.patch(f'/api/v1/locations/{location.id}/', update_data, format='json')

        assert response.status_code == 200
        location.refresh_from_db()
        assert location.is_active is False
        assert location.name == 'Старая локация'

    def test_delete_location(self):
        location = Location.objects.create(name='Location 1')

        response = self.client.delete(f'/api/v1/locations/{location.id}/')

        assert response.status_code == 204
        assert not Location.objects.filter(id=location.id).exists()

    def test_filter_by_is_active(self):
        Location.objects.create(name='Активная 1', is_active=True)
        Location.objects.create(name='Активная 2', is_active=True)
        Location.objects.create(name='Неактивная', is_active=False)

        response = self.client.get('/api/v1/locations/?is_active=true')
        data = response.json()

        assert response.status_code == 200
        assert data['count'] == 2

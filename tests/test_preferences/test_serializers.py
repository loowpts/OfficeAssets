import pytest
from slugify import slugify
from apps.references.models import Category, Location
from apps.references.serializers import CategoryCreateUpdateSerializer, LocationCreateUpdateSerializer
from rest_framework.serializers import ValidationError


@pytest.mark.django_db
class TestCategoryCreateUpdateSerializer:
    
    def test_valid_data(self):
        data = {'name': 'Тестовая категория'}
        serializer = CategoryCreateUpdateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        category = serializer.save()
        
        assert isinstance(category, Category)
        assert category.name == data['name']
        assert category.slug == slugify(data['name'])

    def test_valid_data_update(self):
        category = Category.objects.create(name='Исходное имя')

        update_data = {'name': 'Новое имя'}
        serializer = CategoryCreateUpdateSerializer(category, data=update_data)
        assert serializer.is_valid(), serializer.errors

        updated_category = serializer.save()
        assert updated_category.name == update_data['name']
        # При обновлении name, slug должен остаться старым (slug не обновляется автоматически)
        assert updated_category.slug == slugify('Исходное имя')

    def test_validation_check_empty_name(self):
        category = Category.objects.create(name='Исходное имя')

        update_data = {'name': ''}
        serializer = CategoryCreateUpdateSerializer(category, data=update_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

@pytest.mark.django_db
class TestLocationSerializer:

    def test_valid_name(self):
        data = {'name': '211 Кабинет'}
        serializer = LocationCreateUpdateSerializer(data=data)

        assert serializer.is_valid(), serializer.errors

        location = serializer.save()
        assert location.name == '211 Кабинет'

    def test_update_name(self):
        location = Location.objects.create(name='Исходное название')

        update_data = {'name': 'Новое название'}
        serializer = LocationCreateUpdateSerializer(instance=location, data=update_data)

        assert serializer.is_valid(), serializer.errors

        serializer.save()

        assert location.name == 'Новое название'

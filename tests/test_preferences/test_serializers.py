import pytest
from slugify import slugify
from apps.references.models import Category, Location
from apps.references.serializers import CategorySerializer, LocationSerializer
from rest_framework.serializers import ValidationError


@pytest.mark.django_db
class TestCategorySerializer:

    def test_valid_data(self):
        data = {'name': 'Тестовая категория'}
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        category = serializer.save()

        assert isinstance(category, Category)
        assert category.name == data['name']
        assert category.slug == slugify(data['name'])
        assert category.is_active is True

    def test_valid_data_update(self):
        category = Category.objects.create(name='Исходное имя')

        update_data = {'name': 'Новое имя', 'is_active': False}
        serializer = CategorySerializer(category, data=update_data)
        assert serializer.is_valid(), serializer.errors

        updated_category = serializer.save()
        assert updated_category.name == update_data['name']
        assert updated_category.is_active is False
        assert updated_category.slug == slugify('Исходное имя')

    def test_validation_check_empty_name(self):
        category = Category.objects.create(name='Исходное имя')

        update_data = {'name': ''}
        serializer = CategorySerializer(category, data=update_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_validation_short_name(self):
        data = {'name': 'A'}
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_name_strip(self):
        data = {'name': '  Тестовая категория  '}
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        category = serializer.save()
        assert category.name == 'Тестовая категория'


@pytest.mark.django_db
class TestLocationSerializer:

    def test_valid_name(self):
        data = {'name': '211 Кабинет'}
        serializer = LocationSerializer(data=data)

        assert serializer.is_valid(), serializer.errors

        location = serializer.save()
        assert location.name == '211 Кабинет'
        assert location.is_active is True

    def test_update_name(self):
        location = Location.objects.create(name='Исходное название')

        update_data = {'name': 'Новое название', 'is_active': False}
        serializer = LocationSerializer(instance=location, data=update_data)

        assert serializer.is_valid(), serializer.errors

        serializer.save()

        assert location.name == 'Новое название'
        assert location.is_active is False

    def test_validation_short_name(self):
        data = {'name': 'A'}
        serializer = LocationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_name_strip(self):
        data = {'name': '  Склад 1  '}
        serializer = LocationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        location = serializer.save()
        assert location.name == 'Склад 1'

import pytest
from slugify import slugify
from apps.references.models import Category, Location


@pytest.mark.django_db
class TestCategoryModel:

    def test_create_category(self):
        category = Category.objects.create(name='Тестовая категория')

        assert category.id is not None
        assert category.name == 'Тестовая категория'
        assert category.slug == slugify(category.name)
        assert category.is_active is True
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_is_active_default(self):
        category = Category.objects.create(name='Активная категория')
        assert category.is_active is True

    def test_category_get_active(self):
        Category.objects.create(name='Активная 1', is_active=True)
        Category.objects.create(name='Активная 2', is_active=True)
        Category.objects.create(name='Неактивная', is_active=False)

        active_categories = Category.get_active()
        assert active_categories.count() == 2


@pytest.mark.django_db
class TestLocationModel:

    def test_create_location(self):
        location = Location.objects.create(name='211 Кабинет')

        assert location.id is not None
        assert location.name == '211 Кабинет'
        assert location.is_active is True
        assert location.created_at is not None
        assert location.updated_at is not None

    def test_location_is_active_default(self):
        location = Location.objects.create(name='Склад')
        assert location.is_active is True

    def test_location_get_active(self):
        Location.objects.create(name='Локация 1', is_active=True)
        Location.objects.create(name='Локация 2', is_active=True)
        Location.objects.create(name='Неактивная локация', is_active=False)

        active_locations = Location.get_active()
        assert active_locations.count() == 2

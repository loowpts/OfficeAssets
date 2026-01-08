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


@pytest.mark.django_db
class TestLocationModel:
    def test_create_location(self):

        location = Location.objects.create(name='211 Кабинет')

        assert location.id is not None
        assert location.name == '211 Кабинет'
        assert location.created_at is not None
        assert location.updated_at is not None

from rest_framework import serializers
from .models import Category, Location


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Валидация имени категории"""
        if len(value) < 2:
            raise serializers.ValidationError(
                'Название категории должно быть не менее 2 символов'
            )
        return value.strip()


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор для локаций"""

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
        """Валидация имени локации"""
        if len(value) < 2:
            raise serializers.ValidationError(
                'Название локации должно быть не менее 2 символов'
            )
        return value.strip()

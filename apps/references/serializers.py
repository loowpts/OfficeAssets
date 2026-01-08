from rest_framework import serializers
from .models import Category, Location
from slugify import slugify


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Нужно указать названия категории')
        return value


class LocationCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Нужно указать название местоположения')
        return value

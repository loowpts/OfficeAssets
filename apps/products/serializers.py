from rest_framework import serializers
from .models import Product
from apps.references.serializers import CategorySerializer


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category',
            'category', 'category_name', 'unit',
            'is_consumable', 'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category',
            'unit', 'min_stock', 'is_consumable',
            'description', 'created_at', 'updated_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'sku', 'unit',
            'min_stock', 'is_consumable', 'description' 
        ]

    def validate_sku(self, value):
        return value.upper().strip()
    
    def validate_name(self, value):
        return value.strip()

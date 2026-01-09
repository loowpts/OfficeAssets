from rest_framework import serializers
from apps.products.serializers import ProductListSerializer
from .models import Asset


class AssetListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Asset
        fields = [
            'id', 'product', 'product_name', 'inventory_number',
            'status', 'status_display', 'current_location', 'location_name',
            'created_at'
        ]


class AssetDetailSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'product', 'serial_number', 'inventory_number',
            'status', 'current_location', 'created_at', 'updated_at'
        ]


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Asset
        fields = [
            'product', 'serial_number',
            'inventory_number', 'current_location'
        ]
        
    def validate_product(self, value):
        if value.is_consumable:
            raise serializers.ValidationError(
                'Asset можно создать только для техники (is_consumable=True)'
            )
        return value
    
    def validate_inventory_number(self, value):
        return value.upper().strip()

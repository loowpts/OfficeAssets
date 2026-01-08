from rest_framework import serializers
from .models import Asset


class AssetCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Asset
        fields = [
            'id', 'product', 'serial_number', 'inventory_number',
            'status', 'current_location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_product(self, product):
        if product.is_consumable:
            raise serializers.ValidationError(
                'Расходный материал нельзя добавить в инвентарь'
            )
        return product

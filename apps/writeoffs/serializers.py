from rest_framework import serializers

from apps.products.models import Product
from apps.references.models import Location
from apps.assets.models import Asset
from .models import WriteOff

class WriteOffListSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()

    def get_item_name(self, obj):
        """Возвращает название списанного объекта"""
        if obj.product:
            return f'{obj.product.name} x{obj.quantity}'
        return f'{obj.inventory_item.inventory_number}'

    class Meta:
        model = WriteOff
        fields = [
            'id', 'product', 'inventory_item', 'item_name',
            'quantity', 'location', 'reason', 'date'
        ]
        

class WriteOffConsumableSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_consumable=True)
    )
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)
    reason = serializers.CharField()
    

class WriteOffAssetSerializer(serializers.Serializer):
    inventory_item = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all()
    )
    reason = serializers.CharField()

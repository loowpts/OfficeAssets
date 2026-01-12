from rest_framework import serializers
from apps.references.models import Location
from apps.products.models import Product
from .models import Stock, StockOperations


class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    unit = serializers.CharField(source='product.unit', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'location',
            'location_name', 'quantity', 'unit', 'is_low_stock', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'quantity', 'created_at', 'updated_at'
        ]
    

class StockOperationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)

    class Meta:
        model = StockOperations
        fields = [
            'id', 'product', 'product_name', 'operation_type', 'operation_type_display',
            'quantity', 'from_location', 'to_location', 'comment',
            'timestamp'
        ]

        read_only_fields = [
            'id', 'product', 'product_name', 'operation_type', 'operation_type_display',
            'quantity', 'from_location', 'to_location', 'comment',
            'timestamp'
        ]


class ReceiptSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.filter(is_consumable=True)
    )
    location = serializers.PrimaryKeyRelatedField(
        queryset = Location.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)
    comment = serializers.CharField(required=False, allow_blank=True)
    

class ExpenseSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.filter(is_consumable=True)
    )
    location = serializers.PrimaryKeyRelatedField(
        queryset = Location.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)
    comment = serializers.CharField(required=False, allow_blank=True)


class TransferSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.filter(is_consumable=True)
    )
    from_location = serializers.PrimaryKeyRelatedField(
        queryset = Location.objects.all()
    )
    to_location = serializers.PrimaryKeyRelatedField(
        queryset = Location.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        from_location = attrs.get('from_location')
        to_location = attrs.get('to_location')

        if from_location == to_location:
            raise serializers.ValidationError(
                'Локации отправления и назначения должны различаться'
            )

        return attrs
    
    

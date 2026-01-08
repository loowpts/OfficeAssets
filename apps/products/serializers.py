from rest_framework import serializers
from .models import Product


class ProductCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'sku',
            'is_consumable', 'unit', 'min_stock',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError(
                'Имя продукта обязательно для заполнения'
            )

        if len(value) < 3:
            raise serializers.ValidationError(
                'Название должно быть не меньше 3 символов.'
            )
        return value
            

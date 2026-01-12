from rest_framework import serializers
from apps.assets.models import Asset
from apps.assets.serializers import AssetListSerializer
from apps.references.models import Location
from .models import Issuance


class IssuanceListSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='inventory_item.product.name', read_only=True)
    inventory_number = serializers.CharField(source='inventory_item.inventory_number', read_only=True)

    class Meta:
        model = Issuance
        fields = [
            'id', 'inventory_item', 'asset_name', 'inventory_number',
            'recipient', 'issue_date', 'return_date', 'created_at'
        ]


class IssuanceDetailSerializer(serializers.ModelSerializer):
    inventory_item = AssetListSerializer(read_only=True)
    
    class Meta:
        model = Issuance
        fields = [
            'id', 'inventory_item', 'recipient', 'issue_date',
            'return_date', 'issue_comment', 'return_comment',
            'created_at', 'updated_at'
        ]
    

class IssuanceCreateSerializer(serializers.Serializer):
    inventory_item = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.filter(
            status=Asset.StatusChoices.IN_STOCK
        )
    )
    recipient = serializers.CharField(max_length=255)
    comment = serializers.CharField(required=False, allow_blank=True)
    
    
class IssuanceReturnSerializer(serializers.Serializer):
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Комментарий при возврате'
    )

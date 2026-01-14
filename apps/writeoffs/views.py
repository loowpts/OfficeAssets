from rest_framework import status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from .models import WriteOff
from .services import WriteOffService
from apps.core.exceptions import InsufficientStockError
from .serializers import (
    WriteOffAssetSerializer, WriteOffConsumableSerializer,
    WriteOffListSerializer
)


class WriteOffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WriteOff.objects.select_related(
        'product', 'inventory_item', 'location'
    ).all()
    serializer_class = WriteOffListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'inventory_item', 'location']
    
    @action(detail=False, methods=['post'])
    def create_consumable(self, request):
        serializer = WriteOffConsumableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            write_off = WriteOffService.create_writeoff_consumable(
                product=serializer.validated_data['product'],
                location=serializer.validated_data['location'],
                quantity=serializer.validated_data['quantity'],
                reason=serializer.validated_data.get('reason', '')
            )
        except InsufficientStockError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            WriteOffListSerializer(write_off).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def create_asset(self, request):
        serializer = WriteOffAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            write_off = WriteOffService.create_writeoff_asset(
                inventory_item=serializer.validated_data['inventory_item'],
                reason=serializer.validated_data.get('reason', '')
            )
        except InsufficientStockError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            WriteOffListSerializer(write_off).data,
            status=status.HTTP_201_CREATED
        )

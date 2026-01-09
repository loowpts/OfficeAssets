from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.assets.models import Asset
from apps.assets.serializers import (
    AssetListSerializer,
    AssetDetailSerializer,
    AssetCreateUpdateSerializer
)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('product', 'current_location').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'status', 'current_location']
    search_fields = ['inventory_number', 'serial_number', 'product__name']
    ordering_fields = ['inventory_number', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        return AssetDetailSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        available_assets = self.queryset.filter(status=Asset.StatusChoices.IN_STOCK)
        serializer = self.get_serializer(available_assets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def issued(self, request):
        issued_assets = self.queryset.filter(status=Asset.StatusChoices.ISSUED)
        serializer = self.get_serializer(issued_assets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mark_maintenance(self, request, pk=None):
        asset = self.get_object()
        asset.status = Asset.StatusChoices.MAINTENANCE
        asset.save()
        
        return Response({
            'status': 'Asset отправлен на обслуживание'
        }, status=status.HTTP_200_OK)

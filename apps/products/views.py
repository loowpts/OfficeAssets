from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Product
from apps.products.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category'),all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_consumable', 'unit']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'created_at', 'sku']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    @action(detail=False, methods=['get'])
    def consumables(self, request):
        """Получить список расходных материалов"""
        consumables = self.queryset.filter(is_consumable=True)
        serializer = self.get_serializer(consumables, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def assets(self, request):
        """Получить список техники (не расходники)"""
        assets = self.queryset.filter(is_consumable=False)
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)

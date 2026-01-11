from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apps.references.models import Category, Location
from apps.references.serializers import CategorySerializer, LocationSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для категорий.

    list: Получить список категорий
    retrieve: Получить конкретную категорию
    create: Создать категорию
    update: Обновить категорию
    destroy: Удалить категорию
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet для локаций"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    

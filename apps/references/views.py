from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.references.models import Category, Location
from apps.references.serializers import CategoryCreateUpdateSerializer, LocationCreateUpdateSerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategoryCreateUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    
    
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer


class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all().order_by('id')
    serializer_class = LocationCreateUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['office']


class LocationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationCreateUpdateSerializer
    

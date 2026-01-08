from rest_framework import generics, filters

from django_filters.rest_framework import DjangoFilterBackend
from apps.products.serializers import ProductCreateUpdateSerializer
from .models import Product


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductCreateUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'category']
    
    
class ProductRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    

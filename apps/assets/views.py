from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Asset
from .serializers import AssetCreateSerializer


class AssetView(generics.ListCreateAPIView):
    queryset = Asset.objects.all().order_by('id')
    serializer_class = AssetCreateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['product', 'status', 'current_location']


class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all().order_by('id')
    serializer_class = AssetCreateSerializer

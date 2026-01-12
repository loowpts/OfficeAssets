from rest_framework import status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from .models import Issuance
from .services import IssuancesService
from apps.core.exceptions import AssetNotAvailableError
from .serializers import (
    IssuanceListSerializer, IssuanceDetailSerializer,
    IssuanceCreateSerializer, IssuanceReturnSerializer,
)


class IssuanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Issuance.objects.select_related(
        'inventory_item', 'inventory_item__product'
    ).all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['recipient', 'inventory_item']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return IssuanceListSerializer
        return IssuanceDetailSerializer
    
    @action(detail=False, methods=['post'])
    def create_issuance(self, request):
        serializer = IssuanceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            issuance = IssuancesService.create_issuance(
                inventory_item=serializer.validated_data['inventory_item'],
                recipient=serializer.validated_data['recipient'],
                comment=serializer.validated_data.get('comment', '')
            )

            result_serializer = IssuanceDetailSerializer(issuance)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)

        except AssetNotAvailableError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
                
    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        issuance = self.get_object()
        
        serializer = IssuanceReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_issuance = IssuancesService.create_return(
                issuance=issuance,
                location=serializer.validated_data['location'],
                comment=serializer.validated_data.get('comment', '')
            )
            
            result_serializer = IssuanceDetailSerializer(updated_issuance)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def active(self, request):
        queryset = IssuancesService.get_active_issuances()
        serializer = IssuanceListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

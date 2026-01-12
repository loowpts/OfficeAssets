from rest_framework import filters, status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from apps.references.models import Category, Location

from .models import Stock, StockOperations
from .services import StockService
from .serializers import (
    StockSerializer, StockOperationSerializer,
    ReceiptSerializer, ExpenseSerializer,
    TransferSerializer
)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.select_related('product', 'location').all()
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'location']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        queryset = StockService.get_low_stock_items()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data)
    

class StockOperationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockOperations.objects.select_related(
        'product', 'from_location', 'to_location'
    ).all()
    serializer_class = StockOperationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'product', 'operation_type', 'from_location', 'to_location'
    ]
    
    @action(detail=False, methods=['post'])
    def receipt(self, request):
        serializer = ReceiptSerializer(data=request.data)

        if serializer.is_valid():

            validated_data = serializer.validated_data

            try:
                operation = StockService.create_receipt(
                    product=validated_data['product'],
                    location=validated_data['location'],
                    quantity=validated_data['quantity'],
                    comment=validated_data.get('comment', '')
                )

                result_serializer = StockOperationSerializer(operation)

                return Response(result_serializer.data, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def expense(self, request):
        serializer = ExpenseSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data

            try:
                operation = StockService.create_expense(
                    product=validated_data['product'],
                    location=validated_data['location'],
                    quantity=validated_data['quantity'],
                    comment=validated_data.get('comment', '')
                )

                result_serializer = StockOperationSerializer(operation)

                return Response(result_serializer.data, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        serializer = TransferSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data

            try:
                operation = StockService.create_transfer(
                    product=validated_data['product'],
                    from_location=validated_data['from_location'],
                    to_location=validated_data['to_location'],
                    quantity=validated_data['quantity'],
                    comment=validated_data.get('comment', '')
                )

                result_serializer = StockOperationSerializer(operation)

                return Response(result_serializer.data, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

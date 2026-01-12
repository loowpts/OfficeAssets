from rest_framework.routers import DefaultRouter
from .views import (
    StockViewSet, StockOperationViewSet
)


app_name = 'stock'

router = DefaultRouter()
router.register('stock', StockViewSet, basename='stock')
router.register('stock-operation', StockOperationViewSet, basename='operation')

urlpatterns = router.urls


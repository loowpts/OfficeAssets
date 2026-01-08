from django.urls import path
from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateView,
)


app_name = 'products'

urlpatterns = [
    
    path('products/', ProductListCreateView.as_view(), name='products_list'),
    path('products/<int:pk>/', ProductRetrieveUpdateView.as_view(), name='product-detail'),
    
]



from django.urls import path
from .views import (
    AssetView,
    AssetDetailView
)


app_name = 'assets'

urlpatterns = [
    
    path('assets/', AssetView.as_view(), name='assets_list'),
    path('assets/<int:pk>/', AssetDetailView.as_view(), name='assets_detail'),
    
]


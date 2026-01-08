from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    LocationListCreateView,
    LocationRetrieveUpdateDestroyView
)


app_name = 'references'

urlpatterns = [
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    
    path('locations/', LocationListCreateView.as_view(), name='location-list'),
    path('locations/<int:pk>/', LocationRetrieveUpdateDestroyView.as_view(), name='location-detail'),
    
]




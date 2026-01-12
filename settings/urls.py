from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    path('api/v1/', include('apps.references.urls', namespace='references')),
    path('api/v1/', include('apps.products.urls', namespace='products')),
    path('api/v1/', include('apps.assets.urls', namespace='assets')),
    path('api/v1/', include('apps.stock.urls', namespace='stock')),
    path('api/v1/', include('apps.issues', namespace='issues')),
    
]

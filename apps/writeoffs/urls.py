from rest_framework.routers import DefaultRouter
from .views import (
    WriteOffViewSet
)


app_name = 'writeoffs'

router = DefaultRouter()
router.register('writeoffs', WriteOffViewSet, basename='writeoff')

urlpatterns = router.urls


from rest_framework.routers import DefaultRouter
from .views import (
    IssuanceViewSet
)


app_name = 'issues'

router = DefaultRouter()
router.register('issues', IssuanceViewSet, basename='issuance')

urlpatterns = router.urls

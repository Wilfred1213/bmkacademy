from rest_framework.routers import DefaultRouter
from.api_views import StudentViewSet
router = DefaultRouter()
router.register('', StudentViewSet, basename='students')
urlpatterns = router.urls
from rest_framework.routers import DefaultRouter

from .views import PendingUpdateViewSet, ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('pending-updates', PendingUpdateViewSet, basename='pending-update')

urlpatterns = router.urls

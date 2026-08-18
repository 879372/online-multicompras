from rest_framework.routers import DefaultRouter

from .views import AdminProductViewSet, PendingUpdateViewSet, ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('pending-updates', PendingUpdateViewSet, basename='pending-update')
router.register('admin/products', AdminProductViewSet, basename='admin-product')

urlpatterns = router.urls

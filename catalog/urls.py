from rest_framework.routers import DefaultRouter

from .views import AdminCategoryViewSet, AdminProductConditionViewSet, AdminProductViewSet, CategoryViewSet, PendingUpdateViewSet, ProductConditionViewSet, ProductViewSet, SupplierOfferViewSet, SupplierViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('conditions', ProductConditionViewSet, basename='condition')
router.register('pending-updates', PendingUpdateViewSet, basename='pending-update')
router.register('admin/products', AdminProductViewSet, basename='admin-product')
router.register('admin/categories', AdminCategoryViewSet, basename='admin-category')
router.register('admin/conditions', AdminProductConditionViewSet, basename='admin-condition')
router.register('admin/suppliers', SupplierViewSet, basename='supplier')
router.register('admin/supplier-offers', SupplierOfferViewSet, basename='supplier-offer')

urlpatterns = router.urls

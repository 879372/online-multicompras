from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import AutomationCreateOrStaff
from store_backend.pagination import AdminPageNumberPagination

from .models import Category, PendingUpdate, Product, ProductCondition, Supplier, SupplierOffer
from .serializers import CategorySerializer, PendingUpdateSerializer, ProductConditionSerializer, ProductSerializer, SupplierOfferSerializer, SupplierSerializer
from .warranty_rules import public_warranty_rules


class WarrantyRulesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(public_warranty_rules())


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True)


class AdminCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()


class ProductConditionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductConditionSerializer
    permission_classes = [AllowAny]
    queryset = ProductCondition.objects.filter(is_active=True)


class AdminProductConditionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductConditionSerializer
    permission_classes = [IsAdminUser]
    queryset = ProductCondition.objects.all()


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPageNumberPagination

    def get_queryset(self):
        queryset = Supplier.objects.all()
        search = self.request.query_params.get('search', '').strip()
        return queryset.filter(name__icontains=search) if search else queryset


class SupplierOfferViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierOfferSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPageNumberPagination

    def get_queryset(self):
        queryset = SupplierOffer.objects.select_related('product', 'supplier')
        product = self.request.query_params.get('product')
        supplier = self.request.query_params.get('supplier')
        if product:
            queryset = queryset.filter(product_id=product)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        return queryset


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Public catalog, consumed by the React frontend and the n8n WhatsApp bot."""

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, category__is_active=True, condition__is_active=True).select_related('category', 'condition')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset


class AdminProductViewSet(viewsets.ModelViewSet):
    """Staff CRUD used by the private management panel.

    This route is intentionally separate from the public read-only catalog and
    from the pending-update endpoint used by the n8n automation.
    """

    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPageNumberPagination

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'condition').all().order_by('-updated_at')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class PendingUpdateViewSet(viewsets.ModelViewSet):
    """Owner-only: n8n posts here after the LLM extracts data from a supplier
    WhatsApp message; the owner approves or rejects from the admin or API."""

    serializer_class = PendingUpdateSerializer
    permission_classes = [AutomationCreateOrStaff]

    def get_queryset(self):
        queryset = PendingUpdate.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        pending_update = self.get_object()
        pending_update.approve()
        return Response(self.get_serializer(pending_update).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        pending_update = self.get_object()
        pending_update.reject()
        return Response(self.get_serializer(pending_update).data)

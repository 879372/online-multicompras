from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from accounts.permissions import AutomationCreateOrStaff

from .models import Category, PendingUpdate, Product
from .serializers import CategorySerializer, PendingUpdateSerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True)


class AdminCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Public catalog, consumed by the React frontend and the n8n WhatsApp bot."""

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')
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

    queryset = Product.objects.select_related('category').all().order_by('-updated_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


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

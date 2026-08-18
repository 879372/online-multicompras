from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from catalog.models import PendingUpdate, Product

from .models import Sale
from .serializers import SaleSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.prefetch_related('items__product').select_related('created_by').all().order_by('-created_at')
    serializer_class = SaleSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard(request):
    today = timezone.localdate()
    paid = Sale.objects.filter(status=Sale.STATUS_PAID)
    return Response({
        'active_products': Product.objects.filter(is_active=True).count(),
        'low_stock_products': Product.objects.filter(is_active=True, stock__lte=5).count(),
        'pending_updates': PendingUpdate.objects.filter(status=PendingUpdate.STATUS_PENDING).count(),
        'sales_today': Sale.objects.filter(created_at__date=today).count(),
        'revenue': paid.aggregate(value=Sum('total'))['value'] or 0,
        'sales_by_status': list(Sale.objects.values('status').annotate(total=Count('id')).order_by('status')),
    })

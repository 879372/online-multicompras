from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Q

from store_backend.pagination import AdminPageNumberPagination

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Staff user management for the private dashboard."""

    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = get_user_model().objects.all().order_by('-date_joined')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | Q(first_name__icontains=search)
                | Q(last_name__icontains=search) | Q(email__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(self.get_serializer(request.user).data)

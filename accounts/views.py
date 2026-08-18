from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Staff user management for the private dashboard."""

    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return get_user_model().objects.all().order_by('-date_joined')

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(self.get_serializer(request.user).data)

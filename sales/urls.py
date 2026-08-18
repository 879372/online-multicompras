from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SaleViewSet, dashboard

router = DefaultRouter()
router.register('', SaleViewSet, basename='sale')

urlpatterns = [path('dashboard/', dashboard, name='dashboard'), *router.urls]

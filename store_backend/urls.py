from django.contrib import admin
from django.conf import settings
from django.http import JsonResponse
from django.urls import include, path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/health/', lambda request: JsonResponse({'status': 'ok'})),

    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('accounts.urls')),

    path('api/catalog/', include('catalog.urls')),
    path('api/conversations/', include('conversations.urls')),
    path('api/sales/', include('sales.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if not settings.USE_S3:
    urlpatterns.append(path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}))

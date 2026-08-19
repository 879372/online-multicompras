from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions


class ServiceTokenAuthentication(authentication.BaseAuthentication):
    """Authenticates the n8n bot via a single shared secret (N8N_API_TOKEN env
    var) sent in a dedicated X-N8N-Token header, so rotating it is just an env
    var change in Railway with no admin/shell step required. A dedicated
    header (rather than Authorization: Bearer) avoids colliding with
    JWTAuthentication, which also uses the Bearer scheme and would otherwise
    raise on the shared secret before this class gets a chance to run"""

    def authenticate(self, request):
        token = request.META.get('HTTP_X_N8N_TOKEN')
        if not token:
            return None
        if not settings.N8N_API_TOKEN or token != settings.N8N_API_TOKEN:
            raise exceptions.AuthenticationFailed('Invalid token.')

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='n8n-bot',
            defaults={'is_staff': False, 'is_superuser': False},
        )
        if created:
            user.set_unusable_password()
            user.save()
        return (user, None)

    def authenticate_header(self, request):
        return 'X-N8N-Token'

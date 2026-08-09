from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model. Only the owner/staff logs in (via is_staff/is_superuser);
    customers never authenticate, they only interact through WhatsApp."""
    pass

from rest_framework import viewsets

from .models import Conversation
from .serializers import ConversationSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """Owner-only: n8n posts here on handoff; the owner reviews and closes."""

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

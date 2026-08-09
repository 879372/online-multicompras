from django.db import models


class Conversation(models.Model):
    """Log of a WhatsApp conversation handled by the n8n bot. Lets the owner
    review handoffs where the bot couldn't resolve the customer's request."""

    STATUS_BOT_HANDLING = 'bot_handling'
    STATUS_HANDOFF = 'handoff'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_BOT_HANDLING, 'Bot handling'),
        (STATUS_HANDOFF, 'Handoff'),
        (STATUS_CLOSED, 'Closed'),
    ]

    customer_phone = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOT_HANDLING)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer_phone} ({self.status})'

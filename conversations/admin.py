from django.contrib import admin

from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('customer_phone', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('customer_phone', 'summary')
    readonly_fields = ('customer_phone', 'summary', 'created_at', 'updated_at')

from django.contrib import admin

from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer_name', 'customer_phone')
    inlines = [SaleItemInline]

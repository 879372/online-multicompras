from django.contrib import admin

from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    fields = ('product', 'quantity', 'unit_price', 'condition_name', 'warranty_months', 'imei', 'serial_number', 'battery_health')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer_name', 'customer_phone', 'items__imei', 'items__serial_number')
    inlines = [SaleItemInline]

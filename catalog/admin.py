from django.contrib import admin

from .models import Category, PendingUpdate, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'cash_price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')


def approve_selected(modeladmin, request, queryset):
    for pending_update in queryset.filter(status=PendingUpdate.STATUS_PENDING):
        pending_update.approve()


approve_selected.short_description = 'Approve selected'


@admin.register(PendingUpdate)
class PendingUpdateAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'proposed_price', 'proposed_stock', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('proposed_name', 'raw_text')
    actions = [approve_selected]

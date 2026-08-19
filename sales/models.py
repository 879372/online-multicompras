from django.conf import settings
from django.db import models


class Sale(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_PAID, 'Pago'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50, blank=True)
    customer_city = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Venda #{self.pk} — {self.customer_name}'


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('catalog.Product', related_name='sale_items', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    condition_name = models.CharField(max_length=100, blank=True)
    warranty_months = models.PositiveSmallIntegerField(default=0)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=150, blank=True)
    color = models.CharField(max_length=100, blank=True)
    storage = models.CharField(max_length=100, blank=True)
    imei = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    battery_health = models.PositiveSmallIntegerField(null=True, blank=True)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

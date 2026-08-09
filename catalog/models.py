from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PendingUpdate(models.Model):
    """A price/product change extracted by an LLM (in n8n) from a supplier's
    WhatsApp message. Nothing here touches the live catalog until the owner
    approves it through the Django Admin action or the /approve/ API endpoint,
    which is what keeps unreviewed supplier data out of the public catalog."""

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='pending_updates',
        help_text='Null if this is a brand-new product, not an update to an existing one.',
    )
    proposed_name = models.CharField(max_length=255, blank=True, help_text='Used when product is null (new product).')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    proposed_stock = models.PositiveIntegerField(null=True, blank=True)
    raw_text = models.TextField(help_text='The original supplier message text, for audit/debugging.')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        target = self.product.name if self.product else self.proposed_name
        return f'{target} ({self.status})'

    def approve(self):
        """Applies the proposed price/stock to the existing product, or creates
        a new one, then marks this update approved. Shared by the admin action
        and the /approve/ API endpoint so both stay in sync."""
        from django.utils import timezone

        if self.product:
            self.product.price = self.proposed_price
            if self.proposed_stock is not None:
                self.product.stock = self.proposed_stock
            self.product.save()
        else:
            self.product = Product.objects.create(
                name=self.proposed_name,
                price=self.proposed_price,
                stock=self.proposed_stock or 0,
                category='',
            )
        self.status = self.STATUS_APPROVED
        self.resolved_at = timezone.now()
        self.save()

    def reject(self):
        from django.utils import timezone

        self.status = self.STATUS_REJECTED
        self.resolved_at = timezone.now()
        self.save()

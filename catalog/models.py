from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class ProductCondition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    contact_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    condition = models.ForeignKey(ProductCondition, on_delete=models.PROTECT, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cash_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installments = models.PositiveSmallIntegerField(default=12)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=150, blank=True)
    color = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    storage = models.CharField(max_length=100, blank=True)
    connectivity = models.CharField(max_length=100, blank=True)
    origin = models.CharField(max_length=100, blank=True)
    warranty_months = models.PositiveSmallIntegerField(default=0)
    warranty_provider = models.CharField(max_length=150, blank=True)
    warranty_requires_seal = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/%Y/%m/', null=True, blank=True)
    variants = models.JSONField(
        default=list,
        blank=True,
        help_text='Product options such as model, color and stock. Stored as a list of objects.',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SupplierOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='supplier_offers')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='offers')
    supplier_sku = models.CharField(max_length=100, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(null=True, blank=True)
    variants = models.JSONField(default=list, blank=True)
    source_text = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('purchase_price', '-last_seen_at')
        constraints = [
            models.UniqueConstraint(
                fields=('product', 'supplier', 'supplier_sku'),
                name='unique_product_supplier_sku',
            ),
        ]

    def __str__(self):
        return f'{self.product} — {self.supplier}'


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
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL, related_name='pending_updates')
    proposed_brand = models.CharField(max_length=100, blank=True)
    proposed_model = models.CharField(max_length=150, blank=True)
    proposed_category = models.CharField(max_length=100, blank=True)
    proposed_condition = models.CharField(max_length=100, blank=True)
    proposed_ram = models.CharField(max_length=50, blank=True)
    proposed_storage = models.CharField(max_length=100, blank=True)
    proposed_connectivity = models.CharField(max_length=100, blank=True)
    proposed_origin = models.CharField(max_length=100, blank=True)
    proposed_warranty_months = models.PositiveSmallIntegerField(null=True, blank=True)
    proposed_warranty_provider = models.CharField(max_length=150, blank=True)
    proposed_warranty_requires_seal = models.BooleanField(default=False)
    proposed_variants = models.JSONField(default=list, blank=True)
    supplier_sku = models.CharField(max_length=100, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
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

        if self.status != self.STATUS_PENDING:
            return self.product
        if self.product:
            self.product.purchase_price = self.proposed_price
            if self.proposed_stock is not None:
                self.product.stock = self.proposed_stock
            proposed_fields = {
                'brand': self.proposed_brand,
                'model': self.proposed_model,
                'ram': self.proposed_ram,
                'storage': self.proposed_storage,
                'connectivity': self.proposed_connectivity,
                'origin': self.proposed_origin,
                'warranty_provider': self.proposed_warranty_provider,
            }
            for field, value in proposed_fields.items():
                if value:
                    setattr(self.product, field, value)
            if self.proposed_warranty_months is not None:
                self.product.warranty_months = self.proposed_warranty_months
            if self.proposed_variants:
                self.product.variants = self.proposed_variants
            self.product.warranty_requires_seal = self.proposed_warranty_requires_seal
            self.product.save()
        else:
            category = Category.objects.filter(name__iexact=self.proposed_category).first() if self.proposed_category else None
            category = category or Category.objects.filter(is_active=True).first()
            if category is None:
                category = Category.objects.create(name='Sem categoria')
            condition = ProductCondition.objects.filter(name__iexact=self.proposed_condition).first() if self.proposed_condition else None
            condition = condition or ProductCondition.objects.filter(is_active=True).first()
            if condition is None:
                condition = ProductCondition.objects.create(name='Não informado')
            self.product = Product.objects.create(
                name=self.proposed_name,
                price=self.proposed_price,
                purchase_price=self.proposed_price,
                stock=self.proposed_stock or 0,
                category=category,
                condition=condition,
                brand=self.proposed_brand,
                model=self.proposed_model,
                ram=self.proposed_ram,
                storage=self.proposed_storage,
                connectivity=self.proposed_connectivity,
                origin=self.proposed_origin,
                warranty_months=self.proposed_warranty_months or 0,
                warranty_provider=self.proposed_warranty_provider,
                warranty_requires_seal=self.proposed_warranty_requires_seal,
                variants=self.proposed_variants,
            )
        if self.supplier:
            SupplierOffer.objects.update_or_create(
                product=self.product,
                supplier=self.supplier,
                supplier_sku=self.supplier_sku,
                defaults={
                    'purchase_price': self.proposed_price,
                    'stock': self.proposed_stock,
                    'variants': self.proposed_variants,
                    'source_text': self.raw_text,
                    'is_available': True,
                },
            )
        self.status = self.STATUS_APPROVED
        self.resolved_at = timezone.now()
        self.save()
        return self.product

    def reject(self):
        from django.utils import timezone

        if self.status != self.STATUS_PENDING:
            return
        self.status = self.STATUS_REJECTED
        self.resolved_at = timezone.now()
        self.save()

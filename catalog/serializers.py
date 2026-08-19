from rest_framework import serializers

from .models import Category, PendingUpdate, Product, ProductCondition, Supplier, SupplierOffer


VARIANT_FIELDS = {
    'model', 'color', 'ram', 'storage', 'connectivity', 'purchase_price',
    'stock', 'supplier_sku',
}


def validate_variant_list(value):
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise serializers.ValidationError('Use uma lista de objetos para as variações.')
    for item in value:
        if set(item) - VARIANT_FIELDS:
            raise serializers.ValidationError(
                'Cada variação aceita apenas modelo, cor, RAM, armazenamento, conectividade, preço de compra, estoque e SKU.'
            )
        if 'stock' in item and (not isinstance(item['stock'], int) or item['stock'] < 0):
            raise serializers.ValidationError('O estoque da variação deve ser um número inteiro positivo.')
    return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProductConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCondition
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_name', 'phone', 'notes', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SupplierOfferSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    def validate_variants(self, value):
        return validate_variant_list(value)

    class Meta:
        model = SupplierOffer
        fields = [
            'id', 'product', 'product_name', 'supplier', 'supplier_name', 'supplier_sku',
            'purchase_price', 'stock', 'variants', 'source_text', 'is_available',
            'last_seen_at', 'created_at',
        ]
        read_only_fields = ['last_seen_at', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    installment_value = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    condition_name = serializers.CharField(source='condition.name', read_only=True)

    def get_installment_value(self, obj):
        if not obj.installments:
            return None
        return obj.price / obj.installments

    def validate_variants(self, value):
        return validate_variant_list(value)

    def validate(self, attrs):
        price = attrs.get('price', getattr(self.instance, 'price', None))
        compare_at = attrs.get('compare_at_price', getattr(self.instance, 'compare_at_price', None))
        if compare_at is not None and price is not None and compare_at < price:
            raise serializers.ValidationError({'compare_at_price': 'O preço original não pode ser menor que o preço atual.'})
        return attrs

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'condition', 'condition_name',
            'brand', 'model', 'color', 'ram', 'storage', 'connectivity', 'origin',
            'warranty_months', 'warranty_provider', 'warranty_requires_seal',
            'price', 'purchase_price', 'compare_at_price', 'cash_price',
            'installments', 'installment_value', 'stock', 'description',
            'image', 'variants', 'is_active', 'created_at', 'updated_at',
        ]


class PendingUpdateSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    def validate_proposed_variants(self, value):
        return validate_variant_list(value)

    def validate_confidence(self, value):
        if value is not None and not 0 <= value <= 100:
            raise serializers.ValidationError('A confiança deve estar entre 0 e 100.')
        return value

    class Meta:
        model = PendingUpdate
        fields = [
            'id', 'product', 'proposed_name', 'proposed_price', 'proposed_stock',
            'supplier', 'supplier_name', 'supplier_sku', 'proposed_brand', 'proposed_model',
            'proposed_category', 'proposed_condition', 'proposed_ram', 'proposed_storage',
            'proposed_connectivity', 'proposed_origin', 'proposed_warranty_months',
            'proposed_warranty_provider', 'proposed_warranty_requires_seal',
            'proposed_variants', 'confidence', 'raw_text', 'status', 'created_at', 'resolved_at',
        ]
        read_only_fields = ['status', 'created_at', 'resolved_at']

from rest_framework import serializers

from .models import Category, PendingUpdate, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    installment_value = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    def get_installment_value(self, obj):
        if not obj.installments:
            return None
        return obj.price / obj.installments

    def validate_variants(self, value):
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise serializers.ValidationError('Use uma lista de objetos para as variações.')
        allowed = {'model', 'color', 'stock'}
        for item in value:
            if set(item) - allowed:
                raise serializers.ValidationError('Cada variação aceita apenas model, color e stock.')
            if 'stock' in item and (not isinstance(item['stock'], int) or item['stock'] < 0):
                raise serializers.ValidationError('O estoque da variação deve ser um número inteiro positivo.')
        return value

    def validate(self, attrs):
        price = attrs.get('price', getattr(self.instance, 'price', None))
        compare_at = attrs.get('compare_at_price', getattr(self.instance, 'compare_at_price', None))
        if compare_at is not None and price is not None and compare_at < price:
            raise serializers.ValidationError({'compare_at_price': 'O preço original não pode ser menor que o preço atual.'})
        return attrs

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'price', 'compare_at_price', 'cash_price',
            'installments', 'installment_value', 'stock', 'description',
            'image', 'variants', 'is_active', 'created_at', 'updated_at',
        ]


class PendingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingUpdate
        fields = [
            'id', 'product', 'proposed_name', 'proposed_price', 'proposed_stock',
            'raw_text', 'status', 'created_at', 'resolved_at',
        ]
        read_only_fields = ['status', 'created_at', 'resolved_at']

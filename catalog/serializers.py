from rest_framework import serializers

from .models import PendingUpdate, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'price', 'stock', 'description',
            'image', 'is_active', 'created_at', 'updated_at',
        ]


class PendingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingUpdate
        fields = [
            'id', 'product', 'proposed_name', 'proposed_price', 'proposed_stock',
            'raw_text', 'status', 'created_at', 'resolved_at',
        ]
        read_only_fields = ['status', 'created_at', 'resolved_at']

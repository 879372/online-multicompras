from django.db import transaction
from rest_framework import serializers

from .models import Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price', 'unit_cost', 'subtotal',
            'condition_name', 'warranty_months', 'brand', 'model', 'color', 'storage',
            'imei', 'serial_number', 'battery_health',
        ]
        read_only_fields = ['unit_cost', 'condition_name', 'warranty_months']

    def validate_battery_health(self, value):
        if value is not None and value > 100:
            raise serializers.ValidationError('A saúde da bateria deve estar entre 0 e 100.')
        return value


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'customer_name', 'customer_phone', 'customer_city', 'status', 'total', 'notes', 'items', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['total', 'created_by_name', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop('items')
        sale = Sale.objects.create(created_by=self.context['request'].user, **validated_data)
        total = 0
        for item in items:
            self._snapshot_product(item)
            SaleItem.objects.create(sale=sale, **item)
            total += item['unit_price'] * item['quantity']
        sale.total = total
        sale.save(update_fields=['total'])
        return sale

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        if items is not None:
            instance.items.all().delete()
            total = 0
            for item in items:
                self._snapshot_product(item)
                SaleItem.objects.create(sale=instance, **item)
                total += item['unit_price'] * item['quantity']
            instance.total = total
            instance.save(update_fields=['total'])
        return instance

    @staticmethod
    def _snapshot_product(item):
        product = item['product']
        item.update({
            'unit_cost': product.purchase_price,
            'condition_name': product.condition.name,
            'warranty_months': product.warranty_months,
            'brand': item.get('brand') or product.brand,
            'model': item.get('model') or product.model or product.name,
            'color': item.get('color') or product.color,
            'storage': item.get('storage') or product.storage,
        })

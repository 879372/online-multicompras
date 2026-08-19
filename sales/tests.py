from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Category, Product, ProductCondition

from .models import Sale


class SaleApiTests(APITestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(username='owner', password='strong-pass', is_staff=True)
        category = Category.objects.create(name='Phone')
        condition = ProductCondition.objects.get(name='Seminovo Premium')
        self.product = Product.objects.create(
            name='Phone', category=category, condition=condition, price=1000,
            purchase_price=700, warranty_months=3, brand='Apple', model='iPhone 15', stock=10,
        )
        self.client.force_authenticate(self.staff)

    def test_create_sale_calculates_total_server_side(self):
        response = self.client.post('/api/sales/', {
            'customer_name': 'Maria', 'status': 'paid',
            'items': [{'product': self.product.id, 'quantity': 2, 'unit_price': '950.00'}],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sale.objects.get().total, 1900)
        item = Sale.objects.get().items.get()
        self.assertEqual(item.condition_name, 'Seminovo Premium')
        self.assertEqual(item.warranty_months, 3)
        self.assertEqual(item.unit_cost, 700)

    def test_warranty_pdf_is_generated(self):
        sale = Sale.objects.create(customer_name='Maria', status='paid', created_by=self.staff)
        sale.items.create(product=self.product, quantity=1, unit_price=1000, condition_name='Seminovo Premium', warranty_months=3)
        response = self.client.get(f'/api/sales/{sale.id}/warranty/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_dashboard_returns_management_metrics(self):
        response = self.client.get('/api/sales/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('active_products', response.data)

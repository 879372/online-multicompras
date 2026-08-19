from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, PendingUpdate, Product, ProductCondition


class ProductApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Phone')
        self.condition = ProductCondition.objects.get(name='Novo/Lacrado')
        self.active = Product.objects.create(name='Phone A', category=self.category, condition=self.condition, price=1200, stock=3)
        Product.objects.create(name='Phone hidden', category=self.category, condition=self.condition, price=900, is_active=False)
        self.staff = get_user_model().objects.create_user(username='owner', password='strong-pass', is_staff=True)

    def test_public_catalog_only_returns_active_products(self):
        response = self.client.get(f'/api/catalog/products/?search=Phone&category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [self.active.id])

    def test_admin_products_are_paginated(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get('/api/catalog/admin/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn('results', response.data)

    def test_admin_product_write_requires_staff(self):
        response = self.client.post('/api/catalog/admin/products/', {'name': 'New', 'category': self.category.id, 'condition': self.condition.id, 'price': '10.00'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.staff)
        response = self.client.post('/api/catalog/admin/products/', {'name': 'New', 'category': self.category.id, 'condition': self.condition.id, 'price': '10.00'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_public_categories_only_return_active_records(self):
        Category.objects.create(name='Hidden', is_active=False)
        response = self.client.get('/api/catalog/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['name'] for item in response.data], ['Phone'])

    def test_compare_at_price_must_be_greater_than_current_price(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(f'/api/catalog/admin/products/{self.active.id}/', {'compare_at_price': '100.00'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_automation_can_create_but_cannot_approve_update(self):
        bot = get_user_model().objects.create_user(username='n8n-bot')
        self.client.force_authenticate(bot)
        response = self.client.post('/api/catalog/pending-updates/', {
            'product': self.active.id, 'proposed_price': '1100.00', 'raw_text': 'Phone A 1100',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pending = PendingUpdate.objects.get()
        response = self.client.post(f'/api/catalog/pending-updates/{pending.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

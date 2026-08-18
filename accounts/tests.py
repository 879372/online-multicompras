from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class UserApiTests(APITestCase):
    def test_staff_can_create_user_with_hashed_password(self):
        staff = get_user_model().objects.create_user(username='owner', password='owner-pass', is_staff=True)
        self.client.force_authenticate(staff)
        response = self.client.post('/api/accounts/users/', {'username': 'seller', 'password': 'seller-password', 'is_staff': True})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.get(username='seller').check_password('seller-password'))

    def test_non_staff_cannot_list_users(self):
        user = get_user_model().objects.create_user(username='viewer', password='viewer-pass')
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get('/api/accounts/users/').status_code, status.HTTP_403_FORBIDDEN)

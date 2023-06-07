"""
Test for the user api endpoint
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    """Create a new user api."""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTest(TestCase):
    """Test the public features user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create user success."""

        payload = {
            'email': 'margetest@gmail.com',
            'password': 'margepass12345',
            'name': 'marg',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user email is exists."""


        payload = {
            'email': 'margetest@gmail.com',
            'password': 'margepass12345',
            'name': 'marg',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short_error(self):
        """Test error user password if less than 5 character."""

        payload = {
            'email': 'margetest@gmail.com',
            'password': 'pwd',
            'name': 'marg',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test creating a token for a user."""

        user_details = {
            'email': 'usertest@example.com',
            'password': 'testpass123456',
            'name': 'testuser'
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
            'name': user_details['name'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test crete token if credentials is invalid."""

        create_user(email="usertest@example.com", password="mypasswords")

        payload = {'email': 'usertest@example.com', 'password': 'yourpasswords'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', payload)
        self.assertSetEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting blank password and returning an error."""
        payload = {'email': 'usertest@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', payload)
        self.assertSetEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
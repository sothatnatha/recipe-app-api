"""
Test models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class TestModels(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email successful."""
        email = 'test@example.com'
        password = 'testpassword12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

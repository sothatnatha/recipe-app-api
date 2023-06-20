"""
Test models
"""
from unittest.mock  import patch

from core import models
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

def create_user(email="test@example.com", password="testpassword"):
    """Create a new user for tags apis."""
    return get_user_model().objects.create_user(email, password)

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

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        simple_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in simple_emails:
            user = get_user_model().objects.create_user(email, 'example123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """"Test user without an email raises a valueError (blank emial)."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testW@gmail.com')

    def test_create_superuser(self):
        """"Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_create_recipe(self):
        """Test create recipe with authenticated user."""
        user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test12345'
        )
        recipe = models.Recipe.objects.create(
            user = user,
            title = 'A mock recipe name.',
            time_minutes = 5,
            price =  Decimal(3.50),
            description='Sample receipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test create tag with authenticated user."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='tag1')

        self.assertEqual(str(tag), tag.name)    

    def test_create_ingredient(self):
        """Test create ingredient with authenticated user."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name='Ingredient1')

        self.assertEqual(str(ingredient), ingredient.name)


    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generate file path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
"""Test recipe APIs."""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model
from core.models import Recipe

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_user(**params):
    """Create new user"""
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """Create a new recipe"""

    defaults = {
        'title': 'Sample recipe',
        'description': 'Sample recipe description',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'link': 'https://www.youtube.com/watch?v=KjRDidAuBMw'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated APIs requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to call APIs."""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated APIs requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user2@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving recipes list."""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_list_limited_to_user(self):
        """Test recipe list is limited of authenticate user."""
        user2 = create_user(email='user@example.com', password='test123456')

        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_get_recipe_details(self):
        """Test get recipe detials.""" 

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_successful(self):
        """Test creating a new recipe."""
        payload = {
            'title': 'Sample recipe',
            'description': 'Sample recipe description',
            'time_minutes': 10,
            'price': Decimal('5.20'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test updating a recipe with partial data.""" 
        original_link = "http://example.com/recipe.pdf"
        
        recipe = create_recipe(
            user= self.user,
            title = "Sample recipe title",
            link= original_link
        )

        payload ={'title': 'Update recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code,  status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test updating a recipe with full data.""" 
        
        recipe = create_recipe(
            user= self.user,
            title = "Sample recipe title",
            link= "http://example.com/recipe.pdf",
            description= "Sample recipe description",
        )

        payload = {
            'title': 'New recipe title',
            'link': 'http://example.com/recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 20,
            'price': Decimal('5.20'),
        }
        
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code,  status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_upate_user_return_error(self):
        """Test changing reciper user and return results in errors."""

        new_user = create_user(email='newuser@example.com', password='test12345')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())


    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another user recipe and gives an error."""

        new_user = create_user(email='newuser@example.com', password='test12345')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
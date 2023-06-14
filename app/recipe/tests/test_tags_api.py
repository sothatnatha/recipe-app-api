"""
Test tags api.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import TagSerializer
from core.models import Tag

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """Return tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="test@example.com", password="testpassword"):
    """
    Creates a new user.
    """
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """
    Test the publicly available tags API.
    """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that unauthenticated user.
        """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """
    Test the authorized user.
    """
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_retrieve_tags(self):
        """
        Test retrieving tags.
        """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')

        serailizer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serailizer.data)

    def test_tags_limited_to_user(self):
        """
        Test that tags returned are for the authenticated user.
        """
        user2 = create_user(email='user2@example.com', password='testpassword')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort foods')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tags(self):
        """
        Test updating tags.
        """
        tag = Tag.objects.create(user=self.user, name='After dinner')
        payload = {'name': 'Lunch'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
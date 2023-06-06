""""
Test for the django admin modification
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTest(TestCase):
    """Test Django admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@example.com',
            password = 'test123456'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'user@example.com',
            password = 'user123456',
            name  = 'user test'
        )

    def test_users_list(self):
        """Test users listed on page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

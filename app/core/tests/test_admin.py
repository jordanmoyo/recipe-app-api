"""
test for the admin model
"""
from django.test import TestCase  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.urls import reverse  # type: ignore
from django.test import Client  # type: ignore


class AdminSiteTests(TestCase):
    """Test for admin site"""

    def setUp(self):
        """Setup function"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='user123',
            name='Test user full name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that the edit user page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

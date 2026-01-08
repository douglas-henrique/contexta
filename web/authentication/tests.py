"""
Tests for authentication endpoints.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class AuthenticationTests(TestCase):
    """Test authentication endpoints."""

    def setUp(self):
        """Set up test client and test user."""
        self.client = APIClient()
        self.register_url = reverse("authentication:register")
        self.login_url = reverse("authentication:login")
        self.logout_url = reverse("authentication:logout")
        self.me_url = reverse("authentication:me")
        self.change_password_url = reverse("authentication:change_password")

        # Create a test user
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )

    def test_register_user(self):
        """Test user registration."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123!",
            "password_confirm": "newpass123!",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["username"], "newuser")

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password": "newpass123!",
            "password_confirm": "differentpass123!",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        data = {
            "username": "anotheruser",
            "email": self.user_data["email"],  # Duplicate email
            "password": "newpass123!",
            "password_confirm": "newpass123!",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_user(self):
        """Test user login."""
        data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            "username": self.user_data["username"],
            "password": "wrongpassword",
        }

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile(self):
        """Test getting current user profile."""
        # Login to get token
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        access_token = login_response.data["tokens"]["access"]

        # Get profile
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_data["username"])
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_update_user_profile(self):
        """Test updating current user profile."""
        # Login to get token
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        access_token = login_response.data["tokens"]["access"]

        # Update profile
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        update_data = {"first_name": "Updated"}
        response = self.client.patch(self.me_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")

    def test_me_endpoint_requires_authentication(self):
        """Test that /me endpoint requires authentication."""
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_user(self):
        """Test user logout (token blacklist)."""
        # Login to get tokens
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        access_token = login_response.data["tokens"]["access"]
        refresh_token = login_response.data["tokens"]["refresh"]

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_data = {"refresh": refresh_token}
        response = self.client.post(self.logout_url, logout_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        """Test password change."""
        # Login to get token
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        access_token = login_response.data["tokens"]["access"]

        # Change password
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        change_data = {
            "old_password": self.user_data["password"],
            "new_password": "newpass456!",
            "new_password_confirm": "newpass456!",
        }
        response = self.client.post(self.change_password_url, change_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try logging in with new password
        new_login_data = {
            "username": self.user_data["username"],
            "password": "newpass456!",
        }
        new_login_response = self.client.post(self.login_url, new_login_data, format="json")
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        """Test password change with incorrect old password."""
        # Login to get token
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        access_token = login_response.data["tokens"]["access"]

        # Change password with wrong old password
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        change_data = {
            "old_password": "wrongoldpass",
            "new_password": "newpass456!",
            "new_password_confirm": "newpass456!",
        }
        response = self.client.post(self.change_password_url, change_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

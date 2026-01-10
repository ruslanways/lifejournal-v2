"""
Tests for user login functionality.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestLogin:
    """Test user login flow."""

    def test_login_with_username(self, client, verified_user):
        """Test that login works with username."""
        url = reverse("account_login")
        data = {
            "login": verified_user.username,
            "password": "testpass123",
        }

        response = client.post(url, data, follow=True)
        # Should redirect after successful login
        assert response.status_code == 200
        # Check user is authenticated if context exists
        if response.context:
            assert response.context["user"].is_authenticated
            assert response.context["user"] == verified_user
        else:
            # Verify login worked by checking session
            assert client.session.get("_auth_user_id") == str(verified_user.pk)

    def test_login_with_email(self, client, verified_user):
        """Test that login works with email."""
        url = reverse("account_login")
        data = {
            "login": verified_user.email,
            "password": "testpass123",
        }

        response = client.post(url, data, follow=True)
        # Should redirect after successful login
        assert response.status_code == 200
        # Check user is authenticated if context exists
        if response.context:
            assert response.context["user"].is_authenticated
            assert response.context["user"] == verified_user
        else:
            # Verify login worked by checking session
            assert client.session.get("_auth_user_id") == str(verified_user.pk)

    def test_login_rejects_invalid_credentials(self, client, verified_user):
        """Test that login rejects invalid credentials."""
        url = reverse("account_login")
        data = {
            "login": verified_user.username,
            "password": "wrongpassword",
        }

        response = client.post(url, data)
        # Should show form errors
        assert response.status_code == 200
        form = response.context["form"]
        assert not form.is_valid() or "credentials" in str(response.content).lower()

    def test_login_rejects_nonexistent_user(self, client):
        """Test that login rejects nonexistent user."""
        url = reverse("account_login")
        data = {
            "login": "nonexistent",
            "password": "somepassword",
        }

        response = client.post(url, data)
        # Should show form errors
        assert response.status_code == 200
        form = response.context["form"]
        assert not form.is_valid() or "credentials" in str(response.content).lower()

    def test_login_rejects_inactive_user(self, client, django_user_model):
        """Test that inactive user cannot login."""
        from allauth.account.models import EmailAddress

        inactive_user = django_user_model.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="testpass123",
            is_active=False,
        )
        EmailAddress.objects.create(
            user=inactive_user,
            email=inactive_user.email,
            verified=True,
            primary=True,
        )

        url = reverse("account_login")
        data = {
            "login": inactive_user.username,
            "password": "testpass123",
        }

        response = client.post(url, data)
        # Allauth redirects inactive users to /accounts/inactive/
        assert response.status_code == 302
        assert response.url == "/accounts/inactive/" or response.url.endswith("/accounts/inactive/")

    @pytest.mark.parametrize("login_field", ["username", "email"])
    def test_login_with_different_fields(self, client, verified_user, login_field):
        """Test login works with both username and email fields."""
        url = reverse("account_login")
        login_value = getattr(verified_user, login_field)
        data = {
            "login": login_value,
            "password": "testpass123",
        }

        response = client.post(url, data, follow=True)
        assert response.status_code == 200
        # Check user is authenticated if context exists
        if response.context:
            assert response.context["user"].is_authenticated
            assert response.context["user"] == verified_user
        else:
            # Verify login worked by checking session
            assert client.session.get("_auth_user_id") == str(verified_user.pk)


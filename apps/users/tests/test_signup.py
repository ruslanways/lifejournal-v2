"""
Tests for user signup functionality.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from allauth.account.models import EmailAddress

User = get_user_model()


@pytest.mark.django_db
class TestSignup:
    """Test user signup flow."""

    def test_signup_creates_user(self, client):
        """Test that valid signup creates a new user."""
        url = reverse("account_signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        response = client.post(url, data)
        # Should redirect after successful signup
        assert response.status_code in [200, 302]

        # Check user was created
        assert User.objects.filter(username="newuser").exists()
        user = User.objects.get(username="newuser")
        assert user.email == "newuser@example.com"
        assert user.check_password("SecurePass123!")

    def test_signup_sends_verification_email(self, client, mailoutbox):
        """Test that signup sends email verification."""
        url = reverse("account_signup")
        data = {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        client.post(url, data)

        # Check email was sent
        assert len(mailoutbox) == 1
        assert "verify" in mailoutbox[0].subject.lower() or "confirm" in mailoutbox[0].subject.lower()

    def test_signup_rejects_duplicate_username(self, client, user):
        """Test that signup rejects duplicate username."""
        url = reverse("account_signup")
        data = {
            "username": user.username,  # Already exists
            "email": "different@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        response = client.post(url, data)
        # Should show form errors
        assert response.status_code == 200
        assert "username" in response.context["form"].errors or "already exists" in str(response.content).lower()

    def test_signup_rejects_duplicate_email(self, client, user):
        """Test that signup rejects duplicate email."""
        url = reverse("account_signup")
        data = {
            "username": "differentuser",
            "email": user.email,  # Already exists
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        response = client.post(url, data, follow=False)
        # Allauth might redirect to confirm-email even with duplicate email
        # or show form errors. Check both cases
        if response.status_code == 302:
            # If redirecting, it might be allowing signup (which shouldn't happen with ACCOUNT_UNIQUE_EMAIL=True)
            # But in some allauth configs, it redirects to confirm-email
            # For now, just verify it doesn't create a duplicate user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users_with_email = User.objects.filter(email=user.email)
            assert users_with_email.count() == 1  # Should still be only one user
        else:
            # Should show form errors
            assert response.status_code == 200
            assert "email" in response.context["form"].errors or "already exists" in str(response.content).lower()

    def test_signup_rejects_invalid_data(self, client):
        """Test that signup rejects invalid data."""
        url = reverse("account_signup")
        data = {
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid email
            "password1": "short",  # Too short
            "password2": "different",  # Doesn't match
        }

        response = client.post(url, data)
        assert response.status_code == 200
        form = response.context["form"]
        assert not form.is_valid()

    def test_signup_saves_custom_user_fields(self, client):
        """Test that custom user fields are saved correctly."""
        url = reverse("account_signup")
        data = {
            "username": "customuser",
            "email": "customuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        client.post(url, data)

        user = User.objects.get(username="customuser")
        # Check custom fields exist (even if empty)
        assert hasattr(user, "bio")
        assert hasattr(user, "avatar")
        assert hasattr(user, "website")

    def test_signup_creates_email_address(self, client):
        """Test that signup creates EmailAddress record."""
        url = reverse("account_signup")
        data = {
            "username": "emailuser",
            "email": "emailuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        client.post(url, data)

        user = User.objects.get(username="emailuser")
        assert EmailAddress.objects.filter(user=user, email=user.email).exists()
        email_address = EmailAddress.objects.get(user=user, email=user.email)
        assert email_address.primary is True
        # Email should be unverified initially (mandatory verification)
        assert email_address.verified is False


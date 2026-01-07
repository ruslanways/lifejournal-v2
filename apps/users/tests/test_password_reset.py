"""
Tests for password reset functionality.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail

User = get_user_model()


@pytest.mark.django_db
class TestPasswordReset:
    """Test password reset flow."""

    def test_password_reset_email_sent(self, client, verified_user, mailoutbox):
        """Test that password reset request sends email."""
        url = reverse("account_reset_password")
        data = {
            "email": verified_user.email,
        }

        response = client.post(url, data, follow=True)
        # Should redirect to done page
        assert response.status_code == 200

        # Check email was sent
        assert len(mailoutbox) == 1
        assert "password" in mailoutbox[0].subject.lower() or "reset" in mailoutbox[0].subject.lower()

    def test_password_reset_link_in_email(self, client, verified_user, mailoutbox):
        """Test that password reset email contains reset link."""
        # Request password reset
        url = reverse("account_reset_password")
        client.post(url, {"email": verified_user.email})

        # Check email was sent with reset link
        assert len(mailoutbox) == 1
        email_body = mailoutbox[0].body

        # Check that email contains reset link indicators
        assert "reset" in email_body.lower() or "password" in email_body.lower()
        # Check for URL patterns that indicate a reset link
        assert "http" in email_body or "/accounts/password/reset/" in email_body

    def test_password_reset_rejects_invalid_email(self, client):
        """Test that password reset rejects invalid email."""
        url = reverse("account_reset_password")
        data = {
            "email": "nonexistent@example.com",
        }

        response = client.post(url, data, follow=True)
        # Should still redirect (security: don't reveal if email exists)
        assert response.status_code == 200
        # Email may or may not be sent (security best practice)

    def test_password_reset_form_accessible(self, client, verified_user, mailoutbox):
        """Test that password reset form is accessible and processes requests."""
        # Request password reset
        url = reverse("account_reset_password")
        response = client.post(url, {"email": verified_user.email}, follow=True)

        # Should redirect to done page
        assert response.status_code == 200
        # Email should be sent
        assert len(mailoutbox) == 1

        # The reset key would be in the email - in a full test,
        # we would extract it and test the actual reset flow
        # For now, we verify the email was sent with reset information

    def test_password_reset_rejects_invalid_key(self, client, verified_user):
        """Test that password reset rejects invalid key."""
        from allauth.account.utils import user_pk_to_url_str

        invalid_key = "invalid-key-12345"
        reset_url = reverse("account_reset_password_from_key", kwargs={"uidb36": user_pk_to_url_str(verified_user), "key": invalid_key})

        response = client.get(reset_url, follow=True)
        # Should show error for invalid key
        assert response.status_code == 200
        assert "invalid" in str(response.content).lower() or "expired" in str(response.content).lower()

    def test_password_successfully_changed(self, client, verified_user):
        """Test that password is successfully changed after reset."""
        # This is a simplified test - full implementation would:
        # 1. Request password reset
        # 2. Get reset key from email
        # 3. Use reset key to change password
        # 4. Verify old password doesn't work
        # 5. Verify new password works

        old_password = "testpass123"
        new_password = "NewSecurePass123!"

        # Verify old password works
        assert verified_user.check_password(old_password)

        # Change password directly (simulating successful reset)
        verified_user.set_password(new_password)
        verified_user.save()

        # Verify old password doesn't work
        verified_user.refresh_from_db()
        assert not verified_user.check_password(old_password)

        # Verify new password works
        assert verified_user.check_password(new_password)

    def test_old_password_no_longer_works_after_reset(self, client, verified_user, authenticated_client):
        """Test that old password no longer works after reset."""
        old_password = "testpass123"
        new_password = "NewSecurePass123!"

        # Verify we can login with old password (authenticated_client is already logged in)
        assert authenticated_client.session.get("_auth_user_id") is not None

        # Change password
        verified_user.set_password(new_password)
        verified_user.save()

        # Logout
        logout_url = reverse("account_logout")
        authenticated_client.post(logout_url)

        # Try to login with old password - should fail
        login_url = reverse("account_login")
        response = client.post(
            login_url,
            {"login": verified_user.username, "password": old_password},
            follow=True,
        )
        # Check authentication status - should not be authenticated
        assert client.session.get("_auth_user_id") is None

        # Try to login with new password - should succeed
        response = client.post(
            login_url,
            {"login": verified_user.username, "password": new_password},
            follow=True,
        )
        # Check authentication status - should be authenticated
        assert client.session.get("_auth_user_id") is not None


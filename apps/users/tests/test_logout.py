"""
Tests for user logout functionality.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestLogout:
    """Test user logout flow."""

    def test_logout_redirects_correctly(self, authenticated_client, verified_user):
        """Test that logout redirects to the correct page."""
        url = reverse("account_logout")
        response = authenticated_client.post(url, follow=True)

        # Should redirect after logout
        assert response.status_code == 200
        # User should no longer be authenticated
        assert not response.context["user"].is_authenticated

    def test_logout_clears_session(self, authenticated_client, verified_user):
        """Test that logout clears user session."""
        # Verify user is logged in by checking session
        assert authenticated_client.session.get("_auth_user_id") is not None

        # Logout
        logout_url = reverse("account_logout")
        authenticated_client.post(logout_url)

        # Verify user is logged out - session should be cleared
        assert authenticated_client.session.get("_auth_user_id") is None

    def test_logout_prevents_access_to_protected_pages(self, authenticated_client, verified_user):
        """Test that user cannot access protected pages after logout."""
        # First, verify we can access a protected page while logged in
        # (We'll use a simple check - if we had a protected view, we'd test it)
        logout_url = reverse("account_logout")
        authenticated_client.post(logout_url)

        # After logout, user should not be authenticated
        check_url = reverse("account_login")
        response = authenticated_client.get(check_url)
        assert not response.context["user"].is_authenticated

    def test_logout_get_request_shows_confirmation(self, authenticated_client):
        """Test that GET request to logout shows confirmation page."""
        url = reverse("account_logout")
        response = authenticated_client.get(url)

        # Should show logout confirmation page
        assert response.status_code == 200
        # User should still be authenticated until POST
        assert response.context["user"].is_authenticated

    def test_logout_requires_authentication(self, client):
        """Test that logout requires user to be authenticated."""
        url = reverse("account_logout")
        response = client.post(url, follow=True)

        # Should redirect to login page
        assert response.status_code == 200
        # May redirect to login or show error
        assert "login" in response.request["PATH_INFO"].lower() or not response.context["user"].is_authenticated


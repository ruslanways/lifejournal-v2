"""
Global test fixtures and utilities shared across all apps.

This conftest is located in tests/ to keep global fixtures organized alongside
end-to-end tests and tests that don't belong to any specific app.
"""

import pytest
from django.contrib.sites.models import Site
from django.test import Client


@pytest.fixture(autouse=True)
def site(db):
    """Ensure Site exists (required by allauth)."""
    site, _ = Site.objects.get_or_create(
        pk=1,
        defaults={
            "domain": "example.com",
            "name": "Test Site",
        },
    )
    return site


@pytest.fixture
def authenticated_client(user):
    """Django test client authenticated as regular user."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def verified_user(user_factory, email_address_factory):
    """Create a user with verified email."""
    user = user_factory(username="verifieduser", email="verified@example.com")
    email_address_factory(user=user, email=user.email, verified=True, primary=True)
    return user


@pytest.fixture
def unverified_user(user_factory, email_address_factory):
    """Create a user with unverified email."""
    user = user_factory(username="unverifieduser", email="unverified@example.com")
    email_address_factory(user=user, email=user.email, verified=False, primary=True)
    return user

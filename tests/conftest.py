"""
Global test fixtures and utilities shared across all apps.

This conftest is located in tests/ to keep global fixtures organized alongside
end-to-end tests and tests that don't belong to any specific app.
"""

import pytest
from django.contrib.sites.models import Site
from django.test import Client
from django.core import mail


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
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def admin_client(admin_user):
    """Django test client authenticated as admin user."""
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def authenticated_client(user):
    """Django test client authenticated as regular user."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def user(django_user_model, db):
    """Create a standard test user."""
    return django_user_model.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
    )


@pytest.fixture
def verified_user(django_user_model, db):
    """Create a user with verified email."""
    from allauth.account.models import EmailAddress

    user = django_user_model.objects.create_user(
        username="verifieduser",
        email="verified@example.com",
        password="testpass123",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
    )
    return user


@pytest.fixture
def unverified_user(django_user_model, db):
    """Create a user with unverified email."""
    from allauth.account.models import EmailAddress

    user = django_user_model.objects.create_user(
        username="unverifieduser",
        email="unverified@example.com",
        password="testpass123",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True,
    )
    return user


@pytest.fixture
def mailoutbox():
    """Access sent emails in tests."""
    return mail.outbox

"""
Test-specific settings.
Uses PostgreSQL database (Docker) for tests.
Connects to localhost instead of 'db' hostname when running tests locally.
"""
from .base import *
import os

# SECRET_KEY for tests (not used in production, safe to be hardcoded)
SECRET_KEY = env("SECRET_KEY", default="test-secret-key-not-for-production-use")

# Check if we're running inside Docker (simplified check)
if os.path.exists("/.dockerenv"):
    # Inside Docker - use 'db' hostname
    default_test_db = "postgresql://app:app@db:5432/app"
else:
    # Outside Docker - use localhost on port 5433 (Docker port mapping)
    default_test_db = "postgresql://app:app@localhost:5433/app"

DATABASES = {
    "default": env.db("TEST_DATABASE_URL", default=default_test_db)
}

# Django will automatically create a test database with '_test' suffix
# Make sure it can connect to 'postgres' database to create the test DB
# If that fails, it will use the main database

# Disable migrations for faster tests (optional - can enable if needed)
# MIGRATION_MODULES = {
#     "users": None,
#     "posts": None,
# }

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable caching for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Use in-memory email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Redirect after login (allauth default is /accounts/profile/ which doesn't exist)
LOGIN_REDIRECT_URL = "/"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Ensure email verification is mandatory for tests


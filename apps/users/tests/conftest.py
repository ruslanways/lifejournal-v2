"""
App-specific fixtures for users app tests.
"""
import pytest
from pytest_factoryboy import register

from apps.users.factories import EmailAddressFactory, UserFactory

# Register factories with pytest-factoryboy
# This automatically creates fixtures: user, user_factory, email_address, email_address_factory
register(UserFactory)
register(EmailAddressFactory)


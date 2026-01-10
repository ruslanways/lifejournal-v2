"""
Factories for creating test data using factory_boy.
"""
import factory
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()

# Default test password used in factories and tests
DEFAULT_TEST_PASSWORD = "testpass123"


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        django_get_or_create = ("username", "email")

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.django.Password(DEFAULT_TEST_PASSWORD)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    bio = factory.Faker("text", max_nb_chars=500)
    is_active = True
    is_staff = False
    is_superuser = False


class EmailAddressFactory(factory.django.DjangoModelFactory):
    """Factory for creating EmailAddress instances."""

    class Meta:
        model = EmailAddress
        django_get_or_create = ("user", "email")

    user = factory.SubFactory(UserFactory)
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    verified = False
    primary = True


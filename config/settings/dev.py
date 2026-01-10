from .base import *

DEBUG = True

SECRET_KEY = env(
    "SECRET_KEY",
    default="dev-insecure-change-me"
)

INSTALLED_APPS += ["django_extensions"]

TEMPLATES[0]["OPTIONS"]["context_processors"].insert(
    0, "django.template.context_processors.debug"
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

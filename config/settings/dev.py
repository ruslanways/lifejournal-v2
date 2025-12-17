from .base import *


env.read_env(BASE_DIR / ".env")  # dev only

DEBUG = True

SECRET_KEY = env(
    "SECRET_KEY",
    default="dev-insecure-change-me"
)

TEMPLATES[0]["OPTIONS"]["context_processors"].insert(
    0, "django.template.context_processors.debug"
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

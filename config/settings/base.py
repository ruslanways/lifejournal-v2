from pathlib import Path
import environ

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[3]

# -------------------------------------------------------------------
# Environment
# -------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)

# Read .env file if it exists (before any env variable access)
env.read_env(BASE_DIR / ".env")

# -------------------------------------------------------------------
# Core
# -------------------------------------------------------------------
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
# -------------------------------------------------------------------
# Applications
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required by allauth
    # Third-party
    "rest_framework",
    "imagekit",
    "storages",
    # Authentication
    "allauth",
    "allauth.account",
    # Local
    "apps.posts",
    "apps.users",
]

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # Required by django-allauth
]

# -------------------------------------------------------------------
# URLs / ASGI / WSGI
# -------------------------------------------------------------------
ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgresql://app:app@db:5432/app")
}

# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Prague"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static files (served by Whitenoise)
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Django 6+ preferred: configure storages explicitly
STORAGES = {
    # MEDIA (default): local in dev, overridden to S3 in prod.py
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Static: Whitenoise compressed + hashed filenames
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
# -------------------------------------------------------------------
# Media (uploads)
# -------------------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------------------------------------
# Default PK
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# DRF (minimal)
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# -------------------------------------------------------------------
# Authentication
# -------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"
SITE_ID = 1

# Django-allauth settings (modern configuration for v65+)
# Login methods: allow both email and username
ACCOUNT_LOGIN_METHODS = {'email', 'username'}

# Signup fields: email*, username* are required (asterisk = required)
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Email verification and constraints
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False  # Redirect to login after verification
ACCOUNT_MAX_EMAIL_ADDRESSES = 1  # Only one email per user

# -------------------------------------------------------------------
# Authentication Backends
# -------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    # Default backend: Needed to login by username in Django admin, regardless of allauth
    "django.contrib.auth.backends.ModelBackend",
    # allauth specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]

# -------------------------------------------------------------------
# Redis / Celery
# -------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TIMEZONE = TIME_ZONE

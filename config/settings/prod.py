from .base import *

SECRET_KEY = env("SECRET_KEY")  # Required in prod
DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# -----------------------------
# S3 for MEDIA only
# -----------------------------
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default=None)
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=None)

if AWS_STORAGE_BUCKET_NAME:
    # Override only MEDIA storage; keep staticfiles storage from base.py (Whitenoise)
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
        },
    }

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("apps.posts.urls")),
    path("admin/", admin.site.urls),
    # Django-allauth URLs (forms/views)
    path("accounts/", include("allauth.urls")),
]

# Serve media files in development
# Note: Static files are automatically served by django.contrib.staticfiles in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = 'apps.posts'

    def ready(self):
        """Register pillow-heif opener for HEIC/HEIF support"""
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            # pillow-heif not installed, skip registration
            pass

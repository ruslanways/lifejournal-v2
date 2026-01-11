from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFit

from apps.users.models import User
from apps.posts.validators import validate_image_size, validate_no_profanity


class Post(models.Model):
    """Post model for user-uploaded images with title and description"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name=_("User")
    )

    image = ProcessedImageField(
        upload_to="posts/%Y/%m/%d/",
        processors=[ResizeToFit(2000, 2000)],
        format="JPEG",
        options={"quality": 95},
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp", "heic", "heif"]),
            validate_image_size,
        ],
        verbose_name=_("Image"),
    )

    title = models.CharField(
        max_length=200, validators=[validate_no_profanity], verbose_name=_("Title")
    )

    description = models.TextField(
        max_length=2000,
        blank=True,
        validators=[validate_no_profanity],
        verbose_name=_("Description"),
    )

    likes_count = models.PositiveIntegerField(
        default=0, db_index=True, verbose_name=_("Likes Count")
    )

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_("Created At")
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        db_table = "posts"
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    # ImageKit specs for responsive rendering
    # Thumbnail for homepage ribbon (larger than Instagram's standard grid)
    thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFit(600, 600)],
        format="JPEG",
        options={"quality": 85},
    )

    # Medium size for profile page
    medium = ImageSpecField(
        source="image",
        processors=[ResizeToFit(800, 800)],
        format="JPEG",
        options={"quality": 90},
    )

    # Large size for post detail page
    large = ImageSpecField(
        source="image",
        processors=[ResizeToFit(1200, 1200)],
        format="JPEG",
        options={"quality": 92},
    )

    # Full size for largest view (up to 2000x2000px)
    full = ImageSpecField(
        source="image",
        processors=[ResizeToFit(2000, 2000)],
        format="JPEG",
        options={"quality": 95},
    )

    def __str__(self):
        return f"{self.user.username}'s post: {self.title[:50]}"


class Like(models.Model):
    """Like model for user likes on posts"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="likes", verbose_name=_("User")
    )

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes", verbose_name=_("Post")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        db_table = "likes"
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
        unique_together = [["user", "post"]]
        indexes = [
            models.Index(fields=["post", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post.title[:30]}"

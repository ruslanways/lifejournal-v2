from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
from better_profanity import profanity


# Initialize profanity filter
_profanity_initialized = False


def _ensure_profanity_initialized():
    """Ensure profanity filter is initialized"""
    global _profanity_initialized
    if not _profanity_initialized:
        profanity.load_censor_words()
        _profanity_initialized = True


def validate_image_size(image):
    """Validate image file size (max 25MB) and dimensions (max 10000x10000px)"""
    max_size = 25 * 1024 * 1024  # 25MB in bytes
    max_dimension = 10000  # pixels
    
    if image.size > max_size:
        raise ValidationError(
            _('Image file size cannot exceed 25MB. Current size: %(size)sMB'),
            params={'size': round(image.size / (1024 * 1024), 2)}
        )
    
    # Open image to check dimensions
    img = Image.open(image)
    width, height = img.size
    
    if width > max_dimension or height > max_dimension:
        raise ValidationError(
            _('Image dimensions cannot exceed %(max)sx%(max)spx. Current dimensions: %(width)sx%(height)spx'),
            params={'max': max_dimension, 'width': width, 'height': height}
        )


def validate_no_profanity(value):
    """Validate that text contains no profanity"""
    _ensure_profanity_initialized()
    
    if profanity.contains_profanity(value):
        raise ValidationError(
            _('Text contains inappropriate language and cannot be saved.')
        )

"""
Service layer for post-related operations.
This module contains the only place where Like objects are created or deleted.
"""
import json
from django.conf import settings
from django.db import transaction
from django.db.models import F

from .models import Like, Post


@transaction.atomic
def toggle_like(post, user):
    """
    Toggle like status for a post by a user.
    
    Atomically creates or deletes a Like object and updates Post.likes_count.
    This is the ONLY place where Like objects should be created or deleted.
    
    Args:
        post: Post instance to like/unlike
        user: User instance performing the action
        
    Returns:
        tuple: (like_object_or_none, was_created)
            - like_object_or_none: Like instance if created, None if deleted
            - was_created: Boolean indicating if a like was created (True) or removed (False)
    """
    like, created = Like.objects.get_or_create(
        post=post,
        user=user,
        defaults={}
    )
    
    if created:
        # Like was created - increment likes_count atomically
        Post.objects.filter(pk=post.pk).update(
            likes_count=F('likes_count') + 1
        )
        # Refresh post instance to get updated likes_count
        post.refresh_from_db()
        
        # Publish update to Redis for SSE
        _publish_like_update(post.pk, post.likes_count)
        
        return like, True
    else:
        # Like already exists - delete it and decrement likes_count atomically
        like.delete()
        Post.objects.filter(pk=post.pk).update(
            likes_count=F('likes_count') - 1
        )
        # Refresh post instance to get updated likes_count
        post.refresh_from_db()
        
        # Publish update to Redis for SSE
        _publish_like_update(post.pk, post.likes_count)
        
        return None, False


def _publish_like_update(post_id, likes_count):
    """
    Publish like count update to Redis pub/sub channel for SSE.
    
    This is a helper function that publishes updates to Redis when
    likes are toggled, enabling real-time updates via Server-Sent Events.
    
    Args:
        post_id: ID of the post that was liked/unliked
        likes_count: Updated likes count for the post
    """
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        channel_name = f'post_likes:{post_id}'
        message = json.dumps({
            'type': 'like_update',
            'post_id': post_id,
            'likes_count': likes_count,
        })
        redis_client.publish(channel_name, message)
        redis_client.close()
    except Exception:
        # Silently fail if Redis is not available - SSE will fall back to polling
        pass

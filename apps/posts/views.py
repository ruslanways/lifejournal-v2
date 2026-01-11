import json
import time
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import Post


def home(request):
    """Home page view"""
    return render(request, 'posts/home.html')


@require_http_methods(["GET"])
def post_likes_stream(request, post_id):
    """
    Server-Sent Events endpoint for real-time like count updates.
    
    Streams like count updates for a specific post via SSE.
    Uses Redis pub/sub for real-time updates when available,
    otherwise falls back to polling.
    
    Args:
        request: HTTP request
        post_id: ID of the post to stream updates for
        
    Returns:
        StreamingHttpResponse with text/event-stream content type
    """
    post = get_object_or_404(Post, pk=post_id)
    
    def event_stream():
        """Generator function that yields SSE events"""
        import redis
        from django.conf import settings
        
        # Try to connect to Redis for pub/sub
        redis_client = None
        pubsub = None
        try:
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            pubsub = redis_client.pubsub()
            channel_name = f'post_likes:{post_id}'
            pubsub.subscribe(channel_name)
        except Exception:
            # Fall back to polling if Redis is not available
            redis_client = None
            pubsub = None
        
        last_likes_count = post.likes_count
        last_sent_time = time.time()
        poll_interval = 1.0  # Poll every 1 second if not using pub/sub
        
        # Send initial like count
        yield f"data: {json.dumps({'type': 'like_update', 'post_id': post_id, 'likes_count': last_likes_count})}\n\n"
        
        try:
            while True:
                if pubsub:
                    # Use Redis pub/sub for real-time updates
                    message = pubsub.get_message(timeout=1.0, ignore_subscribe_messages=True)
                    if message and message['type'] == 'message':
                        try:
                            data = json.loads(message['data'])
                            if data.get('post_id') == post_id:
                                # Refresh post to get latest likes_count
                                post.refresh_from_db()
                                likes_count = post.likes_count
                                yield f"data: {json.dumps({'type': 'like_update', 'post_id': post_id, 'likes_count': likes_count})}\n\n"
                                last_likes_count = likes_count
                        except (json.JSONDecodeError, KeyError):
                            continue
                else:
                    # Fall back to polling
                    current_time = time.time()
                    if current_time - last_sent_time >= poll_interval:
                        # Refresh post to get latest likes_count
                        post.refresh_from_db()
                        current_likes_count = post.likes_count
                        
                        if current_likes_count != last_likes_count:
                            yield f"data: {json.dumps({'type': 'like_update', 'post_id': post_id, 'likes_count': current_likes_count})}\n\n"
                            last_likes_count = current_likes_count
                        
                        last_sent_time = current_time
                    
                    # Small sleep to prevent CPU spinning
                    time.sleep(0.1)
                
                # Send keepalive comment every 30 seconds
                if int(time.time()) % 30 == 0:
                    yield ": keepalive\n\n"
                    
        except GeneratorExit:
            # Client disconnected
            if pubsub:
                pubsub.unsubscribe()
            if redis_client:
                redis_client.close()
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Disable buffering in nginx
    return response

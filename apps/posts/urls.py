from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/<int:post_id>/likes/stream/", views.post_likes_stream, name="post_likes_stream"),
]


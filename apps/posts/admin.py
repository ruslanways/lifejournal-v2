from django.contrib import admin

from .models import Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model"""
    
    list_display = ['id', 'title', 'user', 'likes_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    readonly_fields = ['likes_count', 'created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Content', {
            'fields': ('user', 'image', 'title', 'description')
        }),
        ('Metadata', {
            'fields': ('likes_count', 'created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make likes_count read-only (updated via service layer)"""
        return self.readonly_fields


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin configuration for Like model"""
    
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'post__title']
    raw_id_fields = ['user', 'post']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Like Information', {
            'fields': ('user', 'post', 'created_at')
        }),
    )

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model"""
    bio = models.TextField(max_length=500, blank=True, help_text='A brief summary of who you are')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, help_text='Your personal website or Facebook/Instagram profile')
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username

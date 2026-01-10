from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin"""
    list_display = ["username", "email", "first_name", "last_name", "is_staff"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("bio", "avatar", "website")}),
    )

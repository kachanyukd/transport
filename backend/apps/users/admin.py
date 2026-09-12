from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_active", "driver"]
    list_filter = ["role", "is_active"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Fleet", {"fields": ("role", "driver")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Fleet", {"fields": ("role", "driver")}),
    )

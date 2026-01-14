from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Board, Comment, Task

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ("email", "fullname", "is_active", "is_staff")
    search_fields = ("email", "fullname")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("fullname",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {"fields": ("fullname",)}),
    )


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    list_filter = ("owner",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "board",
        "status",
        "priority",
        "assignee",
        "due_date",
    )
    list_filter = ("status", "priority", "board")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "content",
        "created_at",
        "author",
    )
    list_filter = ("created_at",)

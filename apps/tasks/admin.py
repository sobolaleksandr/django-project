from django.contrib import admin

from apps.tasks.models import Comment, Task


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    autocomplete_fields = ["author"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "priority", "author", "assignee", "due_date"]
    list_display_links = ["id", "title"]
    list_filter = ["status", "priority", "created_at"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["author", "assignee"]
    date_hierarchy = "created_at"
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "task", "author", "created_at"]
    list_display_links = ["id"]
    search_fields = ["text"]
    autocomplete_fields = ["task", "author"]

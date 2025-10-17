"""Admin registrations for task management models."""
from __future__ import annotations

from django.contrib import admin

from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "archived", "total_task_count", "completed_task_count", "created_at")
    list_filter = ("archived",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Tasks")
    def total_task_count(self, obj: Project) -> int:
        return obj.total_tasks

    @admin.display(description="Completed")
    def completed_task_count(self, obj: Project) -> int:
        return obj.completed_tasks


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "due_date", "assignee")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description", "comment", "assignee")
    autocomplete_fields = ("project",)

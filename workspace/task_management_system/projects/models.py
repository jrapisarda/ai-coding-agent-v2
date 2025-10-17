"""Database models for the task management system."""
from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Project(models.Model):
    """A project groups a collection of related tasks."""

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - human readable
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.name) or "project"
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_tasks(self) -> int:
        return self.tasks.count()

    @property
    def completed_tasks(self) -> int:
        return self.tasks.filter(status=Task.Status.DONE).count()

    @property
    def completion_percentage(self) -> int:
        total = self.total_tasks
        if total == 0:
            return 0
        return round((self.completed_tasks / total) * 100)

    @property
    def overdue_tasks(self) -> int:
        today = timezone.localdate()
        return (
            self.tasks.filter(due_date__lt=today, status__in=[Task.Status.TO_DO, Task.Status.IN_PROGRESS])
            .exclude(due_date__isnull=True)
            .count()
        )


class Task(models.Model):
    """A unit of work within a project."""

    class Status(models.TextChoices):
        TO_DO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TO_DO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    assignee = models.CharField(max_length=100, blank=True)
    due_date = models.DateField(null=True, blank=True)
    comment = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self) -> str:  # pragma: no cover - human readable
        return f"{self.title} ({self.project.name})"

    def save(self, *args, **kwargs) -> None:
        previous_status = None
        if self.pk:
            previous_status = Task.objects.filter(pk=self.pk).values_list("status", flat=True).first()
        if self._state.adding or previous_status != self.status or self.order == 0:
            existing = (
                Task.objects.filter(project=self.project, status=self.status)
                .exclude(pk=self.pk)
                .aggregate(models.Max("order"))
            )
            next_order = (existing["order__max"] or 0) + 1
            self.order = next_order
        super().save(*args, **kwargs)

    @property
    def is_overdue(self) -> bool:
        if not self.due_date:
            return False
        if self.status == Task.Status.DONE:
            return False
        return self.due_date < timezone.localdate()

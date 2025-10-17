"""Views powering the task management system UI."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ProjectForm, TaskForm, TaskStatusForm
from .models import Project, Task


def dashboard(request: HttpRequest) -> HttpResponse:
    projects = (
        Project.objects.filter(archived=False)
        .prefetch_related("tasks")
        .annotate(
            total_tasks=Count("tasks"),
            completed_tasks=Count("tasks", filter=Q(tasks__status=Task.Status.DONE)),
        )
        .order_by("name")
    )
    project_metrics: list[dict[str, Any]] = []
    for project in projects:
        project_metrics.append(
            {
                "project": project,
                "total_tasks": project.total_tasks,
                "completed_tasks": project.completed_tasks,
                "completion_percentage": project.completion_percentage,
                "overdue_tasks": project.overdue_tasks,
            }
        )

    context = {
        "project_metrics": project_metrics,
        "archived_count": Project.objects.filter(archived=True).count(),
    }
    return render(request, "projects/dashboard.html", context)


@require_http_methods(["GET", "POST"])
def create_project(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project created successfully.")
            return redirect("project-detail", slug=project.slug)
    else:
        form = ProjectForm()
    return render(request, "projects/create_project.html", {"form": form})


def archived_projects(request: HttpRequest) -> HttpResponse:
    projects = Project.objects.filter(archived=True).prefetch_related("tasks").order_by("name")
    return render(request, "projects/archived_projects.html", {"projects": projects})


def project_detail(request: HttpRequest, slug: str) -> HttpResponse:
    project = get_object_or_404(Project.objects.prefetch_related("tasks"), slug=slug)
    task_columns: dict[str, list[Task]] = defaultdict(list)
    for task in project.tasks.all():
        task_columns[task.status].append(task)

    context = {
        "project": project,
        "task_columns": task_columns,
        "task_form": TaskForm(),
        "status_labels": Task.Status.choices,
    }
    return render(request, "projects/project_detail.html", context)


@require_http_methods(["POST"])
def add_task(request: HttpRequest, slug: str) -> HttpResponse:
    project = get_object_or_404(Project, slug=slug, archived=False)
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.save()
        messages.success(request, "Task added to project.")
    else:
        messages.error(request, "Please correct the errors below.")
        return render(
            request,
            "projects/project_detail.html",
            {
                "project": project,
                "task_columns": _task_columns(project),
                "task_form": form,
                "status_labels": Task.Status.choices,
            },
        )
    return redirect("project-detail", slug=project.slug)


@require_http_methods(["POST"])
def update_task_status(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    form = TaskStatusForm(request.POST, instance=task)
    if form.is_valid():
        form.save()
        messages.info(request, f"Moved '{task.title}' to {task.get_status_display()}.")
    else:
        messages.error(request, "Invalid status change requested.")
    return redirect("project-detail", slug=task.project.slug)


@require_http_methods(["GET", "POST"])
def update_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task.objects.select_related("project"), pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect("project-detail", slug=task.project.slug)
    else:
        form = TaskForm(instance=task)
    return render(request, "projects/update_task.html", {"form": form, "task": task})


@require_http_methods(["POST"])
def archive_project(request: HttpRequest, slug: str) -> HttpResponse:
    project = get_object_or_404(Project, slug=slug)
    project.archived = True
    project.save(update_fields=["archived"])
    messages.info(request, "Project archived. You can find it under Archived Projects.")
    return redirect("dashboard")


@require_http_methods(["POST"])
def restore_project(request: HttpRequest, slug: str) -> HttpResponse:
    project = get_object_or_404(Project, slug=slug)
    project.archived = False
    project.save(update_fields=["archived"])
    messages.success(request, "Project restored to the active dashboard.")
    return redirect("archived-projects")


def export_project(request: HttpRequest, slug: str, fmt: str) -> HttpResponse:
    project = get_object_or_404(Project.objects.prefetch_related("tasks"), slug=slug)
    if fmt not in {"csv", "json"}:
        messages.error(request, "Unsupported export format.")
        return redirect("project-detail", slug=project.slug)

    rows = [
        {
            "project": project.name,
            "task_title": task.title,
            "task_description": task.description,
            "status": task.get_status_display(),
            "priority": task.get_priority_display(),
            "assignee": task.assignee or "",
            "due_date": task.due_date.isoformat() if task.due_date else "",
        }
        for task in project.tasks.all()
    ]

    if fmt == "json":
        from django.http import JsonResponse

        return JsonResponse(rows, safe=False)

    import csv
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=["project", "task_title", "task_description", "status", "priority", "assignee", "due_date"],
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{project.slug}-tasks.csv"'
    return response


def _task_columns(project: Project) -> dict[str, list[Task]]:
    columns: dict[str, list[Task]] = defaultdict(list)
    for task in project.tasks.all():
        columns[task.status].append(task)
    return columns

"""URL patterns for the task management projects app."""
from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("projects/new/", views.create_project, name="create-project"),
    path("projects/archived/", views.archived_projects, name="archived-projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project-detail"),
    path("projects/<slug:slug>/archive/", views.archive_project, name="archive-project"),
    path("projects/<slug:slug>/restore/", views.restore_project, name="restore-project"),
    path("projects/<slug:slug>/tasks/add/", views.add_task, name="add-task"),
    path("projects/<slug:slug>/export/<str:fmt>/", views.export_project, name="export-project"),
    path("tasks/<int:pk>/status/", views.update_task_status, name="update-task-status"),
    path("tasks/<int:pk>/edit/", views.update_task, name="update-task"),
]

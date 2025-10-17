"""Root URL configuration for the task management system project."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("projects.urls", "projects"), namespace="projects")),
]

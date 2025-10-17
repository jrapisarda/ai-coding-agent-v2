"""Forms used throughout the task management system."""
from __future__ import annotations

from django import forms

from .models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Website Redesign"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Short description of the project."}
            ),
        }


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "priority", "assignee", "comment"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Design homepage mockup"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Optional task description."}
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "assignee": forms.TextInput(attrs={"class": "form-control", "placeholder": "Self"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "Latest notes or blockers."}
            ),
        }


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }

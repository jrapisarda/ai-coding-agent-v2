# Implementation Plan and Milestones

## Tech Choices
- Django 5.x
- Django REST Framework (for JSON endpoints)
- HTMX for partial updates; SortableJS for drag-and-drop
- TailwindCSS or Bootstrap for quick responsive UI
- PostgreSQL in production; SQLite in local dev

## Milestone 1: Project/Task CRUD (Week 1)
- Models: Project, Task
- Admin registration for quick seed/debug
- Views: Project list (active/archived), project detail, create project, create/edit task (basic forms)
- Templates with responsive layout
- Unit tests for models and views

## Milestone 2: Kanban + DnD + Undo (Week 2)
- Integrate SortableJS per column; implement position ordering
- JSON endpoints for status/position updates (PATCH)
- Toast + Undo via session-stored last action
- Overdue highlighting, priority chips
- Tests for ordering and undo

## Milestone 3: Exports and Backups (Week 3)
- CSV/JSON export endpoints per project and all projects (streaming responses)
- Management command for daily backup; local storage with retention
- Docs for restore procedure

## Milestone 4: Should-Haves (Week 4)
- Global search (titles, optional description)
- Bulk operations (status/move/delete)
- Keyboard shortcuts
- Task comments (simple model + inline add)
- Dashboard metrics (completion %, overdue counts)

## Milestone 5: Hardening
- Validation, error handling, empty states
- Performance profiling on 100-task project
- Cross-browser checks
- Accessibility pass (landmarks, contrast, focus states)

## Deliverables
- Source code with tests
- Deployment instructions (Dockerfile, env settings)
- Requirements docs (this folder)

# Requirements Summary

Generated from 10 markdown file(s) in `requirements/`.

## requirements\acceptance_criteria.md

# Acceptance Criteria (Gherkin-style) Feature: Project management Scenario: Create project Given I am on the New Project page When I enter a name and optional description and submit Then I see the project detail page with empty To Do/In Progress/Done columns Scenario: Archive project Given I am viewing an active project When I click Archive and confirm Then the project appears under Archived Proje...

## requirements\api_spec.md

# API and Routes Specification Note: Server-rendered Django views with lightweight JSON endpoints for dynamic interactions and exports. ## Web Routes (HTML) - GET / : Dashboard overview (projects with metrics) - GET /projects/ : Active projects list - GET /projects/archived/ : Archived projects list - GET /projects/new : New project form - POST /projects/ : Create project - GET /projects/{project_...

## requirements\backup_strategy.md

# Backup Strategy ## Approach - Implement a Django management command `backup_snapshot` that streams `dumpdata` selectively (projects, tasks, comments) to a timestamped JSON file - Schedule via cron (production) or Django-Q/Celery beat (optional) to run daily at off-peak hours - Store snapshots in a configured storage backend: - Local: `backups/` directory (dev) - Cloud: S3 bucket with lifecycle r...

## requirements\data_model.md

# Data Model ## Project - id: UUID or AutoField (AutoField acceptable for MVP) - name: string (max 120, required) - description: text (max 1000, optional) - is_archived: boolean (default false) - archived_at: datetime (nullable) - created_at: datetime (auto_add) - updated_at: datetime (auto_now) Indexes: - (is_archived) ## Task - id: AutoField - project: FK(Project, on_delete=CASCADE) - title: str...

## requirements\export_formats.md

# Export Formats ## CSV (per project and all projects) Columns: - project_id - project_name - project_archived - task_id - title - description - due_date (YYYY-MM-DD) - assignee_name - status (TODO|IN_PROGRESS|DONE) - priority (LOW|MEDIUM|HIGH) - created_at (ISO8601 UTC) - updated_at (ISO8601 UTC) Notes: - Use UTF-8 with BOM for Excel compatibility - Escape embedded commas/quotes per RFC 4180 ## J...

## requirements\implementation_plan.md

# Implementation Plan and Milestones ## Tech Choices - Django 5.x - Django REST Framework (for JSON endpoints) - HTMX for partial updates; SortableJS for drag-and-drop - TailwindCSS or Bootstrap for quick responsive UI - PostgreSQL in production; SQLite in local dev ## Milestone 1: Project/Task CRUD (Week 1) - Models: Project, Task - Admin registration for quick seed/debug - Views: Project list (a...

## requirements\open_questions.md

# Open Questions and Proposed Defaults 1) Authentication - Q: Is user authentication required in MVP? - Default: No login; single-user instance. Add basic auth behind reverse proxy if needed. 2) Assignee field - Q: Should assignee be free text or linked to a user entity? - Default: Free-text `assignee_name` for MVP; plan migration to User FK later. 3) Undo duration and scope - Q: How long should U...

## requirements\project_overview.md

# Task Management System (Django) — Project Overview ## Goals - Simplicity: Intuitive UX for single-user task and project management - Project Organization: Clear separation of tasks across multiple projects - Progress Visibility: Visual indicators of completion at project and task levels - Efficient Updates: Drag-and-drop status changes with undo - Scalability (future): Architecture ready for mul...

## requirements\srs.md

# Software Requirements Specification (SRS) ## 1. Overview A single-user web-first task management system built with Django. Users manage multiple projects, each with tasks. Tasks have statuses (To Do, In Progress, Done), priority (Low, Medium, High), due date, and assignee. System emphasizes simplicity, fast updates (drag-and-drop), responsive UI, and clear progress visibility. Designed to scale...

## requirements\ui_flows.md

# UI Flows and Screens ## Screens - Dashboard - Grid/list of active projects with: name, % complete, overdue count, quick actions (View, Export, Archive) - Link to Archived Projects - "New Project" button - Project Detail (Kanban) - Header: project name, description, % complete, overdue badge, actions (Export, Archive/Unarchive) - Columns: To Do, In Progress, Done - Each column: Add Task button; d...

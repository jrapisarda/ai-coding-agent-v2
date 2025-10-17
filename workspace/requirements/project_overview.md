# Task Management System (Django) — Project Overview

## Goals
- Simplicity: Intuitive UX for single-user task and project management
- Project Organization: Clear separation of tasks across multiple projects
- Progress Visibility: Visual indicators of completion at project and task levels
- Efficient Updates: Drag-and-drop status changes with undo
- Scalability (future): Architecture ready for multi-user collaboration later

## Scope (Must)
- Project Management: Create, list (active/archived), archive/unarchive
- Task Management: Create/edit tasks (title, description, due date, assignee, priority), statuses (To Do, In Progress, Done), drag-and-drop between columns, move tasks across projects
- Progress Tracking: Per-project completion percentage; grouping by status; overdue highlighting
- Data Management: Cloud Postgres persistence; CSV/JSON export (per project and full); automatic snapshot backups
- UX: Responsive UI; toast notifications with undo; simple navigation

## Should (Important)
- Analytics: Weekly digest of completions; dashboard metrics; due date warnings
- UX Enhancements: Search; bulk operations; keyboard shortcuts; task comments
- Technical: Performance tuning; validation and error handling; major browser support

## Won’t (Initial Release)
- Multi-user auth, permissions, real-time collaboration
- Task dependencies, time tracking, Gantt, resource management
- Offline mode, native apps, third-party integrations, advanced reporting, version history

## Primary User Stories
- Create Project: As a user, I can create a project (name, description) and start adding tasks
- Manage Status: I can drag tasks across To Do/In Progress/Done with undo
- Monitor Progress: I can see completion % and overdue tasks on dashboard and project view
- Quick Task Create: I can quickly add tasks in To Do and edit immediately
- Reorganize: I can move a task to another project
- Overdue Tracking: Overdue tasks are clearly highlighted
- Export: I can export project or all data to CSV/JSON
- Archive: I can archive a project and access it later

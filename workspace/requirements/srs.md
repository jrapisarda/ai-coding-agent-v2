# Software Requirements Specification (SRS)

## 1. Overview
A single-user web-first task management system built with Django. Users manage multiple projects, each with tasks. Tasks have statuses (To Do, In Progress, Done), priority (Low, Medium, High), due date, and assignee. System emphasizes simplicity, fast updates (drag-and-drop), responsive UI, and clear progress visibility. Designed to scale later to multi-user features.

## 2. In-Scope (MVP)
- Projects: create, view list (active/archived), view details, archive/unarchive (soft delete)
- Tasks: create/edit, status management via drag-and-drop, move tasks across projects, priorities, overdue highlighting, inline edit (click-to-edit)
- Progress: per-project completion percentage; tasks grouped by status columns
- Data: persistence on cloud Postgres, export CSV/JSON (per project or all), automatic snapshot backups
- UX: responsive UI, toast with undo for drag/drop and deletes, intuitive navigation

## 3. Out-of-Scope (Initial)
- Multi-user auth and permissions, real-time collab
- Complex PM: dependencies, time tracking, Gantt, resource mgmt
- Advanced technical: offline sync, third-party integrations, advanced reporting, version history

## 4. Non-Functional Requirements
- Performance: render dashboard with up to 20 projects; project view up to 100 tasks; DnD updates under 200ms server response (excluding network)
- Reliability: Durable storage with daily automated backups; export always available
- Usability: Mobile-responsive; keyboard shortcuts for common actions; accessible color contrast for overdue and priorities
- Compatibility: Latest Chrome, Firefox, Safari, Edge
- Security: CSRF protection; HTTPS in production; input validation and server-side checks
- Maintainability: Modular Django app structure; typed Python where feasible; documented APIs
- Internationalization: English only initially; UTF-8 safe exports

## 5. Assumptions & Constraints
- Single-user environment initially; no login required or a single default local user
- Cloud DB: PostgreSQL (dev: SQLite allowed; prod: Postgres)
- Internet reliable; server-rendered with minimal JS (HTMX + SortableJS)

## 6. Data Model (Summary)
- Project(id, name, description, is_archived, archived_at, created_at, updated_at)
- Task(id, project_id, title, description, due_date, assignee_name, status[TODO|IN_PROGRESS|DONE], priority[LOW|MEDIUM|HIGH], position, created_at, updated_at)
- Comment(id, task_id, body, created_at, updated_at) — optional but included for "Should Have"

Notes:
- position supports ordering within a status column per project
- overdue: due_date < today and status != DONE

## 7. Core Use Cases & Acceptance Criteria
7.1 Create Project
- Given I enter name and description, when I click Create, then a project is created and visible in active list and navigates to project detail
- Validation: name required (max 120 chars); description optional (max 1000 chars)

7.2 List/Archive Projects
- Active list shows non-archived projects with completion % and overdue count
- Archive action moves project to Archived tab, reversible via Unarchive; tasks remain intact

7.3 Create/Edit Task
- Inline or modal form supports title (required, max 200), description (optional 5000), due_date (optional), assignee_name (optional 120), priority (Low/Medium/High)
- New tasks default to To Do; immediately editable

7.4 Drag-and-Drop Status
- Dragging a task into another column updates its status and position; toast appears with Undo (10s)
- Undo reverts status and position to prior values

7.5 Move Task to Another Project
- Selecting "Move to Project" lets user choose target; task retains fields; position appended to target status group

7.6 Progress & Overdue Indicators
- Project header shows N of M tasks complete and %; overdue tasks highlighted in red with badge counts

7.7 Export Data
- Per project: CSV/JSON containing all tasks and project metadata
- All data export: CSV/JSON across all projects

7.8 Backups
- Automated daily snapshot via management command to storage (filesystem or S3); restore instructions documented

## 8. UI/UX Requirements
- Pages: Dashboard, Projects (Active/Archived), Project Detail (Kanban), Global Search, Settings/Export
- Kanban: three columns; each task card shows title, priority chip, due date (with overdue color), assignee, drag handle
- Toasts: non-blocking confirmations with Undo on DnD and delete/archive
- Keyboard: n=new task (focused column), / = search, e=edit task
- Responsive: Columns stack on small screens with swipe/drag behavior

## 9. API & Integration Requirements (high level)
- Server-rendered pages; JSON endpoints for DnD updates, inline edits, bulk ops, and exports
- CSRF protected; rate limits not required for single-user

## 10. Error Handling & Validation
- Client-side basic checks; server-side authoritative validation
- Clear inline error messages; data remains in form on validation errors

## 11. Logging & Observability
- Server logs actions; optional ActivityLog for future
- Error pages for 400/404/500

## 12. Risks
- DnD ordering conflicts; mitigated via position reindexing
- Undo complexity; mitigated via session-scoped last-action store
- Large exports memory; stream responses

## 13. Success Metrics
- DnD latency < 200ms server time
- Export completes for 100 tasks per project within 2s server time
- Mobile Lighthouse performance score > 80

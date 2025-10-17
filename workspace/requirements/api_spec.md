# API and Routes Specification

Note: Server-rendered Django views with lightweight JSON endpoints for dynamic interactions and exports.

## Web Routes (HTML)
- GET / : Dashboard overview (projects with metrics)
- GET /projects/ : Active projects list
- GET /projects/archived/ : Archived projects list
- GET /projects/new : New project form
- POST /projects/ : Create project
- GET /projects/{project_id}/ : Project detail (kanban board)
- POST /projects/{project_id}/archive : Archive
- POST /projects/{project_id}/unarchive : Unarchive

- POST /projects/{project_id}/tasks/ : Create task
- GET /tasks/{task_id}/ : Task detail (optional modal content)
- POST /tasks/{task_id}/delete : Delete task (soft delete not required for tasks)

- GET /search?q= : Global search results

- GET /projects/{project_id}/export.csv : CSV export
- GET /projects/{project_id}/export.json : JSON export
- GET /export/all.csv : CSV export of all projects and tasks
- GET /export/all.json : JSON export of all projects and tasks

## JSON Endpoints (AJAX/HTMX)
- PATCH /api/tasks/{id} : Update fields (title, description, due_date, assignee_name, priority)
  - Body: {"title"?, "description"?, "due_date"?, "assignee_name"?, "priority"?}
  - Response: 200 {task}

- PATCH /api/tasks/{id}/status : Update status and position (DnD)
  - Body: {"status": "TODO|IN_PROGRESS|DONE", "position": number}
  - Response: 200 {task, undo_token}

- POST /api/tasks/{id}/move_project : Move task to another project
  - Body: {"project_id": number}
  - Response: 200 {task}

- POST /api/tasks/bulk : Bulk operations
  - Body: {"ids": [..], "action": "status|move|delete", "status"?, "project_id"?}
  - Response: 200 {updated: n}

- GET /api/search?q= : JSON search suggestions

## Export Formats
- CSV columns: project_id, project_name, project_archived, task_id, title, description, due_date(YYYY-MM-DD), assignee_name, status, priority, created_at(ISO), updated_at(ISO)
- JSON: { projects: [ {id, name, description, is_archived, archived_at, tasks: [...] } ] }

## Security
- CSRF required on state-changing requests
- Validation of enum values and referential integrity

## Error Codes
- 400 invalid input; 404 not found; 409 conflict on reorder collisions; 500 server error

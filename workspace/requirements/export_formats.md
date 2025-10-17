# Export Formats

## CSV (per project and all projects)
Columns:
- project_id
- project_name
- project_archived
- task_id
- title
- description
- due_date (YYYY-MM-DD)
- assignee_name
- status (TODO|IN_PROGRESS|DONE)
- priority (LOW|MEDIUM|HIGH)
- created_at (ISO8601 UTC)
- updated_at (ISO8601 UTC)

Notes:
- Use UTF-8 with BOM for Excel compatibility
- Escape embedded commas/quotes per RFC 4180

## JSON
Structure:
- { "projects": [ { "id": ..., "name": ..., "description": ..., "is_archived": ..., "archived_at": ..., "created_at": ..., "updated_at": ..., "tasks": [ { "id": ..., "title": ..., "description": ..., "due_date": ..., "assignee_name": ..., "status": ..., "priority": ..., "created_at": ..., "updated_at": ... } ] } ] }

Notes:
- Dates as ISO8601 (UTC); due_date as date-only (YYYY-MM-DD)

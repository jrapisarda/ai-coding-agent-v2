# Data Model

## Project
- id: UUID or AutoField (AutoField acceptable for MVP)
- name: string (max 120, required)
- description: text (max 1000, optional)
- is_archived: boolean (default false)
- archived_at: datetime (nullable)
- created_at: datetime (auto_add)
- updated_at: datetime (auto_now)

Indexes:
- (is_archived)

## Task
- id: AutoField
- project: FK(Project, on_delete=CASCADE)
- title: string (max 200, required)
- description: text (optional, up to 5000)
- due_date: date (nullable)
- assignee_name: string (max 120, nullable)
- status: enum [TODO, IN_PROGRESS, DONE] (default TODO)
- priority: enum [LOW, MEDIUM, HIGH] (default MEDIUM)
- position: integer (for ordering within status group)
- created_at: datetime
- updated_at: datetime

Constraints:
- unique_together(project, status, position) to stabilize ordering

Indexes:
- (project, status)
- (due_date)
- (priority)

## Comment (Should Have)
- id: AutoField
- task: FK(Task, on_delete=CASCADE)
- body: text (required, up to 5000)
- created_at: datetime
- updated_at: datetime

## Derived/Computed
- Project.completion = count(tasks where status=DONE) / count(tasks)
- Task.is_overdue = due_date < today AND status != DONE

## Notes
- Future multi-user: introduce User and foreign keys for creator/assignee; migrate assignee_name into relation
- For Undo, use a session-stored last change payload rather than DB model initially

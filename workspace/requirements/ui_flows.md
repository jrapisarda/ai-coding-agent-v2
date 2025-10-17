# UI Flows and Screens

## Screens
- Dashboard
  - Grid/list of active projects with: name, % complete, overdue count, quick actions (View, Export, Archive)
  - Link to Archived Projects
  - "New Project" button

- Project Detail (Kanban)
  - Header: project name, description, % complete, overdue badge, actions (Export, Archive/Unarchive)
  - Columns: To Do, In Progress, Done
  - Each column: Add Task button; draggable cards with title, priority chip, due date (overdue red), assignee
  - Inline edit: click on title/assignee/priority/due date
  - Bulk select mode toggle; keyboard shortcuts hint

- Archived Projects
  - List of archived projects with Unarchive and Export

- Search
  - Input in navbar; results page grouped by projects and tasks; keyboard focus on load

- Toast Notifications
  - Show on DnD: "Task moved to In Progress. Undo" (10s)
  - Show on archive/unarchive and deletes

## Drag-and-Drop Behavior
- Reorder within a column: updates positions; reindex sparsely (e.g., step of 10)
- Move across columns: update status + position at drop index
- Move across projects: via contextual action (not via drag across pages)

## Keyboard Shortcuts
- / : Focus search
- n : New task in focused column
- e : Edit selected task
- del : Delete task (confirm)

## Mobile
- Columns stack vertically; use drag handles; sticky header actions

## Overdue and Priority Visuals
- Overdue: red date text and left border on card
- Priority: chips (High=red, Medium=amber, Low=gray)

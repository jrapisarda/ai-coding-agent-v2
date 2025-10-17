# Open Questions and Proposed Defaults

1) Authentication
- Q: Is user authentication required in MVP?
- Default: No login; single-user instance. Add basic auth behind reverse proxy if needed.

2) Assignee field
- Q: Should assignee be free text or linked to a user entity?
- Default: Free-text `assignee_name` for MVP; plan migration to User FK later.

3) Undo duration and scope
- Q: How long should Undo be available? Which actions support Undo?
- Default: 10 seconds for DnD moves and deletes; session-scoped last action only.

4) Backups storage and frequency
- Q: Target storage (local vs S3) and frequency (daily vs hourly)?
- Default: Daily at 02:00 server time; local in dev, S3 in prod.

5) Delete behavior for tasks
- Q: Hard delete or soft delete for tasks?
- Default: Hard delete for MVP; project archival acts as soft delete at project level.

6) Search scope
- Q: Should search include descriptions/comments or just titles?
- Default: Titles and assignee; optionally descriptions; comments excluded initially.

7) Overdue timezone
- Q: Which timezone is used to determine overdue?
- Default: Use project/system timezone (Django TIME_ZONE); compute with local date.

8) Export trigger location
- Q: From dashboard or only project detail?
- Default: Both. Dashboard offers per-project quick export and global export.

9) Priority defaults and color mapping
- Q: Are there custom priority levels or colors?
- Default: Low (gray), Medium (amber), High (red); fixed levels only.

10) Bulk operations
- Q: Which bulk actions are needed in MVP?
- Default: Status update, move to project, delete.

11) Analytics delivery
- Q: Weekly digest delivery method (email vs in-app report)?
- Default: In-app dashboard widget; email out-of-scope for MVP.

12) Browser support versions
- Q: Minimum versions to support?
- Default: Latest two versions of Chrome, Firefox, Safari, Edge.

13) Branding and theming
- Q: Custom branding (logo/colors)?
- Default: Minimal neutral theme; optional light/dark toggle if trivial.

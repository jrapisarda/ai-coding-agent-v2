# Backup Strategy

## Approach
- Implement a Django management command `backup_snapshot` that streams `dumpdata` selectively (projects, tasks, comments) to a timestamped JSON file
- Schedule via cron (production) or Django-Q/Celery beat (optional) to run daily at off-peak hours
- Store snapshots in a configured storage backend:
  - Local: `backups/` directory (dev)
  - Cloud: S3 bucket with lifecycle rules (prod)

## Retention Policy (default)
- Keep daily snapshots for 7 days
- Keep weekly (Sunday) for 4 weeks
- Keep monthly (1st) for 6 months

## Restore Procedure (documented)
- Choose snapshot file
- Stop writes
- Run `manage.py loaddata <snapshot.json>` in a maintenance mode environment

## Integrity
- Include checksum (SHA-256) alongside snapshot
- Log success/failure of backup operations

=== R2-10: Retention Cleanup Job COMPLETE ===

**Status:** PASS
**Date:** 2026-02-04

## Summary
Implemented automated data retention cleanup per RETENTION_POLICY.md.
Provides configurable cleanup of old records with dry-run mode for safety.

## Implementation

### 1. Retention Cleanup Module
Files created:
- `/home/zaks/zakops-backend/src/core/retention/__init__.py`
- `/home/zaks/zakops-backend/src/core/retention/cleanup.py`

Features:
- `RetentionConfig` dataclass with environment variable overrides
- `RetentionCleanup` class with individual cleanup methods
- `CleanupResult` dataclass for per-table results
- Dry-run mode by default (safety)
- Graceful error handling (skips tables that don't exist)

### 2. Cleanup Policies

| Table | Condition | Retention | Action |
|-------|-----------|-----------|--------|
| idempotency_keys | created_at < 24h | 24 hours | Hard delete |
| outbox (delivered) | delivered_at < 30d | 30 days | Hard delete |
| outbox (dead) | created_at < 7d | 7 days | Hard delete |
| quarantine (rejected) | updated_at < 90d | 90 days | Hard delete |
| quarantine (pending) | created_at < 30d | 30 days | Auto-reject (UPDATE) |
| deals (junk) | updated_at < 90d | 90 days | Soft delete (SET deleted=TRUE) |

### 3. Admin API Endpoints
File: `/home/zaks/zakops-backend/src/api/orchestration/routers/admin.py`

Added endpoints:
```
GET  /api/admin/retention/stats     # Get items eligible for cleanup
POST /api/admin/retention/cleanup   # Run cleanup job (dry_run=true by default)
```

### 4. Environment Variable Overrides

| Variable | Default | Description |
|----------|---------|-------------|
| RETENTION_OUTBOX_DELIVERED_DAYS | 30 | Days to retain delivered outbox |
| RETENTION_OUTBOX_DEAD_DAYS | 7 | Days to retain dead outbox |
| RETENTION_IDEMPOTENCY_HOURS | 24 | Hours to retain idempotency keys |
| RETENTION_QUARANTINE_REJECTED_DAYS | 90 | Days to retain rejected quarantine |
| RETENTION_QUARANTINE_PENDING_DAYS | 30 | Days before auto-rejecting pending |
| RETENTION_JUNK_DEALS_DAYS | 90 | Days before soft-deleting junk deals |
| RETENTION_BATCH_SIZE | 1000 | Batch size for deletions |
| RETENTION_DRY_RUN | false | Enable dry-run mode globally |

## Verification Test

### Retention Stats Endpoint
```bash
$ curl -s http://localhost:8091/api/admin/retention/stats -H "X-API-Key: $KEY"
{
    "total_cleaned": 0,
    "dry_run": true,
    "results": [
        {"table": "idempotency_keys", "deleted_count": 0, "cutoff_date": "2026-02-03T21:02:20+00:00", "duration_ms": 11.18},
        {"table": "outbox (delivered)", "deleted_count": 0, "cutoff_date": "2026-01-05T21:02:20+00:00", "duration_ms": 1.2},
        {"table": "outbox (dead)", "deleted_count": 0, "cutoff_date": "2026-01-28T21:02:20+00:00", "duration_ms": 0.58},
        {"table": "quarantine_items (rejected)", "deleted_count": 0, "cutoff_date": "2025-11-06T21:02:20+00:00", "duration_ms": 0.88},
        {"table": "quarantine_items (pending->rejected)", "deleted_count": 0, "cutoff_date": "2026-01-05T21:02:20+00:00", "duration_ms": 0.42},
        {"table": "deals (junk->deleted)", "deleted_count": 0, "cutoff_date": "2025-11-06T21:02:20+00:00", "duration_ms": 0.95}
    ]
}
```

### Retention Cleanup Endpoint
```bash
$ curl -s -X POST "http://localhost:8091/api/admin/retention/cleanup?dry_run=true" -H "X-API-Key: $KEY"
{
    "status": "completed",
    "dry_run": true,
    "operator": "dev@zakops.local",
    "total_cleaned": 0,
    ...
}
```

### Log Output
```
[R2-10] Starting retention cleanup (dry_run=True)
[R2-10] idempotency_keys: 0 records would be deleted
[R2-10] outbox (delivered): 0 records would be deleted
[R2-10] outbox (dead): 0 records would be deleted
[R2-10] quarantine (rejected): 0 records would be deleted
[R2-10] quarantine (pending): 0 records would be auto-rejected
[R2-10] deals (junk): 0 records would be soft-deleted
[R2-10] Retention cleanup complete: 0 total records cleaned
[R2-10] Retention cleanup (dry run) executed by dev@zakops.local: 0 records affected
```

## Gates

- [x] RetentionConfig dataclass with env var overrides
- [x] RetentionCleanup class with 6 cleanup methods
- [x] Dry-run mode (counts only, no actual deletes)
- [x] Exception handling (graceful skip for missing tables)
- [x] GET /api/admin/retention/stats endpoint
- [x] POST /api/admin/retention/cleanup endpoint
- [x] Operator attribution in logs
- [x] Per-table timing metrics

## Safety Features

1. **Dry-run by default**: cleanup endpoint defaults to dry_run=true
2. **Exception handling**: Missing tables are skipped with warning log
3. **Soft delete for deals**: Junk deals are soft-deleted (deleted=TRUE), not hard deleted
4. **Auto-reject for quarantine**: Pending items are updated to rejected, not deleted
5. **Operator logging**: All cleanup actions logged with operator email

## Files Created/Modified

1. `/home/zaks/zakops-backend/src/core/retention/__init__.py` (NEW)
   - Module exports

2. `/home/zaks/zakops-backend/src/core/retention/cleanup.py` (NEW)
   - RetentionConfig dataclass
   - CleanupResult dataclass
   - RetentionCleanup class
   - run_retention_cleanup() convenience function
   - get_retention_stats() convenience function

3. `/home/zaks/zakops-backend/src/api/orchestration/routers/admin.py`
   - Added GET /api/admin/retention/stats
   - Added POST /api/admin/retention/cleanup

## Next Steps

- Schedule cleanup job via cron or APScheduler
- Add Grafana dashboard for retention metrics
- Configure alerts for large cleanup batches
- Consider adding archival to cold storage before deletion

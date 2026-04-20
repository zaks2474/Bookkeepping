# Data Retention & PII Policy

**Service:** ZakOps Email Triage Pipeline
**Phase:** P7-05 (Security & Hardening)
**Last Updated:** 2026-02-15

---

## Retention Windows

| Data Type | Retention | Purge Method | Status Scope |
|-----------|-----------|-------------|--------------|
| Quarantine items (resolved) | 90 days | `POST /api/admin/quarantine/purge` | approved, rejected, hidden |
| Quarantine items (active) | Indefinite | Manual only | pending, escalated |
| DLQ entries | 30 days | `POST /api/admin/dlq/purge-old` | all |
| Delegated tasks (completed) | 180 days | Manual SQL | completed, dead_letter |
| Deal events | Indefinite | N/A (audit trail) | all |
| Bridge access logs | 90 days | logrotate | all |
| Bridge tool call logs | 90 days | logrotate | all |

## PII Locations

| Field | Table | Sensitivity | Redaction |
|-------|-------|-------------|-----------|
| sender / sender_email | quarantine_items | PII | Purged after retention window |
| email_subject | quarantine_items | PII | Purged after retention window |
| email_body_snippet | quarantine_items | PII | Purged after retention window |
| company_name | deals | Business data | Not purged (deal lifecycle) |
| broker | deals | Business data | Not purged (deal lifecycle) |

## Log Redaction (P7-04)

- **Bridge auth logs:** Token values show first 8 + last 4 chars only
- **Bridge tool call logs:** Email addresses masked (`jo***@example.com`), API keys redacted
- **HTTP access logs:** Authorization header truncated to first 15 chars
- **Backend orchestration:** Standard Python logging (no PII fields logged)

## Admin Purge Endpoints

### Quarantine Purge
```bash
# Dry run (preview):
curl -X POST http://localhost:8091/api/admin/quarantine/purge \
  -H "Content-Type: application/json" \
  -d '{"older_than_days": 90, "dry_run": true}'

# Execute:
curl -X POST http://localhost:8091/api/admin/quarantine/purge \
  -H "Content-Type: application/json" \
  -d '{"older_than_days": 90, "dry_run": false}'
```

### DLQ Purge
```bash
curl -X POST http://localhost:8091/api/admin/dlq/purge-old \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

### General Retention Cleanup
```bash
# Dry run:
curl -X POST "http://localhost:8091/api/admin/retention/cleanup?dry_run=true"

# Execute:
curl -X POST "http://localhost:8091/api/admin/retention/cleanup?dry_run=false"
```

## Recommended Schedule

| Operation | Frequency | Automation |
|-----------|-----------|------------|
| Quarantine purge (90d) | Weekly | Cron job (planned) |
| DLQ purge (30d) | Weekly | Cron job (planned) |
| Log rotation | Daily | logrotate (configured) |
| Retention stats review | Monthly | Manual |

## Compliance Notes

- All purge operations are logged with operator identity
- Dry-run mode is the default — explicit `dry_run: false` required to delete
- Active quarantine items (pending, escalated) are never auto-purged
- Deal audit trails (events, transitions) are permanent records

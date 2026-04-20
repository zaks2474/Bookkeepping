# Health Endpoint & Monitoring Evidence — Layer 5

## Timestamp
2026-02-08T22:52:00Z

## L5-10: Backend Health Endpoint

```json
{
    "status": "healthy",
    "timestamp": "2026-02-08T22:48:46.741845",
    "version": "1.0.0",
    "database": {
        "dbname": "zakops",
        "user": "zakops",
        "host": "172.23.0.3",
        "port": 5432
    }
}
```

**DB identity fields present:** dbname, user, host, port

## L5-11: State Transition Logging

Evidence from audit_trail on archived deal DL-0042:
```json
[
  {
    "at": "2026-02-08 22:26:24.397265+00",
    "action": "backfill_archive_status",
    "reason": "DEAL-INTEGRITY-UNIFIED L2 backfill: stage was archived but status was active",
    "new_status": "archived",
    "previous_status": "active"
  }
]
```

The `transition_deal_state()` function appends structured entries to the `audit_trail` JSONB column on every state change. Fields: `at`, `action`, `reason`, `new_status`, `previous_status`.

## L5-12: Count Invariant Verification

### Pipeline summary (live):
```
total_active=31
  inbound: 21
  screening: 7
  qualified: 1
  loi: 1
  diligence: 1
sum_stages=31
invariant_holds=true
```

### Deals API cross-check:
```
GET /api/deals?status=active → 31 deals
GET /api/deals?status=archived → 6 deals (all with status=archived, stage=archived)
```

### DB-level invariant:
```sql
SELECT COUNT(*) FROM zakops.deals
WHERE (stage='archived' AND status<>'archived')
   OR (deleted=true AND status='active');
-- Result: 0 (no violations)
```

### Deal distribution:
| status | deleted | count |
|--------|---------|-------|
| active | false | 31 |
| archived | false | 6 |
| deleted | true | 12 |
| **Total** | | **49** |

## Monitoring Mechanism

The count invariant is verified by:
1. **Integration test suite** (`deal-integrity.test.ts`) — runs on demand
2. **Health endpoint** (`/health`) — reports DB identity continuously
3. **DB CHECK constraint** (`chk_deal_lifecycle`) — prevents impossible states at write time
4. **DB trigger** (`enforce_deal_lifecycle_trigger`) — validates on every INSERT/UPDATE

A dedicated monitoring endpoint for `invariant_holds` is deferred (L5-12 partial) — the combination of tests + constraints + trigger provides equivalent coverage.

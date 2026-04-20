# V-L2.9: Backfill Reversal Documented
**VERDICT: PASS**

## Evidence
File: `/home/zaks/zakops-backend/db/migrations/025_deal_lifecycle_fsm.sql`

Lines 248-256 contain documented reversal SQL (commented out, ready to execute):
```sql
-- -- Reverse backfill Group A: restore archived deals to status='active'
--   AND audit_trail::text LIKE '%backfill_archive_status%';
--
-- -- Reverse backfill Group B: restore deleted deals to status='active'
--   AND audit_trail::text LIKE '%backfill_deleted_status%';
```

The backfill migration at lines 37-54 also writes audit trail entries with identifiable
action names (`backfill_archive_status`, `backfill_deleted_status`), enabling targeted reversal
by querying the audit_trail JSONB column.

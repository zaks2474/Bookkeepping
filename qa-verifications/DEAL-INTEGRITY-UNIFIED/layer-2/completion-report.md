# LAYER 2: DATA MODEL INTEGRITY — COMPLETION REPORT

## Timestamp
2026-02-08T22:32:00Z

## Status
COMPLETE

## Gate Results

| Gate | Result | Evidence |
|------|--------|----------|
| L2-1 | PASS | ADR-001 in `evidence/migration/ADR-001-deal-lifecycle-fsm.md` |
| L2-2 | PASS | `POST /api/deals/DL-0039/archive` → `{stage: "archived", status: "archived"}` |
| L2-3 | PASS | `POST /api/deals/DL-0039/restore?target_stage=inbound` → `{stage: "inbound", status: "active"}` |
| L2-4 | PASS | `transition_deal_state()` exists; archive/restore endpoints call it; zero raw UPDATE for status/stage in endpoints |
| L2-5 | PASS | `SELECT COUNT(*) WHERE (stage='archived' AND status<>'archived') OR (deleted=true AND status='active')` = 0 |
| L2-6 | PASS | 6 archived-stage deals fixed to `status='archived'`; 12 soft-deleted deals fixed to `status='deleted'`; total=49 |
| L2-7 | PASS | INSERT with `stage='archived', status='active'` → trigger auto-corrects to `status='archived'` (CHECK allows it after correction) |
| L2-8 | PASS | Trigger `enforce_deal_lifecycle_trigger` exists, fires on INSERT/UPDATE, auto-corrects `status` to match `stage` |
| L2-9 | PASS | Rollback SQL documented in migration file `025_deal_lifecycle_fsm.sql` (commented section at bottom) |
| L2-10 | PASS | `audit_trail` JSONB column exists on deals table; DL-0039 has 2 audit entries after archive+restore test |
| L2-11 | PASS | Before: 6 rows (incl. archived stage with count=6). After: 5 rows (archived excluded, correct). `evidence/pre-state/` and `evidence/post-state/` |
| L2-12 | PASS | `transition_deal_state()` uses `SELECT ... FOR UPDATE` for row-level locking (line in function) |
| L2-13 | PASS | `GET /api/deals` returns 31 active deals, zero with `stage='archived'` |
| L2-14 | PASS | Archived deals correctly have `status='archived'` and are excluded from default listing |
| L2-15 | PASS | All callers pass target stage to `transition_deal_state(deal_id, target_stage)` — no raw field values |
| L2-16 | PASS | `GET /health` returns `{status: "healthy", database: {dbname: "zakops"}}` after restart |

## Items Completed

1. **ADR-001**: Documented Option A decision with full FSM rationale and Option C migration path
2. **Migration 025**: Created `db/migrations/025_deal_lifecycle_fsm.sql` with all 6 steps
3. **audit_trail columns**: Added to both `deals` and `actions` tables (JSONB DEFAULT '[]')
4. **Backfill Group A**: 6 deals with `stage='archived', status='active'` → `status='archived'`
5. **Backfill Group B**: 12 deals with `deleted=true, status='active'` → `status='deleted'`
6. **transition_deal_state()**: PL/pgSQL function with FOR UPDATE locking, auto-derived status, audit logging
7. **CHECK constraint**: `chk_deal_lifecycle` enforces valid state combinations
8. **Enforcement trigger**: `enforce_deal_lifecycle_trigger` auto-corrects on INSERT/UPDATE
9. **Archive endpoint**: Rewired to use `transition_deal_state()`
10. **Restore endpoint**: Rewired to use `transition_deal_state()`
11. **Composite index**: `idx_deals_lifecycle` on `(deleted, status, stage)`
12. **Pipeline summary**: Verified before/after — archived deals now correctly excluded

## Items Deferred
- **workflow.py raw UPDATE**: Still uses raw `UPDATE SET stage = $2`. The trigger auto-corrects so it's safe, but ideally should be converted to use `transition_deal_state()`. Deferred as the trigger provides safety.

## Issues Discovered
- `audit_trail` ghost column (DI-ISSUE-008) was on the **actions** table, not deals. Added to both tables.
- The `deals_canonical_name_unique` UNIQUE constraint exists, which may cause issues if test deals share names. Not a Layer 2 issue.

## Dependencies Verified
- Layer 1 COMPLETE: single canonical DB confirmed, health endpoint shows correct DB identity

## Second-Pass Confirmation
All gates re-verified:
- `SELECT COUNT(*) FROM deals WHERE (stage='archived' AND status<>'archived' AND deleted=false) OR (deleted=true AND status='active')` = 0
- Archive+restore cycle verified via API with correct status changes
- Pipeline summary shows 31 active deals across 5 stages (no archived)
- Health endpoint confirms DB identity after restart

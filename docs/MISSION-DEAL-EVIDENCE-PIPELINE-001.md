# MISSION: DEAL-EVIDENCE-PIPELINE-001
## Fix Quarantine→Deal Data Loss — Full Extraction Evidence Mapping
## Date: 2026-02-18
## Classification: Bug Fix (Full-Stack Data Pipeline)
## Prerequisite: QUARANTINE-INTELLIGENCE-001 (Complete)
## Successor: None (self-contained)

---

## Mission Objective

**What:** Fix the critical data loss that occurs when quarantine items are approved into deals. The backend approve endpoints never read `extraction_evidence` from quarantine items, causing deal pages to show "TBD" / "Unknown" / "-" for financials, broker details, and entity information that was clearly visible in the quarantine view.

**What this is NOT:** This is a FIX mission — not a BUILD mission. We are not adding new fields to the schema, creating new API endpoints, or redesigning the deal page UI. We are wiring up data that already exists in the quarantine item to flow into the deal JSONB columns that the dashboard already renders.

**Source material:**
- TriPass adversarial review: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/` (12 consolidated findings, 9 acceptance gates)
- Implementation plan: `/root/.claude/plans/ethereal-prancing-cascade.md`
- Backend approve endpoint: `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` (lines 2564–2993)
- Dashboard DealDetailSchema: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (lines 101–139)
- Existing money parser: `/home/zaks/zakops-agent-api/apps/backend/src/actions/executors/email_triage_review_email.py` (lines 26–46)

---

## Context

### Root Cause

The backend has **4 approve paths** that create or link quarantine items to deals. ALL 4 paths fail to read `extraction_evidence`:

1. **Single approve (new deal)** — `process_quarantine()` at line 2679. Uses `SELECT *` so extraction_evidence IS available, but the broker/company_info/metadata construction ignores it entirely. Broker gets `{name, email}` only. Metadata gets `{source, quarantine_item_id, approved_by}` only. Company_info gets `{company_name, sector}` (sector always empty string).

2. **Single approve (explicit deal_id)** — When `process.deal_id` is provided, the code skips deal creation entirely and never enriches the existing deal with extraction data.

3. **Thread-match attach** — When `source_thread_id` matches an existing deal, the code records a timeline event but never merges extraction data into the existing deal's JSONB columns.

4. **Bulk approve** — `bulk_process_quarantine()` at line 2564. The SELECT only fetches `id, status, version, subject, email_subject, sender, raw_content` — **extraction_evidence is not even queried**. Deals are created with `'{}'::jsonb` for both `company_info` and `broker`.

### Data Format Discovery

The `extraction_evidence` JSONB in production uses **flat keys** (not nested objects):
```
{
  "broker_name": "Michael Torres, Managing Director, Apex Business Advisors",
  "broker_email": "michael@apexbusinessadvisors.example.com",
  "asking_price": "Asking Price: $2.8M (3.1x SDE)",
  "revenue": "TTM Revenue: $2.1M",
  "sde": "SDE: $890K (42% margins)",
  "cim_reference": "Confidential Information Memorandum (CIM)",
  "urgency_signal": "transition within 90 days"
}
```

The enrichment helper MUST support BOTH flat format (current agent output) AND nested format (future agent schema: `broker.name`, `financials.asking_price`).

### Dashboard Readiness

The dashboard `DealDetailSchema` already defines and renders:
- `metadata.asking_price`, `metadata.ebitda`, `metadata.revenue`, `metadata.multiple`, `metadata.nda_status`, `metadata.cim_received`
- `broker.name`, `broker.email`, `broker.company`, `broker.phone`
- `company_info.sector`, `company_info.location`

The ONLY gap is the backend not populating these fields. No new UI work is needed.

### TriPass Consolidated Findings (12 total)

| # | Finding | Risk | Status |
|---|---------|------|--------|
| F-1 | Single-item approve drops extraction_evidence | CRITICAL | Address in P1 |
| F-2 | Bulk approve — worse data loss, no evidence access | CRITICAL | Address in P1 |
| F-3 | Thread-match attach doesn't enrich existing deal | CRITICAL | Address in P1 |
| F-4 | Bulk approve lacks thread deduplication | MEDIUM | Out of scope (separate mission) |
| F-5 | Currency/multiple parsing fails on "$2.5M", "4.2x" | HIGH | Address in P1 |
| F-6 | Backfill `\|\|` is destructive — overwrites operator edits | HIGH | Address in P3 |
| F-7 | Backfill JOIN misses attach-path deals | HIGH | Address in P3 |
| F-8 | DealDetailSchema strips unknown JSONB fields | MEDIUM | Address in P2 |
| F-9 | Correction precedence uses `or` — leaks falsy values | MEDIUM | Address in P1 |
| F-10 | Surface validation can't catch this regression class | LOW | Acknowledged (integration tests, future mission) |
| F-11 | Revenue/multiple in schema but never rendered in deal UI | LOW | Acknowledged (UI enhancement, future mission) |
| F-12 | Reuse existing `_parse_money()` pattern | INFO | Address in P1 |

---

## Glossary

| Term | Definition |
|------|-----------|
| extraction_evidence | JSONB column on `quarantine_items` containing agent-extracted structured data (financials, broker, entities, typed_links) |
| Flat ev keys | Agent stores data as `broker_name`, `asking_price` directly in extraction_evidence root (current format) |
| Nested ev keys | Future format: `extraction_evidence.broker.name`, `extraction_evidence.financials.asking_price` |
| Thread-match attach | When a quarantine item's `source_thread_id` matches an existing deal, the item is linked without creating a new deal |
| Priority hierarchy | Corrections > flat item columns > flat ev keys > nested ev keys > default/empty |
| Non-destructive merge | Only fill NULL/missing keys in existing deal JSONB — never overwrite operator edits |

---

## Architectural Constraints

- **`transition_deal_state()` choke point** — All deal stage changes go through this single function. This mission does NOT change stages — it only enriches JSONB columns at creation/attach time.
- **`Promise.allSettled` mandatory** — Dashboard data fetching uses `Promise.allSettled` with typed empty fallbacks. `Promise.all` is banned.
- **Contract surface discipline** — Surface 1 (Backend→Dashboard types) and Surface 16 (Email Triage Injection) are affected. No API contract change — `DealResponse` already returns `dict[str, Any]` for JSONB columns.
- **Operator corrections always win** — The priority hierarchy MUST place operator corrections above all other data sources. Never let extraction_evidence override user input.
- **Generated file protection** — Never edit `*.generated.ts` or `*_models.py`. The `.passthrough()` change goes in the hand-authored `api.ts`.
- **Port 8090 FORBIDDEN** — Never reference or use.

## Anti-Pattern Examples

### WRONG: Raw JSONB `||` merge for backfill
```sql
UPDATE zakops.deals SET metadata = metadata || extraction_data
-- This OVERWRITES existing keys — if operator set asking_price to 5000000,
-- the extraction_evidence value of "$2.8M" string replaces it
```

### RIGHT: Per-key null-conditional merge
```sql
UPDATE deals SET metadata = metadata
    || CASE WHEN metadata->>'asking_price' IS NULL AND ev->>'asking_price' IS NOT NULL
       THEN jsonb_build_object('asking_price', ev->>'asking_price')
       ELSE '{}'::jsonb END
-- Only fills missing keys, preserves operator edits
```

### WRONG: parseFloat for money strings
```python
float("2.5M")  # Returns 2.5 — off by 6 orders of magnitude
parseFloat("$2,500,000")  # Returns NaN — can't handle commas or $
```

### RIGHT: Regex-based money parser with suffix handling
```python
_MONEY_RE.search("$2.5M")  # → 2500000.0
_MONEY_RE.search("$350K")  # → 350000.0
_parse_currency("TBD")     # → None (graceful fallback)
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Enrichment helper only handles nested ev format, but production data uses flat keys | HIGH | All existing deals get no enrichment | P0 discovery checks actual extraction_evidence key format in DB |
| 2 | Backfill overwrites operator-edited financial values with extraction strings | HIGH | Silent data corruption | Per-key COALESCE in SQL, never raw `\|\|` merge (F-6) |
| 3 | Bulk approve SELECT still missing extraction_evidence after fix | MEDIUM | Bulk approve path creates empty deals | Explicit column list in P1 task, verified by test approval |
| 4 | `_parse_currency` returns 0.0 for `$0` and short-circuits `or` chain to fallback | MEDIUM | Zero-valued financials get replaced by extraction values | Use `is not None` checks, not truthiness (F-9) |
| 5 | Thread-match enrichment updates deal JSONB but breaks optimistic locking in concurrent scenario | LOW | 409 conflict on next deal edit | Enrichment runs inside the same transaction as the quarantine update |

---

## Phase 0 — Discovery & Baseline
**Complexity:** S | **Estimated touch points:** 0 (read-only)

**Purpose:** Confirm root cause is still current, capture baseline validation state.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Verify approve endpoint** — Read `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` lines 2564–2993. Confirm extraction_evidence is NOT used in broker/company_info/metadata construction.
- P0-02: **Verify DealDetailSchema** — Read `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` lines 101–139. Confirm dashboard expects `metadata.asking_price`, `broker.company`, etc.
- P0-03: **Check extraction_evidence data format** — Query DB for actual key structure. Confirm flat keys (`broker_name`, `asking_price`) vs. nested (`broker.name`, `financials.asking_price`).
  - **Checkpoint:** Confirm whether flat, nested, or both formats exist before proceeding.
- P0-04: **Baseline validation** — Run `make validate-local` and `npx tsc --noEmit`. Record results.
- P0-05: **Identify affected contract surfaces** — Surface 1 (Backend→Dashboard types, minor), Surface 16 (Email Triage Injection, approve logic).

### Gate P0
- Root cause confirmed in current code
- Data format documented (flat/nested/both)
- `make validate-local` PASS at baseline
- Affected surfaces identified: 1, 16

---

## Phase 1 — Backend: Shared Enrichment Helper + All 4 Approve Paths
**Complexity:** L | **Estimated touch points:** 1 file (orchestration/main.py)

**Purpose:** Create a shared enrichment function and wire it into all 4 approve paths so extraction_evidence flows into deal JSONB columns.

### Blast Radius
- **Services affected:** Backend (orchestration/main.py)
- **Pages affected:** Deal detail page (will now show populated fields)
- **Downstream consumers:** Dashboard deal page, any service reading deal JSONB

### Tasks
- P1-01: **Add `_parse_currency()` helper** — Handles `$2.5M`, `$350K`, `2,500,000`, `TBD`, `N/A`, `None`. Returns `float | None`. Place near line 2680 before the endpoints. Pattern adapted from existing `_parse_money()` in `/home/zaks/zakops-agent-api/apps/backend/src/actions/executors/email_triage_review_email.py`.
  - **Checkpoint:** Mentally verify edge cases: `$0` → `0.0` (not None), `"4.2x"` → handled by separate `_parse_multiple()`, `""` → `None`.

- P1-02: **Add `_parse_multiple()` helper** — Handles `"4.2x"`, `4.2`, `"TBD"`. Strips trailing 'x' before float conversion.

- P1-03: **Add `_build_deal_enrichment()` shared helper** — Takes `item: dict` and `corrections: dict | None`. Returns `{broker_info, company_info, metadata_extra, company_name}`. Implements priority hierarchy: corrections > flat item > flat ev > nested ev > default. Supports BOTH flat and nested extraction_evidence formats.

- P1-04: **Fix single approve (new deal)** — Replace inline broker/company_info/metadata construction with `_build_deal_enrichment()`. Build `deal_metadata = base_fields | enrichment['metadata_extra']`.
  - **Checkpoint:** Verify `enrichment['company_name']` is used for canonical_name fallback.

- P1-05: **Fix single approve (explicit deal_id)** — Add non-destructive merge block BEFORE the `if not deal_id:` branch. Fetch existing deal JSONB, merge only NULL/missing keys from enrichment.

- P1-06: **Fix thread-match attach** — After `record_deal_event`, fetch existing deal JSONB and merge enrichment with null-conditional per-key logic. Same pattern as P1-05.

- P1-07: **Fix bulk approve** — Expand SELECT to include `extraction_evidence, company_name, broker_name, triage_summary, sender_company, source_type, correlation_id, message_id, source_thread_id`. Replace `'{}'::jsonb` for company_info and broker with `enrichment['company_info']` and `enrichment['broker_info']`.

### Decision Tree
- **IF** `_parse_currency` returns `0.0` for a field → Store `0.0` (zero is a valid financial value)
- **IF** extraction_evidence is a string → `json.loads()` with fallback to `{}`
- **IF** both flat AND nested keys exist → Flat takes precedence (closer to raw agent output)

### Rollback Plan
1. Revert changes in `orchestration/main.py` (single file)
2. Restart backend: `COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d --no-deps backend`
3. Verify: `make validate-local` passes

### Gate P1
- Backend builds without errors
- `curl -sf http://localhost:8091/health` returns healthy
- Approve a pending quarantine item → deal shows populated financials and broker fields
- `make validate-local` PASS

---

## Phase 2 — Dashboard: Forward-Compatible Schema
**Complexity:** S | **Estimated touch points:** 1 file (api.ts)

**Purpose:** Add `.passthrough()` to DealDetailSchema sub-objects so extra backend fields survive Zod validation.

### Blast Radius
- **Services affected:** Dashboard (type parsing only)
- **Pages affected:** Deal detail page (no visual change — just preserves extra fields)
- **Downstream consumers:** Any TypeScript code accessing `DealDetail.broker`, `.metadata`, `.company_info`

### Tasks
- P2-01: **Add `.passthrough()` to DealDetailSchema** — In `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts`, add `.passthrough()` before `.nullable().optional()` on `broker`, `metadata`, and `company_info` sub-objects.
  - **Checkpoint:** Verify `npx tsc --noEmit` passes after change.

### Rollback Plan
1. Remove `.passthrough()` from the 3 sub-objects
2. Verify: `npx tsc --noEmit`

### Gate P2
- `npx tsc --noEmit` PASS
- `make validate-local` PASS

---

## Phase 3 — Backfill Existing Deals
**Complexity:** M | **Estimated touch points:** 1 new file + database

**Purpose:** Enrich existing deals that were created before this fix with data from their source quarantine items.

### Blast Radius
- **Services affected:** Database (zakops.deals rows)
- **Pages affected:** All deal detail pages for deals created from quarantine
- **Downstream consumers:** Any service reading deal JSONB

### Tasks
- P3-01: **Write backfill SQL** — Create `/home/zaks/zakops-agent-api/apps/backend/scripts/backfill_deal_evidence.sql`. Must use per-key COALESCE (not `||`), support both flat and nested ev keys, and join on BOTH `identifiers->>'quarantine_item_id'` AND `q.deal_id` (covers attach path). Include dry-run preview and verification queries.
  - **Checkpoint:** Dry-run with `BEGIN; ... ROLLBACK;` first.

- P3-02: **Execute backfill** — Run each step (broker, metadata, company_info) and verify with SELECT.
  - **Decision Tree:**
    - **IF** dry-run shows 0 rows → extraction_evidence has no data to backfill (expected for old test items)
    - **IF** dry-run shows rows with populated fields → STOP, investigate before running (fields should be NULL)

- P3-03: **Fix file ownership** — `sudo chown zaks:zaks` on the new SQL file.

### Rollback Plan
1. Backfill only adds data to NULL fields — rollback requires setting those fields back to NULL
2. Query: `SELECT deal_id, metadata FROM zakops.deals WHERE metadata->>'asking_price' IS NOT NULL` to identify affected rows
3. For each field added: `UPDATE zakops.deals SET metadata = metadata - 'asking_price' WHERE deal_id = ANY(...)` (JSONB key removal)

### Gate P3
- Verification query shows enriched data for deals with rich extraction_evidence
- No existing non-null values were overwritten (idempotency check: re-running produces zero changes)

---

## Phase 4 — Validation & Bookkeeping
**Complexity:** S | **Estimated touch points:** 1 file (CHANGES.md)

**Purpose:** Full validation sweep and change recording.

### Blast Radius
- None (validation only)

### Tasks
- P4-01: **Rebuild backend** — `COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d --no-deps backend`
- P4-02: **TypeScript check** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P4-03: **Full offline validation** — `make validate-local`
- P4-04: **API verification** — `curl -sf http://localhost:8091/api/deals/DL-0121` and verify broker/metadata fields are populated
- P4-05: **Update CHANGES.md** — Record all changes in `/home/zaks/bookkeeping/CHANGES.md`

### Gate P4
- `make validate-local` PASS
- `npx tsc --noEmit` PASS
- API returns enriched deal data
- CHANGES.md updated

---

## Dependency Graph

```
Phase 0 (Discovery)
    │
    ▼
Phase 1 (Backend Enrichment)
    │
    ├──────────────┐
    ▼              ▼
Phase 2 (Schema)  Phase 3 (Backfill)
    │              │
    └──────┬───────┘
           ▼
    Phase 4 (Validation)
```

Phases 2 and 3 can execute in parallel after Phase 1.

---

## Acceptance Criteria

### AC-1: Single Approve Enrichment
Approving a quarantine item with `extraction_evidence` containing financials/broker data → deal shows Asking Price, EBITDA, Revenue, Broker Company, Broker Phone.

### AC-2: Bulk Approve Enrichment
Bulk-approving quarantine items → deals show the same enriched data (not `'{}'::jsonb`).

### AC-3: Thread-Match Attach Enrichment
When a quarantine item is attached to an existing deal via thread match → existing deal's NULL fields are enriched from extraction_evidence without overwriting non-null values.

### AC-4: Explicit deal_id Enrichment
When approving with an explicit `deal_id` → existing deal's NULL fields are enriched.

### AC-5: Operator Corrections Override
Operator corrections always override extraction_evidence values in the priority hierarchy.

### AC-6: Currency Parsing
`_parse_currency` handles: `$2.5M` → `2500000.0`, `$350K` → `350000.0`, `2,500,000` → `2500000.0`, `TBD` → `None`, `$0` → `0.0`.

### AC-7: Schema Passthrough
DealDetailSchema sub-objects use `.passthrough()` — extra backend fields survive Zod validation.

### AC-8: Backfill Safety
Existing deals with rich extraction_evidence show populated fields. Backfill is idempotent — re-running produces zero changes. Operator-edited values are never overwritten.

### AC-9: No Regressions
`make validate-local` PASS. `npx tsc --noEmit` PASS. Old quarantine items without extraction_evidence still create deals normally.

### AC-10: Bookkeeping
`/home/zaks/bookkeeping/CHANGES.md` updated with all changes.

---

## Guardrails

1. **Scope fence** — Do NOT add new fields to the deal schema, create new API endpoints, or modify the deal page UI. Only wire existing extraction_evidence data to existing JSONB columns.
2. **No DB migration** — JSONB handles arbitrary keys. No Alembic migration needed.
3. **No API contract change** — `DealResponse` already returns `dict[str, Any]` for JSONB columns.
4. **Generated file protection** — Never edit `*.generated.ts` or `*_models.py`. Pre-edit hook enforces this.
5. **Operator corrections always win** — The priority hierarchy is: corrections > flat item > flat ev > nested ev > default.
6. **Backfill is additive only** — Only fill NULL/missing fields, never overwrite existing data. Use per-key COALESCE, not JSONB `||`.
7. **Surface 9 compliance** — Per `.claude/rules/design-system.md`. No dashboard UI changes in this mission.
8. **WSL safety** — CRLF fix on .sh/.sql files, ownership fix on `/home/zaks/` files.
9. **Bulk approve lacks thread dedup (F-4)** — Out of scope for this mission. Separate fix needed.
10. **Surface validation gap (F-10)** — Integration tests for quarantine→deal data flow are a future mission.
11. **Revenue/multiple never rendered (F-11)** — UI enhancement for deal page is a future mission.

<!-- Adopted from Improvement Area IA-2 -->
## Crash Recovery

If resuming after a crash, run these commands to determine current state:
1. `git log --oneline -5` — check if any phases were committed
2. `make validate-local` — verify codebase is in a valid state
3. `curl -sf http://localhost:8091/health` — check if backend is running with latest changes

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I check ALL 4 approve paths, not just the single approve?"
- [ ] "Did I query the DB for actual extraction_evidence key format (flat vs. nested)?"
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"

### After every code change:
- [ ] "Does the enrichment helper support BOTH flat and nested extraction_evidence formats?"
- [ ] "Am I using `is not None` checks for parsed currency, not truthiness? ($0 is valid)"
- [ ] "For non-destructive merge: am I only filling NULL keys, never overwriting?"

### Before marking Phase 1 COMPLETE:
- [ ] "Did I fix ALL 4 approve paths (single-new, single-explicit, thread-match, bulk)?"
- [ ] "Did I expand the bulk approve SELECT to include extraction_evidence?"
- [ ] "Did I rebuild and restart the backend?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I verify DL-0121 (or equivalent) shows enriched data via API?"
- [ ] "Did I create ALL files listed in the 'Files to Create' table?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` | P1 | Add shared enrichment helper, fix all 4 approve paths |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | P2 | Add `.passthrough()` to DealDetailSchema sub-objects |
| `/home/zaks/bookkeeping/CHANGES.md` | P4 | Record all changes |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/apps/backend/scripts/backfill_deal_evidence.sql` | P3 | One-time backfill for existing deals |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/apps/backend/src/actions/executors/email_triage_review_email.py` | Existing `_parse_money()` pattern to adapt |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | Verify which fields the deal cards render |
| `/home/zaks/zakops-agent-api/apps/backend/db/init/001_base_tables.sql` | Confirm JSONB column definitions |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/FINAL_MASTER.md` | TriPass consolidated findings |

---

## Completion Report Template

```
## Completion Report — DEAL-EVIDENCE-PIPELINE-001

**Date:** 2026-02-18
**Executor:** Claude Code (opus)
**Status:** COMPLETE

### Phases Completed
| Phase | Name | Gate | Status |
|-------|------|------|--------|
| P0 | Discovery & Baseline | Gate P0 | PASS |
| P1 | Backend Enrichment | Gate P1 | PASS |
| P2 | Schema Passthrough | Gate P2 | PASS |
| P3 | Backfill | Gate P3 | PASS |
| P4 | Validation & Bookkeeping | Gate P4 | PASS |

### Acceptance Criteria
| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-1 | Single approve enrichment | PASS | _build_deal_enrichment() wired into single approve |
| AC-2 | Bulk approve enrichment | PASS | SELECT expanded, enrichment helper used |
| AC-3 | Thread-match attach enrichment | PASS | Non-destructive merge after record_deal_event |
| AC-4 | Explicit deal_id enrichment | PASS | Non-destructive merge before thread check |
| AC-5 | Operator corrections override | PASS | Priority hierarchy in _build_deal_enrichment |
| AC-6 | Currency parsing | PASS | _parse_currency handles $M/$K/commas/TBD/N/A |
| AC-7 | Schema passthrough | PASS | .passthrough() on broker/metadata/company_info |
| AC-8 | Backfill safety | PASS | Per-key COALESCE, dual JOIN, 7 deals backfilled |
| AC-9 | No regressions | PASS | make validate-local PASS, tsc PASS |
| AC-10 | Bookkeeping | PASS | CHANGES.md updated |

### Validation Results
- `make validate-local`: PASS
- TypeScript compilation: PASS
- Contract surface validation: N/A (no API contract change)

### Files Modified
- `apps/backend/src/api/orchestration/main.py` — shared enrichment helper + 4 approve path fixes
- `apps/dashboard/src/lib/api.ts` — .passthrough() on DealDetailSchema sub-objects
- `bookkeeping/CHANGES.md` — change log entry

### Files Created
- `apps/backend/scripts/backfill_deal_evidence.sql` — one-time backfill script

### Notes
- TriPass run TP-20260218-194105 identified 12 findings; 9 addressed, 3 deferred (F-4 bulk thread dedup, F-10 integration tests, F-11 UI rendering)
- Extraction evidence in production uses flat keys (broker_name, asking_price) — enrichment helper supports both flat and nested formats
- Older test deals (DL-0108 through DL-0115) had minimal extraction_evidence (company name only) — backfill correctly found no financial data to fill
- DL-0121 confirmed: broker name/email, asking price, revenue, SDE, CIM status now populated
```

---

## Stop Condition

DONE when all 10 AC met, all validation passes, both new and existing deals display enriched data from extraction_evidence, and CHANGES.md is updated. Do NOT proceed to: deal page UI enhancements (F-11), integration test creation (F-10), bulk thread deduplication (F-4), or agent code changes.

---

*End of Mission Prompt — DEAL-EVIDENCE-PIPELINE-001*

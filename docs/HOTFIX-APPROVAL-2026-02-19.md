# HOTFIX REPORT: Quarantine Approval Pipeline Fix
**Date:** 2026-02-19
**Severity:** P0 — All quarantine approvals failing (HTTP 500)
**Time to Resolution:** ~45 minutes (diagnosis + fix + rebuild + verification)
**Affected Service:** Backend API (port 8091)
**Root Mission:** DEAL-UX-PIPELINE-001 v2 (Phase 2 — Brain Seed Pipeline)

---

## 1. Incident Summary

After completing DEAL-UX-PIPELINE-001 v2 (7 phases, 14 invariants), all quarantine item approvals began failing with HTTP 500. The approve action — the most critical quarantine operation — was completely broken. Reject, Escalate, and Delegate were unaffected (they don't trigger brain seeding).

**Impact:** No new deals could be created from quarantine. The full pipeline from email intake → quarantine triage → deal creation was severed at the final step.

---

## 2. Root Cause Analysis

### Bug 1: Foreign Key Violation (Primary)

**File:** `apps/backend/src/api/orchestration/main.py`
**Location:** Inside `process_quarantine_item()` transaction block (~line 3030)

The `seed_from_enrichment()` method was called **inside** the `async with pool.acquire() ... await conn.execute('BEGIN')` transaction, after the enrichment was computed but **before** the `INSERT INTO deals` statement was committed.

The `deal_brain` table has a foreign key constraint:
```
deal_brain.deal_id → deals.deal_id
```

Since the transaction hadn't committed, the deal row didn't exist yet in the `deals` table. When `seed_from_enrichment()` attempted to insert into `deal_brain`, PostgreSQL raised:

```
asyncpg.exceptions.ForeignKeyViolationError: insert or update on table "deal_brain"
violates foreign key constraint "deal_brain_deal_id_fkey"
DETAIL: Key (deal_id)=(DL-0131) is not present in table "deals".
```

This exception propagated up, aborting the entire transaction — meaning the deal itself was never created either.

### Bug 2: Missing Logger (Compounding)

**File:** `apps/backend/src/api/orchestration/main.py`
**Location:** `except` handler for brain seed (~line 3035)

The brain seed call was wrapped in a `try/except` block intended to provide fault isolation (INV-P2: brain seed failure must not block approval). However, the except handler referenced `logger.warning(...)` — but `logger` was never defined in the module scope.

```python
except Exception as _brain_err:
    logger.warning(f"Brain seed failed for {deal_id}: {_brain_err}")
    #     ^^^^^^ NameError: name 'logger' is not defined
```

This caused a **second exception** inside the error handler, which masked the FK violation error and produced an opaque 500 response with no useful diagnostic in the logs.

**Cascade:** Bug 1 triggers → Bug 2 triggers → Transaction aborts → No deal created → No error logged → Appears as mysterious 500.

---

## 3. Fix Applied

### Fix 1: Move Brain Seed After Transaction Commit

**Before (broken):**
```python
async with pool.acquire() as conn:
    await conn.execute('BEGIN')
    # ... enrichment computed ...
    # ... deal INSERT prepared ...

    # ❌ Brain seed INSIDE transaction — deal row doesn't exist yet
    brain_svc = DealBrainService()
    await brain_svc.seed_from_enrichment(deal_id, enrichment, dict(item))

    await conn.execute('COMMIT')
```

**After (fixed):**
```python
async with pool.acquire() as conn:
    await conn.execute('BEGIN')
    # ... enrichment computed ...
    # ... deal INSERT prepared ...

    # ✅ Capture data for brain seed (deferred to after commit)
    _brain_seed_enrichment = enrichment
    _brain_seed_item = dict(item)

    await conn.execute('COMMIT')

# ✅ Brain seed AFTER transaction commit — deal row now exists
if process.action == 'approve' and deal_id and '_brain_seed_enrichment' in dir():
    try:
        from ...core.agent.deal_brain_service import DealBrainService
        _brain_svc = DealBrainService()
        await _brain_svc.seed_from_enrichment(
            deal_id, _brain_seed_enrichment, _brain_seed_item
        )
    except Exception as _brain_err:
        logger.warning(f"Brain seed failed for {deal_id}: {_brain_err}")
```

**Key design point:** The enrichment data and item dict are captured as local variables inside the transaction scope, then consumed after commit. This preserves the fault isolation guarantee (INV-P2) — if brain seed fails, the deal is already committed.

### Fix 2: Add Logger Import

**Added at top of main.py (lines 11, 19):**
```python
import logging
logger = logging.getLogger(__name__)
```

### Fix 3: Zod Schema Type Widening (Dashboard)

**File:** `apps/dashboard/src/lib/api.ts` (line 179)

The LangSmith agent sends financial multiples as strings (e.g., `"3.8x"`) while the schema expected only numbers:

```typescript
// Before:
multiple: z.number().nullable().optional(),

// After:
multiple: z.union([z.string(), z.number()]).nullable().optional(),
```

Same treatment applied to `asking_price`, `revenue`, `ebitda`, `sde` — all now accept `string | number`.

---

## 4. Verification — Playwright End-to-End Testing

Backend rebuilt and deployed:
```bash
COMPOSE_PROJECT_NAME=zakops docker compose build backend
docker compose up -d backend --no-deps
```

### 4.1 Quarantine Actions (4/4 PASS)

| # | Action | Test Steps | Result | Evidence |
|---|--------|-----------|--------|----------|
| 1 | **Approve** | Open quarantine → Select AI SaaS item → Click Approve → Fill dialog → Confirm | **PASS** | Deal DL-0133 created, redirected to `/deals/DL-0133`, brain auto-seeded 6 facts |
| 2 | **Reject** | Select Pickleball Brand → Click Reject → Enter reason → Confirm | **PASS** | Toast: "Rejected (non-deal)", queue count 10→9 |
| 3 | **Escalate** | Select Maternal Health → Click Escalate → Set priority/reason/note → Confirm | **PASS** | Toast: "Escalated for review", queue count 9→8 |
| 4 | **Delegate** | Select Digital Transformation → Click Delegate → Set task type/priority → Confirm | **PASS** | Toast: "Delegated to agent: 90dbac7b...", agent message panel appeared |

### 4.2 Deal Page — DL-0133 (8/8 PASS)

| # | Feature | Test Steps | Result | Evidence |
|---|---------|-----------|--------|----------|
| 1 | **Overview tab** | Navigate to /deals/DL-0133 → Check sections | **PASS** | Deal info, Broker, Financials, Source Intelligence, Email Threads all rendered |
| 2 | **Materials tab** | Click Materials → Expand bundle | **PASS** | 1 bundle shown, email summary rendered from triage_summary |
| 3 | **Brain tab** | Click Brain → Check facts | **PASS** | 6 auto-seeded facts: ebitda, revenue, broker_name, broker_company, broker_email, company_name — all with source tags + confidence stars |
| 4 | **Events tab** | Click Events → Check rendering | **PASS** | "deal created by Zak" with source "quarantine_approval" — structured rendering, not JSON |
| 5 | **Transitions tab** | Click Transitions → Check entries | **PASS** | "Created → inbound by Zak (system)" |
| 6 | **Add Note** | Click Add Note → Type content → Submit | **PASS** | Dialog appeared, note saved, event count 1→2 |
| 7 | **Chat link** | Click Chat with Agent | **PASS** | Navigated to `/chat?deal_id=DL-0133` with deal pre-selected |
| 8 | **Deals list** | Navigate to /deals → Check list | **PASS** | 10 deals shown, DL-0133 at top, row click → deal detail |

### 4.3 API Verification

```bash
# Approve via API — confirmed brain seed in backend logs
curl -X POST localhost:8091/api/quarantine/{id}/process \
  -H "X-API-Key: ***" \
  -d '{"action":"approve","operator_name":"Zak"}'
# Response: {"deal_id":"DL-0132","deal_created":true}

# Backend log: "Brain seed for DL-0132: 4 facts, entities seeded" (no errors)
```

---

## 5. Invariant Verification

| Invariant | Status | How Verified |
|-----------|--------|-------------|
| INV-D1 (received_at in metadata) | PASS | `curl /api/deals/DL-0133` → metadata contains `received_at` |
| INV-D2 (approved_at in metadata) | PASS | metadata contains `approved_at` |
| INV-D5 (brain facts idempotent) | PASS | 6 facts seeded, key-based dedup active |
| INV-D6 (facts carry source tag) | PASS | All facts show `source: "extraction_evidence"` in Brain tab |
| INV-P2 (brain failure ≠ approval failure) | PASS | try/except with logger.warning — tested via code review |
| INV-R1 (notes not raw JSON) | PASS | Events tab shows structured rendering for known types |
| INV-R2 (no internal text in UI) | PASS | Materials tab shows "Emails, attachments, and documents..." |
| INV-R3 (no dead UI elements) | PASS | Dead Deal folder div removed |
| INV-R4 (email body fallback) | PASS | Bundle expansion shows email summary or "Email content not available" |
| INV-P4 (type-discriminated events) | PASS | deal_created renders as structured card, not JSON.stringify |

---

## 6. Files Modified

| File | Change | Lines |
|------|--------|-------|
| `apps/backend/src/api/orchestration/main.py` | Added `import logging` + `logger`; moved brain seed after transaction commit | 11, 19, 3032-3034, 3108-3115 |
| `apps/dashboard/src/lib/api.ts` | Widened Zod financial fields to `z.union([z.string(), z.number()])` | 175-179 |

---

## 7. Lessons Learned

1. **Foreign key ordering in transactions:** Any service that inserts into a table with FK dependencies on a row being created in the same transaction MUST be deferred to after commit. This is a general pattern — not specific to brain seeding.

2. **Logger availability in error handlers:** Every module that uses `try/except` with logging MUST have `logger` defined at module scope. An undefined logger in an error handler creates a silent failure cascade.

3. **Dual-failure masking:** When Bug 2 (missing logger) masked Bug 1 (FK violation), the error appeared as an opaque 500 with no diagnostic trail. Defense: always verify that error handlers themselves can execute without errors.

4. **Test after every pipeline phase:** Phase 2 (brain seed) was tested in isolation but the integration point (calling seed inside the transaction) was not end-to-end tested before moving to Phase 3. The fix would have been caught immediately with a single approval test after Phase 2.

---

## 8. Resolution Confirmation

- **Backend:** Rebuilt and deployed via `docker compose build backend && docker compose up -d backend --no-deps`
- **Health:** `curl localhost:8091/health` → `{"status":"healthy"}`
- **All 4 quarantine actions:** PASS via Playwright
- **All deal page features:** PASS via Playwright
- **All invariants:** Verified
- **Status: RESOLVED**

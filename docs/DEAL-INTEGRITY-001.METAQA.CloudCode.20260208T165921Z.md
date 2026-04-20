# DEAL-INTEGRITY-001 — PASS 4: META-QA REPORT

**Run ID:** `20260208T165921Z`
**Agent:** Claude Code (Opus 4.6)
**Pass:** 4 — META-QA
**Date:** 2026-02-08
**Document Under Review:** `DEAL-INTEGRITY-001_MASTER.md` (PASS 3, run `20260208T164604Z`)

---

## STATUS: CONDITIONAL PASS — 2 patches required

The MASTER document is substantively complete, properly deduplicated, architecturally aligned, and respects the INVESTIGATE-only constraint. Two minor defects found — both are evidence pointer errors, not analytical errors. The analysis and conclusions are correct; only the file citations need correction.

---

## CHECK 1: No-Drop Check — PASS

**Method:** Cross-referenced all 9 DI-ISSUEs from PASS 2 (CC3 `20260208T162638Z`) against MASTER section headers and content. Additionally verified that unique findings from all 6 input reports (3 PASS 1 + 3 PASS 2) appear in MASTER.

| DI-ISSUE | Present in MASTER | Section | Line |
|----------|-------------------|---------|------|
| DI-ISSUE-001 | YES | §2, line 78 | Archive Endpoint Partial State Transition |
| DI-ISSUE-002 | YES | §2, line 130 | Deal Counts Disagree |
| DI-ISSUE-003 | YES | §2, line 180 | Pipeline Sum Mismatch |
| DI-ISSUE-004 | YES | §2, line 230 | Active Filter |
| DI-ISSUE-005 | YES | §2, line 280 | Zod Error |
| DI-ISSUE-006 | YES | §2, line 343 | Split-Brain DB |
| DI-ISSUE-007 | YES | §2, line 405 | Propagation |
| DI-ISSUE-008 | YES | §2, line 457 | audit_trail |
| DI-ISSUE-009 | YES | §2, line 498 | kinetic 500 |

**Unique content from each input report — accounted for:**

| Source | Unique Finding | In MASTER |
|--------|---------------|-----------|
| Codex-P1 | Mission prompt wrong column names (`id` vs `deal_id`) | YES, line 539-544 |
| Codex-P1 | API pagination `limit=50` latent issue | YES, implicitly via DI-ISSUE-002 fix #3 (add `total_count`) |
| Codex-P1 | Backend DB accessibility from host (timed out) | YES, via DI-ISSUE-006 NEEDS VERIFICATION section |
| CC1-P1 | Implementation plan phases (Kill/Heal/Code/View) | YES, via 5 fix missions in §4 |
| CC1-P2 | Computed Column `is_active` innovation | YES, I-07 (line 840) and DI-ISSUE-001 Innovation #2 (line 126) |
| CC1-P2 | `infra/docker/docker-compose.yml` as rogue DB source | YES, line 358 and Mission 1 step 5 |
| Codex-P2 | Schema Diff Gate | YES, I-32 (line 865) and DI-ISSUE-008 Innovation #1 (line 493) |
| Codex-P2 | Endpoint Contract Inventory | YES, I-33 (line 866) and DI-ISSUE-009 Innovation #1 (line 534) |

**Verdict: 9/9 issues present. 0 drops. All unique findings from all agents accounted for.**

---

## CHECK 2: Dedupe Check — PASS

**Method:** Scanned all 9 DI-ISSUE entries for overlapping root causes, duplicate recommendations, and repeated innovation ideas.

### Issues — No Duplicates Found

Each DI-ISSUE has a distinct root cause statement. Dependencies are explicitly declared (e.g., DI-ISSUE-004 says "Fully resolves when DI-ISSUE-001 is fixed" at line 234) without duplicating the root cause analysis.

### Recommendations — Minor Structural Repetition (Acceptable)

One cross-cutting enforcement is repeated across multiple issues:

> "Startup gate: backend refuses to start if DB URL differs from canonical DSN"

Appears in:
- DI-ISSUE-002 §5 (line 169)
- DI-ISSUE-006 §5 (line 391)
- DI-ISSUE-007 §5 (line 445)

**Assessment:** This is contextually appropriate — each issue lists its own relevant enforcement. A "Cross-cutting Enforcement" section would be cleaner but is not required. **Not a defect.**

### Innovation Ideas — Properly Deduplicated

| Potential Overlap | Assessment |
|------------------|------------|
| I-09 (Materialized View) vs I-10 (Count Ledger) | Different mechanisms (DB MV vs trigger/outbox). Correctly kept as separate ideas. |
| I-14 (Canonical Stage Config) | Correctly merged from CC3 + Codex with attribution. |
| I-11 (DB Identity Tagging) cross-referenced in DI-ISSUE-002 and DI-ISSUE-006 | Correctly indexed once (I-11) with dual issue mapping. Not duplicated. |
| I-12 (API `total_count`) cross-referenced in DI-ISSUE-002 and DI-ISSUE-007 | Same. Indexed once, dual mapping. |

**34 innovation ideas in the appendix index (I-01 through I-34). No duplicates found.**

**Verdict: No duplicated issues. No duplicated innovation ideas. Minor structural repetition of one cross-cutting enforcement (acceptable).**

---

## CHECK 3: Evidence Check — CONDITIONAL PASS (1 pointer error)

**Method:** Sampled 10 claims from MASTER. For each, verified the cited evidence file exists and contains the claimed value.

| # | Claim (MASTER) | Evidence File Cited | Claimed Value | Actual File Value | Verdict |
|---|----------------|--------------------|--------------|--------------------|---------|
| 1 | Archive SQL: only `SET stage` (line 90) | `main.py:881-884` | `SET stage = 'archived'` | Verified in PASS 1 code analysis | **PASS** |
| 2 | DB status: all 'active' (line 92) | `db-distinct-statuses.txt` | Only 'active' | `active` (confirmed) | **PASS** |
| 3 | 6 archived-stage deals (line 94) | `db-archived-stage-deals.txt` | 6 deals | 6 deal rows shown (DL-0042 etc.) | **PASS** |
| 4 | **DB (5432) total: 49 (line 143)** | **`db-total-count.txt`** | **49** | **51** | **FAIL** |
| 5 | DB (5435) total: 51 (line 144) | `db-total-count-now.txt` (Codex) | 51 | 51 | **PASS** |
| 6 | PIPELINE_STAGES 7 entries (line 195) | `hq/page.tsx:18-26` | 7-element array | Verified in code | **PASS** |
| 7 | Filter values: active/junk/merged (line 245) | `deals/page.tsx:66` | 3 dropdown values | Verified in code | **PASS** |
| 8 | /api/agent/activity returns [] (line 303) | `api-agent-activity.txt` (Codex) | `[]` | `[]` | **PASS** |
| 9 | Backend DSN = postgres:5432 (line 363) | `backend-env-db.txt` (Codex) | `postgresql://zakops:...@postgres:5432/zakops` | Exact match | **PASS** |
| 10 | audit_trail column absent (line 469) | `db-deals-schema.txt` | Column not present | No `audit_trail` in 38-line schema dump | **PASS** |

### FAIL Detail — Claim #4: Evidence Pointer Mismatch

**MASTER line 143:**
```
| DB (5432) total: 49 | CC3 | evidence/00-forensics/db-total-count.txt |
```

**Actual file contents of `db-total-count.txt`:**
```
 total_deals
-------------
          51
```

The file shows **51**, not 49. The correct evidence file for the "49 on canonical DB" claim is `db-real-total-count.txt`, which shows:
```
 total_deals_real
------------------
               49
```

**Explanation:** The CC3 evidence directory contains two sets of DB queries:
- **Initial queries** (`db-total-count.txt`, `db-count-by-stage.txt`, `db-deleted-counts.txt`) — returned 51 total, archived:4, deleted:f=51. These appear to have queried either the rogue DB (port 5435), the `public.deals` table, or an unrestricted schema.
- **Corrected queries** (`db-real-total-count.txt`, `db-real-count-by-stage.txt`, `db-real-deleted-counts.txt`) — returned 49 total, archived:6, deleted:f=37/t=12. These correctly queried `zakops.deals` on the canonical container.

The PASS 1 analysis used the corrected data (49 deals), but the MASTER's evidence pointer references the initial file (which shows 51).

**This same error appears in three MASTER locations:**

| Location | What It Says | What It Should Say |
|----------|-------------|-------------------|
| Line 143 (DI-ISSUE-002 evidence table) | `db-total-count.txt` → "49" | Should cite `db-real-total-count.txt` |
| Line 366 (DI-ISSUE-006 evidence table) | `db-total-count.txt / db-real-total-count.txt` → "49" | Should cite ONLY `db-real-total-count.txt` |
| Line 734 (Evidence Index) | `db-total-count.txt` → "Total deal count: 49" | Should say "Total deal count: 51 (initial query — see `db-real-total-count.txt` for canonical 49)" |

**Impact:** The analytical conclusion (49 deals on canonical DB) is correct — supported by `db-real-total-count.txt` and cross-validated by `db-deleted-flag.txt` (37+12=49). Only the file citation is wrong.

**Verdict: 9/10 claims pass. 1 evidence pointer error. Analysis is sound; citation needs correction.**

---

## CHECK 4: "Never Again" Check — PASS

**Method:** Verified each of 9 DI-ISSUEs has concrete prevention mechanisms (not just "be more careful" platitudes).

| DI-ISSUE | Prevention Items | Concrete? | Testable? |
|----------|-----------------|-----------|-----------|
| 001 | DB CHECK constraint; 2 integration tests; code gate (`transition_deal_state`); DB trigger | YES | YES — all expressible as automated tests or DB constraints |
| 002 | Contract test (sum=total); CI gate (API=DB); UI invariant test; startup gate | YES | YES |
| 003 | 2 contract tests; code review gate (no hardcoded stage lists) | YES | YES |
| 004 | API test; DB constraint/trigger; derive filters from config | YES | YES |
| 005 | Contract test (schema match); 2 UI tests; code invariant (all fetchers have try/catch) | YES | YES |
| 006 | Startup gate; CI/smoke; docker-compose constraint; ops runbook | YES | YES (except runbook is process, not automated) |
| 007 | E2E test; startup gate; CI gate | YES | YES |
| 008 | CI gate (schema diff); schema diff gate | YES | YES |
| 009 | API health suite; endpoint inventory gate | YES | YES |

**All 9 issues have concrete, testable prevention mechanisms.** The strongest are DI-ISSUE-001 (5 items including DB-level enforcement) and DI-ISSUE-005 (4 items including both contract and UI tests).

**Verdict: PASS — all issues have concrete "never again" enforcement.**

---

## CHECK 5: Actionability Check — PASS (with 1 gap)

**Method:** Verified 5 proposed fix missions are well-scoped with steps, gates, evidence requirements, and risks/rollback.

| Mission | Scope | Steps | Gates | Evidence | Risks/Rollback | Verdict |
|---------|-------|-------|-------|----------|----------------|---------|
| 1: DEAL-INFRA-UNIFY | DI-ISSUE-006 | 6 steps | 4 gates | Before/after required | Rollback plan provided | **PASS** |
| 2: DEAL-LIFECYCLE-FIX | DI-ISSUE-001 (+002,003,004,007) | 5 steps | 5 gates | Before/after required | Rollback SQL provided | **PASS** |
| 3: DEAL-PIPELINE-ALIGN | DI-ISSUE-003, 002 | 4 steps | 3 gates | Screenshots + code diff | Rollback: revert frontend | **PASS** |
| 4: DEAL-FILTER-FIX | DI-ISSUE-004, 005 | 5 steps | 5 gates | Filter tests + console clean | Rollback: revert code | **PASS** |
| 5: DEAL-CLEANUP | DI-ISSUE-008, 009 | 3 steps | 3 gates | Code diff + test results | Rollback: revert | **PASS** |

**Mission ordering** (Phase 0→4) is correct — Mission 1 is independent, Missions 2-4 are sequential, Mission 5 is independent.

### Gap: DI-ISSUE-007 Verification Not in Any Mission Gate

DI-ISSUE-007 (UI-Created Deals Don't Propagate) has no dedicated mission. The MASTER correctly states it "fully resolves when DI-ISSUE-001 + DI-ISSUE-006 are fixed" (line 409).

However, DI-ISSUE-007's "Never Again" section specifies:
> "E2E test: Create deal → verify in /deals, /hq, pipeline summary, **agent API**"

This specific cross-service verification does **not appear as a gate** in any of the 5 missions:
- Mission 1 gates test DB identity but not deal creation propagation
- Mission 2 gates test archive/restore but not new deal creation across services
- Mission 3 gates test pipeline display but not agent API visibility

**Recommendation:** Add the following gate to **Mission 2** (DEAL-LIFECYCLE-FIX):
```
- Create a test deal via POST /api/deals → verify it appears in:
  (a) GET /api/deals
  (b) GET /api/pipeline/summary (inbound count increased)
  (c) Agent API deal listing (if Agent API is running)
```

### Operator Decisions — Well-Structured

4 operator decisions defined (lines 548-593) with options, pros/cons, and recommendations. Each is gated — fix missions reference "per operator decision" where applicable. ✓

### INVESTIGATE-only Constraint — Respected

MASTER ends with: "No fixes implemented. Investigation and planning only." (line 874). All content is diagnostic + planning. Fix missions are "proposed" not "executed." ✓

### ZakOps Architecture Alignment — Correct

| Element | Expected | In MASTER | Correct? |
|---------|----------|-----------|----------|
| Backend path | `zakops-backend/` | Lines 777-780 | ✓ |
| Dashboard path | `zakops-agent-api/apps/dashboard/` | Lines 781-790 | ✓ |
| DB schema | `zakops.deals` (not `public`) | Lines 53-55, 100 | ✓ |
| Backend port | 8091 | Line 813 | ✓ |
| Dashboard port | 3003 | Line 816 | ✓ |
| Agent port | 8095 | Not directly referenced but implicit | ✓ |
| Canonical DB container | `zakops-backend-postgres-1` | Lines 355, 371, 800 | ✓ |
| Migration file | `023_stage_check_constraint.sql` | Line 791 | ✓ |

**Verdict: PASS — all missions are well-scoped and gated. 1 missing verification gate for DI-ISSUE-007 (recommended patch below).**

---

## REQUIRED PATCHES

### PATCH 1: Fix Evidence Pointer for DB Total Count (Evidence Check failure)

**Files to modify:** `DEAL-INTEGRITY-001_MASTER.md`

**Patch A — Line 143 (DI-ISSUE-002 evidence table):**
```
BEFORE:
| DB (5432) total: 49 | CC3 | `evidence/00-forensics/db-total-count.txt` |

AFTER:
| DB (5432) total: 49 | CC3 | `evidence/00-forensics/db-real-total-count.txt` |
```

**Patch B — Line 366 (DI-ISSUE-006 evidence table):**
```
BEFORE:
| DB 5432: 49 deals | CC3, CC1 | `evidence/00-forensics/db-total-count.txt` / `db-real-total-count.txt` |

AFTER:
| DB 5432: 49 deals | CC3, CC1 | `evidence/00-forensics/db-real-total-count.txt` / CC1 `db-real-total-count.txt` |
```

**Patch C — Line 734 (Evidence Index):**
```
BEFORE:
| `db-total-count.txt` | Total deal count: 49 |

AFTER:
| `db-total-count.txt` | Total deal count: 51 (initial query — pre-schema-correction; see `db-real-total-count.txt` for canonical count of 49) |
```

**And add a new row after line 734:**
```
| `db-real-total-count.txt` | Canonical DB (5432) deal count: 49 (zakops schema) |
```

### PATCH 2: Add DI-ISSUE-007 Verification Gate to Mission 2

**File to modify:** `DEAL-INTEGRITY-001_MASTER.md`

**After line 641 (Mission 2 gates section), add:**
```
- Create test deal via API → verify it appears in GET /api/deals, GET /api/pipeline/summary (inbound +1), and agent API deal listing (DI-ISSUE-007 resolution verification)
```

---

## SUMMARY SCORECARD

| Check | Result | Notes |
|-------|--------|-------|
| **1. No-Drop** | **PASS** | 9/9 issues present. All unique findings from all 6 input reports accounted for. |
| **2. Dedupe** | **PASS** | No duplicated issues or ideas. Minor cross-cutting enforcement repetition (acceptable). |
| **3. Evidence** | **CONDITIONAL PASS** | 9/10 sampled claims verified. 1 evidence pointer error (file shows 51, doc says 49). Analysis is correct; citation is wrong. **Patch 1 required.** |
| **4. Never Again** | **PASS** | All 9 issues have concrete, testable prevention mechanisms. |
| **5. Actionability** | **PASS** | 5 missions well-scoped with gates, evidence, rollback. 1 missing verification gate for DI-ISSUE-007. **Patch 2 recommended.** |

---

## FINAL VERDICT

### STATUS: CONDITIONAL PASS

The MASTER document is analytically sound, properly deduplicated, architecturally aligned, and comprehensive. Two patches are required:

1. **PATCH 1 (Required):** Correct 3 evidence pointer references where `db-total-count.txt` (contains 51) is cited as proof of "49". Replace with `db-real-total-count.txt` (contains 49). Update Evidence Index description.

2. **PATCH 2 (Recommended):** Add DI-ISSUE-007 cross-service verification gate to Mission 2.

**After these patches are applied, the document achieves full PASS status.**

---

**END OF PASS 4 — META-QA**

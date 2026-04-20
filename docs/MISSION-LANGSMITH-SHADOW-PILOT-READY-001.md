# MISSION: LANGSMITH-SHADOW-PILOT-READY-001
## Prepare ZakOps for Safe, Measurable LangSmith Shadow-Mode Pilot
## Date: 2026-02-13
## Classification: Platform Readiness — Drift Prevention & Measurement Controls
## Prerequisite: LANGSMITH-INTAKE-HARDEN-001 (complete), QA-LANGSMITH-INTAKE-HARDEN-VERIFY-001 (CONDITIONAL PASS)
## Successor: LangSmith Shadow-Mode Pilot Execution (external injector live)

---

## Mission Objective

Prepare the ZakOps quarantine intake surface for a safe, measurable LangSmith shadow-mode pilot by eliminating source_type naming drift, hardening intake authentication at startup, and adding server-side validation that prevents unknown source_type values from silently entering the system.

This is a **drift-prevention and measurement-readiness** mission, not a feature build. The intake pipeline already works (proven by QA-LANGSMITH-INTAKE-HARDEN-VERIFY-001). This mission closes the remaining drift vectors and adds guardrails so an external automated injector cannot introduce data that breaks isolation, measurement, or traceability.

**Source material:**
- QA scorecard: `/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-harden-verify-001/SCORECARD.md` (ENH-6 finding)
- Injection contract: `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md`
- Backend model: `/home/zaks/zakops-backend/src/api/orchestration/main.py` (lines 272, 1514)
- Dashboard filter: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` (line 327)

**What this mission is NOT:**
- Not a feature build (no new endpoints, no new tables)
- Not a full security audit (auth middleware already exists and is fail-closed)
- Not a dashboard redesign (UI changes are limited to label text)

---

## Context

### Non-Negotiable Decision (LOCKED)

Canonical source_type naming for LangSmith intake:

| Canonical Value | Purpose |
|----------------|---------|
| `langsmith_shadow` | Shadow pilot intake (measurement only) |
| `langsmith_live` | Live intake (future production mode) |

Any other LangSmith label (including `langsmith_production`) is **legacy drift** and must be removed or migrated.

### Current Drift State (3 locations)

| Location | File | Line | Current Value | Required Value |
|----------|------|------|---------------|----------------|
| Backend model comment | `main.py` | 272 | `langsmith_production` | `langsmith_live` |
| Contract documentation | `INJECTION-CONTRACT.md` | 79 | `langsmith_production` | `langsmith_live` |
| Dashboard filter option | `quarantine/page.tsx` | 327 | `langsmith_production` | `langsmith_live` |

### Missing Guardrails (2 items)

1. **No startup validation of ZAKOPS_API_KEY** — The middleware is fail-closed at runtime (returns 503 if key not set), but the backend starts silently without warning. An operator could deploy without setting the key and not notice until the first injection attempt fails.

2. **No server-side source_type validation** — `main.py:1514` accepts ANY string as source_type. An external injector could send `source_type=langsmith_prod` or `source_type=shadow` and it would be silently stored. This breaks measurement isolation because queries filtering on `langsmith_shadow` would miss misspelled values.

### Already Working (verify, don't rebuild)

| Capability | Evidence |
|-----------|----------|
| Dedup measurement (201 vs 200) | `main.py:1551` (200), `main.py:1598` (201) |
| Correlation ID end-to-end | `main.py:1512` → `1559` → `1830` |
| Rate limiting (120/min) | `security.py:150`, `main.py:1506` |
| Shadow-mode API filtering | `main.py:1381,1401` |
| Shadow-mode UI filtering | `quarantine/page.tsx:78-100,320-329` |
| Deal truth from PostgreSQL | All agent-api deal reads via BackendClient → HTTP → PostgreSQL |

---

## Glossary

| Term | Definition |
|------|-----------|
| Shadow-mode | LangSmith items injected with `source_type='langsmith_shadow'` for measurement without affecting production deal flow |
| Fail-closed | Pattern where missing configuration blocks access entirely (503) rather than degrading to open access |
| Injection surface | `POST /api/quarantine` — the only entry point for external quarantine item creation |
| Drift | When the same concept has different labels in different locations (e.g., `langsmith_production` vs `langsmith_live`) |

---

## Architectural Constraints

Per standing rules (CLAUDE.md, MEMORY.md):
- **Contract surface discipline** — `make sync-all-types` after API boundary changes
- **Surface 9 compliance** — `console.warn` for degradation, `console.error` for unexpected
- **Generated files never edited** — *.generated.ts, *_models.py are codegen outputs
- **Port 8090 FORBIDDEN** — decommissioned
- **WSL safety** — CRLF strip on .sh files, chown on files under /home/zaks/

Mission-specific:
- **VALID_SOURCE_TYPES constant** — The backend must define a single authoritative list of allowed source_type values. This constant is the canonical enum.
- **Startup gate pattern** — Follow the existing LAYER 1 DSN verification pattern at `main.py:398-422` for the new API key gate.

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Fix `langsmith_production` in 3 known files but miss a 4th reference in MASTER-PROGRAM or QA docs | HIGH | Drift reappears in future mission citing old docs | Phase 0 discovery greps ALL repos for `langsmith_production` |
| 2 | VALID_SOURCE_TYPES validation breaks existing `email` and `manual` ingestion | MEDIUM | Production intake stops working | Validation list includes ALL 5 canonical values, not just LangSmith ones |
| 3 | Startup gate for ZAKOPS_API_KEY crashes backend when env var is legitimately unset in dev | MEDIUM | Dev environment broken | Gate warns loudly but only hard-fails if injection paths are configured |
| 4 | Dashboard filter label updated but golden test fixture still references old value | LOW | Test drift | Phase 0 checks golden/ directory for source_type references |
| 5 | CRLF in new or modified files | MEDIUM | Runtime failures | WSL safety checklist in every phase gate |

---

## Phase 0 — Discovery & Baseline

**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Confirm all drift locations, verify baseline validation passes, identify any additional references beyond the known 3.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: Run `make validate-local` in monorepo — confirm baseline PASS
- P0-02: Run `npx tsc --noEmit` in dashboard — confirm baseline PASS
- P0-03: Grep ALL repos for `langsmith_production` — capture every occurrence
  - Search paths: `/home/zaks/zakops-backend/`, `/home/zaks/zakops-agent-api/`, `/home/zaks/bookkeeping/`
  - **Checkpoint:** Record exact file:line for every hit. Classify each as CODE, DOCS, QA_EVIDENCE, or SNAPSHOT
- P0-04: Grep ALL repos for `langsmith_live` — capture current state
- P0-05: Verify ZAKOPS_API_KEY startup behavior by reading `main.py:380-429` — confirm no existing startup check
- P0-06: Check golden test fixtures for source_type references: `/home/zaks/zakops-agent-api/apps/dashboard/golden/`

### Gate P0
- `make validate-local` passes
- All `langsmith_production` occurrences cataloged with classifications
- Startup gap confirmed (no ZAKOPS_API_KEY validation in lifespan)

---

## Phase 1 — source_type Canonical Naming

**Complexity:** M
**Estimated touch points:** 3-5 files

**Purpose:** Eliminate `langsmith_production` from all CODE and DOCS surfaces. Replace with `langsmith_live` per the locked naming decision.

### Blast Radius
- **Services affected:** Backend (model comment), Dashboard (filter label)
- **Pages affected:** Quarantine page (filter dropdown)
- **Downstream consumers:** INJECTION-CONTRACT.md (external integrator reference)

### Tasks
- P1-01: **Update backend model comment** — `/home/zaks/zakops-backend/src/api/orchestration/main.py:272`
  - Change: `langsmith_production` → `langsmith_live` in the comment string
  - Evidence: Line 272 shows `langsmith_live` after edit
  - **Checkpoint:** This is a comment-only change — no runtime behavior affected

- P1-02: **Update contract documentation** — `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md:79`
  - Change: `langsmith_production` → `langsmith_live` in the source type values table
  - Evidence: Line 79 shows `langsmith_live`

- P1-03: **Update dashboard filter option** — `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:327`
  - Change: `langsmith_production` → `langsmith_live` in `<option>` value and label
  - Evidence: Line 327 shows `langsmith_live`

- P1-04: **Update any additional CODE/DOCS hits** found in P0-03
  - **Decision Tree:**
    - **IF** hit is in a QA evidence file or pre-compact snapshot → SKIP (historical record, do not modify)
    - **IF** hit is in MASTER-PROGRAM or mission doc → UPDATE to `langsmith_live`
    - **IF** hit is in generated file → SKIP (regenerate via sync pipeline)

### Rollback Plan
1. `git checkout -- src/api/orchestration/main.py docs/INJECTION-CONTRACT.md` (backend)
2. `git checkout -- apps/dashboard/src/app/quarantine/page.tsx` (monorepo)
3. Verify: `make validate-local` passes after rollback

### Gate P1
- Zero occurrences of `langsmith_production` in CODE or DOCS files (QA evidence/snapshots excluded)
- `npx tsc --noEmit` passes
- `langsmith_live` appears in all 3 canonical locations

---

## Phase 2 — Server-Side source_type Validation

**Complexity:** M
**Estimated touch points:** 1-2 files

**Purpose:** Add a VALID_SOURCE_TYPES constant to the backend and validate incoming source_type values on the injection endpoint. Unknown values are rejected with 400 Bad Request, preventing silent drift.

### Blast Radius
- **Services affected:** Backend (injection endpoint)
- **Pages affected:** None (validation is server-side only)
- **Downstream consumers:** Any external injector must send a valid source_type

### Tasks
- P2-01: **Define VALID_SOURCE_TYPES constant** — `/home/zaks/zakops-backend/src/api/orchestration/main.py`
  - Location: Near the QuarantineCreate model (around line 260-274)
  - Values: `{"email", "email_sync", "langsmith_shadow", "langsmith_live", "manual"}`
  - **Checkpoint:** Constant defined, includes all 5 canonical values

- P2-02: **Add validation in POST /api/quarantine handler** — `main.py` around line 1514
  - After the source_type priority resolution (`source_type = item.source_type or ... or "email"`)
  - Check: `if source_type not in VALID_SOURCE_TYPES: return 400`
  - Response: `{"error": "invalid_source_type", "message": "...", "valid_values": [...]}`
  - **Checkpoint:** Validation rejects `langsmith_production`, accepts `langsmith_live`

- P2-03: **Update INJECTION-CONTRACT.md** — Add a note that unknown source_type values are rejected with 400
  - Location: Response Codes table
  - Add row: `400 Bad Request | Invalid source_type value (not in allowed list)`

### Decision Tree
- **IF** existing data in the database contains `langsmith_production` values → These are read-only (GET endpoint returns whatever is stored). Validation only applies to new INSERTs.
- **IF** a migration is needed to update old rows → OUT OF SCOPE for this mission. Document as follow-up.

### Rollback Plan
1. Remove VALID_SOURCE_TYPES constant and validation block from `main.py`
2. Remove 400 row from INJECTION-CONTRACT.md
3. Verify: `make validate-local` passes

### Gate P2
- `VALID_SOURCE_TYPES` constant exists with exactly 5 values
- POST with `source_type=langsmith_production` would return 400 (logic check)
- POST with `source_type=langsmith_shadow` passes validation (logic check)
- INJECTION-CONTRACT.md documents the 400 response for invalid source_type

---

## Phase 3 — Intake Auth Startup Gate

**Complexity:** S
**Estimated touch points:** 1 file

**Purpose:** Add ZAKOPS_API_KEY validation to the backend startup lifespan hook, following the existing LAYER 1 DSN gate pattern. Ensures operators are warned at startup if the key is not set.

### Blast Radius
- **Services affected:** Backend (startup behavior only)
- **Pages affected:** None
- **Downstream consumers:** None (this is a startup-time check)

### Tasks
- P3-01: **Add LAYER 2 — API Key startup gate** — `/home/zaks/zakops-backend/src/api/orchestration/main.py`
  - Location: After the DSN gate block (after line 422, before `yield`)
  - Behavior:
    - Read `ZAKOPS_API_KEY` from environment
    - If not set or empty: print a LOUD warning (not a crash — dev environments may not set it)
    - Log: `"STARTUP WARNING: ZAKOPS_API_KEY is not set — injection paths will return 503 (fail-closed)"`
    - Store in `app.state.api_key_configured = bool(key)`
  - **Checkpoint:** Backend starts with warning when key is absent, starts silently when key is present

### Decision Tree
- **IF** we want a hard failure (RuntimeError) when key is not set → NOT recommended. Dev environments legitimately run without it. The middleware already handles runtime fail-closed.
- **ELSE** → Warning + state flag (recommended). The health endpoint can include `api_key_configured: true/false` for monitoring.

### Rollback Plan
1. Remove the LAYER 2 block from the lifespan function
2. Verify: `make validate-local` passes

### Gate P3
- Backend lifespan function contains API key startup check
- Warning message logged when ZAKOPS_API_KEY is not set
- `app.state.api_key_configured` flag is set

---

## Phase 4 — Full-Stack Verification & Evidence Collection

**Complexity:** M
**Estimated touch points:** 0 (verification only)

**Purpose:** Produce evidence proving all 7 critical items from the mission scope are satisfied. Each item gets a dedicated evidence file.

### Blast Radius
- **Services affected:** None (read-only verification)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks

- P4-01: **Evidence: source_type drift eliminated** — Grep all repos for `langsmith_production` in CODE/DOCS. Must return 0 hits.
- P4-02: **Evidence: intake auth fail-closed** — Read middleware, confirm 503 for unset key, 401 for bad key, startup warning present.
- P4-03: **Evidence: created vs deduped measurable** — Read POST handler, confirm 201 for new and 200 for dedup.
- P4-04: **Evidence: correlation ID end-to-end** — Trace correlation_id from header capture (line 1512) → quarantine INSERT (line 1559) → outbox INSERT (line 1830).
- P4-05: **Evidence: shadow-mode isolation** — Confirm API source_type filter (line 1381) and dashboard filter dropdown (line 320-329).
- P4-06: **Evidence: flood protection active** — Confirm injection_rate_limiter (120/min) called in POST handler (line 1506).
- P4-07: **Evidence: deal truth from PostgreSQL** — Confirm agent-api deal reads go through BackendClient (not filesystem).

### Gate P4
- 7 evidence files produced in `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/`
- Each evidence file references specific file:line locations
- Zero FAIL items

---

## Phase 5 — Documentation & Final Verification

**Complexity:** S
**Estimated touch points:** 2 files

**Purpose:** Final validation, bookkeeping, and completion report.

### Tasks
- P5-01: Run `make validate-local` — must PASS
- P5-02: Run `npx tsc --noEmit` — must PASS
- P5-03: Update `/home/zaks/bookkeeping/CHANGES.md` with all modifications
- P5-04: Write completion report to `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md`

### Gate P5
- `make validate-local` PASS
- `npx tsc --noEmit` PASS
- CHANGES.md updated
- Completion report produced with evidence pack references

---

## Dependency Graph

```
Phase 0 (Discovery)
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
Phase 1 (Naming)   Phase 2 (Validation)  Phase 3 (Auth Gate)
    │                  │                  │
    └──────────────────┴──────────────────┘
                       │
                       ▼
              Phase 4 (Evidence)
                       │
                       ▼
              Phase 5 (Final)
```

Phases 1, 2, and 3 are independent and can execute in parallel after Phase 0.

---

## Acceptance Criteria

### AC-1: source_type Drift Eliminated
Zero occurrences of `langsmith_production` in CODE or DOCS files across all repos (QA evidence/snapshots excluded).

### AC-2: VALID_SOURCE_TYPES Constant Exists
Backend defines a constant with exactly 5 values: `email`, `email_sync`, `langsmith_shadow`, `langsmith_live`, `manual`.

### AC-3: Server-Side Validation Active
POST /api/quarantine rejects unknown source_type values with 400 Bad Request.

### AC-4: Intake Auth Startup Gate
Backend startup warns when ZAKOPS_API_KEY is not set and sets `app.state.api_key_configured`.

### AC-5: Created vs Deduped Measurable
POST /api/quarantine returns 201 for new items, 200 for dedup hits.

### AC-6: Correlation ID End-to-End
correlation_id flows: header → quarantine row → outbox event (with UUID fallback).

### AC-7: Shadow-Mode Isolation
API supports `?source_type=langsmith_shadow` filtering; dashboard exposes filter dropdown.

### AC-8: Flood Protection Active
injection_rate_limiter (120/min) called on POST /api/quarantine.

### AC-9: Deal Truth from PostgreSQL
All agent-api deal state reads go through BackendClient → HTTP → PostgreSQL. Zero filesystem deal-state reads.

### AC-10: No Regressions
`make validate-local` and `npx tsc --noEmit` pass.

### AC-11: Bookkeeping
CHANGES.md updated, completion report produced with evidence pack.

---

## Guardrails

1. **Scope fence** — This mission fixes drift and adds guardrails. It does NOT build new features, create new endpoints, or modify database schema.
2. **Generated file protection** — Do not modify *.generated.ts or *_models.py (enforced by deny rules).
3. **Historical evidence preservation** — Do NOT modify QA evidence files or pre-compact snapshots that contain `langsmith_production`. These are historical records.
4. **No database migration** — If existing rows contain `langsmith_production`, document as follow-up. Do NOT create a migration in this mission.
5. **Dev-friendly startup** — The API key startup gate must WARN, not crash. Dev environments legitimately run without ZAKOPS_API_KEY.
6. **WSL safety** — CRLF strip on any new .sh files, chown on files under /home/zaks/.
7. **Surface 9 compliance** — Per standing rules.
8. **Contract surface discipline** — Run `make sync-all-types` if any API boundary changes.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I grep ALL 3 repos (backend, monorepo, bookkeeping) for `langsmith_production`?"
- [ ] "Did I classify each hit as CODE, DOCS, QA_EVIDENCE, or SNAPSHOT?"
- [ ] "Does `make validate-local` pass at baseline?"

### After every code change:
- [ ] "Did the change preserve the existing runtime behavior (201/200, rate limiting, correlation)?"
- [ ] "Did I update ALL locations, not just the first one I found?"

### Before marking complete:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I produce evidence files for all 7 critical items?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Is there a completion report with AC evidence map?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | 1,2,3 | Fix comment, add VALID_SOURCE_TYPES, add validation, add startup gate |
| `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` | 1,2 | Fix langsmith_production → langsmith_live, add 400 response doc |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | 1 | Fix filter option langsmith_production → langsmith_live |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md` | 5 | Completion report |
| `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/` | 4 | Evidence pack directory (7 files) |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` | Auth middleware reference |
| `/home/zaks/zakops-backend/src/api/shared/security.py` | Rate limiter reference |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py` | Deal truth verification |

---

## Crash Recovery (IA-2)

If resuming after a crash:
1. `git diff` in both repos to see what was already changed
2. `make validate-local` to check current state
3. Check for partial evidence files in `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/`
4. Resume from the earliest incomplete phase

---

## Stop Condition

This mission is DONE when:
- All 11 acceptance criteria are met
- `make validate-local` passes
- `npx tsc --noEmit` passes
- Completion report produced with evidence pack references
- CHANGES.md updated

Do NOT proceed to: LangSmith shadow-mode pilot execution, database migration of existing `langsmith_production` rows, or dashboard feature additions.

---

*End of Mission Prompt — LANGSMITH-SHADOW-PILOT-READY-001*

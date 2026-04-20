# MISSION: LANGSMITH-INTAKE-HARDEN-001
## LangSmith Integration Safety — Canonical Truth, Auth, Measurement, Correlation, Flood Protection
## Date: 2026-02-13
## Classification: Platform Hardening / Integration Safety
## Prerequisite: ZAKOPS-INTAKE-COL-V2-001 (complete)
## Successor: QA-LIH-VERIFY-001

---

## Mission Objective

This mission **hardens the email injection pipeline** to make it safe for LangSmith integration. It resolves five concrete gaps discovered during builder-level forensic investigation of the quarantine intake path.

This is a **FIX mission** — not a feature build. Every gap already has partial infrastructure (rate limiter class, correlation header reading, auth middleware, source_type column). The work is wiring, enforcing, and closing the gaps.

**What this mission is NOT:**
- Not a LangSmith integration build (no LangSmith SDK, no trace IDs, no callback wiring)
- Not a dashboard feature build (minimal UI changes — only shadow-mode filter)
- Not a migration-heavy mission (zero new SQL migrations)

**Source material:**
- Builder forensic investigation from prior session (7 gaps identified)
- `/home/zaks/bookkeeping/docs/_qa_evidence/INTAKE-COL-V2-PROGRAM-COMPLETION.md` — completion report showing current state
- `/home/zaks/zakops-backend/src/api/orchestration/main.py` — quarantine injection endpoint (line 1486)
- `/home/zaks/zakops-backend/src/actions/context/context_pack.py` — split-brain deal registry reads (lines 213-230)
- `/home/zaks/zakops-backend/src/workers/actions_runner.py` — split-brain deal registry reads (line 723)

---

## Context

### Current State (7 Gaps)

| # | Gap | Severity | Location |
|---|-----|----------|----------|
| G1 | `.deal-registry` JSON serves as canonical truth for deal stage/status to `context_pack.py` and `actions_runner.py`, competing with PostgreSQL `zakops.deals` | CRITICAL | `context_pack.py:213-230`, `actions_runner.py:53,723` |
| G2 | Auth is conditional — `APIKeyMiddleware` only enforces when `ZAKOPS_API_KEY` env var is set; no env var = open endpoint | CRITICAL | `apikey.py:18-42` |
| G3 | Quarantine POST returns HTTP 201 for both new-create and dedup-hit — caller cannot distinguish | MEDIUM | `main.py:1520-1541` |
| G4 | Shadow-mode is cosmetic only — `source_type` stored but no filtering capability at API or UI | MEDIUM | `main.py:255-273`, quarantine page.tsx |
| G5 | Correlation ID breaks at outbox boundary — `gen_random_uuid()` replaces original correlation ID | HIGH | `main.py:1800-1815` |
| G6 | `RateLimiter` class exists but is NOT wired to any endpoint | HIGH | `security.py:102-149` |
| G7 | No retry/catch-up mechanism (caller's responsibility — acceptable, but must be documented) | LOW | N/A — documentation only |

### Environment

- Backend API running on port 8091 (Docker container `zakops-backend-1`)
- Quarantine table in `zakops` database, schema `zakops`, with existing columns: `message_id`, `correlation_id`, `source_type`, `injection_metadata`
- Migration 029 (quarantine hardening) already applied — UNIQUE on `message_id`, CHECK constraints
- `RateLimiter` class at `security.py:102-144` with `general_rate_limiter` (60/min) and `auth_rate_limiter` (10/min) already instantiated at lines 147-149
- `check_rate_limit()` helper at `security.py:152-172` exists but is never called

---

## Glossary

| Term | Definition |
|------|-----------|
| Split-brain | Two sources of truth for the same data — `.deal-registry` JSON vs PostgreSQL `zakops.deals` table |
| Injection path | The `POST /api/quarantine` endpoint that external systems (email sync, LangSmith) use to submit items |
| Shadow mode | Items injected with `source_type='langsmith_shadow'` — intended for measurement, not action |
| Correlation ID | UUID that links a quarantine item through approval → deal creation → outbox events |
| Outbox | `zakops.outbox` table — event store for downstream consumers (notifications, webhooks) |
| Dedup | Deduplication — returning existing item when `message_id` already exists in quarantine |

---

## Architectural Constraints

- **`transition_deal_state()` single choke point** — all deal state changes flow through this function. This mission does NOT touch deal state transitions.
- **Contract surface discipline** — any OpenAPI spec changes require corresponding `make sync-*` commands. This mission does NOT change OpenAPI specs (all changes are internal backend logic).
- **Generated files never edited** — per standing deny rules.
- **Port 8090 FORBIDDEN** — per standing rules.
- **Database schema `zakops`** (NOT `public`) — all quarantine, deals, and outbox tables live in the `zakops` schema.
- **No new SQL migrations** — all required columns already exist. Changes are code-level only.

---

## Anti-Pattern Examples

### WRONG: Conditional auth that silently degrades
```python
if not expected_key:
    return await call_next(request)  # No key configured = wide open
```

### RIGHT: Fail-closed auth on injection paths
```python
if not expected_key:
    return JSONResponse(status_code=503, content={"detail": "API key not configured"})
```

### WRONG: Fresh UUID in outbox, breaking correlation chain
```python
VALUES (gen_random_uuid(), 'deal', $1, 'deal_created', $2::jsonb)
```

### RIGHT: Forward the original correlation ID through the entire chain
```python
VALUES ($3, 'deal', $1, 'deal_created', $2::jsonb)  -- $3 = original correlation_id
```

### WRONG: Same HTTP status for create and dedup
```python
return QuarantineResponse(...)  # 201 for both new and existing
```

### RIGHT: Distinct status codes so callers can measure
```python
if existing:
    return JSONResponse(status_code=200, content=...)  # 200 = dedup hit
# ... create new ...
return JSONResponse(status_code=201, content=...)  # 201 = new item created
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Removing `.deal-registry` reads from `context_pack.py` without providing a database alternative breaks the action engine — actions can no longer resolve deal stage/status | HIGH | Action engine fails on every deal | Phase 1 replaces reads with direct PostgreSQL queries using the existing pool, verified by gate |
| 2 | Making auth mandatory breaks the existing email-sync pipeline which may not be sending X-API-Key headers | HIGH | Email ingestion stops working | Phase 2 adds the key to email-sync config and tests both paths |
| 3 | Changing quarantine POST response codes (201→200 for dedup) breaks existing callers that expect 201 always | MEDIUM | Existing integrations fail on 200 response | Phase 3 only changes dedup path; new-create path stays 201 |
| 4 | Rate limiter blocks legitimate burst ingestion from email-sync (many emails arriving simultaneously) | MEDIUM | Email sync hits rate limit during catchup | Phase 5 uses a separate injection_rate_limiter with higher limit (120/min) distinct from general |
| 5 | CRLF not stripped from any new shell scripts | LOW | Delayed failure | WSL safety checklist in post-task protocol |

---

## Crash Recovery

If resuming after a crash, run these 3 commands to determine current state:
1. `git log --oneline -5` in `/home/zaks/zakops-backend/` — see which phases were committed
2. `make validate-local` in `/home/zaks/zakops-agent-api/` — verify codebase integrity
3. `ls /home/zaks/bookkeeping/mission-checkpoints/LANGSMITH-INTAKE-HARDEN-001.md` — check for checkpoint file

---

## Phase 0 — Discovery & Baseline

**Complexity:** S
**Estimated touch points:** 0 files modified

**Purpose:** Verify all 7 gaps are still current before making changes.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks

- P0-01: **Verify split-brain reads exist** — grep for `deal_registry.json` in `context_pack.py` and `actions_runner.py`
  - Evidence: Lines 213-230 in context_pack.py, line 723 in actions_runner.py
  - **Checkpoint:** Both files still read from JSON — if not, re-scope Phase 1

- P0-02: **Verify auth is conditional** — read `apikey.py:18-42`, confirm `if not expected_key: return await call_next(request)` pattern
  - Evidence: `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py`
  - **Checkpoint:** Conditional pattern still present — if hardened already, skip Phase 2

- P0-03: **Verify outbox uses gen_random_uuid()** — read `main.py:1800-1815`
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py`
  - **Checkpoint:** `gen_random_uuid()` still in outbox INSERT — if forwarding already, skip Phase 4

- P0-04: **Verify rate limiter unwired** — grep for `check_rate_limit` or `rate_limit` calls in orchestration routes
  - Evidence: Zero calls in orchestration code
  - **Checkpoint:** Still unwired — if wired already, skip Phase 5

- P0-05: **Capture baseline validation** — `make validate-local` in monorepo
  - Evidence: Exit 0

### Gate P0
- All 7 gaps confirmed current (or specific gaps marked as already-fixed with evidence)
- `make validate-local` passes at baseline

---

## Phase 1 — Canonical Truth Enforcement (End Split-Brain)

**Complexity:** M
**Estimated touch points:** 2-3 files

**Purpose:** Replace `.deal-registry` JSON reads with direct PostgreSQL queries so `zakops.deals` is the single source of truth for deal stage and status.

### Blast Radius
- **Services affected:** Backend (action engine)
- **Pages affected:** None directly (actions run server-side)
- **Downstream consumers:** All action executors that use `context_pack.build()` or `actions_runner` deal lookups

### Tasks

- P1-01: **Replace `_load_deal_registry()` and `_get_deal_from_registry()` in `context_pack.py`** — replace JSON reads (lines 213-230) with a PostgreSQL query against `zakops.deals` using the existing `asyncpg` pool.
  - Evidence: `/home/zaks/zakops-backend/src/actions/context/context_pack.py`
  - Decision: The function that calls `_get_deal_from_registry()` must be identified first. Trace callers to determine if async context is available.
  - **Checkpoint:** JSON read functions removed or replaced. Grep for `deal_registry.json` in context_pack.py returns 0 hits.

- P1-02: **Replace `DealRegistry(REGISTRY_PATH)` in `actions_runner.py`** — replace the JSON load at line 723 with a database query for the specific deal being acted on.
  - Evidence: `/home/zaks/zakops-backend/src/workers/actions_runner.py`
  - **Checkpoint:** Grep for `deal_registry.json` in actions_runner.py returns 0 hits.

- P1-03: **Verify no other backend files read from `.deal-registry` for deal stage/status** — sweep grep across `/home/zaks/zakops-backend/src/` for `deal_registry.json` or `DealRegistry`.
  - Evidence: Grep results
  - **IF** additional readers found → fix them in this phase
  - **ELSE** → proceed

### Decision Tree
- **IF** `context_pack.py` callers are async → use `await pool.fetchrow()` directly
- **ELSE IF** callers are sync → use `asyncio.run()` wrapper or refactor caller to be async
- **ELSE** → create a sync DB helper using `psycopg2` (last resort)

### Rollback Plan
1. `git checkout -- src/actions/context/context_pack.py src/workers/actions_runner.py`
2. Verify: action engine still reads from JSON (original behavior)
3. `make validate-local` passes

### Gate P1
- Zero references to `deal_registry.json` in `context_pack.py` and `actions_runner.py`
- Full grep sweep of `/home/zaks/zakops-backend/src/` for `deal_registry.json` returns only: registry creation/write paths (NOT read-for-truth paths)
- `make validate-local` passes

---

## Phase 2 — Injection Security (Hard-Required Auth)

**Complexity:** S
**Estimated touch points:** 1-2 files

**Purpose:** Make API key authentication mandatory on the quarantine injection path. No scenario where the endpoint is unauthenticated.

### Blast Radius
- **Services affected:** Backend (quarantine endpoint)
- **Pages affected:** None (dashboard uses session auth, not API key)
- **Downstream consumers:** Email-sync pipeline, any future LangSmith injector

### Tasks

- P2-01: **Harden `APIKeyMiddleware` for injection paths** — modify `apikey.py` so that when `ZAKOPS_API_KEY` is not set, POST/PUT/DELETE to `/api/quarantine*` returns 503 (service not configured) instead of silently allowing.
  - Evidence: `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py:18-42`
  - **Checkpoint:** With `ZAKOPS_API_KEY` unset, `curl -X POST localhost:8091/api/quarantine` returns 503 (not 201).

- P2-02: **Verify email-sync sends API key** — check email-sync configuration/code to confirm it sends `X-API-Key` header. If not, add it.
  - Evidence: Grep for `X-API-Key` or `api_key` in email-sync related files
  - **IF** email-sync already sends key → no change needed
  - **ELSE** → add key header to email-sync HTTP client

### Decision Tree
- **IF** `ZAKOPS_API_KEY` is already set in the running backend environment → existing callers are already sending it, change is safe
- **ELSE** → the middleware change will block injection until the env var is set (acceptable — this is the desired fail-closed behavior)

### Rollback Plan
1. `git checkout -- src/api/shared/middleware/apikey.py`
2. Verify: endpoint returns to open behavior when key is unset

### Gate P2
- `apikey.py` no longer has `if not expected_key: return await call_next(request)` for quarantine paths
- Quarantine injection path requires valid API key in all scenarios
- `make validate-local` passes

---

## Phase 3 — Ingest Contract Measurement (Shadow Mode + Dedup Distinction)

**Complexity:** M
**Estimated touch points:** 3-4 files

**Purpose:** Make the injection contract measurable: (1) callers can distinguish created vs deduplicated items by HTTP status, (2) shadow-mode items are filterable at the API and UI.

### Blast Radius
- **Services affected:** Backend (quarantine endpoint, quarantine list endpoint)
- **Pages affected:** Quarantine page (filter UI)
- **Downstream consumers:** Any caller of POST /api/quarantine (response code change for dedup path)

### Tasks

- P3-01: **Return HTTP 200 for dedup hits, 201 for new creates** — modify the quarantine POST handler so that when `existing` is found (lines 1520-1541), the response uses status 200 instead of 201.
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py:1520-1541`
  - **Checkpoint:** POST with duplicate `message_id` returns 200; new `message_id` returns 201.

- P3-02: **Add `source_type` filter to quarantine list endpoint** — add an optional `source_type` query parameter to the GET `/api/quarantine` endpoint so callers can filter by source type (e.g., `?source_type=langsmith_shadow`).
  - Evidence: Find the GET quarantine list endpoint in `main.py`
  - **Checkpoint:** `GET /api/quarantine?source_type=langsmith_shadow` returns only shadow items.

- P3-03: **Add source_type filter to quarantine UI** — add a filter dropdown or toggle to the quarantine page so users can filter by source type.
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
  - **Checkpoint:** UI renders a source_type filter control. TypeScript compiles.

### Rollback Plan
1. Backend: `git checkout -- src/api/orchestration/main.py`
2. Dashboard: `git checkout -- apps/dashboard/src/app/quarantine/page.tsx`
3. `make validate-local` passes

### Gate P3
- POST dedup returns 200, new create returns 201
- GET quarantine supports `source_type` query parameter
- Dashboard quarantine page has source_type filter
- `npx tsc --noEmit` passes
- `make validate-local` passes

---

## Phase 4 — Correlation ID End-to-End Propagation

**Complexity:** S
**Estimated touch points:** 1 file

**Purpose:** Forward the original correlation ID through the entire chain: quarantine → approval → deal creation → outbox event. No more broken chains.

### Blast Radius
- **Services affected:** Backend (outbox event creation in approval flow)
- **Pages affected:** None
- **Downstream consumers:** Any outbox event consumer that uses correlation_id for tracing

### Tasks

- P4-01: **Forward correlation_id to outbox INSERT** — in the `process_quarantine` handler (approval flow), replace `gen_random_uuid()` at line ~1800-1815 with the quarantine item's `correlation_id`. If the quarantine item has no correlation_id (legacy items), fall back to `gen_random_uuid()`.
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py:1800-1815`
  - **Checkpoint:** After change, the outbox INSERT uses `$3` (correlation_id from quarantine row) instead of `gen_random_uuid()`.

- P4-02: **Verify correlation_id is available in the approval flow** — trace the data flow from quarantine row fetch through to the outbox INSERT to confirm `correlation_id` is in scope.
  - Evidence: Read the approval handler to find where the quarantine row is fetched
  - **Checkpoint:** `correlation_id` field is accessible from the fetched quarantine row at the point of outbox INSERT.

### Rollback Plan
1. `git checkout -- src/api/orchestration/main.py` (only the outbox section)
2. Verify: outbox events go back to `gen_random_uuid()`

### Gate P4
- Outbox INSERT for `deal_created` events uses the quarantine item's `correlation_id` (not a fresh UUID)
- Legacy items without correlation_id still work (fallback to `gen_random_uuid()`)
- `make validate-local` passes

---

## Phase 5 — Flood Protection (Rate Limiting)

**Complexity:** S
**Estimated touch points:** 1-2 files

**Purpose:** Wire the existing `RateLimiter` to the quarantine injection path so burst floods are throttled.

### Blast Radius
- **Services affected:** Backend (quarantine POST endpoint)
- **Pages affected:** None
- **Downstream consumers:** Any injector (email-sync, LangSmith) — will receive 429 if rate limited

### Tasks

- P5-01: **Create an injection-specific rate limiter** — instantiate a new `RateLimiter` in `security.py` with a limit appropriate for injection traffic (120 requests/minute — 2x the general limiter, accommodating email-sync bursts).
  - Evidence: `/home/zaks/zakops-backend/src/api/shared/security.py:147-149`
  - **Checkpoint:** `injection_rate_limiter` instance exists in security.py.

- P5-02: **Wire rate limiting to quarantine POST** — call `check_rate_limit()` (or equivalent) at the top of the `create_quarantine_item` handler in `main.py`, keyed on the source IP or API key.
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py:1486-1491`
  - **Checkpoint:** Sending >120 requests/minute to POST `/api/quarantine` results in HTTP 429 responses.

### Decision Tree
- **IF** `check_rate_limit()` at security.py:152-172 already returns a proper 429 response → import and call it
- **ELSE** → create a lightweight dependency function that returns 429 on limit exceeded

### Rollback Plan
1. Remove rate limiter call from quarantine handler
2. `git checkout -- src/api/shared/security.py src/api/orchestration/main.py`

### Gate P5
- `injection_rate_limiter` exists with 120/min limit
- Quarantine POST is rate-limited (verified by code inspection — live burst test optional)
- `make validate-local` passes

---

## Phase 6 — Documentation & Final Verification

**Complexity:** S
**Estimated touch points:** 2-3 files

**Purpose:** Document the hardened injection contract and verify all changes together.

### Tasks

- P6-01: **Document the injection contract** — create or update `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` with: endpoint, required headers, auth requirements, rate limits, response codes (200 vs 201), correlation ID behavior, source_type values.
  - Evidence: New file at documented path

- P6-02: **Run full validation** — `make validate-local` in monorepo + `npx tsc --noEmit` in dashboard
  - Evidence: Exit 0 for both

- P6-03: **Update CHANGES.md** — record all changes from this mission
  - Evidence: `/home/zaks/bookkeeping/CHANGES.md`

- P6-04: **Write completion report** — generate completion report with evidence paths for every AC
  - Evidence: `/home/zaks/bookkeeping/docs/_qa_evidence/LANGSMITH-INTAKE-HARDEN-001-COMPLETION.md`

### Gate P6
- `INJECTION-CONTRACT.md` exists and covers all 5 hardening areas
- `make validate-local` passes
- `npx tsc --noEmit` passes
- CHANGES.md updated
- Completion report produced

---

## Dependency Graph

```
Phase 0 (Discovery)
    │
    ├──────────────────────────────┐
    ▼                              ▼
Phase 1 (Split-Brain)        Phase 2 (Auth)
    │                              │
    ├──────────────┐               │
    ▼              ▼               │
Phase 3 (Measurement)    Phase 4 (Correlation)
    │              │               │
    └──────────────┼───────────────┘
                   ▼
           Phase 5 (Rate Limiting)
                   │
                   ▼
           Phase 6 (Docs + Verification)
```

Notes:
- Phase 1 and Phase 2 can execute in parallel (no dependencies between them)
- Phase 3 depends on Phase 1 completing (quarantine changes in main.py)
- Phase 4 can execute in parallel with Phase 3 (different code sections in main.py)
- Phase 5 depends on Phase 2 (auth must be wired before rate limiting makes sense)
- Phase 6 runs after all others

---

## Acceptance Criteria

### AC-1: Canonical Truth
Zero references to `.deal-registry` JSON for deal stage/status lookups in `context_pack.py` and `actions_runner.py`. All deal stage/status reads come from PostgreSQL `zakops.deals`.

### AC-2: Injection Auth
Quarantine POST endpoint requires valid `X-API-Key` in ALL scenarios. When `ZAKOPS_API_KEY` is unset, the endpoint returns 503 (not silently open).

### AC-3: Measurement Capability
Quarantine POST returns 200 for dedup hits and 201 for new creates. Quarantine list endpoint supports `source_type` filter. Dashboard quarantine page has source_type filter UI.

### AC-4: Correlation Chain
Outbox events created during quarantine approval use the original `correlation_id` from the quarantine item (not `gen_random_uuid()`). Legacy items without correlation_id fall back to `gen_random_uuid()`.

### AC-5: Flood Protection
Quarantine POST is rate-limited with a dedicated `injection_rate_limiter` (120 requests/minute). Exceeding the limit returns HTTP 429.

### AC-6: Documentation
`INJECTION-CONTRACT.md` exists documenting endpoint, auth, rate limits, response codes, correlation behavior, and source_type values.

### AC-7: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes. No existing tests broken.

### AC-8: Bookkeeping
CHANGES.md updated. Completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/LANGSMITH-INTAKE-HARDEN-001-COMPLETION.md`.

---

## Guardrails

1. **Scope fence** — This mission hardens the existing injection pipeline. It does NOT build LangSmith SDK integration, does NOT add new database tables or migrations, and does NOT modify deal state transitions.
2. **No new SQL migrations** — All required columns already exist (migration 029). Changes are code-level only.
3. **Generated files never edited** — Per standing deny rules.
4. **WSL safety** — `sed -i 's/\r$//'` on any new .sh files. `sudo chown zaks:zaks` on files under `/home/zaks/`.
5. **Surface 9 compliance** — Any dashboard UI changes follow design system conventions.
6. **Contract surface discipline** — This mission does NOT change OpenAPI specs. No `make sync-*` needed unless an API response shape changes.
7. **Preserve email-sync** — The email-sync pipeline must continue to work after auth hardening. Verify it sends the API key.
8. **Fail-closed over fail-open** — Auth and rate limiting must fail closed (block access) not fail open (allow access) when misconfigured.
9. **Backward-compatible response codes** — The 200 (dedup) vs 201 (new) change is intentional. Document it clearly. Existing callers checking for `status < 300` are unaffected.
10. **Port 8090 FORBIDDEN** — Per standing rules.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify ALL 7 gaps are still current, or did I assume the forensic report is still accurate?"
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I check ALL backend source files for `.deal-registry` reads, not just the two named in the report?"

### After every code change:
- [ ] "Am I fixing the specific instance AND sweeping for the same pattern elsewhere?"
- [ ] "Does this change fail closed (block) or fail open (allow) when misconfigured?"
- [ ] "Did I handle the legacy/null case? (e.g., quarantine items without correlation_id)"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks, or am I assuming they pass?"
- [ ] "Did I create new .sh files? → CRLF stripped?"
- [ ] "Did I create files under /home/zaks/? → Ownership fixed?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass RIGHT NOW?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce a completion report with evidence paths for every AC?"
- [ ] "Did I create ALL files listed in the Files to Create table?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-backend/src/actions/context/context_pack.py` | 1 | Replace JSON reads with PostgreSQL queries |
| `/home/zaks/zakops-backend/src/workers/actions_runner.py` | 1 | Replace DealRegistry JSON load with DB query |
| `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` | 2 | Fail-closed auth on injection paths |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | 3, 4, 5 | Dedup response codes, outbox correlation, rate limiting |
| `/home/zaks/zakops-backend/src/api/shared/security.py` | 5 | Add injection_rate_limiter instance |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | 3 | Source_type filter UI |
| `/home/zaks/bookkeeping/CHANGES.md` | 6 | Record all changes |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` | 6 | Injection contract documentation |
| `/home/zaks/bookkeeping/docs/_qa_evidence/LANGSMITH-INTAKE-HARDEN-001-COMPLETION.md` | 6 | Completion report |
| `/home/zaks/bookkeeping/mission-checkpoints/LANGSMITH-INTAKE-HARDEN-001.md` | All | Running checkpoint |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Quarantine endpoint source (read before modifying) |
| `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` | Auth middleware source |
| `/home/zaks/zakops-backend/src/api/shared/security.py` | Rate limiter source |
| `/home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py` | Idempotency pattern reference |
| `/home/zaks/bookkeeping/docs/_qa_evidence/INTAKE-COL-V2-PROGRAM-COMPLETION.md` | Prior mission completion report |

---

## Stop Condition

This mission is DONE when:
1. All 8 acceptance criteria (AC-1 through AC-8) are met
2. `make validate-local` passes
3. `npx tsc --noEmit` passes
4. All changes recorded in CHANGES.md
5. Completion report produced with evidence paths for every AC
6. Checkpoint file updated to reflect COMPLETE status

Do NOT proceed to:
- LangSmith SDK integration (separate future mission)
- New database migrations (not needed)
- Dashboard feature builds beyond the source_type filter
- QA verification (that is the successor mission: QA-LIH-VERIFY-001)

<!-- Adopted from Improvement Area IA-2 (Crash Recovery) -->
<!-- Adopted from Improvement Area IA-1 (Context Checkpoint — not needed, mission is under 500 lines and has 6 phases) -->
<!-- Reviewed IA-10 (Test Naming) — N/A, no testing phase in this mission -->
<!-- Reviewed IA-12 (Benchmark Extraction) — N/A, no "raise to X standard" findings -->
<!-- Reviewed IA-14 (Multi-Agent Parity) — N/A, no hooks/rules/skills changes -->
<!-- Reviewed IA-15 (Governance Surfaces) — N/A, no dependency/env/error taxonomy changes -->

---

*End of Mission Prompt — LANGSMITH-INTAKE-HARDEN-001*

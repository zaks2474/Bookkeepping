# DEAL-INTEGRITY-001 — MASTER DIAGNOSIS & PERMANENT FIX PLAN

- **agent_name:** Claude Code (Opus 4.6)
- **run_id:** `20260208T164604Z`
- **timestamp:** 2026-02-08T16:46:04Z
- **pass:** 3 — FINAL CONSOLIDATION
- **repo_revision:** backend=`444dff6`, agent-api=`5eb7ce6`

**Input reports consolidated (6 total):**

| Pass | Agent | Run ID | Report |
|------|-------|--------|--------|
| 1 | CloudCode (CC3) | `20260208T160103Z` | `DEAL-INTEGRITY-001.PASS1.CloudCode.20260208T160103Z.md` |
| 1 | Codex | `20260208-1015-c1xh` | `DEAL-INTEGRITY-001.PASS1.Codex.20260208-1015-c1xh.md` |
| 1 | CloudCode (CC1) | `20260208-0500-pass1` | `DEAL-INTEGRITY-001.PASS1.CloudCode.20260208-0500-pass1.md` |
| 2 | Codex | `20260208-1025-q1zg` | `DEAL-INTEGRITY-001.PASS2.Codex.20260208-1025-q1zg.md` |
| 2 | CloudCode (CC1) | `20260208-1700-pass2` | `DEAL-INTEGRITY-001.PASS2.CloudCode.20260208-1700-pass2.md` |
| 2 | CloudCode (CC3) | `20260208T162638Z` | `DEAL-INTEGRITY-001.PASS2.CloudCode.20260208T162638Z.md` |

---

## 1) Executive Summary

### The ONE Systemic Diagnosis

The deal pipeline crisis stems from **two independent systemic defects** that combine to produce all observed symptoms:

**Defect A — Incoherent Deal Lifecycle State Machine.** The `deals` table encodes visibility/lifecycle through three uncoordinated fields (`status`, `stage`, `deleted`) with no enforced coupling between them. The archive endpoint updates only `stage='archived'`, leaving `status='active'` and `deleted=false`. This single partial transition cascades into five observable symptoms: count disagreements, pipeline sum mismatches, archived deals in active views, broken filters, and perceived propagation failures.

**Defect B — Split-Brain Database Infrastructure.** Two PostgreSQL containers run simultaneously: the canonical `zakops-backend-postgres-1` on port 5432 (49 deals) and a legacy `zakops-postgres` on port 5435 (51 stale deals). The backend API writes to 5432; ops scripts and potentially other services query 5435. This produces divergent counts and makes UI-created deals invisible to some consumers.

These defects are **independent**: Defect A would exist even with one DB (the archive endpoint is broken regardless); Defect B would exist even with a perfect data model (two DBs always diverge). **Both must be fixed for full resolution.**

### Why Counts Drift (The Mechanism)

Each surface applies a different filter combination to potentially different underlying data:

| Surface | Count | Filter Logic | DB |
|---------|-------|-------------|-----|
| DB (5432) total | 49 | All rows | Canonical |
| DB (5435) total | 51 | All rows | **Rogue** |
| API `GET /api/deals` | 37 | `deleted=FALSE` + `status='active'` (no-op) | 5432 |
| /hq header | 37 | `deals.length` from API | 5432 |
| /hq pipeline cards | 31 | Client-side count using 7 of 9 stages | 5432 |
| Ops `psql` (localhost) | 51 | Direct query | **5435** |

The 49→37 gap = 12 soft-deleted deals. The 37→31 gap = 6 archived-stage deals hidden from pipeline cards. The 51→49 gap = 2 stale deals in the rogue DB.

### Why Archived Leaks into Active (The Mechanism)

The archive endpoint (`POST /api/deals/{deal_id}/archive`, `main.py:867-907`) executes:
```sql
UPDATE zakops.deals SET stage = 'archived', updated_at = NOW() WHERE deal_id = $1
```
It sets **only** `stage`. It does NOT set `status='archived'` or `deleted=true`. The deals listing endpoint (`main.py:466-513`) filters `WHERE deleted = FALSE` and optionally `WHERE status = $N` (default `'active'`). Since all 49 deals have `status='active'`, the status filter is a no-op. Archived-stage deals pass through every filter meant to exclude them.

### Why the Zod Error Happens (The Mechanism)

Three contributing factors (not mutually exclusive, explaining "intermittent" nature):

1. **Promise.all fragility** (`hq/page.tsx:38-46`): 4 parallel fetches, 3 without individual try/catch. Any single `ApiError` blanks the entire HQ page.
2. **Agent activity schema mismatch**: `/api/agent/activity` sometimes returns `[]` (array) instead of the expected object `{status, recent, stats, ...}`. `AgentActivityResponseSchema` fails `safeParse`.
3. **Quarantine endpoint instability**: `/api/actions/quarantine` can return non-200 or unexpected shapes, triggering `getQuarantineQueue`'s unprotected `safeParse` failure.

Factor 1 is the **amplifier** (turns any single failure into total blackout). Factors 2 and 3 are **triggers** (specific endpoints that intermittently misbehave).

### Why Creation Doesn't Propagate (The Mechanism)

Two factors:

1. **Visual illusion (Dashboard-internal)**: Deal creation works correctly (`POST /api/deals` inserts with `status='active'`, `stage='inbound'`). But the persistent header/pipeline gap from archived deals makes it look like new deals "don't stick" — the gap remains after creation.
2. **Split-brain data loss (cross-service)**: If the Agent API or RAG service connects to the legacy DB on port 5435, deals created via the Dashboard (→ Backend → DB 5432) are genuinely invisible to those services.

---

## 2) Deduped Issue Registry

### DI-ISSUE-001: Archive Endpoint Performs Partial State Transition

**Severity:** CRITICAL — root cause of DI-ISSUE-002, 003, 004; partial cause of 007
**Confirming agents:** CC3, Codex, CC1 (unanimous across all 6 reports)

#### 1) Confirmed Root Cause (with Evidence)

The `POST /api/deals/{deal_id}/archive` endpoint (`main.py:867-907`) only sets `stage = 'archived'`. It does NOT set `status = 'archived'` or `deleted = true`. Since all 49 deals have `status = 'active'` (the only value ever written), API filters using `?status=active` return archived-stage deals alongside truly active ones. This single partial transition cascades into every downstream count disagreement, filter failure, and pipeline mismatch.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| Archive SQL: only `SET stage = 'archived'` | CC3 | `main.py:881-884` |
| Archive SQL: only `SET stage = 'archived'` | Codex | `main.py:868` via `_evidence/DEAL-INTEGRITY-001-PASS1/backend-main-archive-handlers.txt` |
| DB status: all `'active'` | CC3 | `evidence/00-forensics/db-distinct-statuses.txt` |
| DB status: all `'active'` | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/db-count-by-status-now.txt` |
| 6 archived-stage deals with `deleted=false` | CC3 | `evidence/00-forensics/db-archived-stage-deals.txt` |
| `?status=archived` returns 0 results | CC3 | `evidence/00-forensics/api-deals-archived-filter.txt` |

#### 2) Permanent Fix Approach

1. Modify `POST /api/deals/{deal_id}/archive` to atomically set both: `SET stage = 'archived', status = 'archived', updated_at = NOW()`
2. Backfill existing data: `UPDATE zakops.deals SET status = 'archived' WHERE stage = 'archived' AND deleted = false`
3. Add DB CHECK constraint: `CHECK (stage != 'archived' OR status = 'archived')`
4. Modify `POST /api/deals/{deal_id}/restore` to atomically reset `status = 'active'` when restoring
5. Create a `transition_deal_state(deal_id, target_state)` function — all endpoints call this instead of raw UPDATE queries

#### 3) Industry Best Practice

**Atomic State Transitions via Finite State Machine (FSM).** All three agents converge: Salesforce uses `StageName` with derived `IsClosed`/`IsWon`/`ForecastCategory` recalculated atomically on every stage change. HubSpot uses `dealstage` within a pipeline definition. PipeDrive uses `stage_id`. The standard is a **single authoritative lifecycle field** with validated transitions where a deal cannot occupy an impossible state combination.

#### 4) Why It Fits THIS System

ZakOps has three overlapping state signals (`status`, `stage`, `deleted`) with no enforced coupling. The archive endpoint updates one and ignores the other two, creating phantom states (`status='active' + stage='archived'`). An FSM eliminates impossible states and makes every transition auditable.

#### 5) "Never Again" Enforcement

- **DB CHECK constraint:** `(stage = 'archived') → (status = 'archived')` — prevents partial transitions at the data layer
- **Integration test:** "After archiving, `GET /api/deals?status=active` must NOT return the archived deal"
- **Integration test:** "After archiving, `GET /api/deals?status=archived` MUST return the deal"
- **Code gate:** All state transitions via `transition_deal_state()` function — no raw UPDATE queries for state changes
- **DB trigger:** Auto-enforce status/stage/deleted consistency on every write

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Lifecycle State ENUM Column** | CC3 | Add `lifecycle_state` ENUM (`active`, `archived`, `deleted`). Backfill from current data. All queries use this single field. Deprecate `status` column (always `'active'`, adds no information). | Clean, single-field solution. Requires migration + backfill + endpoint updates. Eliminates the entire class of "which field do I check?" bugs. |
| 2 | **Computed Column `is_active`** | CC1-P2 | `is_active BOOLEAN GENERATED ALWAYS AS (status = 'active' AND stage != 'archived') STORED`. Index it. All "active" queries use `WHERE is_active = true`. | Zero application code changes for enforcement. Backward compatible. Can be added alongside existing fields. Slight schema complexity. |

---

### DI-ISSUE-002: Deal Counts Disagree Across Surfaces

**Severity:** HIGH — user-facing, undermines operator trust
**Confirming agents:** CC3, Codex, CC1 (unanimous)
**Dependency:** Partially resolves when DI-ISSUE-001 is fixed; fully resolves when DI-ISSUE-006 is also fixed

#### 1) Confirmed Root Cause (with Evidence)

Multiple surfaces report different deal counts because each applies a different filter combination to potentially different underlying data. The API returns all 37 non-deleted deals (status filter is a no-op since all deals are `'active'`). The /hq header uses `deals.length` (37). The /hq pipeline cards count only 7 of 9 stages (31). Ops scripts may query the rogue DB (51).

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| DB (5432) total: 49 | CC3 | `evidence/00-forensics/db-total-count.txt` |
| DB (5435) total: 51 | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt` |
| API returns 37 | CC3 | `evidence/00-forensics/api-deals-unfiltered.txt` |
| Pipeline summary: archived=6, total=37 | CC3 | `evidence/00-forensics/api-pipeline-summary.txt` |
| Surface count breakdown table | CC3 | PASS 1 Report §Issue 1 |

#### 2) Permanent Fix Approach

1. Fix DI-ISSUE-001 (archive sets `status='archived'`) so `?status=active` excludes archived deals
2. Fix DI-ISSUE-006 (eliminate rogue DB) so all services query the same data
3. Add `total_count` to `/api/deals` response so UI doesn't rely on `array.length`
4. Ensure `v_pipeline_summary` excludes archived-stage deals from pipeline totals or presents them separately

#### 3) Industry Best Practice

**Single Source of Truth (SSOT) + Server-Side Aggregation.** Salesforce, HubSpot, and Monday.com compute pipeline counts server-side and return structured summary objects. The client renders what the server provides — no client-side re-counting. Additionally: paginated list endpoints must return `total_count` to prevent UI count drift.

#### 4) Why It Fits THIS System

ZakOps is a multi-layer system (Dashboard → Backend → Agent → DB). If any layer counts differently, every surface disagrees. The backend already has `GET /api/pipeline/summary` — the /hq page ignores it and re-counts client-side.

#### 5) "Never Again" Enforcement

- **Contract test:** `sum(stage_counts) == total_active_deals` in every pipeline summary response
- **CI gate:** API count and DB count must match
- **UI invariant test:** `/api/deals/count` must equal `/api/pipeline/summary.total`
- **Startup gate:** Backend refuses to start if DB URL differs from canonical DSN

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **API Returns `total_count` with Paginated List** | Codex | Standard REST pagination: `{total_count: N, deals: [...]}`. UI uses `total_count` instead of `array.length`. | Minimal change. Immediate improvement. Prevents drift when pagination kicks in (50+ deals). |
| 2 | **DB Identity Tagging** | Codex | Add `db_instance_id` row in meta table, echo in every API response header. UI/ops can detect split-brain instantly. | Huge ops clarity. Small schema addition. Catches DI-ISSUE-006-class bugs immediately. |

---

### DI-ISSUE-003: Pipeline Stage Totals Don't Sum to Header Count

**Severity:** HIGH — user-facing, visible math error on /hq
**Confirming agents:** CC3, Codex, CC1 (unanimous)
**Dependency:** Partially resolves when DI-ISSUE-001 is fixed

#### 1) Confirmed Root Cause (with Evidence)

The `/hq` page (`hq/page.tsx:18-26`) defines `PIPELINE_STAGES` as a hardcoded 7-element array: `['inbound', 'screening', 'qualified', 'loi', 'diligence', 'closing', 'portfolio']`. This excludes `'archived'` and `'junk'` from the 9 valid stages. The header shows `total_active_deals: deals.length` = 37 (all non-deleted), but pipeline cards sum to 31. The gap of 6 = exactly the archived-stage deals.

Additionally, the /hq page computes stage counts **client-side** despite the backend already providing server-computed counts via `GET /api/pipeline/summary`. The /hq page ignores this endpoint entirely.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| `PIPELINE_STAGES` array (7 entries) | CC3 | `hq/page.tsx:18-26` |
| Client-side counting logic | CC3 | `hq/page.tsx:62-66` |
| Header = `deals.length` = 37 | CC3 | `hq/page.tsx:72` |
| Archived = 6, total = 37 | CC3, CC1 | `evidence/00-forensics/api-pipeline-summary.txt` |

#### 2) Permanent Fix Approach

1. Use `GET /api/pipeline/summary` for stage counts instead of client-side computation
2. Either exclude archived-stage deals from the header count OR add an "Archived" card
3. Define "active" consistently: `total_active_deals` should only count pipeline-stage deals
4. Handle `'junk'` stage (currently 0 but exists in CHECK constraint)

#### 3) Industry Best Practice

**Server-Side Pipeline Aggregation.** Pipeline dashboards (Grafana, Datadog, Vercel Analytics) compute counts server-side. The client renders, does not re-count. **Consistent Domain Invariants:** All displayed totals must equal the sum of displayed parts.

#### 4) Why It Fits THIS System

The backend already HAS `GET /api/pipeline/summary` returning server-computed counts. The /hq page ignores it and re-computes client-side with a different stage list. Using the existing endpoint eliminates the divergence immediately.

#### 5) "Never Again" Enforcement

- **Contract test:** Pipeline totals must equal sum of displayed stage totals
- **Contract test:** `sum(all stage counts) == total count` in pipeline summary response
- **Code review gate:** No hardcoded stage lists in frontend — derive from shared config or API

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Canonical Stage Configuration Object** | CC3 + Codex | Shared `STAGE_CONFIG` with `pipeline: boolean` flag per stage. Backend and frontend derive all stage lists from it. Archived cannot be omitted unless explicitly flagged. | Single source of truth. Requires contracts package integration (already exists in ZakOps). |
| 2 | **Backend-Driven Pipeline Definition** | CC3 | `GET /api/pipeline/config` returns `{pipeline_stages: [...], terminal_stages: [...], default_stage: "inbound"}`. Frontend renders whatever backend declares. | Maximum flexibility. Adding/removing stages = zero frontend changes. Adds cacheable API call. |

---

### DI-ISSUE-004: Active Filter Doesn't Actually Filter

**Severity:** MEDIUM — user-facing, causes confusion
**Confirming agents:** CC3, Codex, CC1 (unanimous)
**Dependency:** Fully resolves when DI-ISSUE-001 is fixed

#### 1) Confirmed Root Cause (with Evidence)

The `/deals` page status filter dropdown offers `['active', 'junk', 'merged']` and defaults to `'active'`. This sends `?status=active` to the API. Since all deals have `status='active'` (archive never changes it), the filter returns ALL 37 non-deleted deals including archived-stage ones. The filter is technically correct but semantically broken.

Furthermore: no `'archived'` option in the dropdown, `'junk'` and `'merged'` return 0 results, and no stage-based filter exists.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| Filter values: `active/junk/merged` | CC3 | `deals/page.tsx:66` |
| Default: `'active'` | CC3 | `deals/page.tsx:94` |
| All deals `status='active'` | CC3 | `evidence/00-forensics/db-distinct-statuses.txt` |
| Active filter returns 37 (= unfiltered) | CC3 | `evidence/00-forensics/api-deals-active-filter.txt` |

#### 2) Permanent Fix Approach

1. Fix DI-ISSUE-001 first — makes the filter meaningful
2. Add `'archived'` to the dropdown
3. Replace single-field filter with composite filter: lifecycle + stage
4. Update backend semantics: `active` = `deleted=false AND stage!='archived'`

#### 3) Industry Best Practice

**Filter-by-What-Users-See.** Salesforce and HubSpot expose filters matching the user's mental model ("active deals", "archived deals", "deals in screening"), not raw DB column values.

#### 4) Why It Fits THIS System

Users see deals in a pipeline with stages. The natural filter is "show me archived deals" or "show me deals in screening." The current options (`active/junk/merged`) don't map to any meaningful user action.

#### 5) "Never Again" Enforcement

- **API test:** `GET /api/deals?status=active` must NOT return archived-stage deals
- **DB constraint or trigger:** Enforce status/stage consistency
- **Derive filter options from stage config** (see DI-ISSUE-003) so they stay in sync

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Faceted Search with Counts** | CC3 | Display `Active (31) | Archived (6) | All (37)` with sub-facets per stage. Counts from pipeline summary API. | Excellent UX. Users see distribution at a glance. Standard in CRM/e-commerce UIs. |
| 2 | **Dedicated `visibility_state` Filter Enum** | Codex | Backend exposes `visibility_state` (active/archived/junk) for all list queries. Decouples filter semantics from raw DB columns. | Clean semantics. Requires migration. Single source of truth for visibility logic. |

---

### DI-ISSUE-005: Zod Validation Error on Operator HQ (Intermittent)

**Severity:** MEDIUM — intermittent, causes blank HQ or console errors
**Confirming agents:** CC3, Codex, CC1 (all confirm; three non-mutually-exclusive contributing factors identified)

#### 1) Confirmed Root Cause (with Evidence)

**Factor A — Promise.all fragility (CC3):** The `/hq` page uses `Promise.all` with 4 parallel fetches. Three of four (`getDeals`, `getKineticActions`, `getQuarantineQueue`) lack individual try/catch. Any single `ApiError` rejects the entire `Promise.all`, blanking all HQ data.

**Factor B — Agent activity schema mismatch (Codex):** `/api/agent/activity` sometimes returns `[]` (empty array) instead of the expected object `{status, recent, stats, ...}`. The `AgentActivityResponseSchema` (`api.ts:1926`) expects an object, so `safeParse` fails.

**Factor C — Quarantine endpoint instability (CC3):** `getQuarantineQueue` calls `/api/actions/quarantine` without try/catch. Non-200 responses or unexpected shapes trigger unhandled errors.

Factor A is the **amplifier** (structural fragility). Factors B and C are **triggers** (specific endpoints that intermittently misbehave).

**Note:** CC1 hypothesized archived deals with missing fields could also trigger Zod failures, but CC3 found `DealSchema` uses `.passthrough()` which is tolerant of missing fields, weakening this theory.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| Promise.all: 3 of 4 unprotected | CC3 | `hq/page.tsx:38-46` |
| `getQuarantineQueue`: no try/catch | CC3 | `api.ts:758-778` |
| `apiFetch` throws on non-200 | CC3 | `api.ts:397-404` |
| `/api/agent/activity` returns `[]` | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/api-agent-activity.txt` |
| Schema expects object | Codex | `api.ts:1926-1948` via `dashboard-lib-api.txt` |

**NEEDS VERIFICATION:** Open `/hq` with DevTools console to identify which specific schema triggers the Zod error. Commands:
```bash
curl -s http://localhost:3003/api/agent/activity | python3 -c "import sys,json; d=json.load(sys.stdin); print(type(d).__name__, list(d.keys()) if isinstance(d,dict) else len(d))"
curl -s -o /dev/null -w '%{http_code}' http://localhost:8091/api/actions/quarantine
```

#### 2) Permanent Fix Approach

1. Replace `Promise.all` with `Promise.allSettled` in `/hq`
2. Add individual try/catch to `getQuarantineQueue` and `getKineticActions` (match `getAgentActivity`'s existing pattern)
3. Align `/api/agent/activity` response shape: always return typed object, never `[]`
4. Add visual indicator per widget on failure ("Failed to load quarantine data") instead of blanking entire page

#### 3) Industry Best Practice

**Per-Widget Error Boundaries + Schema-First API Contracts.** Dashboard frameworks (Grafana, Datadog) use independent error boundaries per widget. Each section fetches its own data and fails independently. Schema-first contracts with CI validation ensure response shapes match in all environments.

#### 4) Why It Fits THIS System

HQ aggregates 4 independent data sources (deals, pending actions, quarantine, agent activity). A quarantine API failure should not blank pipeline data. The current all-or-nothing fetch is fragile by design.

#### 5) "Never Again" Enforcement

- **Contract test:** `/api/agent/activity` must return an object matching `AgentActivityResponseSchema`
- **UI test:** HQ renders pipeline data even when quarantine or agent API returns 500
- **UI test:** HQ renders without Zod errors in mock mode
- **Code invariant:** All API fetcher functions must have individual try/catch — never throw through `Promise.all`

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **React Suspense Boundaries per Widget** | CC3 | Each HQ section in its own `<Suspense>` + `<ErrorBoundary>`. Errors isolated per widget. Supports streaming SSR. | Clean React pattern. Requires refactoring /hq into sub-components. Better long-term architecture. |
| 2 | **Contract Tests in CI (Zod vs Actual API)** | CC1 | CI job runs Zod schemas against actual API endpoint responses (or fixtures from test DB). Detects schema drift before deployment. | Catches drift pre-production. Requires test DB fixture maintenance. High prevention value. |

---

### DI-ISSUE-006: Split-Brain Database (Two Postgres Instances)

**Severity:** CRITICAL — causes data invisibility / divergent counts
**Confirming agents:** Codex, CC1 (both confirmed independently)
**Note:** CC3 did NOT investigate this — all queries were via `docker exec zakops-backend-postgres-1` (port 5432 only)

#### 1) Confirmed Root Cause (with Evidence)

Two PostgreSQL containers run simultaneously:

| Container | Port | Deals | Used By |
|-----------|------|-------|---------|
| `zakops-backend-postgres-1` | 5432 | 49 | Backend API (runtime `DATABASE_URL=postgresql://zakops:zakops_dev@postgres:5432/zakops`) |
| `zakops-postgres` (legacy) | 5435 | 51 | Potentially: ops scripts, local `psql`, legacy tools, `.env` files with wrong DSN |

The backend API writes to 5432. Any service or script querying 5435 sees stale data. Deals created via the UI go to 5432 and are invisible on 5435. CC1 identified the specific source: `infra/docker/docker-compose.yml` spins up the separate DB on 5435.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| Backend runtime DB = `postgres:5432` | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/backend-env-db.txt` |
| Local queries on `localhost:5435` | Codex | `zakops-backend/.env` |
| Two Postgres containers | CC1 | `docker ps` output cited in report §Issue 4 |
| DB 5432: 49 deals | CC3, CC1 | `evidence/00-forensics/db-total-count.txt` / `db-real-total-count.txt` |
| DB 5435: 51 deals | Codex, CC1 | `_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt` |

**NEEDS VERIFICATION:** Confirm both containers still exist:
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep postgres
```

#### 2) Permanent Fix Approach

1. Stop and remove the legacy `zakops-postgres` container (port 5435)
2. Audit ALL `.env` files and `docker-compose` configs — ensure every service points to `postgres:5432` / `zakops-backend-postgres-1`
3. Remove or comment out the secondary Postgres definition in `infra/docker/docker-compose.yml`
4. Add DB identity to `/health` endpoint (host/port/dbname) so ops can verify

#### 3) Industry Best Practice

**Single Source of Truth (SSOT) per environment.** Multiple DBs = split-brain. All read models derive from one canonical DB. **Service Discovery / Env Injection** (Doppler, Vault, or Docker secrets) prevents DSN drift by injecting the single correct DB URL into all containers at runtime.

#### 4) Why It Fits THIS System

ZakOps has multiple services (Backend, Agent API, RAG) and ops tooling. If any connects to a different DB, counts diverge and writes become invisible. The 51-vs-49 gap and the 6-vs-4 archived count discrepancy between agents are direct evidence of this already happening.

#### 5) "Never Again" Enforcement

- **Startup gate:** Backend refuses to start if DB URL differs from canonical DSN
- **CI/Smoke:** `curl /health` must report same DB identity as ops `psql`
- **Docker-compose:** Single `depends_on` Postgres service; no secondary containers
- **Ops runbook:** Standard `psql` via `docker exec`, never via localhost port forwarding

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Health Endpoint with DB Identity** | Codex | `/health` returns `{db_host, db_port, db_name, db_instance_id}`. Ops scripts validate before querying. Immediately detects split-brain. | Minimal change. Huge ops clarity. First-line defense against future drift. |
| 2 | **Service Discovery / Env Injection** | CC1 | Use Doppler/Vault/Docker secrets to inject single correct DB URL into all containers at runtime. Prevents config drift by making it physically impossible to have divergent DSNs. | Adds infra dependency but eliminates the entire class of "wrong DB URL" bugs. |

---

### DI-ISSUE-007: UI-Created Deals Don't Fully Propagate

**Severity:** MEDIUM — user-facing, new deals appear inconsistently
**Confirming agents:** CC3, Codex, CC1 (all confirm)
**Dependency:** Fully resolves when DI-ISSUE-001 + DI-ISSUE-006 are fixed

#### 1) Confirmed Root Cause (with Evidence)

**Factor A — Visual illusion (CC3):** Deal creation via `POST /api/deals` works correctly — inserts with `status='active'`, `stage='inbound'`, `deleted=false`, creates `deal_created` event. The deal appears in `/deals` and `/hq` pipeline. But the persistent header/pipeline gap (DI-ISSUE-003) creates a perception of non-propagation.

**Factor B — Split-brain data loss (Codex, CC1):** If Agent API or RAG connects to the legacy DB (port 5435), deals created via Dashboard (→ Backend → DB 5432) are genuinely invisible to those services.

Both factors are real. Factor A is visual; Factor B is actual data loss. Fixing DI-ISSUE-001 resolves A; fixing DI-ISSUE-006 resolves B.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| Deal creation SQL correct | CC3 | `main.py:565-621` |
| 21 inbound deals (creation works) | CC3 | `evidence/00-forensics/db-full-breakdown.txt` |
| Backend writes to 5432 | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/backend-env-db.txt` |
| UI list uses `array.length` (no total_count) | Codex | `api.ts:426-452` |

#### 2) Permanent Fix Approach

1. Fix DI-ISSUE-001 (archive endpoint) — resolves the visual count illusion
2. Fix DI-ISSUE-006 (eliminate rogue DB) — resolves cross-service invisibility
3. Add `total_count` to `/api/deals` response
4. Add integration test: create deal → verify in /deals, /hq pipeline, and pipeline summary

#### 3) Industry Best Practice

**Optimistic UI Updates with Server Confirmation.** Modern CRMs immediately show the new deal before server confirms, then reconcile. Additionally: **Single-write DB with explicit read models** ensures all consumers see the same data.

#### 4) Why It Fits THIS System

UI-based creation should be visible to all layers (Dashboard, HQ, Agent). That requires: (a) all layers talk to the same DB, and (b) counts are computed consistently.

#### 5) "Never Again" Enforcement

- **E2E test:** Create deal → verify in /deals, /hq, pipeline summary, agent API
- **Startup gate:** All services verify DB identity matches canonical DSN
- **CI gate:** API count and DB count must match

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Optimistic UI Updates** | CC3 | After `createDeal()`, immediately add to local state. Reconcile on server response. Rollback on failure. | Instant feedback. Better UX. Requires rollback logic. |
| 2 | **API Returns `total_count`** | Codex | Standard REST pagination: `{total_count: N, deals: [...]}`. UI uses `total_count` instead of `array.length`. | Minimal change. Immediate improvement. Prevents future pagination-related count drift. |

---

### DI-ISSUE-008: `audit_trail` Column Referenced but Missing from Schema

**Severity:** LOW (latent) — will cause `UndefinedColumn` SQL error if code path is triggered
**Confirming agents:** CC3 only (Codex, CC1 did not report)

#### 1) Confirmed Root Cause (with Evidence)

Backend code references `audit_trail` column at `main.py:1103, 1142, 1263`, but the `zakops.deals` table schema has no such column. If any code path reaches these lines, it throws a PostgreSQL `UndefinedColumn` error.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| Column references in code | CC3 | `main.py:1103, 1142, 1263` |
| Column absent from schema | CC3 | `evidence/00-forensics/db-deals-schema.txt` |

#### 2) Permanent Fix Approach

Either add the `audit_trail` column via migration (if the feature is intended) or remove the dead code references. **Operator decision required** (see Section 3).

#### 3) Industry Best Practice

**Schema/code parity enforced by migration gates.** ORM-based systems (Django, Rails) detect column references to non-existent fields at startup or via CI migration checks.

#### 4) Why It Fits THIS System

ZakOps uses raw SQL — no ORM to detect missing columns at startup. Manual enforcement is required.

#### 5) "Never Again" Enforcement

- **CI gate:** Run `SELECT audit_trail FROM zakops.deals LIMIT 0` in test DB — must not error
- **Schema diff gate:** Compare SQL column references in code against live schema; fail on mismatch

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Schema Diff Gate** | Codex-P2 | Automated CI check: parse SQL references in Python code, compare against `\d+ zakops.deals` output. Fail build on mismatch. | Prevents all future schema drift. Requires SQL parsing tooling. |
| 2 | **Migration Assertion Test** | CC3 | Test DB fixture that runs all migrations and then executes every SQL template in the codebase with `LIMIT 0`. | Catches missing columns, wrong types, renamed tables. Test maintenance overhead. |

---

### DI-ISSUE-009: `/api/actions/kinetic` Returns HTTP 500

**Severity:** LOW — not called by dashboard, pollutes debugging
**Confirming agents:** CC3 only

#### 1) Confirmed Root Cause (with Evidence)

`GET /api/actions/kinetic` returns HTTP 500 Internal Server Error. The dashboard does not call this endpoint directly — `isKineticApiAvailable()` checks `/api/actions/capabilities` (returns 200), and `getKineticActions` calls `/api/actions?status=pending_approval` (returns 200 with `[]`). Impact is limited to debugging confusion.

**Evidence:**
| Evidence | Agent | Location |
|----------|-------|----------|
| HTTP 500 response | CC3 | `evidence/00-forensics/api-stats-endpoints.txt` |
| Dashboard doesn't call it directly | CC3 | `api.ts:1560-1607` |

#### 2) Permanent Fix Approach

Investigate the endpoint's handler. Either fix the implementation or remove the endpoint if deprecated.

#### 3) Industry Best Practice

**No dead endpoints.** Every endpoint is tested, documented, and returns valid responses. Unused endpoints are removed to reduce attack surface and debugging noise.

#### 4) Why It Fits THIS System

During incident response, a 500 from an unexpected endpoint wastes investigation time. Clean API surface = faster debugging.

#### 5) "Never Again" Enforcement

- **API health suite:** Automated test that hits every documented endpoint and asserts non-500
- **Endpoint inventory gate:** CI check that every route handler has at least one test

#### 6) Best 2 Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Endpoint Contract Inventory** | Codex-P2 | Automated detection of registered routes vs tested routes. Flag untested or dead endpoints. | Prevents endpoint rot. Requires route introspection tooling. |
| 2 | **Deprecation Header Pattern** | CC3 | Deprecated endpoints return `Deprecation: true` header + 200 with empty body instead of 500. Clients and monitoring can detect gracefully. | Clean degradation. Standard HTTP pattern (RFC 8594). |

---

### Additional Finding: Mission Prompt Uses Wrong Column Names

**Source:** Codex PASS 1
**Impact:** Causes false-negative "no rows" errors during investigation

The mission prompt's example DB queries use `id` and `name`, but the actual table uses `deal_id` and `canonical_name`. **Recommendation:** Update mission prompt to use correct column names for future missions.

---

## 3) Operator Decisions Required

Before fix missions can execute, the following decisions must be made:

### Decision 1: Archive Semantics — What Should "Archive" Mean?

**Options:**
| Option | Behavior | Pros | Cons |
|--------|----------|------|------|
| **A: Status Change** | Archive sets `status='archived'`, keeps `deleted=false` | Preserves distinction between archived (recoverable) and deleted. Minimal schema change. | Still has 3 fields to coordinate. |
| **B: Soft Delete** | Archive sets `deleted=true`, stage stays | Leverages existing `deleted` filter that already works. Simplest fix. | Loses distinction between "archived" and "deleted." |
| **C: Lifecycle ENUM** | New `lifecycle_state` column replaces `status` + `deleted`. | Cleanest long-term. Single field for all visibility logic. | Larger migration. Must update all query sites. |

**Recommendation:** Option A as immediate fix (lowest risk), with Option C as a follow-up if the team wants long-term cleanliness.

### Decision 2: Rogue Database Disposition

**Options:**
| Option | Action |
|--------|--------|
| **A: Kill immediately** | `docker stop zakops-postgres && docker rm zakops-postgres`. Verify no services depend on it. |
| **B: Dump then kill** | Export data from 5435 first (`pg_dump`), then kill. Preserves any unique data. |
| **C: Migrate then kill** | Compare 5435 data against 5432, merge any missing deals, then kill. |

**Recommendation:** Option B (dump then kill) — safe, preserves data, low risk.

### Decision 3: `audit_trail` Column — Add or Remove?

**Options:**
| Option | Action |
|--------|--------|
| **A: Add column** | Create migration `ALTER TABLE zakops.deals ADD COLUMN audit_trail JSONB DEFAULT '[]'`. Enable the feature. |
| **B: Remove references** | Delete the 3 code references in `main.py:1103, 1142, 1263`. No migration needed. |

**Recommendation:** Depends on whether audit trail is a desired feature. If yes → A. If dead code → B.

### Decision 4: Pipeline Display — Exclude or Show Archived?

**Options:**
| Option | Action |
|--------|--------|
| **A: Exclude from header** | Header count = only pipeline-stage deals. Archived not counted, not shown. |
| **B: Show Archived card** | Add an "Archived" pipeline card. Header = all non-deleted. Everything sums. |
| **C: Separate section** | Header = pipeline count. Below pipeline: "Archived (6) | Junk (0)" as a separate row. |

**Recommendation:** Option C — clear separation, everything visible, everything sums.

---

## 4) Proposed Fix Missions (Not Executed)

### Mission 1: DEAL-INFRA-UNIFY — Kill the Rogue Database

**Scope:** DI-ISSUE-006
**Priority:** Phase 0 (do first — eliminates noise from all subsequent investigation)

**Steps:**
1. Dump data from `zakops-postgres` (port 5435): `docker exec zakops-postgres pg_dump -U dealengine zakops > /home/zaks/bookkeeping/backups/rogue-db-5435-dump.sql`
2. Compare deal counts and identify any unique data in 5435 not in 5432
3. Stop and remove: `docker stop zakops-postgres && docker rm zakops-postgres`
4. Audit all `.env` files across repos for port 5435 references
5. Remove secondary Postgres definition from `infra/docker/docker-compose.yml`
6. Add DB identity to `/health` endpoint

**Gates:**
- `docker ps | grep postgres` shows exactly ONE container
- All `.env` files contain only `5432` for Postgres port
- `curl localhost:8091/health` reports DB identity matching canonical DSN
- `psql` via `docker exec zakops-backend-postgres-1` returns same count as API

**Evidence required:** Before/after `docker ps`, before/after `.env` diffs, API count == DB count

**Risks/Rollback:** If any service depended on 5435, it will fail at startup. Rollback: `docker start zakops-postgres` (if not removed) or restore from dump.

---

### Mission 2: DEAL-LIFECYCLE-FIX — Fix the Archive State Machine

**Scope:** DI-ISSUE-001 (root cause), resolves DI-ISSUE-002, 003, 004, 007 partially

**Steps:**
1. Modify archive endpoint (`main.py:867-907`) to set `status='archived'` alongside `stage='archived'`
2. Modify restore endpoint to set `status='active'` when restoring
3. Backfill: `UPDATE zakops.deals SET status = 'archived' WHERE stage = 'archived' AND deleted = false`
4. Add CHECK constraint: `CHECK (stage != 'archived' OR status = 'archived')`
5. Rebuild and deploy backend: `docker compose build backend && docker compose up -d backend`

**Gates:**
- `GET /api/deals?status=active` returns 0 deals with `stage='archived'`
- `GET /api/deals?status=archived` returns exactly the archived deals
- DB query: `SELECT COUNT(*) FROM zakops.deals WHERE stage = 'archived' AND status != 'archived'` returns 0
- Archive a test deal → verify `status='archived'` in DB
- Restore test deal → verify `status='active'` in DB

**Evidence required:** Before/after API responses, DB query results, archive/restore test transcript

**Risks/Rollback:** If any code assumes `status='active'` for archived deals, it may break. Rollback: `UPDATE zakops.deals SET status = 'active' WHERE stage = 'archived'` + revert code changes.

---

### Mission 3: DEAL-PIPELINE-ALIGN — Fix Pipeline Display

**Scope:** DI-ISSUE-003, DI-ISSUE-002 (partial)

**Steps:**
1. Modify `/hq` to use `GET /api/pipeline/summary` for stage counts instead of client-side computation
2. Update header count to exclude archived/junk OR add separate display section
3. Add `total_count` to `/api/deals` response
4. Verify `total_active_deals` definition matches displayed stages

**Gates:**
- /hq header count == sum of visible pipeline cards
- `total_count` field present in `/api/deals` response
- No client-side stage counting in `/hq` (verified by code review)

**Evidence required:** Before/after /hq screenshots, API response with `total_count`, code diff

**Risks/Rollback:** UI-only changes. Rollback: revert frontend code, redeploy dashboard.

---

### Mission 4: DEAL-FILTER-FIX — Fix Active Filter + Zod Resilience

**Scope:** DI-ISSUE-004, DI-ISSUE-005

**Steps:**
1. Add `'archived'` to deals page filter dropdown
2. Update backend: `active` filter should mean `stage != 'archived' AND stage != 'junk'` (or rely on fixed `status`)
3. Replace `Promise.all` with `Promise.allSettled` in `/hq`
4. Add individual try/catch to `getQuarantineQueue` and `getKineticActions`
5. Fix `/api/agent/activity` to return object (not array) or update `AgentActivityResponseSchema` to handle both

**Gates:**
- Deals page: "Active" filter excludes archived deals
- Deals page: "Archived" filter shows only archived deals
- /hq renders with pipeline data even when quarantine API returns 500
- No Zod errors in browser console on /hq
- `/api/agent/activity` response matches `AgentActivityResponseSchema`

**Evidence required:** Filter test screenshots, /hq with simulated API failure, browser console clean

**Risks/Rollback:** Frontend + backend changes. Rollback: revert code, redeploy both.

---

### Mission 5: DEAL-CLEANUP — Latent Bug Cleanup

**Scope:** DI-ISSUE-008, DI-ISSUE-009

**Steps:**
1. Resolve `audit_trail` (add column or remove references — per operator decision)
2. Fix or remove `/api/actions/kinetic` endpoint
3. Add API health suite test covering all documented endpoints

**Gates:**
- No `UndefinedColumn` errors possible from `main.py:1103, 1142, 1263` code paths
- `/api/actions/kinetic` returns non-500 (either valid response or 404 if removed)
- All documented API endpoints return non-500 in health suite

**Evidence required:** Code diff, endpoint test results

**Risks/Rollback:** Low risk. Code-only changes. Rollback: revert.

---

### Recommended Mission Execution Order

```
Phase 0: Mission 1 (DEAL-INFRA-UNIFY)     ← Eliminates split-brain noise
Phase 1: Mission 2 (DEAL-LIFECYCLE-FIX)    ← Fixes root cause
Phase 2: Mission 3 (DEAL-PIPELINE-ALIGN)   ← Fixes display after data is correct
Phase 3: Mission 4 (DEAL-FILTER-FIX)       ← Fixes UX + resilience
Phase 4: Mission 5 (DEAL-CLEANUP)          ← Latent bug cleanup
```

**Total estimated scope:** 5 missions, sequential dependency chain. Mission 1 is independent. Missions 2-4 should be done in order. Mission 5 is independent.

---

## 5) Evidence Index

### Evidence Directory A: CC3 Forensics
**Base path:** `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-001/evidence/00-forensics/`

| File | Contents |
|------|----------|
| `db-total-count.txt` | Total deal count: 49 |
| `db-count-by-status.txt` | Count by status (all `'active'`) |
| `db-count-by-stage.txt` | Count by stage (9 stages) |
| `db-status-x-stage.txt` | Cross-tabulation: status x stage x deleted |
| `db-distinct-statuses.txt` | Distinct status values: `['active']` |
| `db-distinct-stages.txt` | Distinct stage values |
| `db-deals-schema.txt` | Full `zakops.deals` table DDL |
| `db-null-status-deals.txt` | NULL status check (none found) |
| `db-recent-deals.txt` | 10 most recent deals with timestamps |
| `db-soft-delete-columns.txt` | Deletion-related columns |
| `db-deals-constraints.txt` | CHECK constraints on deals table |
| `db-deleted-flag.txt` | Count by deleted flag (37 false, 12 true) |
| `db-archived-stage-deals.txt` | 6 archived-stage deals detail |
| `db-deleted-true-deals.txt` | 12 soft-deleted deals detail |
| `db-full-breakdown.txt` | Complete deleted x stage breakdown |
| `api-deals-unfiltered.txt` | `GET /api/deals` → 37 deals |
| `api-deals-active-filter.txt` | `GET /api/deals?status=active` → 37 deals |
| `api-deals-archived-filter.txt` | `GET /api/deals?status=archived` → 0 deals |
| `api-pipeline-summary.txt` | `GET /api/pipeline/summary` → stage counts |
| `api-stats-endpoints.txt` | Endpoint availability (404s, 500s) |

### Evidence Directory B: Codex PASS 1
**Base path:** `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/`

| File | Contents |
|------|----------|
| `backend-env-db.txt` | Backend runtime `DATABASE_URL` (postgres:5432) |
| `db-total-count-now.txt` | DB 5435 total: 51 |
| `api-deals-stage-counts.txt` | API stage count breakdown |
| `backend-pipeline-summary.txt` | Backend pipeline summary |
| `backend-main-deals-list.txt` | Backend list endpoint code |
| `backend-main-archive-handlers.txt` | Backend archive handler code |
| `dashboard-hq-page.txt` | HQ page code excerpt |
| `dashboard-deals-page-filter.txt` | Deals page filter code |
| `dashboard-lib-api.txt` | API client library code |
| `api-agent-activity.txt` | `/api/agent/activity` response (returns `[]`) |
| `db-count-by-status-now.txt` | DB status counts (all active) |
| `db-count-by-stage-now.txt` | DB stage counts (archived: 4 on 5435) |

### Key Code Locations

| File | Lines | Contents |
|------|-------|----------|
| `zakops-backend/src/api/orchestration/main.py` | 466-513 | Deals listing endpoint (filters) |
| `zakops-backend/src/api/orchestration/main.py` | 565-621 | Deal creation endpoint |
| `zakops-backend/src/api/orchestration/main.py` | 867-907 | Archive endpoint (**root cause**) |
| `zakops-backend/src/api/orchestration/main.py` | 1103, 1142, 1263 | `audit_trail` references (latent bug) |
| `zakops-agent-api/apps/dashboard/src/app/hq/page.tsx` | 18-26 | `PIPELINE_STAGES` hardcoded array |
| `zakops-agent-api/apps/dashboard/src/app/hq/page.tsx` | 38-46 | `Promise.all` (fragile fetch pattern) |
| `zakops-agent-api/apps/dashboard/src/app/hq/page.tsx` | 62-66 | Client-side stage counting |
| `zakops-agent-api/apps/dashboard/src/app/hq/page.tsx` | 72 | Header count (`deals.length`) |
| `zakops-agent-api/apps/dashboard/src/app/deals/page.tsx` | 66 | Status filter values |
| `zakops-agent-api/apps/dashboard/src/app/deals/page.tsx` | 94 | Default filter (`'active'`) |
| `zakops-agent-api/apps/dashboard/src/lib/api.ts` | 397-404 | `apiFetch` throws on non-200 |
| `zakops-agent-api/apps/dashboard/src/lib/api.ts` | 758-778 | `getQuarantineQueue` (no try/catch) |
| `zakops-agent-api/apps/dashboard/src/lib/api.ts` | 1926-1948 | `AgentActivityResponseSchema` |
| `zakops-agent-api/apps/dashboard/src/lib/api.ts` | 1941-1956 | `getAgentActivity` (has try/catch) |
| `zakops-backend/migrations/023_stage_check_constraint.sql` | — | `v_pipeline_summary` view definition |

### Verification Commands (For Future Missions)

```bash
# Confirm split-brain status
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep postgres

# Count deals on canonical DB
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT COUNT(*) FROM zakops.deals;"

# Count by stage (canonical DB)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT stage, COUNT(*) FROM zakops.deals WHERE deleted = false GROUP BY stage ORDER BY stage;"

# Verify archive endpoint behavior
curl -s 'http://localhost:8091/api/deals?status=active' | python3 -c "
import sys, json
deals = json.loads(sys.stdin.read())
archived = [d for d in (deals if isinstance(deals, list) else deals.get('deals', [])) if d.get('stage') == 'archived']
print(f'Active filter returns {len(deals if isinstance(deals, list) else deals.get(\"deals\", []))} deals, {len(archived)} are archived-stage')
"

# Test agent activity schema
curl -s http://localhost:3003/api/agent/activity | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Type: {type(d).__name__}', f'Keys: {list(d.keys())}' if isinstance(d, dict) else f'Length: {len(d)}')
"

# Test quarantine endpoint
curl -s -o /dev/null -w '%{http_code}' http://localhost:8091/api/actions/quarantine
```

---

## Appendix: Full Innovation Ideas Index

All unique ideas across all agents, deduplicated. Referenced by issue and source.

| ID | Idea | Source | Applies To |
|----|------|--------|------------|
| I-01 | Lifecycle State ENUM column (`active`/`archived`/`deleted`) | CC3 | DI-ISSUE-001 |
| I-02 | Soft-Delete with `deleted_at` TIMESTAMP tombstone | CC3 | DI-ISSUE-001 |
| I-03 | Event-Sourced Deal Lifecycle | CC3 | DI-ISSUE-001 |
| I-04 | DB Trigger auto-sets `status` on `stage` change | CC1 | DI-ISSUE-001 |
| I-05 | Separate `archived_deals` table | Codex | DI-ISSUE-001 |
| I-06 | State Machine via Python `transitions` library | CC1 | DI-ISSUE-001 |
| I-07 | Computed Column `is_active` (GENERATED ALWAYS AS STORED) | CC1-P2 | DI-ISSUE-001 |
| I-08 | Database-Level Archive Partitioning | CC3 | DI-ISSUE-001 |
| I-09 | Materialized View for Stats (refreshed on write) | CC1 | DI-ISSUE-002 |
| I-10 | Count Ledger Service (trigger/outbox) | Codex | DI-ISSUE-002 |
| I-11 | DB Identity Tagging (meta table + API header) | Codex | DI-ISSUE-002, 006 |
| I-12 | API Returns `total_count` with paginated list | Codex | DI-ISSUE-002, 007 |
| I-13 | CQRS with Read Models | CC3 | DI-ISSUE-002 |
| I-14 | Canonical Stage Configuration Object (shared config) | CC3 + Codex | DI-ISSUE-003 |
| I-15 | Backend-Driven Pipeline Definition (`/api/pipeline/config`) | CC3 | DI-ISSUE-003 |
| I-16 | Pipeline Summary API as Single Source | Codex | DI-ISSUE-003 |
| I-17 | Faceted Search with Counts | CC3 | DI-ISSUE-004 |
| I-18 | Smart Default Filter with URL State | CC3 | DI-ISSUE-004 |
| I-19 | Filter Composition (complex filter params) | CC1 | DI-ISSUE-004 |
| I-20 | Dedicated `visibility_state` Filter Enum | Codex | DI-ISSUE-004 |
| I-21 | Materialized `active_deals` View | Codex | DI-ISSUE-004 |
| I-22 | React Suspense Boundaries per Widget | CC3 | DI-ISSUE-005 |
| I-23 | SWR / TanStack Query for independent data fetching | CC3 | DI-ISSUE-005 |
| I-24 | Unified "Empty State" Object for agent activity | Codex | DI-ISSUE-005 |
| I-25 | Schema Versioning for API evolution | Codex | DI-ISSUE-005 |
| I-26 | Contract Tests in CI (Zod vs actual API) | CC1 | DI-ISSUE-005 |
| I-27 | Service Discovery / Env Injection (Doppler/Vault) | CC1 | DI-ISSUE-006 |
| I-28 | Health Endpoint with DB Identity | Codex | DI-ISSUE-006 |
| I-29 | Optimistic UI Updates | CC3 | DI-ISSUE-007 |
| I-30 | Event-Driven Cache Invalidation (pg_notify/Redis) | CC3 | DI-ISSUE-007 |
| I-31 | Event-Driven Read Model | Codex | DI-ISSUE-007 |
| I-32 | Schema Diff Gate (CI: code refs vs live schema) | Codex-P2 | DI-ISSUE-008 |
| I-33 | Endpoint Contract Inventory (route coverage check) | Codex-P2 | DI-ISSUE-009 |
| I-34 | Deprecation Header Pattern (RFC 8594) | CC3 | DI-ISSUE-009 |

---

**END OF PASS 3 — FINAL CONSOLIDATION**

**Status:** COMPLETE — 9 deduped issues, 4 operator decisions, 5 fix missions, 34 innovation ideas, full evidence index.
**No fixes implemented. Investigation and planning only.**

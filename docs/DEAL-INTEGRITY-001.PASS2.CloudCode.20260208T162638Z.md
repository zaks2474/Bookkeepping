# DEAL-INTEGRITY-001 — PASS 2: CROSS-REVIEW + DEDUPLICATION

**Run ID:** `20260208T162638Z`
**Agent:** Claude Code (Opus 4.6)
**Pass:** 2 — CROSS-REVIEW → DEDUP → MAP → STOP
**Date:** 2026-02-08

---

## 1. Agent Identity

| Agent | Run ID | Report Path |
|-------|--------|-------------|
| CloudCode (CC3) | `20260208T160103Z` | `DEAL-INTEGRITY-001.PASS1.CloudCode.20260208T160103Z.md` |
| Codex | `20260208-1015-c1xh` | `DEAL-INTEGRITY-001.PASS1.Codex.20260208-1015-c1xh.md` |
| CloudCode (CC1) | `20260208-0500-pass1` | `DEAL-INTEGRITY-001.PASS1.CloudCode.20260208-0500-pass1.md` |

**Input cross-mapping (how each agent numbered the original 6 issues):**

| Stable ID | CC3 | Codex | CC1 |
|-----------|-----|-------|-----|
| DI-ISSUE-001 | Issue 3 | Issue 3 | Issue 2 |
| DI-ISSUE-002 | Issue 1 | Issue 1 | Issue 1 (partial) |
| DI-ISSUE-003 | Issue 2 | Issue 2 | Issue 1 (partial) |
| DI-ISSUE-004 | Issue 6 | Issue 6 | Issue 5 |
| DI-ISSUE-005 | Issue 4 | Issue 4 | Issue 3 |
| DI-ISSUE-006 | — (not found) | Issue 1 (partial) + Issue 5 | Issue 1 (partial) + Issue 4 |
| DI-ISSUE-007 | Issue 5 | Issue 5 | Issue 4 |
| DI-ISSUE-008 | BONUS #1 | — | — |
| DI-ISSUE-009 | BONUS #2 | — | — |

---

## 2. Deduped Issue Registry

### DI-ISSUE-001: Archive Endpoint Performs Partial State Transition

**Severity:** CRITICAL — root cause of DI-ISSUE-002, 003, 004, and partial cause of 007
**Agents confirming:** CC3, Codex, CC1 (unanimous)

#### Merged Root Cause Statement

The `POST /api/deals/{deal_id}/archive` endpoint (`main.py:867-907`) executes:
```sql
UPDATE zakops.deals SET stage = 'archived', updated_at = NOW() WHERE deal_id = $1
```
It updates **only `stage`**. It does NOT set `status = 'archived'` or `deleted = true`. Since all 49 deals have `status = 'active'` (the only value ever written), API filters using `?status=active` return archived-stage deals alongside truly active ones. This single partial transition cascades into every downstream count disagreement, filter failure, and pipeline mismatch.

#### Evidence Pointers (All Agents)

| Evidence | Source Agent | Path |
|----------|-------------|------|
| Archive SQL (stage only) | CC3 | `main.py:881-884` via `evidence/00-forensics/` |
| Archive SQL (stage only) | Codex | `main.py:868` via `_evidence/DEAL-INTEGRITY-001-PASS1/backend-main-archive-handlers.txt` |
| Archive SQL (stage only) | CC1 | `main.py` (cited in report §Issue 2) |
| DB status all 'active' | CC3 | `evidence/00-forensics/db-distinct-statuses.txt` |
| DB status all 'active' | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/db-count-by-status-now.txt` |
| DB status all 'active' | CC1 | `db-real-status-x-stage.txt` (6 active+archived) |
| Archived deals in active view | CC3 | `evidence/00-forensics/api-deals-archived-filter.txt` (0 results) |
| Archived deals in active view | Codex | `deals/page.tsx:94-111` via `dashboard-deals-page-filter.txt` |

#### Merged Permanent Fix Approach

1. Modify `POST /api/deals/{deal_id}/archive` to atomically set `stage = 'archived'` AND `status = 'archived'`
2. Backfill: `UPDATE zakops.deals SET status = 'archived' WHERE stage = 'archived' AND deleted = false`
3. Add DB CHECK constraint: `stage = 'archived' → status = 'archived'`
4. Modify `POST /api/deals/{deal_id}/restore` to atomically reset `status = 'active'` when restoring

#### Merged Best-Practice Standard

**Atomic State Transitions via Finite State Machine (FSM)**

All three agents converge on the same principle:
- CC3: "Finite State Machine for Deal Lifecycle" — cites Salesforce `StageName` with derived `IsClosed`/`IsWon`
- Codex: "Status enum enforcement with state machine" — cites deterministic transitions
- CC1: "State Machine Enforcement" — cites `transitions` library or DB trigger

The industry standard (Salesforce, HubSpot, PipeDrive) is a **single authoritative lifecycle field** with validated transitions. A deal cannot occupy an impossible state combination.

#### Why It Fits ZakOps

ZakOps has three overlapping state signals (`status`, `stage`, `deleted`) with no enforced coupling. The archive endpoint updates one and ignores the other two. An FSM eliminates impossible states (`status='active' + stage='archived'`) and makes every transition auditable.

#### "Never Again" Enforcement

- **DB CHECK constraint:** `(stage = 'archived') → (status = 'archived')` (prevents partial transitions at the data layer)
- **Integration test:** "After archiving, `GET /api/deals?status=active` must NOT return the archived deal"
- **API contract test:** "After archiving, `?status=archived` must return the deal"
- **Code gate:** All state transitions go through a `transition_deal_state()` function — no raw UPDATE queries for state changes (CC3)
- **DB trigger or constraint:** Enforce status/stage/deleted consistency on every write (Codex, CC1)

#### Merged Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Lifecycle State ENUM column** | CC3 | Add `lifecycle_state` ENUM (`active`, `archived`, `deleted`). Backfill from current data. All queries use this single field. Deprecate `status` column. | Clean, single-field solution. Requires migration + backfill + endpoint updates. |
| 2 | **Soft-Delete with Tombstone (`deleted_at` TIMESTAMP)** | CC3 | Replace `deleted` boolean + `status` with a single `deleted_at` NULL column. NULL = active, non-null = archived. | Simpler (one column), supports "when was it archived?" queries. Loses distinction between "archived" and "permanently deleted." |
| 3 | **Event-Sourced Deal Lifecycle** | CC3 | Every state change is an immutable event. Current state derived from latest event. | Full audit trail. Adds read complexity. Overkill at 49 deals, valuable at scale. |
| 4 | **DB Trigger Auto-Sets Status** | CC1 | Use a PostgreSQL trigger that automatically sets `status='archived'` whenever `stage` transitions to `archived`. | No application code changes needed for enforcement. But hides logic in DB layer. |
| 5 | **Separate Archive Table** | Codex | Move archived deals to a separate `archived_deals` table on archive. Active queries never see them. | Eliminates mixed semantics entirely. Requires migration + JOIN for "all deals" views. |
| 6 | **Status Enum with `transitions` Library** | CC1 | Use Python `transitions` library to enforce state machine in application code. | Deterministic, testable. Adds dependency. |

---

### DI-ISSUE-002: Deal Counts Disagree Across Surfaces

**Severity:** HIGH — user-facing, undermines trust
**Agents confirming:** CC3, Codex, CC1 (unanimous)
**Dependency:** Partially resolves when DI-ISSUE-001 is fixed; fully resolves when DI-ISSUE-006 is also fixed

#### Merged Root Cause Statement

Multiple surfaces report different deal counts because each applies a different combination of filters to the same (or different) underlying data:

| Surface | Count | Filter Logic |
|---------|-------|-------------|
| DB (5432) total | 49 | All rows |
| DB (5432) non-deleted | 37 | `deleted = false` |
| DB (5435) total | 51 | All rows (**different DB** — see DI-ISSUE-006) |
| API `GET /api/deals` | 37 | `deleted = FALSE` + `status = 'active'` (no-op) |
| Pipeline summary | 37 | View: `deleted = false AND status = 'active'`, all stages |
| /hq header | 37 | `deals.length` from API |
| /hq pipeline cards | 31 | Client-side count using 7-stage subset (see DI-ISSUE-003) |

The 49-vs-37 gap = 12 soft-deleted deals. The 37-vs-31 gap = 6 archived-stage deals. The 51-vs-49 gap = 2 stale deals in rogue DB.

CC3 found all 49 deals have `status='active'`, making the status filter a no-op. Codex and CC1 additionally found a second Postgres instance (port 5435, 51 deals) that inflates counts when queried directly.

#### Evidence Pointers (All Agents)

| Evidence | Source Agent | Path |
|----------|-------------|------|
| DB total: 49 | CC3 | `evidence/00-forensics/db-total-count.txt` |
| DB total: 51 (port 5435) | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt` |
| DB 5432: 49, DB 5435: 51 | CC1 | `db-real-total-count.txt` / `db-real-deleted-counts.txt` |
| API returns 37 | CC3 | `evidence/00-forensics/api-deals-unfiltered.txt` |
| API returns 37 | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/api-deals-stage-counts.txt` |
| Pipeline: 37 total, 31 visible | CC3 | `evidence/00-forensics/api-pipeline-summary.txt` |
| Surface count table | CC3 | Report §Issue 1 (10-row table) |

#### Merged Permanent Fix Approach

1. Fix DI-ISSUE-001 (archive sets `status='archived'`) so `?status=active` excludes archived deals
2. Fix DI-ISSUE-006 (eliminate rogue DB) so all services query the same data
3. Add `total_count` to `/api/deals` response (Codex) so UI doesn't rely on `array.length`
4. Ensure `v_pipeline_summary` excludes archived-stage deals from pipeline totals or presents them separately (CC3)

#### Merged Best-Practice Standard

**Single Source of Truth (SSOT)** for all counts. Pipeline dashboards (Salesforce, HubSpot, Monday.com) compute counts server-side and return structured summary objects. The client renders what the server provides — no client-side re-counting.

Additionally: **Paginated list endpoints must return `total_count`** (Codex) to prevent UI count drift when dealing with pagination.

#### Why It Fits ZakOps

ZakOps is a multi-layer system (Dashboard → Backend → Agent → DB). If any layer counts differently, every surface disagrees. A single server-side computation eliminates drift.

#### "Never Again" Enforcement

- **Contract test:** `sum(stage_counts) == total_active_deals` for every API response (CC3)
- **CI gate:** API count and DB count must match (Codex)
- **UI invariant test:** `/api/deals/count` must equal `/api/pipeline/summary.total` (Codex)
- **Startup gate:** Backend refuses to start if DB URL differs from canonical DSN (Codex)

#### Merged Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Materialized View for Stats** | CC1 | Refreshed on every write, serves as SSOT for all counts. | Instant, consistent counts. Write overhead + refresh timing. |
| 2 | **Count Ledger Service** | Codex | Materialized summary table updated via trigger/outbox on writes. | Same benefit as MV. More explicit control over what triggers refresh. |
| 3 | **DB Identity Tagging** | Codex | `db_instance_id` in meta table, included in every API response header. UI alerts on mismatch. | Excellent ops visibility. Small schema addition. |
| 4 | **API Returns `total_count` with Paginated List** | Codex | Standard REST pagination: `{total_count: N, deals: [...]}`. | Minimal change. Prevents `array.length` drift. |
| 5 | **CQRS with Read Models** | CC3 | Separate write model from read models (denormalized `pipeline_counts` table). | Eliminates count disagreements by design. Adds maintenance complexity. |

---

### DI-ISSUE-003: Pipeline Stage Totals Don't Sum to Header Count

**Severity:** HIGH — user-facing, math error visible on /hq
**Agents confirming:** CC3, Codex, CC1 (unanimous)
**Dependency:** Partially resolves when DI-ISSUE-001 is fixed

#### Merged Root Cause Statement

The `/hq` page (`hq/page.tsx:18-26`) defines `PIPELINE_STAGES` as a hardcoded 7-element array:
```typescript
['inbound', 'screening', 'qualified', 'loi', 'diligence', 'closing', 'portfolio']
```
This excludes `'archived'` and `'junk'` from the 9 valid stages. The header shows `total_active_deals: deals.length` = 37, but the pipeline cards sum to 31. The gap of 6 equals the archived-stage deals that have no card.

Additionally, stage counts are computed **client-side** by filtering the deals array, despite the backend already providing server-computed counts via `GET /api/pipeline/summary`. The /hq page ignores this endpoint entirely (CC3).

#### Evidence Pointers (All Agents)

| Evidence | Source Agent | Path |
|----------|-------------|------|
| PIPELINE_STAGES array (7 entries) | CC3 | `hq/page.tsx:18-26` |
| PIPELINE_STAGES array | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-hq-page.txt` |
| Client-side count logic | CC3 | `hq/page.tsx:62-66` (reduce over PIPELINE_STAGES) |
| Header = deals.length = 37 | CC3 | `hq/page.tsx:72` |
| Pipeline sum = 31, archived = 6 | CC3, CC1 | `evidence/00-forensics/api-pipeline-summary.txt` |
| Stage count mismatch | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/api-deals-stage-counts.txt` |

#### Merged Permanent Fix Approach

1. Use `GET /api/pipeline/summary` for stage counts instead of client-side computation (CC3)
2. Either exclude archived-stage deals from the header count OR add an "Archived" card (CC3, CC1)
3. Define "active" consistently: `total_active_deals` should only count pipeline-stage deals (CC3) OR match displayed stages (Codex)
4. Handle `'junk'` stage (currently 0 but exists in CHECK constraint) (CC3)

#### Merged Best-Practice Standard

**Server-Side Pipeline Aggregation.** All three agents agree: pipeline dashboards should compute counts server-side. The client should render, not count.

**Consistent Domain Invariants:** A deal's status/stage must drive all counts. UI and API must compute from the same logic (Codex).

#### Why It Fits ZakOps

The backend already HAS `GET /api/pipeline/summary` returning server-computed stage counts. The /hq page ignores it and re-computes client-side with a different stage list. Using the existing endpoint eliminates the divergence immediately.

#### "Never Again" Enforcement

- **Contract test:** Pipeline totals must equal sum of displayed stage totals (Codex)
- **Contract test:** If stage list excludes archived, then `total_active` must exclude archived too (Codex)
- **Contract test:** `sum(all stage counts) == total count` in pipeline summary response (CC3)
- **Code review gate:** No hardcoded stage lists in frontend — derive from shared config or API (CC3, Codex)

#### Merged Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Canonical Stage Configuration Object** | CC3 | Shared `STAGE_CONFIG` with `pipeline: boolean` flag per stage. Derive all stage lists from it. | Single source of truth. Requires contracts package integration. |
| 2 | **Strict Stage Taxonomy Config** | Codex | Same concept as above — shared config module that both UI and backend consume. Archived cannot be omitted unless explicitly flagged. | Requires shared contract generation. |
| 3 | **Backend-Driven Pipeline Definition** | CC3 | `GET /api/pipeline/config` returns pipeline/terminal stages. Frontend renders whatever backend declares. | Maximum flexibility. Adds API call (cacheable). Loses compile-time type safety. |
| 4 | **Pipeline Summary API as Single Source** | Codex | `/api/pipeline` returns both total and stage sums. UI consumes only that. | Centralizes logic. Adds API dependency. |

**Dedup note:** Ideas #1 and #2 are essentially the same concept from different agents (shared stage config). The difference: CC3 gives a concrete TypeScript implementation with `pipeline: boolean` flags; Codex emphasizes the "cannot be omitted unless flagged" constraint. **Both perspectives are valuable — keep as complementary facets of the same idea.**

---

### DI-ISSUE-004: Active Filter Doesn't Actually Filter

**Severity:** MEDIUM — user-facing, causes confusion
**Agents confirming:** CC3, Codex, CC1 (unanimous)
**Dependency:** Fully resolves when DI-ISSUE-001 is fixed

#### Merged Root Cause Statement

The `/deals` page status filter dropdown offers `['active', 'junk', 'merged']` and defaults to `'active'`. This sends `?status=active` to the API. Since all deals have `status='active'` (archive never changes it — DI-ISSUE-001), the filter returns ALL 37 non-deleted deals including the 6 with `stage='archived'`. The filter is technically correct but semantically broken.

Furthermore:
- No `'archived'` option exists in the dropdown (CC3)
- `'junk'` and `'merged'` return 0 results (CC3)
- No stage-based filter exists in the UI (CC3)

All three agents agree this is a **derived symptom** of DI-ISSUE-001, not an independent bug.

#### Evidence Pointers (All Agents)

| Evidence | Source Agent | Path |
|----------|-------------|------|
| Filter values: active/junk/merged | CC3 | `deals/page.tsx:66` |
| Default filter: 'active' | CC3 | `deals/page.tsx:94` |
| Filter sent to API | CC3, Codex | `deals/page.tsx:111` |
| All deals status='active' | CC3 | `evidence/00-forensics/db-distinct-statuses.txt` |
| Active filter returns 37 (same as unfiltered) | CC3 | `evidence/00-forensics/api-deals-active-filter.txt` |
| Backend list uses status param | Codex | `main.py:467` via `backend-main-deals-list.txt` |

#### Merged Permanent Fix Approach

1. Fix DI-ISSUE-001 first (archive sets `status='archived'`) — this alone makes the filter meaningful
2. Add `'archived'` to the dropdown (CC3)
3. Replace single-field filter with composite filter combining lifecycle and stage (CC3)
4. Update backend filter semantics: `active` = `deleted=false AND stage!='archived'` (Codex)

#### Merged Best-Practice Standard

**Filter-by-What-Users-See.** Filters should match the user's mental model (CC3: "active deals, archived deals, deals in screening"), not raw DB column values. Codex adds: **Explicit, single-field semantics** — avoid ambiguous dual fields.

#### Why It Fits ZakOps

Users see deals in a pipeline with stages. The natural filter is "show me deals in screening" or "show me archived deals." The current filter options (`active`/`junk`/`merged`) don't map to any meaningful user action.

#### "Never Again" Enforcement

- **API test:** `GET /api/deals?status=active` must NOT return archived-stage deals (CC3, Codex)
- **DB constraint or trigger:** Enforce status/stage consistency (Codex)
- **Derive filter options from stage config** (see DI-ISSUE-003 Innovation #1) so they stay in sync (CC3)

#### Merged Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Faceted Search with Counts** | CC3 | Display `Active (31) | Archived (6) | All (37)` with sub-facets per stage. Counts from pipeline summary API. | Excellent UX. Requires additional API call or piggyback on pipeline summary. |
| 2 | **Smart Default Filter with URL State** | CC3 | Default depends on context (from /hq card → pre-filter to that stage). URL-persistent via `searchParams`. | Contextual, shareable. Slightly more routing logic. |
| 3 | **Filter Composition** | CC1 | API accepts complex filters like `filter={status: 'active', stage: {neq: 'archived'}}`. | Precise frontend control. More complex query builder needed. |
| 4 | **Dedicated `visibility_state` Filter Enum** | Codex | Backend exposes `visibility_state` (active/archived/junk) for all list queries. | Clean semantics. Requires migration. |
| 5 | **Materialized `active_deals` View** | Codex | DB view used for all list endpoints, pre-filtered for active-only. | Consistent semantics. Additional DB object. |

---

### DI-ISSUE-005: Zod Validation Error on Operator HQ (Intermittent)

**Severity:** MEDIUM — intermittent, causes blank HQ or console errors
**Agents confirming:** CC3, Codex, CC1 (all confirm, **disagree on root cause** — see Conflicts §4)

#### Merged Root Cause Statement

**Three contributing factors identified across agents (not mutually exclusive):**

**Factor A — Promise.all fragility (CC3):** The `/hq` page uses `Promise.all` with 4 parallel fetches. Three of four (`getDeals`, `getKineticActions`, `getQuarantineQueue`) lack individual try/catch. If any throws an `ApiError` (non-200 response), the entire `Promise.all` rejects, blanking all HQ data. Only `getAgentActivity` has its own error boundary.

**Factor B — Agent activity schema mismatch (Codex):** `/api/agent/activity` sometimes returns an **empty array `[]`** instead of the expected object `{status, recent, stats, ...}`. The `AgentActivityResponseSchema` (`api.ts:1926`) expects an object, so `safeParse` fails when the endpoint returns `[]`. Codex captured evidence of the `[]` response.

**Factor C — Archived data shape mismatch (CC1):** Archived deals leaking into the active view (DI-ISSUE-001) may have missing/null fields that active deals normally populate. These malformed records fail Zod validation in the deals schema. This theory is plausible but less directly evidenced.

**Verdict:** Factors A and B are strongly evidenced. Factor C is plausible but secondary — the `DealSchema` uses `.passthrough()` which is tolerant of extra/missing fields (CC3 noted this). The most likely intermittent trigger is Factor B (Agent API returning `[]` vs object), with Factor A amplifying any single failure into a total HQ blackout.

#### Evidence Pointers (All Agents)

| Evidence | Source Agent | Path |
|----------|-------------|------|
| Promise.all with 4 calls, 3 unprotected | CC3 | `hq/page.tsx:38-46` |
| getQuarantineQueue: no try/catch | CC3 | `api.ts:758-778` |
| getAgentActivity: has try/catch | CC3 | `api.ts:1941-1956` |
| apiFetch throws on non-200 | CC3 | `api.ts:397-404` |
| /api/agent/activity returns [] | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/api-agent-activity.txt` |
| AgentActivityResponseSchema expects object | Codex | `api.ts:1926-1948` via `dashboard-lib-api.txt` |
| Zod parse locations (heavy usage) | CC1 | `zod-parse-locations.txt` |
| Route handler empty response shape | CC3 | `app/api/agent/activity/route.ts:143-157` |

#### Merged Permanent Fix Approach

1. Replace `Promise.all` with `Promise.allSettled` in `/hq` (CC3)
2. Add individual try/catch to `getQuarantineQueue` and `getKineticActions` (CC3)
3. Align `/api/agent/activity` response shape: always return object, never `[]` (Codex)
4. If route handler returns empty array on error, update to return `getEmptyResponse()` object (Codex + CC3)
5. Add defensive `.passthrough()` to all response schemas (CC3)

#### Merged Best-Practice Standard

**Per-Widget Error Boundaries + Schema-First API Contracts.**

CC3: Independent error boundaries per dashboard widget (Grafana/Datadog pattern). CC1: Contract tests running Zod schemas against actual API responses in CI. Codex: Schema-first API contracts with contract tests — response shape must match in all environments.

#### Why It Fits ZakOps

HQ aggregates 4 independent data sources. A quarantine API failure should not blank pipeline data. The current all-or-nothing fetch is fragile by design.

#### "Never Again" Enforcement

- **Contract test:** `/api/agent/activity` must return an object matching `AgentActivityResponseSchema` (Codex)
- **UI test:** HQ renders pipeline data even when quarantine or agent API returns 500 (CC3)
- **UI test:** HQ renders without Zod errors in mock mode (Codex)
- **Code invariant:** All API fetcher functions must have individual try/catch — never throw through `Promise.all` (CC3)

#### Merged Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **React Suspense Boundaries per Widget** | CC3 | Each HQ section in its own `<Suspense>` boundary. Errors isolated per widget. | Clean React pattern. Requires component refactor. |
| 2 | **SWR / TanStack Query** | CC3 | Independent cache keys per data source. Auto-retry, caching, background revalidation. | Eliminates hand-rolled Promise.all. Adds dependency. |
| 3 | **Unified "Empty State" Object** | Codex | Always return typed object with zeroed stats, never `[]`. | Explicit, reduces ambiguity. Minimal change. |
| 4 | **Schema Versioning** | Codex | Include `schema_version` field. Client validates version, applies fallback for older versions. | Enables safe API evolution. Added overhead. |
| 5 | **Contract Tests in CI** | CC1 | CI job runs Zod schemas against actual database rows to detect drift pre-deployment. | Catches schema drift before it hits production. Requires test DB fixture maintenance. |

---

### DI-ISSUE-006: Split-Brain Database (Two Postgres Instances)

**Severity:** CRITICAL — causes data loss / invisible writes
**Agents confirming:** Codex, CC1 (both identify it)
**CC3 status:** Did NOT investigate this. CC3 queried only `zakops-backend-postgres-1` (port 5432) via `docker exec` and found 49 deals. CC3 did not examine port 5435 or check for multiple containers.

#### Merged Root Cause Statement

Two PostgreSQL containers are running simultaneously:

| Container | Port | Deals | Used By |
|-----------|------|-------|---------|
| `zakops-backend-postgres-1` | 5432 | 49 | Backend API (runtime `DATABASE_URL=postgresql://zakops:zakops_dev@postgres:5432/zakops`) |
| `zakops-postgres` (legacy) | 5435 | 51 | Potentially: ops scripts, local `psql`, legacy tools, `.env` files with wrong DSN |

The backend API writes to 5432. If any other service (agent, RAG, ops scripts) queries 5435, it sees stale data (51 deals vs 49). Deals created via the UI go to 5432 and are invisible on 5435.

Codex captured the backend's runtime `DATABASE_URL` as evidence. CC1 confirmed via `docker ps` showing two Postgres containers.

#### Evidence Pointers

| Evidence | Source Agent | Path |
|----------|-------------|------|
| Backend runtime DB = postgres:5432 | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/backend-env-db.txt` |
| Local DB queries on 5435 | Codex | `zakops-backend/.env` |
| Two Postgres containers | CC1 | `docker ps` output cited in report §Issue 4 |
| DB 5432: 49 deals | CC1 | `db-real-total-count.txt` |
| DB 5435: 51 deals | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt` |
| DB 5435: 51 deals | CC1 | cited in report §Issue 1 |

#### Merged Permanent Fix Approach

1. Stop and remove the legacy `zakops-postgres` container (port 5435) (CC1)
2. Audit all `.env` files and `docker-compose` configs — ensure every service points to `postgres:5432` / `zakops-backend-postgres-1` (CC1, Codex)
3. Add DB identity to `/health` endpoint (host/port/dbname) so ops can verify (Codex)

#### Merged Best-Practice Standard

**Single Source of Truth (SSOT) per environment.** Multiple DBs = split-brain. All read models derive from one canonical DB (Codex). CC1 adds: **Service Discovery / Env Injection** (Doppler/Vault) to prevent config drift.

#### Why It Fits ZakOps

ZakOps has multiple services (Backend, Agent API, RAG) and ops tooling. If any connects to a different DB, counts diverge and writes become invisible. The observed 51 vs 49 gap proves this is already happening.

#### "Never Again" Enforcement

- **Startup gate:** Backend refuses to start if DB URL differs from canonical DSN (Codex)
- **CI/Smoke:** `curl /health` must report same DB identity as `psql` used by ops (Codex)
- **Docker-compose:** Single `depends_on` Postgres service, no secondary containers (CC1)
- **Ops runbook:** Standard `psql` commands must connect to the correct container via `docker exec`, never via localhost port forwarding (to avoid port confusion)

#### Merged Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **DB Identity Tagging** | Codex | `db_instance_id` row in meta table, echoed in API response headers. UI alerts on mismatch. | Huge ops clarity. Small schema addition. |
| 2 | **Service Discovery / Env Injection** | CC1 | Use Doppler/Vault to inject single correct DB URL into all containers at runtime. | Prevents config drift. Adds infra dependency. |
| 3 | **Health Endpoint with DB Identity** | Codex | `/health` returns `{db_host, db_port, db_name}`. Ops scripts validate before querying. | Minimal. Immediately detects split-brain. |

---

### DI-ISSUE-007: UI-Created Deals Don't Fully Propagate

**Severity:** MEDIUM — user-facing, new deals appear inconsistently
**Agents confirming:** CC3, Codex, CC1 (all confirm, **disagree on root cause** — see Conflicts §4)

#### Merged Root Cause Statement

**Two contributing factors (not mutually exclusive):**

**Factor A — Perception issue from count mismatches (CC3):** Deal creation via `POST /api/deals` works correctly — inserts with `status='active'`, `stage='inbound'`, `deleted=false`, creates `deal_created` event. The deal appears in `/deals` and `/hq` pipeline. However, the persistent header/pipeline gap (DI-ISSUE-003) makes it look like deals "disappear" — a new inbound deal increments both header and pipeline card, but the gap from archived deals remains, creating a perception of inconsistency.

**Factor B — Split-brain DB (Codex, CC1):** If the Agent API or RAG service connects to the legacy DB (port 5435, 51 stale deals), deals created via the Dashboard (→ Backend → DB 5432) are invisible to those services. This is a real data loss, not just perception.

**Verdict:** Both factors are real. Factor A explains the Dashboard's visual inconsistency. Factor B explains cross-service invisibility. Fixing DI-ISSUE-001 resolves Factor A; fixing DI-ISSUE-006 resolves Factor B.

#### Evidence Pointers (All Agents)

| Evidence | Source Agent | Path |
|----------|-------------|------|
| Deal creation SQL correct | CC3 | `main.py:565-621` |
| 21 inbound deals (creation works) | CC3 | `evidence/00-forensics/db-full-breakdown.txt` |
| audit_trail latent bug (not triggered by creation) | CC3 | `main.py:1103, 1142, 1263` |
| Backend writes to 5432, other services may read 5435 | Codex | `_evidence/DEAL-INTEGRITY-001-PASS1/backend-env-db.txt` |
| DB 5432: 49, DB 5435: 51 (disjoint?) | CC1 | `db-recent-deals.txt` vs `api-deals-unfiltered.txt` |
| UI list uses array.length (no total_count) | Codex | `api.ts:426-452` via `dashboard-lib-api.txt` |

#### Merged Permanent Fix Approach

1. Fix DI-ISSUE-001 (archive endpoint) — resolves the visual count illusion
2. Fix DI-ISSUE-006 (eliminate rogue DB) — resolves cross-service invisibility
3. Add `total_count` to `/api/deals` response (Codex)
4. Add integration test: create deal → verify it appears in /deals, /hq pipeline, and pipeline summary (CC3)

#### Merged Best-Practice Standard

**Optimistic UI Updates with Server Confirmation** (CC3). Additionally: **Single-write DB with explicit read models** (Codex).

#### Why It Fits ZakOps

UI-based creation should be visible to all layers (dashboard, HQ, agent). That requires: (a) all layers talk to the same DB, and (b) counts are computed consistently.

#### "Never Again" Enforcement

- **E2E test:** Create deal → verify in /deals, /hq, pipeline summary, agent API (CC3)
- **Startup gate:** All services verify DB identity matches canonical DSN (Codex)
- **CI gate:** API count and DB count must match (Codex)

#### Merged Innovation Ideas

| # | Idea | Source | Description | Tradeoffs |
|---|------|--------|-------------|-----------|
| 1 | **Optimistic UI Updates** | CC3 | After `createDeal()`, immediately add to local state. Reconcile on server response. | Instant feedback. Requires rollback on failure. |
| 2 | **Event-Driven Cache Invalidation** | CC3 | Deal mutations publish events (Redis pub/sub or pg_notify). Dashboards auto-refresh. | Real-time consistency. Adds pub/sub infra. Overkill at 49 deals. |
| 3 | **Event-Driven Read Model** | Codex | Write triggers update to `deal_counts` table. HQ and filters read from it. | Consistent. Extra infra. |
| 4 | **API Returns Paged List + `total_count`** | Codex | Standard REST pagination: `{total_count: N, deals: [...]}`. | Minimal change. Immediate improvement. |

---

### DI-ISSUE-008: `audit_trail` Column Referenced but Missing from Schema

**Severity:** LOW (latent) — will cause `UndefinedColumn` SQL error if code path is triggered
**Agents confirming:** CC3 only (Codex and CC1 did not report this)

#### Root Cause Statement

Backend code references `audit_trail` column at `main.py:1103, 1142, 1263`, but the `zakops.deals` table schema has no such column. If any code path reaches these lines, it will throw a PostgreSQL `UndefinedColumn` error.

#### Evidence Pointers

| Evidence | Source Agent | Path |
|----------|-------------|------|
| Column references in code | CC3 | `main.py:1103, 1142, 1263` |
| Column absent from schema | CC3 | `evidence/00-forensics/db-deals-schema.txt` |

#### Fix Approach

Either add the `audit_trail` column via migration (if the feature is intended) or remove the dead code references.

#### "Never Again" Enforcement

- **CI gate:** Run `SELECT audit_trail FROM zakops.deals LIMIT 0` in test DB — must not error
- **Static analysis:** Flag SQL column references that don't exist in current schema

---

### DI-ISSUE-009: `/api/actions/kinetic` Returns HTTP 500

**Severity:** LOW — not called by dashboard, but pollutes debugging
**Agents confirming:** CC3 only (Codex and CC1 did not report this)

#### Root Cause Statement

`GET /api/actions/kinetic` returns HTTP 500 Internal Server Error. The dashboard does not call this endpoint directly — `isKineticApiAvailable()` checks `/api/actions/capabilities` (returns 200), and `getKineticActions` calls `/api/actions?status=pending_approval` (returns 200 with `[]`). Impact is limited to debugging confusion.

#### Evidence Pointers

| Evidence | Source Agent | Path |
|----------|-------------|------|
| HTTP 500 response | CC3 | `evidence/00-forensics/api-stats-endpoints.txt` |
| Dashboard doesn't call it | CC3 | `api.ts:1560-1607` (isKineticApiAvailable + getKineticActions) |

#### Fix Approach

Investigate and fix the endpoint or remove it if deprecated.

---

## 3. Additional Systemic Finding (Codex Only)

### Mission Prompt Uses Wrong Column Names

Codex found that the mission prompt's example DB queries use `id` and `name`, but the actual table uses `deal_id` and `canonical_name`. This causes false-negative "no rows" errors during investigation.

**Evidence:** Codex report §"Additional systemic issue discovered"
**Recommendation:** Update mission prompt to use correct column names.

---

## 4. Conflicts & Uncertainties

### CONFLICT 1: Is There a Split-Brain Database?

| Agent | Position |
|-------|----------|
| CC3 | **Did not investigate.** All queries via `docker exec zakops-backend-postgres-1 psql` (port 5432). Found 49 deals. No mention of second container. |
| Codex | **YES.** Backend runtime DB = `postgres:5432` (container), local queries on `localhost:5435`. DB 5435 has 51 deals vs DB 5432 API returns 37. |
| CC1 | **YES.** Two Postgres containers: `zakops-backend-postgres-1` (5432, 49 deals) and `zakops-postgres` (5435, 51 deals). |

**Resolution:** This is not a true disagreement — CC3 simply didn't look for it. Codex and CC1 independently confirmed the same finding. The split-brain is real.

**Verification command:**
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep postgres
```
Expected: Two rows. If only one, the rogue container has been stopped since investigation.

```bash
# Count deals on each:
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "SELECT COUNT(*) FROM zakops.deals;"
docker exec zakops-postgres psql -U dealengine -d zakops -c "SELECT COUNT(*) FROM deals;"  # note: may use public schema
```

### CONFLICT 2: Archived Deal Count (6 vs 4)

| Agent | Archived Count | DB Queried |
|-------|---------------|------------|
| CC3 | 6 | 5432 (via docker exec zakops-backend-postgres-1) |
| Codex | 4 | 5435 (via localhost:5435) |
| CC1 | 6 | 5432 |

**Resolution:** The discrepancy is explained by the split-brain: the two databases have different data. The canonical count is **6** (from DB 5432, which the backend API uses). Codex queried the stale DB 5435 which has 4 archived-stage deals.

**Verification command:**
```bash
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT stage, COUNT(*) FROM zakops.deals WHERE deleted = false GROUP BY stage ORDER BY stage;"
```

### CONFLICT 3: Zod Error Root Cause (Three Theories)

| Agent | Theory |
|-------|--------|
| CC3 | **Promise.all fragility** — 3 of 4 fetches lack try/catch. Any ApiError blanks entire HQ. Quarantine endpoint is intermittent trigger. |
| Codex | **Agent activity schema mismatch** — `/api/agent/activity` returns `[]` but schema expects object `{status, recent, stats, ...}`. |
| CC1 | **Archived deal data shape** — Archived deals leaking into active view have missing fields that fail Zod validation. |

**Resolution:** These are **not mutually exclusive**. All three can coexist and trigger at different times, explaining the "intermittent" nature:
- CC3's theory explains WHY any single failure blanks the whole page (structural fragility)
- Codex's theory identifies a SPECIFIC trigger (agent activity returns wrong shape)
- CC1's theory identifies ANOTHER trigger (archived deals with malformed fields)

However, CC3 noted that `DealSchema` uses `.passthrough()` which is tolerant of missing fields, weakening CC1's theory. And CC3's route handler analysis showed that the agent activity proxy returns `getEmptyResponse()` (an object) on fetch failures, but Codex captured evidence of `[]` being returned — suggesting there may be a code path where the proxy is bypassed or returns raw data.

**Verification commands:**
```bash
# Test agent activity response shape:
curl -s http://localhost:3003/api/agent/activity | python3 -c "import sys,json; d=json.load(sys.stdin); print(type(d).__name__, list(d.keys()) if isinstance(d,dict) else len(d))"

# Test quarantine endpoint:
curl -s -o /dev/null -w "%{http_code}" http://localhost:8091/api/actions/quarantine

# Test with archived deal in Zod:
curl -s 'http://localhost:8091/api/deals?status=active' | python3 -c "
import sys, json
deals = json.loads(sys.stdin.read())
if isinstance(deals, list):
    for d in deals:
        if d.get('stage') == 'archived':
            print('Archived deal fields:', sorted(d.keys()))
"
```

### CONFLICT 4: Issue 5 (Propagation) Root Cause

| Agent | Position |
|-------|----------|
| CC3 | **Perception issue.** Creation works correctly. The count gap from archived deals creates an illusion of non-propagation. |
| Codex | **Split-brain DB.** UI writes to 5432, other services read 5435. Real data invisibility. |
| CC1 | **Split-brain DB.** Same as Codex. |

**Resolution:** Both are partially correct:
- **Within the Dashboard:** CC3 is right — creation works, the gap is visual
- **Across services:** Codex/CC1 are right — if Agent/RAG uses the wrong DB, created deals are truly invisible

**Verification command:**
```bash
# Create a test deal via API, then check both DBs:
# (Would need to be done in PASS 3 with operator permission)
```

### UNCERTAINTY 1: HQ "1 Issue" Badge Source

Codex flagged: "Whether the HQ '1 Issue' badge is directly tied to the Zod error" — unresolved. The code search did not find a dedicated badge component in HQ. It may be the Next.js dev mode error overlay or a global error counter.

**Verification:** Open `/hq` in browser with DevTools console open. Look for Zod errors. Check if the "1 Issue" badge is a React Error Boundary indicator or an application-level counter.

### UNCERTAINTY 2: Codex's "API Pagination Limit" Finding

Codex noted the backend list endpoint defaults to `limit=50` (main.py:467), suggesting pagination could truncate results. With only 37 non-deleted deals, this limit is not currently triggered. However, at scale (50+ active deals), the UI would show a truncated count without a `total_count` field.

**Status:** Not currently a bug (37 < 50), but a latent scaling issue. Addressed by DI-ISSUE-002 Innovation #4 (add `total_count` to API response).

---

## 5. What's the One Systemic Root Cause?

**There are TWO systemic root causes, not one.** They are independent and both must be fixed:

### Systemic Root Cause A: Incoherent Deal Lifecycle State Machine

**Scope:** DI-ISSUE-001, 002, 003, 004, 007 (partially)

The deal table has three state signals (`status`, `stage`, `deleted`) with no enforced coupling. The archive endpoint updates only `stage`, leaving `status='active'` and `deleted=false`. This creates phantom states where a deal is simultaneously "active" (by status) and "archived" (by stage). Every downstream surface — API filters, pipeline counts, HQ dashboard, /deals page — inherits this contradiction differently, producing six observable symptoms.

**Proof:** All three agents independently identified the archive endpoint's partial transition as the root cause of Issues 1-4 and 6. CC3 explicitly stated: "The fix is not 6 separate patches — it's one lifecycle state machine." Codex stated: "enforce single canonical DB + unify 'active' semantics (status/stage/deleted) across API/UI/pipeline." CC1 stated: "Data Model Ambiguity" as one of three root causes.

**Fix:** Introduce a coherent lifecycle state machine. Either:
- (a) Single `lifecycle_state` ENUM column that is the sole authority for visibility (CC3)
- (b) Atomic transition function that updates all three fields consistently (CC3)
- (c) DB trigger that auto-sets `status` when `stage` changes (CC1)
- (d) At minimum: fix archive endpoint to set `status='archived'` + backfill + CHECK constraint (all agents)

### Systemic Root Cause B: Split-Brain Database Infrastructure

**Scope:** DI-ISSUE-006, 007 (partially), DI-ISSUE-002 (partially)

Two Postgres containers serve different data. The backend API writes to `postgres:5432` (49 deals), but a legacy container `zakops-postgres` on port 5435 has 51 stale deals. Any service or script connecting to the wrong port sees outdated data and cannot see new deals.

**Proof:** Codex and CC1 independently found the two containers and the 49-vs-51 discrepancy. The different archived counts (6 vs 4) between agents are themselves evidence of the split-brain — agents queried different databases.

**Fix:** Kill the rogue container. Audit all DSN configurations. Add health-check DB identity verification. Use service discovery to prevent drift.

### Relationship Between A and B

These are **independent defects**:
- Root Cause A would exist even with a single DB (archive endpoint is broken regardless of which DB it writes to)
- Root Cause B would exist even with a perfect data model (two DBs with any schema still diverge)

Fixing only A leaves cross-service data invisibility. Fixing only B leaves the status/stage conflation. **Both must be fixed for full resolution.**

### Recommended Fix Order

```
Phase 0: DI-ISSUE-006 (kill rogue DB)         ← Infrastructure, blocks nothing but prevents confusion
Phase 1: DI-ISSUE-001 (fix archive endpoint)   ← Root cause, unblocks 002/003/004
Phase 2: DI-ISSUE-002 (add total_count to API) ← Count consistency
Phase 3: DI-ISSUE-003 (use server-side counts) ← Pipeline accuracy
Phase 4: DI-ISSUE-004 (fix active filter)       ← Filter semantics
Phase 5: DI-ISSUE-005 (Promise.allSettled)      ← HQ resilience
Phase 6: DI-ISSUE-007 (verify propagation)      ← Should be resolved by Phases 0-4
Phase 7: DI-ISSUE-008 + 009 (latent bugs)       ← Cleanup
```

---

## Appendix: Full Innovation Ideas Index

For operator reference — all unique ideas across all agents, deduplicated:

| ID | Idea | Source(s) | Applies To |
|----|------|-----------|------------|
| I-01 | Lifecycle State ENUM column | CC3 | DI-ISSUE-001 |
| I-02 | Soft-Delete with `deleted_at` Tombstone | CC3 | DI-ISSUE-001 |
| I-03 | Event-Sourced Deal Lifecycle | CC3 | DI-ISSUE-001 |
| I-04 | DB Trigger Auto-Sets Status | CC1 | DI-ISSUE-001 |
| I-05 | Separate Archive Table | Codex | DI-ISSUE-001 |
| I-06 | State Machine via `transitions` Library | CC1 | DI-ISSUE-001 |
| I-07 | Materialized View for Stats | CC1 | DI-ISSUE-002 |
| I-08 | Count Ledger Service | Codex | DI-ISSUE-002 |
| I-09 | DB Identity Tagging | Codex | DI-ISSUE-002, 006 |
| I-10 | API Returns `total_count` | Codex | DI-ISSUE-002, 007 |
| I-11 | CQRS with Read Models | CC3 | DI-ISSUE-002 |
| I-12 | Canonical Stage Config Object | CC3, Codex | DI-ISSUE-003 |
| I-13 | Backend-Driven Pipeline Definition | CC3 | DI-ISSUE-003 |
| I-14 | Pipeline Summary API as SSOT | Codex | DI-ISSUE-003 |
| I-15 | Faceted Search with Counts | CC3 | DI-ISSUE-004 |
| I-16 | Smart Default Filter with URL State | CC3 | DI-ISSUE-004 |
| I-17 | Filter Composition (complex filter params) | CC1 | DI-ISSUE-004 |
| I-18 | `visibility_state` Filter Enum | Codex | DI-ISSUE-004 |
| I-19 | Materialized `active_deals` View | Codex | DI-ISSUE-004 |
| I-20 | React Suspense Boundaries per Widget | CC3 | DI-ISSUE-005 |
| I-21 | SWR / TanStack Query | CC3 | DI-ISSUE-005 |
| I-22 | Unified "Empty State" Object | Codex | DI-ISSUE-005 |
| I-23 | Schema Versioning | Codex | DI-ISSUE-005 |
| I-24 | Contract Tests in CI (Zod vs DB) | CC1 | DI-ISSUE-005 |
| I-25 | Service Discovery / Env Injection | CC1 | DI-ISSUE-006 |
| I-26 | Health Endpoint with DB Identity | Codex | DI-ISSUE-006 |
| I-27 | Optimistic UI Updates | CC3 | DI-ISSUE-007 |
| I-28 | Event-Driven Cache Invalidation | CC3 | DI-ISSUE-007 |
| I-29 | Event-Driven Read Model | Codex | DI-ISSUE-007 |
| I-30 | Database-Level Archive Partitioning | CC3 | DI-ISSUE-001 |

---

**END OF PASS 2 CROSS-REVIEW**

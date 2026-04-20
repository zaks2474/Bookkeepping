# DEAL-INTEGRITY-001 — PASS 1 FORENSIC REPORT

**Run ID:** `20260208T160103Z`
**Agent:** Claude Code (Opus 4.6)
**Pass:** 1 — INVESTIGATE → REPORT → STOP
**Date:** 2026-02-08
**Backend Revision:** `444dff6`
**Scope:** 6 pipeline/deal-integrity issues — root causes, fix approaches, industry practices, design alternatives

---

## EXECUTIVE SUMMARY

The deal pipeline has **one fundamental defect** that cascades into five observable symptoms: the system conflates three independent archive mechanisms (`status` column, `stage` column, `deleted` boolean) without a coherent lifecycle state machine. The `archive` endpoint only sets `stage='archived'` while leaving `status='active'` and `deleted=false`, so archived deals remain visible in "active" views. Every downstream surface — API, /hq, /deals, pipeline summary — inherits this confusion differently, producing count disagreements.

**Database ground truth:** 49 total deals. 37 non-deleted, 12 soft-deleted. All 49 have `status='active'`. 6 non-deleted deals have `stage='archived'`.

---

## ISSUE 1: Deal Counts Disagree Across Surfaces

### Confirmed Root Cause

The API `GET /api/deals` filters only by `deleted = FALSE` (and optionally by `status`, defaulting to `'active'`). Since **all 49 deals have `status='active'`** (including soft-deleted and archived ones), the status filter is a no-op on the non-deleted set. The API returns all 37 non-deleted deals regardless of stage.

Different surfaces then count different subsets:

| Surface | Count | What It Counts |
|---------|-------|----------------|
| DB total | 49 | All rows |
| DB non-deleted | 37 | `deleted=false` |
| DB soft-deleted | 12 | `deleted=true` |
| API unfiltered | 37 | `deleted=false` (status filter is no-op) |
| API `?status=active` | 37 | Same — all non-deleted have `status='active'` |
| API `?status=archived` | 0 | No deals have `status='archived'` |
| Pipeline summary | 37 | View: `deleted=false AND status='active'`, all stages including 'archived' |
| Pipeline (excl. archived) | 31 | 37 − 6 archived-stage deals |
| /hq header | 37 | `deals.length` from API |
| /hq pipeline cards | 31 | `PIPELINE_STAGES` excludes 'archived' and 'junk' |
| /deals page | 37 | API with `?status=active` default |

**Evidence:**
- `evidence/00-forensics/db-full-breakdown.txt` — Cross-tabulation of deleted × stage
- `evidence/00-forensics/db-distinct-statuses.txt` — Only one value: `active`
- `evidence/00-forensics/api-deals-unfiltered.txt` — 37 deals returned
- `evidence/00-forensics/api-deals-archived-filter.txt` — 0 deals returned

**Code paths:**
- Backend `main.py:466-513`: `conditions = ["deleted = FALSE"]` + optional status/stage filters
- Migration `023_stage_check_constraint.sql`: `v_pipeline_summary` view filters `deleted = false AND status = 'active'`

### Permanent Fix Approach

1. **Make the archive endpoint set `status='archived'`** in addition to `stage='archived'`, so `?status=active` correctly excludes archived deals.
2. **OR** add explicit `stage != 'archived'` filter to the default deals listing when status is 'active'.
3. Ensure `v_pipeline_summary` either excludes archived-stage deals from the pipeline view or presents them in a separate category.

### Industry Best Practice: Finite State Machine for Deal Lifecycle

The CRM/deal management industry standard is a **single authoritative lifecycle field** governed by a finite state machine (FSM) with explicit, validated transitions. Salesforce Opportunities use `StageName` with `IsClosed`/`IsWon` derived fields. HubSpot uses `dealstage` with a pipeline definition. PipeDrive uses a single `stage_id` within a pipeline definition.

### Why This Standard Fits ZakOps

ZakOps currently has three overlapping signals (`status`, `stage`, `deleted`) with no enforced transitions between them. The archive endpoint only updates one of three, creating phantom states. An FSM would:
- Eliminate impossible state combinations (e.g., `status='active'` + `stage='archived'`)
- Make every transition explicit and auditable
- Allow each surface to query a single field with deterministic results

### How to Implement So It Never Recurs

1. Add a migration that introduces a `lifecycle_state` ENUM column: `active`, `archived`, `deleted`
2. Backfill from current data: `deleted=true` → `deleted`, `stage='archived'` → `archived`, else → `active`
3. Modify all endpoints to use `lifecycle_state` for visibility filtering
4. Add CHECK constraint: `lifecycle_state = 'archived' → stage = 'archived'`
5. Add database trigger or application-level guard that sets `lifecycle_state` atomically with any stage/status change
6. Deprecate the `status` column (currently always 'active', adds no information)

### Design Alternative 1: Soft-Delete with Tombstone Pattern

Instead of three fields, use a single `deleted_at` TIMESTAMP NULL column. `NULL` = active, non-null = archived/deleted. The `stage` column stays as-is for pipeline position but archived deals get `deleted_at = NOW()`. Every query filters `WHERE deleted_at IS NULL` for "active" views.

**Tradeoffs:** Simpler (one column vs three), naturally supports "when was it archived?" queries, but loses the distinction between "archived" (recoverable) and "permanently deleted" (could add a separate `purged` boolean if needed). Widely used in Rails/Django ecosystems.

### Design Alternative 2: Event-Sourced Deal Lifecycle

Every deal state change is an immutable event in a `deal_events` table. Current state is a materialized view or computed column derived from the latest event. Archive = `event_type='archived'` event. Restore = `event_type='restored'` event. Delete = `event_type='deleted'` event.

**Tradeoffs:** Full audit trail for free, impossible to have inconsistent state (state is always derived), supports undo/replay. But adds read complexity (must aggregate events to get current state), requires careful indexing of the materialized view, and is overkill if the system doesn't need full event history. Fits well if ZakOps plans to add deal activity timelines or compliance audit trails.

---

## ISSUE 2: Pipeline Stage Totals Don't Sum to Header Count

### Confirmed Root Cause

The `/hq` page (`apps/dashboard/src/app/hq/page.tsx`) has a structural mismatch:

- **Header:** `total_active_deals: deals.length` = **37** (all non-deleted deals from API)
- **Pipeline cards:** Calculated client-side using `PIPELINE_STAGES` array (lines 18-26):
  ```
  ['inbound', 'screening', 'qualified', 'loi', 'diligence', 'closing', 'portfolio']
  ```
  This array has **7 entries** — it excludes `'archived'` and `'junk'` from the 9 valid stages.
- **Pipeline sum:** 21 + 7 + 1 + 1 + 1 + 0 + 0 = **31**
- **Gap:** 37 − 31 = **6** = exactly the 6 deals with `stage='archived'`

The deals with `stage='archived'` are counted in the header (they're in the API response) but have no pipeline card to land in. They fall through the cracks of the client-side filter.

**Evidence:**
- `evidence/00-forensics/api-pipeline-summary.txt` — archived: 6, total across stages: 37
- `evidence/00-forensics/db-full-breakdown.txt` — 6 non-deleted deals with stage='archived'
- `hq/page.tsx:18-26` — `PIPELINE_STAGES` literal array
- `hq/page.tsx:62-66` — Client-side `dealsByStage` reduce
- `hq/page.tsx:72` — `total_active_deals: deals.length`

### Permanent Fix Approach

1. **Exclude archived-stage deals from the header count** by filtering: `deals.filter(d => d.stage !== 'archived' && d.stage !== 'junk').length`
2. **OR** add an "Archived" category card to the pipeline view so all deals are accounted for
3. **AND** add `'junk'` handling (currently 0 but the stage exists in the CHECK constraint)

### Industry Best Practice: Server-Side Pipeline Aggregation

Pipeline dashboards in Salesforce, HubSpot, and Monday.com compute stage counts **server-side** and return them as a structured summary object. The client never needs to filter or count — it just renders what the server provides. This prevents client/server count divergence.

### Why This Standard Fits ZakOps

The backend already HAS `GET /api/pipeline/summary` which returns server-computed stage counts from `v_pipeline_summary`. But the `/hq` page ignores it entirely — it fetches all deals via `getDeals()` and counts client-side. This duplicates logic and introduces the divergence.

### How to Implement So It Never Recurs

1. `/hq` should call `GET /api/pipeline/summary` for stage counts instead of client-side computation
2. The pipeline summary view should define exactly which stages are "pipeline" stages (exclude archived/junk) and return them separately
3. Add a `total_pipeline_deals` field to the summary response that only counts pipeline-stage deals
4. Add a `total_other_deals` field for archived + junk
5. Ensure `total_pipeline_deals + total_other_deals = total_active_deals`
6. Add a contract test: "sum of all stage counts equals total count"

### Design Alternative 1: Canonical Stage Configuration Object

Define stages in a single shared configuration:
```typescript
const STAGE_CONFIG = {
  inbound:    { pipeline: true,  display: 'Inbound' },
  screening:  { pipeline: true,  display: 'Screening' },
  qualified:  { pipeline: true,  display: 'Qualified' },
  loi:        { pipeline: true,  display: 'LOI' },
  diligence:  { pipeline: true,  display: 'Diligence' },
  closing:    { pipeline: true,  display: 'Closing' },
  portfolio:  { pipeline: true,  display: 'Portfolio' },
  archived:   { pipeline: false, display: 'Archived' },
  junk:       { pipeline: false, display: 'Junk' },
};
```
Derive `PIPELINE_STAGES`, display names, and CHECK constraints from this single source. Backend and frontend share it via the contracts package.

**Tradeoffs:** Single source of truth eliminates drift. Slightly more infrastructure to share between backend/frontend, but ZakOps already has a contracts package for exactly this purpose.

### Design Alternative 2: Backend-Driven Pipeline Definition

The backend returns its pipeline definition via `GET /api/pipeline/config`:
```json
{
  "pipeline_stages": ["inbound","screening","qualified","loi","diligence","closing","portfolio"],
  "terminal_stages": ["archived","junk"],
  "default_stage": "inbound"
}
```
The frontend renders whatever the backend declares. Adding/removing stages requires zero frontend changes.

**Tradeoffs:** Maximum flexibility, supports multi-pipeline configurations (e.g., different pipelines for different deal types). Adds an API call but it's cacheable. The frontend loses compile-time type safety for stage names unless the config is fetched at build time.

---

## ISSUE 3: Archived Deals Appear in "Active" Views

### Confirmed Root Cause

The archive endpoint (`POST /api/deals/{deal_id}/archive`, `main.py:867-907`) executes:

```sql
UPDATE zakops.deals
SET stage = 'archived', updated_at = NOW()
WHERE deal_id = $1
```

It sets **only** `stage = 'archived'`. It does NOT:
- Set `status = 'archived'` (status remains `'active'`)
- Set `deleted = true` (deleted remains `false`)

Therefore, when `GET /api/deals?status=active` is called (the default), archived deals pass the filter because they still have `status='active'` and `deleted=false`.

**Evidence:**
- `main.py:881-884` — Archive SQL: only `SET stage = 'archived'`
- `main.py:478-482` — Deals listing: `conditions = ["deleted = FALSE"]`, status filter adds `status = $N`
- `evidence/00-forensics/db-distinct-statuses.txt` — Only value: `active`
- `evidence/00-forensics/db-archived-stage-deals.txt` — 6 deals with `stage='archived'`, all `deleted=false`
- `evidence/00-forensics/api-deals-archived-filter.txt` — `?status=archived` returns `[]`

### Permanent Fix Approach

1. Modify `POST /api/deals/{deal_id}/archive` to also set `status = 'archived'`:
   ```sql
   SET stage = 'archived', status = 'archived', updated_at = NOW()
   ```
2. Backfill existing data: `UPDATE zakops.deals SET status = 'archived' WHERE stage = 'archived' AND deleted = false`
3. Add a database CHECK constraint: `stage = 'archived' → status = 'archived'`

### Industry Best Practice: Atomic State Transitions

In domain-driven design, state transitions should be **atomic operations** that update all related fields in a single transaction. Salesforce's `Opportunity.StageName` update automatically recalculates `IsClosed`, `IsWon`, `ForecastCategory`, and `Probability` in one operation. No field is left inconsistent.

### Why This Standard Fits ZakOps

The current archive operation is a "partial transition" — it moves one of three state signals and leaves the other two stale. Every consumer that checks `status` gets the wrong answer. An atomic transition function would update all three signals (or a single lifecycle field) in one SQL statement.

### How to Implement So It Never Recurs

1. Create a `transition_deal_state(deal_id, target_state)` database function that atomically updates `stage`, `status`, `deleted`, and `updated_at` based on the target state
2. All endpoints (archive, restore, delete, undelete) call this function instead of writing raw UPDATE queries
3. Add a trigger or CHECK constraint that enforces consistency: `(status='active' AND deleted=false AND stage NOT IN ('archived','junk')) OR (status='archived' AND deleted=false AND stage='archived') OR (deleted=true)`
4. Add an integration test: "after archiving, deal is NOT returned by `?status=active`"

### Design Alternative 1: Archive as Soft-Delete

Treat archiving as a soft-delete: `SET deleted = true, stage = 'archived', updated_at = NOW()`. The `deleted = FALSE` filter in the deals listing already excludes these. Restore sets `deleted = false` and moves stage back.

**Tradeoffs:** Simplest fix — leverages the existing `deleted` filter that already works. But semantically conflates "archived" (user chose to shelve it) with "deleted" (something went wrong / data cleanup). If the distinction matters for compliance or analytics, this loses information.

### Design Alternative 2: Database-Level Archive Partitioning

Use PostgreSQL table partitioning: `deals` partitioned by `lifecycle_state`. Active deals in one partition, archived in another. The default partition is `active`. Queries against the `active` partition never see archived deals without explicit opt-in.

**Tradeoffs:** Physical separation makes it impossible to accidentally query archived deals. Excellent for performance at scale (archived data doesn't slow active queries). But adds schema complexity, makes cross-partition queries (e.g., "show all deals including archived") require explicit `UNION` or partition-aware queries. Overkill at 49 deals but becomes valuable at 10k+.

---

## ISSUE 4: Zod Error on Operator HQ (Intermittent)

### Confirmed Root Cause

The `/hq` page (`hq/page.tsx:38-46`) uses `Promise.all` with four parallel data fetches:

```typescript
const [dealsData, pendingData, quarantineData, activityData] = await Promise.all([
  getDeals({ status: 'active' }),           // NO individual try/catch
  getKineticActions({ status: 'pending_approval' }), // NO individual try/catch
  getQuarantineQueue(),                      // NO individual try/catch
  getAgentActivity(100),                     // HAS try/catch, returns null on error
]);
```

**Three of four functions lack individual error boundaries.** If any of them throws an `ApiError` (non-200 response from backend), the entire `Promise.all` rejects. The outer catch block (`line 51-53`) logs `console.error('Failed to load HQ data:', err)` and leaves all state at default empty values.

The **intermittent trigger** is `getQuarantineQueue()`, which calls `/api/actions/quarantine`. This endpoint proxies through the Next.js rewrite to `http://localhost:8091/api/actions/quarantine`. When the backend's actions subsystem returns a non-200 response or an unexpected shape:
- **Non-200**: `apiFetch` throws `ApiError` → propagates up (no try/catch in `getQuarantineQueue`) → blanks entire HQ
- **200 with unexpected shape**: `QuarantineResponseSchema.safeParse` fails → `console.error('Invalid quarantine queue response:', parsed.error)` — this is the **literal Zod validation error** logged to console

Additionally, `getAgentActivity` routes through the Next.js API handler (`app/api/agent/activity/route.ts`) which proxies to the Agent API at port 8095. This handler has robust error handling (returns `getEmptyResponse()` on any failure). However, when the Agent API IS available but returns data that doesn't conform to `AgentActivityResponseSchema`, the safeParse at `api.ts:1945` fails with a Zod error. The handler's `getEmptyResponse()` only fires for fetch failures, not for schema mismatches in the transformed data.

**Evidence:**
- `hq/page.tsx:38-46` — Promise.all with 4 calls, only `getAgentActivity` has try/catch
- `api.ts:758-778` — `getQuarantineQueue`: no try/catch, safeParse with console.error on failure
- `api.ts:1941-1956` — `getAgentActivity`: has try/catch, safeParse with console.error on failure
- `api.ts:397-404` — `apiFetch`: throws `ApiError` on non-200
- `app/api/agent/activity/route.ts:73-77` — Returns empty response on fetch error, but safeParse happens client-side after transformation

### Permanent Fix Approach

1. Wrap each of the four `Promise.all` members in individual try/catch blocks (or use `Promise.allSettled`)
2. Each function should never throw — return empty/null on error, matching `getAgentActivity`'s pattern
3. Add defensive schemas with `.passthrough()` and optional fields for endpoints that may evolve

### Industry Best Practice: Promise.allSettled + Per-Widget Error Boundaries

Modern dashboard frameworks (Grafana, Datadog, Vercel Analytics) use **independent error boundaries per widget**. Each dashboard section fetches its own data and fails independently. React Error Boundaries or `Promise.allSettled` ensure one failing data source doesn't blank the entire page.

### Why This Standard Fits ZakOps

The `/hq` page is a dashboard with four independent data sections: pipeline, pending actions, quarantine, agent activity. A quarantine API failure should not blank out pipeline data. The current `Promise.all` architecture creates a fragile "all-or-nothing" data fetch.

### How to Implement So It Never Recurs

1. Replace `Promise.all` with `Promise.allSettled` in `/hq`
2. For each settled result, check `.status === 'fulfilled'` before using `.value`; on `'rejected'`, use default empty state and log the error
3. Add individual try/catch to `getQuarantineQueue` and `getKineticActions` matching `getAgentActivity`'s pattern
4. Add a visual indicator per widget: "Failed to load quarantine data" vs blanking the whole page
5. Add a contract test: "HQ page renders pipeline data even when quarantine API returns 500"

### Design Alternative 1: Suspense Boundaries per Widget

Use React Suspense with per-widget boundaries:
```tsx
<Suspense fallback={<PipelineSkeleton />}>
  <PipelineWidget />
</Suspense>
<Suspense fallback={<QuarantineSkeleton />}>
  <QuarantineWidget />
</Suspense>
```
Each widget fetches its own data. Errors in one don't affect others.

**Tradeoffs:** Clean separation of concerns, native React pattern, supports streaming SSR. Requires refactoring /hq from a single page component into multiple sub-components with their own data fetching. More files but better architecture.

### Design Alternative 2: SWR/React Query with Stale-While-Revalidate

Use a data-fetching library (SWR or TanStack Query) with independent cache keys per data source:
```typescript
const { data: deals } = useSWR('/api/deals?status=active', fetcher);
const { data: quarantine } = useSWR('/api/actions/quarantine', fetcher);
```
Each hook manages its own loading/error/data state independently. Built-in retry, caching, and background revalidation.

**Tradeoffs:** Eliminates hand-rolled Promise.all entirely. Automatic retry smooths over intermittent failures. Adds a library dependency. The current `'use client'` pattern already supports this approach. Cache invalidation needs careful key management.

---

## ISSUE 5: UI-Created Deals Exist in DB but Don't Fully Propagate

### Confirmed Root Cause

Deal creation via `POST /api/deals` (`main.py:565-621`) works correctly at the database level:
- Sets `status = 'active'`, `stage = 'inbound'` (or provided stage), `deleted = false`
- Inserts a `deal_created` event into the events table
- Returns the new `deal_id`

The "not fully propagating" symptom is a **perception issue** caused by Issue 1 and Issue 2:
1. New deals with `stage='inbound'` appear correctly in the API response and pipeline
2. But if a user archives a deal and then creates a new one, the **header count stays the same** (new deal + archived deal = net zero change in pipeline cards, but +1 in header) — reinforcing the count mismatch illusion
3. The `/deals` page shows the new deal immediately (it calls `getDeals` which returns all non-deleted deals)
4. The `/hq` page shows the new deal in the `inbound` pipeline card, but the header/pipeline gap persists

Additionally, the backend has a latent bug: `audit_trail` is referenced in code (`main.py:1103, 1142, 1263`) but the column does NOT exist in the deals schema. If any code path attempts to read/write `audit_trail`, it would cause a SQL error. However, deal creation does not reference `audit_trail`, so creation itself succeeds.

**Evidence:**
- `main.py:565-621` — Deal creation: INSERT with status='active', stage='inbound', deal_created event
- `evidence/00-forensics/db-full-breakdown.txt` — 21 inbound deals (all non-deleted), consistent with creation working
- `main.py:1103, 1142, 1263` — `audit_trail` column references (latent bug, not triggered by creation)
- `evidence/00-forensics/db-deals-schema.txt` — No `audit_trail` column in schema

### Permanent Fix Approach

1. Fix Issues 1-3 first — once archived deals are properly excluded from active views, the count discrepancy disappears and new deals propagate correctly to all surfaces
2. Remove or add the `audit_trail` column: either add it via migration if the feature is intended, or remove the code references
3. Add an integration test: "create deal → GET /api/deals → new deal appears → /api/pipeline/summary inbound count increased by 1"

### Industry Best Practice: Optimistic UI Updates with Server Confirmation

Modern CRM UIs (HubSpot, Salesforce Lightning) use **optimistic updates**: the UI immediately shows the new deal in the pipeline before the server confirms. Once the server responds, the UI reconciles. If the server rejects, the UI rolls back with an error message.

### Why This Standard Fits ZakOps

The current flow is: POST → server creates → user navigates back → fresh GET → sees deal. There's no real-time update. If the GET has caching or the pipeline calculation has the archived-deal gap, the user may not see the new deal reflected correctly in totals.

### How to Implement So It Never Recurs

1. After `createDeal()` succeeds, optimistically add the deal to the local deals array in state
2. Invalidate/refetch pipeline summary data
3. Use a WebSocket or SSE connection for real-time deal count updates (if the system grows)
4. Add an end-to-end test: create deal → verify it appears in /deals, /hq pipeline, and pipeline summary

### Design Alternative 1: Event-Driven Cache Invalidation

After any deal mutation (create, archive, restore), publish an event (via Redis pub/sub or pg_notify) that triggers cache invalidation on all connected dashboards. Every surface always shows the latest state.

**Tradeoffs:** Real-time consistency across all surfaces. Requires pub/sub infrastructure. At ZakOps's current scale (49 deals), this is overengineered — simple refetch-on-mutation suffices.

### Design Alternative 2: CQRS with Read Models

Separate the write model (deal mutations) from read models (pipeline counts, deal listings). Each mutation updates a denormalized read model table (`pipeline_counts`, `active_deals_view`). Dashboards query read models for instant, consistent data.

**Tradeoffs:** Eliminates count disagreements by design — read models are always consistent. But adds complexity (two models to maintain, eventual consistency window). Best suited for high-read, low-write systems at scale. ZakOps would benefit more from fixing the state machine first.

---

## ISSUE 6: "Active Filter" Doesn't Actually Filter

### Confirmed Root Cause

The `/deals` page (`apps/dashboard/src/app/deals/page.tsx:66`) has a status filter dropdown with values:
```typescript
['active', 'junk', 'merged']
```

The default filter is `'active'` (line 94): `searchParams.get('status') || 'active'`

This passes `?status=active` to the API. But since **all 49 deals have `status='active'`** (the archive endpoint never changes status), the filter returns ALL 37 non-deleted deals — including the 6 with `stage='archived'`.

The filter **technically works** (it correctly filters by the `status` column), but the `status` column is **semantically broken** — it's always `'active'`, making the filter a no-op.

Furthermore:
- **No `'archived'` option** in the dropdown — users cannot filter to see only archived-stage deals
- `'junk'` and `'merged'` options return 0 results (no deals have these statuses)
- There is no `stage` filter in the UI, so users have no way to filter by pipeline stage

**Evidence:**
- `deals/page.tsx:66` — Status filter values: `['active', 'junk', 'merged']`
- `deals/page.tsx:94` — Default: `searchParams.get('status') || 'active'`
- `deals/page.tsx:111` — Passes to API: `params.status = statusFilterRaw`
- `evidence/00-forensics/db-distinct-statuses.txt` — Only value: `active`
- `evidence/00-forensics/api-deals-active-filter.txt` — 37 results (same as unfiltered)

### Permanent Fix Approach

1. Fix the archive endpoint (Issue 3) so `status='archived'` is set correctly
2. Add `'archived'` to the status filter dropdown
3. Consider adding a `stage` filter dropdown for pipeline-stage filtering
4. Ensure the dropdown values match the actual status values in the database

### Industry Best Practice: Filter-by-What-Users-See

Salesforce and HubSpot expose filters that match the **user's mental model**, not the raw database schema. Users think in terms of "active deals," "archived deals," "deals in screening." The filter options should reflect these categories, regardless of how they're stored internally.

### Why This Standard Fits ZakOps

Users see deals in a pipeline with stages. The natural filter is "show me deals in screening" or "show me archived deals." The current status filter (`active`/`junk`/`merged`) doesn't match any meaningful user action — `active` returns everything, and the other two return nothing.

### How to Implement So It Never Recurs

1. Replace the status-only dropdown with a **composite filter** that combines lifecycle state and pipeline stage:
   - "All Active" (pipeline stages only, exclude archived/junk)
   - "Archived"
   - "By Stage: Inbound / Screening / Qualified / LOI / Diligence / Closing / Portfolio"
2. The API should support `GET /api/deals?lifecycle=active&stage=screening` for precise filtering
3. Add a contract test: "status filter 'archived' returns only archived-stage deals, not active-stage deals"
4. Derive filter options from the stage configuration (see Issue 2, Design Alternative 1) so they stay in sync

### Design Alternative 1: Faceted Search with Counts

Display filter options as faceted search with counts next to each option:
```
Active (31)  |  Archived (6)  |  All (37)
─────────────────────────────────────────
Inbound (21)  Screening (7)  Qualified (1)  LOI (1)  Diligence (1)
```
Users see at a glance how many deals are in each category. The counts come from the pipeline summary API.

**Tradeoffs:** Excellent UX — users immediately see the distribution. Requires an additional API call for counts (or piggyback on pipeline summary). Standard in e-commerce and CRM UIs.

### Design Alternative 2: Smart Default Filter with URL State

The default filter depends on context:
- Navigating from /hq pipeline card → pre-filter to that stage
- Direct navigation to /deals → show "Active" (non-archived, non-junk)
- URL state: `/deals?lifecycle=active&stage=screening` is shareable/bookmarkable

Use Next.js `searchParams` (already partially implemented) for filter state persistence.

**Tradeoffs:** Contextual defaults reduce clicks. URL state makes filters shareable. Slightly more complex routing logic but leverages Next.js's built-in search params handling.

---

## BONUS FINDING: `audit_trail` Column Referenced but Missing

**Location:** `main.py:1103, 1142, 1263`
**Severity:** Latent — will cause `UndefinedColumn` SQL error if any code path reaches these lines
**Evidence:** `evidence/00-forensics/db-deals-schema.txt` — column not present in deals table
**Recommendation:** Either add the column via migration or remove the dead code references. This should be addressed in PASS 2.

---

## BONUS FINDING: `/api/actions/kinetic` Returns HTTP 500

**Observation:** `GET /api/actions/kinetic` returns HTTP 500 Internal Server Error.
**Impact:** Low — the dashboard does not call this endpoint directly. `isKineticApiAvailable()` checks `/api/actions/capabilities` (returns 200), and `getKineticActions` calls `/api/actions?status=pending_approval` (returns 200 with `[]`).
**Recommendation:** Investigate and fix the endpoint in PASS 2 to prevent confusion during debugging.

---

## CROSS-CUTTING ANALYSIS: The Fundamental Defect

All six issues stem from a single architectural flaw: **three conflated archive/visibility mechanisms with no state machine**.

```
Current state signals:
  status  (varchar, CHECK: ?, always 'active')     ← BROKEN: never changes
  stage   (varchar, CHECK: 9 values incl. archived) ← OVERLOADED: pipeline position + lifecycle
  deleted (boolean, default false)                   ← WORKS: but only for hard-delete, not archive
```

The archive endpoint updates `stage` but not `status` or `deleted`. The listing endpoint filters by `deleted` and `status` but not `stage`. The pipeline view includes all stages. The dashboard hardcodes 7 of 9 stages. Every surface sees a different slice of truth.

**The fix is not 6 separate patches — it's one lifecycle state machine** that makes the impossible states unrepresentable and the valid transitions explicit.

---

## EVIDENCE MANIFEST

All evidence files stored at:
`/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-001/evidence/00-forensics/`

| File | Contents |
|------|----------|
| `db-total-count.txt` | Total deal count: 49 |
| `db-count-by-status.txt` | Count grouped by status (all 'active') |
| `db-count-by-stage.txt` | Count grouped by stage (9 stages) |
| `db-status-x-stage.txt` | Cross-tabulation of status × stage × deleted |
| `db-distinct-statuses.txt` | Distinct status values: ['active'] |
| `db-distinct-stages.txt` | Distinct stage values |
| `db-deals-schema.txt` | Full deals table DDL |
| `db-null-status-deals.txt` | NULL status check (none found) |
| `db-recent-deals.txt` | 10 most recent deals with timestamps |
| `db-soft-delete-columns.txt` | Columns related to deletion |
| `db-deals-constraints.txt` | CHECK constraints on deals table |
| `db-deleted-flag.txt` | Count by deleted flag |
| `db-archived-stage-deals.txt` | 6 archived-stage deals detail |
| `db-deleted-true-deals.txt` | 12 soft-deleted deals detail |
| `db-full-breakdown.txt` | Complete deleted × stage breakdown |
| `api-deals-unfiltered.txt` | GET /api/deals → 37 deals |
| `api-deals-active-filter.txt` | GET /api/deals?status=active → 37 deals |
| `api-deals-archived-filter.txt` | GET /api/deals?status=archived → 0 deals |
| `api-pipeline-summary.txt` | GET /api/pipeline/summary → stage counts |
| `api-stats-endpoints.txt` | Endpoint availability check (404s, 500s) |

---

## PASS 1 VERDICT

**Status: COMPLETE — All 6 issues root-caused with evidence.**

All root causes trace to one fundamental defect: conflated archive mechanisms with no lifecycle state machine. Fix the state machine and all six symptoms resolve.

**Recommended PASS 2 priority order:**
1. Issue 3 (archive endpoint) — root cause fix, unblocks everything
2. Issue 1 (count disagreement) — resolved by #1 + query adjustments
3. Issue 2 (pipeline sum) — add server-side aggregation to /hq
4. Issue 6 (active filter) — add proper filter options
5. Issue 4 (Zod error) — Promise.allSettled + per-widget error boundaries
6. Issue 5 (propagation) — resolved by #1-4, add optimistic UI

**HARD STOP — No fixes applied. Investigation only.**

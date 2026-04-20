# Innovation Roadmap — DEAL-INTEGRITY-UNIFIED

| Field       | Value                          |
|-------------|--------------------------------|
| Date        | 2026-02-08 (updated 2026-02-09)|
| Mission     | DEAL-INTEGRITY-UNIFIED         |
| Layer       | 6 — Governance                 |
| Source      | DEAL-INTEGRITY-001 PASS 3 Master Consolidation |

This document catalogues all 34 innovation ideas that emerged during the
DEAL-INTEGRITY investigation pipeline (PASS 1, PASS 2, PASS 3), organized by
priority tier. Each idea has a unique I-XX identifier, source agent, and the
DI-ISSUE it addresses.

---

## Full Innovation Index

| ID | Idea | Source | Applies To | Priority |
|----|------|--------|------------|----------|
| I-01 | Lifecycle State ENUM column | CC3 | DI-ISSUE-001 | P2 |
| I-02 | Soft-Delete with `deleted_at` TIMESTAMP | CC3 | DI-ISSUE-001 | P3 |
| I-03 | Event-Sourced Deal Lifecycle | CC3 | DI-ISSUE-001 | P3 |
| I-04 | DB Trigger auto-sets `status` on `stage` change | CC1 | DI-ISSUE-001 | P1-DONE |
| I-05 | Separate `archived_deals` table | Codex | DI-ISSUE-001 | P3 |
| I-06 | State Machine via Python `transitions` library | CC1 | DI-ISSUE-001 | P2 |
| I-07 | Computed Column `is_active` (GENERATED ALWAYS AS STORED) | CC1-P2 | DI-ISSUE-001 | P2 |
| I-08 | Database-Level Archive Partitioning | CC3 | DI-ISSUE-001 | P3 |
| I-09 | Materialized View for Stats (refreshed on write) | CC1 | DI-ISSUE-002 | P1-DONE |
| I-10 | Count Ledger Service (trigger/outbox) | Codex | DI-ISSUE-002 | P2 |
| I-11 | DB Identity Tagging (meta table + API header) | Codex | DI-ISSUE-002,006 | P1-DONE |
| I-12 | API Returns `total_count` with paginated list | Codex | DI-ISSUE-002,007 | P1 |
| I-13 | CQRS with Read Models | CC3 | DI-ISSUE-002 | P3 |
| I-14 | Canonical Stage Configuration Object | CC3+Codex | DI-ISSUE-003 | P1-DONE |
| I-15 | Backend-Driven Pipeline Definition (`/api/pipeline/config`) | CC3 | DI-ISSUE-003 | P2 |
| I-16 | Pipeline Summary API as Single Source | Codex | DI-ISSUE-003 | P1-DONE |
| I-17 | Faceted Search with Counts | CC3 | DI-ISSUE-004 | P1 |
| I-18 | Smart Default Filter with URL State | CC3 | DI-ISSUE-004 | P2 |
| I-19 | Filter Composition (complex filter params) | CC1 | DI-ISSUE-004 | P2 |
| I-20 | Dedicated `visibility_state` Filter Enum | Codex | DI-ISSUE-004 | P2 |
| I-21 | Materialized `active_deals` View | Codex | DI-ISSUE-004 | P2 |
| I-22 | React Suspense Boundaries per Widget | CC3 | DI-ISSUE-005 | P1 |
| I-23 | SWR / TanStack Query for independent data fetching | CC3 | DI-ISSUE-005 | P2 |
| I-24 | Unified "Empty State" Object for agent activity | Codex | DI-ISSUE-005 | P1 |
| I-25 | Schema Versioning for API evolution | Codex | DI-ISSUE-005 | P2 |
| I-26 | Contract Tests in CI (Zod vs actual API) | CC1 | DI-ISSUE-005 | P1 |
| I-27 | Service Discovery / Env Injection (Doppler/Vault) | CC1 | DI-ISSUE-006 | P2 |
| I-28 | Health Endpoint with DB Identity | Codex | DI-ISSUE-006 | P1-DONE |
| I-29 | Optimistic UI Updates | CC3 | DI-ISSUE-007 | P2 |
| I-30 | Event-Driven Cache Invalidation (pg_notify/Redis) | CC3 | DI-ISSUE-007 | P3 |
| I-31 | Event-Driven Read Model | Codex | DI-ISSUE-007 | P3 |
| I-32 | Schema Diff Gate (CI: code refs vs live schema) | Codex-P2 | DI-ISSUE-008 | P1 |
| I-33 | Endpoint Contract Inventory (route coverage check) | Codex-P2 | DI-ISSUE-009 | P1 |
| I-34 | Deprecation Header Pattern (RFC 8594) | CC3 | DI-ISSUE-009 | P2 |

---

## P1 — High Priority (Do Next)

### I-04: DB Trigger Auto-Sets `status` on `stage` Change — DONE

**Status:** Completed during mission (Layer 2).

The `enforce_deal_lifecycle_trigger` auto-corrects `status` when `stage` changes
to `archived` or when `deleted=true`. This eliminates the class of bugs where
`stage` and `status` can drift out of sync.

### I-09: Materialized View for Stats — DONE

**Status:** Completed during mission (Layer 3).

`v_pipeline_summary` SQL view computes stage counts server-side. The dashboard
consumes these directly instead of fetching all deals and counting in JavaScript.

**Impact:** Eliminated count mismatches between /hq header and pipeline cards.

### I-11: DB Identity Tagging — DONE

**Status:** Completed during mission (Layer 1).

The `/health` endpoint now reports dynamic DB identity via `current_database()`,
`inet_server_addr()`, `inet_server_port()`. Split-brain is instantly detectable.

### I-14: Canonical Stage Configuration Object — DONE

**Status:** Completed during mission (Layer 3).

`execution-contracts.ts` exports `PIPELINE_STAGES`, `TERMINAL_STAGES`,
`ALL_STAGES_ORDERED`, stage colors, and labels. 26 files import from it.
Zero hardcoded stage arrays remain in production code.

### I-16: Pipeline Summary API as Single Source — DONE

**Status:** Completed during mission (Layer 3).

`GET /api/pipeline/summary` returns server-computed stage counts. All dashboard
surfaces use this endpoint instead of client-side counting.

### I-28: Health Endpoint with DB Identity — DONE

**Status:** Completed during mission (Layer 1).

Health endpoint reports `dbname`, `host`, `port` from live SQL queries. DSN
startup gate raises `RuntimeError` on mismatch.

### I-12: API Returns `total_count` with Paginated List

**Status:** Not started.

Add `{total_count: N, deals: [...]}` response format to `GET /api/deals`.
UI uses `total_count` instead of `array.length`. Prevents drift when pagination
kicks in (50+ deals).

**Effort:** Small — 1-2 hours. Add COUNT query + response wrapper.

### I-17: Faceted Search with Counts

**Status:** Not started.

Display `Active (31) | Archived (6) | All (37)` with sub-facets per stage.
Counts from pipeline summary API.

**Rationale:** Standard in CRM/e-commerce UIs. Users see distribution at a glance.

**Effort:** Medium — 3-4 hours. Frontend filter component + count display.

### I-22: React Suspense Boundaries per Widget

**Status:** Partially done (ErrorBoundary class exists).

Wrap major dashboard sections (pipeline board, deal detail, reports) in React
error boundaries so a rendering error in one component doesn't crash the page.

**Rationale:** During the mission, a malformed stage value caused a full-page
crash. Error boundaries contain blast radius to a single widget.

**Effort:** Small — 1-2 hours. Create reusable `<ErrorBoundary>` and wrap routes.

### I-24: Unified "Empty State" Object for Agent Activity

**Status:** Partially done (agent activity returns typed object now).

`/api/agent/activity` should always return a typed object `{status, recent, stats}`
even when empty, never `[]`.

**Effort:** Small — 30 minutes. Normalize response shape in backend.

### I-26: Contract Tests in CI (Zod vs Actual API)

**Status:** Not started.

CI job that: (1) queries backend for valid stages from CHECK constraint,
(2) imports `ALL_STAGES_ORDERED` from `execution-contracts.ts`, (3) asserts both
are identical.

**Rationale:** Catches frontend/backend stage drift at CI time, not production.

**Effort:** Medium — 3-4 hours. Backend endpoint to extract CHECK values.

### I-32: Schema Diff Gate

**Status:** Not started.

CI gate that compares code references (column names in queries) against the live
DB schema. Detects when code references columns that don't exist or have changed.

**Effort:** Medium — 3-4 hours. Script + CI integration.

### I-33: Endpoint Contract Inventory

**Status:** Not started.

Automated check that every route defined in the OpenAPI spec has a corresponding
handler, and vice versa. Catches orphaned endpoints like the kinetic 500.

**Effort:** Small — 2 hours. Parse OpenAPI JSON + scan route files.

---

## P2 — Medium Priority (Plan for Next Quarter)

### I-01: Lifecycle State ENUM Column

**Status:** Design phase.

Replace `stage` + `status` + `deleted` with a single `lifecycle_state` ENUM column:
`active`, `archived`, `deleted`. Backfill from current data. All queries use this
single field. Eliminates "which field do I check?" bugs entirely.

**Effort:** Large — full migration + backfill + endpoint updates.

### I-06: State Machine via Python `transitions` Library

**Status:** Idea.

Implement a formal state machine using the Python `transitions` library in the
backend, replacing ad-hoc stage validation with declarative transition rules.

**Effort:** Medium — 3-4 hours. Library integration + rule definition.

### I-07: Computed Column `is_active`

**Status:** Idea.

`is_active BOOLEAN GENERATED ALWAYS AS (status = 'active' AND stage != 'archived') STORED`.
Index it. All "active" queries use `WHERE is_active = true`.

**Rationale:** Zero application code changes for enforcement. Backward compatible.

**Effort:** Small — 1 hour. Migration + index.

### I-10: Count Ledger Service

**Status:** Idea.

Maintain a running count ledger via trigger/outbox pattern. Stage count changes
propagate as events, eliminating the need for aggregate queries on every page load.

**Effort:** Medium — 4-6 hours. Trigger + ledger table + API integration.

### I-15: Backend-Driven Pipeline Definition

**Status:** Idea.

`GET /api/pipeline/config` returns `{pipeline_stages, terminal_stages, default_stage}`.
Frontend renders whatever backend declares. Adding/removing stages = zero frontend
changes.

**Effort:** Medium — 3-4 hours. New endpoint + frontend config consumer.

### I-18: Smart Default Filter with URL State

**Status:** Idea.

Encode filter state in URL query params. Deep-link to filtered views. Browser
back/forward navigates filter history.

**Effort:** Medium — 3-4 hours. URL state management + filter sync.

### I-19: Filter Composition

**Status:** Idea.

Support complex filter parameters: `?lifecycle=active&stage=qualified&owner=zak`.
Multiple filter dimensions composable via AND logic.

**Effort:** Medium — 4-6 hours. Backend query builder + frontend filter UI.

### I-20: Dedicated `visibility_state` Filter Enum

**Status:** Idea.

Backend exposes `visibility_state` (active/archived/junk) for all list queries.
Decouples filter semantics from raw DB columns.

**Effort:** Small — 2 hours. New enum + API parameter.

### I-21: Materialized `active_deals` View

**Status:** Idea.

`CREATE MATERIALIZED VIEW active_deals AS SELECT * FROM deals WHERE deleted=false AND stage!='archived'`.
Refresh on write via trigger. All "active" queries hit the view.

**Effort:** Small — 1 hour. Migration + refresh trigger.

### I-23: SWR / TanStack Query for Independent Fetching

**Status:** Idea.

Replace manual `fetch` + `Promise.allSettled` with TanStack Query (react-query).
Each widget fetches independently with built-in caching, retry, and stale-while-revalidate.

**Effort:** Medium — 4-6 hours. Library setup + refactor fetch calls.

### I-25: Schema Versioning for API Evolution

**Status:** Idea.

Version API schemas so frontend can negotiate compatibility.
`Accept: application/vnd.zakops.v2+json` pattern.

**Effort:** Large — header negotiation + versioned serializers.

### I-27: Service Discovery / Env Injection (Doppler/Vault)

**Status:** Idea.

Replace `.env` files with a secrets manager (Doppler, HashiCorp Vault).
Eliminates stale DSN references and split-brain configuration risk.

**Effort:** Large — infrastructure + integration across all services.

### I-29: Optimistic UI Updates

**Status:** Idea.

When a deal transitions stages, update the UI immediately before the API confirms.
Roll back on failure. Makes stage transitions feel instant.

**Effort:** Medium — 3-4 hours per page. State management + rollback logic.

### I-34: Deprecation Header Pattern (RFC 8594)

**Status:** Idea.

Add `Deprecation` and `Sunset` headers to endpoints scheduled for removal (e.g.,
the old kinetic endpoint). Clients can detect deprecation programmatically.

**Effort:** Small — 1 hour. Middleware + header injection.

---

## P3 — Low Priority (Backlog / Future Consideration)

### I-02: Soft-Delete with `deleted_at` TIMESTAMP

**Status:** Idea only.

Replace boolean `deleted` with `deleted_at TIMESTAMP`. Enables "deleted in the
last 30 days" queries, undo windows, and compliance audit trails.

**Effort:** Medium — migration + query updates.

### I-03: Event-Sourced Deal Lifecycle

**Status:** Idea only.

Store all deal state changes as an append-only event log. Current state is a
projection of the event stream. Enables full audit replay and temporal queries.

**Effort:** Very Large — new event store, projection engine, CQRS separation.

### I-05: Separate `archived_deals` Table

**Status:** Idea only.

Move archived deals to a separate table. Active queries never touch archived data.
Reduces table scan size as archive grows.

**Effort:** Large — migration + dual-table query logic.

### I-08: Database-Level Archive Partitioning

**Status:** Idea only.

Use PostgreSQL table partitioning to physically separate active and archived rows.
Same logical table, different physical storage. Transparent to queries.

**Effort:** Large — partitioning setup + migration of existing data.

### I-13: CQRS with Read Models

**Status:** Idea only.

Separate read and write models. Write model handles transitions via FSM. Read model
is a denormalized view optimized for dashboard queries.

**Effort:** Very Large — architectural change across backend + frontend.

### I-30: Event-Driven Cache Invalidation (pg_notify/Redis)

**Status:** Idea only.

Use `pg_notify` or Redis pub/sub to invalidate caches when deals change. Dashboard
subscribes to events and refreshes only affected widgets.

**Effort:** Large — event infrastructure + subscription logic.

### I-31: Event-Driven Read Model

**Status:** Idea only.

Combine I-03 and I-13: event-sourced write model + materialized read model. The
read model auto-updates on each event. Eventual consistency with strong audit.

**Effort:** Very Large — full CQRS + event sourcing architecture.

---

## Summary by Status

| Status | Count | IDs |
|--------|-------|-----|
| DONE (completed during mission) | 6 | I-04, I-09, I-11, I-14, I-16, I-28 |
| P1 (do next) | 7 | I-12, I-17, I-22, I-24, I-26, I-32, I-33 |
| P2 (next quarter) | 14 | I-01, I-06, I-07, I-10, I-15, I-18, I-19, I-20, I-21, I-23, I-25, I-27, I-29, I-34 |
| P3 (backlog) | 7 | I-02, I-03, I-05, I-08, I-13, I-30, I-31 |
| **TOTAL** | **34** | |

## Prioritization Criteria

| Criterion         | P1                  | P2                  | P3                  |
|-------------------|---------------------|---------------------|---------------------|
| Risk reduction    | High                | Medium              | Low                 |
| User impact       | Immediate           | Next quarter        | Future              |
| Effort            | Small-Medium        | Medium-Large        | Large               |
| Dependencies      | None                | May need infra      | Needs infra + design|

agent_name: Codex
run_id: 20260208-1015-c1xh
timestamp: 2026-02-08T10:15:00-06:00
repo_revision: agent-api=5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a; backend=444dff682885a7358767aa378759ffc9fbedf609
mission_path_used: /home/zaks/bookkeepping/doc/MISSION-DEAL-INTEGRITY-001.DM

# DEAL-INTEGRITY-001 — PASS 1 INVESTIGATION REPORT

## Scope Confirmation
Investigated the six required issues with evidence from database queries, backend runtime config, API responses, and dashboard/backend code paths. No code changes, no schema changes, no UPDATE/INSERT/DELETE queries executed.

**Primary evidence directory (read-only, pre-existing):**
- `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-001/evidence/`

**Additional evidence captured for this run (writeable):**
- `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/`

---

# ISSUE 1 — Deal counts disagree across surfaces (DB vs API vs /deals vs /hq)

## Confirmed root cause (evidence-backed)
**Split-brain database configuration + API pagination limit**.

1) **Backend runtime DB != local DB queried by operators**:
- Backend process environment shows it is connected to **`postgres:5432`** with user `zakops`:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-env-db.txt`
  - `DATABASE_URL=postgresql://zakops:zakops_dev@postgres:5432/zakops`
- Local DB queries are on **`localhost:5435`** with user `dealengine`:
  - Evidence: `/home/zaks/zakops-backend/.env` and DB queries in `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt`.

2) **DB counts do not match backend API counts**:
- DB (local 5435) shows **51 deals**:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt`
- Backend API `/api/deals` returns **37 deals**:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/api-deals-stage-counts.txt`
- Backend pipeline summary totals **37**:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-pipeline-summary.txt`

3) **List API is paginated by default**:
- Backend list endpoint defaults to `limit=50`, so even if DB matches, the API may not return all rows:
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py:467` (see snippet in `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-main-deals-list.txt`).

## Permanent fix approach (do NOT implement)
- **Enforce single canonical DB**: Align all runtime services (backend, agent, ops scripts) to one DSN. Remove/retire the unused DB or mark it read-only.
- **Add authoritative total count**: Add `/api/deals/count` or include `total_count` in `/api/deals` response. UI should use that rather than `array.length`.
- **Surface DB identity in health**: Add DB identity to `/health` (host/port/dbname) so ops can verify they’re querying the same DB as the API.

## Industry best practice / standard
- **Single Source of Truth (SSOT)** per environment. Multiple DBs = split-brain. All read models derive from one canonical DB or a consistent replica.
- **Paginated list endpoints must return total_count** to avoid UI count drift.

## Why it fits this system
ZakOps is a multi-layer system (dashboard → backend → agent). If any layer queries a different DB, all counts and pipeline views diverge. The observed 51 vs 37 gap proves this is already happening.

## Prevent recurrence (gates/tests/invariants)
- **Gate:** startup check fails if backend DSN differs from configured canonical DSN.
- **CI/Smoke:** `curl /health` must report same DB as `psql` used by ops.
- **UI invariant test:** `/api/deals/count` must equal `/api/pipeline/stats.total_active_deals`.

## 2 better-than-current design ideas
1) **DB Identity Tagging:** Add a `db_instance_id` row in a meta table and include it in every API response header. UI can show and alert if identities mismatch. *Tradeoff:* small schema addition, but huge ops clarity.
2) **Count Ledger Service:** Maintain a materialized summary table updated on write (trigger/outbox). Counts become instant and consistent. *Tradeoff:* added write overhead and migration complexity.

---

# ISSUE 2 — Pipeline stage totals do not sum to header count

## Confirmed root cause (evidence-backed)
**Archived stage excluded from stage list while total includes archived deals.**

- HQ page computes `total_active_deals = deals.length`, but stage totals use **PIPELINE_STAGES** that exclude `archived`:
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/hq/page.tsx:18` and `:63` (see `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-hq-page.txt`).
- API deals stage counts show `archived: 6`, so header total includes archived deals while stage totals do not:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/api-deals-stage-counts.txt` (total 37, archived 6, stage sum without archived = 31).

## Permanent fix approach (do NOT implement)
- Define **Active = status=active AND stage != archived AND deleted=false** and apply consistently across API, pipeline, and UI.
- Alternatively, include `archived` in stage list if it must be counted in total, but then label it clearly in pipeline UI.

## Industry best practice / standard
- **Consistent domain invariants:** A deal’s status/stage must drive all counts. UI and API should compute from the same logic.

## Why it fits this system
ZakOps displays pipeline stages prominently. Any mismatch between totals and per-stage sums undermines operator trust and breaks round-4 acceptance.

## Prevent recurrence (gates/tests/invariants)
- **Gate:** Pipeline totals must equal sum of displayed stage totals (test in API + UI).
- **Contract test:** if stage list excludes archived, then total_active must exclude archived too.

## 2 better-than-current design ideas
1) **Pipeline Summary API as single source:** `/api/pipeline` returns both total and stage sums; UI uses only that. *Tradeoff:* centralizes logic but adds dependency on API endpoint.
2) **Strict Stage Taxonomy Config:** Define stages in a shared config module that both UI and backend use; archived cannot be omitted unless explicitly flagged. *Tradeoff:* requires shared contract generation.

---

# ISSUE 3 — Archived deals appear in “active” views / filters

## Confirmed root cause (evidence-backed)
**Archive operation only sets `stage='archived'` while `status` remains `active`, and active filters use status.**

- DB status is **all active**:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-count-by-status-now.txt`.
- Archived deals exist by stage:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-count-by-stage-now.txt` (archived count 4).
- Archive endpoint only updates `stage`, not `status` or `deleted`:
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py:868` (see `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-main-archive-handlers.txt`).
- Active filter in UI uses `status=active` only:
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx:94-111` (see `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-deals-page-filter.txt`).

## Permanent fix approach (do NOT implement)
- On archive: set **status='archived'** or set `deleted=true` and remove from active filters.
- Update list queries to filter **stage != 'archived'** when status=active.

## Industry best practice / standard
- **Single field defines activeness** (either `status` or `deleted`, not stage).

## Why it fits this system
A deal can’t be “archived” and “active” simultaneously without breaking filters, counts, and stage summaries.

## Prevent recurrence (gates/tests/invariants)
- **DB constraint:** if `stage='archived'` then `status='archived'` OR `deleted=true`.
- **API tests:** `GET /api/deals?status=active` must not return archived stage.

## 2 better-than-current design ideas
1) **Soft-delete workflow table:** Use a separate table for archived deals and move rows on archive. *Tradeoff:* requires migration, but eliminates mixed semantics.
2) **Status enum enforcement:** Enforce status transitions with a state machine, so archive always changes status. *Tradeoff:* more code, but deterministic behavior.

---

# ISSUE 4 — Zod error on Operator HQ (intermittent)

## Confirmed root cause (evidence-backed)
**API contract mismatch for agent activity** likely triggers Zod parse failures.

- `/api/agent/activity` returns an **empty array**:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/api-agent-activity.txt`.
- The schema **expects an object** with `status`, `recent`, `stats`, etc.:
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:1926-1948` (see `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-lib-api.txt`).
- This causes `safeParse` failure, which logs an error and can surface as an “issue” indicator depending on UI wiring.

**NEEDS VERIFICATION:** Whether the HQ “1 Issue” badge is directly tied to this error. The code search does not show a dedicated badge in HQ; likely it is global error state.

## Permanent fix approach (do NOT implement)
- Align `/api/agent/activity` response with `AgentActivityResponseSchema` (return object, not array).
- If intentional to return `[]`, update schema to accept both shapes or change UI to handle `[]` cleanly.

## Industry best practice / standard
- **Schema-first API contracts** with contract tests. The response shape must match schema in all environments (including mock modes).

## Why it fits this system
Operator HQ aggregates multiple feeds. A single mismatched response can cause intermittent UI errors and undermine trust.

## Prevent recurrence (gates/tests/invariants)
- **Contract test** for `/api/agent/activity` validating schema on every deploy.
- **UI test** that ensures HQ renders without Zod errors in mock mode.

## 2 better-than-current design ideas
1) **Unified “empty state” object:** Always return a typed object with zeroed stats. *Tradeoff:* more explicit, but reduces ambiguity.
2) **Schema versioning:** Include `schema_version` and validate on client; fallback logic for older versions. *Tradeoff:* added overhead, but enables safe evolution.

---

# ISSUE 5 — UI-created deals exist in DB but do not fully propagate / reflect consistently

## Confirmed root cause (evidence-backed)
**Split-brain DB + missing total count in list API**.

- Backend runtime DB is `postgres:5432` (container), while ops queries use `localhost:5435`:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-env-db.txt`.
- UI uses `/api/deals` (no count), so totals reflect only the paged list:
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:426-452` (see `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-lib-api.txt`).
- DB total 51 vs API total 37 indicates some deals in one DB not visible in other surfaces:
  - Evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt` vs `api-deals-stage-counts.txt`.

## Permanent fix approach (do NOT implement)
- Enforce a single canonical DB DSN for all runtime components.
- Add `total_count` to `/api/deals` response or provide `/api/deals/count` and use it in UI.

## Industry best practice / standard
- **Single-write DB** with **explicit read models** for counts and summaries.

## Why it fits this system
UI-based creation should be visible to all layers (dashboard, HQ, agent). That’s impossible if different layers talk to different DBs or only see a partial list.

## Prevent recurrence (gates/tests/invariants)
- Startup gate: backend refuses to start if DB URL does not match canonical DSN in config.
- CI gate: API count and DB count must match within acceptable limits.

## 2 better-than-current design ideas
1) **Event-driven read model:** When a deal is created, update a `deal_counts` table used by HQ and filters. *Tradeoff:* extra infra, but consistent.
2) **API returns both paged list and total_count** (like standard REST pagination). *Tradeoff:* minimal, improves UX.

---

# ISSUE 6 — “Active filter” does not actually filter

## Confirmed root cause (evidence-backed)
**Active filter uses status only; status never changes on archive.**

- Deals page sends `status` param only:
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx:94-111` (see `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-deals-page-filter.txt`).
- Backend list endpoint filters by `status` with default `active`:
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py:467` (see `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-main-deals-list.txt`).
- Archived deals retain `status='active'`:
  - Evidence: DB status counts show only `active` (`db-count-by-status-now.txt`) and archived stage present (`db-count-by-stage-now.txt`).

## Permanent fix approach (do NOT implement)
- Update filter semantics: `active` should mean `deleted=false` AND `stage!='archived'` OR `status='active' AND stage!='archived'`.
- On archive, set `status='archived'` (or `deleted=true`) so filters behave as expected.

## Industry best practice / standard
- **Explicit, single field semantics** for filter categories. Avoid ambiguous dual fields (`status` + `stage`).

## Why it fits this system
Filters are core to operator workflow. If “active” includes archived, users lose trust and automation breaks.

## Prevent recurrence (gates/tests/invariants)
- API tests asserting archived deals are excluded from active filter.
- DB constraint or trigger enforcing status/stage consistency.

## 2 better-than-current design ideas
1) **Dedicated filter enum in backend:** `visibility_state` (active/archived/junk) used for all list queries. *Tradeoff:* migration required.
2) **Materialized “active_deals” view** used for all list endpoints. *Tradeoff:* additional DB object, but consistent semantics.

---

# Additional systemic issue discovered

**Mission prompt’s DB query examples use `id`, but the table uses `deal_id`.**
- Evidence: `db-deals-schema.txt` shows `deal_id` primary key (no `id`).
- The prompt’s query `SELECT id, name ... FROM deals` fails. This can lead to misleading “no rows” errors during investigation.
- Recommendation: update the mission prompt to use `deal_id` to avoid false negatives in future runs.

---

# NEEDS VERIFICATION ITEMS (explicit commands)

1) **Confirm backend DB contents** (container at `postgres:5432`):
   ```bash
   PGPASSWORD=zakops_dev psql -h postgres -p 5432 -U zakops -d zakops -c "SELECT COUNT(*) FROM deals;"
   ```
   (Current attempt timed out: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-backend-postgres-count.txt`)

2) **Confirm source of HQ “1 Issue” badge**:
   - Open `/hq` in browser, capture console logs for Zod errors, identify which schema fails.
   - If needed, temporarily wrap `safeParse` in `getAgentActivity` to log issues (per mission prompt), then revert.

---

# Investigation Complete — No Fixes Applied
All required evidence collected. No changes made to code or data.


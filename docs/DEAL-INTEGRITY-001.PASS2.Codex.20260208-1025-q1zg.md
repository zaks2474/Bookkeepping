# Agent Identity
agent_name: Codex
run_id: 20260208-1025-q1zg
timestamp: 2026-02-08T10:25:00-06:00
repo_revision: agent-api=5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a; backend=444dff682885a7358767aa378759ffc9fbedf609

# DEAL-INTEGRITY-001 — PASS 2 CROSS-REVIEW + DEDUPLICATION

## 1) Deduped Issue Registry

### DI-ISSUE-001 — Split-brain DB / divergent data sources (counts + propagation)
**Merged root cause statement:** Multiple Postgres instances and inconsistent DSNs cause different services and operators to read/write different databases, yielding inconsistent deal counts (e.g., 37 vs 49/51) and “missing” UI-created deals in other surfaces.

**Evidence pointers (all agents):**
- Codex: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-env-db.txt` (backend DSN uses `postgres:5432`), `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-total-count-now.txt` (51 on localhost:5435), `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/api-deals-stage-counts.txt` (API returns 37).
- CloudCode (T160103Z): `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-001/evidence/00-forensics/db-total-count.txt` (49), `api-deals-unfiltered.txt` (37), `db-deleted-flag.txt` (deleted split).
- CloudCode (0500): summary in `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001.PASS1.CloudCode.20260208-0500-pass1.md` citing ports 5432 vs 5435 and counts 49/51.

**Merged permanent fix approach (no implementation):**
- Establish a single canonical DSN and enforce it across backend, agent, RAG, and ops scripts.
- Remove or quarantine the rogue DB (mark read-only or stop container) once canonical DSN confirmed.
- Add an authoritative count endpoint (`/api/deals/count` or `total_count` in list response) so UI doesn’t infer totals from paginated lists.

**Merged best-practice standard:**
- SSOT database per environment; all read models derived from canonical DB or consistent replicas.
- API list endpoints return `total_count` to avoid pagination-based count drift.

**Why it fits ZakOps:**
ZakOps is multi-layer (dashboard → backend → agent). Any DSN mismatch breaks counts, pipeline, and propagation. Evidence shows it’s already happening.

**Never-again enforcement (gates/tests/invariants):**
- Startup gate: backend refuses to start if DSN ≠ canonical DSN.
- CI/ops check: `/health` reports DB identity; must match operator’s psql DSN.
- Contract invariant: `/api/deals/count == /api/pipeline/stats.total_active_deals`.

**Merged innovation ideas (unique):**
- **DB identity tagging** (meta table + response header): shows DB instance ID in every API response. (Codex)
- **Count ledger/materialized view** updated on writes for instant counts. (CloudCode 0500 + Codex)
- **Secrets manager / env injection** to prevent DSN drift. (CloudCode 0500)

---

### DI-ISSUE-002 — Lifecycle state conflation (status vs stage vs deleted)
**Merged root cause statement:** Archive semantics are split across `status`, `stage`, and `deleted` without a state machine. Archive endpoint only sets `stage='archived'`, leaving `status='active'` and `deleted=false`, so archived deals appear in “active” filters and counts.

**Evidence pointers (all agents):**
- CloudCode (T160103Z): `db-distinct-statuses.txt` (only `active`), `db-archived-stage-deals.txt` (archived-stage deals), archive handler SQL (`main.py:881-884`).
- Codex: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-count-by-status-now.txt` (all active), `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/backend-main-archive-handlers.txt` (archive sets stage only).
- CloudCode (0500): summary and evidence refs in pass1 report.

**Merged permanent fix approach:**
- Make archive transition atomic: update `status` (or `deleted`) alongside `stage`.
- Enforce invariants via DB constraint/trigger or state machine helper.

**Merged best-practice standard:**
- Single authoritative lifecycle field or FSM with explicit transitions; avoid overlapping fields with no enforced relationship.

**Why it fits ZakOps:**
All downstream surfaces (API, HQ, filters, pipeline) depend on “active vs archived.” Conflation causes cross-surface drift.

**Never-again enforcement:**
- DB constraint: `stage='archived' ⇒ status='archived' OR deleted=true`.
- API test: `GET /api/deals?status=active` excludes archived stage.
- State transition function or trigger invoked by all endpoints.

**Merged innovation ideas (unique):**
- **Lifecycle_state enum** with backfill and derived fields. (CloudCode T160103Z)
- **Event-sourced lifecycle** with materialized current state. (CloudCode T160103Z)
- **Soft-delete tombstone** via `deleted_at` rather than mixed fields. (CloudCode T160103Z)

---

### DI-ISSUE-003 — Pipeline totals mismatch (header vs stage sums)
**Merged root cause statement:** HQ totals are derived from all deals, but pipeline stage totals omit `archived` (and `junk`) stages. This creates header counts larger than the sum of visible stage cards.

**Evidence pointers:**
- Codex: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-hq-page.txt` shows PIPELINE_STAGES excludes archived/junk; `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/api-deals-stage-counts.txt` shows archived count.
- CloudCode (T160103Z): `api-pipeline-summary.txt` shows archived=6; `hq/page.tsx` excludes archived; header uses deals.length.

**Merged permanent fix approach:**
- Use backend pipeline summary as the single source for stage counts and totals; ensure totals match displayed stages.
- Or include archived/junk in pipeline display if they are counted in totals.

**Merged best-practice standard:**
- Server-side aggregation for pipeline metrics; client renders, does not recalc.

**Why it fits ZakOps:**
ZakOps already has `/api/pipeline/summary`; duplicating counting in UI introduces drift.

**Never-again enforcement:**
- Contract test: `sum(stages) == total_active` (or explicitly define exclusions) in `/api/pipeline` response.

**Merged innovation ideas:**
- **Shared stage config** module between backend and UI. (CloudCode T160103Z)
- **Backend-driven pipeline config** endpoint. (CloudCode T160103Z)
- **Faceted counts UI** (active/archived counts). (CloudCode T160103Z)

---

### DI-ISSUE-004 — Zod error on Operator HQ (intermittent)
**Merged root cause statement:** HQ data fetches have inconsistent response shapes and error handling. Candidate triggers include: (a) `Promise.all` with no per-call error boundaries (CloudCode T160103Z), (b) `/api/agent/activity` returns `[]` while schema expects an object (Codex), and (c) archived deals leaking into active lists (CloudCode 0500 hypothesis). Root cause requires verification to isolate the actual failing schema.

**Evidence pointers:**
- Codex: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/api-agent-activity.txt` (returns `[]`), schema expects object in `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-lib-api.txt` (AgentActivityResponseSchema).
- CloudCode (T160103Z): `hq/page.tsx` uses Promise.all without per-call boundaries; `getQuarantineQueue` safeParse errors logged in `api.ts` (see pass1 report).
- CloudCode (0500): suggests archived deals missing fields might cause Zod failures (hypothesis).

**Merged permanent fix approach:**
- Align `/api/agent/activity` response to schema or adjust schema to accept array/empty object.
- Use `Promise.allSettled` and per-widget error boundaries in HQ.

**Merged best-practice standard:**
- Schema-first API contracts with contract tests; dashboards isolate failures per widget.

**Why it fits ZakOps:**
Operator HQ aggregates multiple sources; one bad schema should not poison the entire page.

**Never-again enforcement:**
- Contract tests for `/api/agent/activity`, `/api/actions/quarantine`, and HQ pipeline response.
- UI test that HQ renders with mock/empty data without Zod errors.

**Merged innovation ideas:**
- **Unified empty-state object** for agent activity. (Codex)
- **Schema versioning** for evolving API shapes. (Codex)
- **Suspense/error boundaries per widget** (CloudCode T160103Z)

---

### DI-ISSUE-005 — Active filter does not filter (semantic no-op)
**Merged root cause statement:** UI filter sends `status=active` and backend filters by status, but status is always `active` (never changed on archive), so the filter is effectively a no-op. Filter options also don’t map to real DB status values.

**Evidence pointers:**
- Codex: deals page uses status param `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/dashboard-deals-page-filter.txt`; DB status all active `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/db-count-by-status-now.txt`.
- CloudCode (T160103Z): `db-distinct-statuses.txt` only active; `deals/page.tsx` status filter values don’t align with data.

**Merged permanent fix approach:**
- Redefine “active” filter to exclude archived/junk; add archived option; add stage filter.
- Update backend list to accept composite filters (status + stage).

**Merged best-practice standard:**
- User-facing filters should match user mental model (active/archived/by-stage) not raw schema fields.

**Why it fits ZakOps:**
Operators expect filters to reflect pipeline stages and archive status. Current filters are misleading.

**Never-again enforcement:**
- Contract test: status filter returns only expected lifecycle states.
- UI test: archived deal never appears in active filter.

**Merged innovation ideas:**
- **Facet filter with counts** (active/archived by stage). (CloudCode T160103Z)
- **Composite filter API** (`lifecycle=active&stage=screening`). (CloudCode 0500)

---

### DI-ISSUE-006 — Bonus: `audit_trail` column referenced but missing
**Merged root cause statement:** Backend references `audit_trail` column in code but schema doesn’t include it, creating latent runtime errors.

**Evidence pointers:**
- CloudCode (T160103Z): references in `main.py` and `db-deals-schema.txt` missing column.

**Merged permanent fix approach:**
- Add column via migration or remove references. (Decision required.)

**Merged best-practice standard:**
- Schema/code parity enforced by migration gates.

**Why it fits ZakOps:**
Schema drift causes intermittent failures and undermines contract gating.

**Never-again enforcement:**
- CI check: search for references to non-existent columns; run migration assertion.

**Merged innovation ideas:**
- **Schema diff gate**: compare ORM/SQL models to live schema and fail on mismatch.

---

### DI-ISSUE-007 — Bonus: `/api/actions/kinetic` returns 500
**Merged root cause statement:** Endpoint returns 500; not used by UI today but indicates incomplete backend.

**Evidence pointers:**
- CloudCode (T160103Z) bonus finding.

**Merged permanent fix approach:**
- Investigate endpoint; either implement or remove and update docs to prevent confusion.

**Merged best-practice standard:**
- No dead endpoints; every endpoint is tested and documented.

**Why it fits ZakOps:**
Unreliable endpoints complicate ops and debugging during incident response.

**Never-again enforcement:**
- API health suite must validate all documented endpoints.

**Merged innovation ideas:**
- **Endpoint contract inventory** with automated “unused endpoint” detection.

---

## 2) Conflicts & Uncertainties

1) **DB total counts conflict (49 vs 51)**
   - CloudCode (T160103Z) reports 49 total on DB-5432; Codex reports 51 on DB-5435.
   - Resolution command: `PGPASSWORD=zakops_dev psql -h postgres -p 5432 -U zakops -d zakops -c "SELECT COUNT(*) FROM deals;"` and `PGPASSWORD=changeme psql -h localhost -p 5435 -U dealengine -d zakops -c "SELECT COUNT(*) FROM deals;"`.

2) **Cause of HQ “1 Issue” badge**
   - Competing hypotheses: Promise.all failure (CloudCode), agent activity schema mismatch (Codex), archived deals missing fields (CloudCode 0500).
   - Resolution: open `/hq`, capture console errors and Zod safeParse output, identify schema failure source.

3) **Backend DB accessibility from host**
   - Connection to `postgres:5432` timed out from host. Needs environment/network confirmation.
   - Resolution: run query inside backend container or via docker exec to confirm counts.

---

## 3) What’s the One Systemic Root Cause?

**Answer:** ZakOps lacks a single source of truth for both **storage** (multiple DBs) and **lifecycle semantics** (status/stage/deleted). These two systemic failures combine to produce all observed symptoms: inconsistent counts, pipeline mismatch, archived leakage into active views, and perceived propagation failures.

**Proof:**
- Storage split: backend DSN uses `postgres:5432` while operator DB queries target `localhost:5435` (Codex evidence); counts diverge 37 vs 51/49.
- Lifecycle split: archive updates only `stage`, leaving `status='active'` and `deleted=false`, so archived appears active (CloudCode + Codex evidence).

Without resolving both, any UI or API patch is cosmetic.

---

## Appendix: Evidence File Map
- Codex evidence: `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/`
- CloudCode evidence: `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-001/evidence/00-forensics/`


# DEAL-INTEGRITY-001 PASS 1 REPORT

agent_name: CloudCode
run_id: 20260208-0500-pass1
timestamp: 2026-02-08T05:00:00Z
repo_revision: unknown
mission_path_used: /home/zaks/bookkeepping/doc/MISSION-DEAL-INTEGRITY-001.DM

## 1. Executive Summary

The "Deal Integrity" crisis is caused by a convergence of three distinct failures: **Data Model Ambiguity**, **Split-Brain Infrastructure**, and **Pipeline Visualization Gaps**.

1.  **Data Model Ambiguity:** The concept of "Archived" is conflated between `stage` and `status`. Deals are moved to `stage='archived'` but remain `status='active'`. The API's default `status=active` filter therefore leaks archived deals into the active view.
2.  **Pipeline Gap:** The Operator HQ sums the counts of visible pipeline columns (Inbound, Screening, etc.) but excludes the "Archived" column. Since archived deals are technically "active" (per the DB), they are counted in the Header Total but missing from the Column Sums, causing the math error (37 header vs 31 columns).
3.  **Split-Brain Infrastructure:** Two distinct PostgreSQL instances are running simultaneously (`port 5432` vs `port 5435`). The main Backend API uses 5432 (49 deals), but legacy/infra containers use 5435 (51 deals). This explains the "ghost deals" and fluctuating counts (50 vs 37).

## 2. Issues & Root Causes

### Issue 1: Deal Counts Disagree (37 vs 31 vs 49 vs 51)
**Root Cause:**
*   **37 (API/UI):** The API filters `deleted=FALSE`. There are 37 non-deleted deals in DB-5432.
*   **31 (Pipeline Sum):** The UI sums visible columns. 37 active deals minus 6 `stage='archived'` deals = 31. The "Archived" stage is hidden from the pipeline board but included in the "Active" total.
*   **49 (Agent/DB):** The raw DB-5432 has 49 rows. 12 are `deleted=TRUE`. Agents querying raw SQL (or RAG indexes built from raw SQL) see 49.
*   **51 (Rogue DB):** A second Postgres container (`zakops-postgres` on port 5435) exists with 51 stale deals. Some services/tools may be connecting here.

**Evidence:**
*   `db-real-total-count.txt`: 49 rows in DB-5432.
*   `db-real-deleted-counts.txt`: 37 false, 12 true.
*   `api-pipeline-summary.txt`: Sum of counts = 37.

**Fix Approach:**
1.  **Kill Rogue DB:** Stop and remove the container on port 5435.
2.  **Unified Count:** Ensure all "Active" counts explicitly exclude `stage='archived'` OR ensure "Archived" deals have `status='archived'`.

**Better Idea:** Implement a **Materialized View** for stats that is refreshed on every write, serving as the single source of truth for all counts.

---

### Issue 2: Archived Deals Appear in "Active" Filter
**Root Cause:**
The "Archive" action performs `UPDATE deals SET stage='archived'` but leaves `status='active'`.
The API's `list_deals` endpoint defaults to filtering `status='active'`.
Therefore, deals in the "archived" stage are returned in the "active" list.

**Evidence:**
*   `db-real-status-x-stage.txt`: 6 deals have `status='active'` AND `stage='archived'`.
*   `api-deals-active-filter.txt`: Returns 37 deals (includes the 6 archived ones).

**Fix Approach:**
1.  **Data Migration:** `UPDATE deals SET status='archived' WHERE stage='archived' AND status='active';`
2.  **Code Fix:** Update the Archive handler to set `status='archived'`.

**Better Idea:** **State Machine Enforcement**. Use a library like `transitions` or a DB Trigger that automatically sets `status='archived'` whenever `stage` transitions to `archived`.

---

### Issue 3: Zod Error on Operator HQ
**Root Cause:**
The HQ page likely expects deals to have specific fields populated (e.g., `next_action`, `priority`) that are mandatory for active deals but missing/null for archived deals. Since archived deals leak into the active view (Issue 2), they crash the Zod schema validation for the "Active Deals" list.

**Evidence:**
*   `zod-parse-locations.txt`: Confirmed heavy Zod usage on deal lists.
*   The error is intermittent (depends on whether archived deals are loaded/rendered).

**Fix Approach:**
1.  **Filter Fix:** Fixing Issue 2 (removing archived deals from active view) will likely resolve this by stopping the bad data from reaching the UI.
2.  **Schema Loosening:** Make non-critical fields `.nullable()` or `.optional()` in the Zod schema to be resilient to malformed data.

**Better Idea:** **Contract Tests**. A CI job that runs the Zod schema against the *actual* database rows to detect schema drift before deployment.

---

### Issue 4: UI-Created Deals "Do Not Propagate"
**Root Cause:**
**Split Brain.** Deals created via the Dashboard (Port 3003 -> API 8091) go to DB-5432.
If the Agent (or RAG ingestion) is connected to DB-5435 (as hinted by the 51 count), it will NEVER see the new deals.
RAG ingestion likely reads from the wrong DB or is broken/stale.

**Evidence:**
*   `docker ps`: Shows two Postgres containers (ports 5432 and 5435).
*   `db-recent-deals.txt` vs `api-deals-unfiltered.txt`: Disjoint sets of deal IDs.

**Fix Approach:**
1.  **Consolidate Config:** Force all services (Backend, Agent, RAG) to use the EXACT same `DATABASE_URL`.
2.  **Nuke Rogue:** Delete the extra container.

**Better Idea:** **Service Discovery / Env Injection**. Use a secrets manager (e.g., Doppler/Vault) to inject the *single* correct DB URL into all containers at runtime, preventing config drift.

---

### Issue 5: "Active Filter" Does Not Filter
**Root Cause:**
As detailed in Issue 2, the filter works technically (`WHERE status='active'`), but the *data* is wrong (Archived deals are marked active). It is a semantic failure, not a code failure.

**Fix Approach:**
(Same as Issue 2)

**Better Idea:** **Filter Composition**. The API should accept complex filters like `filter={status: 'active', stage: {neq: 'archived'}}` to allow precise frontend control.

---

## 3. Implementation Plan (Pass 2 Input)

**Phase 1: Infrastructure Unification (The "Kill" Phase)**
1.  Stop all services.
2.  Kill `zakops-postgres` (5435).
3.  Verify only `zakops-backend-postgres-1` (5432) remains.
4.  Update all `.env` and `docker-compose` files to point ONLY to 5432.

**Phase 2: Data Cleanup (The "Heal" Phase)**
1.  Run SQL migration: `UPDATE deals SET status='archived' WHERE stage='archived';`.
2.  Run SQL migration: `UPDATE deals SET deleted=TRUE` for any known test data (optional).

**Phase 3: Logic Correction (The "Code" Phase)**
1.  Backend: Update `archive_deal` handler to set `status='archived'`.
2.  Backend: Update `delete_deal` handler to set `deleted=TRUE` (Soft Delete).
3.  Backend: Ensure `GET /api/deals` default filter excludes `archived` status.

**Phase 4: Pipeline Alignment (The "View" Phase)**
1.  Update `/hq` Logic: Ensure `Active Deals` count matches the sum of *displayed* columns.
2.  Either show "Archived" column or subtract them from the header total.

## 4. Verification

*   **Count Invariant:** `DB(status='active')` == `API(len)` == `UI(Header)`.
*   **Split-Brain Check:** Create deal in UI -> Check `psql` -> Check Agent tool `list_deals`. All must match.

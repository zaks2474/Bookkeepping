# DEAL-INTEGRITY-001.PASS2.CloudCode.20260208-1700-pass2.md

## 1. AGENT IDENTITY
- **agent_name:** CloudCode
- **run_id:** 20260208-1700-pass2
- **timestamp:** 2026-02-08T17:00:00Z
- **repo_revision:** 444dff6 (backend), 5eb7ce6 (agent-api)

## 2. DEDUPED ISSUE REGISTRY

| ID | Issue | Root Cause | Fix Approach | Sources |
|---|---|---|---|---|
| **DI-ISSUE-001** | **Split-Brain Database** | Two Postgres instances running (5432 vs 5435). Backend uses 5432 (49 deals); Ops/Legacy uses 5435 (51 deals). | **Infrastructure Unification:** Kill container on 5435. Force all env vars to 5432. | CloudCode, Codex |
| **DI-ISSUE-002** | **Archived Deals in Active View** | `archive` endpoint sets `stage='archived'` but leaves `status='active'`. API filters `status='active'`, leaking archived deals. | **State Machine Fix:** Update `archive` to set `status='archived'`. Backfill existing data. | CloudCode, Codex |
| **DI-ISSUE-003** | **Pipeline Sum Mismatch** | Header counts all non-deleted (37). Pipeline cards exclude 'archived' stage (6). 37 - 6 = 31. | **Pipeline Alignment:** Exclude `stage='archived'` from "Active Deals" header count OR show Archived card. | CloudCode, Codex |
| **DI-ISSUE-004** | **Zod Error on HQ** | Schema mismatch on `/api/agent/activity` (returns `[]`, expects object) AND/OR malformed archived deals in active list. | **Schema Alignment:** Update Zod schema to handle `[]` or fix API to return object. | Codex, CloudCode |
| **DI-ISSUE-005** | **"Active" Filter Broken** | Filter uses `status` column, which is universally `'active'`. | **Semantic Filter:** Implement "Active" = `status='active' AND stage != 'archived'`. | CloudCode, Codex |
| **DI-ISSUE-006** | **UI Creation Propagation** | UI writes to DB-5432. Agent/RAG likely reads from DB-5435 (Rogue) or is stale. | **Unified DB:** Resolving DI-ISSUE-001 fixes this. | CloudCode |

---

## 3. ISSUE DEEP DIVES & RECOMMENDATIONS

### DI-ISSUE-001: Split-Brain Database
*   **Root Cause:** `docker-compose` configuration drift. `infra/docker/docker-compose.yml` spins up a separate DB on 5435.
*   **Evidence:** `docker ps` shows both. Queries return different counts.
*   **Fix:** `docker stop <container_id_5435>`. Update `infra/docker/docker-compose.yml` to use external network or remove it.
*   **Enforcement:** Startup check in Backend that verifies it is talking to the *canonical* DB (e.g. check for a specific sentinel row or config).

### DI-ISSUE-002: Archived Deals in Active View
*   **Root Cause:** "Partial Transition". Archive logic updates 1 of 3 state fields.
*   **Fix:** Update `routers/deals.py` archive handler to set `status='archived'`. Run migration `UPDATE deals SET status='archived' WHERE stage='archived'`.
*   **Best Practice:** **Finite State Machine**. Define valid transitions and side effects in one place.
*   **Innovation:** **Computed Column**. `is_active GENERATED ALWAYS AS (status = 'active' AND stage != 'archived') STORED`. Index it. Query it.

### DI-ISSUE-003: Pipeline Sum Mismatch
*   **Root Cause:** Client-side filtering logic divergence. Header = Raw API count. Columns = Filtered list.
*   **Fix:** Update `/hq` to subtract `deals.filter(d => d.stage === 'archived').length` from the header count.
*   **Innovation:** **Server-Side Aggregation**. `/api/pipeline/summary` already exists. Use it for the header count too.

### DI-ISSUE-004: Zod Error on HQ
*   **Root Cause:** `AgentActivityResponseSchema` expects `{ items: [...] }` but API returns `[...]`.
*   **Fix:** Update `api.ts` schema or Backend `main.py` response model.
*   **Enforcement:** **Contract Tests**. CI job that validates API responses against frontend schemas.

---

## 4. CONFLICTS & UNCERTAINTIES
*   **Agent Activity Schema:** CloudCode suspected data shape (null fields), Codex identified structure mismatch (array vs object). Codex's finding is more specific and actionable.
*   **Resolution:** Verify `/api/agent/activity` response format with `curl`. If array, update Zod schema to `z.array(...)` or wrap in object.

---

## 5. THE ONE SYSTEMIC ROOT CAUSE
**Lifecycle State Fragmentation.**
The concepts of "Active", "Archived", and "Deleted" are spread across three uncoordinated fields (`status`, `stage`, `deleted`) and multiple databases. There is no single definition of "Active Deal".
*   **Fix:** Unify on **Lifecycle State** (Active/Archived/Deleted) and enforce it at the Database level (Constraints/Triggers) and Infrastructure level (Single DB).

---

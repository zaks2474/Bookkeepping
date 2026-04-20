AGENT IDENTITY
- agent_name: Gemini-CLI
- agent_version: 1.0
- run_id: 20260204-0028-gemini
- repo_revision: unknown
- date_time: 2026-02-04T00:28:00Z

# ZakOps Deal Lifecycle: Forensic Assessment

## Executive Summary
The system currently suffers from a critical **Split-Brain Architecture**. The Dashboard and API operate on a PostgreSQL database (`zakops.deals`), while the Agentic automation (specifically `DEAL.CREATE_FROM_EMAIL`) operates on a file-based JSON registry (`deal_registry.json`). 

There is **no active synchronization** between these two worlds. A deal created by an agent will **not** appear in the dashboard. A deal created in the dashboard will **not** be known to the agent's legacy file-based tools.

## Canonical Deal Data Model (As Implemented)

### The Split Reality
The definition of a "Deal" depends entirely on which part of the system you ask.

#### 1. The API/Dashboard View (PostgreSQL)
*   **Source of Truth:** `zakops.deals` table.
*   **Key Fields:**
    *   `deal_id` (PK, string)
    *   `canonical_name` (string)
    *   `stage` (enum string)
    *   `status` (string: active, archived, etc.)
    *   `identifiers` (JSONB)
    *   `company_info` (JSONB)
    *   `broker` (JSONB)
*   **Access:** Read/Written by `zakops-backend/src/api/orchestration/main.py`.

#### 2. The Agent/Executor View (File System)
*   **Source of Truth:** `/home/zaks/DataRoom/.deal-registry/deal_registry.json`.
*   **Key Fields:** Matches the DB structure (dataclass `Deal` in `scripts/deal_registry.py`), but persisted as a giant JSON blob.
*   **Access:** Read/Written by `scripts/deal_registry.py` and `zakops-backend/src/actions/executors/deal_create_from_email.py`.

## Deal State Machine
**Implemented in:** `zakops-backend/src/core/deals/workflow.py` (and duplicated in `scripts/deal_state_machine.py`).

**Stages:**
`inbound` → `screening` → `qualified` → `loi` → `diligence` → `closing` → `portfolio`
                ↓           ↓         ↓         ↓          ↓
              `junk` ←──────←──────←──────←──────←──────←──────┘
                ↓
            `archived`

**Transitions:**
*   Enforced by `DealWorkflowEngine.transition_stage` in the backend.
*   Records events to `zakops.deal_events`.
*   **ASCII Flow:**
    ```text
    [Inbound] --> [Screening] --> [Qualified] --> [LOI] --> [Diligence] --> [Closing]
       |             |               |             |            |
       v             v               v             v            v
    [Junk]        [Junk]          [Junk]        [Junk]       [Junk]
       |
       v
    [Archived]
    ```

## End-to-End "Deal Story" (The Broken Narrative)

1.  **Ingestion:** Email arrives. `ingestion_gateway` writes to `zakops.quarantine_items` (Postgres).
    *   *Status:* **Works**.
2.  **Review:** User views item in Dashboard. Calls `POST /api/quarantine/{id}/process`.
    *   *Status:* **Works** (updates status to 'approved').
3.  **Creation (The Gap):**
    *   **Expectation:** Approval creates a deal.
    *   **Reality:** `process_quarantine` **DOES NOT** insert into `zakops.deals`. It just updates the quarantine item. The user is expected to manually create the deal or provide an existing `deal_id`.
4.  **Automation (The Split):**
    *   If the `DEAL.CREATE_FROM_EMAIL` executor is triggered (e.g. by a background worker or chat command):
        *   It imports `scripts/deal_registry.py` (via a `sys.path` hack).
        *   It writes the deal to `deal_registry.json`.
        *   It creates the folder structure in `DataRoom/`.
        *   **CRITICAL FAILURE:** It does **not** write to `zakops.deals`. The Dashboard remains unaware of this new deal.

## Scenarios & Edge Cases

| Scenario | Implementation Status | Evidence |
| :--- | :--- | :--- |
| **New deal enters quarantine** | **PARTIALLY IMPLEMENTED** | `api/orchestration/main.py::create_quarantine_item` writes to DB. |
| **Quarantine Approve -> Deal Create** | **BROKEN** | `api/orchestration/main.py::process_quarantine` updates status but skips deal creation. |
| **Duplicate Detection** | **PARTIALLY IMPLEMENTED** | `DealMatcher` logic exists in code but runs against JSON registry, not DB. |
| **Agent creates deal** | **SPLIT-BRAIN** | `deal_create_from_email.py` writes to JSON/Files, ignores DB. |
| **Dashboard creates deal** | **PARTIALLY IMPLEMENTED** | `POST /api/deals` writes to DB, but **does not create folders**. |
| **Split-Brain Risk** | **CONFIRMED** | API uses DB; Agents use JSON. They do not talk. |

## Brutally Honest Gap Analysis

### GAP-001: Split-Brain Persistence (P0)
*   **Evidence:** `zakops-backend/src/actions/executors/deal_create_from_email.py` lines 145-155 import legacy `DealRegistry` which writes to JSON. `api/orchestration/main.py` writes to Postgres.
*   **Impact:** Deals created by agents are invisible to the Dashboard. Deals created by Dashboard are invisible to Agents.
*   **Remediation:** Rewrite `DealRegistry` to use SQLModel/SQLAlchemy and point it to `zakops.deals`. Remove `deal_registry.json`.

### GAP-002: Manual Quarantine Cliff (P1)
*   **Evidence:** `api/orchestration/main.py`'s `process_quarantine` function.
*   **Impact:** Approving an email does nothing but change a flag. No deal is created, no workflow is triggered.
*   **Remediation:** Orchestrate the flow: On "Approve", implicitly call `create_deal` (DB) AND trigger `DEAL.CREATE_FROM_EMAIL` (Folders).

### GAP-003: Folderless Dashboard Deals (P1)
*   **Evidence:** `POST /api/deals` inserts a row but performs no file system operations.
*   **Impact:** Deals created in the UI have no DataRoom folders.
*   **Remediation:** Trigger a background job on deal creation to scaffold the folder structure.

## Comparison to Prior Assessment

*   **Confirmed:** "The two quarantine systems don't talk" - Confirmed. The `ingestion_gateway` now writes to DB (good), but the downstream actions revert to file-based logic (bad).
*   **Confirmed:** "Database deal vs DataRoom deal are NOT synchronized."
*   **New Finding:** The "Path B" executor explicitly uses a `sys.path` hack to load legacy scripts, actively enforcing the split-brain architecture.

## Verification Plan

**1. Verify Split-Brain:**
```bash
# 1. Create deal via API
curl -X POST http://localhost:9200/api/deals -d '{"canonical_name": "API Deal", "stage": "inbound"}'
# 2. Check DB
psql -c "SELECT * FROM zakops.deals WHERE canonical_name = 'API Deal'"
# 3. Check JSON Registry (Expected: NOT FOUND)
grep "API Deal" /home/zaks/DataRoom/.deal-registry/deal_registry.json
```

**2. Verify Quarantine Dead End:**
```bash
# 1. Approve item
curl -X POST http://localhost:9200/api/quarantine/{id}/process -d '{"action": "approve"}'
# 2. Check for new deal (Expected: 0 new deals)
psql -c "SELECT count(*) FROM zakops.deals"
```

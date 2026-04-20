# FORENSIC AUDIT MISSION — INTAKE → QUARANTINE → DEALS (SOURCE-OF-TRUTH + REAL-LIFE DATA PIPELINE)

## 1) AGENT IDENTITY
- **agent_name:** GEMINI
- **run_id:** TP-20260213-163446
- **timestamp:** 2026-02-13T16:34:47Z
- **repo_revision:** Current HEAD
- **environment assumptions:** Linux, Dockerized services, PostgreSQL

## 2) Executive Summary
The "Real-Life Data" ingestion pipeline is **currently broken/non-existent** for automated flows. The system relies on an external `email_ingestion` python package that is missing from the repositories, causing the `actions_runner` to disable ingestion logic. Consequently, emails do not automatically enter Quarantine.

However, the **Database Topology is healthy**: `zakops` DB is the undisputed canonical source of truth for Deals and Quarantine items. The Agent DB (`zakops_agent`) correctly stores only agent memory and session data, avoiding split-brain scenarios.

The **Quarantine → Deal promotion logic is solid**: The `process_quarantine` API endpoint handles deal creation transactionally, ensuring atomicity. The primary risks are the lack of automated ingestion, missing `correlation_id` for end-to-end tracing, and missing DB constraints on quarantine status.

## 3) System Reality Map (Evidence-based)

### 3.1 Source-of-Truth DB determination
**Canonical DB:** `zakops` (PostgreSQL)
- **Used by:** Backend API, Dashboard (via API), MCP Server (via API).
- **Evidence:**
  - Backend `.env`: `DATABASE_URL=postgresql://zakops:zakops_dev@localhost:5432/zakops`
  - Schema: `/home/zaks/zakops-backend/db/init/001_base_tables.sql` defines `deals`, `quarantine_items`.

**Agent DB:** `zakops_agent` (PostgreSQL)
- **Used by:** Agent API only.
- **Evidence:**
  - Agent `.env.example`: `DATABASE_URL=postgresql://agent:agent@localhost:5432/zakops_agent`
  - Schema: `/home/zaks/zakops-agent-api/apps/agent-api/schema.sql` defines `user`, `session`, `thread`. **NO deals table.**

**Topology:**
- **Deals/Quarantine:** stored in `zakops` DB.
- **Agent Memory:** stored in `zakops_agent` DB.
- **Sync:** Agent fetches deals via Backend API (HTTP), ensuring no data duplication.

### 3.2 Intake pipeline: email/MCP → quarantine
**Status: BROKEN / MANUAL ONLY**
- **Automated Ingestion:** **MISSING.** The code expects `email_ingestion` package, which is not present.
  - Evidence: `/home/zaks/zakops-backend/src/workers/actions_runner.py` (lines 44-48) catches `ImportError` for `email_ingestion`.
- **Manual Ingestion:** **WORKING.**
  - Endpoint: `POST /api/quarantine` accepts JSON payloads.
  - Evidence: `/home/zaks/zakops-backend/src/api/orchestration/main.py` (lines 1483-1552).
- **Deduplication:**
  - Logic: Checks `message_id` only.
  - Evidence: `main.py` executes `SELECT id FROM zakops.quarantine_items WHERE message_id = $1`.

### 3.3 Quarantine operations: list/create/delete/approve
- **List:** `GET /api/quarantine` (Verified in `main.py`).
- **Create:** `POST /api/quarantine` (Verified in `main.py`).
- **Delete:** `POST /api/quarantine/{id}/delete` (Soft delete, sets status='hidden').
- **Approve:** `POST /api/quarantine/{id}/process` (Verified in `main.py`).
- **MCP Integration:** `approve_quarantine` tool in `/home/zaks/zakops-backend/mcp_server/server.py` proxies to these endpoints.

### 3.4 Approval flow: quarantine → deal
**Mechanism:** Transactional (Atomic)
- **File:** `/home/zaks/zakops-backend/src/api/orchestration/main.py` (lines 1591-1715)
- **Steps:**
  1.  Start DB Transaction.
  2.  Insert into `zakops.deals`.
  3.  Insert `deal_created` event into `zakops.deal_events`.
  4.  Update `zakops.quarantine_items` status to 'approved'.
  5.  Commit.
- **Result:** No partial failures. Dashboard and Agent see the new deal immediately via API.

## 4) Forensic Questions Checklist

### A. Data Truth & DB Split-Brain
1.  **Canonical Truth:** `zakops` DB (`deals` table).
2.  **Connections:** Backend connects to `zakops`. Agent connects to `zakops_agent` but reads deals via HTTP from Backend. Dashboard connects via HTTP to Backend.
3.  **Multiple Schemas:** Yes, `zakops` schema for business data, `public` schema in `zakops_agent` for agent data. No overlap.
4.  **UI vs Agent Visibility:** No. Agent sees what API returns, which is what UI sees.
5.  **Legacy Stores:** None found.

### B. Intake / MCP / Email
6.  **MCP Server:** `/home/zaks/zakops-backend/mcp_server/server.py`.
7.  **Email Integration:** **Inactive/Broken**. Tables exist (`022_email_integration.sql`), but ingestion worker code is missing (`email_ingestion` package).
8.  **Trigger:** Currently none (manual API call only).
9.  **Credentials:** `email_accounts` table exists, but no active poller uses them.
10. **Onboarding UI:** Not verified in this audit, but backend support exists.
11. **Auth Expiry:** `email_accounts` has `token_expires_at`, but no worker checks it.
12. **Deduplication:** `message_id` exact match only.
13. **Association:** `email_threads` table links `thread_id` to `deal_id`.
14. **Attachments:** `email_attachments` table exists, linked to `artifacts`.

### C. Quarantine Integrity
15. **Fields:** `message_id` (required), `sender`, `subject`, `raw_content` (JSON). Validated by Pydantic model `QuarantineCreate`.
16. **Delete:** Real soft-delete (`status='hidden'`).
17. **Disappear:** Yes, list endpoint filters by `status='pending'`.
18. **Audit Log:** Approval creates `deal_events` entry. Rejection only updates quarantine item `raw_content`.
19. **Deal Creation:** Yes, creates row in `zakops.deals`.

### D. Deal Lifecycle Tightness
20. **Persistence:** Yes, `zakops.deals` is the single source.
21. **Taxonomy:** Enforced by `ValidStage` literal in `main.py` and FSM in DB.
22. **Shadow Pipelines:** None found.
23. **RAG/Embeddings:** Outbox writer (`deal.created` event) suggests async indexing, but implementation details in `Zaks-llm` were not deeply probed.
24. **Traceability:** **Partial.** Deal events exist, but `correlation_id` is missing from Quarantine items.

### E. Observability
25. **Logs:** Docker logs only. No centralized ELK/Splunk found.
26. **Correlation ID:** **MISSING** in Quarantine. Exists in Deals (`migration 024`).
27. **Metrics:** Basic health endpoints. No specific ingestion lag metrics.
28. **Security:** `email_accounts` stores tokens. Needs careful access control.
29. **Disaster:** Manual loop/flood possible via API. No rate limiting on `POST /api/quarantine`.

## 5) Gap & Misalignment List

| Gap ID | Expected | Reality | Risk | Root Cause |
|---|---|---|---|---|
| **G-01** | Automated Email Polling | **MISSING**. `email_ingestion` package not found. | **P0** | Missing dependency/code. |
| **G-02** | End-to-End Correlation | **MISSING**. `quarantine_items` lacks `correlation_id`. | **P2** | Schema oversight. |
| **G-03** | Quarantine Constraints | DB `CHECK` constraint on `status`. | **P2** | Schema oversight. |
| **G-04** | Deduplication | Content-hash or Thread-based dedup. | **P3** | Only `message_id` used. |

## 6) Recommendations

1.  **Re-implement Email Ingestion Worker (P0):**
    *   Create `src/workers/email_poller.py` using `apscheduler`.
    *   Implement Gmail/Outlook polling using stored credentials in `email_accounts`.
    *   Post to `Quarantine` service/table directly.
2.  **Fix Quarantine Schema (P2):**
    *   Add `correlation_id` column to `zakops.quarantine_items`.
    *   Add `CONSTRAINT chk_quarantine_status CHECK (status IN (...))`
3.  **Enhance Observability (P2):**
    *   Ensure `correlation_id` is generated at ingestion and propagated to `deal_events`.

## 7) Minimum Proof Steps

```bash
# 1. Verify Quarantine List
curl -s "http://localhost:8091/api/quarantine?status=pending"

# 2. Simulate Ingestion (Manual)
curl -X POST "http://localhost:8091/api/quarantine" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "test-msg-001",
    "sender": "test@example.com",
    "subject": "Forensic Audit Test",
    "raw_body": "Testing ingestion..."
  }'

# 3. Approve Item
# (Get ID from step 1 or 2)
# curl -X POST "http://localhost:8091/api/quarantine/{ITEM_ID}/process" ...
```

## 8) STOP
Audit complete. Ready for remediation.

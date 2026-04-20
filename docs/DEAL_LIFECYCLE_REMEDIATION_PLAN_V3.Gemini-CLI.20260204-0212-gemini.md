AGENT IDENTITY
- agent_name: Gemini-CLI
- run_id: 20260204-0212-gemini
- date_time: 2026-02-04T02:12:00Z
- repo_revision: unknown

# ZakOps Deal Lifecycle: V3 Remediation & Implementation Plan

## 1. Executive Summary

**Current Status:** Critical Fracture.
The ZakOps system currently operates as two disconnected islands:
1.  **The Dashboard Island:** Powered by the Orchestration API and Postgres DB. It sees "Deals" as database rows. It has no files.
2.  **The Agent Island:** Powered by legacy scripts and JSON files. It sees "Deals" as folders on disk. It ignores the DB.

**The Fix:** Unification.
We will aggressively deprecate the JSON registry and file-based state. We will unify all truth into the `zakops` PostgreSQL database. We will force all components (Dashboard, Agent, Scripts) to speak to the Orchestration API.

**Top Priorities (P0):**
1.  **Kill Split-Brain:** Migrate all JSON deals to Postgres. Rewire `DealRegistry` class to be a DB wrapper.
2.  **Enable Ingestion:** Turn on the email pipeline cron job (but only AFTER it points to the DB).
3.  **Bridge the Quarantine Gap:** Make "Approve" transactionally create a deal in the DB *and* scaffold folders.

## 2. Decision Set

### D1: Source of Truth
*   **Recommendation:** **PostgreSQL Only**.
*   **Why:** We cannot have atomic transactions or reliable reporting with split JSON/DB state.
*   **Migration:** One-way sync script `json_to_postgres.py`. Once run, `deal_registry.json` becomes read-only archival.
*   **Proof:** `grep "deal_registry.json"` in codebase returns 0 hits (excluding migration scripts).

### D2: Agent Tooling Contract
*   **Recommendation:** **API-First**.
*   **Why:** Agents currently bypass logic by editing files. This breaks the state machine.
*   **Rule:** Agent tools (`deal_tools.py`) must call `http://localhost:8091/api/...` for ALL mutations. No direct DB access. No direct file writes for metadata.
*   **Proof:** Tools code contains `requests.post` and no `open(..., 'w')`.

### D3: Email Ingestion Architecture
*   **Recommendation:** **Database-Backed Pipeline**.
*   **Design:**
    1.  Poll Gmail → `zakops.quarantine_items` (DB).
    2.  User Approves → `zakops.deals` (DB) + `DataRoom` (Folder Scaffolding).
    3.  Ingestion script acts as a *client* to the internal API, not a direct file writer.
*   **Proof:** `process_quarantine` endpoint transactionally updates 3 tables.

### D4: Auth Model
*   **Recommendation:** **API Key Service-to-Service + User Sessions**.
*   **Design:**
    *   Dashboard → Backend: Passes `X-User-ID` header (initially trusted from internal network, later JWT).
    *   Agent → Backend: Uses `X-API-Key` (system account).
*   **Proof:** `curl` without header returns 401/403.

## 3. Phased Implementation Plan

### Phase 0: Stop the Bleeding (Immediate)
**Objective:** Prevent new data corruption and enable observability.
*   [ ] **P0** (ZK-ISSUE-0002) Enable email ingestion cron job (dry-run mode only).
*   [ ] **P1** (ZK-ISSUE-0020) Fix SSE endpoint to return 200 OK (even if empty) to stop UI polling errors.
*   [ ] **P1** (ZK-ISSUE-0010) Add startup check for RAG service connectivity.

### Phase 1: Data Truth Unification (The Big Rewrite)
**Objective:** Eliminate `deal_registry.json` and legacy scripts.
*   [ ] **P0** (ZK-ISSUE-0001) Create `scripts/migrations/migrate_json_to_postgres.py`.
    *   *Logic:* Read JSON, upsert to `zakops.deals`, map aliases to `zakops.deal_aliases`.
*   [ ] **P0** (ZK-ISSUE-0014) Rewrite `CreateDealFromEmailExecutor` to use `zakops.deals` DB via SQLModel or API.
    *   *Constraint:* MUST NOT import `scripts/deal_registry.py`.
*   [ ] **P1** (ZK-ISSUE-0008) Port SQLite actions to Postgres `zakops.actions`.

### Phase 2: Workflow Repair (Connecting the Wires)
**Objective:** Make "Approve" actually work.
*   [ ] **P1** (ZK-ISSUE-0003) Update `POST /api/quarantine/{id}/process`.
    *   *New Logic:* If `action=approve`, insert into `zakops.deals` (if new) OR link existing.
*   [ ] **P1** (ZK-ISSUE-0004) Add filesystem scaffolding hook.
    *   *Trigger:* On `zakops.deals` insert (via API), dispatch async task `scaffold_deal_folders`.
*   [ ] **P1** (ZK-ISSUE-0006) Fix Dashboard API client to use `/process` instead of `/resolve`.

### Phase 3: Dashboard & API Hardening
**Objective:** Make the UI reliable and secure.
*   [ ] **P1** (ZK-ISSUE-0005) Add Basic Auth / API Key middleware to Dashboard Next.js app.
*   [ ] **P2** (ZK-ISSUE-0018) Add `.passthrough()` to all Dashboard Zod schemas to prevent silent empty views.
*   [ ] **P1** (ZK-ISSUE-0007) Enforce canonical `DealStage` enum in API validation layer.

### Phase 4: Agent & Automation Upgrade
**Objective:** Give the Agent hands.
*   [ ] **P2** (ZK-ISSUE-0009) Implement `create_deal` tool (wraps `POST /api/deals`).
*   [ ] **P2** (ZK-ISSUE-0019) Wire up `deal_extract_email_artifacts` executor to the "Deal Created" event.
*   [ ] **P2** (ZK-ISSUE-0015) Implement `cron/expire_approvals.py` job.

### Phase 5: Legacy Decommission
**Objective:** Clean up the mess.
*   [ ] **P2** Delete `deal_registry.json` and `scripts/deal_registry.py`.
*   [ ] **P2** Delete `ingest_state.db` (SQLite).
*   [ ] **P2** Remove `deal_lifecycle` legacy API module.

## 4. No-Drop Coverage Matrix

| Issue ID | Phase | Task | Verification | Done? |
| :--- | :--- | :--- | :--- | :--- |
| ZK-ISSUE-0001 | Phase 1 | Run JSON->DB migration; Rewrite Executor | `grep "deal_registry.json"` returns 0 | [ ] |
| ZK-ISSUE-0002 | Phase 0 | Enable cron with logging | `tail -f /home/zaks/logs/email_sync.log` | [ ] |
| ZK-ISSUE-0003 | Phase 2 | Update `/process` logic | Approve item -> `SELECT * FROM deals` | [ ] |
| ZK-ISSUE-0004 | Phase 2 | Add folder scaffold hook | Create API deal -> `ls DataRoom/...` | [ ] |
| ZK-ISSUE-0005 | Phase 3 | Add Middleware | `curl` dashboard -> 401 | [ ] |
| ZK-ISSUE-0006 | Phase 2 | Update UI API client | UI Resolution -> Success (200) | [ ] |
| ZK-ISSUE-0007 | Phase 3 | Update Pydantic models | Invalid stage -> 422 Error | [ ] |
| ZK-ISSUE-0008 | Phase 1 | Migrate SQLite->Postgres | `SELECT count(*) FROM actions` | [ ] |
| ZK-ISSUE-0009 | Phase 4 | Register `create_deal` tool | Agent: "Create deal X" -> Success | [ ] |
| ZK-ISSUE-0010 | Phase 0 | Add RAG health check | Agent startup logs "RAG OK" | [ ] |
| ZK-ISSUE-0011 | Phase 4 | Add `correlation_id` col | `SELECT * FROM audit WHERE corr_id=...` | [ ] |
| ZK-ISSUE-0012 | Phase 2 | Add `/note` endpoint | `POST /note` -> 201 Created | [ ] |
| ZK-ISSUE-0013 | Phase 3 | Implement capability endpoints | `GET /capabilities` -> JSON | [ ] |
| ZK-ISSUE-0014 | Phase 1 | Remove `sys.path` hack | Code review `deal_create_from_email.py` | [ ] |
| ZK-ISSUE-0015 | Phase 4 | Add expiry cron | Check stale approvals count = 0 | [ ] |
| ZK-ISSUE-0016 | Phase 3 | Add DB Constraint | Insert dupe -> SQL Error | [ ] |
| ZK-ISSUE-0017 | Phase 5 | Define Policy | Doc exists; Cron scheduled | [ ] |
| ZK-ISSUE-0018 | Phase 3 | Fix Zod schemas | UI shows fields correctly | [ ] |
| ZK-ISSUE-0019 | Phase 4 | Register Executors | Dashboard "Actions" tab populated | [ ] |
| ZK-ISSUE-0020 | Phase 0 | Stub SSE Endpoint | Dashboard console no 501s | [ ] |
| ZK-ISSUE-0021 | Backlog | Design Scheduler | Scheduler Design Doc | [ ] |
| ZK-ISSUE-0022 | Phase 2 | Add Archive endpoints | `POST /archive` -> Success | [ ] |

## 5. Verification & QA Plan

### Gate A: Code Health
*   Run `pytest` on all modified backend modules.
*   Ensure `mypy` passes (no import errors from deleted legacy modules).

### Gate B: End-to-End Proof
**Command:**
```bash
# 1. Simulate inbound email
python -m email_ingestion.inject_test_email "Teaser: SuperSaaS Co"
# 2. Verify Quarantine DB
psql -c "SELECT id FROM zakops.quarantine_items WHERE subject='Teaser: SuperSaaS Co'"
# 3. Approve via API (simulate UI)
curl -X POST .../api/quarantine/{id}/process -d '{"action": "approve"}'
# 4. Verify Deal DB
psql -c "SELECT deal_id FROM zakops.deals WHERE canonical_name='SuperSaaS Co'"
# 5. Verify Folders
ls -d /home/zaks/DataRoom/00-PIPELINE/Inbound/SuperSaaS*
```

**Success Criteria:**
*   Steps 1-5 complete without manual intervention.
*   Deal appears in Dashboard UI.
*   Folders exist on disk.

## 6. Legacy Decommission Plan

**Delete these paths after Phase 5:**
*   `/home/zaks/DataRoom/.deal-registry/deal_registry.json`
*   `/home/zaks/DataRoom/.deal-registry/ingest_state.db`
*   `/home/zaks/scripts/deal_registry.py`
*   `zakops-backend/src/api/deal_lifecycle/` (entire folder)

**Proof of Death:**
```bash
grep -r "deal_registry.json" .
# Should return 0 results
```

## 7. Prioritized Backlog

*   **P2 (Medium):** Implement "Smart Classification" for incoming emails using local LLM to pre-fill quarantine fields.
*   **P3 (Low):** Build "Portfolio View" for deals in `portfolio` stage with monthly KPI tracking.
*   **P3 (Low):** Add "Deal Export" to Zip file for external sharing.

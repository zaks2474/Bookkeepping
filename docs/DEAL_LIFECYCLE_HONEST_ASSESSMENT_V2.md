# ZakOps Deal Lifecycle: Consolidated Issues Register (V2)

**Date:** 2026-02-04
**Status:** Consolidated from 3 Independent Forensic Assessments
**Version:** V2 (All Known Issues Register)

---

## Executive Summary (Top P0/P1 Issues)

| ID | Severity | Title | Reported By |
|----|----------|-------|-------------|
| ZK-ISSUE-0001 | **P0** | Split-brain persistence (Postgres vs JSON vs DataRoom) | All 3 agents |
| ZK-ISSUE-0002 | **P0** | Email ingestion pipeline disabled in production | Claude |
| ZK-ISSUE-0003 | **P1** | Quarantine approval does not create deal | All 3 agents |
| ZK-ISSUE-0004 | **P1** | Dashboard deals do not create DataRoom folders | Gemini, Claude |
| ZK-ISSUE-0005 | **P1** | Dashboard has no authentication | Claude |
| ZK-ISSUE-0006 | **P1** | Dashboard uses wrong quarantine endpoint | Codex |
| ZK-ISSUE-0007 | **P1** | Stage taxonomy conflicts across components | Codex, Gemini |
| ZK-ISSUE-0008 | **P1** | Actions system split (Postgres vs SQLite) | Codex |

---

## All Known Issues Register

---

### ZK-ISSUE-0001: Split-Brain Persistence (Postgres vs JSON vs DataRoom)

**Severity:** P0 (Critical)

**Category:** db, orchestration, legacy

**Description:**
The system has THREE separate deal tracking systems that do not automatically synchronize:
1. PostgreSQL `zakops.deals` — Backend API's source of truth (DL-XXXX IDs)
2. JSON `deal_registry.json` — Email ingestion and legacy executor's source of truth (DEAL-YYYY-### IDs)
3. Filesystem DataRoom folders — Document storage (arbitrary folder names)

Deals created via the API/Dashboard exist only in Postgres. Deals created by the `DEAL.CREATE_FROM_EMAIL` executor exist only in JSON/DataRoom. They never sync.

**Evidence References:**
- `zakops-backend/db/init/001_base_tables.sql:zakops.deals`
- `zakops-backend/src/core/deal_registry.py:Deal`
- `zakops-backend/src/actions/executors/deal_create_from_email.py` (lines 145-155 import legacy DealRegistry)
- `/home/zaks/DataRoom/.deal-registry/deal_registry.json`
- `zakops-backend/src/api/deal_lifecycle/main.py:get_registry`

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Backend uses `zakops.deals` with DL-XXXX IDs. Email ingestion uses `deal_registry.json` with DEAL-YYYY-### IDs. No sync mechanism between them." |
| Gemini-CLI | 20260204-0028-gemini | "API/Dashboard reads/writes PostgreSQL (`zakops.deals`), while Agent Executors read/write `deal_registry.json`. They are completely disconnected." |
| Codex | 20260204-003640-02b34c | "A parallel, legacy Deal exists in the DataRoom JSON registry and is used by the legacy deal_lifecycle API and some action executors; this is separate from Postgres." |

**Suggested Remediation:**
1. Choose single source of truth (recommend: Postgres `zakops.deals`)
2. Rewrite `DealRegistry` to use SQLModel/SQLAlchemy pointing to `zakops.deals`
3. Deprecate `deal_registry.json`
4. Add sync/migration job if needed

**Verification Method:**
```bash
# Create deal via API
curl -X POST http://localhost:8091/api/deals -d '{"canonical_name": "API Deal", "stage": "inbound"}'
# Check JSON Registry (Expected: NOT FOUND)
grep "API Deal" /home/zaks/DataRoom/.deal-registry/deal_registry.json
```

**Needs Verification:** No

---

### ZK-ISSUE-0002: Email Ingestion Pipeline Disabled

**Severity:** P0 (Critical)

**Category:** orchestration, email

**Description:**
The email ingestion pipeline exists and is sophisticated (triage, enrichment, quarantine), but the cron job to run it is NOT ACTIVE. No emails are being processed into quarantine items. Manual deal creation is the only path.

**Evidence References:**
- No active cron job in `/etc/cron.d/`
- `SELECT COUNT(*) FROM zakops.quarantine_items` returns 0
- `/home/zaks/scripts/email_ingestion/` (code exists)
- `/home/zaks/.config/email_sync.env` (credentials file)
- `/home/zaks/logs/email_sync.log` (log location)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "No active cron job in `/etc/cron.d/`. `SELECT COUNT(*) FROM zakops.quarantine_items` returns 0." |

**Suggested Remediation:**
1. Enable cron job: `5 6-21 * * * zaks cd /home/zaks/scripts/email_ingestion && make ingest`
2. Verify IMAP credentials in `/home/zaks/.config/email_sync.env`
3. Test with `--dry-run` first
4. Monitor `/home/zaks/logs/email_sync.log`

**Verification Method:**
```bash
cat /etc/cron.d/dataroom-automation 2>/dev/null || echo "No cron file"
cd /home/zaks/scripts/email_ingestion && python -m email_ingestion.cli --dry-run --days 1
```

**Needs Verification:** No

---

### ZK-ISSUE-0003: Quarantine Approval Does Not Create Deal

**Severity:** P1 (High)

**Category:** ui-backend wiring, orchestration

**Description:**
When a user approves a quarantine item via Dashboard, `POST /api/quarantine/{id}/process` only updates the status field to 'approved'. It does NOT create a deal record in `zakops.deals`. Creating a deal requires a separate manual action.

The `CreateDealFromEmailExecutor` exists and can create deals (with folders), but it is not wired to the quarantine approval flow.

**Evidence References:**
- `zakops-backend/src/api/orchestration/main.py:process_quarantine` (status update only)
- `zakops-backend/src/actions/executors/deal_create_from_email.py:CreateDealFromEmailExecutor` (exists but disconnected)
- `apps/dashboard/src/app/api/actions/quarantine/route.ts` (proxies to backend)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "`POST /api/quarantine/{id}/process` only updates status. `CreateDealFromEmailExecutor` exists but not triggered." |
| Gemini-CLI | 20260204-0028-gemini | "`process_quarantine` **DOES NOT** insert into `zakops.deals`. It just updates the quarantine item." |
| Codex | 20260204-003640-02b34c | "`/api/quarantine/{id}/process` marks status approved/rejected and optionally sets `deal_id` only; it does not create a deal." |

**Suggested Remediation:**
1. Wire `POST /api/quarantine/{id}/process` with `action=approve` to trigger `deal.create_from_email` action
2. Or: Add atomic approve endpoint that creates deal and writes to `zakops.deals`
3. Or: Add "Create Deal" button to quarantine approval dialog
4. Test end-to-end flow

**Verification Method:**
```bash
# Approve item
curl -X POST http://localhost:8091/api/quarantine/{id}/process -d '{"action": "approve"}'
# Check for new deal (Expected: 0 new deals)
psql -c "SELECT count(*) FROM zakops.deals"
```

**Needs Verification:** No

---

### ZK-ISSUE-0004: Dashboard Deals Do Not Create DataRoom Folders

**Severity:** P1 (High)

**Category:** ui-backend wiring, filesystem

**Description:**
When a deal is created via `POST /api/deals` (Dashboard path), it inserts a row in `zakops.deals` but performs NO filesystem operations. The deal has no DataRoom folder structure (01-NDA/, 02-CIM/, etc.).

Conversely, deals created by the `CreateDealFromEmailExecutor` create the folder structure but don't write to Postgres.

**Evidence References:**
- `zakops-backend/src/api/orchestration/main.py:create_deal` (DB insert only)
- `zakops-backend/src/actions/executors/deal_create_from_email.py` (creates folders)
- `/home/zaks/DataRoom/00-PIPELINE/` (folder location)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Gemini-CLI | 20260204-0028-gemini | "`POST /api/deals` inserts a row but performs no file system operations. Deals created in the UI have no DataRoom folders." |
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Creates deal with DL-XXXX ID. Inserts into `zakops.deals`. No folder structure created." |

**Suggested Remediation:**
1. Trigger a background job on deal creation to scaffold the folder structure
2. Or: When deal created in DB, create folder structure via post-commit hook
3. Sync `deal_profile.json` ↔ `zakops.deals` metadata

**Verification Method:**
```bash
# Create deal via API
curl -X POST http://localhost:8091/api/deals -d '{"canonical_name": "Test Corp", "stage": "inbound"}'
# Check for folder (Expected: NOT FOUND)
ls /home/zaks/DataRoom/00-PIPELINE/Inbound/Test*
```

**Needs Verification:** No

---

### ZK-ISSUE-0005: Dashboard Has No Authentication

**Severity:** P1 (High)

**Category:** auth, security

**Description:**
The Dashboard proxies requests to the backend without any user authentication. Next.js rewrites forward requests directly, trusting the internal network. Anyone on the network can access all deals. No user attribution for changes.

**Evidence References:**
- Next.js rewrites in dashboard configuration
- No user session management code
- `apps/dashboard/src/middleware.ts` (injects API key for writes, but no user auth)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Next.js rewrites forward requests directly. No user session management. Trusts internal network." |

**Suggested Remediation:**
1. Add authentication middleware to dashboard
2. Pass user ID in requests to backend
3. Implement RBAC

**Verification Method:**
```bash
# Access dashboard without auth (Expected: should succeed - BAD)
curl -s http://localhost:3003/api/deals | jq 'length'
```

**Needs Verification:** No

---

### ZK-ISSUE-0006: Dashboard Uses Wrong Quarantine Endpoint

**Severity:** P1 (High)

**Category:** ui-backend wiring, endpoints

**Description:**
The Dashboard UI calls `/api/quarantine/{id}/resolve` for quarantine resolution, but the active backend (orchestration API) only exposes `/api/quarantine/{id}/process`. The `/resolve` endpoint exists only in the legacy `deal_lifecycle` API which is not running.

This means quarantine resolution from the UI likely returns 404.

**Evidence References:**
- `apps/dashboard/src/lib/api.ts:resolveQuarantineItem` (calls `/api/quarantine/{id}/resolve`)
- `zakops-backend/src/api/orchestration/main.py:process_quarantine` (only `/process` exists)
- `zakops-backend/src/api/deal_lifecycle/main.py:resolve_quarantine` (legacy, not running)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Codex | 20260204-003640-02b34c | "Dashboard calls legacy `/api/quarantine/{id}/resolve` while orchestration exposes `/api/quarantine/{id}/process`." |

**Suggested Remediation:**
1. Update Dashboard UI to call `/api/quarantine/{id}/process`
2. Or: Implement `/resolve` alias in orchestration API that forwards to `/process`

**Verification Method:**
```bash
# Test legacy endpoint (Expected: 404)
curl -X POST http://localhost:8091/api/quarantine/test-id/resolve
```

**Needs Verification:** Yes (test if Dashboard actually fails)

---

### ZK-ISSUE-0007: Stage Taxonomy Conflicts Across Components

**Severity:** P1 (High)

**Category:** orchestration, legacy, db

**Description:**
Multiple conflicting stage taxonomies exist in the codebase:
1. Active backend (`workflow.py`): `inbound, screening, qualified, loi, diligence, closing, portfolio, junk, archived`
2. DB constraint (`023_stage_check_constraint.sql`): Same as workflow.py
3. Legacy `deal_state_machine.py`: `new_deal, in_review, qualified, negotiation, contract_signed, closed_won, closed_lost`
4. DB default stage is `lead` (NOT in allowed list)
5. `DealRegistry` comments list `archive, rejected` (not in canonical list)

**Evidence References:**
- `zakops-backend/src/core/deals/workflow.py:DealStage`
- `zakops-backend/db/migrations/023_stage_check_constraint.sql:chk_deals_stage`
- `/home/zaks/scripts/deal_state_machine.py:DealStage`
- `zakops-backend/db/init/001_base_tables.sql:zakops.deals` (default `lead`)
- `zakops-backend/src/core/deal_registry.py:Deal` (comments)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Codex | 20260204-003640-02b34c | "Stage taxonomy conflicts across workflow (lead/qualified/proposal/negotiation/won/lost) vs scripts deal_state_machine vs DB default `lead`." |
| Gemini-CLI | 20260204-0028-gemini | "Implemented in `workflow.py` (and duplicated in `scripts/deal_state_machine.py`)." |

**Suggested Remediation:**
1. Align all stage enums and defaults to canonical list
2. Remove/retire legacy `deal_state_machine.py`
3. Fix DB default from `lead` to `inbound`

**Verification Method:**
```bash
# Check for stage conflicts
grep -r "DealStage" /home/zaks/zakops-backend/src/ /home/zaks/scripts/
```

**Needs Verification:** No

---

### ZK-ISSUE-0008: Actions System Split (Postgres vs SQLite)

**Severity:** P1 (High)

**Category:** db, orchestration, legacy

**Description:**
The actions system is split between two databases:
1. Orchestration API uses `zakops.actions` table (Postgres)
2. Action engine uses SQLite database at `ZAKOPS_STATE_DB` (`/home/zaks/DataRoom/.deal-registry/ingest_state.db`)

Actions created/executed by the engine may not appear in the UI or DB metrics.

**Evidence References:**
- `zakops-backend/src/api/orchestration/main.py:list_actions` (Postgres)
- `zakops-backend/src/actions/engine/store.py:SCHEMA_SQL` (SQLite)
- `zakops-backend/src/actions/engine/store.py:_default_state_db_path`

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Codex | 20260204-003640-02b34c | "Orchestration API uses `zakops.actions` (Postgres); action engine uses SQLite `ZAKOPS_STATE_DB`." |

**Suggested Remediation:**
1. Consolidate actions into Postgres
2. Or: Migrate action engine to use `zakops.actions`

**Verification Method:**
```sql
-- Check Postgres actions
SELECT COUNT(*) FROM zakops.actions;
-- Check SQLite actions
sqlite3 /home/zaks/DataRoom/.deal-registry/ingest_state.db "SELECT COUNT(*) FROM actions;"
```

**Needs Verification:** No

---

### ZK-ISSUE-0009: Agent Cannot Create Deals

**Severity:** P2 (Medium)

**Category:** agent tools

**Description:**
The agent has only three deal-related tools: `get_deal`, `search_deals`, `transition_deal`. There is no `create_deal` tool. The agent cannot automate deal discovery or creation.

**Evidence References:**
- `apps/agent-api/app/core/langgraph/tools/deal_tools.py` (only 3 tools exported)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Only tools: `get_deal`, `search_deals`, `transition_deal`. `create_deal` not registered. Intentional limitation for safety." |

**Suggested Remediation:**
1. Add `create_deal` tool with HITL approval requirement
2. Or: Keep as manual-only (policy decision)

**Verification Method:**
```bash
grep -r "def create_deal" /home/zaks/zakops-agent-api/apps/agent-api/
```

**Needs Verification:** No

---

### ZK-ISSUE-0010: RAG Search Integration Unverified

**Severity:** P2 (Medium)

**Category:** agent tools, observability

**Description:**
The `search_deals` tool depends on RAG REST service at port 8052. The RAG service status is unknown ("pool=null at boot" note in service catalog). Deal search may fail silently.

**Evidence References:**
- `apps/agent-api/app/core/langgraph/tools/deal_tools.py:search_deals` (calls `http://host.docker.internal:8052/rag/query`)
- Service catalog note about RAG pool=null at boot

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Tool calls `POST http://host.docker.internal:8052/rag/query`. RAG service status unknown." |
| Codex | 20260204-003640-02b34c | "Partial failure: downstream RAG service down causes `search_deals` errors; no fallback when `ALLOW_TOOL_MOCKS` false." |

**Suggested Remediation:**
1. Verify RAG service running: `curl http://localhost:8052/health`
2. Index existing deals into RAG
3. Add health check to agent startup

**Verification Method:**
```bash
curl http://localhost:8052/health
```

**Needs Verification:** Yes

---

### ZK-ISSUE-0011: No Event Correlation Between Agent and Backend

**Severity:** P2 (Medium)

**Category:** observability, audit

**Description:**
Backend events (`zakops.deal_events`) and agent audit logs (`zakops_agent.audit_log`) are stored in separate databases with no shared `correlation_id` linking them. Cannot trace agent action → backend change.

**Evidence References:**
- `zakops.deal_events` (backend DB)
- `zakops_agent.audit_log` (agent DB)
- No shared correlation_id field

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "`zakops.deal_events` captures backend changes. `zakops_agent.audit_log` captures agent actions. No shared `correlation_id` linking them." |

**Suggested Remediation:**
1. Pass `trace_id` from agent through to backend
2. Store `correlation_id` in both systems
3. Build unified audit view

**Verification Method:**
```sql
-- Check for correlation_id columns
\d zakops.deal_events
\d audit_log  -- in agent DB
```

**Needs Verification:** No

---

### ZK-ISSUE-0012: Deal Notes Endpoint Mismatch

**Severity:** P2 (Medium)

**Category:** endpoints, ui-backend wiring

**Description:**
The Dashboard UI calls `/api/deals/{id}/note` for adding deal notes, but the orchestration API does not define this endpoint. It exists only in the legacy `deal_lifecycle` API which is not running.

**Evidence References:**
- `apps/dashboard/src/lib/api.ts:addDealNote` (calls `/api/deals/{id}/note`)
- `zakops-backend/src/api/deal_lifecycle/main.py:add_deal_note` (legacy, not running)
- `zakops-backend/src/api/orchestration/main.py` (no note endpoint)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Codex | 20260204-003640-02b34c | "UI calls `/api/deals/{id}/note` (legacy) but orchestration API does not define it; deal_lifecycle API does." |

**Suggested Remediation:**
1. Add `/api/deals/{id}/note` to orchestration API
2. Or: Update UI to use new endpoint if one exists

**Verification Method:**
```bash
# Test endpoint (Expected: 404 or 405)
curl -X POST http://localhost:8091/api/deals/DL-0001/note -d '{"content": "test"}'
```

**Needs Verification:** Yes

---

### ZK-ISSUE-0013: Actions Capabilities/Metrics Not Implemented

**Severity:** P2 (Medium)

**Category:** endpoints, orchestration

**Description:**
The endpoints `/api/actions/capabilities` and `/api/actions/metrics` return HTTP 501 (Not Implemented). The Actions UI has limited functionality and cannot show capability metadata.

**Evidence References:**
- `zakops-backend/src/api/orchestration/main.py:get_action_capabilities` (returns 501)
- `zakops-backend/src/api/orchestration/main.py:get_action_metrics` (returns 501)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Codex | 20260204-003640-02b34c | "`/api/actions/capabilities` and `/api/actions/metrics` return 501." |

**Suggested Remediation:**
1. Implement capability registry
2. Or: Provide static list wired to executors

**Verification Method:**
```bash
curl http://localhost:8091/api/actions/capabilities
curl http://localhost:8091/api/actions/metrics
```

**Needs Verification:** No

---

### ZK-ISSUE-0014: deal_create_from_email Uses sys.path Hack

**Severity:** P2 (Medium)

**Category:** legacy, code quality

**Description:**
The `CreateDealFromEmailExecutor` uses a `sys.path` hack to import the legacy `DealRegistry` from scripts, actively enforcing the split-brain architecture instead of using the Postgres database.

**Evidence References:**
- `zakops-backend/src/actions/executors/deal_create_from_email.py` (lines 145-155)
- `scripts/deal_registry.py` (imported via sys.path)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Gemini-CLI | 20260204-0028-gemini | "The 'Path B' executor explicitly uses a `sys.path` hack to load legacy scripts, actively enforcing the split-brain architecture." |

**Suggested Remediation:**
1. Refactor executor to write to Postgres `zakops.deals`
2. Remove sys.path hack
3. Or: Create proper Python package for shared code

**Verification Method:**
```bash
grep -n "sys.path" /home/zaks/zakops-backend/src/actions/executors/deal_create_from_email.py
```

**Needs Verification:** No

---

### ZK-ISSUE-0015: No Approval Expiry Background Job

**Severity:** P3 (Low)

**Category:** agent tools, orchestration

**Description:**
The `expires_at` field exists on approvals, but there is no background job to expire stale approvals. Expiry is checked only when an approval is accessed (lazy expiry). Stale approvals accumulate in queue.

**Evidence References:**
- `apps/agent-api/app/models/approval.py:Approval` (has `expires_at` field)
- `apps/agent-api/app/api/v1/agent.py` (lazy expiry check)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "`expires_at` field exists on approvals. No background job to expire them. Only checked when approval is accessed." |

**Suggested Remediation:**
1. Add background job to expire old approvals
2. Run every 5 minutes
3. Emit `APPROVAL_EXPIRED` audit event

**Verification Method:**
```sql
SELECT COUNT(*) FROM approvals WHERE expires_at < NOW() AND status = 'pending';
```

**Needs Verification:** No

---

### ZK-ISSUE-0016: Duplicate Deal Detection Not Implemented

**Severity:** P2 (Medium)

**Category:** orchestration, db

**Description:**
There is no automatic deduplication when creating deals via API. `POST /api/deals` has no duplicate check on `canonical_name`. The email ingestion has dedup via body_hash, but that operates on a different data store (SQLite/JSON).

**Evidence References:**
- `zakops-backend/src/api/orchestration/main.py:create_deal` (no duplicate check)
- `scripts/email_ingestion/` (has dedup but for emails, not deals)
- `zakops-backend/src/core/deal_registry.py:DealMatcher` (exists but for JSON registry)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "`POST /api/deals` has no duplicate check on `canonical_name`. Email ingestion has dedup via body_hash, but doesn't sync to backend." |
| Codex | 20260204-003640-02b34c | "Duplicate deal detection: PARTIALLY IMPLEMENTED. Quarantine deduplicates by `message_id`; legacy registry has alias matching; no DB-level duplicate deal detection." |

**Suggested Remediation:**
1. Add unique constraint or check on `canonical_name` in `zakops.deals`
2. Or: Add pre-insert duplicate check in create_deal endpoint

**Verification Method:**
```bash
# Create same deal twice (Expected: both succeed - BAD)
curl -X POST http://localhost:8091/api/deals -d '{"canonical_name": "Dupe Test", "stage": "inbound"}'
curl -X POST http://localhost:8091/api/deals -d '{"canonical_name": "Dupe Test", "stage": "inbound"}'
```

**Needs Verification:** No

---

### ZK-ISSUE-0017: No Retention/Cleanup Policy

**Severity:** P3 (Low)

**Category:** orchestration, db

**Description:**
There is no automated cleanup, archival policy, or retention management. Archived deals have `stage='archived'` but `deleted=FALSE`. Folders remain in DataRoom forever.

**Evidence References:**
- `zakops.deals` has `deleted` BOOLEAN column
- `workflow.py`: `ARCHIVED: []` (no transitions out)
- No scheduled cleanup job

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Retention Policy: **NOT IMPLEMENTED** — no automatic cleanup." |

**Suggested Remediation:**
1. Define retention policy (e.g., archive after X days in junk)
2. Add scheduled cleanup job
3. Consider moving old files to cold storage

**Verification Method:** N/A (policy decision)

**Needs Verification:** No

---

### ZK-ISSUE-0018: Dashboard Zod Schema Mismatch Can Hide Deals

**Severity:** P2 (Medium)

**Category:** ui-backend wiring

**Description:**
The Dashboard uses Zod `.safeParse()` on API responses. If the backend returns fields not matching the schema, safeParse returns empty results silently. Deals that exist in DB may not appear in UI due to schema drift.

**Evidence References:**
- Dashboard uses `.safeParse()` pattern
- Zod schemas in dashboard code

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Dashboard uses `.safeParse()` which returns empty on schema mismatch." |

**Suggested Remediation:**
1. Add `.passthrough()` to Zod schemas
2. Log parse failures for debugging
3. Keep schemas in sync with backend OpenAPI

**Verification Method:**
```bash
# Compare backend response fields with dashboard schema
curl http://localhost:8091/api/deals/DL-0001 | jq 'keys'
grep -A 20 "dealSchema" /home/zaks/zakops-agent-api/apps/dashboard/src/
```

**Needs Verification:** Yes

---

### ZK-ISSUE-0019: Action Executors Exist But Not Wired

**Severity:** P2 (Medium)

**Category:** orchestration, ui-backend wiring

**Description:**
Multiple action executors exist in code but are not wired into any UI or automated workflow:
- deal_append_email_materials.py
- deal_backfill_sender_history.py
- deal_dedupe_and_place_materials.py
- deal_enrich_materials.py
- deal_extract_email_artifacts.py
- analysis_build_valuation_model.py
- document_generate_loi.py
- presentation_generate_pitch_deck.py
- diligence_request_docs.py
- communication_send_email.py
- rag_reindex_deal.py

**Evidence References:**
- `zakops-backend/src/actions/executors/` directory
- `zakops-backend/src/actions/capabilities/` YAML specs

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "Status: These exist in code but are not wired into any UI or automated workflow." |
| Master File | N/A | "Action Executors That EXIST but Are Untested" |

**Suggested Remediation:**
1. Wire executors to dashboard actions
2. Add trigger points in quarantine approval flow
3. Add progress tracking

**Verification Method:**
```bash
ls /home/zaks/zakops-backend/src/actions/executors/
```

**Needs Verification:** No

---

### ZK-ISSUE-0020: SSE/WebSocket Events Not Implemented

**Severity:** P2 (Medium)

**Category:** observability, ui-backend wiring

**Description:**
There is no SSE/WebSocket push for real-time updates. Dashboard must poll or manually refresh to see changes. The SSE endpoint exists but returns 501.

**Evidence References:**
- `zakops-backend/src/api/orchestration/routers/events.py` (returns 501)
- No WebSocket implementation

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Master File | N/A | "NO SSE/WebSocket push (dashboard polls or manual refresh)" |

**Suggested Remediation:**
1. Implement SSE endpoint properly
2. Or: Add WebSocket support
3. Or: Document polling as intentional design

**Verification Method:**
```bash
curl http://localhost:8091/api/events/stream
```

**Needs Verification:** No

---

### ZK-ISSUE-0021: No Scheduling or Reminders

**Severity:** P2 (Medium)

**Category:** orchestration

**Description:**
No implementation for:
- Follow-up reminders
- Stage timeout warnings ("Deal in screening for 30 days")
- Scheduled actions
- SLA tracking

**Evidence References:**
- No scheduler code found
- No reminder/notification system

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Master File | N/A | "No implementation for: Follow-up reminders, Stage timeout warnings, Scheduled actions, SLA tracking" |
| Claude-Opus-4-5 | 20260204-0030-839ce03a | "No scheduling/reminders implemented" |

**Suggested Remediation:**
1. Add deal age tracking
2. Implement follow-up reminders
3. Email notifications for pending actions

**Verification Method:** N/A (feature not implemented)

**Needs Verification:** No

---

### ZK-ISSUE-0022: Orchestration API Archive/Restore Endpoints Missing

**Severity:** P3 (Low)

**Category:** endpoints, orchestration

**Description:**
The orchestration API lacks archive/restore endpoints. The DB has `deleted` flag but API has no endpoints to use it. Legacy API has these endpoints but is not running.

**Evidence References:**
- `zakops-backend/db/init/001_base_tables.sql:zakops.deals` (has `deleted` column)
- `zakops-backend/src/api/deal_lifecycle/main.py:archive_deal` (legacy, not running)
- `zakops-backend/src/api/orchestration/main.py` (no archive endpoint)

**Source Attribution:**
| Agent | Run ID | Quote |
|-------|--------|-------|
| Codex | 20260204-003640-02b34c | "DB has `deleted` flag but orchestration API lacks archive/restore endpoints; legacy API has archive/restore against JSON registry." |

**Suggested Remediation:**
1. Add `POST /api/deals/{id}/archive` and `/restore` to orchestration API

**Verification Method:**
```bash
curl -X POST http://localhost:8091/api/deals/DL-0001/archive
```

**Needs Verification:** Yes

---

## Coverage Proof

### Source Reports Used

| # | Agent | Run ID | File Path |
|---|-------|--------|-----------|
| 1 | Claude-Opus-4-5 | 20260204-0030-839ce03a | `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT.Claude-Opus-4-5.20260204-0030-839ce03a.md` |
| 2 | Gemini-CLI | 20260204-0028-gemini | `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT.Gemini-CLI.20260204-0028-gemini.md` |
| 3 | Codex | 20260204-003640-02b34c | `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT.Codex.20260204-003640-02b34c.md` |

### Confirmation

- [x] Every issue from Claude-Opus-4-5 report is represented in V2 (GAP-001 through GAP-008 plus body findings)
- [x] Every issue from Gemini-CLI report is represented in V2 (GAP-001 through GAP-003 plus body findings)
- [x] Every issue from Codex report is represented in V2 (Gaps 1-7 plus body findings)
- [x] Master file issues also captured (executors unwired, SSE stub, no scheduling)

---

## Appendix: Source Mapping

| Issue ID | Claude-Opus-4-5 | Gemini-CLI | Codex | Master File |
|----------|-----------------|------------|-------|-------------|
| ZK-ISSUE-0001 | GAP-003 | GAP-001 | Gap 1 | Phase 3 |
| ZK-ISSUE-0002 | GAP-001 | - | - | Phase 1 |
| ZK-ISSUE-0003 | GAP-002 | GAP-002 | Gap 2 | Phase 2 |
| ZK-ISSUE-0004 | Section 4.1 | GAP-003 | - | Phase 3 |
| ZK-ISSUE-0005 | GAP-007 | - | - | - |
| ZK-ISSUE-0006 | - | - | Gap 3 | - |
| ZK-ISSUE-0007 | - | State Machine | Gap 4 | - |
| ZK-ISSUE-0008 | - | - | Gap 5 | - |
| ZK-ISSUE-0009 | GAP-004 | - | - | - |
| ZK-ISSUE-0010 | GAP-005 | - | Scenarios | - |
| ZK-ISSUE-0011 | GAP-006 | - | - | Phase 6 |
| ZK-ISSUE-0012 | - | - | Gap 6 | - |
| ZK-ISSUE-0013 | - | - | Gap 7 | - |
| ZK-ISSUE-0014 | - | Section 3 | - | - |
| ZK-ISSUE-0015 | GAP-008 | - | - | - |
| ZK-ISSUE-0016 | Section 5.2 | - | Scenarios | - |
| ZK-ISSUE-0017 | Section 5.12 | - | - | - |
| ZK-ISSUE-0018 | Section 5.8 | - | - | - |
| ZK-ISSUE-0019 | Phase 5 | - | - | Phase 5 |
| ZK-ISSUE-0020 | - | - | - | Phase 6 |
| ZK-ISSUE-0021 | Section 7.3 | - | - | Section 5 |
| ZK-ISSUE-0022 | - | - | Scenarios | - |

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P0 | 2 |
| P1 | 6 |
| P2 | 11 |
| P3 | 3 |
| **Total** | **22** |

| Category | Count |
|----------|-------|
| db | 5 |
| orchestration | 9 |
| ui-backend wiring | 6 |
| agent tools | 3 |
| endpoints | 4 |
| legacy | 4 |
| auth/security | 2 |
| observability | 3 |

---

*Consolidated from 3 independent forensic assessments on 2026-02-04. No issues omitted.*

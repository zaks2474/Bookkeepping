# ZakOps Deal Lifecycle V3 Implementation Plan

## AGENT IDENTITY
- **agent_name:** Claude-Opus-4-5
- **agent_version:** claude-opus-4-5-20251101
- **run_id:** 20260204-0212-b214408d
- **date_time:** 2026-02-04T02:12:54Z
- **repo_revision:** a09538f04ed278c32ad6f2a037069b353bf5f797

---

## 1. Executive Summary

### What's Broken (Top Themes from V2)

The ZakOps deal lifecycle system has **22 documented issues** across 8 categories. The fundamental problems are:

1. **Split-Brain Data Architecture (P0)** — Three separate deal tracking systems (Postgres, JSON, DataRoom) that never sync. Agent executors write to JSON; Dashboard reads from Postgres. Deals created in one system are invisible in others.

2. **Email Ingestion Dead (P0)** — The sophisticated email→quarantine→deal pipeline exists but is completely disabled. Zero quarantine items in production.

3. **Broken Quarantine→Deal Flow (P1)** — Even if quarantine worked, approving an item doesn't create a deal. Manual two-step process required.

4. **Auth/Endpoint Chaos (P1)** — Dashboard has no authentication. Dashboard calls wrong endpoints (`/resolve` vs `/process`). Notes endpoint doesn't exist.

5. **Legacy Contamination (P1-P2)** — sys.path hacks, conflicting stage taxonomies, SQLite/Postgres split for actions, dead code paths.

### The Shortest Path to Stability

**Phase 0-2 (Critical):** Stop the bleeding
1. Kill split-brain: Make Postgres THE source of truth for all deal operations
2. Fix endpoint mismatches so Dashboard actually works
3. Wire quarantine approval to deal creation

**Phase 3-4 (Functional):** Make the system usable
1. Enable email ingestion with proper Postgres integration
2. Connect deal creation to folder scaffolding
3. Add authentication

**Phase 5-6 (Production-Ready):** Harden and clean up
1. Add observability (correlation IDs, RAG health checks)
2. Decommission all legacy components
3. Wire action executors

### Non-Negotiable First Decisions

Before any code is written, these decisions MUST be made:

| Decision | Recommendation | Rationale |
|----------|----------------|-----------|
| Source of Truth | Postgres `zakops.deals` | Already has schema, constraints, events |
| Deal ID Format | Keep `DL-XXXX` | Backend already uses this; deprecate `DEAL-YYYY-###` |
| Stage Taxonomy | 9-stage canonical | Already enforced by DB constraint |
| Email Ingestion Target | POST to `/api/quarantine` | Bridge email pipeline to Postgres |
| Agent↔Backend Contract | Agent calls backend HTTP APIs only | Agent never writes to DB directly |

---

## 2. Decision Set

### Decision 2.1: Source-of-Truth Database Model

**Topic:** How to eliminate split-brain and establish unified deal truth

**Options:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | PostgreSQL `zakops.deals` as sole source | Already has schema, constraints, events, API; Dashboard/Agent already use it | Requires rewriting email ingestion and executors |
| B | Keep both Postgres + JSON, add sync job | No executor rewrite needed | Sync failures = split-brain; complex; two sources of bugs |
| C | Migrate everything to new unified schema | Clean slate | Massive effort; breaks everything; no incremental progress |

**Recommendation:** **Option A — Postgres as sole source**

**Migration Approach:**
1. Modify `CreateDealFromEmailExecutor` to call `POST /api/deals` instead of writing to JSON
2. Modify email ingestion to POST to `/api/quarantine` (backend Postgres)
3. Add `folder_path` field population on deal creation
4. Migrate any existing JSON registry deals to Postgres (one-time script)
5. Deprecate and eventually delete `deal_registry.json`

**Verification Proof:**
```bash
# After migration:
# 1. Create deal via API
curl -X POST http://localhost:8091/api/deals -d '{"canonical_name": "Test", "stage": "inbound"}'
# 2. Verify folder created
ls /home/zaks/DataRoom/00-PIPELINE/Inbound/Test*/
# 3. Verify JSON registry NOT updated
grep "Test" /home/zaks/DataRoom/.deal-registry/deal_registry.json  # Should fail
# 4. Verify agent can see deal
curl http://localhost:8091/api/deals | jq '.[] | select(.canonical_name=="Test")'
```

---

### Decision 2.2: Deal Taxonomy and Stage Model

**Topic:** Canonical stage names and allowed transitions

**Options:**

| Option | Description |
|--------|-------------|
| A | Keep existing 9-stage model (inbound, screening, qualified, loi, diligence, closing, portfolio, junk, archived) |
| B | Simplify to 5-stage model (lead, active, won, lost, archived) |
| C | Expand to 12-stage model with sub-stages |

**Recommendation:** **Option A — Keep 9-stage model**

Rationale: Already enforced by DB CHECK constraint. Changing requires migration. 9 stages map well to M&A lifecycle.

**Migration Approach:**
1. Delete `/home/zaks/scripts/deal_state_machine.py` (uses wrong stages)
2. Update DB default from `lead` to `inbound` in init SQL
3. Audit all code for non-canonical stage names, replace with canonical
4. Remove stage references from `deal_registry.py` comments

**Canonical Stage Transitions (STAGE_TRANSITIONS in workflow.py):**
```
inbound    → screening, junk, archived
screening  → qualified, junk, archived
qualified  → loi, junk, archived
loi        → diligence, qualified (regress), junk, archived
diligence  → closing, loi (regress), junk, archived
closing    → portfolio, diligence (regress), junk, archived
portfolio  → archived (terminal success)
junk       → inbound (resurrect), archived
archived   → (terminal, no exits)
```

**Verification Proof:**
```bash
# Confirm no conflicting stage definitions
grep -r "DealStage" /home/zaks/zakops-backend/src/ /home/zaks/scripts/ | grep -v "workflow.py" | wc -l
# Should be 0 after cleanup

# Confirm DB default
psql -c "SELECT column_default FROM information_schema.columns WHERE table_name='deals' AND column_name='stage';"
# Should show 'inbound'
```

---

### Decision 2.3: Agent Tool Contract Boundaries

**Topic:** What the agent can do vs what requires backend

**Options:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | Agent calls backend HTTP APIs only; backend owns all writes | Single source of truth; audit trail; HITL natural | Extra HTTP hop; latency |
| B | Agent writes directly to DB | Lower latency | Split audit logs; bypasses backend validation; HITL harder |
| C | Agent has limited direct DB access for reads | Faster reads | Complexity; inconsistent patterns |

**Recommendation:** **Option A — Agent calls backend APIs only**

Rationale: Backend already has validation, events, idempotency. HITL approval naturally fits HTTP flow.

**Agent Tool Contract:**
```
Tool               | Backend Endpoint              | HITL Required?
-------------------|-------------------------------|---------------
get_deal           | GET /api/deals/{id}           | No
list_deals         | GET /api/deals                | No
search_deals       | POST /rag/query (8052)        | No
transition_deal    | POST /api/deals/{id}/transition | Yes
create_deal (NEW)  | POST /api/deals               | Yes
add_note (NEW)     | POST /api/deals/{id}/notes    | No
```

**Verification Proof:**
```bash
# Grep for direct DB access in agent tools (should be 0)
grep -r "asyncpg\|sqlalchemy\|psycopg" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/
```

---

### Decision 2.4: Email Ingestion Architecture

**Topic:** How emails become deals

**Current State:**
- Email ingestion writes to SQLite `ingest_state.db` and JSON `deal_registry.json`
- Never calls backend API
- Cron job disabled

**Options:**

| Option | Description |
|--------|-------------|
| A | Refactor ingestion to POST directly to `/api/quarantine` |
| B | Add sync job from SQLite/JSON to Postgres |
| C | Replace ingestion pipeline entirely |

**Recommendation:** **Option A — Refactor ingestion to POST to backend**

**Target Architecture:**
```
Gmail IMAP
    ↓
Stage 1-3: Fetch, Normalize, Match (keep existing logic)
    ↓
Stage 4: Persist → POST /api/quarantine (NEW)
    ↓
Quarantine Review (Dashboard)
    ↓
Approve → POST /api/quarantine/{id}/process → Creates Deal in Postgres
    ↓
Deal Folder Created via Backend Hook
    ↓
Deal visible everywhere (Dashboard, Agent, API)
```

**Migration Approach:**
1. Modify `stage_4_persist.py` to call `POST /api/quarantine` instead of SQLite
2. Keep SQLite for dedup cache (message_id tracking) but NOT as deal source
3. Wire quarantine approval to deal creation (separate task)
4. Enable cron job after testing

**Verification Proof:**
```bash
# After refactor, run ingestion
cd /home/zaks/scripts/email_ingestion && python -m email_ingestion.cli --dry-run --days 1
# Check Postgres quarantine (should have items)
psql -c "SELECT COUNT(*) FROM zakops.quarantine_items;"
# Check JSON registry NOT updated
grep "new_email" /home/zaks/DataRoom/.deal-registry/deal_registry.json  # Should fail
```

---

### Decision 2.5: RAG/Embeddings Architecture

**Topic:** What gets embedded, where it lives, refresh strategy

**Current State:**
- RAG service at port 8052
- `search_deals` tool calls it
- Status unknown ("pool=null at boot")

**Recommendation:**

| Aspect | Decision |
|--------|----------|
| What gets embedded | Deal profile data, notes, email content, document text |
| Where embeddings live | Dedicated `crawlrag` database (already exists) |
| Refresh strategy | Re-index on deal update, note add, document upload |
| Health check | Agent startup verifies RAG health; graceful degradation if down |

**Migration Approach:**
1. Add health check to agent startup
2. Add deal indexing hook to deal creation/update endpoints
3. Implement `rag_reindex_deal` executor properly
4. Document graceful degradation behavior

**Verification Proof:**
```bash
# RAG health
curl http://localhost:8052/health
# Create deal, verify indexed
curl -X POST http://localhost:8091/api/deals -d '{"canonical_name": "RAG Test"}'
curl -X POST http://localhost:8052/rag/query -d '{"query": "RAG Test", "top_k": 5}'
```

---

### Decision 2.6: HITL Approval Persistence and Auditability

**Topic:** Where approvals live, how to audit

**Current State:**
- Approvals in `zakops_agent.approvals` table
- Audit log in `zakops_agent.audit_log`
- Backend events in `zakops.deal_events`
- No correlation between them

**Recommendation:**
- Keep approvals in agent DB (LangGraph checkpoint integration)
- Add `correlation_id` field to both agent and backend events
- Pass `X-Correlation-ID` header from agent to backend
- Build unified audit view query

**Migration Approach:**
1. Add `correlation_id` column to `zakops.deal_events` if not exists
2. Modify agent tool calls to generate and pass correlation ID
3. Modify backend to read `X-Correlation-ID` header and store it
4. Create view that joins across databases (or export/import job)

**Verification Proof:**
```bash
# Trigger HITL action
# After approval, check both DBs have same correlation_id
psql -U agent zakops_agent -c "SELECT correlation_id FROM audit_log ORDER BY created_at DESC LIMIT 1;"
psql -c "SELECT correlation_id FROM zakops.deal_events ORDER BY created_at DESC LIMIT 1;"
# Should match
```

---

### Decision 2.7: Authentication Model

**Topic:** Where tokens live, how services authenticate

**Current State:**
- Backend: `X-API-Key` header (shared secret)
- Agent API: JWT-based for /agent endpoints; service token for chatbot
- Dashboard: No auth; proxies with API key injection

**Recommendation:**

| Component | Auth Method | Token Source |
|-----------|-------------|--------------|
| Dashboard → Backend | API Key (middleware inject) | `ZAKOPS_API_KEY` env var |
| Dashboard User Auth | JWT session | OAuth/local auth (NEW) |
| Agent API → Backend | API Key | `ZAKOPS_API_KEY` env var |
| Dashboard → Agent API | Service Token | `DASHBOARD_SERVICE_TOKEN` env var |

**Migration Approach:**
1. Keep existing API key infrastructure
2. Add user authentication to Dashboard (Phase 5)
3. Pass user ID in requests for attribution
4. Implement RBAC in Phase 6

**Verification Proof:**
```bash
# Verify API key required
curl http://localhost:8091/api/deals  # Should work (GET allowed)
curl -X POST http://localhost:8091/api/deals -d '{}'  # Should fail without key
curl -X POST http://localhost:8091/api/deals -H "X-API-Key: $ZAKOPS_API_KEY" -d '{}'  # Should work
```

---

## 3. Phased Implementation Plan

### Phase 0: Stop the Bleeding (Observability + Environment Alignment)

**Objective:** Establish baseline visibility and fix immediate blockers that prevent any progress.

**V2 Issues Covered:**
- ZK-ISSUE-0006 (Dashboard uses wrong quarantine endpoint)
- ZK-ISSUE-0007 (Stage taxonomy conflicts)
- ZK-ISSUE-0010 (RAG search unverified)
- ZK-ISSUE-0012 (Deal notes endpoint mismatch)

**Atomic Task List:**

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 0.1 | Fix Dashboard quarantine endpoint: Change `resolveQuarantineItem` to call `/process` | Frontend | S |
| 0.2 | Fix Dashboard notes endpoint: Change `addDealNote` to correct path | Frontend | S |
| 0.3 | Add `/api/deals/{id}/notes` endpoint to orchestration API | Backend | S |
| 0.4 | Delete `/home/zaks/scripts/deal_state_machine.py` | Backend | S |
| 0.5 | Update DB default stage from `lead` to `inbound` | Backend | S |
| 0.6 | Verify RAG service health; document status | Infra | S |
| 0.7 | Add health check endpoint aggregator | Backend | M |

**Dependencies:** None (can start immediately)

**Risks + Rollback:**
- Risk: Dashboard might have other endpoint mismatches
- Rollback: Revert dashboard changes; add backend aliases

**Gate (Must Pass):**
- [ ] Dashboard quarantine approve works (no 404)
- [ ] Dashboard add note works (no 404)
- [ ] No non-canonical stage names in codebase (ripgrep check)
- [ ] RAG health documented

**Acceptance Criteria:**
1. `curl -X POST http://localhost:8091/api/quarantine/test/process` returns 200 or 404 (not 405)
2. `curl -X POST http://localhost:8091/api/deals/DL-0001/notes` returns 200 or 201
3. `grep -r "lead\|proposal\|negotiation" /home/zaks/zakops-backend/src/` returns 0 matches (excluding comments)
4. RAG status documented in SERVICE-CATALOG.md

**Evidence Required:**
- Screenshot of Dashboard quarantine approval success
- curl output for notes endpoint
- ripgrep output showing zero stage conflicts

---

### Phase 1: Data Truth Unification (Split-Brain Elimination)

**Objective:** Make PostgreSQL `zakops.deals` THE source of truth. Eliminate JSON registry as deal store.

**V2 Issues Covered:**
- ZK-ISSUE-0001 (Split-brain persistence) — PRIMARY
- ZK-ISSUE-0008 (Actions system split)
- ZK-ISSUE-0014 (sys.path hack in executor)

**Atomic Task List:**

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 1.1 | Migrate `CreateDealFromEmailExecutor` to use backend API | Backend | L |
| 1.2 | Remove sys.path hack from executor | Backend | S |
| 1.3 | Migrate action engine from SQLite to Postgres `zakops.actions` | Backend | L |
| 1.4 | Create migration script for existing JSON deals → Postgres | Data | M |
| 1.5 | Run migration in staging, verify | Data | M |
| 1.6 | Update executor to create folder structure via backend hook | Backend | M |
| 1.7 | Deprecate `deal_registry.json` writes (make read-only, then remove) | Backend | M |

**Dependencies:**
- Phase 0 complete (endpoints working)

**Risks + Rollback:**
- Risk: Existing JSON deals lost if migration fails
- Rollback: Keep JSON as read-only backup; re-enable if issues
- Risk: Action engine migration breaks workflows
- Rollback: Feature flag to switch between SQLite and Postgres stores

**Gate (Must Pass):**
- [ ] Creating deal via executor writes to Postgres, not JSON
- [ ] Folder created on Postgres deal creation
- [ ] Actions visible in API match engine state
- [ ] Zero sys.path hacks in production code

**Acceptance Criteria:**
1. `POST /api/deals` creates deal in Postgres AND scaffolds folder
2. `deal_registry.json` not modified by any operation
3. `SELECT COUNT(*) FROM zakops.actions` matches engine state
4. `grep "sys.path" /home/zaks/zakops-backend/src/` returns 0

**Evidence Required:**
- DB query showing deal created via executor
- ls output showing folder structure
- diff showing JSON unchanged
- grep output confirming no sys.path

---

### Phase 2: Contract Alignment (UI ↔ Backend ↔ Agent)

**Objective:** Ensure all API contracts are correct and consistent across Dashboard, Backend, and Agent.

**V2 Issues Covered:**
- ZK-ISSUE-0003 (Quarantine approval doesn't create deal)
- ZK-ISSUE-0004 (Dashboard deals don't create folders)
- ZK-ISSUE-0013 (Actions capabilities/metrics 501)
- ZK-ISSUE-0018 (Zod schema mismatch)
- ZK-ISSUE-0022 (Archive/restore missing)

**Atomic Task List:**

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 2.1 | Wire quarantine approval to deal creation | Backend | M |
| 2.2 | Add folder scaffolding hook to `POST /api/deals` | Backend | M |
| 2.3 | Implement `/api/actions/capabilities` endpoint | Backend | M |
| 2.4 | Implement `/api/actions/metrics` endpoint | Backend | M |
| 2.5 | Add `/api/deals/{id}/archive` endpoint | Backend | S |
| 2.6 | Add `/api/deals/{id}/restore` endpoint | Backend | S |
| 2.7 | Audit Dashboard Zod schemas; add `.passthrough()` | Frontend | M |
| 2.8 | Add schema validation logging in Dashboard | Frontend | S |
| 2.9 | Sync OpenAPI spec with actual endpoints | Backend | M |

**Dependencies:**
- Phase 1 complete (single data source)

**Risks + Rollback:**
- Risk: Quarantine→deal auto-creation causes duplicates
- Rollback: Add idempotency key; disable auto-creation temporarily

**Gate (Must Pass):**
- [ ] Approving quarantine item creates deal in one action
- [ ] Deal creation creates folder
- [ ] `/api/actions/capabilities` returns 200 with data
- [ ] Dashboard shows all deals (no Zod filtering)
- [ ] Archive/restore endpoints work

**Acceptance Criteria:**
1. Approve quarantine → deal exists in Postgres → folder exists in DataRoom
2. Capabilities endpoint returns list of executor types
3. Dashboard deal list matches `psql -c "SELECT COUNT(*) FROM zakops.deals"`

**Evidence Required:**
- End-to-end trace: quarantine approval → deal creation → folder check
- curl output for capabilities/metrics
- Screenshot of dashboard showing same count as DB

---

### Phase 3: Deal Lifecycle Correctness (Stages, HITL, Idempotency)

**Objective:** Ensure stage transitions are correct, HITL approvals work, and operations are idempotent.

**V2 Issues Covered:**
- ZK-ISSUE-0009 (Agent cannot create deals)
- ZK-ISSUE-0011 (No event correlation)
- ZK-ISSUE-0015 (Approval expiry lazy only)
- ZK-ISSUE-0016 (Duplicate deal detection)

**Atomic Task List:**

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 3.1 | Add `create_deal` agent tool with HITL | Agent | M |
| 3.2 | Add `correlation_id` column to `zakops.deal_events` | Backend | S |
| 3.3 | Pass `X-Correlation-ID` header in agent tool calls | Agent | S |
| 3.4 | Store correlation_id in backend events | Backend | S |
| 3.5 | Add background job for approval expiry | Agent | M |
| 3.6 | Add duplicate detection to `POST /api/deals` | Backend | M |
| 3.7 | Add `add_note` agent tool (no HITL) | Agent | S |

**Dependencies:**
- Phase 2 complete (contracts aligned)

**Risks + Rollback:**
- Risk: Duplicate detection blocks legitimate deals
- Rollback: Make duplicate check a warning, not blocker

**Gate (Must Pass):**
- [ ] Agent can create deal (with HITL approval)
- [ ] Correlation IDs match across agent and backend logs
- [ ] Stale approvals automatically expired
- [ ] Duplicate deals rejected with clear error

**Acceptance Criteria:**
1. Agent creates deal → approval needed → approve → deal exists
2. Query both DBs, correlation_id matches
3. Approval older than 1 hour shows as expired
4. Creating same canonical_name twice returns error

**Evidence Required:**
- Agent chat log showing create_deal with HITL
- SQL query showing matching correlation_ids
- Approval record showing auto-expired status
- curl showing duplicate rejection

---

### Phase 4: Deal Knowledge System (Email + RAG + Chat Enrichment)

**Objective:** Enable email ingestion, RAG indexing, and chat-based deal enrichment.

**V2 Issues Covered:**
- ZK-ISSUE-0002 (Email ingestion disabled) — PRIMARY
- ZK-ISSUE-0019 (Action executors unwired)
- ZK-ISSUE-0020 (SSE not implemented)
- ZK-ISSUE-0021 (No scheduling/reminders)

**Atomic Task List:**

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 4.1 | Refactor email ingestion Stage 4 to POST to `/api/quarantine` | Backend | L |
| 4.2 | Test email ingestion with dry-run | QA | M |
| 4.3 | Enable email ingestion cron job | Infra | S |
| 4.4 | Wire `deal_append_email_materials` executor | Backend | M |
| 4.5 | Wire `deal_enrich_materials` executor | Backend | M |
| 4.6 | Wire `rag_reindex_deal` executor | Backend | M |
| 4.7 | Add deal indexing to RAG on create/update | Backend | M |
| 4.8 | Implement SSE endpoint for real-time updates | Backend | L |
| 4.9 | Add deal age tracking field | Backend | S |
| 4.10 | Add basic scheduled reminders (email or log) | Backend | M |

**Dependencies:**
- Phase 3 complete (lifecycle correct)

**Risks + Rollback:**
- Risk: Email ingestion creates noise/spam deals
- Rollback: Run in dry-run mode; manual approval

**Gate (Must Pass):**
- [ ] Emails flow from Gmail → quarantine → deal
- [ ] Deal content indexed in RAG
- [ ] SSE endpoint streams events (or documented as deferred)
- [ ] At least 3 executors wired and tested

**Acceptance Criteria:**
1. Email arrives → quarantine item in DB → approve → deal with folder
2. `search_deals` returns results for indexed deals
3. Dashboard receives real-time update OR polling documented
4. `deal_append_email_materials` successfully copies files

**Evidence Required:**
- End-to-end email → deal trace
- RAG query returning indexed deal
- SSE event received OR documentation
- Executor log showing successful run

---

### Phase 5: Hardening (Security, Reliability, Performance)

**Objective:** Add authentication, improve reliability, add monitoring.

**V2 Issues Covered:**
- ZK-ISSUE-0005 (Dashboard no auth)
- ZK-ISSUE-0017 (No retention policy)

**Atomic Task List:**

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 5.1 | Add user authentication to Dashboard | Frontend | L |
| 5.2 | Pass user ID in backend requests | Frontend | M |
| 5.3 | Add user attribution to deal_events | Backend | S |
| 5.4 | Define retention policy document | Product | S |
| 5.5 | Implement retention cleanup job (if policy defined) | Backend | M |
| 5.6 | Add request tracing (trace ID in logs) | Backend | M |
| 5.7 | Add performance monitoring (response times) | Infra | M |
| 5.8 | Add error alerting (Slack/email on 500s) | Infra | M |

**Dependencies:**
- Phase 4 complete (knowledge system working)

**Risks + Rollback:**
- Risk: Auth breaks existing workflows
- Rollback: Feature flag to disable auth requirement

**Gate (Must Pass):**
- [ ] Dashboard requires login
- [ ] Deal events show user attribution
- [ ] Retention policy documented (even if "no cleanup")
- [ ] Traces visible in logs

**Acceptance Criteria:**
1. Unauthenticated Dashboard access redirects to login
2. `SELECT actor FROM zakops.deal_events` shows user IDs
3. Retention policy document exists
4. Can trace request from Dashboard to Backend to DB via trace ID

**Evidence Required:**
- Screenshot of login page
- DB query showing user actor
- Retention policy document link
- Log grep showing trace ID across services

---

### Phase 6: Legacy Decommission and Final Proof

**Objective:** Remove all legacy components and prove the system is clean.

**V2 Issues Covered:**
- All remaining legacy references
- Final verification of all 22 issues resolved

**Atomic Task List:**

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 6.1 | Delete `deal_registry.json` | Backend | S |
| 6.2 | Delete `/home/zaks/scripts/deal_registry.py` | Backend | S |
| 6.3 | Delete `/home/zaks/scripts/deal_state_machine.py` | Backend | S |
| 6.4 | Delete `zakops-backend/src/api/deal_lifecycle/` | Backend | M |
| 6.5 | Remove SQLite state DB path from code | Backend | S |
| 6.6 | Verify no code references legacy files | QA | M |
| 6.7 | Update SERVICE-CATALOG.md | Docs | S |
| 6.8 | Run full regression test suite | QA | L |
| 6.9 | Final 22-issue checklist verification | QA | M |

**Dependencies:**
- Phase 5 complete (hardening done)

**Risks + Rollback:**
- Risk: Hidden dependency on legacy code
- Rollback: Restore from git if needed

**Gate (Must Pass):**
- [ ] No legacy file references in codebase
- [ ] All 22 V2 issues verified resolved
- [ ] Full regression passes
- [ ] Documentation updated

**Acceptance Criteria:**
1. `find /home/zaks -name "deal_registry.json"` returns nothing
2. `grep -r "deal_state_machine\|deal_registry" /home/zaks/zakops-backend/src/` returns 0
3. All 22 issues marked DONE in coverage matrix
4. SERVICE-CATALOG.md reflects current state

**Evidence Required:**
- find/grep output showing no legacy
- Coverage matrix with all checkmarks
- Test suite passing screenshot
- Documentation diff

---

## 4. No-Drop Coverage Matrix

Every V2 issue MUST be addressed. This matrix ensures no issue is forgotten.

| Issue ID | Title | Severity | Phase | Tasks | Verification | Done |
|----------|-------|----------|-------|-------|--------------|------|
| ZK-ISSUE-0001 | Split-brain persistence | P0 | 1 | 1.1-1.7 | grep JSON unchanged; DB has deals | [ ] |
| ZK-ISSUE-0002 | Email ingestion disabled | P0 | 4 | 4.1-4.3 | Email → quarantine → deal trace | [ ] |
| ZK-ISSUE-0003 | Quarantine approval no deal | P1 | 2 | 2.1 | Approve → deal exists | [ ] |
| ZK-ISSUE-0004 | No DataRoom folders | P1 | 2 | 2.2 | Create deal → folder exists | [ ] |
| ZK-ISSUE-0005 | Dashboard no auth | P1 | 5 | 5.1-5.3 | Login required | [ ] |
| ZK-ISSUE-0006 | Wrong quarantine endpoint | P1 | 0 | 0.1 | Dashboard approve works | [ ] |
| ZK-ISSUE-0007 | Stage taxonomy conflicts | P1 | 0 | 0.4-0.5 | No legacy stages in code | [ ] |
| ZK-ISSUE-0008 | Actions split Postgres/SQLite | P1 | 1 | 1.3 | Single actions table | [ ] |
| ZK-ISSUE-0009 | Agent no create_deal | P2 | 3 | 3.1 | Agent creates deal | [ ] |
| ZK-ISSUE-0010 | RAG unverified | P2 | 0 | 0.6 | Health check documented | [ ] |
| ZK-ISSUE-0011 | No event correlation | P2 | 3 | 3.2-3.4 | Matching correlation_ids | [ ] |
| ZK-ISSUE-0012 | Notes endpoint mismatch | P2 | 0 | 0.2-0.3 | Notes endpoint works | [ ] |
| ZK-ISSUE-0013 | Capabilities/metrics 501 | P2 | 2 | 2.3-2.4 | Endpoints return 200 | [ ] |
| ZK-ISSUE-0014 | sys.path hack | P2 | 1 | 1.2 | No sys.path in code | [ ] |
| ZK-ISSUE-0015 | Approval expiry lazy | P3 | 3 | 3.5 | Stale approvals expired | [ ] |
| ZK-ISSUE-0016 | No duplicate detection | P2 | 3 | 3.6 | Duplicates rejected | [ ] |
| ZK-ISSUE-0017 | No retention policy | P3 | 5 | 5.4-5.5 | Policy documented | [ ] |
| ZK-ISSUE-0018 | Zod schema mismatch | P2 | 2 | 2.7-2.8 | Dashboard shows all deals | [ ] |
| ZK-ISSUE-0019 | Executors unwired | P2 | 4 | 4.4-4.6 | 3+ executors working | [ ] |
| ZK-ISSUE-0020 | SSE not implemented | P2 | 4 | 4.8 | SSE works OR documented | [ ] |
| ZK-ISSUE-0021 | No scheduling/reminders | P2 | 4 | 4.9-4.10 | Reminders working | [ ] |
| ZK-ISSUE-0022 | Archive/restore missing | P3 | 2 | 2.5-2.6 | Endpoints work | [ ] |

---

## 5. Verification and QA Plan

### Gate A: Code Health

**Checks:**
```bash
# Backend lint/type check
cd /home/zaks/zakops-backend && ruff check src/
cd /home/zaks/zakops-backend && mypy src/ --ignore-missing-imports

# Dashboard lint/type check
cd /home/zaks/zakops-agent-api/apps/dashboard && npm run lint
cd /home/zaks/zakops-agent-api/apps/dashboard && npm run typecheck

# Agent API lint/type check
cd /home/zaks/zakops-agent-api/apps/agent-api && ruff check app/
```

**Pass Criteria:** Zero errors (warnings allowed)

### Gate B: End-to-End Proof

**Critical Path Test:**
```bash
# 1. Create deal via API
DEAL_RESP=$(curl -s -X POST http://localhost:8091/api/deals \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"canonical_name": "E2E Test Corp", "stage": "inbound"}')
DEAL_ID=$(echo $DEAL_RESP | jq -r '.deal_id')

# 2. Verify in Postgres
psql -c "SELECT deal_id, stage FROM zakops.deals WHERE deal_id='$DEAL_ID';"

# 3. Verify folder created
ls -la /home/zaks/DataRoom/00-PIPELINE/Inbound/E2E*/

# 4. Verify agent can see it
curl -s http://localhost:8091/api/deals/$DEAL_ID | jq '.canonical_name'

# 5. Transition via agent (requires HITL test)
curl -s -X POST http://localhost:8095/agent/invoke \
  -H "X-Service-Token: $DASHBOARD_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"actor_id\":\"e2e-test\",\"message\":\"Transition deal $DEAL_ID to screening\"}"

# 6. Approve HITL, verify transition
# (manual step in Dashboard)

# 7. Verify final state
psql -c "SELECT deal_id, stage FROM zakops.deals WHERE deal_id='$DEAL_ID';"
```

### QA Pass #1: Functional (Happy Paths)

| Test | Steps | Expected |
|------|-------|----------|
| Deal CRUD | Create, Read, Update, Archive | All operations succeed |
| Stage Transitions | inbound→screening→qualified | Transitions work, events logged |
| Quarantine Flow | Create item, approve, deal created | Deal exists with folder |
| Agent Tools | get_deal, transition_deal, create_deal | All return correct data |
| Email Ingestion | Send test email, wait for cron | Quarantine item created |

### QA Pass #2: Adversarial

| Test | Steps | Expected |
|------|-------|----------|
| Auth Failure | Call without API key | 401 Unauthorized |
| Invalid Stage | Transition to "bogus" | 400 Bad Request |
| Backend Down | Stop backend, call agent | Graceful error message |
| RAG Down | Stop RAG, call search_deals | Error or empty, not crash |
| Duplicate Deal | Create same name twice | Second rejected |
| HITL Timeout | Create approval, wait 2 hours | Approval marked expired |
| Concurrent Transition | Two transitions same deal | One succeeds, one fails |

### Correlation Strategy

**Request Tracing:**
1. Dashboard generates `X-Request-ID` header
2. Backend logs include request ID
3. Agent includes request ID in tool calls
4. Backend stores correlation_id in events

**Trace Query:**
```sql
-- Find all events for a request
SELECT
    de.deal_id, de.event_type, de.actor, de.created_at,
    de.correlation_id
FROM zakops.deal_events de
WHERE de.correlation_id = 'req-12345'
ORDER BY de.created_at;
```

---

## 6. Legacy Decommission Plan

### Components to Remove

| Component | Type | Path | Verification |
|-----------|------|------|--------------|
| deal_registry.json | File | `/home/zaks/DataRoom/.deal-registry/deal_registry.json` | `find -name deal_registry.json` returns empty |
| deal_registry.py | Script | `/home/zaks/scripts/deal_registry.py` | File deleted |
| deal_state_machine.py | Script | `/home/zaks/scripts/deal_state_machine.py` | File deleted |
| deal_lifecycle API | Code | `/home/zaks/zakops-backend/src/api/deal_lifecycle/` | Directory deleted |
| SQLite ingest_state.db (deals) | Database | `/home/zaks/DataRoom/.deal-registry/ingest_state.db` | Keep for email dedup; remove deal tables |
| quarantine.json | File | `/home/zaks/DataRoom/.deal-registry/quarantine.json` | File deleted |
| events JSONL | Directory | `/home/zaks/DataRoom/.deal-registry/events/` | Directory deleted |

### Verification Commands

```bash
# Verify no code references legacy files
grep -r "deal_registry.json" /home/zaks/zakops-backend/src/ /home/zaks/zakops-agent-api/
# Expected: 0 matches

grep -r "deal_state_machine" /home/zaks/zakops-backend/src/ /home/zaks/scripts/
# Expected: 0 matches

grep -r "deal_lifecycle" /home/zaks/zakops-backend/src/
# Expected: 0 matches (after deletion)

grep -r "sys.path" /home/zaks/zakops-backend/src/
# Expected: 0 matches

# Verify files deleted
ls /home/zaks/DataRoom/.deal-registry/deal_registry.json
# Expected: No such file

ls /home/zaks/scripts/deal_registry.py
# Expected: No such file

ls /home/zaks/zakops-backend/src/api/deal_lifecycle/
# Expected: No such directory
```

### What to Keep (Changelog Only)

Record in `/home/zaks/bookkeeping/CHANGES.md`:
```
YYYY-MM-DD: LEGACY DECOMMISSION COMPLETE
- Deleted deal_registry.json (migrated to Postgres)
- Deleted scripts/deal_registry.py (replaced by backend API)
- Deleted scripts/deal_state_machine.py (duplicate of workflow.py)
- Deleted src/api/deal_lifecycle/ (replaced by orchestration API)
- Kept ingest_state.db for email dedup cache only
```

---

## 7. Prioritized Backlog

| Priority | Issue ID | Title | Effort | Owner | Dependencies | Phase |
|----------|----------|-------|--------|-------|--------------|-------|
| P0 | ZK-ISSUE-0001 | Split-brain persistence | L | Backend | None | 1 |
| P0 | ZK-ISSUE-0002 | Email ingestion disabled | L | Backend | Phase 1 | 4 |
| P1 | ZK-ISSUE-0003 | Quarantine no deal creation | M | Backend | Phase 1 | 2 |
| P1 | ZK-ISSUE-0004 | No DataRoom folders | M | Backend | Phase 1 | 2 |
| P1 | ZK-ISSUE-0005 | Dashboard no auth | L | Frontend | Phase 4 | 5 |
| P1 | ZK-ISSUE-0006 | Wrong quarantine endpoint | S | Frontend | None | 0 |
| P1 | ZK-ISSUE-0007 | Stage taxonomy conflicts | S | Backend | None | 0 |
| P1 | ZK-ISSUE-0008 | Actions Postgres/SQLite split | L | Backend | Phase 0 | 1 |
| P2 | ZK-ISSUE-0009 | Agent no create_deal | M | Agent | Phase 2 | 3 |
| P2 | ZK-ISSUE-0010 | RAG unverified | S | Infra | None | 0 |
| P2 | ZK-ISSUE-0011 | No event correlation | M | Backend+Agent | Phase 2 | 3 |
| P2 | ZK-ISSUE-0012 | Notes endpoint mismatch | S | Backend+Frontend | None | 0 |
| P2 | ZK-ISSUE-0013 | Capabilities/metrics 501 | M | Backend | Phase 1 | 2 |
| P2 | ZK-ISSUE-0014 | sys.path hack | S | Backend | Phase 0 | 1 |
| P2 | ZK-ISSUE-0016 | No duplicate detection | M | Backend | Phase 2 | 3 |
| P2 | ZK-ISSUE-0018 | Zod schema mismatch | M | Frontend | Phase 1 | 2 |
| P2 | ZK-ISSUE-0019 | Executors unwired | M | Backend | Phase 2 | 4 |
| P2 | ZK-ISSUE-0020 | SSE not implemented | L | Backend | Phase 3 | 4 |
| P2 | ZK-ISSUE-0021 | No scheduling/reminders | M | Backend | Phase 3 | 4 |
| P3 | ZK-ISSUE-0015 | Approval expiry lazy | M | Agent | Phase 2 | 3 |
| P3 | ZK-ISSUE-0017 | No retention policy | S | Product | Phase 4 | 5 |
| P3 | ZK-ISSUE-0022 | Archive/restore missing | S | Backend | Phase 1 | 2 |

---

## Summary

This V3 plan addresses all 22 issues from the V2 registry through 7 phases:

- **Phase 0:** Fix immediate blockers (endpoints, stages, health checks)
- **Phase 1:** Eliminate split-brain (Postgres as single truth)
- **Phase 2:** Align all contracts (quarantine→deal, folders, capabilities)
- **Phase 3:** Fix deal lifecycle (agent tools, correlation, dedup)
- **Phase 4:** Enable knowledge system (email, RAG, executors)
- **Phase 5:** Harden (auth, retention, monitoring)
- **Phase 6:** Decommission legacy and prove clean

**Key Decisions:**
1. Postgres `zakops.deals` is THE source of truth
2. Keep 9-stage canonical model
3. Agent calls backend APIs only (no direct DB)
4. Email ingestion POSTs to `/api/quarantine`
5. Add correlation IDs across systems
6. Add user auth to Dashboard

**Total Effort Estimate:** ~40-60 developer-days across phases

---

*Plan generated by Claude-Opus-4-5 on 2026-02-04. All 22 V2 issues covered.*

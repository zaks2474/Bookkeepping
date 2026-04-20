# ZakOps Deal Lifecycle: Honest Assessment

**Date:** 2026-02-03
**Status:** Brutally Honest

---

## Executive Summary

The ZakOps deal infrastructure has **solid bones** but significant **gaps in the connective tissue**. The core components exist (database, workflow engine, agent tools, HITL gates) but many integration paths are **partial, untested, or stub implementations**.

---

## The Full Journey: What ACTUALLY Happens to a Deal

### PHASE 1: Email Arrives (Entry Point)

#### What's SUPPOSED to Happen:
1. Email arrives in Gmail inbox
2. Email ingestion pipeline (`/home/zaks/scripts/email_ingestion/`) polls Gmail
3. LLM triages email for M&A relevance
4. Relevant emails are POSTed to `/api/quarantine`
5. Quarantine item stored in `zakops.quarantine_items`

#### What ACTUALLY Happens:
```
REALITY CHECK:
- The email_ingestion pipeline EXISTS and is sophisticated (triage, enrichment, quarantine)
- It writes to local JSON/SQLite quarantine registry
- The bridge to POST /api/quarantine EXISTS (REMEDIATION-001 decision 5C)
- BUT: The cron job to run the pipeline is NOT ACTIVE

Current state: 0 items in quarantine_items table
Manual testing required to verify pipeline → API bridge
```

**GAP: Email ingestion is not running in production. Manual deal creation only.**

---

### PHASE 2: Quarantine Review (Human Decision Gate)

#### What's SUPPOSED to Happen:
1. Dashboard shows pending quarantine items
2. Human reviews item, decides approve/reject
3. On approve: HITL action creates deal from email

#### What ACTUALLY Works:
```python
# POST /api/quarantine/{item_id}/process
# Updates status to 'approved' or 'rejected'
# Links deal_id if provided
```

#### What's MISSING:
```
1. NO automatic deal creation on approve
   - POST /api/quarantine/{item_id}/process just updates status
   - Creating a deal requires SEPARATE action

2. Dashboard quarantine UI exists but may not trigger full workflow:
   - /api/actions/quarantine/route.ts proxies to backend
   - But DEAL.CREATE_FROM_EMAIL executor expects specific inputs

3. The two quarantine systems don't talk:
   - Email ingestion writes to: /home/zaks/DataRoom/_quarantine (local files)
   - Backend reads from: zakops.quarantine_items (database)
   - ingestion_gateway.py bridges them, but inconsistently
```

**GAP: Quarantine approve → Deal create is a multi-step manual process, not one-click.**

---

### PHASE 3: Deal Creation

#### Three Paths to Create a Deal:

**Path A: Direct API (Works)**
```bash
curl -X POST http://localhost:8091/api/deals \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"canonical_name": "Acme Corp", "stage": "inbound"}'
```
- Creates deal with DL-XXXX ID
- Inserts into `zakops.deals`
- No folder structure created

**Path B: DEAL.CREATE_FROM_EMAIL Executor (Sophisticated but Disconnected)**
```
- CreateDealFromEmailExecutor in deal_create_from_email.py
- Creates DataRoom folder structure:
  01-NDA/, 02-CIM/, 03-Financials/, ..., 07-Correspondence/
- Copies quarantine artifacts
- Updates Deal Registry (JSON file)
- Writes deal_profile.json

BUT: Only triggered by Action system, not direct API call
```

**Path C: MCP Server Tools (Partial)**
```python
# mcp_server/server.py
@mcp.tool()
async def create_deal(canonical_name, display_name, description):
    # Calls backend POST /api/deals
    # Does NOT create folder structure
```

**GAP: Database deal vs DataRoom deal are NOT synchronized.**
- `zakops.deals` table has deal_id, stage, status
- `/home/zaks/DataRoom/00-PIPELINE/` has folder with documents
- `deal_registry.json` links them
- No automatic sync when one changes

---

### PHASE 4: Deal Stage Management

#### Stage Taxonomy (Correct):
```
inbound → screening → qualified → loi → diligence → closing → portfolio
                ↓           ↓         ↓         ↓          ↓
              junk ←──────←──────←──────←──────←──────←──────┘
                ↓
            archived (terminal)
```

#### What Works Well:
```python
# DealWorkflowEngine in workflow.py
- Stage validation enforced
- Invalid transitions rejected (HTTP 400)
- Idempotency (24h window)
- Event logging to deal_events
- Database CHECK constraint prevents invalid stages
```

#### Agent Transition (HITL Protected):
```python
# transition_deal tool in deal_tools.py
1. Validates to_stage against enum (BEFORE approval)
2. Fetches current stage from backend (ground truth)
3. Calls POST /api/deals/{id}/transition
4. Re-fetches to verify change (No-Illusions gate)
5. Returns structured result with backend status
```

**This is the best-implemented part of the system.**

---

### PHASE 5: During Active Deal Lifecycle

#### What SHOULD Happen at Each Stage:

| Stage | Expected Activities | What's Implemented |
|-------|--------------------|--------------------|
| inbound | NDA tracking, initial triage | deal_profile.json only |
| screening | Company research, fit assessment | Nothing specific |
| qualified | CIM review, financial modeling | ANALYSIS.BUILD_VALUATION_MODEL (stub) |
| loi | LOI generation, negotiation | DOCUMENT.GENERATE_LOI (stub) |
| diligence | Document requests, due diligence | DILIGENCE.REQUEST_DOCS (stub) |
| closing | Final paperwork | Nothing |
| portfolio | Post-acquisition management | Nothing |

**GAP: Stage-specific automation is mostly capability definitions, not working code.**

#### Action Executors That EXIST but Are Untested:
```
deal_append_email_materials.py    - Copies emails to deal folder
deal_backfill_sender_history.py   - Enriches sender context
deal_dedupe_and_place_materials.py - Deduplicates files
deal_enrich_materials.py          - Extracts metadata
deal_extract_email_artifacts.py   - Entity extraction
analysis_build_valuation_model.py - Financial modeling
document_generate_loi.py          - LOI generation
presentation_generate_pitch_deck.py - Pitch deck
diligence_request_docs.py         - Doc requests
communication_send_email.py       - Outbound email
rag_reindex_deal.py               - RAG indexing
```

**Status: These exist in code but are not wired into any UI or automated workflow.**

---

### PHASE 6: Deal Events & Audit Trail

#### What's Captured:
```sql
-- zakops.deal_events
-- Captures: stage_changed, created, updated
-- With: actor, payload (from_stage, to_stage, reason), timestamp
```

#### What's Missing:
```
1. NO event for: document added, email received, note created
2. NO correlation between deal_events and action execution
3. NO SSE/WebSocket push (dashboard polls or manual refresh)
4. Audit log in Agent API (audit_log table) is SEPARATE from deal_events
```

**GAP: Two disconnected audit trails - agent actions vs deal events.**

---

### PHASE 7: Terminal States

#### Portfolio (Success):
```
deal.stage = 'portfolio'
deal.status = 'active' (still tracked)
Folder remains in DataRoom
No automatic archival
```

#### Junk (Rejected):
```
deal.stage = 'junk'
Can resurrect to 'inbound' (only transition)
Folder remains
No cleanup
```

#### Archived (Final):
```
deal.stage = 'archived'
deal.deleted still = FALSE (soft delete not used consistently)
No transitions out
Folder remains forever
```

**GAP: No automated cleanup, archival policy, or retention management.**

---

## The Brutal Truth: What's Really Missing

### 1. No End-to-End Automation
```
Email → Quarantine → Deal → Pipeline → Close

Currently: Each step requires manual intervention
Should be: Configurable automation with HITL gates only where needed
```

### 2. Three Disconnected Data Stores
```
zakops.deals (database)     ←→ NOT SYNCED ←→     Deal Registry (JSON)
                                    ↓
                            DataRoom (files)
```

### 3. Agent Can't Do Much Autonomously
```
Agent tools available:
- transition_deal (HITL required)
- get_deal (read-only)
- search_deals (RAG, if connected)

Agent CANNOT:
- Create deals autonomously
- Send emails (HITL required)
- Move documents
- Schedule follow-ups
```

### 4. Dashboard Shows Partial Picture
```
Dashboard knows about:
✓ Deal list (from /api/deals)
✓ Pipeline view (from /api/pipeline/summary)
✓ Quarantine items (from /api/quarantine)
✓ Agent activity (from /agent/activity)

Dashboard does NOT show:
✗ DataRoom folder contents
✗ Deal Registry metadata
✗ Document attachments
✗ Email history
✗ Action queue (partially)
```

### 5. No Scheduling or Reminders
```
No implementation for:
- Follow-up reminders
- Stage timeout warnings ("Deal in screening for 30 days")
- Scheduled actions
- SLA tracking
```

---

## Current Production State

```
As of 2026-02-03:

Database:
- 4 deals (3 inbound, 1 qualified)
- 0 quarantine items
- 0 pending actions

Services:
- Backend API: running (8091)
- Agent API: running (8095)
- Dashboard: running (3003)
- Email ingestion: NOT running

Verified Working:
✓ Deal CRUD via API
✓ Stage transitions (including validation)
✓ HITL approval workflow
✓ Agent chat with tool calling
✓ Lazy expiry enforcement

Not Verified/Not Working:
? Email → Quarantine pipeline
? Quarantine → Deal automation
? Document management
? RAG search integration
? Action executor workflows
```

---

## Recommended Priorities

### P0: Make Email Pipeline Work
1. Enable email ingestion cron job
2. Verify ingestion_gateway → POST /api/quarantine flow
3. Test full email → quarantine → deal path

### P1: Connect Database to DataRoom
1. When deal created in DB, create folder structure
2. When folder created, ensure DB record exists
3. Sync deal_profile.json ↔ zakops.deals metadata

### P1: Dashboard Deal Detail View
1. Show DataRoom contents (documents, emails)
2. Show action history
3. Show all deal events

### P2: Stage-Specific Automation
1. Implement at least one executor per stage
2. Wire executors to dashboard actions
3. Add progress tracking

### P3: Notifications & Scheduling
1. Add deal age tracking
2. Implement follow-up reminders
3. Email notifications for pending actions

---

## Architectural Debt

| Issue | Impact | Effort |
|-------|--------|--------|
| Two quarantine systems | Confusion, data loss | Medium |
| DB-DataRoom desync | Missing files, orphan records | High |
| No event correlation | Can't trace actions | Medium |
| Stale v_pipeline_summary view | Uses old stage names | Low |
| No pagination on deal list | Performance at scale | Low |
| RAG disconnected | Search doesn't work | Medium |

---

## Conclusion

**The infrastructure is 60% built.** The critical path (deal creation → stage transitions → HITL approvals) works. But the automation layer (email ingestion → automatic deal creation → stage-specific workflows) is mostly stub code that's never been tested end-to-end.

**To make this production-ready:**
1. Connect email ingestion to the database
2. Sync database deals with DataRoom folders
3. Test and enable action executors
4. Build dashboard views for the full deal context

---

*This assessment was generated from actual code inspection, not documentation.*

---

## Run Index

### Run: 20260204-0030-839ce03a

- **Agent:** Claude-Opus-4-5 (claude-opus-4-5-20251101)
- **Date:** 2026-02-04T00:30:00Z
- **Report:** [DEAL_LIFECYCLE_HONEST_ASSESSMENT.Claude-Opus-4-5.20260204-0030-839ce03a.md](./DEAL_LIFECYCLE_HONEST_ASSESSMENT.Claude-Opus-4-5.20260204-0030-839ce03a.md)
- **JSON:** [DEAL_LIFECYCLE_HONEST_ASSESSMENT.Claude-Opus-4-5.20260204-0030-839ce03a.json](./DEAL_LIFECYCLE_HONEST_ASSESSMENT.Claude-Opus-4-5.20260204-0030-839ce03a.json)

**Top Findings:**
1. **P0: Email ingestion disabled** — No cron job active, 0 quarantine items in DB
2. **P1: Quarantine→Deal gap** — Approving quarantine does NOT auto-create deal
3. **P1: Three disconnected registries** — DB (DL-XXXX), JSON (DEAL-YYYY-###), DataRoom unsynchronized
4. **P1: Dashboard no auth** — Proxies to backend without authentication
5. **CONFIRMED: HITL working** — F-003 No-Illusions Gate verified in deal_tools.py
6. **CONFIRMED: Idempotency** — 24-hour window via deal_events.idempotency_key
7. **NEW: Agent tool limits** — Only get_deal, search_deals, transition_deal (no create)
8. **NEEDS VERIFICATION: RAG search** — search_deals depends on 8052 service status

---

## Run Index Entry
- **Agent:** Gemini-CLI
- **Run ID:** 20260204-0028-gemini
- **Report Path:** /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT.Gemini-CLI.20260204-0028-gemini.md
- **Key Findings:**
  - **Confirmed Split-Brain:** API/Dashboard reads/writes PostgreSQL (`zakops.deals`), while Agent Executors read/write `deal_registry.json`. They are completely disconnected.
  - **Quarantine Dead End:** Approving a quarantine item in the API updates the status but fails to create a deal record.
  - **Legacy Code Debt:** The `deal_create_from_email.py` executor uses a `sys.path` hack to import legacy file-based registry logic.
  - **Folder Desync:** Deals created via Dashboard do not create folders. Deals created via Agent do not appear in Dashboard.

## Run Index Entry — Codex 20260204-003640-02b34c
- agent_name: Codex
- run_id: 20260204-003640-02b34c
- report_path: /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT.Codex.20260204-003640-02b34c.md
- summary:
  - Backend container runs orchestration API, not deal_lifecycle; legacy resolve endpoints exist but likely unused.
  - Quarantine processing in orchestration only updates quarantine status; it does not create deals or tie to pipeline.
  - Dashboard writes (resolve) target legacy `/api/quarantine/{id}/resolve`, while backend orchestration exposes `/api/quarantine/{id}/process`.
  - Stage taxonomy conflicts across workflow (lead/qualified/proposal/negotiation/won/lost) vs scripts deal_state_machine (new_deal/in_review/qualified/negotiation/contract_signed/closed_won/closed_lost) vs DB default `lead`.
  - Deal “source of truth” is Postgres `zakops.deals`, but actions are split with SQLite `ZAKOPS_STATE_DB` and an in-repo JSON registry.
  - Agent API tools operate on backend `/api/deals` with stage validation; approvals/HITL are per-agent, not deal-linked.
  - Duplicate detection and idempotency for quarantine→deal creation are not implemented in orchestration.
  - Notes endpoint mismatch (`/api/notes` in workflow vs `/api/deals/{id}/notes` in orchestration) suggests potential 404s.

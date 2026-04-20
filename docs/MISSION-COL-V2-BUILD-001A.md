# MISSION: COL-V2-BUILD-001A
## Core Wiring, Service Completion, and Compliance Foundation
## Date: 2026-02-13
## Classification: Service Integration + Compliance Foundation
## Prerequisite: COL-V2 QA Verification Complete (19 missions, 516 gates)
## Successor: COL-V2-BUILD-001B (Reflexion, Cognitive Intelligence, RAG Enhancement)

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash or context compaction, run:

```bash
# 1. Determine current phase
cat /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001A.md

# 2. Check validation state
cd /home/zaks/zakops-agent-api && make validate-local

# 3. Check for partial work
git -C /home/zaks/zakops-agent-api status
git -C /home/zaks/zakops-agent-api log --oneline -5
```

Resume from the checkpoint file. Do not re-execute completed phases.

---

## Continuation Protocol
<!-- Adopted from Improvement Area IA-7 -->

After completing **each phase**, write a structured checkpoint:

```bash
cat > /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001A.md << 'CHECKPOINT'
Mission: COL-V2-BUILD-001A
Last completed phase: Phase {N}
Next phase: Phase {N+1}
Validation state: {PASS/FAIL + details}
Open decision trees: {any unresolved forks}
Files modified this session: {list}
CHECKPOINT
```

---

## Mission Objective

**Wire existing COL-V2 services into the agent-api turn pipeline, complete partially-built services, and establish the compliance foundation.** This is Phase 1 of a 3-part build split from the full COL-V2-BUILD-001 scope.

The key discovery that motivated splitting into sub-missions: the backend (`zakops-backend`) ALREADY has all DealBrainService infrastructure built (337-line service, 303-line router with 14 endpoints, 130-line migration). The agent-api also has 10 services that QA gates missed due to wrong search paths. This mission wires those existing services together and completes their missing features.

**What this mission does:**
1. **Core wiring** -- connect 5 existing services into graph.py turn pipeline as fire-and-forget enrichment
2. **Service completion** -- add spec-mandated features to 7 existing service files
3. **Compliance foundation** -- legal hold tables, partition automation function

**What this mission is NOT:**
- This is NOT COL-V2-BUILD-001B (reflexion, cognitive intelligence, RAG enhancement -- next sub-mission)
- This is NOT COL-V2-BUILD-001C (ambient UI, dashboard components, architecture)
- This is NOT a backend build mission -- zakops-backend is already built, do NOT modify it
- This is NOT a redesign -- existing services are EXTENDED, not rewritten

**Source material:**
- Actionable items register: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md`
- Design specification: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` (3,276 lines)
- Parent mission (superseded): `/home/zaks/bookkeeping/docs/MISSION-COL-V2-BUILD-001.md`
- Backend brain service (reference): `/home/zaks/zakops-backend/src/core/agent/deal_brain_service.py` (337 lines)
- Backend brain router (reference): `/home/zaks/zakops-backend/src/api/orchestration/routers/brain.py` (303 lines)

---

## Context

The COL-V2 QA verification (19 missions, 516 gates) found ~195 true scope gaps after correcting for mislocated service files. Post-QA deep audit revealed:

1. **Backend is fully built** -- `deal_brain_service.py` has full CRUD, fact ops, history, entity graph. `brain.py` router has 14 endpoints wired into main.py line 507. Migration `028_deal_brain.sql` creates all tables. Eight additional intelligence services exist in `src/core/agent/`.

2. **Agent-api has 10 partially-built services** that QA gates missed because they searched wrong paths or had grep noise from .venv directories. These services exist and have core logic but need feature completion and graph.py integration.

3. **RRF with k=60** is already built in Zaks-llm (`src/api/rag_rest_api.py`) -- no need to build it.

4. **Services needing wiring into graph.py:** snapshot_writer, brain_extraction, drift_detection, citation_audit, node_registry. All exist as standalone modules but are not called from the turn pipeline.

5. **Services needing completion:** proposal_service (BackendClient migration, expiration), export_service (BackendClient migration, brain appendix), citation_audit (configurable thresholds), replay_service (admin auth, audit log), counterfactual_service (admin auth), summarizer (extractive pre-filter).

---

## Glossary

| Term | Definition |
|------|-----------|
| Deal Brain | Per-deal knowledge accumulator -- facts, risks, decisions, ghost knowledge, summary (S4) |
| Post-turn enrichment | Fire-and-forget coroutine invoked via `asyncio.create_task()` after assistant response, performing snapshot/extraction/drift/citation work without blocking the user |
| BackendClient | Wrapper around httpx in `deal_tools.py` that handles backend URL, auth, timeouts -- mandatory for agent-api to backend calls |
| Fire-and-forget | Pattern: `asyncio.create_task(coro)` with try/except logging inside the coroutine; caller does not await the result |
| Node registry | `node_registry.py` -- routes queries to specialist nodes (Financial, Risk, DealMemory) based on keyword classification |
| Legal hold | Compliance mechanism preventing deletion of conversation data during regulatory or legal review |
| Drift detection | Brain staleness check + contradiction detection + decay confidence computation (S4.5) |

---

## Architectural Constraints

Per standing constraints in CLAUDE.md and contract surface discipline. Mission-specific additions:

- **BackendClient is mandatory for agent-to-backend calls** -- all calls from agent-api to zakops-backend MUST use `BackendClient` from `deal_tools.py`, never raw `httpx.AsyncClient`. Some existing services (proposal_service.py, export_service.py) use raw httpx and must be migrated.
- **Fire-and-forget for non-critical paths** -- brain extraction, drift detection, snapshot writing, and citation audit are post-turn enrichments. They MUST NOT block the user-facing response. Use `asyncio.create_task()` with exception logging, not `await`.
- **Singleton pattern for services** -- all COL-V2 services use module-level singleton instances (e.g., `replay_service = ReplayService()`). Preserve this pattern.
- **Spec section references in docstrings** -- every COL-V2 service module MUST have a docstring citing its COL-DESIGN-SPEC-V2 section (e.g., `COL-DESIGN-SPEC-V2, Section 4.5`). Existing services already follow this.
- **Admin endpoints require role check** -- `/admin/replay` and `/admin/counterfactual` currently only check session auth. They must additionally verify the user has ADMIN role per S6.4/S6.5.
- **Migration path is `migrations/` in agent-api** -- NOT alembic/versions/. Agent-api uses sequential SQL files (e.g., `029_legal_hold.sql`).
- **Backend repo is READ-ONLY** -- do NOT modify zakops-backend. It is already built. Only wire agent-api to use its endpoints via BackendClient.
<!-- Adopted from Improvement Area IA-15 -->
- **Governance surfaces** -- this mission touches dependencies (Surface 10) and error handling (Surface 12). Run `make validate-surface10` and `make validate-surface12` if applicable validators exist.

---

## Anti-Pattern Examples

### WRONG: Raw httpx in agent-api services
```python
async with httpx.AsyncClient(timeout=10.0) as client:
    resp = await client.get(f"{settings.BACKEND_URL}/api/deals/{deal_id}/brain")
```

### RIGHT: BackendClient from deal_tools
```python
from app.core.langgraph.tools.deal_tools import BackendClient
client = BackendClient()
resp = await client.get(f"/api/deals/{deal_id}/brain")
```

### WRONG: Awaiting enrichment in the critical path
```python
# In graph.py turn handler -- blocks user response
await snapshot_writer.write(snapshot)
await trigger_brain_extraction(deal_id, ...)
await check_and_report_drift(...)
```

### RIGHT: Fire-and-forget for enrichment
```python
# In graph.py turn handler -- non-blocking
import asyncio
asyncio.create_task(_post_turn_enrichment(deal_id, thread_id, ...))
```

### WRONG: Hardcoded admin check
```python
if session.user_id != "admin":
    raise HTTPException(403)
```

### RIGHT: Role-based admin check
```python
if session.role not in ("admin", "ADMIN"):
    raise HTTPException(status_code=403, detail="Admin role required")
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | graph.py post-turn enrichment introduces import cycle between services | MEDIUM | Agent-api fails to start | Gate P1: `python -c "from app.core.langgraph.graph import build_graph"` import check |
| 2 | BackendClient migration in proposal_service breaks existing proposal flow | MEDIUM | Proposal execution regresses | Gate P2: curl test proposal endpoint after migration |
| 3 | New migration 029 collides with existing migration numbering | LOW | Migration fails to apply | P3-01 task: check existing migration numbers before creating |
| 4 | CRLF in new .sql migration file causes psql parse error | MEDIUM | Migration won't apply | WSL safety checklist: `sed -i 's/\r$//'` on all new files |
| 5 | Context window pressure from reading 10+ service files during Phase 1 wiring | MEDIUM | Later phases get sloppy | Keep changes focused per phase; checkpoint after each phase |

---

## Phase 0 -- Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify codebase state, confirm backend availability, validate existing service imports, and establish a clean baseline.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Run baseline validation** -- `cd /home/zaks/zakops-agent-api && make validate-local`
  - **Checkpoint:** Must exit 0. If not, fix before proceeding.
- P0-02: **Verify backend is running** -- `curl -sf http://localhost:8091/health`
  - **Decision Tree:**
    - **IF** backend is running -> proceed
    - **ELSE** -> start backend: `cd /home/zaks/zakops-backend && docker compose up -d backend --no-deps`
- P0-03: **Verify backend brain endpoints respond** -- `curl -sf http://localhost:8091/api/deals/test-id/brain`
  - **Decision Tree:**
    - **IF** returns JSON (200 or 404) -> backend brain is wired, confirm ready for integration
    - **ELSE** -> investigate backend brain router wiring (check main.py line 507)
- P0-04: **Run D-item verification checks** from actionable items register:
  - `psql -h localhost -U agent -d zakops_agent -c "\df create_monthly_partitions"` (D1 -- partition function)
  - `psql -h localhost -U zakops -d zakops -c "\d deal_budgets"` (D2 -- budget table)
  - `psql -h localhost -U agent -d zakops_agent -c "SELECT * FROM deal_cost_summary LIMIT 1"` (D7 -- cost view)
  - Record which exist and which don't -- this informs Phase 3 scope.
- P0-05: **Import-check all 10 agent-api services** -- from `/home/zaks/zakops-agent-api/apps/agent-api`:
  - `python -c "from app.services.snapshot_writer import snapshot_writer; print('OK')"`
  - `python -c "from app.services.brain_extraction import trigger_brain_extraction; print('OK')"`
  - `python -c "from app.services.drift_detection import check_staleness; print('OK')"`
  - `python -c "from app.core.security.citation_audit import audit_citations; print('OK')"`
  - `python -c "from app.core.langgraph.node_registry import node_registry; print('OK')"`
  - `python -c "from app.services.proposal_service import proposal_service; print('OK')"`
  - `python -c "from app.services.export_service import export_service; print('OK')"`
  - `python -c "from app.services.replay_service import replay_service; print('OK')"`
  - `python -c "from app.services.counterfactual_service import counterfactual_service; print('OK')"`
  - `python -c "from app.services.momentum_calculator import momentum_calculator; print('OK')"`
  - **Checkpoint:** At least 8 of 10 must import cleanly. Record any failures.
- P0-06: **Write initial checkpoint** -- per Continuity Protocol above

### Gate P0
- `make validate-local` passes
- Backend health check returns 200
- At least 8 of 10 existing services import successfully
- D-item verification results recorded

---

## Phase 1 -- Core Wiring into graph.py
**Complexity:** L
**Estimated touch points:** 1-3 files in agent-api

**Purpose:** Connect 5 existing but unwired services into the graph.py turn pipeline. This is the highest-value integration work -- it makes snapshot writing, brain extraction, drift detection, citation auditing, and specialist routing actually execute during conversations.

### Blast Radius
- **Services affected:** agent-api (port 8095)
- **Pages affected:** None (backend enrichment, no UI change)
- **Downstream consumers:** turn_snapshots table, brain facts, drift alerts, specialist context

### Tasks
- P1-01: **Create `_post_turn_enrichment()` coroutine** in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`:
  - This is a new async function that orchestrates post-turn work
  - Called via `asyncio.create_task()` after the assistant response is generated
  - All calls inside are wrapped in try/except with logging -- individual failures must not crash the enrichment
  - **Checkpoint:** Agent-api still starts: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- P1-02: **Wire snapshot_writer.write() into enrichment** (B9.1):
  - Build a `TurnSnapshot` from the current turn's data and call `snapshot_writer.write()`
  - Populate: thread_id, turn_number, user_id, rendered_system_prompt, model_name, raw_completion, token counts, latency_ms
  - Evidence: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/snapshot_writer.py`
- P1-03: **Wire brain_extraction.trigger_brain_extraction() into enrichment**:
  - brain_extraction may already be imported in graph.py -- verify and connect
  - Pass deal_id, thread_id, assistant response, and brain context
  - Evidence: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/brain_extraction.py`
- P1-04: **Wire drift_detection into enrichment** (B8.1):
  - After brain extraction, call `check_staleness()` and `detect_contradictions()`
  - If stale, log a warning. If contradictions found, log them.
  - Evidence: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/drift_detection.py`
- P1-05: **Wire citation_audit into enrichment** (B1.2):
  - If assistant response contains `[cite-N]` patterns, call `audit_citations()`
  - Log the quality score result
  - Evidence: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/security/citation_audit.py`
- P1-06: **Wire node_registry.route() into pre-LLM-call path** (B4.2):
  - Before the main LLM call, call `node_registry.route(query, context)`
  - If a specialist returns a result with confidence >= 0.6, enhance the system prompt with specialist context (add specialist analysis as additional context)
  - Do NOT replace the main LLM response -- specialists AUGMENT, not replace
  - Evidence: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py`
- P1-07: **Verify no import cycles** -- run full import chain check
- P1-08: **Functional gate: simulate a turn** -- if agent-api is running, trigger a test conversation turn and verify a snapshot record was written to the turn_snapshots table
  - **Decision Tree:**
    - **IF** agent-api is running -> send test message, check DB for snapshot
    - **ELSE** -> rely on import check + code review, note functional test deferred
- P1-09: **Write checkpoint**

### Rollback Plan
1. `git -C /home/zaks/zakops-agent-api checkout -- apps/agent-api/app/core/langgraph/graph.py`
2. Restart agent-api: `cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose restart agent-api`
3. Verify: `make validate-local` passes after rollback

### Gate P1
- Agent-api builds and starts: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- No import cycles: `cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "import app.services.snapshot_writer; import app.services.brain_extraction; import app.services.drift_detection; import app.core.security.citation_audit; import app.core.langgraph.node_registry; print('All imports OK')"`
- `make validate-local` passes

---

## Phase 2 -- Service Completion
**Complexity:** M
**Estimated touch points:** 7 files in agent-api

**Purpose:** Add spec-mandated missing features to 7 existing services: admin auth, BackendClient migration, configurable thresholds, proposal expiration, brain export, replay audit log, extractive pre-filter.

### Blast Radius
- **Services affected:** agent-api
- **Pages affected:** None (service-layer only)
- **Downstream consumers:** graph.py enrichment pipeline, admin API endpoints

### Tasks
- P2-01: **Add admin role check to /admin/replay and /admin/counterfactual** (B2.1, B3.1):
  - Verify session has ADMIN role before allowing access
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py` (lines ~514-539)
  - **Checkpoint:** After change, verify non-admin request is rejected with 403
- P2-02: **Migrate raw httpx to BackendClient** in proposal_service.py and export_service.py (B3-01):
  - Replace all `httpx.AsyncClient` usage with `BackendClient` from deal_tools.py
  - Targets:
    - `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py`
    - `/home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py`
  - **Checkpoint:** Both services still import cleanly after migration
- P2-03: **Add configurable thresholds to citation_audit.py** (B3-03):
  - Replace hardcoded 0.5/0.3 similarity thresholds with module-level constants (e.g., `CITATION_HIGH_THRESHOLD`, `CITATION_LOW_THRESHOLD`)
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/security/citation_audit.py`
- P2-04: **Add proposal expiration** (B3-04):
  - Pending proposals older than 24 hours auto-expire. Add `expires_at` field to proposal creation, check in `execute()`
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py`
- P2-05: **Add trigger_type='correction'** to brain summary correction handler (B3-05):
  - When `_handle_correct_brain_summary` executes, pass `trigger_type='correction'` to the backend brain summary endpoint
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py`
- P2-06: **Add brain export appendix** to export_service markdown output (B3-06):
  - When exporting a deal-scoped thread, include current Deal Brain state (facts, risks, summary) as an appendix section
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py`
- P2-07: **Add replay audit log** (B3-07):
  - Structured log entry recording who replayed what and when (lightweight -- logger, not DB table)
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/replay_service.py`
- P2-08: **Add extractive pre-filter to summarizer** (B3-09):
  - Before sending conversation history to LLM for summarization, filter out low-signal turns (short acknowledgments, repeated questions) to reduce token consumption
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py`
- P2-09: **Write checkpoint**

### Decision Tree
- **IF** BackendClient import path is different from `deal_tools.py` -> check actual import path: `grep -r "class BackendClient" /home/zaks/zakops-agent-api/apps/agent-api/`
- **IF** replay endpoint uses a different auth mechanism than session role -> adapt admin check to the actual auth pattern in use

### Rollback Plan
1. `git -C /home/zaks/zakops-agent-api checkout -- apps/agent-api/app/services/proposal_service.py apps/agent-api/app/services/export_service.py apps/agent-api/app/api/v1/chatbot.py apps/agent-api/app/core/security/citation_audit.py apps/agent-api/app/services/replay_service.py apps/agent-api/app/services/summarizer.py`
2. Restart agent-api
3. Verify: `make validate-local` passes after rollback

### Gate P2
- All modified services import cleanly: run import check for all 7 modified files
- Admin auth rejects non-admin: `curl -X POST http://localhost:8095/admin/replay -H "Content-Type: application/json" -d '{}' | grep -i "403\|admin\|forbidden"` (if agent-api running)
- Proposal service still responds (test with curl if agent-api running)
- `make validate-local` passes

---

## Phase 3 -- Compliance Foundation
**Complexity:** M
**Estimated touch points:** 1-2 new files in agent-api

**Purpose:** Build the legal hold tables and partition automation function that block future compliance features (GDPR, retention policy).

### Blast Radius
- **Services affected:** agent-api (database schema only)
- **Pages affected:** None
- **Downstream consumers:** Retention policy engine (COL-V2-BUILD-001B or later), GDPR pipeline (future)

### Tasks
- P3-01: **Check existing migration numbers** -- `ls /home/zaks/zakops-agent-api/apps/agent-api/migrations/*.sql | sort`
  - **Decision Tree:**
    - **IF** migration 029 already exists -> pick next available number
    - **ELSE** -> use 029
  - **Checkpoint:** Migration number confirmed as unique
- P3-02: **Create migration for legal_hold_locks table** per S7.5:
  - `legal_hold_locks`: thread_id (FK to chat_threads or TEXT), hold_type (VARCHAR), hold_reason (TEXT), set_by (VARCHAR), set_at (TIMESTAMPTZ DEFAULT now()), released_at (TIMESTAMPTZ NULL)
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql` (new file)
- P3-03: **Create legal_hold_log table** in same migration:
  - `legal_hold_log`: id (serial PK), thread_id, action (VARCHAR: 'set', 'release'), hold_type (VARCHAR), actor (VARCHAR), reason (TEXT), created_at (TIMESTAMPTZ DEFAULT now())
- P3-04: **Create create_monthly_partitions() PL/pgSQL function** in same migration:
  - Function signature: `create_monthly_partitions(table_name TEXT, months_ahead INTEGER DEFAULT 3)`
  - Creates monthly range partitions for tables like turn_snapshots and chat_messages
  - Idempotent -- does not fail if partition already exists (use `IF NOT EXISTS`)
- P3-05: **Apply migration** to zakops_agent database:
  - `psql -h localhost -U agent -d zakops_agent -f /home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql`
  - **Decision Tree:**
    - **IF** psql connection fails -> record failure, note for manual application
    - **IF** tables already exist -> migration must use `CREATE TABLE IF NOT EXISTS`
- P3-06: **Fix CRLF and ownership** on migration file:
  - `sed -i 's/\r$//' /home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql`
  - `sudo chown zaks:zaks /home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql`
- P3-07: **Write checkpoint**

### Rollback Plan
1. Drop new tables: `psql -h localhost -U agent -d zakops_agent -c "DROP TABLE IF EXISTS legal_hold_log, legal_hold_locks CASCADE;"`
2. Drop function: `psql -h localhost -U agent -d zakops_agent -c "DROP FUNCTION IF EXISTS create_monthly_partitions;"`
3. Remove migration file
4. Verify: `make validate-local` passes after rollback

### Gate P3
- `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_locks"` shows table schema
- `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_log"` shows table schema
- `psql -h localhost -U agent -d zakops_agent -c "\df create_monthly_partitions"` shows function
- `make validate-local` passes

---

## Phase 4 -- Final Verification & Self-Audit
**Complexity:** S
**Estimated touch points:** 0 (verification only) + bookkeeping files

**Purpose:** Run comprehensive validation, produce completion report, update bookkeeping.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** QA successor mission, COL-V2-BUILD-001B

### Tasks
- P4-01: **Run full validation** -- `cd /home/zaks/zakops-agent-api && make validate-local`
- P4-02: **Run TypeScript compilation** -- `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P4-03: **Import check all modified services** -- re-run import checks for every file modified in Phases 1-3
- P4-04: **Verify backend brain endpoints still accessible** -- `curl -sf http://localhost:8091/api/deals/test-id/brain`
- P4-05: **Update CHANGES.md** -- record all changes in `/home/zaks/bookkeeping/CHANGES.md`
- P4-06: **Produce completion report** -- write `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md` with:
  - Phase-by-phase results
  - Files created and modified
  - Items completed (mapped to actionable items register IDs)
  - Validation results
  - Evidence paths for every AC
- P4-07: **Fix CRLF and ownership** on any new files:
  - `find /home/zaks/zakops-agent-api/apps/agent-api/migrations/ -name "*.sql" -newer /home/zaks/bookkeeping/CHANGES.md | xargs -r sed -i 's/\r$//'`
  - `sudo chown -R zaks:zaks /home/zaks/bookkeeping/docs/_qa_evidence/`
- P4-08: **Update final checkpoint**

### Gate P4
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All modified services import without error
- CHANGES.md updated
- Completion report written

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    |
    v
Phase 1 (Core Wiring -- graph.py)
    |
    v
Phase 2 (Service Completion) --------+
    |                                 | (parallel OK)
    v                                 v
Phase 3 (Compliance Foundation)   [can run parallel with P2]
    |                                 |
    +------- merge ----+--------------+
                       |
                       v
              Phase 4 (Final Verification)
```

Phases execute primarily sequentially: 0 -> 1 -> 2 -> 3 -> 4. Phases 2 and 3 have no dependency on each other and could run in parallel if context allows.

---

## Acceptance Criteria

### AC-1: Post-Turn Enrichment Fires
graph.py `_post_turn_enrichment()` invokes snapshot_writer.write(), brain_extraction.trigger_brain_extraction(), drift_detection.check_staleness() + detect_contradictions(), and citation_audit.audit_citations() (for responses with `[cite-N]`) as non-blocking `asyncio.create_task()` calls.

### AC-2: Node Registry Specialist Routing Integrated
node_registry.route() is called in graph.py pre-LLM-call path. Specialist results with confidence >= 0.6 enhance the system prompt. Specialists augment, not replace.

### AC-3: Admin Auth on Replay and Counterfactual
`/admin/replay` and `/admin/counterfactual` endpoints reject non-admin users with HTTP 403.

### AC-4: BackendClient Migration Complete
All agent-api services that call zakops-backend use BackendClient. No raw `httpx.AsyncClient` remains for backend calls in proposal_service.py or export_service.py.

### AC-5: Legal Hold Tables Exist
`legal_hold_locks` and `legal_hold_log` tables exist in zakops_agent database with correct schema.

### AC-6: Partition Function Exists
`create_monthly_partitions()` PL/pgSQL function exists in zakops_agent database.

### AC-7: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes. No test breakage. All existing services still import cleanly.

### AC-8: Bookkeeping Complete
CHANGES.md updated with all changes. Completion report written at `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md`. Checkpoint file updated.

---

## Guardrails

1. **Scope: Phases 0-4 only** -- do NOT build reflexion, cognitive intelligence, ambient UI, PlanAndExecuteGraph, GDPR service, or dashboard components. Those are COL-V2-BUILD-001B and COL-V2-BUILD-001C.
2. **Generated files** -- never edit `*.generated.ts` or `*_models.py`. Use bridge files.
3. **Migration safety** -- do not modify existing migrations (004, 028, or any existing agent-api migrations). Only create new.
4. **Backend repo READ-ONLY** -- do NOT modify `/home/zaks/zakops-backend/`. It is already built. Only wire agent-api to use its endpoints.
5. **Fire-and-forget for enrichment** -- post-turn enrichment MUST NOT block user response. Use `asyncio.create_task()`.
6. **Contract surface discipline** -- run `make sync-all-types` if any API boundary changes.
7. **Surface 9 compliance** for any dashboard touches (none expected in this sub-mission).
8. **WSL safety** -- strip CRLF from new files (`sed -i 's/\r$//'`), fix ownership (`sudo chown zaks:zaks`) on files under /home/zaks/.
9. **Port 8090 is FORBIDDEN** -- never use or reference.
10. **BackendClient mandatory** -- no raw httpx.AsyncClient in agent-api services for backend calls.
<!-- Adopted from Improvement Area IA-10 -->
11. **Test naming convention** -- if any tests are created during this mission, test names must contain functional keywords (e.g., "enrichment", "snapshot", "admin_auth") that QA grep patterns can find.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify the backend brain endpoints respond, not just the health check?"
- [ ] "Did I record which D-items exist vs. need building?"
- [ ] "Did all 10 service imports succeed? If not, which failed and why?"
- [ ] "Does `make validate-local` pass at baseline?"

### After every code change:
- [ ] "Am I using BackendClient, not raw httpx?"
- [ ] "Is this enrichment fire-and-forget (asyncio.create_task) or blocking the user response?"
- [ ] "Did I add a spec section reference in the docstring?"
- [ ] "Did I run `make sync-all-types` if I changed an API boundary?"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks, not just assume they pass?"
- [ ] "Did I update the checkpoint file?"
- [ ] "Did I create new files? -> CRLF stripped? Ownership fixed?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now, not earlier?"
- [ ] "Does `npx tsc --noEmit` pass?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce the completion report with evidence paths for every AC?"
- [ ] "Did I create ALL files listed in the 'Files to Create' table?"
- [ ] "Is the scope correct -- did I accidentally build anything from 001B or 001C?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py` | P1 | Post-turn enrichment coroutine, node_registry pre-LLM wiring |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py` | P2 | BackendClient migration, proposal expiration, trigger_type |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py` | P2 | BackendClient migration, brain export appendix |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py` | P2 | Admin role check on /admin/replay and /admin/counterfactual |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/security/citation_audit.py` | P2 | Configurable thresholds |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/replay_service.py` | P2 | Replay audit log |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py` | P2 | Extractive pre-filter |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql` | P3 | Legal hold tables + partition function |
| `/home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001A.md` | P0+ | Multi-session checkpoint |
| `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md` | P4 | Completion report |

### Files to Read (sources of truth -- do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` | Design specification (3,276 lines) |
| `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` | Actionable items register (83 items) |
| `/home/zaks/zakops-backend/src/core/agent/deal_brain_service.py` | Backend brain service -- reference for API shapes and method signatures |
| `/home/zaks/zakops-backend/src/api/orchestration/routers/brain.py` | Backend brain router -- reference for endpoint contracts and URL patterns |
| `/home/zaks/zakops-backend/db/migrations/028_deal_brain.sql` | Backend migration -- reference for table schemas |

---

## Stop Condition

This mission is DONE when:
- All 8 acceptance criteria (AC-1 through AC-8) are met
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All changes recorded in CHANGES.md
- Completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md`
- Checkpoint file updated to reflect completion

**Do NOT proceed to:**
- Building reflexion, chain-of-verification, or cognitive intelligence services -- those are COL-V2-BUILD-001B
- Building ambient UI, dashboard components, PlanAndExecuteGraph, or GDPR services -- those are COL-V2-BUILD-001C
- Running the QA successor mission -- that is a separate session
- Modifying zakops-backend -- the backend is READ-ONLY for this mission
- Modifying the COL-DESIGN-SPEC-V2.md -- the spec is a read-only source of truth

---

## Lab Loop Configuration

For automated execution via Lab Loop:

```
TASK_ID=COL-V2-BUILD-001A
REPO_DIR=/home/zaks/zakops-agent-api
GATE_CMD="make validate-local && cd apps/dashboard && npx tsc --noEmit"
```

---

*End of Mission Prompt -- COL-V2-BUILD-001A*

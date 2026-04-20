# MISSION: COL-V2-BUILD-001
## Build and Wire COL-V2 Actionable Items — Backend Brain, Core Integration, Intelligence Services
## Date: 2026-02-13
## Classification: Feature Build + Service Integration
## Prerequisite: COL-V2 QA Verification Complete (19 missions, 516 gates — COMPLETION-REPORT.md)
## Successor: QA-COL-BUILD-VERIFY-001

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash or context compaction, run:

```bash
# 1. Determine current phase
cat /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001.md

# 2. Check validation state
cd /home/zaks/zakops-agent-api && make validate-local

# 3. Check for partial work
git -C /home/zaks/zakops-agent-api status
git -C /home/zaks/zakops-backend status
```

Resume from the checkpoint file. Do not re-execute completed phases.

---

## Context Checkpoint Protocol
<!-- Adopted from Improvement Area IA-1, IA-7 -->

This is an XL multi-session mission. After completing **each phase**, write a structured checkpoint:

```bash
# Write checkpoint after every phase completion
cat > /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001.md << 'CHECKPOINT'
Mission: COL-V2-BUILD-001
Last completed phase: Phase {N}
Next phase: Phase {N+1}
Validation state: {PASS/FAIL + details}
Open decision trees: {any unresolved forks}
Files modified this session: {list}
CHECKPOINT
```

---

## Mission Objective

**Build and integrate 83 actionable items** identified by the COL-V2 QA verification sweep (19 missions, 516 gates). This mission covers:

1. **Backend DealBrainService** — 8 endpoints/methods in zakops-backend that block the brain extraction pipeline
2. **Core wiring** — Connect 7 existing services into graph.py turn pipeline (citation audit, drift detection, snapshot writer)
3. **Service completion** — Add spec-mandated features to 10 existing services that have partial implementations
4. **Database verification** — Confirm 7 items that couldn't be checked during QA (partition functions, indexes, views)
5. **Compliance foundation** — Legal hold tables, partition automation
6. **Intelligence services** — Reflexion, cognitive intelligence, ambient features

**What this mission is NOT:**
- This is NOT a QA mission — no verification families or evidence capture
- This is NOT a redesign — existing services are EXTENDED, not rewritten
- This is NOT a UI-first mission — backend/service work takes priority; UI phases (9) come last

**Source material:**
- Actionable items register: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md`
- QA completion report: `/home/zaks/bookkeeping/docs/_qa_evidence/COMPLETION-REPORT.md`
- Design specification: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` (3,276 lines)
- QA orchestrator: `/home/zaks/bookkeeping/docs/QA-COL-ORCHESTRATOR-PROMPT.md` (4,163 lines)

---

## Context

The COL-V2 QA verification executed 516 gates across 19 missions, finding:
- 213 PASS, 65 REMEDIATED (by Codex), ~195 true SCOPE_GAP, 8 FAIL (sandbox-blocked)
- QA gates searched wrong file paths for several services, inflating the SCOPE_GAP count from 230 to ~195 after manual audit correction
- 10 existing service files have partial implementations needing completion
- 8 backend endpoints are missing entirely (DealBrainService)
- 31 features have zero implementation files

Key files discovered during post-QA audit that QA gates missed:

| File | Lines | What It Implements |
|------|-------|--------------------|
| `apps/agent-api/app/core/security/citation_audit.py` | 144 | CitationCheck, audit_citations(), keyword similarity |
| `apps/agent-api/app/services/replay_service.py` | 234 | ReplayService, `/admin/replay` endpoint |
| `apps/agent-api/app/services/counterfactual_service.py` | 224 | CounterfactualService, `/admin/counterfactual` endpoint |
| `apps/agent-api/app/core/langgraph/node_registry.py` | 296 | NodeRegistry, 3 built-in specialists, route() |
| `apps/agent-api/app/services/proposal_service.py` | 299 | 9 PROPOSAL_HANDLERS, execute(), FOR UPDATE locking |
| `apps/agent-api/app/services/export_service.py` | 258 | Markdown/JSON export, attach_to_deal() |
| `apps/agent-api/app/services/snapshot_writer.py` | 233 | TurnSnapshot (26 fields), write/get/list |
| `apps/agent-api/app/services/drift_detection.py` | 184 | Staleness, contradiction, decay confidence |
| `apps/agent-api/app/services/brain_extraction.py` | 320 | Fact/risk/decision/ghost extraction |
| `apps/agent-api/app/services/momentum_calculator.py` | 113 | 5-component momentum score |

---

## Glossary

| Term | Definition |
|------|-----------|
| Deal Brain | Per-deal knowledge accumulator — facts, risks, decisions, ghost knowledge, summary (S4) |
| Ghost Knowledge | Facts the user references that don't exist in the Deal Brain (QW-1) |
| Turn Snapshot | Complete capture of model input/output for a single conversational turn (S6) |
| Reflexion | Self-critique loop: generate → critique → revise (S8.3) |
| Drift Detection | Brain staleness check + contradiction detection + decay curve (S4.5) |
| HITL | Human-in-the-loop — proposals requiring user approval before execution |
| RRF | Reciprocal Rank Fusion — method for combining dense and sparse retrieval results |
| Ambient Intelligence | Background features: briefings, anomaly detection, smart paste (S17) |

---

## Architectural Constraints

Per standing constraints in CLAUDE.md and contract surface discipline. Mission-specific additions:

- **BackendClient is mandatory for agent→backend calls** — all DealBrainService calls from agent-api MUST use `BackendClient` from `deal_tools.py`, never raw `httpx.AsyncClient`. Some existing services (proposal_service.py, export_service.py) use raw httpx — these must be migrated.
- **Fire-and-forget for non-critical paths** — brain extraction, drift detection, and snapshot writing are post-turn enrichments. They MUST NOT block the user-facing response. Use `asyncio.create_task()` with exception logging, not `await`.
- **Singleton pattern for services** — all COL-V2 services use module-level singleton instances (e.g., `replay_service = ReplayService()`). Preserve this pattern.
- **Spec section references in docstrings** — every COL-V2 service module MUST have a docstring citing its spec section (e.g., `COL-DESIGN-SPEC-V2, Section 4.5`). Existing services already follow this.
- **Admin endpoints require role check** — `/admin/replay` and `/admin/counterfactual` currently only check session auth. They must additionally verify the user has ADMIN role per S6.4/S6.5.

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
# In graph.py turn handler — blocks user response
await snapshot_writer.write(snapshot)
await trigger_brain_extraction(deal_id, ...)
await check_and_report_drift(...)
```

### RIGHT: Fire-and-forget for enrichment
```python
# In graph.py turn handler — non-blocking
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
| 1 | Backend DealBrainService endpoints don't match the request shapes agent-api sends (schema mismatch) | HIGH | Brain pipeline silently fails | Phase 1 gate: round-trip test with curl from agent-api container to backend |
| 2 | graph.py post-turn enrichment (Phase 2) introduces import cycle between services | MEDIUM | Agent-api fails to start | Phase 2 gate: `python -c "from app.core.langgraph.graph import build_graph"` |
| 3 | New migration in zakops-backend collides with existing Alembic head | MEDIUM | Backend won't start | Phase 1 task: check `alembic heads` before creating migration |
| 4 | Context window exhaustion — 10 phases with 83 items | HIGH | Later phases get sloppy | IA-1/IA-7 checkpoints; context checkpoint after Phase 4 |
| 5 | Raw httpx→BackendClient migration in proposal_service.py breaks existing proposal flow | MEDIUM | Proposal execution regresses | Phase 3 gate: verify proposal execute endpoint still responds correctly |

---

## Phase 0 — Discovery & Baseline
**Complexity:** M
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify the codebase state matches the actionable items register and establish a clean validation baseline.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Run baseline validation** — `cd /home/zaks/zakops-agent-api && make validate-local`
  - **Checkpoint:** Must exit 0. If not, fix before proceeding.
- P0-02: **Verify backend is running** — `curl -sf http://localhost:8091/health`
  - **Decision Tree:**
    - **IF** backend is running → proceed to Phase 1
    - **ELSE** → start backend: `cd /home/zaks/zakops-backend && docker compose up -d backend --no-deps`
- P0-03: **Verify database access** — Run the 7 verification-only items (D1-D7) from the actionable items register:
  - `psql -h localhost -U agent -d zakops_agent -c "\dt turn_snapshots"` (D1)
  - `psql -h localhost -U zakops -d zakops -c "\d deal_budgets"` (D2)
  - `psql -h localhost -U agent -d zakops_agent -c "SELECT * FROM deal_cost_summary LIMIT 1"` (D7)
  - Record which items exist and which don't — this informs Phase 2 and Phase 4 scope.
- P0-04: **Verify existing services load** — `cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "from app.services.replay_service import replay_service; print('OK')"`
  - Repeat for: `snapshot_writer`, `counterfactual_service`, `export_service`, `proposal_service`, `brain_extraction`, `drift_detection`, `momentum_calculator`
- P0-05: **Read COL-DESIGN-SPEC-V2.md** — Read the spec sections referenced by Phase 1 items: S4.2, S4.3, S4.6, S15.4
  - Evidence: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md`
- P0-06: **Write checkpoint** — per Continuity Protocol above

### Gate P0
- `make validate-local` passes
- Backend health check returns 200
- At least 6 of 8 existing services import successfully
- D-items verification results recorded

---

## Phase 1 — Backend DealBrainService (Items A1–A8)
**Complexity:** L
**Estimated touch points:** 4–6 files in zakops-backend

**Purpose:** Build the backend DealBrainService that the agent-api brain extraction pipeline depends on. This unblocks Phases 2–3.

### Blast Radius
- **Services affected:** zakops-backend (port 8091)
- **Pages affected:** None directly (backend-only)
- **Downstream consumers:** agent-api brain_extraction.py, proposal_service.py

### Tasks
- P1-01: **Check existing Alembic state** — `cd /home/zaks/zakops-backend && alembic heads` to identify current head revision
  - **Checkpoint:** Record the head revision. New migration must descend from it.
- P1-02: **Create Alembic migration for deal_brain table** — Schema per S4.2: `deal_id` (FK to deals), `facts` (JSONB), `risks` (JSONB), `decisions` (JSONB), `ghost_knowledge` (JSONB), `summary` (TEXT), `version` (INTEGER DEFAULT 1), `last_updated` (TIMESTAMPTZ), `last_summarized_turn` (INTEGER), unique constraint on `deal_id`
  - Target: `/home/zaks/zakops-backend/db/migrations/versions/` (new Alembic revision)
  - **Decision Tree:**
    - **IF** deal_brain table already exists (check `\d deal_brain` in psql) → skip migration, proceed to P1-03
    - **ELSE** → create migration
- P1-03: **Create brain_history table migration** — Schema per S4.6: `id` (serial PK), `deal_id`, `version` (INTEGER), `facts_snapshot` (JSONB), `summary_snapshot` (TEXT), `changed_by` (VARCHAR), `trigger_type` (VARCHAR: 'extraction', 'correction', 'manual'), `created_at` (TIMESTAMPTZ DEFAULT now())
  - **Decision Tree:**
    - **IF** brain_history already exists → skip
    - **ELSE** → add to same migration or create new revision
- P1-04: **Build DealBrainService class** — per S4.2-S4.3, implement:
  - `get_brain(deal_id)` → returns brain object or creates empty brain
  - `update_facts(deal_id, new_facts, source_thread_id, source_turn)` → merge with confidence scoring
  - `update_risks(deal_id, new_risks)` → dedup by description similarity
  - `update_summary(deal_id, summary_text, trigger_type)` → version increment + brain_history INSERT
  - Target: `/home/zaks/zakops-backend/app/services/deal_brain.py` (new file)
- P1-05: **Create API endpoints** — per S4.2-S4.3:
  - `GET /api/deals/{id}/brain` → DealBrainService.get_brain()
  - `POST /api/deals/{id}/brain/facts` → DealBrainService.update_facts()
  - `PUT /api/deals/{id}/brain/summary` → DealBrainService.update_summary()
  - Target: `/home/zaks/zakops-backend/app/api/v1/deals.py` (add to existing router)
  - **Checkpoint:** After wiring, `curl -sf http://localhost:8091/api/deals/test-id/brain` should return valid JSON (empty brain or 404).
- P1-06: **Create brain_history INSERT trigger** — PL/pgSQL trigger on deal_brain that copies the old row to brain_history on UPDATE
  - Target: include in migration from P1-02/P1-03
- P1-07: **Rebuild and restart backend** — `cd /home/zaks/zakops-backend && docker compose build backend && docker compose up -d backend --no-deps`
- P1-08: **Write checkpoint**

### Rollback Plan
1. `cd /home/zaks/zakops-backend && alembic downgrade -1` (reverts migration)
2. `git checkout -- app/services/deal_brain.py app/api/v1/deals.py`
3. Rebuild backend: `docker compose build backend && docker compose up -d backend --no-deps`

### Gate P1
- Backend starts without errors: `curl -sf http://localhost:8091/health`
- `GET /api/deals/{any-uuid}/brain` returns JSON (200 with empty brain or 404)
- `POST /api/deals/{any-uuid}/brain/facts` accepts a test payload and returns 200
- brain_history table exists: `psql -h localhost -U zakops -d zakops -c "\d brain_history"`
- `make validate-local` still passes (agent-api side unaffected)

---

## Phase 2 — Core Wiring into graph.py (Items B1.2, B8.1, B9.1)
**Complexity:** L
**Estimated touch points:** 3–5 files in agent-api

**Purpose:** Connect existing but unwired services (citation audit, drift detection, snapshot writer) into the graph.py turn pipeline as fire-and-forget post-turn enrichments.

### Blast Radius
- **Services affected:** agent-api (port 8095)
- **Pages affected:** None (backend enrichment, no UI change)
- **Downstream consumers:** turn_snapshots table, brain facts, drift alerts

### Tasks
- P2-01: **Create post-turn enrichment function** in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`:
  - After the assistant response is generated, call a new `_post_turn_enrichment()` coroutine via `asyncio.create_task()`
  - This function orchestrates: (1) snapshot_writer.write(), (2) trigger_brain_extraction(), (3) drift_detection checks, (4) citation_audit if citations present
  - All calls are fire-and-forget with try/except logging
  - **Checkpoint:** Agent-api still starts: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- P2-02: **Wire citation_audit into post-completion** — After LLM response, if response contains `[cite-N]` patterns, call `audit_citations()` and log the result. Store quality_score in the turn snapshot's `citations_extracted` field.
  - Target: the enrichment function from P2-01
- P2-03: **Wire drift_detection into post-turn** — After brain extraction, call `check_staleness()` and `detect_contradictions()`. If stale, log a warning. If contradictions found, log them and reduce confidence per the existing logic.
  - Target: the enrichment function from P2-01
- P2-04: **Wire snapshot_writer into post-turn** — Build a `TurnSnapshot` from the current turn's data and call `snapshot_writer.write()`. Populate: thread_id, turn_number, user_id, rendered_system_prompt, model_name, raw_completion, token counts, latency_ms.
  - Target: the enrichment function from P2-01
- P2-05: **Wire node_registry into graph.py** — Before the main LLM call, call `node_registry.route(query, context)`. If a specialist returns a result with confidence >= 0.6, use it to enhance the system prompt (add specialist analysis as context), not to replace the main response.
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
- P2-06: **Write checkpoint**

### Rollback Plan
1. `git checkout -- apps/agent-api/app/core/langgraph/graph.py`
2. Restart agent-api: `cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose restart agent-api`

### Gate P2
- Agent-api builds and starts: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- No import cycles: `cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "import app.services.replay_service; import app.services.snapshot_writer; import app.services.drift_detection; import app.core.security.citation_audit; print('All imports OK')"`
- `make validate-local` passes

---

## Phase 3 — Service Completion (Items B1–B10)
**Complexity:** L
**Estimated touch points:** 10–12 files in agent-api

**Purpose:** Add spec-mandated features to the 10 existing services that have partial implementations.

### Blast Radius
- **Services affected:** agent-api
- **Pages affected:** None (service-layer only)
- **Downstream consumers:** graph.py enrichment pipeline, API endpoints

### Tasks
- P3-01: **Migrate raw httpx to BackendClient** in `proposal_service.py` and `export_service.py` — Replace all `httpx.AsyncClient` usage with `BackendClient` from deal_tools.py
  - Targets: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py`, `/home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py`
  - **Checkpoint:** Both services still import cleanly after migration.
- P3-02: **Add admin role check** to `/admin/replay` and `/admin/counterfactual` endpoints — verify `session.role` includes admin privileges before allowing access
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py` (lines 514-539)
- P3-03: **Add configurable thresholds to citation_audit.py** — Replace hardcoded 0.5/0.3 similarity thresholds with module-level constants or config values
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/security/citation_audit.py`
- P3-04: **Add proposal expiration** — Pending proposals older than 24 hours should be auto-expired. Add an `expires_at` field to proposal creation and a check in `execute()`.
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py`
- P3-05: **Add trigger_type field** to brain history writes — When `_handle_correct_brain_summary` executes, pass `trigger_type='correction'` to the backend brain summary endpoint
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py` (line 235+)
- P3-06: **Add brain export integration** to export_service.py — When exporting a deal-scoped thread, include the current Deal Brain state (facts, risks, summary) as an appendix section in the markdown export
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py`
- P3-07: **Add replay audit log** — Log who replayed what and when, to a structured log entry (not a DB table — lightweight)
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/replay_service.py`
- P3-08: **Add counterfactual history** — Store counterfactual analysis results as a JSONB field on the turn_snapshot (reuse existing infrastructure)
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/counterfactual_service.py`
- P3-09: **Add extractive pre-filter to summarizer** — Before sending conversation history to LLM for summarization, filter out low-signal turns (short acknowledgments, repeated questions) to reduce token consumption
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py`
- P3-10: **Write checkpoint**

### Rollback Plan
1. `git checkout -- apps/agent-api/app/services/*.py apps/agent-api/app/api/v1/chatbot.py apps/agent-api/app/core/security/citation_audit.py`
2. Restart agent-api

### Gate P3
- All modified services import cleanly: run import check for all 7 modified files
- Proposal execute endpoint responds (test with curl if agent-api is running)
- Export service produces markdown that includes a brain appendix section (unit test or manual check)
- `make validate-local` passes

---

## Phase 4 — Compliance Foundation (Items C1, C2)
**Complexity:** M
**Estimated touch points:** 2–3 files in agent-api

**Purpose:** Build the legal hold and partition automation foundation that blocks compliance features.

### Blast Radius
- **Services affected:** agent-api (database schema)
- **Pages affected:** None
- **Downstream consumers:** Retention policy engine (future), GDPR pipeline (future)

### Tasks
- P4-01: **Create migration 029 — Legal Hold Tables** per S7.5:
  - `legal_hold_locks`: thread_id (FK), hold_type (VARCHAR), hold_reason (TEXT), set_by (VARCHAR), set_at (TIMESTAMPTZ), released_at (TIMESTAMPTZ NULL)
  - `legal_hold_log`: id (serial PK), thread_id, action (VARCHAR: 'set', 'release'), hold_type, actor (VARCHAR), reason (TEXT), created_at (TIMESTAMPTZ)
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/migrations/` (new SQL file)
  - **Decision Tree:**
    - **IF** tables already exist → skip, record in checkpoint
    - **ELSE** → create migration following existing migration naming convention (sequential number)
- P4-02: **Create partition automation function** per S6.6:
  - PL/pgSQL function `create_monthly_partitions(table_name, months_ahead)` that creates monthly range partitions for turn_snapshots and chat_messages
  - Include in migration 029 or separate migration
  - **Decision Tree:**
    - **IF** function already exists (check D1 from Phase 0) → skip
    - **ELSE** → create
- P4-03: **Run migration** — Apply the new migration to zakops_agent database
- P4-04: **Write checkpoint**

### Rollback Plan
1. Drop new tables: `psql -h localhost -U agent -d zakops_agent -c "DROP TABLE IF EXISTS legal_hold_log, legal_hold_locks CASCADE;"`
2. Drop function: `psql -h localhost -U agent -d zakops_agent -c "DROP FUNCTION IF EXISTS create_monthly_partitions;"`

### Gate P4
- `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_locks"` shows table schema
- `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_log"` shows table schema
- `psql -h localhost -U agent -d zakops_agent -c "\df create_monthly_partitions"` shows function
- `make validate-local` passes

---

<!-- Adopted from Improvement Area IA-1: Context checkpoint at midpoint -->

## CONTEXT CHECKPOINT — Phases 0–4 Complete

If context is constrained after Phase 4, summarize progress, commit intermediate work with
`git add -p && git commit -m "COL-V2-BUILD-001: Phases 0-4 (backend brain + core wiring + service completion + compliance foundation)"`,
update the checkpoint file, and continue in a fresh session.

---

## Phase 5 — Reflexion & Chain-of-Verification (Items C3, C4)
**Complexity:** L
**Estimated touch points:** 3–4 new files in agent-api

**Purpose:** Build the self-critique and verification pipeline that improves response quality.

### Blast Radius
- **Services affected:** agent-api
- **Pages affected:** None (backend intelligence)
- **Downstream consumers:** graph.py turn pipeline, turn_snapshots

### Tasks
- P5-01: **Build ReflexionCritique service** per S8.3-S8.4:
  - Class: `ReflexionService` with `critique(response, evidence, brain_facts)` method
  - Returns: `CritiqueResult` (Pydantic model) with `issues: list[str]`, `severity: str`, `should_revise: bool`, `revised_response: str | None`
  - Logic: Use a smaller/faster LLM call to evaluate the main response against evidence. If issues found and severity > threshold, generate a revised response.
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` (new file)
- P5-02: **Build Chain-of-Verification** per S8.5:
  - Function: `verify_claims(response_text, evidence_sources)` → list of verified/unverified claims
  - Logic: Extract claims from response, check each against evidence, flag unsupported claims
  - Can be integrated into ReflexionService or separate module
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` or `/home/zaks/zakops-agent-api/apps/agent-api/app/services/claim_verification.py`
- P5-03: **Wire reflexion into graph.py** — After main LLM response but before sending to user, optionally run reflexion critique. Use a config flag to enable/disable (default: enabled for deal-scoped chats only).
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
- P5-04: **Store critique_result in turn snapshot** — The TurnSnapshot dataclass already has a `critique_result` field. Populate it from the reflexion output.
- P5-05: **Write checkpoint**

### Rollback Plan
1. Remove new files: `rm apps/agent-api/app/services/reflexion.py`
2. Revert graph.py changes: `git checkout -- apps/agent-api/app/core/langgraph/graph.py`

### Gate P5
- ReflexionService imports: `python -c "from app.services.reflexion import ReflexionService; print('OK')"`
- CritiqueResult model validates: `python -c "from app.services.reflexion import CritiqueResult; CritiqueResult(issues=[], severity='none', should_revise=False); print('OK')"`
- graph.py still builds: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- `make validate-local` passes

---

## Phase 6 — Cognitive Intelligence (Items C8–C15)
**Complexity:** XL
**Estimated touch points:** 6–8 new files in agent-api + 2–3 dashboard files

**Purpose:** Build the cognitive intelligence services: decision fatigue sentinel, stall predictor, ghost knowledge SSE, momentum UI.

### Blast Radius
- **Services affected:** agent-api, dashboard
- **Pages affected:** Chat interface (ghost knowledge toast), deal detail (momentum colors)
- **Downstream consumers:** SSE event stream, dashboard components

### Tasks
- P6-01: **Build DecisionFatigueSentinel** per S14.1:
  - Track decisions per session (5 decisions in 2 hours → warning, 3-hour continuous session → warning)
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py` (new file)
- P6-02: **Build StallPredictor** per S14.2:
  - Compare days_in_stage against median stage duration; predict stall probability
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/stall_predictor.py` (new file)
- P6-03: **Add ghost_knowledge_flags to SSE events** per S14.7:
  - When brain extraction detects ghost knowledge, emit an SSE event with the flagged items
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py` (add new event type)
- P6-04: **Add momentum UI color bands** per S20:
  - In the dashboard deal detail page, render momentum score with green (70+), amber (40-69), red (0-39) color coding
  - Target: Dashboard deal detail component (identify the correct file during discovery)
  - Per Surface 9 design system rules
- P6-05: **Add spaced repetition service** per S14.5:
  - `get_review_facts(deal_id)` → returns facts below decay threshold that need user reinforcement
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py` (new file)
  - Depends on: drift_detection.py `compute_decay_confidence()`
- P6-06: **Write checkpoint**

### Decision Tree
- **IF** dashboard deal detail page doesn't have a momentum display yet → create one per Surface 9
- **ELSE IF** momentum display exists but without colors → add color bands only

### Rollback Plan
1. Remove new service files
2. Revert SSE events: `git checkout -- apps/agent-api/app/schemas/sse_events.py`
3. Revert dashboard changes: `git checkout -- apps/dashboard/...`

### Gate P6
- All new services import: fatigue_sentinel, stall_predictor, spaced_repetition
- SSE events schema still validates (no broken discriminated union)
- Dashboard compiles: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- `make validate-local` passes

---

## Phase 7 — RAG Enhancement & Export Completion (Items C5, C7, B5, B6.4)
**Complexity:** M
**Estimated touch points:** 3–4 files across agent-api and Zaks-llm

**Purpose:** Enhance retrieval quality and complete the export/memo features.

### Blast Radius
- **Services affected:** agent-api, Zaks-llm (RAG service)
- **Pages affected:** None directly
- **Downstream consumers:** Chat responses (better retrieval), export downloads

### Tasks
- P7-01: **Verify RRF k=60 in RAG service** — Check `/home/zaks/Zaks-llm/` for the hybrid retrieval implementation. Verify the fusion parameter.
  - **Decision Tree:**
    - **IF** RRF with k=60 exists → record as verified, skip
    - **ELSE IF** hybrid exists but k != 60 → update the parameter
    - **ELSE** → this is a Zaks-llm change, create a TODO and proceed (out of primary scope)
- P7-02: **Add HyDE query option** per S11.3 — Add a `hyde` parameter to `rag_rest.py` that generates a hypothetical document from the query before embedding
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_rest.py`
- P7-03: **Add RankedChunk type** per S11 — Create a Pydantic model for typed retrieval results with `score`, `source`, `relevance`, `chunk_text`
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/` (new or existing schema file)
- P7-04: **Build Living Deal Memo** per S12.3 — Add a `generate_memo(deal_id)` method to ExportService that produces a structured memo with 7 sections: Executive Summary, Key Facts, Risk Assessment, Decision History, Open Items, Momentum Analysis, Recommendation
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py`
- P7-05: **Write checkpoint**

### Rollback Plan
1. `git checkout -- apps/agent-api/app/services/rag_rest.py apps/agent-api/app/services/export_service.py`

### Gate P7
- RankedChunk model validates: `python -c "from app.schemas... import RankedChunk; print('OK')"`
- Export service memo generation works (dry run or unit test)
- `make validate-local` passes

---

## Phase 8 — Agent Architecture (Items C24–C26, B4.2–B4.4)
**Complexity:** L
**Estimated touch points:** 4–5 files in agent-api

**Purpose:** Build the PlanAndExecute graph and complete multi-specialist delegation.

### Blast Radius
- **Services affected:** agent-api
- **Pages affected:** None (architecture-level)
- **Downstream consumers:** graph.py routing, specialist nodes

### Tasks
- P8-01: **Build PlanAndExecuteGraph** per S19.2:
  - Decomposes complex queries into steps: (1) plan steps, (2) execute each step, (3) synthesize results
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py` (new file)
- P8-02: **Add 4th specialist (Compliance/Regulatory)** to node_registry — per S19.4
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py`
- P8-03: **Add specialist response synthesis** — When multiple specialists contribute to a query, merge their responses into a coherent answer
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py`
- P8-04: **Add MCP cost/decision ledger** per S19.5 — When MCP tools are called, log cost and decision metadata to the cost_ledger
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py` or MCP integration module
- P8-05: **Write checkpoint**

### Rollback Plan
1. Remove new file: `rm apps/agent-api/app/core/langgraph/plan_execute.py`
2. Revert: `git checkout -- apps/agent-api/app/core/langgraph/node_registry.py apps/agent-api/app/core/langgraph/graph.py`

### Gate P8
- PlanAndExecuteGraph imports: `python -c "from app.core.langgraph.plan_execute import PlanAndExecuteGraph; print('OK')"`
- 4 specialists registered: `python -c "from app.core.langgraph.node_registry import node_registry; assert len(node_registry.list_specialists()) >= 4; print('OK')"`
- `make validate-local` passes

---

## Phase 9 — Ambient Intelligence & UI (Items C16–C23)
**Complexity:** XL
**Estimated touch points:** 8–12 files across agent-api and dashboard

**Purpose:** Build the ambient intelligence features and their dashboard UI components.

### Blast Radius
- **Services affected:** agent-api, dashboard
- **Pages affected:** Chat interface (citation indicators, memory panel, smart paste), deal list (morning briefing, anomaly badges)
- **Downstream consumers:** SSE events, dashboard state

### Tasks
- P9-01: **Build MorningBriefingGenerator** per S17.1:
  - Generates daily briefing: priority deals, momentum deltas, anomalies, action items
  - Scheduled or on-demand via API endpoint
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/morning_briefing.py` (new file)
- P9-02: **Build DealAnomalyDetector** per S17.2:
  - Detects: unusual silence (no activity in N days), activity bursts, pattern deviations
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/anomaly_detector.py` (new file)
- P9-03: **Build SentimentCoach** per S17.5:
  - Per-deal sentiment tracking over time; stores trend data
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py` (new file)
- P9-04: **Build Citation UI Indicators** per S8.2:
  - In chat message display, render citation strength as colored underlines (green=strong, amber=weak, red=orphan)
  - Render "Refined" badge on messages that went through reflexion critique
  - Target: Dashboard chat message component (per Surface 9)
- P9-05: **Build MemoryStatePanel** per S5.4:
  - Sidebar panel showing: Working memory (last 6 messages), Recall (brain facts + summaries), Archival (expired summaries)
  - Target: Dashboard chat sidebar (per Surface 9)
- P9-06: **Build SmartPaste** per S17.4:
  - When user pastes text into chat, extract entities (names, numbers, dates) and offer "Add to Deal Brain" action
  - Target: Dashboard chat input component (per Surface 9)
- P9-07: **Build CommandPalette** per S17.6:
  - Cmd+K shortcut opens palette with context-aware commands (deal actions, navigation, search)
  - Target: Dashboard global component (per Surface 9)
- P9-08: **Write checkpoint**

### Decision Tree
- **IF** building dashboard components → follow Surface 9 design system rules (`.claude/rules/design-system.md`)
- **IF** agent-api is not running → build services first, test UI with mock data

### Rollback Plan
1. Remove new service files from agent-api
2. Revert dashboard component changes: `git checkout -- apps/dashboard/src/...`

### Gate P9
- All new services import cleanly
- Dashboard compiles: `npx tsc --noEmit`
- `make validate-local` passes
- Surface 9 compliance: no design system violations in new components

---

## Phase 10 — Compliance Pipeline (Items C27–C31)
**Complexity:** L
**Estimated touch points:** 3–5 files in agent-api

**Purpose:** Build the GDPR and data retention infrastructure.

### Blast Radius
- **Services affected:** agent-api (database + API)
- **Pages affected:** None (admin-only)
- **Downstream consumers:** Legal hold system, admin panel

### Tasks
- P10-01: **Build retention policy engine** per S7.4:
  - Configurable tiers: 30d (default), 90d (deal-scoped), 365d (legal hold), forever (compliance)
  - Applied per thread based on scope_type and legal_hold status
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/retention_policy.py` (new file)
- P10-02: **Build GDPR deletion automation** per S7.3:
  - `gdpr_purge(user_id)` — deletes all user's threads, messages, snapshots, summaries while respecting legal holds
  - Logs every deletion to legal_hold_log
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py` (new file)
- P10-03: **Build compliance deletion API** per S7.5:
  - `POST /admin/compliance/purge` — accepts user_id, validates admin role, runs GDPR purge, returns audit report
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py` (add admin endpoint)
- P10-04: **Build deletion audit log** per S7.6:
  - Use the legal_hold_log table from Phase 4; add deletion events with who, what, when, why
  - Target: integrate into gdpr_service.py and retention_policy.py
- P10-05: **Write checkpoint**

### Rollback Plan
1. Remove new service files
2. Revert chatbot.py: `git checkout -- apps/agent-api/app/api/v1/chatbot.py`

### Gate P10
- Retention policy imports: `python -c "from app.services.retention_policy import RetentionPolicy; print('OK')"`
- GDPR service imports: `python -c "from app.services.gdpr_service import gdpr_purge; print('OK')"`
- Admin endpoint responds (mock test or curl)
- `make validate-local` passes

---

## Phase 11 — Final Verification & Self-Audit
**Complexity:** M
**Estimated touch points:** 0 (verification only) + bookkeeping files

**Purpose:** Run comprehensive validation, produce completion report, update bookkeeping.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** QA successor mission

### Tasks
- P11-01: **Run full validation** — `cd /home/zaks/zakops-agent-api && make validate-local`
- P11-02: **Run TypeScript compilation** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P11-03: **Verify all new services import** — Run import check for every new file created across all phases
- P11-04: **Verify backend brain endpoints** — curl test for GET/POST brain endpoints
- P11-05: **Count files created and modified** — Produce a summary of all changes
- P11-06: **Update CHANGES.md** — Record all changes from this mission in `/home/zaks/bookkeeping/CHANGES.md`
- P11-07: **Produce completion report** — Write `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001-COMPLETION.md` with:
  - Phase-by-phase results
  - Files created and modified
  - Items completed vs. deferred
  - Validation results
  - Evidence paths for every AC
- P11-08: **Fix CRLF and ownership** — Run `sed -i 's/\r$//'` on any new .sh files, `chown zaks:zaks` on any new files under /home/zaks/

### Gate P11
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All new services import without error
- CHANGES.md updated
- Completion report written

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ▼
Phase 1 (Backend Brain — zakops-backend) ─────────────────────┐
    │                                                          │
    ▼                                                          │
Phase 2 (Core Wiring — graph.py)                               │
    │                                                          │
    ▼                                                          │
Phase 3 (Service Completion) ──────┐                           │
    │                              │                           │
    ▼                              │ (parallel)                │
Phase 4 (Compliance Foundation)    Phase 5 (Reflexion)         │
    │                              │                           │
    └──────────┬───────────────────┘                           │
               │                                               │
               ▼                                               │
    Phase 6 (Cognitive Intelligence) ──────┐                   │
               │                           │ (parallel)        │
               ▼                           ▼                   │
    Phase 7 (RAG + Export)      Phase 8 (Agent Arch)           │
               │                           │                   │
               └──────────┬───────────────┘                    │
                          │                                    │
                          ▼                                    │
               Phase 9 (Ambient Intelligence UI) ◄─────────────┘
                          │
                          ▼
               Phase 10 (Compliance Pipeline)
                          │
                          ▼
               Phase 11 (Final Verification)
```

**Parallel paths:** Phases 4 & 5 can run in parallel. Phases 7 & 8 can run in parallel.

---

## Acceptance Criteria

### AC-1: Backend Brain Service Operational
DealBrainService in zakops-backend responds to GET/POST/PUT brain endpoints with correct JSON. Brain history trigger fires on update.

### AC-2: Core Pipeline Wired
graph.py post-turn enrichment calls snapshot_writer, brain_extraction, drift_detection, and citation_audit as fire-and-forget tasks. No blocking of user response.

### AC-3: Existing Services Completed
All 10 existing services have spec-mandated features added: admin auth on replay/counterfactual, BackendClient migration, configurable thresholds, proposal expiration, brain export in export_service.

### AC-4: Legal Hold Infrastructure
legal_hold_locks and legal_hold_log tables exist. create_monthly_partitions function exists.

### AC-5: Reflexion Pipeline
ReflexionService with CritiqueResult model exists, wired into graph.py for deal-scoped chats. critique_result stored in turn snapshots.

### AC-6: Cognitive Intelligence Services
DecisionFatigueSentinel, StallPredictor, and SpacedRepetition services exist and import cleanly. Ghost knowledge SSE event type registered.

### AC-7: RAG Enhancement
HyDE query option available in rag_rest.py. RankedChunk type defined. Living Deal Memo generation works.

### AC-8: Agent Architecture
PlanAndExecuteGraph exists. NodeRegistry has 4+ specialists with synthesis capability. MCP cost ledger integration in place.

### AC-9: Ambient Intelligence
MorningBriefingGenerator, DealAnomalyDetector, SentimentCoach services exist. Dashboard: citation indicators, MemoryStatePanel, SmartPaste, CommandPalette components created per Surface 9.

### AC-10: Compliance Pipeline
Retention policy engine, GDPR deletion service, and compliance purge admin endpoint exist and import cleanly.

### AC-11: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes. No test breakage. All existing services still function.

### AC-12: Bookkeeping
CHANGES.md updated. Completion report produced with evidence paths. Checkpoint file updated.

---

## Guardrails

1. **Scope: Build what's in the actionable items register** — do not add features beyond the 83 items. Do not redesign existing services.
2. **Generated files** — do not edit `*.generated.ts` or `*_models.py`. Use bridge files.
3. **Migration safety** — do not modify existing migration files (004, 028). Only create new migrations.
4. **Backend repo boundary** — Phase 1 is the ONLY phase that modifies `/home/zaks/zakops-backend/`. All other phases modify agent-api or dashboard.
5. **Fire-and-forget for enrichment** — post-turn enrichment MUST NOT block user response. Use `asyncio.create_task()`.
6. **Contract surface discipline** — run `make sync-all-types` if any API boundary changes.
7. **Surface 9 compliance** — all dashboard components follow design system rules.
8. **WSL safety** — strip CRLF from .sh files, fix ownership on files under /home/zaks/.
9. **Port 8090 is FORBIDDEN** — never use or reference.
10. **BackendClient mandatory** — no raw httpx in agent-api services for backend calls.
<!-- Adopted from Improvement Area IA-15 -->
11. **Governance surfaces** — if touching dependencies → `make validate-surface10`; if touching error handling → `make validate-surface12`; if adding tests → `make validate-surface13`.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify the backend is running before planning Phase 1?"
- [ ] "Did I record which D-items already exist vs. need building?"
- [ ] "Does `make validate-local` pass at baseline?"

### After every code change:
- [ ] "Am I using BackendClient, not raw httpx?"
- [ ] "Is this enrichment fire-and-forget or blocking the user response?"
- [ ] "Did I add a spec section reference in the docstring?"
- [ ] "Did I run `make sync-all-types` if I changed an API boundary?"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks?"
- [ ] "Did I update the checkpoint file?"
- [ ] "Did I create new .sh files? → CRLF stripped?"
- [ ] "Did I create files under /home/zaks/? → Ownership fixed?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Does `npx tsc --noEmit` pass?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce the completion report with evidence paths for every AC?"
- [ ] "Did I create ALL new service files listed in the phases?"
- [ ] "Do test names contain functional keywords for QA grep?" <!-- IA-10 -->

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-backend/app/api/v1/deals.py` | P1 | Add brain GET/POST/PUT endpoints |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py` | P2, P5 | Post-turn enrichment, reflexion wiring, node_registry |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py` | P3 | BackendClient migration, trigger_type, expiration |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py` | P3, P7 | BackendClient migration, brain appendix, living memo |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py` | P3, P10 | Admin auth, compliance endpoint |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/security/citation_audit.py` | P3 | Configurable thresholds |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/replay_service.py` | P3 | Audit log |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/counterfactual_service.py` | P3 | History storage |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py` | P3 | Extractive pre-filter |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_rest.py` | P7 | HyDE query option |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py` | P6 | Ghost knowledge SSE event |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py` | P8 | 4th specialist, synthesis |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-backend/app/services/deal_brain.py` | P1 | DealBrainService class |
| `/home/zaks/zakops-backend/db/migrations/versions/{rev}_deal_brain.py` | P1 | Alembic migration for deal_brain + brain_history |
| `/home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql` | P4 | Legal hold tables + partition function |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` | P5 | ReflexionService + CritiqueResult |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py` | P6 | DecisionFatigueSentinel |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/stall_predictor.py` | P6 | StallPredictor |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py` | P6 | Spaced repetition review service |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py` | P8 | PlanAndExecuteGraph |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/morning_briefing.py` | P9 | MorningBriefingGenerator |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/anomaly_detector.py` | P9 | DealAnomalyDetector |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py` | P9 | SentimentCoach |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/retention_policy.py` | P10 | RetentionPolicy engine |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py` | P10 | GDPR deletion automation |
| `/home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001.md` | P0+ | Multi-session checkpoint |
| `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001-COMPLETION.md` | P11 | Completion report |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` | Design specification (3,276 lines) |
| `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` | Actionable items register (83 items) |
| `/home/zaks/bookkeeping/docs/_qa_evidence/COMPLETION-REPORT.md` | QA completion report |
| `/home/zaks/bookkeeping/docs/QA-COL-ORCHESTRATOR-PROMPT.md` | QA gate definitions |

---

## Stop Condition

This mission is DONE when:
- All 12 acceptance criteria are met
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All changes recorded in CHANGES.md
- Completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001-COMPLETION.md`
- Checkpoint file updated to reflect completion

**Do NOT proceed to:**
- Running the QA successor mission (QA-COL-BUILD-VERIFY-001) — that is a separate session
- Deploying to production — this is development work only
- Modifying the COL-DESIGN-SPEC-V2.md — the spec is a read-only source of truth

---

## Lab Loop Configuration

For automated execution via Lab Loop:

```
TASK_ID=COL-V2-BUILD-001
REPO_DIR=/home/zaks/zakops-agent-api
GATE_CMD="make validate-local && cd apps/dashboard && npx tsc --noEmit"
```

Note: Lab Loop is suitable for iterative Phase-by-Phase execution. Given XL complexity, consider running phases 1-4 as one Lab Loop task and phases 5-11 as a second.

---

*End of Mission Prompt — COL-V2-BUILD-001*

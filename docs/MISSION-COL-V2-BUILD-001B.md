# MISSION: COL-V2-BUILD-001B
## Intelligence Services and Agent Architecture
## Date: 2026-02-13
## Classification: Feature Build
## Prerequisite: COL-V2-BUILD-001A
## Successor: COL-V2-BUILD-001C

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash or context compaction, run:

```bash
# 1. Determine current phase
cat /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001B.md

# 2. Check validation state
cd /home/zaks/zakops-agent-api && make validate-local

# 3. Check for partial work
git -C /home/zaks/zakops-agent-api status
```

Resume from the checkpoint file. Do not re-execute completed phases.

---

## Mission Objective

**Build intelligence services and agent architecture** for the COL-V2 system in the agent-api monorepo. This is the second of three sub-missions splitting the original COL-V2-BUILD-001 scope. It covers:

1. **Reflexion and Chain-of-Verification** — Self-critique pipeline with CritiqueResult model, wired into graph.py enrichment (S8.3-S8.5)
2. **Cognitive intelligence services** — Decision fatigue detection, spaced repetition, sentiment coaching (S14.1, S14.5, S17.5)
3. **Agent architecture** — PlanAndExecuteGraph, 4th specialist node, specialist synthesis, MCP cost ledger (S19.2, S19.4, S19.5)

**What this mission is NOT:**
- This is NOT a backend mission — zakops-backend is **read-only**. Intelligence services there (StallPredictor, MorningBriefing, AnomalyDetector, etc.) are already built.
- This is NOT a dashboard UI mission — no component work. Dashboard UI is COL-V2-BUILD-001C.
- This is NOT a compliance pipeline mission — retention policy, GDPR, and compliance endpoints are COL-V2-BUILD-001C.
- This is NOT a rebuild mission — existing agent-api services are extended, not rewritten.

**Source material:**
- Design specification: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` (3,276 lines)
- Actionable items register: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md`
- Parent mission: `/home/zaks/bookkeeping/docs/MISSION-COL-V2-BUILD-001.md` (Phases 5, 6, 8 scope)
- 001A completion report: `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md`

---

## Context

After COL-V2-BUILD-001A completion, the agent-api has:

- **graph.py enrichment pipeline** — `_post_turn_enrichment()` orchestrates snapshot writing, brain extraction, drift detection, and citation audit as fire-and-forget `asyncio.create_task()` calls
- **Node registry wired** — `node_registry.route(query, context)` called before main LLM call; specialist results with confidence >= 0.6 enhance the system prompt
- **Service completion** — BackendClient migration done, admin role checks on replay/counterfactual, configurable thresholds in citation_audit, proposal expiration
- **Compliance foundation** — legal_hold_locks, legal_hold_log tables, create_monthly_partitions function in zakops_agent database

Key existing files this mission depends on:

| File | Lines | What It Provides |
|------|-------|--------------------|
| `apps/agent-api/app/core/langgraph/graph.py` | ~500+ | `_post_turn_enrichment()` pipeline, node_registry wiring |
| `apps/agent-api/app/core/langgraph/node_registry.py` | 296 | NodeRegistry with 3 specialists (FinancialAnalyst, RiskAssessor, DealMemory) |
| `apps/agent-api/app/services/snapshot_writer.py` | 233 | TurnSnapshot with `critique_result` field ready for reflexion |
| `apps/agent-api/app/services/drift_detection.py` | 184 | `compute_decay_confidence()` for spaced repetition scoring |
| `apps/agent-api/app/schemas/sse_events.py` | ~200+ | SSE event type discriminated union |

Backend intelligence services (already built — call via BackendClient, do NOT duplicate):

| Service | Path | Spec Section |
|---------|------|-------------|
| StallPredictor | `zakops-backend/src/core/agent/stall_predictor.py` | S14.2 |
| MorningBriefingGenerator | `zakops-backend/src/core/agent/morning_briefing.py` | S17.1 |
| DealAnomalyDetector | `zakops-backend/src/core/agent/anomaly_detector.py` | S17.2 |
| LivingMemoGenerator | `zakops-backend/src/core/agent/living_memo_generator.py` | S12.3 |
| DevilsAdvocateService | `zakops-backend/src/core/agent/devils_advocate.py` | S10 |
| GhostKnowledgeDetector | `zakops-backend/src/core/agent/ghost_knowledge_detector.py` | QW-1 |
| MomentumCalculator | `zakops-backend/src/core/agent/momentum_calculator.py` | S20 |
| BottleneckHeatmap | `zakops-backend/src/core/agent/bottleneck_heatmap.py` | S14.3 |

---

## Glossary

| Term | Definition |
|------|-----------|
| Reflexion | Self-critique loop: generate response, critique against evidence, optionally revise (S8.3) |
| Chain-of-Verification | Extract claims from response, verify each against evidence sources (S8.5) |
| CritiqueResult | Pydantic model: issues, severity, should_revise, revised_response |
| Decision Fatigue Sentinel | Tracks decisions per session, warns at configurable thresholds (S14.1) |
| Spaced Repetition | Surfaces brain facts below decay threshold for reinforcement (S14.5) |
| Decay Confidence | Score from drift_detection.compute_decay_confidence() — decreases as facts age without reinforcement |
| PlanAndExecuteGraph | LangGraph subgraph: decompose complex query into steps, execute each, synthesize (S19.2) |
| Specialist | Domain-specific node in NodeRegistry — FinancialAnalyst, RiskAssessor, DealMemory, Compliance (S19.4) |
| MCP Cost Ledger | Log of tool call costs and decision metadata when MCP tools are invoked (S19.5) |

---

## Architectural Constraints

Per standing constraints in CLAUDE.md and contract surface discipline. Mission-specific additions:

- **BackendClient is mandatory for agent-to-backend calls** — all calls to backend intelligence services MUST use `BackendClient` from `deal_tools.py`, never raw `httpx.AsyncClient`.
- **Fire-and-forget for non-critical paths** — Reflexion runs in the `_post_turn_enrichment()` pipeline. It MUST NOT block the user-facing response. Use `asyncio.create_task()` with exception logging.
- **Reflexion is config-gated** — A flag controls whether reflexion critique runs. Default: enabled for deal-scoped chats only. General chats skip it.
- **Singleton pattern for services** — All COL-V2 services use module-level singleton instances (e.g., `reflexion_service = ReflexionService()`). Preserve this pattern.
- **Spec section references in docstrings** — Every new service module MUST have a docstring citing its COL-DESIGN-SPEC-V2 section (e.g., `COL-DESIGN-SPEC-V2, Section 8.3`).
- **No backend modification** — zakops-backend is read-only in this mission. Call existing endpoints via BackendClient; do not duplicate service logic.
- **SSE event schema stability** — Adding a new event type to sse_events.py must not break the existing discriminated union. The new type must follow the existing pattern.

---

## Anti-Pattern Examples

### WRONG: Blocking reflexion in the critical path
```python
# In graph.py main response path — adds 2-5s latency to every turn
critique = await reflexion_service.critique(response, evidence, brain_facts)
if critique.should_revise:
    response = critique.revised_response
return response  # user waited for critique to finish
```

### RIGHT: Fire-and-forget reflexion in enrichment pipeline
```python
# In _post_turn_enrichment() — non-blocking
async def _post_turn_enrichment(deal_id, thread_id, response, evidence, brain_facts, ...):
    # ... snapshot, brain extraction, drift ...
    try:
        critique = await reflexion_service.critique(response, evidence, brain_facts)
        snapshot_writer.update_critique(thread_id, turn_number, critique)
    except Exception as e:
        logger.warning(f"Reflexion critique failed: {e}")
```

### WRONG: Duplicating StallPredictor in agent-api
```python
# Building a new stall_predictor.py in agent-api — duplicates backend logic
class StallPredictor:
    async def predict(self, deal_id):
        # reimplements all the logic from zakops-backend
```

### RIGHT: Calling backend endpoint via BackendClient
```python
from app.core.langgraph.tools.deal_tools import BackendClient
client = BackendClient()
result = await client.get(f"/api/deals/{deal_id}/stall-prediction")
```

### WRONG: Hardcoded decision fatigue threshold
```python
if self.decision_count > 5:  # magic number buried in logic
    self._emit_warning()
```

### RIGHT: Configurable constants at module level
```python
DEFAULT_DECISION_THRESHOLD = 5
DEFAULT_TIME_WINDOW_HOURS = 2
DEFAULT_SESSION_DURATION_HOURS = 3

class DecisionFatigueSentinel:
    def __init__(self, decision_threshold=DEFAULT_DECISION_THRESHOLD, ...):
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Reflexion LLM call adds unbearable latency even as fire-and-forget (token cost, concurrent requests) | MEDIUM | Resource exhaustion under load | Config flag defaults to deal-scoped only; enrichment pipeline has try/except; Phase 1 gate verifies non-blocking design |
| 2 | Import cycle between reflexion.py and graph.py (circular dependency) | MEDIUM | Agent-api fails to start | Phase 1 gate: `python -c "from app.core.langgraph.graph import build_graph"` — catches immediately |
| 3 | New SSE event type breaks the discriminated union in sse_events.py | MEDIUM | Dashboard SSE parsing fails | Phase 2 gate: schema validation + `npx tsc --noEmit` catches type breakage |
| 4 | PlanAndExecuteGraph creates recursive LangGraph calls that don't terminate | LOW | Infinite loop / hang | Design with explicit step limit; Phase 3 gate: import + structural check |
| 5 | 001A not actually complete — graph.py enrichment pipeline missing or broken | HIGH | Entire mission builds on sand | Phase 0 verifies enrichment pipeline exists and imports before any work begins |

---

## Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify that COL-V2-BUILD-001A is complete and the enrichment pipeline exists before building on top of it.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Run baseline validation** — `cd /home/zaks/zakops-agent-api && make validate-local`
  - **Checkpoint:** Must exit 0. If not, fix before proceeding.
- P0-02: **Verify 001A completion — enrichment pipeline** — Confirm `_post_turn_enrichment()` exists in graph.py and that snapshot_writer, brain_extraction, drift_detection, citation_audit are called within it.
  - Evidence: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
  - **Decision Tree:**
    - **IF** `_post_turn_enrichment()` exists and calls all 4 services → proceed
    - **ELSE** → STOP. 001A prerequisite is not met. Do not proceed.
- P0-03: **Verify 001A completion — legal hold tables** — `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_locks"`
  - **Decision Tree:**
    - **IF** tables exist → proceed
    - **ELSE IF** database is unavailable → proceed with note (tables are not a direct dependency for this mission's code, but prerequisite is not fully verified)
    - **ELSE** → STOP. 001A prerequisite is not met.
- P0-04: **Verify existing services import** — Run:
  ```bash
  cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "
  from app.core.langgraph.graph import build_graph
  from app.services.snapshot_writer import snapshot_writer
  from app.services.drift_detection import drift_detection_service
  from app.core.langgraph.node_registry import node_registry
  print('All imports OK')
  "
  ```
  - **Checkpoint:** All imports succeed. If not, diagnose and fix before proceeding.
- P0-05: **Read spec sections** — Read COL-DESIGN-SPEC-V2.md sections: S8.3-S8.5 (Reflexion), S14.1 (Fatigue), S14.5 (Spaced Repetition), S17.5 (Sentiment), S19.2 (PlanAndExecute), S19.4 (Specialists), S19.5 (MCP)
- P0-06: **Write checkpoint**

### Gate P0
- `make validate-local` passes
- `_post_turn_enrichment()` exists in graph.py
- All 4 prerequisite services import successfully
- Spec sections read

---

## Phase 1 — Reflexion & Chain-of-Verification
**Complexity:** L
**Estimated touch points:** 2 files (1 new, 1 modify)

**Purpose:** Build the self-critique pipeline that evaluates LLM responses against evidence and brain facts, improving response quality for deal-scoped chats.

### Blast Radius
- **Services affected:** agent-api (new service + graph.py enrichment)
- **Pages affected:** None (backend enrichment, no UI change)
- **Downstream consumers:** turn_snapshots.critique_result, graph.py `_post_turn_enrichment()`

### Tasks
- P1-01: **Build ReflexionService** in `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` (new file):
  - Define `CritiqueResult` Pydantic model: `issues: list[str]`, `severity: str`, `should_revise: bool`, `revised_response: str | None`
  - Implement `critique(response: str, evidence: list[str], brain_facts: list[str]) -> CritiqueResult` — uses a focused LLM call to evaluate response fidelity against evidence. If issues found and severity exceeds threshold, generates revised response.
  - Implement `verify_claims(response_text: str, evidence_sources: list[str]) -> list[dict]` — Chain-of-Verification per S8.5. Extracts claims, checks each against evidence, returns list with verified/unverified status.
  - Module-level singleton: `reflexion_service = ReflexionService()`
  - Docstring: cite `COL-DESIGN-SPEC-V2, Sections 8.3-8.5`
  - **Checkpoint:** `python -c "from app.services.reflexion import ReflexionService, CritiqueResult; print('OK')"`
- P1-02: **Wire reflexion into graph.py enrichment** — Add reflexion critique call to `_post_turn_enrichment()`:
  - Read config flag (e.g., `REFLEXION_ENABLED` or a settings attribute). Default: enabled for deal-scoped chats only.
  - If enabled, call `reflexion_service.critique()` with the response, evidence, and brain facts.
  - Store the `CritiqueResult` in the turn snapshot via `snapshot_writer.update_critique()` or by including it in the initial snapshot write.
  - Wrap in try/except with logger.warning — reflexion failure must never crash the enrichment pipeline.
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
  - **Checkpoint:** `python -c "from app.core.langgraph.graph import build_graph; print('OK')"` — no import cycles.
- P1-03: **Functional gate test** — Call `ReflexionService.critique()` with a known-bad response (claims not supported by evidence) and verify it returns `should_revise=True` and populates `issues`.
  ```bash
  cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "
  import asyncio
  from app.services.reflexion import reflexion_service, CritiqueResult
  # Verify CritiqueResult model validates
  cr = CritiqueResult(issues=['test'], severity='high', should_revise=True, revised_response='fixed')
  assert cr.should_revise == True
  assert len(cr.issues) == 1
  print('CritiqueResult model OK')
  print('ReflexionService functional gate PASS')
  "
  ```
- P1-04: **Write checkpoint**

### Rollback Plan
1. Remove new file: `rm /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py`
2. Revert graph.py: `git checkout -- /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
3. Restart agent-api if running: `cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose restart agent-api`

### Gate P1
- ReflexionService imports: `python -c "from app.services.reflexion import ReflexionService, CritiqueResult; print('OK')"`
- verify_claims exists: `python -c "from app.services.reflexion import ReflexionService; assert hasattr(ReflexionService, 'verify_claims') or callable(getattr(ReflexionService(), 'verify_claims', None)); print('OK')"`
- graph.py builds without import cycles: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- CritiqueResult model validates with known-bad input (should_revise=True)
- `make validate-local` passes

---

## Phase 2 — Cognitive Intelligence Services
**Complexity:** M
**Estimated touch points:** 4 files (3 new, 1 modify)

**Purpose:** Build the cognitive intelligence layer: decision fatigue detection, spaced repetition for brain facts, sentiment coaching, and ghost knowledge SSE integration.

### Blast Radius
- **Services affected:** agent-api (3 new services + SSE schema)
- **Pages affected:** None directly (SSE event type addition, but no dashboard consumer yet — that's 001C)
- **Downstream consumers:** SSE event stream (Surface 7), graph.py enrichment pipeline
<!-- Adopted from Improvement Area IA-15 -->
- **Governance surface:** Surface 12 (error handling in new services)

### Tasks
- P2-01: **Build DecisionFatigueSentinel** in `/home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py` (new file):
  - Track proposals approved/rejected per session
  - Configurable thresholds at module level: `DEFAULT_DECISION_THRESHOLD = 5`, `DEFAULT_TIME_WINDOW_HOURS = 2`, `DEFAULT_SESSION_DURATION_HOURS = 3`
  - Warn at threshold (5 decisions in 2 hours) or continuous session duration (3 hours)
  - Method: `record_decision(session_id: str, decision_type: str)` and `check_fatigue(session_id: str) -> FatigueWarning | None`
  - Module-level singleton: `fatigue_sentinel = DecisionFatigueSentinel()`
  - Docstring: cite `COL-DESIGN-SPEC-V2, Section 14.1`
  - **Checkpoint:** `python -c "from app.services.fatigue_sentinel import fatigue_sentinel; print('OK')"`
- P2-02: **Build SpacedRepetitionService** in `/home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py` (new file):
  - Method: `get_review_facts(deal_id: str) -> list[dict]` — returns brain facts below decay threshold needing reinforcement
  - Uses `drift_detection.compute_decay_confidence()` for scoring
  - Configurable decay threshold at module level
  - Module-level singleton: `spaced_repetition_service = SpacedRepetitionService()`
  - Docstring: cite `COL-DESIGN-SPEC-V2, Section 14.5`
  - **Checkpoint:** `python -c "from app.services.spaced_repetition import spaced_repetition_service; print('OK')"`
- P2-03: **Build SentimentCoach** in `/home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py` (new file):
  - Per-deal sentiment trend tracking over conversation turns
  - Method: `record_sentiment(deal_id: str, turn_number: int, sentiment_score: float)` and `get_trend(deal_id: str) -> SentimentTrend`
  - Module-level singleton: `sentiment_coach = SentimentCoach()`
  - Docstring: cite `COL-DESIGN-SPEC-V2, Section 17.5`
  - **Checkpoint:** `python -c "from app.services.sentiment_coach import sentiment_coach; print('OK')"`
- P2-04: **Add ghost knowledge SSE event type** to `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py`:
  - Follow the existing discriminated union pattern for SSE event types
  - New event type: `ghost_knowledge_flags` with fields: `deal_id`, `flags` (list of ghost knowledge items), `detected_at` (timestamp)
  - **Checkpoint:** `python -c "from app.schemas.sse_events import *; print('SSE events OK')"` — no import errors or schema breaks
- P2-05: **Functional gate — fatigue tracking** — Verify DecisionFatigueSentinel tracks 5 decisions and triggers warning:
  ```bash
  cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "
  from app.services.fatigue_sentinel import DecisionFatigueSentinel
  sentinel = DecisionFatigueSentinel()
  session = 'test-session'
  for i in range(5):
      sentinel.record_decision(session, 'approve')
  warning = sentinel.check_fatigue(session)
  assert warning is not None, 'Expected fatigue warning after 5 decisions'
  print('DecisionFatigueSentinel functional gate PASS')
  "
  ```
- P2-06: **Write checkpoint**

### Decision Tree
- **IF** sse_events.py uses Literal type discriminator for event types → add new Literal value and corresponding model class
- **ELSE IF** sse_events.py uses Enum for event types → add new enum member and corresponding model class
- **ELSE** → study existing pattern and follow it exactly

### Rollback Plan
1. Remove new files: `rm /home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py /home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py /home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py`
2. Revert SSE events: `git checkout -- /home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py`

### Gate P2
- All 3 new services import: `python -c "from app.services.fatigue_sentinel import fatigue_sentinel; from app.services.spaced_repetition import spaced_repetition_service; from app.services.sentiment_coach import sentiment_coach; print('All cognitive services OK')"`
- SSE events schema validates: `python -c "from app.schemas.sse_events import *; print('SSE schema OK')"`
- DecisionFatigueSentinel tracks 5 decisions and triggers warning (functional gate from P2-05)
- Dashboard TypeScript still compiles: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- `make validate-local` passes

---

## Phase 3 — Agent Architecture
**Complexity:** L
**Estimated touch points:** 3 files (1 new, 2 modify)

**Purpose:** Build the PlanAndExecute subgraph for complex query decomposition, expand the specialist roster, add specialist response synthesis, and integrate MCP cost tracking.

### Blast Radius
- **Services affected:** agent-api (LangGraph architecture layer)
- **Pages affected:** None (architecture-level, no UI)
- **Downstream consumers:** graph.py routing, specialist nodes, MCP tool integration

### Tasks
- P3-01: **Build PlanAndExecuteGraph** in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py` (new file):
  - Decompose complex queries into ordered steps: (1) plan steps from query, (2) execute each step (potentially calling LLM or tools), (3) synthesize step results into coherent response
  - Include explicit step limit (e.g., `MAX_STEPS = 10`) to prevent runaway execution
  - Module-level function or class: `PlanAndExecuteGraph` with `run(query, context)` method
  - Docstring: cite `COL-DESIGN-SPEC-V2, Section 19.2`
  - **Checkpoint:** `python -c "from app.core.langgraph.plan_execute import PlanAndExecuteGraph; print('OK')"`
- P3-02: **Add 4th specialist (Compliance/Regulatory)** to `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py`:
  - Add `ComplianceSpecialist` following the existing FinancialAnalyst/RiskAssessor/DealMemory pattern
  - Domain: regulatory requirements, compliance checks, legal considerations
  - Per spec S19.4
  - **Checkpoint:** Verify 4 specialists: `python -c "from app.core.langgraph.node_registry import node_registry; specs = node_registry.list_specialists(); assert len(specs) >= 4; print(f'{len(specs)} specialists registered')"`
- P3-03: **Add specialist response synthesis** to node_registry.py:
  - New method: `synthesize(results: list[SpecialistResult]) -> str` — merges multiple specialist analyses into a coherent combined response
  - When multiple specialists contribute to a query (confidence >= threshold for multiple domains), synthesize their outputs rather than picking one
  - **Checkpoint:** `python -c "from app.core.langgraph.node_registry import node_registry; assert hasattr(node_registry, 'synthesize'); print('Synthesis method OK')"`
- P3-04: **Add MCP cost/decision ledger** — When MCP tools are called, log cost and decision metadata:
  - Create a lightweight logging mechanism (module-level function or class) that records: tool_name, input_tokens, output_tokens, cost_estimate, decision_context, timestamp
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py` or a new module in the langgraph directory
  - Per spec S19.5
  - **Checkpoint:** Verify ledger import and interface exist
- P3-05: **Write checkpoint**

### Decision Tree
- **IF** node_registry.py uses a list/dict for specialist registration → add ComplianceSpecialist to the same structure
- **ELSE IF** specialists are registered via decorators or class inheritance → follow the same pattern
- **IF** MCP tool integration already exists in graph.py → add ledger calls alongside existing tool dispatch
- **ELSE** → create standalone cost_ledger module that can be imported where needed

### Rollback Plan
1. Remove new file: `rm /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py`
2. Revert modified files: `git checkout -- /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
3. Restart agent-api if running: `cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose restart agent-api`

### Gate P3
- PlanAndExecuteGraph imports: `python -c "from app.core.langgraph.plan_execute import PlanAndExecuteGraph; print('OK')"`
- 4+ specialists registered: `python -c "from app.core.langgraph.node_registry import node_registry; assert len(node_registry.list_specialists()) >= 4; print('OK')"`
- Synthesis method exists: `python -c "from app.core.langgraph.node_registry import node_registry; assert hasattr(node_registry, 'synthesize'); print('OK')"`
- graph.py still builds: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- `make validate-local` passes

---

## Phase 4 — Final Verification & Bookkeeping
**Complexity:** S
**Estimated touch points:** 0 (verification only) + bookkeeping files

**Purpose:** Run comprehensive validation, produce completion report, update bookkeeping.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** QA successor mission, COL-V2-BUILD-001C

### Tasks
- P4-01: **Run full validation** — `cd /home/zaks/zakops-agent-api && make validate-local`
- P4-02: **Run TypeScript compilation** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P4-03: **Verify all new services import** — Comprehensive import check:
  ```bash
  cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "
  from app.services.reflexion import ReflexionService, CritiqueResult, reflexion_service
  from app.services.fatigue_sentinel import DecisionFatigueSentinel, fatigue_sentinel
  from app.services.spaced_repetition import SpacedRepetitionService, spaced_repetition_service
  from app.services.sentiment_coach import SentimentCoach, sentiment_coach
  from app.core.langgraph.plan_execute import PlanAndExecuteGraph
  from app.core.langgraph.node_registry import node_registry
  from app.core.langgraph.graph import build_graph
  from app.schemas.sse_events import *
  print('ALL IMPORTS PASS')
  "
  ```
- P4-04: **Verify specialist count** — `python -c "from app.core.langgraph.node_registry import node_registry; specs = node_registry.list_specialists(); assert len(specs) >= 4; print(f'{len(specs)} specialists: {[s.name if hasattr(s, \"name\") else str(s) for s in specs]}')" `
- P4-05: **Update CHANGES.md** — Record all changes from this mission in `/home/zaks/bookkeeping/CHANGES.md`
- P4-06: **Produce completion report** — Write `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001B-COMPLETION.md` with:
  - Phase-by-phase results
  - Files created and modified
  - Functional gate results
  - Validation results
  - Evidence paths for every AC
- P4-07: **Fix CRLF and ownership** — Run `sed -i 's/\r$//'` on any new .sh files. Run `chown zaks:zaks` on any new files under `/home/zaks/`.
- P4-08: **Write final checkpoint**

### Gate P4
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All new services import without error (P4-03 script exits 0)
- CHANGES.md updated
- Completion report written

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ▼
Phase 1 (Reflexion & Chain-of-Verification)
    │
    ▼
Phase 2 (Cognitive Intelligence Services)
    │
    ▼
Phase 3 (Agent Architecture)
    │
    ▼
Phase 4 (Final Verification & Bookkeeping)
```

Phases execute sequentially: 0 → 1 → 2 → 3 → 4. No parallel paths — each phase builds on the previous.

---

## Acceptance Criteria

### AC-1: ReflexionService Operational
ReflexionService exists in `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` with `critique()` and `verify_claims()` methods. Wired into graph.py `_post_turn_enrichment()`.

### AC-2: CritiqueResult Stored in Snapshots
CritiqueResult from reflexion is stored in turn_snapshots via the `critique_result` field on TurnSnapshot.

### AC-3: DecisionFatigueSentinel Functional
DecisionFatigueSentinel in `fatigue_sentinel.py` tracks decisions per session and triggers warning at the configurable threshold (default: 5 decisions in 2 hours).

### AC-4: SpacedRepetitionService Returns Review Facts
SpacedRepetitionService in `spaced_repetition.py` returns brain facts below decay threshold via `get_review_facts(deal_id)`, using `drift_detection.compute_decay_confidence()` for scoring.

### AC-5: SentimentCoach Tracks Trends
SentimentCoach in `sentiment_coach.py` tracks per-deal sentiment trends over conversation turns.

### AC-6: Ghost Knowledge SSE Event Registered
New `ghost_knowledge_flags` event type registered in `sse_events.py` following the existing discriminated union pattern.

### AC-7: PlanAndExecuteGraph Exists
PlanAndExecuteGraph in `plan_execute.py` implements plan → execute → synthesize flow with explicit step limit.

### AC-8: NodeRegistry Has 4+ Specialists with Synthesis
NodeRegistry in `node_registry.py` has at least 4 specialists (including Compliance/Regulatory) and a `synthesize()` method for merging multi-specialist results.

### AC-9: MCP Cost Ledger Integration
MCP tool calls are logged with cost and decision metadata to a cost ledger mechanism.

### AC-10: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes. No test breakage. All existing services still function.

### AC-11: Bookkeeping Complete
CHANGES.md updated. Completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001B-COMPLETION.md`. Checkpoint file updated.

---

## Guardrails

1. **Scope: Intelligence services + agent architecture only.** Do NOT build dashboard UI components. Do NOT build the compliance pipeline (retention, GDPR). Those are COL-V2-BUILD-001C.
2. **Backend repo is read-only** — do NOT modify any file in `/home/zaks/zakops-backend/`. Intelligence services there are already built. Call their endpoints via BackendClient.
3. **Generated files never edited** — do not edit `*.generated.ts` or `*_models.py`. Per standing deny rules.
4. **Reflexion is non-blocking** — fire-and-forget in `_post_turn_enrichment()`. Must not add latency to user-facing response path.
5. **Do NOT duplicate backend services** — StallPredictor, AnomalyDetector, MorningBriefing, LivingMemo, DevilsAdvocate, GhostKnowledgeDetector, MomentumCalculator, BottleneckHeatmap are all BACKEND services. Call their endpoints, do not rebuild.
6. **Contract surface discipline** — run `make sync-all-types` if any API boundary changes. SSE event addition affects Surface 7.
7. **Surface 9** — should not apply to this mission (no dashboard component work). If any dashboard file is touched, follow Surface 9 design system rules.
8. **WSL safety** — strip CRLF from any new .sh files (`sed -i 's/\r$//'`). Fix ownership on files under `/home/zaks/` (`chown zaks:zaks`).
9. **Port 8090 is FORBIDDEN** — never use or reference.
10. **Spec section references in docstrings** — all new services MUST cite their COL-DESIGN-SPEC-V2 section in the module docstring.
<!-- Adopted from Improvement Area IA-15 -->
11. **Governance surfaces** — new services touch error handling patterns → `make validate-surface12` applies.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify `_post_turn_enrichment()` actually exists in graph.py — not just assumed from 001A?"
- [ ] "Did I confirm the 3 existing specialists in node_registry.py are present?"
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I read the relevant spec sections (S8.3-S8.5, S14.1, S14.5, S17.5, S19.2, S19.4, S19.5)?"

### After every code change:
- [ ] "Is this service using the singleton pattern (module-level instance)?"
- [ ] "Does the module docstring cite its COL-DESIGN-SPEC-V2 section?"
- [ ] "Is reflexion fire-and-forget, or did I accidentally put it in the critical path?"
- [ ] "Am I building a new service or duplicating something that exists in zakops-backend?"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks and they all passed?"
- [ ] "Did I update the checkpoint file?"
- [ ] "Did I create new .sh files? → CRLF stripped?"
- [ ] "Did I create files under /home/zaks/? → Ownership fixed?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now, not 2 phases ago?"
- [ ] "Does `npx tsc --noEmit` pass?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce the completion report with evidence paths for every AC?"
- [ ] "Did I create ALL files listed in the 'Files to Create' table?"
<!-- Adopted from Improvement Area IA-10 -->
- [ ] "If any tests were written, do test names contain functional keywords (reflexion, fatigue, sentiment, specialist) for QA grep?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py` | P1 | Wire reflexion into `_post_turn_enrichment()`, MCP cost ledger |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py` | P2 | Add `ghost_knowledge_flags` SSE event type |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py` | P3 | Add ComplianceSpecialist, synthesis method |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` | P1 | ReflexionService + CritiqueResult + verify_claims |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py` | P2 | DecisionFatigueSentinel |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py` | P2 | SpacedRepetitionService |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py` | P2 | SentimentCoach |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py` | P3 | PlanAndExecuteGraph |
| `/home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001B.md` | P0+ | Multi-session checkpoint |
| `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001B-COMPLETION.md` | P4 | Completion report |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` | Design specification (3,276 lines) — S8.3-S8.5, S14.1, S14.5, S17.5, S19.2, S19.4, S19.5 |
| `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` | Actionable items register |
| `/home/zaks/zakops-backend/src/core/agent/` | Reference — understand what backend intelligence services exist (do NOT modify) |
| `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md` | 001A completion evidence — verify prerequisite |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/drift_detection.py` | Source for `compute_decay_confidence()` used by spaced_repetition |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/snapshot_writer.py` | Source for `critique_result` field on TurnSnapshot |

---

## Stop Condition

This mission is DONE when:
- All 11 acceptance criteria (AC-1 through AC-11) are met
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All changes recorded in CHANGES.md
- Completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001B-COMPLETION.md`
- Checkpoint file updated to reflect completion

**Do NOT proceed to:**
- Building dashboard UI components (citation indicators, MemoryStatePanel, SmartPaste, CommandPalette) — that is COL-V2-BUILD-001C
- Building the compliance pipeline (retention, GDPR, compliance purge) — that is COL-V2-BUILD-001C
- Running QA verification — that is a separate session
- Modifying COL-DESIGN-SPEC-V2.md — the spec is read-only
- Modifying any file in `/home/zaks/zakops-backend/`

---

## Lab Loop Configuration

For automated execution via Lab Loop:

```
TASK_ID=COL-V2-BUILD-001B
REPO_DIR=/home/zaks/zakops-agent-api
GATE_CMD="make validate-local && cd apps/dashboard && npx tsc --noEmit"
```

---

*End of Mission Prompt — COL-V2-BUILD-001B*

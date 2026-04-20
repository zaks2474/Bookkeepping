# ZakOps Prompt Pack v1 - Comprehensive Implementation Plan

**Document Version:** 1.1
**Created:** 2025-12-27
**Status:** Phase 1 Complete | Phase 2 In Planning
**Owner:** Zaks Deal Lifecycle OS Team
**Note:** Line counts are informational and may drift; treat as approximate.

---

## Executive Summary

This document provides a unified implementation plan for the **ZakOps Prompt Pack v1** system, covering:

1. **Phase 1 (COMPLETED)**: Core infrastructure, protocols, prompts, and guardrails
2. **Phase 2 (PLANNED)**: Critical operational components (Evidence, RAG, Proposals, Sessions)
3. **Phase 3 (PLANNED)**: Quality, testing, and operational readiness

### Project Goals

Build a production-grade **Chat Front Door** system with:
- **Deterministic behavior** through versioned prompts and typed protocols
- **Security-first design** with guardrails and secret scanning
- **Grounded responses** requiring citations for factual claims
- **Operator control** over all write operations (proposal/approval workflow)
- **Local-first** with optional cloud worker for specialized analysis

### Current Status

| Component | Status | Completion |
|-----------|--------|-----------|
| **Phase 1: Foundation** | ✅ Complete | 100% |
| **Phase 2: Operations** | 🔄 Planned | 0% |
| **Phase 3: Production Ready** | 🔄 Planned | 0% |
| **Overall** | 🟡 In Progress | 65% |

**To Production:** Complete Phase 2 (4 critical components) to enable end-to-end Chat Front Door operation.

---

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                      Chat Front Door (SSE)                       │
│                     /api/chat (streaming)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Session Manager    │◄─── Durable store (Redis optional)
                  │  (Phase 2 - TODO)    │
                  └──────────┬───────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │         Evidence Bundle Builder            │
        │           (Phase 2 - TODO)                 │
        │  Parallel retrieval: RAG + Events +        │
        │    Case File + Registry + Actions          │
        └────┬───────────┬────────┬──────────┬───────┘
             │           │        │          │
       ┌─────▼──┐   ┌───▼───┐  ┌─▼──┐  ┌────▼────┐
       │  RAG   │   │Events │  │Case│  │Registry │
       │ :8052  │   │ Store │  │File│  │+ Actions│
       │(Phase2)│   │       │  │    │  │         │
       └────────┘   └───────┘  └────┘  └─────────┘
             │
             └──────────────┬──────────────────┐
                            ▼                  │
                 ┌────────────────────┐        │
                 │   Task Packet      │        │
                 │   (Phase 1 ✅)     │        │
                 │  - scope           │        │
                 │  - policy          │        │
                 │  - evidence[]      │        │
                 │  - tooling         │        │
                 └─────────┬──────────┘        │
                           │                   │
              ┌────────────┴────────────┐      │
              ▼                         ▼      │
    ┌──────────────────┐      ┌─────────────────────┐
    │  Local Controller │      │   Gemini Worker     │
    │  (vLLM Qwen 32B) │      │  (Cloud, opt-in)    │
    │  (Phase 1 ✅)    │      │  (Phase 1 ✅)       │
    │                  │      │                     │
    │  - Orchestration │      │  - Classification   │
    │  - Tool planning │      │  - Extraction       │
    │  - Grounding     │      │  - No tools         │
    │  - Citations     │      │  - Strict JSON      │
    └────────┬─────────┘      └──────────┬──────────┘
             │                           │
             └─────────┬─────────────────┘
                       ▼
            ┌────────────────────┐
            │   Guardrails       │
            │   (Phase 1 ✅)     │
            │  - No silent drops │
            │  - Scope gating    │
            │  - Approval gating │
            │  - Citation mins   │
            └─────────┬──────────┘
                      │
         ┌────────────┴───────────┐
         ▼                        ▼
   ┌──────────┐          ┌────────────────┐
   │  Answer  │          │  Proposals     │
   │+ Citations│         │  (Phase 2 TODO)│
   └──────────┘          │  - Durable store│
                         │  - 7-day TTL    │
                         │  - Approval UI  │
                         └────────────────┘
```

### Key Design Decisions

1. **Task Packet Protocol**: Standard JSON envelope for all agent-to-agent calls
2. **Versioned Prompts**: Immutable prompt packs (v1, v2, ...) selected via env var
3. **Controller/Worker Separation**: Local orchestration + opt-in cloud analysis
4. **Guardrails Post-Generation**: LLM mistakes caught before returning to user
5. **Proposal/Approval Workflow**: All writes require operator confirmation

---

## Phase 1: Foundation (COMPLETED) ✅

### Scope

Build the core infrastructure for deterministic, secure agent behavior.

### Components Implemented

#### 1.1 Task Packet Protocol ✅

**Files:**
- `src/core/task_packet.py` (143 lines)
- `prompts/v1/01_message_envelope.schema.json` (148 lines)

**What It Does:**
- Defines standard JSON envelope for all inter-agent communication
- Includes scope (global/deal/document), policy flags, evidence bundle, tooling constraints
- Pydantic models with `extra="forbid"` for strict validation
- Factory method `TaskPacket.new()` for easy construction

**Key Features:**
```python
packet = TaskPacket.new(
    message="What is the EBITDA for Vertical-MSP-2025?",
    component="chat_front_door",
    scope_type="deal",
    deal_id="Vertical-MSP-2025",
    allow_cloud=False,  # Local-only by default
    allowed_tools=["query_rag", "read_case_file"],
)
```

**Acceptance Criteria:**
- ✅ Schema validates all required fields
- ✅ Scope constraints enforced (deal_id required for deal scope)
- ✅ Pydantic validation catches malformed packets
- ✅ JSON serialization/deserialization roundtrip works

---

#### 1.2 Prompt Pack System ✅

**Files:**
- `src/core/prompt_pack.py` (88 lines)
- `prompts/README.md` (19 lines)
- `prompts/v1/` (directory structure)

**What It Does:**
- Loads versioned prompts from filesystem
- Runtime version selection via `ZAKOPS_PROMPT_PACK_VERSION` env var
- LRU cache for repeated loads (256 prompt capacity)
- Logical name mapping (e.g., "charter" → "00_zakops_charter.md")

**Key Features:**
```python
# Load charter prompt
charter = load_prompt("charter")  # Uses env version or default v1

# Or specify version explicitly
controller_prompt = load_prompt("controller_system", version="v1")
```

**Acceptance Criteria:**
- ✅ Prompts load from versioned directories (v1/, v2/, ...)
- ✅ Missing files raise FileNotFoundError
- ✅ Unknown names raise KeyError
- ✅ LRU cache reduces filesystem reads

---

#### 1.3 Prompt Protocol Models ✅

**Files:**
- `src/core/prompt_protocol.py` (207 lines)

**What It Does:**
- Defines Pydantic models for controller and worker outputs
- Implements 4 guardrail validation functions
- Enforces citation requirements for financial claims

**Models:**
- `ControllerResponse` (answer/proposal/error status)
- `ControllerCitation` (evidence references)
- `ControllerProposal` (tool call proposals with approval flags)
- `WorkerClassificationV1` (document categorization)
- `WorkerExtractionV1` (field extraction with confidence)
- `WorkerBlocked` (secret detection response)

**Guardrails:**
1. **No Silent Drops**: Every request must return answer, proposal, or error
2. **Scope Gating**: Global scope cannot propose write tools
3. **Approval Gating**: LOI/CLOSING/EXIT_PLANNING/CLOSED_WON require approval=true
4. **Citation Minimums**: Financial claims require at least 1 citation

**Acceptance Criteria:**
- ✅ Models validate JSON structure
- ✅ Guardrails catch policy violations
- ✅ Financial claim regex detects EBITDA/SDE/ARR/revenue/margin/price/valuation
- ✅ Write tools blocked in global scope

---

#### 1.4 Secret Scanning ✅

**Files:**
- `src/core/secret_scan.py` (46 lines)

**What It Does:**
- Scans text for credential-like patterns before:
  - Sending to cloud LLMs (Gemini worker gate)
  - Indexing into RAG
  - Logging/tracing
- Conservative approach: better false positives than leaks

**Patterns (7 total):**
```python
("aws_access_key_id", r"AKIA[0-9A-Z]{16}")
("aws_secret_access_key", r"(?i)aws(.{0,20})?secret(.{0,20})?=\s*[0-9a-zA-Z/+]{35,}")
("github_token", r"ghp_[A-Za-z0-9]{30,}")
("openai_key", r"sk-[A-Za-z0-9]{20,}")
("google_api_key", r"AIza[0-9A-Za-z\-_]{30,}")
("private_key_block", r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")
("bearer_token", r"(?i)authorization:\s*bearer\s+[A-Za-z0-9\-\._~\+\/]+=*")
```

**Usage:**
```python
findings = find_secrets_in_text(payload)
if findings:
    return WorkerBlocked(reason="secret_detected")
```

**Acceptance Criteria:**
- ✅ Detects AWS keys (AKIA prefix)
- ✅ Detects GitHub tokens (ghp_ prefix)
- ✅ Detects OpenAI keys (sk- prefix)
- ✅ Detects private key blocks (PEM format)
- ✅ Returns list of pattern names (not secret values)

---

#### 1.5 Gemini Worker ✅

**Files:**
- `src/core/gemini_worker.py` (86 lines)

**What It Does:**
- Invokes cloud LLM for analysis-only tasks (no tools)
- Strict JSON output validated against schemas
- Secret-scan gate before cloud send
- Supports classification and extraction task types

**Flow:**
```python
# 1. Check policy
if not packet.policy.allow_cloud:
    return WorkerBlocked(reason="cloud_disabled")

# 2. Secret scan
findings = find_secrets_in_text(payload)
if findings:
    return WorkerBlocked(reason="secret_detected")

# 3. Invoke cloud LLM
resp = router.invoke_with_fallback(...)

# 4. Parse and validate JSON
data = json.loads(_extract_json(resp.content))
return WorkerClassificationV1.model_validate(data)
```

**Acceptance Criteria:**
- ✅ Blocks if allow_cloud=False
- ✅ Blocks if secrets detected
- ✅ Returns WorkerBlocked on non-JSON response
- ✅ Validates output against schema (classification_v1 or extraction_v1)

---

#### 1.6 Controller ✅

**Files:**
- `src/agents/controller.py` (68 lines)

**What It Does:**
- Local vLLM-based orchestrator
- Receives Task Packet, returns ControllerResponse
- Enforces guardrails post-generation
- No tool execution (only proposals)

**Flow:**
```python
# 1. Load system prompt
system_prompt = load_prompt("controller_system")

# 2. Serialize packet to JSON
payload = packet.model_dump_json()

# 3. Invoke LLM
msg = llm.invoke([SystemMessage(system_prompt), HumanMessage(payload)])

# 4. Parse JSON response
resp = ControllerResponse.model_validate(json.loads(_extract_json(msg.content)))

# 5. Validate guardrails
violations = validate_controller_response(packet, resp)
if violations:
    return ControllerResponse(status="error", error={"code": "guardrail_violation", ...})

return resp
```

**Acceptance Criteria:**
- ✅ Loads controller prompt from prompt pack
- ✅ Serializes Task Packet to JSON
- ✅ Parses LLM output (handles markdown code blocks)
- ✅ Validates guardrails and returns error if violated

---

#### 1.7 Prompts (Charter + Controller + Worker) ✅

**Files:**
- `prompts/v1/00_zakops_charter.md` (66 lines)
- `prompts/v1/10_controller_system.prompt.md` (91 lines)
- `prompts/v1/20_worker_gemini_system.prompt.md` (61 lines)

**Charter (Non-Negotiables):**
1. Deal is the unit of work (everything anchors to deal_id)
2. Control plane is truth (registry + events + state machine)
3. Folders are derived views (safe to rebuild)
4. Deterministic-first (schemas + policy drive behavior)
5. Audit everywhere (events + run-ledger metadata)
6. No silent drops (every request → traceable result)
7. No irreversible actions without approval
8. Draft-only outbound comms (humans send)
9. No secrets in traces/RAG/cloud calls
10. Grounded answers (citations or "not found")

**Controller Prompt:**
- Input: Task Packet JSON
- Output: Strict JSON (answer/proposal/error)
- Enforces: Scope gating, approval gating, citation minimums, no silent drops
- No tool execution (only proposes tools)

**Worker Prompt:**
- Input: Task Packet JSON with task_type (classification_v1 or extraction_v1)
- Output: Strict JSON matching output schema
- No tools (analysis-only)
- Grounded (use only provided evidence)
- Secret detection → blocked response

**Acceptance Criteria:**
- ✅ Charter defines 10 non-negotiables
- ✅ Controller prompt specifies strict JSON output
- ✅ Worker prompt specifies task-specific schemas
- ✅ All prompts reference charter

---

#### 1.8 Role Agent Prompts ✅

**Files:**
- `prompts/v1/30_role_agents/comms.prompt.md` (28 lines)
- `prompts/v1/30_role_agents/rag_expert.prompt.md` (27 lines)
- `prompts/v1/30_role_agents/deal_sourcing.prompt.md` (26 lines)
- `prompts/v1/30_role_agents/deal_case_manager.prompt.md` (34 lines)
- `prompts/v1/30_role_agents/underwriter.prompt.md` (34 lines)
- `prompts/v1/30_role_agents/diligence_coordinator.prompt.md` (29 lines)

**Role Cards:**

| Agent | Purpose | Key Rules |
|-------|---------|-----------|
| **Comms** | Draft emails/messages | Never send; draft only; ask for missing info |
| **RAG Expert** | Grounded answers from knowledge base | Never claim docs exist without retrieval |
| **Deal Sourcing** | New deal intake and screening | Classify source, extract basics |
| **Deal Case Manager** | Lifecycle orchestration | Keep deal moving, propose next actions |
| **Underwriter** | Financial analysis | Extract metrics with citations, identify risks |
| **Diligence Coordinator** | DD checklist management | Track open items, recommend specialists |

**Acceptance Criteria:**
- ✅ All 6 role agents have prompt cards
- ✅ Each references charter
- ✅ Each defines input (Task Packet) and output expectations
- ✅ Each includes "Hard Rules" or "Boundaries" section

---

#### 1.9 Output Schemas ✅

**Files:**
- `prompts/v1/schemas/classification_v1.schema.json` (35 lines)
- `prompts/v1/schemas/extraction_v1.schema.json` (53 lines)

**Classification Schema:**
```json
{
  "schema_version": "zakops.worker.classification.v1",
  "category": "CIM|TEASER|FINANCIALS|NDA|BANK_STATEMENT|TAX_RETURN|CORRESPONDENCE|OTHER|UNKNOWN",
  "confidence": 0.0-1.0,
  "rationale": "...",
  "unknowns": ["list of missing context"],
  "citations": [{"evidence_id": "...", "quote": "..."}]
}
```

**Extraction Schema:**
```json
{
  "schema_version": "zakops.worker.extraction.v1",
  "confidence": 0.0-1.0,
  "extracted": {
    "company_name": "...",
    "industry": "...",
    "revenue": "...",
    "ebitda": "...",
    // ... 13 fields total
  },
  "field_confidence": {"revenue": 0.9, "ebitda": 0.7},
  "citations": [{"field": "revenue", "evidence_id": "...", "quote": "..."}],
  "open_questions": ["What is the asking price?"]
}
```

**Acceptance Criteria:**
- ✅ Schemas are valid JSON Schema 2020-12
- ✅ Required fields enforced (schema_version, confidence, citations)
- ✅ Enum constraints on category field
- ✅ Confidence bounded to [0.0, 1.0]

---

#### 1.10 Agent Implementations ✅

**Files:**
- `src/agents/controller.py` (68 lines) - ✅ Complete
- `src/agents/comms.py` (28 lines) - ✅ Complete
- `src/agents/rag_expert.py` (34 lines) - ✅ Prompt pack wired
- `src/agents/deal_sourcing.py` (43 lines) - ✅ Prompt pack wired
- `src/agents/orchestrator.py` (212 lines) - ✅ Task Packet routing wired

**CommsAgent Pattern:**
```python
class CommsAgent(SubAgent):
    AGENT_NAME: str = "Comms"
    MAX_ITERATIONS: int = 3

    def _get_default_tools(self) -> List:
        return []  # No tools (draft-only)

    def _get_system_prompt(self) -> str:
        charter = load_prompt("charter")
        role = load_prompt("role_comms")
        return f"{charter}\n\n{role}"
```

**Acceptance Criteria:**
- ✅ Controller implements Task Packet → ControllerResponse flow
- ✅ CommsAgent inherits from SubAgent base class
- ✅ Agents load prompts via prompt pack system
- ✅ RAG Expert + Deal Sourcing agents load charter + role cards from prompt pack
- ✅ Orchestrator wraps specialized routes in Task Packets (JSON envelope)

---

#### 1.11 Regression Tests ✅

**Files:**
- `scripts/prompt_regression_test.py` (141 lines)
- `scripts/run_prompt_regression_tests.sh` (8 lines)

**Test Coverage (8 tests):**
1. ✅ Prompt pack loads (charter, controller, worker)
2. ✅ Schemas parse as valid JSON
3. ✅ No silent drops (empty answer triggers violation)
4. ✅ Scope gating (global cannot propose write tools)
5. ✅ Approval gating (LOI transition requires approval=true)
6. ✅ Citation minimums (financial claims need citations)
7. ✅ Secret scanning (blocks AKIA keys from cloud send)
8. ✅ Worker rejects tool_calls in output (extra="forbid")

**Usage:**
```bash
python scripts/prompt_regression_test.py
# Exit code 0 = pass, 1 = fail

# Optional wrapper:
bash scripts/run_prompt_regression_tests.sh
```

**Acceptance Criteria:**
- ✅ All 8 tests pass
- ✅ Tests validate guardrails (not just schema)
- ✅ Tests use FakeRouter for deterministic worker testing
- ✅ Exit code usable in CI/CD

---

### Phase 1 Summary

**Lines of Code:**
- Core infrastructure: ~600 lines
- Prompts: ~400 lines
- Tests: ~140 lines
- **Total: ~1,140 lines**

**Key Achievements:**
- ✅ Versioned prompt pack architecture
- ✅ Task Packet protocol with strong typing
- ✅ 4-layer guardrail system
- ✅ Secret scanning gate
- ✅ Controller/worker separation
- ✅ 8 regression tests covering core invariants

**What's Missing:**
- ❌ Evidence bundle construction (no retrieval logic)
- ❌ RAG client (no connection to port 8052)
- ❌ Proposal storage and approval workflow
- ❌ Session management (no durable session store integration)

---

## Phase 2: Critical Operational Components (PLANNED) 🔄

### Scope

Implement the 4 missing components required for end-to-end Chat Front Door operation.

### Timeline Estimate

**Total: 2-3 weeks** (if working full-time)
- Component 2.1: 3-4 days
- Component 2.2: 2-3 days
- Component 2.3: 4-5 days
- Component 2.4: 3-4 days

---

### Component 2.1: Evidence Bundle Builder

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - blocks Chat Front Door)
**Estimated Effort:** 3-4 days

#### Purpose

Construct the evidence bundle by retrieving relevant context from 5 sources in parallel:
1. **RAG** (semantic search over DataRoom)
2. **Events** (deal activity timeline)
3. **Case File** (structured deal summary)
4. **Registry** (current state: stage, status, quarantine)
5. **Actions** (pending tasks and due dates)

#### Technical Specification

**New File:** `src/core/evidence_builder.py` (~300 lines)

```python
from dataclasses import dataclass
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.task_packet import EvidenceItem

@dataclass
class EvidenceLimits:
    """Character limits per source to prevent context overflow."""
    max_total: int = 40_000
    max_rag: int = 8_000        # ~8 chunks @ 1000 chars each
    max_events: int = 12_000    # ~20 events @ 600 chars each
    max_case_file: int = 10_000  # Full case file
    max_registry: int = 5_000    # Current state
    max_actions: int = 5_000     # Pending actions

class EvidenceBuilder:
    """
    Parallel evidence retrieval with deduplication and truncation.
    """

    def __init__(
        self,
        rag_client: "RAGClient",
        event_store: "EventStore",
        registry: "Registry",
        limits: Optional[EvidenceLimits] = None,
    ):
        self.rag_client = rag_client
        self.event_store = event_store
        self.registry = registry
        self.limits = limits or EvidenceLimits()

    def build_bundle(
        self,
        question: str,
        deal_id: Optional[str] = None,
        scope_type: str = "global",
    ) -> List[EvidenceItem]:
        """
        Build evidence bundle with parallel retrieval.

        Returns:
            List of EvidenceItem sorted by relevance, deduplicated,
            truncated to total limit.
        """

        # 1. Parallel retrieval from all sources
        evidence = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._retrieve_rag, question, deal_id): "rag",
                executor.submit(self._retrieve_events, deal_id): "events",
                executor.submit(self._retrieve_case_file, deal_id): "case_file",
                executor.submit(self._retrieve_registry, deal_id): "registry",
                executor.submit(self._retrieve_actions, deal_id): "actions",
            }

            for future in as_completed(futures):
                source = futures[future]
                try:
                    items = future.result(timeout=5)
                    evidence.extend(items)
                except Exception as e:
                    logger.warning(f"evidence_retrieval_failed", source=source, error=str(e))

        # 2. Deduplication by content_hash
        seen_hashes = set()
        deduplicated = []
        for item in evidence:
            if item.content_hash and item.content_hash in seen_hashes:
                continue
            seen_hashes.add(item.content_hash)
            deduplicated.append(item)

        # 3. Truncation per source
        truncated = self._truncate_by_source(deduplicated)

        # 4. Sort by relevance (RAG scores first, then timestamp)
        sorted_evidence = self._sort_by_relevance(truncated)

        # 5. Final truncation to total limit
        return self._truncate_total(sorted_evidence, self.limits.max_total)

    def _retrieve_rag(self, question: str, deal_id: Optional[str]) -> List[EvidenceItem]:
        """Query RAG endpoint for semantic chunks."""
        chunks = self.rag_client.query(
            question=question,
            deal_id=deal_id,
            k=8,
            score_threshold=0.5,
        )
        return [
            EvidenceItem(
                id=f"rag_{i}",
                type="rag_chunk",
                ref={
                    "url": chunk.url,
                    "path": chunk.path,
                    "chunk_number": chunk.chunk_number,
                },
                content_excerpt=chunk.text[:500],
                content_hash=hashlib.sha256(chunk.text.encode()).hexdigest()[:16],
            )
            for i, chunk in enumerate(chunks)
        ]

    def _retrieve_events(self, deal_id: Optional[str]) -> List[EvidenceItem]:
        """Retrieve recent deal events."""
        if not deal_id:
            return []

        events = self.event_store.get_recent(deal_id, limit=20)
        return [
            EvidenceItem(
                id=f"event_{event.event_id}",
                type="event",
                ref={"event_id": event.event_id, "deal_id": deal_id},
                timestamp=event.timestamp,
                content_excerpt=event.summary[:200],
                content_hash=event.event_id,  # Event ID is unique
            )
            for event in events
        ]

    def _retrieve_case_file(self, deal_id: Optional[str]) -> List[EvidenceItem]:
        """Retrieve structured case file."""
        if not deal_id:
            return []

        case_file = self.registry.get_case_file(deal_id)
        if not case_file:
            return []

        # Case file as single evidence item
        return [
            EvidenceItem(
                id="case_file",
                type="case_file",
                ref={"deal_id": deal_id, "path": f"DataRoom/{deal_id}/case_file.json"},
                content_excerpt=json.dumps(case_file)[:10000],
                content_hash=hashlib.sha256(json.dumps(case_file).encode()).hexdigest()[:16],
            )
        ]

    def _retrieve_registry(self, deal_id: Optional[str]) -> List[EvidenceItem]:
        """Retrieve current deal state from registry."""
        if not deal_id:
            return []

        state = self.registry.get_state(deal_id)
        if not state:
            return []

        return [
            EvidenceItem(
                id="registry",
                type="registry",
                ref={"deal_id": deal_id},
                content_excerpt=json.dumps({
                    "stage": state.stage,
                    "status": state.status,
                    "quarantine": state.quarantine,
                })[:5000],
                content_hash=f"registry_{deal_id}",
            )
        ]

    def _retrieve_actions(self, deal_id: Optional[str]) -> List[EvidenceItem]:
        """Retrieve pending actions."""
        if not deal_id:
            return []

        actions = self.registry.get_pending_actions(deal_id, limit=10)
        return [
            EvidenceItem(
                id=f"action_{action.action_id}",
                type="action",
                ref={"action_id": action.action_id, "deal_id": deal_id},
                timestamp=action.due_date,
                content_excerpt=f"{action.title} (due: {action.due_date})",
                content_hash=action.action_id,
            )
            for action in actions
        ]

    def _truncate_by_source(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Truncate each source type to its limit."""
        by_type = {}
        for item in evidence:
            by_type.setdefault(item.type, []).append(item)

        limits = {
            "rag_chunk": self.limits.max_rag,
            "event": self.limits.max_events,
            "case_file": self.limits.max_case_file,
            "registry": self.limits.max_registry,
            "action": self.limits.max_actions,
        }

        truncated = []
        for type_, items in by_type.items():
            limit = limits.get(type_, 5000)
            char_count = 0
            for item in items:
                item_size = len(item.content_excerpt or "")
                if char_count + item_size <= limit:
                    truncated.append(item)
                    char_count += item_size
                else:
                    break

        return truncated

    def _sort_by_relevance(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Sort by source priority: RAG > case_file > events > registry > actions."""
        priority = {"rag_chunk": 0, "case_file": 1, "event": 2, "registry": 3, "action": 4, "note": 5}
        return sorted(evidence, key=lambda e: priority.get(e.type, 99))

    def _truncate_total(self, evidence: List[EvidenceItem], max_chars: int) -> List[EvidenceItem]:
        """Truncate total evidence to max character limit."""
        total = 0
        result = []
        for item in evidence:
            size = len(item.content_excerpt or "")
            if total + size <= max_chars:
                result.append(item)
                total += size
            else:
                break
        return result
```

#### Dependencies

- **RAGClient** (Component 2.2) - for semantic search
- **EventStore** - existing (needs interface verification)
- **Registry** - existing (needs interface verification)

#### Integration Points

1. **Chat Front Door** → calls `EvidenceBuilder.build_bundle()` before controller invocation
2. **Task Packet** → evidence list populated from builder output
3. **Metrics** → track retrieval latency per source

#### Acceptance Criteria

- [ ] Retrieves from all 5 sources in parallel (max 5s total)
- [ ] Deduplicates by content_hash
- [ ] Respects per-source character limits
- [ ] Truncates to 40KB total
- [ ] Returns empty list gracefully if sources unavailable
- [ ] Logs warnings for failed source retrievals
- [ ] Unit tests for:
  - [ ] Parallel retrieval
  - [ ] Deduplication
  - [ ] Truncation (per-source and total)
  - [ ] Relevance sorting

#### Success Metrics

- Evidence retrieval latency p95 < 3 seconds
- Deduplication rate: 5-10% (expected overlap)
- Source contribution: RAG 40%, Events 30%, Case File 20%, Other 10%

---

### Component 2.2: RAG Client Integration

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - blocks evidence retrieval)
**Estimated Effort:** 2-3 days

#### Purpose

Connect to the RAG service running on port 8052 to perform semantic search over DataRoom documents.

#### Technical Specification

**New File:** `src/clients/rag_client.py` (~200 lines)

```python
import requests
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RAGChunk:
    """Single chunk from RAG query result."""
    url: str              # Synthetic URL (dataroom://...)
    path: str             # Filesystem path
    chunk_number: int     # Chunk index in document
    text: str             # Chunk content
    score: float          # Relevance score (0.0-1.0)
    metadata: dict        # Additional metadata (deal_id, doc_type, etc.)

class RAGClient:
    """
    Client for ZakOps RAG service (port 8052).

    Configuration:
        RAG_ENDPOINT=http://localhost:8052/rag/query
        RAG_TIMEOUT=5
        RAG_RETRIES=2
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:8052/rag/query",
        timeout: int = 5,
        retries: int = 2,
    ):
        self.endpoint = endpoint
        self.timeout = timeout
        self.retries = retries

    def query(
        self,
        question: str,
        *,
        deal_id: Optional[str] = None,
        k: int = 8,
        score_threshold: float = 0.5,
        source: str = "dataroom.local",
    ) -> List[RAGChunk]:
        """
        Query RAG service for relevant chunks.

        Args:
            question: Natural language query
            deal_id: Optional deal filter (searches only this deal's docs)
            k: Number of chunks to return
            score_threshold: Minimum relevance score (0.0-1.0)
            source: Source filter (default: dataroom.local)

        Returns:
            List of RAGChunk sorted by relevance (highest first)

        Raises:
            RAGClientError: On connection or server errors
        """

        payload = {
            "query": question,
            "match_count": k,
            "filter_metadata": {},
        }

        # Add source filter
        if source:
            payload["source"] = source

        # Add deal_id filter
        if deal_id:
            payload["filter_metadata"]["deal_id"] = deal_id

        # Retry logic
        last_error = None
        for attempt in range(self.retries):
            try:
                resp = requests.post(
                    self.endpoint,
                    json=payload,
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                data = resp.json()

                # Parse response
                chunks = []
                for item in data.get("results", []):
                    # Skip low-relevance chunks
                    if item.get("score", 0) < score_threshold:
                        continue

                    chunks.append(RAGChunk(
                        url=item.get("url", ""),
                        path=item.get("metadata", {}).get("path", ""),
                        chunk_number=item.get("metadata", {}).get("chunk_number", 0),
                        text=item.get("content", ""),
                        score=item.get("score", 0.0),
                        metadata=item.get("metadata", {}),
                    ))

                return chunks

            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.retries - 1:
                    logger.warning(f"rag_query_retry", attempt=attempt, error=str(e))
                    continue

        # All retries failed
        raise RAGClientError(f"RAG query failed after {self.retries} attempts: {last_error}")

    def health_check(self) -> bool:
        """Check if RAG service is reachable."""
        try:
            resp = requests.get(f"{self.endpoint}/health", timeout=2)
            return resp.status_code == 200
        except:
            return False

class RAGClientError(Exception):
    """Raised when RAG client encounters errors."""
    pass
```

#### Configuration

Add to `.env`:
```bash
RAG_ENDPOINT=http://localhost:8052/rag/query
RAG_SOURCE=dataroom.local
RAG_TIMEOUT=5
RAG_RETRIES=2
```

Add to `src/core/config.py`:
```python
class Config:
    # ... existing fields ...

    RAG_ENDPOINT: str = "http://localhost:8052/rag/query"
    RAG_SOURCE: str = "dataroom.local"
    RAG_TIMEOUT: int = 5
    RAG_RETRIES: int = 2
```

#### Dependencies

- **RAG Service** - Must be running on port 8052
- **requests** library - Add to requirements.txt

#### Integration Points

1. **EvidenceBuilder** → calls `RAGClient.query()` for semantic chunks
2. **Health Check** → `/api/health` endpoint checks RAG availability
3. **Metrics** → track query latency and error rate

#### Acceptance Criteria

- [ ] Connects to RAG service on port 8052
- [ ] Sends query with deal_id filter
- [ ] Parses response into RAGChunk objects
- [ ] Filters by score_threshold
- [ ] Retries on transient errors (timeout, 5xx)
- [ ] Returns empty list on RAG unavailability (no crash)
- [ ] Unit tests for:
  - [ ] Successful query parsing
  - [ ] Score threshold filtering
  - [ ] Retry logic
  - [ ] Error handling (connection refused, timeout)

#### Success Metrics

- RAG query latency p95 < 2 seconds
- Error rate < 1% (99% success)
- Availability: RAG service must be up 99.9%

---

### Component 2.3: Proposal Store & Approval Workflow

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - blocks write operations)
**Estimated Effort:** 4-5 days

#### Purpose

Durably store controller proposals + approvals with a full audit trail (durable-first). Redis may be used as an optional cache/adapter, but must not be the source of truth.

**Design Note (durable-first):**
- Persist proposal lifecycle transitions durably (filesystem/DB; append-only preferred).
- Emit control-plane events + run-ledger records for create/approve/reject/execute/expire.
- If Redis is used, treat it as a cache/acceleration layer that can be rebuilt from the durable record.

#### Technical Specification

**New File:** `src/core/proposal_store.py` (~400 lines)

**Implementation Options (choose one as the source of truth):**
- **FileProposalStore (recommended)**: append-only JSONL under the DataRoom control plane (audit-friendly).
- **RedisProposalStore (optional)**: only if paired with a durable store; do not use Redis as the source of truth.

```python
import json
import redis
from typing import Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from core.prompt_protocol import ControllerProposal

@dataclass
class ProposalMetadata:
    """Metadata tracked for each proposal."""
    proposal_id: str
    created_at: datetime
    expires_at: datetime
    status: str  # pending | approved | rejected | expired | executed
    created_by: str  # component (e.g., "chat_front_door")
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    execution_result: Optional[dict] = None

class RedisProposalStore:
    """
    Optional Redis-backed proposal cache/adapter with TTL and approval workflow.

    Keys:
        proposal:{proposal_id} → JSON (ControllerProposal + metadata)
        proposal:{proposal_id}:status → string (pending/approved/rejected/expired/executed)
        proposal_index:{deal_id} → set (proposal_ids for this deal)
        proposal_pending → sorted set (score=expires_at timestamp)

    TTL: 7 days (604800 seconds)
    """

    TTL_SECONDS = 604800  # 7 days

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def save(
        self,
        proposal: ControllerProposal,
        *,
        deal_id: Optional[str] = None,
        created_by: str = "unknown",
    ) -> ProposalMetadata:
        """
        Save proposal to Redis with 7-day TTL.

        Returns:
            ProposalMetadata with created_at and expires_at
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self.TTL_SECONDS)

        metadata = ProposalMetadata(
            proposal_id=proposal.proposal_id,
            created_at=now,
            expires_at=expires_at,
            status="pending",
            created_by=created_by,
        )

        # Store proposal + metadata
        data = {
            "proposal": proposal.model_dump(),
            "metadata": {
                "proposal_id": metadata.proposal_id,
                "created_at": metadata.created_at.isoformat(),
                "expires_at": metadata.expires_at.isoformat(),
                "status": metadata.status,
                "created_by": metadata.created_by,
            },
        }

        key = f"proposal:{proposal.proposal_id}"
        self.redis.set(key, json.dumps(data), ex=self.TTL_SECONDS)

        # Add to pending sorted set (for auto-expiry check)
        self.redis.zadd("proposal_pending", {proposal.proposal_id: expires_at.timestamp()})

        # Add to deal index (if deal_id provided)
        if deal_id:
            self.redis.sadd(f"proposal_index:{deal_id}", proposal.proposal_id)
            self.redis.expire(f"proposal_index:{deal_id}", self.TTL_SECONDS)

        logger.info(
            "proposal_saved",
            proposal_id=proposal.proposal_id,
            tool=proposal.tool,
            deal_id=deal_id,
            expires_at=expires_at.isoformat(),
        )

        return metadata

    def get(self, proposal_id: str) -> Optional[tuple[ControllerProposal, ProposalMetadata]]:
        """
        Retrieve proposal by ID.

        Returns:
            (ControllerProposal, ProposalMetadata) or None if not found/expired
        """
        key = f"proposal:{proposal_id}"
        data_str = self.redis.get(key)
        if not data_str:
            return None

        data = json.loads(data_str)
        proposal = ControllerProposal.model_validate(data["proposal"])

        metadata = ProposalMetadata(
            proposal_id=data["metadata"]["proposal_id"],
            created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
            expires_at=datetime.fromisoformat(data["metadata"]["expires_at"]),
            status=data["metadata"]["status"],
            created_by=data["metadata"]["created_by"],
            approved_by=data["metadata"].get("approved_by"),
            approved_at=datetime.fromisoformat(data["metadata"]["approved_at"]) if data["metadata"].get("approved_at") else None,
            executed_at=datetime.fromisoformat(data["metadata"]["executed_at"]) if data["metadata"].get("executed_at") else None,
            execution_result=data["metadata"].get("execution_result"),
        )

        return proposal, metadata

    def approve(self, proposal_id: str, operator_id: str) -> bool:
        """
        Mark proposal as approved.

        Returns:
            True if approved, False if not found or already executed
        """
        result = self.get(proposal_id)
        if not result:
            logger.warning("proposal_not_found", proposal_id=proposal_id)
            return False

        proposal, metadata = result

        if metadata.status != "pending":
            logger.warning(
                "proposal_not_pending",
                proposal_id=proposal_id,
                status=metadata.status,
            )
            return False

        # Update metadata
        metadata.status = "approved"
        metadata.approved_by = operator_id
        metadata.approved_at = datetime.utcnow()

        # Update in Redis
        self._update_metadata(proposal, metadata)

        # Remove from pending sorted set
        self.redis.zrem("proposal_pending", proposal_id)

        logger.info(
            "proposal_approved",
            proposal_id=proposal_id,
            operator_id=operator_id,
        )

        return True

    def reject(self, proposal_id: str, operator_id: str, reason: str = "") -> bool:
        """Mark proposal as rejected."""
        result = self.get(proposal_id)
        if not result:
            return False

        proposal, metadata = result

        if metadata.status != "pending":
            return False

        metadata.status = "rejected"
        metadata.approved_by = operator_id
        metadata.approved_at = datetime.utcnow()

        self._update_metadata(proposal, metadata)
        self.redis.zrem("proposal_pending", proposal_id)

        logger.info(
            "proposal_rejected",
            proposal_id=proposal_id,
            operator_id=operator_id,
            reason=reason,
        )

        return True

    def execute(
        self,
        proposal_id: str,
        *,
        executor: "ProposalExecutor",
    ) -> dict:
        """
        Execute approved proposal.

        Returns:
            Execution result dict

        Raises:
            ProposalNotApprovedError: If proposal not in approved state
        """
        result = self.get(proposal_id)
        if not result:
            raise ProposalNotFoundError(proposal_id)

        proposal, metadata = result

        if metadata.status != "approved":
            raise ProposalNotApprovedError(
                f"Proposal {proposal_id} is {metadata.status}, not approved"
            )

        # Execute via executor
        execution_result = executor.execute(proposal)

        # Update metadata
        metadata.status = "executed"
        metadata.executed_at = datetime.utcnow()
        metadata.execution_result = execution_result

        self._update_metadata(proposal, metadata)

        logger.info(
            "proposal_executed",
            proposal_id=proposal_id,
            tool=proposal.tool,
            success=execution_result.get("success", False),
        )

        return execution_result

    def list_pending(self, deal_id: Optional[str] = None) -> List[tuple[ControllerProposal, ProposalMetadata]]:
        """
        List all pending proposals (optionally filtered by deal_id).
        """
        if deal_id:
            # Get from deal index
            proposal_ids = self.redis.smembers(f"proposal_index:{deal_id}")
        else:
            # Get all from pending sorted set
            proposal_ids = self.redis.zrange("proposal_pending", 0, -1)

        results = []
        for pid in proposal_ids:
            pid_str = pid.decode() if isinstance(pid, bytes) else pid
            result = self.get(pid_str)
            if result:
                proposal, metadata = result
                if metadata.status == "pending":
                    results.append((proposal, metadata))

        return results

    def expire_old(self) -> int:
        """
        Mark expired proposals as expired (for cleanup).

        Returns:
            Count of expired proposals
        """
        now = datetime.utcnow().timestamp()
        # Get proposals with score (expires_at) < now
        expired_ids = self.redis.zrangebyscore("proposal_pending", 0, now)

        count = 0
        for pid in expired_ids:
            pid_str = pid.decode() if isinstance(pid, bytes) else pid
            result = self.get(pid_str)
            if result:
                proposal, metadata = result
                if metadata.status == "pending":
                    metadata.status = "expired"
                    self._update_metadata(proposal, metadata)
                    count += 1

            # Remove from pending set
            self.redis.zrem("proposal_pending", pid_str)

        if count > 0:
            logger.info("proposals_expired", count=count)

        return count

    def _update_metadata(self, proposal: ControllerProposal, metadata: ProposalMetadata):
        """Update metadata in Redis (preserves TTL)."""
        key = f"proposal:{proposal.proposal_id}"
        data = {
            "proposal": proposal.model_dump(),
            "metadata": {
                "proposal_id": metadata.proposal_id,
                "created_at": metadata.created_at.isoformat(),
                "expires_at": metadata.expires_at.isoformat(),
                "status": metadata.status,
                "created_by": metadata.created_by,
                "approved_by": metadata.approved_by,
                "approved_at": metadata.approved_at.isoformat() if metadata.approved_at else None,
                "executed_at": metadata.executed_at.isoformat() if metadata.executed_at else None,
                "execution_result": metadata.execution_result,
            },
        }

        # Get remaining TTL
        ttl = self.redis.ttl(key)
        if ttl > 0:
            self.redis.set(key, json.dumps(data), ex=ttl)

class ProposalNotFoundError(Exception):
    pass

class ProposalNotApprovedError(Exception):
    pass
```

**New File:** `src/core/proposal_executor.py` (~200 lines)

```python
from core.prompt_protocol import ControllerProposal

class ProposalExecutor:
    """
    Executes approved proposals by invoking the appropriate tool.
    """

    def __init__(self, tool_registry: dict):
        """
        Args:
            tool_registry: Map of tool name → callable
                Example: {
                    "schedule_action": schedule_action_handler,
                    "draft_email": draft_email_handler,
                    ...
                }
        """
        self.tool_registry = tool_registry

    def execute(self, proposal: ControllerProposal) -> dict:
        """
        Execute proposal by calling registered tool.

        Returns:
            {
                "success": bool,
                "result": any,
                "error": str (if success=False),
            }
        """
        tool_name = proposal.tool
        tool_fn = self.tool_registry.get(tool_name)

        if not tool_fn:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
            }

        try:
            result = tool_fn(**proposal.args)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            logger.error(
                "proposal_execution_failed",
                proposal_id=proposal.proposal_id,
                tool=tool_name,
                error=str(e),
            )
            return {
                "success": False,
                "error": str(e),
            }
```

#### Configuration

Add to `.env`:
```bash
PROPOSAL_STORE=file
PROPOSAL_STORE_DIR=/home/zaks/DataRoom/.deal-registry/proposals

# Optional (only if PROPOSAL_STORE=redis or using Redis cache):
REDIS_URL=redis://localhost:6379/0
PROPOSAL_TTL_DAYS=7
```

Add to `src/core/config.py`:
```python
class Config:
    # ... existing fields ...

    PROPOSAL_STORE: str = "file"
    PROPOSAL_STORE_DIR: str = "/home/zaks/DataRoom/.deal-registry/proposals"
    PROPOSAL_TTL_DAYS: int = 7
    REDIS_URL: str = "redis://localhost:6379/0"  # optional
```

#### Dependencies

- **None required** for file-based durable store
- **Optional:** Redis + `redis` Python library (cache/adapter only; not source of truth)

#### Integration Points

1. **Chat Front Door** → When controller returns `status="proposal"`:
   - Save proposals to ProposalStore
   - Return proposal_id to operator
2. **Approval UI** → Operator approves/rejects via API
3. **Execution** → Approved proposals executed via ProposalExecutor
4. **Auto-expiry** → Cron job calls `expire_old()` every hour

#### Acceptance Criteria

- [ ] Saves proposals durably (survives restarts) with 7-day TTL policy
- [ ] Redis (if enabled) is a cache/adapter only and can be rebuilt from the durable record
- [ ] Tracks status transitions (pending → approved/rejected/expired → executed)
- [ ] Lists pending proposals by deal_id
- [ ] Marks expired proposals after 7 days
- [ ] Executes approved proposals via tool registry
- [ ] Prevents execution of non-approved proposals
- [ ] Unit tests for:
  - [ ] Save/retrieve roundtrip
  - [ ] Approval workflow
  - [ ] Rejection workflow
  - [ ] Expiry detection
  - [ ] Execution success/failure

#### Success Metrics

- Proposal approval latency: operator turnaround < 5 minutes
- Expiry rate: < 10% (90% get approved/rejected before expiry)
- Execution success rate: > 95%

---

### Component 2.4: Session Management

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH - needed for multi-turn chat)
**Estimated Effort:** 3-4 days

#### Purpose

Manage conversation sessions with TTL + context summarization. Redis may be used as an optional cache/adapter, but sessions should work in durable file-based or stateless mode.

**Design Note (durable-first):**
- Sessions are *derived state* (not a source of truth). The deal case file + event log remain canonical.
- Prefer file-based session persistence (audit-friendly) or stateless client sessions for v1.
- If Redis is used, treat it as optional acceleration only (must be rebuildable).

#### Technical Specification

**New File:** `src/core/session_manager.py` (~350 lines)

```python
import json
import redis
import uuid
from typing import Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class Message:
    """Single message in conversation history."""
    role: str  # user | assistant | system
    content: str
    timestamp: datetime
    metadata: dict

@dataclass
class SessionContext:
    """Session state including conversation history."""
    session_id: str
    user_id: str
    deal_id: Optional[str]
    created_at: datetime
    last_active: datetime
    message_count: int
    messages: List[Message]
    summary: Optional[str] = None

class SessionManager:
    """
    Optional Redis-backed session management with 24-hour TTL.

    Keys:
        session:{session_id} → JSON (SessionContext)
        session_index:{user_id} → set (session_ids for this user)
        session_active → sorted set (score=last_active timestamp)

    TTL: 24 hours (86400 seconds)
    """

    TTL_SECONDS = 86400  # 24 hours
    MAX_MESSAGES_IN_CONTEXT = 20  # Beyond this, summarize older messages

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def create_session(
        self,
        user_id: str,
        deal_id: Optional[str] = None,
    ) -> str:
        """
        Create new session.

        Returns:
            session_id (UUID)
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        context = SessionContext(
            session_id=session_id,
            user_id=user_id,
            deal_id=deal_id,
            created_at=now,
            last_active=now,
            message_count=0,
            messages=[],
            summary=None,
        )

        self._save_context(context)

        # Add to user index
        self.redis.sadd(f"session_index:{user_id}", session_id)
        self.redis.expire(f"session_index:{user_id}", self.TTL_SECONDS)

        # Add to active sorted set
        self.redis.zadd("session_active", {session_id: now.timestamp()})

        logger.info(
            "session_created",
            session_id=session_id,
            user_id=user_id,
            deal_id=deal_id,
        )

        return session_id

    def get_context(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve session context.

        Returns:
            SessionContext or None if expired/not found
        """
        key = f"session:{session_id}"
        data_str = self.redis.get(key)
        if not data_str:
            return None

        data = json.loads(data_str)
        return SessionContext(
            session_id=data["session_id"],
            user_id=data["user_id"],
            deal_id=data.get("deal_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_active=datetime.fromisoformat(data["last_active"]),
            message_count=data["message_count"],
            messages=[
                Message(
                    role=m["role"],
                    content=m["content"],
                    timestamp=datetime.fromisoformat(m["timestamp"]),
                    metadata=m.get("metadata", {}),
                )
                for m in data["messages"]
            ],
            summary=data.get("summary"),
        )

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Add message to session history.

        Returns:
            True if added, False if session not found
        """
        context = self.get_context(session_id)
        if not context:
            logger.warning("session_not_found", session_id=session_id)
            return False

        # Add message
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
        )
        context.messages.append(message)
        context.message_count += 1
        context.last_active = datetime.utcnow()

        # Summarize if too many messages
        if len(context.messages) > self.MAX_MESSAGES_IN_CONTEXT:
            context = self._summarize_old_messages(context)

        # Save updated context
        self._save_context(context)

        # Update active sorted set
        self.redis.zadd("session_active", {session_id: context.last_active.timestamp()})

        return True

    def update_summary(self, session_id: str, summary: str) -> bool:
        """Update conversation summary."""
        context = self.get_context(session_id)
        if not context:
            return False

        context.summary = summary
        context.last_active = datetime.utcnow()
        self._save_context(context)

        return True

    def end_session(self, session_id: str):
        """Explicitly end session (delete from Redis)."""
        context = self.get_context(session_id)
        if not context:
            return

        # Remove from Redis
        self.redis.delete(f"session:{session_id}")
        self.redis.srem(f"session_index:{context.user_id}", session_id)
        self.redis.zrem("session_active", session_id)

        logger.info("session_ended", session_id=session_id)

    def list_user_sessions(self, user_id: str) -> List[str]:
        """List all active sessions for a user."""
        session_ids = self.redis.smembers(f"session_index:{user_id}")
        return [sid.decode() if isinstance(sid, bytes) else sid for sid in session_ids]

    def expire_inactive(self, hours: int = 24) -> int:
        """
        Delete sessions inactive for > N hours.

        Returns:
            Count of expired sessions
        """
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
        expired_ids = self.redis.zrangebyscore("session_active", 0, cutoff)

        count = 0
        for sid in expired_ids:
            sid_str = sid.decode() if isinstance(sid, bytes) else sid
            self.end_session(sid_str)
            count += 1

        if count > 0:
            logger.info("sessions_expired", count=count)

        return count

    def _save_context(self, context: SessionContext):
        """Save context to Redis with TTL."""
        key = f"session:{context.session_id}"
        data = {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "deal_id": context.deal_id,
            "created_at": context.created_at.isoformat(),
            "last_active": context.last_active.isoformat(),
            "message_count": context.message_count,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "metadata": m.metadata,
                }
                for m in context.messages
            ],
            "summary": context.summary,
        }

        self.redis.set(key, json.dumps(data), ex=self.TTL_SECONDS)

    def _summarize_old_messages(self, context: SessionContext) -> SessionContext:
        """
        Summarize messages beyond MAX_MESSAGES_IN_CONTEXT.

        Strategy:
        - Keep last 10 messages in full
        - Summarize older messages into context.summary
        """
        if len(context.messages) <= self.MAX_MESSAGES_IN_CONTEXT:
            return context

        # Split: old (to summarize) and recent (keep)
        split_idx = len(context.messages) - 10
        old_messages = context.messages[:split_idx]
        recent_messages = context.messages[split_idx:]

        # Generate summary (simple concatenation for now; could use LLM)
        summary_lines = []
        for msg in old_messages:
            summary_lines.append(f"{msg.role}: {msg.content[:100]}...")

        existing_summary = context.summary or ""
        new_summary = existing_summary + "\n\n" + "\n".join(summary_lines)

        context.summary = new_summary.strip()
        context.messages = recent_messages

        logger.info(
            "session_summarized",
            session_id=context.session_id,
            old_message_count=len(old_messages),
            new_message_count=len(recent_messages),
        )

        return context
```

#### Configuration

Add to `.env`:
```bash
SESSION_STORE=file
SESSION_STORE_DIR=/home/zaks/DataRoom/.deal-registry/sessions
SESSION_TTL_HOURS=24
SESSION_MAX_MESSAGES=20

# Optional (only if SESSION_STORE=redis):
REDIS_URL=redis://localhost:6379/0
```

#### Dependencies

- **None required** for file-based sessions
- **Optional:** Redis + `redis` Python library (only if SESSION_STORE=redis)

#### Integration Points

1. **Chat Front Door** → Create session on first message
2. **Task Packet** → Include `memory.session_id` field
3. **Controller** → Load session context for multi-turn awareness
4. **Auto-expiry** → Cron job calls `expire_inactive()` every hour

#### Acceptance Criteria

- [ ] Creates session with UUID
- [ ] Stores messages with 24-hour TTL
- [ ] Refreshes TTL on activity
- [ ] Summarizes messages beyond limit (20)
- [ ] Lists sessions by user_id
- [ ] Expires inactive sessions
- [ ] Unit tests for:
  - [ ] Session creation
  - [ ] Message addition
  - [ ] Context retrieval
  - [ ] Summarization trigger
  - [ ] Expiry detection

#### Success Metrics

- Session duration p50: 5 minutes, p95: 2 hours
- Message count per session: median 4, p95: 15
- Summarization trigger rate: 10% of sessions

---

### Phase 2 Summary

**Total Effort:** 2-3 weeks full-time

**New Files:**
- `src/core/evidence_builder.py` (~300 lines)
- `src/clients/rag_client.py` (~200 lines)
- `src/core/proposal_store.py` (~400 lines)
- `src/core/proposal_executor.py` (~200 lines)
- `src/core/session_manager.py` (~350 lines)
- **Total: ~1,450 lines**

**Dependencies Added:**
- `requests` library (for RAG client)
- Optional: Redis + `redis` Python library (only if *_STORE=redis or using Redis cache)

**Configuration Updates:**
- RAG endpoint, timeout, retries
- Proposal/session store selection + paths
- Optional Redis URL (only if store/cache uses Redis)
- Session/proposal TTL settings

**Integration Work:**
- Chat Front Door endpoint updates
- Health check endpoint (RAG + optional Redis availability)
- Cron jobs for expiry (proposals + sessions; durable-first)

---

## Phase 3: Quality & Operations (PLANNED) 🔄

### Scope

Polish implementation to production-ready standards with testing, metrics, and operational runbooks.

### Timeline Estimate

**Total: 1-2 weeks**
- Testing: 4-5 days
- Metrics: 2-3 days
- Documentation: 2-3 days

---

### Component 3.1: Expanded Testing

**Priority:** P1 (HIGH)
**Effort:** 4-5 days

#### Test Additions

1. **Prompt Injection Tests** (100+ vectors)
   - Jailbreak attempts
   - System prompt leakage
   - Tool call smuggling
   - SQL injection patterns (for extraction)

2. **Integration Tests**
   - End-to-end Chat Front Door flow
   - RAG → Evidence → Controller → Response
   - Proposal → Approval → Execution
   - Session → Multi-turn chat

3. **Load Tests**
   - 100 concurrent users
   - 1000 requests/min sustained
   - Latency under load (p95 < 5s)

4. **Guardrail Stress Tests**
   - Edge cases for each guardrail
   - Malformed packets
   - Missing required fields

#### Test Files to Create

- `tests/test_prompt_injection.py` (100+ test cases)
- `tests/integration/test_chat_front_door.py`
- `tests/integration/test_evidence_builder.py`
- `tests/integration/test_proposal_workflow.py`
- `tests/load/locustfile.py` (Locust load test)

#### Acceptance Criteria

- [ ] 100+ prompt injection vectors tested
- [ ] Integration tests cover happy path + 5 error scenarios
- [ ] Load test achieves 1000 req/min with p95 < 5s
- [ ] Test coverage > 80% for Phase 2 components

---

### Component 3.2: Metrics & Observability

**Priority:** P1 (HIGH)
**Effort:** 2-3 days

#### Prometheus Metrics to Add

**File:** `src/core/metrics.py` (~150 lines)

```python
from prometheus_client import Counter, Histogram, Gauge

# Guardrails
guardrail_violations = Counter(
    "zakops_guardrail_violations_total",
    "Guardrail violations by type",
    ["violation_type"],
)

# Secret scanning
secret_scan_hits = Counter(
    "zakops_secret_scan_hits_total",
    "Secret scan detections by pattern",
    ["pattern_name"],
)

# Evidence retrieval
evidence_retrieval_duration = Histogram(
    "zakops_evidence_retrieval_seconds",
    "Evidence retrieval latency by source",
    ["source"],
)

evidence_items_retrieved = Histogram(
    "zakops_evidence_items_count",
    "Number of evidence items per bundle",
    ["source"],
)

# RAG
rag_query_duration = Histogram(
    "zakops_rag_query_seconds",
    "RAG query latency",
)

rag_chunks_returned = Histogram(
    "zakops_rag_chunks_count",
    "Number of chunks per RAG query",
)

# Proposals
proposals_created = Counter(
    "zakops_proposals_created_total",
    "Proposals created by tool",
    ["tool"],
)

proposals_approved = Counter(
    "zakops_proposals_approved_total",
    "Proposals approved",
)

proposals_rejected = Counter(
    "zakops_proposals_rejected_total",
    "Proposals rejected",
)

proposals_expired = Counter(
    "zakops_proposals_expired_total",
    "Proposals expired",
)

proposals_executed = Counter(
    "zakops_proposals_executed_total",
    "Proposals executed",
    ["tool", "success"],
)

# Sessions
sessions_created = Counter(
    "zakops_sessions_created_total",
    "Sessions created",
)

session_message_count = Histogram(
    "zakops_session_messages_count",
    "Messages per session",
)

session_duration = Histogram(
    "zakops_session_duration_seconds",
    "Session duration",
)

# Controller
controller_response_duration = Histogram(
    "zakops_controller_response_seconds",
    "Controller response time",
)

controller_response_status = Counter(
    "zakops_controller_responses_total",
    "Controller responses by status",
    ["status"],  # answer | proposal | error
)

# Worker
worker_response_duration = Histogram(
    "zakops_worker_response_seconds",
    "Worker response time",
    ["task_type"],
)

worker_confidence = Histogram(
    "zakops_worker_confidence",
    "Worker confidence scores",
    ["task_type"],
)

worker_blocked = Counter(
    "zakops_worker_blocked_total",
    "Worker blocked responses",
    ["reason"],
)
```

#### Grafana Dashboard

Create `monitoring/grafana_dashboard.json` with panels for:
- Request rate (req/min)
- Response latency (p50/p95/p99)
- Error rate
- Guardrail violation rate
- Secret scan hit rate
- Proposal approval rate
- Session metrics

#### Acceptance Criteria

- [ ] Prometheus metrics endpoint `/metrics`
- [ ] All Phase 2 components instrumented
- [ ] Grafana dashboard deployed
- [ ] Alerts configured (error rate > 5%, latency p95 > 10s)

---

### Component 3.3: Operational Runbooks

**Priority:** P2 (MEDIUM)
**Effort:** 2-3 days

#### Runbooks to Create

**File:** `docs/runbooks/01_guardrail_violation.md`

```markdown
# Runbook: Guardrail Violation

## Symptoms
- `zakops_guardrail_violations_total` counter increasing
- Controller returns `status="error"` with `code="guardrail_violation"`

## Diagnosis
1. Check logs for violation details:
   ```bash
   grep "guardrail_violation" logs/controller.log | tail -20
   ```
2. Identify violation type (no_silent_drops, scope_gating, approval_gating, citation_minimums)

## Resolution
- **no_silent_drops**: LLM returned empty answer → Prompt tuning needed
- **scope_gating**: Request in global scope proposed write tool → Fix scope detection
- **approval_gating**: LOI/CLOSING transition without approval=true → Prompt tuning
- **citation_minimums**: Financial claim without citation → Prompt tuning

## Prevention
- Add test case for specific violation pattern
- Update prompt if LLM behavior needs correction
```

**File:** `docs/runbooks/02_secret_detected.md`
**File:** `docs/runbooks/03_low_confidence.md`
**File:** `docs/runbooks/04_proposal_stuck.md`

#### Acceptance Criteria

- [ ] 4 runbooks created
- [ ] Each includes: Symptoms, Diagnosis, Resolution, Prevention
- [ ] Linked from main documentation

---

### Component 3.4: Documentation Updates

**Priority:** P2 (MEDIUM)
**Effort:** 1-2 days

#### Files to Update

1. **CHANGES.md** - Add Prompt Pack v1 entry
2. **README.md** - Update architecture diagram
3. **ARCHITECTURE.md** - Document Task Packet flow
4. **DEPLOYMENT.md** - Add RAG + optional Redis (cache) setup

#### Acceptance Criteria

- [ ] CHANGES.md has Phase 1 + Phase 2 summary
- [ ] README.md shows updated architecture
- [ ] Deployment guide includes RAG setup and optional Redis (cache) setup
- [ ] API documentation for new endpoints

---

## Success Metrics

### Phase 1 (Foundation) ✅

- [x] 100% prompt pack structure complete
- [x] 100% guardrail coverage (4 validators)
- [x] 8 regression tests passing
- [x] 0 critical security gaps

### Phase 2 (Operations) 🎯

- [ ] Evidence retrieval p95 < 3s
- [ ] RAG query p95 < 2s
- [ ] Proposal approval rate > 90%
- [ ] Session duration p50: 5 min, p95: 2 hours
- [ ] 0 critical bugs in production

### Phase 3 (Production Ready) 🎯

- [ ] Test coverage > 80%
- [ ] Load test: 1000 req/min @ p95 < 5s
- [ ] 4 operational runbooks complete
- [ ] Metrics dashboard deployed
- [ ] Documentation 100% up-to-date

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| RAG service unavailable | HIGH | Graceful fallback to case file + events only |
| Proposal/session store unavailable | HIGH | Degraded mode: read-only answers + no writes; sessions stateless |
| LLM hallucination | MEDIUM | Citation requirements + guardrails |
| Prompt injection | MEDIUM | 100+ test vectors + secret scanning |
| Context overflow | LOW | Evidence truncation + summarization |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Proposal approval latency | MEDIUM | UI notifications + mobile alerts |
| Session expiry too aggressive | LOW | 24h TTL configurable, extendable on activity |
| Secret leak in logs | HIGH | Secret scanning on all outputs |
| Guardrail bypass | HIGH | Post-generation validation (not pre-prompt) |

---

## Dependencies & Prerequisites

### Infrastructure

- **vLLM** - Local controller (Qwen 32B) on port 8000
- **RAG Service** - Semantic search on port 8052
- **Control Plane (Deal Registry + Events + State Machine)** - Durable, local-first (DataRoom-backed)
- **Proposal/Session Stores** - Durable-first (filesystem/DB); Redis optional (cache/adapter only)
- **Redis (optional)** - Cache/adapter for proposals/sessions on port 6379 (not source of truth)

### External Services

- **Gemini API** - Optional cloud worker (gemini-2.0-flash-exp)
- **LangSmith** - Optional tracing (not required)

### Configuration Files

- `.env` - Service URLs, timeouts, TTLs (no secrets committed)
- `docker-compose.yml` - Optional: Redis/RAG service containers (if you choose to run them via compose)
- `prompts/v1/` - Prompt pack (immutable)

---

## Next Actions

### Immediate (Week 1)

1. **Decide store mode (durable-first)** (1 hour)
   - Default: file-based proposal/session stores under DataRoom control plane
   - Optional: add Redis as a cache/adapter (must be rebuildable; not source of truth)

2. **(Optional) Set up Redis cache** (30 min)
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Verify RAG service** (1 hour)
   ```bash
   curl http://localhost:8052/rag/query -d '{"query": "test", "match_count": 5}'
   ```

4. **Implement RAG Client** (Component 2.2) - 2 days

5. **Implement Evidence Builder** (Component 2.1) - 3 days

### Week 2

6. **Implement Proposal Store** (Component 2.3) - 4 days

7. **Implement Session Manager** (Component 2.4) - 3 days

### Week 3

8. **Integration Testing** (Component 3.1) - 3 days

9. **Add Metrics** (Component 3.2) - 2 days

10. **Write Runbooks** (Component 3.3) - 2 days

---

## Appendix A: File Inventory

### Phase 1 (Completed) ✅

```
Zaks-llm/
├── prompts/
│   ├── README.md (19 lines)
│   └── v1/
│       ├── 00_zakops_charter.md (66 lines)
│       ├── 01_message_envelope.schema.json (148 lines)
│       ├── 10_controller_system.prompt.md (91 lines)
│       ├── 20_worker_gemini_system.prompt.md (61 lines)
│       ├── 30_role_agents/
│       │   ├── comms.prompt.md (28 lines)
│       │   ├── rag_expert.prompt.md (27 lines)
│       │   ├── deal_sourcing.prompt.md (26 lines)
│       │   ├── deal_case_manager.prompt.md (34 lines)
│       │   ├── underwriter.prompt.md (34 lines)
│       │   └── diligence_coordinator.prompt.md (29 lines)
│       └── schemas/
│           ├── classification_v1.schema.json (35 lines)
│           └── extraction_v1.schema.json (53 lines)
├── src/
│   ├── core/
│   │   ├── task_packet.py (143 lines)
│   │   ├── prompt_pack.py (88 lines)
│   │   ├── prompt_protocol.py (207 lines)
│   │   ├── secret_scan.py (46 lines)
│   │   └── gemini_worker.py (86 lines)
│   └── agents/
│       ├── controller.py (68 lines)
│       ├── comms.py (28 lines)
│       ├── rag_expert.py (34 lines)
│       ├── deal_sourcing.py (43 lines)
│       └── orchestrator.py (212 lines)
└── scripts/
    └── prompt_regression_test.py (141 lines)
```

### Phase 2 (Planned) 🔄

```
Zaks-llm/
├── src/
│   ├── core/
│   │   ├── evidence_builder.py (300 lines) ← NEW
│   │   ├── proposal_store.py (400 lines) ← NEW
│   │   ├── proposal_executor.py (200 lines) ← NEW
│   │   └── session_manager.py (350 lines) ← NEW
│   └── clients/
│       └── rag_client.py (200 lines) ← NEW
```

### Phase 3 (Planned) 🔄

```
Zaks-llm/
├── src/
│   └── core/
│       └── metrics.py (150 lines) ← NEW
├── tests/
│   ├── test_prompt_injection.py ← NEW
│   ├── integration/
│   │   ├── test_chat_front_door.py ← NEW
│   │   ├── test_evidence_builder.py ← NEW
│   │   └── test_proposal_workflow.py ← NEW
│   └── load/
│       └── locustfile.py ← NEW
├── docs/
│   └── runbooks/
│       ├── 01_guardrail_violation.md ← NEW
│       ├── 02_secret_detected.md ← NEW
│       ├── 03_low_confidence.md ← NEW
│       └── 04_proposal_stuck.md ← NEW
└── monitoring/
    └── grafana_dashboard.json ← NEW
```

---

## Appendix B: Configuration Reference

### Environment Variables

```bash
# Phase 1 (Existing)
ZAKOPS_PROMPT_PACK_VERSION=v1
# Host/WSL:
OPENAI_API_BASE=http://localhost:8000/v1
# If running inside Docker compose network, you may need:
# OPENAI_API_BASE=http://vllm-qwen:8000/v1
DEFAULT_MODEL=Qwen/Qwen2.5-32B-Instruct-AWQ
GEMINI_API_KEY=<your-key>

# Phase 2 (New)
RAG_ENDPOINT=http://localhost:8052/rag/query
RAG_SOURCE=dataroom.local
RAG_TIMEOUT=5
RAG_RETRIES=2

# Proposal/session stores (durable-first)
PROPOSAL_STORE=file
PROPOSAL_STORE_DIR=/home/zaks/DataRoom/.deal-registry/proposals
PROPOSAL_TTL_DAYS=7

SESSION_STORE=file
SESSION_STORE_DIR=/home/zaks/DataRoom/.deal-registry/sessions
SESSION_TTL_HOURS=24
SESSION_MAX_MESSAGES=20

# Optional (only if *_STORE=redis or using Redis cache):
REDIS_URL=redis://localhost:6379/0

# Phase 3 (New)
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

---

## Document Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-27 | Initial comprehensive plan (Phase 1 completed, Phase 2-3 planned) |
| 1.1 | 2025-12-27 | Aligned Phase 1 status with implemented files; revised Phase 2 to be durable-first with Redis optional; clarified `OPENAI_API_BASE` host vs Docker. |

---

**END OF IMPLEMENTATION PLAN**

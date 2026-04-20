# ZakOps AI Agent System — Ultimate Design Document

**Version:** 1.0.0
**Date:** January 2026
**Status:** APPROVED FOR IMPLEMENTATION
**Classification:** Internal Technical Architecture

---

## 1. Executive Summary

### What We Are Building

ZakOps Agent is a **production-grade, locally-hosted AI agent system** for Deal Lifecycle Management that serves as the intelligence layer for SACS AIOps 3.0. The agent orchestrates deal intake, document analysis, pipeline transitions, approval workflows, and communication drafting—all running on a single high-performance workstation with optional cloud escalation.

### Why This Architecture Is Best-in-Class

1. **Full Local Control**: Runs entirely on RTX 5090 (32GB VRAM) without mandatory internet dependency, avoiding the brittleness we experienced with LangSmith Agent Builder's MCP tool binding limitations [Project Context].

2. **Production-Grade Reliability**: LangGraph state machine with PostgreSQL checkpointing ensures zero lost work across crashes [A][B][C consensus].

3. **Competitive Performance**: Qwen3-32B achieves 61 tokens/sec on RTX 5090 [B] with tool-calling quality approaching GPT-4 class [A], at zero marginal cost per inference.

4. **Hybrid Escalation**: Complex reasoning tasks route to cloud LLMs (Claude/GPT-4) via LiteLLM gateway, maintaining quality ceiling [A][B][C consensus].

5. **Observable by Design**: OpenTelemetry + self-hosted Langfuse provides complete tracing without vendor lock-in [B][C].

### Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Primary Model** | Qwen3-32B-Instruct (Q4_K_M) | Best tool-calling at 32B tier, fits VRAM, MIT license [B] |
| **Inference Engine** | vLLM | Production-proven, OpenAI-compatible, PagedAttention [A][B][C] |
| **Orchestration** | LangGraph | State machine + checkpointing + HITL patterns [A][B][C] |
| **State Persistence** | PostgreSQL + PostgresSaver | Already in stack, ACID guarantees, no new deps [A][B] |
| **Vector Store** | pgvector (Phase 1) → Qdrant (Phase 3) | Minimize initial complexity, scale when needed [C] |
| **Observability** | OpenTelemetry + Langfuse | Local-first, MIT license, full control [B][C] |
| **Tool Gateway** | Hybrid MCP + Direct calls | MCP for portability, direct for latency-critical [B] |
| **Queue System** | PostgreSQL SKIP LOCKED | Sufficient for hundreds of deals/day, no Redis needed [B] |

---

## 2. Design Goals & Non-Goals

### Design Goals

| ID | Goal | Measurable Criteria |
|----|------|---------------------|
| G1 | **Local-first operation** | System functions fully without internet for 30+ days |
| G2 | **Sub-2-second response latency** | P95 time-to-first-token < 2s for 32K context [B] |
| G3 | **Zero lost work** | 100% state recovery after crash [A][B] |
| G4 | **High tool reliability** | ≥99% tool call success rate, <1% parameter hallucination [A][B] |
| G5 | **Full observability** | 100% trace coverage for all agent operations [B][C] |
| G6 | **Human-in-the-loop gates** | All write operations blockable pending approval [A][B][C] |
| G7 | **Cost efficiency** | ≥80% of tasks completed locally; cloud cost <$0.50/deal [B][C] |
| G8 | **Auditability** | Complete audit trail for all decisions with replay capability [B][C] |

### Non-Goals

| ID | Non-Goal | Rationale |
|----|----------|-----------|
| NG1 | Multi-tenant SaaS deployment | Single-operator system; multi-tenancy adds complexity |
| NG2 | Real-time collaborative editing | Deals are single-owner; not a document editor |
| NG3 | Sub-100ms latency | Agent reasoning requires seconds; not a CRUD API |
| NG4 | 70B+ model without CPU offload | RTX 5090 caps at ~40GB quantized 70B; kills latency [A] |
| NG5 | Training/fine-tuning in-loop | Inference-only system; training is offline process |
| NG6 | LangSmith Agent Builder hosting | Platform limitations proven [Project Context]; tracing only |

---

## 3. System Requirements

### 3.1 Functional Requirements

#### FR1: Deal Triage
- System SHALL classify incoming deals by type, priority, and confidence
- System SHALL route low-confidence items to quarantine with explanation
- System SHALL emit `deal.triaged` event with classification metadata

#### FR2: Document Analysis
- System SHALL extract structured data from deal documents (PDFs, emails)
- System SHALL identify key entities (parties, dates, amounts, terms)
- System SHALL store extracted data in deal metadata with source provenance

#### FR3: Pipeline Transitions
- System SHALL validate stage transitions against allowed state machine
- System SHALL require approval for critical transitions (e.g., to Won/Lost)
- System SHALL emit events for all transitions with actor and reason

#### FR4: Action Planning
- System SHALL decompose complex requests into executable steps
- System SHALL estimate risk level for each action
- System SHALL queue actions requiring human approval before execution

#### FR5: Communication Drafting
- System SHALL generate contextual responses using deal history
- System SHALL support templates with variable substitution
- System SHALL flag drafts for human review before sending

#### FR6: Quarantine Management
- System SHALL list, approve, reject, and re-classify quarantined items
- System SHALL track quarantine reasons and resolution history
- System SHALL escalate items exceeding configurable age threshold

### 3.2 Non-Functional Requirements

| Category | Requirement | Target | Validation Method |
|----------|-------------|--------|-------------------|
| **Latency** | Time-to-first-token | P50 <1s, P95 <2s | Load test with 32K context |
| **Latency** | Tool call round-trip | P95 <200ms | APM tracing |
| **Throughput** | Token generation | ≥50 tok/s sustained [B] | vLLM benchmark |
| **Reliability** | Workflow completion | ≥99% success | End-to-end tracking |
| **Reliability** | Crash recovery | 100% state recovery | Chaos testing |
| **Privacy** | Data residency | All PII local-only | Audit; no cloud logging |
| **Cost** | Cloud LLM spend | <$0.50/deal average | Cost tracking dashboard |
| **Scale** | Concurrent deals | 100 active threads | Load test |
| **Context** | Window size | 32K tokens minimum | Needle-in-haystack test |
| **Availability** | Uptime | 99.9% during business hours | Health check monitoring |

---

## 4. Architecture Overview

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ZAKOPS AI AGENT SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                    │
│  │   Next.js    │   │   FastAPI    │   │  Cloudflare  │                    │
│  │  Dashboard   │   │   Backend    │   │   Tunnel     │                    │
│  │   :3003      │   │   :8090      │   │  (optional)  │                    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                    │
│         │                  │                  │                             │
│         └──────────────────┼──────────────────┘                             │
│                            │                                                 │
│                            ▼                                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     AGENT ORCHESTRATOR (LangGraph)                     │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │ │
│  │  │ Router  │─▶│ Planner │─▶│Executor │─▶│Verifier │─▶│ Output  │    │ │
│  │  │  Node   │  │  Node   │  │  Node   │  │  Node   │  │  Node   │    │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │ │
│  │       │            │            │            │            │          │ │
│  │       └────────────┴────────────┴────────────┴────────────┘          │ │
│  │                                 │                                     │ │
│  │                                 ▼                                     │ │
│  │                    ┌─────────────────────┐                           │ │
│  │                    │   State Manager     │                           │ │
│  │                    │  (PostgresSaver)    │                           │ │
│  │                    └─────────────────────┘                           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                            │                                                 │
│         ┌──────────────────┼──────────────────┐                             │
│         │                  │                  │                             │
│         ▼                  ▼                  ▼                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                      │
│  │ LLM Gateway │   │Tool Gateway │   │Memory Layer │                      │
│  │  (LiteLLM)  │   │(Validation) │   │ (Retrieval) │                      │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                      │
│         │                 │                 │                              │
│    ┌────┴────┐      ┌─────┴─────┐     ┌─────┴─────┐                       │
│    │         │      │           │     │           │                       │
│    ▼         ▼      ▼           ▼     ▼           ▼                       │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                    │
│ │vLLM  │ │Cloud │ │Direct│ │ MCP  │ │Postgres│ │ RAG  │                    │
│ │:8000 │ │ LLMs │ │Tools │ │:9100 │ │pgvector│ │:8052 │                    │
│ │      │ │      │ │      │ │      │ │:5432  │ │      │                    │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘                    │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     OBSERVABILITY LAYER                                │ │
│  │   OpenTelemetry Collector  ──▶  Langfuse  ──▶  Dashboards/Alerts     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. REQUEST INGESTION                                                     │
│     ┌─────────┐      ┌─────────┐      ┌─────────┐                       │
│     │ User/   │─────▶│ FastAPI │─────▶│ Agent   │                       │
│     │ System  │      │ :8090   │      │ Thread  │                       │
│     └─────────┘      └─────────┘      └─────────┘                       │
│                                             │                            │
│  2. ORCHESTRATION                           ▼                            │
│     ┌─────────────────────────────────────────────────────┐             │
│     │                  LangGraph State                     │             │
│     │  {                                                   │             │
│     │    thread_id: "deal-DL-0001",                       │             │
│     │    messages: [...],                                  │             │
│     │    deal_context: {...},                              │             │
│     │    plan: [...],                                      │             │
│     │    current_step: 0,                                  │             │
│     │    pending_approval: null                            │             │
│     │  }                                                   │             │
│     └─────────────────────────────────────────────────────┘             │
│                            │                                             │
│  3. NODE EXECUTION         ▼                                             │
│     ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                     │
│     │ Route  │─▶│ Plan   │─▶│Execute │─▶│Verify  │──▶ (loop or end)   │
│     └────────┘  └────────┘  └────────┘  └────────┘                     │
│         │           │           │           │                           │
│         ▼           ▼           ▼           ▼                           │
│     [Checkpoint] [Checkpoint] [Checkpoint] [Checkpoint]                 │
│                                                                          │
│  4. TOOL EXECUTION                                                       │
│     ┌──────────────────────────────────────────────────────┐            │
│     │  Tool Call: transition_deal(deal_id, stage)          │            │
│     │                      │                                │            │
│     │           ┌──────────┼──────────┐                    │            │
│     │           ▼          ▼          ▼                    │            │
│     │     [Validate]  [Authorize] [Execute]                │            │
│     │           │          │          │                    │            │
│     │           └──────────┼──────────┘                    │            │
│     │                      ▼                                │            │
│     │              [Emit Event + Log]                       │            │
│     └──────────────────────────────────────────────────────┘            │
│                                                                          │
│  5. PERSISTENCE & EVENTS                                                 │
│     ┌────────────────────────────────────────────────────────┐          │
│     │                    PostgreSQL                          │          │
│     │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │          │
│     │  │ deals    │  │ events   │  │checkpts  │            │          │
│     │  │          │  │          │  │          │            │          │
│     │  └──────────┘  └──────────┘  └──────────┘            │          │
│     └────────────────────────────────────────────────────────┘          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Key Abstractions & Interfaces

```python
# Core State Interface [B adapted]
class AgentState(TypedDict):
    thread_id: str
    messages: list[BaseMessage]
    deal_id: Optional[str]
    deal_context: Optional[DealContext]
    plan: Optional[list[PlanStep]]
    current_step: int
    pending_approval: Optional[ApprovalRequest]
    error: Optional[ErrorInfo]

# Tool Interface [B]
class ToolPermission(Enum):
    READ = "read"        # No approval needed
    WRITE = "write"      # May need approval
    CRITICAL = "critical" # Always needs approval

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict  # JSON Schema
    permission: ToolPermission
    idempotency_required: bool
    timeout_ms: int

# Event Interface [B adapted]
class AgentEvent(BaseModel):
    event_id: str
    event_type: str
    thread_id: str
    deal_id: Optional[str]
    actor_type: Literal["user", "agent", "system"]
    actor_id: str
    payload: dict
    trace_id: str
    timestamp: datetime
```

---

## 5. Component-by-Component Design

### 5.1 LLM Inference Layer

#### Purpose
Serve local language model inference with OpenAI-compatible API, with fallback routing to cloud providers.

#### Responsibilities
- Load and serve Qwen3-32B-Instruct model
- Handle concurrent inference requests with batching
- Provide function/tool calling capability
- Route complex requests to cloud when confidence is low

#### Inputs/Outputs

```
INPUT:  ChatCompletionRequest {messages, tools?, temperature, max_tokens}
OUTPUT: ChatCompletionResponse {choices, usage, tool_calls?}
```

#### Internal Design

**Primary Model Configuration** [B]:
```bash
vllm serve Qwen/Qwen3-32B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 32000 \
  --gpu-memory-utilization 0.90 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --tensor-parallel-size 1
```

**Router Model (Optional)** [A][C]:
- Qwen3-8B as fast classifier for routing decisions
- Runs alongside main model if VRAM permits (~5GB additional)

**LiteLLM Gateway Configuration** [C]:
```python
# config.yaml
model_list:
  - model_name: local-primary
    litellm_params:
      model: openai/Qwen3-32B-Instruct
      api_base: http://localhost:8000/v1

  - model_name: cloud-claude
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: ${ANTHROPIC_API_KEY}

router_settings:
  routing_strategy: simple-shuffle
  fallbacks:
    - local-primary
    - cloud-claude

  # Cost controls
  set_budget:
    max_budget: 50.0  # USD per day
```

#### Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Qwen3-32B over Qwen2.5-32B | Qwen3 matches Qwen2.5-72B quality at half params [B]; better tool calling |
| AWQ over GPTQ | Better vLLM support, minimal quality loss [general knowledge] |
| 32K context over 128K | 32K sufficient for deal workflows; saves VRAM for KV cache |
| LiteLLM over direct SDK | Unified interface, built-in fallbacks, cost tracking [C] |

#### Failure Modes & Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| OOM | vLLM error logs | Reduce max-model-len; fall back to cloud |
| Timeout (>30s) | Request timeout | Retry once, then escalate to cloud |
| Hallucinated tool params | Validation layer rejects | Retry with stricter prompt |
| Model corruption | Health check fails | Reload model; alert operator |

#### Observability

- **Metrics**: tokens/sec, TTFT_p50/p95, requests/sec, error_rate, cache_hit_rate
- **Logs**: Request/response hashes, latency, tool calls, routing decisions
- **Traces**: Span per inference call with model version and prompt hash

#### Security

- vLLM listens on localhost only (not exposed to network)
- API key required for LiteLLM proxy
- No PII in cloud-routed requests (redaction layer)

---

### 5.2 Agent Orchestrator (LangGraph)

#### Purpose
Coordinate multi-step agent workflows as a state machine with persistence, human-in-the-loop gates, and crash recovery.

#### Responsibilities
- Route incoming requests to appropriate workflow type
- Execute plan-and-execute patterns for complex tasks
- Persist state after every node transition
- Block execution pending human approval when required
- Enable workflow replay and debugging

#### Inputs/Outputs

```
INPUT:  AgentRequest {thread_id?, deal_id?, message, context?}
OUTPUT: AgentResponse {thread_id, messages, actions_taken, pending_approval?}
```

#### Internal Design

**State Graph Definition** [A][B combined]:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

class DealAgentState(TypedDict):
    thread_id: str
    messages: Annotated[list, add_messages]
    deal_id: Optional[str]
    deal_context: Optional[dict]
    plan: Optional[list[dict]]
    current_step: int
    pending_approval: Optional[dict]
    iteration_count: int  # Safety limit

def create_deal_agent(db_url: str) -> CompiledGraph:
    graph = StateGraph(DealAgentState)

    # Nodes
    graph.add_node("router", router_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("approval_gate", approval_gate_node)
    graph.add_node("output", output_node)

    # Edges
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_decision, {
        "simple": "executor",      # Direct tool call
        "complex": "planner",      # Multi-step planning
        "clarify": "output",       # Need user input
    })
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges("executor", post_execute, {
        "needs_approval": "approval_gate",
        "continue": "verifier",
        "error": "output",
    })
    graph.add_conditional_edges("approval_gate", check_approval, {
        "approved": "verifier",
        "rejected": "output",
        "pending": END,  # Pause workflow
    })
    graph.add_conditional_edges("verifier", verify_result, {
        "success": "output",
        "retry": "executor",
        "escalate": "output",
    })
    graph.add_edge("output", END)

    # Persistence
    checkpointer = PostgresSaver.from_conn_string(db_url)

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["approval_gate"],  # HITL breakpoint
    )
```

**Node Implementations**:

```python
async def router_node(state: DealAgentState) -> dict:
    """Classify request and route to appropriate path."""
    # Safety check
    if state["iteration_count"] > MAX_ITERATIONS:
        return {"error": "Max iterations exceeded"}

    last_message = state["messages"][-1].content

    # Simple heuristic routing (upgrade to LLM classifier later)
    if any(kw in last_message.lower() for kw in ["list", "show", "get"]):
        return {"route": "simple"}
    elif any(kw in last_message.lower() for kw in ["analyze", "plan", "draft"]):
        return {"route": "complex"}
    else:
        # Use LLM to classify
        classification = await classify_request(last_message)
        return {"route": classification}

async def planner_node(state: DealAgentState) -> dict:
    """Generate multi-step plan for complex tasks."""
    context = await build_context(state["deal_id"])

    plan_prompt = PLAN_TEMPLATE.format(
        task=state["messages"][-1].content,
        context=context,
        available_tools=TOOL_DESCRIPTIONS,
    )

    plan = await llm_gateway.complete(
        messages=[{"role": "user", "content": plan_prompt}],
        response_format=PlanSchema,  # Structured output
    )

    return {
        "plan": plan.steps,
        "current_step": 0,
        "deal_context": context,
    }

async def executor_node(state: DealAgentState) -> dict:
    """Execute current plan step or direct tool call."""
    if state["plan"]:
        step = state["plan"][state["current_step"]]
        tool_name = step["tool"]
        tool_args = step["arguments"]
    else:
        # Direct tool call from LLM
        tool_call = await llm_gateway.complete(
            messages=state["messages"],
            tools=TOOL_DEFINITIONS,
        )
        tool_name = tool_call.tool_name
        tool_args = tool_call.arguments

    # Check approval requirement
    tool_def = TOOL_REGISTRY[tool_name]
    if tool_def.permission == ToolPermission.CRITICAL:
        return {
            "pending_approval": {
                "tool": tool_name,
                "args": tool_args,
                "reason": f"Critical action: {tool_name}",
            }
        }

    # Execute tool
    result = await tool_gateway.execute(tool_name, tool_args)

    return {
        "messages": [AIMessage(content=f"Executed {tool_name}: {result}")],
        "current_step": state["current_step"] + 1,
        "iteration_count": state["iteration_count"] + 1,
    }
```

#### Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Plan-and-Execute over pure ReAct | Better for multi-step deal workflows; planner uses stronger model [B] |
| PostgresSaver over MemorySaver | Production durability; already have Postgres [A][B] |
| interrupt_before for HITL | Native LangGraph pattern; clean pause/resume [B] |
| Max iteration limit | Prevents infinite loops; configurable per workflow type |

#### Failure Modes & Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Infinite loop | iteration_count > MAX | Force exit with error message |
| Checkpoint write fails | Exception on save | Retry 3x with backoff; alert if persistent |
| State corruption | Schema validation fails | Restore from previous checkpoint |
| Approval timeout | Configurable TTL | Auto-reject or escalate after threshold |

#### Observability

- **Metrics**: workflow_duration, steps_per_workflow, approval_wait_time, error_rate_by_node
- **Logs**: State transitions, node entry/exit, tool calls, approval decisions
- **Traces**: Span per node with state snapshot hash

---

### 5.3 Tool Gateway

#### Purpose
Provide a unified, validated, permission-checked interface for all tool executions with idempotency support.

#### Responsibilities
- Validate tool call parameters against schemas
- Enforce permission checks (read/write/critical)
- Inject idempotency keys for write operations
- Route to MCP server or direct implementations
- Log all tool executions for audit

#### Inputs/Outputs

```
INPUT:  ToolRequest {name, arguments, idempotency_key?, actor_id, trace_id}
OUTPUT: ToolResponse {success, result?, error?, execution_time_ms}
```

#### Internal Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        TOOL GATEWAY                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                    VALIDATION LAYER                         ││
│  │  - JSON Schema validation (Pydantic)                       ││
│  │  - Parameter range checks                                   ││
│  │  - Required field enforcement                               ││
│  └────────────────────────────────────────────────────────────┘│
│                            │                                    │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                   PERMISSION LAYER                          ││
│  │  - Actor authorization check                                ││
│  │  - Permission level verification                            ││
│  │  - Rate limiting                                            ││
│  └────────────────────────────────────────────────────────────┘│
│                            │                                    │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                  IDEMPOTENCY LAYER                          ││
│  │  - Generate/validate idempotency key                        ││
│  │  - Check for duplicate execution                            ││
│  │  - Return cached result if duplicate                        ││
│  └────────────────────────────────────────────────────────────┘│
│                            │                                    │
│               ┌────────────┴────────────┐                      │
│               ▼                         ▼                      │
│  ┌─────────────────────┐   ┌─────────────────────┐            │
│  │    DIRECT TOOLS     │   │    MCP SERVER       │            │
│  │  (Low latency)      │   │  (Portable)         │            │
│  │                     │   │                     │            │
│  │  - list_deals       │   │  - External APIs    │            │
│  │  - get_deal         │   │  - Third-party      │            │
│  │  - check_health     │   │  - Future tools     │            │
│  └─────────────────────┘   └─────────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Tool Registry** [B adapted]:

```python
TOOL_REGISTRY = {
    "list_deals": ToolDefinition(
        name="list_deals",
        description="List deals with optional stage filter",
        parameters={
            "type": "object",
            "properties": {
                "stage": {"type": "string", "enum": DEAL_STAGES},
                "limit": {"type": "integer", "default": 20, "maximum": 100},
            },
        },
        permission=ToolPermission.READ,
        idempotency_required=False,
        timeout_ms=5000,
    ),
    "transition_deal": ToolDefinition(
        name="transition_deal",
        description="Move deal to a new pipeline stage",
        parameters={
            "type": "object",
            "properties": {
                "deal_id": {"type": "string", "pattern": "^DL-\\d{4}$"},
                "new_stage": {"type": "string", "enum": DEAL_STAGES},
                "reason": {"type": "string"},
            },
            "required": ["deal_id", "new_stage"],
        },
        permission=ToolPermission.WRITE,
        idempotency_required=True,
        timeout_ms=10000,
    ),
    "approve_action": ToolDefinition(
        name="approve_action",
        description="Approve a pending action for execution",
        parameters={
            "type": "object",
            "properties": {
                "action_id": {"type": "string"},
            },
            "required": ["action_id"],
        },
        permission=ToolPermission.CRITICAL,
        idempotency_required=True,
        timeout_ms=15000,
    ),
}
```

**Idempotency Implementation** [B]:

```python
async def execute_with_idempotency(
    tool_name: str,
    args: dict,
    idempotency_key: str,
) -> ToolResponse:
    # Check for existing result
    existing = await db.fetchone(
        "SELECT result, error FROM tool_executions WHERE idempotency_key = $1",
        idempotency_key,
    )
    if existing:
        return ToolResponse(
            success=existing["error"] is None,
            result=existing["result"],
            error=existing["error"],
            cached=True,
        )

    # Execute tool
    try:
        result = await TOOL_IMPLEMENTATIONS[tool_name](**args)
        await db.execute(
            """INSERT INTO tool_executions (idempotency_key, tool_name, args, result)
               VALUES ($1, $2, $3, $4)""",
            idempotency_key, tool_name, json.dumps(args), json.dumps(result),
        )
        return ToolResponse(success=True, result=result)
    except Exception as e:
        await db.execute(
            """INSERT INTO tool_executions (idempotency_key, tool_name, args, error)
               VALUES ($1, $2, $3, $4)""",
            idempotency_key, tool_name, json.dumps(args), str(e),
        )
        return ToolResponse(success=False, error=str(e))
```

#### Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Hybrid MCP + Direct | MCP for future portability; direct for latency-critical [B] |
| Pydantic validation | Type-safe, auto-generates JSON Schema, clear error messages |
| Idempotency keys mandatory for writes | Safe retries; exactly-once semantics [B][C] |
| 3-tier permission model | Clear separation: read (free), write (logged), critical (approved) |

#### Failure Modes & Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Validation failure | Schema error | Return clear error; do not execute |
| MCP server down | Connection timeout | Fall back to direct implementation if available |
| Rate limit exceeded | Counter check | Queue request; retry after backoff |
| Timeout | Execution exceeds timeout_ms | Cancel; return error; log for investigation |

#### Observability

- **Metrics**: tool_call_count (by tool), tool_latency_p95, validation_failure_rate, cache_hit_rate
- **Logs**: Every tool call with args (redacted for sensitive fields), result summary, actor
- **Traces**: Span per tool call linked to parent agent trace

---

### 5.4 Memory & Retrieval Layer

#### Purpose
Provide contextual memory for agent reasoning through vector search, deal history, and document retrieval.

#### Responsibilities
- Store and retrieve deal document embeddings
- Provide semantic search over deal corpus
- Maintain conversation context within threads
- Support cross-deal knowledge queries

#### Inputs/Outputs

```
INPUT:  RetrievalRequest {query, deal_id?, k=5, filters?}
OUTPUT: RetrievalResponse {documents[], scores[], sources[]}
```

#### Internal Design

**Phase 1: pgvector (Immediate)** [A][C]:

```sql
-- Extension and table setup
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE deal_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id TEXT NOT NULL REFERENCES deals(deal_id),
    chunk_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1024),  -- BGE-M3 dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(deal_id, chunk_id)
);

CREATE INDEX ON deal_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX ON deal_embeddings (deal_id);
```

**Phase 3: Qdrant (Scale)** [B][C]:

```python
# Migration path when pgvector hits limits
from qdrant_client import QdrantClient

qdrant = QdrantClient(host="localhost", port=6333)

qdrant.create_collection(
    collection_name="deal_documents",
    vectors_config=VectorParams(
        size=1024,  # BGE-M3
        distance=Distance.COSINE,
    ),
    # Qdrant's killer feature: payload filtering
    payload_schema={
        "deal_id": PayloadSchemaType.KEYWORD,
        "doc_type": PayloadSchemaType.KEYWORD,
        "created_at": PayloadSchemaType.DATETIME,
    },
)
```

**Embedding Model** [B][C]:

```python
# BGE-M3: 72% retrieval accuracy, 8K context, multilingual
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("BAAI/bge-m3")

def embed_document(text: str) -> list[float]:
    # BGE-M3 instruction prefix for retrieval
    return embedder.encode(
        f"Represent this document for retrieval: {text}",
        normalize_embeddings=True,
    ).tolist()

def embed_query(query: str) -> list[float]:
    return embedder.encode(
        f"Represent this query for retrieval: {query}",
        normalize_embeddings=True,
    ).tolist()
```

**Retrieval with Reranking** [C]:

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-large")

async def retrieve_with_rerank(
    query: str,
    deal_id: Optional[str] = None,
    k: int = 5,
    rerank_k: int = 20,
) -> list[Document]:
    # Stage 1: Dense retrieval
    query_embedding = embed_query(query)

    candidates = await db.fetch(
        """
        SELECT chunk_id, content, metadata,
               1 - (embedding <=> $1::vector) as score
        FROM deal_embeddings
        WHERE ($2::text IS NULL OR deal_id = $2)
        ORDER BY embedding <=> $1::vector
        LIMIT $3
        """,
        query_embedding, deal_id, rerank_k,
    )

    # Stage 2: Cross-encoder reranking
    pairs = [(query, doc["content"]) for doc in candidates]
    rerank_scores = reranker.predict(pairs)

    # Combine and sort
    for doc, score in zip(candidates, rerank_scores):
        doc["rerank_score"] = float(score)

    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
    return candidates[:k]
```

#### Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| pgvector Phase 1, Qdrant Phase 3 | Minimize initial deps; migrate when retrieval demands it [C] |
| BGE-M3 embeddings | 72% accuracy, 8K context, MIT license [B] |
| Reranking with bge-reranker | Significant quality uplift for top-k [C] |
| Deal-scoped filtering | Security: no cross-deal leakage by default |

#### Failure Modes & Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Embedding service down | Health check fails | Degrade to keyword search; alert |
| Index corruption | Query returns garbage | Rebuild index from source docs |
| Slow retrieval (>250ms) | Latency monitoring | Increase IVFFlat lists; consider Qdrant |
| Cross-deal leakage | Security audit | Enforce deal_id filter at query layer |

#### Observability

- **Metrics**: retrieval_latency_p95, recall_at_k (offline eval), reranker_uplift
- **Logs**: Query text (hashed), filters applied, result count
- **Traces**: Span for embed + search + rerank stages

---

### 5.5 State & Persistence Layer

#### Purpose
Provide durable storage for deal data, agent state, events, and tool execution history.

#### Responsibilities
- Store deal lifecycle data with full history
- Persist LangGraph checkpoints for crash recovery
- Record all events for audit and replay
- Queue tasks for async processing

#### Internal Design

**Schema Overview**:

```sql
-- Core deal tables (existing at :8090)
-- deals, deal_events, actions, quarantine_items

-- Agent checkpoints (LangGraph)
CREATE TABLE checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_id TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

CREATE INDEX ON checkpoints (thread_id, created_at DESC);

-- Tool execution log (idempotency + audit)
CREATE TABLE tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key TEXT UNIQUE,
    tool_name TEXT NOT NULL,
    args JSONB NOT NULL,
    result JSONB,
    error TEXT,
    actor_id TEXT NOT NULL,
    trace_id TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON tool_executions (tool_name, executed_at DESC);
CREATE INDEX ON tool_executions (actor_id);

-- Task queue (Postgres-based) [B]
CREATE TABLE task_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'dead_letter')),
    idempotency_key TEXT UNIQUE,
    priority INT DEFAULT 0,
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT,
    next_retry_at TIMESTAMPTZ
);

CREATE INDEX ON task_queue (status, priority DESC, created_at ASC)
    WHERE status = 'pending';
CREATE INDEX ON task_queue (next_retry_at)
    WHERE status = 'pending' AND next_retry_at IS NOT NULL;

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    actor_type TEXT NOT NULL CHECK (actor_type IN ('user', 'agent', 'system')),
    actor_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'failure', 'denied')),
    details JSONB DEFAULT '{}',
    trace_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON audit_log (resource_type, resource_id, created_at DESC);
CREATE INDEX ON audit_log (actor_id, created_at DESC);
CREATE INDEX ON audit_log (trace_id);
```

**Task Queue Worker** [B]:

```python
async def claim_task() -> Optional[Task]:
    """Claim next pending task using SKIP LOCKED."""
    return await db.fetchone(
        """
        UPDATE task_queue
        SET status = 'running', started_at = NOW(), attempts = attempts + 1
        WHERE id = (
            SELECT id FROM task_queue
            WHERE status = 'pending'
              AND (next_retry_at IS NULL OR next_retry_at <= NOW())
            ORDER BY priority DESC, created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING *
        """
    )

async def complete_task(task_id: str, result: dict):
    await db.execute(
        """
        UPDATE task_queue
        SET status = 'completed', completed_at = NOW(), payload = payload || $2
        WHERE id = $1
        """,
        task_id, json.dumps({"result": result}),
    )

async def fail_task(task_id: str, error: str, max_attempts: int):
    task = await db.fetchone("SELECT attempts FROM task_queue WHERE id = $1", task_id)

    if task["attempts"] >= max_attempts:
        new_status = "dead_letter"
        next_retry = None
    else:
        new_status = "pending"
        # Exponential backoff: 30s, 60s, 120s, ...
        next_retry = datetime.utcnow() + timedelta(seconds=30 * (2 ** task["attempts"]))

    await db.execute(
        """
        UPDATE task_queue
        SET status = $2, error = $3, next_retry_at = $4
        WHERE id = $1
        """,
        task_id, new_status, error, next_retry,
    )
```

#### Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| PostgreSQL for queue | Sufficient for scale; no Redis needed; transactional with business data [B] |
| SKIP LOCKED for claiming | Standard pattern; no external coordinator needed |
| Exponential backoff | Industry standard for transient failures |
| Dead letter queue | Manual investigation for persistent failures |

---

### 5.6 Observability Layer

#### Purpose
Provide complete visibility into agent operations for debugging, monitoring, and compliance.

#### Responsibilities
- Collect traces for all agent operations
- Aggregate metrics for dashboards and alerting
- Store structured logs for debugging
- Enable trace replay for failed workflows

#### Internal Design

**Stack Selection** [B][C]:
- **Tracing**: OpenTelemetry SDK → Langfuse
- **Metrics**: OpenTelemetry → Prometheus
- **Logs**: Structured JSON → Loki (or file for Phase 1)

**Langfuse Integration**:

```python
from langfuse import Langfuse
from langfuse.decorators import observe

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host="http://localhost:3001",  # Self-hosted
)

@observe(name="agent_workflow")
async def run_agent_workflow(request: AgentRequest) -> AgentResponse:
    trace = langfuse.trace(
        name="deal_agent",
        user_id=request.actor_id,
        session_id=request.thread_id,
        metadata={"deal_id": request.deal_id},
    )

    try:
        # ... workflow execution ...
        span = trace.span(name="llm_inference")
        response = await llm_gateway.complete(...)
        span.end(output=response.content[:500])  # Truncate for storage

        trace.update(status="success")
        return response
    except Exception as e:
        trace.update(status="error", metadata={"error": str(e)})
        raise
```

**Metric Definitions**:

```python
from opentelemetry import metrics

meter = metrics.get_meter("zakops_agent")

# Counters
workflow_count = meter.create_counter(
    "agent.workflow.count",
    description="Total workflows started",
)
tool_call_count = meter.create_counter(
    "agent.tool.call.count",
    description="Tool calls by tool name",
)

# Histograms
workflow_duration = meter.create_histogram(
    "agent.workflow.duration_ms",
    description="Workflow duration in milliseconds",
)
llm_latency = meter.create_histogram(
    "agent.llm.latency_ms",
    description="LLM inference latency",
)

# Gauges
active_workflows = meter.create_up_down_counter(
    "agent.workflow.active",
    description="Currently active workflows",
)
```

**Langfuse Deployment** [B]:

```yaml
# docker-compose.langfuse.yml
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3001:3000"
    environment:
      - DATABASE_URL=postgresql://langfuse:langfuse@postgres:5432/langfuse
      - NEXTAUTH_SECRET=${LANGFUSE_SECRET}
      - NEXTAUTH_URL=http://localhost:3001
      - SALT=${LANGFUSE_SALT}
    depends_on:
      - postgres
```

#### Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Langfuse over LangSmith | Self-hosted, MIT license, full control [B]; LangSmith for tracing only if needed |
| OpenTelemetry | Vendor-agnostic, wide ecosystem, standard [C] |
| Prometheus for metrics | Already ubiquitous; Grafana dashboards |

---

### 5.7 Security Layer

#### Purpose
Protect agent operations through authentication, authorization, and audit logging.

#### Responsibilities
- Authenticate API requests
- Authorize actions based on actor and permission level
- Encrypt sensitive data at rest and in transit
- Maintain complete audit trail

#### Internal Design

**RBAC Model** [B]:

```python
class Role(Enum):
    VIEWER = "viewer"       # Read-only access
    OPERATOR = "operator"   # Can trigger non-critical actions
    APPROVER = "approver"   # Can approve critical actions
    ADMIN = "admin"         # Full access

ROLE_PERMISSIONS = {
    Role.VIEWER: {"read"},
    Role.OPERATOR: {"read", "write"},
    Role.APPROVER: {"read", "write", "approve"},
    Role.ADMIN: {"read", "write", "approve", "admin"},
}

async def check_permission(
    actor: Actor,
    action: str,
    resource: Resource,
) -> bool:
    role = await get_actor_role(actor.id)
    required_permission = get_required_permission(action, resource)
    return required_permission in ROLE_PERMISSIONS[role]
```

**API Authentication**:

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Actor:
    token = credentials.credentials

    # Verify JWT or API key
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return Actor(
            id=payload["sub"],
            role=Role(payload["role"]),
        )
    except jwt.InvalidTokenError:
        # Check API key fallback
        api_key = await db.fetchone(
            "SELECT actor_id, role FROM api_keys WHERE key_hash = $1 AND revoked_at IS NULL",
            hash_key(token),
        )
        if api_key:
            return Actor(id=api_key["actor_id"], role=Role(api_key["role"]))

        raise HTTPException(status_code=401, detail="Invalid credentials")
```

**Secrets Management** [C]:

```python
# Phase 1: Environment variables (acceptable for single-operator)
# Phase 3: HashiCorp Vault integration

import os

class SecretManager:
    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> str:
        if key not in self._cache:
            # Phase 1: Environment
            value = os.getenv(key)
            if not value:
                raise ValueError(f"Secret {key} not found")
            self._cache[key] = value
        return self._cache[key]

    # Phase 3: Vault integration
    # async def get_from_vault(self, path: str) -> str:
    #     async with self.vault_client.read(path) as secret:
    #         return secret["data"]["value"]
```

**Cloudflare Access (External Exposure)** [C]:

```
# Cloudflare tunnel config
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: zakops-agent.zaksops.com
    service: http://localhost:8090
    originRequest:
      access:
        required: true
        teamName: zaksops
        # Require Cloudflare Access authentication
  - service: http_status:404
```

---

## 6. Research Plan & Technical Evaluation

### 6.1 Implementable Now vs. Needs Research

| Component | Status | Notes |
|-----------|--------|-------|
| vLLM + Qwen3-32B | **Ready** | Well-documented; benchmarks available [B] |
| LangGraph + PostgresSaver | **Ready** | Production-proven [A][B][C] |
| pgvector | **Ready** | Already in stack |
| Direct tools (Deal API) | **Ready** | Existing infrastructure |
| Langfuse | **Ready** | Simple Docker deployment |
| BGE-M3 embeddings | **Ready** | HuggingFace model |
| LiteLLM gateway | **Ready** | pip install |
| MCP integration | **Needs Testing** | Verify streamable-http works with LangGraph |
| Qwen3 tool calling | **Needs Testing** | Validate Hermes parser accuracy |
| Reranker quality uplift | **Needs Research** | Measure actual improvement on deal docs |
| Qdrant migration | **Phase 3** | Only if pgvector limits hit |
| Hybrid cloud routing | **Needs Research** | Define routing rules; measure cost/quality |

### 6.2 Candidate Approaches & Decision Criteria

**Model Selection Evaluation** (to verify [B] claims):

```
Test Matrix:
┌────────────────────┬─────────────┬─────────────┬─────────────┐
│ Model              │ Tool Acc.   │ Latency     │ VRAM        │
├────────────────────┼─────────────┼─────────────┼─────────────┤
│ Qwen3-32B-AWQ      │ TBD         │ TBD         │ ~20GB       │
│ Qwen2.5-32B-AWQ    │ TBD         │ TBD         │ ~18GB       │
│ Llama-3.3-70B-Q4   │ TBD         │ TBD         │ ~40GB (OOM?)│
│ DeepSeek-V3-Lite   │ TBD         │ TBD         │ TBD         │
└────────────────────┴─────────────┴─────────────┴─────────────┘

Evaluation Dataset:
- 50 tool-calling prompts derived from deal workflows
- Ground truth annotations for expected tool + parameters
- Measure: exact match, partial match, hallucination rate
```

**Retrieval Quality Evaluation**:

```
Test Methodology:
1. Build eval set: 100 query-document pairs from real deals
2. Measure recall@5, recall@10, MRR
3. Compare: pgvector-only vs pgvector+reranker vs Qdrant+reranker

Acceptance Criteria:
- recall@5 ≥ 0.8
- Reranker must improve MRR by ≥10% to justify latency cost
```

### 6.3 Metrics & Benchmarks

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Tool call accuracy | ≥95% | Eval set with 50 prompts |
| Tool hallucination rate | <1% | Validation rejection logs |
| TTFT (32K context) | P95 <2s | Load test |
| Token throughput | ≥50 tok/s | vLLM benchmark |
| Retrieval recall@5 | ≥80% | Offline eval set |
| Workflow completion | ≥99% | Production tracking |
| Crash recovery | 100% | Chaos testing |
| Cloud cost per deal | <$0.50 | Cost tracking |

### 6.4 Acceptance Thresholds / Definition of Done

**Phase 1 (MVP) Done When:**
- [ ] vLLM serves Qwen3-32B at ≥50 tok/s
- [ ] LangGraph workflow completes simple deal query end-to-end
- [ ] State persists across process restart
- [ ] Tool calls validated and logged
- [ ] Langfuse shows complete trace

**Phase 2 (Hardening) Done When:**
- [ ] Tool accuracy ≥95% on eval set
- [ ] HITL approval workflow functions
- [ ] Queue processes tasks with retry
- [ ] Health checks pass continuously for 24h
- [ ] Crash recovery verified via chaos test

---

## 7. Implementation Roadmap

### Phase 1: Minimum Viable Agent (Weeks 1-4)

**Goal**: Working agent that can list deals, check health, and answer questions.

**Deliverables**:
- [ ] vLLM container with Qwen3-32B serving on :8000
- [ ] LiteLLM proxy with fallback configuration
- [ ] LangGraph agent with router → executor → output flow
- [ ] PostgresSaver checkpointing
- [ ] Direct tool implementations (list_deals, get_deal, check_health)
- [ ] Langfuse tracing integration
- [ ] CLI for testing: `zakops-agent query "List deals in proposal stage"`

**Success Criteria**:
- Agent answers simple queries correctly
- State persists across restart
- Traces visible in Langfuse

### Phase 2: Production Hardening (Weeks 5-8)

**Goal**: Reliable system with observability and approval workflows.

**Deliverables**:
- [ ] Full tool registry with validation
- [ ] Permission layer (read/write/critical)
- [ ] Idempotency key support
- [ ] HITL approval gates
- [ ] Task queue with retry
- [ ] Health check endpoints
- [ ] Error handling and graceful degradation
- [ ] Prometheus metrics
- [ ] Basic authentication

**Success Criteria**:
- Tool error rate <1%
- Approval workflow blocks critical actions
- System recovers from crash without data loss

### Phase 3: Advanced Features (Weeks 9-14)

**Goal**: Full deal lifecycle management with memory and cloud routing.

**Deliverables**:
- [ ] Plan-and-Execute pattern for complex tasks
- [ ] BGE-M3 embeddings + pgvector retrieval
- [ ] Reranking layer
- [ ] Hybrid cloud routing with cost tracking
- [ ] MCP server integration
- [ ] Sub-agents (triage, analysis, drafting)
- [ ] Qdrant migration (if needed)

**Success Criteria**:
- Agent processes deal from intake to transition
- ≥80% tasks handled locally
- Retrieval recall ≥80%

### Phase 4: Optimization (Ongoing)

**Goal**: Performance tuning and cost optimization.

**Deliverables**:
- [ ] Router model fine-tuning
- [ ] Prompt optimization
- [ ] Response caching
- [ ] Batch inference
- [ ] Cost/quality dashboard

---

## 8. Testing Strategy

### 8.1 Unit Testing

```python
# tests/unit/test_tool_validation.py
import pytest
from zakops_agent.tools import validate_tool_call

def test_transition_deal_valid():
    result = validate_tool_call(
        "transition_deal",
        {"deal_id": "DL-0001", "new_stage": "qualified", "reason": "Good fit"},
    )
    assert result.valid is True

def test_transition_deal_invalid_stage():
    result = validate_tool_call(
        "transition_deal",
        {"deal_id": "DL-0001", "new_stage": "invalid_stage"},
    )
    assert result.valid is False
    assert "enum" in result.error.lower()

def test_transition_deal_missing_required():
    result = validate_tool_call(
        "transition_deal",
        {"deal_id": "DL-0001"},  # missing new_stage
    )
    assert result.valid is False
```

### 8.2 Integration Testing

```python
# tests/integration/test_workflow_e2e.py
import pytest
from zakops_agent import create_agent, AgentRequest

@pytest.fixture
async def agent():
    return create_agent(db_url=TEST_DB_URL)

async def test_simple_query_workflow(agent):
    response = await agent.invoke(
        AgentRequest(
            message="List all deals in proposal stage",
            actor_id="test_user",
        )
    )
    assert response.success
    assert "deals" in response.content.lower()

async def test_critical_action_requires_approval(agent):
    response = await agent.invoke(
        AgentRequest(
            message="Approve action ACT-001",
            actor_id="test_user",
        )
    )
    assert response.pending_approval is not None
    assert response.pending_approval["tool"] == "approve_action"

async def test_state_persists_across_restart(agent):
    # Start workflow
    r1 = await agent.invoke(
        AgentRequest(
            thread_id="test-thread",
            message="Analyze deal DL-0001",
        )
    )

    # Simulate restart by creating new agent instance
    agent2 = create_agent(db_url=TEST_DB_URL)

    # Resume should work
    r2 = await agent2.invoke(
        AgentRequest(
            thread_id="test-thread",
            message="Continue",
        )
    )
    assert r2.success
```

### 8.3 Model Evaluation Harness

```python
# evals/tool_calling_eval.py
import json
from pathlib import Path

EVAL_SET = Path("evals/tool_calling_dataset.jsonl")

async def evaluate_tool_calling(model_name: str) -> dict:
    results = {"exact_match": 0, "partial_match": 0, "hallucination": 0, "total": 0}

    with open(EVAL_SET) as f:
        for line in f:
            case = json.loads(line)
            prompt = case["prompt"]
            expected_tool = case["expected_tool"]
            expected_args = case["expected_args"]

            response = await llm_gateway.complete(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                tools=TOOL_DEFINITIONS,
            )

            results["total"] += 1

            if response.tool_calls:
                actual_tool = response.tool_calls[0].name
                actual_args = response.tool_calls[0].arguments

                if actual_tool == expected_tool and actual_args == expected_args:
                    results["exact_match"] += 1
                elif actual_tool == expected_tool:
                    results["partial_match"] += 1
                else:
                    results["hallucination"] += 1
            else:
                results["hallucination"] += 1  # Should have called tool

    return {
        "accuracy": results["exact_match"] / results["total"],
        "partial_accuracy": (results["exact_match"] + results["partial_match"]) / results["total"],
        "hallucination_rate": results["hallucination"] / results["total"],
        "raw": results,
    }
```

### 8.4 Chaos Testing

```bash
#!/bin/bash
# chaos/test_crash_recovery.sh

echo "Starting workflow..."
THREAD_ID=$(curl -s -X POST localhost:8090/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze deal DL-0001"}' | jq -r '.thread_id')

echo "Thread: $THREAD_ID"
sleep 2

echo "Killing agent process..."
pkill -9 -f "zakops_agent"

echo "Restarting agent..."
python -m zakops_agent.server &
sleep 5

echo "Resuming workflow..."
RESULT=$(curl -s -X POST localhost:8090/agent/invoke \
  -H "Content-Type: application/json" \
  -d "{\"thread_id\": \"$THREAD_ID\", \"message\": \"Continue\"}")

if echo "$RESULT" | jq -e '.success' > /dev/null; then
  echo "PASS: Workflow recovered successfully"
else
  echo "FAIL: Workflow did not recover"
  exit 1
fi
```

---

## 9. Deployment & Operations

### 9.1 Service Configuration

```yaml
# docker-compose.yml
version: "3.8"

services:
  vllm:
    image: vllm/vllm-openai:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    ports:
      - "8000:8000"
    command: >
      --model Qwen/Qwen3-32B-Instruct-AWQ
      --quantization awq
      --max-model-len 32000
      --gpu-memory-utilization 0.90
      --enable-auto-tool-choice
      --tool-call-parser hermes
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  agent:
    build: ./agent
    depends_on:
      - vllm
      - postgres
    ports:
      - "8095:8095"
    environment:
      - DATABASE_URL=postgresql://zakops:${DB_PASSWORD}@postgres:5432/zakops
      - VLLM_BASE_URL=http://vllm:8000/v1
      - LANGFUSE_HOST=http://langfuse:3000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8095/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3001:3000"
    environment:
      - DATABASE_URL=postgresql://langfuse:${LANGFUSE_DB_PASSWORD}@postgres:5432/langfuse
      - NEXTAUTH_SECRET=${LANGFUSE_SECRET}
      - NEXTAUTH_URL=http://localhost:3001
```

### 9.2 Health Checks

```python
# zakops_agent/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/health/ready")
async def ready():
    checks = {}

    # Database
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"

    # vLLM
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:8000/health", timeout=5)
            checks["vllm"] = "healthy" if r.status_code == 200 else "unhealthy"
    except Exception as e:
        checks["vllm"] = f"unhealthy: {e}"

    # Overall
    all_healthy = all(v == "healthy" for v in checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        content={"status": "ready" if all_healthy else "not_ready", "checks": checks},
        status_code=status_code,
    )
```

### 9.3 Monitoring & Alerting

**Critical Alerts**:
- vLLM OOM or crash
- Workflow failure rate >5%
- Tool hallucination rate >2%
- Checkpoint write failures
- Queue depth >100 (backlog)

**Warning Alerts**:
- P95 latency >3s
- Cloud cost >$10/day
- Dead letter queue depth >10

---

## 10. Risks, Tradeoffs, and Open Questions

### 10.1 Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Qwen3-32B tool accuracy insufficient | Medium | High | Fallback to cloud; fine-tune on deal data |
| VRAM constraints with large context | Low | Medium | Reduce max-model-len; cloud escalation |
| MCP integration issues (like LangSmith) | Medium | Medium | Direct tool fallback; don't depend on MCP |
| Checkpoint bloat | Medium | Low | TTL on old checkpoints; external storage for large data |
| Hallucinated critical actions | Low | High | HITL gates; never auto-approve critical |

### 10.2 Key Tradeoffs Made

| Tradeoff | Choice | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Model size | 32B over 70B | 70B with offload | Latency priority; 32B sufficient for deals [A] |
| Vector DB | pgvector first | Qdrant from start | Minimize deps; migrate when needed [C] |
| Queue | Postgres over Redis | Redis + Dramatiq | Already have Postgres; simpler ops [B] |
| Observability | Langfuse over LangSmith | LangSmith cloud | Self-hosted; no vendor dependency [B] |

### 10.3 Open Questions

1. **Q: How well does Qwen3 handle multi-turn deal conversations?**
   - *Proposed Test*: Run 20 multi-turn scenarios from real deal history.

2. **Q: What is the actual reranker quality uplift on deal documents?**
   - *Proposed Test*: A/B test on 100 retrieval queries.

3. **Q: When does pgvector hit limits requiring Qdrant?**
   - *Assumption*: >1M vectors or >250ms P95 latency.
   - *Proposed Test*: Load test with synthetic data.

4. **Q: What hybrid routing rules maximize quality while minimizing cost?**
   - *Proposed Test*: Classify 100 queries by complexity; measure local vs cloud quality.

---

## 11. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **HITL** | Human-in-the-loop; workflow pauses for human approval |
| **Checkpoint** | Serialized agent state saved to database |
| **Idempotency Key** | Unique ID ensuring operation executes exactly once |
| **Tool Permission** | Classification: read, write, or critical |
| **Dead Letter Queue** | Queue for tasks that failed all retries |

### B. Decision Log

| Decision | Chose | Over | Reason |
|----------|-------|------|--------|
| Primary Model | Qwen3-32B | Qwen2.5-32B | Better tool calling; newer [B] |
| Inference Engine | vLLM | TensorRT-LLM | Simpler setup; sufficient perf [A][B][C] |
| Framework | LangGraph | AutoGen | Production-proven; checkpointing [A][B][C] |
| Vector DB (Ph1) | pgvector | Qdrant | Already present; minimize deps [C] |
| Observability | Langfuse | LangSmith | Self-hosted; MIT license [B] |
| Queue | Postgres | Redis | No new deps; ACID with business data [B] |

### C. What We Removed or Replaced

| From Inputs | Removed/Replaced | Reason |
|-------------|-----------------|--------|
| Temporal for all workflows [A] | PostgresSaver + queue | LangGraph has built-in checkpointing |
| LangSmith for hosting [A] | Langfuse (self-hosted) | Project context: LangSmith hosting failed |
| Redis + Dramatiq [C] | Postgres queue | Simpler; sufficient for scale |
| Qdrant from Phase 1 [B] | pgvector first | Minimize initial complexity |

### D. Assumptions Made

1. Qwen3-32B is available and works with Hermes tool parser (to verify)
2. RTX 5090 has stable CUDA support for vLLM (to verify)
3. 32K context is sufficient for deal workflows (assumption based on [A][B])
4. Hundreds of deals/day is target scale (not thousands) [B]
5. Single operator (not multi-tenant) [Project Context]

### E. Coverage Map Summary

| Topic | Input A | Input B | Input C | Master Doc |
|-------|---------|---------|---------|------------|
| Model Selection | Qwen2.5-32B | Qwen3-32B | Qwen2.5/Llama3.3 | Qwen3-32B |
| Inference | vLLM | vLLM | vLLM | vLLM |
| Framework | LangGraph | LangGraph | LangGraph | LangGraph |
| State | Postgres | PostgresSaver | Postgres | PostgresSaver |
| Vector DB | pgvector | Qdrant | pgvector→Qdrant | pgvector→Qdrant |
| Embeddings | - | BGE-M3 | bge-m3+reranker | BGE-M3+reranker |
| Tools | MCP | Hybrid | MCP+internal | Hybrid |
| Routing | Semantic | LiteLLM | LiteLLM | LiteLLM |
| Observability | LangSmith | Langfuse | OTel+Langfuse | OTel+Langfuse |
| Queue | Temporal | Postgres | Redis+Dramatiq | Postgres |
| Security | - | ABAC/OPA | Cloudflare/RBAC | RBAC+Cloudflare |
| Testing | - | - | - | Comprehensive |
| Deployment | - | Partial | - | Full |

---

## 12. Quality Audit

### Grades

| Criterion | Grade | Justification |
|-----------|-------|---------------|
| **Completeness** | A | Covers all 8 layers + ops + security + testing |
| **Correctness** | A- | Resolved all contradictions; some claims need verification |
| **Novelty/Edge-of-Tech** | B+ | Uses latest models (Qwen3); standard patterns |
| **Engineering Feasibility** | A | Clear interfaces; realistic timelines; existing infra |
| **Clarity** | A | ASCII diagrams; tables; consistent terminology |

### Top 10 Remaining Weaknesses & Fixes

| # | Weakness | Fix |
|---|----------|-----|
| 1 | Qwen3-32B tool accuracy unverified | Run eval set before Phase 1 commit |
| 2 | No fine-tuning guidance | Add Phase 4 fine-tuning runbook |
| 3 | CI/CD not specified | Add GitHub Actions workflow |
| 4 | Rollback strategy vague | Document specific rollback procedures |
| 5 | Multi-turn conversation handling unproven | Add eval cases for multi-turn |
| 6 | Reranker latency cost not measured | Benchmark before Phase 3 |
| 7 | No load testing plan | Add locust/k6 test scripts |
| 8 | Secrets management Phase 1 is basic | Document Vault migration path |
| 9 | Prompt templates not specified | Add prompt library with versioning |
| 10 | No disaster recovery plan | Document backup/restore procedures |

---

*Document synthesized from Inputs A, B, C per rigorous review process.*
*Ready for implementation review.*

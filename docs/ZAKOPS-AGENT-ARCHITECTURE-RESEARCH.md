# ZakOps AI Agent Architecture Research
## Building a Cutting-Edge Local AI Agent for Deal Lifecycle Management

**Research Date:** January 2026
**Target System:** SACS AIOps 3.0 / ZakOps Deal Lifecycle Platform
**Hardware:** RTX 5090 (32GB VRAM), 64GB DDR5, AMD Ryzen 9

---

## Executive Summary

### Key Recommendations

| Layer | Primary Recommendation | Rationale |
|-------|----------------------|-----------|
| **Model** | Qwen3-32B (Q4 quantized) | Best tool-calling, fits in 32GB VRAM (~20GB), 61 tok/s on RTX 5090 |
| **Inference** | vLLM | Best latency + throughput balance, production-proven, OpenAI-compatible API |
| **Framework** | LangGraph | State machine architecture, PostgresSaver persistence, production track record |
| **Tools** | Hybrid MCP + Direct | Keep MCP for portability, add direct calls for latency-critical operations |
| **Memory** | Qdrant (self-hosted) | Best filtering, Rust performance, mid-scale sweet spot |
| **Embeddings** | BGE-M3 | 72% retrieval accuracy, 8K context, multilingual |
| **Observability** | Langfuse (self-hosted) | Open source, MIT license, full control |
| **Reliability** | LangGraph + PostgreSQL checkpointing | Built-in durability, idempotent tool design |
| **Security** | ABAC with OPA | Context-aware policies, externalized authorization |

### Estimated Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: MVP | 2-3 weeks | Working agent with basic deal operations |
| Phase 2: Production Hardening | 3-4 weeks | Persistence, observability, error handling |
| Phase 3: Advanced Features | 4-6 weeks | Multi-agent, hybrid cloud, full tool suite |
| Phase 4: Optimization | Ongoing | Fine-tuning, cost optimization, scaling |

### Major Risks

1. **Model Quality for Complex Reasoning** - Local 32B may not match GPT-4/Claude for edge cases
   - *Mitigation:* Hybrid routing to cloud for complex tasks
2. **Tool Call Reliability** - Open models have higher hallucination rates than GPT-4
   - *Mitigation:* Structured output enforcement, validation layers
3. **State Management Complexity** - Long-running deal workflows across restarts
   - *Mitigation:* PostgresSaver checkpointing, idempotent tool design

---

## Layer 1: Local Model Selection & Inference

### Current State of the Art (January 2026)

The open-source model landscape has dramatically improved. Key developments:

- **Qwen3 series** matches Qwen2.5 with 2x fewer parameters (Qwen3-32B ~ Qwen2.5-72B quality)
- **DeepSeek V3.2** reaches GPT-4 level but 671B params (37B active MoE)
- **GLM-4.5-Air** specifically optimized for agent/tool use
- **K2** emerged as highest-scoring open model on Agent Leaderboard v2

### RTX 5090 Performance Benchmarks

| Model Size | VRAM Usage | Tokens/sec | Fits in 32GB? |
|------------|------------|------------|---------------|
| 8B (Q4) | ~5GB | 213 tok/s | Yes |
| 32B (Q4) | ~19-20GB | 61 tok/s | Yes |
| 70B (Q4) | ~40GB | N/A single GPU | No - needs 2x 5090 |

**Key Capability:** RTX 5090 can sustain 147K token context windows entirely in VRAM at ~52 tok/s with 30B MoE models.

### Model Recommendations

**Primary: Qwen3-32B-Instruct (Q4_K_M quantization)**
- Best tool calling among open models at this size
- Hybrid thinking modes (reasoning vs fast response)
- 128K context window
- MIT license (fully permissive)
- Qwen-Agent framework provides excellent MCP integration

**Alternative: DeepSeek-V3-Lite (if available) or Mistral-Large-2 (32B)**

**For specialized tasks:**
- **Complex reasoning:** Route to Claude/GPT-4 via hybrid
- **Code generation:** Qwen3-Coder variants
- **Fast classification:** Qwen3-8B as router model

### Inference Engine Comparison

| Engine | Throughput | Latency | Setup Complexity | Best For |
|--------|------------|---------|------------------|----------|
| **vLLM** | Excellent | Low | 1-2 days | Production serving, high concurrency |
| **SGLang** | Highest | Very Low | 1-2 days | Agents with KV cache reuse (RAG) |
| **TensorRT-LLM** | Excellent | Lowest | Weeks | Maximum raw performance, NVIDIA-heavy |
| **llama.cpp** | Good | Medium | Hours | Edge deployment, CPU fallback |
| **Ollama** | Moderate | Medium | Minutes | Development, quick testing |

**Primary Recommendation: vLLM**
- Best balance of performance and setup complexity
- OpenAI-compatible API (drop-in for existing code)
- Production-proven at LinkedIn, Uber, 400+ companies
- Excellent tool calling support with Hermes parser

**Configuration for RTX 5090:**
```bash
vllm serve Qwen/Qwen3-32B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 32000 \
  --gpu-memory-utilization 0.90 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Inference latency (32K context) | < 2 seconds TTFT | vLLM metrics |
| Tool call accuracy | > 95% correct parameters | Berkeley Function Calling Leaderboard methodology |
| Throughput | > 50 tok/s generation | Load testing |
| Context handling | 32K tokens minimum | Needle-in-haystack test |

---

## Layer 2: Agent Architecture & Orchestration

### Current State of the Art

**Framework Landscape 2025:**
- **LangGraph** dominates production deployments (LinkedIn, Uber, Replit)
- **AutoGen** merging with Semantic Kernel for Microsoft Agent Framework (GA Q1 2026)
- **CrewAI** powers 60% of Fortune 500 agents but hits walls at 6-12 months
- **DSPy** excellent for prompt optimization, not agent orchestration

### Framework Comparison

| Framework | Strengths | Weaknesses | Best For |
|-----------|-----------|------------|----------|
| **LangGraph** | State machine, checkpointing, debugging | Learning curve | Complex workflows, production |
| **AutoGen** | Conversational, role-playing | Not yet production-ready (v0.4) | Prototyping, Azure integration |
| **CrewAI** | Simple role-based collaboration | Inflexible for custom patterns | Quick MVPs, sequential tasks |
| **DSPy** | Prompt optimization | Not for multi-agent | Improving prompts |

### Primary Recommendation: LangGraph

**Why LangGraph:**
1. **Graph-based orchestration** - Explicit state machines with nodes, edges, conditional routing
2. **Built-in checkpointing** - PostgresSaver for durable state across restarts
3. **Human-in-the-loop** - Native interrupt/resume patterns for approvals
4. **Time-travel debugging** - Replay any point in execution
5. **Production track record** - Running at scale at major companies

**Architecture Pattern: Plan-and-Execute**

```
┌─────────────────────────────────────────────────────────────┐
│                      DEAL LIFECYCLE AGENT                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   PLANNER   │───▶│  EXECUTOR   │───▶│  VERIFIER   │     │
│  │  (32B LLM)  │    │  (8B LLM)   │    │  (Rules)    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    STATE GRAPH                       │   │
│  │  ┌────┐  ┌────────┐  ┌─────────┐  ┌──────────┐     │   │
│  │  │INIT│─▶│PLANNING│─▶│EXECUTING│─▶│VALIDATING│─▶...│   │
│  │  └────┘  └────────┘  └─────────┘  └──────────┘     │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│               ┌─────────────────────┐                       │
│               │   PostgresSaver     │                       │
│               │   (Checkpoints)     │                       │
│               └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Patterns to Implement:**

1. **ReAct for simple operations** - Direct tool calls for health checks, listings
2. **Plan-and-Execute for complex workflows** - Deal transitions, document analysis
3. **Supervisor pattern for sub-agents** - Triage agent, analysis agent, drafting agent
4. **Human-in-the-loop interrupts** - Approval gates before state transitions

### State Management

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Production configuration
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost:5432/zakops"
)

# Compile graph with persistence
app = graph.compile(checkpointer=checkpointer)

# Resume from checkpoint
config = {"configurable": {"thread_id": "deal-DL-0001"}}
result = await app.ainvoke(input, config)
```

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow completion rate | > 99% | End-to-end success tracking |
| Recovery from crash | 100% state recovery | Chaos testing |
| Human approval latency | < 500ms UI response | APM tracking |
| Sub-agent routing accuracy | > 95% | Evaluation dataset |

---

## Layer 3: Tool Integration & Execution

### MCP vs Function Calling Analysis

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **MCP** | Portable, standardized, multi-runtime | Latency overhead, security concerns | Shared tools across products |
| **Function Calling** | Low latency, tight integration | Vendor-specific, less portable | Single-app, latency-critical |
| **Hybrid** | Best of both | Complexity | Production systems |

### Security Concerns with MCP (2025 Findings)

- 2,000+ MCP servers found without authentication (Knostic research July 2025)
- Over-permissioning patterns identified (Backslash Security June 2025)
- Replit agent deleted production database despite safeguards

**Recommendation: Hybrid approach with security hardening**

### Tool Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TOOL GATEWAY                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  DIRECT TOOLS    │    │    MCP SERVER    │          │
│  │  (Low latency)   │    │   (Portable)     │          │
│  │                  │    │                  │          │
│  │  - list_deals    │    │  - External APIs │          │
│  │  - get_deal      │    │  - Third-party   │          │
│  │  - check_health  │    │  - Future tools  │          │
│  └──────────────────┘    └──────────────────┘          │
│           │                       │                     │
│           ▼                       ▼                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │              VALIDATION LAYER                    │   │
│  │  - JSON Schema validation                        │   │
│  │  - Pydantic models                               │   │
│  │  - Parameter range checks                        │   │
│  │  - Idempotency token injection                   │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │              PERMISSION LAYER                    │   │
│  │  - Read vs Write classification                  │   │
│  │  - Approval requirement check                    │   │
│  │  - Rate limiting                                 │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Tool Reliability Patterns

1. **Structured Output Enforcement**
   - Use JSON mode with schema constraints
   - Pydantic validation on all tool inputs
   - Reject malformed calls before execution

2. **Idempotency**
   - Every write operation accepts idempotency key
   - Store operation results for replay
   - Safe under retries

3. **Approval Workflow**
   ```python
   class ToolPermission(Enum):
       READ = "read"           # No approval needed
       WRITE = "write"         # May need approval
       CRITICAL = "critical"   # Always needs approval

   TOOL_PERMISSIONS = {
       "list_deals": ToolPermission.READ,
       "get_deal": ToolPermission.READ,
       "transition_deal": ToolPermission.WRITE,
       "approve_action": ToolPermission.CRITICAL,
   }
   ```

### Existing MCP Server

Keep the existing MCP server at `localhost:9100` with modifications:
- Add authentication (currently missing per security research)
- Add idempotency token support
- Add rate limiting
- Keep for external/future integrations

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tool call success rate | > 99% | Error rate tracking |
| Parameter hallucination rate | < 1% | Validation rejection logs |
| Average tool latency | < 200ms | APM tracking |
| Approval workflow completion | 100% | End-to-end testing |

---

## Layer 4: Memory Architecture

### Memory Types Required

| Type | Purpose | Storage | TTL |
|------|---------|---------|-----|
| **Working Memory** | Current conversation | LangGraph State | Session |
| **Short-term Memory** | Recent context | PostgreSQL + Checkpoints | Hours/Days |
| **Long-term Memory** | Deal history, documents | Qdrant + PostgreSQL | Permanent |
| **Episodic Memory** | Past interactions | Event log | 90 days |

### Vector Database Comparison

| Database | Best For | Performance | Self-Hosting |
|----------|----------|-------------|--------------|
| **Qdrant** | Complex filtering, mid-scale | Excellent | Docker/K8s |
| **Milvus** | Billion-scale, heavy ops | Excellent | Complex |
| **Chroma** | Prototyping, < 100K vectors | Good | Embedded |
| **Weaviate** | Hybrid search, GraphQL | Good | Docker/K8s |

### Primary Recommendation: Qdrant

**Why Qdrant:**
- Rust-based = excellent memory efficiency and performance
- Best-in-class filtering capabilities (deal metadata queries)
- Simple Docker deployment
- Sweet spot for mid-scale (millions of vectors)
- Active development, good documentation

**Configuration:**
```yaml
# docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
```

### Embedding Model: BGE-M3

**Why BGE-M3:**
- 72% retrieval accuracy (highest in benchmarks)
- 8,192 token context (handles long documents)
- Supports dense + sparse + multi-vector retrieval
- MIT license
- 568M parameters (runs fast locally)

**Alternative:** Nomic-Embed for speed-critical applications (faster, slightly lower accuracy)

### Memory Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MEMORY SYSTEM                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │  WORKING MEMORY │    │  SHORT-TERM     │            │
│  │  (LangGraph)    │    │  (PostgreSQL)   │            │
│  │                 │    │                 │            │
│  │  - Messages     │    │  - Checkpoints  │            │
│  │  - Tool results │    │  - Session data │            │
│  │  - Plan state   │    │  - Recent deals │            │
│  └─────────────────┘    └─────────────────┘            │
│                                                          │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │  LONG-TERM      │    │  EPISODIC       │            │
│  │  (Qdrant)       │    │  (Event Log)    │            │
│  │                 │    │                 │            │
│  │  - Documents    │    │  - Agent runs   │            │
│  │  - Deal history │    │  - Decisions    │            │
│  │  - Knowledge    │    │  - Outcomes     │            │
│  └─────────────────┘    └─────────────────┘            │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              RETRIEVAL LAYER                     │   │
│  │  - Hybrid search (dense + sparse)                │   │
│  │  - Metadata filtering                            │   │
│  │  - Reranking (cross-encoder)                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Retrieval accuracy | > 80% relevant | Human evaluation |
| Query latency | < 100ms | P95 latency |
| Context relevance | > 90% useful | LLM-as-judge |
| Storage efficiency | < 10GB for 10K deals | Disk usage |

---

## Layer 5: Hybrid Cloud Integration

### Routing Strategy

**When to use Local (80% target):**
- Deal CRUD operations
- Document summarization
- Simple classification
- Routine queries
- Structured data extraction

**When to use Cloud (20% target):**
- Complex multi-step reasoning
- Novel situations outside training
- High-stakes decisions requiring verification
- Long-form content generation
- Edge cases local model struggles with

### LLM Gateway Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LLM ROUTER                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              COMPLEXITY CLASSIFIER               │   │
│  │  - Task type detection                           │   │
│  │  - Confidence scoring                            │   │
│  │  - Historical success rates                      │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│            ┌─────────────┼─────────────┐               │
│            ▼             ▼             ▼               │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│     │  LOCAL   │  │  CLAUDE  │  │  GPT-4   │         │
│     │ Qwen3-32B│  │  Sonnet  │  │          │         │
│     │          │  │          │  │          │         │
│     │ - Fast   │  │ - Complex│  │ - Backup │         │
│     │ - Cheap  │  │ - Reason │  │ - Verify │         │
│     └──────────┘  └──────────┘  └──────────┘         │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              FALLBACK CHAIN                      │   │
│  │  Local → Claude → GPT-4 → Graceful Degradation  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Cost Optimization

**RouteLLM approach:** Use trained router to decide local vs cloud
- Can reduce costs by 85% while maintaining 95% GPT-4 quality

**Caching strategy:**
- Redis-based caching with configurable TTL
- Cache similar queries (semantic similarity > 0.95)
- Cross-provider compatibility

**Budget controls:**
- Daily spend limits per provider
- Rate limiting
- Usage tracking and alerts

### Recommended Gateway: LiteLLM

**Why LiteLLM:**
- Unified API for 100+ models
- Built-in fallbacks and retries
- Cost tracking
- Caching support
- OpenAI-compatible

```python
from litellm import completion

# Automatic routing with fallback
response = completion(
    model="qwen/qwen3-32b",  # Primary: local
    messages=messages,
    fallbacks=["claude-3-sonnet", "gpt-4"],  # Fallback chain
)
```

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Local processing rate | > 80% | Router logs |
| Cloud cost per deal | < $0.50 | Cost tracking |
| Fallback success rate | > 99% | Error logs |
| Quality maintenance | > 95% of cloud-only | Evaluation set |

---

## Layer 6: Observability & Debugging

### Platform Comparison

| Platform | Self-Hosted | Cost | LangChain Integration | Best For |
|----------|-------------|------|----------------------|----------|
| **Langfuse** | Free (MIT) | Free self-hosted | Good | Full control, privacy |
| **LangSmith** | Enterprise only | $39/user/mo | Native | LangChain-heavy teams |
| **Phoenix** | Free (OSS) | Free | Good | Evaluation focus |

### Primary Recommendation: Langfuse (Self-Hosted)

**Why Langfuse:**
- Fully open source (MIT license)
- Free self-hosting
- 19K+ GitHub stars, active community
- LangGraph integration
- OpenTelemetry support
- Complete feature set: tracing, prompt versioning, evaluation

**Deployment:**
```yaml
# docker-compose.yml
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://...
      - NEXTAUTH_SECRET=...
      - NEXTAUTH_URL=http://localhost:3000
```

### Metrics to Track

**Agent Performance:**
- Task completion rate
- Average steps to completion
- Tool call success rate
- Error rate by type

**Model Performance:**
- Tokens per request
- Latency (TTFT, generation)
- Cost per request
- Cache hit rate

**Business Metrics:**
- Deals processed per day
- Time to process deal
- Human intervention rate
- Approval turnaround time

### Debugging Workflow

```
┌─────────────────────────────────────────────────────────┐
│                 DEBUGGING WORKFLOW                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. TRACE CAPTURE                                        │
│     └─▶ Langfuse captures full execution trace          │
│                                                          │
│  2. FAILURE DETECTION                                    │
│     └─▶ Automatic alerts on error patterns              │
│                                                          │
│  3. ROOT CAUSE ANALYSIS                                  │
│     └─▶ Step-through replay in Langfuse UI              │
│                                                          │
│  4. REPRODUCTION                                         │
│     └─▶ Export trace as test case                       │
│                                                          │
│  5. FIX VALIDATION                                       │
│     └─▶ Run against regression suite                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Trace coverage | 100% of requests | Langfuse dashboard |
| Alert latency | < 1 minute | Alert timestamp |
| Debug time | < 30 min for typical issue | Incident tracking |
| Dashboard uptime | > 99.9% | Health checks |

---

## Layer 7: Reliability & Production Readiness

### Core Patterns

1. **Durable Execution with Checkpointing**
   - Every state transition saved to PostgreSQL
   - Automatic resume from last checkpoint on restart
   - No lost work due to crashes

2. **Idempotent Tool Design**
   ```python
   async def transition_deal(
       deal_id: str,
       new_stage: str,
       idempotency_key: str  # Required for writes
   ) -> dict:
       # Check if already processed
       existing = await get_by_idempotency_key(idempotency_key)
       if existing:
           return existing.result

       # Execute transition
       result = await execute_transition(deal_id, new_stage)

       # Store result for future replays
       await store_result(idempotency_key, result)
       return result
   ```

3. **Retry with Backoff**
   - Exponential backoff for transient failures
   - Circuit breaker for persistent failures
   - Dead letter queue for manual review

4. **Health Monitoring**
   ```python
   class HealthStatus(BaseModel):
       status: Literal["healthy", "degraded", "unhealthy"]
       components: dict[str, ComponentHealth]
       last_check: datetime

   HEALTH_CHECKS = [
       ("database", check_postgres),
       ("llm", check_vllm),
       ("vector_db", check_qdrant),
       ("mcp_server", check_mcp),
   ]
   ```

### Queue Architecture

**Recommendation: PostgreSQL-based queue (SKIP LISTEN/NOTIFY)**

For ZakOps scale (hundreds of deals/day, not millions), using PostgreSQL's built-in features is simpler than adding RabbitMQ/Redis:

```sql
-- Simple task queue table
CREATE TABLE task_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT DEFAULT 'pending',
    idempotency_key TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT
);

-- Claim task with SELECT FOR UPDATE SKIP LOCKED
```

### Failure Recovery

| Failure Type | Detection | Recovery |
|--------------|-----------|----------|
| LLM timeout | 30s timeout | Retry with backoff, fallback to cloud |
| Tool failure | Exception handling | Retry 3x, then human escalation |
| DB failure | Connection error | Wait for recovery, alert |
| Agent crash | Process monitor | Restart from checkpoint |

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| System uptime | > 99.9% | Health checks |
| Crash recovery | < 30 seconds | Restart timing |
| Data durability | Zero loss | Checkpoint verification |
| Queue processing | < 5 min latency | Queue depth monitoring |

---

## Layer 8: Security & Access Control

### Authentication Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 SECURITY ARCHITECTURE                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              IDENTITY LAYER                      │   │
│  │  - User authentication (OIDC)                    │   │
│  │  - Agent identity (SPIFFE/SPIRE)                 │   │
│  │  - Service-to-service mTLS                       │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │              AUTHORIZATION LAYER                 │   │
│  │  - ABAC policies (OPA/Rego)                      │   │
│  │  - Context-aware decisions                       │   │
│  │  - Least privilege enforcement                   │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │              AUDIT LAYER                         │   │
│  │  - Immutable logs                                │   │
│  │  - All auth decisions logged                     │   │
│  │  - 7-year retention                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### RBAC/ABAC Model

**Roles:**
```python
class Role(Enum):
    VIEWER = "viewer"       # Read-only access
    OPERATOR = "operator"   # Can trigger actions
    APPROVER = "approver"   # Can approve critical actions
    ADMIN = "admin"         # Full access
```

**ABAC Policies (OPA/Rego):**
```rego
# policy.rego
package zakops.authz

default allow = false

# Viewers can read anything
allow {
    input.action == "read"
    input.user.role == "viewer"
}

# Operators can trigger non-critical actions
allow {
    input.action == "write"
    input.user.role == "operator"
    not input.resource.critical
}

# Critical actions require approver role
allow {
    input.action == "approve"
    input.user.role in ["approver", "admin"]
}
```

### Audit Logging

**Required Fields:**
```python
class AuditEvent(BaseModel):
    timestamp: datetime
    event_type: str
    actor_type: Literal["user", "agent", "system"]
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    outcome: Literal["success", "failure", "denied"]
    details: dict
    trace_id: str  # Correlation with observability
```

**Storage:** Append-only PostgreSQL table with row-level security

### Secrets Management

| Secret Type | Storage | Rotation |
|-------------|---------|----------|
| API keys | Environment variables | Manual |
| DB credentials | Docker secrets | Quarterly |
| Encryption keys | File with 0600 perms | Annually |

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Auth coverage | 100% of endpoints | Audit logs |
| Failed auth attempts | < 1% legitimate | Error rate |
| Audit completeness | 100% of operations | Log verification |
| Secret exposure | Zero incidents | Security scanning |

---

## Integrated Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        ZAKOPS AI AGENT SYSTEM                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Next.js   │  │   FastAPI   │  │  Cloudflare │              │
│  │  Dashboard  │  │  Backend    │  │   Tunnel    │              │
│  │   :3003     │  │   :8090     │  │             │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                        │
│                          ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    LANGGRAPH AGENT                          │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │ │
│  │  │ Planner │  │Executor │  │Verifier │  │ Router  │       │ │
│  │  │  Node   │  │  Node   │  │  Node   │  │  Node   │       │ │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │ │
│  │       └────────────┴────────────┴────────────┘             │ │
│  │                          │                                  │ │
│  │                          ▼                                  │ │
│  │              ┌─────────────────────┐                       │ │
│  │              │   PostgresSaver     │                       │ │
│  │              │   (Checkpoints)     │                       │ │
│  │              └─────────────────────┘                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                          │                                        │
│         ┌────────────────┼────────────────┐                      │
│         │                │                │                      │
│         ▼                ▼                ▼                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │    vLLM      │ │   LiteLLM    │ │    Tools     │            │
│  │  Qwen3-32B   │ │   Gateway    │ │   Gateway    │            │
│  │    :8000     │ │              │ │              │            │
│  └──────────────┘ └──────┬───────┘ └──────┬───────┘            │
│                          │                │                      │
│                   ┌──────┴──────┐  ┌──────┴──────┐              │
│                   │   Claude    │  │    MCP      │              │
│                   │   GPT-4     │  │   Server    │              │
│                   │  (Fallback) │  │   :9100     │              │
│                   └─────────────┘  └─────────────┘              │
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  PostgreSQL  │ │   Qdrant     │ │  Langfuse    │            │
│  │    :5432     │ │   :6333      │ │   :3000      │            │
│  │              │ │              │ │              │            │
│  │ - Deals      │ │ - Documents  │ │ - Traces     │            │
│  │ - Actions    │ │ - Embeddings │ │ - Metrics    │            │
│  │ - Events     │ │ - History    │ │ - Prompts    │            │
│  │ - Checkpts   │ │              │ │              │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Deal Intake:**
   ```
   Email/API → Triage Agent → Classification → Quarantine/Pipeline
   ```

2. **Deal Processing:**
   ```
   Deal → Planner → [Analysis, Document, Transition] → Verification → Complete
   ```

3. **Approval Workflow:**
   ```
   Agent Action → Permission Check → Queue → Human Review → Execute/Reject
   ```

---

## Implementation Roadmap

### Phase 1: Minimum Viable Agent (2-3 weeks)

**Goal:** Working agent that can list deals and check health

**Deliverables:**
- [ ] vLLM running with Qwen3-32B
- [ ] Basic LangGraph agent with ReAct pattern
- [ ] Direct tool integration (no MCP yet)
- [ ] PostgreSQL state storage
- [ ] Simple CLI/API interface

**Success Criteria:**
- Agent can answer "List all deals in proposal stage"
- Agent can check system health
- State persists across restarts

### Phase 2: Production Hardening (3-4 weeks)

**Goal:** Reliable system with observability

**Deliverables:**
- [ ] PostgresSaver checkpointing
- [ ] Langfuse integration
- [ ] Error handling and retries
- [ ] Idempotent tool design
- [ ] Health monitoring
- [ ] Basic authentication

**Success Criteria:**
- System recovers from crash without data loss
- Full execution traces in Langfuse
- < 1% error rate

### Phase 3: Advanced Features (4-6 weeks)

**Goal:** Full deal lifecycle management

**Deliverables:**
- [ ] Plan-and-Execute pattern
- [ ] Sub-agents (triage, analysis, drafting)
- [ ] Hybrid cloud routing
- [ ] Qdrant memory integration
- [ ] Human-in-the-loop approvals
- [ ] MCP server integration

**Success Criteria:**
- Agent can process deal from intake to transition
- Complex queries handled correctly
- Approval workflow works end-to-end

### Phase 4: Optimization (Ongoing)

**Goal:** Performance and cost optimization

**Deliverables:**
- [ ] Query caching
- [ ] Router fine-tuning
- [ ] Prompt optimization
- [ ] Memory consolidation
- [ ] Evaluation suite
- [ ] Documentation

**Success Criteria:**
- 80%+ local processing
- < $0.50 cloud cost per deal
- < 2s average response time

---

## Risk Assessment

### Layer 1: Model Selection

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Model quality insufficient | Medium | High | Hybrid routing to cloud |
| VRAM constraints | Low | Medium | Use Q4 quantization, monitor usage |
| Tool call hallucination | Medium | Medium | Validation layers, structured output |

### Layer 2: Agent Architecture

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Framework complexity | Medium | Medium | Start simple, expand gradually |
| State corruption | Low | High | PostgreSQL ACID, checkpointing |
| Infinite loops | Low | Medium | Max iteration limits, timeouts |

### Layer 3: Tool Integration

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP security issues | Medium | High | Authentication, rate limiting |
| Tool failures | Medium | Medium | Retries, fallbacks |
| Latency spikes | Low | Low | Caching, direct calls |

### Layer 4: Memory

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Retrieval quality | Medium | Medium | Evaluation, reranking |
| Storage growth | Low | Low | TTL, cleanup policies |
| Index corruption | Low | High | Backups, rebuild capability |

### Layer 5: Hybrid Cloud

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cloud API failures | Low | Medium | Fallback chain |
| Cost overruns | Medium | Medium | Budget limits, monitoring |
| Vendor lock-in | Low | Medium | Abstraction layer (LiteLLM) |

### Layer 6: Observability

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Trace overhead | Low | Low | Sampling for high volume |
| Storage costs | Low | Medium | Retention policies |
| Alert fatigue | Medium | Medium | Tuned thresholds |

### Layer 7: Reliability

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Checkpoint bloat | Medium | Medium | External storage for large data |
| Recovery time | Low | Medium | Fast restart, warm standby |
| Queue backlog | Low | Medium | Monitoring, scaling |

### Layer 8: Security

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Unauthorized access | Low | High | Auth, audit logging |
| Data exposure | Low | High | Encryption, access controls |
| Agent misuse | Medium | Medium | ABAC policies, human approval |

---

## Appendices

### A. Benchmark Data Sources

**Model Benchmarks:**
- [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [RTX 5090 LLM Benchmarks (RunPod)](https://www.runpod.io/blog/rtx-5090-llm-benchmarks)
- [Vellum LLM Leaderboard](https://www.vellum.ai/llm-leaderboard)

**Framework Comparisons:**
- [LangWatch Framework Comparison](https://langwatch.ai/blog/best-ai-agent-frameworks-in-2025-comparing-langgraph-dspy-crewai-agno-and-more)
- [DataCamp CrewAI vs LangGraph vs AutoGen](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)

**Vector Database Benchmarks:**
- [Firecrawl Vector DB Comparison](https://www.firecrawl.dev/blog/best-vector-databases-2025)
- [LiquidMetal AI Vector Comparison](https://liquidmetal.ai/casesAndBlogs/vector-comparison/)

### B. Configuration Examples

**vLLM Configuration:**
```bash
# Start vLLM with Qwen3-32B
docker run --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen3-32B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 32000 \
  --gpu-memory-utilization 0.90 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

**LangGraph Agent Skeleton:**
```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

class DealAgentState(TypedDict):
    messages: list
    deal_id: Optional[str]
    plan: Optional[list]
    current_step: int

def create_deal_agent():
    graph = StateGraph(DealAgentState)

    graph.add_node("router", route_request)
    graph.add_node("planner", create_plan)
    graph.add_node("executor", execute_step)
    graph.add_node("verifier", verify_result)

    graph.add_edge("router", "planner")
    graph.add_conditional_edges("planner", should_execute)
    graph.add_edge("executor", "verifier")
    graph.add_conditional_edges("verifier", next_step_or_end)

    graph.set_entry_point("router")

    checkpointer = PostgresSaver.from_conn_string(DB_URL)
    return graph.compile(checkpointer=checkpointer)
```

### C. Reference Implementations

**LangGraph Examples:**
- [LangGraph Official Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Plan-and-Execute Tutorial](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/)

**Qwen-Agent:**
- [Qwen-Agent GitHub](https://github.com/QwenLM/Qwen-Agent)

**Langfuse:**
- [Langfuse Self-Hosting](https://langfuse.com/docs/deployment/self-host)
- [LangGraph Integration](https://langfuse.com/docs/integrations/langchain/tracing)

---

## Sources

### Layer 1: Models & Inference
- [The Best Open-Source LLMs in 2026 - BentoML](https://www.bentoml.com/blog/navigating-the-world-of-open-source-large-language-models)
- [RTX 5090 LLM Benchmarks - RunPod](https://www.runpod.io/blog/rtx-5090-llm-benchmarks)
- [RTX 5090 Ollama Benchmark - DatabaseMart](https://www.databasemart.com/blog/ollama-gpu-benchmark-rtx5090)
- [vLLM vs llama.cpp - Red Hat](https://developers.redhat.com/articles/2025/09/30/vllm-or-llamacpp-choosing-right-llm-inference-engine-your-use-case)
- [Qwen3 Release Blog](https://qwenlm.github.io/blog/qwen3/)

### Layer 2: Agent Frameworks
- [Best AI Agent Frameworks 2025 - LangWatch](https://langwatch.ai/blog/best-ai-agent-frameworks-in-2025-comparing-langgraph-dspy-crewai-agno-and-more)
- [LangGraph Review 2025 - Sider.ai](https://sider.ai/blog/ai-tools/langgraph-review-is-the-agentic-state-machine-worth-your-stack-in-2025)
- [Plan-and-Execute Agents - LangChain Blog](https://www.blog.langchain.com/planning-agents/)

### Layer 3: Tools
- [MCP vs Function Calling - MarkTechPost](https://www.marktechpost.com/2025/10/08/model-context-protocol-mcp-vs-function-calling-vs-openapi-tools-when-to-use-each/)
- [MCP Security - Descope](https://www.descope.com/learn/post/mcp)
- [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)

### Layer 4: Memory
- [Best Vector Databases 2025 - Firecrawl](https://www.firecrawl.dev/blog/best-vector-databases-2025)
- [LangGraph Checkpointing Best Practices](https://sparkco.ai/blog/mastering-langgraph-checkpointing-best-practices-for-2025)
- [BGE-M3 vs Nomic Comparison](https://ai-marketinglabs.com/lab-experiments/nv-embed-vs-bge-m3-vs-nomic-picking-the-right-embeddings-for-pinecone-rag)

### Layer 5: Hybrid Cloud
- [RouteLLM - LMSYS](https://lmsys.org/blog/2024-07-01-routellm/)
- [Top LLM Gateways 2025 - Helicone](https://www.helicone.ai/blog/top-llm-gateways-comparison-2025)

### Layer 6: Observability
- [AI Observability Platforms Compared - Softcery](https://softcery.com/lab/top-8-observability-platforms-for-ai-agents-in-2025)
- [Langfuse vs LangSmith](https://langfuse.com/faq/all/langsmith-alternative)

### Layer 7: Reliability
- [Agentic AI Architectures - arXiv](https://arxiv.org/html/2512.09458)
- [Durable Agentic Flows - Temporal](https://temporal.io/blog/from-ai-hype-to-durable-reality-why-agentic-flows-need-distributed-systems)

### Layer 8: Security
- [AI Agent Security 2025 - Obsidian](https://www.obsidiansecurity.com/blog/security-for-ai-agents)
- [AI Agent Access Control - WorkOS](https://workos.com/blog/ai-agent-access-control)
- [Enterprise AI Agent Security Checklist](https://sparkco.ai/blog/2025-enterprise-ai-agent-security-checklist-guide)

---

*Document generated: January 2026*
*For ZakOps / SACS AIOps 3.0*

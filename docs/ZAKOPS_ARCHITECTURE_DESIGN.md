# ZakOps Architecture Design Document
**Version:** 2.0
**Date:** 2026-01-26
**Author:** Claude Opus 4.5

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Repository Structure](#repository-structure)
4. [Service Architecture](#service-architecture)
5. [Docker Infrastructure](#docker-infrastructure)
6. [Database Architecture](#database-architecture)
7. [API Specification](#api-specification)
8. [LangGraph Agent Architecture](#langgraph-agent-architecture)
9. [Authentication & Security](#authentication--security)
10. [Frontend Architecture](#frontend-architecture)
11. [Configuration Management](#configuration-management)
12. [Data Models](#data-models)
13. [Reliability & Idempotency](#reliability--idempotency)
14. [Observability Stack](#observability-stack)
15. [Key File Reference](#key-file-reference)

---

## 1. Executive Summary

ZakOps is an enterprise-grade deal lifecycle management platform with an agentic AI assistant featuring Human-in-the-Loop (HITL) approval workflows. The system architecture consists of:

- **Agent API** (Port 8095): LangGraph-based orchestration engine with HITL approvals
- **Backend API** (Port 8090/8091): Deal lifecycle and orchestration services
- **Dashboard** (Port 3003): Next.js admin interface
- **RAG Service** (Port 8052): Vector-based document retrieval
- **PostgreSQL Databases**: Multiple schemas for deals, agent state, and vectors
- **Observability**: Prometheus, Grafana, Loki logging stack

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ZAKOPS ARCHITECTURE v2.0                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     │
│   │    Dashboard    │     │   Agent API      │     │   Backend API   │     │
│   │   (Port 3003)   │────▶│   (Port 8095)    │────▶│  (Port 8091)    │     │
│   │   Next.js 15    │     │   FastAPI/LG     │     │    FastAPI      │     │
│   └────────┬────────┘     └────────┬─────────┘     └────────┬────────┘     │
│            │                       │                         │              │
│            │              ┌────────▼─────────┐              │              │
│            │              │   LangGraph      │              │              │
│            │              │   State Machine  │              │              │
│            │              │   ┌───────────┐  │              │              │
│            │              │   │   HITL    │  │              │              │
│            │              │   │ Interrupt │  │              │              │
│            │              │   └───────────┘  │              │              │
│            │              └────────┬─────────┘              │              │
│            │                       │                         │              │
│   ┌────────▼───────────────────────▼─────────────────────────▼────────┐    │
│   │                         PostgreSQL Cluster                        │    │
│   │  ┌────────────┐    ┌────────────────┐    ┌─────────────────┐     │    │
│   │  │   zakops   │    │  zakops_agent  │    │    crawlrag     │     │    │
│   │  │   :5432    │    │    (HITL)      │    │   (pgvector)    │     │    │
│   │  │  - deals   │    │  - approvals   │    │   - chunks      │     │    │
│   │  │  - actions │    │  - audit_log   │    │   - embeddings  │     │    │
│   │  │  - events  │    │  - checkpoints │    │                 │     │    │
│   │  └────────────┘    └────────────────┘    └─────────────────┘     │    │
│   └──────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│   │   Prometheus    │    │     Grafana     │    │      Loki       │        │
│   │   (Port 9090)   │    │   (Port 3002)   │    │   (Port 3100)   │        │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                             │
│   ┌─────────────────┐    ┌─────────────────┐                               │
│   │   RAG REST      │    │     Redis       │                               │
│   │   (Port 8052)   │    │   (Port 6379)   │                               │
│   └─────────────────┘    └─────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. System Architecture Overview

### Core Principles
1. **Separation of Concerns**: Agent orchestration, business logic, and UI are distinct services
2. **Human-in-the-Loop**: Critical actions require explicit human approval via interrupt pattern
3. **Idempotency**: All tool executions are crash-safe with SHA-256 based keys
4. **Audit Trail**: Immutable event log for compliance and debugging
5. **Checkpoint Persistence**: Full conversation state survives restarts

### Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Agent Runtime | LangGraph | Latest |
| LLM Provider | OpenAI | GPT-4o |
| Backend Framework | FastAPI | 0.115+ |
| Frontend Framework | Next.js | 15.x |
| Primary Database | PostgreSQL | 16-alpine |
| Vector Database | pgvector | Latest |
| Cache/Queue | Redis | 7-alpine |
| Container Runtime | Docker | Latest |
| Package Manager (Python) | uv | Latest |
| Package Manager (JS) | npm/bun | Latest |

---

## 3. Repository Structure

```
/home/zaks/zakops-agent-api/
├── apps/
│   ├── agent-api/                    # LangGraph Orchestration Engine
│   │   ├── app/
│   │   │   ├── api/v1/              # FastAPI routes
│   │   │   ├── core/
│   │   │   │   ├── langgraph/       # Graph definition & tools
│   │   │   │   ├── security/        # JWT authentication
│   │   │   │   └── config.py        # Environment configuration
│   │   │   ├── models/              # SQLAlchemy models
│   │   │   ├── schemas/             # Pydantic schemas
│   │   │   └── main.py              # FastAPI application entry
│   │   ├── migrations/              # SQL migrations
│   │   ├── scripts/                 # Docker entrypoint, utilities
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── pyproject.toml
│   │
│   ├── backend/                      # Deal Lifecycle & Orchestration
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── deal_lifecycle/  # Port 8090
│   │   │   │   └── orchestration/   # Port 8091
│   │   │   ├── core/
│   │   │   │   ├── agent/           # Agent run tracking
│   │   │   │   └── outbox/          # Event delivery
│   │   │   ├── models/
│   │   │   └── schemas/
│   │   ├── db/migrations/           # Database migrations
│   │   ├── infra/docker/            # Dockerfiles
│   │   └── requirements.txt
│   │
│   └── dashboard/                    # Next.js Admin UI
│       ├── src/
│       │   ├── app/                 # App Router pages
│       │   │   ├── actions/         # Action management
│       │   │   ├── agent/           # Agent activity
│       │   │   ├── chat/            # Agent chat interface
│       │   │   ├── deals/           # Deal management
│       │   │   ├── hq/              # Admin overview
│       │   │   ├── quarantine/      # Quarantine items
│       │   │   └── api/             # API routes
│       │   ├── components/          # React components
│       │   ├── constants/           # Mock data, constants
│       │   └── hooks/               # Custom hooks
│       ├── Dockerfile
│       └── package.json
│
├── packages/
│   └── contracts/                    # Shared OpenAPI specs
│
├── ops/
│   └── observability/
│       ├── prometheus/              # Metrics collection
│       ├── grafana/                 # Dashboards
│       ├── loki/                    # Log aggregation
│       └── promtail/                # Log shipping
│
├── deployments/
│   └── docker/
│       └── docker-compose.yml       # Production compose
│
├── tools/                            # CI/CD utilities
├── docs/                             # Documentation
├── db/                               # Shared migrations
└── Makefile                          # Build targets
```

---

## 4. Service Architecture

### 4.1 Agent API (Port 8095)

**Purpose**: LangGraph-based AI orchestration with HITL approval workflows

**Components**:
- FastAPI application server
- LangGraph state machine with interrupt pattern
- PostgreSQL checkpoint persistence
- JWT-based authentication
- Rate limiting (SlowAPI)

**Key Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with DB connectivity |
| `/agent/invoke` | POST | Invoke agent with message |
| `/agent/approve` | POST | Approve pending tool call |
| `/agent/reject` | POST | Reject pending tool call |
| `/agent/approvals` | GET | List pending approvals |

**Configuration**:
```yaml
Environment Variables:
  - POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  - JWT_SECRET_KEY, JWT_ALGORITHM
  - OPENAI_API_KEY, DEFAULT_LLM_MODEL
  - LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY (optional tracing)
  - ENABLE_HITL, ENABLE_AUDIT_LOG
  - HITL_APPROVAL_TIMEOUT_SECONDS (default: 3600)
```

### 4.2 Backend API - Deal Lifecycle (Port 8090)

**Purpose**: Core deal management business logic

**Key Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/deals` | GET | List all deals |
| `/api/deals/{id}` | GET | Get deal details |
| `/api/deals/{id}/events` | GET | Get deal event history |
| `/api/deals/{id}/case-file` | GET | Get deal case file |
| `/api/deals/{id}/transition` | POST | Transition deal stage |
| `/api/deals/{id}/note` | POST | Add operator note |
| `/api/actions` | GET | List all actions |
| `/api/actions/due` | GET | Get due actions |
| `/api/actions/{id}/execute` | POST | Execute action |
| `/api/quarantine` | GET | List quarantine items |
| `/api/quarantine/{id}/resolve` | POST | Resolve quarantine |

### 4.3 Backend API - Orchestration (Port 8091)

**Purpose**: Service orchestration and agent coordination

**Key Features**:
- Agent API integration
- Cross-service coordination
- Pipeline management

### 4.4 Dashboard (Port 3003)

**Purpose**: Admin web interface for deal management and agent interaction

**Pages**:
| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Redirect to deals |
| Actions | `/actions` | Pending approvals & tasks |
| Deals | `/deals` | Deal lifecycle management |
| Chat | `/chat` | Agent conversation interface |
| Agent | `/agent` | Agent activity monitoring |
| Quarantine | `/quarantine` | Unprocessed items |
| HQ | `/hq` | Admin overview |

### 4.5 RAG Service (Port 8052)

**Purpose**: Vector-based document retrieval for long-term memory

**Database**: `crawlrag` (pgvector extension)

**Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rag/query` | POST | Semantic search |
| `/rag/stats` | GET | Index statistics |
| `/rag/ingest` | POST | Add documents |

---

## 5. Docker Infrastructure

### 5.1 Primary Docker Compose
**File**: `/home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml`

```yaml
services:
  agent-api:
    ports: "8095:8095"
    depends_on: [postgres, redis]
    environment:
      - DATABASE_URL=postgresql://zakops:zakops@postgres:5432/zakops
      - REDIS_URL=redis://redis:6379/0
      - RAG_REST_URL=http://rag-rest:8052
      - AUTH_REQUIRED=true

  backend-deal-lifecycle:
    ports: "8090:8090"
    depends_on: [postgres, redis]

  backend-orchestration:
    ports: "8091:8091"
    depends_on: [postgres, agent-api]

  dashboard:
    network_mode: host
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8091
      - NEXT_PUBLIC_AGENT_API_URL=http://localhost:8095

  postgres:
    image: postgres:16-alpine
    ports: "5432:5432"
    volumes: [postgres-data:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: "6379:6379"
    volumes: [redis-data:/data]

  rag-rest:
    profiles: ["rag"]
    ports: "8052:8052"

  prometheus:
    ports: "9090:9090"

  loki:
    ports: "3100:3100"

  grafana:
    ports: "3002:3000"
```

### 5.2 Dockerfiles

**Agent API** (`apps/agent-api/Dockerfile`):
```dockerfile
FROM python:3.13.2-slim
# Uses uv package manager
# Non-root user: appuser
# Entrypoint: /app/scripts/docker-entrypoint.sh
# CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000
EXPOSE 8000
```

**Backend API** (`apps/backend/infra/docker/Dockerfile.api`):
```dockerfile
FROM python:3.11-slim
# Uses pip with requirements.txt
# Non-root user: zakops (UID 1000)
# CMD: python -m uvicorn src.api.deal_lifecycle.main:app --host 0.0.0.0 --port 8090
```

**Dashboard** (`apps/dashboard/Dockerfile`):
```dockerfile
FROM node:22-alpine AS base
# Multi-stage: deps → builder → runner
# Build args: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_AGENT_API_URL
# Non-root user: nextjs
EXPOSE 3003
```

---

## 6. Database Architecture

### 6.1 Database Overview

| Database | Port | Purpose | Extension |
|----------|------|---------|-----------|
| `zakops` | 5432 | Main application data | Standard |
| `zakops_agent` | 5432 | HITL approvals & state | Standard |
| `crawlrag` | 5434 | Vector embeddings | pgvector |

### 6.2 Schema: zakops (Main)

**Tables**:

```sql
-- Operators table
CREATE TABLE operators (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'operator',  -- admin, operator, viewer
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Artifacts table
CREATE TABLE artifacts (
    id UUID PRIMARY KEY,
    correlation_id UUID,
    deal_id UUID,
    action_id UUID,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024),
    file_type VARCHAR(50),
    file_size BIGINT,
    mime_type VARCHAR(127),
    sha256 VARCHAR(64),
    category VARCHAR(50),
    extracted_text TEXT,
    metadata JSONB DEFAULT '{}',
    storage_backend VARCHAR(50) DEFAULT 'local',
    storage_uri VARCHAR(1024),
    storage_key VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Execution checkpoints (durable execution)
CREATE TABLE execution_checkpoints (
    id UUID PRIMARY KEY,
    execution_id UUID NOT NULL,
    checkpoint_name VARCHAR(255) NOT NULL,
    checkpoint_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.3 Schema: zakops_agent (HITL)

**File**: `/home/zaks/zakops-agent-api/apps/agent-api/migrations/001_approvals.sql`

```sql
-- Approvals table (HITL workflow)
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id VARCHAR(255) NOT NULL,
    checkpoint_id VARCHAR(255),
    tool_name VARCHAR(255) NOT NULL,
    tool_args TEXT NOT NULL,  -- JSON
    actor_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, claimed, approved, rejected, expired
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    claimed_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(255),
    rejection_reason TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_approvals_thread_id ON approvals(thread_id);
CREATE INDEX idx_approvals_actor_id ON approvals(actor_id);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_approvals_tool_name ON approvals(tool_name);
CREATE INDEX idx_approvals_idempotency_key ON approvals(idempotency_key);

-- Tool executions (claim-first idempotency)
CREATE TABLE tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approval_id UUID REFERENCES approvals(id),
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    tool_args TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'claimed',  -- claimed, executing, completed, failed
    result TEXT,
    success BOOLEAN,
    error_message TEXT,
    claimed_at TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Audit log (immutable event trail)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    thread_id VARCHAR(255),
    approval_id UUID,
    tool_execution_id UUID,
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_log_actor_id ON audit_log(actor_id);
CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_log_thread_id ON audit_log(thread_id);
CREATE INDEX idx_audit_log_approval_id ON audit_log(approval_id);

-- PL/pgsql functions
CREATE OR REPLACE FUNCTION cleanup_expired_approvals()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE approvals
    SET status = 'expired'
    WHERE status = 'pending'
      AND expires_at IS NOT NULL
      AND expires_at < NOW();
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION reclaim_stale_claims(stale_threshold_minutes INTEGER DEFAULT 5)
RETURNS INTEGER AS $$
DECLARE
    reclaimed_count INTEGER;
BEGIN
    UPDATE approvals
    SET status = 'pending',
        claimed_at = NULL
    WHERE status = 'claimed'
      AND claimed_at < (NOW() - (stale_threshold_minutes || ' minutes')::INTERVAL);
    GET DIAGNOSTICS reclaimed_count = ROW_COUNT;
    RETURN reclaimed_count;
END;
$$ LANGUAGE plpgsql;
```

### 6.4 Schema: crawlrag (Vector Store)

```sql
-- pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Document chunks with embeddings
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url VARCHAR(2048) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chunks_embedding ON chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 7. API Specification

### 7.1 Agent API (MDv2 Spec)

**Base URL**: `http://localhost:8095`

#### POST /agent/invoke
Invoke the agent with a user message.

**Request**:
```json
{
    "actor_id": "user-123",
    "message": "Transition deal ABC to negotiation stage",
    "thread_id": "optional-thread-id",
    "metadata": {
        "source": "dashboard"
    }
}
```

**Response**:
```json
{
    "thread_id": "thread-abc-123",
    "status": "awaiting_approval",
    "content": "I'll transition the deal to negotiation stage. This requires your approval.",
    "pending_approval": {
        "approval_id": "apr-456",
        "tool": "transition_deal",
        "args": {
            "deal_id": "deal-abc",
            "new_stage": "negotiation"
        },
        "permission_tier": "WRITE",
        "requested_by": "user-123",
        "requested_at": "2026-01-26T10:00:00Z"
    },
    "actions_taken": [],
    "error": null
}
```

#### POST /agent/approve
Approve a pending tool execution.

**Request**:
```json
{
    "approval_id": "apr-456",
    "actor_id": "approver-789"
}
```

**Response**:
```json
{
    "status": "completed",
    "result": {
        "deal_id": "deal-abc",
        "previous_stage": "qualification",
        "new_stage": "negotiation"
    }
}
```

#### POST /agent/reject
Reject a pending tool execution.

**Request**:
```json
{
    "approval_id": "apr-456",
    "actor_id": "approver-789",
    "reason": "Need more information before proceeding"
}
```

#### GET /agent/approvals
List pending approvals.

**Query Parameters**:
- `actor_id`: Filter by requesting actor
- `status`: Filter by status (pending, claimed, approved, rejected)
- `limit`: Max results (default: 50)

### 7.2 Backend API - Deal Lifecycle

**Base URL**: `http://localhost:8090`

#### GET /api/deals
```json
{
    "deals": [
        {
            "id": "deal-123",
            "company_name": "Acme Corp",
            "stage": "qualification",
            "value": 50000,
            "probability": 0.6,
            "created_at": "2026-01-15T08:00:00Z",
            "updated_at": "2026-01-25T14:30:00Z"
        }
    ],
    "total": 42
}
```

#### POST /api/deals/{id}/transition
```json
{
    "new_stage": "negotiation",
    "note": "Customer requested proposal"
}
```

---

## 8. LangGraph Agent Architecture

### 8.1 Graph Definition

**File**: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`

```python
class LangGraphAgent:
    """LangGraph-based agent with HITL approval workflow."""

    def build_graph(self) -> CompiledGraph:
        builder = StateGraph(GraphState)

        # Define nodes
        builder.add_node("chat", self._chat_node)
        builder.add_node("tool_call", self._tool_call_node)
        builder.add_node("approval_gate", self._approval_gate_node)
        builder.add_node("execute_approved_tools", self._execute_approved_node)

        # Define edges
        builder.set_entry_point("chat")
        builder.add_conditional_edges("chat", self._route_after_chat)
        builder.add_edge("tool_call", "chat")
        builder.add_edge("approval_gate", self._route_after_approval)
        builder.add_edge("execute_approved_tools", "chat")

        # Checkpointer for state persistence
        checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)

        return builder.compile(
            checkpointer=checkpointer,
            interrupt_before=["approval_gate"]
        )
```

### 8.2 State Schema

**File**: `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/graph.py`

```python
class GraphState(TypedDict):
    """Master state container for LangGraph."""
    messages: Annotated[list, add_messages]  # Conversation history
    long_term_memory: Optional[str]           # RAG context
    pending_tool_calls: List[PendingToolCall] # HITL queue
    approval_status: Literal["pending", "approved", "rejected"]
    actor_id: str                             # Requesting user
    metadata: Dict[str, Any]                  # Tracing metadata

class PendingToolCall(TypedDict):
    """Individual pending tool execution."""
    tool_name: str
    tool_args: Dict[str, Any]
    tool_call_id: str
    approval_id: Optional[str]
```

### 8.3 Agent Flow Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH FLOW                              │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│   User Message                                                     │
│        │                                                           │
│        ▼                                                           │
│   ┌─────────┐                                                      │
│   │  CHAT   │◀──────────────────────────────────────┐              │
│   │  Node   │                                        │              │
│   └────┬────┘                                        │              │
│        │                                             │              │
│        ▼                                             │              │
│   ┌─────────────────────┐                           │              │
│   │   Route Decision    │                           │              │
│   │ (requires approval?)│                           │              │
│   └─────────┬───────────┘                           │              │
│             │                                        │              │
│      ┌──────┴──────┐                                │              │
│      │             │                                │              │
│      ▼             ▼                                │              │
│   No HITL       HITL Required                       │              │
│      │             │                                │              │
│      ▼             ▼                                │              │
│ ┌──────────┐  ┌─────────────┐                      │              │
│ │TOOL_CALL │  │APPROVAL_GATE│────────┐             │              │
│ │  Node    │  │    Node     │        │             │              │
│ └────┬─────┘  └─────────────┘        │             │              │
│      │              │                │             │              │
│      │         interrupt()           │             │              │
│      │              │                │             │              │
│      │              ▼                │             │              │
│      │        Wait for Human         │             │              │
│      │              │                │             │              │
│      │        ┌─────┴─────┐          │             │              │
│      │        │           │          │             │              │
│      │     Approve     Reject        │             │              │
│      │        │           │          │             │              │
│      │        ▼           ▼          │             │              │
│      │   ┌─────────┐  Return to      │             │              │
│      │   │EXECUTE  │  CHAT with      │             │              │
│      │   │APPROVED │  rejection      │             │              │
│      │   │ Node    │  message────────┼─────────────┘              │
│      │   └────┬────┘                 │                            │
│      │        │                      │                            │
│      └────────┴──────────────────────┘                            │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

### 8.4 Available Tools

**File**: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/__init__.py`

| Tool | HITL Required | Description |
|------|---------------|-------------|
| `duckduckgo_search_tool` | No | Web search via DuckDuckGo |
| `get_deal` | No | Retrieve deal information |
| `search_deals` | No | Search deals by criteria |
| `transition_deal` | **Yes** | Transition deal to new stage |

### 8.5 HITL Tool Detection

```python
# apps/agent-api/app/schemas/agent.py
HITL_TOOLS = {"transition_deal"}

def requires_approval(tool_name: str) -> bool:
    """Check if tool requires HITL approval."""
    return tool_name in HITL_TOOLS
```

---

## 9. Authentication & Security

### 9.1 JWT Authentication

**File**: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/security/agent_auth.py`

```python
# Configuration
JWT_SECRET_KEY: str       # From environment
JWT_ALGORITHM: str = "HS256"
JWT_AUDIENCE: str         # Expected audience claim
JWT_ISSUER: str           # Expected issuer claim

# Key Functions
def create_agent_token(user_id: str, role: str, email: str) -> str:
    """Generate JWT with claims."""

def verify_agent_token(token: str) -> AgentUser:
    """Validate JWT and return user."""

# FastAPI Dependencies
async def get_agent_user(request: Request) -> AgentUser:
    """Extract and validate user from Authorization header."""

async def require_approve_role(user: AgentUser) -> AgentUser:
    """Ensure user has APPROVE role or higher."""
```

### 9.2 Role Hierarchy

```python
ROLE_HIERARCHY = {
    "admin": 100,      # Full access
    "approver": 75,    # Can approve HITL requests
    "operator": 50,    # Standard operations
    "viewer": 25       # Read-only
}

def has_role(user: AgentUser, required_role: str) -> bool:
    """Check if user has required role level."""
    return ROLE_HIERARCHY.get(user.role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
```

### 9.3 Rate Limiting

```python
# apps/agent-api/app/main.py
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

RATE_LIMITS = {
    "root": "1000 per day, 200 per hour",
    "health": "600 per minute",
    "chat": "100 per minute",
    "messages": "200 per minute",
    "login": "5 per minute"
}
```

---

## 10. Frontend Architecture

### 10.1 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Next.js | 15.x |
| Language | TypeScript | 5.7.2 |
| Styling | Tailwind CSS | 4.0 |
| UI Components | Radix UI | Latest |
| Icons | Tabler Icons | Latest |
| Forms | React Hook Form + Zod | Latest |
| Tables | TanStack React Table | Latest |
| Charts | Recharts | Latest |
| Data Fetching | TanStack React Query | Latest |
| Testing | Vitest + Playwright | Latest |

### 10.2 Directory Structure

```
apps/dashboard/src/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page (redirect)
│   ├── globals.css              # Global styles
│   ├── actions/
│   │   └── page.tsx             # Actions management
│   ├── agent/
│   │   └── page.tsx             # Agent activity
│   ├── chat/
│   │   └── page.tsx             # Chat interface
│   ├── deals/
│   │   ├── page.tsx             # Deals list
│   │   └── [id]/page.tsx        # Deal detail
│   ├── hq/
│   │   └── page.tsx             # HQ overview
│   ├── quarantine/
│   │   └── page.tsx             # Quarantine items
│   ├── onboarding/
│   │   └── page.tsx             # Setup flow
│   └── api/                     # API routes
│       └── [...]/route.ts
├── components/
│   ├── ui/                      # Base UI components
│   ├── layout/                  # Layout components
│   └── features/                # Feature-specific
├── constants/
│   └── mock-data.ts             # Development mocks
└── hooks/
    ├── use-deals.ts
    ├── use-agent.ts
    └── use-approvals.ts
```

### 10.3 Environment Configuration

```dockerfile
# Build-time environment variables
ARG NEXT_PUBLIC_API_URL=http://localhost:8091
ARG NEXT_PUBLIC_AGENT_API_URL=http://localhost:8095
```

---

## 11. Configuration Management

### 11.1 Agent API Configuration

**File**: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/config.py`

```python
class Settings(BaseSettings):
    """Environment-aware configuration."""

    # Application
    APP_ENV: str = "development"
    PROJECT_NAME: str = "Web Assistant"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_POOL_SIZE: int = 5

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = 30

    # LLM
    OPENAI_API_KEY: str
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    DEFAULT_LLM_TEMPERATURE: float = 0.2

    # HITL
    ENABLE_HITL: bool = True
    HITL_APPROVAL_TIMEOUT_SECONDS: int = 3600
    ENABLE_AUDIT_LOG: bool = True

    # Memory
    DISABLE_LONG_TERM_MEMORY: bool = False

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "1000 per day,200 per hour"
    RATE_LIMIT_CHAT: str = "100 per minute"

    class Config:
        env_file = ".env"
```

### 11.2 Environment Detection

```python
def get_environment() -> str:
    """Detect runtime environment."""
    env = os.getenv("APP_ENV", "development").lower()
    return {
        "production": "PRODUCTION",
        "staging": "STAGING",
        "test": "TEST"
    }.get(env, "DEVELOPMENT")
```

### 11.3 .env File Priority

```
1. .env.{environment}.local (highest priority)
2. .env.{environment}
3. .env.local
4. .env (lowest priority)
```

---

## 12. Data Models

### 12.1 Agent API Models

**Approval Model**:
```python
class Approval(BaseModel):
    id: str
    thread_id: str
    checkpoint_id: Optional[str]
    tool_name: str
    tool_args: str  # JSON-serialized
    actor_id: str
    status: Literal["pending", "claimed", "approved", "rejected", "expired"]
    idempotency_key: str
    claimed_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    rejection_reason: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
```

**ToolExecution Model**:
```python
class ToolExecution(BaseModel):
    id: str
    approval_id: Optional[str]
    idempotency_key: str
    tool_name: str
    tool_args: str
    status: Literal["claimed", "executing", "completed", "failed"]
    result: Optional[str]
    success: bool
    error_message: Optional[str]
    claimed_at: datetime
    executed_at: Optional[datetime]
    completed_at: Optional[datetime]
```

**AuditLog Model**:
```python
class AuditLog(BaseModel):
    id: str
    actor_id: str
    event_type: str  # approval_created, approval_approved, tool_execution_*, etc.
    thread_id: Optional[str]
    approval_id: Optional[str]
    tool_execution_id: Optional[str]
    payload: Dict[str, Any]
    created_at: datetime
```

### 12.2 Request/Response Schemas

**AgentInvokeRequest**:
```python
class AgentInvokeRequest(BaseModel):
    actor_id: str
    message: str = Field(..., min_length=1, max_length=10000)
    thread_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

**AgentInvokeResponse**:
```python
class AgentInvokeResponse(BaseModel):
    thread_id: str
    status: Literal["completed", "awaiting_approval", "error"]
    content: Optional[str]
    pending_approval: Optional[PendingApproval]
    actions_taken: List[ActionTaken]
    error: Optional[str]
```

**PendingApproval**:
```python
class PendingApproval(BaseModel):
    approval_id: str
    tool: str
    args: Dict[str, Any]
    permission_tier: Literal["READ", "WRITE", "CRITICAL"]
    requested_by: str
    requested_at: datetime
```

---

## 13. Reliability & Idempotency

### 13.1 Idempotency Key Generation

**File**: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/idempotency.py`

```python
def tool_idempotency_key(thread_id: str, tool_name: str, tool_args: Dict) -> str:
    """
    Generate deterministic idempotency key.

    Format: "{thread_id}:{tool_name}:{sha256_hash}"

    Properties:
    - Restart-safe: Same inputs → same key
    - Collision-resistant: SHA-256 hash
    - Debuggable: Includes tool name prefix
    """
    canonical_json = json.dumps(tool_args, sort_keys=True, separators=(',', ':'))
    args_hash = hashlib.sha256(canonical_json.encode()).hexdigest()[:16]
    return f"{thread_id}:{tool_name}:{args_hash}"
```

### 13.2 Claim-First Execution Pattern

```
1. BEFORE executing tool:
   └── INSERT INTO tool_executions (status='claimed', idempotency_key=...)

2. EXECUTE tool:
   └── UPDATE tool_executions SET status='executing', executed_at=NOW()

3. AFTER execution:
   └── UPDATE tool_executions SET status='completed', result=..., completed_at=NOW()

4. ON RESTART:
   └── SELECT * FROM tool_executions WHERE idempotency_key = ?
       └── If exists and completed → Skip (return cached result)
       └── If exists and claimed → Resume execution
       └── If not exists → Execute normally
```

### 13.3 Stale Claim Recovery

```python
def reclaim_stale_claims(stale_threshold_minutes: int = 5) -> int:
    """
    Recover approvals stuck in 'claimed' status from crashed workers.

    Called before each approval operation to ensure:
    - No approvals remain stuck indefinitely
    - Crashed workers don't block the queue
    """
    return db.execute("""
        UPDATE approvals
        SET status = 'pending', claimed_at = NULL
        WHERE status = 'claimed'
          AND claimed_at < (NOW() - INTERVAL '{} minutes')
    """.format(stale_threshold_minutes))
```

### 13.4 Approval Timeout

```python
# Configuration
HITL_APPROVAL_TIMEOUT_SECONDS = 3600  # 1 hour default

# Periodic cleanup
def cleanup_expired_approvals() -> int:
    """Mark timed-out approvals as expired."""
    return db.execute("""
        UPDATE approvals
        SET status = 'expired'
        WHERE status = 'pending'
          AND expires_at IS NOT NULL
          AND expires_at < NOW()
    """)
```

---

## 14. Observability Stack

### 14.1 Prometheus (Port 9090)

**Configuration**: `/home/zaks/zakops-agent-api/ops/observability/prometheus/prometheus.yml`

**Scrape Targets**:
- Agent API: `agent-api:8000/metrics`
- Backend API: `backend:8090/metrics`
- cAdvisor: `cadvisor:8080/metrics`

### 14.2 Grafana (Port 3002)

**Default Credentials**: admin/admin

**Dashboards**:
- API Performance
- Agent Activity
- Container Resources
- Database Metrics

### 14.3 Loki (Port 3100)

**Configuration**: `/home/zaks/zakops-agent-api/ops/observability/loki/loki-config.yml`

**Log Sources**:
- Docker container logs via Promtail
- Application structured logs

### 14.4 Promtail

**Configuration**: `/home/zaks/zakops-agent-api/ops/observability/promtail/promtail-config.yml`

**Collection**:
- Docker socket for container logs
- Container label-based filtering

---

## 15. Key File Reference

| Component | File Path | Purpose |
|-----------|-----------|---------|
| Agent Graph | `apps/agent-api/app/core/langgraph/graph.py` | LangGraph state machine |
| Graph State | `apps/agent-api/app/schemas/graph.py` | State definition |
| Main App | `apps/agent-api/app/main.py` | FastAPI entry point |
| Approval Model | `apps/agent-api/app/models/approval.py` | HITL data model |
| Agent Endpoints | `apps/agent-api/app/api/v1/agent.py` | MDv2 API routes |
| Tools | `apps/agent-api/app/core/langgraph/tools/__init__.py` | Agent tools |
| Config | `apps/agent-api/app/core/config.py` | Environment config |
| JWT Auth | `apps/agent-api/app/core/security/agent_auth.py` | Authentication |
| Agent Schema | `apps/agent-api/app/schemas/agent.py` | Request/response |
| HITL Migration | `apps/agent-api/migrations/001_approvals.sql` | HITL tables |
| Backend Main | `apps/backend/src/api/deal_lifecycle/main.py` | Deal lifecycle API |
| Foundation SQL | `apps/backend/db/migrations/001_foundation_tables.sql` | Core tables |
| Dashboard | `apps/dashboard/package.json` | Frontend config |
| Docker Compose | `deployments/docker/docker-compose.yml` | Orchestration |
| Environment | `apps/agent-api/.env.example` | Config template |

---

## Document Metadata

| Field | Value |
|-------|-------|
| Created | 2026-01-26 |
| Author | Claude Opus 4.5 |
| Version | 2.0 |
| Status | Complete |
| Location | `/home/zaks/bookkeeping/docs/ZAKOPS_ARCHITECTURE_DESIGN.md` |
| Related | `LEGACY_DECOMMISSION_REPORT_20260126.md`, `DATABASE_FORENSICS_20260126.md`, `RAG_ARCHITECTURE_FORENSICS_20260125.md` |

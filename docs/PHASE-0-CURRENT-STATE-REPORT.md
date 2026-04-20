# PHASE 0: Current State Report
## ZakOps World-Class Execution Platform - Infrastructure Inventory

**Generated**: 2026-01-17
**Purpose**: Read-only verification before implementing Master Mission v2

---

## Executive Summary

| Component | Status | Key Finding |
|-----------|--------|-------------|
| **UI Pages** | ✅ Complete | 6 routes, Next.js App Router, shadcn/ui |
| **Backend APIs** | ✅ Complete | 60+ endpoints on 8090, 18 on 9200 |
| **Database** | ✅ Complete | PostgreSQL + 4 SQLite databases |
| **Agent Bridge** | ⚠️ Partial | MCP server ready, **NO deployed agent** |
| **Streaming** | ⚠️ Partial | SSE/WebSocket exist, **no reconnect logic** |
| **Authentication** | ❌ Missing | No auth on main APIs (except Bridge) |

**Critical Gap**: No LangSmith Agent deployed - the system has MCP tools but no `assistant_id`.

---

## 1. UI Pages Inventory

### Routes (Next.js App Router)

| Route | File | Purpose |
|-------|------|---------|
| `/` | `src/app/page.tsx` | Redirects to `/dashboard` |
| `/dashboard` | `src/app/dashboard/page.tsx` | Pipeline funnel, deals, actions, quarantine summary |
| `/deals` | `src/app/deals/page.tsx` | Deal list with filtering, sorting, bulk ops |
| `/deals/[id]` | `src/app/deals/[id]/page.tsx` | Deal workspace (Overview, Actions, Pipeline, Materials, Case File, Events tabs) |
| `/actions` | `src/app/actions/page.tsx` | Actions Command Center with status filtering |
| `/quarantine` | `src/app/quarantine/page.tsx` | Email quarantine queue with approval/rejection |
| `/chat` | `src/app/chat/page.tsx` | RAG-grounded chat with deal context |

### Component Structure (~95 components)

```
/src/components/
├── ui/           # Shadcn/Radix primitives (95+ files)
├── actions/      # action-card.tsx, action-input-form.tsx
├── forms/        # Wrapped form fields (10+ components)
├── layout/       # app-sidebar, header, providers, page-container
├── kbar/         # Command palette (Cmd+K)
└── modal/        # Alert dialogs
```

### State Management Approach

| Pattern | Usage |
|---------|-------|
| **React Context** | Theme management only |
| **useState hooks** | All page-level state |
| **URL params** | Filters persisted in URL |
| **localStorage** | Chat history, user preferences |
| **No Redux/Zustand** | Direct fetch with manual state |
| **No React Query** | Manual caching, polling (3s intervals) |

### Existing Type Definitions

**Location**: `/home/zaks/zakops-dashboard/src/types/api.ts`

Already defined:
- `DealStage` - 9 stages (inbound → archived)
- `DealStatus` - 4 statuses
- `ActionStatus` - 8 statuses (PENDING_APPROVAL, QUEUED, READY, RUNNING, etc.)
- `RiskLevel` - low, medium, high
- `QuarantineClassification` - DEAL_SIGNAL, UNCERTAIN, JUNK
- Full Deal, Action, QuarantineItem, SenderProfile types

---

## 2. Backend API Inventory

### API Servers

| Server | Port | Framework | Auth |
|--------|------|-----------|------|
| Deal Lifecycle API | 8090 | FastAPI | ❌ None |
| Orchestration API | 9200 | FastAPI + asyncpg | ❌ None |
| Agent Bridge | 9100 | FastMCP | ✅ Bearer token |

### Key Endpoints (Deal Lifecycle API - 8090)

**Deals (10 endpoints)**:
- `GET /api/deals` - List with filters (stage, status, broker, age)
- `GET /api/deals/{deal_id}` - Full deal with enrichments
- `POST /api/deals` - Create deal
- `PATCH /api/deals/{deal_id}` - Update deal
- `POST /api/deals/{deal_id}/transition` - Stage transition with approval
- `POST /api/deals/{deal_id}/note` - Add operator note
- `GET /api/deals/{deal_id}/events` - Event history
- `POST /api/deals/{deal_id}/archive` - Soft delete
- `POST /api/deals/{deal_id}/restore` - Unarchive

**Actions (15 endpoints)**:
- `GET /api/actions` - List with filters
- `POST /api/actions` - Create action (idempotency supported)
- `GET /api/actions/{action_id}` - Get action details
- `POST /api/actions/{action_id}/approve` - Approve for execution
- `POST /api/actions/{action_id}/execute` - Execute action
- `POST /api/actions/{action_id}/cancel` - Cancel action
- `POST /api/actions/{action_id}/retry` - Retry failed action
- `GET /api/actions/capabilities` - List all capabilities
- `POST /api/actions/plan` - AI-driven action planning
- `GET /api/actions/metrics` - Execution metrics

**Quarantine (8 endpoints)**:
- `GET /api/quarantine` - List pending items
- `GET /api/actions/quarantine/{id}/preview` - Local preview
- `POST /api/actions/quarantine/{id}/approve` - Approve → create deal
- `POST /api/actions/quarantine/{id}/reject` - Reject item

**Chat (5 endpoints)**:
- `POST /api/chat` - SSE streaming chat
- `POST /api/chat/complete` - Non-streaming chat
- `POST /api/chat/execute-proposal` - Execute AI proposal
- `GET /api/chat/session/{session_id}` - Get session history
- `GET /api/chat/llm-health` - LLM backend health

### Request/Response Shapes

All endpoints return JSON. Common patterns:
- List endpoints: `{ count: number, items: T[] }`
- Create endpoints: `{ success: boolean, created_new: boolean, item: T }`
- Action endpoints: `{ success: boolean, action: Action }`
- Error responses: `{ detail: string }` with HTTP status codes

---

## 3. Database Schema Inventory

### PostgreSQL (zakops database)

**Connection**: `postgresql://dealengine:changeme@localhost:5435/zakops`

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `zakops.deals` | Deal records | deal_id, stage, status, JSONB metadata |
| `zakops.deal_aliases` | Name matching | alias_normalized (unique) |
| `zakops.deal_events` | Audit trail | event_type, source, actor, details |
| `zakops.actions` | Action queue | action_id, status, idempotency_key |
| `zakops.quarantine_items` | Email triage | classification, urgency, confidence |
| `zakops.email_ingestion_state` | Email tracking | message_id, is_processed |
| `zakops.sender_profiles` | Sender metadata | is_broker, quality_rating |
| `zakops.deferred_actions` | Scheduled tasks | action_spec, scheduled_for |

**Views**:
- `v_active_deals` - Deals with computed fields
- `v_pipeline_summary` - Stage counts
- `v_pending_actions` - Actions awaiting approval
- `v_quarantine_dashboard` - Quarantine with sender info

**Functions**:
- `next_deal_id()` - Generates DEAL-YYYY-NNN
- `next_action_id()` - Generates ACT-YYYYMMDD-hash
- `record_deal_event()` - Creates audit records

### SQLite Databases

| Database | Size | Purpose |
|----------|------|---------|
| `ingest_state.db` | 2.5M | Email ingestion state, chat sessions |
| `sender_history.db` | 116K | Sender backfill tracking |
| `email_triage_state.db` | 56K | Triage state |
| `email_backfill_state.db` | 32K | Backfill operations |

---

## 4. Agent Bridge Inventory

### Current Implementation

**Location**: `/home/zaks/scripts/agent_bridge/`

**Framework**: FastMCP (MCP Protocol Server)
**Transport**: SSE at `/sse`
**Health**: `/health` (no auth)

### Tool Definitions (12 tools)

| Tool | Risk | Description |
|------|------|-------------|
| `zakops_list_deals` | Low | List deals with filters |
| `zakops_get_deal` | Medium | Get deal + filesystem enrichments |
| `zakops_update_deal_profile` | **High** | Atomic write to deal_profile.json |
| `zakops_write_deal_artifact` | **High** | Write files to deal folders |
| `zakops_list_deal_artifacts` | Low | List files in deal folder |
| `zakops_list_quarantine` | Low | List quarantine items |
| `zakops_create_action` | **High** | Create approval-gated actions |
| `zakops_get_action` | Low | Get action status |
| `zakops_list_actions` | Low | List actions with filters |
| `zakops_approve_quarantine` | **High** | Approve → create deal |
| `rag_query_local` | Low | RAG search |
| `rag_reindex_deal` | Medium | Trigger reindex |

### ⚠️ CRITICAL: No Deployed Agent

**Finding**: No `assistant_id` configured anywhere in the codebase.

- No LangSmith agent deployment metadata
- No agent credentials or integration tokens
- Bridge is MCP-ready but not integrated with LangSmith Agent Builder
- Cloudflare tunnel template exists but not deployed

---

## 5. Streaming Implementation Inventory

### Server-Side Streaming

| Endpoint | Transport | Purpose |
|----------|-----------|---------|
| `POST /api/chat` | SSE | Chat token streaming |
| `ws://localhost:9200/ws/updates` | WebSocket | Real-time broadcasts |

**SSE Event Types**:
- `progress` - Workflow phase tracking (1-4)
- `token` - Individual response tokens
- `evidence` - RAG results, case file sections
- `done` - Final response with citations, proposals
- `error` - Error events

### Client-Side Streaming

**Location**: `/home/zaks/zakops-dashboard/src/lib/api.ts`

**Function**: `streamChatMessage()` - Async generator
- Uses `fetch` with `response.body.getReader()`
- Manual SSE parsing with text decoder
- Token batching (100ms window)
- AbortController for cancellation

### ⚠️ CRITICAL: No Reconnection Logic

| Component | Reconnect | Backoff |
|-----------|-----------|---------|
| WebSocket | ❌ No | ❌ No |
| Chat Stream | ❌ No (manual abort only) | ❌ No |

**Code comment from api-client.ts**:
> "This is a simple implementation. For production, consider using a library like `reconnecting-websocket` or implementing reconnection logic."

### Authentication on Streams

| Stream | Auth Method |
|--------|-------------|
| SSE `/api/chat` | ❌ None (same as HTTP) |
| WebSocket `/ws/updates` | ❌ None |

---

## 6. Critical Questions Answered

| Question | Answer |
|----------|--------|
| **What is the deployed agent's assistant_id?** | ❌ **None deployed** |
| **How is the agent currently invoked?** | Ad-hoc MCP calls, no thread/run model |
| **How does SSE auth work today?** | No auth - permissive CORS |
| **Are there canonical lifecycle enums?** | ✅ Yes in `/src/types/api.ts` |
| **Is run history persisted locally?** | Partial - chat sessions in SQLite |
| **What's the current onboarding flow?** | ❌ None - direct to dashboard |

---

## 7. Gap Analysis vs Target Architecture

### Phase 1: Execution Model Contracts

| Requirement | Current State | Gap |
|-------------|--------------|-----|
| Deal stage transitions | ✅ Exists (deal_lifecycle_api.py) | Need client-side enforcement |
| Action status machine | ✅ Exists | Need UI alignment |
| Quarantine states | ✅ Exists | Minor - need deferred state |
| Tool risk classification | ⚠️ Implicit | Need explicit manifest |
| Agent event types | ❌ Missing | Need full contract |

### Phase 2: Agent Invocation

| Requirement | Current State | Gap |
|-------------|--------------|-----|
| Thread/Run model | ❌ Ad-hoc MCP | **Major refactor needed** |
| Idempotency keys | ⚠️ Partial (action-level) | Need run-level |
| Run persistence | ❌ Missing | Need agent_runs table |
| Tool call tracking | ❌ Missing | Need agent_tool_calls table |
| Approval workflow | ✅ Exists (actions) | Need tool-level integration |

### Phase 3: Real-Time Feed

| Requirement | Current State | Gap |
|-------------|--------------|-----|
| SSE proxy with auth | ❌ No auth | Need API route with session |
| Event ID passthrough | ❌ Not implemented | Need for resume |
| Reconnection logic | ❌ Missing | Need exponential backoff |
| Query invalidation | ❌ Manual refresh | Need React Query integration |

### Phase 5: Agent Capability Manifest

| Requirement | Current State | Gap |
|-------------|--------------|-----|
| System prompt contract | ❌ Missing | Need full operating contract |
| Tool gateway enforcement | ⚠️ Partial (path safety) | Need risk-level enforcement |
| Event alignment | ❌ Missing | Need shared event types |

---

## 8. Risk Assessment

### High Priority Risks

1. **No Agent Deployment** - Cannot test agent integration without assistant_id
2. **No Authentication** - All APIs open except Agent Bridge
3. **No Reconnection** - Dropped streams leave stale UI
4. **Ad-hoc Invocation** - No thread context, no run history

### Medium Priority Risks

1. **No React Query** - Manual caching prone to stale data
2. **SQLite for Chat** - Not scalable for multi-process
3. **In-memory WebSocket Manager** - Single-process only

### Low Priority Risks

1. **Type drift** - Backend/frontend types may diverge
2. **No API versioning** - Breaking changes hard to manage

---

## 9. Recommended Delta Plan

### Immediate Actions (Before Code Changes)

1. **Deploy LangSmith Agent** - Get `assistant_id` for testing
2. **Configure Cloudflare Tunnel** - Enable cloud agent access
3. **Add API Authentication** - At minimum, API key on Deal API

### Phase 1 Delta (Contracts)

- **Preserve**: Existing type definitions in `/src/types/api.ts`
- **Add**: `DEAL_TRANSITIONS` map, agent event types
- **Align**: Backend status enums with frontend types

### Phase 2 Delta (Agent Integration)

- **Major**: Implement thread/run model in AgentBridge
- **Add**: PostgreSQL tables for `agent_threads`, `agent_runs`, `agent_tool_calls`
- **Modify**: MCP tools to record run context

### Phase 3 Delta (Real-Time)

- **Add**: Next.js API route for SSE proxy with session auth
- **Add**: `useRealtimeEvents` hook with reconnection
- **Add**: React Query provider and cache invalidation

### Phase 5 Delta (Agent Contract)

- **Create**: Agent operating contract as system prompt
- **Add**: Tool gateway with risk enforcement
- **Align**: Event types between agent and UI

---

## 10. Files Referenced

**UI**:
- `/home/zaks/zakops-dashboard/src/app/` - All page routes
- `/home/zaks/zakops-dashboard/src/types/api.ts` - Type definitions
- `/home/zaks/zakops-dashboard/src/lib/api.ts` - API client

**Backend**:
- `/home/zaks/scripts/deal_lifecycle_api.py` - Main API (3,861 lines)
- `/home/zaks/scripts/api/main.py` - Orchestration API (909 lines)
- `/home/zaks/scripts/agent_bridge/mcp_server.py` - Agent Bridge

**Database**:
- `/home/zaks/scripts/db/schema.sql` - PostgreSQL schema
- `/home/zaks/DataRoom/.deal-registry/*.db` - SQLite databases

**Streaming**:
- `/home/zaks/scripts/chat_orchestrator.py` - SSE generator
- `/home/zaks/zakops-dashboard/src/lib/api-client.ts` - WebSocket hook

---

*End of Phase 0 Report*

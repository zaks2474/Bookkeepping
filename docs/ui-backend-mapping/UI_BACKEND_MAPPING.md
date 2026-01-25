# ZakOps UI-Backend Mapping

**Generated**: 2026-01-25
**Version**: 1.0.0

## Overview

This document maps each UI feature to its corresponding backend API endpoints, documenting the complete data flow from user action to API call.

---

## Backend Services

| Service | Port | Base URL | Status |
|---------|------|----------|--------|
| Deal API | 8090 | `http://localhost:8090` | UP |
| RAG API | 8052 | `http://localhost:8052` | DOWN (404 on /health) |
| MCP Server | 9100 | `http://localhost:9100` | DOWN (404 on /health) |

---

## Feature Mappings

### 1. Dashboard (`/dashboard`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Pipeline Funnel | `GET /api/deals` | GET | `?status=active` | `Deal[]` |
| Deal Count by Stage | `GET /api/deals` | GET | `?status=active` | Computed from `Deal[]` |
| Approval Queue | `GET /api/kinetic/actions` | GET | `?status=PENDING_APPROVAL` | `KineticAction[]` |
| Agent Activity Widget | `GET /api/agent/activity` | GET | `?limit=100` | `AgentActivityResponse` |
| Today's Tasks | `GET /api/kinetic/actions` | GET | `?scheduled_for=today` | `KineticAction[]` |

**API Client Functions**:
- `getDeals({ status: 'active' })`
- `getKineticActions({ status: 'PENDING_APPROVAL' })`
- `fetch('/api/agent/activity?limit=100')`

---

### 2. Deals List (`/deals`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Deal Table/Board | `GET /api/deals` | GET | Query params for filters | `Deal[]` |
| Create Deal | `POST /api/deals` | POST | `CreateDealRequest` | `Deal` |
| Bulk Archive | `POST /api/deals/bulk/archive` | POST | `{ deal_ids: string[] }` | `{ success: boolean }` |
| Bulk Delete | `POST /api/deals/bulk/delete` | POST | `{ deal_ids: string[] }` | `{ success: boolean }` |

**API Client Functions**:
- `getDeals(filters)`
- `createDeal(data)`
- `bulkArchiveDeals(dealIds)`
- `bulkDeleteDeals(dealIds)`

**Filter Parameters**:
- `status`: 'active' | 'archived' | 'all'
- `stage`: DealStage
- `search`: string (company name search)
- `sort`: 'created_at' | 'updated_at' | 'company_name'
- `order`: 'asc' | 'desc'

---

### 3. Deal Detail (`/deals/[id]`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Deal Info | `GET /api/deals/{id}` | GET | - | `DealDetail` |
| Deal Events | `GET /api/deals/{id}/events` | GET | - | `DealEvent[]` |
| Deal Actions | `GET /api/kinetic/actions` | GET | `?deal_id={id}` | `KineticAction[]` |
| Capabilities | `GET /api/capabilities` | GET | - | `Capability[]` |
| Update Deal | `PATCH /api/deals/{id}` | PATCH | `UpdateDealRequest` | `Deal` |
| Delete Deal | `DELETE /api/deals/{id}` | DELETE | - | `{ success: boolean }` |
| Archive Deal | `POST /api/deals/{id}/archive` | POST | - | `Deal` |
| Change Stage | `POST /api/deals/{id}/stage` | POST | `{ stage: DealStage }` | `Deal` |
| Add Note | `POST /api/deals/{id}/notes` | POST | `{ content: string }` | `Note` |

**Kinetic Action Operations** (on deal detail):
| Action | API Endpoint | Method |
|--------|--------------|--------|
| Approve | `POST /api/kinetic/actions/{id}/approve` | POST |
| Run | `POST /api/kinetic/actions/{id}/run` | POST |
| Cancel | `POST /api/kinetic/actions/{id}/cancel` | POST |
| Retry | `POST /api/kinetic/actions/{id}/retry` | POST |
| Reject | `POST /api/kinetic/actions/{id}/reject` | POST |

**API Client Functions**:
- `getDeal(id)`
- `getDealEvents(id)`
- `getKineticActions({ deal_id: id })`
- `getCapabilities()`
- `updateDeal(id, data)`
- `deleteDeal(id)`
- `archiveDeal(id)`
- `transitionDealStage(id, stage)`
- `addDealNote(id, content)`
- `approveAction(id)`, `runAction(id)`, `cancelAction(id)`, `retryAction(id)`, `rejectAction(id)`

---

### 4. Actions Command Center (`/actions`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Actions List | `GET /api/kinetic/actions` | GET | Query params | `KineticAction[]` |
| Action Detail | `GET /api/kinetic/actions/{id}` | GET | - | `KineticAction` |
| Create Action | `POST /api/kinetic/actions` | POST | `CreateActionRequest` | `KineticAction` |
| Approve | `POST /api/kinetic/actions/{id}/approve` | POST | - | `KineticAction` |
| Run | `POST /api/kinetic/actions/{id}/run` | POST | - | `KineticAction` |
| Cancel | `POST /api/kinetic/actions/{id}/cancel` | POST | - | `KineticAction` |
| Retry | `POST /api/kinetic/actions/{id}/retry` | POST | - | `KineticAction` |
| Reject | `POST /api/kinetic/actions/{id}/reject` | POST | - | `KineticAction` |
| Bulk Approve | `POST /api/kinetic/actions/bulk/approve` | POST | `{ action_ids: string[] }` | `{ success: boolean }` |

**Filter Parameters**:
- `status`: ActionStatus
- `deal_id`: string
- `action_type`: string
- `capability_id`: string

**Polling**: 5-second interval for status updates when actions are in PROCESSING state

---

### 5. Agent Activity (`/agent/activity`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Runs List | `GET /api/agent/runs` | GET | Query params | `AgentRun[]` |
| Run Detail | `GET /api/agent/runs/{id}` | GET | - | `AgentRun` |
| Run Events | `GET /api/agent/runs/{id}/events` | GET | - | `AgentEvent[]` |
| Activity Stats | `GET /api/agent/activity` | GET | `?limit=N` | `AgentActivityResponse` |

**API Client Functions**:
- `getAgentRuns(filters)`
- `getAgentRun(id)`
- `getAgentRunEvents(id)`
- `fetch('/api/agent/activity')`

---

### 6. Quarantine (`/quarantine`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Queue List | `GET /api/triage/quarantine` | GET | `?decision=pending` | `QuarantineItem[]` |
| Item Detail | `GET /api/triage/quarantine/{id}` | GET | - | `QuarantineItem` |
| Approve | `POST /api/triage/quarantine/{id}/approve` | POST | `{ deal_id?: string }` | `QuarantineItem` |
| Reject | `POST /api/triage/quarantine/{id}/reject` | POST | `{ reason?: string }` | `QuarantineItem` |

**API Client Functions**:
- `getQuarantineQueue()`
- `getQuarantineItem(id)`
- `approveQuarantineItem(id, dealId?)`
- `rejectQuarantineItem(id, reason?)`

---

### 7. Chat (`/chat`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Send Message | `POST /api/chat/stream` | POST (SSE) | `ChatRequest` | SSE stream |
| Get Sessions | `GET /api/chat/sessions` | GET | - | `ChatSession[]` |
| Create Session | `POST /api/chat/sessions` | POST | `{ title?: string }` | `ChatSession` |
| Delete Session | `DELETE /api/chat/sessions/{id}` | DELETE | - | `{ success: boolean }` |

**SSE Stream Events**:
- `message`: Chat response chunks
- `evidence`: RAG retrieval results
- `proposal`: Action proposals
- `error`: Error events
- `done`: Stream completion

**API Client Functions**:
- `streamChatMessage(message, sessionId, scope, onChunk, onEvidence, onError)`
- `getChatSessions()`
- `createChatSession(title?)`
- `deleteChatSession(id)`

---

### 8. Operator HQ (`/hq`)

| UI Element | API Endpoint | Method | Request | Response |
|------------|--------------|--------|---------|----------|
| Pipeline Stats | `GET /api/deals` | GET | `?status=active` | Computed stats |
| Pending Actions | `GET /api/kinetic/actions` | GET | `?status=PENDING_APPROVAL` | `KineticAction[]` |
| Quarantine Count | `GET /api/triage/quarantine` | GET | `?decision=pending` | `QuarantineItem[]` |
| Agent Activity | `GET /api/agent/activity` | GET | `?limit=100` | `AgentActivityResponse` |

**Computed Metrics**:
- `total_active_deals`: Count of active deals
- `pending_actions`: Count of PENDING_APPROVAL actions
- `quarantine_pending`: Count of pending quarantine items
- `recent_events_24h`: Agent runs in last 24h
- `deals_by_stage`: Deal count per pipeline stage

---

## API Client Architecture

### Location
`/home/zaks/zakops-dashboard/src/lib/api.ts`

### Configuration
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8090';
```

### Validation
All API responses are validated using Zod schemas defined in the api.ts file:
- `DealSchema`, `DealDetailSchema`
- `KineticActionSchema`
- `QuarantineItemSchema`
- `CapabilitySchema`
- `AgentRunSchema`, `AgentEventSchema`

### Error Handling
```typescript
class ApiError extends Error {
  status: number;
  code?: string;
}
```

---

## Data Flow Diagrams

### Deal Lifecycle
```
UI: /deals (Create)
  → POST /api/deals
  → DB: deals table
  → UI: /deals/[id] (View)
  → PATCH /api/deals/{id} (Update)
  → POST /api/deals/{id}/stage (Transition)
  → POST /api/deals/{id}/archive (Archive)
```

### Action Lifecycle
```
UI: /actions (Create)
  → POST /api/kinetic/actions
  → Status: PENDING_APPROVAL
  → UI: Approve button
  → POST /api/kinetic/actions/{id}/approve
  → Status: READY
  → UI: Run button
  → POST /api/kinetic/actions/{id}/run
  → Status: PROCESSING
  → (Backend execution)
  → Status: COMPLETED | FAILED
```

### Chat Flow
```
UI: /chat (Send message)
  → POST /api/chat/stream (SSE)
  → RAG retrieval (port 8052)
  → LLM generation
  → SSE chunks to UI
  → Evidence panel update
  → Optional: Action proposal
```

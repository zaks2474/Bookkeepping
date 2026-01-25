# ZakOps Dashboard UI Inventory

**Generated**: 2026-01-25
**UI Repository**: `/home/zaks/zakops-dashboard`
**Framework**: Next.js 15 (App Router)
**Version**: 0.1.0

## Table of Contents
1. [Routes](#routes)
2. [Key Components](#key-components)
3. [User Actions](#user-actions)
4. [Data Flows](#data-flows)
5. [State Management](#state-management)

---

## Routes

| Route | File | Description | Auth Required |
|-------|------|-------------|---------------|
| `/` | `src/app/page.tsx` | Root redirect to /dashboard | No |
| `/dashboard` | `src/app/dashboard/page.tsx` | Main dashboard with pipeline overview | Yes |
| `/deals` | `src/app/deals/page.tsx` | Deals list (table/board views) | Yes |
| `/deals/[id]` | `src/app/deals/[id]/page.tsx` | Deal detail with tabs | Yes |
| `/actions` | `src/app/actions/page.tsx` | Actions Command Center | Yes |
| `/agent/activity` | `src/app/agent/activity/page.tsx` | Agent activity monitoring | Yes |
| `/quarantine` | `src/app/quarantine/page.tsx` | Email triage queue | Yes |
| `/chat` | `src/app/chat/page.tsx` | Chat interface with RAG | Yes |
| `/hq` | `src/app/hq/page.tsx` | Operator HQ overview | Yes |
| `/onboarding` | `src/app/onboarding/page.tsx` | User onboarding flow | No |
| `/ui-test` | `src/app/ui-test/page.tsx` | UI component testing | Dev only |

---

## Key Components

### Layout Components
| Component | Location | Purpose |
|-----------|----------|---------|
| `RootLayout` | `src/app/layout.tsx` | App shell with sidebar |
| `Sidebar` | `src/components/Sidebar.tsx` | Navigation sidebar |
| `Header` | `src/components/Header.tsx` | Top navigation bar |

### Dashboard Components
| Component | Location | Purpose |
|-----------|----------|---------|
| `PipelineFunnel` | `src/components/dashboard/PipelineFunnel.tsx` | Visual deal pipeline |
| `DealList` | `src/components/dashboard/DealList.tsx` | Compact deal listing |
| `ApprovalQueue` | `src/components/dashboard/ApprovalQueue.tsx` | Pending approvals widget |
| `TodayNextUpStrip` | `src/components/dashboard/TodayNextUpStrip.tsx` | Daily task overview |
| `ExecutionInbox` | `src/components/dashboard/ExecutionInbox.tsx` | Execution status inbox |
| `AgentActivityWidget` | `src/components/agent-activity/AgentActivityWidget.tsx` | Agent activity summary |

### Deal Components
| Component | Location | Purpose |
|-----------|----------|---------|
| `DealCard` | `src/components/deals/DealCard.tsx` | Deal card for board view |
| `DealTable` | `src/components/deals/DealTable.tsx` | Deal table view |
| `DealDetail` | `src/app/deals/[id]/page.tsx` | Full deal detail page |
| `StageSelector` | `src/components/deals/StageSelector.tsx` | Pipeline stage selector |
| `NotesPanel` | `src/components/deals/NotesPanel.tsx` | Deal notes management |

### Actions Components
| Component | Location | Purpose |
|-----------|----------|---------|
| `ActionCard` | `src/components/actions/ActionCard.tsx` | Individual action display |
| `ActionStatusBadge` | `src/components/actions/ActionStatusBadge.tsx` | Status indicator |
| `BulkActionBar` | `src/components/actions/BulkActionBar.tsx` | Bulk operation controls |
| `CreateActionDialog` | `src/components/actions/CreateActionDialog.tsx` | Action creation modal |

### Agent Visibility Layer (PRESERVE)
| Component | Location | Purpose |
|-----------|----------|---------|
| `AgentActivityPage` | `src/app/agent/activity/page.tsx` | Full activity view |
| `AgentRunsTable` | `src/components/agent-activity/AgentRunsTable.tsx` | Runs listing |
| `AgentEventsTimeline` | `src/components/agent-activity/AgentEventsTimeline.tsx` | Events timeline |
| `AgentActivityWidget` | `src/components/agent-activity/AgentActivityWidget.tsx` | Dashboard widget |

### Chat Components
| Component | Location | Purpose |
|-----------|----------|---------|
| `ChatPage` | `src/app/chat/page.tsx` | Main chat interface |
| `MessageList` | `src/components/chat/MessageList.tsx` | Message display |
| `ChatInput` | `src/components/chat/ChatInput.tsx` | User input area |
| `EvidencePanel` | `src/components/chat/EvidencePanel.tsx` | RAG evidence display |
| `DebugPanel` | `src/components/chat/DebugPanel.tsx` | Debug information |

### Quarantine Components
| Component | Location | Purpose |
|-----------|----------|---------|
| `QuarantinePage` | `src/app/quarantine/page.tsx` | Email triage queue |
| `QuarantineCard` | `src/components/quarantine/QuarantineCard.tsx` | Individual email card |
| `PreviewPanel` | `src/components/quarantine/PreviewPanel.tsx` | Email preview |

### Operator HQ Components
| Component | Location | Purpose |
|-----------|----------|---------|
| `OperatorHQ` | `src/components/operator-hq/OperatorHQ.tsx` | HQ dashboard view |
| `StatsCards` | `src/components/operator-hq/StatsCards.tsx` | Key metrics display |

---

## User Actions

### Deal Management
| Action | Route | API Endpoint | Method |
|--------|-------|--------------|--------|
| List deals | `/deals` | `GET /api/deals` | GET |
| View deal | `/deals/[id]` | `GET /api/deals/{id}` | GET |
| Create deal | `/deals` | `POST /api/deals` | POST |
| Update deal | `/deals/[id]` | `PATCH /api/deals/{id}` | PATCH |
| Delete deal | `/deals/[id]` | `DELETE /api/deals/{id}` | DELETE |
| Archive deal | `/deals/[id]` | `POST /api/deals/{id}/archive` | POST |
| Change stage | `/deals/[id]` | `POST /api/deals/{id}/stage` | POST |
| Add note | `/deals/[id]` | `POST /api/deals/{id}/notes` | POST |
| Bulk archive | `/deals` | `POST /api/deals/bulk/archive` | POST |
| Bulk delete | `/deals` | `POST /api/deals/bulk/delete` | POST |

### Kinetic Actions
| Action | Route | API Endpoint | Method |
|--------|-------|--------------|--------|
| List actions | `/actions` | `GET /api/kinetic/actions` | GET |
| Get action | `/actions` | `GET /api/kinetic/actions/{id}` | GET |
| Create action | `/actions` | `POST /api/kinetic/actions` | POST |
| Approve action | `/actions`, `/deals/[id]` | `POST /api/kinetic/actions/{id}/approve` | POST |
| Run action | `/actions`, `/deals/[id]` | `POST /api/kinetic/actions/{id}/run` | POST |
| Cancel action | `/actions`, `/deals/[id]` | `POST /api/kinetic/actions/{id}/cancel` | POST |
| Retry action | `/actions`, `/deals/[id]` | `POST /api/kinetic/actions/{id}/retry` | POST |
| Reject action | `/actions`, `/deals/[id]` | `POST /api/kinetic/actions/{id}/reject` | POST |
| Bulk approve | `/actions` | `POST /api/kinetic/actions/bulk/approve` | POST |

### Quarantine Management
| Action | Route | API Endpoint | Method |
|--------|-------|--------------|--------|
| List queue | `/quarantine` | `GET /api/triage/quarantine` | GET |
| Approve item | `/quarantine` | `POST /api/triage/quarantine/{id}/approve` | POST |
| Reject item | `/quarantine` | `POST /api/triage/quarantine/{id}/reject` | POST |

### Chat & RAG
| Action | Route | API Endpoint | Method |
|--------|-------|--------------|--------|
| Send message | `/chat` | `POST /api/chat/stream` | POST (SSE) |
| Get sessions | `/chat` | `GET /api/chat/sessions` | GET |
| Create session | `/chat` | `POST /api/chat/sessions` | POST |
| Delete session | `/chat` | `DELETE /api/chat/sessions/{id}` | DELETE |

### Agent Activity
| Action | Route | API Endpoint | Method |
|--------|-------|--------------|--------|
| List runs | `/agent/activity` | `GET /api/agent/runs` | GET |
| Get run | `/agent/activity` | `GET /api/agent/runs/{id}` | GET |
| List events | `/agent/activity` | `GET /api/agent/runs/{id}/events` | GET |
| Get activity | `/hq` | `GET /api/agent/activity` | GET |

---

## Data Flows

### Deal Pipeline Flow
```
[Inbound] → [Screening] → [Qualified] → [LOI] → [Diligence] → [Closing] → [Portfolio]
```

### Kinetic Action State Machine
```
[PENDING_APPROVAL] → [READY] → [PROCESSING] → [COMPLETED]
                 ↓         ↓              ↓
            [REJECTED] [CANCELLED]    [FAILED] → [READY] (retry)
```

### Email Triage Flow
```
[Incoming Email] → [Quarantine Queue] → [Human Review] → [Approve/Reject] → [Create Deal or Discard]
```

### Chat Flow
```
[User Input] → [Stream Request] → [SSE Response] → [Evidence Panel] → [Optional Action Proposal]
```

---

## State Management

### Client-Side State
- **React useState/useEffect**: Primary state management
- **localStorage**: Chat session persistence, user preferences
- **URL params**: Filter state (deals, actions)
- **Polling**: Action status updates (5s interval on actions page)

### Server-Side State
- **Deal API** (port 8090): Deals, actions, capabilities, events
- **RAG API** (port 8052): Chat, document search
- **MCP Server** (port 9100): Tool orchestration

### Key State Interfaces
```typescript
// Deal states
type DealStage = 'inbound' | 'screening' | 'qualified' | 'loi' | 'diligence' | 'closing' | 'portfolio';
type DealStatus = 'active' | 'archived' | 'deleted';

// Action states
type ActionStatus = 'PENDING_APPROVAL' | 'QUEUED' | 'READY' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REJECTED';

// Quarantine states
type QuarantineDecision = 'pending' | 'approved' | 'rejected';
```

---

## API Client Location

All API calls are centralized in:
- **File**: `/home/zaks/zakops-dashboard/src/lib/api.ts`
- **Validation**: Zod schemas for all responses
- **Error handling**: Centralized with typed errors
- **Base URL**: Configurable via `NEXT_PUBLIC_API_URL` (default: `http://localhost:8090`)

# ZakOps UI-Backend Gaps and Fix Plan

**Generated**: 2026-01-25
**Priority Levels**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)

---

## Executive Summary

Based on the UI-Backend mapping analysis, the following gaps have been identified:

| Priority | Count | Description |
|----------|-------|-------------|
| P0 | 2 | Backend services down (RAG, MCP) |
| P1 | 0 | No critical UI gaps found |
| P2 | 3 | Minor enhancement opportunities |
| P3 | 2 | Documentation/testing gaps |

**Overall Assessment**: The UI is well-wired to the Deal API backend. The primary gaps are infrastructure-related (RAG and MCP services not responding).

---

## P0 - Critical Gaps

### GAP-001: RAG API Service Not Responding
**Severity**: P0
**Affected Feature**: Chat (`/chat`)
**Symptom**: `GET http://localhost:8052/health` returns 404

**Impact**:
- Chat feature may not function for RAG retrieval
- Evidence panel may show no results
- Document search capabilities unavailable

**Root Cause Analysis**:
- RAG API service may not be running
- Health endpoint may have different path
- Service may be on different port

**Fix Plan**:
1. Verify RAG API service status: `systemctl status rag-api` or check docker
2. Check service logs for errors
3. Verify correct port binding
4. Test alternative health endpoints: `/`, `/api/health`, `/healthz`

**Validation**:
```bash
curl -s http://localhost:8052/health && echo "RAG API OK"
```

---

### GAP-002: MCP Server Not Responding
**Severity**: P0
**Affected Feature**: Tool orchestration
**Symptom**: `GET http://localhost:9100/health` returns 404

**Impact**:
- Tool execution may fail
- Agent capabilities may be limited
- Action execution could be impaired

**Root Cause Analysis**:
- MCP server may not be running
- Service discovery issue
- Network configuration problem

**Fix Plan**:
1. Verify MCP server status
2. Check service configuration
3. Verify port binding and network access

**Validation**:
```bash
curl -s http://localhost:9100/health && echo "MCP Server OK"
```

---

## P2 - Medium Priority Gaps

### GAP-003: Agent Activity Endpoint Inconsistency
**Severity**: P2
**Affected Feature**: Dashboard, HQ (`/dashboard`, `/hq`)
**Symptom**: Using raw `fetch()` instead of API client function

**Details**:
In `/dashboard/page.tsx` and `/hq/page.tsx`, agent activity is fetched using:
```typescript
fetch('/api/agent/activity?limit=100').then(r => r.ok ? r.json() : null).catch(() => null)
```

Instead of a centralized API client function.

**Impact**:
- Inconsistent error handling
- No Zod validation on response
- Code duplication

**Fix Plan**:
1. Add `getAgentActivity()` function to `/src/lib/api.ts`
2. Add Zod schema for `AgentActivityResponse`
3. Update dashboard and HQ pages to use the new function

**Code Change**:
```typescript
// In api.ts
export const AgentActivityResponseSchema = z.object({
  stats: z.object({
    runsCompleted24h: z.number(),
    // ... other fields
  }),
  // ... other fields
});

export async function getAgentActivity(limit: number = 100): Promise<AgentActivityResponse> {
  const response = await fetch(`${API_BASE_URL}/api/agent/activity?limit=${limit}`);
  if (!response.ok) throw new ApiError(response.status, 'Failed to fetch agent activity');
  return AgentActivityResponseSchema.parse(await response.json());
}
```

---

### GAP-004: Missing Error Boundary Components
**Severity**: P2
**Affected Feature**: All pages
**Symptom**: No error boundaries for graceful error handling

**Impact**:
- Unhandled errors may crash entire page
- Poor user experience on API failures
- No recovery mechanism

**Fix Plan**:
1. Create reusable `ErrorBoundary` component
2. Add `error.tsx` files to route directories
3. Implement graceful fallback UI

---

### GAP-005: Loading States Inconsistency
**Severity**: P2
**Affected Feature**: Various pages
**Symptom**: Inconsistent loading state handling

**Details**:
Some pages use skeleton loaders, others use spinners, some show nothing during load.

**Fix Plan**:
1. Standardize on skeleton loader approach
2. Create reusable loading components
3. Add `loading.tsx` files to route directories

---

## P3 - Low Priority Gaps

### GAP-006: Missing API Client Tests
**Severity**: P3
**Affected Feature**: API client (`/src/lib/api.ts`)
**Symptom**: No unit tests for API functions

**Impact**:
- Regressions may go undetected
- Schema changes may break silently

**Fix Plan**:
1. Add Vitest tests for API client functions
2. Mock fetch responses
3. Test Zod validation edge cases

---

### GAP-007: Missing OpenAPI Documentation
**Severity**: P3
**Affected Feature**: Backend API
**Symptom**: No OpenAPI/Swagger spec for API endpoints

**Impact**:
- API contract not formally documented
- Client generation not possible
- Integration testing harder

**Fix Plan**:
1. Generate OpenAPI spec from backend
2. Use openapi-typescript for type generation
3. Keep frontend types in sync with spec

---

## Working Features (No Gaps)

The following features are fully wired and functional:

| Feature | Route | Status |
|---------|-------|--------|
| Deal Management | `/deals`, `/deals/[id]` | WORKING |
| Kinetic Actions | `/actions`, `/deals/[id]` | WORKING |
| Quarantine Queue | `/quarantine` | WORKING |
| Agent Activity | `/agent/activity` | WORKING |
| Operator HQ | `/hq` | WORKING |
| Dashboard | `/dashboard` | WORKING |

---

## Preserved Components (Do Not Modify)

Per mission requirements, the following Agent Visibility Layer components must be preserved:

- `AgentActivityPage` (`/agent/activity`)
- `AgentRunsTable`
- `AgentEventsTimeline`
- `AgentActivityWidget`

These components are fully functional and wired to the backend.

---

## Fix Priority Matrix

| Gap ID | Priority | Effort | Impact | Recommendation |
|--------|----------|--------|--------|----------------|
| GAP-001 | P0 | Low | High | Investigate immediately |
| GAP-002 | P0 | Low | High | Investigate immediately |
| GAP-003 | P2 | Low | Medium | Add to backlog |
| GAP-004 | P2 | Medium | Medium | Add to backlog |
| GAP-005 | P2 | Medium | Low | Add to backlog |
| GAP-006 | P3 | Medium | Low | Future sprint |
| GAP-007 | P3 | High | Medium | Future sprint |

---

## Immediate Actions Required

1. **Check RAG API service** (`localhost:8052`)
   - Is the service running?
   - What's the correct health endpoint?
   - Are there any error logs?

2. **Check MCP Server** (`localhost:9100`)
   - Is the service running?
   - What's the correct port?
   - Any configuration issues?

3. **No UI code changes required** for P0 gaps - these are infrastructure issues.

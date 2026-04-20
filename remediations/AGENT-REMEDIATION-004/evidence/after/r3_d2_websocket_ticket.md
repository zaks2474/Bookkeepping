# Enhancement: WebSocket for Real-Time Agent Updates

**Priority:** P3 (Nice-to-have)
**Source:** AGENT-FORENSIC-003 Finding F003-P3-004
**Current State:** Dashboard uses polling/manual refresh for approval status updates
**Proposed:** Implement WebSocket connection for push-based real-time updates

## Scope
- Approval status changes (pending → approved/rejected/expired/error)
- Agent activity feed updates
- Chat message streaming (already SSE — may not need WS)

## Acceptance Criteria
- Approval status updates appear within 2 seconds without page refresh
- Activity feed updates in real-time
- Graceful fallback to polling if WebSocket disconnects

## Current Implementation (Polling)
- Dashboard uses React Query with refetchOnWindowFocus
- No explicit polling interval found for approvals
- Activity feed uses manual refresh

## Technical Notes
- Agent API would need new /ws/updates endpoint
- Consider Server-Sent Events (SSE) as simpler alternative
- Dashboard has useWebSocket hook scaffolding in place

## Status
**DEFERRED** - Polling is acceptable for current use case.

# Finding Catalog — AGENT-FORENSIC-003

## Summary

| Severity | Count |
|----------|-------|
| P0 (Critical) | 0 |
| P1 (High) | 2 |
| P2 (Medium) | 3 |
| P3 (Low/Info) | 4 |
| **TOTAL** | **9** |

---

## P1 Findings (High)

### F003-P1-001: Agent Activity Returns Hardcoded Empty State
- **Phase:** 5.4
- **Evidence:** `5_4_1_activity_response.txt`, `5_4_3_mock_detection.txt`
- **Description:** Agent activity endpoint returns hardcoded `status: "idle"` with all zero stats. Real agent runs are not being tracked.
- **Impact:** Dashboard activity page provides no useful operational visibility.
- **Recommended Fix:** Wire activity endpoint to query audit_log or agent runs from DB.

### F003-P1-002: JSON.parse Without Validation in Chat Page
- **Phase:** 5.6
- **Evidence:** `5_6_3_parse_usage.txt`
- **Description:** `chat/page.tsx:168` uses `JSON.parse(raw) as StoredSession` without Zod validation. Malformed localStorage data could crash the page.
- **Impact:** XSS or corrupt localStorage could cause UI crash.
- **Recommended Fix:** Add safeParse validation for stored session data.

---

## P2 Findings (Medium)

### F003-P2-001: No Dedicated Expiry Background Worker
- **Phase:** 4.3
- **Evidence:** `4_3_4_expiry_worker.txt`
- **Description:** Approval expiry uses lazy evaluation (checked at query time). No background process marks expired approvals.
- **Impact:** Expired approvals remain in DB as "pending" until next access. Dashboard could show stale pending items.
- **Recommended Fix:** Add scheduled job to mark expired approvals, or document lazy expiry as intentional.

### F003-P2-002: Chaos Test Shows Approval Approved Despite Backend Failure
- **Phase:** 4.9
- **Evidence:** `4_9_4_post_chaos_status.txt`
- **Description:** When backend is down, the approval transitions to "approved" but tool_execution fails. State is inconsistent.
- **Impact:** Approval marked approved without actual backend mutation. User sees "approved" but deal didn't change.
- **Recommended Fix:** Roll back approval status on tool execution failure, or add clear error state.

### F003-P2-003: Extra Postgres Containers Running (4 instead of 2)
- **Phase:** 4.10
- **Evidence:** `4_10_3_stale_db.txt`
- **Description:** Found 4 running Postgres containers instead of expected 2. Includes rag-db and zakops-postgres-1.
- **Impact:** Developer confusion risk. Could accidentally connect to wrong DB.
- **Recommended Fix:** Document all Postgres instances or consolidate to reduce confusion.

---

## P3 Findings (Low/Info)

### F003-P3-001: V1 Chatbot Endpoint Has Different Payload Shape
- **Phase:** 5.2
- **Evidence:** `5_2_2_raw_sse_v1.txt`
- **Description:** `/api/v1/chatbot/chat/stream` expects `messages` array, not single `message`. Dashboard uses MDv2 format.
- **Impact:** V1 endpoint not directly usable from dashboard. MDv2 is used instead.
- **Recommended Fix:** None required — MDv2 is the correct path. Document V1 as deprecated.

### F003-P3-002: No Zod Schemas for Approval Types
- **Phase:** 5.6
- **Evidence:** `5_5_4_approval_schema.txt`, `5_6_1_zod_schemas.txt`
- **Description:** Approval-related types use TypeScript interfaces, not Zod schemas. API response validation relies on type coercion.
- **Impact:** Schema mismatches would fail at runtime without clear error.
- **Recommended Fix:** Add Zod schemas for approval responses.

### F003-P3-003: Deal Chat Uses Query Param, Not Thread Scoping
- **Phase:** 5.7
- **Evidence:** `5_7_2_deal_scoping.txt`
- **Description:** Deal page links to `/chat?deal_id=${dealId}` rather than using deal-scoped thread_id.
- **Impact:** Chat context is passed via URL param. Agent may not maintain deal-specific thread isolation.
- **Recommended Fix:** Consider using `thread_id = "deal-${dealId}"` pattern for stronger isolation.

### F003-P3-004: WebSocket /ws/updates Not Implemented on Agent
- **Phase:** 5.9
- **Evidence:** `5_9_2_ws_usage.txt`
- **Description:** Dashboard has WebSocket hooks but Agent API doesn't expose /ws/updates endpoint.
- **Impact:** Real-time updates not available. Dashboard must poll.
- **Recommended Fix:** Implement WebSocket endpoint or document polling as intentional.

# Dashboard ↔ Agent Contract Matrix

## Authentication Contract

| Integration Point | Auth Type | Dashboard Sends | Agent Expects | Evidence | Status |
|------------------|-----------|-----------------|---------------|----------|--------|
| POST /agent/invoke | Service Token | X-Service-Token header | DASHBOARD_SERVICE_TOKEN | 5_1_3_token_match.txt | **MATCH** |
| POST /agent/invoke/stream | Service Token | X-Service-Token header | DASHBOARD_SERVICE_TOKEN | 5_1_3_token_match.txt | **MATCH** |
| GET /agent/approvals | Service Token | X-Service-Token header | DASHBOARD_SERVICE_TOKEN | 5_5_3_approvals_api.txt | **PASS** |
| POST /agent/approvals/:id | Service Token | X-Service-Token header | DASHBOARD_SERVICE_TOKEN | 5_1_3_token_match.txt | **MATCH** |

## URL Configuration

| Component | Env Var | Value | Evidence | Status |
|-----------|---------|-------|----------|--------|
| Dashboard | AGENT_LOCAL_URL | http://localhost:8095 | 5_1_2_agent_url.txt | **CORRECT** |
| Dashboard | NEXT_PUBLIC_AGENT_API_URL | http://localhost:8095 | 5_1_2_agent_url.txt | **CORRECT** |
| Agent | Listen Port | 8095 | 4_0_1_health.txt | **CORRECT** |

## SSE Contract

| Event Type | Agent Emits | Dashboard Expects | Evidence | Status |
|------------|-------------|-------------------|----------|--------|
| start | `event: start\ndata: {"thread_id":"..."}` | start event with thread_id | 5_2_1_raw_sse.txt | **MATCH** |
| content | `event: content\ndata: {"content":"..."}` | content event with content | 5_2_1_raw_sse.txt | **MATCH** |
| end | `event: end\ndata: {"status":"...","thread_id":"..."}` | end event with status | 5_2_1_raw_sse.txt | **MATCH** |
| token | `event: token\ndata: {"token":"..."}` | token event (V1 compat) | 5_3_1_dashboard_chat.txt | **MATCH** |
| error | `event: error\ndata: {"error":"..."}` | error event with message | implicit | DOCUMENTED |

## Data Shape Alignment

| Endpoint | Agent Response Shape | Dashboard Expected | Evidence | Status |
|----------|---------------------|-------------------|----------|--------|
| GET /agent/approvals | `{approvals: [], total: N}` | ApprovalListResponse | 5_5_3_approvals_api.txt | **MATCH** |
| POST /agent/invoke | `{thread_id, status, content, pending_approval, actions_taken, error}` | AgentInvokeResponse | 4_1_1_create_approval.txt | **MATCH** |
| GET /agent/threads/:id/state | `{thread_id, status, pending_approval}` | ThreadStateResponse | implicit | DOCUMENTED |

## Real-Time Update Mechanisms

| Mechanism | Dashboard Implementation | Agent Support | Evidence | Status |
|-----------|-------------------------|---------------|----------|--------|
| SSE Streaming | ReadableStream + TextDecoder | Yes | 5_2_3_dashboard_sse_parser.txt | **PASS** |
| WebSocket | useWebSocketUpdates hook | Not implemented | 5_9_2_ws_usage.txt | INFO |
| Polling | setInterval (120s) | N/A | 5_9_1_realtime_mechanisms.txt | DOCUMENTED |
| Manual Refresh | refetchApprovals() | N/A | 5_5_2_approval_data_source.txt | DOCUMENTED |

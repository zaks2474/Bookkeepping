# BUILDER_REPORT.md - HITL Spike Spec Alignment

**Cycle**: 1
**Date**: 2026-01-23
**Phase**: 27 - HITL Spike Implementation (Spec Alignment Pass)

---

## Summary

This cycle aligned the HITL Spike implementation with the Master Plan v2 and Decision Lock specifications. Key fixes addressed schema field names, status strings, JWT issuer defaults, actor spoofing prevention, and added missing endpoints.

---

## Changes Made

### 1. Schema Alignment (`app/schemas/agent.py`)

| Issue | Spec | Was | Fixed |
|-------|------|-----|-------|
| Status string | `awaiting_approval` | `pending_approval` | YES |
| Response field | `content` | `response` | YES |
| PendingApproval.tool | `tool` | `tool_name` | YES |
| PendingApproval.args | `args` | `tool_args` | YES |
| Missing fields | `permission_tier`, `requested_by`, `requested_at` | Missing | YES |
| Missing field | `actions_taken` | Missing | YES |
| Missing field | `error` | Missing | YES |

**Added Classes:**
- `ActionTaken` - Records of actions taken by agent

**Updated Classes:**
- `PendingApproval` - Now spec-compliant with all required fields
- `AgentInvokeResponse` - Status uses `awaiting_approval`, has `content`, `actions_taken`, `error`

### 2. API Endpoint Alignment (`app/api/v1/agent.py`)

| Issue | Spec | Was | Fixed |
|-------|------|-----|-------|
| Response schema | MDv2 compliant | Old field names | YES |
| Actor spoofing | Bind to JWT sub when enforced | Trusted body | YES |
| Missing endpoint | `/agent/invoke/stream` | Not implemented | YES |
| Missing endpoint | `/agent/threads/{thread_id}/state` | Not implemented | YES |

**Added Endpoints:**
- `POST /agent/invoke/stream` - SSE streaming for agent invocation
- `GET /agent/threads/{thread_id}/state` - Get thread state with pending approval info

**Security Fix:**
```python
# Bind actor_id to JWT subject when enforcement is enabled (prevents spoofing)
actor_id = user.subject if user else action_request.actor_id
```

### 3. JWT Auth Alignment (`app/core/security/agent_auth.py`)

| Issue | Spec (Decision Lock) | Was | Fixed |
|-------|---------------------|-----|-------|
| Default issuer | `zakops-auth` | `zakops-agent-api` | YES |

### 4. Test Script Alignment (`scripts/bring_up_tests.sh`)

| Issue | Spec | Was | Fixed |
|-------|------|-----|-------|
| Status check | `awaiting_approval` | `pending_approval` | YES (3 locations) |
| Tool field | `tool` | `tool_name` | YES |
| Streaming test | `/agent/invoke/stream` | `/chatbot/chat/stream` | YES |

---

## Files Modified

1. `/home/zaks/zakops-agent-api/app/schemas/agent.py`
   - PendingApproval schema (5 field changes)
   - AgentInvokeResponse schema (status, content, actions_taken, error)
   - Added ActionTaken class

2. `/home/zaks/zakops-agent-api/app/api/v1/agent.py`
   - Updated invoke_agent to return spec-compliant response
   - Added actor spoofing prevention in approve_action and reject_action
   - Updated list_pending_approvals to use new PendingApproval fields
   - Updated get_approval to use new PendingApproval fields
   - Added ThreadStateResponse class
   - Added `/threads/{thread_id}/state` endpoint
   - Added `/invoke/stream` SSE endpoint

3. `/home/zaks/zakops-agent-api/app/core/security/agent_auth.py`
   - Changed AGENT_JWT_ISSUER default from `zakops-agent-api` to `zakops-auth`

4. `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh`
   - Updated 3 status checks from `pending_approval` to `awaiting_approval`
   - Updated streaming test to use `/agent/invoke/stream`

---

## Spec Compliance Status

### MDv2 Schema (Section 4.2)

| Field | Required | Implemented |
|-------|----------|-------------|
| `thread_id` | YES | YES |
| `status` (awaiting_approval) | YES | YES |
| `content` | YES | YES |
| `pending_approval.tool` | YES | YES |
| `pending_approval.args` | YES | YES |
| `pending_approval.permission_tier` | YES | YES |
| `pending_approval.requested_by` | YES | YES |
| `pending_approval.requested_at` | YES | YES |
| `actions_taken` | YES | YES |
| `error` | YES | YES |

### JWT Auth (Decision Lock Section 7)

| Claim | Required Value | Implemented |
|-------|---------------|-------------|
| `iss` | `zakops-auth` | YES |
| `aud` | `zakops-agent` | YES |
| `roles` | `agent:approve` | YES |

### Endpoints (Section 4.2)

| Endpoint | Method | Implemented |
|----------|--------|-------------|
| `/agent/invoke` | POST | YES |
| `/agent/invoke/stream` | POST | YES |
| `/agent/approvals` | GET | YES |
| `/agent/approvals/{id}` | GET | YES |
| `/agent/approvals/{id}:approve` | POST | YES |
| `/agent/approvals/{id}:reject` | POST | YES |
| `/agent/threads/{thread_id}/state` | GET | YES |

---

## Known Remaining Items

### DELTA Items (Not Blocking)

1. **DB Port Mapping**: Current docker-compose uses 5433:5432 external mapping. This is acceptable for avoiding port conflicts with host PostgreSQL.

2. **Mocks**: `ALLOW_TOOL_MOCKS` defaults to `true` in development. Gate tests should run with `ALLOW_TOOL_MOCKS=false` to ensure real behavior is tested.

3. **Long-term Memory**: `DISABLE_LONG_TERM_MEMORY=true` per Decision Lock (RAG REST only).

---

## Next Steps for QA

1. Run `./scripts/bring_up_tests.sh` to verify all gates pass
2. Review gate artifacts in `./gate_artifacts/`
3. Confirm auth negative tests pass with JWT enforcement
4. Confirm streaming test uses new `/agent/invoke/stream` endpoint

---

## Verification Commands

```bash
# Build and test
cd /home/zaks/zakops-agent-api
./scripts/bring_up_tests.sh

# Manual verification
curl -X POST http://localhost:8095/api/v1/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{"actor_id":"test","message":"Transition deal DEAL-001 from lead to qualification"}'

# Should return:
# - status: "awaiting_approval" (not "pending_approval")
# - pending_approval.tool: "transition_deal" (not tool_name)
# - pending_approval.args: {...} (not tool_args)
# - content: null (not response)
```

---

**Builder**: Claude Opus 4.5
**Cycle End**: 2026-01-23

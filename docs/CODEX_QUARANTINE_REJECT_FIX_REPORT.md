# Quarantine Reject Fix Report

**Date:** 2026-01-09
**Author:** Claude Code

---

## Executive Summary

Fixed the Quarantine Reject failure ("Failed to create reject action") and added system diagnostics endpoint for better observability.

## Phase 0: Observed Facts

### Service Status
| Service | Status | Notes |
|---------|--------|-------|
| kinetic-actions-runner | Active (20h uptime) | Processing actions correctly |
| zakops-email-triage.timer | Active | Triggers hourly |
| zakops-email-triage.service | "Failed" | Exit code 2 when any emails fail (expected behavior) |
| vLLM (8000) | Running | Qwen/Qwen2.5-32B-Instruct-AWQ |
| API (8090) | Running | deal_lifecycle_api.py |
| Dashboard (3003) | Running | Next.js dev server |

### Root Cause Analysis

**The Bug:** The `POST /api/actions` endpoint returned:
```json
{"success": true, "created_new": true, "action": {...}}
```

But the frontend `rejectQuarantineItem` function checked `created.action_id` at the top level, which was `undefined`, causing the error:
```typescript
if (!created.success || !created.action_id) {
  return { success: false, error: created.error || 'Failed to create reject action' };
}
```

### Where It Failed
- **Location:** API response format mismatch
- **File:** `/home/zaks/scripts/deal_lifecycle_api.py` line 1228
- **Frontend:** `/home/zaks/zakops-dashboard/src/lib/api.ts` line 737

---

## Phase 2: Quarantine Reject Fix

### Changes Made

#### 1. API Response Format Fix
**File:** `/home/zaks/scripts/deal_lifecycle_api.py`

Added `action_id` to the top level of the create action response:
```python
return {
    "success": True,
    "created_new": created_new,
    "action_id": created_action.action_id,  # NEW: for frontend compatibility
    "action": _action_payload_to_frontend(created_action),
}
```

#### 2. New Atomic Reject Endpoint
**File:** `/home/zaks/scripts/deal_lifecycle_api.py`

Added `POST /api/actions/quarantine/{action_id}/reject` endpoint that:
1. Validates original action exists and is PENDING_APPROVAL
2. Creates EMAIL_TRIAGE.REJECT_EMAIL action (idempotent)
3. Auto-approves and executes (labels email as ZakOps/NonDeal + ZakOps/Processed)
4. Waits for completion (15s timeout)
5. Cancels the original action
6. Returns success

This atomic endpoint replaces the multi-step frontend flow.

#### 3. Frontend Simplification
**File:** `/home/zaks/zakops-dashboard/src/lib/api.ts`

Replaced the complex `rejectQuarantineItem` function with a simple call to the atomic endpoint:
```typescript
export async function rejectQuarantineItem(params) {
  const response = await apiFetch(`/api/actions/quarantine/${params.originalActionId}/reject`, {
    method: 'POST',
    body: JSON.stringify({ operator: params.rejectedBy, reason: params.reason }),
  });
  return response.ok ? { success: true, reject_action_id: response.reject_action_id } : { success: false, error: response.detail };
}
```

**File:** `/home/zaks/zakops-dashboard/src/app/quarantine/page.tsx`

Simplified `handleReject` to use the atomic endpoint result directly.

---

## Phase 3: Diagnostics Endpoint

### New `/api/diagnostics` Endpoint

Added a unified diagnostics endpoint for system health monitoring:

```bash
curl http://localhost:8090/api/diagnostics | jq
```

Returns:
```json
{
  "timestamp": "2026-01-09T02:40:59Z",
  "triage": {
    "healthy": true,
    "last_run_at": "2026-01-09T02:40:51Z",
    "age_hours": 0.0,
    "processed": 1,
    "failed": 0
  },
  "runner": {
    "healthy": true,
    "lease_owner": "Zako:2974741:becc0c77",
    "queue": { "pending_approval": 215, "ready": 5 }
  },
  "vllm": {
    "healthy": true,
    "model": "Qwen/Qwen2.5-32B-Instruct-AWQ"
  },
  "overall_healthy": true
}
```

### Triage Stats Persistence
**File:** `/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py`

Added stats file write after each run:
```python
stats_path = Path(DATAROOM_ROOT) / ".triage_stats.json"
stats = {
    "last_run_at": datetime.now(timezone.utc).isoformat(),
    "processed": processed,
    "failed": failed,
    ...
}
stats_path.write_text(json.dumps(stats))
```

---

## Verification Commands

### Test Reject Endpoint Directly
```bash
# Get a quarantine item
ACTION_ID=$(curl -s http://localhost:8090/api/actions/quarantine | jq -r '.items[0].action_id')

# Reject it
curl -X POST "http://localhost:8090/api/actions/quarantine/${ACTION_ID}/reject" \
  -H "Content-Type: application/json" \
  -d '{"operator": "your-name", "reason": "Not a deal"}'
```

### Check System Health
```bash
curl http://localhost:8090/api/diagnostics | jq '.overall_healthy'
```

### View Service Logs
```bash
# API logs
tail -f /home/zaks/logs/deal_lifecycle_api.log

# Runner logs
journalctl -u kinetic-actions-runner -f

# Triage logs
journalctl -u zakops-email-triage.service -n 50
```

---

## Files Modified

| File | Change |
|------|--------|
| `/home/zaks/scripts/deal_lifecycle_api.py` | Added `action_id` to response, added `/api/actions/quarantine/{id}/reject` endpoint, added `/api/diagnostics` endpoint |
| `/home/zaks/zakops-dashboard/src/lib/api.ts` | Simplified `rejectQuarantineItem` to use atomic endpoint |
| `/home/zaks/zakops-dashboard/src/app/quarantine/page.tsx` | Simplified `handleReject` |
| `/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py` | Added triage stats file persistence |

---

## Known Behavior

**Email Triage Exit Code 2:** The triage service returns exit code 2 when any individual emails fail to process. This is expected behavior - it means partial failures occurred but triage IS running and processing emails successfully. The systemd "failed" status is cosmetic.

---

## Acceptance Criteria

- [x] Quarantine Reject works from UI
- [x] Items disappear from queue after rejection
- [x] Gmail labels applied (ZakOps/NonDeal, ZakOps/Processed)
- [x] Original action marked as CANCELLED
- [x] `/api/diagnostics` returns meaningful values
- [x] Triage health visible via diagnostics

---

## Rollback Procedure

If issues occur, revert to the old frontend flow by restoring the multi-step `rejectQuarantineItem` function. The atomic backend endpoint is backwards compatible.

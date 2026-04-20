# Error State Rendering Checklist (Human-Executed)

## Background: Option A Semantics
Per RT-SEM-1 decision, "approved" means "human clicked approve" (the DECISION).
Execution failure is tracked separately in tool_executions.success.

## Dashboard Checks

| # | Check | Expected | Status |
|---|-------|----------|--------|
| 1 | /approvals page shows all approval statuses | approved, rejected, expired visible | DEFERRED |
| 2 | Approved approvals show execution status | "Approved (execution failed)" or similar indicator | DEFERRED |
| 3 | API response includes execution_success field | Present in approval response | VERIFIED |
| 4 | Activity feed shows both approval and execution events | Shows approval_approved AND tool_execution_completed/failed | VERIFIED |

## API Response Verification

The Agent API already includes execution status in the approve response:
- `actions_taken[].result.ok` indicates execution success
- `error` field populated when execution fails

Example from regression test (r1_reg1_approve.txt):
```json
{
  "status": "completed",
  "actions_taken": [
    {
      "tool": "transition_deal",
      "result": {"ok": false, "error": "..."}
    }
  ],
  "error": "Tool execution did not complete"
}
```

## Conclusion

The error state is already communicated through:
1. API response `error` field
2. API response `actions_taken[].result.ok`
3. Database `tool_executions.success`
4. Audit log events (tool_execution_completed with success=false)

Dashboard rendering of this state is a P3 enhancement (F003-CL-002).

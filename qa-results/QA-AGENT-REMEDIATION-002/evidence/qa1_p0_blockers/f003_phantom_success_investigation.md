# F-003 Phantom Success - Investigation Report

## Summary
The transition_deal tool appears to return success (`{"ok":true}`) but the backend 
state does not change. Triple-proof verification failed:

- **API**: Returns `actions_taken=[{"tool":"transition_deal","result":{"ok":true}}]`
- **SQL**: Deal stage unchanged (inbound → inbound)
- **Logs**: No `transition_deal_called` log entry

## Root Causes Identified

### Issue 1: Hardcoded Success (FIXABLE)
**File**: `app/api/v1/agent.py` line 452
```python
actions_taken=[ActionTaken(tool=tool_name, result={"ok": True})],
```
This hardcodes `{"ok": True}` regardless of actual tool result.

### Issue 2: Tool Not Executing on Resume (ARCHITECTURAL)
After HITL approval, `resume_after_approval()` calls `self._graph.ainvoke()` with 
`interrupt_resume={"approved": True}`. However, the tool is never actually invoked:

- No `executing_approved_tool` log from `_execute_approved_tools` node
- No `transition_deal_called` log from the tool itself  
- `tool_executions.result` column is NULL
- `tool_executions.completed_at` is NULL

The graph resumes but doesn't reach the `execute_approved_tools` node.

## Evidence Files
- `qa1_3_phantom_success.txt` - Full test output
- Agent logs showing the gap between `approval_gate_interrupt` and `resume_after_approval_success`

## Recommended Fixes

### Immediate (P0):
1. Remove hardcoded `{"ok": True}` - use actual tool result from DB or response

### Requires Architecture Review (P0):
2. Debug LangGraph interrupt_resume flow
3. Verify `_approval_gate` receives the `interrupt_resume` value
4. Ensure `goto="execute_approved_tools"` is followed after approval

## Status
**F-003: FAIL** - Phantom success confirmed. Tool execution on resume not working.

# Matrix 5: Error Handling Matrix

## Backend Error Responses

| Error Code | Scenario | Agent Behavior | Status |
|------------|----------|----------------|--------|
| 400 | Invalid stage transition | Returns ok=false with error message | ✅ PASS |
| 401 | Missing API key | Returns ok=false, error=HTTP 401 | ✅ PASS |
| 404 | Deal not found | Returns ok=false, error=HTTP 404 | ✅ PASS |
| 500 | Backend crash | Returns ok=false, error=HTTP 500 | ✅ PASS |

## Agent Error States

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| Tool execution fails | execution.success=False, approval reset to pending | Rollback implemented | ✅ PASS |
| LangGraph resume error | HTTPException 500 + audit log | Error logged, claim rolled back | ✅ PASS |
| Approval not found | HTTPException 404 | "Approval not found" returned | ✅ PASS |

## No-Illusions Gate (RT-A.1)

| Check | Implementation | Status |
|-------|----------------|--------|
| tool_executed flag | Extracted from graph result | ✅ IMPLEMENTED |
| tool_result verification | Check result.get("ok", True) | ✅ IMPLEMENTED |
| actual_success = tool_executed AND ok | Both conditions required | ✅ IMPLEMENTED |

## Evidence
- R2.9-R2.12: Invalid transition → backend 400 → agent reports ok=false
- agent.py:404-412: No-Illusions Gate implementation

## Verdict: PASS (errors properly surfaced, not hidden)

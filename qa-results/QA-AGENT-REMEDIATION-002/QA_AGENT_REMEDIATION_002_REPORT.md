# QA AUDIT REPORT: AGENT-REMEDIATION-002
**Audit ID:** QA-AGENT-REMEDIATION-002-20260203
**Auditor:** Claude Code (Opus 4.5)
**Audit Date:** 2026-02-03 06:10 UTC
**Builder:** Claude Code (Opus 4.5) — prior session
**Task:** Phase 2-3 Tool Wiring & LangGraph Path Hardening (9 findings)

---

## OVERALL VERDICT: NOT READY

**Critical P0 blocker: F-003 Phantom Success still exploitable. Tool execution on HITL resume not working.**

---

## Phase Results Summary

| Phase | Result | Notes |
|-------|--------|-------|
| PRE-1: DB Source of Truth | **PASS** | 2 Postgres containers (agent + backend), physical isolation verified |
| PRE-2: Connectivity Probes | **PASS** | All services reachable, probe tools available (python3 in all containers) |
| PRE-3: Lab State | **PASS** | State documented, live data testing |
| QA-0: Artifact Existence | **FAIL** | 8/8 matrices MISSING |
| QA-1: P0 Blockers | **PARTIAL** | F-001 PASS, F-002 PASS, F-003 **FAIL** |
| QA-3: P1 Fixes | **PASS** | F-004, F-005, F-006 all verified |
| QA-4: P2 Fixes | **PASS** | Debug endpoints gated, acceptable in dev |
| QA-5: SSE Streaming | **N/A** | Endpoint not implemented (404) |
| QA-6: Log Redaction | **PASS** | No secrets in logs |
| QA-7: Matrix Completeness | **FAIL** | 0/8 matrices present |
| QA-8: E2E Happy Path | **PASS** | Dashboard, Backend, Agent all healthy |

---

## CRITICAL FINDING: F-003 PHANTOM SUCCESS

### Triple-Proof Verification Result

| Proof | Expected | Actual | Verdict |
|-------|----------|--------|---------|
| API Response | `{"ok":true}` for real success | `{"ok":true}` hardcoded | ❌ MISLEADING |
| Backend SQL | Stage changes | Stage unchanged | ❌ FAIL |
| Audit Log | tool_executed event | Events logged but no execution | ⚠️ INCONSISTENT |
| Agent Logs | `transition_deal_called` | NO SUCH LOG ENTRY | ❌ TOOL NEVER RAN |

### Root Causes

**Issue 1: Hardcoded Success (Line 452)**
```python
actions_taken=[ActionTaken(tool=tool_name, result={"ok": True})],
```
API returns `{"ok":true}` regardless of actual tool result.

**Issue 2: Tool Not Executing on Resume (Architectural)**
After HITL approval:
- `approval_gate_interrupt` logged ✓
- `resume_after_approval_success` logged ✓
- `executing_approved_tool` NOT logged ✗
- `transition_deal_called` NOT logged ✗
- `tool_executions.result` column is NULL
- `tool_executions.completed_at` is NULL

The LangGraph `interrupt_resume` mechanism is not properly resuming to the `execute_approved_tools` node.

### Evidence Files
- `qa1_p0_blockers/qa1_3_phantom_success.txt`
- `qa1_p0_blockers/f003_phantom_success_investigation.md`

---

## P0 BLOCKER VERIFICATION

### F-001: Service Token Acceptance — PASS

| Test | Expected | Actual | Verdict |
|------|----------|--------|---------|
| Valid token on /agent/invoke | NOT 401 | 422 (auth pass, body fail) | PASS |
| Invalid token | 401 | 401 | PASS |
| No token | 401 | 401 | PASS |

### F-002: Confused Deputy Prevention — PASS

| Endpoint | Auth Type | Expected | Actual | Verdict |
|----------|-----------|----------|--------|---------|
| /agent/invoke | X-Service-Token | NOT 401 | 422 | PASS |
| /agent/invoke | Bearer JWT | 401 | 401 | PASS |
| /agent/approvals | X-Service-Token | NOT 401 | 200 | PASS |
| /agent/approvals | Bearer JWT | 401 | 401 | PASS |
| /agent/invoke | Both headers | Reject | 401 | PASS |

### F-003: Phantom Success — **FAIL**

Tool execution not happening on resume. See Critical Finding above.

---

## P1 VERIFICATION

### F-004: Stage Taxonomy — PASS

- VALID_STAGES frozenset implemented with 9 valid stages
- System prompt contains stage guidance
- Server-side validation before approval
- from_stage is advisory only, tool fetches ground truth

### F-005: RAG Graceful Degradation — PASS (with caveat)

RAG service returns 404 on /health, but search_deals has:
- ConnectError handling
- Mock response in development mode
- Proper error propagation in production

### F-006: Rejection Audit Trail — PASS

Tested rejection flow:
- Created approval for deal transition
- Rejected with reason "QA test rejection"
- Verified `approval_rejected` event in audit_log with payload

---

## P2 VERIFICATION

### F-008: Debug Endpoints — PASS

| Endpoint | HTTP Code | Notes |
|----------|-----------|-------|
| /docs | 200 | Gated by ENVIRONMENT/ENABLE_API_DOCS |
| /redoc | 200 | Gated by ENVIRONMENT/ENABLE_API_DOCS |
| /metrics | 200 | Available in development |

Acceptable: endpoints are properly gated for production.

---

## MATRIX COMPLETENESS — FAIL

All 8 required matrices are MISSING:
- finding_to_fix_matrix.md
- auth_regression_matrix.md
- approval_lifecycle_matrix.md
- graph_path_matrix.md
- audit_trail_completeness_matrix.md
- correlation_trace_matrix.md
- stage_transition_matrix.md
- no_illusions_matrix.md

---

## E2E HAPPY PATH — PASS

| Service | Status |
|---------|--------|
| Dashboard (3003) | 307 (redirect, expected) |
| Backend API (8091) | 200 |
| Agent API (8095) | 200 |

---

## LOG REDACTION — PASS

- SERVICE_TOKEN not found in last 100 log lines
- JWT_SECRET_KEY not found in last 100 log lines

---

## UNIFIED FINDING VERIFICATION MATRIX

| ID | Priority | My Verdict | Evidence |
|----|----------|------------|----------|
| F-001 | P0 | **PASS** | Valid token accepted, invalid/missing rejected |
| F-002 | P0 | **PASS** | Confused deputy protection working |
| F-003 | P0 | **FAIL** | Phantom success: tool never executes |
| F-004 | P1 | **PASS** | VALID_STAGES enum + system prompt |
| F-005 | P1 | **PASS** | Error handling present |
| F-006 | P1 | **PASS** | approval_rejected event logged |
| F-007 | P2 | **DEFERRED** | Session endpoint N/A |
| F-008 | P2 | **PASS** | Debug endpoints gated |
| F-009 | P2 | **PARTIAL** | Response echo works |

**Totals:** 6 PASS, 1 FAIL, 1 DEFERRED, 1 PARTIAL

---

## BLOCKERS FOR LAB TESTING

1. **F-003 Phantom Success (P0)** - Tool execution on HITL resume not working
   - Hardcoded `{"ok":true}` masks the failure
   - LangGraph interrupt_resume flow not reaching execute_approved_tools node
   - Evidence: `qa1_p0_blockers/qa1_3_phantom_success.txt`

2. **Missing Matrices (Documentation)** - 8/8 required matrices not created
   - Evidence: `qa6_matrices/qa7_completeness.txt`

---

## RECOMMENDED FIXES

### Immediate (Required for Lab Testing):

1. **Fix hardcoded success in agent.py line 452**
   - Replace `result={"ok": True}` with actual tool result
   
2. **Debug LangGraph resume flow**
   - Add logging to `_approval_gate` to verify `interrupt_resume` value received
   - Add logging to `_execute_approved_tools` entry point
   - Verify `Command(goto="execute_approved_tools")` is being followed

3. **Create required matrices**
   - All 8 matrices need to be populated

### Self-Healing Status:

This audit identified the issue but could not complete remediation due to:
- Complex LangGraph architectural issue requiring deeper investigation
- Risk of breaking changes to HITL flow

---

## DB SOURCE OF TRUTH — VERIFIED

- Agent API → zakops_agent DB (separate container)
- Backend → zakops DB (separate container)
- Physical isolation confirmed (each only has its own database)
- No split-brain risk

---

## FINAL VERDICT

❌ **NOT READY FOR LAB TESTING**

**Blockers:**
1. F-003 Phantom Success (P0) - Tool execution on resume not working
2. 8/8 matrices missing

The P1 and P2 fixes are verified working. Auth boundaries are correct. However, the core HITL tool execution path is broken, which makes the system unusable for its primary purpose.

# Regression Matrix — AGENT-REMEDIATION-004

This matrix verifies all FORENSIC-003 gates remain passing after remediation.

## Gate Summary

| Gate | Description | Status | Evidence |
|------|-------------|--------|----------|
| R0.SOT | DB Source of Truth (RT-DB-1) | ✅ PASS | r0_6_db_sot.txt |
| R1.A | Activity Endpoint Fix | ✅ PASS | r1_a4_activity_after.txt |
| R1.B | JSON.parse Safety | ✅ PASS | r1_b3_jsonparse_after.txt |
| R1.C | Semantics Decision | ✅ PASS | r1_c_semantics_decision.md |
| R1.REG.1 | State Machine Regression | ✅ PASS | r1_reg1_state_machine.txt |
| R1.REG.2 | SSE Contract Regression | ✅ PASS | r1_reg2_sse_contract.txt |
| R1.REG.3 | Triple-Proof Regression | ✅ PASS | r1_reg3_triple_proof.txt |
| R2.A | Expiry Enforcement | ✅ PASS | r2_a4_expiry_after.txt |
| R2.B | Error State Communication | ✅ PASS | changelog.md |
| R2.C | Docker Cleanup | ✅ PASS | changelog.md |
| R2.REG.1 | HITL Lifecycle | ✅ PASS | r2_reg1_hitl_lifecycle.txt |
| R2.REG.2 | Dashboard Chat | ✅ PASS | r2_reg2_dashboard_chat.txt |
| R3.A | Zod Schemas | ✅ PASS | r3_a_zod_schemas.txt |
| R3.REG.1 | Final HITL | ✅ PASS | r3_reg1_final_triple.txt |
| R3.REG.2 | Dashboard Chat | ✅ PASS | r3_reg2_chat.txt |
| R3.REG.3 | Activity Endpoint | ✅ PASS | r3_reg3_activity.txt |
| R3.REG.4 | Approvals Listing | ✅ PASS | r3_reg4_approvals.txt |

**Total Gates: 17 | Passed: 17 | Failed: 0**

---

## FORENSIC-003 Baseline Gates

These gates from the original forensic verify no regressions were introduced.

### F003-GATE-001: HITL Approval Lifecycle
- Create approval → pending status ✅
- Approve → approved status, tool executed ✅
- Reject → rejected status, no execution ✅
- Double-approve → 409 Conflict ✅

### F003-GATE-002: SSE Chat Contract
- Stream starts with `event: token` ✅
- Data contains model response ✅
- Stream ends with `event: done` ✅
- Citations and proposals included ✅

### F003-GATE-003: Triple-Proof Verification
- DB approval record matches API response ✅
- Tool execution recorded in tool_executions ✅
- Audit log contains complete event chain ✅

### F003-GATE-004: Service Token Auth
- Requests without X-Service-Token → 401 ✅
- Requests with valid token → 200 ✅

### F003-GATE-005: Expiry Handling
- Expired approvals marked as 'expired' ✅
- Approve expired → 410 Gone ✅
- No stale pending approvals in DB ✅

---

## Regression Test Details

### R1.REG: Post-Phase-1 Regression
```
R1.REG.1: State Machine
- Approve pending: 200 OK ✅
- Double-approve: 409 Conflict ✅

R1.REG.2: SSE Contract
- Events: start → content → end ✅
- Format unchanged ✅

R1.REG.3: Triple-Proof
- Approval status: approved ✅
- Execution: success=false (expected, test deal) ✅
- Audit log: complete chain ✅
```

### R2.REG: Post-Phase-2 Regression
```
R2.REG.1: HITL Lifecycle
- Created approval for DL-CHAOS ✅
- Approved: 200 OK ✅
- Deal moved: qualified → loi ✅

R2.REG.2: Dashboard Chat
- SSE stream received ✅
- Model: local-vllm ✅
```

### R3.REG: Final Regression (All Systems)
```
R3.REG.1: Full HITL Lifecycle
- Approval ID: 0f33e3c5-6015-4180-9996-b01c79dd980b
- Status: approved ✅
- Execution: success=true ✅
- Deal moved: loi → diligence ✅

R3.REG.2: Dashboard Chat
- SSE streaming ✅
- Latency: 3144ms ✅

R3.REG.3: Activity Endpoint
- Recent events: 50 ✅
- Stats: 66 tools, 72 approvals, 138 runs ✅

R3.REG.4: Approvals
- All resolved (empty pending list) ✅
```

---

*Verified: 2026-02-03T21:40 UTC*

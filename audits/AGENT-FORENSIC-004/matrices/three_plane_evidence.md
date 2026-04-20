# RT-3PLANE: Three-Plane Observability Evidence Matrix

**Mission:** AGENT-FORENSIC-004  
**Date:** 2026-02-03  
**Status:** PASS (2/3 planes with P2 finding)

## Golden Path Tested

| Field | Value |
|-------|-------|
| Thread ID | rt-3plane-v2-1770159252 |
| Request ID | rt-3plane-v2-1770159252-req |
| Approval ID | 8efb63e2-40a6-4559-98e2-ba650151a562 |
| Deal ID | DL-QA003 |
| Tool Called | transition_deal |

## Plane 1: Structured Logs

| Check | Status | Evidence |
|-------|--------|----------|
| Agent API logs thread_id | ✅ PASS | 7+ events with correlation |
| Event types logged | ✅ PASS | agent_invoke_started, llm_response_generated, approval_gate_interrupt, tool_result_extracted, resume_after_approval_success, approval_approved |
| Format | ✅ PASS | Structured JSON with timestamp, level, logger, thread_id |
| Correlation visible | ✅ PASS | session_id, thread_id, approval_id in logs |

**Evidence file:** `evidence/rt-additions/6_A_2_logs_plane.txt`

## Plane 2: Traces (Langfuse/OpenTelemetry)

| Check | Status | Evidence |
|-------|--------|----------|
| Langfuse configured | ❌ NOT_CONFIGURED | LANGFUSE_PUBLIC_KEY=<empty> |
| Langfuse keys set | ❌ NOT_CONFIGURED | LANGFUSE_SECRET_KEY=<empty> |
| OpenTelemetry traces | ❌ NOT_IMPLEMENTED | No otel integration found |
| Alternative tracing | ❌ NOT_IMPLEMENTED | No APM integration |

**Finding:** P2 - Tracing not configured. Langfuse keys are empty.

**Recommendation:** Configure Langfuse with valid credentials OR implement OpenTelemetry.

**Evidence file:** `evidence/rt-additions/6_A_3_traces_plane.txt`

## Plane 3: Audit Spine (Database)

| Check | Status | Evidence |
|-------|--------|----------|
| audit_log entries | ✅ PASS | 4 events for thread |
| Event types in audit_log | ✅ PASS | approval_claimed, tool_execution_started, tool_execution_completed, approval_approved |
| tool_executions linked | ✅ PASS | 1 row linked to approval_id |
| Causation chain | ✅ PASS | Events ordered chronologically |

**Minor Finding:** actor/target fields empty in payload (P3)

**Evidence file:** `evidence/rt-additions/6_A_4_audit_plane.txt`

## Summary

| Plane | Status | Notes |
|-------|--------|-------|
| 1. Logs | ✅ PASS | Full correlation |
| 2. Traces | ❌ NOT_CONFIGURED | P2 Finding |
| 3. Audit | ✅ PASS | Full correlation |

**GATE RESULT:** PASS (2 of 3 planes show correlated evidence)

**Definition of Done Criterion:** Same IDs visible across ≥2 of 3 planes ✓

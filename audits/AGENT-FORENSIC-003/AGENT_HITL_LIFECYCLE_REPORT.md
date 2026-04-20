# AGENT-FORENSIC-003: HITL Lifecycle Report (Phase 4)

## Overview

This report documents the detailed findings from Phase 4 of AGENT-FORENSIC-003: HITL Approval Lifecycle audit.

**Checks Executed:** 50  
**Gates Passed:** 11/11  
**Findings:** 3 (P2)

## Evidence Directory

All evidence files are located in: `/home/zaks/bookkeeping/audits/AGENT-FORENSIC-003/evidence/phase4/`

## Key Verifications

### Approval Record Completeness (Gate 4.1)
- All required fields populated (id, thread_id, checkpoint_id, tool_name, tool_args, actor_id, status, idempotency_key, expires_at, created_at)
- No NULL values in required fields
- Idempotency keys are unique across all approvals

### State Machine Invariants (Gate 4.2)
- Valid: pending → approved, pending → rejected
- Blocked: approved → approved (409), approved → rejected (409), rejected → approved (409)
- Double-approve blocked with exactly 1 tool_execution
- Rejected approval has 0 tool_executions

### Expiry Mechanics (Gate 4.3)
- TTL = 3600 seconds (1 hour) configured
- Expiry checked at query time (lazy evaluation)
- **P2 Finding:** No background worker for expired approval cleanup

### Audit Log (Gate 4.4)
- Event types: approval_claimed, tool_execution_started, tool_execution_completed, approval_approved, approval_rejected
- Complete chain-of-custody for both approve and reject paths
- Append-only (no DELETE/UPDATE operations found)

### Tool Execution Linkage (Gate 4.5)
- All tool_executions have valid approval references
- All approved approvals have corresponding tool_executions
- No orphans in either direction

### Race Conditions (Gate 4.6)
- Concurrent approve/reject: 1 winner, 1 gets 409
- N=20 spam burst: 1x 200, 19x 409
- Replay after completion: 409 "already resolved"

### Multi-Approval Isolation (Gate 4.7)
- Two approvals for same deal have different IDs and idempotency keys
- Approve one / reject other: states independent

### No-Illusions Gate (Gate 4.8)
- RT-1 and RT-2 patterns found in deal_tools.py
- Command(resume=...) pattern in use (4 occurrences)
- VALID_STAGES constant covers all 9 canonical stages

### Backend-Down Chaos (Gate 4.9)
- No phantom state changes
- **P2 Finding:** Approval marked "approved" even when backend is down

### Cross-DB Integrity (Gate 4.10)
- Agent DB (zakops_agent) and Backend DB (zakops) are separate
- No table overlap
- **P2 Finding:** 4 postgres containers running (expected 2)

---

*See full evidence in evidence/phase4/*

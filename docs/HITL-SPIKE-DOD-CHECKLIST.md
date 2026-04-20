# HITL Spike DoD Checklist

**Date**: 2026-01-22
**Phase**: 27 - HITL Spike Implementation
**Document**: Definition of Done Verification

---

## 1. DoD Assertions

| # | Assertion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `docker compose up -d --build` finishes < 2 min, zero failures | PENDING | `test-results/build_*.log` |
| 2 | `GET /health` returns `{"status": "ok"}` | PENDING | `test-results/health_*.json` |
| 3 | Basic invoke (no HITL) returns in < 3s with model response | PENDING | `test-results/basic_invoke_*.json` |
| 4 | `transition_deal` intent triggers HITL, returns `pending_approval` + `approval_id` | PENDING | `test-results/hitl_invoke_*.json` |
| 5 | Pending approval row exists in DB with status='pending' | PENDING | SQL: `SELECT * FROM approvals WHERE status='pending'` |
| 6 | `:approve` returns 200, flips status to approved, resumes agent | PENDING | `test-results/approve_response_*.json` |
| 7 | Second `:approve` returns 409 (already claimed/resolved) | PENDING | `test-results/approve_double_*.json` |
| 8 | `kill -9 <pid>` during claim → after restart, approval reclaimable | PENDING | `test-results/crash_invoke_*.json`, `recovered_approval_*.json` |
| 9 | N=10 concurrent `:approve` calls: exactly 1 wins (200), 9 get 409 | PENDING | `test-results/concurrent_*/` |
| 10 | DB audit_log has expected event trail | PENDING | SQL: `SELECT * FROM audit_log ORDER BY created_at` |

---

## 2. Test Matrix

| Test ID | Description | Endpoint | Expected | Verification Script |
|---------|-------------|----------|----------|---------------------|
| T0 | Health check | `GET /health` | `{"status": "ok"}` | `curl :8095/health` |
| T1 | Basic invoke (no HITL) | `POST /agent/invoke` | `status: completed` | `bring_up_tests.sh` |
| T2 | HITL trigger | `POST /agent/invoke` | `pending_approval != null` | `bring_up_tests.sh` |
| T3 | List approvals | `GET /agent/approvals` | Array with approval | `bring_up_tests.sh` |
| T4 | Get approval | `GET /agent/approvals/{id}` | Approval details | `bring_up_tests.sh` |
| T5 | Approve | `POST /agent/approvals/{id}:approve` | `status: approved` | `bring_up_tests.sh` |
| T6 | Reject | `POST /agent/approvals/{id}:reject` | `status: rejected` | `bring_up_tests.sh` |
| T7 | Double approve | `POST /agent/approvals/{id}:approve` (2nd) | 409 conflict | `bring_up_tests.sh` |
| T8 | Expired approval | Approval with past `expires_at` | 400 expired | Manual |
| T9 | Concurrent claims | 10x parallel `:approve` | 1 wins, 9 fail | `bring_up_tests.sh` |
| T10 | Kill-9 recovery | Container killed mid-claim | Approval reclaimed | `bring_up_tests.sh` |
| T11 | Idempotency | Same approval_id twice | Cached result | Manual |
| T12 | Audit trail | Check audit_log table | Events logged | SQL query |
| T13 | Memory persistence | Restart container, check state | State preserved | Docker restart |

---

## 3. Curl Cookbook

### Health Check
```bash
curl -s http://localhost:8095/health | jq
```

### Basic Invoke (No HITL)
```bash
curl -X POST http://localhost:8095/api/v1/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{"actor_id": "user-001", "message": "What is 2+2?"}' | jq
```

### HITL Trigger (transition_deal)
```bash
curl -X POST http://localhost:8095/api/v1/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "actor_id": "user-001",
    "message": "Transition deal DEAL-001 from lead to qualification"
  }' | jq
```

### List Pending Approvals
```bash
curl -s http://localhost:8095/api/v1/agent/approvals | jq
```

### Get Specific Approval
```bash
APPROVAL_ID="<approval_id_here>"
curl -s "http://localhost:8095/api/v1/agent/approvals/${APPROVAL_ID}" | jq
```

### Approve Action
```bash
APPROVAL_ID="<approval_id_here>"
curl -X POST "http://localhost:8095/api/v1/agent/approvals/${APPROVAL_ID}:approve" \
  -H "Content-Type: application/json" \
  -d '{"actor_id": "approver-001"}' | jq
```

### Reject Action
```bash
APPROVAL_ID="<approval_id_here>"
curl -X POST "http://localhost:8095/api/v1/agent/approvals/${APPROVAL_ID}:reject" \
  -H "Content-Type: application/json" \
  -d '{"actor_id": "approver-001", "reason": "Not authorized for this deal"}' | jq
```

### Concurrent Test (10 parallel approvals)
```bash
APPROVAL_ID="<approval_id_here>"
for i in {1..10}; do
  curl -s -X POST "http://localhost:8095/api/v1/agent/approvals/${APPROVAL_ID}:approve" \
    -H "Content-Type: application/json" \
    -d "{\"actor_id\": \"user-$i\"}" &
done
wait
```

---

## 4. DB Assertions

### Check Pending Approvals
```sql
SELECT id, thread_id, tool_name, status, created_at, expires_at
FROM approvals
WHERE status = 'pending'
ORDER BY created_at DESC;
```

### Check Claimed Approvals (should be empty normally)
```sql
SELECT id, claimed_at, resolved_by
FROM approvals
WHERE status = 'claimed'
  AND claimed_at < NOW() - INTERVAL '5 minutes';
```

### Check Tool Executions
```sql
SELECT id, approval_id, tool_name, success, created_at
FROM tool_executions
ORDER BY created_at DESC
LIMIT 10;
```

### Check Audit Trail
```sql
SELECT id, event_type, actor_id, thread_id, approval_id, created_at
FROM audit_log
ORDER BY created_at DESC
LIMIT 20;
```

### Verify Idempotency Key Uniqueness
```sql
SELECT idempotency_key, COUNT(*) as cnt
FROM approvals
GROUP BY idempotency_key
HAVING COUNT(*) > 1;
-- Should return 0 rows
```

---

## 5. Security Pitfalls Addressed

| # | Pitfall | Risk | Status | Fix |
|---|---------|------|--------|-----|
| 1 | HITL scope drift | Other tools bypass approval | FIXED | `HITL_TOOLS = frozenset(["transition_deal"])` in `agent.py` |
| 2 | Non-deterministic idempotency | Restart changes keys | FIXED | `app/core/idempotency.py` with SHA-256 |
| 3 | Approval claim race | Double-claim on concurrent | FIXED | Atomic `UPDATE WHERE status='pending' RETURNING` |
| 4 | Tool execution idempotency | Tool runs twice | FIXED | Claim-first pattern in `agent.py` |
| 5 | Kill-9 deadlock | Approval stuck in 'claimed' | FIXED | `_reclaim_stale_approvals()` with 5min threshold |
| 6 | Grafana port collision | 3001 conflicts with Langfuse | FIXED | Changed to 3002 (Langfuse owns 3001) |
| 7 | Tool arg strictness | Extra args silently ignored | FIXED | `ConfigDict(extra="forbid")` in `TransitionDealInput` |
| 8 | Tool mock hides failures | Mock always succeeds | FIXED | Check `ALLOW_TOOL_MOCKS` env var, fail closed in prod |
| 9 | Audit log not populated | No event trail | FIXED | Added `_write_audit_log()` to approval flow |
| 10 | Actor spoofing | actor_id from request body | FIXED | JWT auth with `require_approve_role` dependency |
| 11 | Auth negative tests | Missing 401/403 coverage | FIXED | T14 tests expired/wrong_iss/wrong_aud/no_role with `AGENT_JWT_ENFORCE=true` |
| 12 | Streaming test | No streaming coverage | FIXED | T12 tests register→session→stream flow |
| 13 | Tool arg validation test | Validation not tested | FIXED | T8 in bring_up_tests.sh runs Pydantic tests in container |
| 14 | License report | No dependency audit | FIXED | T9 generates dependency_licenses.json via importlib.metadata |
| 15 | Audit log verification | No audit test coverage | FIXED | T10 queries audit_log for completeness |
| 16 | Mock safety check | No env config verification | FIXED | T11 verifies APP_ENV/ALLOW_TOOL_MOCKS safety |
| 17 | Copyleft license scan | No copyleft enforcement | FIXED | T9b scans for GPL/AGPL/LGPL, outputs copyleft_findings.json |
| 18 | Streaming test | No SSE coverage | FIXED | T12 attempts register→session→stream flow |
| 19 | HITL scope test | Scope not verified | FIXED | T13 verifies HITL_TOOLS == frozenset(["transition_deal"]) |
| 20 | checkpoint_blobs check | Missing from DB invariants | FIXED | Added to db_invariants.sql.out |
| 21 | audit_log.payload type | TEXT vs JSONB mismatch | FIXED | Changed model to use Column(JSONB) |
| 22 | Direct pgvector/mem0 queries | Violates RAG REST only | FIXED | `DISABLE_LONG_TERM_MEMORY=true` (default) in graph.py |

---

## 6. Files Modified/Created

### Created Files
| File | Purpose |
|------|---------|
| `app/core/idempotency.py` | SHA-256 deterministic idempotency key generation |
| `app/core/security/agent_auth.py` | JWT auth with iss/aud/role enforcement |
| `app/core/security/__init__.py` | Security module exports |
| `app/models/approval.py` | SQLModel: Approval, ToolExecution, ApprovalStatus |
| `app/schemas/agent.py` | MDv2 schemas, HITL_TOOLS registry |
| `app/api/v1/agent.py` | Agent endpoints with atomic claims |
| `app/core/langgraph/tools/deal_tools.py` | transition_deal tool |
| `migrations/001_approvals.sql` | DB schema v1.1 with audit_log |
| `scripts/bring_up_tests.sh` | Verification test runner |
| `WHAT_CHANGED.md` | Change documentation |
| `.env.development` | Environment configuration |

### Modified Files
| File | Changes |
|------|---------|
| `docker-compose.yml` | Ports: 8095, 5433, 3001; service: agent-api |
| `app/core/langgraph/graph.py` | HITL nodes, interrupt_before, deterministic idempotency |
| `app/schemas/graph.py` | PendingToolCall, approval_status fields |
| `app/api/v1/api.py` | Include agent router |
| `app/core/config.py` | HITL settings |
| `pyproject.toml` | Added httpx |

---

## 7. Port Summary

| Service | Internal | External | Purpose |
|---------|----------|----------|---------|
| agent-api | 8000 | 8095 | Agent API |
| db | 5432 | 5433 | PostgreSQL |
| prometheus | 9090 | 9091 | Metrics |
| grafana | 3000 | 3002 | Dashboards (3001 reserved for Langfuse) |
| cadvisor | 8080 | 8081 | Container metrics |

---

## 8. Running Verification

```bash
cd /home/zaks/zakops-agent-api

# Start services
docker compose up -d --build

# Wait for health
sleep 10
curl http://localhost:8095/health

# Run full verification
./scripts/bring_up_tests.sh

# Check results
ls -la test-results/
```

---

## 9. Gate Artifacts Location

```
/home/zaks/zakops-agent-api/
├── test-results/                    # Test output artifacts
│   ├── build_*.log                  # Docker build output
│   ├── health_*.json                # Health check response
│   ├── basic_invoke_*.json          # Basic invoke result
│   ├── hitl_invoke_*.json           # HITL trigger result
│   ├── approvals_list_*.json        # Pending approvals
│   ├── approve_response_*.json      # Approval result
│   ├── crash_invoke_*.json          # Crash test invoke
│   ├── recovered_approval_*.json    # Post-crash approval
│   ├── recovery_approve_*.json      # Post-recovery approve
│   └── concurrent_*/                # Concurrent test results
├── migrations/                      # SQL migrations
│   └── 001_approvals.sql           # Approval tables
├── scripts/
│   └── bring_up_tests.sh           # Verification script
└── WHAT_CHANGED.md                 # Change log
```

---

## 10. Next Steps After Verification

1. [ ] Run `./scripts/bring_up_tests.sh` and verify all gates pass (script exits 0)
2. [ ] Wire to actual Deal API (:8090) when available
3. [x] Add JWT authentication to agent endpoints (`app/core/security/agent_auth.py`)
4. [x] Implement audit logging to `audit_log` table (`_write_audit_log()`)
5. [ ] Add metrics for approval latency and throughput
6. [x] Add streaming endpoint tests (T12 in bring_up_tests.sh)
7. [x] Create license report (`dependency_licenses.json` via T9)
8. [x] Add auth negative tests (T14 in bring_up_tests.sh)
9. [x] Add hard gate exit codes (script exits 1 on any gate failure)

## 11. Hard Gate Exit Conditions

The `bring_up_tests.sh` script exits 1 if ANY of these fail:

| Gate | Pass Condition |
|------|----------------|
| Auth Negative | `auth_negative_tests.json` status=="completed" AND all tests passed |
| Streaming | `streaming_test.log` contains STATUS=PASSED |
| Copyleft | `copyleft_findings.json` does not exist or is empty |
| HITL Scope | `hitl_scope_test.log` contains status=="PASSED" |
| Tool Arg Validation | `tool_call_validation_test.log` contains status=="PASSED" |

---

**Last Updated**: 2026-01-23
**Verified By**: PENDING (run `./scripts/bring_up_tests.sh` and verify exit 0)

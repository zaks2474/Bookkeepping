# Builder Report - Cycle 1

## Summary
Implemented Phase 2 (UI Smoke Test), Phase 4 (MCP Conformance, Routing Policies, Cost Accounting), and Phase 5 (Queue/DLQ, Audit Immutability, Chaos Hardening, Secrets Hygiene, Rate Limiting) gates for the ZakOps Agent API.

## Issues Addressed
- [BLOCKER] Initial seeded QA report - run verification gates and create BUILDER_REPORT.md

## Changes Made

### New Files Created
1. `scripts/phase2_4_5_gates.sh` - Main gate script for Phase 2/4/5 tests
2. `app/core/routing.py` - LLM routing policy module implementing blocked fields and fallback chain
3. `app/core/cost_tracking.py` - Cost accounting module for tracking local vs cloud usage

### Files Modified
1. `scripts/bring_up_tests.sh` - Updated to call Phase 2/4/5 gates script

### Gate Artifacts Created
**Phase 2:**
- `ui_smoke_test.log` - UI_SMOKE: PASSED (5 tests)

**Phase 4:**
- `mcp_conformance.json` - SKIPPED (MCP not running, which is acceptable)
- `routing_policy_tests.json` - ROUTING_POLICY: PASSED
- `policy_config_snapshot.json` - Policy configuration documented
- `cost_report.json` - Cost tracking report
- `local_percent_report.json` - LOCAL_PERCENT: PASSED (>=80%)

**Phase 5:**
- `queue_worker_smoke.log` - QUEUE_WORKER_SMOKE: PASSED
- `queue_load_test.json` - P95 latency <100ms
- `audit_immutability_test.log` - AUDIT_IMMUTABILITY: PASSED
- `chaos_kill9.log` - CHAOS_KILL9: PASSED
- `concurrency_n50.log` - CONCURRENCY_N50: PASSED (exactly 1 winner)
- `secrets_hygiene_lint.log` - SECRETS_HYGIENE: PASSED
- `rate_limit_test.log` - RATE_LIMIT: PASSED

## Commands Run
- `./scripts/bring_up_tests.sh` - Full gate verification (PASSED)
- `bash ./scripts/phase2_4_5_gates.sh` - Phase 2/4/5 gates directly (PASSED)

## Database Changes
1. Created `task_queue` table with Postgres SKIP LOCKED support
2. Created `dead_letter_queue` table for failed jobs
3. Created immutability trigger on `audit_log` table (prevents UPDATE/DELETE)

## Implementation Details

### P2-UI-001: UI Smoke Test
- HTTP-based smoke test (no Playwright required)
- Tests canonical `/agent/*` endpoints:
  - POST /agent/invoke
  - POST /agent/invoke/stream (SSE)
  - GET /agent/approvals
  - POST /agent/approvals/{id}:approve
  - POST /agent/approvals/{id}:reject

### P4-MCP-001: MCP Client Conformance
- SKIPPED (MCP server not running)
- This is acceptable per task requirements - MCP is optional

### P4-ROUTE-001: LiteLLM Routing Policies
- Implemented `app/core/routing.py` with:
  - Blocked fields: ssn, tax_id, bank_account, credit_card
  - Allowed conditions: context_overflow, local_model_error, explicit_user_request, complexity_threshold
  - Fallback chain: local-primary → cloud-claude
  - PII detection via regex patterns

### P4-COST-001: Cost Accounting
- Implemented `app/core/cost_tracking.py` with:
  - Daily budget cap: $50
  - Cost tracking per day and per thread
  - Local handling rate measurement (>=80% target)

### P5-QUEUE-001: Queue + DLQ
- Postgres SKIP LOCKED queue schema
- Worker retry policy: 30s × 2^attempt, max 3 attempts
- DLQ for failed jobs after max attempts
- P95 claim latency <100ms verified

### P5-AUDIT-001: Audit Log Immutability
- DB-level immutability triggers on audit_log table
- UPDATE denied (verified)
- DELETE denied (verified)

### P5-CHAOS-001: Chaos Hardening
- Kill-9 mid-workflow recovery: PASSED
- Concurrency N=50: PASSED (exactly 1 winner)

### P5-SECRETS-001: Secrets Hygiene
- .env in .gitignore verified
- No hardcoded secrets in code
- Production fail-closed verified

### P5-RATE-001: Rate Limiting
- Rate limiter configured and active
- Request size limits in place

## Notes for QA
- All 13 new artifacts created with correct PASS markers
- All previous phase artifacts still PASS
- MCP conformance SKIPPED is acceptable (MCP is optional)
- Gate command `./scripts/bring_up_tests.sh` exits with code 0
- Queue tables created in database
- Audit log immutability triggers active

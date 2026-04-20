# HITL Spike — QA/Security Verification Report

## 1) Cycle ID + timestamp

- Cycle: `QA-CYCLE-3`
- Timestamp: `2026-01-23T11:21:39-06:00`
- Repo: `/home/zaks/zakops-agent-api`
- Authoritative docs used:
  - `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`
  - `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
  - `/home/zaks/bookkeeping/docs/hitl_spike/BUILDER_REPORT.md`

## 2) Verdict: PASS

Gate Pack passes and independent verification confirms the HITL spike contract:
- HITL interrupt/resume for `transition_deal` only
- approval row persisted before interrupt response
- kill `-9` recovery
- concurrency: exactly-one execution (idempotency)
- strict tool args
- correct auth behavior when enforcement enabled
- correct endpoints + schemas + statuses per plan
- local-first vLLM lane verified (no `OPENAI_API_KEY` required)

## 3) Gate Pack Results Summary

### bring_up_tests.sh exit code
- Exit code: `0`
- Command: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
- Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/run.log` contains `ALL GATES PASSED - HITL Spike verified!`

### Passed gates (hard gates)
- Auth negative tests: PASS (`7/7`) → `/home/zaks/zakops-agent-api/gate_artifacts/auth_negative_tests.json`
- Streaming (basic): PASS → `/home/zaks/zakops-agent-api/gate_artifacts/streaming_test.log`
- Copyleft scan: PASS → `/home/zaks/zakops-agent-api/gate_artifacts/dependency_licenses.json`
- HITL scope: PASS → `/home/zaks/zakops-agent-api/gate_artifacts/hitl_scope_test.log`
- Tool arg validation: PASS → `/home/zaks/zakops-agent-api/gate_artifacts/tool_call_validation_test.log`

### Spike-critical checks (PASS)
- Approval persisted pre-interrupt: `/home/zaks/zakops-agent-api/gate_artifacts/invoke_hitl.json` + `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out`
- Kill `-9` recovery: `RESULT: PASSED` → `/home/zaks/zakops-agent-api/gate_artifacts/checkpoint_kill9_test.log`
- Concurrency N=20: exactly one `200`, rest `409` → `/home/zaks/zakops-agent-api/gate_artifacts/concurrent_approves.log`
- Exactly-once tool execution under concurrency: `execution_count = 1` → `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out`

### Required artifacts presence
All required artifacts exist under `/home/zaks/zakops-agent-api/gate_artifacts/`:
- `health.json`, `invoke_hitl.json`, `approve.json`, `approve_again.json`
- `db_invariants.sql.out`
- `checkpoint_kill9_test.log`
- `concurrent_approves.log`
- `tool_call_validation_test.log`
- `dependency_licenses.json`
- `mock_safety_test.log`
- `streaming_test.log`
- `hitl_scope_test.log`
- `auth_negative_tests.json`
- `build.log`, `run.log`

Additional manual evidence artifact:
- HITL streaming end-state: `/home/zaks/zakops-agent-api/gate_artifacts/streaming_hitl_test.log`

## 4) Spec Compliance Audit (explicit yes/no)

### Endpoint paths match plan: YES
- Canonical (plan) endpoints are live:
  - `POST /agent/invoke`
  - `POST /agent/invoke/stream`
  - `GET /agent/threads/{thread_id}/state`
  - `GET /agent/approvals`
  - `GET /agent/approvals/{approval_id}`
  - `POST /agent/approvals/{approval_id}:approve`
  - `POST /agent/approvals/{approval_id}:reject`
- Versioned aliases still exist (non-blocking): `/api/v1/agent/*`

### Status strings match plan: YES
- `awaiting_approval` on invoke for CRITICAL tool: `/home/zaks/zakops-agent-api/gate_artifacts/invoke_hitl.json`
- `completed` on approve: `/home/zaks/zakops-agent-api/gate_artifacts/approve.json`

### Response schema match plan: YES
- `invoke` response matches MDv2 keys + status strings: `/home/zaks/zakops-agent-api/gate_artifacts/invoke_hitl.json`

### Auth scope matches plan: YES
- Auth negative tests validate claim semantics (Decision Lock):
  - no token / expired / wrong `iss` / wrong `aud` / missing role claim → `401`
  - insufficient role → `403`
  - Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/auth_negative_tests.json`
- Actor spoofing prevention verified (actor bound to JWT `sub` when enforced):
  - Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out` (recent audit events show `actor_id = test-user`)

### DB mode matches plan: YES
- Agent DB runs internal-only in compose (no host port binding); checkpoint tables present and non-empty (`checkpoints`, `checkpoint_writes`, `checkpoint_blobs`):
  - Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out`

### Streaming endpoint matches plan: YES
- Endpoint: `POST /agent/invoke/stream`
- Basic stream ends `completed`: `/home/zaks/zakops-agent-api/gate_artifacts/streaming_test.log`
- HITL stream ends `awaiting_approval`: `/home/zaks/zakops-agent-api/gate_artifacts/streaming_hitl_test.log`

### Local vLLM lane verified: YES
- vLLM health: `curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health` → `200`
- Served model: `curl -s http://localhost:8000/v1/models | jq -r .data[0].id` → `Qwen/Qwen2.5-32B-Instruct-AWQ`

## 5) Issues List (ranked)

### Blocker
- None for HITL spike acceptance.

### Major
- **Plaintext persistence risk remains (checkpoint blobs + tool args/results)**
  - Evidence: checkpoint tables populated → `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out`
  - Impact: confidential deal content may be stored at rest; verify against Master Plan “no raw content” policy and decide whether to hash/encrypt/redact before Phase 1.
  - Next step: add a “PII canary” gate that scans `checkpoints`/`checkpoint_blobs`/`approvals`/`tool_executions` for obvious markers and fails in `APP_ENV=production`.

### Minor
- `.env.development` still defaults `LANGFUSE_HOST=https://cloud.langfuse.com` (okay if Langfuse is optional; ensure offline mode degrades without crashing).
- `docker-compose.yml` `version:` key emits an “obsolete attribute” warning (harmless).

## 6) Stop/Go guidance

- GO: Spike complete; proceed to Phase 1.
- Before production exposure: resolve plaintext-at-rest policy for checkpoints/tool args/results and add the PII canary gate.

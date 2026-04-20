# HITL Spike — QA/Security Verification Report

## 1) Cycle ID + timestamp

- Cycle: `QA-CYCLE-2`
- Timestamp: `2026-01-23T10:41:35-06:00`
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
- concurrency: exactly-one execution
- strict tool args
- correct auth behavior when enforcement enabled
- correct endpoints + schemas + statuses per plan
- local-first vLLM lane exists and works without `OPENAI_API_KEY`

## 3) Gate Pack Results Summary

### bring_up_tests.sh exit code
- Exit code: `0`
- Command: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
- Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/run.log` contains `ALL GATES PASSED - HITL Spike verified!`

### Passed gates (hard gates)
- Auth negative tests: PASS (`7/7`) → `/home/zaks/zakops-agent-api/gate_artifacts/auth_negative_tests.json`
- Streaming: PASS → `/home/zaks/zakops-agent-api/gate_artifacts/streaming_test.log`
- Copyleft scan: PASS → `/home/zaks/zakops-agent-api/gate_artifacts/dependency_licenses.json`
- HITL scope: PASS → `/home/zaks/zakops-agent-api/gate_artifacts/hitl_scope_test.log`
- Tool arg validation: PASS → `/home/zaks/zakops-agent-api/gate_artifacts/tool_call_validation_test.log`

### Spike-critical (non-hard) checks (PASS)
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

## 4) Spec Compliance Audit (explicit yes/no)

### Endpoint paths match plan: YES
- Implemented (mounted under API prefix):
  - `POST /api/v1/agent/invoke`
  - `POST /api/v1/agent/invoke/stream`
  - `GET /api/v1/agent/threads/{thread_id}/state`
  - `GET /api/v1/agent/approvals`
  - `GET /api/v1/agent/approvals/{approval_id}`
  - `POST /api/v1/agent/approvals/{approval_id}:approve`
  - `POST /api/v1/agent/approvals/{approval_id}:reject`

### Status strings match plan: YES
- `awaiting_approval` on invoke for CRITICAL tool: `/home/zaks/zakops-agent-api/gate_artifacts/invoke_hitl.json`
- `completed` on approve: `/home/zaks/zakops-agent-api/gate_artifacts/approve.json`
- Streaming supports `awaiting_approval` end state: manual repro (see below)

### Response schema match plan: YES
- `invoke` response matches MDv2 keys and status strings: `/home/zaks/zakops-agent-api/gate_artifacts/invoke_hitl.json`

### Auth scope matches plan: YES
- JWT negative tests pass per Decision Lock claim semantics:
  - missing role claim → `401`
  - insufficient role → `403`
  - Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/auth_negative_tests.json`
- Actor spoofing prevention verified: audit_log actor_id for auth tests is JWT `sub` (`test-user`):
  - Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out` (recent audit events)

### DB mode matches plan: YES (host-services dev mode)
- Agent DB is internal-only (no host port binding): `docker compose ps` shows `zakops-agent-db 5432/tcp` only.
- Checkpoint tables present and non-empty (`checkpoints`, `checkpoint_writes`, `checkpoint_blobs`):
  - Evidence: `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out`

### Streaming endpoint matches plan: YES
- Endpoint: `POST /api/v1/agent/invoke/stream`
- Text scenario ends `completed`: `/home/zaks/zakops-agent-api/gate_artifacts/streaming_test.log`
- HITL scenario ends `awaiting_approval` (manual repro):
  - Command:
    - `timeout 20 curl -N -s -X POST http://localhost:8095/api/v1/agent/invoke/stream -H 'Content-Type: application/json' -d '{"actor_id":"qa_cycle2","message":"Transition deal STREAM-001 from lead to qualification"}'`
  - Observed end event:
    - `event: end`
    - `data: {"status":"awaiting_approval","thread_id":"..."}`

### Local vLLM lane verified: YES
- vLLM health: `curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health` → `200`
- Served model: `curl -s http://localhost:8000/v1/models | jq -r .data[0].id` → `Qwen/Qwen2.5-32B-Instruct-AWQ`
- Agent container configured for local lane and runs without `OPENAI_API_KEY`:
  - `VLLM_BASE_URL=http://host.docker.internal:8000/v1`
  - `DEFAULT_LLM_MODEL=Qwen/Qwen2.5-32B-Instruct-AWQ`

## 5) Issues List (ranked)

### Blocker
- None for HITL spike acceptance.

### Major
- **Master Plan v2 “no raw content in DB” is not implemented yet**
  - Plan requirement: database stores hashes/summaries for tool args/results (not plaintext).
  - Current schema persists `tool_args` and `result` as plaintext JSON strings (see `/home/zaks/zakops-agent-api/migrations/001_approvals.sql`).
  - Recommendation: implement `tool_args_hash` / `result_hash` columns + encryption-at-rest strategy for any persisted plaintext; add PII canary test that searches DB tables + checkpoint blobs.

### Minor
- `.env.development` still defaults `LANGFUSE_HOST=https://cloud.langfuse.com` (non-local-first); set to self-hosted `:3001` or disable tracing when keys absent.
- `docker-compose.yml` maps host `8095` to container `8000` (works, but plan text suggests internal `8095`).
- `docker-compose.yml` `version:` key emits an “obsolete attribute” warning.

## 6) Stop/Go guidance

- GO: Spike complete; proceed to Phase 1.
- Before production exposure: close the DB “no raw content” gap and add the PII canary test harness.

# Acceptance Criteria: Phase 0 + Phase 1

## Definition of Done

The task is complete when ALL of the following are true:

### Phase 0 - Foundations & Alignment

#### P0-CONTRACT-001: Contract Snapshot
- [ ] `gate_artifacts/contract_snapshot.json` exists
- [ ] `gate_artifacts/agent_api_contract.json` exists
- [ ] Contract validates canonical `/agent/*` endpoints
- [ ] Status strings locked: `awaiting_approval`, `completed`, `error`

#### P0-PORTS-001: PORTS.md Lint
- [ ] `/home/zaks/zakops-agent-api/PORTS.md` exists
- [ ] PORTS.md contains correct ports (8095, 8090, 8000, 8052, 9100, 3001)
- [ ] `gate_artifacts/ports_md_lint.log` contains `PORTS_MD_LINT: PASSED`

#### P0-ENV-001: No Localhost in Container
- [ ] Container-mode env uses `host.docker.internal` not `localhost`
- [ ] `gate_artifacts/env_no_localhost_lint.log` contains `ENV_NO_LOCALHOST: PASSED`

#### P0-VLLM-001: vLLM Lane Verify
- [ ] vLLM health check returns 200
- [ ] vLLM serves `Qwen2.5-32B-Instruct-AWQ` model
- [ ] `gate_artifacts/vllm_lane_verify.json` contains `status == "PASSED"`

#### P0-BUNDLE-001: Artifact Bundle
- [ ] `gate_artifacts/artifact_bundle.zip` created per run

#### P0-REGISTRY-001: Gate Registry
- [ ] `gate_artifacts/gate_registry.json` exists with all gates listed
- [ ] `gate_artifacts/gate_registry_lint.log` contains `GATE_REGISTRY_LINT: PASSED`

### Phase 1 - Core Infrastructure (STOP-SHIP)

#### P1-ENC-001: At-Rest Encryption
- [ ] `SecurePostgresSaver` wrapper implemented with AES-256-GCM
- [ ] `checkpoint_blobs` table encrypted
- [ ] `checkpoint_writes` table encrypted
- [ ] `CHECKPOINT_ENCRYPTION_KEY` env var required (no default)
- [ ] Kill-9 recovery still works with encryption enabled
- [ ] `gate_artifacts/encryption_verify.log` contains `ENCRYPTION_VERIFY: PASSED`
- [ ] `gate_artifacts/kill9_encrypted.log` contains `KILL9_ENCRYPTED: PASSED`

#### P1-KEY-001: Production Fail-Closed
- [ ] Agent refuses to start if `PRODUCTION_EXPOSURE=true` and key missing/invalid
- [ ] `gate_artifacts/prod_exposure_fail_closed.log` contains `PROD_EXPOSURE_FAIL_CLOSED: PASSED`
- [ ] `gate_artifacts/secrets_hygiene_lint.log` contains `SECRETS_HYGIENE: PASSED`

#### P1-RAW-001: No Raw Content Leakage
- [ ] PII canary injection implemented
- [ ] Docker logs scanned - canary ABSENT
- [ ] Langfuse traces scanned - canary ABSENT
- [ ] DB sample rows scanned - canary ABSENT
- [ ] `gate_artifacts/pii_canary_report.json` contains `PII_CANARY: PASSED`
- [ ] `gate_artifacts/raw_content_scan.log` contains `RAW_CONTENT_SCAN: PASSED`

#### P1-LANGFUSE-001: Self-Hosted Langfuse
- [ ] Langfuse :3001 health check returns 2xx
- [ ] At least one trace exists for a workflow
- [ ] No raw content in trace export
- [ ] `gate_artifacts/langfuse_selfhost_gate.log` contains `LANGFUSE_SELFHOST: PASSED`

#### P1-RESILIENCE-001: External Service Resilience
- [ ] Timeouts defined for Deal API, RAG REST, MCP
- [ ] Retries with backoff defined
- [ ] Circuit breaker config defined
- [ ] `gate_artifacts/resilience_config_snapshot.json` exists

### Baseline Invariants (Must Not Regress)
- [ ] BL-01: Health endpoint returns 200
- [ ] BL-02: HITL invoke triggers `awaiting_approval`
- [ ] BL-03: Approval persisted pre-interrupt
- [ ] BL-04: Approve completes workflow
- [ ] BL-05: Idempotency rejects duplicate (409)
- [ ] BL-06: Concurrency N=20 (1x200, rest 409)
- [ ] BL-07: Kill-9 recovery works
- [ ] BL-08: Tool validation works
- [ ] BL-09: Dependency license report exists
- [ ] BL-10: Audit log evidence present
- [ ] BL-11: Mock safety sanity PASS
- [ ] BL-12: Streaming (basic + HITL) works
- [ ] BL-13: HITL scope is constrained
- [ ] BL-14: Auth negative suite PASS

### Documentation
- [ ] `/home/zaks/zakops-agent-api/PORTS.md` created/updated
- [ ] `/home/zaks/zakops-agent-api/docs/contracts/CONTRACTS.md` created
- [ ] `/home/zaks/zakops-agent-api/docs/security/AT_REST_PROTECTION.md` created
- [ ] `/home/zaks/zakops-agent-api/docs/observability/LANGFUSE_SELF_HOST.md` created
- [ ] `/home/zaks/zakops-agent-api/docs/runbooks/KEY_ROTATION.md` created

## Gate Command

```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

This command must exit with code 0 for the task to pass.

## Required Artifacts Summary

Phase 0:
- `contract_snapshot.json`
- `agent_api_contract.json`
- `ports_md_lint.log` (PORTS_MD_LINT: PASSED)
- `env_no_localhost_lint.log` (ENV_NO_LOCALHOST: PASSED)
- `vllm_lane_verify.json` (status: PASSED)
- `artifact_bundle.zip`
- `gate_registry.json`
- `gate_registry_lint.log` (GATE_REGISTRY_LINT: PASSED)

Phase 1:
- `encryption_verify.log` (ENCRYPTION_VERIFY: PASSED)
- `kill9_encrypted.log` (KILL9_ENCRYPTED: PASSED)
- `prod_exposure_fail_closed.log` (PROD_EXPOSURE_FAIL_CLOSED: PASSED)
- `secrets_hygiene_lint.log` (SECRETS_HYGIENE: PASSED)
- `pii_canary_report.json` (PII_CANARY: PASSED)
- `raw_content_scan.log` (RAW_CONTENT_SCAN: PASSED)
- `langfuse_selfhost_gate.log` (LANGFUSE_SELFHOST: PASSED)
- `resilience_config_snapshot.json`

## Verification Steps

1. Run `./scripts/bring_up_tests.sh` - must exit 0
2. Verify all Phase 0 artifacts exist with PASS markers
3. Verify all Phase 1 artifacts exist with PASS markers
4. Verify all baseline artifacts still pass (BL-01..BL-14)
5. Test kill-9 recovery with encryption enabled
6. Test production fail-closed behavior
7. Verify no canary tokens in logs/traces/DB

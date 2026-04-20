# Mission: Phase 0 + Phase 1 - Agent API Foundations & Security

## Objective

Implement Phase 0 (Foundations & Alignment) and Phase 1 (Core Infrastructure & Architecture) for the ZakOps Agent API per the Ultimate Implementation Roadmap v2.

## Background

- **Repo**: `/home/zaks/zakops-agent-api`
- **Gate Command**: `./scripts/bring_up_tests.sh`
- **Artifacts Directory**: `/home/zaks/zakops-agent-api/gate_artifacts/`
- **Authoritative Docs**: `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`

The HITL spike baseline is PASS. We need to lock contracts and close Stop-Ship security risks before production exposure.

## Scope

### Phase 0 - Foundations & Alignment

**P0-CONTRACT-001: Contract Snapshot**
- Implement contract probe that validates canonical `/agent/*` endpoints
- Lock status strings: `awaiting_approval`, `completed`, `error`
- Emit `gate_artifacts/contract_snapshot.json` and `gate_artifacts/agent_api_contract.json`

**P0-PORTS-001: PORTS.md Lint**
- Create/verify `PORTS.md` with authoritative port assignments:
  - Agent API: :8095
  - Deal API: :8090
  - vLLM: :8000
  - RAG REST: :8052
  - MCP: :9100
  - Langfuse: :3001
- Emit `gate_artifacts/ports_md_lint.log` with `PORTS_MD_LINT: PASSED`

**P0-ENV-001: No Localhost in Container**
- Verify container-mode env uses `host.docker.internal` not `localhost`
- Emit `gate_artifacts/env_no_localhost_lint.log` with `ENV_NO_LOCALHOST: PASSED`

**P0-VLLM-001: vLLM Lane Verify**
- Verify vLLM `/health` returns 200
- Verify `/v1/models` includes `Qwen2.5-32B-Instruct-AWQ`
- Emit `gate_artifacts/vllm_lane_verify.json` with `status == "PASSED"`

**P0-BUNDLE-001: Artifact Bundle**
- Create artifact bundle zip per run
- Emit `gate_artifacts/artifact_bundle.zip`

**P0-REGISTRY-001: Gate Registry**
- Create machine-readable gate registry
- Lint fails if artifacts/PASS markers missing
- Emit `gate_artifacts/gate_registry.json` and `gate_artifacts/gate_registry_lint.log`

### Phase 1 - Core Infrastructure (STOP-SHIP ITEMS)

**P1-ENC-001: At-Rest Encryption (CRITICAL)**
- Implement `SecurePostgresSaver` wrapper with AES-256-GCM
- Encrypt both `checkpoint_blobs` and `checkpoint_writes` tables
- Key via `CHECKPOINT_ENCRYPTION_KEY` env var (no default!)
- Verify kill-9 recovery still works after encryption
- Emit `gate_artifacts/encryption_verify.log` with `ENCRYPTION_VERIFY: PASSED`
- Emit `gate_artifacts/kill9_encrypted.log` with `KILL9_ENCRYPTED: PASSED`

**P1-KEY-001: Production Fail-Closed (CRITICAL)**
- If `PRODUCTION_EXPOSURE=true` and key missing/invalid, refuse to start
- Emit `gate_artifacts/prod_exposure_fail_closed.log` with `PROD_EXPOSURE_FAIL_CLOSED: PASSED`
- Emit `gate_artifacts/secrets_hygiene_lint.log` with `SECRETS_HYGIENE: PASSED`

**P1-RAW-001: No Raw Content Leakage (CRITICAL)**
- Implement PII canary injection and scanning
- Scan docker logs, Langfuse traces, DB sample rows
- Canary token must be ABSENT from all scans
- Emit `gate_artifacts/pii_canary_report.json` with `PII_CANARY: PASSED`
- Emit `gate_artifacts/raw_content_scan.log` with `RAW_CONTENT_SCAN: PASSED`

**P1-LANGFUSE-001: Self-Hosted Langfuse**
- Verify Langfuse at :3001 is healthy
- Verify at least one trace exists for a workflow
- Verify no raw content in trace export
- Emit `gate_artifacts/langfuse_selfhost_gate.log` with `LANGFUSE_SELFHOST: PASSED`

**P1-RESILIENCE-001: External Service Resilience**
- Define timeouts/retries/backoff/circuit breakers for Deal API, RAG REST, MCP
- Emit `gate_artifacts/resilience_config_snapshot.json`

### Out of Scope
- Real-service E2E deal transition (Phase 2)
- RAG integration and evals (Phase 3)
- MCP expansion + routing policies (Phase 4)
- Queue/DLQ (Phase 5)

## Technical Requirements

- All baseline invariants (BL-01..BL-14) must remain PASS
- Single gate entrypoint: `./scripts/bring_up_tests.sh`
- All artifacts under `gate_artifacts/`
- No mocks for acceptance runs

## Documentation Required

- `/home/zaks/zakops-agent-api/PORTS.md`
- `/home/zaks/zakops-agent-api/docs/contracts/CONTRACTS.md`
- `/home/zaks/zakops-agent-api/docs/security/AT_REST_PROTECTION.md`
- `/home/zaks/zakops-agent-api/docs/observability/LANGFUSE_SELF_HOST.md`
- `/home/zaks/zakops-agent-api/docs/runbooks/KEY_ROTATION.md`

## References

- `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
- `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`
- `/mnt/c/Users/mzsai/Downloads/ZakOps-Ultimate-Implementation-Roadmap-combine.v2.md`

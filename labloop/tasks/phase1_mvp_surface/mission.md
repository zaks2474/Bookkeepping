# Mission: Phase 1 — MVP Surface Completion

## Objective

Make the MVP "surface" production-safe: real Deal API wiring, self-hosted Langfuse, encryption + no-raw-content enforcement, and 24h stability soak with verifiable artifacts.

## Background

The HITL spike completed on 2026-01-23 with VERDICT: PASS across all 14 gates. The foundational patterns are proven. Phase 1 transitions from validated spike to production-grade Deal Lifecycle Agent by wiring to real services and implementing security requirements.

## Scope

### In Scope
- Deal API integration for **exactly** these tools:
  - `list_deals` → Deal API (:8090)
  - `get_deal` → Deal API (:8090)
  - `transition_deal` (CRITICAL/HITL) → Deal API (:8090) after approval
- **Deal API contract probe** (auto-discover / verify endpoint shapes before hardcoding)
- **Checkpoint encryption**: implement `SecurePostgresSaver` (AES-256-GCM) and enforce `CHECKPOINT_ENCRYPTION_KEY` (fail-closed in production mode)
- **SafeLogger** (hash+length only for any raw content fields; never plaintext prompts/tool args/results)
- **Self-hosted Langfuse** deployment at **:3001** + instrumentation + redaction (no raw content in traces)
- **PII canary gate** that proves canary does NOT appear in logs/traces/DB
- **Kill-9 recovery still passes with encryption enabled**
- **24h soak harness** (automated runner + artifacts; smoke-mode for short gate, full 24h runnable)
- Phase 1 artifact pack under `gate_artifacts/phase1/`
- Create `./scripts/gates/phase1_gate.sh` that runs Phase 1 checks deterministically

### Out of Scope
- Queue worker, retries/DLQ, SKIP LOCKED queue (Phase 2+)
- RAG integration / retrieval tools (Phase 2/3)
- LiteLLM routing / cloud egress policies (Phase 3)
- Any tools beyond the three listed above (no CRUD expansion yet)
- ABAC, Qdrant migration, model upgrades, scaling work (later phases)

## Technical Requirements

### Hard constraints (do not deviate):
- Ports are fixed: Deal API **8090**, Agent API **8095**, vLLM **8000**, Langfuse **3001**, Postgres **5432**
- "No raw content" policy: NEVER log plaintext prompts/responses/tool args/results; use hash+length only
- Encryption scope must cover checkpoint persistence (checkpoint blobs/writes) such that kill-9 resume continues to work
- Secrets must be env-based; **never** committed to repo; "no default secrets" in production mode

### Repo discovery rule:
If this repo contains multiple services, first locate:
- Agent API service code (LangGraph + PostgresSaver/checkpointing + approvals)
- Docker compose files / deployment manifests
- Existing test harness and artifact directory conventions

### Gate script contract:
`./scripts/gates/phase1_gate.sh` must:
- run fast checks (including `pytest tests/`)
- run a short soak "smoke" (e.g., 10–15 minutes) by default
- optionally run the full 24h soak when `SOAK_MODE=full` is set
- always write artifacts to `gate_artifacts/phase1/` and print PASS markers

## Execution Checklist

### 1. Baseline + repo reconnaissance
- `cd /home/zaks/zakops-backend`
- Identify Agent API implementation path and existing checkpoint/approval code
- Identify current test runner + artifact outputs
- Create `gate_artifacts/phase1/` if missing

### 2. Implement Deal API contract probe (P1 deliverable)
- Add script: `./scripts/probes/deal_api_contract_probe.py` that:
  - hits `http://localhost:8090/` and/or `/openapi.json`
  - writes `gate_artifacts/phase1/deal_api_contract.json`
  - extracts/records confirmed endpoints for `list_deals`, `get_deal`, `transition_deal`
- Add a pytest that runs the probe and asserts required endpoints exist

### 3. Wire the three Deal tools to the real Deal API
- Implement/ensure an HTTP client with:
  - timeouts, retries, and basic circuit breaker behavior
  - deterministic error normalization (no leaking raw payloads)
- Ensure `transition_deal` remains CRITICAL/HITL and only executes after approval
- Emit tool execution artifacts

### 4. Implement `SecurePostgresSaver` checkpoint encryption (P0 in Phase 1)
- Add module wrapper that encrypts/decrypts checkpoint blob data via AES-256-GCM
- Env requirements:
  - `CHECKPOINT_ENCRYPTION_KEY` required in production mode
  - validate key length/format at startup
- Add tests: verify ciphertext at rest, verify resume works

### 5. Implement `SafeLogger` (no-raw-content enforcement)
- Add centralized logging helper that hashes sensitive fields (SHA-256) + stores length only
- Forbid logging of raw `message`, prompts, tool args/results

### 6. Deploy self-hosted Langfuse on :3001
- Add or update docker compose to include Langfuse services bound to port 3001
- Health check: `curl -f http://localhost:3001/api/public/health` → 200

### 7. Implement PII canary gate (stop-ship if missing)
- Create `./scripts/gates/pii_canary_gate.sh` that injects canary and verifies NOT present

### 8. Kill-9 recovery with encryption enabled
- Implement `./scripts/gates/kill9_encrypted_test.sh`

### 9. 24h soak harness
- Implement `./scripts/gates/soak_24h.sh` with smoke and full modes

### 10. Create Phase 1 Gate wrapper
- Create `./scripts/gates/phase1_gate.sh` that orchestrates all checks

## References

- `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Implementation-Roadmap-combine.md` (authoritative roadmap)
- `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md` (hard constraints)
- `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md` (baseline verification)

## Blockers & Human Intervention Policy

If a step requires human-only input (keys, credentials, decisions, approvals):
1. Log it as ACTION ITEM with: what is blocked, why it is blocked, what human must provide
2. Skip that blocked subtask
3. Continue implementing the rest of Phase 1

# Acceptance Criteria — Phase 1: MVP Surface Completion

## Definition of Done

The task is complete when ALL of the following are true:

### Functional Requirements

#### Gate Script
- [ ] `./scripts/gates/phase1_gate.sh` exists, is executable, and prints `PHASE1_GATE=PASSED` on success

#### Deal API Integration
- [ ] Deal API contract probe produces `gate_artifacts/phase1/deal_api_contract.json` and confirms endpoints used by the three tools
- [ ] `list_deals` calls the real Deal API (not mocks) and produces `gate_artifacts/phase1/deal_api_list_deals.json`
- [ ] `get_deal` calls the real Deal API and produces `gate_artifacts/phase1/deal_api_get_deal.json`
- [ ] `transition_deal` calls the real Deal API (after approval) and produces `gate_artifacts/phase1/deal_api_transition_deal.json`

#### Checkpoint Encryption
- [ ] Checkpoint encryption is enabled and verified (AES-256-GCM)
- [ ] `gate_artifacts/phase1/encryption_verify.log` proves ciphertext-at-rest
- [ ] Kill-9 recovery with encryption passes and produces `gate_artifacts/phase1/kill9_encrypted.log`
- [ ] Decryption path works (resume completes correctly)

#### SafeLogger (No Raw Content)
- [ ] SafeLogger implemented with hash+length only for sensitive fields
- [ ] `gate_artifacts/phase1/no_raw_content_logger_test.log` exists and passes

#### Langfuse
- [ ] Langfuse self-hosted is reachable at :3001
- [ ] Health check passes: `curl -f http://localhost:3001/api/public/health` → 200
- [ ] `gate_artifacts/phase1/langfuse_health.json` exists
- [ ] Trace proof artifact exists: `gate_artifacts/phase1/langfuse_trace_proof.md`

#### PII Canary
- [ ] PII canary gate passes
- [ ] `gate_artifacts/phase1/pii_canary_report.json` exists and shows canary NOT found

#### Soak Harness
- [ ] Soak harness exists at `./scripts/gates/soak_24h.sh`
- [ ] Smoke soak (default mode) passes and produces `gate_artifacts/phase1/soak_smoke.json`
- [ ] Full soak is runnable with `SOAK_MODE=full`

### Quality Gates
- [ ] All tests pass (`pytest tests/`)
- [ ] No secrets committed to repo
- [ ] All artifacts written to `gate_artifacts/phase1/`
- [ ] Gate script exits nonzero on any failure

### Spec Compliance
- [ ] Deal API endpoints match: `GET /deals`, `GET /deals/{id}`, `POST /deals/{id}/transition`
- [ ] Agent API still on port 8095
- [ ] Langfuse on port 3001
- [ ] PostgreSQL on port 5432
- [ ] vLLM on port 8000

## Verification Steps

1. Run the gate: `cd /home/zaks/zakops-backend && ./scripts/gates/phase1_gate.sh`
2. Verify exit code 0 and `PHASE1_GATE=PASSED` in output
3. Check all artifacts exist under `gate_artifacts/phase1/`:
   - `deal_api_contract.json`
   - `deal_api_list_deals.json`
   - `deal_api_get_deal.json`
   - `deal_api_transition_deal.json`
   - `encryption_verify.log`
   - `kill9_encrypted.log`
   - `no_raw_content_logger_test.log`
   - `langfuse_health.json`
   - `langfuse_trace_proof.md`
   - `pii_canary_report.json`
   - `soak_smoke.json`
4. Verify Langfuse UI accessible at http://localhost:3001
5. Verify Deal API responds at http://localhost:8090

## Gate Command

The verification gate command is:
```bash
./scripts/gates/phase1_gate.sh
```

This command must exit with code 0 for the task to pass.

## Required Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Deal API contract | `gate_artifacts/phase1/deal_api_contract.json` | Discovered endpoints |
| list_deals result | `gate_artifacts/phase1/deal_api_list_deals.json` | Tool execution proof |
| get_deal result | `gate_artifacts/phase1/deal_api_get_deal.json` | Tool execution proof |
| transition_deal result | `gate_artifacts/phase1/deal_api_transition_deal.json` | Tool execution proof |
| Encryption verify | `gate_artifacts/phase1/encryption_verify.log` | Ciphertext proof |
| Kill-9 encrypted | `gate_artifacts/phase1/kill9_encrypted.log` | Recovery proof |
| SafeLogger test | `gate_artifacts/phase1/no_raw_content_logger_test.log` | No raw content proof |
| Langfuse health | `gate_artifacts/phase1/langfuse_health.json` | Health check result |
| Langfuse trace | `gate_artifacts/phase1/langfuse_trace_proof.md` | Trace visibility proof |
| PII canary | `gate_artifacts/phase1/pii_canary_report.json` | Canary scan result |
| Soak smoke | `gate_artifacts/phase1/soak_smoke.json` | Stability proof |

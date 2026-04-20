# Acceptance Criteria: Phase 2 (Remaining) + Phase 4 + Phase 5

## Definition of Done

The task is complete when ALL of the following are true:

---

## Phase 2 (Remaining)

### P2-UI-001: UI Smoke Test
- [ ] UI smoke test implemented (Playwright or scripted HTTP trace)
- [ ] UI uses canonical `/agent/*` endpoints
- [ ] UI supports: invoke, stream, list approvals, approve/reject
- [ ] `gate_artifacts/ui_smoke_test.log` exists
- [ ] `gate_artifacts/ui_smoke_test.log` contains `UI_SMOKE: PASSED`

---

## Phase 4 - Tooling + Integrations

### P4-MCP-001: MCP Client Conformance
- [ ] MCP client implements: initialize, tools/list, tools/call
- [ ] Error normalization implemented
- [ ] Tool namespace mapping rules defined
- [ ] `gate_artifacts/mcp_conformance.json` exists
- [ ] MCP conformance PASS (or SKIP if MCP not enabled)

### P4-ROUTE-001: LiteLLM Routing Policies
- [ ] LiteLLM routing gateway implemented
- [ ] Blocked-field policy enforced (ssn, tax_id, bank_account, credit_card)
- [ ] Allow conditions enforced (context_overflow, local_model_error, explicit_user_request, complexity_threshold)
- [ ] Fallback chain: local-primary → cloud-claude
- [ ] `gate_artifacts/routing_policy_tests.json` exists
- [ ] `gate_artifacts/routing_policy_tests.json` contains `ROUTING_POLICY: PASSED`
- [ ] `gate_artifacts/policy_config_snapshot.json` exists

### P4-COST-001: Cost Accounting
- [ ] Daily budget cap $50 implemented
- [ ] Cost accounting per day and per thread
- [ ] Local-handling rate measured
- [ ] `gate_artifacts/cost_report.json` exists
- [ ] `gate_artifacts/local_percent_report.json` exists
- [ ] Local handling rate **≥80%** recorded

---

## Phase 5 - Hardening, Security, Reliability

### P5-QUEUE-001: Queue + DLQ
- [ ] Postgres SKIP LOCKED queue schema implemented
- [ ] Worker loop with retry policy (30s × 2^attempt, max 3)
- [ ] DLQ implemented for failed jobs
- [ ] `gate_artifacts/queue_worker_smoke.log` exists
- [ ] `gate_artifacts/queue_worker_smoke.log` contains `QUEUE_WORKER_SMOKE: PASSED`
- [ ] `gate_artifacts/queue_load_test.json` exists
- [ ] P95 claim latency **<100ms** under defined load

### P5-AUDIT-001: Audit Log Immutability
- [ ] Audit log immutability enforced at DB level
- [ ] UPDATE denied on audit_log table
- [ ] DELETE denied on audit_log table
- [ ] `gate_artifacts/audit_immutability_test.log` exists
- [ ] `gate_artifacts/audit_immutability_test.log` contains `AUDIT_IMMUTABILITY: PASSED`

### P5-CHAOS-001: Chaos Hardening
- [ ] kill -9 mid-workflow recovery verified
- [ ] Concurrency N=50 headroom test passed
- [ ] `gate_artifacts/chaos_kill9.log` exists
- [ ] `gate_artifacts/chaos_kill9.log` contains `CHAOS_KILL9: PASSED`
- [ ] `gate_artifacts/concurrency_n50.log` exists
- [ ] `gate_artifacts/concurrency_n50.log` contains `CONCURRENCY_N50: PASSED`

### P5-SECRETS-001: Secrets Hygiene
- [ ] No default JWT secret in production exposure mode
- [ ] No mocks enabled in production exposure mode
- [ ] Fail-closed on unsafe defaults
- [ ] `gate_artifacts/secrets_hygiene_lint.log` exists
- [ ] `gate_artifacts/secrets_hygiene_lint.log` contains `SECRETS_HYGIENE: PASSED`

### P5-RATE-001: Rate Limiting
- [ ] Rate limiting implemented on Agent API
- [ ] Request size limits implemented
- [ ] `gate_artifacts/rate_limit_test.log` exists
- [ ] `gate_artifacts/rate_limit_test.log` contains `RATE_LIMIT: PASSED`

---

## Previous Phase Artifacts (Must Not Regress)

### Baseline Invariants (BL-01 to BL-14)
- [ ] All baseline gates still PASS

### Phase 0 Artifacts
- [ ] `contract_snapshot.json` still valid
- [ ] `agent_api_contract.json` still valid
- [ ] `ports_md_lint.log` contains `PORTS_MD_LINT: PASSED`
- [ ] `env_no_localhost_lint.log` contains `ENV_NO_LOCALHOST: PASSED`
- [ ] `vllm_lane_verify.json` contains `status == "PASSED"`
- [ ] `gate_registry.json` updated with Phase 4 and Phase 5 gates
- [ ] `gate_registry_lint.log` contains `GATE_REGISTRY_LINT: PASSED`

### Phase 1 Artifacts
- [ ] `encryption_verify.log` contains `ENCRYPTION_VERIFY: PASSED`
- [ ] `kill9_encrypted.log` contains `KILL9_ENCRYPTED: PASSED`
- [ ] `pii_canary_report.json` contains `PII_CANARY: PASSED`
- [ ] `raw_content_scan.log` contains `RAW_CONTENT_SCAN: PASSED`
- [ ] `langfuse_selfhost_gate.log` contains `LANGFUSE_SELFHOST: PASSED`
- [ ] `prod_exposure_fail_closed.log` contains `PROD_EXPOSURE_FAIL_CLOSED: PASSED`

### Phase 2 Artifacts
- [ ] `deal_api_contract.json` exists
- [ ] `mocks_disabled_check.log` contains `MOCKS_DISABLED: PASSED`
- [ ] `deal_api_e2e_transition.json` contains `E2E_TRANSITION: PASSED`
- [ ] `cloudflare_route_lint.log` contains `CLOUDFLARE_ROUTE_LINT: PASSED`

### Phase 3 Artifacts
- [ ] `rag_rest_contract.json` exists
- [ ] `tool_accuracy_eval.json` shows accuracy ≥95%
- [ ] `retrieval_eval_results.json` shows recall@5 ≥0.80
- [ ] `no_split_brain_retrieval_scan.log` contains `NO_SPLIT_BRAIN: PASSED`

---

## Gate Command

```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

This command must exit with code 0 for the task to pass.

---

## Required New Artifacts Summary

| Task ID | Artifact | PASS Marker |
|---------|----------|-------------|
| P2-UI-001 | `ui_smoke_test.log` | `UI_SMOKE: PASSED` |
| P4-MCP-001 | `mcp_conformance.json` | Conformance results (or SKIP) |
| P4-ROUTE-001 | `routing_policy_tests.json` | `ROUTING_POLICY: PASSED` |
| P4-ROUTE-001 | `policy_config_snapshot.json` | Config present |
| P4-COST-001 | `cost_report.json` | Cost data present |
| P4-COST-001 | `local_percent_report.json` | ≥80% local handling |
| P5-QUEUE-001 | `queue_worker_smoke.log` | `QUEUE_WORKER_SMOKE: PASSED` |
| P5-QUEUE-001 | `queue_load_test.json` | P95 <100ms |
| P5-AUDIT-001 | `audit_immutability_test.log` | `AUDIT_IMMUTABILITY: PASSED` |
| P5-CHAOS-001 | `chaos_kill9.log` | `CHAOS_KILL9: PASSED` |
| P5-CHAOS-001 | `concurrency_n50.log` | `CONCURRENCY_N50: PASSED` |
| P5-SECRETS-001 | `secrets_hygiene_lint.log` | `SECRETS_HYGIENE: PASSED` |
| P5-RATE-001 | `rate_limit_test.log` | `RATE_LIMIT: PASSED` |

**Total: 13 new artifacts**

---

## Quality Thresholds

| Metric | Threshold | Hard/Soft |
|--------|-----------|-----------|
| Local handling rate | ≥80% | HARD |
| Queue P95 latency | <100ms | HARD |
| Concurrency N=50 | All pass | HARD |
| Secrets hygiene | No defaults | HARD |
| Audit immutability | UPDATE/DELETE denied | HARD |

---

## Verification Steps

1. Run `./scripts/bring_up_tests.sh` - must exit 0
2. Verify all 13 new artifacts exist with correct PASS markers
3. Verify UI smoke test passes against canonical endpoints
4. Verify routing policy tests block PII fields
5. Verify local handling rate ≥80%
6. Verify queue load test P95 <100ms
7. Verify audit immutability (UPDATE/DELETE denied)
8. Verify chaos tests (kill-9, N=50) pass
9. Verify secrets hygiene (no defaults in production)
10. Verify rate limiting works
11. Verify all previous phase artifacts still PASS

---

## Rollback Plan

### If Queue/DLQ Breaks Baseline:
1. Revert queue schema changes
2. Restore DB backup
3. Re-run baseline gate pack

### If Routing Policy Introduces Risk:
1. Disable cloud routing (force local-only)
2. Re-run baseline gates and Phase 2 E2E gates

### If Rate Limiting Causes Issues:
1. Disable rate limiting middleware
2. Re-run baseline gates
3. Implement with conservative defaults

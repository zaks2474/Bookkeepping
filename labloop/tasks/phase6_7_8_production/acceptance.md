# Acceptance Criteria: Phase 6 + Phase 7 + Phase 8

## Definition of Done

The task is complete when ALL of the following are true:

---

## Phase 6 - Evaluation, Red-Team, QA

### P6-CI-001: CI Gate Runner
- [ ] CI gate runner implemented
- [ ] `./scripts/bring_up_tests.sh` runs in CI mode
- [ ] Artifacts retained and summary published
- [ ] `gate_artifacts/ci_gate_run.log` exists
- [ ] `gate_artifacts/ci_gate_run.log` contains `CI_GATES: PASSED`

### P6-REDTEAM-001: Adversarial Red-Team Suite
- [ ] Prompt injection tests implemented
- [ ] Tool-arg manipulation tests implemented
- [ ] Role escalation tests implemented
- [ ] Data exfil attempt tests implemented
- [ ] All attacks blocked/detected
- [ ] `gate_artifacts/redteam_report.json` exists
- [ ] `gate_artifacts/redteam_report.json` contains `REDTEAM: PASSED`

### P6-EVALTREND-001: Eval Trend Tracking
- [ ] Eval trend tracking implemented
- [ ] Tool accuracy trends stored
- [ ] Retrieval metrics trends stored
- [ ] Latency trends stored
- [ ] `gate_artifacts/eval_trend.csv` exists (or `eval_trend.json`)
- [ ] Trend data appended with each run

---

## Phase 7 - Deployment, Monitoring, Operations

### P7-OPS-001: Runbooks
- [ ] Startup/shutdown runbook exists
- [ ] Key rotation runbook exists
- [ ] Backup/restore runbook exists
- [ ] Stuck approval triage runbook exists
- [ ] Double execution triage runbook exists
- [ ] Runbooks linted and validated
- [ ] `gate_artifacts/runbook_lint.log` exists
- [ ] `gate_artifacts/runbook_lint.log` contains `RUNBOOK_LINT: PASSED`

### P7-BACKUP-001: Backup/Restore Drill
- [ ] Backup drill executed
- [ ] Restore drill executed
- [ ] Data integrity verified after restore
- [ ] Drill is non-destructive
- [ ] `gate_artifacts/backup_restore_drill.log` exists
- [ ] `gate_artifacts/backup_restore_drill.log` contains `BACKUP_RESTORE: PASSED`

### P7-MONITORING-001: Monitoring Smoke
- [ ] Required metrics defined
- [ ] Alert thresholds defined
- [ ] Dashboards accessible
- [ ] Monitoring smoke checks pass
- [ ] `gate_artifacts/monitoring_smoke.log` exists
- [ ] `gate_artifacts/monitoring_smoke.log` contains `MONITORING_SMOKE: PASSED`

### P7-RELEASE-001: Release Readiness Check
- [ ] Go/No-Go checklist implemented
- [ ] Release readiness computed from required artifacts
- [ ] All prerequisite phases verified
- [ ] `gate_artifacts/release_readiness_check.json` exists
- [ ] `gate_artifacts/release_readiness_check.json` contains `RELEASE_READY: PASSED`

---

## Phase 8 - Scaling, Optimization, Continuous Improvement

### P8-BENCH-001: Benchmarks
- [ ] Hardware signature recorded
- [ ] vLLM tok/s baseline recorded
- [ ] Agent API latency P50/P95 recorded
- [ ] Tool call latency P95 recorded
- [ ] Retrieval latency P95 recorded
- [ ] Queue throughput recorded
- [ ] Migration triggers defined (pgvector→Qdrant, Postgres→Redis, model upgrade)
- [ ] `gate_artifacts/benchmarks.json` exists
- [ ] `gate_artifacts/benchmarks.json` contains `BENCHMARKS: PASSED`
- [ ] `gate_artifacts/migration_trigger_status.json` exists

### P8-CADENCE-001: CI Cadence Schedule
- [ ] Weekly eval refresh schedule defined
- [ ] Monthly red-team rerun schedule defined
- [ ] Quarterly restore drill schedule defined
- [ ] `gate_artifacts/ci_cadence_schedule.md` exists

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
- [ ] `gate_registry.json` updated with Phase 6, 7, 8 gates
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
- [ ] `ui_smoke_test.log` contains `UI_SMOKE: PASSED`

### Phase 3 Artifacts
- [ ] `rag_rest_contract.json` exists
- [ ] `tool_accuracy_eval.json` shows accuracy ≥95%
- [ ] `retrieval_eval_results.json` shows recall@5 ≥0.80
- [ ] `no_split_brain_retrieval_scan.log` contains `NO_SPLIT_BRAIN: PASSED`

### Phase 4 Artifacts
- [ ] `routing_policy_tests.json` contains `ROUTING_POLICY: PASSED`
- [ ] `policy_config_snapshot.json` exists
- [ ] `cost_report.json` exists
- [ ] `local_percent_report.json` shows ≥80% local handling

### Phase 5 Artifacts
- [ ] `queue_worker_smoke.log` contains `QUEUE_WORKER_SMOKE: PASSED`
- [ ] `queue_load_test.json` shows P95 <100ms
- [ ] `audit_immutability_test.log` contains `AUDIT_IMMUTABILITY: PASSED`
- [ ] `chaos_kill9.log` contains `CHAOS_KILL9: PASSED`
- [ ] `concurrency_n50.log` contains `CONCURRENCY_N50: PASSED`
- [ ] `secrets_hygiene_lint.log` contains `SECRETS_HYGIENE: PASSED`
- [ ] `rate_limit_test.log` contains `RATE_LIMIT: PASSED`

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
| P6-CI-001 | `ci_gate_run.log` | `CI_GATES: PASSED` |
| P6-REDTEAM-001 | `redteam_report.json` | `REDTEAM: PASSED` |
| P6-EVALTREND-001 | `eval_trend.csv` | Trend data present |
| P7-OPS-001 | `runbook_lint.log` | `RUNBOOK_LINT: PASSED` |
| P7-BACKUP-001 | `backup_restore_drill.log` | `BACKUP_RESTORE: PASSED` |
| P7-MONITORING-001 | `monitoring_smoke.log` | `MONITORING_SMOKE: PASSED` |
| P7-RELEASE-001 | `release_readiness_check.json` | `RELEASE_READY: PASSED` |
| P8-BENCH-001 | `benchmarks.json` | `BENCHMARKS: PASSED` |
| P8-BENCH-001 | `migration_trigger_status.json` | Triggers present |
| P8-CADENCE-001 | `ci_cadence_schedule.md` | Schedule present |

**Total: 10 new artifacts**

---

## Quality Thresholds

| Metric | Threshold | Hard/Soft |
|--------|-----------|-----------|
| Red-team attacks | All blocked | HARD |
| Backup/restore | Drill PASS | HARD |
| Release readiness | All phases PASS | HARD |
| Runbooks | All linted | HARD |

---

## Verification Steps

1. Run `./scripts/bring_up_tests.sh` - must exit 0
2. Verify all 10 new artifacts exist with correct PASS markers
3. Verify CI gate runner produces reproducible results
4. Verify red-team suite blocks all attack vectors
5. Verify eval trend is appended (not overwritten)
6. Verify runbooks are complete and linted
7. Verify backup/restore drill is successful
8. Verify monitoring smoke checks pass
9. Verify release readiness check aggregates all phases
10. Verify benchmarks are recorded with hardware signature
11. Verify migration triggers are defined
12. Verify cadence schedule is documented
13. Verify all previous phase artifacts still PASS

---

## Rollback Plan

### If Red-Team Finds Vulnerabilities:
1. Document vulnerability in redteam_report.json
2. Create hotfix task for each vulnerability
3. Re-run red-team after fixes
4. Do NOT proceed to production until REDTEAM: PASSED

### If Backup/Restore Fails:
1. Investigate failure cause
2. Fix backup/restore procedure
3. Re-run drill until PASSED
4. Stop-Ship if drill cannot pass

### If Release Readiness Fails:
1. Identify failing prerequisite phase
2. Fix the failing phase
3. Re-run release readiness check
4. Do NOT expose to production until RELEASE_READY: PASSED

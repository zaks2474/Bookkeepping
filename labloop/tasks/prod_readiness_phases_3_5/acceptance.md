# Acceptance Criteria

## Definition of Done

The task is complete when ALL of the following are true:

### Phase 3: Security Hardening

- [ ] `docs/security/asvs_l1.yaml` exists with ≥10 requirements documented
- [ ] `docs/security/api_top10.yaml` exists with all 10 API risks documented
- [ ] `docs/security/THREAT_MODEL.md` exists
- [ ] `tools/quality/security_checklist_validate.py` exists and runs
- [ ] `apps/agent-api/app/core/security/rbac_coverage.py` exists
- [ ] `apps/agent-api/tests/security/test_rbac_coverage.py` exists
- [ ] `apps/backend/tests/security/test_owasp_api_top10.py` exists
- [ ] `apps/agent-api/app/core/security/output_validation.py` exists
- [ ] `apps/agent-api/tests/security/test_output_sanitization.py` passes
- [ ] `tools/scripts/security_scan.sh` exists and is executable
- [ ] `tools/gates/phase3_security_gate.sh` exists and is executable
- [ ] `artifacts/security/checklist_validation.json` shows passed=true

### Phase 4: External Access

- [ ] `ops/external_access/endpoint_classification.yaml` exists with all endpoints
- [ ] `ops/external_access/cloudflare/README.md` exists
- [ ] `ops/external_access/cloudflare/cloudflared_config.yml` exists
- [ ] `ops/external_access/cloudflare/access_policies.yaml` exists
- [ ] `tools/quality/cloudflare_config_validate.py` exists and runs
- [ ] `apps/agent-api/app/core/middleware/rate_limiter.py` exists
- [ ] `apps/agent-api/tests/security/test_rate_limits.py` passes
- [ ] `tools/gates/phase4_external_access_gate.sh` exists and is executable
- [ ] `artifacts/policies/cloudflare_validation.json` shows passed=true

### Phase 5: Performance

- [ ] `tools/load-tests/generate_k6_thresholds.py` exists and generates thresholds
- [ ] `tools/load-tests/scenarios/slo-validation.js` exists
- [ ] `tools/load-tests/generated/thresholds.js` generated from SLOs
- [ ] `docs/perf/VLLM_TUNING.md` exists
- [ ] `tools/scripts/record_vllm_benchmark.py` exists
- [ ] `apps/agent-api/app/core/telemetry/cost_tracking.py` exists
- [ ] `tools/gates/phase5_performance_gate.sh` exists and is executable
- [ ] `artifacts/perf/thresholds_used.json` exists

### Makefile Integration

- [ ] Root Makefile has `phase3`, `phase4`, `phase5` targets
- [ ] `make phase3` runs successfully
- [ ] `make phase4` runs successfully
- [ ] `make phase5` runs successfully

### Quality Gates

- [ ] All existing tests still pass (no regressions)
- [ ] No linting errors in new Python files
- [ ] All shell scripts pass basic syntax check

## Verification Steps

1. Run `make phase3` - should exit 0
2. Run `make phase4` - should exit 0
3. Run `make phase5` - should exit 0
4. Verify artifact files exist and show passing status

## Gate Command

```bash
make phase3 && make phase4 && make phase5
```

This command must exit with code 0 for the task to pass.

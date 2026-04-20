# Acceptance Criteria

## Definition of Done

The task is complete when ALL of the following are true:

### Phase 6: Observability

- [ ] `packages/observability/otel_conventions.py` exists with SpanNames, Attributes classes
- [ ] `docs/observability/OTEL_CONVENTIONS.md` exists
- [ ] `tools/quality/generate_slo_alerts.py` exists and generates alerts
- [ ] `tools/quality/alert_rules_validate.py` exists and validates alerts
- [ ] `ops/observability/prometheus/alerts/slo_alerts.yml` generated
- [ ] `tools/synthetic/canary.py` exists
- [ ] `ops/observability/grafana/dashboards/zakops_overview.json` exists and is valid JSON
- [ ] `docs/observability/DASHBOARDS.md` exists
- [ ] `tools/gates/phase6_observability_gate.sh` exists and is executable
- [ ] `artifacts/observability/alert_rules_validation.json` shows passed=true

### Phase 7: Data Governance

- [ ] `docs/data/DATA_GOVERNANCE_OVERVIEW.md` exists
- [ ] `docs/data/DATA_CLASSIFICATION.md` exists
- [ ] `docs/data/RETENTION_POLICY.yaml` exists with required keys
- [ ] `docs/data/DELETION_POLICY.md` exists
- [ ] `docs/data/BACKUP_RESTORE_POLICY.md` exists
- [ ] `docs/data/TENANT_ISOLATION.md` exists
- [ ] `tools/quality/data_policy_validate.py` exists and passes
- [ ] `packages/security/pii_redaction.py` exists with required functions
- [ ] `apps/agent-api/tests/security/test_pii_redaction.py` exists
- [ ] `apps/backend/tests/security/test_tenant_isolation.py` exists
- [ ] `tools/gates/phase7_data_governance_gate.sh` exists and is executable
- [ ] `artifacts/data/data_policy_validation.json` shows passed=true

### Phase 8: Documentation

- [ ] `docs/docs_checklist.yaml` exists
- [ ] `docs/user/GETTING_STARTED.md` exists with required sections
- [ ] `docs/user/WORKFLOWS.md` exists
- [ ] `docs/user/APPROVALS.md` exists
- [ ] `docs/user/AUDIT_LOGS.md` exists
- [ ] `docs/api/OVERVIEW.md` exists
- [ ] `docs/api/AUTH.md` exists
- [ ] `docs/api/ENDPOINTS.md` exists
- [ ] `docs/troubleshooting/TROUBLESHOOTING.md` exists with Common Issues section
- [ ] `docs/troubleshooting/RUNBOOKS.md` exists
- [ ] `docs/training/ROLE_GUIDES.md` exists
- [ ] `docs/training/FAQ.md` exists
- [ ] `docs/demos/DEMO_SCRIPT.md` exists
- [ ] `tools/quality/docs_validate.py` exists and passes
- [ ] `tools/demos/run_demo.sh` exists and is executable
- [ ] `tools/gates/phase8_documentation_gate.sh` exists and is executable
- [ ] `artifacts/docs/docs_validation.json` shows passed=true

### Makefile Integration

- [ ] Root Makefile has `phase6`, `phase7`, `phase8` targets
- [ ] `make phase6` runs successfully
- [ ] `make phase7` runs successfully
- [ ] `make phase8` runs successfully

### Quality Gates

- [ ] All existing tests still pass (no regressions)
- [ ] All shell scripts pass basic syntax check
- [ ] All JSON files are valid

## Verification Steps

1. Run `make phase6` - should exit 0
2. Run `make phase7` - should exit 0
3. Run `make phase8` - should exit 0
4. Verify artifact files exist and show passing status

## Gate Command

```bash
make phase6 && make phase7 && make phase8
```

This command must exit with code 0 for the task to pass.

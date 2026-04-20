# Acceptance Criteria

## Definition of Done

The task is complete when ALL of the following are true:

### Phase 0: SLOs + Risk Model

- [ ] `docs/slos/SLO_DEFINITIONS.md` exists with API and Agent SLOs documented
- [ ] `docs/slos/slo_config.yaml` exists with ≥6 SLO definitions and error budget thresholds
- [ ] `docs/slos/ERROR_BUDGET_POLICY.md` exists with threshold states
- [ ] `docs/risk/RISK_REGISTER.md` exists with ≥12 documented risks (NIST AI RMF aligned)
- [ ] `docs/risk/NIST_AI_RMF_MAPPING.md` exists with framework alignment
- [ ] `tools/quality/slo_validate.py` exists and runs successfully
- [ ] `tools/quality/risk_validate.py` exists and runs successfully
- [ ] `tools/gates/phase0_slo_gate.sh` exists and is executable
- [ ] `tools/gates/phase0_risk_gate.sh` exists and is executable
- [ ] `artifacts/quality/slo_validation.json` shows `passed: true`
- [ ] `artifacts/quality/risk_validation.json` shows `passed: true`

### Phase 1: Agent Intelligence Validation

- [ ] `apps/agent-api/evals/golden_trace.schema.json` exists with valid JSON schema
- [ ] Golden traces GT-001 through GT-010 exist in `apps/agent-api/evals/golden_traces/`
- [ ] `apps/agent-api/evals/golden_trace_runner.py` exists with CI/local modes
- [ ] `apps/agent-api/evals/datasets/tool_selection/v1/cases.json` exists with ≥20 test cases
- [ ] `apps/agent-api/tests/security/test_owasp_llm_top10.py` exists
- [ ] `tools/gates/golden_trace_gate.sh` exists and is executable
- [ ] `tools/gates/owasp_llm_gate.sh` exists and is executable
- [ ] `docs/agent/GOLDEN_TRACE_GUIDE.md` exists
- [ ] Golden trace runner passes 100% in CI mode
- [ ] OWASP LLM security tests pass

### Phase 2: Trust UX + Audit

- [ ] `apps/dashboard/src/components/approvals/ApprovalCard.tsx` exists with required features
- [ ] `apps/dashboard/src/components/audit/AuditLogViewer.tsx` exists with required features
- [ ] `docs/ux/TRUST_UX_CHECKLIST.md` exists
- [ ] `tools/gates/phase2_trust_ux_gate.sh` exists and is executable

### Makefile Integration

- [ ] Root Makefile has `phase0`, `phase1`, `phase2` targets
- [ ] `make phase0` runs successfully (slo-validate + risk-validate)
- [ ] `make phase1` runs successfully (golden-traces + owasp-tests)
- [ ] `make phase2` runs successfully (trust-ux-check)

### Quality Gates

- [ ] All existing tests still pass (no regressions)
- [ ] No linting errors in new Python files
- [ ] All shell scripts pass shellcheck

## Verification Steps

1. Run `make phase0` - should exit 0
2. Run `make phase1` - should exit 0
3. Run `make phase2` - should exit 0
4. Verify artifact files exist and show passing status

## Gate Command

```bash
make phase0 && make phase1 && make phase2
```

This command must exit with code 0 for the task to pass.

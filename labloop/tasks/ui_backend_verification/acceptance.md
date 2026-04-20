# Acceptance Criteria: UI-Backend Verification

## Gate Pass Requirements (ALL REQUIRED)

- [ ] All 7 services responding healthy (Deal API, RAG API, MCP Server, Orchestration API, Dashboard, Postgres, Redis)
- [ ] All documented mappings verified with live HTTP requests (0 failures in audit)
- [ ] All 6 workflow Playwright tests pass with screenshot evidence
- [ ] All claimed gap fixes verified (no TODO/PLACEHOLDER markers in fixed files)
- [ ] Double verification pass (curl-based) agrees with primary pass (Python-based)
- [ ] `gate_final_report.json` shows `overall_status: "PASS"`
- [ ] No manual exceptions or "acceptable failures"

## Required Artifacts

- [ ] `tools/gates/verify_services.sh` - Service health check script
- [ ] `tools/verification/audit_mappings.py` - Mapping audit script
- [ ] `e2e/workflow_verification.spec.ts` - Playwright workflow tests
- [ ] `tools/verification/verify_gaps_closed.py` - Gap closure verifier
- [ ] `tools/verification/double_check.sh` - Curl-based double check
- [ ] `tools/gates/ui_backend_verification_gate.sh` - Master gate script

## Required Evidence Artifacts

- [ ] `gate_artifacts/contract_probe_results.json` - All services healthy
- [ ] `gate_artifacts/mapping_audit_results.json` - 0 failures, 0 warnings
- [ ] `gate_artifacts/playwright_results.json` - All 6 workflows pass
- [ ] `gate_artifacts/gap_closure_verification.json` - 0 failures, <30% unverified
- [ ] `gate_artifacts/double_check_results.json` - 0 failures
- [ ] `gate_artifacts/gate_final_report.json` - overall_status: "PASS"
- [ ] `gate_artifacts/w1_dashboard_evidence.png` - Dashboard load screenshot
- [ ] `gate_artifacts/w2_deal_list_evidence.png` - Deal list screenshot
- [ ] `gate_artifacts/w3_deal_detail_evidence.png` - Deal detail screenshot
- [ ] `gate_artifacts/w4_transition_evidence.png` - Stage transition screenshot
- [ ] `gate_artifacts/w5_activity_evidence.png` - Activity feed screenshot
- [ ] `gate_artifacts/w6_error_handling_evidence.png` - Error handling screenshot

## Verification Protocol

1. **Phase 1**: Service Health - All 7 services must respond correctly
2. **Phase 2**: Mapping Audit - Every endpoint in UI_BACKEND_MAPPING.json verified
3. **Phase 3**: Workflow E2E - All 6 Playwright tests pass
4. **Phase 4**: Gap Closure - All claimed fixes proven with evidence
5. **Phase 5**: Double Check - Second pass agrees with first pass
6. **Phase 6**: Cross-Reference - Both verification passes show 0 failures

## Failure Handling

- If ANY phase fails, gate halts
- Must fix root cause (not just make test pass)
- Document fix in GAPS_AND_FIX_PLAN.md
- Re-run full gate to check for regressions

## Success Definition

```
Gate exit code: 0
gate_final_report.json: { "overall_status": "PASS" }
All phase results: "pass"
All evidence artifacts: present and valid
```

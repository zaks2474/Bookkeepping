# MISSION: ZakOps Production Readiness — Phases 0–2
## SLOs/Risk → Agent Validation → Trust UX

**Version:** 2.0 (Enhanced)
**Reference:** /home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_ROADMAP_v2.md

---

## CRITICAL CONTEXT

### What This Mission Produces

| Phase | Primary Output | Gate |
|-------|----------------|------|
| **0** | SLO definitions + risk register | Documents validate |
| **1** | Agent evaluation framework | Golden traces pass, tool accuracy ≥95% |
| **2** | Trust UX + audit visibility | Components exist, gates pass |

### Hard Rules

1. **Don't break existing functionality** — Run existing tests before AND after changes
2. **CI must be fast** — Evals use mocked agent responses in CI, real agent locally
3. **Start small, structure for scale** — 10 golden traces now, schema supports 100
4. **Every gate must be deterministic** — No flaky tests, no network dependencies in CI
5. **Document limitations** — If something is deferred, create a TODO with clear scope

---

## PHASE 0: SLOs + RISK MODEL

### Required Directories
```
mkdir -p docs/slos docs/risk tools/quality artifacts/quality
```

### Required Files

1. **docs/slos/SLO_DEFINITIONS.md** - SLO documentation with:
   - API SLOs: Availability 99.5%, Latency P95 500ms, P99 2000ms
   - Agent SLOs: Availability 99.0%, Latency P95 5000ms, Tool Accuracy 95%

2. **docs/slos/slo_config.yaml** - Machine-readable SLO config with:
   - At least 6 SLO definitions
   - Error budget thresholds (green/yellow/orange/red)

3. **docs/slos/ERROR_BUDGET_POLICY.md** - Error budget policy with threshold states

4. **docs/risk/RISK_REGISTER.md** - NIST AI RMF-aligned risk register with:
   - At least 12 documented risks
   - Categories: Validity, Safety, Security, Privacy, Transparency
   - Each risk: ID, description, likelihood, impact, mitigation, owner, status

5. **docs/risk/NIST_AI_RMF_MAPPING.md** - Framework alignment documentation

6. **tools/quality/slo_validate.py** - SLO config validator (outputs to artifacts/quality/slo_validation.json)
7. **tools/quality/risk_validate.py** - Risk register validator (outputs to artifacts/quality/risk_validation.json)
8. **tools/gates/phase0_slo_gate.sh** - SLO validation gate
9. **tools/gates/phase0_risk_gate.sh** - Risk validation gate

---

## PHASE 1: AGENT INTELLIGENCE VALIDATION

### Required Directories
```
mkdir -p apps/agent-api/evals/golden_traces
mkdir -p apps/agent-api/evals/datasets/tool_selection/v1
mkdir -p apps/agent-api/tests/security
mkdir -p artifacts/evals
```

### Required Files

1. **apps/agent-api/evals/golden_trace.schema.json** - Schema for golden traces

2. **apps/agent-api/evals/golden_traces/GT-001.json through GT-010.json** - 10 golden traces:
   - GT-001: Basic deal query
   - GT-002: Deal transition (requires approval)
   - GT-003: List deals query
   - GT-004: Deal value query
   - GT-005: Invalid deal ID handling
   - GT-006: Ambiguous request
   - GT-007: Create deal request
   - GT-008: Stage transition to closed_won (requires approval)
   - GT-009: Search deals by filter
   - GT-010: No tool needed (general question)

3. **apps/agent-api/evals/golden_trace_runner.py** - Runner with CI/local modes
   - CI mode: uses mock_response from trace files
   - Local mode: calls real agent at localhost:8095

4. **apps/agent-api/evals/datasets/tool_selection/v1/cases.json** - 20+ tool selection test cases

5. **apps/agent-api/tests/security/test_owasp_llm_top10.py** - OWASP LLM security tests

6. **tools/gates/golden_trace_gate.sh** - Golden trace gate (100% pass required)
7. **tools/gates/owasp_llm_gate.sh** - OWASP LLM gate

8. **docs/agent/GOLDEN_TRACE_GUIDE.md** - Documentation for adding traces

---

## PHASE 2: TRUST UX + AUDIT

### Required Directories
```
mkdir -p apps/dashboard/src/components/approvals
mkdir -p apps/dashboard/src/components/audit
mkdir -p docs/ux
```

### Required Files

1. **apps/dashboard/src/components/approvals/ApprovalCard.tsx** - Approval card with:
   - WHAT action display
   - DEAL context
   - WHY approval needed
   - CHANGES preview (diff)
   - Approve/Reject buttons

2. **apps/dashboard/src/components/audit/AuditLogViewer.tsx** - Audit viewer with:
   - Timeline view
   - Actor filter
   - Action filter
   - Request ID visible and copyable
   - Export JSON/CSV

3. **docs/ux/TRUST_UX_CHECKLIST.md** - Trust UX completion checklist

4. **tools/gates/phase2_trust_ux_gate.sh** - Trust UX component gate

---

## MAKEFILE UPDATES

Add these targets to the root Makefile:

```makefile
# Production Readiness Phases
.PHONY: phase0 phase1 phase2

phase0: slo-validate risk-validate
	@echo "Phase 0 complete"

phase1: golden-traces owasp-tests
	@echo "Phase 1 complete"

phase2: trust-ux-check
	@echo "Phase 2 complete"

slo-validate:
	@python3 tools/quality/slo_validate.py

risk-validate:
	@python3 tools/quality/risk_validate.py

golden-traces:
	@CI=true python -m apps.agent_api.evals.golden_trace_runner

owasp-tests:
	@cd apps/agent-api && CI=true python -m pytest tests/security/ -v

trust-ux-check:
	@bash tools/gates/phase2_trust_ux_gate.sh
```

---

## DISCOVERY FIRST

Before implementing, run discovery to understand current state:

```bash
cd /home/zaks/zakops-agent-api
git checkout -b feat/prod-readiness-phases-0-2

# Check structure
find . -maxdepth 3 -type d -not -path '*/node_modules/*' -not -path '*/.git/*' | head -50
ls -la apps/agent-api/evals/ 2>/dev/null || echo "No evals dir yet"
ls -la apps/dashboard/src/components/ 2>/dev/null
```

---

## REFERENCE

Full implementation details in:
/home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_ROADMAP_v2.md

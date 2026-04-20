# MISSION: ZakOps Production Readiness — Phases 3–5
## Security → External Access → Performance

**Version:** 2.0 (Enhanced)
**Reference:** /home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_PHASES_3_5.md

---

## CRITICAL CONTEXT

### What This Mission Produces

| Phase | Primary Output | Gate |
|-------|----------------|------|
| **3** | Security baseline + RBAC proof + supply chain scans | Docs exist, RBAC 100%, 0 critical vulns |
| **4** | Endpoint classification + rate limiting + Cloudflare IaC | Classification valid, abuse tests pass |
| **5** | k6 thresholds + vLLM docs + cost tracking | Thresholds from SLOs, docs exist |

### Hard Rules

1. **Security controls must be enforced by code** — Not just documented
2. **Gates must work offline** — No external API calls required in CI
3. **External tools are optional locally** — Provide fallback/skip paths
4. **Performance tests don't mutate production data** — Use test fixtures
5. **Credentials never in code** — Use env vars, validate config shapes only

---

## PHASE 3: SECURITY HARDENING

### Required Directories
```
mkdir -p docs/security artifacts/security
mkdir -p apps/agent-api/app/core/security
mkdir -p apps/agent-api/tests/security
mkdir -p apps/backend/tests/security
```

### Required Files

1. **docs/security/asvs_l1.yaml** - OWASP ASVS Level 1 checklist (machine-readable)
   - At least 10+ requirements documented
   - Each with: id, title, status (complete/not_applicable), enforcement_location, test_reference

2. **docs/security/api_top10.yaml** - OWASP API Security Top 10 checklist
   - All 10 risks documented
   - Each with: id, name, status, controls list

3. **docs/security/THREAT_MODEL.md** - Threat model documentation

4. **tools/quality/security_checklist_validate.py** - Validates security checklists

5. **apps/agent-api/app/core/security/rbac_coverage.py** - RBAC coverage validator

6. **apps/agent-api/tests/security/test_rbac_coverage.py** - RBAC coverage tests

7. **apps/backend/tests/security/test_owasp_api_top10.py** - API security tests

8. **apps/agent-api/app/core/security/output_validation.py** - Output sanitization

9. **apps/agent-api/tests/security/test_output_sanitization.py** - Sanitization tests

10. **tools/scripts/security_scan.sh** - Supply chain security scan script

11. **tools/gates/phase3_security_gate.sh** - Phase 3 security gate

---

## PHASE 4: EXTERNAL ACCESS + POLICY ENFORCEMENT

### Required Directories
```
mkdir -p ops/external_access/cloudflare artifacts/policies
mkdir -p apps/agent-api/app/core/middleware
```

### Required Files

1. **ops/external_access/endpoint_classification.yaml** - Endpoint classification
   - All endpoints classified (public/authenticated/admin/internal)
   - Rate limit profiles defined

2. **ops/external_access/cloudflare/README.md** - Cloudflare setup guide

3. **ops/external_access/cloudflare/cloudflared_config.yml** - Tunnel config template

4. **ops/external_access/cloudflare/access_policies.yaml** - Access policies

5. **tools/quality/cloudflare_config_validate.py** - Config validator (no credentials needed)

6. **apps/agent-api/app/core/middleware/rate_limiter.py** - Rate limiting middleware

7. **apps/agent-api/tests/security/test_rate_limits.py** - Rate limit tests

8. **tools/gates/phase4_external_access_gate.sh** - Phase 4 gate

---

## PHASE 5: PERFORMANCE (SLO-BOUND)

### Required Directories
```
mkdir -p tools/load-tests/{scenarios,profiles,generated} artifacts/perf
mkdir -p docs/perf artifacts/benchmarks
mkdir -p apps/agent-api/app/core/telemetry
```

### Required Files

1. **tools/load-tests/generate_k6_thresholds.py** - Generate thresholds from SLOs

2. **tools/load-tests/scenarios/slo-validation.js** - k6 load test scenario

3. **docs/perf/VLLM_TUNING.md** - vLLM tuning guide

4. **tools/scripts/record_vllm_benchmark.py** - vLLM benchmark recorder

5. **apps/agent-api/app/core/telemetry/cost_tracking.py** - Token cost tracking

6. **apps/agent-api/tests/test_cost_tracking.py** - Cost tracking tests

7. **tools/gates/phase5_performance_gate.sh** - Phase 5 gate

---

## MAKEFILE UPDATES

Add these targets to the root Makefile:

```makefile
# Phases 3-5: Security, External Access, Performance
.PHONY: phase3 phase4 phase5 security perf

security: phase3
perf: phase5

phase3:
	@echo "=== Phase 3: Security ==="
	@bash tools/gates/phase3_security_gate.sh

phase4:
	@echo "=== Phase 4: External Access ==="
	@bash tools/gates/phase4_external_access_gate.sh

phase5:
	@echo "=== Phase 5: Performance ==="
	@bash tools/gates/phase5_performance_gate.sh
```

---

## DISCOVERY FIRST

Before implementing, run discovery to understand current state:

```bash
cd /home/zaks/zakops-agent-api

# Check existing security infrastructure
ls -la apps/agent-api/app/core/security/ 2>/dev/null || echo "No security module"
ls -la apps/agent-api/app/core/middleware/ 2>/dev/null || echo "No middleware"

# Check available tools
command -v trivy || echo "trivy: NOT INSTALLED"
command -v k6 || echo "k6: NOT INSTALLED"
command -v pip-audit || echo "pip-audit: NOT INSTALLED"

# Create directories
mkdir -p artifacts/{security,perf,policies,benchmarks}
mkdir -p docs/{security,perf}
mkdir -p ops/external_access/cloudflare
mkdir -p tools/load-tests/{scenarios,profiles,generated}
```

---

## REFERENCE

Full implementation details in:
/home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_PHASES_3_5.md

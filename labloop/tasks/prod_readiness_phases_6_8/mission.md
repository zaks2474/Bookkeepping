# MISSION: ZakOps Production Readiness — Phases 6–8
## Observability → Data Governance → Documentation

**Version:** 2.0 (Enhanced)
**Reference:** /home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_PHASES_6_8.md

---

## CRITICAL CONTEXT

### What This Mission Produces

| Phase | Primary Output | Gate |
|-------|----------------|------|
| **6** | OTEL conventions + SLO alerts + canary + dashboards | Conventions defined, alerts generated |
| **7** | Data policies + tenant isolation + PII redaction | Policies exist, PII tests pass |
| **8** | User docs + API docs + troubleshooting + demo script | Docs complete, demo passes |

### Hard Rules

1. **Observability config must be validated without running services**
2. **Data governance = docs + validation, not full implementation**
3. **RAG gates are conditional on RAG service availability**
4. **Demo gate has mock mode for CI**
5. **All docs must exist and have required sections**

---

## PHASE 6: OBSERVABILITY

### Required Directories
```
mkdir -p packages/observability
mkdir -p docs/observability
mkdir -p ops/observability/prometheus/alerts
mkdir -p ops/observability/grafana/dashboards
mkdir -p tools/synthetic
mkdir -p artifacts/observability
```

### Required Files

1. **packages/observability/otel_conventions.py** - OTEL semantic conventions
   - SpanNames class with http(), database(), agent(), llm(), tool() methods
   - HttpAttributes, DbAttributes, LlmAttributes, AgentAttributes classes
   - build_http_attributes(), build_llm_attributes(), build_agent_attributes() helpers
   - PII_PATTERNS list for validation

2. **docs/observability/OTEL_CONVENTIONS.md** - OTEL conventions documentation

3. **tools/quality/generate_slo_alerts.py** - Generate Prometheus alerts from SLOs
   - Reads docs/slos/slo_config.yaml
   - Outputs to ops/observability/prometheus/alerts/slo_alerts.yml
   - Outputs to artifacts/observability/generated_slo_alerts.yml

4. **tools/quality/alert_rules_validate.py** - Validate alert rules against SLOs
   - Checks every SLO has corresponding alert
   - Optional promtool validation if available
   - Outputs to artifacts/observability/alert_rules_validation.json

5. **tools/synthetic/canary.py** - Synthetic canary monitoring
   - Checks backend, orchestration, agent-api health endpoints
   - Checks agent invoke endpoint
   - Outputs to artifacts/observability/canary_run.json
   - Graceful skip if services not running

6. **ops/observability/grafana/dashboards/zakops_overview.json** - Grafana dashboard
   - API Availability stat
   - API Latency P95 stat
   - Token Usage timeseries
   - Estimated Cost stat
   - Agent Invocations timeseries

7. **docs/observability/DASHBOARDS.md** - Dashboard documentation

8. **tools/gates/phase6_observability_gate.sh** - Phase 6 gate

---

## PHASE 7: DATA GOVERNANCE

### Required Directories
```
mkdir -p docs/data
mkdir -p packages/security
mkdir -p artifacts/data
mkdir -p apps/agent-api/tests/security
mkdir -p apps/backend/tests/security
```

### Required Files

1. **docs/data/DATA_GOVERNANCE_OVERVIEW.md** - Data governance overview
   - Data classification table (Public, Internal, Confidential, Restricted)
   - Data domains table

2. **docs/data/DATA_CLASSIFICATION.md** - Data classification guide
   - Classification levels
   - Handling requirements table
   - PII inventory

3. **docs/data/RETENTION_POLICY.yaml** - Machine-readable retention policy
   - retention_rules for: deals, agent_runs, approval_logs, user_sessions, rag_documents
   - backup_schedule
   - compliance section

4. **docs/data/DELETION_POLICY.md** - Deletion policy

5. **docs/data/BACKUP_RESTORE_POLICY.md** - Backup and restore policy

6. **docs/data/TENANT_ISOLATION.md** - Tenant isolation documentation
   - Single-tenant mode documentation
   - Configuration instructions

7. **tools/quality/data_policy_validate.py** - Data policy validator
   - Checks all required docs exist
   - Validates RETENTION_POLICY.yaml structure
   - Outputs to artifacts/data/data_policy_validation.json

8. **packages/security/pii_redaction.py** - PII redaction module
   - PII_PATTERNS dict with patterns for email, phone, ssn, credit_card, ip_address
   - redact_text(), redact_dict(), detect_pii(), has_pii() functions
   - redact_sensitive_fields() function

9. **apps/agent-api/tests/security/test_pii_redaction.py** - PII redaction tests
   - TestPIIDetection class
   - TestPIIRedaction class
   - TestPIIInLogs class
   - TestPIIInTraces class

10. **apps/backend/tests/security/test_tenant_isolation.py** - Tenant isolation tests

11. **tools/gates/phase7_data_governance_gate.sh** - Phase 7 gate

---

## PHASE 8: DOCUMENTATION + TRAINING

### Required Directories
```
mkdir -p docs/user
mkdir -p docs/api
mkdir -p docs/troubleshooting
mkdir -p docs/training
mkdir -p docs/demos
mkdir -p tools/demos
mkdir -p artifacts/docs
```

### Required Files

1. **docs/docs_checklist.yaml** - Documentation checklist for validation

2. **docs/user/GETTING_STARTED.md** - User getting started guide
   - Sections: Prerequisites, Installation, First Steps

3. **docs/user/WORKFLOWS.md** - Workflow documentation
   - Sections: Deal Lifecycle, Approvals

4. **docs/user/APPROVALS.md** - Approvals documentation
   - Sections: Overview, Approval Flow

5. **docs/user/AUDIT_LOGS.md** - Audit logs documentation
   - Sections: Overview, Viewing Logs

6. **docs/api/OVERVIEW.md** - API overview
   - Sections: Introduction, Authentication

7. **docs/api/AUTH.md** - Authentication documentation
   - Sections: Getting Tokens, Using Tokens

8. **docs/api/ENDPOINTS.md** - API endpoints documentation
   - Sections: Deals, Agent

9. **docs/troubleshooting/TROUBLESHOOTING.md** - Troubleshooting guide
   - Sections: Common Issues, Getting Help
   - Quick Diagnostics section
   - Authentication Failures, Agent Not Responding, etc.

10. **docs/troubleshooting/RUNBOOKS.md** - Operational runbooks
    - Sections: Service Restart, Health Checks

11. **docs/training/ROLE_GUIDES.md** - Role-based guides
    - Sections: Operator, Admin

12. **docs/training/FAQ.md** - Frequently asked questions

13. **docs/demos/DEMO_SCRIPT.md** - Demo script documentation
    - Sections: Setup, Script, Cleanup

14. **tools/quality/docs_validate.py** - Documentation validator
    - Validates docs against docs_checklist.yaml
    - Checks required sections exist
    - Outputs to artifacts/docs/docs_validation.json

15. **tools/demos/run_demo.sh** - Automated demo script
    - Checks services health
    - Creates demo deal
    - Agent invoke with approval
    - Verifies audit log
    - Outputs to artifacts/docs/demo_run.json

16. **tools/gates/phase8_documentation_gate.sh** - Phase 8 gate

---

## MAKEFILE UPDATES

Add these targets to the root Makefile:

```makefile
# Phases 6-8: Observability, Data Governance, Documentation
.PHONY: phase6 phase7 phase8 observability docs demo

phase6:
	@echo "=== Phase 6: Observability ==="
	@bash tools/gates/phase6_observability_gate.sh

phase7:
	@echo "=== Phase 7: Data Governance ==="
	@bash tools/gates/phase7_data_governance_gate.sh

phase8:
	@echo "=== Phase 8: Documentation ==="
	@bash tools/gates/phase8_documentation_gate.sh

observability: phase6
docs: phase8

demo:
	@bash tools/demos/run_demo.sh
```

---

## DISCOVERY FIRST

Before implementing, run discovery:

```bash
cd /home/zaks/zakops-agent-api

# Check what exists from previous phases
ls -la docs/slos/slo_config.yaml    # Phase 0
ls -la docs/security/               # Phase 3

# Create directories
mkdir -p packages/{observability,security}
mkdir -p docs/{observability,data,user,api,troubleshooting,training,demos}
mkdir -p ops/observability/{prometheus/alerts,grafana/dashboards}
mkdir -p tools/{synthetic,demos}
mkdir -p artifacts/{observability,data,docs}
```

---

## REFERENCE

Full implementation details in user message above.

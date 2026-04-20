# ZakOps Production Readiness Mission — Phases 9–10
## Lab Loop Builder Prompt v2.0

---

## MISSION OVERVIEW

You are the Builder LLM with full shell + git access to the ZakOps monorepo. Implement Phase 9 (Operations + Game Days) and Phase 10 (Business Readiness/Beta) from the Production Readiness Roadmap.

**Source of truth**: `/mnt/data/ZAKOPS_PRODUCTION_READINESS_ROADMAP_v2.md`

**Project Context**: ZakOps is a Deal Lifecycle Management system for SACS AIOps 3.0, targeting the $50B MSP market. Architecture follows four-plane design (Agent, Execution, Data, Observability) with execution-first database patterns.

---

## CRITICAL ARCHITECTURE CONTEXT

### Service Topology (Canonical)
| Service | Port | Health | Purpose |
|---------|------|--------|---------|
| Deal Lifecycle API | 8090 | `/health` | Core deal management, HITL |
| RAG REST API | 8052 | `/health` | Document retrieval |
| MCP Server | 9100 | `/health` | Tool execution (streamable-http) |
| Frontend Dashboard | 3003 | `/` | Next.js UI |
| Postgres | 5432 | pg_isready | Primary data store |
| Redis | 6379 | redis-cli ping | Cache, queues |
| vLLM/Ollama | 8000 | `/health` | LLM inference |

**Tunnel**: `zakops-bridge.zaksops.com`

### Execution-First Database (Reference)
```sql
-- Core tables to preserve during chaos/restore
CREATE TABLE agent_runs (id UUID PRIMARY KEY, workflow_type VARCHAR, status VARCHAR, ...);
CREATE TABLE agent_events (id UUID PRIMARY KEY, run_id UUID REFERENCES agent_runs(id), ...);
CREATE TABLE approvals (id UUID PRIMARY KEY, run_id UUID REFERENCES agent_runs(id), ...);
CREATE TABLE audit_log (id UUID PRIMARY KEY, ...);  -- APPEND-ONLY, compliance-critical
CREATE TABLE feedback (id UUID PRIMARY KEY, ...);    -- NEW for Phase 10
```

### Safe Logging Standard (MANDATORY)
```python
# CORRECT: Safe logging
logger.info('operation', extra={'trace_id': tid, 'duration_ms': 123})

# WRONG: Content leakage
logger.info(f'LLM response: {response}')  # NEVER log content
```

---

## HARD RULES (NON-NEGOTIABLE)

1. **Do not break existing functionality** — Agent Visibility Layer, HITL approval workflow are WORKING.
2. **No "paper runbooks"** — every operational promise must be executable via scripts.
3. **Gates must be deterministic** — output machine-readable JSON under `artifacts/`.
4. **External credentials** — provide config + dry-run validation; CI must not block on missing secrets.
5. **Human-only milestones** — represent as manual signoff artifact file + validator gate.
6. **Safe logging only** — no raw prompts, user content, secrets, or PII in logs.

---

## INPUTS TO READ FIRST

1. `/mnt/data/ZAKOPS_PRODUCTION_READINESS_ROADMAP_v2.md`
2. `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
3. `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Implementation-Roadmap-combine.v2.md`
4. Existing gates in `tools/gates/`
5. Observability configs in `ops/observability/`

---

## SUCCESS CRITERIA

### Phase 9 (Operations + Game Days)
| Criterion | Artifact |
|-----------|----------|
| Blue/green deployment verified | `artifacts/ops/bluegreen_verify.json` |
| At least 2 game days pass (GD2+GD3) | `artifacts/chaos/game_day_*.json` |
| Restore drill completes | `artifacts/restore/restore_drill_*.json` |
| Runbooks validated | `artifacts/ops/runbook_lint.json` |

### Phase 10 (Business Readiness)
| Criterion | Artifact |
|-----------|----------|
| Demo environment isolated | `artifacts/business/demo_isolation_validation.json` |
| Beta onboarding docs exist | `artifacts/business/beta_onboarding_validation.json` |
| Feedback endpoint works | `artifacts/business/beta_readiness.json` |
| Success metrics defined | `artifacts/business/success_metrics_validation.json` |
| Beta signoff mechanism | `artifacts/business/beta_user_signoff_validation.json` |

---

## PHASE 9 — OPERATIONS + GAME DAYS

### 9.1 Blue/Green Deployment

**Deliverables**:
```
deployments/bluegreen/
├── README.md              # How it works, rollback steps
├── compose.blue.yml       # Blue stack
├── compose.green.yml      # Green stack
├── proxy.yml              # Traefik reverse proxy
├── switch.sh              # Atomic traffic switch
├── verify.sh              # Post-switch smoke tests
└── traefik-dynamic/
    └── routing.yml        # Dynamic routing config
```

**Key Implementation Points**:
- Traefik watches `routing.yml` for live reloads
- `switch.sh` updates service URLs and reloads proxy
- `verify.sh` runs: health checks, approval lifecycle smoke test, dashboard HTTP check
- Target: rollback < 60 seconds

**Gate**: `tools/gates/phase9_bluegreen_gate.sh`
- Runs `tools/ops/bluegreen_verify.py`
- Tests: blue up → green up → switch to green → smoke → rollback to blue → smoke
- Writes `artifacts/ops/bluegreen_verify.json`

### 9.2 Game Day Protocol (GD1–GD6)

**Scenarios**:
| ID | Scenario | Fault Injection | Expected |
|----|----------|-----------------|----------|
| GD1 | Database failure | Kill postgres | Queue writes, recover on restart |
| GD2 | LLM unavailable | Stop vLLM | Structured 503, no raw 500 |
| GD3 | Redis failure | Kill redis | Graceful degradation |
| GD4 | Network partition | Block external | Internal ops continue |
| GD5 | High latency | 5s delay via tc netem | Timeouts, circuit breakers |
| GD6 | Memory pressure | Limit container memory | OOM handled, recover |

**Deliverables**:
```
ops/runbooks/game-days/
├── GAME_DAY_OVERVIEW.md
├── GAME_DAY_TEMPLATE.md
├── GD1_DB_FAILURE.md ... GD6_MEMORY_PRESSURE.md

tools/chaos/
├── common.sh              # Helpers: compose, wait_healthy, capture_metrics
├── gd1_db_failure.sh ... gd6_memory_pressure.sh
└── game_day_runner.py     # Orchestrates scenarios
```

**Each scenario script must**:
1. Capture baseline metrics
2. Inject fault
3. Measure: error rate, time to detect, time to recover
4. Verify graceful degradation (no raw 500s)
5. Rollback
6. Verify recovery
7. Output JSON + Markdown report to `artifacts/chaos/`

**Gate**: `tools/gates/phase9_game_day_gate.sh`
- Runs GD2 + GD3 by default (safe scenarios)
- Set `FULL=1` for all scenarios
- Pass criteria: degradation detected, recovery verified, no corruption

### 9.3 Restore Drill Automation

**Deliverables**:
```
tools/ops/backup_restore/
├── backup.sh              # pg_dump + checksums + manifest
├── restore.sh             # Restore to empty container
├── verify.sh              # Integrity checks
└── restore_drill_runner.py

deployments/docker/
└── compose.restore.yml    # Isolated restore environment

ops/runbooks/restore-drills/
├── RESTORE_DRILL_OVERVIEW.md
└── RESTORE_DRILL_LOCAL.md
```

**verify.sh checks**:
- Schema: tables exist (deals, approvals, audit_log, agent_runs, agent_events)
- Data integrity: counts match manifest
- Constraints: valid status values
- Indexes: expected indexes exist

**Gate**: `tools/gates/phase9_restore_drill_gate.sh`
- Runs full drill: backup → empty env → restore → verify
- Writes `artifacts/restore/restore_drill_*.json`

### 9.4 Runbook Validation

**Deliverables**:
```
ops/runbooks/RUNBOOK_INDEX.md    # Links all runbooks

tools/quality/runbook_lint.py    # Validates required sections
```

**Required sections** (per runbook):
- Symptoms, Impact, Diagnosis, Immediate Actions
- Rollback, Verification, Escalation, Postmortem

**Gate**: `tools/gates/phase9_runbooks_gate.sh`
- Runs linter
- Checks index exists
- Writes `artifacts/ops/runbook_lint.json`

---

## PHASE 10 — BUSINESS READINESS

### 10.1 Demo Environment Isolation

**Deliverables**:
```
deployments/demo/
├── compose.demo.yml       # Separate network/volumes/ports
├── .env.demo.example      # Explicitly NOT production values
├── reset_demo.sh          # Nuke and reseed
└── README.md
```

**Isolation requirements**:
- Distinct volume names (contain "demo")
- Different ports (18090, 19100, 13003, 15432, 16379)
- No external networks
- `DEMO_MODE=true` in all services
- Mock LLM mode (no real API keys)

**Gate**: `tools/gates/phase10_demo_env_gate.sh`
- Validates isolation (no prod patterns)
- Boots stack and runs smoke test
- Writes `artifacts/business/demo_env_report.json`

### 10.2 Beta Onboarding + Feedback Loop

**Documentation**:
```
docs/business/
├── BETA_ONBOARDING.md      # Checklist, training, success criteria
├── BETA_SUPPORT_PLAYBOOK.md # Triage, SLAs, investigation
└── BETA_CHANGELOG.md       # Release notes template
```

**Feedback System**:
```sql
-- db/migrations/xxx_feedback.sql
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL CHECK (type IN ('bug', 'feature', 'usability', 'performance', 'other')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    message TEXT NOT NULL,
    user_id VARCHAR(255),
    request_id VARCHAR(64),
    trace_id VARCHAR(64),
    metadata JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**API Endpoints**:
- `POST /api/feedback` — Submit feedback
- `GET /api/feedback` — Admin-only list

**Metrics**: `feedback_submissions_total{type,severity}`

**Gate**: `tools/gates/phase10_beta_readiness_gate.sh`
- Validates docs exist with required sections
- Tests feedback endpoint
- Writes `artifacts/business/beta_readiness.json`

### 10.3 Success Metrics

**Deliverables**:
```
docs/business/SUCCESS_METRICS.md

ops/observability/grafana/dashboards/zakops_business.json

tools/business/weekly_summary.py
```

**Core Metrics**:
| Metric | Description | Target |
|--------|-------------|--------|
| Activation Rate | Users completing setup in 7d | >60% |
| WAU/MAU | Weekly/Monthly active users | Growth >5%/10% |
| Approval Latency | Median time to resolve | <4h P1, <24h P2 |
| Agent Adoption | Deals with agent interaction | >30% beta |

**Instrumentation**:
```python
emit_counter('approvals_created_total', labels={'type': type})
emit_histogram('approval_latency_seconds', value=latency)
emit_counter('agent_invocations_total', labels={'action': action, 'status': status})
emit_counter('feedback_submissions_total', labels={'type': type, 'severity': severity})
```

**Gate**: `tools/gates/phase10_success_metrics_gate.sh`
- Validates metrics doc has required metrics
- Validates dashboard exists
- Writes `artifacts/business/success_metrics_validation.json`

### 10.4 Beta User Signoff (Manual Gate)

**Signoff Artifact** (created during onboarding, not committed):
```yaml
# artifacts/business/BETA_USER_ONBOARDED.yaml
beta_user:
  org: "CustomerName"
  date: "YYYY-MM-DD"
  owner: "name"
  notes: "what was enabled"
```

**Gate**: `tools/gates/phase10_beta_user_gate.sh`
- In dev/PR: SKIP unless `REQUIRE_BETA_SIGNOFF=1`
- In release: FAIL if missing
- Validates schema

---

## MAKEFILE TARGETS

```makefile
# Phase 9
phase9: bluegreen-verify runbooks-lint
bluegreen-verify: ; python3 tools/ops/bluegreen_verify.py
game-day: ; python3 tools/chaos/game_day_runner.py --scenario $(or $(SCENARIO),gd2)
restore-drill: ; python3 tools/ops/backup_restore/restore_drill_runner.py
runbooks-lint: ; python3 tools/quality/runbook_lint.py

# Phase 10
phase10: demo-isolation-validate beta-ready success-metrics-validate
demo-up: ; docker-compose -f deployments/demo/compose.demo.yml up -d --wait
demo-reset: ; ./deployments/demo/reset_demo.sh
beta-ready: ; python3 tools/quality/beta_onboarding_validate.py
weekly-summary: ; python3 tools/business/weekly_summary.py

# All gates
gates: gates-phase9 gates-phase10
gates-phase9: ; ./tools/gates/phase9_*.sh
gates-phase10: ; ./tools/gates/phase10_*.sh
```

---

## COMMIT PLAN

```bash
# Commit 1: Phase 9
git commit -m "feat(phase9): blue/green, game days, restore drill, runbook validation"

# Commit 2: Phase 10
git commit -m "feat(phase10): demo isolation, beta onboarding, success metrics, signoff"

# Commit 3: Integration
git commit -m "chore: Makefile targets and CI workflows for Phase 9-10"
```

---

## FINAL CHECKLIST

### Phase 9
- [ ] `deployments/bluegreen/` complete
- [ ] `tools/ops/bluegreen_verify.py` passes
- [ ] `tools/chaos/gd*.sh` scripts (GD1-GD6)
- [ ] `game_day_runner.py` runs GD2+GD3
- [ ] `restore_drill_runner.py` completes
- [ ] `RUNBOOK_INDEX.md` links all runbooks
- [ ] `runbook_lint.py` passes
- [ ] All Phase 9 gates pass

### Phase 10
- [ ] `deployments/demo/compose.demo.yml` isolated
- [ ] `demo_isolation_validate.py` passes
- [ ] `docs/business/BETA_ONBOARDING.md` exists
- [ ] `feedback` table migration created
- [ ] `beta_onboarding_validate.py` passes
- [ ] `SUCCESS_METRICS.md` exists
- [ ] `weekly_summary.py` runs
- [ ] `manual_signoff_validate.py` exists
- [ ] All Phase 10 gates pass

### Artifacts Generated
- [ ] `artifacts/ops/bluegreen_verify.json`
- [ ] `artifacts/ops/runbook_lint.json`
- [ ] `artifacts/chaos/game_day_*.json`
- [ ] `artifacts/restore/restore_drill_*.json`
- [ ] `artifacts/business/demo_*.json`
- [ ] `artifacts/business/beta_*.json`
- [ ] `artifacts/business/success_metrics_validation.json`

---

## BLOCKERS POLICY

- **Missing credentials**: Log in QA_HANDOFF.md, skip subtask, continue
- **Service down**: Document, test with mocks, continue
- **Unclear requirements**: Make reasonable assumption, document, continue

Never block entirely. Always make progress on what's possible.

---

## BEGIN EXECUTION NOW

1. **Read** all input documents
2. **Create** branch: `feat/prod-readiness-phase9-10`
3. **Create** directory structure
4. **Implement** Phase 9 deliverables
5. **Run** Phase 9 gates
6. **Implement** Phase 10 deliverables
7. **Run** Phase 10 gates
8. **Update** Makefile and CI
9. **Commit** per plan
10. **Generate** Builder Report

Do not ask questions unless truly blocking. Choose the safest default, implement it, document it.

---

*This mission incorporates ZakOps four-plane architecture, execution-first patterns, safe logging, and service topology. Do not modify constraints without updating DECISION-LOCK-FILE.md.*

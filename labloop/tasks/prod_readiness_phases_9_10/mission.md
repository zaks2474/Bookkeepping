# MISSION: ZakOps Production Readiness — Phases 9–10
## Operations + Game Days → Business Readiness

**Version:** 2.0
**Reference:** /home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_PHASES_9_10.md

---

## CRITICAL CONTEXT

### What This Mission Produces

| Phase | Primary Output | Gate |
|-------|----------------|------|
| **9** | Blue/green deployment, game days, restore drills, runbooks | Operations validated |
| **10** | Demo environment, beta onboarding, feedback system, success metrics | Business ready |

### Hard Rules

1. **Do not break existing functionality** — Agent Visibility Layer, HITL approval workflow are WORKING
2. **No "paper runbooks"** — every operational promise must be executable via scripts
3. **Gates must be deterministic** — output machine-readable JSON under `artifacts/`
4. **Safe logging only** — no raw prompts, user content, secrets, or PII in logs

---

## PHASE 9: OPERATIONS + GAME DAYS

### Required Directories
```
mkdir -p deployments/bluegreen/traefik-dynamic
mkdir -p tools/ops/backup_restore
mkdir -p tools/chaos
mkdir -p ops/runbooks/game-days
mkdir -p ops/runbooks/restore-drills
mkdir -p artifacts/ops artifacts/chaos artifacts/restore
```

### 9.1 Blue/Green Deployment
- `deployments/bluegreen/README.md`
- `deployments/bluegreen/compose.blue.yml`
- `deployments/bluegreen/compose.green.yml`
- `deployments/bluegreen/proxy.yml`
- `deployments/bluegreen/switch.sh`
- `deployments/bluegreen/verify.sh`
- `tools/ops/bluegreen_verify.py`
- `tools/gates/phase9_bluegreen_gate.sh`

### 9.2 Game Day Scenarios (GD1-GD6)
- `tools/chaos/common.sh`
- `tools/chaos/gd1_db_failure.sh` through `gd6_memory_pressure.sh`
- `tools/chaos/game_day_runner.py`
- `ops/runbooks/game-days/GAME_DAY_OVERVIEW.md`
- `ops/runbooks/game-days/GD1_DB_FAILURE.md` through `GD6_MEMORY_PRESSURE.md`
- `tools/gates/phase9_game_day_gate.sh`

### 9.3 Restore Drill
- `tools/ops/backup_restore/backup.sh`
- `tools/ops/backup_restore/restore.sh`
- `tools/ops/backup_restore/verify.sh`
- `tools/ops/backup_restore/restore_drill_runner.py`
- `deployments/docker/compose.restore.yml`
- `ops/runbooks/restore-drills/RESTORE_DRILL_OVERVIEW.md`
- `tools/gates/phase9_restore_drill_gate.sh`

### 9.4 Runbook Validation
- `ops/runbooks/RUNBOOK_INDEX.md`
- `tools/quality/runbook_lint.py`
- `tools/gates/phase9_runbooks_gate.sh`

---

## PHASE 10: BUSINESS READINESS

### Required Directories
```
mkdir -p deployments/demo
mkdir -p docs/business
mkdir -p tools/business
mkdir -p db/migrations
mkdir -p artifacts/business
```

### 10.1 Demo Environment Isolation
- `deployments/demo/compose.demo.yml`
- `deployments/demo/.env.demo.example`
- `deployments/demo/reset_demo.sh`
- `deployments/demo/README.md`
- `tools/quality/demo_isolation_validate.py`
- `tools/gates/phase10_demo_env_gate.sh`

### 10.2 Beta Onboarding + Feedback
- `docs/business/BETA_ONBOARDING.md`
- `docs/business/BETA_SUPPORT_PLAYBOOK.md`
- `docs/business/BETA_CHANGELOG.md`
- `db/migrations/xxx_feedback.sql`
- `tools/quality/beta_onboarding_validate.py`
- `tools/gates/phase10_beta_readiness_gate.sh`

### 10.3 Success Metrics
- `docs/business/SUCCESS_METRICS.md`
- `ops/observability/grafana/dashboards/zakops_business.json`
- `tools/business/weekly_summary.py`
- `tools/gates/phase10_success_metrics_gate.sh`

### 10.4 Beta User Signoff
- `tools/quality/manual_signoff_validate.py`
- `tools/gates/phase10_beta_user_gate.sh`

---

## MAKEFILE UPDATES

Add these targets to the root Makefile:
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
```

---

## REFERENCE

Full implementation details in:
`/home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_PHASES_9_10.md`

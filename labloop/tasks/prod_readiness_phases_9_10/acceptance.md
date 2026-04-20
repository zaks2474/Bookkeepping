# Acceptance Criteria

## Definition of Done

The task is complete when ALL of the following are true:

### Phase 9: Operations + Game Days

#### Blue/Green Deployment
- [ ] `deployments/bluegreen/` directory exists with all required files
- [ ] `compose.blue.yml` and `compose.green.yml` exist
- [ ] `switch.sh` and `verify.sh` are executable
- [ ] `tools/ops/bluegreen_verify.py` exists
- [ ] `tools/gates/phase9_bluegreen_gate.sh` exists and is executable
- [ ] `artifacts/ops/bluegreen_verify.json` generated with passed=true

#### Game Days
- [ ] `tools/chaos/common.sh` exists
- [ ] Game day scripts `gd1_db_failure.sh` through `gd6_memory_pressure.sh` exist
- [ ] `tools/chaos/game_day_runner.py` exists
- [ ] `ops/runbooks/game-days/GAME_DAY_OVERVIEW.md` exists
- [ ] Individual game day runbooks (GD1-GD6) exist
- [ ] `tools/gates/phase9_game_day_gate.sh` exists and is executable
- [ ] `artifacts/chaos/game_day_*.json` generated

#### Restore Drill
- [ ] `tools/ops/backup_restore/backup.sh` exists
- [ ] `tools/ops/backup_restore/restore.sh` exists
- [ ] `tools/ops/backup_restore/verify.sh` exists
- [ ] `tools/ops/backup_restore/restore_drill_runner.py` exists
- [ ] `ops/runbooks/restore-drills/RESTORE_DRILL_OVERVIEW.md` exists
- [ ] `tools/gates/phase9_restore_drill_gate.sh` exists and is executable
- [ ] `artifacts/restore/restore_drill_*.json` generated

#### Runbook Validation
- [ ] `ops/runbooks/RUNBOOK_INDEX.md` exists and links all runbooks
- [ ] `tools/quality/runbook_lint.py` exists
- [ ] `tools/gates/phase9_runbooks_gate.sh` exists and is executable
- [ ] `artifacts/ops/runbook_lint.json` generated with passed=true

### Phase 10: Business Readiness

#### Demo Environment
- [ ] `deployments/demo/compose.demo.yml` exists with isolation (different ports, volumes)
- [ ] `deployments/demo/.env.demo.example` exists
- [ ] `deployments/demo/reset_demo.sh` exists and is executable
- [ ] `tools/quality/demo_isolation_validate.py` exists
- [ ] `tools/gates/phase10_demo_env_gate.sh` exists and is executable
- [ ] `artifacts/business/demo_isolation_validation.json` generated

#### Beta Onboarding
- [ ] `docs/business/BETA_ONBOARDING.md` exists with required sections
- [ ] `docs/business/BETA_SUPPORT_PLAYBOOK.md` exists
- [ ] `docs/business/BETA_CHANGELOG.md` exists
- [ ] `db/migrations/xxx_feedback.sql` exists with feedback table schema
- [ ] `tools/quality/beta_onboarding_validate.py` exists
- [ ] `tools/gates/phase10_beta_readiness_gate.sh` exists and is executable
- [ ] `artifacts/business/beta_readiness.json` generated

#### Success Metrics
- [ ] `docs/business/SUCCESS_METRICS.md` exists with required metrics
- [ ] `ops/observability/grafana/dashboards/zakops_business.json` exists (valid JSON)
- [ ] `tools/business/weekly_summary.py` exists
- [ ] `tools/gates/phase10_success_metrics_gate.sh` exists and is executable
- [ ] `artifacts/business/success_metrics_validation.json` generated

#### Beta User Signoff
- [ ] `tools/quality/manual_signoff_validate.py` exists
- [ ] `tools/gates/phase10_beta_user_gate.sh` exists and is executable

### Makefile Integration
- [ ] Root Makefile has `phase9` and `phase10` targets
- [ ] `make phase9` runs successfully
- [ ] `make phase10` runs successfully

### Quality Gates
- [ ] All shell scripts pass syntax check
- [ ] All Python scripts pass syntax check
- [ ] All JSON files are valid

## Verification Steps

1. Run `make phase9` - should exit 0
2. Run `make phase10` - should exit 0
3. Verify artifact files exist and show passing status

## Gate Command

```bash
make phase9 && make phase10
```

This command must exit with code 0 for the task to pass.

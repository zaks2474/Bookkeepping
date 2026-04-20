# Mission: Phase 6 + Phase 7 + Phase 8 - Production Readiness

## Objective

Complete Phase 6 (Evaluation, Red-Team, QA), Phase 7 (Deployment, Monitoring, Operations), and Phase 8 (Scaling, Optimization, Continuous Improvement) for the ZakOps Agent API per the Ultimate Implementation Roadmap v2.

## Background

- **Repo**: `/home/zaks/zakops-agent-api`
- **Gate Command**: `./scripts/bring_up_tests.sh`
- **Artifacts Directory**: `/home/zaks/zakops-agent-api/gate_artifacts/`
- **Authoritative Docs**: `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`

**Prerequisites Completed:**
- Phase 0: Foundations & Alignment ✅
- Phase 1: Core Infrastructure (Security) ✅
- Phase 2: MVP Build ✅
- Phase 3: Intelligence ✅
- Phase 4: Tooling + Integrations ✅
- Phase 5: Hardening, Security, Reliability ✅

## Scope

---

### Phase 6 - Evaluation, Red-Team, QA

#### P6-CI-001: CI Gate Runner
- Run `./scripts/bring_up_tests.sh` in CI mode
- Retain artifacts and publish summary
- CI must be reproducible and deterministic
- Output `gate_artifacts/ci_gate_run.log` with `CI_GATES: PASSED`

#### P6-REDTEAM-001: Adversarial Red-Team Suite
- Implement adversarial test suites:
  - Prompt injection attempts
  - Tool-arg manipulation
  - Role escalation attempts
  - Data exfil attempts (cloud routing)
- All attacks must be blocked/detected
- Output `gate_artifacts/redteam_report.json` with `REDTEAM: PASSED`

#### P6-EVALTREND-001: Eval Trend Tracking
- Store eval trends (tool accuracy + retrieval metrics + latency)
- Append-only trend tracking across runs
- Output `gate_artifacts/eval_trend.csv` (or JSON) updated with each run

---

### Phase 7 - Deployment, Monitoring, Operations

#### P7-OPS-001: Runbooks
- Create comprehensive runbooks:
  - Startup/shutdown procedures
  - Key rotation procedures
  - Backup/restore procedures
  - Stuck approval triage
  - Suspected double execution triage
- Runbooks must be linted and validated
- Output `gate_artifacts/runbook_lint.log` with `RUNBOOK_LINT: PASSED`

#### P7-BACKUP-001: Backup/Restore Drill
- Execute and log a backup/restore drill
- Must be non-destructive
- Verify data integrity after restore
- Output `gate_artifacts/backup_restore_drill.log` with `BACKUP_RESTORE: PASSED`

#### P7-MONITORING-001: Monitoring Smoke
- Define required metrics and alert thresholds
- Implement monitoring smoke checks
- Verify dashboards are accessible
- Output `gate_artifacts/monitoring_smoke.log` with `MONITORING_SMOKE: PASSED`

#### P7-RELEASE-001: Release Readiness Check
- Implement Go/No-Go checklist gate
- Compute release readiness from required artifacts
- All prerequisite phases must PASS
- Output `gate_artifacts/release_readiness_check.json` with `RELEASE_READY: PASSED`

---

### Phase 8 - Scaling, Optimization, Continuous Improvement

#### P8-BENCH-001: Benchmarks
- Record baseline benchmarks with hardware signature:
  - vLLM tok/s baseline
  - Agent API latency P50/P95
  - Tool call latency P95
  - Retrieval latency P95
  - Queue throughput
- Define migration triggers:
  - pgvector → Qdrant triggers
  - Postgres queue → Redis triggers
  - Model upgrade trigger
- Output `gate_artifacts/benchmarks.json` with `BENCHMARKS: PASSED`
- Output `gate_artifacts/migration_trigger_status.json`

#### P8-CADENCE-001: CI Cadence Schedule
- Define continuous cadence:
  - Weekly eval refresh
  - Monthly red-team rerun
  - Quarterly restore drill
- Document cadence schedule for CI integration
- Output `gate_artifacts/ci_cadence_schedule.md`

---

## Out of Scope

- No safety-reducing optimizations
- No cross-service scaling beyond single-host profile

## Technical Requirements

- All Phase 0-5 artifacts must remain PASS
- All baseline invariants (BL-01..BL-14) must remain PASS
- Single gate entrypoint: `./scripts/bring_up_tests.sh`
- All artifacts under `gate_artifacts/`
- No mocks for acceptance runs

## Constraints from Decision Lock

### Observability (locked)
- Langfuse self-hosted + OpenTelemetry
- Never log raw prompts/responses (hash + length only)
- Retention: 30 days

### Security (locked)
- Default deny
- All auth attempts logged
- Audit log immutable

## Release Readiness Requirements

No production exposure allowed unless:
1. Phase 2 PASS (MVP E2E real-service, mocks disabled)
2. Phase 1 PASS (at-rest protection + no-raw-content gates)
3. Phase 5 PASS (queue + audit immutability + secrets hygiene + rate limiting)
4. Phase 6 PASS (CI gates + red-team)
5. Phase 7 PASS (runbooks + backup/restore drill)

Required evidence bundle for production:
- Baseline artifacts (BL-01..BL-14)
- All Phase 1-7 artifacts with PASS markers

## References

- `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
- `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`
- `/mnt/c/Users/mzsai/Downloads/ZakOps-Ultimate-Implementation-Roadmap-combine.v2.md`

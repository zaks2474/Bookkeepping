# MISSION: CLAUDE-CODE-ENHANCE-002
## Slimmed Hardening of Claude Hook Infrastructure (7 Enhancements)
## Date: 2026-02-11
## Classification: Infrastructure Enhancement Consolidation
## Prerequisite: /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/SCORECARD.md reports FULL PASS
## Successor: /home/zaks/bookkeeping/docs/QA-CCE2-VERIFY-001.md must report FULL PASS before enhancement backlog is closed

---

## Preamble: Builder Operating Context

The builder already auto-loads `CLAUDE.md`, canonical memory, hooks, deny rules, and path-scoped rules. This mission extends the verified baseline from `CLAUDE-CODE-ENHANCE-001` without redesigning existing behavior.

---

## 1. Mission Objective

Execute one focused enhancement mission that closes the technically justified subset of `QA-CCE-VERIFY-001` opportunities.

Included enhancements:
- ENH-1: Dedicated `make qa-cce-verify`
- ENH-2: Hook contract lint (`validate-claude-hook-config.py`)
- ENH-3: Compact-recovery JSON test harness
- ENH-4: Deterministic fixture mode in `task-completed.sh`
- ENH-5: Machine-readable gate markers in `task-completed.sh`
- ENH-7: Configurable snapshot retention in `pre-compact.sh`
- ENH-10: Objective post-compact context quality assertions

Explicitly removed from this mission:
- ENH-6 (standalone ownership validator script)
- ENH-8 (bookkeeping readability standard + validator)
- ENH-9 (enforced artifact convention script)

Scope boundary:
- This mission touches hook/runtime infrastructure and verification tooling only.
- It does not modify dashboard/backend/API behavior.

---

## 2. Context

Current verified baseline (2026-02-11):
- `/home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/SCORECARD.md` is FULL PASS (`41/41 required checks`, `50 evidence files`).
- Hook contracts are currently valid and functioning.

Why this slim version:
- Technical value is concentrated in runtime reliability + deterministic verification.
- Governance-heavy additions (ENH-6/8/9) create maintenance overhead without proportional risk reduction.

### 2b. Glossary

| Term | Definition |
|------|------------|
| Hook Contract | Required matcher/timeout/async/command semantics for PreCompact, TaskCompleted, SessionStart(compact) |
| Fixture Mode | Deterministic mode where task-completed scans explicit target paths |
| Gate Marker | Structured output line: `GATE_RESULT:<gate>:PASS|FAIL` |

### 2c. Enhancement Mapping Matrix

| Enhancement | Target Implementation |
|-------------|------------------------|
| ENH-1 | `Makefile` target `qa-cce-verify` |
| ENH-2 | `bookkeeping/scripts/validate-claude-hook-config.py` |
| ENH-3 | `bookkeeping/scripts/tests/test-compact-recovery-json.sh` |
| ENH-4 | `task-completed.sh` fixture mode via `TASK_COMPLETED_TARGETS` |
| ENH-5 | Structured gate markers in `task-completed.sh` |
| ENH-7 | `pre-compact.sh` retention via `SNAPSHOT_RETENTION` (default preserved) |
| ENH-10 | `compact-recovery.sh` quality assertions + validator checks |

---

## 3. Architectural Constraints

- **No regression of existing hooks**
Meaning: existing valid pass paths for PreCompact, TaskCompleted, SessionStart, Stop remain valid.
Why: source mission is already FULL PASS.

- **Preserve hook exit semantics**
Meaning: `exit 0` allow, `exit 2` block; do not introduce blocking via `exit 1`.
Why: contract correctness.

- **Backward-compatible defaults**
Meaning: new env-driven controls must preserve current behavior when unset.
Why: safe rollout.

- **Deterministic QA behavior**
Meaning: verification must support deterministic fixture-driven runs.
Why: repeatable QA.

- **No generated-file edits**
Meaning: avoid generated artifacts.
Why: contract-managed outputs.

- **Mission scope fence**
Meaning: no product feature work.
Why: enhancement closure only.

- **`make validate-local` applicability**
Meaning: `make validate-local` is not a required gate for this mission.
Why: mission does not change application codepaths, contract surfaces, or generated API artifacts.

- **WSL hygiene for new scripts**
Meaning: LF endings, executable bit, sane ownership.
Why: runtime safety.

---

## 3b. Anti-Pattern Examples

### WRONG: Hardcoded retention only
```bash
RETENTION=10
```

### RIGHT: Configurable with safe default
```bash
RETENTION="${SNAPSHOT_RETENTION:-10}"
```

### WRONG: Non-deterministic QA scan
```bash
find /home/zaks -type f ...
```

### RIGHT: Fixture-driven scan
```bash
TASK_COMPLETED_TARGETS="/tmp/a.sh,/tmp/b.sh"
```

### WRONG: Human-only gate output
```text
Gate failed
```

### RIGHT: Machine-readable gate output
```text
GATE_RESULT:gate1:FAIL
GATE_RESULT:overall:PASS
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Enhancements unintentionally alter current pass behavior | MEDIUM | HIGH | Phase gates re-validate hook contracts after each runtime edit |
| 2 | Fixture mode behaves like full scan | MEDIUM | MEDIUM | Explicit target-only logic + dedicated harness |
| 3 | `qa-cce-verify` target exists but misses critical checks | MEDIUM | MEDIUM | AC requires complete command coverage in runner |
| 4 | Quality assertions become subjective and brittle | LOW | MEDIUM | Define objective criteria only (non-empty, key paths, recent changes markers) |

---

## 4. Phases

## Phase 0 - Discovery and Baseline
**Complexity:** S
**Estimated touch points:** 1 created

**Purpose:** capture current known-good baseline before edits.

### Tasks
- P0-01: **Create baseline file**
  - File: `/home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-BASELINE.md`
  - Include:
    - hook contract snapshot from `/home/zaks/.claude/settings.json`
    - syntax/ownership snapshots for 3 hook scripts
    - ENH closure checklist for ENH-1/2/3/4/5/7/10
  - **Checkpoint:** baseline exists and has timestamped command output.

### Gate P0
- Baseline document exists and lists all 7 enhancement items.

### Rollback Plan
1. Remove the baseline file.
2. Recreate baseline before proceeding.

---

## Phase 1 - Hook Runtime Hardening
**Complexity:** M
**Estimated touch points:** 3 modified

**Purpose:** implement runtime enhancements in existing hooks.

### Tasks
- P1-01: **Add retention configurability**
  - File: `/home/zaks/.claude/hooks/pre-compact.sh`
  - Add `SNAPSHOT_RETENTION` support with default `10`.
  - **Checkpoint:** default behavior unchanged when env unset.

- P1-02: **Add deterministic fixture mode**
  - File: `/home/zaks/.claude/hooks/task-completed.sh`
  - Add `TASK_COMPLETED_TARGETS` override for controlled scans.
  - **Checkpoint:** fixture mode scans only provided targets.

- P1-03: **Add machine-readable markers**
  - File: `/home/zaks/.claude/hooks/task-completed.sh`
  - Emit `GATE_RESULT:*` lines for each gate and overall status.
  - **Checkpoint:** output parseable for pass and fail paths.

- P1-04: **Add objective context quality assertions**
  - File: `/home/zaks/.claude/hooks/compact-recovery.sh`
  - Enforce objective criteria only:
    - non-empty context
    - contains key path markers
    - contains recent changes marker
  - **Checkpoint:** JSON remains valid and includes quality metadata.

### Gate P1
- Modified hooks pass `bash -n`, no CRLF, and targeted runtime checks.

### Rollback Plan
1. Restore edited hooks from pre-phase backups.
2. Re-run baseline checks.

---

## Phase 2 - Validator, Harness, and Make Target Wiring
**Complexity:** M
**Estimated touch points:** 4 created, 1 modified

**Purpose:** add deterministic verification tooling and single command entrypoint.

### Tasks
- P2-01: **Create hook contract validator**
  - File: `/home/zaks/bookkeeping/scripts/validate-claude-hook-config.py`
  - Validate required events and contract semantics.
  - **Checkpoint:** passes on current settings.

- P2-02: **Create compact-recovery JSON harness**
  - File: `/home/zaks/bookkeeping/scripts/tests/test-compact-recovery-json.sh`
  - Validate required JSON keys and objective context criteria.
  - **Checkpoint:** harness exits 0.

- P2-03: **Create task-completed fixture harness**
  - File: `/home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh`
  - Verify deterministic pass/fail cycle using fixtures.
  - **Checkpoint:** expected exit codes verified.

- P2-04: **Create combined runner**
  - File: `/home/zaks/bookkeeping/scripts/run-qa-cce-verify.sh`
  - Execute all mission validators/harnesses in deterministic order.
  - **Checkpoint:** exits non-zero on first failure.

- P2-05: **Add Make target**
  - File: `/home/zaks/zakops-agent-api/Makefile`
  - Add `qa-cce-verify` target that calls runner script.
  - **Checkpoint:** `make qa-cce-verify` runs successfully from repo root.

### Gate P2
- Validator + harnesses pass and make target passes.

### Rollback Plan
1. Remove newly created scripts.
2. Revert Makefile target addition only.

---

## Phase 3 - Final Verification and Bookkeeping
**Complexity:** S
**Estimated touch points:** 2 created, 1 updated

**Purpose:** complete evidence closure and handoff to QA.

### Tasks
- P3-01: **Run final mission verification suite**
  - Commands:
    - `python3 /home/zaks/bookkeeping/scripts/validate-claude-hook-config.py`
    - `bash /home/zaks/bookkeeping/scripts/tests/test-compact-recovery-json.sh`
    - `bash /home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh`
    - `cd /home/zaks/zakops-agent-api && make qa-cce-verify`
  - **Checkpoint:** all pass.

- P3-02: **Create completion report**
  - File: `/home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md`
  - Must map every AC to evidence.
  - **Checkpoint:** AC coverage complete.

- P3-03: **Update mission checkpoint and CHANGES**
  - Files:
    - `/home/zaks/bookkeeping/mission-checkpoints/CLAUDE-CODE-ENHANCE-002.md`
    - `/home/zaks/bookkeeping/CHANGES.md`
  - **Checkpoint:** successor QA explicitly unblocked.

### Gate P3
- Verification suite passes, completion/checkpoint/changelog entries exist.

### Rollback Plan
1. Fix failing check.
2. Re-run full final suite and regenerate closure artifacts if needed.

---

## 4b. Dependency Graph

```
Phase 0 (Baseline)
    |
    v
Phase 1 (Hook Runtime Hardening)
    |
    v
Phase 2 (Validator/Harness/Make Wiring)
    |
    v
Phase 3 (Final Verification + Closure)
```

---

## 5. Acceptance Criteria

### AC-1: Baseline captured for all 7 enhancement items
`CLAUDE-CODE-ENHANCE-002-BASELINE.md` exists and tracks ENH-1/2/3/4/5/7/10.

### AC-2: Fixture mode implemented for TaskCompleted
`task-completed.sh` supports deterministic `TASK_COMPLETED_TARGETS` override.

### AC-3: Machine-readable gate markers implemented
`task-completed.sh` emits `GATE_RESULT` lines.

### AC-4: Snapshot retention is configurable and backward compatible
`pre-compact.sh` supports `SNAPSHOT_RETENTION` with default behavior preserved.

### AC-5: Compact recovery quality assertions are objective
`compact-recovery.sh` validates non-empty context + required markers.

### AC-6: Hook contract validator implemented
`validate-claude-hook-config.py` exists and exits 0 on valid config.

### AC-7: Compact-recovery harness implemented
`test-compact-recovery-json.sh` exists and exits 0.

### AC-8: TaskCompleted fixture harness implemented
`test-task-completed-fixture-mode.sh` exists and exits 0.

### AC-9: `make qa-cce-verify` implemented and passing
Make target exists and runs all required checks successfully.

### AC-10: No regression and bookkeeping closure complete
Existing hook chain remains intact; completion report, checkpoint, and CHANGES entry are present.

---

## 6. Guardrails

1. Do not add product features.
2. Do not modify generated files.
3. Do not weaken hook exit-code semantics.
4. Preserve existing SessionStart/Stop baseline behavior.
5. Keep new scripts ASCII/LF/executable.
6. Keep quality checks objective, not subjective.
7. `make validate-local` is not a required gate for this mission.
8. Do not remove existing make targets or CI gates.
9. Do not use destructive git history commands.
10. Do not mark complete without AC-to-evidence mapping.

---

## 7. Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture baseline from real current files?
- [ ] Did I track exactly 7 enhancements (1,2,3,4,5,7,10)?

### After hook edits
- [ ] Are defaults backward compatible?
- [ ] Is output deterministic and machine-readable?
- [ ] Did I preserve LF/executable/ownership hygiene?

### Before mission close
- [ ] Does `make qa-cce-verify` pass now?
- [ ] Are all ACs mapped in completion report?
- [ ] Is checkpoint updated with QA successor?

---

## 8. File Paths Reference

### Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/.claude/hooks/pre-compact.sh` | 1 | configurable retention |
| `/home/zaks/.claude/hooks/task-completed.sh` | 1 | fixture mode + machine markers |
| `/home/zaks/.claude/hooks/compact-recovery.sh` | 1 | objective quality assertions |
| `/home/zaks/zakops-agent-api/Makefile` | 2 | add `qa-cce-verify` target |
| `/home/zaks/bookkeeping/CHANGES.md` | 3 | mission closure entry |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-BASELINE.md` | 0 | baseline and enhancement checklist |
| `/home/zaks/bookkeeping/scripts/validate-claude-hook-config.py` | 2 | hook contract validation |
| `/home/zaks/bookkeeping/scripts/tests/test-compact-recovery-json.sh` | 2 | compact recovery harness |
| `/home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh` | 2 | deterministic task-completed harness |
| `/home/zaks/bookkeeping/scripts/run-qa-cce-verify.sh` | 2 | unified runner |
| `/home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md` | 3 | completion evidence report |
| `/home/zaks/bookkeeping/mission-checkpoints/CLAUDE-CODE-ENHANCE-002.md` | 3 | checkpoint and successor handoff |

### Files to Read (Do Not Modify)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/QA-CCE-VERIFY-001.md` | source enhancement findings |
| `/home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/SCORECARD.md` | verified baseline |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | format compliance |

---

## 9. Stop Condition

Stop when AC-1 through AC-10 are satisfied, `make qa-cce-verify` passes, and completion/checkpoint/changelog artifacts are present.

Do not proceed to subsequent Claude hook enhancement work until `/home/zaks/bookkeeping/docs/QA-CCE2-VERIFY-001.md` reports FULL PASS.

---
*End of Mission Prompt - CLAUDE-CODE-ENHANCE-002*

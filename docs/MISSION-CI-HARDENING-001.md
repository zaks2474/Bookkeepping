# MISSION: CI-HARDENING-001
## CI and Pipeline Hardening for Frontend Governance and Hook Resilience
## Date: 2026-02-10
## Classification: Infrastructure Remediation
## Prerequisite: /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/QA-FGH-VERIFY-001-COMPLETION.md reports FULL PASS
## Successor: QA-CIH-VERIFY-001 (must report FULL PASS before closing CI hardening backlog)

---

## Preamble: Builder Operating Context

The builder auto-loads `/home/zaks/zakops-agent-api/CLAUDE.md`, canonical memory at `/root/.claude/projects/-home-zaks/memory/MEMORY.md`, hooks, deny rules, and path-scoped rules. This mission references those systems and adds mission-specific CI and enforcement hardening only.

---

## 1. Mission Objective

This mission hardens CI and local validation pipelines so frontend governance enforcement is repeatable and regression-resistant. It closes the remaining high-value enhancement backlog after `FRONTEND-GOVERNANCE-HARDENING-001` and `QA-FGH-VERIFY-001`.

This is an infrastructure-hardening mission, not a product-feature mission. It modifies hook resilience, validation scripts, Make targets, and CI workflow wiring. It does not change dashboard business behavior, backend API contracts, or database schema.

Mandatory inclusion from your direction:
- **Step 1 is inside this mission as Phase 1**: fix `/home/zaks/.claude/hooks/stop.sh` project detection fallback so constrained PATH runs do not skip all gates.

Primary source materials:
- `/home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/QA-FGH-VERIFY-001-COMPLETION.md`
- `/home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md`
- `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`
- `/home/zaks/.claude/hooks/stop.sh`
- `/home/zaks/zakops-agent-api/.github/workflows/ci.yml`

Out of scope:
- Frontend feature implementation
- Net-new contract surfaces beyond current 14
- Broad redesign of CI architecture
- Playwright infrastructure rollout beyond policy/enforcement checks

---

## 2. Context

Verified current facts:

1. Governance mission passed with one INFO in QA:
- `VF-01.5` showed constrained PATH can skip hook gates due project detection before Gate E executes.
- Source: `/home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/QA-FGH-VERIFY-001-COMPLETION.md`

2. `stop.sh` Gate E scanner resilience exists, but project detection path is still brittle under highly constrained launch contexts.
- File: `/home/zaks/.claude/hooks/stop.sh`

3. CI plan-gates still use a direct `rg`-dependent Gate E snippet.
- File: `/home/zaks/zakops-agent-api/.github/workflows/ci.yml`

4. Frontend governance rules now exist and should be enforced continuously:
- `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
- `/home/zaks/zakops-agent-api/.claude/rules/accessibility.md`
- `/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md`

5. Surface 9 validator is enriched and must remain stable.
- `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh`

6. 14-surface contract baseline is currently healthy and must not regress.
- `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
- `/home/zaks/zakops-agent-api/CLAUDE.md`
- `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`

---

## Crash Recovery Protocol <!-- Adopted from Improvement Area IA-2 -->

If resuming after crash/interruption, run exactly:

```bash
cd /home/zaks/zakops-agent-api && git log --oneline -5
cd /home/zaks/zakops-agent-api && make validate-local
find /home/zaks/bookkeeping/docs -maxdepth 1 -type f -name "MISSION-CI-HARDENING-001*" -o -name "CI-HARDENING-001-*"
```

If baseline validation fails during recovery, classify pre-existing vs mission-induced breakage before continuing.

---

## Continuation Protocol <!-- Adopted from Improvement Area IA-7 -->

At end of each session, update:
- `/home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md`

Checkpoint minimum content:
1. Completed phases
2. Remaining phases
3. Current validation state (`make validate-local`, governance target, CI dry-run checks)
4. Open blockers and decisions
5. Exact next command

---

## Context Checkpoint <!-- Adopted from Improvement Area IA-1 -->

If context becomes constrained mid-mission:
1. Write status to `/home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md`
2. Commit logically complete intermediate work
3. Resume via Crash Recovery Protocol

---

## 2b. Glossary

| Term | Definition |
|------|-----------|
| Step 1 | Mandatory first hardening task: stop-hook project-detection fallback fix |
| Gate E | Raw `httpx` usage guard in `stop.sh` and CI plan-gates |
| Project detection | Logic that determines whether hook should run gates or skip |
| Governance gate | Validation enforcing frontend governance rules and section anchors |
| Frontmatter lint | Validation that rule files include valid path-scoped frontmatter |
| Policy drift | Mismatch between documented frontend tooling policy and live config assumptions |

---

## 3. Architectural Constraints

- **Step 1 first, no exceptions**
Meaning: Project-detection fallback hardening in `stop.sh` must happen before any CI wiring work.
Why: It closes the only residual QA INFO on core runtime enforcement.

- **No feature code changes**
Meaning: Do not edit dashboard/backend product logic to satisfy CI checks.
Why: Mission is enforcement hardening only.

- **Fail-closed principle for critical guards**
Meaning: Scanner or detection errors must not silently pass critical checks.
Why: Silent pass creates hidden security/integrity risk.

- **CI checks must be deterministic**
Meaning: Avoid environment-sensitive checks that randomly pass/fail.
Why: CI trust depends on stable results.

- **Surface 9 and 14-surface baseline must not regress**
Meaning: Preserve existing validation behavior and counts.
Why: Previous mission chain depends on stable enforcement.

- **Generated files remain protected**
Meaning: No edits to `*.generated.ts` or `*_models.py`.
Why: Pipeline-owned artifacts.

- **Port 8090 remains forbidden**
Meaning: No new references in CI scripts, rules, or docs.
Why: Legacy drift hazard.

- **WSL safety remains mandatory**
Meaning: New shell scripts use LF; ownership is sane under `/home/zaks/`.
Why: Prevent delayed failures.

---

## 3b. Anti-Pattern Examples

### WRONG: Hook skips when project detection cannot resolve git
```bash
MONOREPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$MONOREPO_ROOT" ]; then
  echo "skipping"
  exit 0
fi
```

### RIGHT: Multi-path project detection fallback
```bash
# 1) git rev-parse when available
# 2) explicit fallback path when Makefile signature exists
# 3) fail/skip with explicit reason only when no trusted root found
```

### WRONG: CI Gate E assumes rg only
```bash
if rg -n "httpx\." apps/agent-api/app/core/langgraph/tools/deal_tools.py; then
  exit 1
fi
```

### RIGHT: CI Gate E scanner fallback with explicit rc handling
```bash
if command -v rg; then scanner=rg; else scanner=grep; fi
# rc=0 violation, rc=1 clean, rc>=2 scanner error (fail)
```

### WRONG: Rule files accepted without path frontmatter checks
```text
Rule exists -> PASS
```

### RIGHT: Rule structure enforced in CI
```text
Rule exists + frontmatter exists + required dashboard paths present -> PASS
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Step 1 patch fixes one launch path but still skips gates in another shell context | HIGH | Residual hidden enforcement gap | Phase 1 gate includes normal + constrained PATH + outside-repo tests |
| 2 | CI gate scripts rely on local-only paths and fail on GitHub runner | HIGH | CI noise and failed merges | Phase 2 enforces repo-local checks for CI-critical gates |
| 3 | New governance checks are too brittle and create false positives | MEDIUM | Developer friction and bypass pressure | Phase 2 decision tree refines anchors and robust matching |
| 4 | CI wiring lands without local make target parity | MEDIUM | Local/CI behavior divergence | Phase 3 creates aggregate make target used by both local and CI |
| 5 | Hardening work regresses 14-surface baseline | MEDIUM | Breaks prior remediation chain | Every phase gate includes `make validate-local`; final includes contract validation |

---

## 4. Phases

## Phase 0 - Discovery and Baseline
**Complexity:** S  
**Estimated touch points:** 0 files modified

**Purpose:** Capture pre-change evidence and validate current baseline.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Create baseline evidence file**
  - Create `/home/zaks/bookkeeping/docs/CI-HARDENING-001-BASELINE.md`.
  - Capture outputs for:
    - `cd /home/zaks/zakops-agent-api && make validate-local`
    - `cd /home/zaks/zakops-agent-api && make validate-surface9`
    - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
  - **Checkpoint:** Baseline file includes timestamped outputs.

- P0-02: **Capture hook and CI Gate E baseline**
  - Record current Gate E and project-detection blocks from:
    - `/home/zaks/.claude/hooks/stop.sh`
    - `/home/zaks/zakops-agent-api/.github/workflows/ci.yml`
  - **Checkpoint:** Evidence clearly captures pre-change behavior.

### Decision Tree
- **IF** baseline validation fails -> stop and classify pre-existing breakage.
- **ELSE** proceed.

### Rollback Plan
1. No rollback required (read-only phase).
2. Verify clean state: `cd /home/zaks/zakops-agent-api && git status --short`.

### Gate P0
- Baseline evidence file exists.
- Hook and CI Gate E pre-state captured.

---

## Phase 1 - Mandatory Step 1: stop.sh Project Detection Fallback Hardening
**Complexity:** S  
**Estimated touch points:** 1 file modified

**Purpose:** Ensure hook gates run under constrained launch contexts when repo root is still inferable.

### Blast Radius
- **Services affected:** Hook runtime validation flow
- **Pages affected:** None
- **Downstream consumers:** Session stop enforcement

### Tasks
- P1-01: **Patch project detection in stop hook**
  - Modify `/home/zaks/.claude/hooks/stop.sh` to use ordered project detection:
    - `git rev-parse --show-toplevel` when available
    - fallback to explicit known monorepo path (`/home/zaks/zakops-agent-api`) when it exists and contains expected Makefile signature
    - optional env override path if provided (for testability)
    - explicit skip reason only when no trusted root is discoverable
  - **Checkpoint:** Detection logic is explicit and deterministic.

- P1-02: **Preserve existing gate chain**
  - Ensure Gates A/B/E behavior remains unchanged except improved project detection entry.
  - **Checkpoint:** Gate labels and time-budget checks remain coherent.

- P1-03: **Validate detection paths**
  - Test scenarios:
    - normal runtime from repo context
    - constrained PATH launch from login shell
    - outside-repo launch with no trusted root (intentional skip with explicit message)
  - **Checkpoint:** constrained PATH no longer triggers false global skip when trusted root exists.

### Decision Tree
- **IF** trusted root cannot be validated -> skip with explicit reason (not silent).
- **ELSE** run gates.

### Rollback Plan
1. Revert `/home/zaks/.claude/hooks/stop.sh` only.
2. Re-run baseline hook tests and `make validate-local`.

### Gate P1
- Constrained PATH run executes gates when trusted root exists.
- Outside-repo run skips with explicit reason.
- No regression in normal hook behavior.

---

## Phase 2 - Add Repo-Local CI Governance Validation Scripts
**Complexity:** M  
**Estimated touch points:** 3-5 files created/modified

**Purpose:** Convert governance checks into reusable scripts consumable by local and CI workflows.

### Blast Radius
- **Services affected:** Validation scripts and CI gate inputs
- **Pages affected:** None
- **Downstream consumers:** Make targets, CI workflows, QA missions

### Tasks
- P2-01: **Create rule frontmatter validator script**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh`.
  - Validate `.claude/rules/*.md` frontmatter schema and required path coverage for dashboard governance rules.
  - **Checkpoint:** Script exits non-zero on malformed/missing frontmatter for scoped governance rules.

- P2-02: **Create governance anchor validator script**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh`.
  - Verify required anchors across:
    - `design-system.md`
    - `accessibility.md`
    - `component-patterns.md`
  - Include no-8090 drift check for governance files.
  - **Checkpoint:** Script outputs clear PASS/FAIL per check family.

- P2-03: **Create CI Gate E scanner fallback script**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh`.
  - Implement rg->grep fallback and explicit rc handling semantics (0 violation, 1 clean, >=2 error).
  - **Checkpoint:** Script can replace inline CI Gate E snippet.

- P2-04: **Optional local-only hook contract validator**
  - Optional script: `/home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-contract.sh`.
  - If `/home/zaks/.claude/hooks/stop.sh` exists, validate expected detection/gate markers.
  - Must not break CI when hook file is absent.
  - **Checkpoint:** Local contract check supports QA evidence without CI false failures.

### Decision Tree
- **IF** a script depends on non-repo paths -> make that check optional or local-only.
- **ELSE** enforce strictly in CI.

### Rollback Plan
1. Remove new scripts and references.
2. Re-run baseline validation.

### Gate P2
- New scripts execute successfully and produce deterministic results.
- Repo-local checks are CI-safe.

---

## Phase 3 - Add Aggregate Make Targets and Local/CI Parity
**Complexity:** M  
**Estimated touch points:** 1 file modified (+ optional docs)

**Purpose:** Create a single local entrypoint for governance hardening checks and align local with CI behavior.

### Blast Radius
- **Services affected:** Make target graph
- **Pages affected:** None
- **Downstream consumers:** Developers, hooks, CI jobs

### Tasks
- P3-01: **Add aggregate governance target**
  - Modify `/home/zaks/zakops-agent-api/Makefile`.
  - Add target `validate-frontend-governance` that runs:
    - rule frontmatter validator
    - frontend governance anchor validator
    - CI Gate E scan validator
  - **Checkpoint:** target exists and exits non-zero on violations.

- P3-02: **Align with existing validation flows**
  - Decide and wire where appropriate:
    - add to `validate-local` and/or `validate-full`
    - keep runtime acceptable (no significant slowdown)
  - **Checkpoint:** chosen placement documented and tested.

- P3-03: **Retain 14-surface baseline integrity**
  - Ensure `validate-contract-surfaces` remains unchanged in semantics.
  - **Checkpoint:** 14-surface output unaffected.

### Decision Tree
- **IF** adding governance target to `validate-local` causes unacceptable runtime -> keep separate but mandatory in CI.
- **ELSE** include in `validate-local` for strongest parity.

### Rollback Plan
1. Revert Makefile changes.
2. Re-run `make validate-local` and `make validate-contract-surfaces`.

### Gate P3
- `make validate-frontend-governance` passes.
- Local validation path remains stable.

---

## Phase 4 - CI Workflow Hardening and Gate Wiring
**Complexity:** L  
**Estimated touch points:** 1-2 files modified

**Purpose:** Enforce governance checks and scanner resilience at CI level.

### Blast Radius
- **Services affected:** GitHub CI workflow
- **Pages affected:** None
- **Downstream consumers:** PR merge quality gates

### Tasks
- P4-01: **Replace inline CI Gate E with script**
  - Modify `/home/zaks/zakops-agent-api/.github/workflows/ci.yml` plan-gates Gate E step.
  - Replace inline `rg` snippet with `bash tools/infra/validate-gatee-scan.sh`.
  - **Checkpoint:** CI gate logic now matches fallback semantics.

- P4-02: **Add frontend governance CI gate**
  - Add CI step (or dedicated lightweight job) running:
    - `make validate-frontend-governance`
  - Ensure step runs for relevant change sets (dashboard/rules/infra scripts/workflow edits).
  - **Checkpoint:** CI enforces governance rules and structure.

- P4-03: **Preserve existing gate chain behavior**
  - Keep current plan-gates contract checks and dependency graph coherent.
  - **Checkpoint:** CI workflow remains readable and non-fragile.

### Decision Tree
- **IF** CI job fan-out causes excessive runtime -> keep in `plan-gates` rather than new job.
- **ELSE** dedicated job is acceptable if dependency graph remains clear.

### Rollback Plan
1. Revert CI workflow changes.
2. Re-run local governance target and baseline validations.

### Gate P4
- CI workflow references script-based Gate E.
- Frontend governance checks are enforced by CI path.

---

## Phase 5 - Documentation and Policy Drift Safeguards
**Complexity:** M  
**Estimated touch points:** 2-4 files modified/created

**Purpose:** Make hardening behavior discoverable and self-maintainable.

### Blast Radius
- **Services affected:** Operator/developer documentation
- **Pages affected:** None
- **Downstream consumers:** Future missions, QA, maintainers

### Tasks
- P5-01: **Document CI governance gate usage**
  - Update relevant docs to mention:
    - `make validate-frontend-governance`
    - CI step location in `ci.yml`
    - Gate E fallback semantics
  - **Checkpoint:** docs provide command-level guidance.

- P5-02: **Add policy drift check (repo-safe)**
  - Add a repo-safe check script or documented process to keep governance policy statements aligned with live assumptions.
  - Avoid hard failing CI on non-repo path dependencies.
  - **Checkpoint:** drift mechanism exists and is explicitly scoped.

- P5-03: **Record mission evidence references**
  - Prepare evidence index for QA successor mission.
  - **Checkpoint:** evidence mapping ready before final verification.

### Decision Tree
- **IF** a drift check requires non-repo files -> make it informational/local-only.
- **ELSE** enforce in CI.

### Rollback Plan
1. Revert documentation or drift-check additions.
2. Re-run local governance validation.

### Gate P5
- Docs include governance and CI hardening references.
- Drift safeguard exists with explicit enforcement scope.

---

## Phase 6 - Final Verification and Bookkeeping
**Complexity:** M  
**Estimated touch points:** 2-4 files modified

**Purpose:** Validate end-to-end mission success and close with traceable evidence.

### Blast Radius
- **Services affected:** Validation and documentation flow
- **Pages affected:** None
- **Downstream consumers:** QA-CIH-VERIFY-001

### Tasks
- P6-01: **Run final validation suite**
  - `cd /home/zaks/zakops-agent-api && make validate-frontend-governance`
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api && make validate-surface9`
  - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
  - `cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh`
  - **Checkpoint:** all required commands pass.

- P6-02: **Create completion report**
  - Create `/home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md` with:
    - phase outcomes
    - AC-by-AC evidence mapping
    - before/after summary for Step 1 behavior
  - **Checkpoint:** completion report contains explicit evidence paths.

- P6-03: **Update bookkeeping**
  - Update `/home/zaks/bookkeeping/CHANGES.md`.
  - Update `/home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md`.
  - **Checkpoint:** closure artifacts complete.

### Decision Tree
- **IF** any final gate fails -> remediate and re-run failed gate plus `make validate-local`.
- **ELSE** finalize and hand off to QA successor.

### Rollback Plan
1. Revert latest phase changes.
2. Re-run baseline validation commands.
3. Rebuild completion evidence.

### Gate P6
- Final suite passes.
- Completion and bookkeeping artifacts exist and are complete.

---

## 4b. Dependency Graph

```
Phase 0 (Discovery and Baseline)
    |
    v
Phase 1 (Mandatory Step 1: stop.sh detection fallback)
    |
    v
Phase 2 (Repo-local governance scripts)
    |
    v
Phase 3 (Make target parity)
    |
    v
Phase 4 (CI workflow hardening)
    |
    v
Phase 5 (Documentation and drift safeguards)
    |
    v
Phase 6 (Final verification and bookkeeping)
```

Phases execute sequentially. Phase 1 is a hard prerequisite for all later phases.

---

## 5. Acceptance Criteria

### AC-1: Baseline Evidence Captured
`CI-HARDENING-001-BASELINE.md` exists with pre-change validation and hook/CI Gate E snapshots.

### AC-2: Step 1 Completed
`/home/zaks/.claude/hooks/stop.sh` project detection fallback is hardened and no longer globally skips when trusted root is inferable.

### AC-3: Hook Detection Behavior Verified
Normal, constrained PATH, and outside-repo behavior are explicitly tested and documented.

### AC-4: Rule Frontmatter Validator Implemented
CI-safe script validates governance rule frontmatter and path scopes.

### AC-5: Governance Anchor Validator Implemented
CI-safe script validates required governance anchors across frontend rule files.

### AC-6: Scripted CI Gate E Validation Implemented
Inline CI `rg` dependency is replaced by a script with scanner fallback and explicit rc handling.

### AC-7: Aggregate Make Target Added
`make validate-frontend-governance` exists and runs all required governance checks.

### AC-8: CI Workflow Enforces Governance
`ci.yml` includes governance target and script-based Gate E enforcement.

### AC-9: Surface 9 and 14-Surface Baseline Preserved
`make validate-surface9` and `make validate-contract-surfaces` pass with unchanged core semantics.

### AC-10: Documentation Updated
CI hardening behavior and commands are documented and discoverable.

### AC-11: No Regressions
`make validate-local` passes; no forbidden generated/migration changes introduced.

### AC-12: Bookkeeping Complete
CHANGES, checkpoint, and completion report are updated with evidence links.

---

## 6. Guardrails

1. Do not change frontend product behavior in this mission.
2. Do not alter backend API semantics or database schema.
3. Do not weaken existing hook gate semantics to force pass.
4. Do not make CI hard-fail on non-repo path dependencies.
5. Do not remove existing Surface 9 checks while adding new gates.
6. Do not edit generated files or migration files.
7. Do not introduce port 8090 references.
8. Keep hook and CI guard behavior fail-closed for scanner/runtime errors.
9. Maintain local and CI parity where feasible.
10. Capture evidence for each phase gate.

---

## 7. Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture baseline hook and CI Gate E behavior before edits?
- [ ] Did I confirm 14-surface baseline was healthy pre-change?
- [ ] Did I log baseline outputs with timestamps?

### After Phase 1
- [ ] Does constrained PATH still run gates when trusted root exists?
- [ ] Does outside-repo launch skip with explicit reason?
- [ ] Did I avoid introducing silent pass paths?

### After Phases 2-4
- [ ] Are new validators CI-safe and deterministic?
- [ ] Did I replace inline CI Gate E logic with script-based fallback?
- [ ] Does `make validate-frontend-governance` provide local/CI parity?

### Before Mission Complete
- [ ] Did final validation suite pass?
- [ ] Is 14-surface baseline still green?
- [ ] Are completion, CHANGES, and checkpoint artifacts updated?

---

## 8. File Paths Reference

### Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/.claude/hooks/stop.sh` | 1 | Step 1 project-detection fallback hardening |
| `/home/zaks/zakops-agent-api/Makefile` | 3 | Add `validate-frontend-governance` target and parity wiring |
| `/home/zaks/zakops-agent-api/.github/workflows/ci.yml` | 4 | Use script-based Gate E and governance gate wiring |
| `/home/zaks/bookkeeping/CHANGES.md` | 6 | Record CI hardening changes |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh` | 2 | Validate rule frontmatter/path scopes |
| `/home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh` | 2 | Validate governance anchors and drift |
| `/home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh` | 2 | CI-safe Gate E scanner fallback check |
| `/home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-contract.sh` | 2 optional | Local-only hook contract verification |
| `/home/zaks/bookkeeping/docs/CI-HARDENING-001-BASELINE.md` | 0 | Baseline evidence |
| `/home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md` | 6 | Completion report with AC mapping |
| `/home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md` | all | Continuation checkpoint |

### Files to Read (Do Not Modify Unless Explicit Task Requires It)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/QA-FGH-VERIFY-001-COMPLETION.md` | Source of residual INFO and ENH context |
| `/home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md` | Upstream execution mission constraints |
| `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md` | Original gap registry context |
| `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` | Governance source rule |
| `/home/zaks/zakops-agent-api/.claude/rules/accessibility.md` | Governance rule |
| `/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md` | Governance rule |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` | Existing enforcement baseline |
| `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` | 14-surface baseline validator |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Prompt formatting standard |

---

## 9. Stop Condition

Stop when AC-1 through AC-12 are all satisfied, including mandatory Step 1 completion, CI governance gates are wired and passing, and no regressions appear in Surface 9 or 14-surface baseline validation.

Do not proceed to broader CI redesign initiatives or new feature work in this mission. Those are separate follow-on scopes after `QA-CIH-VERIFY-001` completes with FULL PASS.

---

*End of Mission Prompt - CI-HARDENING-001*

# MISSION: INFRA-ENHANCEMENTS-UNIFIED-001
## Unified Enhancement Execution for Surface, Governance, and CI Hardening
## Date: 2026-02-10
## Classification: Infrastructure Enhancement Consolidation
## Prerequisite: QA-S10-14-VERIFY-001, QA-FGH-VERIFY-001, and QA-CIH-VERIFY-001 all report FULL PASS
## Successor: QA-IEU-VERIFY-001 (must report FULL PASS before enhancement backlog is considered closed)

---

## Preamble: Builder Operating Context

The builder auto-loads `/home/zaks/zakops-agent-api/CLAUDE.md`, canonical memory, hooks, deny rules, and path-scoped rules. This mission extends the existing infrastructure hardening baseline. It does not restate standing rules; it references them and adds enhancement-specific implementation work.

---

## 1. Mission Objective

This mission consolidates all non-blocking enhancement backlog items from the following QA runs into one execution pass:
- `/home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/SCORECARD.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/QA-FGH-VERIFY-001-COMPLETION.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/SCORECARD.md`

This is an enhancement hardening mission. It strengthens validator quality, policy consistency, CI guard depth, and QA/bookkeeping automation. It is not a product feature mission.

In scope:
- Validator unit harnesses and policy checks
- Schema-driven contract checks for performance/governance/manifest sections
- CI guard consolidation and anti-regression checks
- Pre-commit style safety checks for stale labels and contract drift
- QA scaffolding and completion-report automation utilities

Out of scope:
- Dashboard/backend feature behavior changes
- New contract surfaces beyond current 14
- Database schema changes or migrations
- Broad CI architecture redesign

---

## 2. Context

Verified current state:

1. Base remediation chains are complete and stable:
- Surfaces 10-14 registration: FULL PASS
- Frontend governance hardening: FULL PASS
- CI hardening: FULL PASS

2. Core infrastructure already exists and is healthy:
- `validate-frontend-governance.sh`, `validate-gatee-scan.sh`, `validate-rule-frontmatter.sh`, and `validate-stop-hook-contract.sh` exist under `/home/zaks/zakops-agent-api/tools/infra/`.
- `make validate-frontend-governance` exists and is wired into `validate-local`.
- `ci.yml` already uses script-based Gate E enforcement.

3. Enhancement backlog remains open across three clusters:
- Validator quality and testability (unit fixtures, strictness checks)
- CI anti-drift and anti-regression checks (no inline Gate E, four-way count guard, YAML lint)
- Automation and maintainability (QA scaffolding, AC coverage checks, reconciliation helper)

4. This mission should avoid redoing already-implemented enhancements and instead harden what remains unresolved.

---

## Crash Recovery Protocol <!-- Adopted from Improvement Area IA-2 -->

If resuming after interruption, run:

```bash
cd /home/zaks/zakops-agent-api && git log --oneline -5
cd /home/zaks/zakops-agent-api && make validate-local
cd /home/zaks/bookkeeping && find /home/zaks/bookkeeping/docs -maxdepth 1 -type f -name "MISSION-INFRA-ENHANCEMENTS-UNIFIED-001*" -o -name "INFRA-ENHANCEMENTS-UNIFIED-001-*"
```

If baseline validation fails during recovery, classify pre-existing versus mission-induced breakage before continuing.

---

## Continuation Protocol <!-- Adopted from Improvement Area IA-7 -->

At session end, update:
- `/home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md`

Checkpoint minimum content:
1. Completed phases
2. Remaining phases
3. Current validation state
4. Open blockers/decisions
5. Exact next command

---

## Context Checkpoint <!-- Adopted from Improvement Area IA-1 -->

If context becomes constrained mid-mission:
1. Write progress to `/home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md`.
2. Commit logically complete intermediate work.
3. Resume via Crash Recovery Protocol.

---

## 2b. Glossary

| Term | Definition |
|------|------------|
| Four-way count | Surface count reconciliation across contract catalog, CLAUDE.md, unified validator header, and manifest section |
| Gate E policy | Rule that raw `httpx` usage in `deal_tools.py` is forbidden and must be enforced with fail-closed scanner behavior |
| Strict S14 | Surface 14 performance-budget enforcement mode that fails on threshold violations in CI |
| Governance anchors | Required section-level or keyword-level contract markers in design rules |
| QA scaffold | Script/template utility that pre-creates evidence layout and boilerplate scorecard/completion structure |

---

## 2c. Enhancement Coverage Matrix

This mission must absorb all enhancement lines from the three QA outputs into one execution plan.

| Enhancement Cluster | Source Items | Target Phase |
|---------------------|--------------|--------------|
| Validator unit harnesses (Gate E + Surface 10-14) | QA-FGH ENH-1, QA-S10-14 ENH-2, QA-CIH ENH-1 | Phase 2 |
| Frontmatter/governance schema checks | QA-FGH ENH-2/3, QA-CIH ENH-5 | Phase 1 |
| Surface 14 strict CI enforcement | QA-S10-14 ENH-7 | Phase 4 |
| Four-way count CI enforcement | QA-S10-14 ENH-5, QA-CIH ENH-8 | Phase 4 |
| CLAUDE contract table guard | QA-S10-14 ENH-6 | Phase 5 |
| Stale surface-label guard | QA-S10-14 ENH-9, QA-FGH ENH-9, QA-CIH ENH-6 | Phase 5 |
| Workflow structure linting | QA-CIH ENH-2 | Phase 4 |
| Inline Gate E snippet prohibition | QA-CIH ENH-4 | Phase 4 |
| `validate-surfaces-new` meta target | QA-S10-14 ENH-3 | Phase 3 |
| `validate-hook-contract` formal target | QA-CIH ENH-3 | Phase 3 |
| Performance-budget schema lint | QA-S10-14 ENH-1 | Phase 1 |
| Manifest contract section schema lint | QA-S10-14 ENH-4 | Phase 1 |
| Policy drift enforcement polish | QA-FGH ENH-8 | Phase 5 |
| Governance runtime benchmark check | QA-CIH ENH-7 | Phase 5 |
| QA scaffold tooling | QA-S10-14 ENH-10, QA-FGH ENH-10, QA-CIH ENH-10 | Phase 6 |
| AC coverage + reconciliation automation | QA-S10-14 ENH-8, QA-CIH ENH-9 | Phase 6 |
| Governance changelog assist | QA-FGH ENH-7 | Phase 6 |
| Skill vs rule comparison report | QA-FGH ENH-6 | Phase 6 |

---

## 3. Architectural Constraints

- **No product behavior changes**
Meaning: Do not alter dashboard/backend feature logic to satisfy enhancement checks.
Why: This mission is infrastructure hardening only.

- **Fail-closed for critical scanners**
Meaning: Scanner failure states must produce explicit non-zero outcomes for enforcement gates.
Why: Silent pass breaks trust in policy checks.

- **No generated or migration file edits**
Meaning: Keep generated artifacts and migration files immutable.
Why: Contract pipelines own generated files; migration drift is high risk.

- **Keep 14-surface baseline intact**
Meaning: Existing validation semantics for surfaces 1-14 must remain valid.
Why: Prior mission chain depends on these guarantees.

- **Preserve Surface 9 behavior**
Meaning: Enhancements must not remove existing design-system checks.
Why: Surface 9 was recently hardened and verified.

- **CI and local parity where practical**
Meaning: The same validators should be runnable locally and in CI, except clearly documented CI-only checks.
Why: Prevent environment-specific drift.

- **No inline policy logic in workflow when script exists**
Meaning: Enforcement logic belongs in versioned scripts under `tools/infra`.
Why: Reduces duplication and stale snippets.

- **WSL hygiene remains mandatory**
Meaning: New shell scripts must use LF and sane ownership.
Why: Prevent delayed runtime failures.

---

## 3b. Anti-Pattern Examples

### WRONG: Inline CI policy duplication
```bash
if rg -n "httpx\\.(AsyncClient|get|post|put|patch|delete)" apps/agent-api/app/core/langgraph/tools/deal_tools.py; then
  exit 1
fi
```

### RIGHT: Script-based policy gate
```bash
bash tools/infra/validate-gatee-scan.sh
```

### WRONG: Documentation-only contract checks
```text
PERFORMANCE-BUDGET.md exists -> PASS
```

### RIGHT: Schema-backed validation
```text
Document exists + JSON schema validation + threshold key checks -> PASS
```

### WRONG: Count consistency checked manually once
```text
Engineer eyeballs four files and says "looks 14"
```

### RIGHT: Deterministic count guard
```text
Script computes 4 authoritative counts and fails CI on mismatch
```

### WRONG: QA evidence boilerplate handwritten each run
```text
Create folders and scorecard manually every mission
```

### RIGHT: QA scaffold utility
```text
Script generates evidence skeleton, scorecard template, and checkpoint boilerplate
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Enhancements duplicate already-completed work and introduce drift | MEDIUM | Waste + inconsistency | Phase 0 inventory explicitly marks existing vs missing before edits |
| 2 | New strict checks are over-brittle and cause false CI failures | HIGH | Merge blockage | Phase 1/4 decision trees require proportional checks and explicit CI-only scoping |
| 3 | Hook and Gate E checks diverge again between local and CI | MEDIUM | Policy split-brain | Phase 4 enforces script-only Gate E policy and parity checks |
| 4 | Automation scripts are added but not discoverable/used | MEDIUM | Process debt persists | Phase 6 and Phase 7 require runbook integration and make target exposure |
| 5 | 14-surface baseline regresses while adding enhancements | LOW | High confidence loss | Every phase gate includes no-regression validation |

---

## 4. Phases

## Phase 0 - Discovery and Baseline
**Complexity:** S  
**Estimated touch points:** 0 files modified

**Purpose:** Confirm real current state and capture enhancement baseline before changes.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Create baseline report**
  - Create `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-BASELINE.md`.
  - Capture outputs for:
    - `cd /home/zaks/zakops-agent-api && make validate-local`
    - `cd /home/zaks/zakops-agent-api && make validate-surface9`
    - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
  - **Checkpoint:** Baseline report includes timestamped outputs.

- P0-02: **Inventory enhancement status**
  - Record for each enhancement whether status is `already_done`, `partial`, or `missing`.
  - Evidence sources:
    - `/home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/SCORECARD.md`
    - `/home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/QA-FGH-VERIFY-001-COMPLETION.md`
    - `/home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/SCORECARD.md`
  - **Checkpoint:** Matrix is explicit and actionable.

### Decision Tree
- **IF** baseline validations fail -> stop and classify pre-existing breakage.
- **ELSE** continue.

### Rollback Plan
1. No rollback required (read-only phase).
2. Verify clean state with `git status --short` in touched repos.

### Gate P0
- Baseline report exists.
- Enhancement inventory exists with explicit done/missing mapping.

---

## Phase 1 - Schema Contracts and Structural Validators
**Complexity:** L  
**Estimated touch points:** 8-12 files created/modified

**Purpose:** Convert key doc/policy checks from text heuristics into schema-backed validators.

### Blast Radius
- **Services affected:** Infra validators, Surface 14 support files
- **Pages affected:** None
- **Downstream consumers:** CI gates, QA evidence checks, maintainers

### Tasks
- P1-01: **Add performance-budget schema + validator**
  - Create schema file:
    - `/home/zaks/zakops-agent-api/tools/infra/schemas/performance-budget.schema.json`
  - Create validator script:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-performance-budget-schema.sh`
  - Validate `/home/zaks/bookkeeping/docs/PERFORMANCE-BUDGET.md` shape and required fields.
  - **Checkpoint:** Validator exits non-zero for malformed fixture.

- P1-02: **Add governance-anchor contract schema + validator**
  - Create schema file:
    - `/home/zaks/zakops-agent-api/tools/infra/schemas/governance-anchor-contract.schema.json`
  - Create validator script:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-governance-anchor-schema.sh`
  - Verify required anchors in:
    - `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
    - `/home/zaks/zakops-agent-api/.claude/rules/accessibility.md`
    - `/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md`
  - **Checkpoint:** Validator output is structured and deterministic.

- P1-03: **Add manifest contract-surfaces schema validator**
  - Create schema file:
    - `/home/zaks/zakops-agent-api/tools/infra/schemas/manifest-contract-surfaces.schema.json`
  - Create validator script:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-manifest-contract-section.sh`
  - Enforce required fields and expected surface entries.
  - **Checkpoint:** Script can detect malformed or incomplete manifest section.

### Decision Tree
- **IF** schema strictness causes high false positives -> narrow to required-core fields and log advisory extras.
- **ELSE** enforce strictly.

### Rollback Plan
1. Revert new schema files and validators.
2. Re-run baseline validation.

### Gate P1
- All 3 schema validators exist and execute.
- Validators demonstrate fail behavior on intentionally broken fixtures.

---

## Phase 2 - Validator Unit Harnesses and Hook Self-Tests
**Complexity:** L  
**Estimated touch points:** 10-16 files created/modified

**Purpose:** Add reproducible fixture-based tests for critical validators and hook behavior.

### Blast Radius
- **Services affected:** Validator reliability and regression confidence
- **Pages affected:** None
- **Downstream consumers:** CI and QA maintainers

### Tasks
- P2-01: **Add Gate E fixture test harness**
  - Create fixture set under:
    - `/home/zaks/zakops-agent-api/tools/infra/tests/fixtures/gatee/`
  - Create runner:
    - `/home/zaks/zakops-agent-api/tools/infra/tests/test-validate-gatee-scan.sh`
  - Cover clean, violation, and scanner-error scenarios.
  - **Checkpoint:** Harness returns deterministic pass/fail per case.

- P2-02: **Add Surface 10-14 validator fixture harness**
  - Create fixture sets under:
    - `/home/zaks/zakops-agent-api/tools/infra/tests/fixtures/surfaces10-14/`
  - Create runner:
    - `/home/zaks/zakops-agent-api/tools/infra/tests/test-validate-surfaces10-14.sh`
  - Cover minimal valid and intentional invalid cases.
  - **Checkpoint:** Harness exercises each validator at least one pass and one fail case.

- P2-03: **Add stop-hook self-test mode**
  - Implement self-test wrapper script:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-selftest.sh`
  - Validate detection branches (`git-rev-parse`, `known-path-fallback`, `env-override`) and fail-closed behavior.
  - **Checkpoint:** Self-test generates explicit branch outcomes.

### Decision Tree
- **IF** full hook execution is environment-sensitive -> use controlled wrapper with mocked paths and explicit expected outcomes.
- **ELSE** run direct hook-path tests.

### Rollback Plan
1. Revert test harness files.
2. Keep production validators unchanged.
3. Re-run `make validate-local`.

### Gate P2
- Gate E harness passes.
- Surface 10-14 harness passes.
- Hook self-test script passes.

---

## Phase 3 - Make Target Consolidation
**Complexity:** M  
**Estimated touch points:** 1-2 files modified

**Purpose:** Expose new validators and harnesses through clear make entrypoints.

### Blast Radius
- **Services affected:** Developer and CI invocation surface
- **Pages affected:** None
- **Downstream consumers:** CI workflow, QA scripts, operators

### Tasks
- P3-01: **Add `validate-surfaces-new` target**
  - Modify `/home/zaks/zakops-agent-api/Makefile`.
  - Aggregate Surface 10-14 validations and related schema checks.
  - **Checkpoint:** target runs without side effects and exits non-zero on failures.

- P3-02: **Add `validate-hook-contract` target**
  - Modify `/home/zaks/zakops-agent-api/Makefile`.
  - Wire to `/home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-contract.sh` and/or self-test wrapper.
  - **Checkpoint:** target is callable and documented.

- P3-03: **Add `validate-enhancements` target**
  - Aggregate new harnesses and CI-policy scripts for local dry-runs.
  - **Checkpoint:** single command runs core enhancement guards.

### Decision Tree
- **IF** runtime for `validate-local` becomes excessive -> keep heavy harness in `validate-enhancements` and enforce in CI only.
- **ELSE** include in `validate-local`.

### Rollback Plan
1. Revert Makefile edits.
2. Re-run baseline validations.

### Gate P3
- New make targets exist and execute.
- Existing targets remain stable.

---

## Phase 4 - CI Policy Hardening
**Complexity:** L  
**Estimated touch points:** 3-6 files modified/created

**Purpose:** Enforce enhancement checks at PR level with deterministic CI gates.

### Blast Radius
- **Services affected:** GitHub Actions gating
- **Pages affected:** None
- **Downstream consumers:** PR merge safety

### Tasks
- P4-01: **Add workflow-structure lint step**
  - Update `/home/zaks/zakops-agent-api/.github/workflows/ci.yml`.
  - Add YAML/workflow linting gate using deterministic toolchain.
  - **Checkpoint:** lint gate runs in CI context and is reproducible.

- P4-02: **Add inline Gate E prohibition guard**
  - Create script:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-ci-gatee-policy.sh`
  - Enforce that workflow uses script-based Gate E and does not reintroduce inline snippets.
  - **Checkpoint:** script fails on inline pattern reintroduction.

- P4-03: **Add four-way count CI guard**
  - Create script:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-surface-count-consistency.sh`
  - Fail CI if counts diverge across contract-surfaces, CLAUDE.md, unified validator header, manifest section.
  - **Checkpoint:** script produces explicit count outputs.

- P4-04: **Enforce strict Surface 14 in CI**
  - Update CI to run:
    - `STRICT=1 bash tools/infra/validate-surface14.sh`
  - Keep local default advisory mode unchanged unless explicitly requested.
  - **Checkpoint:** strict-mode step is wired and documented.

### Decision Tree
- **IF** strict mode depends on build artifacts unavailable in current job -> add deterministic artifact prep step.
- **ELSE** run strict check directly.

### Rollback Plan
1. Revert CI/workflow changes.
2. Re-run local validation and workflow syntax checks.

### Gate P4
- CI workflow includes lint, no-inline Gate E, four-way count, and strict S14 checks.
- Existing plan-gates remain coherent.

---

## Phase 5 - Pre-Commit Style Guards and Drift Protections
**Complexity:** M  
**Estimated touch points:** 5-8 files modified/created

**Purpose:** Catch common drift patterns before CI where possible.

### Blast Radius
- **Services affected:** Local developer workflow, policy drift checks
- **Pages affected:** None
- **Downstream consumers:** All contributors

### Tasks
- P5-01: **Add stale surface-label scanner**
  - Create script:
    - `/home/zaks/zakops-agent-api/tools/infra/scan-stale-surface-labels.sh`
  - Scan hooks, workflow, and key docs for stale count labels (`7`, `9`, etc. where `14` is required).
  - **Checkpoint:** script reports exact offending file+line.

- P5-02: **Add CLAUDE surface-table guard**
  - Create script:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-claude-surface-table.sh`
  - Ensure CLAUDE contract surface table includes expected S10-S14 entries and total.
  - **Checkpoint:** guard fails on missing rows/total mismatch.

- P5-03: **Formalize pre-commit hook install path**
  - Create installable hook script:
    - `/home/zaks/zakops-agent-api/tools/hooks/pre-commit`
  - Hook invokes stale-label scanner and core drift guards.
  - **Checkpoint:** script can be installed and run manually (`bash tools/hooks/pre-commit`).

- P5-04: **Strengthen policy drift check integration**
  - Extend `/home/zaks/zakops-agent-api/tools/infra/check-governance-drift.sh` to include new guards.
  - **Checkpoint:** drift output clearly separates PASS, DRIFT, and INFO.

### Decision Tree
- **IF** repo chooses not to auto-install pre-commit hook -> keep script as manual/pre-CI command and document clearly.
- **ELSE** wire installation helper and ensure idempotency.

### Rollback Plan
1. Revert new guard scripts and hook script.
2. Keep CI checks as primary enforcement.
3. Re-run `make validate-local`.

### Gate P5
- New drift/label/table guards run and report correctly.
- Pre-commit style script is callable.

---

## Phase 6 - QA and Bookkeeping Automation Utilities
**Complexity:** L  
**Estimated touch points:** 8-14 files created/modified

**Purpose:** Reduce manual QA/report overhead and standardize mission closure artifacts.

### Blast Radius
- **Services affected:** Bookkeeping/QA workflow
- **Pages affected:** None
- **Downstream consumers:** QA executors and mission authors

### Tasks
- P6-01: **Add QA scaffold generator**
  - Create:
    - `/home/zaks/bookkeeping/scripts/qa-scaffold.sh`
  - Generate evidence folder skeleton, scorecard skeleton, and completion skeleton for a mission ID.
  - **Checkpoint:** script successfully scaffolds a dry-run mission directory.

- P6-02: **Add AC coverage checker**
  - Create:
    - `/home/zaks/bookkeeping/scripts/check-ac-coverage.py`
  - Compare source mission AC list with completion report AC claims.
  - **Checkpoint:** script outputs missing/extra AC references.

- P6-03: **Add reconciliation table generator**
  - Create:
    - `/home/zaks/bookkeeping/scripts/generate-reconciliation-table.py`
  - Produce before/after surface-count tables from authoritative files.
  - **Checkpoint:** tool outputs markdown-ready table.

- P6-04: **Add governance changelog helper and skill-vs-rule report**
  - Create:
    - `/home/zaks/bookkeeping/scripts/governance-changelog-helper.sh`
    - `/home/zaks/bookkeeping/scripts/compare-frontend-skill-vs-rule.py`
  - **Checkpoint:** scripts run with clear output and no destructive side effects.

- P6-05: **Document automation utilities**
  - Create runbook:
    - `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-AUTOMATION-RUNBOOK.md`
  - **Checkpoint:** each utility has command examples and expected outputs.

### Decision Tree
- **IF** script depends on unavailable runtime library -> implement equivalent shell/python standard-library fallback.
- **ELSE** keep dependency minimal and deterministic.

### Rollback Plan
1. Revert added automation scripts and runbook.
2. Preserve core infra checks unchanged.

### Gate P6
- QA/bookkeeping utilities execute successfully in dry-run mode.
- Runbook exists and references all utilities.

---

## Phase 7 - Final Verification and Bookkeeping
**Complexity:** M  
**Estimated touch points:** 3-6 files modified/created

**Purpose:** Validate consolidated enhancement mission outcomes and close cleanly.

### Blast Radius
- **Services affected:** Validation workflow and docs
- **Pages affected:** None
- **Downstream consumers:** QA-IEU-VERIFY-001

### Tasks
- P7-01: **Run final validation suite**
  - Required commands:
    - `cd /home/zaks/zakops-agent-api && make validate-local`
    - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
    - `cd /home/zaks/zakops-agent-api && make validate-frontend-governance`
    - `cd /home/zaks/zakops-agent-api && make validate-surfaces-new`
    - `cd /home/zaks/zakops-agent-api && make validate-hook-contract`
    - `cd /home/zaks/zakops-agent-api && bash tools/infra/check-governance-drift.sh`
  - **Checkpoint:** all required commands pass.

- P7-02: **Create completion report**
  - Create:
    - `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md`
  - Include:
    - Phase outcomes
    - AC-by-AC evidence mapping
    - Enhancement matrix status (`implemented`, `deferred`, `not_applicable`)
  - **Checkpoint:** completion report is evidence-linked.

- P7-03: **Update bookkeeping artifacts**
  - Update:
    - `/home/zaks/bookkeeping/CHANGES.md`
    - `/home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md`
  - **Checkpoint:** successor QA handoff clearly stated.

### Decision Tree
- **IF** any final gate fails -> remediate, re-run failed gate, then re-run `make validate-local`.
- **ELSE** finalize and hand off to QA.

### Rollback Plan
1. Revert latest phase changes.
2. Re-run baseline validations.
3. Rebuild completion artifacts.

### Gate P7
- Final suite passes.
- Completion, CHANGES, and checkpoint artifacts are complete.

---

## 4b. Dependency Graph

```text
Phase 0 (Discovery/Baseline)
    |
    v
Phase 1 (Schemas/Structural Validators)
    |
    v
Phase 2 (Unit Harnesses + Hook Self-Tests)
    |
    v
Phase 3 (Make Target Consolidation)
    |
    v
Phase 4 (CI Policy Hardening)
    |
    +------------------+
    |                  |
    v                  v
Phase 5 (Drift Guards) Phase 6 (QA/Bookkeeping Automation)
    |                  |
    +---------+--------+
              |
              v
Phase 7 (Final Verification + Bookkeeping)
```

Phases 5 and 6 may run in parallel after Phase 4 passes.

---

## 5. Acceptance Criteria

### AC-1: Baseline and Enhancement Inventory Captured
`INFRA-ENHANCEMENTS-UNIFIED-001-BASELINE.md` exists and includes a done/missing enhancement matrix.

### AC-2: Performance Budget Schema Validation Implemented
Schema + validator exist and enforce required contract fields for `PERFORMANCE-BUDGET.md`.

### AC-3: Governance Anchor Schema Validation Implemented
Schema-backed governance anchor validator exists and is deterministic.

### AC-4: Manifest Contract Section Schema Validation Implemented
Manifest contract-surface section is schema-validated with explicit fail states.

### AC-5: Gate E Fixture Harness Implemented
Fixture-based tests for `validate-gatee-scan.sh` cover clean/violation/scanner-error cases.

### AC-6: Surface 10-14 Fixture Harness Implemented
Fixture tests exist for validators `validate-surface10.sh` through `validate-surface14.sh`.

### AC-7: Hook Self-Test Mode Implemented
A deterministic stop-hook self-test utility verifies detection-path and fail-closed expectations.

### AC-8: Make Target Consolidation Complete
`validate-surfaces-new`, `validate-hook-contract`, and enhancement aggregate targets are available.

### AC-9: CI Policy Hardening Complete
CI includes workflow lint, no-inline Gate E policy check, four-way count check, and strict S14 enforcement.

### AC-10: Stale Label and CLAUDE Table Guards Implemented
Pre-commit style scanners catch stale count labels and CLAUDE surface table drift.

### AC-11: Policy Drift and Benchmarking Strengthened
Governance drift checks include new guards and runtime benchmark output.

### AC-12: QA Scaffold Utility Implemented
Reusable QA scaffold script generates evidence/scorecard/completion skeletons.

### AC-13: AC Coverage and Reconciliation Automation Implemented
Scripts generate AC coverage reports and reconciliation tables automatically.

### AC-14: Governance Changelog and Skill-vs-Rule Helpers Implemented
Automation helpers exist and are documented for repeatable usage.

### AC-15: No Regressions
`make validate-local`, `make validate-contract-surfaces`, and `make validate-frontend-governance` pass.

### AC-16: Bookkeeping Complete
Completion report, CHANGES update, and mission checkpoint are present with evidence links.

---

## 6. Guardrails

1. Do not implement product features in this mission.
2. Do not add new contract surfaces beyond 14.
3. Do not weaken existing Gate E or stop-hook semantics.
4. Do not edit generated files or migration files.
5. Keep enforcement logic in scripts, not duplicated inline in workflow YAML.
6. Keep CI-only checks explicitly labeled as CI-only where needed.
7. Preserve Surface 9 and existing 14-surface validation semantics.
8. Keep all paths absolute in reports and mission artifacts.
9. Capture evidence for every phase gate and AC.
10. If uncertainty remains, classify as `INFO` and defer rather than forcing a brittle implementation.

---

## 7. Executor Self-Check Prompts

### After Phase 0
- [ ] Did I explicitly mark which enhancements are already done versus missing?
- [ ] Did baseline validation pass before any edits?
- [ ] Did I capture current CI/workflow enforcement markers?

### After Phases 1-2
- [ ] Are validators schema-backed where intended, not keyword-grep only?
- [ ] Do new harnesses include both pass and fail fixtures?
- [ ] Did hook self-test verify all detection branches?

### After Phases 3-4
- [ ] Are new make targets actually wired and runnable?
- [ ] Is CI using scripts instead of inline policy duplication?
- [ ] Is strict S14 enforced in CI without breaking local advisory workflow?

### Before Mission Complete
- [ ] Did final validation commands run successfully right now?
- [ ] Did I update completion report, checkpoint, and CHANGES with evidence paths?
- [ ] Is successor `QA-IEU-VERIFY-001` clearly unblocked?

---

## 8. File Paths Reference

### Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/Makefile` | 3,7 | Add enhancement targets and validation wiring |
| `/home/zaks/zakops-agent-api/.github/workflows/ci.yml` | 4 | Add lint/policy/count/strict S14 checks |
| `/home/zaks/zakops-agent-api/tools/infra/check-governance-drift.sh` | 5 | Expand drift coverage and benchmark output |
| `/home/zaks/bookkeeping/CHANGES.md` | 7 | Record enhancement mission changes |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-BASELINE.md` | 0 | Baseline evidence + enhancement inventory |
| `/home/zaks/zakops-agent-api/tools/infra/schemas/performance-budget.schema.json` | 1 | Surface 14 contract schema |
| `/home/zaks/zakops-agent-api/tools/infra/schemas/governance-anchor-contract.schema.json` | 1 | Governance anchor schema |
| `/home/zaks/zakops-agent-api/tools/infra/schemas/manifest-contract-surfaces.schema.json` | 1 | Manifest contract section schema |
| `/home/zaks/zakops-agent-api/tools/infra/validate-performance-budget-schema.sh` | 1 | Schema validator for PERFORMANCE-BUDGET |
| `/home/zaks/zakops-agent-api/tools/infra/validate-governance-anchor-schema.sh` | 1 | Schema validator for governance anchors |
| `/home/zaks/zakops-agent-api/tools/infra/validate-manifest-contract-section.sh` | 1 | Manifest section validator |
| `/home/zaks/zakops-agent-api/tools/infra/tests/test-validate-gatee-scan.sh` | 2 | Gate E fixture test harness |
| `/home/zaks/zakops-agent-api/tools/infra/tests/test-validate-surfaces10-14.sh` | 2 | Surface 10-14 fixture harness |
| `/home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-selftest.sh` | 2 | Stop-hook self-test utility |
| `/home/zaks/zakops-agent-api/tools/infra/validate-ci-gatee-policy.sh` | 4 | Disallow inline Gate E policy snippets |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface-count-consistency.sh` | 4 | Four-way count reconciliation guard |
| `/home/zaks/zakops-agent-api/tools/infra/scan-stale-surface-labels.sh` | 5 | Stale label pre-commit guard |
| `/home/zaks/zakops-agent-api/tools/infra/validate-claude-surface-table.sh` | 5 | CLAUDE table drift guard |
| `/home/zaks/zakops-agent-api/tools/hooks/pre-commit` | 5 | Installable pre-commit style guard runner |
| `/home/zaks/bookkeeping/scripts/qa-scaffold.sh` | 6 | QA scaffold generator |
| `/home/zaks/bookkeeping/scripts/check-ac-coverage.py` | 6 | Mission AC coverage checker |
| `/home/zaks/bookkeeping/scripts/generate-reconciliation-table.py` | 6 | Reconciliation table generator |
| `/home/zaks/bookkeeping/scripts/governance-changelog-helper.sh` | 6 | Changelog helper for governance changes |
| `/home/zaks/bookkeeping/scripts/compare-frontend-skill-vs-rule.py` | 6 | Skill-vs-rule comparison report |
| `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-AUTOMATION-RUNBOOK.md` | 6 | Utility usage runbook |
| `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md` | 7 | Completion report with AC mapping |
| `/home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md` | all | Continuation checkpoint |

### Files to Read (Do Not Modify Unless Explicitly Tasked)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/SCORECARD.md` | Source enhancement backlog for surfaces 10-14 |
| `/home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/QA-FGH-VERIFY-001-COMPLETION.md` | Source enhancement backlog for governance hardening |
| `/home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/SCORECARD.md` | Source enhancement backlog for CI hardening |
| `/home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md` | Prior mission patterns and constraints |
| `/home/zaks/bookkeeping/docs/QA-CIH-VERIFY-001.md` | Expected QA verification structure for successor mission |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh` | Existing validator baseline |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh` | Existing validator baseline |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh` | Existing validator baseline |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh` | Existing validator baseline |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh` | Existing validator baseline |
| `/home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh` | Existing Gate E enforcement baseline |
| `/home/zaks/.claude/hooks/stop.sh` | Existing hook detection and gate behavior |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Prompt generation standard |

---

## 9. Stop Condition

Stop when AC-1 through AC-16 are satisfied, all enhancement clusters in the coverage matrix are either implemented or explicitly classified with rationale, and no regression appears in Surface 9 or the 14-surface baseline.

Do not proceed to unrelated platform redesigns or feature initiatives in this mission. Hand off only to `QA-IEU-VERIFY-001` for independent verification.

---

*End of Mission Prompt - INFRA-ENHANCEMENTS-UNIFIED-001*

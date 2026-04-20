# MISSION: QA-IEU-VERIFY-001
## Independent QA Verification and Remediation - INFRA-ENHANCEMENTS-UNIFIED-001
## Date: 2026-02-10
## Classification: QA Verification and Remediation
## Prerequisite: /home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md execution complete
## Successor: Post-enhancement platform missions only after FULL PASS

---

## Preamble: Builder Operating Context

The builder already loads project guardrails (`CLAUDE.md`, canonical memory, hooks, deny rules, path-scoped rules). This QA mission does not restate those systems. It independently verifies that `/home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md` was executed correctly and did not regress Surface 9 and 14-surface infrastructure integrity.

---

## 1. Mission Objective

This mission performs independent QA verification and in-scope remediation for `INFRA-ENHANCEMENTS-UNIFIED-001`.

Source mission under test:
- `/home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md`
- Expected structure: 8 phases (Phase 0 through Phase 7), 16 acceptance criteria (AC-1 through AC-16)
- Critical expectations:
  - Schema validators implemented for performance budget, governance anchors, and manifest contract section
  - Unit harnesses implemented for Gate E and Surfaces 10-14 validators
  - Hook self-test utility implemented and deterministic
  - Make target consolidation completed (`validate-surfaces-new`, `validate-hook-contract`, `validate-enhancements`)
  - CI hardening implemented (workflow lint, no-inline Gate E guard, four-way count guard, strict S14)
  - Drift guards and pre-commit style scripts implemented
  - QA/bookkeeping automation utilities implemented and documented
  - No regression in Surface 9 and 14-surface baseline

Expected execution artifacts from source mission:
- `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-BASELINE.md`
- `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md`
- `/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-AUTOMATION-RUNBOOK.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `INFRA-ENHANCEMENTS-UNIFIED-001`

QA scope:
- Verify all 16 ACs with concrete evidence
- Verify enhancement coverage matrix closure
- Verify no regressions in enforcement/runtime validation
- Apply minimal remediation only when required to satisfy source mission ACs

Out of scope:
- Product feature implementation
- Contract surface expansion beyond 14
- New platform architecture beyond enhancement mission scope

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md
  rg -n '^## Phase ' /home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md')
t=p.read_text()
phase_count=len(re.findall(r'^## Phase ', t, flags=re.M))
ac_count=len(re.findall(r'^### AC-', t, flags=re.M))
print('phase_count=', phase_count)
print('ac_count=', ac_count)
raise SystemExit(0 if (phase_count==8 and ac_count==16) else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** mission exists and has 8 phases + 16 ACs.

### PF-2: Execution Artifact Presence

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACTS ==="
  ls -l /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-BASELINE.md
  ls -l /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md
  ls -l /home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md
  ls -l /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-AUTOMATION-RUNBOOK.md
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'INFRA-ENHANCEMENTS-UNIFIED-001' /home/zaks/bookkeeping/CHANGES.md
  else
    echo "INFO: /home/zaks/bookkeeping/CHANGES.md unreadable in this runtime context"
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/PF-2-execution-artifacts.txt
```

**PASS if:** required artifacts exist and CHANGES evidence is captured either directly or via explicit runtime-context note.

**If FAIL:** classify as `NOT_EXECUTED` and stop gate progression.

### PF-3: Baseline Validation Health

```bash
{
  echo "=== PF-3 BASELINE VALIDATION HEALTH ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-surface9
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/PF-3-baseline-validation-health.txt
```

**PASS if:** all commands exit 0.

### PF-4: Runtime Context + Core Enhancement Files Snapshot

```bash
{
  echo "=== PF-4 RUNTIME CONTEXT + CORE ENH FILES ==="
  cd /home/zaks/zakops-agent-api && git rev-parse --abbrev-ref HEAD
  cd /home/zaks/zakops-agent-api && git status --short
  ls -l /home/zaks/zakops-agent-api/tools/infra/schemas/
  ls -l /home/zaks/zakops-agent-api/tools/infra/tests/
  ls -l /home/zaks/zakops-agent-api/tools/hooks/pre-commit
  ls -l /home/zaks/bookkeeping/scripts/qa-scaffold.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/PF-4-runtime-enhancement-snapshot.txt
```

**PASS if:** runtime context is captured and enhancement artifact roots are present.

### PF-5: Four-Way Count Baseline Snapshot

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/PF-5-four-way-count-baseline.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text() if (repo/'INFRASTRUCTURE_MANIFEST.md').exists() else ''
cs_count=len(re.findall(r'^### Surface \d+:', cs, flags=re.M))
cla_count=int(re.search(r'Contract Surfaces \((\d+) Total\)', cla).group(1))
vs_count=int(re.search(r'Validates all (\d+) contract surfaces', vs).group(1))
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', man)
man_count=len([ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]) if sec else -1
print('contract-surfaces.md=', cs_count)
print('CLAUDE.md=', cla_count)
print('validator_header=', vs_count)
print('manifest_section=', man_count)
ok=(cs_count==cla_count==vs_count==14 and man_count in (14,-1))
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** authoritative counts are stable at 14.

---

## 3. Verification Families (VF)

## Verification Family 01 - Prerequisite, Baseline, and Coverage Matrix Integrity (AC-1)

### VF-01.1: Completion Report Presence and Structure

```bash
{
  echo "=== VF-01.1 COMPLETION STRUCTURE ==="
  wc -l /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md
  rg -n 'Phase 0|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5|Phase 6|Phase 7|AC-1|AC-16|PASS|FAIL|INFO' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-01.1-completion-structure.txt
```

**PASS if:** completion report exists and includes phase outcomes + AC mapping references.

### VF-01.2: Baseline Report Contains Enhancement Inventory

```bash
{
  echo "=== VF-01.2 BASELINE INVENTORY ==="
  ls -l /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-BASELINE.md
  rg -n 'already_done|partial|missing|Enhancement|QA-S10-14|QA-FGH|QA-CIH' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-BASELINE.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-01.2-baseline-inventory.txt
```

**PASS if:** baseline includes explicit enhancement status inventory.

### VF-01.3: Coverage Matrix Closure in Completion Report

```bash
{
  echo "=== VF-01.3 COVERAGE MATRIX CLOSURE ==="
  rg -n 'Enhancement Coverage Matrix|implemented|deferred|not_applicable|Cluster|Phase' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-01.3-coverage-matrix-closure.txt
```

**PASS if:** completion report records final status for enhancement clusters.

### VF-01.4: Checkpoint and CHANGES Mission Trace

```bash
{
  echo "=== VF-01.4 CHECKPOINT + CHANGES TRACE ==="
  ls -l /home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md
  tail -n 120 /home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'INFRA-ENHANCEMENTS-UNIFIED-001' /home/zaks/bookkeeping/CHANGES.md
  else
    echo "INFO: CHANGES unreadable in this runtime context; relying on completion/checkpoint evidence"
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-01.4-checkpoint-changes-trace.txt
```

**PASS if:** checkpoint exists and mission trace is verifiable through available closure artifacts.

**Gate VF-01:** All 4 checks PASS.

---

## Verification Family 02 - Schema Contracts and Structural Validators (AC-2, AC-3, AC-4)

### VF-02.1: Schema + Validator File Presence

```bash
{
  echo "=== VF-02.1 SCHEMA + VALIDATOR PRESENCE ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/schemas/performance-budget.schema.json
  ls -l /home/zaks/zakops-agent-api/tools/infra/schemas/governance-anchor-contract.schema.json
  ls -l /home/zaks/zakops-agent-api/tools/infra/schemas/manifest-contract-surfaces.schema.json
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-performance-budget-schema.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-governance-anchor-schema.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-manifest-contract-section.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-02.1-schema-validator-presence.txt
```

**PASS if:** all 6 files exist and validator scripts are executable.

### VF-02.2: Performance Budget Schema Validator Semantics

```bash
{
  echo "=== VF-02.2 PERFORMANCE SCHEMA VALIDATOR SEMANTICS ==="
  sed -n '1,240p' /home/zaks/zakops-agent-api/tools/infra/validate-performance-budget-schema.sh
  rg -n 'PERFORMANCE-BUDGET\.md|schema|strict|threshold|budget|exit 1|FAIL|PASS' /home/zaks/zakops-agent-api/tools/infra/validate-performance-budget-schema.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-02.2-performance-schema-semantics.txt
```

**PASS if:** script references schema-backed checks for required budget fields.

### VF-02.3: Governance Anchor Schema Validator Semantics

```bash
{
  echo "=== VF-02.3 GOVERNANCE SCHEMA VALIDATOR SEMANTICS ==="
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/infra/validate-governance-anchor-schema.sh
  rg -n 'design-system\.md|accessibility\.md|component-patterns\.md|schema|anchor|exit 1|FAIL|PASS' /home/zaks/zakops-agent-api/tools/infra/validate-governance-anchor-schema.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-02.3-governance-schema-semantics.txt
```

**PASS if:** schema-backed anchor checks for all three governance rules are present.

### VF-02.4: Manifest Contract Section Validator Semantics

```bash
{
  echo "=== VF-02.4 MANIFEST SCHEMA VALIDATOR SEMANTICS ==="
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/infra/validate-manifest-contract-section.sh
  rg -n 'INFRASTRUCTURE_MANIFEST\.md|Contract Surfaces|schema|14|exit 1|FAIL|PASS' /home/zaks/zakops-agent-api/tools/infra/validate-manifest-contract-section.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-02.4-manifest-schema-semantics.txt
```

**PASS if:** script enforces manifest contract-surface section structure and count checks.

### VF-02.5: Runtime Schema Validator Execution

```bash
{
  echo "=== VF-02.5 RUNTIME SCHEMA VALIDATOR EXECUTION ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-performance-budget-schema.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-governance-anchor-schema.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-manifest-contract-section.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-02.5-runtime-schema-validators.txt
```

**PASS if:** all three validators exit 0.

**Gate VF-02:** All 5 checks PASS.

---

## Verification Family 03 - Harnesses and Hook Self-Test (AC-5, AC-6, AC-7)

### VF-03.1: Fixture Directories and Harness Presence

```bash
{
  echo "=== VF-03.1 FIXTURE + HARNESS PRESENCE ==="
  ls -la /home/zaks/zakops-agent-api/tools/infra/tests/fixtures/gatee/
  ls -la /home/zaks/zakops-agent-api/tools/infra/tests/fixtures/surfaces10-14/
  ls -l /home/zaks/zakops-agent-api/tools/infra/tests/test-validate-gatee-scan.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/tests/test-validate-surfaces10-14.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-selftest.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-03.1-harness-presence.txt
```

**PASS if:** fixture directories and harness/selftest scripts exist and are executable.

### VF-03.2: Gate E Harness Coverage Markers

```bash
{
  echo "=== VF-03.2 GATE E HARNESS COVERAGE ==="
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/infra/tests/test-validate-gatee-scan.sh
  rg -n 'clean|violation|scanner|error|PASS|FAIL|case' /home/zaks/zakops-agent-api/tools/infra/tests/test-validate-gatee-scan.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-03.2-gatee-harness-coverage.txt
```

**PASS if:** harness explicitly covers clean, violation, and scanner-error style cases.

### VF-03.3: Surface 10-14 Harness Coverage Markers

```bash
{
  echo "=== VF-03.3 SURFACE10-14 HARNESS COVERAGE ==="
  sed -n '1,320p' /home/zaks/zakops-agent-api/tools/infra/tests/test-validate-surfaces10-14.sh
  rg -n 'validate-surface10|validate-surface11|validate-surface12|validate-surface13|validate-surface14|pass|fail|fixture' /home/zaks/zakops-agent-api/tools/infra/tests/test-validate-surfaces10-14.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-03.3-surface-harness-coverage.txt
```

**PASS if:** harness references validators 10-14 and pass/fail fixture logic.

### VF-03.4: Hook Self-Test Coverage Markers

```bash
{
  echo "=== VF-03.4 HOOK SELFTEST COVERAGE ==="
  sed -n '1,320p' /home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-selftest.sh
  rg -n 'git-rev-parse|known-path-fallback|env-override|fail closed|Gate E|PASS|FAIL' /home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-selftest.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-03.4-hook-selftest-coverage.txt
```

**PASS if:** self-test covers all required detection branches and fail-closed behavior markers.

### VF-03.5: Runtime Harness and Self-Test Execution

```bash
{
  echo "=== VF-03.5 RUNTIME HARNESS + SELFTEST ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/tests/test-validate-gatee-scan.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/tests/test-validate-surfaces10-14.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-stop-hook-selftest.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-03.5-runtime-harness-selftest.txt
```

**PASS if:** all three scripts exit 0.

**Gate VF-03:** All 5 checks PASS.

---

## Verification Family 04 - Make Target Consolidation (AC-8)

### VF-04.1: New Make Targets Presence

```bash
{
  echo "=== VF-04.1 MAKE TARGET PRESENCE ==="
  rg -n '^validate-surfaces-new:|^validate-hook-contract:|^validate-enhancements:' /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-04.1-make-target-presence.txt
```

**PASS if:** all three targets exist.

### VF-04.2: Make Target Wiring to Expected Scripts

```bash
{
  echo "=== VF-04.2 MAKE TARGET WIRING ==="
  rg -n 'validate-surface10\.sh|validate-surface11\.sh|validate-surface12\.sh|validate-surface13\.sh|validate-surface14\.sh|validate-stop-hook-contract\.sh|validate-stop-hook-selftest\.sh|validate-ci-gatee-policy\.sh|validate-surface-count-consistency\.sh' /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-04.2-make-target-wiring.txt
```

**PASS if:** wiring references required scripts or documented alternatives.

### VF-04.3: Make Dry-Run Graph for New Targets

```bash
{
  echo "=== VF-04.3 MAKE DRY-RUN GRAPH ==="
  cd /home/zaks/zakops-agent-api && make -n validate-surfaces-new
  cd /home/zaks/zakops-agent-api && make -n validate-hook-contract
  cd /home/zaks/zakops-agent-api && make -n validate-enhancements
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-04.3-make-dryrun-graph.txt
```

**PASS if:** dry-run commands resolve successfully.

### VF-04.4: Runtime New Target Execution

```bash
{
  echo "=== VF-04.4 RUNTIME NEW TARGET EXECUTION ==="
  cd /home/zaks/zakops-agent-api && make validate-surfaces-new
  cd /home/zaks/zakops-agent-api && make validate-hook-contract
  cd /home/zaks/zakops-agent-api && make validate-enhancements
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-04.4-runtime-new-targets.txt
```

**PASS if:** all three targets exit 0.

### VF-04.5: Local Validation Stability After Consolidation

```bash
{
  echo "=== VF-04.5 LOCAL VALIDATION STABILITY ==="
  cd /home/zaks/zakops-agent-api && make validate-local
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-04.5-local-validation-stability.txt
```

**PASS if:** local validation remains healthy.

**Gate VF-04:** All 5 checks PASS.

---

## Verification Family 05 - CI Policy Hardening (AC-9)

### VF-05.1: Workflow Lint Step Present

```bash
{
  echo "=== VF-05.1 WORKFLOW LINT STEP ==="
  rg -n 'actionlint|yamllint|workflow lint|Lint workflow|lint.*ci\.yml' /home/zaks/zakops-agent-api/.github/workflows/ci.yml
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-05.1-workflow-lint-step.txt
```

**PASS if:** workflow has an explicit linting step for workflow structure.

### VF-05.2: No-Inline Gate E Policy Guard Present and Wired

```bash
{
  echo "=== VF-05.2 NO-INLINE GATE E POLICY ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-ci-gatee-policy.sh
  rg -n 'validate-ci-gatee-policy\.sh' /home/zaks/zakops-agent-api/.github/workflows/ci.yml /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-05.2-no-inline-gatee-policy.txt
```

**PASS if:** policy script exists and is wired into CI and/or enhancement target path.

### VF-05.3: Four-Way Surface Count CI Guard Present and Wired

```bash
{
  echo "=== VF-05.3 FOUR-WAY COUNT GUARD ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface-count-consistency.sh
  rg -n 'validate-surface-count-consistency\.sh' /home/zaks/zakops-agent-api/.github/workflows/ci.yml /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-05.3-four-way-count-guard.txt
```

**PASS if:** script exists and is wired for enforcement.

### VF-05.4: Strict Surface 14 Enforcement in CI

```bash
{
  echo "=== VF-05.4 STRICT SURFACE14 IN CI ==="
  rg -n 'STRICT=1.*validate-surface14\.sh|validate-surface14\.sh.*STRICT=1|Surface 14.*STRICT' /home/zaks/zakops-agent-api/.github/workflows/ci.yml
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-05.4-strict-s14-ci.txt
```

**PASS if:** CI explicitly runs strict Surface 14 validation.

### VF-05.5: Gate E Inline Snippet Regression Check

```bash
{
  echo "=== VF-05.5 INLINE GATE E REGRESSION CHECK ==="
  rg -n 'if rg -n .*httpx|Raw httpx client usage found in deal_tools\.py' /home/zaks/zakops-agent-api/.github/workflows/ci.yml || true
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-ci-gatee-policy.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-05.5-inline-gatee-regression-check.txt
```

**PASS if:** inline snippet is absent and policy script exits 0.

**Gate VF-05:** All 5 checks PASS.

---

## Verification Family 06 - Drift Guards and Pre-Commit Style Protections (AC-10, AC-11)

### VF-06.1: Stale Surface Label Scanner Presence and Semantics

```bash
{
  echo "=== VF-06.1 STALE LABEL SCANNER ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/scan-stale-surface-labels.sh
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/infra/scan-stale-surface-labels.sh
  rg -n '7 surfaces|9 surfaces|14 surfaces|stop\.sh|ci\.yml|CLAUDE\.md|contract-surfaces' /home/zaks/zakops-agent-api/tools/infra/scan-stale-surface-labels.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-06.1-stale-label-scanner.txt
```

**PASS if:** scanner exists and targets stale-label drift patterns.

### VF-06.2: CLAUDE Surface Table Guard Presence and Semantics

```bash
{
  echo "=== VF-06.2 CLAUDE SURFACE TABLE GUARD ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-claude-surface-table.sh
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/infra/validate-claude-surface-table.sh
  rg -n 'Contract Surfaces|14 Total|\| 10 \||\| 11 \||\| 12 \||\| 13 \||\| 14 \|' /home/zaks/zakops-agent-api/tools/infra/validate-claude-surface-table.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-06.2-claude-table-guard.txt
```

**PASS if:** guard validates total and S10-S14 rows.

### VF-06.3: Pre-Commit Style Hook Script Presence and Wiring

```bash
{
  echo "=== VF-06.3 PRE-COMMIT STYLE HOOK ==="
  ls -l /home/zaks/zakops-agent-api/tools/hooks/pre-commit
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/hooks/pre-commit
  rg -n 'scan-stale-surface-labels\.sh|validate-claude-surface-table\.sh|check-governance-drift\.sh|validate-surface-count-consistency\.sh' /home/zaks/zakops-agent-api/tools/hooks/pre-commit
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-06.3-precommit-hook-wiring.txt
```

**PASS if:** pre-commit style hook exists and invokes core guard scripts.

### VF-06.4: Governance Drift Script Extended Coverage

```bash
{
  echo "=== VF-06.4 GOVERNANCE DRIFT EXTENDED COVERAGE ==="
  sed -n '1,320p' /home/zaks/zakops-agent-api/tools/infra/check-governance-drift.sh
  rg -n 'scan-stale-surface-labels|validate-claude-surface-table|benchmark|runtime|DRIFT|PASS|INFO' /home/zaks/zakops-agent-api/tools/infra/check-governance-drift.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-06.4-drift-script-coverage.txt
```

**PASS if:** drift script includes new guard coverage and benchmark-related output.

### VF-06.5: Runtime Guard Execution

```bash
{
  echo "=== VF-06.5 RUNTIME GUARD EXECUTION ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/scan-stale-surface-labels.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-claude-surface-table.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/check-governance-drift.sh
  cd /home/zaks/zakops-agent-api && bash tools/hooks/pre-commit
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-06.5-runtime-guard-execution.txt
```

**PASS if:** all guard scripts run and exit 0.

**Gate VF-06:** All 5 checks PASS.

---

## Verification Family 07 - QA and Bookkeeping Automation Utilities (AC-12, AC-13, AC-14)

### VF-07.1: Utility Script Presence and Executability

```bash
{
  echo "=== VF-07.1 AUTOMATION SCRIPT PRESENCE ==="
  ls -l /home/zaks/bookkeeping/scripts/qa-scaffold.sh
  ls -l /home/zaks/bookkeeping/scripts/check-ac-coverage.py
  ls -l /home/zaks/bookkeeping/scripts/generate-reconciliation-table.py
  ls -l /home/zaks/bookkeeping/scripts/governance-changelog-helper.sh
  ls -l /home/zaks/bookkeeping/scripts/compare-frontend-skill-vs-rule.py
  ls -l /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-AUTOMATION-RUNBOOK.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-07.1-automation-script-presence.txt
```

**PASS if:** all scripts and runbook exist.

### VF-07.2: QA Scaffold Dry-Run Execution

```bash
{
  echo "=== VF-07.2 QA SCAFFOLD DRY RUN ==="
  rm -rf /tmp/QA-IEU-SCAFFOLD-DRYRUN
  mkdir -p /tmp/QA-IEU-SCAFFOLD-DRYRUN
  cd /home/zaks/bookkeeping && bash scripts/qa-scaffold.sh QA-IEU-DRYRUN /tmp/QA-IEU-SCAFFOLD-DRYRUN
  find /tmp/QA-IEU-SCAFFOLD-DRYRUN -maxdepth 3 -type f | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-07.2-qa-scaffold-dryrun.txt
```

**PASS if:** scaffold script creates expected evidence/scorecard/completion skeleton.

### VF-07.3: AC Coverage Checker Runtime

```bash
{
  echo "=== VF-07.3 AC COVERAGE CHECKER RUNTIME ==="
  cd /home/zaks/bookkeeping && python3 scripts/check-ac-coverage.py \
    /home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md \
    /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-07.3-ac-coverage-runtime.txt
```

**PASS if:** checker runs successfully and reports AC coverage status.

### VF-07.4: Reconciliation Table Generator Runtime

```bash
{
  echo "=== VF-07.4 RECONCILIATION TABLE RUNTIME ==="
  cd /home/zaks/bookkeeping && python3 scripts/generate-reconciliation-table.py
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-07.4-reconciliation-generator-runtime.txt
```

**PASS if:** script outputs markdown-ready reconciliation table.

### VF-07.5: Governance Helper and Skill-vs-Rule Runtime

```bash
{
  echo "=== VF-07.5 GOVERNANCE HELPER + SKILL-RULE RUNTIME ==="
  cd /home/zaks/bookkeeping && bash scripts/governance-changelog-helper.sh --dry-run
  cd /home/zaks/bookkeeping && python3 scripts/compare-frontend-skill-vs-rule.py
  rg -n 'qa-scaffold\.sh|check-ac-coverage\.py|generate-reconciliation-table\.py|governance-changelog-helper\.sh|compare-frontend-skill-vs-rule\.py' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-AUTOMATION-RUNBOOK.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-07.5-governance-helper-skillrule-runtime.txt
```

**PASS if:** both utilities run and runbook references all automation scripts.

**Gate VF-07:** All 5 checks PASS.

---

## Verification Family 08 - No Regression and Bookkeeping Closure (AC-15, AC-16)

### VF-08.1: Final Validation Command Set Passes

```bash
{
  echo "=== VF-08.1 FINAL VALIDATION COMMAND SET ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
  cd /home/zaks/zakops-agent-api && make validate-surfaces-new
  cd /home/zaks/zakops-agent-api && make validate-hook-contract
  cd /home/zaks/zakops-agent-api && bash tools/infra/check-governance-drift.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-08.1-final-validation-commands.txt
```

**PASS if:** all listed commands exit 0.

### VF-08.2: Completion Report AC Coverage (1..16)

```bash
{
  echo "=== VF-08.2 COMPLETION AC COVERAGE ==="
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12|AC-13|AC-14|AC-15|AC-16' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-08.2-completion-ac-coverage.txt
```

**PASS if:** all 16 ACs are explicitly represented.

### VF-08.3: Successor Handoff Integrity

```bash
{
  echo "=== VF-08.3 SUCCESSOR HANDOFF ==="
  rg -n 'QA-IEU-VERIFY-001|Successor|handoff|FULL PASS' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md /home/zaks/bookkeeping/mission-checkpoints/INFRA-ENHANCEMENTS-UNIFIED-001.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-08.3-successor-handoff.txt
```

**PASS if:** completion/checkpoint artifacts clearly indicate QA handoff and closure status.

### VF-08.4: Evidence Completeness Audit

```bash
{
  echo "=== VF-08.4 EVIDENCE COMPLETENESS ==="
  find /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence -maxdepth 1 -type f | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/VF-08.4-evidence-completeness.txt
```

**PASS if:** evidence files exist for all executed PF/VF/XC/ST checks.

**Gate VF-08:** All 4 checks PASS.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Source AC Set vs Completion AC Claims

```bash
{
  echo "=== XC-1 AC RECONCILIATION ==="
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12|AC-13|AC-14|AC-15|AC-16' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/XC-1-ac-reconciliation.txt
```

**PASS if:** completion claims align exactly with source AC set.

### XC-2: Coverage Matrix vs Delivered Artifacts

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/XC-2-coverage-matrix-vs-artifacts.txt
from pathlib import Path
mission=Path('/home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md').read_text()
completion=Path('/home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md').read_text()
checks=[
  'validate-performance-budget-schema.sh',
  'validate-governance-anchor-schema.sh',
  'validate-manifest-contract-section.sh',
  'test-validate-gatee-scan.sh',
  'test-validate-surfaces10-14.sh',
  'validate-stop-hook-selftest.sh',
  'validate-surfaces-new',
  'validate-hook-contract',
  'validate-enhancements',
  'validate-ci-gatee-policy.sh',
  'validate-surface-count-consistency.sh',
  'scan-stale-surface-labels.sh',
  'validate-claude-surface-table.sh',
  'qa-scaffold.sh',
  'check-ac-coverage.py',
  'generate-reconciliation-table.py',
]
ok=True
for c in checks:
    present=(c in completion)
    print(c, '->', 'PASS' if present else 'FAIL')
    if not present:
        ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** completion report references all critical enhancement deliverables.

### XC-3: Make Targets vs Script Files Alignment

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/XC-3-make-vs-scripts-alignment.txt
from pathlib import Path
import re
mk=Path('/home/zaks/zakops-agent-api/Makefile').read_text()
base=Path('/home/zaks/zakops-agent-api/tools/infra')
targets={
    'validate-surfaces-new': ['validate-surface10.sh','validate-surface11.sh','validate-surface12.sh','validate-surface13.sh','validate-surface14.sh'],
    'validate-hook-contract': ['validate-stop-hook-contract.sh'],
    'validate-enhancements': ['validate-ci-gatee-policy.sh','validate-surface-count-consistency.sh'],
}
ok=True
for t,scripts in targets.items():
    has_target=bool(re.search(rf'^{t}:',mk,flags=re.M))
    print(f'{t}_target=', 'PASS' if has_target else 'FAIL')
    if not has_target:
        ok=False
    for s in scripts:
        exists=(base/s).exists()
        print(f'  {s}_exists=', 'PASS' if exists else 'FAIL')
        if not exists:
            ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** target definitions align with expected script files.

### XC-4: CI Wiring vs Policy Scripts Alignment

```bash
{
  echo "=== XC-4 CI WIRING VS POLICY SCRIPTS ==="
  rg -n 'validate-ci-gatee-policy\.sh|validate-surface-count-consistency\.sh|validate-gatee-scan\.sh|STRICT=1.*validate-surface14\.sh|actionlint|yamllint' /home/zaks/zakops-agent-api/.github/workflows/ci.yml
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-ci-gatee-policy.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface-count-consistency.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/XC-4-ci-wiring-alignment.txt
```

**PASS if:** workflow references corresponding policy scripts and strict S14/lint steps.

### XC-5: Four-Way Count Script vs Actual Authoritative Counts

```bash
{
  echo "=== XC-5 COUNT SCRIPT VS AUTHORITATIVE COUNTS ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-surface-count-consistency.sh
  python3 - <<'PY'
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text() if (repo/'INFRASTRUCTURE_MANIFEST.md').exists() else ''
cs_count=len(re.findall(r'^### Surface \d+:', cs, flags=re.M))
cla_count=int(re.search(r'Contract Surfaces \((\d+) Total\)', cla).group(1))
vs_count=int(re.search(r'Validates all (\d+) contract surfaces', vs).group(1))
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', man)
man_count=len([ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]) if sec else -1
print('contract-surfaces.md=', cs_count)
print('CLAUDE.md=', cla_count)
print('validator_header=', vs_count)
print('manifest_section=', man_count)
ok=(cs_count==cla_count==vs_count==14 and man_count in (14,-1))
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/XC-5-count-script-vs-authoritative.txt
```

**PASS if:** script and authoritative counts agree.

### XC-6: Automation Runbook vs Utility Files

```bash
{
  echo "=== XC-6 RUNBOOK VS UTILITY FILES ==="
  rg -n 'qa-scaffold\.sh|check-ac-coverage\.py|generate-reconciliation-table\.py|governance-changelog-helper\.sh|compare-frontend-skill-vs-rule\.py' /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-AUTOMATION-RUNBOOK.md
  ls -l /home/zaks/bookkeeping/scripts/qa-scaffold.sh
  ls -l /home/zaks/bookkeeping/scripts/check-ac-coverage.py
  ls -l /home/zaks/bookkeeping/scripts/generate-reconciliation-table.py
  ls -l /home/zaks/bookkeeping/scripts/governance-changelog-helper.sh
  ls -l /home/zaks/bookkeeping/scripts/compare-frontend-skill-vs-rule.py
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/XC-6-runbook-vs-utilities.txt
```

**PASS if:** runbook references all utility scripts and files exist.

---

## 5. Stress Tests (ST)

### ST-1: `validate-enhancements` Determinism (3 runs)

```bash
{
  echo "=== ST-1 VALIDATE-ENHANCEMENTS DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make validate-enhancements
  cd /home/zaks/zakops-agent-api && make validate-enhancements
  cd /home/zaks/zakops-agent-api && make validate-enhancements
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/ST-1-validate-enhancements-determinism.txt
```

**PASS if:** all three runs pass consistently.

### ST-2: `validate-surfaces-new` Determinism (3 runs)

```bash
{
  echo "=== ST-2 VALIDATE-SURFACES-NEW DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make validate-surfaces-new
  cd /home/zaks/zakops-agent-api && make validate-surfaces-new
  cd /home/zaks/zakops-agent-api && make validate-surfaces-new
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/ST-2-validate-surfaces-new-determinism.txt
```

**PASS if:** all three runs pass with stable output.

### ST-3: Hook Self-Test Stability (2 runs)

```bash
{
  echo "=== ST-3 HOOK SELFTEST STABILITY ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-stop-hook-selftest.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-stop-hook-selftest.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/ST-3-hook-selftest-stability.txt
```

**PASS if:** both runs pass with consistent branch outcomes.

### ST-4: Stale Label Scanner Stability (2 runs)

```bash
{
  echo "=== ST-4 STALE LABEL SCANNER STABILITY ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/scan-stale-surface-labels.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/scan-stale-surface-labels.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/ST-4-stale-label-scanner-stability.txt
```

**PASS if:** both runs are deterministic.

### ST-5: Snapshot Regeneration + Four-Way Count Stability

```bash
{
  echo "=== ST-5 SNAPSHOT + COUNT STABILITY ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-surface-count-consistency.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/ST-5-snapshot-count-stability.txt
```

**PASS if:** snapshot regeneration succeeds and count consistency remains valid.

### ST-6: New File Ownership and Line Ending Hygiene

```bash
{
  echo "=== ST-6 OWNERSHIP + LINE ENDING HYGIENE ==="
  find /home/zaks/zakops-agent-api/tools/infra -maxdepth 2 -type f \( -name 'validate-*' -o -name 'scan-*' -o -name '*.schema.json' \) | sort
  file /home/zaks/zakops-agent-api/tools/infra/validate-performance-budget-schema.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-governance-anchor-schema.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-manifest-contract-section.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-ci-gatee-policy.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-surface-count-consistency.sh
  file /home/zaks/zakops-agent-api/tools/infra/scan-stale-surface-labels.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-claude-surface-table.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/ST-6-file-hygiene.txt
```

**PASS if:** files are present and not CRLF-corrupted.

### ST-7: Forbidden File Regression Guard

```bash
{
  echo "=== ST-7 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
  cd /home/zaks/zakops-agent-api && git diff --name-only | rg 'generated\.ts$|_models\.py$|/migrations/' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-IEU-VERIFY-001/evidence/ST-7-forbidden-file-regression-guard.txt
```

**PASS if:** no forbidden-file edits are introduced by QA remediations.

---

## 6. Remediation Protocol

When a check fails:

1. Capture failing command and evidence path.
2. Classify failure:
- `NOT_EXECUTED`
- `MISSING_FIX`
- `REGRESSION`
- `SCOPE_GAP`
- `FALSE_POSITIVE`
- `NOT_IMPLEMENTED`
- `PARTIAL`
- `VIOLATION`
- `CI_WIRING_GAP`
- `COUNT_MISMATCH`
- `AUTOMATION_GAP`

3. Apply minimal remediation aligned to `INFRA-ENHANCEMENTS-UNIFIED-001` scope.
4. Re-run failed check first.
5. Re-run no-regression baseline:
- `cd /home/zaks/zakops-agent-api && make validate-local`
- `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
- `cd /home/zaks/zakops-agent-api && make validate-frontend-governance`

6. If CI/policy scripts were remediated, re-run:
- VF-05 family
- XC-4
- XC-5

7. If automation scripts were remediated, re-run:
- VF-07 family
- XC-6

8. Record remediations in scorecard and completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Add strict JSON-schema validation for mission completion reports.
### ENH-2: Add fixture mutation fuzz tests for schema validators.
### ENH-3: Add CI artifact upload for enhancement verification logs.
### ENH-4: Add diff-aware stale-label scanner that only checks changed files in pre-commit mode.
### ENH-5: Add benchmark trend history file for governance/drift checks.
### ENH-6: Add machine-readable summary output mode (`--json`) for all new validators.
### ENH-7: Add utility to auto-generate QA scorecard totals from evidence files.
### ENH-8: Add rule to ensure new validator scripts have usage/help text.
### ENH-9: Add periodic cron-based dry-run for automation utilities in housekeeping pipeline.
### ENH-10: Add consolidated validator SDK module to reduce shell duplication.

---

## 8. Scorecard Template

```
QA-IEU-VERIFY-001 - Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL / NOT_EXECUTED ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (Prerequisite + Coverage Matrix Integrity): __ / 4 checks PASS
  VF-02 (Schema Contracts + Validators): __ / 5 checks PASS
  VF-03 (Harnesses + Hook Self-Test): __ / 5 checks PASS
  VF-04 (Make Target Consolidation): __ / 5 checks PASS
  VF-05 (CI Policy Hardening): __ / 5 checks PASS
  VF-06 (Drift Guards + Pre-Commit): __ / 5 checks PASS
  VF-07 (QA/Bookkeeping Automation): __ / 5 checks PASS
  VF-08 (No Regression + Closure): __ / 4 checks PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 checks PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 tests PASS

Total: __ / 56 checks PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not build product features in this QA mission.
2. Remediate only what is required for `INFRA-ENHANCEMENTS-UNIFIED-001` AC closure.
3. Do not weaken Gate E, hook detection, or fail-closed semantics.
4. Preserve Surface 9 and 14-surface baseline behavior.
5. Do not edit generated files or migration files.
6. Keep all evidence paths absolute.
7. Every PASS requires captured evidence output.
8. Use `INFO`/`SKIP` classifications explicitly when runtime context prevents direct verification.
9. Do not force `FULL PASS` when AC evidence is incomplete.
10. Keep remediation scope minimal and traceable.

---

## 10. Stop Condition

Stop when all 56 checks pass (or are explicitly and correctly classified as `SKIP/INFO/FALSE_POSITIVE`), required remediations are re-verified, and baseline no-regression validations remain green.

Do not declare `FULL PASS` unless all 16 ACs are evidenced, enhancement coverage matrix closure is demonstrated, CI/drift/automation checks are operational, and surface-count consistency remains stable.

---

*End of Mission Prompt - QA-IEU-VERIFY-001*

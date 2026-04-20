# MISSION: QA-CIH-VERIFY-001
## Independent QA Verification and Remediation - CI-HARDENING-001
## Date: 2026-02-10
## Classification: QA Verification and Remediation
## Prerequisite: /home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md execution complete
## Successor: Post-CI governance automation and optimization missions only after FULL PASS

---

## Preamble: Builder Operating Context

The builder already loads project guardrails (`CLAUDE.md`, canonical memory, hooks, deny rules, path-scoped rules). This QA mission does not restate those systems. It independently verifies that `/home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md` was executed correctly and did not regress the Surface 9 and 14-surface contract baseline.

---

## 1. Mission Objective

This mission performs independent QA verification and in-scope remediation for `CI-HARDENING-001`.

Source mission under test:
- `/home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md`
- Expected structure: 7 phases (Phase 0 through Phase 6), 12 acceptance criteria (AC-1 through AC-12)
- Critical expectations:
  - Step 1 hardens `/home/zaks/.claude/hooks/stop.sh` project detection fallback
  - Hook behavior is verified for normal runtime, constrained PATH, and env-override branch
  - CI-safe validators exist for rule frontmatter, governance anchors, and Gate E raw `httpx` scanning
  - `make validate-frontend-governance` exists and is wired for local/CI parity
  - `.github/workflows/ci.yml` uses script-based Gate E and enforces frontend governance checks
  - Surface 9 and 14-surface baseline remain stable

Expected execution artifacts from source mission:
- `/home/zaks/bookkeeping/docs/CI-HARDENING-001-BASELINE.md`
- `/home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `CI-HARDENING-001`

QA scope:
- Verify all ACs with concrete evidence
- Cross-check consistency across hook behavior, scripts, Make targets, workflow wiring, and docs
- Stress-test deterministic behavior for hardened gates
- Apply minimal remediation only when required to satisfy source mission ACs

Out of scope:
- Product feature implementation
- Contract surface expansion beyond 14
- CI architecture redesign beyond source mission commitments

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md
  rg -n '^## Phase ' /home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md')
t=p.read_text()
phase_count=len(re.findall(r'^## Phase ', t, flags=re.M))
ac_count=len(re.findall(r'^### AC-', t, flags=re.M))
print('phase_count=', phase_count)
print('ac_count=', ac_count)
raise SystemExit(0 if (phase_count==7 and ac_count==12) else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** source mission exists and reports 7 phases + 12 ACs.

### PF-2: Execution Artifact Presence

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACTS ==="
  ls -l /home/zaks/bookkeeping/docs/CI-HARDENING-001-BASELINE.md
  ls -l /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md
  ls -l /home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md
  rg -n 'CI-HARDENING-001' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/PF-2-execution-artifacts.txt
```

**PASS if:** all execution artifacts exist and `CHANGES.md` includes mission ID.

**If FAIL:** classify as `NOT_EXECUTED` and stop gate progression.

### PF-3: Baseline Validation Health

```bash
{
  echo "=== PF-3 BASELINE VALIDATION HEALTH ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-surface9
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/PF-3-baseline-validation-health.txt
```

**PASS if:** all commands exit 0.

### PF-4: Hook and CI Wiring Snapshot

```bash
{
  echo "=== PF-4 HOOK + CI SNAPSHOT ==="
  ls -l /home/zaks/.claude/hooks/stop.sh
  ls -l /home/zaks/zakops-agent-api/.github/workflows/ci.yml
  rg -n 'Project Detection|MONOREPO_ROOT_OVERRIDE|git rev-parse|known-path-fallback|Gate A|Gate B|Gate E|validate-contract-surfaces \(14 surfaces\)|Validation gates not executed' /home/zaks/.claude/hooks/stop.sh
  rg -n 'plan-gates|Gate B|Gate C|Gate D|Gate E|validate-gatee-scan\.sh|validate-frontend-governance|raw httpx|deal_tools\.py' /home/zaks/zakops-agent-api/.github/workflows/ci.yml
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/PF-4-hook-ci-snapshot.txt
```

**PASS if:** snapshot captures Step 1 project-detection logic and CI Gate E/governance wiring markers.

### PF-5: Four-Way 14-Surface Baseline Snapshot

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/PF-5-four-way-count-baseline.txt
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

**PASS if:** authoritative counts remain 14 (manifest may be regenerated later if stale).

---

## 3. Verification Families (VF)

## Verification Family 01 - Prerequisite Chain and Execution Evidence (AC-1, AC-12)

### VF-01.1: Completion Report Presence and Structure

```bash
{
  echo "=== VF-01.1 COMPLETION STRUCTURE ==="
  wc -l /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md
  rg -n 'Phase 0|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5|Phase 6|AC-1|AC-12|PASS|FAIL|INFO' /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-01.1-completion-structure.txt
```

**PASS if:** completion report exists and includes phase + AC evidence mapping.

### VF-01.2: Baseline Evidence Integrity

```bash
{
  echo "=== VF-01.2 BASELINE EVIDENCE ==="
  ls -l /home/zaks/bookkeeping/docs/CI-HARDENING-001-BASELINE.md
  head -n 120 /home/zaks/bookkeeping/docs/CI-HARDENING-001-BASELINE.md
  rg -n 'make validate-local|make validate-surface9|make validate-contract-surfaces|stop\.sh|ci\.yml' /home/zaks/bookkeeping/docs/CI-HARDENING-001-BASELINE.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-01.2-baseline-integrity.txt
```

**PASS if:** baseline file contains pre-change validation and hook/CI Gate E evidence.

### VF-01.3: Checkpoint Closure Integrity

```bash
{
  echo "=== VF-01.3 CHECKPOINT INTEGRITY ==="
  ls -l /home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md
  tail -n 120 /home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-01.3-checkpoint-integrity.txt
```

**PASS if:** checkpoint documents completion state or clear successor handoff.

### VF-01.4: CHANGES Entry Integrity

```bash
{
  echo "=== VF-01.4 CHANGES ENTRY ==="
  rg -n 'CI-HARDENING-001|validate-frontend-governance|validate-gatee-scan|stop\.sh' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-01.4-changes-entry.txt
```

**PASS if:** mission ID and meaningful summary are present in `CHANGES.md`.

**Gate VF-01:** All 4 checks PASS.

---

## Verification Family 02 - Step 1 stop.sh Hardening and Runtime Behavior (AC-2, AC-3)

### VF-02.1: Static Detection Chain Markers

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.1-detection-chain-static.txt
from pathlib import Path
p=Path('/home/zaks/.claude/hooks/stop.sh')
t=p.read_text()
checks={
  'env_override': 'MONOREPO_ROOT_OVERRIDE',
  'git_rev_parse': 'git rev-parse --show-toplevel',
  'known_path_fallback': '/home/zaks/zakops-agent-api',
  'detection_method_echo': 'Project detected via',
  'makefile_signature': 'validate-fast',
}
ok=True
for k,v in checks.items():
    present=v in t
    print(f'{k}=', 'PASS' if present else 'FAIL')
    if not present:
        ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** Step 1 detection chain is fully present.

### VF-02.2: Explicit Skip Messaging (No Silent Skip)

```bash
{
  echo "=== VF-02.2 EXPLICIT SKIP MESSAGING ==="
  rg -n 'SKIP:|Validation gates not executed|No trusted monorepo root found|Makefile missing|lacks validate-fast target' /home/zaks/.claude/hooks/stop.sh
  rg -n 'silent|echo "skipping"' /home/zaks/.claude/hooks/stop.sh || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.2-explicit-skip-messaging.txt
```

**PASS if:** explicit skip reasons exist and no silent skip pattern is used.

### VF-02.3: Gate Chain and Surface Label Integrity

```bash
{
  echo "=== VF-02.3 GATE CHAIN + LABELS ==="
  rg -n 'Gate A: validate-fast|Gate B: validate-contract-surfaces \(14 surfaces\)|Gate E: raw httpx client usage check|All gates passed' /home/zaks/.claude/hooks/stop.sh
  rg -n '9 surfaces' /home/zaks/.claude/hooks/stop.sh || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.3-gate-chain-labels.txt
```

**PASS if:** Gate A/B/E are present, Gate B says 14 surfaces, stale 9-surface label is absent.

### VF-02.4: Runtime Normal Hook Behavior

```bash
{
  echo "=== VF-02.4 STOP HOOK NORMAL RUNTIME ==="
  cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh
  echo "stop_hook_exit=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.4-stop-hook-normal-runtime.txt
```

**PASS if:** hook completes within timeout and exits cleanly.

### VF-02.5: Runtime Constrained PATH Behavior

```bash
{
  echo "=== VF-02.5 STOP HOOK CONSTRAINED PATH ==="
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'timeout 35 bash /home/zaks/.claude/hooks/stop.sh; echo stop_hook_exit=$?'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.5-stop-hook-constrained-path-runtime.txt
```

**PASS if:** constrained PATH run does not globally skip when trusted root is inferable.

### VF-02.6: Env-Override Branch Behavior

```bash
{
  echo "=== VF-02.6 STOP HOOK ENV OVERRIDE BRANCH ==="
  cd /tmp && env -i PATH=/usr/bin:/bin HOME=/home/zaks MONOREPO_ROOT_OVERRIDE=/home/zaks/zakops-agent-api bash -lc 'timeout 35 bash /home/zaks/.claude/hooks/stop.sh'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.6-stop-hook-env-override-runtime.txt
```

**PASS if:** output indicates detection via env-override path and gates execute successfully.

**Gate VF-02:** All 6 checks PASS.

---

## Verification Family 03 - Validator Script Implementation and Behavior (AC-4, AC-5, AC-6)

### VF-03.1: Required Scripts Exist and Are Executable

```bash
{
  echo "=== VF-03.1 REQUIRED SCRIPT PRESENCE ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-contract.sh 2>/dev/null || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-03.1-script-presence.txt
```

**PASS if:** first three scripts exist and are executable (`validate-stop-hook-contract.sh` may be absent if mission chose not to implement optional task).

### VF-03.2: Frontmatter Validator Coverage

```bash
{
  echo "=== VF-03.2 RULE FRONTMATTER VALIDATOR COVERAGE ==="
  sed -n '1,220p' /home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh
  rg -n 'accessibility\.md|component-patterns\.md|design-system\.md|apps/dashboard/src/components/\*\*|apps/dashboard/src/app/\*\*|frontmatter|---' /home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-03.2-frontmatter-validator-coverage.txt
```

**PASS if:** validator enforces required rule files and path-scope frontmatter checks.

### VF-03.3: Frontend Governance Anchor Validator Coverage

```bash
{
  echo "=== VF-03.3 GOVERNANCE ANCHOR VALIDATOR COVERAGE ==="
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh
  rg -n 'design-system\.md|accessibility\.md|component-patterns\.md|breakpoint|z-index|dark mode|animation|state management|anti-convergence|WCAG|aria|server component|client component|8090' /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-03.3-governance-validator-coverage.txt
```

**PASS if:** validator checks required governance anchors and no-8090 drift.

### VF-03.4: Gate E Scanner Script Semantics

```bash
{
  echo "=== VF-03.4 GATE E SCANNER SCRIPT SEMANTICS ==="
  sed -n '1,260p' /home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh
  rg -n 'rg|grep|httpx\\\.\(AsyncClient\|get\|post\|put\|patch\|delete\)|deal_tools\.py|exit 1|exit 2|scanner error|fail closed' /home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-03.4-gatee-script-semantics.txt
```

**PASS if:** script implements rg->grep fallback and explicit rc handling semantics.

### VF-03.5: Runtime Script Execution

```bash
{
  echo "=== VF-03.5 RUNTIME SCRIPT EXECUTION ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-rule-frontmatter.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-frontend-governance.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-gatee-scan.sh
  if [ -f /home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-contract.sh ]; then
    cd /home/zaks/zakops-agent-api && bash tools/infra/validate-stop-hook-contract.sh
  else
    echo "optional_validate-stop-hook-contract=absent"
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-03.5-runtime-script-execution.txt
```

**PASS if:** all required scripts exit 0; optional script either passes or is explicitly absent.

**Gate VF-03:** All 5 checks PASS.

---

## Verification Family 04 - Make Target Parity and Local Enforcement (AC-7)

### VF-04.1: Make Target Definition Present

```bash
{
  echo "=== VF-04.1 MAKE TARGET DEFINITION ==="
  rg -n '^validate-frontend-governance:' /home/zaks/zakops-agent-api/Makefile
  rg -n 'validate-rule-frontmatter\.sh|validate-frontend-governance\.sh|validate-gatee-scan\.sh' /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-04.1-make-target-definition.txt
```

**PASS if:** target exists and includes all required validators.

### VF-04.2: Make Dry-Run Command Graph

```bash
{
  echo "=== VF-04.2 MAKE DRY RUN GRAPH ==="
  cd /home/zaks/zakops-agent-api && make -n validate-frontend-governance
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-04.2-make-dryrun-governance.txt
```

**PASS if:** dry run resolves to the intended script chain.

### VF-04.3: Placement in validate-local or validate-full (or explicit rationale)

```bash
{
  echo "=== VF-04.3 LOCAL/CI PARITY PLACEMENT ==="
  rg -n '^validate-local:|^validate-full:' /home/zaks/zakops-agent-api/Makefile
  cd /home/zaks/zakops-agent-api && make -n validate-local
  cd /home/zaks/zakops-agent-api && make -n validate-full
  rg -n 'validate-frontend-governance|runtime|parity|CI-only' /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-04.3-parity-placement.txt
```

**PASS if:** target is integrated into local/full path, or non-integration is explicitly justified in completion artifact.

### VF-04.4: Runtime Aggregate Target Pass

```bash
{
  echo "=== VF-04.4 RUN AGGREGATE TARGET ==="
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-04.4-run-aggregate-target.txt
```

**PASS if:** command exits 0.

### VF-04.5: Local Validation Stability After Target Addition

```bash
{
  echo "=== VF-04.5 LOCAL VALIDATION STABILITY ==="
  cd /home/zaks/zakops-agent-api && make validate-local
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-04.5-local-validation-stability.txt
```

**PASS if:** local validation still exits 0 after integration.

**Gate VF-04:** All 5 checks PASS.

---

## Verification Family 05 - CI Workflow Wiring and Gate Enforcement (AC-8)

### VF-05.1: CI Gate E Uses Script-Based Validator

```bash
{
  echo "=== VF-05.1 CI GATE E SCRIPT WIRING ==="
  rg -n 'Gate E|validate-gatee-scan\.sh' /home/zaks/zakops-agent-api/.github/workflows/ci.yml
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-05.1-ci-gatee-script-wiring.txt
```

**PASS if:** workflow Gate E calls `bash tools/infra/validate-gatee-scan.sh`.

### VF-05.2: Inline Gate E rg Snippet Removed

```bash
{
  echo "=== VF-05.2 INLINE RG SNIPPET REMOVED ==="
  rg -n 'if rg -n|grep -nE.*httpx|Raw httpx client usage found in deal_tools\.py' /home/zaks/zakops-agent-api/.github/workflows/ci.yml || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-05.2-inline-gatee-removal.txt
```

**PASS if:** inline scan snippet is removed in favor of script-based validator.

### VF-05.3: Frontend Governance CI Gate Present

```bash
{
  echo "=== VF-05.3 FRONTEND GOVERNANCE CI GATE ==="
  rg -n 'validate-frontend-governance|validate-rule-frontmatter\.sh|validate-frontend-governance\.sh' /home/zaks/zakops-agent-api/.github/workflows/ci.yml
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-05.3-governance-ci-gate.txt
```

**PASS if:** workflow enforces frontend governance checks.

### VF-05.4: Plan-Gates Chain Coherence Preserved

```bash
{
  echo "=== VF-05.4 PLAN-GATES COHERENCE ==="
  rg -n '^  plan-gates:|Gate B|Gate C|Gate D|Gate E|validate-contract-surfaces|validate-agent-config|validate_sse_schema\.py' /home/zaks/zakops-agent-api/.github/workflows/ci.yml
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-05.4-plan-gates-coherence.txt
```

**PASS if:** existing plan-gates chain remains coherent while including new hardening checks.

### VF-05.5: CI-Safe Runtime of Gate E Script Under Constrained PATH

```bash
{
  echo "=== VF-05.5 CI-SAFE GATE E RUNTIME ==="
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'bash tools/infra/validate-gatee-scan.sh'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-05.5-ci-safe-gatee-runtime.txt
```

**PASS if:** script runs cleanly under constrained PATH without hidden tool assumptions.

**Gate VF-05:** All 5 checks PASS.

---

## Verification Family 06 - Baseline Preservation and No Regression (AC-9, AC-11)

### VF-06.1: Surface 9 Validation Pass

```bash
{
  echo "=== VF-06.1 SURFACE9 VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-surface9
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-06.1-surface9-validation.txt
```

**PASS if:** command exits 0.

### VF-06.2: Unified 14-Surface Validation Pass

```bash
{
  echo "=== VF-06.2 UNIFIED 14-SURFACE VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-06.2-unified-surface-validation.txt
```

**PASS if:** command exits 0 and output confirms full 14-surface behavior.

### VF-06.3: Local Validation Pass

```bash
{
  echo "=== VF-06.3 LOCAL VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-local
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-06.3-local-validation.txt
```

**PASS if:** command exits 0.

### VF-06.4: Dashboard TypeScript Compile Pass

```bash
{
  echo "=== VF-06.4 DASHBOARD TSC ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-06.4-dashboard-tsc.txt
```

**PASS if:** command exits 0.

### VF-06.5: Forbidden File Regression Guard

```bash
{
  echo "=== VF-06.5 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
  cd /home/zaks/zakops-agent-api && git diff --name-only | rg 'generated\.ts$|_models\.py$|/migrations/' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-06.5-forbidden-file-regression-guard.txt
```

**PASS if:** no forbidden-file regressions are introduced during QA remediation.

**Gate VF-06:** All 5 checks PASS.

---

## Verification Family 07 - Documentation and Bookkeeping Closure (AC-10, AC-12)

### VF-07.1: Documentation Discoverability of New Governance/CI Commands

```bash
{
  echo "=== VF-07.1 DOCUMENTATION DISCOVERABILITY ==="
  rg -n 'validate-frontend-governance|validate-gatee-scan\.sh|Gate E|frontend governance|CI hardening' /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md /home/zaks/bookkeeping/CHANGES.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-07.1-documentation-discoverability.txt
```

**PASS if:** documentation and closure artifacts contain discoverable references to new checks/wiring.

### VF-07.2: Completion Report AC Coverage (1..12)

```bash
{
  echo "=== VF-07.2 COMPLETION AC COVERAGE ==="
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12' /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-07.2-completion-ac-coverage.txt
```

**PASS if:** all 12 ACs are explicitly accounted for.

### VF-07.3: Checkpoint + CHANGES Closure State

```bash
{
  echo "=== VF-07.3 CHECKPOINT + CHANGES CLOSURE ==="
  tail -n 120 /home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md
  rg -n 'CI-HARDENING-001|QA-CIH-VERIFY-001|successor|handoff' /home/zaks/bookkeeping/CHANGES.md /home/zaks/bookkeeping/mission-checkpoints/CI-HARDENING-001.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-07.3-closure-artifacts.txt
```

**PASS if:** closure artifacts clearly indicate mission completion and QA handoff.

### VF-07.4: Evidence Completeness Audit

```bash
{
  echo "=== VF-07.4 EVIDENCE COMPLETENESS ==="
  find /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence -maxdepth 1 -type f | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-07.4-evidence-completeness.txt
```

**PASS if:** evidence files exist for all executed PF/VF/XC/ST checks.

**Gate VF-07:** All 4 checks PASS.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Source AC Set vs Completion AC Claims

```bash
{
  echo "=== XC-1 AC SET RECONCILIATION ==="
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-CI-HARDENING-001.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12' /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/XC-1-ac-reconciliation.txt
```

**PASS if:** completion AC claims align exactly with source mission AC set.

### XC-2: stop.sh Claims vs Runtime Evidence

```bash
{
  echo "=== XC-2 STOP HOOK CLAIMS VS RUNTIME ==="
  rg -n 'Project Detection|env-override|git rev-parse|known-path-fallback|SKIP:|Validation gates not executed|Gate E|fail closed' /home/zaks/.claude/hooks/stop.sh
  cat /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.4-stop-hook-normal-runtime.txt
  cat /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.5-stop-hook-constrained-path-runtime.txt
  cat /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/VF-02.6-stop-hook-env-override-runtime.txt
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/XC-2-stop-hook-claims-vs-runtime.txt
```

**PASS if:** static claims match runtime outcomes across all three test contexts.

### XC-3: Make Target Recipe vs CI Workflow Wiring

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/XC-3-make-vs-ci-wiring.txt
from pathlib import Path
mk=Path('/home/zaks/zakops-agent-api/Makefile').read_text()
ci=Path('/home/zaks/zakops-agent-api/.github/workflows/ci.yml').read_text()
checks={
  'make_has_validate_frontend_governance': 'validate-frontend-governance:' in mk,
  'make_has_frontmatter_validator': 'validate-rule-frontmatter.sh' in mk,
  'make_has_governance_validator': 'validate-frontend-governance.sh' in mk,
  'make_has_gatee_validator': 'validate-gatee-scan.sh' in mk,
  'ci_has_gatee_script': 'validate-gatee-scan.sh' in ci,
  'ci_has_governance_gate': ('validate-frontend-governance' in ci or 'validate-frontend-governance.sh' in ci),
}
ok=True
for k,v in checks.items():
    print(f'{k}=', 'PASS' if v else 'FAIL')
    if not v:
        ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** local target and CI workflow are aligned on required validators.

### XC-4: Validator Expectations vs Rule File Reality

```bash
{
  echo "=== XC-4 VALIDATOR EXPECTATIONS VS RULE FILES ==="
  ls -l /home/zaks/zakops-agent-api/.claude/rules/design-system.md
  ls -l /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
  ls -l /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
  rg -n 'design-system\.md|accessibility\.md|component-patterns\.md' /home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/XC-4-validator-vs-rule-files.txt
```

**PASS if:** validators reference actual rule files and expected rule set.

### XC-5: Gate E Semantics Parity (stop.sh vs validate-gatee-scan.sh)

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/XC-5-gatee-semantics-parity.txt
from pathlib import Path
stop=Path('/home/zaks/.claude/hooks/stop.sh').read_text()
scan=Path('/home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh').read_text()
checks={
  'pattern_mentions_httpx_family_stop': 'httpx\\.(AsyncClient|get|post|put|patch|delete)' in stop,
  'pattern_mentions_httpx_family_scan': 'httpx\\.(AsyncClient|get|post|put|patch|delete)' in scan,
  'stop_has_rg_fallback': ('command -v rg' in stop and 'command -v grep' in stop),
  'scan_has_rg_fallback': ('command -v rg' in scan and 'command -v grep' in scan),
  'stop_has_scanner_error_fail_closed': ('scanner error' in stop or 'Fail closed' in stop or 'fail closed' in stop),
  'scan_has_scanner_error_fail_closed': ('scanner error' in scan or 'Fail closed' in scan or 'fail closed' in scan),
}
ok=True
for k,v in checks.items():
    print(f'{k}=', 'PASS' if v else 'FAIL')
    if not v:
        ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** stop hook and CI script enforce equivalent Gate E semantics.

### XC-6: Four-Way 14-Count Stability After QA Checks

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/XC-6-four-way-count-stability.txt
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

**PASS if:** 14-surface count remains stable across authoritative sources.

---

## 5. Stress Tests (ST)

### ST-1: Governance Aggregate Determinism (3 Consecutive Runs)

```bash
{
  echo "=== ST-1 GOVERNANCE AGGREGATE DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/ST-1-governance-determinism.txt
```

**PASS if:** all three runs pass consistently.

### ST-2: Constrained PATH Hook Stability (2 Consecutive Runs)

```bash
{
  echo "=== ST-2 CONSTRAINED PATH HOOK STABILITY ==="
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'timeout 35 bash /home/zaks/.claude/hooks/stop.sh'
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'timeout 35 bash /home/zaks/.claude/hooks/stop.sh'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/ST-2-constrained-path-hook-stability.txt
```

**PASS if:** both runs complete without timeout or false block.

### ST-3: Gate E Script Stability Under Constrained PATH (2 Runs)

```bash
{
  echo "=== ST-3 GATE E SCRIPT STABILITY UNDER CONSTRAINED PATH ==="
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'bash tools/infra/validate-gatee-scan.sh'
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'bash tools/infra/validate-gatee-scan.sh'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/ST-3-gatee-constrained-path-stability.txt
```

**PASS if:** both runs succeed with deterministic behavior.

### ST-4: No Port 8090 Regression Sweep

```bash
{
  echo "=== ST-4 NO PORT 8090 REGRESSION SWEEP ==="
  rg -n '8090' /home/zaks/.claude/hooks/stop.sh /home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh /home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh /home/zaks/zakops-agent-api/.github/workflows/ci.yml /home/zaks/bookkeeping/docs/CI-HARDENING-001-COMPLETION.md /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/ST-4-no-8090-regression-sweep.txt
```

**PASS if:** no forbidden 8090 drift is introduced.

### ST-5: Snapshot Regeneration and Count Stability

```bash
{
  echo "=== ST-5 SNAPSHOT REGEN + COUNT STABILITY ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  python3 - <<'PY'
import re
from pathlib import Path
m=Path('/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md').read_text()
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', m)
cnt=len([ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]) if sec else -1
print('manifest_contract_surface_count=', cnt)
raise SystemExit(0 if cnt==14 else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/ST-5-snapshot-count-stability.txt
```

**PASS if:** snapshot regeneration succeeds and manifest contract surface section remains 14.

### ST-6: File Ownership and Line Ending Hygiene

```bash
{
  echo "=== ST-6 OWNERSHIP + LINE ENDING HYGIENE ==="
  ls -l /home/zaks/.claude/hooks/stop.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh
  file /home/zaks/.claude/hooks/stop.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-rule-frontmatter.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-gatee-scan.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/ST-6-file-hygiene.txt
```

**PASS if:** ownership is sane and scripts are not CRLF-corrupted.

### ST-7: Forbidden File Regression Guard (Post-QA)

```bash
{
  echo "=== ST-7 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
  cd /home/zaks/zakops-agent-api && git diff --name-only | rg 'generated\.ts$|_models\.py$|/migrations/' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CIH-VERIFY-001/evidence/ST-7-forbidden-file-regression-guard.txt
```

**PASS if:** no forbidden files are modified as part of QA remediation.

---

## 6. Remediation Protocol

When a gate fails:

1. Capture exact failing command and evidence path.
2. Classify failure:
- `NOT_EXECUTED`
- `MISSING_FIX`
- `REGRESSION`
- `SCOPE_GAP`
- `FALSE_POSITIVE`
- `NOT_IMPLEMENTED`
- `PARTIAL`
- `VIOLATION`
- `PATH_DETECTION_GAP`
- `CI_WIRING_GAP`
- `COUNT_MISMATCH`

3. Apply minimal in-scope remediation aligned to `CI-HARDENING-001`.
4. Re-run failed check first.
5. Re-run no-regression baseline:
- `cd /home/zaks/zakops-agent-api && make validate-local`
- `cd /home/zaks/zakops-agent-api && make validate-surface9`
- `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`

6. If hook behavior was remediated, re-run:
- VF-02.4
- VF-02.5
- VF-02.6

7. If CI wiring or manifest changed, re-run:
- VF-05 family
- XC-6
- ST-5

8. Record remediation in scorecard and completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Add unit-test harness for `validate-gatee-scan.sh` with fixture files (clean/violation/scanner-error cases).
### ENH-2: Add a reusable YAML lint step for workflow structural correctness in PR checks.
### ENH-3: Add dedicated `make validate-hook-contract` target and wire optional script formally.
### ENH-4: Add CI assertion that forbids inline Gate E snippets in workflow files.
### ENH-5: Add machine-readable schema for governance anchor sets to reduce validator drift.
### ENH-6: Add pre-commit guard for stale surface-count labels in hooks/workflows/docs.
### ENH-7: Add benchmark check to track `validate-frontend-governance` runtime budgets.
### ENH-8: Add snapshot diff summarizer for manifest changes across runs.
### ENH-9: Add automated AC coverage checker for completion reports.
### ENH-10: Add QA scaffold command for CI-hardening mission family evidence skeletons.

---

## 8. Scorecard Template

```
QA-CIH-VERIFY-001 - Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL / NOT_EXECUTED ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (Prerequisite + Evidence Integrity): __ / 4 checks PASS
  VF-02 (Step 1 stop.sh Hardening + Runtime): __ / 6 checks PASS
  VF-03 (Validator Scripts): __ / 5 checks PASS
  VF-04 (Make Target Parity): __ / 5 checks PASS
  VF-05 (CI Workflow Wiring): __ / 5 checks PASS
  VF-06 (Baseline Preservation + No Regression): __ / 5 checks PASS
  VF-07 (Documentation + Bookkeeping Closure): __ / 4 checks PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 checks PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 tests PASS

Total: __ / 52 checks PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not build product features in this QA mission.
2. Remediate only what is required to satisfy `CI-HARDENING-001` ACs.
3. Do not weaken stop-hook gate semantics to force a pass.
4. Do not bypass CI failures by removing or loosening critical gates.
5. Preserve Surface 9 and 14-surface baseline behavior.
6. Do not edit generated files or migration files.
7. Use absolute paths in every command and evidence artifact.
8. Every PASS must have captured `tee` evidence.
9. If services/context limit runtime checks, classify explicitly as `INFO` or `SKIP`, never silent PASS.
10. If evidence is ambiguous, escalate as `INFO` instead of forcing `FULL PASS`.

---

## 10. Stop Condition

Stop when all 52 checks pass (or are explicitly and correctly classified as `SKIP/INFO/FALSE_POSITIVE`), all required remediations are applied and re-verified, and baseline validations remain green.

Do not declare `FULL PASS` unless Step 1 hook hardening behavior, CI gate wiring, validator scripts, aggregate governance target, and 14-surface no-regression checks are all satisfied with concrete evidence.

---

*End of Mission Prompt - QA-CIH-VERIFY-001*

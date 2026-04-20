# MISSION: QA-FGH-VERIFY-001
## Independent QA Verification and Remediation - FRONTEND-GOVERNANCE-HARDENING-001
## Date: 2026-02-10
## Classification: QA Verification and Remediation
## Prerequisite: /home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md execution complete
## Successor: CI/Pipeline hardening follow-up missions only after FULL PASS

---

## Preamble: Builder Operating Context

The builder already loads project guardrails (`CLAUDE.md`, canonical memory, hooks, deny rules, path-scoped rules). This QA mission does not restate those systems. It independently verifies that `/home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md` was executed correctly and did not regress the 14-surface infrastructure baseline.

---

## 1. Mission Objective

This mission performs independent QA verification and minimal in-scope remediation for `FRONTEND-GOVERNANCE-HARDENING-001`.

Source mission under test:
- `/home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md`
- Expected structure: 7 phases (Phase 0 through Phase 6), 12 acceptance criteria (AC-1 through AC-12)
- Critical expectations:
  - Gate E in `/home/zaks/.claude/hooks/stop.sh` is PATH-resilient and fail-closed
  - Frontend governance rules `accessibility.md` and `component-patterns.md` exist and are path-scoped
  - `design-system.md` governance coverage is expanded and linked to frontend-design skill
  - `validate-surface9.sh` enforces new governance anchors
  - 14-surface contract baseline remains healthy

Expected execution artifacts from source mission:
- `/home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-BASELINE.md`
- `/home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `FRONTEND-GOVERNANCE-HARDENING-001`
- `/home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md`

QA scope:
- Verify all ACs with evidence
- Verify no regression in Surface 9 and 14-surface validation
- Verify hook resilience and fail-closed behavior for Gate E
- Remediate only failures required to satisfy source mission ACs

Out of scope:
- Frontend feature implementation
- New contract surfaces
- Full Playwright rollout redesign

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md
  rg -n '^## Phase ' /home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** mission exists and shows 7 phases + 12 ACs.

### PF-2: Execution Artifact Presence

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACTS ==="
  ls -l /home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-BASELINE.md
  ls -l /home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-COMPLETION.md
  ls -l /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md
  ls -l /home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md
  rg -n 'FRONTEND-GOVERNANCE-HARDENING-001' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/PF-2-execution-artifacts.txt
```

**PASS if:** all artifacts exist and CHANGES contains mission entry.

**If FAIL:** classify as `NOT_EXECUTED` and stop gate progression.

### PF-3: Baseline Validation Health

```bash
{
  echo "=== PF-3 BASELINE VALIDATION HEALTH ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-surface9
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/PF-3-baseline-validation-health.txt
```

**PASS if:** all commands exit 0.

### PF-4: Runtime Hook Context Snapshot

```bash
{
  echo "=== PF-4 HOOK CONTEXT SNAPSHOT ==="
  ls -l /home/zaks/.claude/hooks/stop.sh
  sed -n '1,220p' /home/zaks/.claude/hooks/stop.sh
  command -v rg || true
  command -v grep || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/PF-4-hook-context-snapshot.txt
```

**PASS if:** hook file readable and scanner tooling context captured.

### PF-5: 14-Surface Count Baseline Snapshot

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/PF-5-four-way-count-baseline.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text() if (repo/'INFRASTRUCTURE_MANIFEST.md').exists() else ''
cs_count=len(re.findall(r'^### Surface \d+:',cs,flags=re.M))
cla_count=int(re.search(r'Contract Surfaces \((\d+) Total\)',cla).group(1))
vs_count=int(re.search(r'Validates all (\d+) contract surfaces',vs).group(1))
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)',man)
man_count=len([ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]) if sec else -1
print('contract-surfaces.md=',cs_count)
print('CLAUDE.md=',cla_count)
print('validator_header=',vs_count)
print('manifest_section=',man_count)
ok=(cs_count==cla_count==vs_count==14 and man_count in (14,-1))
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** core authoritative counts remain 14 (manifest may be regenerated later if stale).

---

## 3. Verification Families (VF)

## Verification Family 01 - Hook Gate E PATH Resilience and Fail-Closed Behavior (AC-2, AC-9)

### VF-01.1: Static Gate E Branching Logic Present

```bash
{
  echo "=== VF-01.1 GATE E BRANCHING ==="
  rg -n 'Gate E|command -v rg|command -v grep|fail closed|scanner error|raw httpx' /home/zaks/.claude/hooks/stop.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-01.1-gatee-branching.txt
```

**PASS if:** hook shows rg-first, grep-fallback, and explicit fail-closed error path.

### VF-01.2: Static Gate E Return-Code Handling

```bash
{
  echo "=== VF-01.2 GATE E RC HANDLING ==="
  rg -n 'GATE_E_RC|== 0|== 1|else|exit 2' /home/zaks/.claude/hooks/stop.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-01.2-gatee-rc-handling.txt
```

**PASS if:** script distinguishes match-found, no-match, and scanner-error outcomes.

### VF-01.3: Gate B Label Accuracy Preserved

```bash
{
  echo "=== VF-01.3 GATE B LABEL ==="
  rg -n 'Gate B: validate-contract-surfaces \(14 surfaces\)|all 14' /home/zaks/.claude/hooks/stop.sh
  rg -n '9 surfaces' /home/zaks/.claude/hooks/stop.sh || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-01.3-gateb-label-accuracy.txt
```

**PASS if:** Gate B explicitly references 14 surfaces and stale 9-surface wording is absent.

### VF-01.4: Normal Hook Runtime Pass

```bash
{
  echo "=== VF-01.4 STOP HOOK NORMAL RUNTIME ==="
  cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh
  echo "stop_hook_exit=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-01.4-stop-hook-normal-runtime.txt
```

**PASS if:** hook completes within timeout and exits cleanly.

### VF-01.5: Constrained PATH Hook Runtime Pass

```bash
{
  echo "=== VF-01.5 STOP HOOK CONSTRAINED PATH ==="
  env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'command -v rg >/dev/null 2>&1; echo rg_present=$?; command -v grep >/dev/null 2>&1; echo grep_present=$?'
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'timeout 35 bash /home/zaks/.claude/hooks/stop.sh; echo stop_hook_exit=$?'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-01.5-stop-hook-constrained-path.txt
```

**PASS if:** constrained PATH run does not silently bypass Gate E and exits correctly.

**Gate VF-01:** All 5 checks PASS.

---

## Verification Family 02 - New Rule Files and Path Scoping (AC-3, AC-4)

### VF-02.1: Accessibility Rule File Presence

```bash
{
  echo "=== VF-02.1 ACCESSIBILITY RULE PRESENCE ==="
  ls -l /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
  sed -n '1,220p' /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-02.1-accessibility-rule-presence.txt
```

**PASS if:** file exists and includes path frontmatter.

### VF-02.2: Component Patterns Rule File Presence

```bash
{
  echo "=== VF-02.2 COMPONENT-PATTERNS RULE PRESENCE ==="
  ls -l /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
  sed -n '1,240p' /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-02.2-component-patterns-rule-presence.txt
```

**PASS if:** file exists and includes path frontmatter.

### VF-02.3: Path Frontmatter Coverage Validation

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-02.3-frontmatter-coverage.txt
from pathlib import Path
files=[
 '/home/zaks/zakops-agent-api/.claude/rules/accessibility.md',
 '/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md',
]
required=['apps/dashboard/src/components/**','apps/dashboard/src/app/**']
ok=True
for f in files:
    txt=Path(f).read_text()
    print('FILE:',f)
    if not txt.startswith('---'):
        print('  FAIL: missing frontmatter start')
        ok=False
    for r in required:
        present=r in txt
        print(f'  {r}:', 'PASS' if present else 'FAIL')
        if not present: ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** both rule files include required dashboard path scopes.

### VF-02.4: Accessibility Rule Actionability Anchors

```bash
{
  echo "=== VF-02.4 ACCESSIBILITY ACTIONABILITY ==="
  rg -n 'WCAG|contrast|keyboard|focus|aria|semantic|reduced motion|prefers-reduced-motion' /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-02.4-accessibility-actionability.txt
```

**PASS if:** actionable accessibility anchors exist.

### VF-02.5: Component Patterns Rule Actionability Anchors

```bash
{
  echo "=== VF-02.5 COMPONENT-PATTERNS ACTIONABILITY ==="
  rg -n 'server component|client component|loading|empty|error|suspense|state ownership|compos' /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-02.5-component-patterns-actionability.txt
```

**PASS if:** actionable component pattern anchors exist.

**Gate VF-02:** All 5 checks PASS.

---

## Verification Family 03 - Design System Enrichment and Skill Linkage (AC-5, AC-6)

### VF-03.1: Skill Preload Linkage Present

```bash
{
  echo "=== VF-03.1 SKILL PRELOAD LINKAGE ==="
  rg -n 'Skill Preloads|/home/zaks/.claude/skills/frontend-design/SKILL.md|frontend-design' /home/zaks/zakops-agent-api/.claude/rules/design-system.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-03.1-skill-preload-linkage.txt
```

**PASS if:** design-system rule includes explicit local skill linkage.

### VF-03.2: Governance Gap Anchors Present in design-system.md

```bash
{
  echo "=== VF-03.2 GOVERNANCE GAP ANCHORS ==="
  rg -n 'breakpoint|responsive|z-index|dark mode|animation performance|GPU|layout|state management|anti-convergence|variation|tone' /home/zaks/zakops-agent-api/.claude/rules/design-system.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-03.2-governance-gap-anchors.txt
```

**PASS if:** all governance categories are represented.

### VF-03.3: Category A Constraints Not Regressed

```bash
{
  echo "=== VF-03.3 CATEGORY A NON-REGRESSION ==="
  rg -n 'Promise.allSettled|Promise.all|PIPELINE_STAGES|JSON 502|bridge|generated' /home/zaks/zakops-agent-api/.claude/rules/design-system.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-03.3-categorya-nonregression.txt
```

**PASS if:** existing architectural constraints remain present.

### VF-03.4: No Forbidden Port Drift in Frontend Governance Docs

```bash
{
  echo "=== VF-03.4 NO 8090 DRIFT ==="
  rg -n '8090' /home/zaks/zakops-agent-api/.claude/rules/design-system.md /home/zaks/zakops-agent-api/.claude/rules/accessibility.md /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-03.4-no-8090-drift.txt
```

**PASS if:** no new 8090 references introduced.

### VF-03.5: design-system Rule Structure Integrity

```bash
{
  echo "=== VF-03.5 DESIGN-SYSTEM STRUCTURE ==="
  wc -l /home/zaks/zakops-agent-api/.claude/rules/design-system.md
  rg -n '^## |^### ' /home/zaks/zakops-agent-api/.claude/rules/design-system.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-03.5-design-system-structure.txt
```

**PASS if:** rule structure remains coherent after enrichment.

**Gate VF-03:** All 5 checks PASS.

---

## Verification Family 04 - Surface 9 Validator Enforcement Hardening (AC-7, AC-8)

### VF-04.1: validate-surface9 Includes New Rule Presence Checks

```bash
{
  echo "=== VF-04.1 SURFACE9 NEW RULE CHECKS ==="
  rg -n 'accessibility\.md|component-patterns\.md' /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-04.1-surface9-new-rule-checks.txt
```

**PASS if:** validator explicitly checks new governance rule files.

### VF-04.2: validate-surface9 Includes New Section-Anchor Checks

```bash
{
  echo "=== VF-04.2 SURFACE9 NEW SECTION ANCHORS ==="
  rg -n 'breakpoint|z-index|dark mode|animation|state|Skill Preloads|frontend-design' /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-04.2-surface9-section-anchors.txt
```

**PASS if:** validator includes checks for new governance anchors.

### VF-04.3: Existing Surface 9 Core Checks Preserved

```bash
{
  echo "=== VF-04.3 SURFACE9 CORE CHECKS PRESERVED ==="
  rg -n 'generated file imports|hardcoded stage|Promise\.allSettled|design-system-manifest|design-system\.md' /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-04.3-surface9-core-preserved.txt
```

**PASS if:** prior core checks remain present.

### VF-04.4: Runtime Surface 9 Validation

```bash
{
  echo "=== VF-04.4 RUN SURFACE9 VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-surface9
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-04.4-run-surface9-validation.txt
```

**PASS if:** command exits 0.

### VF-04.5: Runtime Unified Contract Validation Still Passes

```bash
{
  echo "=== VF-04.5 RUN UNIFIED CONTRACT VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-04.5-run-unified-contract-validation.txt
```

**PASS if:** command exits 0 and preserves 14-surface state.

**Gate VF-04:** All 5 checks PASS.

---

## Verification Family 05 - Tooling Policy and Discoverability (AC-10)

### VF-05.1: Tooling Policy Document Presence and Structure

```bash
{
  echo "=== VF-05.1 TOOLING POLICY PRESENCE ==="
  ls -l /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md
  sed -n '1,260p' /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-05.1-tooling-policy-presence.txt
```

**PASS if:** policy file exists and is readable.

### VF-05.2: Tooling Policy Contains Skill Usage Guidance

```bash
{
  echo "=== VF-05.2 TOOLING POLICY SKILL GUIDANCE ==="
  rg -n 'frontend-design|Skill|SKILL\.md|design-system' /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-05.2-tooling-policy-skill-guidance.txt
```

**PASS if:** policy explains frontend-design skill usage expectations.

### VF-05.3: Tooling Policy Contains Playwright Status Guidance

```bash
{
  echo "=== VF-05.3 TOOLING POLICY PLAYWRIGHT GUIDANCE ==="
  rg -n 'Playwright|MCP|disabled|enable|settings\.json|verification' /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-05.3-tooling-policy-playwright-guidance.txt
```

**PASS if:** policy explicitly addresses current status and usage criteria.

### VF-05.4: Tooling Policy Reflects Live Settings

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-05.4-policy-vs-settings.txt
import json
from pathlib import Path
settings=Path('/home/zaks/.claude/settings.json')
j=json.loads(settings.read_text())
pw=j.get('mcpServers',{}).get('playwright',{})
print('playwright_disabled=',pw.get('disabled'))
print('policy_exists=',Path('/home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md').exists())
raise SystemExit(0)
PY
```

**PASS if:** policy and live setting state are both captured and reconcilable.

### VF-05.5: Policy Discoverability in Mission Artifacts

```bash
{
  echo "=== VF-05.5 POLICY DISCOVERABILITY ==="
  rg -n 'FRONTEND-TOOLING-POLICY\.md' /home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-COMPLETION.md /home/zaks/bookkeeping/CHANGES.md /home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-05.5-policy-discoverability.txt
```

**PASS if:** policy is referenced from at least one mission closure artifact.

**Gate VF-05:** All 5 checks PASS.

---

## Verification Family 06 - No Regression and Closure Integrity (AC-1, AC-11, AC-12)

### VF-06.1: No-Regression Validation Suite

```bash
{
  echo "=== VF-06.1 NO-REGRESSION SUITE ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-06.1-no-regression-suite.txt
```

**PASS if:** both commands exit 0.

### VF-06.2: Completion Report AC Coverage

```bash
{
  echo "=== VF-06.2 COMPLETION AC COVERAGE ==="
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12' /home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-06.2-completion-ac-coverage.txt
```

**PASS if:** all 12 ACs are explicitly represented.

### VF-06.3: Checkpoint Closure Integrity

```bash
{
  echo "=== VF-06.3 CHECKPOINT CLOSURE ==="
  ls -l /home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md
  tail -n 80 /home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-06.3-checkpoint-closure.txt
```

**PASS if:** checkpoint indicates final state or clear successor handoff.

### VF-06.4: Evidence Completeness

```bash
{
  echo "=== VF-06.4 EVIDENCE COMPLETENESS ==="
  find /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence -maxdepth 1 -type f | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-06.4-evidence-completeness.txt
```

**PASS if:** evidence files exist for all executed PF/VF/XC/ST checks.

**Gate VF-06:** All 4 checks PASS.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Source Mission ACs vs Completion Claims

```bash
{
  echo "=== XC-1 AC RECONCILIATION ==="
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-FRONTEND-GOVERNANCE-HARDENING-001.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12' /home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/XC-1-ac-reconciliation.txt
```

**PASS if:** completion coverage matches source mission AC set.

### XC-2: Rule Files vs Surface 9 Validator Alignment

```bash
{
  echo "=== XC-2 RULES VS S9 VALIDATOR ALIGNMENT ==="
  ls -l /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
  ls -l /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
  rg -n 'accessibility\.md|component-patterns\.md' /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/XC-2-rules-vs-s9-validator.txt
```

**PASS if:** validator expectations match actual rule files.

### XC-3: design-system Skill Reference vs Local Skill File

```bash
{
  echo "=== XC-3 DESIGN-SYSTEM VS SKILL FILE ==="
  rg -n '/home/zaks/.claude/skills/frontend-design/SKILL.md' /home/zaks/zakops-agent-api/.claude/rules/design-system.md
  ls -l /home/zaks/.claude/skills/frontend-design/SKILL.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/XC-3-design-system-vs-skill.txt
```

**PASS if:** reference and target file both exist.

### XC-4: Tooling Policy vs Live Playwright Setting

```bash
{
  echo "=== XC-4 POLICY VS SETTINGS ==="
  python3 - <<'PY'
import json
from pathlib import Path
j=json.loads(Path('/home/zaks/.claude/settings.json').read_text())
print('playwright_disabled=',j.get('mcpServers',{}).get('playwright',{}).get('disabled'))
PY
  rg -n 'Playwright|disabled|enable' /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/XC-4-policy-vs-playwright-setting.txt
```

**PASS if:** policy text is consistent with live settings state.

### XC-5: Hook PATH Resilience Claims vs Runtime Evidence

```bash
{
  echo "=== XC-5 HOOK CLAIMS VS RUNTIME ==="
  rg -n 'PATH-resilient|falls back|grep|scanner error|fail closed' /home/zaks/.claude/hooks/stop.sh
  cat /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-01.4-stop-hook-normal-runtime.txt
  cat /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/VF-01.5-stop-hook-constrained-path.txt
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/XC-5-hook-claims-vs-runtime.txt
```

**PASS if:** static claims and runtime outcomes are consistent.

### XC-6: 14-Surface Stability after Governance Changes

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/XC-6-four-way-count-stability.txt
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

**PASS if:** governance changes did not destabilize 14-surface count integrity.

---

## 5. Stress Tests (ST)

### ST-1: Repeated Surface 9 Validation Determinism

```bash
{
  echo "=== ST-1 S9 DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make validate-surface9
  cd /home/zaks/zakops-agent-api && make validate-surface9
  cd /home/zaks/zakops-agent-api && make validate-surface9
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/ST-1-s9-determinism.txt
```

**PASS if:** all three runs pass consistently.

### ST-2: Repeated Hook Normal Runtime Stability

```bash
{
  echo "=== ST-2 HOOK NORMAL STABILITY ==="
  cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh
  cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/ST-2-hook-normal-stability.txt
```

**PASS if:** both runs complete without false failures/timeouts.

### ST-3: Repeated Hook Constrained PATH Stability

```bash
{
  echo "=== ST-3 HOOK CONSTRAINED PATH STABILITY ==="
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'timeout 35 bash /home/zaks/.claude/hooks/stop.sh'
  cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin HOME=/home/zaks bash -lc 'timeout 35 bash /home/zaks/.claude/hooks/stop.sh'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/ST-3-hook-constrained-path-stability.txt
```

**PASS if:** constrained PATH behavior remains stable across runs.

### ST-4: Governance Rule Drift Sentinel

```bash
{
  echo "=== ST-4 GOVERNANCE DRIFT SENTINEL ==="
  rg -n 'breakpoint|z-index|dark mode|animation|state management|anti-convergence|Skill Preloads' /home/zaks/zakops-agent-api/.claude/rules/design-system.md
  rg -n 'WCAG|contrast|focus|aria|semantic' /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
  rg -n 'server component|client component|loading|empty|error|suspense|state' /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/ST-4-governance-drift-sentinel.txt
```

**PASS if:** expected governance anchors remain present.

### ST-5: Forbidden Port Regression Guard

```bash
{
  echo "=== ST-5 NO PORT 8090 REGRESSION ==="
  rg -n '8090' /home/zaks/zakops-agent-api/.claude/rules/design-system.md /home/zaks/zakops-agent-api/.claude/rules/accessibility.md /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md /home/zaks/.claude/hooks/stop.sh /home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/ST-5-no-8090-regression.txt
```

**PASS if:** no forbidden 8090 references introduced.

### ST-6: New/Modified File Ownership and Line Ending Hygiene

```bash
{
  echo "=== ST-6 OWNERSHIP + LINE ENDING HYGIENE ==="
  ls -l /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
  ls -l /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
  ls -l /home/zaks/zakops-agent-api/.claude/rules/design-system.md
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh
  ls -l /home/zaks/.claude/hooks/stop.sh
  file /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
  file /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
  file /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh
  file /home/zaks/.claude/hooks/stop.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/ST-6-file-hygiene.txt
```

**PASS if:** ownership is sane and no CRLF corruption is present.

### ST-7: Forbidden File Regression Guard

```bash
{
  echo "=== ST-7 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
  cd /home/zaks/zakops-agent-api && git diff --name-only | rg 'generated\.ts$|_models\.py$|/migrations/' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-FGH-VERIFY-001/evidence/ST-7-forbidden-file-regression-guard.txt
```

**PASS if:** no forbidden-file regressions are introduced during QA remediation.

---

## 6. Remediation Protocol

When a gate fails:

1. Capture evidence path and exact failing command.
2. Classify failure:
- `MISSING_FIX`
- `REGRESSION`
- `SCOPE_GAP`
- `FALSE_POSITIVE`
- `NOT_IMPLEMENTED`
- `PARTIAL`
- `VIOLATION`
- `PATH_RESILIENCE_GAP`
- `RULE_SCOPE_GAP`

3. Apply minimal remediation aligned to `FRONTEND-GOVERNANCE-HARDENING-001` scope.
4. Re-run failed check first.
5. Re-run baseline no-regression checks:
- `cd /home/zaks/zakops-agent-api && make validate-local`
- `cd /home/zaks/zakops-agent-api && make validate-surface9`
- `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`

6. If hook/path logic was remediated, re-run both:
- VF-01.4 normal hook run
- VF-01.5 constrained PATH hook run

7. Record remediation in scorecard and QA completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Add dedicated unit tests for Gate E scanner branch and rc handling.
### ENH-2: Add CI lint that validates all `.claude/rules/*.md` include valid path frontmatter.
### ENH-3: Add rule-schema checker for required governance anchors in `design-system.md`.
### ENH-4: Add `make validate-frontend-governance` aggregate target.
### ENH-5: Add stop-hook self-test mode that emulates constrained PATH automatically.
### ENH-6: Add automated comparison report between frontend-design skill and Category B sections.
### ENH-7: Add changelog auto-insertion for governance rule updates.
### ENH-8: Add policy drift check: tooling policy vs `settings.json` live values.
### ENH-9: Add pre-commit rule preventing stale surface count labels in hook output.
### ENH-10: Add QA scaffold command for frontend-governance mission family.

---

## 8. Scorecard Template

```
QA-FGH-VERIFY-001 - Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL / NOT_EXECUTED ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (Gate E PATH Resilience): __ / 5 checks PASS
  VF-02 (New Rule Files + Scope): __ / 5 checks PASS
  VF-03 (Design-System Enrichment): __ / 5 checks PASS
  VF-04 (Surface 9 Enforcement Hardening): __ / 5 checks PASS
  VF-05 (Tooling Policy): __ / 5 checks PASS
  VF-06 (No Regression + Closure): __ / 4 checks PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 checks PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 tests PASS

Total: __ / 47 checks PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not add product features in this QA mission.
2. Do not redesign frontend architecture beyond mission AC remediation.
3. Do not weaken existing Surface 9 checks while remediating.
4. Do not bypass hook failures by broadening allow paths.
5. Do not edit generated files or migration files.
6. Keep all file paths absolute in evidence and reports.
7. Classify service/context limitations as `SKIP` with evidence, never silent PASS.
8. Preserve 14-surface contract baseline.
9. If ambiguity remains, mark `INFO` and escalate rather than forcing PASS.
10. Every PASS requires concrete evidence output.

---

## 10. Stop Condition

Stop when all 47 checks pass (or are explicitly and correctly classified as `SKIP/INFO/FALSE_POSITIVE`), required remediations are applied and re-verified, `make validate-local` remains green, and scorecard plus evidence paths are complete.

Do not declare `FULL PASS` unless Gate E resilience, frontend governance rule coverage, Surface 9 enforcement hardening, and no-regression criteria are all satisfied.

---

*End of Mission Prompt - QA-FGH-VERIFY-001*

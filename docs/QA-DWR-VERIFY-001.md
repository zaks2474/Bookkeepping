# MISSION: QA-DWR-VERIFY-001
## Independent QA Verification and Remediation - DASHBOARD-WORLDCLASS-REMEDIATION-001
## Date: 2026-02-11
## Classification: QA Verification and Remediation
## Prerequisite: `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md` execution complete
## Successor: Dashboard enhancement backlog missions only after FULL PASS

---

## Preamble: Builder Operating Context

The builder already loads project guardrails (`CLAUDE.md`, memory, hooks, deny rules, path-scoped rules). This QA mission does not restate those systems. It independently verifies that `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md` was executed correctly and that no regressions were introduced.

---

## 1. Mission Objective

This mission performs independent QA verification and minimal in-scope remediation for `DASHBOARD-WORLDCLASS-REMEDIATION-001`.

Source mission under test:
- `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md`
- Expected structure:
  - 8 phases (`Phase 0` through `Phase 7`)
  - 12 acceptance criteria (`AC-1` through `AC-12`)
  - 10 findings (`F-01` through `F-10`)

Critical expectations:
- Board view no longer fails with `currentDeals.forEach is not a function`.
- Settings export path is functional or explicit degraded behavior without runtime overlay crash.
- Onboarding follows canonical sequence and no hidden step jumps occur.
- Quarantine input state is deterministic (no ghost character persistence).
- Dashboard layout is visually aligned and refresh toasts are not noisy in auto-refresh mode.
- Ask Agent drawer and Chat IA are upgraded and coherent.
- Settings page has scroll-safe structure and explicit return navigation.
- Regression harness and validation artifacts exist.

Expected execution artifacts from source mission:
- `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md`
- `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-BASELINE.md`
- `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md`
- `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-WORLDCLASS-REMEDIATION-001.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `DASHBOARD-WORLDCLASS-REMEDIATION-001`

QA scope:
- Verify all ACs with evidence.
- Verify all 10 findings are closed with before/after proof.
- Cross-check consistency across code, tests, artifacts, and mission claims.
- Apply minimal remediation only if needed to satisfy source mission ACs.

Out of scope:
- New product feature development.
- Contract-surface expansion.
- Platform redesign outside reported dashboard findings.

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md
  rg -n '^## Phase ' /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md')
t=p.read_text()
phase_count=len(re.findall(r'^## Phase ', t, flags=re.M))
ac_count=len(re.findall(r'^### AC-', t, flags=re.M))
print('phase_count=', phase_count)
print('ac_count=', ac_count)
raise SystemExit(0 if (phase_count==8 and ac_count==12) else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** source mission exists and reports 8 phases + 12 ACs.

### PF-2: Execution Artifact Presence

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACT PRESENCE ==="
  ls -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md
  ls -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-BASELINE.md
  ls -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md
  ls -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
  ls -l /home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-WORLDCLASS-REMEDIATION-001.md
  rg -n 'DASHBOARD-WORLDCLASS-REMEDIATION-001' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/PF-2-execution-artifact-presence.txt
```

**PASS if:** all required artifacts exist and `CHANGES.md` contains mission ID.

**If FAIL:** classify as `NOT_EXECUTED` and stop gate progression.

### PF-3: Screenshot Bundle Baseline Integrity

```bash
{
  echo "=== PF-3 SCREENSHOT BUNDLE INTEGRITY ==="
  ls -lah /home/zaks/bookkeeping/docs/Dash-sreenshots-1
  find /home/zaks/bookkeeping/docs/Dash-sreenshots-1 -maxdepth 1 -type f -name '*.png' | sort
  python3 - <<'PY'
from pathlib import Path
p=Path('/home/zaks/bookkeeping/docs/Dash-sreenshots-1')
count=len(list(p.glob('*.png')))
print('png_count=', count)
raise SystemExit(0 if count==15 else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/PF-3-screenshot-bundle-integrity.txt
```

**PASS if:** bundle contains exactly 15 PNG files.

### PF-4: Validation Baseline Health

```bash
{
  echo "=== PF-4 VALIDATION BASELINE HEALTH ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/PF-4-validation-baseline-health.txt
```

**PASS if:** all commands exit 0.

### PF-5: Remediation Test Harness Presence

```bash
{
  echo "=== PF-5 REMEDIATION TEST HARNESS PRESENCE ==="
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/deals-board-shape.test.ts
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/dashboard-refresh-toast.test.tsx
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/onboarding-sequence.test.tsx
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/quarantine-input-state.test.tsx
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/settings-export-route.test.ts
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/dashboard-worldclass-remediation.spec.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/PF-5-remediation-test-harness-presence.txt
```

**PASS if:** all mission-expected tests exist.

---

## 3. Verification Families (VF)

## Verification Family 01 - Execution Evidence and AC Mapping (AC-12)

### VF-01.1: Completion Report Structure and Coverage

```bash
{
  echo "=== VF-01.1 COMPLETION STRUCTURE ==="
  wc -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
  rg -n 'F-01|F-02|F-03|F-04|F-05|F-06|F-07|F-08|F-09|F-10' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-01.1-completion-structure-coverage.txt
```

**PASS if:** all findings and all 12 ACs are traceable in completion artifact.

### VF-01.2: Baseline vs Validation Evidence Presence

```bash
{
  echo "=== VF-01.2 BASELINE VS VALIDATION EVIDENCE ==="
  head -n 120 /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-BASELINE.md
  head -n 120 /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md
  rg -n 'make validate-local|npm run type-check|npm run test|npm run test:e2e' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-01.2-baseline-validation-evidence.txt
```

**PASS if:** pre and post validation evidence is explicit and command-level.

### VF-01.3: Screenshot Index Completeness

```bash
{
  echo "=== VF-01.3 SCREENSHOT INDEX COMPLETENESS ==="
  wc -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md
  rg -n 'Screenshot 2026-02-10' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md
  rg -n 'F-01|F-02|F-03|F-04|F-05|F-06|F-07|F-08|F-09|F-10' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-01.3-screenshot-index-completeness.txt
```

**PASS if:** index includes all screenshot references and finding mappings.

### VF-01.4: Checkpoint Closure Integrity

```bash
{
  echo "=== VF-01.4 CHECKPOINT CLOSURE ==="
  tail -n 160 /home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-WORLDCLASS-REMEDIATION-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-01.4-checkpoint-closure.txt
```

**PASS if:** checkpoint states completion or clear successor handoff.

**Gate VF-01:** All 4 checks PASS.

---

## Verification Family 02 - Functional Breakers (Board + Export) (AC-1, AC-2)

### VF-02.1: Board Fix Static Verification

```bash
{
  echo "=== VF-02.1 BOARD FIX STATIC ==="
  rg -n 'currentDeals\\.forEach|Array\\.isArray|deals\\?\\.deals|forEach is not a function' /home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-02.1-board-fix-static.txt
```

**PASS if:** board implementation normalizes payload shape before iteration.

### VF-02.2: Board Regression Test Pass

```bash
{
  echo "=== VF-02.2 BOARD REGRESSION TEST ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/deals-board-shape.test.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-02.2-board-regression-test.txt
```

**PASS if:** board-shape regression test passes.

### VF-02.3: Export Path Wiring Verification

```bash
{
  echo "=== VF-02.3 EXPORT PATH WIRING ==="
  rg -n '/api/settings/data/export|Failed to export data|exportUserData' /home/zaks/zakops-agent-api/apps/dashboard/src/lib/settings/preferences-api.ts /home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/DataSection.tsx /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/data/export/route.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-02.3-export-path-wiring.txt
```

**PASS if:** export action and route are aligned and explicit error handling exists.

### VF-02.4: Export Route Regression Test Pass

```bash
{
  echo "=== VF-02.4 EXPORT ROUTE REGRESSION TEST ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/settings-export-route.test.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-02.4-export-route-regression-test.txt
```

**PASS if:** export route regression test passes.

### VF-02.5: E2E Board + Export Assertions

```bash
{
  echo "=== VF-02.5 E2E BOARD + EXPORT ASSERTIONS ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts --grep "board|export"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-02.5-e2e-board-export.txt
```

**PASS if:** E2E checks for board/export pass.

**Gate VF-02:** All 5 checks PASS.

---

## Verification Family 03 - Onboarding and Quarantine Determinism (AC-3, AC-4, AC-5)

### VF-03.1: Canonical Step Sequence Static Verification

```bash
{
  echo "=== VF-03.1 ONBOARDING SEQUENCE STATIC ==="
  rg -n \"title: 'Welcome'|title: 'Your Profile'|title: 'Connect Email'|title: 'Meet Your Agent'|title: 'Preferences'|title: 'All Set!'\" /home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-03.1-onboarding-sequence-static.txt
```

**PASS if:** canonical step set and order are present in wizard configuration.

### VF-03.2: Onboarding Sequence Regression Test

```bash
{
  echo "=== VF-03.2 ONBOARDING SEQUENCE REGRESSION TEST ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/onboarding-sequence.test.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-03.2-onboarding-sequence-test.txt
```

**PASS if:** onboarding-sequence test passes.

### VF-03.3: Quarantine Input Determinism Regression Test

```bash
{
  echo "=== VF-03.3 QUARANTINE INPUT REGRESSION TEST ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/quarantine-input-state.test.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-03.3-quarantine-input-test.txt
```

**PASS if:** quarantine input-state test passes.

### VF-03.4: Onboarding State Hook Contract Verification

```bash
{
  echo "=== VF-03.4 ONBOARDING STATE HOOK CONTRACT ==="
  rg -n 'setCurrentStep|markComplete|reset|current_step|migrateFromLocalStorage|displayStep' /home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useOnboardingState.ts /home/zaks/zakops-agent-api/apps/dashboard/src/lib/onboarding/onboarding-api.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-03.4-onboarding-hook-contract.txt
```

**PASS if:** state transitions and reset/migration logic are explicit and deterministic.

### VF-03.5: E2E Onboarding + Quarantine Assertions

```bash
{
  echo "=== VF-03.5 E2E ONBOARDING + QUARANTINE ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts --grep "onboarding|quarantine"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-03.5-e2e-onboarding-quarantine.txt
```

**PASS if:** onboarding and quarantine E2E checks pass.

**Gate VF-03:** All 5 checks PASS.

---

## Verification Family 04 - Dashboard UX Alignment and Refresh Behavior (AC-6, AC-7)

### VF-04.1: Refresh Feedback Logic Static Verification

```bash
{
  echo "=== VF-04.1 REFRESH FEEDBACK STATIC ==="
  rg -n 'toast\\.success\\(|setInterval\\(|manual|auto|isInitial|source' /home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-04.1-refresh-feedback-static.txt
```

**PASS if:** refresh feedback is source-aware and auto refresh is non-noisy.

### VF-04.2: Dashboard Refresh Toast Regression Test

```bash
{
  echo "=== VF-04.2 REFRESH TOAST REGRESSION TEST ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/dashboard-refresh-toast.test.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-04.2-refresh-toast-test.txt
```

**PASS if:** refresh toast regression test passes.

### VF-04.3: Layout Cohesion Evidence in Completion Artifact

```bash
{
  echo "=== VF-04.3 LAYOUT COHESION EVIDENCE ==="
  rg -n 'F-01|layout|height|All Deals|Execution Inbox|Quarantine' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-04.3-layout-cohesion-evidence.txt
```

**PASS if:** completion report includes explicit F-01 before/after evidence.

### VF-04.4: E2E Dashboard UX Assertions

```bash
{
  echo "=== VF-04.4 E2E DASHBOARD UX ASSERTIONS ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts --grep "dashboard|refresh|layout"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-04.4-e2e-dashboard-ux.txt
```

**PASS if:** dashboard UX E2E checks pass.

### VF-04.5: Responsive Safety Verification

```bash
{
  echo "=== VF-04.5 RESPONSIVE SAFETY ==="
  rg -n 'md:|lg:|overflow-y-auto|min-h-0|grid-cols-3|md:col-span-2' /home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/ExecutionInbox.tsx /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AgentActivityWidget.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-04.5-responsive-safety.txt
```

**PASS if:** responsive layout controls are present and consistent.

**Gate VF-04:** All 5 checks PASS.

---

## Verification Family 05 - Ask Agent and Chat IA Hardening (AC-8, AC-9)

### VF-05.1: Ask Agent Drawer UX Contract

```bash
{
  echo "=== VF-05.1 ASK AGENT DRAWER UX CONTRACT ==="
  rg -n 'Ask Agent|SheetContent|Input|Send|SuggestionButton|Context:' /home/zaks/zakops-agent-api/apps/dashboard/src/components/agent/AgentDrawer.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-05.1-ask-agent-drawer-contract.txt
```

**PASS if:** drawer contains clear composer and coherent interaction primitives.

### VF-05.2: Chat History / Session Recall Contract

```bash
{
  echo "=== VF-05.2 CHAT HISTORY SESSION RECALL ==="
  rg -n 'sessionId|restoreSession|getChatSession|Session:|New Chat|loadSession|saveSession' /home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-05.2-chat-history-session-recall.txt
```

**PASS if:** session/history recall behavior is explicit in chat implementation.

### VF-05.3: Provider Selector UX Contract

```bash
{
  echo "=== VF-05.3 PROVIDER SELECTOR UX CONTRACT ==="
  rg -n 'ProviderSelector|Local vLLM|OpenAI|Anthropic|connected|offline|settings' /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ProviderSelector.tsx /home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-05.3-provider-selector-contract.txt
```

**PASS if:** provider status and selection affordances are explicit and usable.

### VF-05.4: Shared Drawer/Chat State E2E

```bash
{
  echo "=== VF-05.4 SHARED DRAWER CHAT STATE E2E ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts --grep "drawer|chat|shared state|Ask Agent"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-05.4-shared-drawer-chat-e2e.txt
```

**PASS if:** shared-state E2E checks pass.

### VF-05.5: Completion Evidence for F-02 and F-06

```bash
{
  echo "=== VF-05.5 COMPLETION EVIDENCE F-02 F-06 ==="
  rg -n 'F-02|F-06|Ask Agent|Chat|history|provider|before|after' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-05.5-completion-evidence-f02-f06.txt
```

**PASS if:** completion report provides explicit closure evidence for chat/drawer findings.

**Gate VF-05:** All 5 checks PASS.

---

## Verification Family 06 - Settings and Setup Cohesion (AC-10)

### VF-06.1: Settings Scroll and Shell Integrity

```bash
{
  echo "=== VF-06.1 SETTINGS SCROLL SHELL INTEGRITY ==="
  rg -n 'container|max-w|overflow|flex|min-h-0|SettingsNav' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx /home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-06.1-settings-scroll-shell-integrity.txt
```

**PASS if:** settings shell and section navigation support deterministic scrolling.

### VF-06.2: Return Navigation Presence

```bash
{
  echo "=== VF-06.2 SETTINGS RETURN NAVIGATION ==="
  rg -n 'Back|Return|Dashboard|href=.*/dashboard|router\\.push\\(.*/dashboard' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx /home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-06.2-settings-return-navigation.txt
```

**PASS if:** explicit return navigation affordance is present.

### VF-06.3: E2E Settings Cohesion Checks

```bash
{
  echo "=== VF-06.3 E2E SETTINGS COHESION ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts --grep "settings|navigation|scroll"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-06.3-e2e-settings-cohesion.txt
```

**PASS if:** settings cohesion E2E checks pass.

### VF-06.4: Completion Evidence for F-09 and F-10

```bash
{
  echo "=== VF-06.4 COMPLETION EVIDENCE F-09 F-10 ==="
  rg -n 'F-09|F-10|settings|setup|scroll|navigation|before|after' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-06.4-completion-evidence-f09-f10.txt
```

**PASS if:** completion report shows explicit closure of settings/setup findings.

**Gate VF-06:** All 4 checks PASS.

---

## Verification Family 07 - No Regression and Closure Discipline (AC-11, AC-12)

### VF-07.1: Full Validation Pass

```bash
{
  echo "=== VF-07.1 FULL VALIDATION PASS ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-07.1-full-validation-pass.txt
```

**PASS if:** all required validation commands pass.

### VF-07.2: Forbidden File Regression Guard

```bash
{
  echo "=== VF-07.2 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
  cd /home/zaks/zakops-agent-api && git diff --name-only | rg 'generated\\.ts$|_models\\.py$|/migrations/' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-07.2-forbidden-file-regression-guard.txt
```

**PASS if:** no forbidden-file edits are introduced by QA remediation.

### VF-07.3: Bookkeeping Closure Integrity

```bash
{
  echo "=== VF-07.3 BOOKKEEPING CLOSURE ==="
  rg -n 'DASHBOARD-WORLDCLASS-REMEDIATION-001|QA-DWR-VERIFY-001|successor|handoff' /home/zaks/bookkeeping/CHANGES.md /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md /home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-WORLDCLASS-REMEDIATION-001.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-07.3-bookkeeping-closure.txt
```

**PASS if:** closure and QA handoff are discoverable in artifacts.

### VF-07.4: QA Evidence Completeness

```bash
{
  echo "=== VF-07.4 QA EVIDENCE COMPLETENESS ==="
  find /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence -maxdepth 1 -type f | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/VF-07.4-qa-evidence-completeness.txt
```

**PASS if:** evidence files exist for all executed PF/VF/XC/ST checks.

**Gate VF-07:** All 4 checks PASS.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Source AC Set vs Completion AC Claims

```bash
{
  echo "=== XC-1 AC SET RECONCILIATION ==="
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/XC-1-ac-set-reconciliation.txt
```

**PASS if:** completion AC claims align exactly with source AC set.

### XC-2: Finding Reconciliation Table Integrity

```bash
{
  echo "=== XC-2 FINDING RECONCILIATION INTEGRITY ==="
  rg -n 'F-01|F-02|F-03|F-04|F-05|F-06|F-07|F-08|F-09|F-10|Before|After|Status|Evidence' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/XC-2-finding-reconciliation-integrity.txt
```

**PASS if:** completion artifact reconciles all findings with evidence.

### XC-3: Test Matrix vs Mission File-Create Contract

```bash
{
  echo "=== XC-3 TEST MATRIX VS FILE-CREATE CONTRACT ==="
  rg -n 'deals-board-shape\\.test\\.ts|dashboard-refresh-toast\\.test\\.tsx|onboarding-sequence\\.test\\.tsx|quarantine-input-state\\.test\\.tsx|settings-export-route\\.test\\.ts|dashboard-worldclass-remediation\\.spec\\.ts' /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-WORLDCLASS-REMEDIATION-001.md
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/deals-board-shape.test.ts
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/dashboard-refresh-toast.test.tsx
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/onboarding-sequence.test.tsx
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/quarantine-input-state.test.tsx
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/settings-export-route.test.ts
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/dashboard-worldclass-remediation.spec.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/XC-3-test-matrix-vs-contract.txt
```

**PASS if:** all mission-declared test artifacts exist.

### XC-4: Screenshot Source vs Index vs Completion

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/XC-4-screenshot-source-index-completion.txt
from pathlib import Path
import re
src=Path('/home/zaks/bookkeeping/docs/Dash-sreenshots-1')
idx=Path('/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md').read_text()
cmp=Path('/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md').read_text()
pngs=sorted([p.name for p in src.glob('*.png')])
print('source_png_count=', len(pngs))
ok=True
for n in pngs:
    in_idx=n in idx
    in_cmp=n in cmp
    print(f'{n}: index={"PASS" if in_idx else "FAIL"} completion={"PASS" if in_cmp else "FAIL"}')
    if not in_idx:
        ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** every source screenshot appears in index (and expected subset appears in completion evidence references).

### XC-5: Validation Log Consistency

```bash
{
  echo "=== XC-5 VALIDATION LOG CONSISTENCY ==="
  rg -n 'make validate-local|npm run type-check|npm run test|npm run test:e2e' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md
  rg -n 'PASS|FAIL|exit 0|exit 1' /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/XC-5-validation-log-consistency.txt
```

**PASS if:** validation artifact consistently reflects executed command outcomes.

### XC-6: AC-to-VF Coverage Completeness

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/XC-6-ac-to-vf-coverage.txt
ac_to_vf={
 'AC-1':'VF-02',
 'AC-2':'VF-02',
 'AC-3':'VF-03',
 'AC-4':'VF-03',
 'AC-5':'VF-03',
 'AC-6':'VF-04',
 'AC-7':'VF-04',
 'AC-8':'VF-05',
 'AC-9':'VF-05',
 'AC-10':'VF-06',
 'AC-11':'VF-07',
 'AC-12':'VF-01/VF-07',
}
for ac,vf in ac_to_vf.items():
    print(f'{ac} -> {vf}')
print('ac_count=', len(ac_to_vf))
raise SystemExit(0 if len(ac_to_vf)==12 else 1)
PY
```

**PASS if:** all 12 ACs are explicitly mapped to verification families.

---

## 5. Stress Tests (ST)

### ST-1: Board Determinism Across Repeated Runs

```bash
{
  echo "=== ST-1 BOARD DETERMINISM ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/deals-board-shape.test.ts
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/deals-board-shape.test.ts
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/deals-board-shape.test.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/ST-1-board-determinism.txt
```

**PASS if:** all three runs pass consistently.

### ST-2: Onboarding Sequence Determinism Across Repeated Runs

```bash
{
  echo "=== ST-2 ONBOARDING DETERMINISM ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/onboarding-sequence.test.tsx
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/onboarding-sequence.test.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/ST-2-onboarding-determinism.txt
```

**PASS if:** repeated runs remain stable.

### ST-3: Quarantine Input Determinism Across Repeated Runs

```bash
{
  echo "=== ST-3 QUARANTINE INPUT DETERMINISM ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/quarantine-input-state.test.tsx
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/quarantine-input-state.test.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/ST-3-quarantine-input-determinism.txt
```

**PASS if:** repeated runs remain stable.

### ST-4: Refresh Toast Behavior Stability

```bash
{
  echo "=== ST-4 REFRESH TOAST STABILITY ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/dashboard-refresh-toast.test.tsx
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- src/__tests__/dashboard-refresh-toast.test.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/ST-4-refresh-toast-stability.txt
```

**PASS if:** refresh-toast tests pass repeatedly.

### ST-5: E2E Mission Spec Stability

```bash
{
  echo "=== ST-5 E2E MISSION SPEC STABILITY ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e -- tests/e2e/dashboard-worldclass-remediation.spec.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/ST-5-e2e-mission-spec-stability.txt
```

**PASS if:** mission E2E spec passes consistently across repeated runs.

### ST-6: Full Validation Re-run Stability

```bash
{
  echo "=== ST-6 FULL VALIDATION RERUN STABILITY ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/ST-6-full-validation-rerun-stability.txt
```

**PASS if:** no drift appears on immediate re-run.

### ST-7: Artifact Integrity Under Re-audit

```bash
{
  echo "=== ST-7 ARTIFACT INTEGRITY UNDER RE-AUDIT ==="
  wc -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
  wc -l /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md
  sha256sum /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md
  sha256sum /home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-DWR-VERIFY-001/evidence/ST-7-artifact-integrity-reraudit.txt
```

**PASS if:** artifacts are stable and not unexpectedly changing during QA.

---

## 6. Remediation Protocol

When any PF/VF/XC/ST check fails:

1. Capture and read the failing evidence file.
2. Classify failure:
   - `MISSING_FIX`
   - `REGRESSION`
   - `SCOPE_GAP`
   - `FALSE_POSITIVE`
   - `NOT_IMPLEMENTED`
   - `PARTIAL`
   - `VIOLATION`
3. Apply minimal remediation in source code only where required.
4. Re-run the failed check and corresponding family gate.
5. Re-run:
   - `cd /home/zaks/zakops-agent-api && make validate-local`
   - `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check`
6. Record remediation in QA completion report with:
   - failure classification
   - file paths changed
   - before/after evidence references

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Visual Regression Snapshots
Add deterministic screenshot regression checks for dashboard layout symmetry and drawer/chat surfaces.

### ENH-2: AC-to-Test Manifest Generator
Auto-generate AC coverage matrix from mission + test filenames.

### ENH-3: Structured Completion Schema
Use JSON schema for completion reports to enforce finding and AC reconciliation fields.

### ENH-4: Toast Policy Lint
Add lint rule for manual-only success toasts in polling contexts.

### ENH-5: Onboarding Flow Invariant Checker
Add static check that step IDs and progression transitions remain canonical.

### ENH-6: Input State Fuzz Test
Add fuzz-style UI state test for controlled inputs under delete/refresh cycles.

### ENH-7: Settings Navigation Contract Test
Add reusable test helper for explicit return-path presence on settings-like pages.

### ENH-8: Drawer-Chat Contract Surface
Formalize drawer/chat shared-state behavior as a dedicated frontend contract check.

### ENH-9: QA Evidence Index Generator
Auto-build evidence index file from `evidence/` directory and expected gate list.

### ENH-10: Mission Drift Checker
Script that verifies source mission file-path contract entries were created as promised.

---

## 8. Scorecard Template

```text
QA-DWR-VERIFY-001 - Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (Execution Evidence): __ / 4 PASS
  VF-02 (Functional Breakers): __ / 5 PASS
  VF-03 (Onboarding + Quarantine): __ / 5 PASS
  VF-04 (Dashboard UX + Refresh): __ / 5 PASS
  VF-05 (Ask Agent + Chat IA): __ / 5 PASS
  VF-06 (Settings Cohesion): __ / 4 PASS
  VF-07 (No Regression + Closure): __ / 4 PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 PASS

Total: __ / 45 PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not build new features under this QA mission.
2. Remediate minimally; do not redesign unrelated systems.
3. Every PASS must be evidence-backed (`tee` output file).
4. If services are unavailable, mark live gates `INFO` with explicit reason, not silent PASS.
5. Preserve existing governance and contract-surface baselines.
6. Do not edit generated files or migrations.
7. Keep remediation changes scoped to mission findings.
8. Re-run `make validate-local` and dashboard type-check after every remediation.
9. Distinguish `FAIL` from `ENHANCEMENT`; do not mix them.
10. Keep QA artifact paths deterministic under `qa-verifications/QA-DWR-VERIFY-001/`.

---

## 10. Stop Condition

Stop when all required PF, VF, XC, and ST checks pass (or are explicitly classified as `INFO` with valid justification), all needed remediations are applied and re-verified, `make validate-local` passes, dashboard type-check passes, and the scorecard is fully completed.

If any finding `F-01` through `F-10` remains unresolved in evidence, mission verdict cannot be `FULL PASS`.

---
*End of Mission Prompt - QA-DWR-VERIFY-001*

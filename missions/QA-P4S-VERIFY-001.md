# MISSION: QA-P4S-VERIFY-001
## Independent QA Verification and Remediation — DASHBOARD-P4-STABILIZE-001
## Date: 2026-02-12
## Classification: QA Verification and Remediation
## Prerequisite: /home/zaks/bookkeeping/missions/DASHBOARD-P4-STABILIZE-001.md execution complete
## Successor: None (terminal QA for this stabilization cycle)

---

## Preamble: Builder Operating Context

This is an independent QA mission. It verifies implementation quality for DASHBOARD-P4-STABILIZE-001 (15 findings across 7 phases) and applies surgical remediation only if a gate fails. The builder already loads CLAUDE.md, MEMORY.md, hooks, rules, and deny rules. This prompt references standing rules by name — it does not repeat them.

---

## 1. Mission Objective

Verify, cross-check, stress-test, and remediate execution results for:
- `/home/zaks/bookkeeping/missions/DASHBOARD-P4-STABILIZE-001.md`

Expected source shape:
- 7 phases (`Phase 0` through `Phase 6`)
- 9 acceptance criteria (`AC-1` through `AC-9`)
- 15 findings (`F-1` through `F-15`)

Expected execution artifacts:
- `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/baseline-validation.txt`
- `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/findings-verification.md`
- `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/remediation-log.md`
- `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `DASHBOARD-P4-STABILIZE-001`

Scope:
- Verify all 15 finding remediations (F-1 through F-15) against current source code
- Confirm all 9 ACs pass with independent evidence
- Browser-verify critical UI changes (chat history, dashboard, settings, board)
- Stress-test edge cases: deal ID security, cache behavior, proxy routing, scroll behavior
- Confirm no regressions to M-04 through M-12 responsive/accessibility work

Out of scope:
- Backend Python code changes
- New feature development
- Generated file modifications
- Database or migration changes

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/missions/DASHBOARD-P4-STABILIZE-001.md
  rg -n '^## Phase [0-9]+' /home/zaks/bookkeeping/missions/DASHBOARD-P4-STABILIZE-001.md
  rg -n '^### AC-[0-9]+:' /home/zaks/bookkeeping/missions/DASHBOARD-P4-STABILIZE-001.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/missions/DASHBOARD-P4-STABILIZE-001.md')
t=p.read_text()
phase_count=len(re.findall(r'^## Phase [0-9]+', t, flags=re.M))
ac_count=len(re.findall(r'^### AC-[0-9]+:', t, flags=re.M))
finding_count=len(re.findall(r'\| F-\d+', t))
print('phase_count=', phase_count)
print('ac_count=', ac_count)
print('finding_count=', finding_count)
raise SystemExit(0 if (phase_count==7 and ac_count==9) else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** source mission reports 7 phases and 9 ACs.

### PF-2: Execution Artifact Presence

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACTS ==="
  for f in baseline-validation.txt findings-verification.md remediation-log.md completion-summary.md; do
    ls -l "/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/$f"
  done
  rg -n 'DASHBOARD-P4-STABILIZE-001' /home/zaks/bookkeeping/CHANGES.md | head -5
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/PF-2-execution-artifacts.txt
```

**PASS if:** all 4 artifact files exist and CHANGES.md includes mission ID.

### PF-3: Baseline Validation

```bash
{
  echo "=== PF-3 BASELINE VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-local
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/PF-3-baseline-validation.txt
```

**PASS if:** `make validate-local` exits 0. If not, stop — codebase is broken before QA starts.

### PF-4: TypeScript Compilation

```bash
{
  echo "=== PF-4 TYPESCRIPT COMPILATION ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
  echo "EXIT_CODE=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/PF-4-typescript-compilation.txt
```

**PASS if:** `tsc --noEmit` exits 0.

### PF-5: Dashboard Running

```bash
{
  echo "=== PF-5 DASHBOARD RUNNING ==="
  curl -sf http://localhost:3003/ -o /dev/null && echo "DASHBOARD=UP" || echo "DASHBOARD=DOWN"
  curl -sf http://localhost:8091/health -o /dev/null && echo "BACKEND=UP" || echo "BACKEND=DOWN"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/PF-5-dashboard-running.txt
```

**PASS if:** Dashboard is UP. Backend UP is preferred but not blocking — live verification gates become code-only if backend is down.

### PF-6: E2E Test Suite Baseline

```bash
{
  echo "=== PF-6 E2E TEST SUITE ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test tests/e2e/smoke.spec.ts --reporter=line 2>&1
  echo "EXIT_CODE=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/PF-6-e2e-baseline.txt
```

**PASS if:** smoke test exits 0.

---

## 3. Verification Families (VF)

## Verification Family 01 — Chat Page Fixes (F-1, F-2, F-3 → AC-1, AC-2)

### VF-01.1: F-1 — No nested button in ChatHistoryRail

```bash
{
  echo "=== VF-01.1 NO NESTED BUTTON ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx"
  echo "--- Checking outer element is div role=button, not <button> ---"
  rg -n 'role=.button.' "$FILE"
  rg -n 'tabIndex=' "$FILE"
  rg -n 'onKeyDown=' "$FILE"
  echo "--- Ensuring no raw <button> wrapping session items ---"
  OUTER_BUTTONS=$(rg -c '<button' "$FILE" 2>/dev/null) || OUTER_BUTTONS=0
  echo "outer_button_count=$OUTER_BUTTONS"
  echo "--- Inner <Button> (shadcn) for delete should remain ---"
  rg -n '<Button' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-01.1-no-nested-button.txt
```

**PASS if:** outer element uses `role="button"` with `tabIndex` and `onKeyDown`; no raw `<button` wrapping session items; inner `<Button` (shadcn) remains for delete.

### VF-01.2: F-2 — History dedup guard

```bash
{
  echo "=== VF-01.2 HISTORY DEDUP GUARD ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx"
  echo "--- Checking sessionId guard before archiveCurrentSession ---"
  rg -n 'archivedSessionId.*!==.*sessionId|sessionId.*!==.*archivedSessionId' "$FILE"
  echo "--- Checking archiveCurrentSession is conditional ---"
  rg -n -A2 'handleLoadFromHistory' "$FILE" | rg -v '^--$'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-01.2-history-dedup-guard.txt
```

**PASS if:** `archiveCurrentSession()` call is guarded by session ID comparison.

### VF-01.3: F-3 — Visible border separation

```bash
{
  echo "=== VF-01.3 VISIBLE BORDER SEPARATION ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx"
  echo "--- Checking for visible border class (not border-transparent) ---"
  rg -n 'border-border' "$FILE"
  echo "--- Ensuring border-transparent is removed ---"
  TRANSPARENT=$(rg -c 'border-transparent' "$FILE" 2>/dev/null) || TRANSPARENT=0
  echo "border_transparent_count=$TRANSPARENT"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-01.3-visible-border.txt
```

**PASS if:** `border-border` class present; `border-transparent` count is 0.

### VF-01.4: F-1 Browser Verification — Zero hydration errors on /chat

Open `/chat` in Playwright, collect console errors, verify 0 hydration-related errors.

**PASS if:** No console errors containing "hydration" or "nested" on /chat page load.
**Note:** This is a browser-based check. If dashboard is down per PF-5, mark as SKIP with justification.

**Gate VF-01:** All 4 checks PASS. Chat page has no nested buttons, dedup guard active, visible borders, zero hydration errors.

---

## Verification Family 02 — Performance Stabilization (F-4, F-5, F-6 → AC-3)

### VF-02.1: F-4 — Global staleTime reduced

```bash
{
  echo "=== VF-02.1 STALETIME REDUCED ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx"
  rg -n 'staleTime' "$FILE"
  echo "--- Checking value is <= 60s ---"
  python3 - <<'PY'
import re
from pathlib import Path
t=Path('/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx').read_text()
m=re.search(r'staleTime:\s*(\d[\d\s*]+)', t)
if m:
    expr=m.group(1).strip()
    print(f'staleTime_expr={expr}')
    val=eval(expr)
    print(f'staleTime_ms={val}')
    raise SystemExit(0 if val <= 60000 else 1)
else:
    print('NO_STALETIME_FOUND')
    raise SystemExit(1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-02.1-staletime-reduced.txt
```

**PASS if:** staleTime is <= 60000ms (60 seconds).

### VF-02.2: F-4 — refetchOnMount enabled

```bash
{
  echo "=== VF-02.2 REFETCH ON MOUNT ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx"
  rg -n 'refetchOnMount' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-02.2-refetch-on-mount.txt
```

**PASS if:** `refetchOnMount` is `true` (not `false`).

### VF-02.3: F-5 — No double proxy (rewrites removed)

```bash
{
  echo "=== VF-02.3 NO DOUBLE PROXY ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/next.config.ts"
  echo "--- Checking rewrites function is removed ---"
  REWRITE_COUNT=$(rg -c 'rewrites\(\)|async rewrites' "$FILE" 2>/dev/null) || REWRITE_COUNT=0
  echo "rewrite_function_count=$REWRITE_COUNT"
  echo "--- Checking for explanatory comment ---"
  rg -n 'middleware.ts|double.proxy' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-02.3-no-double-proxy.txt
```

**PASS if:** `rewrite_function_count=0`; middleware handles all `/api/*` routing.

### VF-02.4: F-6 — Timeout values aligned

```bash
{
  echo "=== VF-02.4 TIMEOUT ALIGNED ==="
  echo "--- middleware.ts timeout ---"
  rg -n 'PROXY_TIMEOUT_MS' /home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts
  echo "--- backend-fetch.ts timeout ---"
  rg -n 'PROXY_TIMEOUT_MS' /home/zaks/zakops-agent-api/apps/dashboard/src/lib/backend-fetch.ts
  echo "--- Both should default to 15000 ---"
  python3 - <<'PY'
import re
from pathlib import Path
mw=Path('/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts').read_text()
bf=Path('/home/zaks/zakops-agent-api/apps/dashboard/src/lib/backend-fetch.ts').read_text()
mw_default=re.search(r"PROXY_TIMEOUT_MS\s*\|\|\s*'(\d+)'", mw)
bf_default=re.search(r"PROXY_TIMEOUT_MS\s*\|\|\s*'(\d+)'", bf)
mw_val=mw_default.group(1) if mw_default else 'NOT_FOUND'
bf_val=bf_default.group(1) if bf_default else 'NOT_FOUND'
print(f'middleware_default={mw_val}')
print(f'backend_fetch_default={bf_val}')
print(f'aligned={mw_val == bf_val}')
raise SystemExit(0 if mw_val == bf_val else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-02.4-timeout-aligned.txt
```

**PASS if:** Both files default to the same timeout value.

**Gate VF-02:** All 4 checks PASS. Global staleTime reduced, refetchOnMount enabled, single proxy path, timeouts aligned.

---

## Verification Family 03 — Dashboard Data & Layout (F-7 through F-11 → AC-4, AC-5)

### VF-03.1: F-7 — Deal ID regex accepts alphanumeric

```bash
{
  echo "=== VF-03.1 DEAL ID REGEX ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx"
  rg -n 'isValidDealId|DL-' "$FILE"
  echo "--- Verify regex accepts alphanumeric ---"
  python3 - <<'PY'
import re
from pathlib import Path
t=Path('/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx').read_text()
m=re.search(r'\/\^DL-(.+?)\$\/', t)
if m:
    pattern=m.group(1)
    print(f'regex_suffix_pattern={pattern}')
    accepts_alpha='A-Z' in pattern or 'a-z' in pattern or 'A-Za-z' in pattern
    print(f'accepts_alpha={accepts_alpha}')
    raise SystemExit(0 if accepts_alpha else 1)
else:
    print('NO_DL_REGEX_FOUND')
    raise SystemExit(1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-03.1-deal-id-regex.txt
```

**PASS if:** regex pattern includes alphabetic characters (accepts `DL-IDEM2`).

### VF-03.2: F-7 — Security: rejects special characters

```bash
{
  echo "=== VF-03.2 DEAL ID SECURITY ==="
  python3 - <<'PY'
import re
# Replicate the isValidDealId logic
def is_valid(id_str):
    reserved = {'new','global','edit','bulk'}
    if id_str.lower() in reserved: return False
    if re.match(r'^DL-[A-Za-z0-9]+$', id_str, re.I): return True
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', id_str, re.I): return True
    return False

tests = [
    ('DL-0086', True),
    ('DL-IDEM2', True),
    ('DL-abc123', True),
    ("DL-'; DROP TABLE deals;--", False),
    ('DL-../../../etc/passwd', False),
    ('DL-<script>alert(1)</script>', False),
    ('DL-foo bar', False),
    ('DL-', False),
    ('new', False),
]
all_pass = True
for id_str, expected in tests:
    result = is_valid(id_str)
    status = 'OK' if result == expected else 'FAIL'
    if result != expected: all_pass = False
    print(f'{status}: is_valid("{id_str}") = {result} (expected {expected})')
raise SystemExit(0 if all_pass else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-03.2-deal-id-security.txt
```

**PASS if:** All test cases match expected results (alphanumeric accepted, special chars rejected).

### VF-03.3: F-8 — Server-side deal count

```bash
{
  echo "=== VF-03.3 SERVER SIDE DEAL COUNT ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx"
  echo "--- All Deals description should NOT use filteredDeals.length ---"
  CLIENTSIDE=$(rg -c 'filteredDeals\.length.*deal' "$FILE" 2>/dev/null) || CLIENTSIDE=0
  echo "client_side_length_in_description=$CLIENTSIDE"
  echo "--- Should use pipelineData or stageCounts ---"
  rg -n 'pipelineData\?\.total_active|stageCounts\[' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-03.3-server-side-count.txt
```

**PASS if:** `filteredDeals.length` is NOT used in deal count description text; `pipelineData?.total_active` or `stageCounts` is used instead.

### VF-03.4: F-9 — Viewport-relative ScrollArea height

```bash
{
  echo "=== VF-03.4 VIEWPORT RELATIVE HEIGHT ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx"
  echo "--- Checking max-h-[500px] is removed ---"
  FIXED=$(rg -c 'max-h-\[500px\]' "$FILE" 2>/dev/null) || FIXED=0
  echo "fixed_500px_count=$FIXED"
  echo "--- Checking viewport-relative height ---"
  rg -n 'max-h-\[.*vh\]|max-h-screen' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-03.4-viewport-relative-height.txt
```

**PASS if:** `max-h-[500px]` count is 0; viewport-relative class (e.g., `vh`) is present.

### VF-03.5: F-10 — No "0 stages" on pipeline failure

```bash
{
  echo "=== VF-03.5 PIPELINE DEGRADATION ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx"
  echo "--- Check pipeline description handles null pipelineData ---"
  rg -n 'pipelineData\s*\?' "$FILE" | head -5
  echo "--- Should not hardcode '0 stages' ---"
  ZERO_STAGES=$(rg -c "0 stages" "$FILE" 2>/dev/null) || ZERO_STAGES=0
  echo "hardcoded_zero_stages=$ZERO_STAGES"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-03.5-pipeline-degradation.txt
```

**PASS if:** `hardcoded_zero_stages=0`; pipeline description conditionally shows stage count.

### VF-03.6: F-11 — Alert cards clickable

```bash
{
  echo "=== VF-03.6 ALERT CARDS CLICKABLE ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx"
  echo "--- Check alerts have Link wrapper ---"
  rg -n 'alert\.deal_id' "$FILE"
  rg -n 'Link.*href.*deals' "$FILE" | rg -i 'alert'
  echo "--- Check cursor-pointer on alert cards ---"
  rg -n 'cursor-pointer' "$FILE" | rg -i 'alert\|deal_id'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-03.6-alert-clickable.txt
```

**PASS if:** Alerts with `deal_id` are wrapped in `Link` with navigation and `cursor-pointer`.

**Gate VF-03:** All 6 checks PASS. Deal IDs are secure and alphanumeric-friendly, counts use server data, height is viewport-relative, pipeline handles degradation, alerts are clickable.

---

## Verification Family 04 — Board View Interactivity (F-12, F-13 → AC-5)

### VF-04.1: F-12 — DealCard has Link navigation

```bash
{
  echo "=== VF-04.1 DEALCARD LINK NAVIGATION ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx"
  echo "--- Check Link import ---"
  rg -n "import Link from 'next/link'" "$FILE"
  echo "--- Check Link wrapper in DealCard ---"
  rg -n 'Link.*href.*deals' "$FILE"
  echo "--- Drag handle should remain separate ---"
  rg -n 'dragHandleProps' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-04.1-dealcard-link.txt
```

**PASS if:** `Link` imported, `<Link href="/deals/...">` wraps card content, drag handle props remain separate.

### VF-04.2: F-13 — Drag-and-drop confirmation

```bash
{
  echo "=== VF-04.2 DRAG CONFIRMATION ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx"
  echo "--- Check window.confirm in handleDragEnd ---"
  rg -n 'window\.confirm' "$FILE"
  rg -n 'DEAL_STAGE_LABELS' "$FILE"
  echo "--- Confirmation should show deal name and stage labels ---"
  rg -n 'dealName\|fromLabel\|toLabel' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-04.2-drag-confirmation.txt
```

**PASS if:** `window.confirm` is called before transition; dialog shows deal name and human-readable stage labels.

**Gate VF-04:** All 2 checks PASS. Board cards navigate on click, drag requires confirmation.

---

## Verification Family 05 — Settings Page (F-14, F-15 → AC-6)

### VF-05.1: F-14 — Header outside scroll area

```bash
{
  echo "=== VF-05.1 HEADER OUTSIDE SCROLL ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx"
  echo "--- Check for fixed header + scrollable content split ---"
  rg -n 'Fixed header|Scrollable content|overflow-y-auto' "$FILE"
  echo "--- Back arrow should be in the fixed header div, not the scrollable area ---"
  rg -n -B2 'Back to Dashboard' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-05.1-header-outside-scroll.txt
```

**PASS if:** Layout split into fixed header (with back arrow) and scrollable content. `overflow-y-auto` is on the content div, not the root div.

### VF-05.2: F-15 — Nav visual container

```bash
{
  echo "=== VF-05.2 NAV VISUAL CONTAINER ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx"
  echo "--- Check for border/card styling on nav container ---"
  rg -n 'border.*border-border\|bg-card\|rounded-lg' "$FILE"
  echo "--- Verify sticky container has visual boundary ---"
  rg -n 'sticky.*border\|border.*sticky' "$FILE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-05.2-nav-visual-container.txt
```

**PASS if:** Nav container has visible border/background styling (e.g., `border-border`, `bg-card`).

### VF-05.3: F-14/F-15 — Settings responsive check (375/768/1280px)

Browser-verify that settings page renders correctly at all 3 breakpoints. Open `/settings`, resize to 375px, 768px, 1280px. Check: nav visible/dropdown, sections scroll, back arrow accessible.

**PASS if:** No layout breakage at any breakpoint. Nav switches to dropdown on mobile.
**Note:** Browser-based check. If dashboard is down per PF-5, mark as SKIP.

**Gate VF-05:** All 3 checks PASS. Settings header is fixed, nav has container, responsive layout intact.

---

## Verification Family 06 — Tests & Validation (AC-7, AC-8, AC-9)

### VF-06.1: E2E regression suite passes

```bash
{
  echo "=== VF-06.1 E2E REGRESSION SUITE ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test tests/e2e/smoke.spec.ts tests/e2e/responsive-regression.spec.ts tests/e2e/cross-page-integration-flows.spec.ts --reporter=line 2>&1
  echo "EXIT_CODE=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-06.1-e2e-regression.txt
```

**PASS if:** All E2E tests pass (exit 0).

### VF-06.2: Contract surfaces pass

```bash
{
  echo "=== VF-06.2 CONTRACT SURFACES ==="
  cd /home/zaks/zakops-agent-api && make validate-local
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-06.2-contract-surfaces.txt
```

**PASS if:** `make validate-local` exits 0 (14/14 surfaces).

### VF-06.3: Completion summary covers all ACs

```bash
{
  echo "=== VF-06.3 COMPLETION SUMMARY AC COVERAGE ==="
  FILE="/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md"
  for ac in AC-1 AC-2 AC-3 AC-4 AC-5 AC-6 AC-7 AC-8 AC-9; do
    HIT=$(rg -c "$ac" "$FILE" 2>/dev/null) || HIT=0
    echo "$ac: count=$HIT"
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-06.3-completion-ac-coverage.txt
```

**PASS if:** All 9 ACs appear in the completion summary.

### VF-06.4: CHANGES.md entry completeness

```bash
{
  echo "=== VF-06.4 CHANGES ENTRY ==="
  rg -n 'DASHBOARD-P4-STABILIZE-001' /home/zaks/bookkeeping/CHANGES.md
  rg -n 'F-1\|F-7\|F-12\|F-15' /home/zaks/bookkeeping/CHANGES.md | head -10
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/VF-06.4-changes-entry.txt
```

**PASS if:** CHANGES.md has dated entry mentioning mission ID and key findings.

**Gate VF-06:** All 4 checks PASS. E2E green, surfaces green, completion report complete, CHANGES updated.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Remediation log ↔ source code agreement

```bash
{
  echo "=== XC-1 REMEDIATION LOG VS SOURCE CODE ==="
  echo "--- F-1: remediation-log says div role=button. Verify: ---"
  rg -c 'role=.button.' /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx
  echo "--- F-5: remediation-log says rewrites removed. Verify: ---"
  REWRITE=$(rg -c 'async rewrites' /home/zaks/zakops-agent-api/apps/dashboard/next.config.ts 2>/dev/null) || REWRITE=0
  echo "rewrite_count=$REWRITE"
  echo "--- F-7: remediation-log says A-Za-z0-9. Verify: ---"
  rg 'A-Za-z0-9' /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx
  echo "--- F-12: remediation-log says Link wrapper. Verify: ---"
  rg -c "import Link from 'next/link'" /home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/XC-1-remediation-vs-code.txt
```

**PASS if:** All remediation claims match current source code.

### XC-2: Completion summary ↔ remediation log agreement

```bash
{
  echo "=== XC-2 COMPLETION VS REMEDIATION LOG ==="
  COMPLETION="/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md"
  REMEDIATION="/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/remediation-log.md"
  echo "--- Files modified count ---"
  rg -c 'ChatHistoryRail\|providers\.tsx\|middleware\.ts\|next\.config\|DealBoard\|SettingsNav\|settings/page\|dashboard/page\|deals/\[id\]' "$COMPLETION"
  rg -c 'ChatHistoryRail\|providers\.tsx\|middleware\.ts\|next\.config\|DealBoard\|SettingsNav\|settings/page\|dashboard/page\|deals/\[id\]' "$REMEDIATION"
  echo "--- Both should mention all 15 findings ---"
  for f in F-1 F-2 F-3 F-4 F-5 F-6 F-7 F-8 F-9 F-10 F-11 F-12 F-13 F-14 F-15; do
    C_HIT=$(rg -c "$f" "$COMPLETION" 2>/dev/null) || C_HIT=0
    R_HIT=$(rg -c "$f" "$REMEDIATION" 2>/dev/null) || R_HIT=0
    echo "$f: completion=$C_HIT remediation=$R_HIT"
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/XC-2-completion-vs-remediation.txt
```

**PASS if:** Both artifacts reference all 15 findings and the same set of modified files.

### XC-3: Completion summary ↔ CHANGES.md narrative consistency

```bash
{
  echo "=== XC-3 COMPLETION VS CHANGES ==="
  echo "--- Key findings mentioned in both ---"
  for term in "staleTime" "rewrites" "timeout" "alphanumeric" "DealCard" "border-border" "window.confirm" "scroll" "max-h"; do
    C=$(rg -c "$term" /home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md 2>/dev/null) || C=0
    H=$(rg -c "$term" /home/zaks/bookkeeping/CHANGES.md 2>/dev/null) || H=0
    echo "$term: completion=$C changes=$H"
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/XC-3-completion-vs-changes.txt
```

**PASS if:** Major fix keywords appear in both artifacts.

### XC-4: Findings verification ↔ current state agreement

```bash
{
  echo "=== XC-4 FINDINGS VERIFICATION VS CURRENT STATE ==="
  VERIFY="/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/findings-verification.md"
  echo "--- Findings verification should show CONFIRMED for all ---"
  rg 'CONFIRMED\|PARTIALLY ADDRESSED\|NEEDS LIVE' "$VERIFY" | wc -l
  echo "--- All findings should now be REMEDIATED (code changed since verification) ---"
  echo "F-1: $(rg -c '<button' /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx 2>/dev/null || echo 0) raw buttons"
  echo "F-5: $(rg -c 'async rewrites' /home/zaks/zakops-agent-api/apps/dashboard/next.config.ts 2>/dev/null || echo 0) rewrite functions"
  echo "F-9: $(rg -c 'max-h-\[500px\]' /home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx 2>/dev/null || echo 0) fixed 500px"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/XC-4-findings-vs-current.txt
```

**PASS if:** Findings verification documented pre-fix state; current code shows fixes applied (0 raw buttons, 0 rewrites, 0 fixed 500px).

**XC Gate:** XC-1 through XC-4 all PASS.

---

## 5. Stress Tests (ST)

### ST-1: Deal ID validation edge cases

```bash
{
  echo "=== ST-1 DEAL ID EDGE CASES ==="
  python3 - <<'PY'
import re
def is_valid(id_str):
    reserved = {'new','global','edit','bulk'}
    if id_str.lower() in reserved: return False
    if re.match(r'^DL-[A-Za-z0-9]+$', id_str, re.I): return True
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', id_str, re.I): return True
    return False

edge_cases = [
    ('DL-0', True, 'single digit'),
    ('DL-9999999999', True, 'very long numeric'),
    ('DL-ABCdef123', True, 'mixed case alpha'),
    ('DL-', False, 'empty suffix'),
    ('dl-0086', True, 'lowercase prefix'),
    ('DL-foo/bar', False, 'path separator'),
    ('DL-foo%20bar', False, 'URL encoded space'),
    ('../../../etc/passwd', False, 'path traversal'),
    ('DL-<img onerror=alert(1)>', False, 'XSS payload'),
    ("DL-'; DROP TABLE--", False, 'SQL injection'),
    ('DL-null', True, 'literal null string'),
    ('00000000-0000-0000-0000-000000000000', True, 'nil UUID'),
]
all_pass = True
for id_str, expected, desc in edge_cases:
    result = is_valid(id_str)
    status = 'OK' if result == expected else 'FAIL'
    if result != expected: all_pass = False
    print(f'{status}: "{id_str}" ({desc}) = {result} (expected {expected})')
raise SystemExit(0 if all_pass else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/ST-1-deal-id-edge-cases.txt
```

**PASS if:** All edge cases match expected behavior.

### ST-2: Proxy routing after rewrite removal

```bash
{
  echo "=== ST-2 PROXY ROUTING ==="
  echo "--- Verify middleware handles key API routes ---"
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts"
  echo "--- handledByRoutes list ---"
  rg -A20 'handledByRoutes' "$FILE" | rg "'/api/"
  echo "--- Catch-all proxy for unhandled routes ---"
  rg -n 'backendProxyUrl' "$FILE"
  echo "--- JSON 502 error handling ---"
  rg -n 'backend_unavailable' "$FILE"
  echo "--- Live route test (if backend UP) ---"
  curl -sf http://localhost:3003/api/deals -o /dev/null && echo "DEALS_ROUTE=OK" || echo "DEALS_ROUTE=FAIL_OR_BACKEND_DOWN"
  curl -sf http://localhost:3003/api/pipeline -o /dev/null && echo "PIPELINE_ROUTE=OK" || echo "PIPELINE_ROUTE=FAIL_OR_BACKEND_DOWN"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/ST-2-proxy-routing.txt
```

**PASS if:** Middleware has catch-all proxy, JSON 502 handler, and live routes work (or backend is down — not a proxy failure).

### ST-3: React Query cache behavior verification

```bash
{
  echo "=== ST-3 CACHE BEHAVIOR ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx"
  python3 - <<'PY'
import re
from pathlib import Path
t=Path('/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx').read_text()
stale=re.search(r'staleTime:\s*([\d\s*]+)', t)
gc=re.search(r'gcTime:\s*([\d\s*]+)', t)
refetch_mount=re.search(r'refetchOnMount:\s*(true|false)', t)
refetch_focus=re.search(r'refetchOnWindowFocus:\s*(true|false)', t)
retry=re.search(r'retry:\s*(\d+)', t)
stale_val=eval(stale.group(1).strip()) if stale else None
gc_val=eval(gc.group(1).strip()) if gc else None
print(f'staleTime={stale_val}ms ({stale_val/1000 if stale_val else "N/A"}s)')
print(f'gcTime={gc_val}ms ({gc_val/1000 if gc_val else "N/A"}s)')
print(f'refetchOnMount={refetch_mount.group(1) if refetch_mount else "N/A"}')
print(f'refetchOnWindowFocus={refetch_focus.group(1) if refetch_focus else "N/A"}')
print(f'retry={retry.group(1) if retry else "N/A"}')
# Sanity: gcTime should be > staleTime
if stale_val and gc_val:
    print(f'gcTime_gt_staleTime={gc_val > stale_val}')
    raise SystemExit(0 if gc_val > stale_val and stale_val <= 60000 else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/ST-3-cache-behavior.txt
```

**PASS if:** staleTime <= 60s, gcTime > staleTime, refetchOnMount is true.

### ST-4: Settings scroll behavior at all breakpoints

Browser-verify at 375px, 768px, 1280px:
1. Navigate to `/settings`
2. Scroll to bottom section (Appearance)
3. Verify back arrow is still visible
4. Verify nav switches to dropdown on mobile

**PASS if:** Back arrow visible at all scroll positions; mobile uses dropdown nav.
**Note:** Browser-based check. If dashboard is down per PF-5, mark as SKIP.

### ST-5: DealBoard Link ↔ drag coexistence

```bash
{
  echo "=== ST-5 LINK DRAG COEXISTENCE ==="
  FILE="/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx"
  echo "--- Link is inside Draggable but NOT on drag handle ---"
  rg -n 'dragHandleProps' "$FILE"
  rg -n 'Link href' "$FILE"
  echo "--- Confirm drag handle and Link are siblings, not nested ---"
  python3 - <<'PY'
from pathlib import Path
t=Path('/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx').read_text()
# Link should appear AFTER dragHandleProps closing div
drag_pos=t.find('dragHandleProps')
link_pos=t.find('<Link href')
print(f'dragHandleProps_at={drag_pos}')
print(f'Link_at={link_pos}')
print(f'link_after_drag={link_pos > drag_pos}')
raise SystemExit(0 if link_pos > drag_pos else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/ST-5-link-drag-coexistence.txt
```

**PASS if:** `<Link>` appears after `dragHandleProps` div (siblings, not nested); drag handle remains clickable independently.

### ST-6: Full E2E regression (responsive + cross-page + smoke)

```bash
{
  echo "=== ST-6 FULL E2E REGRESSION ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test tests/e2e/ --reporter=line 2>&1
  echo "EXIT_CODE=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/ST-6-full-e2e-regression.txt
```

**PASS if:** All E2E tests pass (exit 0). If specific tests fail, classify and remediate.

### ST-7: Post-stress validation

```bash
{
  echo "=== ST-7 POST STRESS VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
  echo "EXIT_CODE=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-P4S-VERIFY-001/evidence/ST-7-post-stress-validation.txt
```

**PASS if:** Both `make validate-local` and `tsc --noEmit` exit 0.

**ST Gate:** ST-1 through ST-7 all PASS.

---

## 6. Remediation Protocol

For any FAIL:

1. Read the failing evidence file.
2. Classify as one of:
   - `MISSING_FIX` — finding was not addressed
   - `REGRESSION` — fix introduced a new issue
   - `SCOPE_GAP` — edge case not covered by source mission
   - `FALSE_POSITIVE` — check is wrong, code is correct
   - `NOT_IMPLEMENTED` — Phase 6 test file missing
   - `PARTIAL` — fix applied but incomplete
   - `VIOLATION` — architectural constraint violated
3. Apply minimal in-scope fix (per source mission guardrails).
4. Re-run the failed check with `tee` to evidence file.
5. Re-run affected VF gate.
6. Re-run `make validate-local`.
7. Record remediation in completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Chat history E2E test
Add dedicated Playwright test for chat history dedup (click same history item 5x, verify no duplicates). Source mission Phase 6 did not create this specific test.

### ENH-2: DealBoard click vs drag E2E test
Add Playwright test that verifies clicking a board card navigates, while drag handle initiates drag. Complex to test with Playwright but valuable for regression coverage.

### ENH-3: Pipeline degradation E2E test
Add test that simulates backend failure (mock /api/pipeline to 500) and verifies dashboard still renders with fallback data.

### ENH-4: Settings sticky header visual test
Add visual regression screenshot for settings page at all breakpoints to catch header scroll regressions.

### ENH-5: Alert navigation E2E test
Add Playwright test that clicks an alert with deal_id and verifies navigation to the correct deal page.

### ENH-6: React Query staleTime monitoring
Add a development-only check (console.info) that logs when a query's staleTime differs from the global default, helping identify misconfigured hooks.

### ENH-7: Timeout configuration centralization
Move timeout defaults to a shared constants file instead of having each file parse `PROXY_TIMEOUT_MS` independently.

### ENH-8: DealCard drag-click disambiguation test
Verify that quick click (< 200ms) navigates, while hold+move (> 200ms) initiates drag — prevent accidental navigation during drag.

### ENH-9: Settings IntersectionObserver robustness
Test that the active section detection works correctly when scrolling rapidly or when sections have zero height.

### ENH-10: Hydration error CI gate
Add a Playwright console error collector to CI that fails on any hydration error across all pages (not just /chat).

---

## 8. Scorecard Template

```text
QA-P4S-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (Source Mission Integrity): [ PASS / FAIL ]
  PF-2 (Execution Artifacts): [ PASS / FAIL ]
  PF-3 (Baseline Validation): [ PASS / FAIL ]
  PF-4 (TypeScript Compilation): [ PASS / FAIL ]
  PF-5 (Dashboard Running): [ PASS / FAIL / SKIP ]
  PF-6 (E2E Baseline): [ PASS / FAIL ]

Verification Families:
  VF-01 (Chat Fixes — F-1,F-2,F-3): __ / 4 PASS
  VF-02 (Performance — F-4,F-5,F-6): __ / 4 PASS
  VF-03 (Dashboard Data — F-7..F-11): __ / 6 PASS
  VF-04 (Board View — F-12,F-13): __ / 2 PASS
  VF-05 (Settings — F-14,F-15): __ / 3 PASS
  VF-06 (Tests & Validation): __ / 4 PASS

Cross-Consistency:
  XC-1 through XC-4: __ / 4 PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 PASS

Total: __ / 40 required checks PASS, __ FAIL, __ INFO, __ SKIP

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **Do not build new features** — this is a QA verification mission.
2. **Remediate, do not redesign** — fixes must follow the same pattern as the source mission.
3. **Evidence-first** — every PASS needs captured output via `tee`.
4. **No backend changes** — all fixes are dashboard-side per source mission guardrails.
5. **No generated file edits** — per standing deny rules.
6. **Surface 9 compliance** — `console.warn` for degradation, `console.error` for unexpected.
7. **WSL safety** — `sed -i 's/\r$//'` on new .sh files; `sudo chown zaks:zaks` on files under `/home/zaks/`.
8. **Preserve prior fixes** — remediation must not revert M-04 through M-12 work.
9. **Services-down accommodation** — browser-based gates (VF-01.4, VF-05.3, ST-4) become SKIP if dashboard is down.
10. **Re-run dependent gates after remediation** — any fix triggers re-verification of affected VF + XC + ST-7.

---

## 10. Stop Condition

Stop when all 40 required checks pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` passes, and the scorecard is complete with evidence references.

Do NOT proceed to:
- New feature development
- Backend modifications
- Mobile-specific testing beyond responsive spot-checks
- Next UI Masterplan phase

---

*End of Mission Prompt — QA-P4S-VERIFY-001*

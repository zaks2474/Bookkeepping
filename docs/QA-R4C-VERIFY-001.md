# MISSION: QA-R4C-VERIFY-001
## Independent QA Verification and Remediation — DASHBOARD-R4-CONTINUE-001
## Date: 2026-02-10
## Classification: QA Verification and Remediation — Full-Stack Dashboard
## Prerequisite: `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-R4-CONTINUE-001.md` execution complete or partially complete
## Successor: Dashboard R4 closure decision (FULL PASS required before any new R4 scope)

---

## Preamble: Builder Operating Context

The builder already loads standing guardrails (`CLAUDE.md`, `MEMORY.md`, hooks, deny rules, path-scoped rules). This QA prompt does not restate those systems. It verifies whether Dashboard R4 continuation was executed correctly in the current environment and remediates only where verification fails.

<!-- Adopted from Improvement Area IA-2 -->
## Crash Recovery Protocol (Run First if Session Is Resumed)

If this QA session resumes after interruption, run these before any gate:

```bash
cd /home/zaks/zakops-agent-api && git log --oneline -5
cd /home/zaks/zakops-agent-api && make validate-local
ls -la /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence 2>/dev/null || true
```

Use outputs to determine whether this is first-run verification or continuation.

<!-- Adopted from Improvement Area IA-7 -->
## Continuation Protocol (Mandatory for This Mission)

After each completed VF family, append current state to:
- `/home/zaks/bookkeeping/mission-checkpoints/QA-R4C-VERIFY-001.md`

Checkpoint must include:
- Completed gates
- Open FAIL/INFO/SKIP items
- Current remediation count
- Current validation baseline (`make validate-local`, `make validate-contract-surfaces`)

---

## 1. Mission Objective

Perform independent QA verification and in-scope remediation for:
- Source mission: `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-R4-CONTINUE-001.md`

This QA must verify:
- Source mission intent: Dashboard Round 4 continuation (phases 0-6, AC-1 through AC-8)
- Delivered functionality for Settings, Onboarding, Quality Hardening, UX Polish, Page Audits, and E2E/CI gates
- Architectural compliance with today’s baseline (14 contract surfaces, Surface 9 governance, CI/hook hardening)
- Evidence integrity and bookkeeping consistency

This is a QA mission, not a redesign/build mission. Remediation is allowed only to satisfy source mission ACs or to fix clear regressions/violations found during QA.

---

## 2. Context and Environment Evolution

Since `DASHBOARD-R4-CONTINUE-001` was authored, the environment evolved materially:

1. Contract surface baseline is now **14**, not 9.
2. Surface 9 governance is expanded and enforced via:
   - `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
   - `/home/zaks/zakops-agent-api/.claude/rules/accessibility.md`
   - `/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md`
3. Validation pipeline changed:
   - `make validate-local` includes governance checks
   - `make validate-contract-surfaces` validates 14 surfaces
4. CI/hook hardening exists and must not regress (Gate E script-based scanning, governance gates).
5. Existing Dashboard-R4 evidence is uneven (batches 0-3 + batch 9 visible on disk; batches 4-8 may be missing). QA must classify execution mode before scoring.

Implication: This QA cannot blindly trust old completion claims; it must verify against current filesystem/runtime truth.

---

## 2b. Glossary

| Term | Definition |
|------|------------|
| `VERIFY_ONLY` | Source execution artifacts exist and gates can be audited without building missing scope first |
| `EXECUTE_AND_VERIFY` | Source execution artifacts missing; QA must implement/remediate then verify |
| Surface 9 | Dashboard design-system and frontend governance contract |
| 14-surface baseline | Cross-source consistency across contract catalog, validator, manifest, and `CLAUDE.md` |
| Degradation path | Expected failure path requiring `console.warn`, not `console.error` |

---

## 3. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-R4-CONTINUE-001.md
  rg -n '^## PHASE [0-9]+' /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-R4-CONTINUE-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-R4-CONTINUE-001.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-R4-CONTINUE-001.md')
t=p.read_text()
phase_count=len(re.findall(r'^## PHASE [0-9]+', t, flags=re.M))
ac_count=len(re.findall(r'^### AC-', t, flags=re.M))
print('phase_count=', phase_count)
print('ac_count=', ac_count)
raise SystemExit(0 if (phase_count==7 and ac_count==8) else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** source mission structure remains 7 phases + 8 ACs.

### PF-2: Execution Artifact Inventory (Dashboard-R4)

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACT INVENTORY ==="
  ls -la /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4
  for b in 0 1 2 3 4 5 6 7 8 9; do
    d="/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-$b"
    if [ -d "$d" ]; then
      echo "batch-$b: EXISTS files=$(find \"$d\" -type f | wc -l)"
      find "$d" -maxdepth 2 -type f | sed 's/^/  - /'
    else
      echo "batch-$b: MISSING"
    fi
  done
  ls -la /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/MISSION-COMPLETION-REPORT.md 2>/dev/null || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/PF-2-execution-artifact-inventory.txt
```

**PASS if:** inventory is captured without ambiguity.

### PF-3: Execution Mode Classification

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/PF-3-execution-mode-classification.txt
from pathlib import Path
base=Path('/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4')
present=[]
for b in range(4,10):
    d=base/f'batch-{b}'
    if d.exists():
        present.append(b)
print('present_batches_4_9=',present)
if len(present)==6:
    mode='VERIFY_ONLY'
elif len(present)==0:
    mode='EXECUTE_AND_VERIFY'
else:
    mode='PARTIAL_EXECUTION_REMEDIATE'
print('mode=',mode)
raise SystemExit(0)
PY
```

**PASS if:** mode is emitted as one of: `VERIFY_ONLY`, `PARTIAL_EXECUTION_REMEDIATE`, `EXECUTE_AND_VERIFY`.

### PF-4: Baseline Validation Health

```bash
{
  echo "=== PF-4 BASELINE VALIDATION HEALTH ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/PF-4-baseline-validation-health.txt
```

**PASS if:** all commands exit 0.

### PF-5: Service and Port Snapshot

```bash
{
  echo "=== PF-5 SERVICE SNAPSHOT ==="
  curl -sf http://localhost:3003/ >/dev/null && echo "dashboard_3003=UP" || echo "dashboard_3003=DOWN"
  curl -sf http://localhost:8091/health >/dev/null && echo "backend_8091=UP" || echo "backend_8091=DOWN"
  curl -sf http://localhost:8095/health >/dev/null && echo "agent_8095=UP" || echo "agent_8095=DOWN"
  curl -sf http://localhost:8090/ >/dev/null && echo "port_8090=UP_VIOLATION" || echo "port_8090=DOWN_OK"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/PF-5-service-snapshot.txt
```

**PASS if:** `port_8090=DOWN_OK`. Other services may be DOWN; mark affected live checks as `SKIP_SERVICES_DOWN`.

### PF-6: Four-Way 14-Surface Reconciliation Baseline

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/PF-6-four-way-surface-baseline.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
val=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text() if (repo/'INFRASTRUCTURE_MANIFEST.md').exists() else ''
cs_count=len(re.findall(r'^### Surface \d+:', cs, flags=re.M))
cla_count=len(re.findall(r'^\| \d+ \|', cla, flags=re.M))
val_count=int(re.search(r'Validates all (\d+) contract surfaces', val).group(1))
man_count=len(re.findall(r'^- S\d+ ', man, flags=re.M))
print('contract_surfaces_md=', cs_count)
print('claude_table=', cla_count)
print('validator_header=', val_count)
print('manifest_entries=', man_count)
ok=(cs_count==cla_count==val_count==14 and man_count==14)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** all 4 authoritative sources report 14.

---

## 3b. Verification Mode Rules (Mandatory)

- **IF `mode=VERIFY_ONLY`**: verify all gates; remediate only true FAIL findings.
- **IF `mode=PARTIAL_EXECUTION_REMEDIATE`**: execute missing source-scope work for AC-related gaps, then verify.
- **IF `mode=EXECUTE_AND_VERIFY`**: treat this as delayed execution + QA under the same source mission constraints.
- P0/P1/P2 items found missing: classify as FAIL until remediated.
- P3 items missing: classify as INFO/DEFERRED only if explicitly documented.

---

## 4. Verification Families (VF)

## Verification Family 01 — Settings Redesign (AC-1)

### VF-01.1: Settings Structure Coverage (6 sections)

```bash
{
  echo "=== VF-01.1 SETTINGS SECTION COVERAGE ==="
  rg -n 'AI Provider|Provider Configuration|Email Integration|Agent Configuration|Notification Preferences|Data & Privacy|Appearance|Theme' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-01.1-settings-structure-coverage.txt
```

**PASS if:** all six section intents are present in rendered settings code.

### VF-01.2: Anchor Navigation Coverage

```bash
{
  echo "=== VF-01.2 SETTINGS ANCHORS ==="
  rg -n 'id="(provider|email|agent|notifications|data|appearance)"|href="#(provider|email|agent|notifications|data|appearance)"|scrollIntoView|location.hash' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-01.2-settings-anchor-navigation.txt
```

**PASS if:** section IDs and anchor navigation mechanism are both present.

### VF-01.3: Email Integration Endpoint Wiring

```bash
{
  echo "=== VF-01.3 EMAIL ENDPOINT WIRING ==="
  rg -n '/api/integrations/email/connect|/api/integrations/email/test|/api/integrations/email' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-01.3-settings-email-endpoint-wiring.txt
```

**PASS if:** connect/test/disconnect wiring is discoverable or explicitly stubbed with graceful behavior.

### VF-01.4: Agent Preferences Persistence Wiring

```bash
{
  echo "=== VF-01.4 AGENT PREFERENCES PERSISTENCE ==="
  rg -n '/api/user/preferences|preferences' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings --glob '*.ts' --glob '*.tsx'
  rg -n 'GET|PATCH|save|load|persist' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-01.4-settings-agent-preferences-persistence.txt
```

**PASS if:** settings include read/write persistence path for preferences (not client-only volatile state).

### VF-01.5: Appearance/Theme/Timezone Persistence

```bash
{
  echo "=== VF-01.5 APPEARANCE + TIMEZONE ==="
  rg -n 'theme|dark|light|system|timezone|timeZone|Intl\.DateTimeFormat|localStorage|cookie|preferences' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-01.5-settings-appearance-timezone.txt
```

**PASS if:** theme + timezone controls exist and persistence mechanism is present.

### VF-01.6: Settings Surface 9 + Governance Compliance

```bash
{
  echo "=== VF-01.6 SETTINGS GOVERNANCE COMPLIANCE ==="
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-surface9.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-frontend-governance.sh
  rg -n 'Promise\.all\(' /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings --glob '*.ts' --glob '*.tsx' | rg -v 'Promise\.allSettled' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-01.6-settings-surface9-governance.txt
```

**PASS if:** validators pass and no forbidden `Promise.all` pattern is introduced.

**Gate VF-01:** 6/6 checks PASS.

---

## Verification Family 02 — Onboarding Redesign (AC-2)

### VF-02.1: Onboarding Route and Files Present

```bash
{
  echo "=== VF-02.1 ONBOARDING FILE INVENTORY ==="
  find /home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding -type f \( -name '*.ts' -o -name '*.tsx' \)
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-02.1-onboarding-file-inventory.txt
```

**PASS if:** onboarding route implementation files exist.

### VF-02.2: Six Endpoint Wiring Check

```bash
{
  echo "=== VF-02.2 ONBOARDING ENDPOINT WIRING ==="
  rg -n '/api/onboarding/status|/api/onboarding/profile|/api/onboarding/email-skipped|/api/onboarding/demo/start|/api/onboarding/complete|/api/onboarding/reset' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-02.2-onboarding-endpoint-wiring.txt
```

**PASS if:** all six endpoint intents are represented in frontend onboarding flow.

### VF-02.3: No localStorage State for Onboarding

```bash
{
  echo "=== VF-02.3 ONBOARDING STORAGE POLICY ==="
  rg -n 'localStorage|sessionStorage' /home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding --glob '*.ts' --glob '*.tsx' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-02.3-onboarding-storage-policy.txt
```

**PASS if:** no onboarding state is persisted via `localStorage` (session drafts allowed if documented).

### VF-02.4: Resume/Status-on-Load Behavior

```bash
{
  echo "=== VF-02.4 ONBOARDING RESUME STATUS ==="
  rg -n 'onboarding.*status|resume|currentStep|useEffect|fetch' /home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-02.4-onboarding-resume-status.txt
```

**PASS if:** onboarding flow is backend-status-driven on load.

### VF-02.5: Completion Redirect and Reset Flow

```bash
{
  echo "=== VF-02.5 ONBOARDING REDIRECT + RESET ==="
  rg -n 'router\.push\(|redirect\(|/dashboard|onboarding/reset|redo onboarding' /home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding /home/zaks/zakops-agent-api/apps/dashboard/src/app/settings --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-02.5-onboarding-redirect-reset.txt
```

**PASS if:** complete state routes to dashboard and reset path is discoverable.

### VF-02.6: Skip Policy Validation (Email Step Only)

```bash
{
  echo "=== VF-02.6 ONBOARDING SKIP POLICY ==="
  rg -n 'skip|Skip' /home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding --glob '*.ts' --glob '*.tsx' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-02.6-onboarding-skip-policy.txt
```

**PASS if:** skip affordance is limited to email step or clearly constrained by logic.

### VF-02.7: Onboarding Surface 9 Compliance

```bash
{
  echo "=== VF-02.7 ONBOARDING SURFACE 9 ==="
  rg -n 'Promise\.all\(' /home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding --glob '*.ts' --glob '*.tsx' | rg -v 'Promise\.allSettled' || true
  rg -n 'console\.error' /home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding --glob '*.ts' --glob '*.tsx' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-02.7-onboarding-surface9.txt
```

**PASS if:** no forbidden `Promise.all`; `console.error` use is justified for unexpected failures.

**Gate VF-02:** 7/7 checks PASS.

---

## Verification Family 03 — Quality Hardening (AC-3)

### VF-03.1: Zod Strictness Sweep

```bash
{
  echo "=== VF-03.1 ZOD STRICTNESS ==="
  rg -n '\.passthrough\(\)|z\.unknown\(\)' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-03.1-zod-strictness-sweep.txt
```

**PASS if:** zero production hits or every hit is explicitly justified and non-runtime.

### VF-03.2: Error Boundary Coverage Across Major Pages

```bash
{
  echo "=== VF-03.2 ERROR BOUNDARY COVERAGE ==="
  rg -n 'ErrorBoundary|error\.tsx|componentDidCatch|errorElement' /home/zaks/zakops-agent-api/apps/dashboard/src/app --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-03.2-error-boundary-coverage.txt
```

**PASS if:** boundaries exist for major routes (`deals`, `actions`, `quarantine`, `settings`, `onboarding`, `hq`, `agent/activity`).

### VF-03.3: Mock/Fallback Leakage in Production API Routes

```bash
{
  echo "=== VF-03.3 MOCK FALLBACK LEAKAGE ==="
  rg -n 'mock|fallback.*data|dummy|fake|stub' /home/zaks/zakops-agent-api/apps/dashboard/src/app/api --glob '*.ts' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-03.3-mock-fallback-leakage.txt
```

**PASS if:** no production mock fallback leaks unless explicitly gated to dev/test.

### VF-03.4: Correlation ID Enforcement

```bash
{
  echo "=== VF-03.4 CORRELATION ID ==="
  rg -n 'X-Correlation-ID|x-correlation-id|correlation_id|uuid' /home/zaks/zakops-agent-api/apps/dashboard/src/lib /home/zaks/zakops-agent-api/apps/dashboard/src/app/api --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-03.4-correlation-id-enforcement.txt
```

**PASS if:** correlation ID header generation and propagation are present.

### VF-03.5: Error Envelope Standardization

```bash
{
  echo "=== VF-03.5 ERROR ENVELOPE STANDARDIZATION ==="
  rg -n 'NextResponse\.json\(\{.*(code|message|details|correlation_id)' /home/zaks/zakops-agent-api/apps/dashboard/src/app/api --glob '*.ts' || true
  rg -n '\{error\}|\{detail\}|\{message\}' /home/zaks/zakops-agent-api/apps/dashboard/src/app/api --glob '*.ts' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-03.5-error-envelope-standardization.txt
```

**PASS if:** standardized envelope dominates and no inconsistent regression introduced.

### VF-03.6: Operator Identity and Profile Endpoint

```bash
{
  echo "=== VF-03.6 OPERATOR IDENTITY + PROFILE ENDPOINT ==="
  rg -n 'operatorName|operator_name|/api/user/profile|/api/me|/api/user/me|/api/auth/me' /home/zaks/zakops-agent-api/apps/dashboard/src /home/zaks/zakops-backend/src --glob '*.ts' --glob '*.tsx' --glob '*.py'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-03.6-operator-identity-profile-endpoint.txt
```

**PASS if:** identity is validated server-side or routed through authenticated profile endpoint.

### VF-03.7: Idempotency/Action Safety Evidence

```bash
{
  echo "=== VF-03.7 IDEMPOTENCY SAFETY ==="
  rg -n 'Idempotency-Key|idempotency|409' /home/zaks/zakops-agent-api/apps/dashboard/src /home/zaks/zakops-backend/src --glob '*.ts' --glob '*.tsx' --glob '*.py' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-03.7-idempotency-safety.txt
```

**PASS if:** evidence shows duplicate action protection behavior or explicit deferral documentation.

**Gate VF-03:** 7/7 checks PASS.

---

## Verification Family 04 — UX Polish (AC-4)

### VF-04.1: Pagination Coverage (deals/actions/quarantine)

```bash
{
  echo "=== VF-04.1 PAGINATION COVERAGE ==="
  rg -n 'pagination|Pagination|pageSize|page=|limit|offset|cursor|nextPage|prevPage' /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals /home/zaks/zakops-agent-api/apps/dashboard/src/app/actions /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-04.1-pagination-coverage.txt
```

**PASS if:** pagination behavior exists on intended lists.

### VF-04.2: Filter Persistence in URL

```bash
{
  echo "=== VF-04.2 FILTER URL PERSISTENCE ==="
  rg -n 'useSearchParams|searchParams|URLSearchParams|router\.replace|router\.push' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-04.2-filter-url-persistence.txt
```

**PASS if:** active filter/sort state is encoded in URL and restorable.

### VF-04.3: Keyboard Accessibility Controls

```bash
{
  echo "=== VF-04.3 KEYBOARD CONTROLS ==="
  rg -n 'onKeyDown|onKeyUp|Escape|Enter|ArrowDown|ArrowUp|tabIndex|role="dialog"|role="button"' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-04.3-keyboard-controls.txt
```

**PASS if:** keyboard navigation and close/submit handlers are present for interactive flows.

### VF-04.4: SSE Reconnect and Health Signaling

```bash
{
  echo "=== VF-04.4 SSE RECONNECT ==="
  rg -n 'EventSource|reconnect|retry|lastEventId|onerror|onclose|connection.*health' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-04.4-sse-reconnect-health.txt
```

**PASS if:** reconnect/retry handling exists and user-visible signal is present.

### VF-04.5: Double-Submit Protection

```bash
{
  echo "=== VF-04.5 DOUBLE-SUBMIT PROTECTION ==="
  rg -n 'isLoading|isSubmitting|disabled=.*(isLoading|isSubmitting)|debounce|throttle' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-04.5-double-submit-protection.txt
```

**PASS if:** action controls prevent rapid duplicate submissions.

### VF-04.6: Alerts/Deferred-Actions Enum Drift Check

```bash
{
  echo "=== VF-04.6 ALERT ENUM DRIFT ==="
  rg -n 'deferred-actions|alerts|status|toLowerCase|enum' /home/zaks/zakops-agent-api/apps/dashboard/src /home/zaks/zakops-backend/src --glob '*.ts' --glob '*.tsx' --glob '*.py'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-04.6-alert-enum-drift.txt
```

**PASS if:** no unresolved enum mismatch remains between frontend and backend.

**Gate VF-04:** 6/6 checks PASS.

---

## Verification Family 05 — Page Audits (AC-5)

### VF-05.1: `/hq` Component Audit

```bash
{
  echo "=== VF-05.1 HQ COMPONENT AUDIT ==="
  find /home/zaks/zakops-agent-api/apps/dashboard/src/app/hq -type f \( -name '*.ts' -o -name '*.tsx' \)
  rg -n 'QuickStat|Pipeline|Activity|Chart|metric|summary' /home/zaks/zakops-agent-api/apps/dashboard/src/app/hq --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-05.1-hq-component-audit.txt
```

**PASS if:** `/hq` route has real data-bearing components (not placeholder-only).

### VF-05.2: `/hq` Data Fetching Pattern

```bash
{
  echo "=== VF-05.2 HQ DATA FETCHING PATTERN ==="
  rg -n 'Promise\.allSettled|Promise\.all|pipelineSummary|total_count|count' /home/zaks/zakops-agent-api/apps/dashboard/src/app/hq --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-05.2-hq-data-fetching-pattern.txt
```

**PASS if:** multi-fetch uses `Promise.allSettled` and count signals are server-sourced.

### VF-05.3: `/agent/activity` Structure Audit

```bash
{
  echo "=== VF-05.3 AGENT ACTIVITY STRUCTURE ==="
  find /home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity -type f \( -name '*.ts' -o -name '*.tsx' \)
  rg -n 'timeline|activity|event|run|trace' /home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity --glob '*.ts' --glob '*.tsx'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-05.3-agent-activity-structure.txt
```

**PASS if:** route has functioning activity/timeline UI and data path.

### VF-05.4: Route Link Integrity in Audited Pages

```bash
{
  echo "=== VF-05.4 ROUTE LINK INTEGRITY ==="
  rg -n 'href="/[^"]+"|router\.push\("/[^"]+' /home/zaks/zakops-agent-api/apps/dashboard/src/app/hq /home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity --glob '*.ts' --glob '*.tsx' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-05.4-route-link-integrity.txt
```

**PASS if:** no clearly broken/internal dead links are found.

### VF-05.5: Bulk Archive Endpoint Wiring

```bash
{
  echo "=== VF-05.5 BULK ARCHIVE WIRING ==="
  rg -n 'bulk-archive|bulk_archive|bulkArchive' /home/zaks/zakops-agent-api/apps/dashboard/src /home/zaks/zakops-backend/src --glob '*.ts' --glob '*.tsx' --glob '*.py'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-05.5-bulk-archive-wiring.txt
```

**PASS if:** frontend + backend wiring exists, or deferral is explicit and justified.

### VF-05.6: Empty/Error-State Resilience

```bash
{
  echo "=== VF-05.6 EMPTY ERROR RESILIENCE ==="
  rg -n 'empty|no data|try again|retry|error state|fallback' /home/zaks/zakops-agent-api/apps/dashboard/src/app/hq /home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity --glob '*.ts' --glob '*.tsx' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-05.6-empty-error-resilience.txt
```

**PASS if:** pages expose explicit empty/error handling paths and avoid white-screen failure modes.

**Gate VF-05:** 6/6 checks PASS.

---

## Verification Family 06 — E2E and CI Gates (AC-6)

### VF-06.1: E2E Inventory and Growth Check

```bash
{
  echo "=== VF-06.1 E2E INVENTORY ==="
  find /home/zaks/zakops-agent-api/apps/dashboard/tests /home/zaks/zakops-agent-api/apps/dashboard/e2e -type f \( -name '*.spec.ts' -o -name '*.spec.tsx' \) 2>/dev/null
  rg -n 'test\(|it\(|test\.describe' /home/zaks/zakops-agent-api/apps/dashboard/tests /home/zaks/zakops-agent-api/apps/dashboard/e2e --glob '*.spec.ts' --glob '*.spec.tsx' 2>/dev/null | wc -l
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-06.1-e2e-inventory-growth.txt
```

**PASS if:** post-R4 suite is present and coverage is materially above pre-batch baseline.

### VF-06.2: Dead-UI Gate Spec Presence

```bash
{
  echo "=== VF-06.2 DEAD-UI SPEC PRESENCE ==="
  ls -la /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/no-dead-ui.spec.ts
  rg -n '/dashboard|/deals|/actions|/quarantine|/settings|/hq|/agent/activity|/chat|/onboarding' /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/no-dead-ui.spec.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-06.2-dead-ui-spec-presence.txt
```

**PASS if:** dead-UI test exists and covers major routes.

### VF-06.3: Phase-Coverage Spec Presence

```bash
{
  echo "=== VF-06.3 PHASE COVERAGE SPEC ==="
  ls -la /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/phase-coverage.spec.ts
  rg -n 'settings|onboarding|hq|agent/activity|pagination|filter|correlation' /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/phase-coverage.spec.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-06.3-phase-coverage-spec.txt
```

**PASS if:** phase-coverage spec exists and maps to Phases 1-5 concerns.

### VF-06.4: API Contract Gate Script Runtime

```bash
{
  echo "=== VF-06.4 API CONTRACT GATE SCRIPT ==="
  ls -la /home/zaks/zakops-agent-api/tools/infra/validate-api-contract.sh
  cd /home/zaks/zakops-agent-api && bash tools/infra/validate-api-contract.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-06.4-api-contract-gate-runtime.txt
```

**PASS if:** script exists and exits 0.

### VF-06.5: CI/Make Wiring for R4 Gate Assets

```bash
{
  echo "=== VF-06.5 CI MAKE WIRING R4 GATES ==="
  rg -n 'validate-api-contract|no-dead-ui|phase-coverage|playwright' /home/zaks/zakops-agent-api/Makefile /home/zaks/zakops-agent-api/.github/workflows/ci.yml || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-06.5-ci-make-wiring-r4-assets.txt
```

**PASS if:** wiring exists, OR explicit deferral is documented as non-blocking.

### VF-06.6: Playwright Parse/Listing Health

```bash
{
  echo "=== VF-06.6 PLAYWRIGHT LIST HEALTH ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test --list
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-06.6-playwright-list-health.txt
```

**PASS if:** suite parses and lists tests successfully.

**Gate VF-06:** 6/6 checks PASS.

---

## Verification Family 07 — Validation Clean + Architecture Compliance (AC-7)

### VF-07.1: `make validate-local`

```bash
{
  echo "=== VF-07.1 VALIDATE LOCAL ==="
  cd /home/zaks/zakops-agent-api && make validate-local
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-07.1-validate-local.txt
```

**PASS if:** exit 0.

### VF-07.2: 14-Surface Unified Validator

```bash
{
  echo "=== VF-07.2 14-SURFACE VALIDATOR ==="
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-07.2-validate-contract-surfaces.txt
```

**PASS if:** 14/14 checks pass.

### VF-07.3: Frontend Governance Validation

```bash
{
  echo "=== VF-07.3 FRONTEND GOVERNANCE VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-07.3-validate-frontend-governance.txt
```

**PASS if:** governance checks pass.

### VF-07.4: `Promise.all` Sweep for Dashboard App/API

```bash
{
  echo "=== VF-07.4 PROMISE.ALL SWEEP ==="
  rg -n 'Promise\.all\(' /home/zaks/zakops-agent-api/apps/dashboard/src/app --glob '*.ts' --glob '*.tsx' | rg -v 'Promise\.allSettled' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-07.4-promise-all-sweep.txt
```

**PASS if:** zero unresolved forbidden hits.

### VF-07.5: Bridge Import Discipline

```bash
{
  echo "=== VF-07.5 BRIDGE IMPORT DISCIPLINE ==="
  rg -n 'api-types\.generated|agent-api-types\.generated' /home/zaks/zakops-agent-api/apps/dashboard/src --glob '*.ts' --glob '*.tsx' | rg -v 'src/types/api\.ts|src/types/agent-api\.ts' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-07.5-bridge-import-discipline.txt
```

**PASS if:** no direct generated-type imports outside bridge files.

### VF-07.6: Port 8090 Drift Scan

```bash
{
  echo "=== VF-07.6 PORT 8090 DRIFT SCAN ==="
  rg -n '8090' /home/zaks/zakops-agent-api/apps/dashboard/src /home/zaks/zakops-agent-api/.claude/rules /home/zaks/.claude/hooks --glob '*.ts' --glob '*.tsx' --glob '*.md' --glob '*.sh' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-07.6-port-8090-drift.txt
```

**PASS if:** no active runtime drift to 8090 (drift-checker script references are acceptable).

### VF-07.7: Type Sync Discipline

```bash
{
  echo "=== VF-07.7 TYPE SYNC DISCIPLINE ==="
  cd /home/zaks/zakops-agent-api && make sync-all-types
  cd /home/zaks/zakops-agent-api && git status --short
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-07.7-type-sync-discipline.txt
```

**PASS if:** sync runs clean; no unexpected generated drift from QA remediation.

**Gate VF-07:** 7/7 checks PASS.

---

## Verification Family 08 — Evidence and Bookkeeping (AC-8)

### VF-08.1: Batch 4-9 Evidence Completeness

```bash
{
  echo "=== VF-08.1 BATCH 4-9 EVIDENCE COMPLETENESS ==="
  for b in 4 5 6 7 8 9; do
    d="/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-$b"
    if [ -d "$d" ]; then
      echo "batch-$b=EXISTS files=$(find \"$d\" -type f | wc -l)"
      find "$d" -maxdepth 2 -type f | sed 's/^/  - /'
    else
      echo "batch-$b=MISSING"
    fi
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-08.1-batch-4-9-evidence-completeness.txt
```

**PASS if:** executed phases have matching evidence; missing phases are explicitly classified.

### VF-08.2: Mission Completion Report Consistency

```bash
{
  echo "=== VF-08.2 MISSION COMPLETION CONSISTENCY ==="
  ls -la /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/MISSION-COMPLETION-REPORT.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|batch-4|batch-5|batch-6|batch-7|batch-8|batch-9' /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/MISSION-COMPLETION-REPORT.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-08.2-mission-completion-consistency.txt
```

**PASS if:** completion report claims are traceable to evidence artifacts.

### VF-08.3: CHANGES.md Entry Integrity

```bash
{
  echo "=== VF-08.3 CHANGES ENTRY ==="
  rg -n 'DASHBOARD-R4-CONTINUE|Batch 4|Batch 5|Batch 6|Batch 7|Batch 8|Batch 9|R4' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-08.3-changes-entry-integrity.txt
```

**PASS if:** source mission work is recorded with meaningful detail.

### VF-08.4: Deferred Scope Disclosure Check

```bash
{
  echo "=== VF-08.4 DEFERRED SCOPE DISCLOSURE ==="
  rg -n 'deferred|P3|not implemented|out of scope' /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/MISSION-COMPLETION-REPORT.md /home/zaks/bookkeeping/CHANGES.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-08.4-deferred-scope-disclosure.txt
```

**PASS if:** deferred items are explicit (no silent omission).

### VF-08.5: Final Validation Snapshot

```bash
{
  echo "=== VF-08.5 FINAL VALIDATION SNAPSHOT ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/VF-08.5-final-validation-snapshot.txt
```

**PASS if:** final validation is clean after all remediations.

**Gate VF-08:** 5/5 checks PASS.

---

## 5. Cross-Consistency Checks (XC)

### XC-1: Source Mission Claims vs Evidence Reality

```bash
{
  echo "=== XC-1 SOURCE CLAIMS VS EVIDENCE ==="
  rg -n 'Phase 1|Phase 2|Phase 3|Phase 4|Phase 5|Phase 6|batch-4|batch-5|batch-6|batch-7|batch-8|batch-9' /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/MISSION-COMPLETION-REPORT.md
  find /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4 -maxdepth 2 -type d | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/XC-1-claims-vs-evidence.txt
```

**PASS if:** claim/evidence alignment is consistent; mismatches are called out as FAIL or INFO.

### XC-2: AC-to-VF Coverage Matrix Integrity

```bash
{
  echo "=== XC-2 AC TO VF COVERAGE ==="
  printf 'AC-1 -> VF-01\nAC-2 -> VF-02\nAC-3 -> VF-03\nAC-4 -> VF-04\nAC-5 -> VF-05\nAC-6 -> VF-06\nAC-7 -> VF-07\nAC-8 -> VF-08\n'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/XC-2-ac-vf-coverage-matrix.txt
```

**PASS if:** every AC is verified by one VF family.

### XC-3: 14-Surface Baseline Stability After QA

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/XC-3-four-way-surface-post.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
val=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text() if (repo/'INFRASTRUCTURE_MANIFEST.md').exists() else ''
print('contract_surfaces_md=',len(re.findall(r'^### Surface \d+:', cs, flags=re.M)))
print('claude_rows=',len(re.findall(r'^\| \d+ \|', cla, flags=re.M)))
print('validator_declared=',int(re.search(r'Validates all (\d+) contract surfaces', val).group(1)))
print('manifest_entries=',len(re.findall(r'^- S\d+ ', man, flags=re.M)))
PY
```

**PASS if:** still 14/14/14/14.

### XC-4: Governance Rule Coverage vs Validators

```bash
{
  echo "=== XC-4 GOVERNANCE RULE COVERAGE ==="
  ls -la /home/zaks/zakops-agent-api/.claude/rules/design-system.md
  ls -la /home/zaks/zakops-agent-api/.claude/rules/accessibility.md
  ls -la /home/zaks/zakops-agent-api/.claude/rules/component-patterns.md
  rg -n 'design-system|accessibility|component-patterns' /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh /home/zaks/zakops-agent-api/tools/infra/validate-frontend-governance.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/XC-4-governance-coverage.txt
```

**PASS if:** validator coverage matches active governance rule files.

### XC-5: R4 Gate Assets vs CI/Make Exposure

```bash
{
  echo "=== XC-5 R4 GATE ASSETS VS CI/MAKE ==="
  ls -la /home/zaks/zakops-agent-api/tools/infra/validate-api-contract.sh
  ls -la /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/no-dead-ui.spec.ts
  ls -la /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/phase-coverage.spec.ts
  rg -n 'validate-api-contract|no-dead-ui|phase-coverage' /home/zaks/zakops-agent-api/Makefile /home/zaks/zakops-agent-api/.github/workflows/ci.yml || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/XC-5-r4-gate-assets-vs-wiring.txt
```

**PASS if:** assets and enforcement wiring are coherent, or gaps are explicitly classified.

### XC-6: Legacy-Standard Claim Drift Detection

```bash
{
  echo "=== XC-6 LEGACY CLAIM DRIFT ==="
  rg -n '9 contract surfaces|all 9|Surface 9 only baseline|old standard' /home/zaks/bookkeeping/docs/QA-R4C-VERIFY-001.md /home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/MISSION-COMPLETION-REPORT.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/XC-6-legacy-claim-drift.txt
```

**PASS if:** no stale surface-count assumptions remain unresolved.

---

## 6. Stress Tests (ST)

### ST-1: Determinism — `make validate-local` x2

```bash
{
  echo "=== ST-1 VALIDATE-LOCAL DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-local
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/ST-1-validate-local-determinism.txt
```

**PASS if:** both runs pass without drift.

### ST-2: Determinism — Surface and Governance Validators x2

```bash
{
  echo "=== ST-2 SURFACE/GOVERNANCE DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make validate-frontend-governance
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/ST-2-surface-governance-determinism.txt
```

**PASS if:** all runs stable and green.

### ST-3: Hook Contract Self-Test (if available)

```bash
{
  echo "=== ST-3 HOOK CONTRACT SELF-TEST ==="
  if [ -f /home/zaks/zakops-agent-api/tools/infra/validate-stop-hook-selftest.sh ]; then
    cd /home/zaks/zakops-agent-api && bash tools/infra/validate-stop-hook-selftest.sh
  else
    echo "INFO: validate-stop-hook-selftest.sh not present"
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/ST-3-hook-contract-selftest.txt
```

**PASS if:** script passes when present; otherwise INFO.

### ST-4: Snapshot Stability + Manifest Surface Count

```bash
{
  echo "=== ST-4 SNAPSHOT STABILITY ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  rg -n '^## Contract Surfaces \(14 Total' /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md
  rg -n '^- S[0-9]+' /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md | wc -l
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/ST-4-snapshot-stability.txt
```

**PASS if:** snapshot succeeds and manifest still has 14 entries.

### ST-5: Playwright Suite Listing Stability x2

```bash
{
  echo "=== ST-5 PLAYWRIGHT LIST STABILITY ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test --list
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test --list
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/ST-5-playwright-list-stability.txt
```

**PASS if:** both list passes are deterministic.

### ST-6: File Hygiene (UTF-8/LF + ownership sanity)

```bash
{
  echo "=== ST-6 FILE HYGIENE ==="
  file /home/zaks/zakops-agent-api/tools/infra/validate-api-contract.sh
  file /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/no-dead-ui.spec.ts
  file /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/phase-coverage.spec.ts
  ls -la /home/zaks/zakops-agent-api/tools/infra/validate-api-contract.sh /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/no-dead-ui.spec.ts /home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/phase-coverage.spec.ts
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/ST-6-file-hygiene.txt
```

**PASS if:** text files are sane and runnable; no CRLF breakage.

### ST-7: Forbidden-File Regression Guard

```bash
{
  echo "=== ST-7 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
} | tee /home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/ST-7-forbidden-file-regression-guard.txt
```

**PASS if:** QA work did not introduce forbidden generated-file edits.

---

## 7. Remediation Protocol

For any FAIL gate:

1. Read evidence output and identify exact failure point.
2. Classify as one of:
   - `NOT_EXECUTED`
   - `PARTIAL`
   - `REGRESSION`
   - `VIOLATION`
   - `SCOPE_GAP`
   - `FALSE_POSITIVE`
3. Apply minimal fix within source mission scope.
4. Re-run the failing gate.
5. Re-run `make validate-local`.
6. Record remediation in completion report with:
   - Gate ID
   - Root cause
   - Fix summary
   - Evidence file path

---

## 8. Enhancement Opportunities (Non-Blocking)

### ENH-1: Add explicit `validate-api-contract` Make target and wire into CI gates
### ENH-2: Add dashboard route-coverage report generated from Playwright specs
### ENH-3: Add schema check for settings section IDs (`provider/email/agent/notifications/data/appearance`)
### ENH-4: Add static checker for onboarding endpoint completeness (6 required endpoints)
### ENH-5: Add CI guard for onboarding localStorage prohibition
### ENH-6: Add automated claim-vs-evidence checker for Dashboard-R4 completion report
### ENH-7: Add governance benchmark trend for dashboard validator runtime
### ENH-8: Add `--json` output mode for `validate-api-contract.sh`
### ENH-9: Add pre-commit drift check for stale surface-count wording in dashboard docs
### ENH-10: Add QA scaffold template specialized for dashboard mission family

---

## 9. Scorecard Template

```text
QA-R4C-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________
Execution Mode: [ VERIFY_ONLY / PARTIAL_EXECUTION_REMEDIATE / EXECUTE_AND_VERIFY ]

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL / INFO ]
  PF-6: [ PASS / FAIL ]

Verification Families:
  VF-01 (Settings / AC-1): __ / 6 PASS
  VF-02 (Onboarding / AC-2): __ / 7 PASS
  VF-03 (Quality / AC-3): __ / 7 PASS
  VF-04 (UX / AC-4): __ / 6 PASS
  VF-05 (Page Audits / AC-5): __ / 6 PASS
  VF-06 (E2E + CI / AC-6): __ / 6 PASS
  VF-07 (Validation + Architecture / AC-7): __ / 7 PASS
  VF-08 (Evidence + Bookkeeping / AC-8): __ / 5 PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 PASS

Total: __ / 69 checks PASS, __ FAIL, __ INFO, __ SKIP

Remediations Applied: __
Deferred Items: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 10. Guardrails

1. Do not build net-new feature scope beyond source mission commitments.
2. Remediate failures; do not redesign architecture opportunistically.
3. Preserve Surface 9 + 14-surface baseline.
4. Do not modify generated files or `.env` files.
5. Preserve prior hardening work (FGH/CIH/IEU mission outcomes).
6. Every PASS must have evidence output (tee file or file-path proof).
7. Services-down states become `SKIP_SERVICES_DOWN`, not false FAIL.
8. P3 gaps are INFO/DEFERRED only if explicitly documented.
9. Keep CRLF/ownership hygiene for any new remediation scripts.
10. Re-run `make validate-local` after every remediation cycle.

---

## 11. File Paths Reference

### Files to Modify (Only if remediating)

| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/**` | AC-1 remediation |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/**` | AC-2 remediation |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/**` | AC-3/AC-4 remediation |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/**` | AC-3/AC-4 remediation |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/**` | AC-6 remediation |
| `/home/zaks/zakops-agent-api/tools/infra/validate-api-contract.sh` | AC-6 remediation |
| `/home/zaks/bookkeeping/CHANGES.md` | Bookkeeping |

### Files to Read (Do not modify unless explicitly remediating)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-R4-CONTINUE-001.md` | Source mission contract |
| `/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/MISSION-COMPLETION-REPORT.md` | Claimed completion baseline |
| `/home/zaks/zakops-agent-api/CLAUDE.md` | 14-surface system baseline |
| `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` | Surface definitions |
| `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` | Unified validator behavior |
| `/home/zaks/zakops-agent-api/.github/workflows/ci.yml` | CI gate wiring |

### Evidence Output Root

| Path |
|------|
| `/home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/evidence/` |

---

## 12. Stop Condition

Stop when all 69 checks pass (or are explicitly classified as `INFO`/`SKIP_SERVICES_DOWN`/`DEFERRED` with evidence), all required remediations are re-verified, and final baseline validation is green.

Produce:
- `/home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/SCORECARD.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-R4C-VERIFY-001/QA-R4C-VERIFY-001-COMPLETION.md`

Do not proceed to new Dashboard R4 scope until verdict is `FULL PASS` or a documented conditional decision is approved.

---

*End of Mission Prompt — QA-R4C-VERIFY-001*

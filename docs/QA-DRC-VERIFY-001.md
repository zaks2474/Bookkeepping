# MISSION: QA-DRC-VERIFY-001
## Independent QA Verification & Remediation — Dashboard Route Coverage Remediation
## Date: 2026-02-15
## Classification: QA Verification & Remediation
## Prerequisite: Dashboard Route Coverage Remediation (completion report: `/home/zaks/bookkeeping/docs/DASHBOARD-ROUTE-REMEDIATION-COMPLETION-REPORT.md`)
## Successor: None (standalone QA)

---

## 1. Mission Objective

This is an **independent, line-by-line QA verification** of the Dashboard Route Coverage Remediation completed on 2026-02-15. The source mission addressed cascading 404 failures across 8 of 12 dashboard pages caused by missing Next.js route handlers, middleware routing gaps, and code bugs.

**What this mission does:**
- Independently re-verify every deliverable claimed in the completion report
- Cross-check all 10 new route handler files for pattern compliance
- Verify all 4 bug fixes with evidence
- Validate Surface 17 (Dashboard Route Coverage) registration across all 4 infrastructure sources
- Verify dead code deletion
- Stress-test middleware routing logic and handler-to-api.ts mapping completeness
- Remediate any findings and re-verify

**What this mission is NOT:**
- This is NOT a feature build — do not add new functionality
- This is NOT a backend remediation — Category 3 items (backend 404s/500s) are out of scope
- This does NOT re-audit the entire dashboard — only the deliverables from the source remediation

**Source artifacts (read ALL before starting verification):**

| Artifact | Path | Purpose |
|----------|------|---------|
| Completion Report | `/home/zaks/bookkeeping/docs/DASHBOARD-ROUTE-REMEDIATION-COMPLETION-REPORT.md` | Primary source of truth — 22 checkable items, 7 sections |
| System Health Audit | `/home/zaks/bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md` | Root cause analysis, 5 categories, remediation scope |
| Surface 17 Validator | `/home/zaks/zakops-agent-api/tools/infra/validate-surface17.sh` | Automated route coverage enforcement |
| Endpoint Liveness Probe | `/home/zaks/zakops-agent-api/tools/infra/validate-endpoint-liveness.sh` | Runtime endpoint verification |
| Contract Surfaces Rule | `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` | Surface 17 definition |

**Completion report summary:**
- 10 new route handler files created
- 1 route handler file modified (GET method added)
- 1 middleware file modified (3 new prefixes)
- 3 bug fixes applied (chat fallback, activity CSS, quarantine working state)
- 1 dead code file deleted
- Surface 17 validator created and registered
- Endpoint liveness probe created
- Smoke test script created
- Infrastructure count updated to 17 across all 4 sources
- 43/43 Surface 17 checks PASS, 0 FAIL, 3 WARN (expected)

---

## 2. Glossary

| Term | Definition |
|------|-----------|
| Route handler | Next.js `route.ts` file under `app/api/` that handles HTTP requests — the middle layer of the 3-layer proxy |
| `handledByRoutes` | Array in `middleware.ts` listing URL prefixes that should be handled by route handlers instead of the middleware proxy |
| `backendFetch` | Helper from `@/lib/backend-fetch` used by route handlers to proxy requests to the backend (port 8091) |
| Surface 17 | Dashboard API Route Coverage Contract — validates api.ts→route handler→middleware mapping |
| 3-layer proxy | Backend API (8091) → Next.js Route Handlers → api.ts functions → React Components |
| Drift detection | Surface 17 CHECK 3 — scans api.ts for new endpoints that don't have matching route handlers |

---

## 3. Pre-Flight (PF-1 through PF-5)

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-drc-001-pf1.txt
```
**PASS if:** Exit 0. If not, stop — codebase is broken before QA starts.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-drc-001-pf2.txt
```
**PASS if:** Exit 0 with no errors. Zero TypeScript type errors in the dashboard.

### PF-3: Surface 17 Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-surface17 2>&1 | tee /tmp/qa-drc-001-pf3.txt
```
**PASS if:** Exit 0, output contains "43/43 PASS" with 0 FAIL. WARNs are acceptable.

### PF-4: Four-Way Consistency
```bash
cd /home/zaks/zakops-agent-api && bash tools/infra/validate-surface-count-consistency.sh 2>&1 | tee /tmp/qa-drc-001-pf4.txt
```
**PASS if:** Output shows "PASS: All 4 sources agree: 17 surfaces".

### PF-5: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence && echo "READY" | tee /tmp/qa-drc-001-pf5.txt
```
**PASS if:** Output shows "READY".

---

## 4. Verification Families

## Verification Family 01 — Route Handler Existence & Pattern Compliance (Completion Report §3.1)

Verifies all 10 new route handler files exist, use the correct pattern (backendFetch import, try/catch 502, async params), and proxy to the correct backend path.

### VF-01.1: All 10 new route handler files exist
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-01.1-file-existence.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard/src/app/api
FILES=(
  "quarantine/[id]/route.ts"
  "quarantine/bulk-process/route.ts"
  "quarantine/bulk-delete/route.ts"
  "quarantine/[id]/undo-approve/route.ts"
  "actions/capabilities/route.ts"
  "actions/[id]/approve/route.ts"
  "actions/[id]/cancel/route.ts"
  "actions/[id]/retry/route.ts"
  "actions/[id]/update/route.ts"
  "actions/metrics/route.ts"
)
PASS=0; FAIL=0
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    echo "EXISTS: $f"; ((PASS++))
  else
    echo "MISSING: $f"; ((FAIL++))
  fi
done
echo "Result: $PASS/10 exist, $FAIL missing" | tee "$EVIDENCE"
```
**PASS if:** 10/10 exist, 0 missing.

### VF-01.2: All 10 route handlers import `backendFetch` from `@/lib/backend-fetch`
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-01.2-backendFetch-import.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
grep -rl "from '@/lib/backend-fetch'" \
  src/app/api/quarantine/\[id\]/route.ts \
  src/app/api/quarantine/bulk-process/route.ts \
  src/app/api/quarantine/bulk-delete/route.ts \
  src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  src/app/api/actions/capabilities/route.ts \
  src/app/api/actions/\[id\]/approve/route.ts \
  src/app/api/actions/\[id\]/cancel/route.ts \
  src/app/api/actions/\[id\]/retry/route.ts \
  src/app/api/actions/\[id\]/update/route.ts \
  src/app/api/actions/metrics/route.ts \
  2>&1 | tee "$EVIDENCE"
```
**PASS if:** All 10 file paths appear in the output (each imports backendFetch).

### VF-01.3: All route handlers have try/catch with 502 JSON error response
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-01.3-error-pattern.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
grep -rl "backend_unavailable" \
  src/app/api/quarantine/\[id\]/route.ts \
  src/app/api/quarantine/bulk-process/route.ts \
  src/app/api/quarantine/bulk-delete/route.ts \
  src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  src/app/api/actions/capabilities/route.ts \
  src/app/api/actions/\[id\]/approve/route.ts \
  src/app/api/actions/\[id\]/cancel/route.ts \
  src/app/api/actions/\[id\]/retry/route.ts \
  src/app/api/actions/\[id\]/update/route.ts \
  src/app/api/actions/metrics/route.ts \
  2>&1 | tee "$EVIDENCE"
```
**PASS if:** All 10 file paths appear in the output (each has the 502 error pattern).

### VF-01.4: Dynamic route handlers use Next.js 15 async params pattern
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-01.4-async-params.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
# All dynamic [id] routes must use: { params }: { params: Promise<{ id: string }> }
grep -n "params.*Promise" \
  src/app/api/quarantine/\[id\]/route.ts \
  src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  src/app/api/actions/\[id\]/approve/route.ts \
  src/app/api/actions/\[id\]/cancel/route.ts \
  src/app/api/actions/\[id\]/retry/route.ts \
  src/app/api/actions/\[id\]/update/route.ts \
  2>&1 | tee "$EVIDENCE"
```
**PASS if:** All 6 dynamic-param route files appear with the `Promise<{ id: string }>` pattern. Static routes (bulk-process, bulk-delete, capabilities, metrics) should NOT appear.

### VF-01.5: Timeout values match completion report claims
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-01.5-timeouts.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
echo "=== 60s timeout (bulk operations) ==="
grep -n "timeoutMs.*60000" \
  src/app/api/quarantine/bulk-process/route.ts \
  src/app/api/quarantine/bulk-delete/route.ts
echo "=== 30s timeout (action mutations + undo) ==="
grep -n "timeoutMs.*30000" \
  src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  src/app/api/actions/\[id\]/approve/route.ts \
  src/app/api/actions/\[id\]/cancel/route.ts \
  src/app/api/actions/\[id\]/retry/route.ts \
  src/app/api/actions/\[id\]/update/route.ts
echo "=== No explicit timeout (GET routes — use backendFetch default) ==="
grep -c "timeoutMs" \
  src/app/api/quarantine/\[id\]/route.ts \
  src/app/api/actions/capabilities/route.ts \
  src/app/api/actions/metrics/route.ts 2>&1 || true
echo "DONE" | tee "$EVIDENCE"
```
**PASS if:** bulk-process and bulk-delete show 60000. undo-approve, approve, cancel, retry, update show 30000. GET-only routes (quarantine/[id], capabilities, metrics) show 0 matches.

### VF-01.6: Backend proxy paths are correct
Manually read each route handler and verify the backendFetch URL matches the backend endpoint path from the completion report:
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-01.6-proxy-paths.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
echo "=== Quarantine routes ==="
grep -n "backendFetch\|/api/quarantine" src/app/api/quarantine/\[id\]/route.ts
grep -n "backendFetch\|/api/quarantine" src/app/api/quarantine/bulk-process/route.ts
grep -n "backendFetch\|/api/quarantine" src/app/api/quarantine/bulk-delete/route.ts
grep -n "backendFetch\|/api/quarantine" src/app/api/quarantine/\[id\]/undo-approve/route.ts
echo "=== Actions routes ==="
grep -n "backendFetch\|/api/actions" src/app/api/actions/capabilities/route.ts
grep -n "backendFetch\|/api/actions" src/app/api/actions/\[id\]/approve/route.ts
grep -n "backendFetch\|/api/actions" src/app/api/actions/\[id\]/cancel/route.ts
grep -n "backendFetch\|/api/actions" src/app/api/actions/\[id\]/retry/route.ts
grep -n "backendFetch\|/api/actions" src/app/api/actions/\[id\]/update/route.ts
grep -n "backendFetch\|/api/actions" src/app/api/actions/metrics/route.ts
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Each route handler proxies to the matching backend path listed in §3.1 table:
- `quarantine/[id]` → `/api/quarantine/${id}`
- `quarantine/bulk-process` → `/api/quarantine/bulk-process`
- `quarantine/bulk-delete` → `/api/quarantine/bulk-delete`
- `quarantine/[id]/undo-approve` → `/api/quarantine/${id}/undo-approve`
- `actions/capabilities` → `/api/actions/capabilities`
- `actions/[id]/approve` → `/api/actions/${actionId}/approve`
- `actions/[id]/cancel` → `/api/actions/${actionId}/cancel`
- `actions/[id]/retry` → `/api/actions/${actionId}/retry`
- `actions/[id]/update` → `/api/actions/${actionId}/update`
- `actions/metrics` → `/api/actions/metrics`

### VF-01.7: HTTP method exports match completion report
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-01.7-http-methods.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
echo "=== GET exports ==="
grep -l "export.*async.*function GET" \
  src/app/api/quarantine/\[id\]/route.ts \
  src/app/api/actions/capabilities/route.ts \
  src/app/api/actions/metrics/route.ts 2>&1
echo "=== POST exports ==="
grep -l "export.*async.*function POST" \
  src/app/api/quarantine/bulk-process/route.ts \
  src/app/api/quarantine/bulk-delete/route.ts \
  src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  src/app/api/actions/\[id\]/approve/route.ts \
  src/app/api/actions/\[id\]/cancel/route.ts \
  src/app/api/actions/\[id\]/retry/route.ts \
  src/app/api/actions/\[id\]/update/route.ts 2>&1
echo "DONE" | tee "$EVIDENCE"
```
**PASS if:** GET routes appear under GET exports. POST routes appear under POST exports. No mismatches.

**Gate VF-01:** All 7 checks pass. Route handlers are correctly created, use the standard pattern, and proxy to the right backend paths.

---

## Verification Family 02 — Method Addition & Middleware Routing (Completion Report §3.2, §3.3)

### VF-02.1: actions/[id]/route.ts exports both GET and DELETE
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-02.1-actions-id-methods.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
grep -n "export.*async.*function" src/app/api/actions/\[id\]/route.ts 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Output shows both `GET` and `DELETE` function exports.

### VF-02.2: Middleware handledByRoutes contains all 13 required prefixes
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-02.2-middleware-prefixes.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
# Extract the handledByRoutes array and verify all 13 prefixes
sed -n '/const handledByRoutes/,/\];/p' src/middleware.ts 2>&1 | tee "$EVIDENCE"
```
**PASS if:** The array contains ALL 13 prefixes, including the 3 new ones:
1. `/api/actions/`
2. `/api/chat`
3. `/api/events`
4. `/api/agent/`
5. `/api/alerts`
6. `/api/checkpoints`
7. `/api/deferred-actions`
8. `/api/pipeline`
9. `/api/quarantine/health`
10. `/api/quarantine/`
11. `/api/settings/` (NEW)
12. `/api/onboarding` (NEW)
13. `/api/user` (NEW)

### VF-02.3: Middleware prefix matching logic is correct
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-02.3-middleware-logic.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
# The for-loop match logic should handle exact match AND prefix match
grep -A3 "for (const prefix of handledByRoutes)" src/middleware.ts 2>&1 | tee "$EVIDENCE"
```
**PASS if:** The condition handles both exact match (`=== prefix`) and prefix starts-with (`startsWith(prefix + '/')` or `startsWith(prefix)`).

**Gate VF-02:** All 3 checks pass. Method addition and middleware routing are correct.

---

## Verification Family 03 — Bug Fixes (Completion Report §4)

### VF-03.1: Chat fallback `final_text` fix (§4.1)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-03.1-chat-final-text.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
# Strategy 3 done event must include final_text: helpfulResponse
grep -n "final_text" src/app/api/chat/route.ts 2>&1 | tee "$EVIDENCE"
```
**PASS if:** There is a `final_text: helpfulResponse` (or equivalent variable reference) in the Strategy 3 fallback done event. The line should be near line 247 per the completion report.

### VF-03.2: Activity CSS overlay fix (§4.2)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-03.2-activity-css.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
# #runs-section div must NOT have permanent p-2 -m-2
# It should only have these classes conditionally (during highlight state)
grep -n "runs-section\|p-2 -m-2\|highlightedStat.*runs" src/app/agent/activity/page.tsx 2>&1 | tee "$EVIDENCE"
```
**PASS if:** `p-2 -m-2` is NOT a permanent class on the runs-section element. It should appear only within a conditional expression gated by `highlightedStat === 'runs'` or similar.

### VF-03.3: Quarantine `working` state derived (not useState) (§4.3)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-03.3-quarantine-working.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
echo "=== Should find derived working state ==="
grep -n "const working" src/app/quarantine/page.tsx
echo "=== Should NOT find setWorking ==="
grep -c "setWorking" src/app/quarantine/page.tsx 2>/dev/null || echo "0 matches (CORRECT)"
echo "=== Verify working uses derived state (OR of individual states) ==="
grep -A1 "const working" src/app/quarantine/page.tsx
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:**
- `const working = approving || rejecting || escalating || bulkProcessing || deleting` (or similar derived expression)
- `setWorking` does NOT appear anywhere in the file (0 matches)
- No `useState(false)` for `working`

### VF-03.4: Dead code deletion verified (§4.4)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-03.4-dead-code-deleted.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
if [ -f "src/app/api/actions/quarantine/[actionId]/preview/route.ts" ]; then
  echo "FAIL: Dead code file still exists"
else
  echo "PASS: Dead code file correctly deleted"
fi
# Also check parent directories are clean
ls -la src/app/api/actions/quarantine/ 2>&1 || echo "PASS: quarantine dir under actions also cleaned up"
echo "DONE" | tee "$EVIDENCE"
```
**PASS if:** The file `actions/quarantine/[actionId]/preview/route.ts` does NOT exist.

**Gate VF-03:** All 4 checks pass. All bug fixes are correctly applied and dead code is removed.

---

## Verification Family 04 — Surface 17 Validator & Registration (Completion Report §2.2, §5.1)

### VF-04.1: Surface 17 validator script exists and is executable
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-04.1-validator-exists.txt"
cd /home/zaks/zakops-agent-api
ls -la tools/infra/validate-surface17.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** File exists. Ownership is `zaks:zaks`.

### VF-04.2: Surface 17 validator runs clean with evidence
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-04.2-validator-run.txt"
cd /home/zaks/zakops-agent-api && bash tools/infra/validate-surface17.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Output shows 43/43 PASS, 0 FAIL. WARNs are acceptable per completion report (3 expected for proxy-only endpoints).

### VF-04.3: Surface 17 registered in validate-contract-surfaces.sh
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-04.3-validator-registration.txt"
cd /home/zaks/zakops-agent-api
grep -n "surface17\|Surface 17\|S17\|validate-surface17" tools/infra/validate-contract-surfaces.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** The unified validator references Surface 17 and calls validate-surface17.sh.

### VF-04.4: Surface 17 in CLAUDE.md
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-04.4-claudemd.txt"
cd /home/zaks/zakops-agent-api
grep -n "17.*Route Coverage\|Route Coverage.*17\|Dashboard Route Coverage" CLAUDE.md 2>&1 | tee "$EVIDENCE"
```
**PASS if:** CLAUDE.md lists Surface 17 as "Dashboard Route Coverage" and shows "17 Total".

### VF-04.5: Surface 17 in contract-surfaces.md
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-04.5-contract-surfaces-rule.txt"
cd /home/zaks/zakops-agent-api
grep -A5 "Surface 17" .claude/rules/contract-surfaces.md 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Surface 17 is defined with boundary description, validation command, and key files listed.

### VF-04.6: Surface 17 in INFRASTRUCTURE_MANIFEST.md
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-04.6-manifest.txt"
cd /home/zaks/zakops-agent-api
grep -n "17 Total\|Surface 17\|Route Coverage" INFRASTRUCTURE_MANIFEST.md 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Manifest shows "17 Total" and lists Surface 17.

### VF-04.7: Makefile targets registered
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-04.7-makefile-targets.txt"
cd /home/zaks/zakops-agent-api
grep -n "validate-surface17:\|validate-endpoint-liveness:\|smoke-test:" Makefile 2>&1 | tee "$EVIDENCE"
```
**PASS if:** All 3 targets (`validate-surface17`, `validate-endpoint-liveness`, `smoke-test`) are defined in the Makefile.

**Gate VF-04:** All 7 checks pass. Surface 17 is fully registered across all infrastructure sources.

---

## Verification Family 05 — Endpoint Liveness & Smoke Test Scripts (Completion Report §2.3, §2.4)

### VF-05.1: Endpoint liveness probe script exists
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-05.1-liveness-exists.txt"
cd /home/zaks/zakops-agent-api
ls -la tools/infra/validate-endpoint-liveness.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** File exists. Ownership is `zaks:zaks`.

### VF-05.2: Liveness probe covers 15+ GET endpoints (per completion report)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-05.2-liveness-coverage.txt"
cd /home/zaks/zakops-agent-api
grep -c "curl\|http://localhost:3003/api/" tools/infra/validate-endpoint-liveness.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** At least 15 curl targets or endpoint references are present.

### VF-05.3: Liveness probe has pre-flight reachability checks
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-05.3-liveness-preflight.txt"
cd /home/zaks/zakops-agent-api
grep -n "3003\|8091\|SKIP\|reachab" tools/infra/validate-endpoint-liveness.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Script checks dashboard (3003) and backend (8091) reachability before running probes, with SKIP behavior when either is down.

### VF-05.4: Smoke test script exists
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-05.4-smoke-exists.txt"
cd /home/zaks/zakops-agent-api
ls -la tools/infra/smoke-test.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** File exists. Ownership is `zaks:zaks`.

### VF-05.5: Smoke test covers 9 dashboard pages (per completion report)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-05.5-smoke-coverage.txt"
cd /home/zaks/zakops-agent-api
grep -c "localhost:3003\|/dashboard\|/deals\|/actions\|/quarantine\|/chat\|/agent\|/hq\|/settings\|/onboarding" tools/infra/smoke-test.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** At least 9 page paths are referenced.

**Gate VF-05:** All 5 checks pass. Liveness probe and smoke test are correctly implemented.

---

## Verification Family 06 — Infrastructure Fix Accuracy (Completion Report §5)

### VF-06.1: validate-contract-surfaces.sh says "all 17" (not 16)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-06.1-validator-count.txt"
cd /home/zaks/zakops-agent-api
grep -n "all.*17.*contract\|all.*contract.*17" tools/infra/validate-contract-surfaces.sh | head -3
grep -c "all.*16.*contract" tools/infra/validate-contract-surfaces.sh 2>/dev/null || echo "0 stale references"
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Shows "all 17 contract" and 0 stale "16" references.

### VF-06.2: validate-surface-count-consistency.sh uses EXPECTED=17
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-06.2-consistency-expected.txt"
cd /home/zaks/zakops-agent-api
grep -n "EXPECTED=\|expected=" tools/infra/validate-surface-count-consistency.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Expected count is set to 17 (not 16).

### VF-06.3: No stale "16 surfaces" references in infrastructure files
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-06.3-stale-16.txt"
cd /home/zaks/zakops-agent-api
grep -rn "16 Total\|16 contract\|16 surfaces" CLAUDE.md INFRASTRUCTURE_MANIFEST.md tools/infra/validate-contract-surfaces.sh tools/infra/validate-surface-count-consistency.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Zero matches — no stale references to 16 surfaces remain.

**Gate VF-06:** All 3 checks pass. Infrastructure counts are consistent at 17.

---

## Verification Family 07 — File Ownership & WSL Safety (Completion Report §6.3)

### VF-07.1: All new route handler files owned by zaks:zaks
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-07.1-route-ownership.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard/src/app/api
ls -la quarantine/*/route.ts quarantine/bulk-*/route.ts actions/*/route.ts actions/[id]/*/route.ts actions/capabilities/route.ts actions/metrics/route.ts 2>&1 | tee "$EVIDENCE"
```
**PASS if:** All files are owned by `zaks:zaks` (not `root:root`).

### VF-07.2: Infrastructure scripts owned by zaks:zaks
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-07.2-script-ownership.txt"
cd /home/zaks/zakops-agent-api
ls -la tools/infra/validate-surface17.sh tools/infra/validate-endpoint-liveness.sh tools/infra/smoke-test.sh 2>&1 | tee "$EVIDENCE"
```
**PASS if:** All 3 scripts are owned by `zaks:zaks`.

### VF-07.3: No CRLF in shell scripts
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-07.3-crlf-check.txt"
cd /home/zaks/zakops-agent-api
for f in tools/infra/validate-surface17.sh tools/infra/validate-endpoint-liveness.sh tools/infra/smoke-test.sh; do
  if grep -Pq '\r' "$f"; then
    echo "CRLF FOUND: $f"
  else
    echo "CLEAN: $f"
  fi
done 2>&1 | tee "$EVIDENCE"
```
**PASS if:** All 3 scripts show "CLEAN" (no CRLF).

**Gate VF-07:** All 3 checks pass. File ownership and WSL safety are correct.

---

## Verification Family 08 — System Health Audit Report (Completion Report §2.1)

### VF-08.1: System health audit report exists
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-08.1-audit-exists.txt"
ls -la /home/zaks/bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md 2>&1 | tee "$EVIDENCE"
```
**PASS if:** File exists.

### VF-08.2: Audit report contains all 5 issue categories
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-08.2-audit-categories.txt"
grep -c "Category 1:\|Category 2:\|Category 3:\|Category 4:\|Category 5:" /home/zaks/bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Count is 5 (all categories present).

### VF-08.3: Audit report scope exclusions match completion report
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/VF-08.3-scope-exclusions.txt"
grep -n "Out-of-Scope\|In-Scope\|backend" /home/zaks/bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md 2>&1 | tee "$EVIDENCE"
```
**PASS if:** In-scope items match what was remediated. Out-of-scope items match completion report §9.

**Gate VF-08:** All 3 checks pass. System health audit report is complete and accurate.

---

## 5. Cross-Consistency Checks (XC-1 through XC-5)

### XC-1: Completion Report File Count vs Actual Filesystem
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/XC-1-file-count.txt"
echo "Completion report claims: 13 created, 11 modified, 1 deleted"
echo "=== Verify created files ==="
cd /home/zaks/zakops-agent-api
CREATED=0
for f in \
  apps/dashboard/src/app/api/quarantine/\[id\]/route.ts \
  apps/dashboard/src/app/api/quarantine/bulk-process/route.ts \
  apps/dashboard/src/app/api/quarantine/bulk-delete/route.ts \
  apps/dashboard/src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  apps/dashboard/src/app/api/actions/capabilities/route.ts \
  apps/dashboard/src/app/api/actions/\[id\]/approve/route.ts \
  apps/dashboard/src/app/api/actions/\[id\]/cancel/route.ts \
  apps/dashboard/src/app/api/actions/\[id\]/retry/route.ts \
  apps/dashboard/src/app/api/actions/\[id\]/update/route.ts \
  apps/dashboard/src/app/api/actions/metrics/route.ts \
  tools/infra/validate-surface17.sh \
  tools/infra/validate-endpoint-liveness.sh; do
  [ -f "$f" ] && ((CREATED++))
done
echo "Created files found: $CREATED/12"
echo "(Note: bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md is the 13th — check separately)"
[ -f "/home/zaks/bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md" ] && echo "Health audit: EXISTS" || echo "Health audit: MISSING"
echo "=== Verify deleted file ==="
[ ! -f "apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts" ] && echo "Dead code: DELETED" || echo "Dead code: STILL EXISTS"
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:** 12/12 monorepo created files exist, health audit exists, dead code deleted.

### XC-2: Surface 17 Validator Manifest vs Actual Route Files
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/XC-2-manifest-vs-actual.txt"
cd /home/zaks/zakops-agent-api
echo "=== Surface 17 validator manifest entries ==="
grep -E "^#.*route\.ts|CHECK.*PASS|CHECK.*FAIL|CHECK.*WARN" <(bash tools/infra/validate-surface17.sh 2>&1) | head -50
echo "=== Actual route.ts files on disk ==="
find apps/dashboard/src/app/api -name "route.ts" | sort
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Every route.ts file on disk appears in the validator manifest (or has a documented reason for exclusion). No phantom entries in the manifest that don't correspond to actual files.

### XC-3: Completion Report Bug Fix Claims vs Actual Code
For each bug fix, verify the completion report description matches what's actually in the code.
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/XC-3-bugfix-crosscheck.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
echo "=== Bug 1: Chat final_text — expect helpfulResponse in done event ==="
grep -B2 -A2 "final_text" src/app/api/chat/route.ts
echo ""
echo "=== Bug 2: Activity CSS — expect conditional p-2 -m-2 ==="
grep -B2 -A2 "p-2 -m-2\|runs-section" src/app/agent/activity/page.tsx | head -20
echo ""
echo "=== Bug 3: Quarantine working — expect derived state ==="
grep -B1 -A1 "const working" src/app/quarantine/page.tsx
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Code matches the completion report descriptions exactly:
- Chat: `final_text: helpfulResponse` in done event
- Activity: `p-2 -m-2` conditional, not permanent
- Quarantine: `working` derived from individual state variables, not useState

### XC-4: Health Audit Findings vs Remediation Coverage
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/XC-4-audit-coverage.txt"
echo "=== Category 1: 12 missing route handlers — how many were created? ==="
echo "Report claims 10 new + 1 method addition = 11 fixes"
echo "Remaining: /api/actions GET (list) and /api/actions POST (create) — these are middleware-proxied, not route-handled"
echo ""
echo "=== Category 2: 3 middleware routing gaps — all fixed? ==="
cd /home/zaks/zakops-agent-api/apps/dashboard
grep "settings\|onboarding\|user" src/middleware.ts | grep -c "handledByRoutes\|'/api/settings\|'/api/onboarding\|'/api/user" 2>/dev/null || echo "0"
echo ""
echo "=== Category 4: 5 bugs — how many fixed? ==="
echo "Fixed: #1 (CSS), #2 (chat), #5 (working state) = 3 of 5"
echo "Out of scope: #3 (pipeline), #4 (terminal stage) = 2 — documented in completion report §9"
echo ""
echo "=== Category 5: 1 dead code — deleted? ==="
[ ! -f "src/app/api/actions/quarantine/[actionId]/preview/route.ts" ] && echo "DELETED" || echo "EXISTS"
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Category coverage aligns with completion report: Cat 1 remediated (minus 2 proxy-only), Cat 2 fully remediated, Cat 4 partially (3/5, 2 out-of-scope documented), Cat 5 fully remediated.

### XC-5: Smoke Test Script vs Completion Report Claim
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/XC-5-smoke-test.txt"
cd /home/zaks/zakops-agent-api
echo "=== Smoke test existence ==="
[ -f "tools/infra/smoke-test.sh" ] && echo "EXISTS" || echo "MISSING"
echo "=== Completion report claims: Playwright-based ==="
grep -c "playwright\|Playwright" tools/infra/smoke-test.sh 2>/dev/null || echo "0 playwright references"
echo "=== Page count ==="
grep -c "localhost:3003" tools/infra/smoke-test.sh 2>/dev/null || echo "0 page targets"
echo "DONE" 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Smoke test exists, references Playwright (or curl-based HTTP checks as alternative), and covers 9+ pages.

---

## 6. Stress Tests (ST-1 through ST-4)

### ST-1: Middleware routing precedence — quarantine/health vs quarantine/
The `handledByRoutes` array contains both `/api/quarantine/health` and `/api/quarantine/`. Verify that `/api/quarantine/health` is listed BEFORE `/api/quarantine/` to avoid incorrect prefix matching.
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/ST-1-routing-precedence.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
grep -n "quarantine" src/middleware.ts 2>&1 | tee "$EVIDENCE"
```
**PASS if:** `/api/quarantine/health` appears before `/api/quarantine/` in the array, OR the matching logic correctly handles this regardless of order (e.g., exact match takes priority).

### ST-2: New route handlers don't introduce Promise.all (banned pattern)
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/ST-2-promise-all-ban.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
grep -rn "Promise\.all" \
  src/app/api/quarantine/ \
  src/app/api/actions/ 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Zero matches. No route handler uses the banned `Promise.all` pattern.

### ST-3: No route handler imports from generated files directly
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/ST-3-generated-import-ban.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
grep -rn "api-types.generated\|agent-api-types.generated" \
  src/app/api/quarantine/ \
  src/app/api/actions/ 2>&1 | tee "$EVIDENCE"
```
**PASS if:** Zero matches. No route handler imports generated type files directly.

### ST-4: Console.error vs console.warn classification in route handlers
Per Surface 9 conventions, backend-unavailable catch blocks should use `console.warn` (expected degradation), not `console.error` (unexpected failure).
```bash
EVIDENCE="/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/ST-4-log-level.txt"
cd /home/zaks/zakops-agent-api/apps/dashboard
echo "=== console.error in new route handlers (should be 0 or minimal) ==="
grep -rn "console\.error" \
  src/app/api/quarantine/\[id\]/route.ts \
  src/app/api/quarantine/bulk-process/route.ts \
  src/app/api/quarantine/bulk-delete/route.ts \
  src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  src/app/api/actions/capabilities/route.ts \
  src/app/api/actions/\[id\]/approve/route.ts \
  src/app/api/actions/\[id\]/cancel/route.ts \
  src/app/api/actions/\[id\]/retry/route.ts \
  src/app/api/actions/\[id\]/update/route.ts \
  src/app/api/actions/metrics/route.ts 2>&1 || echo "0 matches"
echo "=== console.warn in new route handlers ==="
grep -rn "console\.warn" \
  src/app/api/quarantine/\[id\]/route.ts \
  src/app/api/quarantine/bulk-process/route.ts \
  src/app/api/quarantine/bulk-delete/route.ts \
  src/app/api/quarantine/\[id\]/undo-approve/route.ts \
  src/app/api/actions/capabilities/route.ts \
  src/app/api/actions/\[id\]/approve/route.ts \
  src/app/api/actions/\[id\]/cancel/route.ts \
  src/app/api/actions/\[id\]/retry/route.ts \
  src/app/api/actions/\[id\]/update/route.ts \
  src/app/api/actions/metrics/route.ts 2>&1 || echo "0 matches"
echo "DONE" | tee "$EVIDENCE"
```
**PASS if:** Backend-unavailable catch blocks use `console.warn` (or no logging at all — the 502 JSON response is sufficient). If `console.error` is used in catch blocks, classify as VIOLATION or INFO based on context.

---

## 7. Remediation Protocol

When a gate fails:

1. **Read the evidence file** — understand exactly what failed
2. **Classify the failure:**
   - `MISSING_FIX` — Completion report claimed a fix, but it's not in the code
   - `REGRESSION` — A previously working feature was broken by the remediation
   - `PATTERN_VIOLATION` — Code works but violates architectural constraints (e.g., Promise.all, console.error)
   - `INFRASTRUCTURE_GAP` — Registration or count is wrong
   - `FALSE_POSITIVE` — The gate command is wrong, not the code
   - `PARTIAL` — Fix is present but incomplete
3. **Apply the fix** following the original guardrails (per contract surface discipline, Surface 9, etc.)
4. **Re-run the specific gate** and capture new evidence
5. **Re-run `make validate-local`** to ensure no regressions
6. **Record in the completion report** with remediation ID (R-1, R-2, ...)

---

## 8. Enhancement Opportunities (ENH-1 through ENH-10)

### ENH-1: Route Handler Template/Generator
Create a CLI or slash command that scaffolds a new route handler from a template, ensuring pattern compliance (backendFetch import, try/catch 502, async params for dynamic routes) automatically. This would prevent the class of bugs that led to this remediation.

### ENH-2: Surface 17 Integration into validate-local
Consider adding `validate-surface17` to the `make validate-local` target so route coverage drift is caught in every session, not just when explicitly run.

### ENH-3: Middleware handledByRoutes Auto-Discovery
Instead of a manually maintained prefix array, have middleware auto-discover route handler directories. This eliminates the Category 2 failure class entirely.

### ENH-4: Runtime 404 Detection Dashboard Widget
Add a dashboard developer widget (dev-mode only) that highlights when api.ts calls return HTML instead of JSON, making proxy layer gaps immediately visible during development.

### ENH-5: Endpoint Liveness as CI Gate
Integrate `validate-endpoint-liveness` into the CI pipeline (when services are available in CI) as a non-blocking advisory check.

### ENH-6: Route Handler Unit Tests
Add unit tests for route handlers that mock `backendFetch` and verify correct URL construction, method usage, timeout values, and error handling.

### ENH-7: Category 3 Backend Endpoint Remediation
The 6 backend-missing endpoints (deals enrichment, tasks, case-file, materials, anomalies, briefing) remain broken. Create a dedicated backend mission to implement or deprecate these endpoints.

### ENH-8: Category 4 Remaining Bug Fixes
Two Category 4 bugs remain: pipeline "0 deals" display and "terminal stage" transition check. These may require backend investigation.

### ENH-9: Quarantine Working State Unit Test
The `working` derived state fix should have a test that verifies it correctly reflects the OR of all individual operation states.

### ENH-10: Surface 17 WARN Resolution
The 3 WARNs (proxy-only endpoints without route handlers) could be resolved by either: (a) documenting them as permanent exceptions in the manifest, or (b) creating minimal route handlers for them.

---

## 9. Scorecard Template

```
QA-DRC-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):           [ PASS / FAIL ]
  PF-2 (TypeScript):               [ PASS / FAIL ]
  PF-3 (Surface 17 baseline):      [ PASS / FAIL ]
  PF-4 (Four-way consistency):     [ PASS / FAIL ]
  PF-5 (Evidence directory):       [ PASS / FAIL ]

Verification Gates:
  VF-01 (Route Handlers):          __ / 7 gates PASS
  VF-02 (Method + Middleware):     __ / 3 gates PASS
  VF-03 (Bug Fixes):              __ / 4 gates PASS
  VF-04 (Surface 17 Registration): __ / 7 gates PASS
  VF-05 (Liveness & Smoke):       __ / 5 gates PASS
  VF-06 (Infra Fix Accuracy):     __ / 3 gates PASS
  VF-07 (Ownership & WSL):        __ / 3 gates PASS
  VF-08 (Health Audit Report):    __ / 3 gates PASS

Cross-Consistency:
  XC-1 (File count):              [ PASS / FAIL ]
  XC-2 (Manifest vs actual):      [ PASS / FAIL ]
  XC-3 (Bug fix cross-check):     [ PASS / FAIL ]
  XC-4 (Audit coverage):          [ PASS / FAIL ]
  XC-5 (Smoke test):              [ PASS / FAIL ]

Stress Tests:
  ST-1 (Routing precedence):      [ PASS / FAIL ]
  ST-2 (Promise.all ban):         [ PASS / FAIL ]
  ST-3 (Generated import ban):    [ PASS / FAIL ]
  ST-4 (Log level classification): [ PASS / FAIL ]

Total: __ / 49 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 10. Guardrails

1. **Scope fence:** This is a QA verification mission. Do NOT build new features, create new route handlers, or modify infrastructure beyond what's needed for remediation.
2. **Remediate, don't redesign:** If a route handler has a pattern violation, fix the specific issue — don't rewrite the handler.
3. **Evidence-based only:** Every PASS/FAIL needs evidence captured via `tee` to the evidence directory. "I checked and it's fine" is NOT evidence.
4. **Generated file protection:** Do NOT modify `*.generated.ts` or `*_models.py` files.
5. **Category 3 items are NOT failures:** Backend-missing endpoints are documented as out-of-scope. Mark as INFO/DEFERRED if encountered during verification.
6. **Surface 9 compliance:** Console.warn for expected degradation (backend-down), console.error for unexpected failures.
7. **WSL safety:** If creating any new .sh files during remediation, strip CRLF and fix ownership.
8. **Services-down accommodation:** If dashboard or backend isn't running, runtime verification gates (endpoint liveness, smoke test) become SKIP — not FAIL. Document as SKIP with reason.
9. **Preserve prior fixes:** Remediation must not revert any ET-VALIDATION-001 deliverables or other prior mission work.
10. **Per contract surface discipline:** If remediation changes any route handler, re-run `make validate-surface17` afterward.

---

## 11. Stop Condition

Stop when:
- All 49 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE with evidence)
- All remediations are applied and re-verified
- `make validate-local` passes
- `make validate-surface17` passes (43/43 PASS, 0 FAIL)
- The scorecard is complete with all gates filled
- The completion report is written to `/home/zaks/bookkeeping/docs/QA-DRC-VERIFY-001-COMPLETION.md`
- Evidence files are captured in `/home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/`
- CHANGES.md is updated

Do NOT:
- Fix the 6 backend-missing endpoints (Category 3)
- Fix the pipeline "0 deals" or "terminal stage" bugs (Category 4, #3 and #4)
- Add new features or refactor existing code beyond remediation scope
- Modify generated files

---

<!-- Adopted from Improvement Area IA-2: Crash Recovery Protocol -->
## Crash Recovery

If resuming after a session crash, determine current state:
1. `ls /home/zaks/bookkeeping/qa-verifications/QA-DRC-VERIFY-001/evidence/` — see which evidence files already exist
2. `cd /home/zaks/zakops-agent-api && make validate-local` — verify codebase is still clean
3. Check the last evidence file created to determine which gate was in progress
4. Resume from the next unverified gate

---

*End of Mission Prompt — QA-DRC-VERIFY-001*

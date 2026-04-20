# MISSION: QA-SR-VERIFY-001
## QA Verification & Remediation — SURFACE-REMEDIATION-001 + 002 Combined Audit
## Date: 2026-02-10
## Classification: QA Verification — Infrastructure Remediation
## Prerequisite: SURFACE-REMEDIATION-001 (complete) + SURFACE-REMEDIATION-002 (complete or attempted)
## Successor: SURFACE-IMPL-001 (blocked until this QA passes)

---

## Mission Objective

Independently verify that both SURFACE-REMEDIATION missions achieved what they claimed. V1 performed surgical fixes on 15 audit findings and created 4 reference documents. V2 performed full-stack sweeps across all 4 repositories for the same 7 anti-patterns. This QA verifies every acceptance criterion from both missions, cross-checks between them, stress-tests edge cases, and remediates any failures found.

**Source missions:**
- V1: `/home/zaks/bookkeeping/docs/MISSION-SURFACE-REMEDIATION-001.md` (309 lines, 7 AC, 5 phases)
- V2: `/home/zaks/bookkeeping/docs/MISSION-SURFACE-REMEDIATION-002.md` (311 lines, 9 AC, 7 sweeps)
- Forensic audit: `/home/zaks/bookkeeping/docs/FORENSIC-AUDIT-RESULTS-FORENSIC-AUDIT-SURFACES-002` (1,229 lines)

**Evidence artifacts from V1:**
- `/home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md` (95 lines)
- `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md` (104 lines)
- `/home/zaks/bookkeeping/docs/ERROR-SHAPES.md` (158 lines)
- `/home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md` (270 lines)

**Evidence artifacts from V2 (if executed):**
- `/home/zaks/bookkeeping/docs/SWEEP-002-DISCOVERY.md`
- `/home/zaks/bookkeeping/docs/SURFACE-REMEDIATION-002-COMPLETION.md`

---

## Pre-Flight

Before any verification gates, establish baseline:

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-sr-preflight-validate.txt
echo "EXIT: $?"
```
**PASS if:** exit 0. If not, stop — the codebase is broken before QA starts.

### PF-2: V2 Execution Status
```bash
ls -la /home/zaks/bookkeeping/docs/SWEEP-002-DISCOVERY.md 2>/dev/null && echo "V2_DISCOVERY=EXISTS" || echo "V2_DISCOVERY=MISSING"
ls -la /home/zaks/bookkeeping/docs/SURFACE-REMEDIATION-002-COMPLETION.md 2>/dev/null && echo "V2_COMPLETION=EXISTS" || echo "V2_COMPLETION=MISSING"
```
**Record result.** If V2 was not executed, all VF-06 through VF-12 gates become **EXECUTE + VERIFY** (run the sweep yourself, then verify). If V2 was executed, gates become **VERIFY ONLY**.

### PF-3: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-sr-preflight-tsc.txt
echo "EXIT: $?"
```
**PASS if:** exit 0.

---

## Verification Family 01 — Port Drift Elimination (V1 Phase 1 + V2 Sweep 1)

### VF-01.1: Dashboard Makefile — Zero 8090
```bash
grep -n "8090" /home/zaks/zakops-agent-api/apps/dashboard/Makefile 2>&1 | tee /tmp/qa-sr-vf01-1.txt
```
**PASS if:** Zero hits, OR all hits are in comments explaining decommission.

### VF-01.2: Dashboard smoke-test.sh — Zero 8090
```bash
grep -rn "8090" /home/zaks/zakops-agent-api/apps/dashboard/smoke-test.sh 2>/dev/null | tee /tmp/qa-sr-vf01-2.txt
echo "EXIT: $?"
```
**PASS if:** Zero hits or file doesn't exist.

### VF-01.3: Full-Stack Port 8090 Sweep (V2 Sweep 1)
```bash
grep -rn "8090" /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" --include="*.sh" \
  --include="*.yml" --include="*.yaml" --include="*.json" --include="*.md" --include="Makefile" \
  2>/dev/null | grep -v node_modules | grep -v ".next/" | grep -v __pycache__ | grep -v ".git/" \
  | grep -v "\.lock" | grep -v "package-lock" \
  | tee /tmp/qa-sr-vf01-3.txt
wc -l < /tmp/qa-sr-vf01-3.txt
```
**PASS if:** Every remaining hit is classified as one of: comment, migration file, lock/dependency file, generated file, or documentation about the decommission. Zero active code/config paths reference 8090.

### VF-01.4: RAG Health Endpoint Alignment
```bash
grep -n "health" /home/zaks/zakops-agent-api/apps/agent-api/app/core/resilience.py 2>&1 | tee /tmp/qa-sr-vf01-4a.txt
grep -n "health\|def.*check\|\.get(" /home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_rest.py 2>&1 | tee /tmp/qa-sr-vf01-4b.txt
```
**PASS if:** The health endpoint path declared in resilience.py for RAG matches the actual endpoint called in rag_rest.py (both should be `/` since RAG exposes health at root).

### VF-01.5: URL Variable Documentation in Middleware
```bash
head -40 /home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts 2>&1 | tee /tmp/qa-sr-vf01-5.txt
```
**PASS if:** A comment block exists documenting the URL variable mapping (API_URL, BACKEND_URL, NEXT_PUBLIC_API_URL, AGENT_API_URL, AGENT_LOCAL_URL) with which is canonical.

### VF-01.6: External Script Path Fixed
```bash
grep -n "chat_benchmark\|/home/zaks/scripts/" /home/zaks/zakops-agent-api/apps/dashboard/Makefile 2>&1 | tee /tmp/qa-sr-vf01-6.txt
```
**PASS if:** Zero references to `/home/zaks/scripts/` (external path). Any benchmark reference uses monorepo-relative path or the target has been removed.

**Gate VF-01:** All 6 checks pass. Port 8090 is eliminated full-stack.

---

## Verification Family 02 — Promise.allSettled Enforcement (V1 Phase 2 + V2 Sweep 2)

### VF-02.1: Pipeline Route — Specific Fix Verification
```bash
grep -n "Promise\." /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/pipeline/route.ts 2>&1 | tee /tmp/qa-sr-vf02-1.txt
```
**PASS if:** Only `Promise.allSettled` appears. Zero `Promise.all(` without `Settled`.

### VF-02.2: Pipeline Route — Typed Empty Fallbacks
Read `apps/dashboard/src/app/api/pipeline/route.ts` and verify that `Promise.allSettled` results are handled with typed empty fallbacks on rejection (not throwing on partial failure). The pattern must match the Deal Integrity mandate.
**PASS if:** Each `allSettled` result checks `status === 'fulfilled'` and provides a typed fallback for `'rejected'`.

### VF-02.3: Full-Stack Promise.all Sweep — Dashboard Source
```bash
grep -rn "Promise\.all(" /home/zaks/zakops-agent-api/apps/dashboard/src/ \
  --include="*.ts" --include="*.tsx" \
  2>/dev/null | grep -v node_modules | grep -v "Promise\.allSettled" \
  | tee /tmp/qa-sr-vf02-3.txt
wc -l < /tmp/qa-sr-vf02-3.txt
```
**PASS if:** Zero hits, OR every remaining hit has a documented justification (non-data-fetching use, test mock, build utility). Each unjustified hit is a FAIL that requires remediation.

### VF-02.4: Promise.all in Server API Routes (High Priority)
```bash
grep -rn "Promise\.all(" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/ \
  --include="*.ts" \
  2>/dev/null | grep -v "Promise\.allSettled" \
  | tee /tmp/qa-sr-vf02-4.txt
wc -l < /tmp/qa-sr-vf02-4.txt
```
**PASS if:** Strictly zero hits. Server API routes are the highest priority — no exceptions.

### VF-02.5: Promise.all in Page Components (Data-Fetching)
```bash
grep -rn "Promise\.all(" /home/zaks/zakops-agent-api/apps/dashboard/src/app/ \
  --include="*.tsx" \
  2>/dev/null | grep -v "Promise\.allSettled" \
  | tee /tmp/qa-sr-vf02-5.txt
wc -l < /tmp/qa-sr-vf02-5.txt
```
**PASS if:** Zero hits in page components. These are server-rendered data-fetching paths.

**Gate VF-02:** All 5 checks pass. Promise.all is fully eradicated from data-fetching paths.

---

## Verification Family 03 — Console Log Level Compliance (V1 Phase 2 + V2 Sweep 3)

### VF-03.1: Agent Activity Route — Specific Fix
```bash
grep -n "console\.\(error\|warn\)" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/agent/activity/route.ts 2>&1 | tee /tmp/qa-sr-vf03-1.txt
```
**PASS if:** Degradation paths (backend unreachable, empty data) use `console.warn`. Only genuinely unexpected failures use `console.error`.

### VF-03.2: Full Dashboard Server Route Sweep
```bash
grep -rn "console\.error" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/ \
  --include="*.ts" --include="*.tsx" \
  2>/dev/null | tee /tmp/qa-sr-vf03-2.txt
wc -l < /tmp/qa-sr-vf03-2.txt
```
**Action:** For each hit, read surrounding context (10 lines above/below). Classify as:
- **CORRECT** — genuinely unexpected failure (data corruption, invariant violation, unrecoverable error)
- **VIOLATION** — expected degradation (backend down, timeout, partial data, feature unavailable)

**PASS if:** Zero VIOLATION classifications. Every `console.error` in server API routes guards a genuinely unexpected failure.

### VF-03.3: Full Dashboard Source Sweep (Beyond API Routes)
```bash
grep -rn "console\.error" /home/zaks/zakops-agent-api/apps/dashboard/src/ \
  --include="*.ts" --include="*.tsx" \
  2>/dev/null | grep -v node_modules | grep -v "__tests__" | grep -v "\.test\." | grep -v "\.spec\." \
  | tee /tmp/qa-sr-vf03-3.txt
wc -l < /tmp/qa-sr-vf03-3.txt
```
**PASS if:** Each hit is classified. All expected-degradation cases use `console.warn`. Evidence table provided.

### VF-03.4: Agent-API Logger Level Sweep
```bash
grep -rn "logger\.error" /home/zaks/zakops-agent-api/apps/agent-api/app/ \
  --include="*.py" \
  2>/dev/null | grep -v __pycache__ | grep -v tests/ \
  | tee /tmp/qa-sr-vf03-4.txt
wc -l < /tmp/qa-sr-vf03-4.txt
```
**PASS if:** Each hit classified. Expected degradation (RAG unreachable, optional service timeout) uses `logger.warning`. Unexpected failures use `logger.error`.

### VF-03.5: Surface 9 Manifest Cross-Check
Read `apps/dashboard/src/types/design-system-manifest.ts` and confirm it declares the `console.warn` for degradation / `console.error` for unexpected convention. Then verify VF-03.2 through VF-03.4 classifications are consistent with this declaration.
**PASS if:** Classifications align with Surface 9 manifest.

**Gate VF-03:** All 5 checks pass. Log levels are Surface 9 compliant across the full stack.

---

## Verification Family 04 — FSM Stage Name Integrity (V1 Phase 3 + V2 Sweep 4)

### VF-04.1: Canonical Stage Source of Truth
```bash
grep -n "STAGE_TRANSITIONS\|DealStage\|class.*Stage" /home/zaks/zakops-backend/src/core/deals/workflow.py 2>&1 | head -30 | tee /tmp/qa-sr-vf04-1.txt
```
**Record:** The canonical stages. Expected: inbound, screening, qualified, loi, diligence, closing, portfolio, junk, archived.

### VF-04.2: Backend Test Files — Zero Legacy Stages
```bash
grep -rni "initial_review\|due_diligence\|closed_won\|closed_lost\|under_review\|negotiation\|prospecting" \
  /home/zaks/zakops-backend/tests/ \
  --include="*.py" \
  2>/dev/null | tee /tmp/qa-sr-vf04-2.txt
wc -l < /tmp/qa-sr-vf04-2.txt
```
**PASS if:** Zero hits.

### VF-04.3: Backend Source Code — Zero Legacy Stages
```bash
grep -rni "initial_review\|due_diligence\|closed_won\|closed_lost\|under_review\|negotiation\|prospecting" \
  /home/zaks/zakops-backend/src/ \
  --include="*.py" \
  2>/dev/null | grep -v __pycache__ | grep -v "migration" \
  | tee /tmp/qa-sr-vf04-3.txt
wc -l < /tmp/qa-sr-vf04-3.txt
```
**PASS if:** Zero hits (excluding migration files).

### VF-04.4: Monorepo — Zero Legacy Stages
```bash
grep -rni "initial_review\|due_diligence\|closed_won\|closed_lost\|under_review\|negotiation\|prospecting" \
  /home/zaks/zakops-agent-api/ \
  --include="*.ts" --include="*.tsx" --include="*.py" --include="*.json" \
  2>/dev/null | grep -v node_modules | grep -v ".next/" | grep -v __pycache__ | grep -v ".git/" \
  | tee /tmp/qa-sr-vf04-4.txt
wc -l < /tmp/qa-sr-vf04-4.txt
```
**PASS if:** Zero hits (excluding generated files and migration files).

### VF-04.5: "lead" Stage in Test Context
```bash
grep -rni "\"lead\"\|'lead'" \
  /home/zaks/zakops-backend/tests/ /home/zaks/zakops-agent-api/apps/dashboard/tests/ \
  --include="*.py" --include="*.ts" \
  2>/dev/null | tee /tmp/qa-sr-vf04-5.txt
wc -l < /tmp/qa-sr-vf04-5.txt
```
**PASS if:** Zero hits where "lead" is used as a stage name. Hits where "lead" refers to a deal type or contact role are acceptable (document justification).

### VF-04.6: Playwright Spec — Bulk Delete Navigation
```bash
grep -n "goto\|expect.*url\|page\.\|toHaveURL\|waitForURL" \
  /home/zaks/zakops-agent-api/apps/dashboard/tests/deals-bulk-delete.spec.ts 2>&1 \
  | tee /tmp/qa-sr-vf04-6.txt
```
**PASS if:** Navigation URL and URL assertions are consistent (both reference the same page). The spec does not navigate to `/deals` and then assert `/deals-bulk-delete`.

**Gate VF-04:** All 6 checks pass. Legacy FSM stage names are eradicated full-stack.

---

## Verification Family 05 — Environment & Config Hygiene (V1 Phase 4 + V2 Sweeps 5–6)

### VF-05.1: Dashboard README Accuracy
```bash
grep -ni "env.example.txt\|env\.example\.txt\|feature.flag\|FEATURE_" \
  /home/zaks/zakops-agent-api/apps/dashboard/README.md 2>&1 \
  | tee /tmp/qa-sr-vf05-1.txt
```
**PASS if:** Zero references to non-existent files (env.example.txt) or non-existent feature flags.

### VF-05.2: Agent-API .env.example Completeness
Read `apps/agent-api/app/core/config.py` and extract every environment variable it reads. Compare against `apps/agent-api/.env.example`.
```bash
grep -n "os\.getenv\|os\.environ\|Field.*env=" /home/zaks/zakops-agent-api/apps/agent-api/app/core/config.py 2>&1 | tee /tmp/qa-sr-vf05-2a.txt
cat /home/zaks/zakops-agent-api/apps/agent-api/.env.example | tee /tmp/qa-sr-vf05-2b.txt
```
**PASS if:** Every required variable (no default in code) appears in .env.example. Variables with sensible defaults in code are optional but recommended to include.

### VF-05.3: Hardcoded Secrets in Deployment Compose
```bash
grep -n "DASHBOARD_SERVICE_TOKEN\|SERVICE_TOKEN\|SECRET\|PASSWORD\|API_KEY" \
  /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml 2>&1 \
  | tee /tmp/qa-sr-vf05-3.txt
```
**PASS if:** No secret variables have hardcoded literal values. All use `${VAR:?...}` or `${VAR}` without defaults.

### VF-05.4: Full-Stack Compose Secret Sweep (V2 Sweep 6)
```bash
grep -rni "password:\|secret:\|token:\|api_key:" \
  /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  --include="docker-compose*.yml" --include="docker-compose*.yaml" \
  2>/dev/null | grep -v node_modules | grep -v ".git/" \
  | tee /tmp/qa-sr-vf05-4.txt
wc -l < /tmp/qa-sr-vf05-4.txt
```
**Action per hit:** Classify as:
- **SAFE** — References `${VAR}` or `${VAR:?...}` (no hardcoded value)
- **LOCAL-DEV** — Default `postgres` password for local development (flag, document)
- **VIOLATION** — Hardcoded real secret value

**PASS if:** Zero VIOLATION hits. LOCAL-DEV hits are flagged but acceptable.

### VF-05.5: Full-Stack Inline Secret Values
```bash
grep -rn "password:\s*['\"][^$]" \
  /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  --include="docker-compose*.yml" --include="docker-compose*.yaml" \
  2>/dev/null | grep -v node_modules | grep -v ".git/" \
  | tee /tmp/qa-sr-vf05-5.txt
wc -l < /tmp/qa-sr-vf05-5.txt
```
**PASS if:** Zero hits with non-variable hardcoded secret strings. Hits referencing `${VAR}` patterns are acceptable.

### VF-05.6: Performance Baseline Reference
```bash
grep -ni "baseline\|benchmark\|performance.*target\|SLO\|SLA" \
  /home/zaks/zakops-agent-api/apps/dashboard/audit/risk-assessment.md 2>&1 \
  | tee /tmp/qa-sr-vf05-6.txt
```
**PASS if:** No references to performance baselines that don't exist. Any baseline mention includes a note that it's pending Surface 14.

### VF-05.7: Full-Stack .env.example Currency (V2 Sweep 5)
```bash
find /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  \( -name ".env.example" -o -name ".env.template" -o -name ".env.sample" -o -name "env.example*" \) \
  2>/dev/null | grep -v node_modules \
  | tee /tmp/qa-sr-vf05-7.txt
```
**Action per file:** Read the example and its corresponding config loader. Check that every required variable is listed.
**PASS if:** Every .env.example file across all repos is current with its service's config loader.

**Gate VF-05:** All 7 checks pass. Environment and config hygiene is verified full-stack.

---

## Verification Family 06 — Cross-Service Documentation Quality (V1 Phase 5)

### VF-06.1: SERVICE-TOPOLOGY.md — Existence and Coverage
```bash
wc -l /home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md 2>&1
grep -ci "dashboard\|backend\|agent.api\|rag\|vllm\|openwebui" /home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md 2>&1
```
**PASS if:** File exists, is non-empty, and references all 6 services (dashboard, backend, agent-api, RAG, vLLM, OpenWebUI).

### VF-06.2: SERVICE-TOPOLOGY.md — Required Fields per Service
Read the document. For each of the 6 services, verify it includes:
- Canonical port
- Health endpoint path and response shape
- Startup dependency requirements
- Environment variable for discovery
- Failure detection mechanism

**PASS if:** All 6 services have all 5 fields documented. No "TBD" or empty sections.

### VF-06.3: SERVICE-TOPOLOGY.md — Port Accuracy
Cross-check declared ports against actual code:
```bash
grep -n "port" /home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md | head -20
grep -n "PORT\|port" /home/zaks/zakops-backend/docker-compose.yml | head -10
grep -n "PORT\|port" /home/zaks/zakops-agent-api/apps/agent-api/docker-compose.yml | head -10
```
**PASS if:** Ports in SERVICE-TOPOLOGY.md match actual docker-compose declarations. Backend is 8091 (NOT 8090). Dashboard is 3003. Agent-api is 8095.

### VF-06.4: ENV-CROSSREF.md — Existence and Structure
```bash
wc -l /home/zaks/bookkeeping/docs/ENV-CROSSREF.md 2>&1
grep -c "DASHBOARD_SERVICE_TOKEN\|DATABASE_URL\|ZAKOPS_API_KEY\|RAG_REST_URL\|OPENAI_API_KEY" \
  /home/zaks/bookkeeping/docs/ENV-CROSSREF.md 2>&1
```
**PASS if:** File exists, is non-empty, and includes the key cross-service variables (DASHBOARD_SERVICE_TOKEN, DATABASE_URL, ZAKOPS_API_KEY, RAG_REST_URL, OPENAI_API_KEY).

### VF-06.5: ENV-CROSSREF.md — Duplicated Variables Covered
The forensic audit identified these variables as duplicated across services: APP_ENV, DASHBOARD_SERVICE_TOKEN, DATABASE_URL, DEAL_API_URL, DEBUG, LOG_FORMAT, LOG_LEVEL, OPENAI_API_KEY, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER, RAG_REST_URL, ZAKOPS_API_KEY.
```bash
for var in APP_ENV DASHBOARD_SERVICE_TOKEN DATABASE_URL DEAL_API_URL DEBUG LOG_FORMAT LOG_LEVEL OPENAI_API_KEY POSTGRES_DB POSTGRES_PASSWORD POSTGRES_PORT POSTGRES_USER RAG_REST_URL ZAKOPS_API_KEY; do
  echo -n "$var: "
  grep -c "$var" /home/zaks/bookkeeping/docs/ENV-CROSSREF.md 2>/dev/null || echo "0"
done | tee /tmp/qa-sr-vf06-5.txt
```
**PASS if:** All 14 duplicated variables are referenced in the document.

### VF-06.6: ERROR-SHAPES.md — All 6 Shapes Documented
```bash
wc -l /home/zaks/bookkeeping/docs/ERROR-SHAPES.md 2>&1
grep -ci "ErrorResponse\|HTTPException\|validation.*error\|rate.*limit\|SSE.*error\|502\|middleware" \
  /home/zaks/bookkeeping/docs/ERROR-SHAPES.md 2>&1
```
**PASS if:** File exists, is non-empty, and covers all 6 error shapes: Backend ErrorResponse, Backend HTTPException, Agent-API validation error, Agent-API rate limit error, Agent-API SSE error, Dashboard middleware 502.

### VF-06.7: ERROR-SHAPES.md — Normalizer Documentation
Read the document and verify it explains what the dashboard error normalizer (`error-normalizer.ts`) does with each error shape.
**PASS if:** Each shape's section explains the normalizer's handling.

### VF-06.8: TEST-COVERAGE-GAPS.md — Three Matrices Present
```bash
wc -l /home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md 2>&1
grep -ci "endpoint\|API.*coverage\|page.*E2E\|FSM.*transition" /home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md 2>&1
```
**PASS if:** File exists, is non-empty, and contains all three coverage matrices (API endpoints, dashboard pages, FSM transitions).

### VF-06.9: TEST-COVERAGE-GAPS.md — Numbers Match Audit
The forensic audit reported: 93 endpoints (32 tested, 61 untested), 13 pages (10 E2E, 3 no E2E), 22 FSM transitions (1 tested, 21 untested).
Read the document and verify the numbers are consistent with (or more accurate than) the audit.
**PASS if:** Coverage numbers are present and either match the audit or explain discrepancies with evidence.

### VF-06.10: TEST-COVERAGE-GAPS.md — CI Status Documented
```bash
grep -ci "CI\|github.*action\|workflow\|pipeline\|playwright" /home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md 2>&1
```
**PASS if:** Document includes CI enforcement status (which test suites run in CI vs local only).

**Gate VF-06:** All 10 checks pass. Cross-service documentation is complete and accurate.

---

## Verification Family 07 — Proxy Timeout Coverage (V1 Phase 2 + V2 Sweep 7)

### VF-07.1: Middleware Proxy Timeout — Specific Fix
```bash
grep -n "AbortController\|timeout\|signal\|PROXY_TIMEOUT" \
  /home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts 2>&1 \
  | tee /tmp/qa-sr-vf07-1.txt
```
**PASS if:** An explicit timeout mechanism exists (AbortController with signal, or timeout option) in the middleware proxy.

### VF-07.2: Middleware Proxy Timeout — Configurable
Read the middleware and verify the timeout is configurable via environment variable (not hardcoded).
**PASS if:** Timeout value comes from an env variable with a sensible default (e.g., 30s).

### VF-07.3: Full-Stack Server-Side Fetch Sweep — Dashboard
```bash
grep -rn "fetch(" /home/zaks/zakops-agent-api/apps/dashboard/src/ \
  --include="*.ts" --include="*.tsx" \
  2>/dev/null | grep -v node_modules | grep -v "__tests__" | grep -v "\.test\." | grep -v "\.spec\." \
  | tee /tmp/qa-sr-vf07-3.txt
wc -l < /tmp/qa-sr-vf07-3.txt
```
**Action per hit:** Determine if server-side. For each server-side fetch, verify timeout exists.
**PASS if:** Every server-side fetch call has an explicit timeout. Client-side (React component) fetches are excluded.

### VF-07.4: Agent-API HTTP Client Timeout Sweep
```bash
grep -rn "httpx\.\|aiohttp\.\|requests\.\|AsyncClient\|Client(" \
  /home/zaks/zakops-agent-api/apps/agent-api/app/ \
  --include="*.py" \
  2>/dev/null | grep -v __pycache__ | grep -v tests/ \
  | tee /tmp/qa-sr-vf07-4.txt
wc -l < /tmp/qa-sr-vf07-4.txt
```
**Action per hit:** Verify a `timeout` parameter is passed.
**PASS if:** Every HTTP client instantiation or call has an explicit timeout.

### VF-07.5: Backend HTTP Client Timeout Check
```bash
grep -rn "httpx\.\|aiohttp\.\|requests\.\|AsyncClient\|Client(" \
  /home/zaks/zakops-backend/src/ \
  --include="*.py" \
  2>/dev/null | grep -v __pycache__ | grep -v tests/ \
  | tee /tmp/qa-sr-vf07-5.txt
wc -l < /tmp/qa-sr-vf07-5.txt
```
**Action per hit:** Verify timeout parameter.
**PASS if:** Every HTTP client call in backend source has an explicit timeout.

**Gate VF-07:** All 5 checks pass. Every server-side HTTP call across the stack has an explicit timeout.

---

## Verification Family 08 — Regression Safety

### VF-08.1: make validate-local
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-sr-vf08-1.txt
echo "EXIT: $?"
```
**PASS if:** exit 0.

### VF-08.2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-sr-vf08-2.txt
echo "EXIT: $?"
```
**PASS if:** exit 0.

### VF-08.3: ESLint — No New Errors
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx next lint 2>&1 | tee /tmp/qa-sr-vf08-3.txt
echo "EXIT: $?"
```
**PASS if:** exit 0, or same error count as before remediation (no new errors introduced).

### VF-08.4: Backend Test Syntax (No Import Errors from Stage Name Changes)
```bash
cd /home/zaks/zakops-backend && python -m py_compile tests/unit/test_idempotency.py 2>&1
python -m py_compile tests/integration/test_golden_path_deal.py 2>&1
echo "EXIT: $?"
```
**PASS if:** Both files compile without syntax errors.

### VF-08.5: Bookkeeping — CHANGES.md Updated
```bash
grep -ci "SURFACE-REMEDIATION" /home/zaks/bookkeeping/CHANGES.md 2>&1
tail -50 /home/zaks/bookkeeping/CHANGES.md | head -30
```
**PASS if:** CHANGES.md contains entries for SURFACE-REMEDIATION-001. If V2 was executed, also contains entry for SURFACE-REMEDIATION-002.

**Gate VF-08:** All 5 checks pass. No regressions introduced.

---

## Verification Family 09 — Cross-Consistency Checks

### XC-1: Documentation vs Codebase Port Agreement
Cross-check SERVICE-TOPOLOGY.md declared ports against actual compose files and middleware config.
**PASS if:** All ports in documentation match live code. No 8090 appears in topology doc.

### XC-2: ENV-CROSSREF vs .env.example Agreement
Compare the variables listed in ENV-CROSSREF.md against actual .env.example files. The crossref should be a superset.
**PASS if:** Every variable in .env.example files appears in ENV-CROSSREF.md.

### XC-3: ERROR-SHAPES vs error-normalizer.ts Agreement
Read `error-normalizer.ts` and verify the shapes it handles match what ERROR-SHAPES.md documents.
```bash
grep -n "normalize\|shape\|detail\|error\|message" \
  /home/zaks/zakops-agent-api/apps/dashboard/src/lib/error-normalizer.ts 2>&1 | head -30
```
**PASS if:** Every error shape handled by the normalizer is documented in ERROR-SHAPES.md, and vice versa.

### XC-4: TEST-COVERAGE-GAPS vs Actual Test Files
Spot-check 5 endpoints marked "UNTESTED" in TEST-COVERAGE-GAPS.md:
```bash
# Pick 5 endpoints the doc says are untested and verify no test file covers them
grep -rn "actions/capabilities\|deals/by-alias\|quarantine/health\|auth/logout\|events/stats" \
  /home/zaks/zakops-agent-api/apps/dashboard/tests/ /home/zaks/zakops-backend/tests/ \
  --include="*.ts" --include="*.py" \
  2>/dev/null | tee /tmp/qa-sr-xc4.txt
wc -l < /tmp/qa-sr-xc4.txt
```
**PASS if:** The spot-checked endpoints are indeed untested (zero hits or only tangential references).

### XC-5: V1 Deferred P4-02 Resolution
The V1 completion noted P4-02 (.env.example update) was blocked by deny rules and deferred for manual application.
```bash
grep -c "DATABASE_URL\|DEAL_API_URL\|RAG_REST_URL\|MCP_URL\|VLLM_BASE_URL\|LOCAL_EMBEDDER_URL\|DASHBOARD_SERVICE_TOKEN\|HITL_" \
  /home/zaks/zakops-agent-api/apps/agent-api/.env.example 2>&1
```
**PASS if:** Count is >= 8 (all deferred variables were manually added). The manual action from V1 was completed.

**Gate XC:** All 5 cross-consistency checks pass.

---

## Stress Tests

### ST-1: Resilience Config Consistency
Read the full resilience config and verify every service entry has consistent fields (timeout, retries, circuit breaker threshold).
```bash
cat /home/zaks/zakops-agent-api/apps/agent-api/app/core/resilience.py | head -80
```
**PASS if:** All service entries use the same field schema. No service is missing timeout or retry config.

### ST-2: Middleware Timeout vs Resilience Config Timeout
Compare the dashboard middleware proxy timeout value against the backend timeout declared in agent-api resilience config. The proxy timeout should be >= the resilience timeout (otherwise the proxy gives up before the retry logic completes).
**PASS if:** Proxy timeout >= resilience config backend timeout, or the relationship is documented.

### ST-3: Docker Compose Port Declarations Match Service Topology
```bash
grep -n "ports:" -A2 /home/zaks/zakops-backend/docker-compose.yml 2>&1
grep -n "ports:" -A2 /home/zaks/zakops-agent-api/apps/agent-api/docker-compose.yml 2>&1
grep -n "ports:" -A2 /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml 2>&1
```
**PASS if:** Port declarations in compose files match SERVICE-TOPOLOGY.md. No compose file exposes 8090.

### ST-4: Duplicate Dashboard Codebase Env Drift
The audit flagged a duplicate dashboard at `/home/zaks/zakops-dashboard/`. Check if it still exists and has conflicting env:
```bash
ls -la /home/zaks/zakops-dashboard/.env.local 2>/dev/null
diff /home/zaks/zakops-agent-api/apps/dashboard/.env.local /home/zaks/zakops-dashboard/.env.local 2>/dev/null
```
**PASS if:** Either the duplicate doesn't exist, or its .env.local is consistent with the monorepo dashboard. Flag discrepancies as INFO.

### ST-5: Pipeline Route Fallback Shape Check
Read `apps/dashboard/src/app/api/pipeline/route.ts` and verify the `Promise.allSettled` fallback values have the correct TypeScript types (not `any`, not `undefined` where an object is expected).
**PASS if:** Fallback values are properly typed and match the expected response shape.

### ST-6: Agent-API .env.example vs .env Parity
```bash
wc -l /home/zaks/zakops-agent-api/apps/agent-api/.env.example 2>&1
wc -l /home/zaks/zakops-agent-api/apps/agent-api/.env 2>&1
```
**PASS if:** .env.example has >= the number of entries as .env (example should be comprehensive).

### ST-7: Orphaned Config Variables
Check if any variables in .env.example files are never read by the corresponding service's code:
```bash
# Extract variable names from agent-api .env.example and check each against config.py
grep "^[A-Z]" /home/zaks/zakops-agent-api/apps/agent-api/.env.example | cut -d= -f1 | while read var; do
  COUNT=$(grep -c "$var" /home/zaks/zakops-agent-api/apps/agent-api/app/core/config.py 2>/dev/null) || COUNT=0
  if [ "$COUNT" -eq 0 ]; then
    echo "ORPHAN: $var (in .env.example but not in config.py)"
  fi
done | tee /tmp/qa-sr-st7.txt
```
**PASS if:** Zero orphaned variables (every variable in example is read by code). Or orphans are documented with justification (e.g., used by framework directly, not config.py).

**Gate ST:** All 7 stress tests pass or produce INFO-only findings.

---

## Remediation Protocol

For any FAIL result:

1. **Read the evidence** — Open the tee'd output file and the source file
2. **Classify the failure:**
   - **MISSING_FIX** — V1/V2 should have caught this but didn't → fix it now
   - **REGRESSION** — A subsequent change broke a previous fix → fix it now
   - **SCOPE_GAP** — Neither V1 nor V2 covered this case → fix it now, add to evidence
   - **FALSE_POSITIVE** — The gate is too strict, the code is actually correct → document justification, mark PASS with note
3. **Apply the fix** following the same guardrails as the original missions
4. **Re-run the specific gate** to verify the fix
5. **Re-run `make validate-local`** after each fix
6. **Record the remediation** in the completion report with: gate ID, failure description, fix applied, evidence

---

## Enhancement Opportunities

### ENH-1: Automated Port Decommission Gate
Add a CI gate or pre-commit hook that greps for 8090 and fails if found in active code. Prevents port drift from recurring.

### ENH-2: Promise.all Lint Rule
Add an ESLint rule or pre-commit check that flags `Promise.all(` in `apps/dashboard/src/app/` directories. The Deal Integrity mandate should be machine-enforced, not human-remembered.

### ENH-3: Log Level Lint Rule
Add an ESLint rule that flags `console.error` in `apps/dashboard/src/app/api/` unless accompanied by a `// UNEXPECTED:` comment. Forces developers to explicitly classify error severity.

### ENH-4: .env.example Drift Detection
Add a CI step or make target that compares config loader variables against .env.example and fails on mismatch. Prevents the drift that the forensic audit found.

### ENH-5: Compose Secret Scanner
Add a pre-commit hook that scans docker-compose files for hardcoded secret values (regex: `(password|secret|token|api_key):\s*['"][^$]`). Prevents future hardcoded secrets.

### ENH-6: FSM Stage Name Guard
Add a grep-based CI gate that searches for legacy stage names across the codebase. The canonical stage list from `workflow.py` should be the source of truth, and any deviation should break the build.

### ENH-7: Timeout Coverage Report
Add a make target that scans for all `fetch(`, `httpx.`, `requests.`, `aiohttp.` calls and reports which have explicit timeouts and which don't. Run periodically to catch new untimed calls.

### ENH-8: SERVICE-TOPOLOGY.md Auto-Generation
Add a make target that generates SERVICE-TOPOLOGY.md from actual compose files, health endpoints, and env files. Currently the document is manually maintained and will drift.

### ENH-9: Cross-Service Error Shape Contract Test
Add a contract test that hits each service's error paths and verifies the response shape matches ERROR-SHAPES.md. Currently the shapes are documented but not machine-verified.

### ENH-10: Documentation Freshness Dates
Add a `Last verified:` date to each reference document (SERVICE-TOPOLOGY.md, ENV-CROSSREF.md, ERROR-SHAPES.md, TEST-COVERAGE-GAPS.md). Allows future sessions to know when the docs were last validated against reality.

---

## Scorecard Template

```
QA-SR-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):      [ PASS / FAIL ]
  PF-2 (V2 execution status): [ V2_COMPLETE / V2_NOT_RUN ]
  PF-3 (tsc):                 [ PASS / FAIL ]

Verification Gates:
  VF-01 (Port Drift):           __ / 6  gates PASS
  VF-02 (Promise.allSettled):   __ / 5  gates PASS
  VF-03 (Log Levels):           __ / 5  gates PASS
  VF-04 (FSM Stages):           __ / 6  gates PASS
  VF-05 (Env & Config):         __ / 7  gates PASS
  VF-06 (Documentation):        __ / 10 gates PASS
  VF-07 (Proxy Timeouts):       __ / 5  gates PASS
  VF-08 (Regression Safety):    __ / 5  gates PASS

Cross-Consistency:
  XC-1 through XC-5:            __ / 5  gates PASS

Stress Tests:
  ST-1 through ST-7:            __ / 7  tests PASS

Total: __ / 61 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## Guardrails

1. **Do not implement Surfaces 10–14** — This is a QA mission, not a build mission
2. **Do not modify generated files** — Deny rule protected
3. **Do not modify migration files** — Historical records
4. **Surface 9 compliance** on any dashboard remediation fixes
5. **WSL safety** — CRLF + ownership on any new files
6. **Remediate, don't redesign** — Fix failures to meet the original mission's acceptance criteria. Do not add new features or refactor beyond what's needed to pass the gate
7. **Evidence-based only** — Every PASS needs a tee'd output file or file:line reference. No "I checked and it's fine" without evidence

---

## Stop Condition

Stop when all 61 verification gates pass (or are documented as FALSE_POSITIVE with justification), all remediations are applied and re-verified, `make validate-local` passes, and the scorecard is complete. Produce the filled scorecard as the final deliverable.

Do not proceed to SURFACE-IMPL-001 until this QA mission produces a FULL PASS or CONDITIONAL PASS (with all conditions documented).

---

*End of Mission Prompt — QA-SR-VERIFY-001*

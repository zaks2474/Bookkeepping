# MISSION: SURFACE-REMEDIATION-002
## Full-Stack Pattern Sweep — Post-Surgical Cross-Repo Audit & Fix
## Date: 2026-02-09
## Classification: Infrastructure Remediation — Full-Stack Sweep
## Prerequisite: SURFACE-REMEDIATION-001 (must be complete — surgical fixes landed first)
## Successor: SURFACE-IMPL-001 (new surface builds, blocked until this mission passes)

---

## Mission Objective

SURFACE-REMEDIATION-001 fixed 15 specific instances flagged by the forensic audit. This companion mission sweeps the **entire codebase across all four repositories** for the same categories of problems, ensuring no identical issues survive in files the audit didn't examine.

**The pattern:** For every category of fix in V1, this mission runs a full-stack grep/search across all repos, fixes any additional hits, and proves zero remaining violations with evidence.

**Repositories in scope:**
- `/home/zaks/zakops-agent-api` (monorepo: agent-api + dashboard + contracts + deployments)
- `/home/zaks/zakops-backend` (backend)
- `/home/zaks/Zaks-llm` (RAG/LLM)
- `/home/zaks/bookkeeping` (docs — read-only for code, writable for reports)

---

## Sweep Categories

### Sweep 1 — Decommissioned Port 8090

V1 fixed `apps/dashboard/Makefile` and `smoke-test.sh`. This sweep covers everything else.

**Search command:**
```bash
grep -rn "8090" /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" --include="*.sh" \
  --include="*.yml" --include="*.yaml" --include="*.json" --include="*.md" --include="*.env*" \
  --include="Makefile" --include="Dockerfile" \
  | grep -v node_modules | grep -v .next | grep -v __pycache__ | grep -v ".git/"
```

**Action per hit:**
- If it's an active code path or config pointing to port 8090 → fix to 8091
- If it's a comment explaining the decommission → leave it
- If it's in a generated file (api-types.generated.ts, backend_models.py) → skip (deny rule protected)
- If it's a lock file or dependency → skip

**Gate S1:** The search command returns zero active code/config hits for port 8090 across all repos. Document every hit found and the disposition (fixed / comment / skip).

---

### Sweep 2 — Banned Promise.all in Data-Fetching

V1 fixed `apps/dashboard/src/app/api/pipeline/route.ts`. This sweep covers the entire dashboard and any other service that fetches data.

**Search command:**
```bash
grep -rn "Promise\.all\b" /home/zaks/zakops-agent-api/apps/dashboard/src/ \
  --include="*.ts" --include="*.tsx" \
  | grep -v node_modules | grep -v "Promise\.allSettled"
```

Also check agent-api service code for the same pattern:
```bash
grep -rn "Promise\.all\b" /home/zaks/zakops-agent-api/apps/agent-api/ \
  --include="*.py" \
  | grep -v __pycache__
```

**Action per hit:**
- If it's a multi-fetch data-fetching call (fetching from backend/agent/RAG) → convert to `Promise.allSettled` with typed empty fallbacks
- If it's a utility or non-data-fetching use (e.g., Promise.all for file operations, build scripts) → document why it's acceptable and leave it
- If it's in a test file mocking data → acceptable, document and leave

**Gate S2:** Every `Promise.all` hit in dashboard source code is either converted to `Promise.allSettled` or has a documented justification for why it's not a data-fetching call. Zero unjustified `Promise.all` in data-fetching paths.

---

### Sweep 3 — console.error for Expected Degradation

V1 fixed `apps/dashboard/src/app/api/agent/activity/route.ts`. This sweep covers all dashboard code AND agent-api code.

**Search command (dashboard — server routes, lib, components):**
```bash
grep -rn "console\.error" /home/zaks/zakops-agent-api/apps/dashboard/src/ \
  --include="*.ts" --include="*.tsx" \
  | grep -v node_modules | grep -v __tests__ | grep -v ".test." | grep -v ".spec."
```

**Search command (agent-api):**
```bash
grep -rn "console\.error\|logger\.error" /home/zaks/zakops-agent-api/apps/agent-api/ \
  --include="*.py" \
  | grep -v __pycache__ | grep -v tests/
```

**Action per hit:**
- Read the surrounding code context (at least 10 lines above and below)
- If the error is triggered by an expected degradation path (backend unreachable, partial data, timeout on optional service, feature flag disabled) → change to `console.warn` / `logger.warning`
- If the error is triggered by a genuinely unexpected failure (uncaught exception, data corruption, invariant violation) → leave as `console.error` / `logger.error`
- Document the classification decision for each hit

**Gate S3:** Every `console.error` / `logger.error` in dashboard source and agent-api source has been classified. All expected-degradation cases use warn level. Evidence table lists every hit with file:line, context summary, and classification (degradation→warn / unexpected→error / already correct).

---

### Sweep 4 — Legacy FSM Stage Names

V1 fixed `test_idempotency.py` and `test_golden_path_deal.py`. This sweep covers all code in all repos.

**Canonical stages** (from `zakops-backend/src/core/deals/workflow.py`):
`inbound`, `screening`, `qualified`, `loi`, `diligence`, `closing`, `portfolio`, `junk`, `archived`

**Legacy/suspect stage names to search for:**
```bash
grep -rni "initial_review\|due_diligence\|closed_won\|closed_lost\|under_review\|\"lead\"\|'lead'\|negotiation\|prospecting" \
  /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  --include="*.ts" --include="*.tsx" --include="*.py" --include="*.sql" --include="*.json" \
  | grep -v node_modules | grep -v .next | grep -v __pycache__ | grep -v ".git/"
```

**Action per hit:**
- If it's in test code → update to canonical stage name
- If it's in application code → update to canonical stage name (this is a bug)
- If it's in a migration file → leave it (migrations are append-only historical records)
- If it's in documentation → update to canonical stage name
- If it's in OpenAPI spec or generated files → skip (managed by sync pipeline)

**Gate S4:** The search command returns zero hits in active code and tests (migration files excluded). Evidence table lists every hit and disposition.

---

### Sweep 5 — Stale .env.example Files

V1 fixed agent-api `.env.example`. This sweep covers all `.env.example` / `.env.template` / `.env.sample` files across all repos.

**Search command:**
```bash
find /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  -name ".env.example" -o -name ".env.template" -o -name ".env.sample" -o -name "env.example*" \
  2>/dev/null | grep -v node_modules
```

**Action per file found:**
- Read the corresponding config loading code for that service
- Identify every variable the code reads (os.getenv, process.env, config class fields)
- Compare against what the example file documents
- Add missing required variables with descriptive comments (e.g., `# Required: RAG REST API URL`)
- Remove variables that the code no longer reads
- Mark secret variables with `# SECRET — do not commit real values`

**Gate S5:** Every .env.example file across all repos is current: no variables listed that code doesn't use, no required variables missing that code expects. Evidence: diff of each example file (before/after).

---

### Sweep 6 — Hardcoded Secrets in Compose & Config

V1 fixed one hardcoded DASHBOARD_SERVICE_TOKEN in deployment compose. This sweep checks all compose files and config files for any hardcoded secrets.

**Search command:**
```bash
grep -rni "password\|secret\|token\|api_key\|apikey" \
  /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  --include="docker-compose*.yml" --include="docker-compose*.yaml" \
  | grep -v node_modules | grep -v ".git/"
```

Also check for inline secret values (not variable references):
```bash
grep -rn "password:\s*['\"]" \
  /home/zaks/zakops-agent-api/ /home/zaks/zakops-backend/ /home/zaks/Zaks-llm/ \
  --include="docker-compose*.yml" --include="docker-compose*.yaml" \
  | grep -v node_modules | grep -v ".git/"
```

**Action per hit:**
- If the value is a hardcoded literal (not a `${VAR}` reference) for a secret variable → replace with `${VAR_NAME:?VAR_NAME must be set}` fail-fast pattern
- If the value is a `${VAR:-default}` with a real secret as default → remove the default, use `${VAR:?...}` instead
- If the value is a `${VAR:-default}` with a non-secret default (e.g., `${POSTGRES_DB:-zakops}`) → acceptable, leave it
- If the value is `postgres` as a default password for local dev → flag but don't change without user confirmation (local dev convenience vs security)

**Gate S6:** Zero hardcoded secret literals in compose files. Every secret variable either references an env var without a default or uses the fail-fast `${VAR:?}` pattern. Evidence: table of every hit with disposition.

---

### Sweep 7 — Proxy Timeout Gaps

V1 added a timeout to the main middleware proxy. This sweep checks for any other `fetch()` calls in server-side dashboard code and agent-api HTTP clients that lack timeouts.

**Search command (dashboard server-side fetch):**
```bash
grep -rn "fetch(" /home/zaks/zakops-agent-api/apps/dashboard/src/ \
  --include="*.ts" --include="*.tsx" \
  | grep -v node_modules | grep -v __tests__ | grep -v ".test." | grep -v ".spec."
```

**Search command (agent-api HTTP clients):**
```bash
grep -rn "httpx\.\|aiohttp\.\|requests\.\|fetch(" /home/zaks/zakops-agent-api/apps/agent-api/ \
  --include="*.py" \
  | grep -v __pycache__ | grep -v tests/
```

**Action per hit:**
- Read the surrounding context to determine if the call is server-side (not client-side React)
- For server-side fetch calls: verify an explicit timeout mechanism exists (AbortController, signal, timeout option)
- For Python HTTP clients: verify a timeout parameter is passed
- If no timeout exists on a server-to-server call → add one with a sensible default
- Client-side fetch in React components → out of scope (browser handles these)

**Gate S7:** Every server-side HTTP call (dashboard fetch, agent-api httpx/aiohttp/requests) has an explicit timeout. Evidence: table of every server-side HTTP call with file:line, timeout value, and status (had timeout / added timeout / client-side skip).

---

## Phase 0 — Discovery

Before fixing anything:

- P0-01: Run all seven search commands and capture raw output to `/home/zaks/bookkeeping/docs/SWEEP-002-DISCOVERY.md`
- P0-02: Count total hits per sweep category
- P0-03: Verify `make validate-local` passes at baseline
- P0-04: If any sweep has zero hits beyond what V1 already fixed, mark that sweep as CLEAN and skip it

### Gate P0

Discovery report exists with hit counts. Baseline validation passes. Sweeps with zero actionable hits are marked CLEAN.

---

## Phase 1 — Execute Sweeps

Work through Sweeps 1–7 in order. For each sweep:
1. Fix all actionable hits
2. Build the evidence table (file:line, context, disposition)
3. Re-run the search command to verify zero remaining violations
4. Run `make validate-local` after each sweep to catch regressions early

### Gate P1

All seven sweep gates (S1–S7) pass. `make validate-local` passes.

---

## Phase 2 — Final Verification & Evidence

- P2-01: Run all seven search commands one final time and capture output proving zero violations
- P2-02: Run `make validate-local` final pass
- P2-03: Run `npx tsc --noEmit` in dashboard to verify TypeScript compilation
- P2-04: Write completion report to `/home/zaks/bookkeeping/docs/SURFACE-REMEDIATION-002-COMPLETION.md` with:
  - Per-sweep: total hits found, hits fixed, hits justified-as-acceptable, hits skipped (generated/migration)
  - Final search command output (proving zero remaining violations)
  - Validation results

### Gate P2

Completion report exists. All sweep gates pass. Validation passes. TypeScript compiles.

---

## Acceptance Criteria

### AC-1: Zero Decommissioned Ports
No active code or config across any repo references port 8090.

### AC-2: Zero Banned Promise.all
No unjustified `Promise.all` in dashboard data-fetching paths. Every remaining `Promise.all` has a documented justification.

### AC-3: Correct Log Levels
Every `console.error` / `logger.error` is classified. All expected-degradation paths use warn level.

### AC-4: Canonical Stages Only
No legacy FSM stage names in active code or tests (migration files excluded).

### AC-5: Current .env Examples
Every .env.example file matches what its service's code actually reads.

### AC-6: No Hardcoded Secrets
Zero hardcoded secret values in compose files.

### AC-7: Universal Timeouts
Every server-side HTTP call has an explicit timeout.

### AC-8: No Regressions
`make validate-local` passes. TypeScript compilation succeeds. No existing tests broken.

### AC-9: Evidence Trail
Completion report documents every hit found, every fix applied, and every justification for items left unchanged.

---

## Guardrails

1. **Do not implement Surfaces 10–14.** This is still a fix mission
2. **Do not modify generated files** (api-types.generated.ts, backend_models.py) — deny rule protected
3. **Do not modify migration files** — they are historical records
4. **Do not rename environment variables** — document inconsistencies, don't rename (breaks deployed configs)
5. **Do not remove @pytest.mark.skip decorators** — fix content within skipped tests, don't change skip status
6. **Flag but don't auto-fix local dev passwords** — `postgres` as a default dev password is a security/convenience tradeoff that needs user decision
7. **Surface 9 compliance** — All dashboard changes must comply with `.claude/rules/design-system.md`
8. **WSL safety** — `sed -i 's/\r$//'` on new .sh files, `sudo chown zaks:zaks` on files under `/home/zaks/`
9. **Classify, don't guess** — For console.error/warn decisions, read the actual code context. If uncertain whether something is expected degradation or unexpected failure, err toward leaving it as error and documenting the uncertainty
10. **Respect repo boundaries** — Fix code in the repo that owns it. Don't fix backend patterns from the monorepo or vice versa

---

## Stop Condition

Stop when all acceptance criteria AC-1 through AC-9 are met, all seven sweep gates pass with evidence, and the completion report is written. Produce a summary listing each AC with evidence paths.

This mission's sole deliverable is a codebase where every instance of the seven anti-patterns has been found, classified, and either fixed or justified — not just the instances the audit happened to flag.

---

*End of Mission Prompt — SURFACE-REMEDIATION-002*

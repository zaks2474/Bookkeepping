# MISSION: SURFACE-REMEDIATION-001
## Cross-Service Forensic Remediation — Surfaces 10–14 Pre-Build Cleanup
## Date: 2026-02-09
## Classification: Infrastructure Remediation — Cross-Service
## Prerequisite: FORENSIC-AUDIT-SURFACES-002 (complete, findings documented)
## Successor: SURFACE-IMPL-001 (new surface builds, blocked until this mission passes)

---

## Mission Objective

The forensic audit FORENSIC-AUDIT-SURFACES-002 investigated five areas (Dependency Health, Secret & Environment Variable Registry, Error Taxonomy, Test Coverage, Performance Budget) and found concrete inconsistencies, drift, stale tests, missing timeouts, port mismatches, naming conflicts, and dead references across all four services. This mission remediates those findings so the codebase is in a clean, consistent state before Surfaces 10–14 are built on top of it.

**This is a FIX mission, not a BUILD mission.** The five new surfaces are out of scope. This mission fixes what the audit found broken, inconsistent, or missing so the surface implementations have a stable foundation.

**Audit report:** `/home/zaks/bookkeeping/docs/FORENSIC-AUDIT-RESULTS-FORENSIC-AUDIT-SURFACES-002`

---

## Context: What the Audit Found (Summary)

Across 1,229 lines of evidence-backed findings:

1. **Port drift** — Dashboard Makefile and smoke scripts assume backend on port 8090 (decommissioned), while the live backend runs on 8091
2. **URL variable sprawl** — The dashboard uses 5 different env variable names (API_URL, BACKEND_URL, NEXT_PUBLIC_API_URL, AGENT_API_URL, AGENT_LOCAL_URL) to discover the same backend, with no canonical choice
3. **RAG health endpoint mismatch** — Agent-api resilience config declares `/health` for RAG but the RAG client actually calls `/` (which is what RAG exposes)
4. **Hardcoded default secrets in compose** — Deployment compose embeds a default DASHBOARD_SERVICE_TOKEN value rather than requiring explicit configuration
5. **Docs drift** — Dashboard README references `env.example.txt` and feature flags that don't exist in code
6. **Stale FSM tests** — Backend tests reference legacy stage names (initial_review, due_diligence, closed_won) that don't match the canonical DealStage enum (inbound, screening, qualified, loi, diligence, closing, portfolio, junk, archived)
7. **CI test gaps** — Agent-api CI only runs `evals/` (not `tests/`); dashboard CI doesn't run Playwright at all
8. **Error shape inconsistency** — Agent-api mixes at least 3 error shapes (validation handler, rate limit handler, HTTPException detail strings) with no unified schema
9. **Dashboard server routes log console.error for expected degradation** — Violates Surface 9 convention (console.warn for degradation, console.error for unexpected only)
10. **No proxy timeout** — Dashboard middleware proxy has no explicit timeout on backend fetch calls
11. **Pipeline route uses Promise.all** — `apps/dashboard/src/app/api/pipeline/route.ts` uses `Promise.all` instead of the mandatory `Promise.allSettled`
12. **Performance baselines mentioned but never recorded** — Risk assessment references baselines that don't exist
13. **Dashboard Makefile references external script path** — Points to `/home/zaks/scripts/chat_benchmark.py` which may be the wrong location
14. **Agent-api .env sparse** — Only two variables in .env while config requires many more, relying on silent defaults
15. **Env examples stale** — Code expects variables (LOCAL_EMBEDDER_URL, RAG_REST_TIMEOUT) not present in .env.example files

---

## Architectural Constraints (MANDATORY)

These patterns are already established and must be preserved:

- **`transition_deal_state()`** is the single choke point for all deal state changes — no direct mutations
- **`Promise.allSettled`** with typed empty fallbacks is mandatory for multi-fetch — `Promise.all` is banned in dashboard data-fetching
- **Next.js middleware** proxies all `/api/*` requests and returns JSON 502 on backend failure — never HTML 500
- **`PIPELINE_STAGES`** in `execution-contracts.ts` is the single source of truth for stage definitions
- **Server-side deal counts only** — no client-side `.length` counting for display
- **Surface 9 (Component Design System)** — `console.warn` for expected degradation, `console.error` for unexpected failures only
- **Port 8090 is FORBIDDEN** — legacy, decommissioned
- **Contract surface discipline** — All sync flows via `make sync-*` targets; generated files never edited directly

---

## Phase 0 — Discovery & Baseline

**Purpose:** Verify the audit findings are still current before touching code. The codebase may have changed since the audit.

### Tasks

- P0-01: Verify port 8090 still appears in dashboard Makefile and smoke-test.sh
- P0-02: Verify Promise.all (not allSettled) still exists in `apps/dashboard/src/app/api/pipeline/route.ts`
- P0-03: Verify console.error usage in dashboard server routes for degradation paths
- P0-04: Verify RAG health endpoint mismatch in agent-api resilience config vs rag_rest.py
- P0-05: Verify stale FSM stage names in backend tests
- P0-06: Capture current `make validate-local` baseline (must pass before any changes)

### Gate P0

All findings confirmed or marked superseded. `make validate-local` passes at baseline. Discovery report written to completion evidence.

---

## Phase 1 — Port Drift & URL Canonicalization

**Purpose:** Eliminate the decommissioned port 8090 from all code paths and establish a canonical backend URL variable.

### Tasks

- P1-01: **Fix port 8090 → 8091** in `apps/dashboard/Makefile` (all references)
  - Evidence: `zakops-agent-api/apps/dashboard/Makefile`
- P1-02: **Fix port 8090 → 8091** in `apps/dashboard/smoke-test.sh` (if present)
  - Evidence: `zakops-agent-api/apps/dashboard/smoke-test.sh`
- P1-03: **Fix RAG health endpoint** in agent-api resilience config — change declared health path from `/health` to `/` to match what RAG actually exposes, OR add a comment documenting the mismatch and why it exists
  - Evidence: `zakops-agent-api/apps/agent-api/app/core/resilience.py` vs `zakops-agent-api/apps/agent-api/app/services/rag_rest.py`
- P1-04: **Document URL variable mapping** — Add a comment block at top of `apps/dashboard/src/middleware.ts` documenting which env variables exist, what each controls, and which is canonical for backend discovery. Do NOT rename variables (that would break running configs) — document them
  - Evidence: `zakops-agent-api/apps/dashboard/src/middleware.ts`
- P1-05: **Fix external script path** in dashboard Makefile — Update reference from `/home/zaks/scripts/chat_benchmark.py` to the correct monorepo-relative path, or remove the target if the script doesn't exist at either location
  - Evidence: `zakops-agent-api/apps/dashboard/Makefile`

### Gate P1

- `grep -r "8090" apps/dashboard/` returns zero hits (excluding comments that explain the port is decommissioned)
- RAG health path in resilience config matches actual RAG health endpoint
- `make validate-local` still passes

---

## Phase 2 — Dashboard Code Fixes

**Purpose:** Fix the three contract violations the audit found in dashboard code.

### Tasks

- P2-01: **Fix Promise.all → Promise.allSettled** in `apps/dashboard/src/app/api/pipeline/route.ts`
  - Must follow the established pattern: typed empty fallbacks on rejection, no throwing on partial failure
  - Evidence: `zakops-agent-api/apps/dashboard/src/app/api/pipeline/route.ts`
- P2-02: **Fix console.error → console.warn** for expected degradation paths in dashboard server routes
  - Only change cases where the error is an expected degradation (backend down, partial data) — NOT unexpected failures
  - Files flagged by audit: `apps/dashboard/src/app/api/agent/activity/route.ts`
  - Search for additional violations: `grep -rn "console\.error" apps/dashboard/src/app/api/`
  - Evidence: Surface 9 manifest at `apps/dashboard/src/types/design-system-manifest.ts`
- P2-03: **Add explicit timeout to middleware proxy fetch** — Add an AbortController with a configurable timeout (environment variable with sensible default, e.g., 30s) to the backend fetch in `apps/dashboard/src/middleware.ts`
  - The middleware currently uses bare `fetch()` with no timeout — this means a hung backend causes the dashboard to hang indefinitely
  - Evidence: `zakops-agent-api/apps/dashboard/src/middleware.ts`

### Gate P2

- Zero `Promise.all` in dashboard data-fetching code (verify: `grep -rn "Promise\.all[^S]" apps/dashboard/src/` — only `Promise.allSettled` should remain)
- `console.error` in server API routes is only used for genuinely unexpected failures, not backend-down degradation
- Middleware proxy has an explicit timeout mechanism
- `make validate-local` still passes
- TypeScript compilation succeeds (`npx tsc --noEmit`)

---

## Phase 3 — Stale Test Remediation

**Purpose:** Fix tests that reference legacy stage names and address the most critical test integrity issues.

### Tasks

- P3-01: **Update FSM test stage names** in `zakops-backend/tests/unit/test_idempotency.py` — Replace legacy stages (initial_review, due_diligence, closed_won, etc.) with canonical stages from `zakops-backend/src/core/deals/workflow.py` (inbound, screening, qualified, loi, diligence, closing, portfolio, junk, archived)
  - Evidence: `zakops-backend/tests/unit/test_idempotency.py`, `zakops-backend/src/core/deals/workflow.py`
- P3-02: **Update golden path test stage names** — If `zakops-backend/tests/integration/test_golden_path_deal.py` uses non-canonical stage names (e.g., `stage: "lead"`), update them to match the DealStage enum
  - Note: This test class is marked `@pytest.mark.skip` — fix the stage names but do NOT remove the skip decorator (that's a separate decision)
  - Evidence: `zakops-backend/tests/integration/test_golden_path_deal.py`
- P3-03: **Fix Playwright spec inconsistency** — `zakops-agent-api/apps/dashboard/tests/deals-bulk-delete.spec.ts` navigates `/deals` but expects `/deals-bulk-delete`. Determine the correct behavior and fix
  - Evidence: `zakops-agent-api/apps/dashboard/tests/deals-bulk-delete.spec.ts`

### Gate P3

- Zero references to legacy stage names (initial_review, due_diligence, closed_won) in test files: `grep -rn "initial_review\|due_diligence\|closed_won" zakops-backend/tests/` returns zero hits
- Playwright spec navigates to the correct URL for its test purpose
- `make validate-local` still passes

---

## Phase 4 — Environment & Config Hygiene

**Purpose:** Fix docs drift, stale .env examples, and hardcoded default secrets.

### Tasks

- P4-01: **Update dashboard README** — Remove or correct references to `env.example.txt` and feature flags that don't exist in code. The README must describe the actual environment, not a fictional one
  - Evidence: `zakops-agent-api/apps/dashboard/README.md`
- P4-02: **Update agent-api .env.example** — Add missing variables that the code expects but the example doesn't document: LOCAL_EMBEDDER_URL, RAG_REST_TIMEOUT, and any others found by comparing `apps/agent-api/app/core/config.py` against `apps/agent-api/.env.example`
  - Evidence: `zakops-agent-api/apps/agent-api/app/core/config.py`, `zakops-agent-api/apps/agent-api/.env.example`
- P4-03: **Remove hardcoded default secret from deployment compose** — The default DASHBOARD_SERVICE_TOKEN value in `zakops-agent-api/deployments/docker/docker-compose.yml` should be replaced with `${DASHBOARD_SERVICE_TOKEN:?DASHBOARD_SERVICE_TOKEN must be set}` or equivalent fail-fast pattern
  - Do NOT remove the variable — just remove the hardcoded default so deployment fails fast if the secret isn't explicitly configured
  - Evidence: `zakops-agent-api/deployments/docker/docker-compose.yml`
- P4-04: **Audit and document performance baselines** — The risk assessment at `apps/dashboard/audit/risk-assessment.md` mentions performance baselines that don't exist. Either remove the reference or add a note that baselines are pending Surface 14 implementation
  - Evidence: `zakops-agent-api/apps/dashboard/audit/risk-assessment.md`

### Gate P4

- Dashboard README does not reference files that don't exist
- Agent-api .env.example contains entries for all variables that config.py reads with no default
- No hardcoded secret values in deployment compose files
- `make validate-local` still passes

---

## Phase 5 — Cross-Service Consistency Documentation

**Purpose:** Create the lightweight documentation artifacts that the surface implementations will build on. These are READ documents, not enforcement mechanisms — they codify what the audit discovered.

### Tasks

- P5-01: **Create service topology document** at `/home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md`
  - Contents: For each service (dashboard, backend, agent-api, RAG, vLLM, OpenWebUI), document:
    - Canonical port
    - Health endpoint path and response shape
    - Startup dependency requirements (what must be up before this service works)
    - Environment variable for discovery
    - Failure detection mechanism (how callers know this service is down)
  - Source: Audit findings Area 1, all evidence paths listed there
- P5-02: **Create environment variable cross-reference** at `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md`
  - Contents: The complete variable inventory from the audit (Area 2), organized by:
    - Variables that appear in multiple services (cross-service alignment required)
    - Variables classified as secrets (must never have hardcoded defaults)
    - Variables with naming conflicts (same concept, different names)
  - Source: Audit findings Area 2, variable inventory table
- P5-03: **Create error shape inventory** at `/home/zaks/bookkeeping/docs/ERROR-SHAPES.md`
  - Contents: Document every distinct error response shape found across services:
    - Backend ErrorResponse (structured, with ErrorCode)
    - Backend FastAPI HTTPException (detail string)
    - Agent-api validation error ({detail, errors})
    - Agent-api rate limit error ({error, detail, retry_after})
    - Agent-api SSE error (event: error with JSON payload)
    - Dashboard middleware 502 ({error, message, correlation_id})
  - For each shape: which endpoints emit it, what the dashboard normalizer does with it
  - Source: Audit findings Area 3, all evidence paths listed there
- P5-04: **Create test coverage gap report** at `/home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md`
  - Contents: The three coverage maps from the audit:
    - API endpoint coverage (93 endpoints, 32 tested, 61 untested)
    - Dashboard page E2E coverage (13 pages, 10 covered, 3 not)
    - FSM transition coverage (22 transitions, 1 tested via archive, 21 untested)
  - Plus: CI enforcement status (what runs where)
  - Source: Audit findings Area 4, all evidence paths listed there

### Gate P5

- All four documents exist and are non-empty
- Service topology document covers all 6 services
- Environment cross-reference includes all variables flagged as duplicated in the audit
- Error shape inventory covers all 6 distinct shapes identified
- Test coverage gap report includes all three matrices from the audit
- Documents are in `/home/zaks/bookkeeping/docs/` (standard bookkeeping location)

---

## Acceptance Criteria

### AC-1: Port Drift Eliminated
Zero references to port 8090 in active code (excluding comments). All Makefile and script references point to 8091.

### AC-2: Contract Violations Fixed
`Promise.all` replaced with `Promise.allSettled` in pipeline route. `console.error` used only for unexpected failures in dashboard API routes. Middleware proxy has explicit timeout.

### AC-3: Test Integrity
All test files reference canonical FSM stage names only. Playwright spec navigation matches test intent.

### AC-4: Environment Hygiene
README is accurate. .env.example files cover required variables. No hardcoded secrets in compose defaults.

### AC-5: Cross-Service Documentation
Four reference documents exist in bookkeeping documenting service topology, environment variables, error shapes, and test coverage gaps.

### AC-6: No Regressions
`make validate-local` passes after all changes. TypeScript compilation succeeds. No existing test breakage introduced by the remediation.

### AC-7: Bookkeeping
`/home/zaks/bookkeeping/CHANGES.md` updated with a remediation summary. All code changes committed with descriptive messages.

---

## Guardrails

1. **Do not implement Surfaces 10–14.** This mission fixes findings and creates documentation. The surface implementations are a separate mission
2. **Do not rename environment variables in running code.** Document the mapping, but renaming would break deployed configurations. Variable renaming is a Phase 1 task for the eventual Surface 11 implementation
3. **Do not modify generated files.** `api-types.generated.ts` and `backend_models.py` are off-limits per existing deny rules
4. **Do not remove the @pytest.mark.skip decorator** from skipped tests. Fix the stage names within them, but the decision to un-skip is separate
5. **Preserve existing health endpoint behavior.** Fix the resilience config to match reality — do not change what the services actually expose
6. **Surface 9 compliance** — All dashboard component changes must comply with `.claude/rules/design-system.md`
7. **WSL safety** — `sed -i 's/\r$//'` on any new .sh files. `sudo chown zaks:zaks` on files created under `/home/zaks/`
8. **Respect the pre-task protocol** — Read CLAUDE.md, run `make infra-check`, identify affected surfaces before writing code

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `apps/dashboard/Makefile` | P1 | Port 8090→8091, fix script path |
| `apps/dashboard/smoke-test.sh` | P1 | Port 8090→8091 (if present) |
| `apps/agent-api/app/core/resilience.py` | P1 | RAG health endpoint path |
| `apps/dashboard/src/middleware.ts` | P1, P2 | URL docs comment, proxy timeout |
| `apps/dashboard/src/app/api/pipeline/route.ts` | P2 | Promise.all → Promise.allSettled |
| `apps/dashboard/src/app/api/agent/activity/route.ts` | P2 | console.error → console.warn |
| `zakops-backend/tests/unit/test_idempotency.py` | P3 | Legacy stage names |
| `zakops-backend/tests/integration/test_golden_path_deal.py` | P3 | Legacy stage names |
| `apps/dashboard/tests/deals-bulk-delete.spec.ts` | P3 | Navigation URL fix |
| `apps/dashboard/README.md` | P4 | Remove stale references |
| `apps/agent-api/.env.example` | P4 | Add missing variables |
| `deployments/docker/docker-compose.yml` | P4 | Remove default secret |
| `apps/dashboard/audit/risk-assessment.md` | P4 | Fix performance baseline reference |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md` | P5 | Service registry reference |
| `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md` | P5 | Environment variable cross-reference |
| `/home/zaks/bookkeeping/docs/ERROR-SHAPES.md` | P5 | Error response shape inventory |
| `/home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md` | P5 | Test coverage gap matrices |

### Files to Read (sources of truth)
| File | Purpose |
|------|---------|
| `zakops-backend/src/core/deals/workflow.py` | Canonical FSM stages |
| `zakops-backend/src/api/shared/error_codes.py` | Error code definitions |
| `apps/dashboard/src/types/design-system-manifest.ts` | Surface 9 conventions |
| `apps/dashboard/src/types/execution-contracts.ts` | PIPELINE_STAGES authority |
| `apps/agent-api/app/core/config.py` | Agent config variable requirements |

---

## Stop Condition

Stop when all acceptance criteria AC-1 through AC-7 are met, `make validate-local` passes, and all code changes are committed. Produce a completion summary listing each AC with evidence paths.

Do not proceed to Surface 10–14 implementation. This mission's sole deliverable is a clean, consistent codebase and the four reference documents that the surface implementations will build on.

---

*End of Mission Prompt — SURFACE-REMEDIATION-001*

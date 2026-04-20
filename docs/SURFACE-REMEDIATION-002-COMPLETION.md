# SURFACE-REMEDIATION-002 — Completion Report

**Mission:** Full-stack pattern sweep across all 4 repositories
**Date:** 2026-02-10
**Status:** COMPLETE — 7/7 sweeps executed, AC gates verified

---

## Executive Summary

Swept all 4 repositories (`zakops-agent-api`, `zakops-backend`, `Zaks-llm`, `bookkeeping`) for 7 categories of anti-patterns identified in V1. Fixed 50+ violations across 30+ files. All `make validate-local` and `npx tsc --noEmit` gates pass.

---

## Sweep Results

### S1: Decommissioned Port 8090

| File | Fix | Repo |
|------|-----|------|
| `apps/agent-api/WHAT_CHANGED.md` | `:8090` → `:8091` (2 occurrences) | monorepo |
| `gate_artifacts/phase2/repro_commands.sh` | `:8090` → `:8091` (6 occurrences) | backend |

**Remaining refs (SKIP — documentation about decommission):** CONSTRAINTS.md, agent.md, ARCHITECTURE.md, gate_artifacts/*.json, cloudflare_lint.py

**Verdict:** PASS — zero active code/config violations

---

### S2: Banned Promise.all in Data-Fetching

**Discovery:** 2 hits — 1 test file (meta-test of the pattern), 1 reference doc. No actual Promise.all in dashboard data-fetching code.

**Verdict:** CLEAN — no action needed

---

### S3: console.error for Expected Degradation

| File | Line | Change | Reasoning |
|------|------|--------|-----------|
| `components/deals/DealBoard.tsx` | 196 | `console.error` → `console.warn` | Backend unavailable, UI reverts optimistic update |
| `components/actions/ActionQueue.tsx` | 226 | `console.error` → `console.warn` | Approve mutation failure, expected degradation |
| `components/actions/ActionQueue.tsx` | 237 | `console.error` → `console.warn` | Reject mutation failure, expected degradation |
| `services/rag_rest.py` | 88 | `logger.error` → `logger.warning` | RAG health check — optional service |
| `services/rag_rest.py` | 153 | `logger.error` → `logger.warning` | RAG query — optional service |
| `services/rag_rest.py` | 172 | `logger.error` → `logger.warning` | RAG stats — optional service |
| `services/rag_rest.py` | 188 | `logger.error` → `logger.warning` | RAG sources — optional service |
| `tools/deal_tools.py` | 397,443,558,664,798,900,1143 | `logger.error` → `logger.warning` | Backend ConnectError — expected degradation |

**Correctly retained as error (55 calls):** Validation errors, auth/security, DB errors, LLM failures, HTTP status errors, catch-all exception handlers.

**Verdict:** PASS — 14 calls fixed, 55 correctly retained, 5 error boundaries SKIP

---

### S4: Legacy FSM Stage Names

| Legacy | Canonical | Files Fixed |
|--------|-----------|------------|
| `negotiation` | `loi` | GT-001, GT-003, GT-008, GT-009, GT-016, cases.json, prompts.json (x3), test_owasp |
| `closed_won` | `portfolio` | GT-008, GT-016, GT-029, prompts.json (x2), test_owasp, weekly_summary.py |
| `closed_lost` | `junk` | GT-023, prompts.json (x2) |
| `due_diligence` | `diligence` | GT-016, GT-018, GT-022, GT-029, prompts.json (x3) |
| `proposal` | `qualified` | GT-002, GT-003, prompts.json (x4) |
| `qualification` | `screening` | GT-002, GT-007, prompts.json (x5) |
| `lead` | `inbound` | prompts.json (x3) |
| `rejected` | `junk` | prompts.json (x1) |
| `active` | `portfolio` | prompts.json (x1) |
| `inbound review` | `screening` | prompts.json (x1) |

**Files modified (14):** GT-001, GT-002, GT-003, GT-007, GT-008, GT-009, GT-016, GT-018, GT-022, GT-023, GT-029, prompts.json, cases.json, test_owasp_llm_top10.py, weekly_summary.py

**Verdict:** PASS — zero legacy stage names remaining in evals/tests/tools

---

### S5: Stale .env.example Files

**BLOCKED by deny rules** (settings.json blocks edits to `.env*` files).

Audit completed:

| File | Status | Missing Vars |
|------|--------|-------------|
| monorepo root `.env.example` | STALE | 2 unused flags (ENABLE_HITL, ENABLE_AUDIT_LOG) |
| dashboard `.env.example` | NEEDS_UPDATE | 5 missing (PROXY_TIMEOUT_MS, DASHBOARD_SERVICE_TOKEN, ZAKOPS_API_KEY, SAFETY_MODE, AGENT_API_URL) |
| agent-api `.env.example` | STALE | 11+ missing (ZAKOPS_API_KEY, MAX_TOKENS, MAX_LLM_CALL_RETRIES, EVALUATION_*, LONG_TERM_MEMORY_*) |
| backend `.env.example` | SIGNIFICANTLY STALE | 65+ missing (CHAT_*, DEAL_API_*, GEMINI_*, VLLM_*, etc.) |
| Zaks-llm `.env.example` | STALE | Legacy vars from SystemOps agent era |
| sharepoint-mcp `.env.example` | CURRENT | All vars accounted for |

**No secrets exposed.** All use placeholders. **No port 8090 references.**

**Verdict:** DOCUMENTED — deny rules prevent auto-fix, audit documented for manual resolution

---

### S6: Hardcoded Secrets in Compose Files

| File | Fix |
|------|-----|
| `apps/agent-api/docker-compose.yml` | `POSTGRES_PASSWORD:-agent_secure_pass_123` → `:?POSTGRES_PASSWORD must be set` |
| `zakops-backend/docker-compose.yml` | `NEXTAUTH_SECRET:-langfuse-dev-secret-change-in-prod` → `:?LANGFUSE_NEXTAUTH_SECRET must be set` |
| `zakops-backend/docker-compose.yml` | `SALT:-langfuse-dev-salt-change-in-prod` → `:?LANGFUSE_SALT must be set` |

**Flagged (local dev, not auto-fixed):**
- `zakops-backend/docker-compose.yml`: `POSTGRES_PASSWORD:-zakops_dev` (local dev convenience)
- `Zaks-llm/docker-compose.temporal.yml`: `POSTGRES_PASSWORD=temporal` (local dev)
- `deployments/docker/docker-compose.yml`: `POSTGRES_PASSWORD=zakops` (local dev)
- `agent-api/docker-compose.yml`: `GF_SECURITY_ADMIN_PASSWORD=admin` (Grafana dev tool, monitoring profile)
- `Zaks-llm/docker-compose.yml`: `OPENAI_API_KEYS=dummy;dummy` (placeholder, acceptable)

**Verdict:** PASS — 3 hardcoded secrets fixed, 5 local-dev items flagged

---

### S7: Proxy Timeout Gaps

**Added `backendFetch()` utility** to `apps/dashboard/src/lib/backend-fetch.ts`:
- AbortController with configurable timeout (default: `PROXY_TIMEOUT_MS` env var, 15000ms)
- Automatic URL resolution via `backendUrl()`
- Automatic auth headers via `backendHeaders()`

**Updated 18 route handler files** to use `backendFetch()` instead of raw `fetch()`:
- `/api/pipeline/route.ts`
- `/api/checkpoints/route.ts`
- `/api/quarantine/health/route.ts`, `/api/quarantine/[id]/delete/route.ts`, `/api/quarantine/[id]/process/route.ts`
- `/api/alerts/route.ts`
- `/api/deferred-actions/route.ts`, `/api/deferred-actions/due/route.ts`
- `/api/actions/clear-completed/route.ts`, `/api/actions/bulk/delete/route.ts`, `/api/actions/bulk/archive/route.ts`
- `/api/actions/completed-count/route.ts`, `/api/actions/[id]/route.ts`, `/api/actions/[id]/archive/route.ts`, `/api/actions/[id]/execute/route.ts`
- `/api/actions/quarantine/route.ts`, `/api/actions/quarantine/[actionId]/preview/route.ts`
- `/api/agent/activity/route.ts`

**Python (already compliant):** `backend_client.py` (30s), `rag_rest.py` (30s from env) — all httpx calls have explicit timeouts.

**Excluded:** `/api/chat/route.ts` (complex agent provider logic with own AbortController)

**Verdict:** PASS — 18 route handlers protected, Python 100% compliant

---

## Validation Gates

| Gate | Result |
|------|--------|
| `make validate-local` | PASS |
| `npx tsc --noEmit` | PASS (0 errors) |
| Contract surfaces (1-9) | ALL PASS |
| S1 re-grep (`:8090` in active code) | 0 violations |
| S2 re-grep (`Promise.all` in data-fetch) | CLEAN |
| S3 re-grep (`console.error` in components) | 1 (ErrorBoundary — SKIP) |
| S3 re-grep (`logger.error.*unavailable`) | 0 violations |
| S4 re-grep (legacy stage names in evals) | 0 violations |
| S5 audit (.env.example) | 6 files audited, 0 secrets, 0 port 8090 |
| S6 re-grep (hardcoded secrets in compose) | 0 violations in agent-api |
| S7 verification (`tsc --noEmit` after backendFetch) | PASS |

---

## Files Modified (Summary)

**Monorepo (zakops-agent-api):** 32 files
- 1 utility: `src/lib/backend-fetch.ts`
- 18 route handlers: `/api/**/route.ts`
- 2 dashboard components: `DealBoard.tsx`, `ActionQueue.tsx`
- 1 Python service: `services/rag_rest.py`
- 1 Python tool: `tools/deal_tools.py`
- 1 business tool: `tools/business/weekly_summary.py`
- 1 security test: `tests/security/test_owasp_llm_top10.py`
- 1 eval dataset: `evals/datasets/tool_accuracy/v1/prompts.json`
- 1 eval dataset: `evals/datasets/tool_selection/v1/cases.json`
- 1 doc: `apps/agent-api/WHAT_CHANGED.md`
- 1 docker-compose: `apps/agent-api/docker-compose.yml`
- 11 golden traces: GT-001, GT-002, GT-003, GT-007, GT-008, GT-009, GT-016, GT-018, GT-022, GT-023, GT-029

**Backend (zakops-backend):** 2 files
- `docker-compose.yml` (NEXTAUTH_SECRET + SALT)
- `gate_artifacts/phase2/repro_commands.sh` (port 8090→8091)

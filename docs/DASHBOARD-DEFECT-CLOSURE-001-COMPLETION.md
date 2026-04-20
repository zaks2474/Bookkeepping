# Completion Report: DASHBOARD-DEFECT-CLOSURE-001

**Date:** 2026-02-15
**Scope:** Final defect closure for dashboard pipeline, deal sub-resources, agent routing, and runtime validation
**Trigger:** Post-Route-Coverage-Remediation investigation revealed 5 remaining defect categories: stale pipeline view, missing deal sub-resource endpoints, broken sentiment path, inconsistent agent base-path construction, and absent runtime response validation
**Classification:** Defect Closure, Multi-Phase

---

## 1. Root Cause Analysis

### Problem Statement
After the Dashboard Route Coverage Remediation closed all missing route handlers, a second investigation revealed deeper structural defects:

1. **Pipeline counts showing zero** — the `v_pipeline_summary` view in `001_base_tables.sql` was stale (didn't match migration 023), and the backend had no error handling on the pipeline query
2. **Deal detail tabs empty** — `/api/deals/{id}/case-file`, `/enrichment`, `/materials` endpoints didn't exist
3. **Sentiment panel broken** — `api.ts` called `/api/agent/api/v1/chatbot/sentiment/` (double `/api` prefix) and no route handler existed
4. **Agent route base-path drift** — 7 route handlers each constructed `AGENT_API_URL` independently with inconsistent patterns (`/v1/` vs `/api/v1/`)
5. **No runtime validation** — backend responses for enrichment, tasks, sentiment, and case-file passed through `api.ts` without any shape checking

### Impact Assessment (Pre-Remediation)
- **HQ pipeline section**: showed 0 counts despite 9 active deals
- **Deal detail**: 3 tabs (Case File, Enrichment, Materials) rendered empty or errored
- **Sentiment trend**: never loaded (404 from double-prefixed path)
- **Agent chat routes**: worked by coincidence but had latent path bugs (missing `/api` prefix on threads)
- **Silent data corruption**: malformed backend responses could propagate to UI without warning

---

## 2. Execution Summary

### Phase Breakdown

| Phase | Description | Result |
|-------|-------------|--------|
| P0 | Verify reality — DB columns, endpoint states | PASS — migration 023 confirmed, all 3 sub-resources 404 |
| P1 | Pipeline fix — init script alignment + HTTPException(500) | PASS |
| P2 | Backend deal sub-resource endpoints (case-file, enrichment, materials) | PASS — 3 new endpoints verified |
| P3A | Sync chain — update-spec + sync-types + sync-backend-models + tsc | PASS — 0 TS errors |
| P3B | Zod runtime enforcement — safeParse for 4 endpoint responses | PASS |
| P4 | agentFetch helper + migrate all 8 agent route handlers + sentiment fix | PASS — 0 direct AGENT_API_URL in handlers |
| P5 | Surface 17 enforcement tightening — manifest, PROXY_PASS_EXCEPTIONS, WARN→FAIL | PASS — 44/44, 0 FAIL, 0 WARN, 2 INFO |
| P6 | Liveness + smoke upgrades — shape-validated probes, deal sub-resource checks | PASS |
| P7 | Final verification + CHANGES.md | PASS — all gates green |

### Session Structure
- **Session A (Backend):** Phases 0→1→2 — DB verification, pipeline fix, 3 new endpoints
- **Session B (Dashboard):** Phases 3A→3B→4 — sync chain, Zod schemas, agentFetch migration
- **Session C (Infra):** Phases 5→6→7 — S17 enforcement, liveness/smoke, final verification

---

## 3. Deliverables

### 3.1 Pipeline Reliability (Phase 1)

| Item | Detail |
|------|--------|
| Init script fix | `001_base_tables.sql` view now matches migration 023 |
| Error handling | `get_pipeline_summary()` raises `HTTPException(500)` on DB error |
| Fallback behavior | Dashboard route handler detects non-2xx → falls back to `/api/deals` counts |

**Design decision:** Backend raises HTTP 500 on pipeline query failure (NOT `200 []`), because the dashboard route handler checks `summaryResponse.ok` — returning `200 []` would suppress the fallback and show zero counts.

### 3.2 Deal Sub-Resource Endpoints (Phase 2)

| Endpoint | Response Shape | 404 Behavior |
|----------|---------------|-------------|
| `GET /api/deals/{id}/case-file` | `{ deal_id, version: "v1", generated_at, data: {deal, brain, counts} }` | Deal not found OR no brain data |
| `GET /api/deals/{id}/enrichment` | `{ deal_id, display_name, broker, aliases, materials, ... }` | Deal not found only (200 with defaults if no brain) |
| `GET /api/deals/{id}/materials` | `{ deal_id, deal_path, correspondence[], aggregate_links, pending_auth }` | Deal not found only (200 with empty correspondence if no approved items) |

**v1 structural defaults in materials:**
- `bundle_id`: `"qi-{quarantine_item_id}"` (traceable + unique)
- `format`: `"email"`, `attachments`: `[]`, `links`: `{ "all": [] }`
- `aggregate_links`: all zeros + empty arrays
- `pending_auth`: `[]`

### 3.3 Zod Runtime Enforcement (Phase 3B)

| Schema | Function | Failure Behavior |
|--------|----------|-----------------|
| `CaseFileEnvelopeSchema` | `getDealCaseFile()` | `console.warn` + return `null` |
| `DealEnrichmentSchema` | `getDealEnrichment()` | `console.warn` + return `null` |
| `DelegatedTaskSchema` + `DealTasksResponseSchema` | `getDealTasks()` | `console.warn` + return `{ tasks: [], count: 0 }` |
| `SentimentTrendSchema` | `getSentimentTrend()` | `console.warn` + return `null` |

### 3.4 agentFetch Helper (Phase 4)

**File:** `apps/dashboard/src/lib/agent-fetch.ts`

- Centralizes: base URL resolution (`AGENT_LOCAL_URL > AGENT_API_URL > NEXT_PUBLIC_AGENT_API_URL > localhost:8095`), service token injection, Content-Type header
- Exports: `agentFetch(path, options)` and `getAgentBaseUrl()`
- **8 route handlers migrated**, 0 direct `AGENT_API_URL` usage remaining in `src/app/api/`

**Sentiment fix:** Path corrected from `/api/agent/api/v1/chatbot/sentiment/${dealId}` to `/api/agent/sentiment/${dealId}` with new route handler at `app/api/agent/sentiment/[dealId]/route.ts`.

**Threads fix:** Path corrected from `/v1/chatbot/threads` (missing `/api`) to `/api/v1/chatbot/threads`.

### 3.5 Surface 17 Enforcement (Phase 5)

| Change | Detail |
|--------|--------|
| Manifest expanded | 43 → 44 entries (added sentiment) |
| `PROXY_PASS_EXCEPTIONS` | `/api/actions` and `/api/quarantine` root lists → INFO |
| Drift detection | Upgraded from WARN to FAIL |
| Dynamic segments | Added `[dealId]` to search patterns |
| **Final state** | 44/44 PASS, 0 FAIL, 0 WARN, 2 INFO |

### 3.6 Liveness + Smoke Upgrades (Phase 6)

**Liveness additions:**
- `/api/pipeline/summary` — shape check (`jq '.[0].stage'`)
- `/api/deals/{id}/case-file` — shape check (`jq '.deal_id'`)
- `/api/deals/{id}/enrichment` — shape check (`jq '.deal_id'`)
- `/api/deals/{id}/materials` — shape check (`jq '.deal_id'`)
- Pre-flight deal_id fetch; skip sub-resource probes with INFO if no deals

**Smoke additions:**
- Pipeline summary: verify JSON array with `stage` + `count` fields
- Deal sub-resources: verify 200 or 404 for case-file/enrichment/materials

---

## 4. Files Modified

### zakops-backend (2 files)

| File | Action |
|------|--------|
| `db/init/001_base_tables.sql` | EDIT — stale view → migration 023 version |
| `src/api/orchestration/main.py` | EDIT — HTTPException(500) on pipeline failure + 3 new endpoints |

### zakops-agent-api (11 files: 2 new, 9 edited)

| File | Action |
|------|--------|
| `apps/dashboard/src/lib/agent-fetch.ts` | **NEW** — centralized agentFetch helper |
| `apps/dashboard/src/app/api/agent/sentiment/[dealId]/route.ts` | **NEW** — sentiment proxy route |
| `apps/dashboard/src/lib/api.ts` | EDIT — Zod schemas + safeParse + sentiment path fix |
| `apps/dashboard/src/app/api/chat/complete/route.ts` | EDIT — migrate to agentFetch |
| `apps/dashboard/src/app/api/chat/threads/route.ts` | EDIT — migrate to agentFetch + fix /api prefix |
| `apps/dashboard/src/app/api/chat/threads/[id]/route.ts` | EDIT — migrate to agentFetch |
| `apps/dashboard/src/app/api/chat/threads/[id]/messages/route.ts` | EDIT — migrate to agentFetch |
| `apps/dashboard/src/app/api/chat/execute-proposal/route.ts` | EDIT — migrate to agentFetch |
| `apps/dashboard/src/app/api/agent/activity/route.ts` | EDIT — migrate to agentFetch |
| `apps/dashboard/src/app/api/chat/route.ts` | EDIT — migrate to agentFetch + getAgentBaseUrl |
| `tools/infra/validate-surface17.sh` | EDIT — manifest + PROXY_PASS_EXCEPTIONS + WARN→FAIL |
| `tools/infra/validate-endpoint-liveness.sh` | EDIT — shape-validated deal sub-resource probes |
| `tools/infra/smoke-test.sh` | EDIT — pipeline + deal detail assertions |

---

## 5. Verification Results

| Gate | Result |
|------|--------|
| `make validate-local` | PASS |
| `npx tsc --noEmit` | 0 errors |
| `make validate-surface17` | 44/44 PASS, 0 FAIL, 0 WARN, 2 INFO |
| `make validate-contract-surfaces` | ALL 17 SURFACES PASS |
| `validate-surface-count-consistency` | 4-way consistent (17) |

---

## 6. Deferred ENH Backlog

| ENH | Description | Reason Deferred |
|-----|-------------|-----------------|
| CI contract tests | Golden payload snapshots validating backend responses against Zod schemas | Requires backend-in-CI infrastructure (D3 decision) |
| Playwright E2E | DOM-level assertions for empty states, console error detection | Existing smoke tests cover HTTP-level; Playwright adds marginal value vs. effort |

---

## 7. Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | agentFetch helper + migrate ALL agent routes (Option B) | Prevents future base-path drift; single source of truth for agent URL |
| D2 | Synthetic `bundle_id = "qi-{id}"` for v1 materials | Traceable, unique, avoids null bundle_id breaking UI key props |
| D3 | CI contract tests deferred as ENH | Runtime Zod catches shape issues now; CI golden payloads need backend-in-CI |

---

## 8. Artifacts

| Artifact | Path |
|----------|------|
| Investigation Report | `/home/zaks/bookkeeping/docs/DASHBOARD-DEFECT-CLOSURE-001-INVESTIGATION.md` |
| Execution Quickstart | `/home/zaks/bookkeeping/docs/DASHBOARD-DEFECT-CLOSURE-001-QUICKSTART.md` |
| Completion Report | `/home/zaks/bookkeeping/docs/DASHBOARD-DEFECT-CLOSURE-001-COMPLETION.md` |
| Plan (v3) | `/root/.claude/plans/cozy-exploring-lobster.md` |
| CHANGES.md Entry | `/home/zaks/bookkeeping/CHANGES.md` (2026-02-15 DASHBOARD-DEFECT-CLOSURE-001) |

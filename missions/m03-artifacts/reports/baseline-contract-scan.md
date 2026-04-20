# Baseline Contract Scan — M03
**Date:** 2026-02-11
**Purpose:** Freeze current contract-drift inventory before remediation

## Violation 1: Non-502 Backend-Unavailable Responses (5 instances, 4 files)

| # | File | Line | Current Status | Error Key | Log Message |
|---|------|------|---------------|-----------|-------------|
| V1.1 | `app/api/actions/quarantine/[actionId]/preview/route.ts` | 49 | 500 | `backend_unavailable` | (implicit) |
| V1.2 | `app/api/chat/complete/route.ts` | 59 | 500 | `chat_error` | "Backend unavailable (degraded)" |
| V1.3 | `app/api/chat/execute-proposal/route.ts` | 34 | 500 | `proposal_error` | "Backend unavailable (degraded)" |
| V1.4 | `app/api/chat/route.ts` (POST) | 275 | 500 | `chat_error` | "Backend unavailable (degraded)" |
| V1.5 | `app/api/chat/route.ts` (GET) | 387 | 500 | (status field) | Connection error to agent |

### Classification Notes
- V1.1–V1.4: All are outer catch blocks for backend/agent connection failures. Clear 502 candidates.
- V1.5: GET health check endpoint — outer catch catches connection errors to agent API. This is an upstream unavailability condition (502), not an internal logic error. The 503 at line 379 correctly covers "agent reports unhealthy"; the 500 at line 387 should be 502 for "can't reach agent at all".

### Already-Correct Routes (27 instances)
Settings (preferences, email, account, data/export), quarantine CRUD, actions CRUD, deferred-actions, alerts, pipeline, checkpoints, onboarding, user/profile — all already return 502 for backend-unavailable.

## Violation 2: Hardcoded Stage Array (1 instance)

| # | File | Line | Current | Should Be |
|---|------|------|---------|-----------|
| V2.1 | `app/deals/new/page.tsx` | 20-28 | Local `const STAGES = [...]` | Import `PIPELINE_STAGES` from `execution-contracts.ts` |

### Note
`app/deals/page.tsx:58` already correctly uses `ALL_STAGES_ORDERED` from execution-contracts. Only `deals/new` has the violation.

## Violation 3: Client-Side Count Label (1 instance)

| # | File | Line | Current | Should Be |
|---|------|------|---------|-----------|
| V3.1 | `app/dashboard/page.tsx` | 209 | `{deals.length} active deals` | `{pipelineData?.total_active ?? deals.length}` |

### Context
- `pipelineData` is fetched via `getPipeline()` and has `total_active: number` field (server-computed)
- `deals` is fetched via `getDeals({ status: 'active' })` — could be a subset if pagination applies
- The label says "active deals" implying total semantics → server-computed value is correct

### Already-Correct Pages
- `deals/page.tsx` uses `totalCount` from server via `result.totalCount` (line 115) ✅

## Promise.allSettled Compliance

| Page | Multi-Fetch? | Uses allSettled? | Status |
|------|-------------|-----------------|--------|
| Dashboard | Yes (6 calls) | Yes (line 67) | ✅ Compliant |
| Deals | No (single `getDeals`) | N/A | ✅ Non-applicable (documented) |

## Total Remediation Items: 7
- 5 status code fixes (V1.1–V1.5)
- 1 stage source fix (V2.1)
- 1 count label fix (V3.1)

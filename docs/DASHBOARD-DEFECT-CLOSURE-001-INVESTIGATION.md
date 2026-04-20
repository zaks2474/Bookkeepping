# DASHBOARD-DEFECT-CLOSURE-001: Final Implementation Plan (v3)

> Incorporates: Investigation Report findings + Plan Patch Suggestions + Builder Review + User Decisions (D1-D3) + Pipeline Fallback Correction

---

## Confirmed Decisions

| # | Decision | Status |
|---|----------|--------|
| D1 | Phase 4 Option B: `agentFetch` helper + migrate ALL agent routes | APPROVED |
| D2 | Synthetic `bundle_id = "qi-{id}"` for v1 materials | APPROVED |
| D3 | CI contract tests deferred as ENH; runtime Zod now | APPROVED |

---

## Phase 0 — Verify Reality (no-code, fast)

### Tasks
1. Query DB: `SELECT column_name FROM information_schema.columns WHERE table_schema='zakops' AND table_name='v_pipeline_summary' ORDER BY ordinal_position;`
   - **Expect:** `stage`, `count`, `avg_days_in_stage`
2. Curl 3 deal sub-resource endpoints to confirm they 404 today:
   - `GET /api/deals/{sample_id}/case-file`
   - `GET /api/deals/{sample_id}/materials`
   - `GET /api/deals/{sample_id}/enrichment`
3. Curl pipeline summary: `GET /api/pipeline/summary` — confirm it returns data (or identify failure mode)

### Gate P0
- DB columns match expectation (or identify what's missing)
- All 3 deal sub-resources return 404 (confirming they don't exist yet)
- Pipeline summary state documented

---

## Phase 1 — Pipeline: Make Rebuild Regressions Impossible

### Tasks

| # | Task | File | Action |
|---|------|------|--------|
| 1-01 | Verify migration 023 applied | Live DB | Query column names (Phase 0 result) |
| 1-02 | If NOT applied: apply migration 023 | `db/migrations/023_stage_check_constraint.sql` | `psql -U zakops -d zakops -f ...` |
| 1-03 | Update init script view definition | `/home/zaks/zakops-backend/db/init/001_base_tables.sql:280-299` | EDIT — replace stale view with 023 version |
| 1-04 | Add try/except to `get_pipeline_summary()` | `/home/zaks/zakops-backend/src/api/orchestration/main.py:2636-2646` | EDIT — on DB error: `raise HTTPException(status_code=500, detail="Pipeline query failed")` |
| 1-05 | Verify pipeline works | Live test | `curl http://localhost:8091/api/pipeline/summary` |

### IMPORTANT: Pipeline Fallback Correction
Backend MUST raise `HTTPException(500)` on DB error — NOT return `200 []`.

**Why:** Dashboard route handler (`api/pipeline/route.ts`) checks `summaryResponse.ok`. If backend returns `200 []`, the route handler treats it as success and passes the empty array through — the `/api/deals` fallback never fires. Raising 500 causes `ok === false` → fallback activates → HQ still shows correct counts from deal data.

### Acceptance Criteria
- HQ shows non-zero stage counts when active deals exist
- If pipeline summary DB query fails but `/api/deals` works → HQ still shows correct counts via fallback
- If both fail → HQ shows zeros (expected safe empty state)
- Fresh DB init (`001_base_tables.sql`) produces correct view definition

### Gate P1
- `curl /api/pipeline/summary` returns JSON array with `count` field
- `001_base_tables.sql` view matches migration 023 (identical SQL)
- Backend has `raise HTTPException(status_code=500)` in except block (not return `[]`)

---

## Phase 2 — Backend Deal Sub-Resource Endpoints

**File:** EDIT `/home/zaks/zakops-backend/src/api/orchestration/main.py`
**Pattern:** Follows `list_deal_tasks` (main.py:2961) — verify deal exists, query related tables, return dict.
**Ownership:** Backend-owned. No dashboard route handlers needed (middleware catch-all proxies to backend).

### 2A: GET /api/deals/{deal_id}/materials

**Data sources:** `deals` (folder_path) + `quarantine_items` (approved, linked to deal)

**Contract (v1-safe, fully structured):**
```json
{
  "deal_id": "string (REQUIRED)",
  "deal_path": "string|null",
  "correspondence": [
    {
      "bundle_id": "qi-{quarantine_item_id}",
      "subject": "string|null",
      "from": "string|null",
      "date": "string|null (ISO timestamp)",
      "format": "email",
      "bundle_path": null,
      "attachments": [],
      "links": { "all": [] }
    }
  ],
  "aggregate_links": {
    "summary": { "primary_count": 0, "tracking_count": 0, "duplicates_removed": 0 },
    "primary_links": [],
    "tracking_links": [],
    "social_links": [],
    "unsubscribe_links": []
  },
  "pending_auth": []
}
```

**Behavior:**
- 200 with structured payload when deal exists (even if no approved quarantine items → empty correspondence)
- 404 only when deal doesn't exist

### 2B: GET /api/deals/{deal_id}/enrichment

**Data sources:** `deals` (display_name, broker, company_info) + `deal_brain` (summary_confidence, last_email_ingestion) + `deal_entity_graph` (aliases) + `email_threads` (last_email_at)

**Contract (v1-safe):**
```json
{
  "deal_id": "string (REQUIRED)",
  "display_name": "string|null",
  "target_company_name": "string|null",
  "broker": { "name": null, "email": null, "company": null, "phone": null, "domain": null },
  "last_email_at": "string|null (ISO timestamp)",
  "enrichment_confidence": 0,
  "enriched_at": "string|null (ISO timestamp)",
  "materials": { "total": 0, "by_type": {}, "auth_required_count": 0 },
  "aliases": []
}
```

**Behavior:**
- 200 with empty/default fields when deal exists but no brain data (enrichment section shows defaults, not hidden)
- 404 only when deal doesn't exist
- `materials.total = 0` → "Legacy enrichment links" section in Materials tab won't render (correct)

### 2C: GET /api/deals/{deal_id}/case-file

**Data sources:** `deals` + `deal_brain` + `deal_events` (count) + `email_threads` (count) + `delegated_tasks` (status summary)

**Contract (versioned envelope):**
```json
{
  "deal_id": "string (REQUIRED)",
  "version": "v1",
  "generated_at": "ISO timestamp",
  "data": {
    "deal": { "...full deal record..." },
    "brain": { "...deal_brain fields or null..." },
    "event_count": 0,
    "thread_count": 0,
    "task_summary": { "total": 0, "by_status": {} }
  }
}
```

**Behavior:**
- 200 with envelope when deal exists AND brain data is present
- 404 when deal doesn't exist OR brain data is absent → UI shows "Case file unavailable" + retry button
- Envelope metadata (`version`, `generated_at`) visible in raw JSON dump — useful for operators

### Gate P2
- `curl /api/deals/{existing_id}/case-file` → 200 with envelope containing `deal_id`, `version`, `data`
- `curl /api/deals/{existing_id}/enrichment` → 200 with all required keys
- `curl /api/deals/{existing_id}/materials` → 200 with structured correspondence + aggregate_links
- `curl /api/deals/NONEXISTENT/case-file` → 404 with `{ detail: "..." }`
- All 3 proxy through dashboard middleware → deal detail tabs populate

---

## Phase 3 — Sync Chain + Zod Enforcement

### 3A: Sync Chain
```bash
make update-spec                    # Fetch live OpenAPI → zakops-api.json
make sync-types                     # Backend OpenAPI → Dashboard TS types
make sync-backend-models            # Backend OpenAPI → Agent Python models
cd apps/dashboard && npx tsc --noEmit  # TypeScript compilation check
```

### 3B: Zod Runtime Enforcement

Add Zod schemas + `safeParse` for currently-unvalidated endpoints in `api.ts`:

| Endpoint | Current | Action |
|----------|---------|--------|
| enrichment | TS interface only | Add Zod schema + safeParse |
| tasks | TS interface only | Add Zod schema + safeParse |
| sentiment | No validation | Add Zod schema + safeParse |
| case-file | `unknown` | Add envelope Zod schema + safeParse |

**Fallback rules (consistent):**
- enrichment parse failure → return `null` + `console.warn`
- tasks parse failure → return `{ tasks: [], count: 0 }` + `console.warn`
- sentiment parse failure → return `null` + `console.warn`
- case-file parse failure → return `null` + `console.warn`

**Deferred (ENH):** CI contract tests validating backend responses against Zod schemas.

### Gate P3
- `npx tsc --noEmit` → 0 errors
- New endpoints appear in `packages/contracts/openapi/zakops-api.json`
- `make validate-local` → PASS
- Zod schemas exist for enrichment, tasks, sentiment, case-file
- Each has safeParse with console.warn on failure

---

## Phase 4 — Agent Routing: agentFetch Helper + Sentiment Fix (Option B)

### 4A: Create `agentFetch` Helper

**NEW file:** `apps/dashboard/src/lib/agent-fetch.ts`

```typescript
// Centralized agent API fetch — prevents base-path guessing
const AGENT_API_URL = process.env.AGENT_LOCAL_URL || process.env.AGENT_API_URL || 'http://localhost:8095';

export async function agentFetch(path: string, options?: RequestInit): Promise<Response> {
  // Normalize: path should start with /api/v1/ for agent API
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = `${AGENT_API_URL.replace(/\/$/, '')}${normalizedPath}`;
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
}
```

### 4B: Migrate Existing Agent Route Handlers

| File | Current Pattern | New Pattern |
|------|----------------|-------------|
| `chat/complete/route.ts` | `${AGENT_API_URL}/api/v1/chatbot/chat` | `agentFetch('/api/v1/chatbot/chat', ...)` |
| `chat/threads/route.ts` | `${AGENT_API_URL}/v1/chatbot/threads` | `agentFetch('/api/v1/chatbot/threads', ...)` (fix missing `/api`) |
| `agent/activity/route.ts` | `${AGENT_API_URL}/agent/activity` | `agentFetch('/api/v1/agent/activity', ...)` or keep if different API |
| Other agent routes | Various | Migrate to `agentFetch` |

### 4C: Create Sentiment Route Handler + Fix api.ts

1. **NEW** `apps/dashboard/src/app/api/agent/sentiment/[dealId]/route.ts`
   - GET handler using `agentFetch('/api/v1/chatbot/sentiment/${dealId}')`
   - Returns 502 JSON on agent unavailability

2. **EDIT** `apps/dashboard/src/lib/api.ts:2658`
   - Change from: `/api/agent/api/v1/chatbot/sentiment/${dealId}`
   - To: `/api/agent/sentiment/${dealId}`

### Gate P4
- `agentFetch` helper exists and is used by ALL agent route handlers
- No more direct `${AGENT_API_URL}` usage in route handlers (only in `agent-fetch.ts`)
- `getSentimentTrend` calls `/api/agent/sentiment/${dealId}`
- Route handler exists at `app/api/agent/sentiment/[dealId]/route.ts`
- `npx tsc --noEmit` → 0 errors
- No inconsistent base paths across agent routes

---

## Phase 5 — Surface 17 Enforcement Tightening

**File:** EDIT `tools/infra/validate-surface17.sh`

### Changes (ordered to prevent false positives)
1. Add sentiment route handler to manifest: `agent/sentiment/[dealId]/route.ts GET`
2. Add `PROXY_PASS_EXCEPTIONS` array:
   ```bash
   PROXY_PASS_EXCEPTIONS=(
     "/api/actions"      # Root list: proxies to backend GET /api/actions (main.py:1196)
     "/api/quarantine"   # Root list: proxies to backend GET /api/quarantine (main.py:1502)
   )
   ```
3. CHECK 3: unmatched endpoint → **FAIL** (not WARN)
4. Matched proxy-pass exceptions → **INFO** (with documented justification)

### Target State
- 44/44 PASS (43 existing + sentiment), 0 FAIL, 0 WARN, 2 INFO

### Gate P5
- `make validate-surface17` → 0 FAIL, 0 WARN
- Proxy-pass exceptions documented in script
- Adding a new `apiFetch('/api/foo')` without handler or exception → FAIL

---

## Phase 6 — Liveness + Smoke Upgrades

### 6A: Liveness Probe

**File:** EDIT `tools/infra/validate-endpoint-liveness.sh`

Add endpoints with **shape validation** (not just HTTP status):
- `GET /api/pipeline/summary` — verify `jq '.[0].stage'` exists
- `GET /api/deals/{sample_id}/case-file` — verify `jq '.deal_id'` exists
- `GET /api/deals/{sample_id}/enrichment` — verify `jq '.deal_id'` exists
- `GET /api/deals/{sample_id}/materials` — verify `jq '.deal_id'` exists

Pre-flight: fetch sample deal_id from `GET /api/deals?limit=1`. Skip deal sub-resource probes with INFO if no deals.

### 6B: Smoke Suite

**File:** EDIT `tools/infra/smoke-test.sh`

Add:
- HQ page: pipeline section renders (non-zero total when deals exist)
- Deal detail: case-file/enrichment/materials return expected 200/404
- Pipeline summary: verify JSON array with stage+count fields

**ENH (deferred):** Playwright E2E for DOM rendering, empty states, console error assertions.

### Gate P6
- `make validate-endpoint-liveness` → all endpoints return JSON with expected shape
- `make smoke-test` → all pages accessible
- Scripts have `chown zaks:zaks`, no CRLF

---

## Phase 7 — Verification + Completion

### Automated Gates (all must pass)
```bash
make validate-local                                    # PASS
cd apps/dashboard && npx tsc --noEmit                  # 0 errors
make validate-surface17                                # 0 FAIL, 0 WARN
make validate-contract-surfaces                        # all 17 surfaces PASS
bash tools/infra/validate-surface-count-consistency.sh # PASS (17)
make validate-endpoint-liveness                        # all endpoints JSON with shape
make smoke-test                                        # all pages accessible
```

### Completion
- Update `/home/zaks/bookkeeping/CHANGES.md`
- Update completion report
- Register ENH: CI contract tests (golden payload snapshots)
- Register ENH: Playwright E2E for empty states

---

## Dependency Graph

```
Phase 0 (Verify reality — no code)
    │
    ▼
Phase 1 (Pipeline verify + init fix + HTTPException)
    │
    ▼
Phase 2 (3 backend endpoints) ──→ Phase 3A (Sync chain)
                                       │
                                       ▼
                                 Phase 3B (Zod enforcement)
                                       │
                                       ▼
                                 Phase 4 (agentFetch + sentiment + migrate routes)
                                       │
                                       ▼
                                 Phase 5 (S17 enforcement)
                                       │
                                       ▼
                                 Phase 6 (Liveness + smoke)
                                       │
                                       ▼
                                 Phase 7 (Verification + completion)
```

---

## Files Summary

### zakops-backend (2 files edited)
| File | Action |
|------|--------|
| `db/init/001_base_tables.sql` | EDIT: update stale view to match migration 023 |
| `src/api/orchestration/main.py` | EDIT: 3 new endpoints + HTTPException on pipeline failure |

### zakops-agent-api (8+ files edited, 2 new)
| File | Action |
|------|--------|
| `apps/dashboard/src/lib/agent-fetch.ts` | NEW: agentFetch helper |
| `apps/dashboard/src/app/api/agent/sentiment/[dealId]/route.ts` | NEW: sentiment proxy route |
| `apps/dashboard/src/lib/api.ts` | EDIT: fix sentiment path + add Zod schemas |
| `apps/dashboard/src/app/api/chat/complete/route.ts` | EDIT: migrate to agentFetch |
| `apps/dashboard/src/app/api/chat/threads/route.ts` | EDIT: migrate to agentFetch (fix /api prefix) |
| `apps/dashboard/src/app/api/agent/activity/route.ts` | EDIT: migrate to agentFetch |
| `tools/infra/validate-surface17.sh` | EDIT: PROXY_PASS_EXCEPTIONS + WARN→FAIL + manifest |
| `tools/infra/validate-endpoint-liveness.sh` | EDIT: 4 new probes with shape validation |
| `tools/infra/smoke-test.sh` | EDIT: pipeline + deal detail assertions |

### bookkeeping (2 files)
| File | Action |
|------|--------|
| `CHANGES.md` | Record all changes |
| `docs/DASHBOARD-DEFECT-CLOSURE-001-INVESTIGATION.md` | Update with final results |

---

## Rollback Plan

- All changes are additive or view alignment. No destructive operations.
- Phase 1: Revert `001_base_tables.sql` edit + revert main.py HTTPException. Migration 023 stays.
- Phase 2: Remove 3 endpoint functions from main.py, restart backend.
- Phase 3: `git checkout -- packages/contracts/` + re-run sync. Remove Zod schemas from api.ts.
- Phase 4: Remove agentFetch, revert route handlers to direct fetch.
- Phase 5-6: `git checkout` on validator scripts.

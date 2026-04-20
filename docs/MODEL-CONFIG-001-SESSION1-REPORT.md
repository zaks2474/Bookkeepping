# MODEL-CONFIG-001 — Session 1 Report
## Phases P0–P2: Database + Backend API + Dashboard Wiring

**Date:** 2026-02-21
**Executor:** Claude Opus 4.6
**Branch:** `feat/model-config-001` (2 commits)
**Status:** SESSION 1 COMPLETE — 3 of 9 phases done

---

## Phases Completed

| Phase | Name | Gate | Status |
|-------|------|------|--------|
| P0 | Discovery & Baseline | `make validate-local`, `npx tsc --noEmit`, encryption check | PASS |
| P1 | Database + Backend API | All 8 endpoints verified via curl | PASS |
| P2 | Dashboard Proxy + Types + Hooks | `npx tsc --noEmit`, OpenAPI synced | PASS |

## Phases Remaining

| Phase | Name | Session |
|-------|------|---------|
| P3 | Settings UI Redesign | Session 2 |
| P4 | Chat Quick-Switch + Route Rewrite | Session 2 |
| P5 | Google AI Provider | Session 2 |
| P6 | Model Management Page | Session 3 |
| P7 | Cleanup + Surface Compliance + E2E Tests | Session 3 |
| P8 | Final Validation + Completion Report | Session 3 |

---

## Phase 0 — Discovery & Baseline

All preconditions verified:
- `make validate-local`: PASS
- `npx tsc --noEmit`: PASS
- `is_encryption_available()`: True (Fernet key set in backend container)
- `cryptography>=42.0.0`: Present in requirements.txt
- Latest migration: 038 → next is 039

---

## Phase 1 — Database Schema + Backend API

### Migration 039
- Table `zakops.model_configurations` with 15 columns
- Partial unique index `idx_one_active_per_context` enforces exactly one active model per (user_id, context)
- UNIQUE constraint on `(user_id, context, provider)` — one config per provider per context
- Seed data: local vLLM for chat (active) and email_triage (inactive)

### Backend Router (8 Endpoints)

| Method | Path | Purpose | Verified |
|--------|------|---------|----------|
| GET | `/api/user/model-config` | List all configs (keys hidden) | Yes |
| GET | `/api/user/model-config/active` | Active model per context | Yes |
| PUT | `/api/user/model-config` | Upsert with encrypted key storage | Yes |
| POST | `/api/user/model-config/activate` | Transactional activation | Yes |
| POST | `/api/user/model-config/test` | Rate-limited connection test (10s/provider, 15s timeout) | Yes |
| POST | `/api/user/model-config/resolve` | Internal-only key resolution (token + Origin protected) | Yes |
| DELETE | `/api/user/model-config/{id}` | Delete with guardrails (409 for active/local) | Yes |
| POST | `/api/user/model-config/migrate` | Batch localStorage migration (all-or-nothing) | Yes |

### Security Verification
- API keys encrypted via Fernet, version > 0 enforced (503 if encryption unavailable)
- GET responses return `has_api_key: bool` — never the actual key
- Resolve endpoint returns 403 without `X-Internal-Resolve-Token` header
- Resolve endpoint rejects requests with non-null `Origin` header
- All key lifecycle events logged to `deal_events` (aggregate_type='model_config')

### Key Propagation
- Saving an API key for provider X propagates to ALL contexts for that provider
- Verified: set OpenAI key for chat → email_triage OpenAI row also gets `has_api_key: true`

### Delete Guardrails
- Cannot delete active model → 409 "Switch to another model first"
- Cannot delete local provider → 409 "Local provider cannot be removed"

### Rate Limiting
- Connection test: max 1 per provider per 10 seconds → 429 on second attempt
- Verified via consecutive curl requests

---

## Phase 2 — Dashboard Proxy + Types + React Query Hooks

### OpenAPI Sync Chain
```
make update-spec → make sync-types → npx tsc --noEmit  ← ALL PASS
```

### Types (`model-config-types.ts`)
- `ModelContext`: 'chat' | 'email_triage'
- `ModelProvider`: 'local' | 'openai' | 'anthropic' | 'google' | 'custom'
- `ModelConfig`, `ActiveModels`, `ModelConfigCreate`, `ModelConfigActivate`, `ModelConfigTestResult`, `MigrationItem`
- `ProviderMeta` with static `PROVIDERS` array (5 providers, models, apiKeyPrefix, docsUrl)
- Helper functions: `detectProviderFromKey()`, `getProviderMeta()`, `formatRelativeTime()`

### API Client (`model-config-api.ts`)
- 7 functions: `fetchModelConfigs`, `fetchActiveModels`, `upsertModelConfig`, `setActiveModel`, `testModelConnection`, `deleteModelConfig`, `migrateFromLocalStorage`
- All use `fetch('/api/settings/models/...')` with shared `handleResponse<T>()` error handler

### Proxy Routes (4 files)
| Route File | Methods | Backend Target |
|-----------|---------|---------------|
| `models/route.ts` | GET, PUT, DELETE | `/api/user/model-config` |
| `models/active/route.ts` | GET, POST | `/api/user/model-config/active`, `/activate` |
| `models/test/route.ts` | POST | `/api/user/model-config/test` (20s proxy timeout) |
| `models/migrate/route.ts` | POST | `/api/user/model-config/migrate` |

All use `backendFetch()` with automatic API key injection and timeout.

### React Query Hooks (`useModelConfig.ts`)
| Hook | Type | Cache |
|------|------|-------|
| `useModelConfigs()` | query | 30s staleTime |
| `useActiveModels()` | query | 10s staleTime |
| `useUpsertModelConfig()` | mutation | invalidates all |
| `useSetActiveModel()` | mutation | optimistic update + rollback |
| `useTestModelConnection()` | mutation | invalidates list |
| `useDeleteModelConfig()` | mutation | invalidates all |
| `useMigrateFromLocalStorage()` | mutation | invalidates all |

---

## Files Created

| # | File | Phase | Lines |
|---|------|-------|-------|
| 1 | `apps/backend/db/migrations/039_model_configurations.sql` | P1 | 53 |
| 2 | `apps/backend/db/migrations/039_model_configurations_rollback.sql` | P1 | 10 |
| 3 | `apps/backend/src/api/orchestration/routers/model_config.py` | P1 | ~500 |
| 4 | `apps/dashboard/src/lib/settings/model-config-types.ts` | P2 | 165 |
| 5 | `apps/dashboard/src/lib/settings/model-config-api.ts` | P2 | 79 |
| 6 | `apps/dashboard/src/hooks/useModelConfig.ts` | P2 | 164 |
| 7 | `apps/dashboard/src/app/api/settings/models/route.ts` | P2 | 82 |
| 8 | `apps/dashboard/src/app/api/settings/models/active/route.ts` | P2 | 53 |
| 9 | `apps/dashboard/src/app/api/settings/models/test/route.ts` | P2 | 35 |
| 10 | `apps/dashboard/src/app/api/settings/models/migrate/route.ts` | P2 | 34 |

## Files Modified

| # | File | Phase | Change |
|---|------|-------|--------|
| 1 | `apps/backend/src/api/orchestration/main.py` | P1 | Router registration |
| 2 | `packages/contracts/openapi/zakops-api.json` | P2 | Model config endpoints added |
| 3 | `apps/dashboard/src/lib/api-types.generated.ts` | P2 | Regenerated from OpenAPI |
| 4 | `apps/agent-api/app/schemas/backend_models.py` | P2 | Regenerated (Surface 2 sync) |

---

## Validation Results

| Check | Result |
|-------|--------|
| `make validate-local` | PASS |
| `npx tsc --noEmit` | PASS |
| Contract surfaces (17/17) | ALL PASS |
| Surface 2 stale codegen | RESOLVED (regenerated locally) |

---

## Issues Encountered & Resolved

| # | Issue | Resolution |
|---|-------|-----------|
| 1 | Import path wrong (3 dots vs 4 dots) | `from ....core.security.encryption` — routers/ is 4 levels deep |
| 2 | curl 401 on backend | Added `X-API-Key` header from container env |
| 3 | No `agent_events` table | Used `deal_events` with `aggregate_type='model_config'` |
| 4 | `src/lib/` in root `.gitignore` | Force-add with `git add -f` |
| 5 | Surface 2 stale codegen (4 sessions) | `datamodel-codegen` not in container; ran locally |

---

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | (P1) | `MODEL-CONFIG-001 P1: Database schema + backend API endpoints` |
| 2 | e3ec490 | `MODEL-CONFIG-001 P2: Dashboard proxy, types, React Query hooks` |

---

## Session 2 Entry Point

Start at **Phase 3 — Settings UI Redesign**. All backend endpoints and dashboard infrastructure are ready. Key files to consume:

- Types: `apps/dashboard/src/lib/settings/model-config-types.ts`
- API: `apps/dashboard/src/lib/settings/model-config-api.ts`
- Hooks: `apps/dashboard/src/hooks/useModelConfig.ts`
- Plan: `/home/zaks/bookkeeping/docs/MODEL-CONFIG-001.md` (Phases P3-P5)
- Checkpoint: `/home/zaks/bookkeeping/mission-checkpoints/MODEL-CONFIG-001.md`

# MISSION: MODEL-CONFIG-001
## Simplified Multi-Model Configuration (LangSmith-Style UX)
## Date: 2026-02-21
## Classification: Feature Build (Full-Stack, XL)
## Prerequisite: SYSTEM-MATURITY-REMEDIATION-001 (Complete 2026-02-20)
## Successor: QA-MC-VERIFY-001

---

## Mission Objective

**What:** Replace the broken localStorage-based provider system with a server-persisted, encrypted, LangSmith-inspired multi-model configuration. Two independent model contexts (Chat Agent + Email Triage Agent), one-click switching, real connection tests, and a clean UX.

**What this is NOT:** This is NOT an agent-api runtime override mission. The email triage context is stored but the agent-api `LLMRegistry` is not modified. That is a separate follow-up. This is NOT a CORS remediation mission — the `allow_origins=["*"]` is a known issue tracked separately.

**Source material:**
- 8 LangSmith UI screenshots (provided by user 2026-02-21)
- 3-Pass Escalation Report: `/home/zaks/bookkeeping/docs/MODEL-CONFIG-001-3PASS-ESCALATION.md`
- Broken provider system: `apps/dashboard/src/lib/settings/provider-settings.ts` (localStorage only)
- Encryption module: `apps/backend/src/core/security/encryption.py` (Fernet, key versioning)

---

## Context

**What exists now (broken):**
- `apps/dashboard/src/lib/settings/provider-settings.ts` — localStorage only, never reaches agent-api
- `apps/dashboard/src/components/settings/ProviderSection.tsx` — radio buttons for 4 providers, fake connection tests (format validation only)
- `apps/dashboard/src/app/api/chat/route.ts` — reads `body.providerConfig` from client (API keys sent in request body)
- `apps/agent-api/app/services/llm.py` — `LLMRegistry` initialized at startup from env vars, no runtime switching
- `apps/backend/` — no model config endpoints, no model tables
- Email triage (`email_triage_review_email.py`, 851 lines) — purely regex/keyword extraction, zero LLM calls

**What we build:**
- Server-persisted model configs with encrypted API keys (Fernet, mandatory — no plaintext fallback)
- Backend CRUD endpoints + real connection test (server-side API call with latency measurement)
- Dashboard settings redesign: tab-based dual-context selector with paste-aware key input
- Chat header always-visible model name with quick-switch dropdown (LangSmith-style)
- Chat route reads active model from backend via model-resolver module (not localStorage)
- Google AI provider added (Gemini models)
- One-time transactional localStorage migration to server

**Contract Surfaces Affected:** 1 (Backend → Dashboard), 8 (Agent Config), 9 (Design System), 11 (Env Registry), 12 (Error Taxonomy), 17 (Dashboard Route Coverage)

---

## Glossary

| Term | Definition |
|------|-----------|
| Model context | Independent model selection scope: `chat` (main agent) or `email_triage` (email processing). Email triage context is stored for future use — the current runtime is rule-based, not model-based. |
| Provider | An LLM API service: local (vLLM), openai, anthropic, google, custom |
| Active model | The model+provider currently selected for a given context. Enforced by a partial unique index: exactly one `is_active=true` per (user_id, context) |
| Model resolver | Dashboard-side module (`model-resolver.ts`) that reads active config from backend, caches it, and creates the appropriate provider instance |
| Shared key model | One API key per (user_id, provider). When a key is saved for any context, it propagates to all contexts for that provider |
| Text-only mode | Cloud providers do not receive ZakOps tools (security boundary). Preserved from existing architecture |

---

## Architectural Constraints

- **Mandatory encryption for API keys** — Reuse `apps/backend/src/core/security/encryption.py` (`encrypt_token()` / `decrypt_token()`). Keys encrypted at rest via Fernet. If `is_encryption_available()` returns `false`, the PUT endpoint MUST return HTTP 503 — never store version-0 (plaintext) keys. <!-- Adopted from 3-Pass Finding S1 -->
- **No decrypted keys in browser-visible HTTP** — Decrypted API keys never appear in any response visible to the browser. The resolve mechanism uses internal-only auth. GET endpoints return `has_api_key: bool`, never the key itself. <!-- Adopted from 3-Pass Findings A2, S2 -->
- **Partial unique index for active model invariant** — `CREATE UNIQUE INDEX ... WHERE is_active = true` ensures exactly one active model per (user_id, context) at the DB level. Application code wraps activation in a transaction. <!-- Adopted from 3-Pass Finding A1 -->
- **Promise.allSettled mandatory** — All multi-fetch in dashboard uses `Promise.allSettled` with typed fallbacks. `Promise.all` is banned.
- **console.warn for degradation** — Provider unavailable = `console.warn`. Decryption failure = `console.error`.
- **Surface 9 compliance** — New UI follows design system rules (per `.claude/rules/design-system.md`).
- **Port 8090 FORBIDDEN** — Never reference.
- **Contract surface discipline** — `make update-spec → make sync-types → npx tsc --noEmit` after backend API changes.
- **Generated files never edited** — Use bridge types only.
- **Local-first architecture** — Local vLLM remains default/primary. Cloud providers are opt-in.
- **Text-only mode for cloud** — Cloud providers don't get ZakOps tools (existing pattern, preserved).

---

## Anti-Pattern Examples

### WRONG: API keys in localStorage
```typescript
localStorage.setItem('zakops-provider-settings', JSON.stringify({ openai: { apiKey: 'sk-...' } }));
```

### RIGHT: API keys encrypted server-side
```typescript
await fetch('/api/settings/models', {
  method: 'PUT',
  body: JSON.stringify({ provider: 'openai', api_key: 'sk-...', model: 'gpt-4.1', context: 'chat' }),
});
// Backend encrypts immediately, GET never returns the key (only has_api_key: true/false)
```

### WRONG: Client sends API key on every chat request
```typescript
const providerConfig = JSON.parse(localStorage.getItem('zakops-provider-settings'));
fetch('/api/chat', { body: JSON.stringify({ providerConfig }) }); // key in request body!
```

### RIGHT: Server resolves model config internally
```typescript
// model-resolver.ts (server-side only):
const activeModel = await getActiveModelConfig('chat'); // reads from backend, cached 10s
const apiKey = await resolveApiKey(activeModel.id); // internal-only, never browser-visible
const provider = createProvider(activeModel.provider, activeModel.model, apiKey);
```

### WRONG: Silent plaintext fallback when encryption unavailable
```python
encrypted, version = encrypt_token(api_key)  # Returns (plaintext, 0) silently!
row = await conn.execute("INSERT ... VALUES ($1, $2)", encrypted, version)
```

### RIGHT: Refuse to store without encryption
```python
if not is_encryption_available():
    raise HTTPException(503, "API key encryption not configured. Contact administrator.")
encrypted, version = encrypt_token(api_key)
assert version > 0, "Encryption must produce version > 0"
```

### WRONG: Delete active model, leaving no active
```
DELETE /api/user/model-config/42  → 200 OK  (but that was the active chat model!)
```

### RIGHT: Guard deletes
```
DELETE /api/user/model-config/42  → 409 "Deactivate this model first by switching to another"
DELETE /api/user/model-config/1   → 409 "Local provider cannot be removed"
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Encryption key unset after deploy → PUT returns 503, user can't save any keys | MEDIUM | Feature unusable | Phase 0 hard gate: verify `TOKEN_ENCRYPTION_KEY` is set. Phase 7 adds to env registry (Surface 11) |
| 2 | Two concurrent activate requests leave 0 or 2 active models | MEDIUM | Broken chat routing | A1: Partial unique index + transactional activation in Phase 1 |
| 3 | Chat route cache returns stale model after switch → user sees old model for 10s | MEDIUM | UX friction | Mutation invalidates cache immediately + toast confirms switch |
| 4 | Resolve endpoint called from browser via CORS * → key exfiltration | HIGH | Security breach | S2: Internal-only auth token + Origin header rejection on resolve |
| 5 | localStorage migration partially succeeds → keys in limbo | MEDIUM | Data loss | S5: Batch migration endpoint, all-or-nothing transaction, don't clear localStorage until confirmed |
| 6 | Connection test hangs on unresponsive provider API | MEDIUM | Backend worker stuck | S3: 15s timeout + 10s per-provider rate limit |
| 7 | CRLF in new .sh files | LOW | Script breakage | WSL safety checklist in every phase |

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ▼
Phase 1 (Database + Backend API)
    │
    ▼
Phase 2 (Dashboard Proxy + Types + Hooks) ─────┐
    │                                            │
    ▼                                            │
Phase 3 (Settings UI Redesign)                   │
    │                                            │
    ▼                                            │
Phase 4 (Chat Quick-Switch + Route Rewrite) ◄────┘
    │
    ▼
Phase 5 (Google AI Provider)
    │
    ▼
Phase 6 (Model Management Page)
    │
    ▼
Phase 7 (Cleanup + Surface Compliance + E2E Tests)
    │
    ▼
Phase 8 (Final Validation + Completion Report)
```

Phases execute sequentially. Phase 2 produces the types/hooks needed by both Phase 3 and Phase 4.

---

## Phase 0 — Discovery & Baseline
**Complexity:** S | **Touch points:** 0 files modified

**Purpose:** Verify baseline, confirm encryption availability, identify affected surfaces.

### Blast Radius
- **Services:** None
- **Pages:** None
- **Downstream:** All subsequent phases depend on P0 passing

### Tasks
- P0-01: Run `make validate-local` — baseline must pass
- P0-02: Run `npx tsc --noEmit` in `apps/dashboard` — baseline must pass
- P0-03: Verify `TOKEN_ENCRYPTION_KEY` is set in backend Docker env AND `is_encryption_available()` returns `True`
  - **Checkpoint:** If encryption unavailable, STOP. Do not proceed. Fix the env first.
- P0-04: Verify `encryption.py` has `encrypt_token()` and `decrypt_token()` at `apps/backend/src/core/security/encryption.py`
- P0-05: Verify `cryptography>=42.0.0` is in `apps/backend/requirements.txt`
- P0-06: Confirm latest migration is `038_artifact_versioning.sql` → next is `039`
- P0-07: Identify affected surfaces: 1, 8, 9, 11, 12, 17 with corresponding gates:
  - `make validate-surface9` (Design System)
  - `make validate-surface11` (Env Registry)
  - `make validate-surface12` (Error Taxonomy)
  - `make validate-surface17` (Dashboard Route Coverage)

### Gate P0
- `make validate-local` PASS
- `npx tsc --noEmit` PASS
- `is_encryption_available()` returns `True` (hard stop if not)
- `cryptography>=42.0.0` confirmed in requirements.txt

---

## Phase 1 — Database Schema + Backend API
**Complexity:** L | **Touch points:** 4 files created, 1 modified

**Purpose:** Create the `model_configurations` table with encrypted key storage, partial unique index, and backend CRUD+test+resolve endpoints with mandatory encryption, rate limiting, timeout, audit logging, and delete guardrails.

### Blast Radius
- **Services:** Backend (port 8091)
- **Pages:** None yet (backend only)
- **Downstream:** Dashboard proxy (Phase 2), chat route (Phase 4)

### Tasks

- P1-01: **Create migration** `apps/backend/db/migrations/039_model_configurations.sql`
  - Table `zakops.model_configurations` with columns:
    - `id` (SERIAL PRIMARY KEY)
    - `user_id` (VARCHAR, default 'default')
    - `context` (VARCHAR, CHECK IN ('chat', 'email_triage'))
    - `provider` (VARCHAR, CHECK IN ('local', 'openai', 'anthropic', 'google', 'custom'))
    - `model` (VARCHAR)
    - `is_active` (BOOLEAN, default false)
    - `api_key_encrypted` (TEXT, nullable)
    - `api_key_version` (INTEGER, default 0)
    - `endpoint` (VARCHAR, nullable — for local/custom only)
    - `last_test_status` (VARCHAR, nullable — 'success'/'error'/'timeout')
    - `last_test_at` (TIMESTAMPTZ, nullable)
    - `last_test_message` (TEXT, nullable)
    - `last_test_latency_ms` (INTEGER, nullable) <!-- 3-Pass U2 -->
    - `created_at` (TIMESTAMPTZ, default NOW())
    - `updated_at` (TIMESTAMPTZ, default NOW())
  - UNIQUE constraint on `(user_id, context, provider)`
  - Partial unique index: `CREATE UNIQUE INDEX idx_one_active_per_context ON zakops.model_configurations (user_id, context) WHERE is_active = true;` <!-- 3-Pass A1 -->
  - Seed default local configs for both contexts (is_active=true for chat, is_active=false for email_triage)
  - **Checkpoint:** Run migration, verify table + index exist

- P1-02: **Create rollback** `apps/backend/db/migrations/039_model_configurations_rollback.sql`

- P1-03: **Create backend router** `apps/backend/src/api/orchestration/routers/model_config.py`

  Endpoints:
  - `GET /api/user/model-config` — List all configs. API key NEVER returned — only `has_api_key: bool`. Include `last_test_latency_ms` in response.
  - `GET /api/user/model-config/active` — Active model per context: `{ chat: {...}, email_triage: {...} }`
  - `PUT /api/user/model-config` — Upsert config:
    - Check `is_encryption_available()` first → 503 if false <!-- 3-Pass S1 -->
    - Encrypt API key with `encrypt_token()`, assert version > 0
    - Propagate API key to ALL rows matching (user_id, provider) regardless of context <!-- 3-Pass A5 -->
    - Return upserted config (without key)
    - Log `model_config.key_stored` to `zakops.agent_events` <!-- 3-Pass S4 -->
  - `POST /api/user/model-config/activate` — Set active model:
    - Wrap in transaction: `BEGIN → UPDATE SET is_active=false WHERE context=$1 → UPDATE SET is_active=true WHERE id=$2 → COMMIT`
    - Log `model_config.activated` to `zakops.agent_events` <!-- 3-Pass S4 -->
  - `POST /api/user/model-config/test` — Real server-side connection test:
    - Rate limit: max 1 test per provider per 10 seconds (in-memory dict) → 429 if exceeded <!-- 3-Pass S3 -->
    - Timeout: `asyncio.wait_for(test_call, timeout=15.0)` → structured timeout error <!-- 3-Pass S3 -->
    - Decrypt key → call provider API with minimal prompt → measure latency → store result + latency_ms
    - Auto-test on key save: trigger test after successful PUT with api_key <!-- 3-Pass U5 -->
    - Log `model_config.test_executed` to `zakops.agent_events` <!-- 3-Pass S4 -->
  - `POST /api/user/model-config/resolve` — Internal-only:
    - Check `X-Internal-Resolve-Token` header matches `INTERNAL_RESOLVE_TOKEN` env var → 403 if missing/wrong <!-- 3-Pass A2, S2 -->
    - Check `Origin` header → reject non-null origins (block browser requests) <!-- 3-Pass S2 -->
    - Returns decrypted API key for active model (server-to-server only)
    - NOT included in OpenAPI spec (excluded from codegen)
    - Log every call as security event <!-- 3-Pass S4 -->
  - `DELETE /api/user/model-config/{config_id}` — Delete with guardrails:
    - Cannot delete where `is_active=true` → 409 "Switch to another model first" <!-- 3-Pass A6 -->
    - Cannot delete where `provider='local'` → 409 "Local provider cannot be removed" <!-- 3-Pass A6 -->
    - Log `model_config.key_deleted` to `zakops.agent_events` <!-- 3-Pass S4 -->
  - `POST /api/user/model-config/migrate` — Batch migration endpoint:
    - Accepts array of configs from localStorage <!-- 3-Pass S5 -->
    - Stores all-or-nothing in a single transaction
    - Returns success/failure for the batch

  - **Checkpoint:** All endpoints return valid JSON via curl

- P1-04: **Register router** in `apps/backend/src/api/orchestration/main.py`
  - Add `from .routers.model_config import router as model_config_router`
  - Add `app.include_router(model_config_router)` after `preferences_router`

### Rollback Plan
1. Drop table: `psql -U zakops -d zakops -f 039_model_configurations_rollback.sql`
2. Remove router import from `main.py`
3. `make validate-local` passes

### Gate P1
```bash
# Run migration
psql -U zakops -d zakops -f apps/backend/db/migrations/039_model_configurations.sql
# Verify partial unique index exists
psql -U zakops -d zakops -c "\di zakops.idx_one_active_per_context"
# Rebuild + restart backend
cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend
# Test endpoints
curl -sf http://localhost:8091/api/user/model-config | python3 -m json.tool
curl -sf http://localhost:8091/api/user/model-config/active | python3 -m json.tool
# Upsert test (should succeed)
curl -sf -X PUT http://localhost:8091/api/user/model-config \
  -H "Content-Type: application/json" \
  -d '{"context":"chat","provider":"openai","model":"gpt-4.1","api_key":"sk-test-key"}' | python3 -m json.tool
# Verify key not returned
curl -sf http://localhost:8091/api/user/model-config | python3 -m json.tool | grep -c "api_key_encrypted"  # 0
# Verify key propagation: OpenAI key should be set for email_triage too
curl -sf http://localhost:8091/api/user/model-config | python3 -m json.tool | grep has_api_key  # both true
# Verify delete guardrails
curl -sf -X DELETE http://localhost:8091/api/user/model-config/1  # local → 409
# Verify resolve is protected (no internal token → 403)
curl -sf http://localhost:8091/api/user/model-config/resolve -X POST -H "Content-Type: application/json" -d '{}' | python3 -m json.tool  # 403
# Verify rate limit on test
curl -sf -X POST http://localhost:8091/api/user/model-config/test -H "Content-Type: application/json" -d '{"config_id":1}'
curl -sf -X POST http://localhost:8091/api/user/model-config/test -H "Content-Type: application/json" -d '{"config_id":1}'  # 429
```
- Commit: `MODEL-CONFIG-001 P1: Database schema + backend API endpoints`

---

## Phase 2 — Dashboard Proxy Routes + Types + React Query Hooks
**Complexity:** M | **Touch points:** 6 files created

**Purpose:** Wire dashboard to backend model config endpoints with typed API client and React Query hooks. Run OpenAPI sync chain.

### Blast Radius
- **Services:** Dashboard (port 3003)
- **Pages:** None yet (infrastructure)
- **Downstream:** Settings UI (Phase 3), chat switcher (Phase 4)

### Tasks

- P2-01: **Update OpenAPI spec and sync types**
  ```bash
  make update-spec && make sync-types && npx tsc --noEmit
  ```
  - **Checkpoint:** New model-config endpoints visible in generated types. Note: the resolve endpoint is NOT in the spec (intentionally excluded).

- P2-02: **Create types file** `apps/dashboard/src/lib/settings/model-config-types.ts`
  - Types: `ModelContext`, `ModelProvider`, `ModelConfig`, `ModelConfigCreate`, `ActiveModels`, `ProviderMeta`, `ConnectionTestResult`
  - Static `PROVIDERS` array with metadata: id, name, icon component name, models[], requiresApiKey, apiKeyPrefix (for paste detection), docsUrl
  - Include Google provider with models: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`

- P2-03: **Create API client** `apps/dashboard/src/lib/settings/model-config-api.ts`
  - Functions: `fetchModelConfigs()`, `fetchActiveModels()`, `upsertModelConfig()`, `setActiveModel()`, `testModelConnection()`, `deleteModelConfig()`, `migrateFromLocalStorage()`
  - All use `fetch('/api/settings/models/...')` pattern

- P2-04: **Create proxy routes**
  - `apps/dashboard/src/app/api/settings/models/route.ts` — GET (list), PUT (upsert)
  - `apps/dashboard/src/app/api/settings/models/active/route.ts` — GET (active), POST (activate)
  - `apps/dashboard/src/app/api/settings/models/test/route.ts` — POST (test connection)
  - `apps/dashboard/src/app/api/settings/models/migrate/route.ts` — POST (batch migration) <!-- 3-Pass S5 -->

- P2-05: **Create React Query hook** `apps/dashboard/src/hooks/useModelConfig.ts`
  - `useModelConfigs()` — list all, 30s staleTime
  - `useActiveModels()` — active per context, 10s staleTime
  - `useSetActiveModel()` — mutation with optimistic update + cache invalidation on `['model-configs']` query key
  - `useUpsertModelConfig()` — mutation, invalidates both query keys on success
  - `useTestModelConnection()` — mutation (no cache, fires and returns)

### Gate P2
```bash
make update-spec && make sync-types && npx tsc --noEmit
# Start dashboard, verify Network tab:
# GET /api/settings/models/active → returns { chat: {...}, email_triage: {...} }
```
- Commit: `MODEL-CONFIG-001 P2: Dashboard proxy, types, React Query hooks`

---

## Phase 3 — Settings UI Redesign
**Complexity:** L | **Touch points:** 3 files created, 2 modified

**Purpose:** Replace `ProviderSection` with LangSmith-style `ModelConfigSection` using tabs for dual context, paste-aware key input, latency display, and transactional localStorage migration.

### Blast Radius
- **Services:** Dashboard
- **Pages:** `/settings`
- **Downstream:** None

### Tasks

- P3-01: **Create `ProviderConfigDialog`** `apps/dashboard/src/components/settings/ProviderConfigDialog.tsx`
  - Dialog for configuring a single provider
  - API key input (password with eye toggle)
  - **Paste-aware key input:** On paste, detect format (sk- → OpenAI, sk-ant- → Anthropic, AIza → Google). If provider mismatch, show warning: "This looks like an Anthropic key. Did you mean to configure Anthropic?" with "Switch to Anthropic" link. Auto-trim whitespace on paste. <!-- 3-Pass U3 -->
  - Model selector (Select dropdown from `PROVIDERS[provider].models`)
  - Endpoint URL (local/custom only)
  - "Test Connection" button with rich feedback: spinner → "Connected in 342ms" (green) or "Failed: 401 Unauthorized" (red). Show latency prominently. <!-- 3-Pass U2 -->
  - **Auto-test on save:** After saving a key, automatically trigger a connection test. <!-- 3-Pass U5 -->
  - "Save" button calls `useUpsertModelConfig()`
  - "Remove API Key" destructive action
  - **Checkpoint:** Dialog opens, key paste detection works

- P3-02: **Create `ModelConfigSection`** `apps/dashboard/src/components/settings/ModelConfigSection.tsx`
  - Replaces `ProviderSection` entirely
  - `Tabs` for Chat Agent / Email Triage Agent context switching
  - **Email Triage tab info banner:** "Email Triage currently uses rule-based processing. Model-based triage will be available in a future update." Active model can be configured but shows "Not yet active" badge. <!-- 3-Pass A3 -->
  - Active model `Select` dropdown (only shows configured providers)
  - Provider list with status badges:
    - "Connected (2 min ago)" — green, with freshness timestamp <!-- 3-Pass U5 -->
    - "API Key Set" — blue (has key but not tested or test is stale >24h)
    - "Not Configured" — gray
  - Each provider row: icon, name, model, status badge, latency badge (if tested), Edit button
  - "Server-persisted (encrypted)" badge
  - "Re-test all" button that tests all configured providers in parallel (Promise.allSettled) <!-- 3-Pass U5 -->
  - "Manage Models" link → `/settings/models`
  - **Checkpoint:** Section renders, tabs switch contexts

- P3-03: **Create localStorage migration helper** `apps/dashboard/src/lib/settings/migrate-provider-settings.ts`
  - On first `useModelConfigs()` load: if backend returns empty configs AND localStorage has `zakops-provider-settings`
  - Read ALL localStorage settings
  - Send ALL providers in a single `POST /api/settings/models/migrate` batch call <!-- 3-Pass S5 -->
  - Backend stores all-or-nothing (transaction)
  - On success: set `zakops-provider-migrated: true` in localStorage AND clear keys from localStorage. Toast: "Provider settings migrated to server (encrypted)"
  - On failure: leave localStorage untouched, show warning toast: "Migration failed. Your settings are still stored locally."
  - **Checkpoint:** Migration toast appears on first load with old localStorage data

- P3-04: **Update settings page** `apps/dashboard/src/app/settings/page.tsx`
  - Replace `import { ProviderSection }` with `import { ModelConfigSection }`
  - Replace `<ProviderSection />` with `<ModelConfigSection />`

- P3-05: **Update section config** in `apps/dashboard/src/lib/settings/preferences-types.ts`
  - Rename 'provider' section label to 'AI Models' (keep id for URL compatibility)

### Rollback Plan
1. Revert settings page to use `<ProviderSection />`
2. localStorage fallback still works

### Gate P3
```bash
# Open http://localhost:3003/settings
# Verify:
# 1. "AI Models" section with Chat / Email Triage tabs
# 2. Email Triage tab shows "rule-based processing" info banner
# 3. Active model dropdown shows Local vLLM
# 4. Click "Edit" on OpenAI → dialog opens with key input + model selector
# 5. Paste an Anthropic key → shows provider mismatch warning
# 6. Save an OpenAI key → auto-test runs → badge shows "Connected (just now)" with latency
# 7. "Server-persisted (encrypted)" badge visible
# 8. "Re-test all" button works
npx tsc --noEmit
```
- Commit: `MODEL-CONFIG-001 P3: Settings UI redesign with dual-context tabs`

---

## Phase 4 — Chat Quick-Switch + Route Rewrite
**Complexity:** L | **Touch points:** 3 files created, 2 modified

**Purpose:** Create always-visible model name header with quick-switch dropdown. Extract model resolution to a dedicated module. Rewrite chat route to read model config from backend.

### Blast Radius
- **Services:** Dashboard
- **Pages:** `/chat`
- **Downstream:** All chat interactions

### Tasks

- P4-01: **Create model resolver** `apps/dashboard/src/lib/agent/model-resolver.ts` <!-- 3-Pass A4 -->
  - `getActiveModelConfig(context: ModelContext)` — 10s TTL module-level cache (same pattern as profile cache in route.ts)
  - `resolveApiKey(configId: number)` — calls resolve endpoint with `X-Internal-Resolve-Token` header + `INTERNAL_RESOLVE_TOKEN` env var
  - `resolveActiveProvider(context: ModelContext): Promise<AgentProviderType>` — high-level: get config → if local, return agentProvider → if cloud, resolve key → create provider
  - Failover: if backend is down → return local provider (graceful degradation)
  - **Checkpoint:** Module imports cleanly, TypeScript compiles

- P4-02: **Create `ModelSwitcher`** `apps/dashboard/src/components/chat/ModelSwitcher.tsx`
  - **Always-visible model name:** Renders as `[provider-icon] Claude Sonnet 4.6 [chevron-down]` — the full model name is always visible, not hidden behind a click <!-- 3-Pass U1 -->
  - On narrow screens, truncate to provider icon + short name: `[icon] Sonnet 4.6 [v]`
  - Color-code: local = default text, cloud = blue accent
  - `DropdownMenu` showing configured models with provider icons
  - Only shows models with valid config (has_api_key or local)
  - Health dot: green (tested <24h, success), yellow (untested or stale >24h), red (test failed)
  - Latency badge in dropdown: "342ms" in gray <!-- 3-Pass U2 -->
  - "Manage models..." link at bottom → `/settings#models`
  - Uses `useActiveModels()` + `useSetActiveModel()`
  - **Model switch toast:** On successful activation → toast `Switched to [icon] Claude Sonnet 4.6` (3s auto-dismiss). On failure → error toast. Brief loading spinner during mutation. <!-- 3-Pass U4 -->
  - **Checkpoint:** Dropdown renders with model names and health dots

- P4-03: **Rewrite chat route** `apps/dashboard/src/app/api/chat/route.ts`
  - Remove: `body.providerConfig` reading, localStorage dependency, inline provider creation
  - Add: Import `resolveActiveProvider` from `model-resolver.ts`
  - Flow: `const provider = await resolveActiveProvider('chat');` → use provider for chat
  - Failover chain preserved: selected provider → local vLLM → backend agent → helpful text
  - Add `INTERNAL_RESOLVE_TOKEN` to env (generated in Phase 1, consumed here)
  - **Checkpoint:** Chat works with local model after rewrite

- P4-04: **Update chat page** `apps/dashboard/src/app/chat/page.tsx`
  - Replace `ProviderSelector` import with `ModelSwitcher`
  - Remove localStorage reads for provider config in `sendMessage()`
  - Remove `providerConfig` from request body
  - Keep text-only mode banner (derived from `useActiveModels()` — show when active provider !== 'local')

### Decision Tree
- **IF** backend model-config endpoint is down → use local provider (graceful degradation via model-resolver)
- **ELSE IF** active model is 'local' → use `agentProvider` (existing path, full tools)
- **ELSE** → resolve API key via internal endpoint, create cloud provider (text-only mode)

### Rollback Plan
1. Revert chat route to read `body.providerConfig`
2. Revert chat page to use `ProviderSelector`
3. Remove model-resolver.ts
4. localStorage still works

### Gate P4
```bash
# Open http://localhost:3003/chat
# 1. ModelSwitcher shows current model name in header (always visible)
# 2. Chat with local model → tools work
# 3. Switch to configured cloud model → toast confirms switch → response from cloud
# 4. Text-only banner appears for cloud
# 5. Switch back to local → tools restored → toast confirms
# 6. No localStorage reads in Network tab for provider config
# 7. No providerConfig in chat request body
npx tsc --noEmit
```
- Commit: `MODEL-CONFIG-001 P4: Chat quick-switch + server-side model routing`

---

## Phase 5 — Google AI Provider
**Complexity:** S | **Touch points:** 1 file created, 1 modified

**Purpose:** Add Google AI (Gemini) as a provider option.

### Blast Radius
- **Services:** Dashboard
- **Pages:** `/chat` (new provider available), `/settings` (new provider in list)
- **Downstream:** None

### Tasks

- P5-01: **Create Google provider** `apps/dashboard/src/lib/agent/providers/google.ts`
  - Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
  - Auth: `x-goog-api-key` header
  - Text-only mode (same pattern as openai.ts / anthropic.ts)
  - Models: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`

- P5-02: **Add Google to model resolver provider factory** in `model-resolver.ts`
  - Import `createGoogleProvider`
  - Add `case 'google':` in provider creation switch

### Gate P5
```bash
# Add Google API key via Settings UI
# Switch to Gemini 2.5 Pro in chat
# Verify response comes from Google (check model name in response)
npx tsc --noEmit
```
- Commit: `MODEL-CONFIG-001 P5: Google AI (Gemini) provider`

---

## Phase 6 — Model Management Page
**Complexity:** M | **Touch points:** 1 file created, 1 modified

**Purpose:** Dedicated `/settings/models` page with LangSmith-style provider x context grid.

### Blast Radius
- **Services:** Dashboard
- **Pages:** `/settings/models` (new)
- **Downstream:** None

### Tasks

- P6-01: **Create management page** `apps/dashboard/src/app/settings/models/page.tsx`
  - Grid layout: rows = providers, columns = Chat Agent / Email Triage Agent
  - Each cell: model name, status badge with freshness ("Connected 5m ago" / "Never tested"), latency badge, Set Active / Add Key button
  - Reuses `ProviderConfigDialog` for editing
  - Architecture note footer (local = full tools, cloud = text-only, encrypted storage)
  - **Last tested freshness:** badges show recency — green (<1h), yellow (<24h), gray (never/stale). Warning if active provider hasn't been tested in >24h. <!-- 3-Pass U5 -->

- P6-02: **Add nav entry** for model management
  - Update settings nav or add link from `ModelConfigSection`

### Gate P6
```bash
# Navigate to http://localhost:3003/settings/models
# Verify grid renders with all 5 providers x 2 contexts
# Verify status badges show freshness timestamps
# Verify buttons work (edit, set active)
make validate-surface17  # Route coverage
npx tsc --noEmit
```
- Commit: `MODEL-CONFIG-001 P6: Model management page`

---

## Phase 7 — Cleanup + Surface Compliance + E2E Tests
**Complexity:** L | **Touch points:** 5+ files modified, 1 created

**Purpose:** Deprecate old provider system, run surface validations, add E2E tests, update env registry.

### Blast Radius
- **Services:** Dashboard, Backend (env registry)
- **Pages:** All previously modified pages
- **Downstream:** None

### Tasks

- P7-01: **Deprecate old provider files**
  - Mark `provider-settings.ts` with `@deprecated` JSDoc
  - Mark `ProviderSection.tsx` with `@deprecated`
  - Remove `providerConfig` from chat request body type
  - Keep files for one release cycle

- P7-02: **Update OpenAPI spec and sync types** (mandatory chain per IA-15)
  ```bash
  make update-spec && make sync-types && npx tsc --noEmit
  ```

- P7-03: **Add provider icons** to `apps/dashboard/src/components/icons.tsx`
  - Add icons for: server (local), openai, anthropic, google, custom endpoint

- P7-04: **Update env registry** (Surface 11)
  - Add `TOKEN_ENCRYPTION_KEY` to env registry if not already present
  - Add `INTERNAL_RESOLVE_TOKEN` to env registry

- P7-05: **Create E2E tests** `apps/dashboard/tests/e2e/model-config.spec.ts`
  - Test: Settings page shows AI Models section with model configuration tabs
  - Test: Chat page shows model switcher with current model name visible
  - Test: Model management page loads with provider grid
  - Test: Provider config dialog opens with API key input and model selector
  - Use functional keywords in test names (per IA-10): "model", "provider", "settings", "switcher"

- P7-06: **Run surface validations**
  ```bash
  make validate-surface9   # Design system
  make validate-surface11  # Env registry (TOKEN_ENCRYPTION_KEY, INTERNAL_RESOLVE_TOKEN)
  make validate-surface12  # Error taxonomy
  make validate-surface17  # Route coverage (/settings/models)
  ```

### Gate P7
```bash
npx playwright test model-config --reporter=line  # E2E tests pass
make validate-local  # Full offline validation
make validate-surface9 && make validate-surface11 && make validate-surface12 && make validate-surface17
```
- Commit: `MODEL-CONFIG-001 P7: Cleanup, deprecation, surface compliance, E2E tests`

---

## Phase 8 — Final Validation + Completion Report
**Complexity:** S | **Touch points:** 2 files modified

**Purpose:** Full validation sweep, browser verification, bookkeeping, completion report.

### Blast Radius
- **Services:** None (verification only)
- **Pages:** None (verification only)
- **Downstream:** QA-MC-VERIFY-001

### Tasks

- P8-01: Run full validation
  ```bash
  make validate-local
  npx tsc --noEmit
  npx playwright test --reporter=line
  ```

- P8-02: Browser verification of all pages:
  - `/settings` — AI Models section with tabs, email triage info banner, freshness badges
  - `/settings/models` — Management grid with provider x context, latency badges
  - `/chat` — Always-visible model name in header, dropdown with health dots, switch toast
  - All cloud providers work end-to-end (if keys configured)

- P8-03: Update `/home/zaks/bookkeeping/CHANGES.md`

- P8-04: Write completion report to `/home/zaks/bookkeeping/docs/MODEL-CONFIG-001-COMPLETION.md`

### Gate P8
- All AC pass
- `make validate-local` PASS
- `npx tsc --noEmit` PASS
- Completion report written
- CHANGES.md updated
- Commit: `MODEL-CONFIG-001: Simplified multi-model configuration`

---

## Acceptance Criteria

### AC-1: Server-persisted model configs
`model_configurations` table exists with encrypted API key storage. `GET /api/user/model-config` returns configs without exposing keys (`has_api_key: true/false` only).

### AC-2: Mandatory encryption
API keys encrypted via Fernet at rest. `PUT` with `api_key` returns 503 if encryption unavailable. No version-0 (plaintext) keys exist in the `model_configurations` table.

### AC-3: Active model invariant
Partial unique index enforces exactly one `is_active=true` per (user_id, context). Activation is transactional. Concurrent activations do not corrupt state.

### AC-4: Dual model contexts
Chat and Email Triage have independent active model selections. Changing one does not affect the other. Email Triage tab shows "rule-based" info banner.

### AC-5: One-click model switching
Selecting a model in the chat dropdown or settings activates it immediately without page reload. Toast confirms the switch.

### AC-6: Real connection tests with latency
"Test Connection" performs a real server-side API call with 15s timeout. Result includes latency in milliseconds. Rate limited to 1 per provider per 10s. Auto-test on key save.

### AC-7: Settings UI redesign
Settings page shows "AI Models" section with Chat/Email Triage tabs, provider list with freshness-aware status badges, paste-aware key input with format detection.

### AC-8: Chat quick-switch with always-visible model name
Chat header shows current model name at all times (not hidden behind click). Dropdown shows configured models with health indicators and latency.

### AC-9: Chat route server-side routing
Chat route reads active model from backend via model-resolver (not localStorage/request body). API key resolved via internal-only endpoint with dedicated auth token.

### AC-10: Google AI provider
Gemini models available as a provider option with real API integration.

### AC-11: Model management page
`/settings/models` page shows provider x context grid with freshness timestamps, latency badges, and configuration controls.

### AC-12: localStorage migration
Existing localStorage provider settings migrated to server via batch endpoint (all-or-nothing transaction). localStorage not cleared until migration confirmed.

### AC-13: Failover behavior
If selected cloud provider fails, system falls back to local vLLM gracefully. If backend model-config endpoint is down, chat route uses local provider.

### AC-14: Delete guardrails
Cannot delete active model (409). Cannot delete local provider (409). Can delete non-active cloud configs.

### AC-15: Audit trail
Key lifecycle events (store, delete, activate, test) logged to `zakops.agent_events` with event_type `model_config.*`. Keys/encrypted keys never appear in logs.

### AC-16: Resolve endpoint security
Resolve endpoint requires `X-Internal-Resolve-Token` header. Rejects requests with non-null `Origin` header. Returns 403 without valid token.

### AC-17: No regressions
`make validate-local` PASS, `npx tsc --noEmit` PASS, existing E2E tests pass, surface validations pass for 9, 11, 12, 17.

### AC-18: Bookkeeping
CHANGES.md updated, changes committed, completion report produced.

---

## Guardrails

1. **Scope:** Model configuration system only. Do not touch deal workflow, agent tools, email triage business logic, or agent-api `LLMRegistry`.
2. **Generated files:** Never edit `api-types.generated.ts` or `backend_models.py`. Use bridge types.
3. **API keys:** NEVER return decrypted keys via GET or any browser-visible response. Only the resolve endpoint (internal-only, token-protected) decrypts.
4. **No plaintext keys:** Never store `api_key_version = 0`. If encryption is unavailable, refuse the write.
5. **Migration safety:** Do not modify existing migration files. New migration is `039`.
6. **Surface 9 compliance** — All new UI follows design system rules (per `.claude/rules/design-system.md`).
7. **Governance surface gates** — Surfaces 9, 11, 12, 17 validated with `make validate-surface{N}` in Phase 7 gate (per IA-15).
8. **WSL safety:** `sed -i 's/\r$//'` on new .sh files, `sudo chown zaks:zaks` on new files under `/home/zaks/`.
9. **Promise.allSettled only** — no `Promise.all` in dashboard data fetching.
10. **Text-only mode preserved** — Cloud providers do not get ZakOps tools (security boundary).
11. **Local-first** — Local vLLM remains the default. Cloud is opt-in.
12. **Port 8090 FORBIDDEN.**

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Does `make validate-local` pass at baseline?"
- [ ] "Is `is_encryption_available()` returning `True` in the running backend?"
- [ ] "Is `cryptography>=42.0.0` in requirements.txt?"

### After every code change:
- [ ] "Did I run `make update-spec && make sync-types && npx tsc --noEmit` after backend API changes?"
- [ ] "Am I returning `has_api_key` instead of the actual key in GET responses?"
- [ ] "Am I using `Promise.allSettled` (not `Promise.all`) in dashboard data fetching?"
- [ ] "Does the resolve endpoint check `X-Internal-Resolve-Token` AND reject non-null Origin?"
- [ ] "Am I refusing to store keys with version 0?"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks?"
- [ ] "Did I create new files under /home/zaks/? → Ownership fixed with `sudo chown zaks:zaks`?"
- [ ] "Did I create new .sh files? → CRLF stripped with `sed -i 's/\r$//'`?"
- [ ] "Does `npx tsc --noEmit` still pass?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I write the completion report?"
- [ ] "Did I verify all pages in browser (settings, settings/models, chat)?"
- [ ] "Did I create ALL files listed in the 'Files to Create' table?"
- [ ] "Do E2E test names contain functional keywords (model, provider, settings, switcher) for QA grep?"

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash:
```bash
git log --oneline -10  # What phases are committed?
make validate-local    # Is the codebase clean?
psql -U zakops -d zakops -c "\dt zakops.model_configurations"  # Is the table there?
psql -U zakops -d zakops -c "\di zakops.idx_one_active_per_context"  # Is the index there?
curl -sf http://localhost:8091/api/user/model-config | jq .  # Are endpoints up?
```

---

## Context Checkpoint
<!-- Adopted from Improvement Area IA-1 -->

This is an XL mission with 9 phases. If context is becoming constrained, summarize progress so far, commit intermediate work, and continue in a fresh continuation. Write a checkpoint to `/home/zaks/bookkeeping/mission-checkpoints/MODEL-CONFIG-001.md` with: phases completed, phases remaining, current validation state, any open decisions. <!-- Also IA-7 -->

---

## File Paths Reference

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `apps/backend/db/migrations/039_model_configurations.sql` | P1 | Schema + partial unique index + seed data |
| `apps/backend/db/migrations/039_model_configurations_rollback.sql` | P1 | Rollback |
| `apps/backend/src/api/orchestration/routers/model_config.py` | P1 | Backend CRUD + test + resolve + migrate + audit logging |
| `apps/dashboard/src/lib/settings/model-config-types.ts` | P2 | Shared types + provider metadata |
| `apps/dashboard/src/lib/settings/model-config-api.ts` | P2 | API client functions |
| `apps/dashboard/src/hooks/useModelConfig.ts` | P2 | React Query hooks |
| `apps/dashboard/src/app/api/settings/models/route.ts` | P2 | Proxy: list/upsert |
| `apps/dashboard/src/app/api/settings/models/active/route.ts` | P2 | Proxy: active/activate |
| `apps/dashboard/src/app/api/settings/models/test/route.ts` | P2 | Proxy: test connection |
| `apps/dashboard/src/app/api/settings/models/migrate/route.ts` | P2 | Proxy: batch migration |
| `apps/dashboard/src/components/settings/ProviderConfigDialog.tsx` | P3 | Config dialog with paste detection |
| `apps/dashboard/src/components/settings/ModelConfigSection.tsx` | P3 | Settings section with tabs |
| `apps/dashboard/src/lib/settings/migrate-provider-settings.ts` | P3 | Transactional localStorage migration |
| `apps/dashboard/src/lib/agent/model-resolver.ts` | P4 | Model resolution + caching + failover |
| `apps/dashboard/src/components/chat/ModelSwitcher.tsx` | P4 | Chat dropdown with always-visible model name |
| `apps/dashboard/src/lib/agent/providers/google.ts` | P5 | Google AI provider |
| `apps/dashboard/src/app/settings/models/page.tsx` | P6 | Management page |
| `apps/dashboard/tests/e2e/model-config.spec.ts` | P7 | E2E tests |

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `apps/backend/src/api/orchestration/main.py` | P1 | Register model_config router |
| `apps/dashboard/src/app/settings/page.tsx` | P3 | Replace ProviderSection → ModelConfigSection |
| `apps/dashboard/src/lib/settings/preferences-types.ts` | P3 | Rename section label to 'AI Models' |
| `apps/dashboard/src/app/api/chat/route.ts` | P4 | Use model-resolver, remove providerConfig |
| `apps/dashboard/src/app/chat/page.tsx` | P4 | Replace ProviderSelector → ModelSwitcher |
| `apps/dashboard/src/components/icons.tsx` | P7 | Add provider icons |
| `apps/dashboard/src/lib/settings/provider-settings.ts` | P7 | Mark @deprecated |
| `packages/contracts/openapi/zakops-api.json` | P2/P7 | Via `make update-spec` |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `apps/backend/src/core/security/encryption.py` | Fernet encrypt/decrypt functions to reuse |
| `apps/backend/src/api/orchestration/routers/preferences.py` | Pattern for single-user CRUD, _get_pool(), parameterized SQL |
| `apps/dashboard/src/lib/agent/providers/openai.ts` | Pattern for cloud provider implementation |
| `apps/dashboard/src/lib/agent/providers/anthropic.ts` | Pattern for cloud provider implementation |
| `apps/dashboard/src/hooks/useUserPreferences.ts` | Pattern for React Query hooks |
| `apps/dashboard/src/components/settings/SettingsSectionCard.tsx` | Reusable wrapper pattern |
| `.claude/rules/design-system.md` | Surface 9 UI rules |

---

## Git Commit Cadence
<!-- Per Cross-Cutting Standard #15 -->

| Phase | Commit Message |
|-------|---------------|
| P1 | `MODEL-CONFIG-001 P1: Database schema + backend API endpoints` |
| P2 | `MODEL-CONFIG-001 P2: Dashboard proxy, types, React Query hooks` |
| P3 | `MODEL-CONFIG-001 P3: Settings UI redesign with dual-context tabs` |
| P4 | `MODEL-CONFIG-001 P4: Chat quick-switch + server-side model routing` |
| P5 | `MODEL-CONFIG-001 P5: Google AI (Gemini) provider` |
| P6 | `MODEL-CONFIG-001 P6: Model management page` |
| P7 | `MODEL-CONFIG-001 P7: Cleanup, deprecation, surface compliance, E2E tests` |
| P8 | `MODEL-CONFIG-001: Simplified multi-model configuration` |

Branch: `feat/model-config-001`

---

## Completion Report Template
<!-- Section 9b — MANDATORY deliverable -->

```
## Completion Report — MODEL-CONFIG-001

**Date:** 2026-02-21
**Executor:** Claude Opus 4.6
**Status:** COMPLETE / PARTIAL

### Phases Completed
| Phase | Name | Gate | Status |
|-------|------|------|--------|
| P0 | Discovery & Baseline | Gate P0 | |
| P1 | Database + Backend API | Gate P1 | |
| P2 | Dashboard Proxy + Types + Hooks | Gate P2 | |
| P3 | Settings UI Redesign | Gate P3 | |
| P4 | Chat Quick-Switch + Route Rewrite | Gate P4 | |
| P5 | Google AI Provider | Gate P5 | |
| P6 | Model Management Page | Gate P6 | |
| P7 | Cleanup + Surface Compliance | Gate P7 | |
| P8 | Final Validation | Gate P8 | |

### Acceptance Criteria
| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-1 | Server-persisted model configs | | |
| AC-2 | Mandatory encryption | | |
| AC-3 | Active model invariant | | |
| AC-4 | Dual model contexts | | |
| AC-5 | One-click model switching | | |
| AC-6 | Real connection tests with latency | | |
| AC-7 | Settings UI redesign | | |
| AC-8 | Chat quick-switch with always-visible name | | |
| AC-9 | Chat route server-side routing | | |
| AC-10 | Google AI provider | | |
| AC-11 | Model management page | | |
| AC-12 | localStorage migration | | |
| AC-13 | Failover behavior | | |
| AC-14 | Delete guardrails | | |
| AC-15 | Audit trail | | |
| AC-16 | Resolve endpoint security | | |
| AC-17 | No regressions | | |
| AC-18 | Bookkeeping | | |

### Validation Results
- `make validate-local`: ___
- TypeScript compilation: ___
- E2E tests: ___
- Surface 9 (design system): ___
- Surface 11 (env registry): ___
- Surface 12 (error taxonomy): ___
- Surface 17 (route coverage): ___

### Files Modified / Created
(list)

### Notes
(deviations, decisions, 3-Pass improvements adopted)
```

---

## Stop Condition

DONE when all 18 AC pass, `make validate-local` passes, all surface validations pass (9, 11, 12, 17), E2E tests pass, all pages verified in browser (settings, settings/models, chat), completion report produced, CHANGES.md updated, all changes committed on `feat/model-config-001` branch.

Do NOT proceed to: QA verification (separate mission QA-MC-VERIFY-001), email triage model switching implementation (the config is stored but the agent-api runtime override is a separate mission), additional providers beyond the 5 defined, or CORS remediation (separate scope).

---

*End of Mission Prompt — MODEL-CONFIG-001*

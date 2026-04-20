# MASTER PLAN: Runtime Provider Switching — Full-Stack Implementation

**Supersedes:** `RUNTIME-PROVIDER-SWITCHING-FIX-PLAN.md`
**Date:** 2026-02-23
**Classification:** Architecture + UX + Production Hardening
**3-Pass Escalation:** Correctness | UX Redesign | World-Class Alignment

---

## Executive Summary

The model-config architecture (MODEL-CONFIG-001, P0-P5) already implements true multi-provider routing. Each provider (OpenAI, Anthropic, Google, Custom, Local) calls its actual API endpoint with correct auth. **The routing code works.**

**Three blockers prevent it from functioning in practice:**

| # | Blocker | Root Cause | Impact |
|---|---------|-----------|--------|
| 1 | `INTERNAL_RESOLVE_TOKEN` never generated | Missing from backend `.env` AND dashboard `.env.local` | All cloud key resolution returns 403 → silent fallback to Qwen |
| 2 | 6 silent fallback paths in `model-resolver.ts` | `console.warn()` + return local instead of throwing | User never knows cloud provider failed |
| 3 | Cache not invalidated after model activation | `invalidateModelCache()` exported but never called | 10s window where stale provider serves requests |

**This plan addresses:**
- 9 architectural issues (Pass 1)
- 3 UX gaps vs LangSmith reference (Pass 2)
- 25 production readiness findings (Pass 3)

---

## Architectural Invariants (MUST hold at all times)

| # | Invariant | Enforcement |
|---|-----------|------------|
| INV-1 | If user selects provider X, execution MUST use provider X | Throw on key resolution failure, never silent fallback |
| INV-2 | If provider API key is missing, execution MUST error | Error message: "Provider X has no API key. Add one in Settings > Models." |
| INV-3 | If provider fails, system MUST NOT silently downgrade | Re-throw cloud errors; user sees explicit failure, not Qwen output |
| INV-4 | Switching models MUST preserve conversation history | Full `messages[]` array passed to new provider on every request |
| INV-5 | Runtime logs MUST show which provider actually executed | `[MODEL_ROUTER] Provider: X \| Model: Y \| Local: Z` on every request + response |
| INV-6 | Backend down = graceful degradation (only valid silent fallback) | If no config available, use local with visible "fallback" warning |

---

## Affected Contract Surfaces

| Surface | Impact | Sync Required |
|---------|--------|--------------|
| Surface 9 (Design System) | ModelSwitcher UI changes | `make validate-surface9` |
| Surface 11 (Env Registry) | INTERNAL_RESOLVE_TOKEN added | `make validate-surface11` |
| No API spec changes | No generated types affected | — |

---

## Phase 0 — Discovery & Baseline

**Complexity:** S | **Blast Radius:** None (read-only)

### Tasks
1. Confirm current state: `curl http://localhost:8091/api/user/model-config/active` → expect `provider: "local"`
2. Confirm `INTERNAL_RESOLVE_TOKEN` missing from both `.env` files
3. Confirm `invalidateModelCache()` is imported but never called in activation route
4. Run `make validate-local` — baseline must pass

### Gate
- All 4 confirmations documented
- `make validate-local` PASS

---

## Phase 1 — Critical Infrastructure Fix (INTERNAL_RESOLVE_TOKEN + Silent Fallback)

**Complexity:** M | **Blast Radius:** Dashboard + Backend env files + model-resolver.ts + route.ts

### P1-01: Generate and set INTERNAL_RESOLVE_TOKEN

1. Generate: `openssl rand -hex 32`
2. Add to `apps/backend/.env`: `INTERNAL_RESOLVE_TOKEN=<token>`
3. Add to `apps/dashboard/.env.local`: `INTERNAL_RESOLVE_TOKEN=<same-token>`
4. Rebuild backend container: `docker compose build backend && docker compose up -d backend`
5. Restart dashboard

**AC:** Token exists in both files, values match, backend returns 403 (not 500) on unauthenticated resolve call.

**Verification:**
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8091/api/user/model-config/resolve \
  -H 'Content-Type: application/json' -d '{"config_id": 1}'
# Expected: 403 (not 500)
```

**Rollback:** Remove lines from both `.env` files, restart services.

### P1-02: Remove silent fallbacks in model-resolver.ts

**File:** `apps/dashboard/src/lib/agent/model-resolver.ts`

Replace 6 silent fallback paths with explicit errors when `config.provider !== 'local'`:

| Line | Current | Fix |
|------|---------|-----|
| 158-160 | `if (!config.has_api_key) return fallback` | Throw: "Provider {X} has no API key configured. Add one in Settings > Models." |
| 163-166 | `if (!apiKey) return fallback` | Throw: "Could not decrypt API key for {X}. Verify INTERNAL_RESOLVE_TOKEN is set." |
| 180-182 | `if (!config.endpoint) return fallback` | Throw: "Custom provider has no endpoint configured." |
| 195-197 | `default: return fallback` | Throw: "Unknown provider: {X}" |
| 199-201 | `catch (error) return fallback` | Re-throw original error |

**Keep** line 143-145 (`!config` fallback) — backend-down is the ONLY legitimate silent fallback. Add warning flag: `{ provider: agentProvider, ..., isLocal: true, isFallback: true }`.

**AC:** Selecting a cloud provider with no API key shows a user-visible error, NOT silent Qwen.

**Verification:** Activate OpenAI (no key) → send chat → expect error, not Qwen response.

**Rollback:** Revert model-resolver.ts from git.

### P1-03: Invalidate cache after model activation

**File:** `apps/dashboard/src/app/api/settings/models/active/route.ts`

After successful activation POST, call `invalidateModelCache()`.

```typescript
import { invalidateModelCache } from '@/lib/agent/model-resolver';
// After backend returns 200:
invalidateModelCache();
```

**AC:** After switching models in Settings, next chat request uses new provider within 1 second (not up to 10s stale).

**Verification:** Activate model A → immediately send chat → log shows model A (not stale model B).

### P1-04: Enhanced observability logging

**File:** `apps/dashboard/src/app/api/chat/route.ts`

Replace line 131:
```
[MODEL_ROUTER] Provider: {providerName} | Model: {modelName} | Local: {isLocal} | Fallback: {isFallback}
```

Add after successful response (after line 156):
```
[MODEL_ROUTER] Response OK | Provider: {providerName} | Latency: {latencyMs}ms | Tokens: {tokens}
```

Add on error (line 211):
```
[MODEL_ROUTER] FAIL | Provider: {providerName} | Error: {message}
```

**AC:** Every chat request produces at least 2 log lines: resolution + outcome.

### Gate P1
- `INTERNAL_RESOLVE_TOKEN` set and matching in both services
- Zero silent fallback paths for cloud providers
- Cache invalidated on activation
- `[MODEL_ROUTER]` logs visible on every chat request
- `make validate-local` PASS
- `npx tsc --noEmit` PASS

---

## Phase 2 — UX Redesign (Match LangSmith Reference)

**Complexity:** M | **Blast Radius:** ModelSwitcher.tsx only (Surface 9)

### LangSmith Reference (from screenshot)

The target UI is a clean dark-theme dropdown:
- "MODEL" label at top
- Currently selected model displayed with provider brand icon + chevron
- Dropdown opens with search bar ("Search models...")
- Models grouped by provider with brand icons (Anthropic "A\", OpenAI spiral, Google "G")
- Checkmark on active model
- "Manage models" at bottom with gear icon

### Current State Assessment

| Feature | Current | LangSmith | Status |
|---------|---------|-----------|--------|
| Provider brand icons | IconBrandOpenai, IconRobot, etc. | Provider-specific icons | PARITY |
| Single-click activation | `handleSwitch()` on click | Same | PARITY |
| "Manage models" link | Present in dropdown | Present | PARITY |
| Health dot indicator | Green/red/amber circle | Not shown | ZakOps AHEAD |
| Latency display | `{latency_ms}ms` badge | Not shown | ZakOps AHEAD |
| **Model grouping by provider** | Flat list | Grouped with headers | **GAP (HIGH)** |
| **Search/filter** | None | Search input | **GAP (MEDIUM)** |
| **Active checkmark** | Blue "Active" badge | Checkmark icon | **GAP (MEDIUM)** |

### P2-01: Model grouping by provider

**File:** `apps/dashboard/src/components/chat/ModelSwitcher.tsx`

Transform flat `chatConfigs.map()` into grouped rendering:

```
Group configs by provider → For each provider with configs:
  <DropdownMenuLabel>{providerIcon} {providerName}</DropdownMenuLabel>
  <DropdownMenuItem>{model1}</DropdownMenuItem>
  <DropdownMenuItem>{model2}</DropdownMenuItem>
  <DropdownMenuSeparator />
```

Use `PROVIDERS` array from `model-config-types.ts:71-131` for ordering and metadata.

**AC:** Models visually grouped under provider headers with brand icons.

### P2-02: Search/filter models

**File:** `apps/dashboard/src/components/chat/ModelSwitcher.tsx`

Add `useState<string>` for search query. Insert `<Input placeholder="Search models..." />` as first child of `DropdownMenuContent`. Filter by model name or provider name.

**AC:** Typing "claude" filters to only Anthropic models. Clearing restores full list.

### P2-03: Active model checkmark

**File:** `apps/dashboard/src/components/chat/ModelSwitcher.tsx`

Replace:
```tsx
<Badge className="text-[10px] px-1 py-0 h-4">Active</Badge>
```

With:
```tsx
<IconCheck className="h-4 w-4 text-green-500" />
```

**AC:** Active model shows green checkmark inline, not a blue badge.

### P2-04: Dropdown max-height for scroll

Add `className="max-h-72 overflow-y-auto"` to `DropdownMenuContent` for lists exceeding viewport.

### Gate P2
- Visual comparison: dropdown matches LangSmith reference layout
- Grouped by provider with headers
- Search filters correctly
- Active model has checkmark
- Long model lists scroll
- `npx tsc --noEmit` PASS
- Surface 9 compliance: `make validate-surface9`

---

## Phase 3 — Production Hardening

**Complexity:** L | **Blast Radius:** Backend + Dashboard (ops layer, not user-facing)

### P3-01: Feature flag gating

**File:** `apps/backend/db/migrations/` (new migration)

Add feature flag: `model_config_cloud_enabled` (default: `true`).

In `model-resolver.ts`, check flag before cloud provider creation. If disabled, throw: "Cloud providers are temporarily disabled by administrator."

In `model_config.py` activate endpoint, reject non-local activation if flag is off.

**AC:** Setting flag to `false` blocks all cloud provider activations. Setting to `true` restores them. No deploy required.

**Rollback command:**
```sql
UPDATE zakops.feature_flags SET enabled=false WHERE name='model_config_cloud_enabled';
```

### P3-02: Rate limiting on activation endpoint

**File:** `apps/backend/src/api/orchestration/routers/model_config.py`

Add in-memory rate limit (same pattern as test endpoint line 450): 1 activation per 5 seconds per user.

**AC:** Rapid-fire activation calls return 429 after first.

### P3-03: Boot diagnostics for INTERNAL_RESOLVE_TOKEN

**File:** `/home/zaks/.claude/hooks/session-start.sh` (or equivalent)

Add check: both dashboard and backend `.env` files contain `INTERNAL_RESOLVE_TOKEN` and values match.

**AC:** Boot diagnostics report PASS/FAIL for token alignment.

### P3-04: Fernet key versioning awareness

**File:** `apps/backend/src/core/security/encryption.py`

Document current behavior: only v1 key supported. If key rotated, all encrypted API keys become unrecoverable.

Add startup warning if `ENCRYPTION_KEY` env var is missing or empty.

**AC:** Backend logs explicit warning on startup if encryption key is missing.

### P3-05: Error format standardization

Ensure all provider error responses include:
```json
{
  "error": true,
  "code": "provider_error",
  "provider": "openai",
  "message": "OpenAI API returned 401: Invalid API key",
  "correlation_id": "corr-xxx"
}
```

**File:** `apps/dashboard/src/app/api/chat/route.ts` — catch block at line 210.

**AC:** Cloud provider errors propagate to frontend with provider name and error code.

### Gate P3
- Feature flag blocks cloud activation when disabled
- Rate limiting returns 429 on spam
- Boot diagnostics check token alignment
- Error messages include provider name + correlation ID
- `make validate-local` PASS

---

## Phase 4 — Integration Testing & Verification

**Complexity:** M | **Blast Radius:** None (read-only verification)

### P4-01: End-to-end cloud provider test

1. Activate OpenAI config (id=3) for chat context
2. Send chat message
3. Verify dashboard log: `[MODEL_ROUTER] Provider: openai | Model: gpt-4.1 | Local: false`
4. Verify response content comes from OpenAI (not Qwen)
5. Verify SSE `done` event includes `model_used: "openai"`

### P4-02: Error path test

1. Activate OpenAI config with invalid API key
2. Send chat message
3. Verify user sees explicit error (not silent Qwen response)
4. Verify log: `[MODEL_ROUTER] FAIL | Provider: openai | Error: 401`

### P4-03: Mid-chat switching test

1. Start conversation with local Qwen (3+ messages)
2. Switch to OpenAI mid-chat via ModelSwitcher
3. Send another message
4. Verify OpenAI receives full conversation history
5. Verify no UI reset / page reload

### P4-04: Feature flag kill switch test

1. Set `model_config_cloud_enabled = false`
2. Attempt to activate OpenAI
3. Verify activation rejected
4. Verify existing chat falls back to local with explicit warning
5. Re-enable flag, verify cloud activation works again

### P4-05: Cache invalidation test

1. Activate model A
2. Send chat → verify model A serves
3. Activate model B (within 10s)
4. Send chat immediately → verify model B serves (not stale model A)

### Gate P4
- All 5 tests pass
- `make validate-local` PASS
- `make validate-live` PASS (if services running)

---

## Phase 5 — Bookkeeping & Documentation

**Complexity:** S | **Blast Radius:** None

### Tasks
1. Record all changes in `/home/zaks/bookkeeping/CHANGES.md`
2. Add runbook entry: "Model Config Emergency Rollback" to RUNBOOKS.md
3. Fix file ownership: `sudo chown zaks:zaks` on any new/modified files
4. Fix CRLF: `sed -i 's/\r$//'` on any new `.sh` files

### Gate P5
- CHANGES.md updated
- All files owned by `zaks:zaks`
- No CRLF in shell scripts

---

## Files Summary

| Phase | Action | File | Change |
|-------|--------|------|--------|
| P1 | Modify | `apps/backend/.env` | Add INTERNAL_RESOLVE_TOKEN |
| P1 | Modify | `apps/dashboard/.env.local` | Add INTERNAL_RESOLVE_TOKEN |
| P1 | Modify | `apps/dashboard/src/lib/agent/model-resolver.ts` | Replace 5 silent fallbacks with thrown errors, add `isFallback` flag |
| P1 | Modify | `apps/dashboard/src/app/api/chat/route.ts` | Enhanced `[MODEL_ROUTER]` logging (3 log points) |
| P1 | Modify | `apps/dashboard/src/app/api/settings/models/active/route.ts` | Call `invalidateModelCache()` after activation |
| P2 | Modify | `apps/dashboard/src/components/chat/ModelSwitcher.tsx` | Grouped dropdown, search, checkmark, max-height |
| P3 | Create | `apps/backend/db/migrations/04X_model_config_feature_flag.sql` | `model_config_cloud_enabled` flag |
| P3 | Modify | `apps/backend/src/api/orchestration/routers/model_config.py` | Rate limit activation, flag check |
| P3 | Modify | `apps/dashboard/src/lib/agent/model-resolver.ts` | Feature flag check before cloud |

---

## 3-Pass Findings Summary

### Pass 1: Full-Stack Correctness (9 findings)

| # | Finding | Severity | Phase |
|---|---------|----------|-------|
| F1 | INTERNAL_RESOLVE_TOKEN not set anywhere | CRITICAL | P1-01 |
| F2 | 6 silent fallback paths mask cloud failures | CRITICAL | P1-02 |
| F3 | Cache not invalidated after activation (10s stale window) | HIGH | P1-03 |
| F4 | Email triage context hardcoded to 'chat' | CRITICAL | Deferred (no email_triage UI yet) |
| F5 | Fernet key rotation breaks all encrypted keys | CRITICAL | P3-04 (documented) |
| F6 | Per-user isolation missing (DEFAULT_USER_ID) | HIGH | Deferred (single-user MVP) |
| F7 | `invalidateModelCache()` imported but never called | HIGH | P1-03 |
| F8 | No correlation ID in model-resolver logs | MEDIUM | P1-04 |
| F9 | Multi-tab: 10s stale cache risk | HIGH | P1-03 (server-side invalidation) |

### Pass 2: UX Gaps (3 actionable gaps)

| # | Gap | Current | Target | Phase |
|---|-----|---------|--------|-------|
| G1 | Model grouping by provider | Flat list | Grouped with provider headers + icons | P2-01 |
| G2 | Search/filter in dropdown | None | Text input filtering | P2-02 |
| G3 | Active model indicator | Blue "Active" badge | Green checkmark icon | P2-03 |
| — | Provider brand icons | Present | Present | PARITY |
| — | Single-click activation | Present | Present | PARITY |
| — | "Manage models" link | Present | Present | PARITY |
| — | Health dot + latency display | Present | Not in LangSmith | ZakOps AHEAD |

### Pass 3: Production Readiness (25 findings, 8 addressed)

| Priority | Count | Addressed | Deferred |
|----------|-------|-----------|----------|
| P0 | 3 | 3 (token, boot check, flag) | 0 |
| P1 | 6 | 5 (fallback, cache, logging, rate limit, errors) | 1 (fallback chain config) |
| P2 | 9 | 0 | 9 (metrics, audit, multi-tab broadcast, etc.) |
| P3 | 3 | 0 | 3 (token rotation, cost awareness, JWT resolve) |

---

## Definition of Done

1. Activating OpenAI in Settings → next chat request calls `api.openai.com` (verified by log)
2. Activating Anthropic in Settings → next chat request calls `api.anthropic.com`
3. Missing API key → user sees explicit error, NOT silent Qwen response
4. Failed key resolution → user sees explicit error with guidance
5. ModelSwitcher dropdown matches LangSmith layout (grouped, searchable, checkmark)
6. Mid-chat switching preserves conversation history
7. Feature flag can disable cloud providers without deploy
8. `[MODEL_ROUTER]` logs show provider + model + latency on every request
9. `make validate-local` PASS
10. `npx tsc --noEmit` PASS

---

## Stop Condition

This plan covers Phases 0-5 (infrastructure fix + UX redesign + production hardening + testing + bookkeeping). Do NOT proceed to:
- Per-user isolation (multi-tenant) — separate mission
- Prometheus metrics — separate mission
- Fernet key rotation tooling — separate mission
- Fallback chain configuration UI — separate mission

---

## Deferred Items (Next Mission Candidates)

| Item | Priority | Rationale |
|------|----------|-----------|
| Per-user model config isolation | P1 | Requires auth/session rework |
| Email triage context routing | P1 | No email triage chat UI exists yet |
| Prometheus metrics (per-provider latency/error rate) | P2 | Observability stack not deployed |
| Fernet key rotation tooling | P2 | Ops procedure, not blocking runtime |
| Fallback chain configuration UI | P2 | Requires new settings section |
| Multi-tab broadcast channel | P2 | React Query staleTime handles most cases |
| Cost awareness indicators | P3 | Cosmetic, not functional |
| Short-lived JWT for key resolution | P3 | Current token approach is secure enough |

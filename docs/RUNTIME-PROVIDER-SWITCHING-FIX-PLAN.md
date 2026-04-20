# PLAN: Runtime Provider Switching Fix

## Context

The model-config architecture (MODEL-CONFIG-001, P0-P5) already implements true multi-provider routing:
- `route.ts:130` calls `resolveActiveProvider('chat')` and branches on `isLocal` (line 140-149)
- Cloud providers (OpenAI, Anthropic, Google, Custom) each call their real API endpoints
- ModelSwitcher activates configs via backend, deactivates previous in same context atomically

**However, it doesn't work in practice** because:
1. `INTERNAL_RESOLVE_TOKEN` was never generated — key resolution always fails silently
2. Model-resolver silently falls back to local Qwen on ANY error instead of throwing
3. No visible proof of which provider actually executed

This is an operational + defensive-coding fix, not an architecture rewrite.

## Affected Contract Surfaces
- None changed (no API spec changes, no DB changes, no generated types)

## Phase 1: Generate and Set INTERNAL_RESOLVE_TOKEN

### Tasks
1. Generate a secure random token (32-byte hex)
2. Add `INTERNAL_RESOLVE_TOKEN=<token>` to `/home/zaks/zakops-agent-api/apps/backend/.env`
3. Add `INTERNAL_RESOLVE_TOKEN=<same-token>` to `/home/zaks/zakops-agent-api/apps/dashboard/.env.local`

### Files Modified
- `apps/backend/.env` — add 1 line
- `apps/dashboard/.env.local` — add 1 line

### Gate
- Token exists in both files, values match

---

## Phase 2: Remove Silent Fallback to Local

### Problem
`model-resolver.ts` lines 159, 165, 196, 200 all `console.warn()` and return local provider when the user explicitly chose a cloud provider. This masks errors.

### Fix
When `config.provider !== 'local'` (user explicitly chose cloud):
- **No API key** → throw error: "Provider X has no API key configured. Add one in Settings > Models."
- **Key resolution failed** → throw error: "Could not decrypt API key for provider X. Check INTERNAL_RESOLVE_TOKEN."
- **Unknown provider** → throw error: "Unknown provider: X"
- **Provider creation failed** → re-throw the original error

When backend is down / no config returned → still fall back to local (legitimate graceful degradation, we don't know user intent).

### Files Modified
- `apps/dashboard/src/lib/agent/model-resolver.ts` — replace silent fallbacks with thrown errors

---

## Phase 3: Add Observability Logging

### Fix
In `route.ts`, enhance the log at line 131 to use the format the user requested:
```
[MODEL_ROUTER] Provider: anthropic | Model: claude-sonnet-4-20250514 | Local: false
```

Also add a log AFTER successful provider response:
```
[MODEL_ROUTER] Response OK | Provider: anthropic | Latency: 1234ms
```

### Files Modified
- `apps/dashboard/src/app/api/chat/route.ts` — enhance 2 log lines

---

## Phase 4: Restart Services and Verify

### Tasks
1. Rebuild + restart backend container (picks up new env var)
2. Restart dashboard (picks up new env var)
3. Verify INTERNAL_RESOLVE_TOKEN is loaded:
   - `curl -s http://localhost:8091/api/user/model-config/resolve` should return 403 (token mismatch without header) not 500
4. Activate the OpenAI config (id=3) for chat context:
   - `curl -X POST http://localhost:8091/api/user/model-config/activate -H 'Content-Type: application/json' -d '{"config_id": 3, "context": "chat"}'`
5. Verify active config now shows openai:
   - `curl http://localhost:8091/api/user/model-config/active` → chat.provider should be "openai"
6. Check dashboard logs for `[MODEL_ROUTER] Provider: openai` on next chat request

### Verification
- Send a test chat message via the UI
- Dashboard server log shows: `[MODEL_ROUTER] Provider: openai | Model: gpt-4.1 | Local: false`
- Response comes from OpenAI (not Qwen) — content style/speed difference is obvious
- If OpenAI key is invalid, user sees an explicit error (not silent Qwen fallback)

---

## Files Summary

| Action | File | Change |
|--------|------|--------|
| Modify | `apps/backend/.env` | Add INTERNAL_RESOLVE_TOKEN |
| Modify | `apps/dashboard/.env.local` | Add INTERNAL_RESOLVE_TOKEN |
| Modify | `apps/dashboard/src/lib/agent/model-resolver.ts` | Replace silent fallbacks with thrown errors |
| Modify | `apps/dashboard/src/app/api/chat/route.ts` | Enhance logging format |

## What This Does NOT Change
- No new providers, no new SDKs, no new endpoints
- No DB schema changes
- No generated types
- No contract surface changes
- Cloud providers remain text-only (no ZakOps tools) — that's by design

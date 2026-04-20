# 3-Pass Escalation Report — MODEL-CONFIG-001
## Simplified Multi-Model Configuration (LangSmith-Style UX)
## Date: 2026-02-21
## Auditor: Claude Opus 4.6
## Input: MODEL-CONFIG-001 mission plan (717 lines, 9 phases, 14 AC)

---

## Executive Summary

The MODEL-CONFIG-001 plan is **architecturally sound** with good phase decomposition, clear dependency graph, and proper surface awareness. However, codebase deep-dive reveals **2 stop-the-line issues**, **6 architecture corrections**, **5 security hardening items**, and **5 UX differentiation opportunities** that collectively upgrade this from a good plan to a world-class implementation.

**Stop-the-line issues** (must fix before Phase 1):
1. Resolve endpoint (`POST /api/user/model-config/resolve`) returns decrypted API keys over HTTP — combined with `CORS: ["*"]` on the backend, this is a key exfiltration vector.
2. Encryption module silently degrades to plaintext (version 0) when `TOKEN_ENCRYPTION_KEY` is unset — the plan should REFUSE to store keys without encryption, not silently store them in cleartext.

---

## Pass 1 — Architecture & Correctness

### Finding A1: `is_active` Invariant Needs DB-Level Enforcement
**What:** The plan defines `is_active` as a boolean column with app-level logic in the `activate` endpoint to "deactivate others." Two concurrent activate requests can leave 0 or 2 active models per context.

**Why:** The preferences router pattern (which this follows) uses single-row upsert. But model configs have N rows per context — the "exactly one active" invariant is a multi-row constraint that app-level logic alone can't guarantee under concurrency.

**How:**
- Add a partial unique index: `CREATE UNIQUE INDEX idx_one_active_per_context ON model_configurations (user_id, context) WHERE is_active = true;`
- Wrap activate in a transaction: `BEGIN → UPDATE SET is_active=false WHERE context=$1 → UPDATE SET is_active=true WHERE id=$2 → COMMIT`
- The partial unique index acts as a DB-level safety net — if the transaction logic fails, the DB will reject the duplicate.

**AC:** `INSERT` two `is_active=true` rows for the same (user_id, context) → DB returns unique violation error.

---

### Finding A2: Resolve Endpoint Should Be Eliminated as a REST API
**What:** The plan creates `POST /api/user/model-config/resolve` as a backend REST endpoint that returns decrypted API keys. The chat route (running in Next.js server) calls this over HTTP.

**Why:** This creates an HTTP endpoint that returns plaintext API keys. Even with `backendHeaders()` auth, any process on the network that can reach port 8091 with the API key header can extract every stored provider key. The backend has `CORS: ["*"]` — a browser-based attack from any origin could call this.

**How:** Instead of a REST endpoint, the chat route should call the backend's `/api/user/model-config/active` endpoint (which returns `has_api_key: true` + `provider` + `model` but NOT the key). Then, for cloud providers, the chat route sends the message payload to a NEW backend endpoint `POST /api/user/model-config/proxy-chat` which:
1. Decrypts the key server-side
2. Calls the cloud provider API server-side
3. Returns the response

This way, **decrypted keys never leave the backend process.** The dashboard's chat route becomes a pass-through for cloud models.

**Alternative (simpler):** If proxy-chat is too complex for Phase 1, keep the resolve endpoint but:
- Bind it to `127.0.0.1` only (not the Docker network)
- Add a `X-Internal-Resolve-Token` header that only the Next.js server knows
- Exclude it from OpenAPI spec (no codegen, no client access)
- Log every call to the resolve endpoint as a security event

**AC:** Decrypted API keys never appear in any HTTP response visible to the browser. Verify with browser DevTools Network tab.

---

### Finding A3: Email Triage Context Is Aspirational — Document It
**What:** The plan creates dual contexts (chat + email_triage) as if both use LLMs today. Codebase audit reveals `email_triage_review_email.py` (851 lines) is purely regex/keyword extraction — **zero LLM calls.**

**Why:** Building the infrastructure is correct (forward-looking), but the plan reads as if email triage already uses a model. This creates confusion about what the "Email Triage" tab in settings actually controls right now.

**How:**
- In P3-02 (ModelConfigSection), the Email Triage tab should show: "Email Triage currently uses rule-based processing. Model-based triage will be available in a future update."
- Disable the "Set Active" control for email_triage context with a tooltip explaining why.
- Still store the config in the DB (ready for future use).
- Update AC-2 to say "independent selections stored; email_triage context is stored but not yet consumed by the runtime."

**AC:** Email Triage tab shows informational banner. Active model can be configured but a "not yet active" badge is visible.

---

### Finding A4: Chat Route Is 500+ Lines — Extract Model Resolution
**What:** The chat route (`route.ts`) is already 522 lines. The plan adds `getActiveModelConfig()` with cache + provider creation logic + resolve call directly into this file.

**Why:** Adding ~80 more lines to a 500+ line route makes it hard to test and maintain. The model resolution logic is independent of the chat flow.

**How:** Create `apps/dashboard/src/lib/agent/model-resolver.ts`:
```typescript
export async function resolveActiveProvider(context: ModelContext): Promise<AgentProviderType> {
  const activeModel = await getActiveModelConfig(context); // cached 10s
  if (activeModel.provider === 'local') return agentProvider;
  const apiKey = await resolveApiKey(activeModel.id); // server-to-server
  return createProvider(activeModel.provider, activeModel.model, apiKey);
}
```
- Chat route reduces to: `const provider = await resolveActiveProvider('chat');`
- Cacheing, failover, and provider creation all live in the resolver.
- Add this file to Phase 4 file list.

**AC:** Chat route `POST` handler is under 400 lines after refactor.

---

### Finding A5: API Key Propagation Needs Explicit Semantics
**What:** The plan says "When saving a key for provider X in context Y, also propagate to other contexts for same provider (shared keys)." The implementation details are vague.

**Why:** If a user sets an OpenAI key for Chat, the same key should auto-populate for Email Triage (when that becomes active). But what if the user later sets a DIFFERENT key for Email Triage? Is that allowed? The plan doesn't specify.

**How:** Define explicit semantics:
- **Shared key model:** One API key per (user_id, provider). The `api_key_encrypted` column lives on a separate `provider_credentials` table, and `model_configurations` references it via `provider`.
- **OR simpler:** Keep one table, but upsert logic is: "If the user provides an `api_key` in the PUT body, update `api_key_encrypted` for ALL rows matching (user_id, provider), regardless of context." If the user explicitly wants different keys per context (edge case), they can use the custom provider for the second one.
- Document this behavior in the API: `PUT /api/user/model-config` response includes `api_key_propagated_to: ["email_triage"]`.

**AC:** Set API key for OpenAI/Chat → GET model-config shows `has_api_key: true` for OpenAI/Email Triage too.

---

### Finding A6: Delete Endpoint Needs Guardrails
**What:** `DELETE /api/user/model-config/{config_id}` has no restrictions.

**Why:** Deleting the active model for a context leaves no active model. Deleting the local provider removes the default fallback. Both are dangerous.

**How:**
- Cannot delete a config where `is_active=true` — return 409 with "Deactivate this model first by switching to another."
- Cannot delete the local provider config — return 409 with "Local provider cannot be removed."
- Can delete cloud provider configs freely (removes key + config).

**AC:** Attempt to DELETE active model → 409. Attempt to DELETE local config → 409. Delete non-active cloud config → 200.

---

## Pass 2 — Security, Reliability, Failure Containment

### Finding S1: STOP-THE-LINE — Encryption Must Be Mandatory, Not Graceful Degradation
**What:** `encryption.py` returns `(plaintext_token, 0)` when encryption is unavailable. The plan accepts this fallback.

**Why:** Silently storing API keys in plaintext defeats the entire purpose of the encryption system. A misconfiguration (key env var accidentally deleted) would store all subsequently saved keys in cleartext without any user-visible warning. This is a security trap.

**How:**
- In the model_config router's `PUT` handler: call `is_encryption_available()` before encrypting. If `false`, return `HTTP 503 Service Unavailable` with body `{"error": "encryption_unavailable", "message": "API key encryption is not configured. Contact your administrator."}`.
- Never store api_key with version 0 in the model_configurations table. Version 0 = no key stored.
- Add a health check sub-check: `GET /health` includes `"encryption": true/false`.
- Phase 0 gate becomes hard: if `is_encryption_available()` is false, STOP. Do not proceed.

**AC:** With `TOKEN_ENCRYPTION_KEY` unset, `PUT` with `api_key` returns 503. No version-0 keys exist in DB.

---

### Finding S2: STOP-THE-LINE — Resolve Endpoint + CORS Wildcard = Key Exfiltration
**What:** Backend has `CORSMiddleware(allow_origins=["*"])`. If `/api/user/model-config/resolve` exists as a standard endpoint, any website can call it with the API key header.

**Why:** The `ZAKOPS_API_KEY` is a shared secret between dashboard and backend. If it leaks (or is guessable), combined with CORS *, any origin can extract all stored provider keys via the resolve endpoint.

**How:** See A2 above for the architectural fix (eliminate resolve endpoint). Additionally:
- For Phase 1, add the resolve endpoint to an explicit CORS exclusion list OR use a decorator that blocks browser-origin requests (check `Origin` header, reject non-null origins).
- Long-term: tighten CORS to `["http://localhost:3003"]` (dashboard only). This is out of scope for MODEL-CONFIG-001 but should be filed as a follow-up.

**AC:** Browser `fetch('http://localhost:8091/api/user/model-config/resolve', ...)` from any origin returns CORS error or 403.

---

### Finding S3: Connection Test Needs Rate Limiting + Timeout
**What:** `POST /api/user/model-config/test` calls external provider APIs. No rate limiting or timeout specified.

**Why:**
- Without timeout: a hanging external API blocks the backend worker indefinitely.
- Without rate limiting: automated calls could burn through the user's API quota or trigger provider rate limits.

**How:**
- Add `asyncio.wait_for(test_call, timeout=15.0)` around each provider test.
- Rate limit: max 1 test per provider per 10 seconds (simple in-memory dict with timestamps).
- Return timeout as a structured error: `{"status": "error", "message": "Connection timed out after 15s"}`.

**AC:** Test with a non-responsive endpoint → returns timeout error within 20s. Rapid-fire test calls → 429 after 2nd call within 10s.

---

### Finding S4: Audit Trail for Key Lifecycle Events
**What:** The plan creates CRUD endpoints for model configs including API key storage. No audit logging mentioned.

**Why:** API key creation, rotation, deletion, and connection tests are security-sensitive operations. The backend already has `action_audit_events` (SQLite) and `agent_events` (PostgreSQL). Model config changes should be logged for compliance and debugging.

**How:**
- Log to `agent_events` (PostgreSQL, append-only) with event types:
  - `model_config.key_stored` (provider, context, has_key=true)
  - `model_config.key_deleted` (provider, context)
  - `model_config.activated` (provider, context, model)
  - `model_config.test_executed` (provider, status, latency_ms)
- Never log the actual key or encrypted key.
- Add to Phase 1 tasks.

**AC:** After storing a key, `SELECT * FROM zakops.agent_events WHERE event_type LIKE 'model_config.%'` returns audit rows.

---

### Finding S5: localStorage Migration Should Be Transactional
**What:** Migration reads from localStorage, sends each provider to the server, then sets `migrated` flag.

**Why:** If migration succeeds for OpenAI but fails for Anthropic (network error), the `migrated` flag might not get set, causing retry. Or worse, it gets set, and the Anthropic key is lost (cleared from localStorage but never reached server).

**How:**
- Step 1: Read all localStorage settings.
- Step 2: Send ALL providers in a single `POST /api/user/model-config/migrate` batch endpoint (new).
- Step 3: Backend stores all-or-nothing (transaction).
- Step 4: On success, set `migrated` flag AND clear keys from localStorage.
- Step 5: On failure, leave localStorage untouched, show warning toast.
- Alternative (simpler): Don't clear localStorage until user explicitly confirms migration worked. Migration just copies, doesn't move.

**AC:** Disconnect network mid-migration → localStorage untouched, no data loss. Reconnect → migration succeeds on retry.

---

## Pass 3 — World-Class UX + Product Differentiation

### Finding U1: Model Name in Chat Header (LangSmith Parity)
**What:** The plan describes a `DropdownMenu` for ModelSwitcher. LangSmith shows the current model name prominently in the header bar at all times.

**Why:** Users need constant awareness of which model they're talking to. A dropdown icon alone doesn't convey this — you have to click to see.

**How:**
- `ModelSwitcher` renders as: `[provider-icon] Claude Sonnet 4.6 [chevron-down]`
- The full model name is always visible, not hidden behind a click.
- On narrow screens, truncate to provider icon + short name: `[icon] Sonnet 4.6 [v]`
- Color-code the text: local = default, cloud = blue accent.
- This matches LangSmith's always-visible model indicator.

**AC:** Chat page header shows current model name without clicking any dropdown.

---

### Finding U2: Connection Test with Latency Display
**What:** Plan says "Test Connection button with status feedback." This is generic.

**Why:** LangSmith differentiates by showing connection quality, not just pass/fail. Showing latency helps users choose between models (e.g., local vLLM at 50ms vs OpenAI at 800ms).

**How:**
- Test button shows: `[spinner]` → `Connected in 342ms` (green) or `Failed: 401 Unauthorized` (red)
- Store `last_test_latency_ms` alongside `last_test_status` in DB.
- In the model management grid, show latency as a subtle badge: "342ms" in gray.
- In the ModelSwitcher dropdown, show colored latency dots: green (<500ms), yellow (500-2000ms), red (>2000ms or failed).

**AC:** Test Connection shows "Connected in Xms" with green styling. Management grid shows latency badge per provider.

---

### Finding U3: Paste-Aware API Key Input
**What:** Plan says "password input with eye toggle" for API keys.

**Why:** Users always paste API keys (never type them). The UX should optimize for paste, not type. Auto-detecting key format on paste reduces errors.

**How:**
- On paste event, detect format:
  - Starts with `sk-` → "Looks like an OpenAI key" (green hint)
  - Starts with `sk-ant-` → "Looks like an Anthropic key" (green hint)
  - Starts with `AIza` → "Looks like a Google AI key" (green hint)
  - Other → "Key format not recognized" (yellow hint, not blocking)
- If user is configuring OpenAI but pastes an Anthropic key → "This looks like an Anthropic key. Did you mean to configure Anthropic?" with a "Switch to Anthropic" link.
- Auto-trim whitespace on paste (common copy-paste artifact).

**AC:** Paste an Anthropic key into OpenAI dialog → shows provider mismatch warning with switch link.

---

### Finding U4: Model Switch Confirmation Toast
**What:** Plan says "Instant switch, no reload." But no feedback that the switch happened.

**Why:** When a user clicks a model in the dropdown, the dropdown closes. Without feedback, they're left wondering: did it work? Is the next message going to the new model? LangSmith shows a subtle transition animation.

**How:**
- On successful activation mutation: show toast `Switched to [provider-icon] Claude Sonnet 4.6` (Sonner, 3s auto-dismiss).
- If activation fails: show error toast `Failed to switch model. Still using [current model].`
- The ModelSwitcher should show a brief loading state (spinner replacing chevron) during the mutation.

**AC:** Switch model → toast appears within 500ms confirming the switch with model name and icon.

---

### Finding U5: "Last Tested" Freshness Indicator
**What:** The plan stores `last_test_status` and `last_test_at`. The management page shows status badges.

**Why:** A connection test from 3 days ago is stale — the key might have been revoked. Users should see when the test was run, not just pass/fail.

**How:**
- Status badges show recency: "Connected (2 min ago)" in green, "Connected (3 days ago)" in yellow, "Never tested" in gray.
- The settings section shows a "Re-test all" button that tests all configured providers in parallel (Promise.allSettled).
- Auto-test on key save: after successfully saving an API key, automatically run a connection test.
- Show a warning if a provider hasn't been tested in >24h and is set as active.

**AC:** Save an API key → auto-test runs → badge shows "Connected (just now)." After 24h without test → yellow "stale" indicator.

---

## Consolidated 10x Improvements

| # | Pass | Finding | Severity | Phase Impact |
|---|------|---------|----------|-------------|
| A1 | Arch | Partial unique index for is_active | HIGH | P1 (migration) |
| A2 | Arch | Eliminate resolve endpoint / proxy-chat | CRITICAL | P1 (router), P4 (chat route) |
| A3 | Arch | Email triage context as aspirational | MEDIUM | P3 (UI) |
| A4 | Arch | Extract model-resolver.ts | MEDIUM | P4 (new file) |
| A5 | Arch | Explicit API key propagation semantics | MEDIUM | P1 (router) |
| A6 | Arch | Delete endpoint guardrails | MEDIUM | P1 (router) |
| S1 | Sec | Mandatory encryption (no version 0) | CRITICAL | P1 (router) |
| S2 | Sec | Resolve endpoint + CORS fix | CRITICAL | P1 (router) |
| S3 | Sec | Rate limit + timeout on test | HIGH | P1 (router) |
| S4 | Sec | Audit trail for key lifecycle | MEDIUM | P1 (router) |
| S5 | Sec | Transactional localStorage migration | MEDIUM | P3 (migration) |
| U1 | UX | Model name in chat header | HIGH | P4 (ModelSwitcher) |
| U2 | UX | Connection test with latency | MEDIUM | P1 (router), P3 (dialog) |
| U3 | UX | Paste-aware API key input | MEDIUM | P3 (dialog) |
| U4 | UX | Model switch toast | LOW | P4 (ModelSwitcher) |
| U5 | UX | Last-tested freshness + auto-test | MEDIUM | P1 (schema), P6 (page) |

---

## Stop-the-Line Issues

### STL-1: Encryption Must Be Mandatory
**Current plan:** Falls back to plaintext (version 0) silently.
**Required:** `PUT` with `api_key` returns 503 if encryption unavailable. Phase 0 gate: `is_encryption_available()` must return `True`.
**Verified:** `TOKEN_ENCRYPTION_KEY` IS set in `apps/backend/.env`. `cryptography>=42.0.0` IS in `requirements.txt`. Risk is low but the code path must still refuse version 0.

### STL-2: Resolve Endpoint + CORS Wildcard
**Current plan:** Creates REST endpoint returning decrypted keys. Backend has `allow_origins=["*"]`.
**Required:** Either (a) eliminate resolve endpoint and proxy chat through backend, or (b) add explicit CORS exclusion + internal-only auth token for the resolve endpoint.
**Recommendation:** Option (b) for Phase 1 simplicity, with option (a) as a future hardening mission.

---

## Amended Phase 1 Tasks (incorporating improvements)

Original P1-01 migration additions:
```sql
-- A1: Partial unique index for active model invariant
CREATE UNIQUE INDEX idx_one_active_per_context
  ON zakops.model_configurations (user_id, context)
  WHERE is_active = true;

-- U2/U5: Additional columns for latency tracking
ALTER TABLE ... ADD COLUMN last_test_latency_ms INTEGER;
```

Original P1-03 router additions:
- S1: `PUT` handler checks `is_encryption_available()` → 503 if false
- S2: Resolve endpoint gets `X-Internal-Resolve-Token` header check + Origin header rejection
- S3: Test endpoint gets 15s timeout + 10s per-provider rate limit
- S4: All mutations log to `agent_events` table
- A5: PUT handler propagates API keys across all contexts for same provider
- A6: DELETE returns 409 for active models and local provider

---

## Verdict

The original plan scores **7/10** — solid architecture, correct phase ordering, good surface awareness. With the 16 improvements above, it becomes **9.5/10**: secure by default, delightful UX, production-hardened.

The 2 stop-the-line issues (STL-1, STL-2) are non-negotiable prerequisites. The 6 architecture corrections (A1-A6) should be incorporated before execution. The 5 security items (S1-S5) are hard requirements. The 5 UX items (U1-U5) are differentiators that make this LangSmith-quality rather than just functional.

**Recommendation:** Update MODEL-CONFIG-001 with these findings, then proceed to execution.

---

*End of 3-Pass Escalation Report*

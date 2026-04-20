AGENT IDENTITY
- agent_name: Codex
- run_id: 20260205-1840-p1r4
- date_time: 2026-02-05T18:40:00Z
- repo_revision_dashboard: b96b33c5547258663123a637dcff741c96b028c9
- repo_revision_backend: 2a68de172c7faf1df6f53357f4b43b0161d5dd32
- repo_revision_agent_api: b96b33c5547258663123a637dcff741c96b028c9

# Round-4 PASS1 — Augmented Findings & Improvements

## A) What’s Missing (blind spots across Claude-Opus + Codex + Gemini)
1) **Complete action inventory for `/hq` and `/agent/activity` pages** — only Codex lists these pages; no report maps their UI actions to endpoints or verifies method correctness. NEEDS VERIFICATION: enumerate `apps/dashboard/src/app/hq/page.tsx` and `apps/dashboard/src/app/agent/activity/page.tsx` for fetches; map to `/api/*` routes; confirm backend handlers.
2) **Settings “Test Connection” mismatch** — only Codex flags `GET /api/chat` usage; Claude/Gemini omit. This is a direct 405 risk. NEEDS VERIFICATION: inspect `apps/dashboard/src/lib/settings/provider-settings.ts:139-147` and `apps/dashboard/src/app/api/chat/route.ts`.
3) **Dashboard `/api/alerts` + `/api/deferred-actions/due` contract drift** — no report checks these endpoints; they can silently fail if status enums or field names mismatch. NEEDS VERIFICATION: trace `apps/dashboard/src/app/api/alerts/route.ts` and `/api/deferred-actions/due/route.ts` vs backend fields.
4) **Ask Agent sidebar actions** — only mentioned as “not integrated,” but no contract map for its quick actions, nor any SSE wiring verification from the drawer. NEEDS VERIFICATION: find drawer component and confirm it calls `/api/chat` and handles streaming.
5) **Next.js rewrites vs API route handler precedence audit** — only Codex highlights this; other reports do not require a systematic scan to ensure `route.ts` doesn’t override rewrites and drop HTTP methods.
6) **Auth wiring clarity** — Claude/Gemini do not address X‑API‑Key injection. This is a P0 risk if any client-side POST/PUT/PATCH/DELETE bypasses Next API routes.
7) **Method matrix for every `route.ts`** — none of the plans require extracting `export function GET/POST/DELETE…` for every Next API route and comparing to UI calls.
8) **Settings data persistence** — all plans discuss email settings, but none define server‑side persistence model, encryption, or rotation. NEEDS VERIFICATION: what backend endpoints exist for settings storage, and how secrets are stored.
9) **Consistency checks between UI counts and agent counts** — all mention mismatch, but no plan includes a hard “counts must match” gate for deals/quarantine/actions; needs explicit QA gate.
10) **SSE client behavior in browser** — no report verifies reconnection/partial‑token handling in the dashboard chat UI (only curl/SSE assumptions).
11) **Bulk operation semantics** — no report defines payload schemas (`ids` vs `deal_ids`) and response shapes for bulk endpoints (deals/actions/quarantine), risking UI/back‑end drift.
12) **Error schema normalization** — reports note toast errors but don’t specify a standard error payload (JSON shape) and UI handling for 401/403/405.

## B) What’s Wrong / Weak (fragile or ambiguous recommendations)
1) **“Just add backend endpoints”** (Claude/Gemini): Several tasks propose creating endpoints without deciding if the correct fix is instead to align UI to existing endpoints. Example: quarantine delete might be undesired by product; better to disable UI or use “reject” only. NEEDS VERIFICATION: confirm with product policy and backend semantics.
2) **“Force SQL fallback”** (Gemini): Correct for data consistency short‑term, but it hides RAG staleness instead of fixing index freshness. Should be framed as a temporary mitigation with a hard deadline and RAG reindex gate.
3) **Missing API key integration plan** (Claude/Gemini): They propose endpoint fixes but ignore that write routes will still fail without X‑API‑Key or equivalent auth. This will cause “works in dev, fails in prod.”
4) **Bulk endpoints assumed to exist** (Claude/Gemini): They recommend `/api/kinetic/actions/bulk/delete` or `/api/deals/bulk-*` without verifying backend implementation. Needs an explicit verification step (route scan, OpenAPI). Otherwise plan risks adding proxy to non‑existent endpoints.
5) **No guarantee of “No Dead UI” gating** (Claude/Gemini): Both list E2E gates but don’t add automated static detection for empty handlers / disabled actions (a key requirement).
6) **Plan lacks explicit rollback** (Claude/Gemini): No rollback strategy for routing changes, API proxy changes, or auth header insertion. For a dashboard, these are reversible via feature flags.
7) **No explicit schema contract extraction** (All): None define how to generate/verify request/response schemas across the UI endpoints; “contract gate” is described but not operationalized.
8) **Quarantine preview diagnosis is thin** (All): The “preview not found” may be a mismatch between action_id vs item_id or missing content. Needs explicit data model check and endpoint behavior (GET /api/quarantine/{id} vs /api/actions/{id}).
9) **Actions endpoint confusion** (All): Backend contains two actions routers (orchestration vs routers/actions). Plans don’t define a single canonical contract; this is likely to recur.
10) **Settings redesign lacks data model** (All): None specify DB schema or API for settings persistence; missing enforcement for secure storage.

## C) “What else is broken?” — systematic expansion + detection plan
Pattern 1 — **405 Method Not Allowed**
- Likely elsewhere: Any Next API route `route.ts` that only exports GET/POST while UI calls DELETE/PATCH.
- Detection: script to extract exported methods and compare to UI fetch methods.
  - `find apps/dashboard/src/app/api -name 'route.ts' -print` + `grep -E 'export (async )?function (GET|POST|PUT|PATCH|DELETE)'`.
  - `rg -n "fetch\(|apiFetch\(" apps/dashboard/src -g"*.ts*"` and map method usage.
- Prevention: Contract Gate that fails CI on method mismatch.

Pattern 2 — **Proxy path mismatches** (`/api/actions` vs `/api/kinetic/actions`)
- Likely elsewhere: quarantine, deals bulk endpoints, capabilities, clear‑completed.
- Detection: parse `next.config.ts` rewrites and `route.ts` handlers; verify target paths exist in backend route list.
- Prevention: auto‑generated proxy map from backend OpenAPI + test harness.

Pattern 3 — **Client-side writes without auth**
- Likely elsewhere: any direct `apiFetch` call with `method !== 'GET'`.
- Detection: `rg -n "apiFetch\(.*method: 'POST'|PUT|PATCH|DELETE" apps/dashboard/src/lib/api.ts` and confirm the call path uses server route with API key.
- Prevention: lint rule disallowing client-side write calls to `/api/*` without server proxy.

Pattern 4 — **Demo-only UI**
- Likely elsewhere: onboarding, Ask Agent drawer, Settings localStorage, mock timers.
- Detection: `rg -n "localStorage|mock|setTimeout\(|demo|fake" apps/dashboard/src/components apps/dashboard/src/app`.
- Prevention: CI rule that blocks merging if onboarding steps lack backend API calls.

Pattern 5 — **Data desync (agent vs UI)**
- Likely elsewhere: pipeline counts, actions counts, quarantine counts.
- Detection: contract test that compares backend `/api/deals` counts vs agent tool output; fail if mismatch > 0.
- Prevention: “single source of truth” gate + telemetry on count mismatch.

## D) World-class upgrades (dashboard‑specific, 10+ ideas)
1) **Contract-first UI client generation**: generate typed TS client (and Zod schemas) from backend OpenAPI; prohibit hand-written `/api/*` strings in UI.
2) **No‑Dead‑UI CI Gate**: static scan + Playwright that clicks every button and verifies non‑stub response. Fail if any 404/405/500 or noop handler detected.
3) **Method/Route Diff Tool**: CI job that diffs UI `fetch` usage against backend route list and Next API method exports.
4) **Unified Ops Endpoint**: `POST /api/ops` on the BFF handles bulk operations with consistent payloads and atomic results.
5) **Settings as a first‑class model**: store provider/email/agent settings in a `user_settings` table with encryption + rotation; UI reads/writes via `/api/settings/*`.
6) **Correlation ID injection middleware**: Next.js middleware that adds `x-correlation-id` to every request and surfaces it in UI toasts/logs.
7) **UI contract watchdog**: runtime boundary checks (safeParse) for every API response; fallback UI on schema mismatch.
8) **Ask Agent unified chat provider**: all chat surfaces (drawer, full chat, deal‑level chat) share a single SSE client and message renderer.
9) **Resilient SSE handling**: automatic reconnect, resume via last event ID; show connection health in UI.
10) **Ops health ribbon**: dashboard banner showing backend/agent/rag status; disables dependent UI actions automatically.
11) **Bulk action preview/rollback**: show affected items before bulk delete/archive; allow undo window.
12) **Feature flagging for risky UI flows**: enable/disable onboarding and settings sections per environment to prevent demo‑ware in prod.

## Verification Steps (for ambiguous items)
- **Check backend routes**: `python - <<'PY'` to load FastAPI app and list routes; compare with UI map.
- **Check UI method use**: `rg -n "apiFetch\("` and inspect method per call.
- **Check proxy overrides**: compare `apps/dashboard/src/app/api/**/route.ts` against `next.config.ts` rewrites.
- **Check settings persistence**: search for `/api/settings` routes; if missing, mark NEEDS IMPLEMENTATION.


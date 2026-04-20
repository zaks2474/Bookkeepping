# Remediation Log — DASHBOARD-P4-STABILIZE-001
**Date:** 2026-02-11

## Phase 1: Chat Page Critical Fixes

### F-1: Nested `<button>` in ChatHistoryRail (Sev-1)
- **File:** `apps/dashboard/src/components/chat/ChatHistoryRail.tsx`
- **Fix:** Replaced outer `<button>` with `<div role="button" tabIndex={0}>` with keyboard handler (Enter/Space). Inner `<Button>` for delete remains unchanged with `stopPropagation`.
- **Result:** No more nested interactive elements. Hydration error eliminated. Keyboard accessibility preserved.

### F-2: History dedup unconditional re-archive (Sev-2)
- **File:** `apps/dashboard/src/app/chat/page.tsx`
- **Fix:** Added guard `if (archivedSessionId !== sessionId)` before calling `archiveCurrentSession()` in `handleLoadFromHistory`. Prevents unnecessary re-archive when loading the already-active session.
- **Result:** Eliminates redundant localStorage writes and potential history duplication.

### F-3: No visual separation between history items (Sev-2)
- **File:** `apps/dashboard/src/components/chat/ChatHistoryRail.tsx`
- **Fix:** Changed `border border-transparent` to `border border-border/40`. Items now have a subtle visible border at 40% opacity.
- **Result:** Clear visual delineation between history entries.

## Phase 2: Performance Stabilization

### F-4: Global staleTime too aggressive (Sev-2)
- **File:** `apps/dashboard/src/components/layout/providers.tsx`
- **Fix:** Reduced `staleTime` from `5 * 60 * 1000` (5min) to `30 * 1000` (30s). Changed `refetchOnMount` from `false` to `true` so stale data gets refreshed on component mount.
- **Result:** Per-hook `staleTime` overrides now work correctly. Dashboard data refreshes more frequently.

### F-5: Double proxy — rewrites + middleware (Sev-2)
- **File:** `apps/dashboard/next.config.ts`
- **Fix:** Removed the `rewrites()` function that proxied `/api/:path*` to backend. Middleware already handles all `/api/*` proxying with proper JSON 502 error responses.
- **Result:** Single proxy path through middleware. No more double-proxy ambiguity.

### F-6: Timeout mismatch — 30000 vs 15000 (Sev-2)
- **File:** `apps/dashboard/src/middleware.ts`
- **Fix:** Changed default timeout from `'30000'` to `'15000'` to match `backend-fetch.ts`. Both now read `PROXY_TIMEOUT_MS` with the same 15000ms fallback.
- **Result:** Consistent timeout behavior across all backend fetch paths.

## Phase 3: Dashboard Data & Layout

### F-7: Deal ID regex too strict (Sev-2)
- **File:** `apps/dashboard/src/app/deals/[id]/page.tsx`
- **Fix:** Changed regex from `^DL-\d+$/i` (digits only) to `^DL-[A-Za-z0-9]+$/i` (alphanumeric). Now accepts IDs like `DL-IDEM2`.
- **Result:** All backend-issued deal IDs are accepted. Verified DL-IDEM2 loads in browser.

### F-8: Client-side deal count (Sev-2)
- **File:** `apps/dashboard/src/app/dashboard/page.tsx`
- **Fix:** Replaced `filteredDeals.length` in the All Deals CardDescription with server-side counts: `stageCounts[selectedStage]` when filtered, `pipelineData?.total_active` when unfiltered.
- **Result:** Deal counts match server-computed values per DEAL-INTEGRITY-UNIFIED-001 mandate.

### F-9: Fixed max-h-[500px] on ScrollArea (Sev-2)
- **File:** `apps/dashboard/src/app/dashboard/page.tsx`
- **Fix:** Changed `max-h-[500px]` to `max-h-[60vh]` for viewport-relative sizing.
- **Result:** Deals list adapts to viewport height instead of being capped at a fixed pixel value.

### F-10: Pipeline "0 stages" on API failure (Sev-2)
- **File:** `apps/dashboard/src/app/dashboard/page.tsx`
- **Fix:** When `pipelineData` is null, the stage count phrase is omitted entirely (just shows deal count). When available, shows proper singular/plural: "across N stage(s)".
- **Result:** No misleading "0 stages" text on degraded data.

### F-11: Alert cards not clickable (Sev-2)
- **File:** `apps/dashboard/src/app/dashboard/page.tsx`
- **Fix:** When `alert.deal_id` is present, wraps alert card in `<Link href="/deals/{deal_id}">` with `cursor-pointer` and hover state. Alerts without deal_id remain non-interactive.
- **Result:** Actionable alerts now navigate to the relevant deal workspace.

## Phase 4: Board View Interactivity

### F-12: DealCard not clickable (Sev-2)
- **File:** `apps/dashboard/src/components/deals/DealBoard.tsx`
- **Fix:** Wrapped the card content area (name, company, date, priority) in `<Link href="/deals/{deal_id}">` with hover opacity transition. Drag handle remains separate and unaffected.
- **Result:** Clicking a deal card navigates to deal workspace. Dragging still works via the grip handle.

### F-13: Drag-and-drop fires without confirmation (Sev-2)
- **File:** `apps/dashboard/src/components/deals/DealBoard.tsx`
- **Fix:** Added `window.confirm()` dialog before executing stage transition. Shows deal name, from-stage label, and to-stage label. Canceling reverts the drop.
- **Result:** Accidental drag-and-drop transitions are prevented by user confirmation.

## Phase 5: Settings Page

### F-14: Settings scroll issues (Sev-2)
- **File:** `apps/dashboard/src/app/settings/page.tsx`
- **Fix:** Split layout into fixed header (back arrow + title) and scrollable content area. Header stays pinned while sections scroll independently.
- **Result:** Back arrow always visible. Content scrolls properly within viewport.

### F-15: No visual container boundaries for nav (Sev-2)
- **File:** `apps/dashboard/src/components/settings/SettingsNav.tsx`
- **Fix:** Added `rounded-lg border border-border/60 bg-card p-2` to the desktop nav container. Creates a card-like visual boundary around navigation items.
- **Result:** Clear visual grouping of settings navigation.

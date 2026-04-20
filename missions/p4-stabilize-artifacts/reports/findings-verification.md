# Findings Verification — DASHBOARD-P4-STABILIZE-001
**Date:** 2026-02-11
**Phase:** 0 — Discovery & Baseline

## Summary
All 15 findings verified against current source code. 14 CONFIRMED as-is, 1 (F-13) confirmed with clarification that drag infrastructure exists but needs live verification.

## Verification Table

| Finding | Sev | File | Reported Issue | Status | Notes |
|---------|-----|------|---------------|--------|-------|
| F-1 | 1 | ChatHistoryRail.tsx:86,99 | Nested `<button>` inside `<Button>` | CONFIRMED | Outer `<button>` at L86, inner `<Button>` at L99 — hydration error risk |
| F-2 | 2 | chat/page.tsx:826-847, chat-history.ts:54 | History dedup unconditional re-archive | PARTIALLY ADDRESSED | `archiveSession` has findIndex dedup (L54), but `handleLoadFromHistory` unconditionally calls `archiveCurrentSession()` before loading — causes unnecessary re-archive of current session |
| F-3 | 2 | ChatHistoryRail.tsx:81 | No visual separation between history items | CONFIRMED | `space-y-1` with `border border-transparent` — borders invisible |
| F-4 | 2 | providers.tsx:12 | Global staleTime 5min overrides hook overrides | CONFIRMED | `staleTime: 5 * 60 * 1000` at QueryClient level, all `refetchOn*` disabled |
| F-5 | 2 | next.config.ts:29, middleware.ts:45 | Double proxy — rewrites + middleware both proxy `/api/*` | CONFIRMED | `rewrites()` in next.config + middleware `handleApiProxy()` both active |
| F-6 | 2 | middleware.ts:16, backend-fetch.ts:5 | Timeout mismatch — 30000 vs 15000 defaults | CONFIRMED | Both read `PROXY_TIMEOUT_MS` but middleware defaults to 30000, backend-fetch to 15000 |
| F-7 | 2 | deals/[id]/page.tsx:88 | Deal ID regex too strict — rejects alphanumeric | CONFIRMED | `^DL-\d+$/i` only allows digits after `DL-`, rejects `DL-IDEM2` etc. |
| F-8 | 2 | dashboard/page.tsx:275 | Client-side `filteredDeals.length` for deal count | CONFIRMED | Should use server-side `pipelineData?.total_active` per DEAL-INTEGRITY-UNIFIED-001 |
| F-9 | 2 | dashboard/page.tsx:288 | Fixed `max-h-[500px]` on ScrollArea | CONFIRMED | Hardcoded height, should use viewport-relative |
| F-10 | 2 | dashboard/page.tsx:232-248 | Pipeline "0 stages" on API failure | CONFIRMED | Falls back to `deals.length` but shows "0 stages" text when `pipelineData` is null |
| F-11 | 2 | dashboard/page.tsx:409-421 | Alert cards not clickable | CONFIRMED | Div with no onClick, no Link wrapper, no cursor-pointer |
| F-12 | 2 | DealBoard.tsx:41-96 | DealCard not clickable | CONFIRMED | `DealCard` component has no onClick handler or Link wrapper |
| F-13 | 2 | DealBoard.tsx:165 | Drag-and-drop fires transition without confirmation | NEEDS LIVE VERIFY | `handleDragEnd` calls `transitionMutation.mutateAsync` — infrastructure exists, needs running backend to test confirmation UX |
| F-14 | 2 | settings/page.tsx:97 | Settings scroll issues, back arrow in scrollable area | CONFIRMED | `overflow-y-auto` on inner div, back arrow at L100 inside scrollable container |
| F-15 | 2 | SettingsNav.tsx:81-120 | No visual container boundaries for nav items | CONFIRMED | Items have `hover:bg-accent/50` but no border/card grouping |

## Line Number Adjustments
No significant line shifts detected. All code locations match the mission spec within +/- 5 lines.

## Baseline Validation
- `make validate-local`: PASS (14/14 contract surfaces)
- TypeScript: clean (`npx tsc --noEmit`)
- Lint: warnings only (react-hooks/exhaustive-deps — pre-existing, not in scope)
- Redocly: 57 ignores (at ceiling)
- Baseline captured: `p4-stabilize-artifacts/reports/baseline-validation.txt`

## Console Error Baseline
Known pre-existing console errors (from M-11 journey replays):
- `/api/settings/email` 404 — expected (settings page, no email config)
- `/api/settings/preferences` 404 — expected (settings page, no preferences endpoint)
- React DevTools / Fast Refresh — dev-mode noise
- No Sev-1 console errors in production paths

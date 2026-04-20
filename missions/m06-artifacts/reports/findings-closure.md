# Findings Closure — UI-MASTERPLAN-M06
**Date:** 2026-02-11
**Mission:** UI-MASTERPLAN-M06 (Actions Command Center Polish)

## F-12: "New Action" button hidden at 375px (Sev-2)
**Status:** CLOSED

**Root Cause:** Toolbar buttons (Clear, Refresh, New Action) used full text labels at all breakpoints. Combined with sidebar width (48px) and page padding (32px), only ~295px remained for buttons at 375px — insufficient for 3 text-labeled buttons (~310px).

**Fix Applied:**
- Clear and Refresh buttons: icon-only below `sm` (640px), text labels at `sm`+
- `aria-label` added to icon-only buttons for screen reader accessibility
- Button container changed from `flex shrink-0` to `flex flex-wrap` for overflow safety
- "New Action" retains full text label at all breakpoints (primary CTA)
- Net horizontal savings at 375px: ~120px, leaving room for all 3 buttons

**Evidence:**
- Before: `m06-artifacts/before/actions-375.png` — only Clear (text) and Refresh (text) visible
- After: `m06-artifacts/after/actions-375.png` — compact icon buttons, search + filter fit cleanly
- E2E: `actions-mobile-primary-controls.spec.ts` — 5/5 PASS

---

## F-11: Empty detail panel wastes space on desktop (Sev-3)
**Status:** CLOSED

**Root Cause:** Desktop layout used a fixed `lg:grid-cols-3` grid with the detail panel always rendered. When no action was selected, a full-height Card with "Select an action to view details" consumed ~33% of viewport width — providing no actionable content.

**Fix Applied:**
- Grid layout made adaptive: `grid-cols-1` when no action selected, `lg:grid-cols-3` when selected
- Empty state card removed entirely — no more placeholder panel
- Action list spans full viewport width when browsing (maximizes list productivity)
- Detail panel renders only on action selection (desktop: inline panel, mobile: bottom sheet unchanged)

**Evidence:**
- Before: `m06-artifacts/before/actions-1280.png` — empty card with bolt icon taking 33% width
- After: `m06-artifacts/after/actions-1280.png` — action list spans full content width
- E2E: `actions-detail-workflow.spec.ts` — 4/4 PASS

---

## Additional Improvements (no finding ID)
- Search input `min-width` reduced from 200px to 150px for better mobile fit
- Type filter dropdown width responsive: 160px mobile, 200px desktop
- `data-testid` attributes added: `new-action-btn`, `action-detail-panel`

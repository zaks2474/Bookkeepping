# Interaction Closure Matrix — Actions Command Center
**Mission:** UI-MASTERPLAN-M06
**Page:** `/actions`
**Status:** BASELINE (Phase 0)

## Legend
- **Real** = Wired to live backend endpoint returning real data
- **Client-only** = Operates purely in browser (no backend call)
- **Placeholder** = UI exists but endpoint returns 404 or not implemented
- **Degraded** = Control visible but disabled/limited due to missing data
- **Hidden** = Control intentionally not rendered at this breakpoint

## Controls Matrix

| # | Control | Type | 1280px | 768px | 375px | Endpoint/Notes |
|---|---------|------|--------|-------|-------|----------------|
| 1 | Clear dropdown | button | Real | Real | Real | Opens archive/delete submenu |
| 2 | Refresh | button | Real | Real | Real | Re-fetches actions data |
| 3 | New Action | button | Degraded | Degraded | Degraded | Conditional on capabilities.length > 0; currently hidden (no capabilities loaded) |
| 4 | Search actions | textbox | Real | Real | Real | Client-side filter |
| 5 | Type filter dropdown | combobox | Real | Real | Real | Filters by action type |
| 6 | Deal ID filter badge | badge+button | Real | Real | Real | Shows when deal_id param present; x to clear |
| 7 | Status tabs (All/Pending/Ready/Processing/Completed/Failed) | tabs | Real | Real | Real | Updates URL + refetches |
| 8 | Pending Approval stat card | button | Real (metrics) | Real | Hidden (no metrics) | Clickable filter; conditional on metrics loaded |
| 9 | Processing stat card | button | Real (metrics) | Real | Hidden | Same |
| 10 | 24h Success Rate stat card | button | Real (metrics) | Real | Hidden | Same |
| 11 | Failed (24h) stat card | button | Real (metrics) | Real | Hidden | Same |
| 12 | Select All checkbox | checkbox | Real | Real | Real | Bulk selection header |
| 13 | Per-action checkbox | checkbox | Real | Real | Real | Individual selection |
| 14 | Action card (compact, in list) | clickable | Real | Real | Real | Selects action for detail view |
| 15 | Bulk Archive Selected | button | Real | Real | Real | Shown when selection active |
| 16 | Bulk Delete Selected | button | Real | Real | Real | Shown when selection active |
| 17 | Cancel bulk selection | button | Client-only | Client-only | Client-only | Clears selection |
| 18 | Detail panel (desktop) | panel | Real | Hidden | Hidden | `hidden lg:block`; shows selected action or empty state |
| 19 | Mobile detail sheet | sheet | Hidden | Real | Real | Fixed bottom sheet when action selected; `lg:hidden` |
| 20 | Detail: Approve | button | Real | Real (sheet) | Real (sheet) | Conditional on status=pending_approval |
| 21 | Detail: Run | button | Real | Real (sheet) | Real (sheet) | Conditional on status=ready |
| 22 | Detail: Cancel | button | Real | Real (sheet) | Real (sheet) | Conditional on status=pending_approval/queued/ready |
| 23 | Detail: Retry | button | Real | Real (sheet) | Real (sheet) | Conditional on status=failed + retryable |
| 24 | Detail: Edit inputs | button | Real | Real (sheet) | Real (sheet) | Conditional on status=pending_approval |
| 25 | Detail: Audit Trail toggle | button | Client-only | Client-only | Client-only | Collapsible section |
| 26 | Detail: Inputs toggle | button | Client-only | Client-only | Client-only | Collapsible section |
| 27 | Detail: Outputs toggle | button | Client-only | Client-only | Client-only | Collapsible section |
| 28 | Detail: Close (mobile) | button | Hidden | Client-only | Client-only | Closes mobile detail sheet |
| 29 | Create Action dialog | dialog | Real | Real | Real | Opens from "New Action" button |
| 30 | Create: Capability select | combobox | Real | Real | Real | Lists capabilities from API |
| 31 | Create: Deal ID input | textbox | Client-only | Client-only | Client-only | Required field |
| 32 | Create: Dynamic inputs form | form | Client-only | Client-only | Client-only | Schema-driven from capability |
| 33 | Create: Submit | button | Real | Real | Real | POST to create action |
| 34 | Create: Cancel | button | Client-only | Client-only | Client-only | Closes dialog |
| 35 | Clear Confirm dialog | dialog | Real | Real | Real | Confirms archive/delete |
| 36 | Clear Confirm: Execute | button | Real | Real | Real | Performs clear operation |
| 37 | Clear Confirm: Cancel | button | Client-only | Client-only | Client-only | Closes dialog |

## Summary (Baseline)
| Status | Count |
|--------|-------|
| Real | ~22 |
| Client-only | ~10 |
| Degraded | 1 (New Action — capabilities not loaded) |
| Placeholder | 0 |
| Hidden (by design) | 4 (detail panel, metric cards at mobile) |
| Broken | 0 |

## Post-Fix Status (Phase 2)

### F-12 Resolution
- Toolbar buttons (Clear, Refresh) are now icon-only below `sm` (640px) — saves ~120px horizontal space
- "New Action" retains full text label at all breakpoints as the primary CTA
- Button container uses `flex-wrap` for overflow safety
- `aria-label` added for accessibility on icon-only buttons
- When capabilities load, "New Action" fits comfortably at 375px alongside compact Clear/Refresh

### F-11 Resolution
- Empty detail panel completely removed — no more static placeholder card
- Grid layout is now adaptive: `grid-cols-1` when no action selected, `lg:grid-cols-3` when selected
- Action list spans full width on desktop when browsing (no wasted 33%)
- Detail panel only appears when user selects an action, providing full context
- Mobile bottom sheet behavior unchanged (still shows on action selection below lg)

### Updated Control Matrix Changes
| # | Control | Change |
|---|---------|--------|
| 1 | Clear dropdown | Icon-only below sm, text at sm+ |
| 2 | Refresh | Icon-only below sm, text at sm+ |
| 18 | Detail panel (desktop) | Now conditional — only rendered when action selected |
| 5 | Type filter dropdown | Width responsive: 160px mobile, 200px sm+ |
| 4 | Search actions | min-width reduced: 200px → 150px for better mobile fit |

## Closed Issues
- **F-12**: CLOSED — toolbar compact at mobile, New Action reachable
- **F-11**: CLOSED — adaptive layout eliminates empty detail panel waste

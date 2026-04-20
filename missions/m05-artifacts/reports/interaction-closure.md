# Interaction Closure Matrix — Deal Workspace (`/deals/[id]`)
**Mission:** UI-MASTERPLAN-M05
**Test deal:** DL-0086
**Status:** FINAL (Phase 2)

## Controls

| # | Control | Type | 375px | 768px | 1280px | Disposition | Notes |
|---|---------|------|-------|-------|--------|-------------|-------|
| 1 | Back to Deals | button | visible | visible | visible | client-only | router.push('/deals') |
| 2 | Add Note | button | visible | visible | visible | real | Opens note dialog → addDealNote API |
| 3 | Chat | link+button | visible | visible | visible | real | Links to /chat?deal_id= |
| 4 | Refresh | button | visible (wrapped) | visible | visible | real | Re-fetches all deal data |
| 5 | Overview tab | tab | visible | visible | visible | real | Shows info cards |
| 6 | Actions tab | tab | visible | visible | visible | real | Shows kinetic actions |
| 7 | Pipeline tab | tab | visible | visible | visible | real | Shows pipeline outputs |
| 8 | Materials tab | tab | visible (scroll) | visible | visible | **degraded-explicit** | Null → amber "unavailable" + Retry |
| 9 | Case File tab | tab | visible (scroll) | visible | visible | **degraded-explicit** | Null → amber "unavailable" + Retry |
| 10 | Events tab | tab | visible (scroll) | visible | visible | real | Shows event history |
| 11 | Stage Transitions | card | below fold | visible | visible | real | Shows allowed transitions |
| 12 | Actions rail | card | below fold | visible | visible | real | Shows top 5 actions |
| 13 | View All Actions | link+button | below fold | visible | visible | real | Links to /actions?deal_id= |
| 14 | Stage badge | badge | visible | visible | visible | display-only | Shows stage with dot color |
| 15 | Status badge | badge | hidden when active | hidden when active | hidden when active | display-only | Only shown when status != active (avoids redundancy) |

## Resolutions Applied
- Control 4 (Refresh): Header now wraps with `flex-wrap` — visible at all breakpoints
- Controls 5-10 (All tabs): TabsList now scrollable with `overflow-x-auto flex-nowrap`
- Controls 8, 9 (Materials, Case File): Explicit degraded messaging with amber text + Retry button
- Control 15 (Status badge): Hidden when status=active to avoid redundancy (F-10)
- Cards: `grid-cols-[auto_1fr]` layout replaces `flex justify-between` for mobile readability (F-08)

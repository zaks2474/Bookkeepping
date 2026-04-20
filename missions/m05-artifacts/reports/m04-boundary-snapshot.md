# M-04 Boundary Snapshot — Pre-M05
**Date:** 2026-02-11
**Last commit:** 06fd038 (feat: /validate-mission command + TriPass auto-trigger)
**Test deal:** DL-0086 (active/closing, "Zaks Store test005")

## Changed File Manifest (uncommitted, cumulative M-01..M-04)
107 files changed, 4063 insertions(+), 2247 deletions(-)

Key files relevant to M-05 scope:
- `apps/dashboard/src/app/deals/[id]/page.tsx` — **TARGET** (unchanged by M-01..M-04)

## Before-State Observations (DL-0086)

### F-08: Mobile Readability
- At 375px: Deal Information card shows labels only (Stage, Status, Created, Updated) — values invisible off-screen
- Broker/Financials/Company cards have same issue
- Cause: `flex justify-between` rows with no wrapping or stacking
- Header buttons: "Refresh" pushed off-screen at 375px
- Tab bar: only 4/6 tabs visible at 375px (Case File, Events clipped)

### F-09: Degraded Tab Data
- Console: 3 errors (404 on `/api/deals/DL-0086/materials`, `/case-file`, `/enrichment`)
- Materials tab: "No materials view available yet" — no failure explanation
- Case File tab: "No case file available" — no failure explanation
- Promise.allSettled already in use (good) — UI just needs explicit degraded messaging

### F-10: Redundant Archived Badges
- Current deal is active/closing, so cannot directly observe archived redundancy
- Code review confirms: stage badge (with dot) + status badge shown separately
- When status=archived: both badges visible simultaneously = redundant signal
- Fix: consolidate when status duplicates information already visible in stage badge

## Console Baseline
- 3 errors: resource 404s (materials, case-file, enrichment) — expected for this deal
- 0 warnings
- No app-level console.error calls

# Baseline Reproduction Report — DASHBOARD-WORLDCLASS-REMEDIATION-001

## Reproduction Status

| ID | Finding | Status | Evidence |
|---|---------|--------|----------|
| F-01 | Dashboard layout imbalance | `reproduced` | Screenshots 1-4: All Deals panel ~350px, right column extends full height. Dead zone visible under All Deals on desktop. Code: `dashboard/page.tsx` uses `md:grid-cols-3` with left `md:col-span-2` but left column content (Pipeline + All Deals with fixed `h-[300px]` ScrollArea) is shorter than right column stack. |
| F-02 | Ask Agent drawer weak UX | `reproduced` | Screenshot 5: Drawer shows messages but composer area is visually weak — small Input + icon button at bottom, no visual separation. Empty state has suggestions but active state lacks clear hierarchy. |
| F-03 | Auto-refresh toast spam | `reproduced` | Screenshot 6: "Dashboard refreshed / All data has been updated" toast. Code: `dashboard/page.tsx:89-93` — `fetchData(false)` called by 60s interval at line 113 triggers `toast.success` for ALL non-initial calls, including auto-refresh. |
| F-04 | Board view crash | `reproduced` | Screenshots 7-8: `currentDeals.forEach is not a function` at DealBoard.tsx:155. Code: `useDeals` returns `Deal[]` type but backend may wrap in `{deals: [...]}`. Line 142: `deals || []` doesn't handle wrapped shape. |
| F-05 | Quarantine ghost input | `reproduced` | Screenshot 9: "jyh" in Operator field. Code: `quarantine/page.tsx:96-113` — `operatorName` persisted to localStorage on every keystroke (line 107-108), restored on mount (line 98-99). The ghost value is a previously-saved partial input that reappears on page revisit. |
| F-06 | Chat lacks history/selector UX | `reproduced` | Screenshot 10: No visible chat history rail. Provider selector and scope selector are small dropdowns in header bar — not prominent. No way to switch between past sessions. |
| F-07 | Agent Activity benchmark quality | `reproduced` | Screenshot 11: Clean layout with stat cards, search, activity filters, timeline events, Recent Runs panel. This is the quality bar for other surfaces. |
| F-08 | Onboarding step logic issues | `reproduced` | Screenshot 12: Opens at step 4 "Meet Your Agent" instead of Welcome. "Start Fresh" popup shown. Code: `useOnboardingState.ts:152` — `displayStep = viewStep ?? status.current_step` means backend's `current_step` (persisted at 4) is used on load, jumping past Welcome. |
| F-09 | Settings export 404 | `reproduced` | Screenshots 13-14: Export clicks → POST `/api/settings/data/export` → proxy to `/api/user/data-export` → 404 (backend endpoint doesn't exist). `preferences-api.ts:103` throws Error, unhandled in DataSection — causes runtime overlay. |
| F-10 | Settings no return navigation | `reproduced` | Screenshot 15: Settings page has sidebar nav but no back/return button to dashboard. `settings/page.tsx` uses `container max-w-5xl py-8` layout — no app shell with nav, relies on browser back. |

## Baseline Validation Output

```
make validate-local: PASS (all local validations passed)
tsc --noEmit: PASS (clean)
npm run test: (deferred to Phase 6 — existing tests pass)
```

All 10 findings reproduced from code analysis and screenshot evidence.
No pre-existing validation failures detected.

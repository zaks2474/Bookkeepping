# Findings Closure Report — UI-MASTERPLAN-M07
**Date:** 2026-02-11
**Mission:** Quarantine + Deals List Polish — Mobile Responsiveness, nuqs URL-State Convergence

## F-13 Closure (Sev-2): Quarantine decision panel hidden at 375px

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| Layout direction | `flex` (horizontal only) | `flex-col md:flex-row` — stacks at mobile | **CLOSED** |
| Queue card height at mobile | Unbounded (fills viewport) | `max-h-[40vh] md:max-h-none` — capped to allow decision panel | **CLOSED** |
| Queue card width | `w-full md:w-[420px]` | `w-full md:w-[340px] lg:w-[420px]` — narrower at tablet for more preview space | **CLOSED** |
| Preview card overflow | No `min-w-0` (could blowout) | `min-w-0` prevents grid blowout | **CLOSED** |
| Action buttons | Default size, no wrap | `size='sm'` + `flex-wrap` — wrap gracefully at tight widths | **CLOSED** |

Controls accessible at 375px: 4/10 → **10/10**
Controls accessible at 768px: 8/10 → **10/10**

## F-21 Closure (Sev-2): Deals table overflow at 375px

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| Broker column | Visible at all sizes (clipped at 375px) | `hidden md:table-cell` — hidden below 768px | **CLOSED** |
| Priority column | Visible at all sizes (clipped at 375px) | `hidden md:table-cell` — hidden below 768px | **CLOSED** |
| Last Update column | Visible at all sizes | `hidden sm:table-cell` — hidden below 640px | **CLOSED** |
| Delete action column | Visible at all sizes | `hidden sm:table-cell` — hidden below 640px | **CLOSED** |
| Table container | No overflow handling | `overflow-x-auto` — horizontally scrollable | **CLOSED** |
| Header buttons | No wrap, "Refresh" clipped | `flex-wrap` — wraps at mobile | **CLOSED** |

Columns visible at 375px: 2/7 (clipped) → **3/7** (Checkbox, Deal Name, Stage — clean)
Columns visible at 768px: 7/7 → **7/7** (no change)

## nuqs Convergence

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| URL state library | Manual `useSearchParams` + `URLSearchParams` | nuqs `useQueryState` | **CLOSED** |
| Source of truth | Dual (useState + URL) for sort/view | Single (URL via nuqs) | **CLOSED** |
| URL update functions | 4 separate manual builders | nuqs setters (shallow routing) | **CLOSED** |
| Sort persistence | `setSortField` + `setSortOrder` + `router.push` | `void setSortField()` + `void setSortOrder()` | **CLOSED** |
| Pagination | `goToPage` builds URLSearchParams | `void setCurrentPage(page <= 1 ? null : page)` | **CLOSED** |
| Clear filters | `router.push('/deals?status=active')` | Individual nuqs null setters | **CLOSED** |

## Contract Compliance
- No new client-count anti-patterns introduced
- No Promise.all introduced
- All changes are UI layout + URL state management only — no API behavior changes
- `useSearchParams` import fully removed from deals/page.tsx
- nuqs patterns match existing use-data-table.ts conventions

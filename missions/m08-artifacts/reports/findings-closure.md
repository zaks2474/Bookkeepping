# M08 Findings Closure

## F-23: Agent Activity stat cards stack vertically at 375px (Sev-3)

**Status:** CLOSED

**Root Cause:**
Stats grid used `grid gap-4 md:grid-cols-4` which defaults to single column below `md` (768px). At 375px, all 4 stat cards stacked vertically consuming ~400px of vertical space, pushing tabs and activity list below the fold.

**Fix Applied:**
- Changed stats grid to `grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4`
- Made StatCard compact at mobile: `p-3 md:p-4` padding, `text-xs md:text-sm truncate` for descriptions, `text-2xl md:text-3xl` for values

**Files Modified:**
- `apps/dashboard/src/app/agent/activity/page.tsx`

**Evidence:**
- Before: Stats consume full viewport width per card, 1x4 vertical stack
- After: Stats in 2x2 grid at 375px, compact card dimensions
- E2E: `agent-activity-mobile-density.spec.ts` — 5 tests, all pass

---

## F-14: Operator HQ stage labels truncate at 375px (Sev-2)

**Status:** CLOSED

**Root Cause:**
QuickStats used `grid grid-cols-4 gap-4 px-6 py-4` which forced 4 columns at all widths, causing label compression at 375px. PipelineOverview used `grid grid-cols-7 gap-4` which forced all 7 stage cards into a single row, causing severe badge text truncation at 375px.

**Fix Applied:**
- QuickStats: `grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 px-4 md:px-6`
- PipelineOverview: `grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-3 md:gap-4`

**Files Modified:**
- `apps/dashboard/src/components/operator-hq/QuickStats.tsx`
- `apps/dashboard/src/components/operator-hq/PipelineOverview.tsx`

**Evidence:**
- Before: Labels compressed/truncated at 375px
- After: Full labels readable at all breakpoints
- E2E: `hq-pipeline-legibility-and-controls.spec.ts` — 5 tests, all pass

---

## Summary

| Finding | Severity | Status | Tests |
|---------|----------|--------|-------|
| F-23 | Sev-3 | CLOSED | 5 E2E |
| F-14 | Sev-2 | CLOSED | 5 E2E |

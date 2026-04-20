# Findings Closure Report — M-09 Dashboard + Onboarding Polish
**Date:** 2026-02-11

## F-19 Closure (Sev-2): Dashboard Today & Next Up cards clip at 375px

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| Card width | `w-64` (256px fixed) | `w-56 sm:w-64` (224px mobile, 256px sm+) | **CLOSED** |
| Scroll affordance | ScrollBar present but invisible | Right-fade gradient overlay at mobile (`sm:hidden`) | **CLOSED** |
| Second card visibility | ~30% visible, clipped | ~40% visible with fade hint to scroll | **CLOSED** |

Cards accessible at 375px: 1/2 → **1/2 + visible scroll cue**
Cards accessible at 768px: 2/2 → **2/2** (no change)

## F-20 Closure (Sev-2): Pipeline count 0→N flash during load

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| Pipeline description during load | "0 active deals across 0 stages" | `<Skeleton />` placeholder (h-4 w-48) | **CLOSED** |
| All Deals description during load | "0 deals" | `<Skeleton />` placeholder (h-4 w-32) | **CLOSED** |
| Settled state | "9 active deals across 3 stages" | "9 active deals across 3 stages" (unchanged) | **CLOSED** |

Count flash eliminated: shows skeleton → real data with no intermediate zeros.

## F-17 Closure (Sev-2): Onboarding resume banner excessive space

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| Component | `<Alert>` with grid icon layout | Custom `<div>` with flex row | **CLOSED** |
| Text | "Welcome back! You were on step N of 6: Title" | "Step N/6: **Title**" with `truncate` | **CLOSED** |
| Layout at 1280px | ~150px height (text wraps in Alert) | ~45px single line | **CLOSED** |
| Layout at 375px | ~160px (text wraps + buttons wrap) | ~40px single line (text truncates) | **CLOSED** |
| Padding | Alert default padding | `px-3 py-2.5` compact | **CLOSED** |

Banner height: 150px → **45px** (70% reduction)

## F-18 Closure (Sev-2): Onboarding stepper labels hidden at 375px

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| Label CSS | `hidden sm:inline` (all labels) | Current step: `inline`, others: `hidden sm:inline` | **CLOSED** |
| Labels at 375px | 0/6 visible (icons only) | 1/6 visible (current step shows label) | **CLOSED** |
| Labels at 768px | 6/6 visible | 6/6 visible (no change) | **CLOSED** |
| Stepper margin | `mb-8` always | `mb-4 sm:mb-8` (reduced at mobile) | **CLOSED** |
| Stepper overflow | None | `overflow-x-auto` (safety valve) | **CLOSED** |

User context at 375px: none (icons only) → **knows current step name**

## Contract Compliance
- No new client-count anti-patterns introduced
- No Promise.all introduced
- Skeleton uses existing `<Skeleton>` component (already imported)
- All changes are UI layout only — no API behavior changes
- Alert import removed after component replacement (no dead imports)

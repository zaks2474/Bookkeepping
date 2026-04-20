# Boundary Snapshot — M-09 Dashboard + Onboarding Polish
**Date:** 2026-02-11
**Baseline from:** M-08 completion (post-M-07 deals/quarantine polish)

## Dashboard (/dashboard)

### 1280px (Desktop)
- **Today & Next Up**: 2 items visible (both Deal cards), horizontal strip with scroll area
- **Pipeline card**: "9 active deals across 3 stages" — inbound(6), screening(2), closing(1)
- **All Deals**: 8 deals listed with "View all →" link
- **Agent Activity**: Full text visible, 4 activity items, Ask Agent + View All buttons
- **Execution Inbox**: 0 items, tabs visible (All/Approvals/Ready/Failed/Quarantine)
- **Quarantine**: Status healthy, Pending 0
- **Alerts**: 1 alert (stale_deals — 2 deal(s) >7 days)
- **No clipping or overflow issues at 1280px**

### 768px (Tablet)
- **Today & Next Up**: 2 cards visible (full width with scroll)
- **Pipeline**: Full text visible, stage buttons wrap to 2 lines (closing on second row)
- **Agent Activity**: Text clipping — "Tool execution com...", "Tool execution star...", "Approval processin..."
- **Execution Inbox**: Partially visible, "Latest" dropdown clipped to right edge
- **Layout**: 2-column grid still active but tight

### 375px (Mobile) — F-19 VISIBLE
- **Today & Next Up**: First card fully visible, second card clipped at right edge (~30% visible)
- **No scroll affordance**: ScrollBar is present but not visually obvious at mobile
- **Pipeline**: Full text, stage buttons wrap normally
- **All Deals**: "View all" link aligned right, deal list renders cleanly
- **Below fold**: Agent Activity, Execution Inbox, Quarantine, Alerts all single-column

### F-20 Count Coherence
- **Initial load state**: "0 active deals across 0 stages" visible before data arrives
- **Settled state**: "9 active deals across 3 stages"
- **Source**: `pipelineData?.total_active ?? deals.length` — falls back to `deals.length` (0) when pipelineData is null
- **Stage count**: `STAGE_ORDER.filter(s => stageCounts[s] > 0).length` — 0 when stageCounts all zero
- **TodayNextUpStrip**: Hidden during loading (`!loading` guard on line 177)

## Onboarding (/onboarding)

### 1280px (Desktop)
- **Stepper**: 6 steps with icons + labels, horizontal layout
- **Label clipping**: "All Set!" partially clipped at right edge
- **Resume banner**: Full width Alert with text + 3 buttons (Resume, Start Fresh, X dismiss)
- **Banner height**: ~150px — significant vertical space before step content
- **Step content**: Welcome page with 4 feature cards in 2x2 grid, "What we'll set up" list

### 768px (Tablet)
- **Stepper labels**: Wrapping to 2 lines ("Your Profile", "Connect Email", "Meet Your Agent")
- **"All Set!"**: Clipped at right edge
- **Resume banner**: Same layout, text wraps more aggressively (~180px height)
- **Feature cards**: 2-column grid still works

### 375px (Mobile) — F-17, F-18 VISIBLE
- **F-18 Stepper labels**: Completely hidden — only 6 icon circles visible with no text context
- **Stepper class**: `hidden sm:inline` on label spans — disappears below 640px
- **F-17 Resume banner**: Text wraps extensively (~160px height), buttons wrap
- **Banner layout**: `flex items-center justify-between` doesn't adapt to vertical stacking
- **Content below banner starts ~350px from top** — half the viewport is stepper+banner

## Files Under Modification

| File | Findings | Lines |
|------|----------|-------|
| `apps/dashboard/src/components/dashboard/TodayNextUpStrip.tsx` | F-19 | 222 |
| `apps/dashboard/src/app/dashboard/page.tsx` | F-20 | 425 |
| `apps/dashboard/src/components/onboarding/OnboardingWizard.tsx` | F-17, F-18 | 406 |

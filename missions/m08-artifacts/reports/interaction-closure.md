# M08 Interaction Closure Matrix

## /agent/activity

| Control | 375px | 768px | 1280px | Status |
|---------|-------|-------|--------|--------|
| Search input | visible, full width | visible | visible | real |
| Tab: All Activity | visible | visible | visible | real |
| Tab: Approvals | visible | visible | visible | real |
| Tab: Errors | visible | visible | visible | real |
| Tab: Completions | visible | visible | visible | real |
| Tab: System | visible | visible | visible | real |
| Refresh button | visible, within viewport | visible | visible | real |
| Status badge (Idle/Working) | visible | visible | visible | real |
| Stat: Total Runs | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Stat: Completed | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Stat: Failed | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Stat: Avg Duration | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Recent Runs list | visible below stats | visible | visible | real |
| Run detail panel | scroll-to on select | visible | visible | real |

### F-23 Resolution
- **Before:** Stats stacked 1x4 at 375px, pushing tabs and activity list below the fold.
- **After:** Stats in compact 2x2 grid at 375px with reduced padding (`p-3 md:p-4`, `text-2xl md:text-3xl`). Tabs and activity list are visible above the fold.

---

## /hq (Operator HQ)

| Control | 375px | 768px | 1280px | Status |
|---------|-------|-------|--------|--------|
| Stat: Active Deals | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Stat: Pending Approvals | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Stat: Quarantine | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Stat: Events (24h) | visible, 2x2 grid | visible, 4-col | visible, 4-col | real |
| Tab: Pipeline | visible | visible | visible | real |
| Tab: Approvals | visible | visible | visible | real |
| Tab: Activity | visible | visible | visible | real |
| Refresh button | visible | visible | visible | real |
| Stage: Inbound | visible, 3-col grid | visible, 4-col | visible, 7-col | real |
| Stage: Screening | visible, 3-col grid | visible, 4-col | visible, 7-col | real |
| Stage: Qualified | visible, 3-col grid | visible, 4-col | visible, 7-col | real |
| Stage: Diligence | visible (row 2) | visible, 4-col | visible, 7-col | real |
| Stage: Closing | visible (row 2) | visible (row 2) | visible, 7-col | real |
| Stage: Portfolio | visible (row 2) | visible (row 2) | visible, 7-col | real |
| Pipeline Flow bar | visible | visible | visible | real |
| View All Deals button | visible | visible | visible | real |
| Review Quarantine button | visible | visible | visible | real |

### F-14 Resolution
- **Before:** QuickStats in 4-col grid at 375px caused label truncation. Pipeline stages in 7-col grid caused badge text to clip.
- **After:** QuickStats uses `grid-cols-2 md:grid-cols-4` with reduced gap/padding. Pipeline stages use `grid-cols-3 sm:grid-cols-4 lg:grid-cols-7` for progressive disclosure. All labels remain fully readable.

---

## Coverage Summary
- **Total controls mapped:** 31
- **Real:** 31
- **Degraded:** 0
- **Hidden:** 0
- **Coverage:** 100%

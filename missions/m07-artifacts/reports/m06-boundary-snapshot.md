# M-06 Boundary Snapshot — M-07 Baseline
**Date:** 2026-02-11
**Prior Mission:** M-06 (not yet executed — M-05 was last)
**Current State:** Post-M-05, pre-M-07

## Git State
- Monorepo has uncommitted changes from prior missions (M-01 through M-05)
- Dashboard running on :3003 (bare Next.js)
- Backend running on :8091 (Docker)

## Pages Under Scope

### /quarantine (quarantine/page.tsx — 790 lines)
- Layout: Side-by-side flex — Queue card (`w-full md:w-[420px]`) + Preview/Decision card (`flex-1`)
- At 375px: Only Queue card visible; preview/decision panel completely hidden (F-13 CONFIRMED)
- At 768px: Both panels visible but right panel clipped — Approve button partially cut off, Reject reason label truncated
- At 1280px: Full layout, all controls visible and functional
- Controls: Clear, Reject, Approve buttons + Operator input + Reject reason input
- Queue: 0 items at time of capture

### /deals (deals/page.tsx — 696 lines)
- Layout: Filter bar (search + stage + status dropdowns) + Table/Board view toggle + Paginated table
- At 375px: Table overflows — only Deal Name + partial Stage badge visible (F-21 CONFIRMED)
- At 768px: All columns visible but tight; filter dropdowns stacked
- At 1280px: Full table layout, all 7 columns visible
- View modes: Table (default) and Board (Kanban)
- Data: 9 deals loaded (active status filter default)

## Responsive Issues Confirmed
| Finding | Page | Severity | Status |
|---------|------|----------|--------|
| F-13 | /quarantine | Sev-2 | Preview/decision panel hidden at 375px |
| F-21 | /deals | Sev-2 | Table overflow at 375px — Broker/Priority/Last Update/Delete clipped |

## Additional Observations
- Refresh button text clipped at 375px on deals page header
- Filter dropdowns at 375px stack vertically (acceptable)
- Board view not tested at mobile (out of F-21 scope but may benefit from fixes)

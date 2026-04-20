# Dashboard Count Semantics Baseline — M-09
**Date:** 2026-02-11

## F-20: Pipeline Count 0→N Flash

### Current Behavior
1. Page loads → `loading = true` → Skeleton shown for Pipeline card
2. `fetchData('initial')` fires `Promise.allSettled` with 6 API calls
3. All state is `[]` or `null` during fetch
4. `loading` set to `false` after all settle → real content renders
5. **Pipeline description** renders: `{pipelineData?.total_active ?? deals.length} active deals across {STAGE_ORDER.filter(s => stageCounts[s] > 0).length} stages`

### The Problem
- When `loading = false` but `pipelineData` hasn't propagated yet (or settled as rejected):
  - `pipelineData?.total_active` → `undefined`
  - Fallback: `deals.length` → could be 0 if deals also failed
  - Stage count: `STAGE_ORDER.filter(...)` → 0 (all stageCounts are 0)
- Result: **"0 active deals across 0 stages"** briefly visible before data populates

### Source Code Reference
- `apps/dashboard/src/app/dashboard/page.tsx:209`
- Fallback chain: `pipelineData?.total_active ?? deals.length`
- Stage count: `STAGE_ORDER.filter(s => stageCounts[s] > 0).length`

### Related Loading Guards
- TodayNextUpStrip: `{!loading && <TodayNextUpStrip ... />}` (line 177) — properly guarded
- Pipeline card: No loading guard on description text — shows stale/zero counts
- Skeleton: Only shown inside `<CardContent>` when `loading` is true (line 224)
- CardHeader (with description) always renders — no skeleton substitute for count text

### Fix Strategy
The pipeline description should show a skeleton/placeholder while `loading` is true,
or use a dedicated loading state for the count text. Options:
1. **Inline skeleton**: Replace count text with `<Skeleton />` when `loading`
2. **Hide count during load**: Only show count text when `pipelineData` is non-null
3. **Use pipelineData as primary gate**: Show "Loading..." text until pipelineData arrives

### Current State Values (settled)
| Metric | Value |
|--------|-------|
| pipelineData.total_active | 9 |
| deals.length | 8 (different due to pagination/filtering) |
| Active stages | 3 (inbound, screening, closing) |
| Stage counts | inbound: 6, screening: 2, closing: 1 |

### Note on deals.length Discrepancy
`deals.length` (8) differs from `pipelineData.total_active` (9) because
deals are fetched with `{ status: 'active' }` which may paginate, while
pipeline total_active is a server-computed aggregate. This is correct behavior
per DEAL-INTEGRITY-UNIFIED L3 (server-side counts only).

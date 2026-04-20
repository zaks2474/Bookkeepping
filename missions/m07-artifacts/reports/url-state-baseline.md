# URL State Baseline — deals/page.tsx
**Date:** 2026-02-11
**Purpose:** Document all manual URLSearchParams touchpoints for nuqs convergence

## Current Implementation (Manual URLSearchParams)

### Parameters Read from URL
| Parameter | Variable | Default | Line |
|-----------|----------|---------|------|
| `view` | `initialView` / `viewMode` | `'table'` | 84-85 |
| `stage` | `stageFilterRaw` / `stageFilter` | `''` (→ ALL_FILTER) | 88, 93 |
| `status` | `statusFilterRaw` / `statusFilter` | `'active'` | 89, 94 |
| `q` | `searchQuery` | `''` | 90 |
| `sortBy` | `sortFieldRaw` / `sortField` | `'days_since_update'` | 97, 99 |
| `sortOrder` | `sortOrderRaw` / `sortOrder` | `'asc'` | 98, 100 |
| `page` | `currentPage` | `1` | 104 |

### URL Update Functions (all use `new URLSearchParams` + `router.push`)
| Function | Lines | Parameters Touched | Notes |
|----------|-------|-------------------|-------|
| `updateFilter(key, value)` | 129-140 | stage, status (dynamic) | Deletes `page` on filter change |
| `updateViewMode(mode)` | 143-152 | view | Deletes when 'table' (default) |
| `toggleSort(field)` | 204-217 | sortBy, sortOrder | Also updates local state |
| `goToPage(page)` | 224-232 | page | Deletes when page=1 |

### Anti-Patterns Found
1. **Dual state**: `sortField`/`sortOrder` stored in BOTH `useState` AND URL — source of truth conflict
2. **Dual state**: `viewMode` stored in BOTH `useState` AND URL
3. **No shallow routing**: Every `router.push` triggers a full navigation cycle
4. **Inconsistent defaults**: `searchQuery` read from URL but never written back (client-side filter only)
5. **Manual param building**: 4 separate functions all construct URLSearchParams from scratch

## nuqs Convergence Plan
Replace all 7 URL parameters with `useQueryStates` from nuqs:
- Single source of truth (URL = state)
- Shallow routing by default (no page reload)
- Type-safe parsers (`parseAsString`, `parseAsInteger`)
- Automatic default handling (no sentinel values needed)

### Existing nuqs Patterns (reference)
- `apps/dashboard/src/hooks/use-data-table.ts` — uses `useQueryState`, `useQueryStates`, `parseAsInteger`, `parseAsString`
- `apps/dashboard/src/app/layout.tsx` — `NuqsAdapter` configured at root
- nuqs v2.4.1 installed

# SCHEMA-ALIGN-001 — Final Report

**Codename:** SCHEMA-ALIGN-001
**Date:** 2026-02-04
**Executor:** Claude Opus 4.5
**Mode:** ZodError Eradication
**Status:** COMPLETE

---

## Executive Summary

This mission addressed schema mismatches between dashboard Zod schemas and backend API responses. The primary issue was `ActionMetricsSchema` which expected a completely different field structure than what the backend returns.

### Results

| Category | Count |
|----------|-------|
| FIXED | 1 (ActionMetricsSchema + UI) |
| VERIFIED | 6 (all major endpoints) |
| NO_ERROR | All other schemas (using .passthrough() and .nullable().optional()) |

---

## Finding Details

### Primary Issue: ActionMetricsSchema Mismatch

**Root Cause:** The Zod schema expected a different field structure than the backend returns.

**Before (Incorrect):**
```typescript
const ActionMetricsSchema = z.object({
  queue_lengths: z.record(z.number()),
  avg_duration_by_type: z.record(...),
  success_rate_24h: z.number(),
  total_24h: z.number(),
  completed_24h: z.number(),
  failed_24h: z.number(),
  error_breakdown: z.array(...),
});
```

**Backend Actually Returns:**
```json
{
  "total_actions": 0,
  "pending_approval": 0,
  "completed_today": 0,
  "failed_today": 0,
  "avg_approval_time_seconds": null,
  "avg_execution_time_seconds": null,
  "by_capability": {},
  "version": "1.0.0"
}
```

**Fix Applied:**
1. Updated `ActionMetricsSchema` to match backend response
2. Updated `ActionMetrics` interface
3. Updated `actions/page.tsx` UI to use correct field names:
   - `queue_lengths.PENDING_APPROVAL` → `pending_approval`
   - `queue_lengths.PROCESSING` → Derived from statusCounts
   - `metrics.total_24h / success_rate_24h` → Computed from `completed_today / (completed_today + failed_today)`
   - `metrics.failed_24h` → `failed_today`

---

## Files Changed

### Modified Files
- `apps/dashboard/src/lib/api.ts`
  - Line 1402-1410: Updated `ActionMetrics` interface
  - Line 1497-1508: Updated `ActionMetricsSchema` Zod schema

- `apps/dashboard/src/app/actions/page.tsx`
  - Line 702: Changed from `queue_lengths.PENDING_APPROVAL` to `pending_approval`
  - Line 722: Changed from `queue_lengths.PROCESSING` to statusCounts fallback
  - Line 742-744: Changed success rate calculation
  - Line 764: Changed from `failed_24h` to `failed_today`

---

## Verification Status

| Endpoint | Status | Notes |
|----------|--------|-------|
| /api/deals | ✓ PASS | Returns deal data correctly |
| /api/actions | ✓ PASS | Returns actions (empty array expected) |
| /api/actions/metrics | ✓ PASS | Schema now validates correctly |
| /api/actions/capabilities | ✓ PASS | Returns capabilities |
| /api/quarantine | ✓ PASS | Returns quarantine items |
| /api/pipeline | ✓ PASS | Returns pipeline data |

---

## Why Other Schemas Don't Cause ZodErrors

The dashboard already had defensive patterns in place:

1. **`.passthrough()`** on most schemas - Allows extra fields from backend without failing
2. **`.nullable().optional()`** on most fields - Handles missing/null values gracefully
3. **`safeParse()` with fallbacks** - Returns empty arrays/null instead of throwing
4. **Transformation layers** (e.g., `/api/pipeline` route) - Transforms backend responses to expected shape

---

## Regression Guard Recommendations

1. **Add schema tests** - Create a test file that validates actual backend responses against Zod schemas
2. **Add CI check** - Run schema validation as part of dashboard build
3. **Document schema contract** - Keep Zod schemas as source of truth, update when backend changes

---

## Evidence Artifacts

1. `evidence/phase0_mismatch_table.md` - Initial mismatch analysis
2. `evidence/after/endpoint_verification.txt` - Verification results

---

*End of SCHEMA-ALIGN-001 Report*
*Executor: Claude Opus 4.5*
*Generated: 2026-02-04*

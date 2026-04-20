# SCHEMA-ALIGN-001 — Phase 0: Mismatch Table

Generated: 2026-02-04

## Critical Mismatches (ZodError Causing)

| # | Endpoint | Field | Zod Expects | Backend Returns | Impact |
|---|----------|-------|-------------|-----------------|--------|
| 1 | /api/actions/metrics | `queue_lengths` | `Record<string, number>` | NOT PRESENT | ZodError - fails validation |
| 2 | /api/actions/metrics | `avg_duration_by_type` | `Record<{avg_seconds, count}>` | NOT PRESENT | ZodError |
| 3 | /api/actions/metrics | `success_rate_24h` | `number` | NOT PRESENT | ZodError |
| 4 | /api/actions/metrics | `total_24h` | `number` | NOT PRESENT | ZodError |
| 5 | /api/actions/metrics | `completed_24h` | `number` | NOT PRESENT | ZodError |
| 6 | /api/actions/metrics | `failed_24h` | `number` | NOT PRESENT | ZodError |
| 7 | /api/actions/metrics | `error_breakdown` | `[{error, count}]` | NOT PRESENT | ZodError |
| 8 | /api/actions/metrics | `total_actions` | NOT EXPECTED | `0` | Extra field (passthrough saves) |
| 9 | /api/actions/metrics | `pending_approval` | NOT EXPECTED | `0` | Extra field |
| 10 | /api/actions/metrics | `completed_today` | NOT EXPECTED | `0` | Extra field |
| 11 | /api/actions/metrics | `failed_today` | NOT EXPECTED | `0` | Extra field |
| 12 | /api/actions/metrics | `avg_approval_time_seconds` | NOT EXPECTED | `null` | Extra field |
| 13 | /api/actions/metrics | `avg_execution_time_seconds` | NOT EXPECTED | `null` | Extra field |
| 14 | /api/actions/metrics | `by_capability` | NOT EXPECTED | `{}` | Extra field |
| 15 | /api/actions/metrics | `version` | NOT EXPECTED | `"1.0.0"` | Extra field |
| 16 | /api/pipeline | `total_active` | `number` (required) | NOT PRESENT | ZodError |
| 17 | /api/pipeline | `stages` | `Record<PipelineStageSchema>` | `{ archived: 3, ... }` (numbers) | ZodError - type mismatch |

## Backend Response Samples

### /api/actions/metrics
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

### /api/deals/stages/summary (aka /api/pipeline)
```json
{
  "stages": {
    "archived": 3,
    "diligence": 1,
    "inbound": 11,
    "loi": 1,
    "qualified": 1,
    "screening": 4
  },
  "available_stages": [...]
}
```

## Analysis

1. **ActionMetricsSchema** - Complete field name mismatch between frontend expectation and backend reality
2. **PipelineResponseSchema** - Structural mismatch: expects objects with {count, deals[], avg_age}, gets plain numbers
3. **QuarantineItemSchema** - Overly flexible with many optional fields, but passthrough() handles extras

## Next Step: Fix Zod schemas to match backend responses

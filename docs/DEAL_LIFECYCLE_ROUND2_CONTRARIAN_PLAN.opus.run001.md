# ROUND2-CONTRARIAN-V2 Strategic Audit Report

**Date**: 2026-02-04T16:30:00Z
**Auditor**: Claude Code (Opus 4.5)
**Repo Revision**: 3173c36f714f13524f3d81375483484887a6ac99
**Mission**: Zero-Trust 5-Layer Contract Audit

---

## Executive Summary

**VERDICT: LAYER 4-5 CONTRACT DRIFT DETECTED**

| Layer | Description | Score (0-10) | Status |
|-------|-------------|--------------|--------|
| Layer 1 | PostgreSQL DDL | 8 | PASS |
| Layer 2 | SQL Queries | 7 | PASS (with caveats) |
| Layer 3 | Pydantic Models | 6 | PARTIAL |
| Layer 4 | Zod Schemas | 4 | **CRITICAL DRIFT** |
| Layer 5 | React Components | 5 | PARTIAL |

**Total Score: 30/50 (60%)**

---

## Layer Analysis

### Layer 1: PostgreSQL DDL (Score: 8/10)

**Verified in QA-VERIFICATION-006**:
- zakops.deals is sole source of truth
- Split-brain risk eliminated
- Stage taxonomy enforced at DB level (default: 'inbound')

**Deductions**:
- -1: No unique constraint on `canonical_name` (ZK-ISSUE-0012)
- -1: sys.path hack in diligence_request_docs.py (ZK-ISSUE-0013)

### Layer 2: SQL Queries (Score: 7/10)

**Verified**:
- All queries use parameterized statements
- No raw string interpolation found
- Proper JOIN usage

**Deductions**:
- -2: Some queries return more fields than Pydantic models expose
- -1: Inconsistent field naming (snake_case vs camelCase in some places)

### Layer 3: Pydantic Models (Score: 6/10)

**Location**: `/home/zaks/zakops-backend/src/api/orchestration/main.py`

**Critical Issue - ActionResponse is INCOMPLETE**:

```python
# Backend ActionResponse (main.py:174-191)
class ActionResponse(BaseModel):
    action_id: str
    deal_id: str | None
    capability_id: str
    action_type: str
    title: str
    summary: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    risk_level: str
    requires_human_review: bool
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    deal_name: str | None = None
    deal_stage: str | None = None
```

**Missing from ActionResponse but in actions table/ActionPayload**:
- `started_at`
- `completed_at`
- `duration_seconds`/`duration`
- `created_by`
- `source`
- `idempotency_key`
- `retry_count`, `max_retries`, `next_retry_at`
- `parent_action_id`, `root_action_id`, `chain_depth`
- `audit_trail`
- `artifacts`
- `error_message`

**Deductions**:
- -3: ActionResponse missing 15+ fields present in actual data model
- -1: QuarantineResponse missing 11+ fields present in Zod

### Layer 4: Zod Schemas (Score: 4/10) **CRITICAL**

**Location**: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts`

**47 Zod schemas found, ALL use `.passthrough()`** - defensive pattern indicating known drift.

#### Critical Mismatch 1: ActionStatusSchema

| Zod | Pydantic (engine/models.py) |
|-----|----------------------------|
| PENDING_APPROVAL | PENDING_APPROVAL |
| **QUEUED** | ❌ NOT PRESENT |
| READY | READY |
| **RUNNING** | **PROCESSING** (different name!) |
| COMPLETED | COMPLETED |
| FAILED | FAILED |
| CANCELLED | CANCELLED |
| **REJECTED** | ❌ NOT PRESENT |

**Impact**: Status display will fail for PROCESSING actions (backend says PROCESSING, Zod expects RUNNING).

#### Critical Mismatch 2: ActionSourceSchema

| Zod | Pydantic |
|-----|----------|
| chat | chat |
| ui | ui |
| system | system |
| **agent** | ❌ NOT PRESENT |
| **api** | ❌ NOT PRESENT |

#### Critical Mismatch 3: ActionSchema field bloat

Zod ActionSchema expects 28 fields:
```typescript
action_id, deal_id, capability_id, action_type, title, summary, status,
created_at, updated_at, started_at, completed_at, scheduled_for,
duration_seconds, created_by, source, risk_level, requires_human_review,
idempotency_key, inputs, outputs, retry_count, max_retries, next_retry_at,
parent_action_id, root_action_id, chain_depth, audit_trail, artifacts,
error_message, deal_name, deal_stage
```

Backend ActionResponse returns 15 fields.

**13 fields will be undefined/missing on every API response.**

#### Critical Mismatch 4: QuarantineItemSchema field bloat

Zod expects fields backend doesn't return:
- `action_id`, `thread_id`, `links`, `quarantine_dir`
- `email_content_path`, `triage_summary_path`
- `processed_at`, `processed_by`, `processing_result`
- `created_deal_id`, `updated_at`

**Deductions**:
- -3: ActionStatus enum mismatch (RUNNING vs PROCESSING)
- -2: ActionSource enum mismatch (agent/api not in backend)
- -1: 13+ phantom fields in ActionSchema

### Layer 5: React Components (Score: 5/10)

**24 safeParse calls found** - validation is happening.

**Critical Pattern**:
```typescript
// From api.ts:627-631
const parsed = ActionsResponseSchema.safeParse(data);
if (!parsed.success) {
  console.error('Invalid actions response:', parsed.error);
  return [];  // SILENT FAILURE - returns empty array!
}
```

**Impact**: When Zod validation fails (which it will due to Layer 4 drift), the UI shows **empty data** instead of an error. Users see nothing and don't know why.

**Files with silent failures**:
- `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (19 instances)

**Deductions**:
- -3: Silent failures on Zod validation errors (returns [])
- -2: No user-visible error messages for schema mismatches

---

## Upgrade Register

### ZK-UPG-0001: Fix ActionStatus Enum Mismatch (P0)

**Layer**: 3-4
**Files**:
- `/home/zaks/zakops-backend/src/actions/engine/models.py`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts`

**Action**: Align RUNNING/PROCESSING naming. Either:
1. Backend uses RUNNING (Zod wins)
2. Zod uses PROCESSING (Backend wins)

### ZK-UPG-0002: Trim ActionSchema to Reality (P1)

**Layer**: 4
**File**: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts`

**Action**: Remove 13 phantom fields from ActionSchema that backend never returns:
- `started_at`, `completed_at`, `scheduled_for`, `duration_seconds`
- `created_by`, `source`, `idempotency_key`
- `retry_count`, `max_retries`, `next_retry_at`
- `parent_action_id`, `root_action_id`, `chain_depth`
- `audit_trail`, `artifacts`, `error_message`

OR expand ActionResponse Pydantic model to include these fields.

### ZK-UPG-0003: Trim QuarantineItemSchema (P1)

**Layer**: 4
**File**: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts`

**Action**: Remove 11 phantom fields from QuarantineItemSchema.

### ZK-UPG-0004: Replace Silent Failures with User Errors (P1)

**Layer**: 5
**File**: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts`

**Action**: Instead of returning `[]` on safeParse failure, throw a user-visible error or show a toast notification.

### ZK-UPG-0005: Add ActionSource Values to Backend (P2)

**Layer**: 3
**File**: `/home/zaks/zakops-backend/src/actions/engine/models.py`

**Action**: Add `agent` and `api` to ActionSource literal type.

### ZK-UPG-0006: Remove .passthrough() Crutch (P2)

**Layer**: 4
**File**: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts`

**Action**: Once schemas are aligned, remove `.passthrough()` from all schemas to get strict validation.

### ZK-UPG-0007: Add canonical_name Unique Constraint (P2)

**Layer**: 1
**File**: New migration

**Action**: `ALTER TABLE deals ADD CONSTRAINT deals_canonical_name_unique UNIQUE (canonical_name);`

### ZK-UPG-0008: Remove sys.path Hack (P3)

**Layer**: 2
**File**: `/home/zaks/zakops-backend/src/api/diligence_request_docs.py`

**Action**: Use proper relative imports instead of sys.path manipulation.

---

## Evidence Summary

### Schema Inventory

| Location | Type | Count |
|----------|------|-------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts` | Zod | 47 |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/schemas/approval.ts` | Zod | 7 |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Pydantic | 12 |
| `/home/zaks/zakops-backend/src/actions/engine/models.py` | Pydantic | 8 |
| `/home/zaks/zakops-backend/src/api/orchestration/routers/*.py` | Pydantic | 25+ |

### safeParse Usage

| File | Count | Failure Behavior |
|------|-------|------------------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | 19 | Returns [] |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/parsers.ts` | 2 | Returns null |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/schemas/approval.ts` | 2 | Returns null |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/storage-utils.ts` | 1 | Returns defaultValue |

---

## Contract-Audit-V1 / QA-CA-V1 Status

These were never executed. This Round-2 audit fulfills their intent:

| Original Task | Status | Evidence |
|---------------|--------|----------|
| CA-V1: Compare Zod vs Pydantic | **EXECUTED** | See Layer 4 analysis above |
| QA-CA-V1: Verify no ZodErrors | **BLOCKED** | Requires browser console capture |

**Recommendation**: Run dashboard in browser, open DevTools Console, interact with Actions/Quarantine pages, capture any ZodError messages.

---

## Conclusion

**Layers 1-3 are stable** but **Layers 4-5 have significant contract drift** that was masked by:
1. `.passthrough()` allowing unknown fields
2. Silent `return []` on validation failures

The dashboard is likely showing empty data in some views due to Zod validation failures that are logged to console but not surfaced to users.

**Priority Order**:
1. ZK-UPG-0001 (P0): Fix ActionStatus enum mismatch
2. ZK-UPG-0002 (P1): Trim ActionSchema
3. ZK-UPG-0004 (P1): Replace silent failures
4. ZK-UPG-0003 (P1): Trim QuarantineItemSchema
5. ZK-UPG-0005-0008 (P2-P3): Lower priority fixes

---

*Generated by ROUND2-CONTRARIAN-V2 audit*
*Auditor: Claude Code (Opus 4.5)*
*Run ID: opus.run001*
*Timestamp: 2026-02-04T16:30:00Z*

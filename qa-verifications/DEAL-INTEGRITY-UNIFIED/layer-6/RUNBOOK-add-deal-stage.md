# Runbook: Adding a New Deal Stage

| Field       | Value                          |
|-------------|--------------------------------|
| Date        | 2026-02-08                     |
| Mission     | DEAL-INTEGRITY-UNIFIED         |
| Layer       | 6 — Governance                 |
| Authority   | ADR-003                        |

## Prerequisites

- Access to `zakops-agent-api` repo (dashboard + contracts)
- Access to `zakops-backend` repo (API + DB migrations)
- Canonical database running on port 5432 (see ADR-002)

## Procedure

### Step 1: Update `execution-contracts.ts`

**File:** `apps/dashboard/src/types/execution-contracts.ts`

1. Add the new stage to `PIPELINE_STAGES` or `TERMINAL_STAGES` array in the
   correct position (order determines display order).
2. Add an entry to `DEAL_STAGE_LABELS` with the human-readable label.
3. Add an entry to `DEAL_STAGE_BG_COLORS` with the card/badge background color.
4. Add an entry to `DEAL_STAGE_COLUMN_COLORS` with the pipeline column color.
5. Verify `ALL_STAGES_ORDERED` automatically includes the new stage (it is
   derived from `[...PIPELINE_STAGES, ...TERMINAL_STAGES]`).

```typescript
// Example: Adding "Due Diligence" after "Proposal"
export const PIPELINE_STAGES = [
  "Lead",
  "Qualified",
  "Discovery",
  "Proposal",
  "Due Diligence",   // <-- NEW
  "Negotiation",
  "Contract Sent",
] as const;
```

### Step 2: Update `types/api.ts` DealStage Union Type

**File:** `apps/dashboard/src/types/api.ts`

Add the new stage string to the `DealStage` union type:

```typescript
export type DealStage =
  | "Lead"
  | "Qualified"
  | "Discovery"
  | "Proposal"
  | "Due Diligence"   // <-- NEW
  | "Negotiation"
  | "Contract Sent"
  | "Won"
  | "Lost";
```

### Step 3: Update Backend DB CHECK Constraint

**File:** New Alembic migration in `zakops-backend/alembic/versions/`

Update the `chk_deal_lifecycle` CHECK constraint on the `deals` table:

```sql
ALTER TABLE deals DROP CONSTRAINT IF EXISTS chk_deal_lifecycle;
ALTER TABLE deals ADD CONSTRAINT chk_deal_lifecycle CHECK (
  stage IN (
    'Lead', 'Qualified', 'Discovery', 'Proposal',
    'Due Diligence',  -- NEW
    'Negotiation', 'Contract Sent', 'Won', 'Lost'
  )
);
```

Create this as a proper Alembic migration so it is versioned and reversible.

### Step 4: Update `transition_deal_state()` Function

**File:** `zakops-backend/app/services/deal_lifecycle.py` (or equivalent)

Define which stages can transition TO the new stage and which stages the new
stage can transition TO:

```python
VALID_TRANSITIONS = {
    # ...existing...
    "Proposal": ["Due Diligence", "Negotiation", "Lost"],     # updated
    "Due Diligence": ["Negotiation", "Proposal", "Lost"],     # NEW
    "Negotiation": ["Contract Sent", "Due Diligence", "Lost"], # updated
    # ...
}
```

### Step 5: Update `enforce_deal_lifecycle()` Trigger

If there is a PostgreSQL trigger function `enforce_deal_lifecycle()` that
validates transitions at the DB level, update its transition map to match
Step 4.

### Step 6: Run `make sync-all-types`

```bash
cd /home/zaks/zakops-agent-api && make sync-all-types
```

This verifies that the frontend type definitions match the backend OpenAPI
contract. Fix any errors before proceeding.

### Step 7: Run `make validate-local`

```bash
cd /home/zaks/zakops-agent-api && make validate-local
```

This runs:
- TypeScript compilation (`tsc --noEmit`)
- ESLint checks
- Unit tests

All must pass.

### Step 8: Verify Dashboard Renders New Stage

Start the dashboard and manually verify:

```bash
npm run dev
```

Check these pages:
- **Pipeline board** (`/deals`): New column appears in correct position with
  correct color.
- **Deal detail page**: Stage dropdown includes new stage.
- **Deal create form**: New stage available if applicable.
- **Reports/analytics**: Any stage-based charts include the new stage.

### Step 9: Update Tests

- **Backend**: Add/update tests for `transition_deal_state()` covering
  transitions to and from the new stage.
- **Frontend**: Update any snapshot tests or integration tests that assert on
  stage lists.
- **Smoke tests**: Run `bash /home/zaks/zakops-backend/scripts/qa_smoke.sh` to
  verify end-to-end.

## Rollback

To remove a stage:
1. Migrate any deals currently in that stage to an adjacent stage.
2. Reverse all steps above (remove from arrays, types, constraints, transitions).
3. Run `make sync-all-types && make validate-local`.

## Verification Checklist

- [ ] `execution-contracts.ts` updated (arrays, labels, colors)
- [ ] `types/api.ts` DealStage union updated
- [ ] Alembic migration for CHECK constraint created and applied
- [ ] `transition_deal_state()` updated with valid transitions
- [ ] `enforce_deal_lifecycle()` trigger updated (if applicable)
- [ ] `make sync-all-types` passes
- [ ] `make validate-local` passes
- [ ] Dashboard renders new stage correctly on all pages
- [ ] Backend and frontend tests updated and passing

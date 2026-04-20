# ADR-001: Deal Lifecycle State Machine Design

## Status
ACCEPTED (2026-02-08)

## Context
The ZakOps deals table uses three fields to represent lifecycle state: `status`, `stage`, and `deleted`. These fields were never formally coordinated, leading to impossible states:
- 6 deals with `stage='archived'` but `status='active'` (DI-ISSUE-001)
- 12 deals with `deleted=true` but `status='active'`

Three options were considered:
- **Option A**: Retain three-field system, add centralized FSM function + DB constraints
- **Option B**: Merge status into stage only
- **Option C**: Single `lifecycle_state` ENUM column replacing all three fields

## Decision
**Option A with full FSM infrastructure.** Rationale:
- Delivers correctness immediately with minimal migration risk
- The FSM infrastructure (transition function + trigger + constraints) solves the coordination problem by design
- Future migration to Option C requires changing only `transition_deal_state()` — all callers already go through it

## Implementation
1. **`transition_deal_state(deal_id, target_stage, actor, reason)`** — centralized PL/pgSQL function
   - Uses `SELECT ... FOR UPDATE` for concurrency safety (Q8)
   - Automatically derives `status` from `stage` (archived/junk → 'archived', else → 'active')
   - Appends to `audit_trail` JSONB column
   - Records `deal_events` entry
   - Idempotent: returns current state if already in target

2. **CHECK constraint `chk_deal_lifecycle`** — rejects impossible state combinations at DB level
3. **Trigger `enforce_deal_lifecycle_trigger`** — auto-corrects on INSERT/UPDATE (belt-and-suspenders)
4. **`audit_trail` JSONB column** — per-deal lifecycle history

## Valid States
| status | stage | deleted | Description |
|--------|-------|---------|-------------|
| active | inbound..portfolio | false | Normal active deal |
| archived | archived, junk | false | Terminal deal |
| deleted | any | true | Soft-deleted |

## Path to Option C
When ready, the migration is:
1. Add `lifecycle_state` ENUM column
2. Update `transition_deal_state()` to write to it
3. Backfill from existing fields
4. Update queries to use new column
5. Drop `status`, `deleted` columns

No callers of `transition_deal_state()` need to change.

## Consequences
- All state-changing code SHOULD use `transition_deal_state()`
- Raw UPDATEs are caught by the trigger (auto-corrected)
- The CHECK constraint is the final safety net
- Adding a new terminal stage requires updating the function, trigger, and constraint

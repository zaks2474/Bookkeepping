# Change Protocol — Deal State Modifications

| Field       | Value                          |
|-------------|--------------------------------|
| Date        | 2026-02-08                     |
| Mission     | DEAL-INTEGRITY-UNIFIED         |
| Layer       | 6 — Governance                 |
| Authority   | ADR-002, ADR-003               |

## Purpose

This protocol defines the mandatory PR checklist that activates when any
deal-state-related file is modified. It ensures that changes to the deal
lifecycle remain consistent across the full stack.

---

## Trigger Files

A PR **must** follow this protocol if it modifies any of the following files:

| File / Pattern                                              | Layer    |
|-------------------------------------------------------------|----------|
| `zakops-backend/app/services/deal_lifecycle.py`             | Backend  |
| — specifically `transition_deal_state()` function           |          |
| `zakops-backend/alembic/versions/*` (deals table changes)   | Backend  |
| — specifically `chk_deal_lifecycle` CHECK constraint        |          |
| `zakops-backend/app/api/routes/deals.py`                    | Backend  |
| — specifically archive/restore endpoints                    |          |
| `apps/dashboard/src/types/execution-contracts.ts`           | Frontend |
| `apps/dashboard/src/types/api.ts` (DealStage type)          | Frontend |
| `packages/contracts/openapi/zakops-api.json` (stage enums)  | Contract |

---

## Required Checks

When a PR touches any trigger file, the following checks are **mandatory**
before merge:

### 1. ADR Review

- [ ] Confirm the change is consistent with **ADR-002** (canonical database).
- [ ] Confirm the change is consistent with **ADR-003** (stage configuration
      authority).
- [ ] If the change conflicts with an ADR, a new ADR must be proposed and
      accepted before the PR can merge.

### 2. Stage Configuration Consistency

- [ ] `PIPELINE_STAGES` + `TERMINAL_STAGES` in `execution-contracts.ts` matches
      the `DealStage` union type in `types/api.ts`.
- [ ] Both match the `chk_deal_lifecycle` CHECK constraint in the database.
- [ ] Both match the valid keys in `transition_deal_state()`.
- [ ] Stage labels, background colors, and column colors are defined for every
      stage in `ALL_STAGES_ORDERED`.

### 3. Type Synchronization

```bash
cd /home/zaks/zakops-agent-api && make sync-all-types
```

- [ ] Command completes without errors.
- [ ] No type drift detected between OpenAPI contract and frontend types.

### 4. Local Validation

```bash
cd /home/zaks/zakops-agent-api && make validate-local
```

- [ ] TypeScript compilation passes (`tsc --noEmit`).
- [ ] ESLint passes with no new errors.
- [ ] All unit tests pass.

### 5. Backend Validation

```bash
cd /home/zaks/zakops-backend && bash scripts/test.sh
```

- [ ] All backend tests pass.
- [ ] If a new migration was added, it applies cleanly to a fresh database.

### 6. Smoke Test

```bash
cd /home/zaks/zakops-backend && bash scripts/qa_smoke.sh
```

- [ ] End-to-end smoke test passes.
- [ ] Deal CRUD operations work with the modified stages.

### 7. Manual Verification

- [ ] Dashboard pipeline board renders all stages in correct order.
- [ ] Stage transitions work from the UI (drag-and-drop or dropdown).
- [ ] Archive and restore operations function correctly.
- [ ] Health endpoint (`/health`) reports correct `db_name: "zakops"`.

---

## PR Template Addition

When a PR triggers this protocol, include this section in the PR description:

```markdown
## Deal State Change Protocol

**Trigger file(s) modified:** [list files]
**ADR compliance:** [ADR-002: Yes/No] [ADR-003: Yes/No]

### Checklist
- [ ] Stage config consistency verified
- [ ] `make sync-all-types` passes
- [ ] `make validate-local` passes
- [ ] Backend tests pass
- [ ] Smoke test passes
- [ ] Manual UI verification done
```

---

## Escalation

If any check fails and cannot be resolved by the PR author:

1. Tag the PR with `deal-lifecycle-review`.
2. Do not merge until all checks pass.
3. If a CHECK constraint or transition function change is involved, require
   explicit sign-off from the database owner.

---

## Automation (Future)

These checks should be automated in CI. Until then, they are enforced via
code review discipline. See `innovation-roadmap.md` — "Automated Parity Tests"
for the planned CI integration.

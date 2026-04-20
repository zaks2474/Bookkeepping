# ADR-003: Stage Configuration Authority — Single Canonical Config

| Field       | Value                          |
|-------------|--------------------------------|
| Status      | **Accepted**                   |
| Date        | 2026-02-08                     |
| Mission     | DEAL-INTEGRITY-UNIFIED         |
| Layer       | 6 — Governance                 |
| Deciders    | Zak (owner), Claude (advisor)  |

## Context

Prior to this mission, the dashboard codebase contained **8+ hardcoded stage
arrays** scattered across multiple files. Each array defined a different subset,
ordering, or labeling of deal stages:

- Some included "Won" and "Lost"; others omitted them.
- Color mappings were duplicated with inconsistent values.
- Column ordering on the pipeline board differed from dropdown ordering.
- Adding or renaming a stage required finding and updating every instance — a
  process that was error-prone and never fully completed.

This led to:
- **UI inconsistencies**: Stages appeared in different orders on different pages.
- **Silent bugs**: A stage present in one array but missing from another caused
  deals to vanish from certain views.
- **High maintenance cost**: Every stage change was a multi-file scavenger hunt.

## Decision

**Single canonical stage configuration file:**

```
apps/dashboard/src/types/execution-contracts.ts
```

This file is the **sole authority** for all stage-related data in the frontend.

### Exports

| Export                     | Type                    | Description                                      |
|----------------------------|-------------------------|--------------------------------------------------|
| `PIPELINE_STAGES`          | `readonly string[]` (7) | Active pipeline stages in display order           |
| `TERMINAL_STAGES`          | `readonly string[]` (2) | Terminal stages: `["Won", "Lost"]`                |
| `ALL_STAGES_ORDERED`       | `readonly string[]` (9) | Full ordered list: `[...PIPELINE, ...TERMINAL]`   |
| `DEAL_STAGE_BG_COLORS`     | `Record<string, string>` | Background colors for cards/badges per stage      |
| `DEAL_STAGE_COLUMN_COLORS` | `Record<string, string>` | Column header/border colors for pipeline board    |
| `DEAL_STAGE_LABELS`        | `Record<string, string>` | Human-readable labels (e.g., `"Closed Won"`)      |

### Enforcement

- **ESLint rule (planned)**: Any file importing a stage constant from a
  non-canonical source should trigger a lint warning.
- **Code review policy**: PRs that introduce new stage arrays outside
  `execution-contracts.ts` must be rejected.
- **Type safety**: The `DealStage` union type in `types/api.ts` must match
  `ALL_STAGES_ORDERED` exactly. The `make sync-all-types` command verifies this.

## Consequences

### Positive
- **Adding a stage** means updating **one file** on the frontend, plus the
  corresponding DB constraint and transition function on the backend. See
  `RUNBOOK-add-deal-stage.md` for the full procedure.
- **Consistency guaranteed** — every component pulls from the same source.
- **Discoverable** — new developers find the single file immediately.

### Negative / Constraints
- **Tight coupling to one file** — if `execution-contracts.ts` has a bug, it
  affects the entire dashboard. Mitigated by type-checking and tests.
- **Backend is a separate authority** — the backend DB `CHECK` constraint and
  `transition_deal_state()` function define the backend's stage list
  independently. The `make sync-all-types` command exists to verify parity, but
  it is a manual step (automated in CI).

## Related Documents
- `RUNBOOK-add-deal-stage.md` — step-by-step procedure
- `change-protocol.md` — PR checklist for stage file changes
- `ADR-002-canonical-database.md` — the DB where stages are enforced

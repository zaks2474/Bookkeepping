# PlanSpec Contract (Planner ↔ Executor)

ZakOps uses a shared, machine-validated contract so the Intelligence Plane can propose actions safely and the Execution Plane can run them deterministically with audit trails.

## Source of truth

- Pydantic model: `/home/zaks/scripts/actions/contracts/plan_spec.py`
- JSON Schema export: `/home/zaks/scripts/actions/contracts/plan_spec.schema.json`

## What it is

`PlanSpec` is **output-only**: planners produce it, executors consume it.

It is designed to be:
- deterministic-first (planner proposes; executor validates)
- approval-gated (steps can require human approval)
- auditable (each step is explicit and structured)

## How to validate

```bash
python3 - <<'PY'
from actions.contracts.plan_spec import PlanSpec

spec = PlanSpec(
    plan_id="PLAN-TEST",
    goal="Draft an LOI for DEAL-2026-001",
    steps=[],
)
print(spec.model_dump())
PY
```

## Notes

- Do not enable LangSmith tracing for PlanSpec generation in this phase.
- PlanSpec should never include secrets (credentials, tokens, raw OAuth payloads).
- Large bodies/documents should be referenced by path/artifact ID, not embedded.


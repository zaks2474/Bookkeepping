# Planner + Unified Manifest + Memory — Verification (No Tracing)

**Date:** 2025-12-31  
**Scope:** Intelligence Plane (planner/validator/manifest/memory) for Kinetic Action Engine v1.2  
**Hard constraints honored:** No LangSmith tracing; no changes to existing chat endpoint contracts.

---

## What Was Built

### 1) PlanSpec (planner → executor contract)
- **Contract (authoritative):** `/home/zaks/scripts/actions/contracts/plan_spec.py`
- **JSON Schema (generated):** `/home/zaks/scripts/actions/contracts/plan_spec.schema.json`
- Purpose: Stable, machine-validated format for Claude’s executor to consume (planning only; no execution).

### 2) Unified Capability Manifest (single planner source of truth)
- **Manifest file:** `/home/zaks/scripts/tools/manifest/manifest.json`
- **Builder:** `/home/zaks/scripts/tools/manifest/builder.py`
- **Loader/registry:** `/home/zaks/scripts/tools/manifest/registry.py`

Manifest includes **both**:
- Kinetic Action capabilities (internal executors): `DOCUMENT.GENERATE_LOI`, `COMMUNICATION.DRAFT_EMAIL`, etc.
- ToolGateway tools (MCP): `TOOL.gmail__send_email`, `TOOL.gmail__search_emails`, `TOOL.crawl4ai__single_page`, etc.

Each entry includes:
- `tool_name`
- `input_schema`
- `output_artifacts` (for kinetic actions) and/or `output_schema` (for tool outputs)
- `risk_level`, `requires_approval`
- `safety_class`: `reversible|gated|irreversible`
- `irreversible` boolean

### 3) Deterministic validator
- **Validator:** `/home/zaks/scripts/actions/intelligence/validator.py`
- Enforces:
  - step capability exists in manifest
  - required inputs present (based on manifest JSON schema `required`)
  - irreversible/gated steps must be explicitly gated in the PlanSpec
  - optional mode gate: `ZAKOPS_PLANNER_MODE=no_irreversible|offline` blocks irreversible steps

### 4) Action Memory (retrieval-based learning)
- **Memory store:** `/home/zaks/scripts/actions/memory/store.py`
- Storage: `ZAKOPS_STATE_DB` (SQLite, WAL)
- Writes a compact per-action summary (PlanSpec + outcome + artifacts + edit signal) after terminal completion.
- Retrieval: best-effort SQLite FTS (if available), with a deterministic token-overlap fallback.

### 5) Runner integration (best-effort, non-blocking)
- **Runner hook:** `/home/zaks/scripts/actions_runner.py`
- After an action reaches a terminal state (`COMPLETED` or `FAILED` without retry), the runner writes an ActionSummary into memory.

---

## How To Regenerate Artifacts

### Regenerate the unified manifest
```bash
cd /home/zaks/scripts
python3 -m tools.manifest.builder
```

### Regenerate PlanSpec JSON schema
```bash
cd /home/zaks
python3 scripts/actions/contracts/plan_spec.py
```

---

## How To Use The Planner (Code)

Primary entrypoint:
- `/home/zaks/scripts/actions/intelligence/planner.py` → `ToolRAGPlanner.plan()`

Example (deterministic-only):
```python
import os
os.environ["ZAKOPS_PLANNER_USE_LLM"] = "false"

from actions.intelligence.planner import ToolRAGPlanner

planner = ToolRAGPlanner()
plan = planner.plan("Generate LOI for DEAL-2025-001", deal_id="DEAL-2025-001")
```

Planner outputs a `PlanSpec`:
- `status=OK` with `steps[]`, OR
- `status=NEEDS_TOOL` with `missing_capability`, OR
- `status=BLOCKED` with `blocked_reason`

---

## Acceptance Tests (Implemented)

1) **Generate LOI**
- Input: `"Generate LOI for DEAL-2025-001"`
- Expected: `PlanSpec.status=OK` with `DOCUMENT.GENERATE_LOI`, or `NEEDS_TOOL` if not registered
- Verified via unit test: `scripts/tests/test_intelligence_planner_manifest_memory.py::test_planner_returns_planspec_for_loi`

2) **Send email**
- Input: `"Send email to broker@example.com"`
- Expected: Plan includes a send step marked `gated=true` (`irreversible=true`) so executor cannot auto-send
- Verified via unit test: `scripts/tests/test_intelligence_planner_manifest_memory.py::test_send_email_plan_marks_send_step_gated`

---

## Unit Test Evidence

Run:
```bash
bash /home/zaks/scripts/run_unit_tests.sh
```

Result (current): ✅ PASS (27 tests)

Key new test file:
- `/home/zaks/scripts/tests/test_intelligence_planner_manifest_memory.py`

Coverage includes:
- manifest lookup
- planner PlanSpec output (LOI)
- validator blocks unsafe irreversible step missing gate
- memory retrieval influences plan selection


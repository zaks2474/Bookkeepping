# Kinetic Actions End-to-End Implementation Plan

**Date**: 2025-12-31
**Author**: Claude (Opus 4.5)
**Status**: IMPLEMENTATION PLAN
**Goal**: Make Kinetic Actions execute real workflows (Runner + Steps + ContextPack + Artifacts + Approval Gates)

---

## Executive Summary

Actions are not progressing because:
1. **The runner process is NOT running** - No systemd unit exists
2. **Executors exist but are deterministic stubs** - No LLM integration
3. **No ContextPack** - Actions can't gather deal context from DataRoom/RAG
4. **No step tracking** - Workflows aren't resumable/auditable

---

## Root Cause Analysis (Section A)

### Current State

| Component | Status | Location |
|-----------|--------|----------|
| ActionStore (SQLite) | EXISTS | `/home/zaks/DataRoom/.deal-registry/ingest_state.db` |
| actions_runner.py | EXISTS but NOT RUNNING | `/home/zaks/scripts/actions_runner.py` |
| actions_admin.py | EXISTS | `/home/zaks/scripts/actions_admin.py` |
| Executors | EXISTS (5 registered) | `/home/zaks/scripts/actions/executors/` |
| systemd service | MISSING | Need `/etc/systemd/system/kinetic-actions-runner.service` |
| ContextPack builder | MISSING | Need `/home/zaks/scripts/actions/context/context_pack.py` |
| Step engine | MISSING | Need `action_steps` table in SQLite |

### Executors Registered

```
- COMMUNICATION.DRAFT_EMAIL
- DILIGENCE.REQUEST_DOCS
- DOCUMENT.GENERATE_LOI
- ANALYSIS.BUILD_VALUATION_MODEL
- PRESENTATION.GENERATE_PITCH_DECK
- TOOL.* (dynamic gateway)
```

### Why Actions Don't Complete

1. Runner not running → Actions stay in READY/PROCESSING forever
2. Even if runner runs, executors are stub-only (no Gemini integration)
3. No context pack → LLM can't draft personalized content

---

## Implementation Plan

### Phase 0: Prove the Runner Works (30 min)

**Goal**: Get runner running and prove one action completes

1. Create systemd service for runner
2. Start runner
3. Create test TOOL.noop action
4. Verify COMPLETED status + audit trail

**Deliverables**:
- `/etc/systemd/system/kinetic-actions-runner.service`
- `/home/zaks/bookkeeping/docs/ACTIONS-RUNNER-RCA.md`

### Phase 1: Step Engine (1 hr)

**Goal**: Persisted, resumable workflow steps

1. Add `action_steps` table to SQLite schema
2. Create step model: `{step_id, action_id, name, status, started_at, ended_at, output_ref, error}`
3. Add step management methods to ActionStore
4. Update executors to report steps

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS action_steps (
  step_id TEXT PRIMARY KEY,
  action_id TEXT NOT NULL,
  step_index INTEGER NOT NULL,
  name TEXT NOT NULL,
  status TEXT NOT NULL,  -- PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED
  started_at TEXT,
  ended_at TEXT,
  output_ref TEXT,  -- JSON pointer to artifact or outputs key
  error TEXT,       -- JSON ActionError
  UNIQUE(action_id, step_index)
);
CREATE INDEX IF NOT EXISTS idx_steps_action_id ON action_steps(action_id);
```

**Rules**:
- Workflows are resumable: failed step can be retried without repeating completed steps
- Send/commit steps require explicit approval gate

### Phase 2: ContextPack Builder (1 hr)

**Goal**: Centralized context gathering for all action types

**Location**: `/home/zaks/scripts/actions/context/context_pack.py`

**ContextPack Contents**:
```python
@dataclass
class ContextPack:
    deal_id: str
    deal_record: Dict[str, Any]  # From registry
    broker_info: Optional[Dict[str, Any]]
    stage: str
    status: str

    # Evidence
    recent_events: List[Dict]  # Last N events
    case_summary: Optional[str]  # From case file
    rag_evidence: List[Dict]  # RAG chunks relevant to action

    # Materials (optional)
    extracted_links: List[Dict]  # If enrichment ran

    # Memory (CodeX hook)
    prior_actions_summary: Optional[str]  # Summary of related actions
```

**Sources**:
- Deal registry → deal record, broker info
- Event store → recent events
- Case files → case summary, key facts
- RAG → relevant documents (via `/rag/search`)
- Enrichment → extracted materials

### Phase 3: REQUEST_DOCS MVP Workflow (1.5 hr)

**Goal**: Prove real-world execution with Gemini-drafted email

**Workflow Steps**:
1. `gather_context` - Build ContextPack
2. `draft_email` - Use Gemini 2.5 to draft broker email (strict JSON `{subject, body}`)
3. `store_artifact` - Save draft as artifact
4. Action → COMPLETED with artifact link

**Critical**: No auto-send. Sending requires separate SEND_EMAIL action with approval gate.

**Executor Enhancement**:
```python
# /home/zaks/scripts/actions/executors/diligence_request_docs.py
class RequestDocsExecutor(ActionExecutor):
    def execute(self, payload, ctx):
        # Step 1: Gather context
        self.emit_step(ctx, "gather_context", status="IN_PROGRESS")
        context_pack = build_context_pack(payload.deal_id, action_type=self.action_type)
        self.emit_step(ctx, "gather_context", status="COMPLETED")

        # Step 2: Draft email with Gemini
        self.emit_step(ctx, "draft_email", status="IN_PROGRESS")
        draft = self.draft_with_gemini(context_pack, payload.inputs)
        self.emit_step(ctx, "draft_email", status="COMPLETED")

        # Step 3: Store artifact
        artifact = self.save_email_draft(ctx, draft)

        return ExecutionResult(
            outputs={"draft": draft},
            artifacts=[artifact],
            follow_up_action={  # Suggest SEND_EMAIL (requires approval)
                "type": "COMMUNICATION.SEND_EMAIL",
                "inputs": {"draft_artifact_id": artifact.artifact_id},
                "requires_approval": True
            }
        )
```

### Phase 4: PlanSpec Interface (30 min)

**Goal**: CodeX-compatible plan input format

**Location**: `/home/zaks/scripts/actions/planner.py` (extend existing)

**PlanSpec Schema**:
```python
@dataclass
class PlanStep:
    tool_name: str           # e.g., "rag_search", "draft_email", "send_email"
    args: Dict[str, Any]     # Tool arguments
    expects_artifact: bool   # Does this step produce an artifact?
    reversible: bool         # Can be rolled back?
    approval_required: bool  # Gate before execution?

@dataclass
class PlanSpec:
    plan_id: str
    action_id: str
    steps: List[PlanStep]
    safety_constraints: List[str]  # e.g., "no_auto_send", "max_cost_usd:1.00"
    created_at: str
    created_by: str  # "codex_planner" or "manual"
```

### Phase 5: Integration Tests (30 min)

**Tests**:
1. `test_runner_picks_up_action` - Create action, runner processes, COMPLETED
2. `test_request_docs_produces_artifact` - REQUEST_DOCS creates draft artifact
3. `test_send_requires_approval` - SEND_EMAIL action requires explicit approval gate

**Location**: `/home/zaks/scripts/tests/test_actions_e2e.py`

---

## File Changes Summary

### New Files

| File | Purpose |
|------|---------|
| `/etc/systemd/system/kinetic-actions-runner.service` | Runner daemon |
| `/home/zaks/scripts/actions/context/__init__.py` | Context module |
| `/home/zaks/scripts/actions/context/context_pack.py` | ContextPack builder |
| `/home/zaks/scripts/tests/test_actions_e2e.py` | Integration tests |
| `/home/zaks/bookkeeping/docs/ACTIONS-RUNNER-RCA.md` | Root cause analysis |
| `/home/zaks/bookkeeping/docs/ACTIONS-E2E-VERIFICATION.md` | Final verification |

### Modified Files

| File | Changes |
|------|---------|
| `/home/zaks/scripts/actions/engine/store.py` | Add step management methods |
| `/home/zaks/scripts/actions/engine/models.py` | Add ActionStep model |
| `/home/zaks/scripts/actions/executors/diligence_request_docs.py` | Add Gemini integration |
| `/home/zaks/scripts/actions/executors/base.py` | Add step emission helpers |
| `/home/zaks/scripts/actions/planner.py` | Add PlanSpec interface |
| `/home/zaks/scripts/actions_runner.py` | Add step tracking |

---

## Constraints (Hard Requirements)

1. **No LangSmith tracing** - Do not enable LANGCHAIN_TRACING_V2
2. **No changes to chat contracts** - /api/chat* unchanged
3. **Gemini only for drafting** - No other LLM providers
4. **Draft-only for sends** - No auto-sending emails
5. **Deterministic-first** - Policy drives behavior, agents recommend

---

## Execution Order

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
```

Each phase has clear deliverables that can be verified before proceeding.

---

## Success Criteria

1. Runner is running as systemd service
2. TOOL.noop action completes (PENDING → READY → PROCESSING → COMPLETED)
3. REQUEST_DOCS creates Gemini-drafted email artifact
4. SEND_EMAIL requires explicit approval (cannot auto-execute)
5. All 3 integration tests pass
6. Documentation complete (RCA + Verification)

---

## Appendix: Current Action Flow

```
Chat proposes action → /api/actions (POST) → ActionStore.create_action()
                                           → status=PENDING_APPROVAL

Operator approves → /api/actions/{id}/approve → status=READY

Operator runs → /api/actions/{id}/execute → next_attempt_at=now

Runner picks up → actions_runner.py poll → begin_processing()
                                        → executor.execute()
                                        → mark_action_completed()
                                        → status=COMPLETED

BUT: Runner not running → Actions stay in READY forever
```

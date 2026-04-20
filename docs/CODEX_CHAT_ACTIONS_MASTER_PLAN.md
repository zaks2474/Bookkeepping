# ZakOps Master Plan — Chat + Actions Unification (Local‑First)

**Source plan:** `/root/.claude/plans/sharded-exploring-sifakis.md` (Codex-reviewed 2026-01-08)  
**Scope:** Make Chat and Actions feel “one system”: Chat proposes; Actions execute (approval-gated).  
**Contracts:** Preserve the existing HTTP contracts + dashboard behavior (no breaking changes).  
**Tracing:** Do **not** enable LangSmith tracing in this phase.

---

## Non‑Negotiables

- **Chat never executes side effects** (no ToolGateway/MCP calls from chat).
- **Actions are the only execution plane** (approval-gated, auditable, retriable).
- **No auto-send / no auto-delete email.**
- **No silent cloud calls.** Any cloud-required work must be explicit (`cloud_required`) and approval-gated.
- **No secrets in git/logs** (sanitize all reports; avoid embedding email bodies/attachments).
- **Incremental and reversible** changes only (feature flags and rollbacks).

---

## Current Architecture (Ground Truth)

**Frontend (dashboard):**
- Next.js dev: `http://localhost:3003` (proxy to backend via `/api/*`)
- Chat UI: `/chat` (proposal cards + `/api/chat/execute-proposal`)
- Quarantine UI: `/quarantine` (decision UX over `EMAIL_TRIAGE.REVIEW_EMAIL`)

**Backend (public contract used by dashboard):**
- FastAPI: `scripts/deal_lifecycle_api.py` on `:8090`
- Chat endpoints:
  - `POST /api/chat` (SSE)
  - `POST /api/chat/complete`
  - `POST /api/chat/execute-proposal`
- Actions endpoints:
  - `GET /api/actions`, `POST /api/actions/*` (approve/run/retry/cancel/unstick)
  - Debug: `GET /api/actions/debug/missing-executors`, `.../capability-mismatches`

**Chat engine (already implemented):**
- `scripts/chat_orchestrator.py` (deterministic-first + local vLLM)
- Optional **LangGraph “brain”** integration via `ZAKOPS_BRAIN_MODE` calling `http://localhost:8080/api/deal-chat`
- Proposal canonicalization already exists (`schedule_action → create_task`, etc.)

**Actions engine (already implemented):**
- SQLite-backed `ActionStore` + systemd runner (`kinetic-actions-runner.service`)
- Creation-time validation exists (`validate_action_creation`)
- Quarantine/deal material pipelines already exist and must not regress.

---

## Master Implementation Phases (incremental)

### Phase 0 — Baseline Evidence + Contract Snapshot (NO behavior changes)

**Deliverables**
- `scripts/codex_chat_actions_baseline.py` (safe evidence collector; no secrets)
- `bookkeeping/docs/CODEX_CHAT_ACTIONS_VERIFICATION_BASELINE.md` (sanitized report)

**What to capture**
- Running services/ports: `3003`, `8090`, `8000`, optional `8080`
- `GET /api/version` (via `:8090` and via dashboard proxy `:3003/api/version`)
- `GET /api/chat/llm-health`
- Action engine coverage: capability count + `missing-executors` output
- Runner + timers status: `kinetic-actions-runner`, triage timer, controller timer
- Chat contract snapshots (shape only; redact content/citations snippets)

**Acceptance**
- Report exists, contains concrete evidence, and contains no email bodies or secrets.

---

### Phase 1 — Chat “Planner/Proposer” Reliability (compatibility-first)

**Objective**
- Keep current UI proposal cards working.
- Make proposal extraction deterministic and schema-stable.

**Work**
- Update `scripts/chat_orchestrator.py` system prompt to prefer **strict JSON proposals** (while parser still supports legacy YAML-like blocks).
- Harden proposal parser:
  - tolerate multiline bodies (best-effort) but discourage them
  - parse inline JSON for fields like `inputs` where possible
  - enforce canonical proposal types (already present; extend only if needed)
- Strengthen scope behavior:
  - In `global` scope, do not emit deal-required proposals unless deal_id is known.

**Acceptance**
- Chat continues returning the same `/api/chat/complete` shape.
- No “unknown proposal type” / “content:null” regressions.

---

### Phase 2 — Actions Reliability Surfacing (no new persisted states)

**Objective**
- Prevent broken actions at creation time; surface legacy mismatches clearly.

**Work**
- Keep rejecting unknown executor/capability mismatches on action creation.
- For legacy missing executors: ensure actions end `FAILED` with structured `error.code=executor_not_found` (UI can render as “Blocked” without adding a new DB status).
- Ensure remediation endpoints stay stable:
  - `POST /api/actions/{id}/retry`
  - `POST /api/actions/{id}/cancel`
  - `POST /api/actions/{id}/unstick`

**Acceptance**
- No action can be created that cannot ever run.
- Missing executor situations are discoverable via debug endpoint and clearly visible in UI.

---

### Phase 3 — Orchestration Run History (reuse existing run ledger)

**Objective**
- Make controller loops and automation runs observable without adding tracing.

**Work**
- Prefer appending run records to the existing run ledger:
  - `bookkeeping/scripts/run_ledger.py` → `/home/zaks/logs/run-ledger.jsonl`
- Add “run id / outcome” emission to controller loops where useful (no secrets).

**Acceptance**
- Operators can answer: “What ran? When? What did it propose? Did it fail?” using local logs/ledger.

---

## Rollback Strategy

Rollback must be instant and safe:
- Keep proposal parsing backward compatible (JSON preferred, YAML still accepted).
- Any new behavior behind an env flag must default to the existing behavior.
- Document exact restart commands for the actual runtime (systemd vs nohup) in the baseline report.

---

## Test & Verification Checklist

**Backend**
- `bash /home/zaks/scripts/run_unit_tests.sh`
- Add/extend tests for:
  - proposal canonicalization and parser stability
  - execute-proposal success paths for `create_action` and `request_docs`

**Frontend**
- `cd /home/zaks/zakops-dashboard && npm run build`
- Manual:
  - Chat proposals approve/reject works
  - Quarantine approve/reject still works
  - Actions list renders with null-able fields


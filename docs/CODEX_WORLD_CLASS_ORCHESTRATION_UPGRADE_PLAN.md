# CODEX — ZakOps “World-Class” Orchestration Upgrade Plan
Temporal + LangGraph Agentic Triage + n8n (Peripheral Workflows)

Date: 2026-01-07  
Status: Ready for implementation (Phase 0 → Phase 3)  
Scope: **Production-ready upgrades without breaking existing contracts**

## Goal

Make ZakOps reliably **agentic + local-first + observable + fast to iterate** by:
1) Moving scheduling/orchestration from systemd timers into **Temporal** (durable, observable workflows).
2) Upgrading email triage to a **LangGraph agentic runtime** that uses the exported Agent Builder spec and is powered by **local vLLM Qwen** (OpenAI-compatible endpoint).
3) Using **n8n** for peripheral workflows (notifications, follow-ups, auth-required link queues) without contaminating core logic.

## Non-Negotiables (Preserved)

- No automatic sending of email (SEND remains approval-gated).
- No automatic deletion of emails.
- No LangSmith tracing (keep OFF unless explicitly enabled later).
- No secrets in git/logs; no accidental cloud calls.
- Only **one canonical email processor active** after cutover (no dual scheduling).
- Deterministic guardrails remain hard constraints (denylist/receipt rules, etc.).

## Current Baseline (Known Working)

- Quarantine UI exists at `/quarantine` and is action-backed (`EMAIL_TRIAGE.REVIEW_EMAIL` + preview endpoint).
- Approve creates deal workspace + registry entry and persists email artifacts.
- Reject exists (`EMAIL_TRIAGE.REJECT_EMAIL`) and cancels review item.
- Deal “Materials” UI/endpoint exists and is filesystem-backed.
- Email triage supports local vLLM/Qwen assist/full modes and writes `triage_summary.json`/`triage_summary.md` into quarantine.

## Dependencies (Pin + Install)

These phases introduce new runtime dependencies. Keep them **explicitly pinned** and install via a Make target so the system is reproducible.

- Temporal Python SDK: `temporalio`
- LangGraph: `langgraph` (plus its minimal deps)

Plan:
- Add `bookkeeping/requirements-orchestration.txt` with pinned versions.
- Add `make orchestration-deps` to install them into a venv at `/home/zaks/.venvs/zakops-orchestration` (PEP 668 safe).

---

# Phase 0 — Verification-First (No Behavior Changes)

## Objective

Generate a **reproducible baseline report** and prove triage is local-vLLM-only before any orchestration cutover.

## Step 0.1 — Baseline script (single source of truth)

Add:
- `/home/zaks/scripts/codex_baseline_check.py`

Script outputs **Markdown** suitable for committing into:
- `bookkeeping/docs/CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md`

Baseline script must:
- Verify service + port health:
  - backend API `:8090`
  - dashboard `:3003`
  - vLLM `:8000` (`/v1/models`)
  - brain `:8080` (`/health`)
  - `kinetic-actions-runner.service`
  - `zakops-email-triage.timer` + `.service`
  - `zakops-deal-lifecycle-controller.timer` + `.service`
- Print **allowlisted** env vars only (never print secrets):
  - allowlist: `EMAIL_TRIAGE_*`, `ZAKOPS_*`, `OPENAI_API_BASE`, `VLLM_MODEL`, `DEFAULT_MODEL`
  - redact any key containing `KEY|TOKEN|SECRET|PASSWORD` (defense-in-depth)
- Query triage state DB stats (read-only):
  - `DataRoom/.deal-registry/email_triage_state.db` counts + classification breakdown
- Capture recent triage logs (journal tail).

## Step 0.2 — Run verification suite

Commands:
- `python3 /home/zaks/scripts/codex_baseline_check.py > /home/zaks/bookkeeping/docs/CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md`
- `bash /home/zaks/scripts/run_unit_tests.sh`
- `cd /home/zaks/bookkeeping && make triage-test`
- Quarantine E2E:
  - If ` /home/zaks/scripts/test_quarantine_e2e.sh` exists: run it.
  - Else: create it (minimal) and run it.

## Gate Criteria

Proceed only if:
- Baseline checks pass
- Unit tests pass
- vLLM returns a local model list (Qwen expected)
- Triage base URL resolves to localhost (no cloud)

---

# Phase 1 — Temporal as Durable Orchestration Backbone (Wrapper-First)

## Objective

Replace systemd timer scheduling for triage + controller with Temporal schedules, while **wrapping existing scripts** first (no rewrite).

## Step 1.1 — Local Temporal stack + UI

Preferred: add a dedicated compose file:
- `/home/zaks/Zaks-llm/docker-compose.temporal.yml`

Services:
- Temporal server
- Postgres (persisted volume)
- Temporal UI (local only; pick a stable port like `8233` or `8088`)

## Step 1.2 — Python worker module

Add directory:
- `/home/zaks/scripts/temporal_worker/`

Files:
- `activities.py` — wrappers calling existing entrypoints via subprocess:
  - `python3 -m email_triage_agent.run_once` (cwd `/home/zaks/bookkeeping/scripts`)
  - `python3 /home/zaks/scripts/deal_lifecycle_controller.py` (or canonical controller entrypoint)
  - capture stdout/stderr + durations + exit code into structured result
  - **stdout/stderr hygiene**: truncate large outputs and write full logs to a file (path returned in result) to avoid bloating Temporal history
  - **log redaction**: never write env dumps or secrets; preserve existing “allowlist + redact” discipline from Phase 0
- `workflows.py` — scheduled workflows:
  - hourly triage schedule
  - hourly controller schedule
  - single-flight (no overlap); bounded retries aligned with idempotency
- `schedules.py` — create/update schedules idempotently
- `worker.py` — run worker, graceful shutdown
 - `config.py` — centralize Temporal host/namespace/task-queue/schedule IDs and keep defaults local-lab friendly

## Step 1.3 — Make targets (operator UX)

Modify:
- `/home/zaks/bookkeeping/Makefile`

Add:
- `temporal-up`, `temporal-down`, `temporal-logs`
- `temporal-worker` (start worker)
- `temporal-schedules` (create schedules)
- `temporal-status` (health + schedules summary)
- `orchestration-audit` (assert no dual scheduling)
 - `temporal-run-once` (manual single-run of triage/controller workflows; required before enabling schedules)

## Step 1.4 — Cutover (NO dual scheduling)

Hard rule: **do not run both systemd timers and Temporal schedules simultaneously**.

Cutover checklist:
1) Start Temporal stack.
2) Start worker.
3) Run workflows manually once (no schedules yet) and verify in Temporal UI.
4) Disable systemd timers:
   - `zakops-email-triage.timer`
   - `zakops-deal-lifecycle-controller.timer`
5) Enable Temporal schedules.
6) Verify only Temporal is triggering runs.

## Step 1.5 — Operational guardrails

- **Single scheduler invariant**: `make orchestration-audit` must fail if systemd timers are enabled *and* Temporal schedules exist.
- **Single-flight**: schedules use overlap=SKIP and workflows also self-check for already-running logical run IDs (defense-in-depth).
- **Failure visibility**: failed activities must surface exit code + log path and never “silently succeed”.

## Step 1.5 — Tests

Add:
- `/home/zaks/scripts/tests/test_temporal_worker_smoke.py` (unittest; subprocess mocked)

## Acceptance (Phase 1)

- Temporal UI shows workflow histories and schedule triggers.
- Hourly triage + controller run via Temporal.
- No duplicate processors are active.
- Existing tests still pass.

---

# Phase 2 — LangGraph Agentic Triage Using Exported Agent Spec

## Objective

Introduce a LangGraph triage backend that:
- Uses local vLLM Qwen endpoint only
- Uses exported Agent Builder spec as prompt/source-of-truth
- Produces strict structured outputs for Quarantine UI
- Preserves deterministic hard guardrails
- Reduces false positives and improves extraction quality

## Step 2.1 — Load exported agent spec (best-effort, never break triage)

Spec dir (already present):
- `/home/zaks/bookkeeping/configs/email_triage_agent/agent_config/`

Implement a loader that extracts:
- system prompt/instructions
- tool descriptions (even if not used)
- examples/few-shot if present

If parsing fails:
- degrade gracefully (fallback to current `llm_triage` prompt)
- do not break triage

## Step 2.2 — Implement LangGraph triage runtime module

Add:
- `/home/zaks/bookkeeping/scripts/email_triage_agent/langgraph_triage.py`

Graph nodes:
1) classify
2) extract entities/links/attachments
3) apply deterministic guardrails (post-LLM)

Hard guardrails (enforced after model output):
- Denylisted sender domain → cannot be `DEAL_SIGNAL`
- Receipt/transactional indicators → cannot be `DEAL_SIGNAL` (unless explicit override flag enabled; default off)
- Only allow `EMAIL_TRIAGE_LLM_BASE_URL` that resolves to localhost/RFC1918 (SSRF-safe); **hard-block** non-local URLs regardless of config
- Bound inputs: cap body/snippet length, max links, max attachments metadata passed to the model

Output: strict JSON matching the existing triage contract and persisted to `triage_summary.json`/`.md`.

## Step 2.3 — Feature-flag integration (zero-risk rollout)

Add:
- `EMAIL_TRIAGE_LLM_BACKEND=llm_triage|langgraph` (default: `llm_triage` until proven)
- Keep: `EMAIL_TRIAGE_LLM_MODE=off|assist|full`

Rules:
- assist: only runs agentic triage for deterministic deal-signal candidates; may downgrade confidently
- full: runs agentic triage for all non-denylisted emails; guardrails still block receipts/marketing

## Step 2.4 — Operator feedback loop + evaluation

Write JSONL feedback on operator decisions:
- `/home/zaks/DataRoom/.deal-registry/triage_feedback.jsonl`

Data minimization:
- Do **not** write raw email bodies into feedback.
- Store only: ids, sender domain, subject hash (or truncated), model classification/confidence, operator decision, and timestamps.

Add:
- `/home/zaks/bookkeeping/scripts/email_triage_agent/eval_triage.py`
- Output report: `/home/zaks/bookkeeping/docs/EMAIL_TRIAGE_EVAL_REPORT.md`

## Step 2.5 — Tests

Add `unittest` coverage:
- guardrail enforcement
- schema validation
- backend switch behavior (`llm_triage` vs `langgraph`)

## Acceptance (Phase 2)

- Quarantine shows high-quality summaries + extracted fields.
- False positives drop materially.
- No cloud calls; local-only vLLM.
- All tests pass; rollback via env flag is instant.

---

# Phase 3 — n8n for Peripheral Workflows (Optional, Off by Default)

## Objective

Keep core logic in code; make integrations easy to change.

## Step 3.1 — Run n8n locally

Add an n8n service gated by a docker profile (starts only when explicitly enabled):
- `http://localhost:5678`

Auth:
- Require operator-provided env (no default passwords committed).
- Keep n8n behind a docker profile or separate compose file so it never starts by accident.

## Step 3.2 — SSRF-safe webhook emitter

Add:
- `/home/zaks/scripts/integrations/n8n_webhook.py`

Rules:
- Only allow webhook URLs that are localhost / 127.0.0.1 / RFC1918
- Single env var: `ZAKOPS_N8N_WEBHOOK_URL` (unset → no-op)
- Non-blocking “best-effort” delivery (do not break core flows)

Events:
- `quarantine.created`
- `quarantine.approved` (deal created)
- `quarantine.rejected`
- `materials.auth_required_links_detected`

## Step 3.3 — Starter workflows (export JSON)

Add directory:
- `/home/zaks/bookkeeping/docs/n8n_workflows/`

## Acceptance (Phase 3)

- Webhooks received locally by n8n.
- Integration is fully disabled when env var is unset.
- SSRF protection blocks non-local URLs.

---

# Rollback Plan (Required)

- Triage backend rollback:
  - `EMAIL_TRIAGE_LLM_BACKEND=llm_triage`
  - `EMAIL_TRIAGE_LLM_MODE=off` (deterministic-only)
- Orchestration rollback:
  - Disable Temporal schedules and stop worker
  - Re-enable systemd timers:
    - `zakops-email-triage.timer`
    - `zakops-deal-lifecycle-controller.timer`
- n8n rollback:
  - `unset ZAKOPS_N8N_WEBHOOK_URL` (no-op)
  - stop n8n service/profile

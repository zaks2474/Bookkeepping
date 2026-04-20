# Deal Lifecycle Agents — Operating Model & Build Plan

> **ARCHIVED (2025-12-27)**: Superseded by `/home/zaks/bookkeeping/docs/WORLD-CLASS-ORCHESTRATION-PLAN.md`.

**Author:** Codex (with ZakOps operator direction)  
**Date:** 2025-12-26  
**Status:** DRAFT — Awaiting Operator Approval  
**Scope:** Reframe ZakOps from “cron + scripts” into a deal-centric, lifecycle-aware, AI-assisted platform (years-long horizon) without throwing away what already works.

**Companion docs:**
- `/home/zaks/bookkeeping/docs/WORLD-CLASS-ORCHESTRATION-PLAN.md` (detailed patterns + phase specs)
- `/mnt/c/Users/mzsai/Downloads/zakops_unified_execution_plan.md` (tight “contracts-first” execution plan)

---

## 0) North Star (What We’re Building)

ZakOps should behave like a **deal operating system**:
- A **business opportunity** enters a lifecycle and stays “alive” for months/years.
- AI participates continuously as **roles** (case manager, underwriter, diligence coordinator), not as one-off utilities.
- The system is **time-aware** (follow-ups, milestones, reminders, reviews).
- Every change is traceable via **events, state transitions, and scheduled actions**.
- Humans approve high-stakes decisions (LOI, closing, exit), but AI keeps the process moving.

## 0.1) Non-Negotiables (Success Definition)

1. **Deal is the unit of work** (not a cron run).
2. **Every inbound email produces either** a deal-linked `email_received` event **or** a quarantine item (no silent drops).
3. **Folders are derived views**, never the source of truth.
4. **Deterministic-first:** policy + schemas drive behavior; agents recommend/draft, but do not “free-run.”
5. **Approval gates enforced** for LOI / CLOSING / EXIT_PLANNING / CLOSED_WON.
6. **Audit trail everywhere:** deal events + run-ledger + action execution records.

---

## 1) Ground Truth: What Exists Today (Baseline)

### 1.1 Runtime agents (interactive)
- `zakops-api` runs `OrchestratorAgent` with sub-agents:
  - `SystemOps`, `RAGExpert`, `DealSourcing`, `Comms`
- LLM runtime: **local vLLM** OpenAI-compatible API
  - Model: `Qwen/Qwen2.5-32B-Instruct-AWQ`

### 1.2 Deal platform primitives (durable state)
Already implemented and available (script-driven, but real foundations):
- **Deal registry**: `/home/zaks/DataRoom/.deal-registry/deal_registry.json`
- **Quarantine**: `/home/zaks/DataRoom/.deal-registry/quarantine.json`
- **Event store**: `/home/zaks/DataRoom/.deal-registry/events/*.jsonl`
- **Lifecycle state machine**: `/home/zaks/scripts/deal_state_machine.py`
- **Deferred actions queue**: `/home/zaks/DataRoom/.deal-registry/deferred_actions.json`
- **Deferred action processor** (cron heartbeat): `/home/zaks/scripts/process_deferred_actions.py`
- **Durable checkpoints**: `/home/zaks/DataRoom/.deal-registry/checkpoints/*.json`
- **AI advisory layer** (stage-aware): `/home/zaks/scripts/deal_ai_advisor.py`

### 1.3 Observability + safety
- **Run ledger**: `/home/zaks/logs/run-ledger.jsonl` (append-only)
- **Secret scanning gates**: `zakops_secret_scan.py` + hooks in RAG/SharePoint paths

### 1.4 Email ingestion (still “Stage A” / run-based)
- Email ingestion is cron-driven via `sync_acquisition_emails.py` (IMAP pull + attachments + OCR + manifests).
- DFP ingestion/classification exists as scripts (`ingestion_gateway.py`, `classification_router.py`) and DFP API endpoints, but the overall behavior still feels “file drop → scripts”.

---

## 2) The Structural Shift (Why It Still Feels Wrong)

### Current “unit of work”
- A cron run is the unit: `email_sync`, `rag_index`, `sharepoint_sync`.

### Required “unit of work”
- A **deal** is the unit: `deal_id` with:
  - stage/state (state machine)
  - immutable history (event sourcing)
  - commitments over time (deferred actions)
  - evolving case context (“case file”)

**Key rule:** Folders and dashboards are **derived views**; they are not the source of truth.

---

## 3) Agent Model (Redefining “Agents” as Lifecycle Roles)

### 3.1 How agents should behave
Agents should:
- Load deal context (registry + events + relevant artifacts)
- Produce structured outputs and/or schedule actions
- Emit events + run-ledger records (metadata-only where possible)
- Never execute irreversible actions without explicit approval

### 3.2 Recommended agent roster (v1)

Start with **6 core role agents** (and keep existing utility agents):

| Agent | Mission | Inputs | Writes | Hard boundaries |
|------|---------|--------|--------|-----------------|
| **Deal Case Manager** (NEW) | Own the deal lifecycle end-to-end; turn events into “next actions” and keep the deal’s case file current | new emails, doc arrivals, operator notes, due deferred-actions | deal events, stage transitions, deferred actions, case-file summary | no sending emails, no destructive ops |
| **Underwriter** (NEW) | Convert CIM/financials into structured financial picture + valuation view + risks + questions | extracted docs + RAG + known buy-box criteria | analysis artifacts + `ai_recommendation` events | no LOI/price commitments without approval |
| **Diligence Coordinator** (NEW) | Run DD playbook: check missing docs, maintain checklist, schedule follow-ups, deadline tracking | registry + doc inventory + events | deferred actions + DD checklist artifacts + events | no contacting counterparties directly |
| **Portfolio Operator** (NEW) | Post-close cadence: 30/60/90 day integration milestones, KPI reminders, quarterly reviews | events + scheduled actions | deferred actions + ops artifacts + events | never changes production systems |
| **Comms (Draft-Only)** (existing) | Produce drafts and outbox artifacts for operator approval | deal context + operator intent | draft artifacts | never send |
| **Knowledge (RAG Expert)** (existing) | Grounded retrieval, summaries, “what do we know?” queries | RAG tools | none (optionally writes summaries) | don’t hallucinate sources |

Optional (later):
- **Exit Strategist** (role agent, invoked only when stage enters `exit_planning`)
- **Deal Sourcing** (lead generation; no outreach without approval)
- **Governance/Eval** (continuous evaluation + safety regression)

---

## 4) Orchestration Evolution (From Cron Runs to Durable Workflows)

### 4.1 Keep cron, but change what it means
Cron becomes a **heartbeat**:
- It does not define “the process”.
- It runs the durable workflow engine: **deferred action processor** + “new event” scanners.

### 4.2 Workflow engine (already exists)
Use `/home/zaks/scripts/process_deferred_actions.py` as the lightweight workflow runner:
- Due actions invoke role agents (starting with AI advisory + case manager updates).
- Recurrence supports year-spanning cadence (quarterly reviews, annual check-ins).

### 4.3 What becomes event-driven
The platform should treat these as events:
- `email_received`
- `document_attached`
- `document_classified`
- `stage_changed`
- `ai_recommendation`
- `checkpoint_created/updated`
- `action_scheduled/executed/failed`

**Policy-as-code** determines:
- stage transitions allowed (state machine)
- when quarantine triggers
- what actions to schedule next

---

## 5) Ingestion Re-Think (Email → Lifecycle Entry/Continuation)

### 5.1 Target behavior
When an email arrives, the system should:
1) Link to a deal (or quarantine)
2) Emit `email_received` event
3) Attach docs (`document_attached` + `document_classified`)
4) Update stage if policy says so
5) Schedule next actions (follow-ups, requests, reviews)
6) Update the deal’s case file

### 5.2 Minimum change to achieve this (no rewrite)
Keep `sync_acquisition_emails.py` for IMAP + OCR + manifests, but add a **post-step**:
- For each new manifest, call the Deal Case Manager / ingestion gateway:
  - compute match confidence
  - quarantine if needed
  - emit events
  - schedule actions

---

## 6) Implementation Plan (Incremental, Low-Risk)

### Phase 0 — Contracts & “Spine First” (1–2 days)
Deliverables:
- Define stable schemas + canonical storage paths:
  - **Deal “case file”** (projection) at `/home/zaks/DataRoom/.deal-registry/case_files/{deal_id}.json`
  - **Event schemas** (validate on emit)
  - **Action schemas** (validate on schedule)
- Add **policy-as-code** (single automation truth source):
  - `/home/zaks/DataRoom/.deal-registry/policy/stage_policies.yaml`
  - stage `on_enter` actions, `on_document` triggers, stall thresholds, recurrence templates, approval gates
- Confirm authoritative sources:
  - **Deal registry + events** are authoritative
  - folders/views are derived (safe to rebuild)
- Ensure a “single query” status path exists (CLI or API) that returns:
  - stage + summary + next actions + alerts

Acceptance:
- A new operator can answer: “What’s the status of DEAL-X and what’s next?” via a single API or doc.

### Phase 0.5 — LLM Provider Abstraction (Optional, Recommended) (0.5–1 day)
Deliverables:
- Implement `LLMProvider` abstraction:
  - local vLLM (OpenAI-compatible) provider (baseline)
  - Gemini provider (opt-in)
- Define reliability rules:
  - fallback to local on cloud failure/timeouts
  - low-confidence results → quarantine (never silently “force match”)
- Enforce safe observability:
  - log provider/model + input hashes + short summaries (avoid raw sensitive content)

Acceptance:
- A single “classify document” call can run through Gemini and safely fall back to local.

### Phase 1 — Deal Case Manager Agent (2–4 days)
Deliverables:
- Implement `DealCaseManagerAgent` in `Zaks-llm/src/agents/dealflow/` as a role agent:
  - reads registry + events + quarantine + deferred actions (read-only where possible)
  - produces structured outputs + schedules actions (write via safe tool wrappers)
  - exposes explicit actions (not free-form tool sprawl): “ingest manifest”, “resolve quarantine”, “schedule follow-up”, “summarize deal”
  - strict tool surface (no raw shell, no arbitrary file writes, no outbound comms)
- Add Orchestrator routing to `deal_case_manager`.

Acceptance:
- Operator can ask ZakOps: “Summarize DEAL-2025-014 and schedule a 30-day follow-up” and see events + actions updated.

### Phase 2 — Ingestion → Events + Actions (2–3 days)
Deliverables:
- Integrate manifest processing into the lifecycle spine:
  - each manifest produces `email_received` + relevant document events
  - low-confidence matches go to quarantine with explicit resolution actions
  - schedule follow-ups based on stage/policy (e.g., request CIM after 2 days)

Acceptance:
- Every inbound email produces a deal-linked event or a quarantine item (no silent drops).

### Phase 3 — Underwriter + Diligence Agents (3–5 days)
Deliverables:
- Underwriter role agent:
  - converts extracted financials/CIM to structured facts + memo updates
  - schedules diligence actions
- Diligence coordinator:
  - maintains DD checklist and “missing docs” list
  - schedules reminders and deadlines

Acceptance:
- For a qualified deal, ZakOps can produce: financial quick-look, risks, questions, and a DD plan with scheduled reminders.

### Phase 4 — Portfolio Operator + Exit Strategist (as needed)
Deliverables:
- Portfolio operator cadence templates:
  - 30/60/90-day integration plan
  - quarterly KPI review reminders
  - annual strategy refresh
- Exit strategist (only once needed):
  - exit readiness checklist + value-maximization actions

Acceptance:
- A closed deal automatically enters a multi-year review cadence.

### Phase 5 — API + Dashboard (2–3 days)
Deliverables:
- Add operator-facing endpoints (read + controlled writes):
  - deals: list/get/events/case-file
  - actions: list/due/execute/cancel (approval-gated where needed)
  - quarantine: list/resolve
  - pipeline + alerts
- Minimum dashboard views:
  - stage funnel, stuck-deal alerts, due actions, quarantine inbox, agent activity log

Acceptance:
- Operator can manage lifecycle without folder spelunking.

### Phase 6 — Evaluation & Optimization (Ongoing)
Deliverables:
- Track quality + throughput metrics:
  - quarantine rate + resolution outcomes
  - classification accuracy (where ground truth exists)
  - time-in-stage, stall frequency, action execution success rate
- Add guardrail checks:
  - hallucination/citation adherence for RAG outputs
  - “no secrets in artifacts” scanning at critical boundaries

---

## 7) Guardrails (Non-Negotiables)
- **No secrets** in traces, datasets, docs, or SharePoint.
- **No outbound actions** without operator approval (draft-only for comms).
- **Approval gates** enforced for LOI / CLOSING / EXIT_PLANNING / CLOSED_WON.
- **Deterministic-first**: prefer policy + structured outputs over free-form “agent magic”.
- **Everything leaves an audit trail**: run-ledger + deal events + deferred action execution record.
- **No silent drops**: every inbound email is a deal event or quarantine item.
- **Strict tool surface** for lifecycle agents: no raw shell; no unrestricted file writes.

---

## 8) What This Plan Does NOT Do (Yet)
- Replace cron with Temporal/Dagster/Prefect.
- Build a full UI/CRM.
- Auto-send emails.
- Auto-move/mass-rename legacy folders without human review.

---

## 9) Operator Decisions Needed (Before Execution Starts)

1. Confirm stage list and naming (v1 in `/home/zaks/scripts/deal_state_machine.py`).
2. Confirm approval gates: LOI / CLOSING / EXIT_PLANNING / CLOSED_WON.
3. Confirm quarantine threshold and override policy rules.
4. Confirm whether Gemini is used for classification only vs extraction/underwriting.
5. Confirm canonical buy-box criteria location (policy-as-code vs case-file field vs separate config).

---

## 10) Next Step (Operator Choice)

Pick one:
1) **Start Phase 0 now**: define the deal “case file” schema + event/action contracts.
2) **Start Phase 1 now**: implement `DealCaseManagerAgent` and add it to the orchestrator routing.

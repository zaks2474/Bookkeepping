# ZakOps Deal Lifecycle OS — Unified Execution Plan

**Author**: Claude (AI Assistant), incorporating Codex contributions
**Date**: 2025-12-26
**Status**: DRAFT - Awaiting Operator Approval
**Goal**: Evolve ZakOps from "cron + scripts" into a deal-centric, lifecycle-aware, AI-assisted system that can run for **years per deal**—while reusing what already works and staying structurally compatible with world-class orchestration platforms.

---

## 0. Non-Negotiable Outcomes (Success Definition)

1. **Deal is the unit of work** (not a cron run)
2. **Every inbound email produces either:**
   - a deal-linked `email_received` event, **OR**
   - a `quarantine_added` item (no silent drops)
3. **Folders are derived views**, never the source of truth
4. **Deterministic-first**: policy + schemas drive behavior; agents recommend and draft, but do not "free-run"
5. **Approval gates** enforced for LOI / CLOSING / EXIT_PLANNING / CLOSED_WON
6. **Audit trail everywhere**: event log + run-ledger + action execution record

**Core Principle**: Prefer policy + structured outputs over free-form "agent magic."

---

## 1. Ground Truth: What Already Exists

### 1.1 Durable Spine (Reuse; Do Not Rebuild)

| Component | Location | Status |
|-----------|----------|--------|
| Deal Registry | `/home/zaks/DataRoom/.deal-registry/deal_registry.json` | Exists |
| Event Store | `/home/zaks/DataRoom/.deal-registry/events/*.jsonl` | Exists |
| State Machine | `/home/zaks/scripts/deal_state_machine.py` | Exists |
| Deferred Actions Queue | `/home/zaks/DataRoom/.deal-registry/deferred_actions.json` | Exists |
| Deferred Action Processor | `/home/zaks/scripts/process_deferred_actions.py` | Exists |
| Durable Checkpoints | `/home/zaks/DataRoom/.deal-registry/checkpoints/*.json` | Exists |
| AI Advisory Layer | `/home/zaks/scripts/deal_ai_advisor.py` | Exists |
| Quarantine | `/home/zaks/DataRoom/.deal-registry/quarantine.json` | Exists |
| Run Ledger | `/home/zaks/logs/run-ledger.jsonl` | Exists |
| Secret Scanning | `/home/zaks/scripts/zakops_secret_scan.py` | Exists |

**Directive**: Reuse these as the "workflow engine core." Any new component must write through this spine (events + actions), not around it.

### 1.2 Interactive Runtime (Already in Place)

| Agent | Location | Status |
|-------|----------|--------|
| OrchestratorAgent | `Zaks-llm/src/agents/orchestrator.py` | Active |
| SystemOps | `Zaks-llm/src/agents/systemops.py` | Active |
| RAGExpert | `Zaks-llm/src/agents/rag_expert.py` | Active |
| DealSourcing | `Zaks-llm/src/agents/deal_sourcing.py` | Active |
| Comms | `Zaks-llm/src/agents/comms.py` | Active (draft-only) |

**Directive**: Keep local vLLM as baseline and add a clean provider abstraction for Gemini.

### 1.3 What Still Feels Wrong

| Current State | Required State |
|---------------|----------------|
| Cron run is the unit of work | **Deal** is the unit of work |
| Agents are stateless utilities | Agents are **lifecycle roles** with memory |
| Email sync = file drop | Email = **business event** entering lifecycle |
| Folders are source of truth | Folders are **derived views**; registry is truth |
| Reactive (runs when triggered) | **Proactive** (schedules follow-ups, alerts on stalls) |

---

## 2. Target Architecture (5-Plane Model)

### 2.1 Architectural Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION PLANE                           │
│         API endpoints + Dashboard + CLI + Alerts                │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE PLANE                           │
│    Role Agents: Case Manager, Underwriter, Diligence,          │
│                 Portfolio Operator, Exit Strategist             │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     WORKFLOW PLANE                              │
│      Deferred Actions + Policy-as-Code + Action Processor       │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     CONTROL PLANE (TRUTH)                       │
│       Registry + Events + State Machine + Case Files            │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE PLANE (DERIVED)                     │
│          DataRoom Folders + SharePoint + Manifests              │
└─────────────────────────────────────────────────────────────────┘
```

**Key Principle**: Control Plane is truth. Storage Plane is derived. Never invert this.

### 2.2 Deal Lifecycle Stages (v1)

```
INBOUND ──▶ SCREENING ──▶ QUALIFIED ──▶ LOI ──▶ DILIGENCE ──▶ CLOSING
    │           │             │          │          │            │
    ▼           ▼             ▼          ▼          ▼            ▼
CLOSED_LOST CLOSED_LOST  CLOSED_LOST CLOSED_LOST CLOSED_LOST  CLOSED_LOST
                                                                 │
                                                                 ▼
                                         INTEGRATION ──▶ OPERATIONS ──▶ GROWTH
                                                                          │
                                                              ┌───────────┴───────────┐
                                                              ▼                       ▼
                                                        EXIT_PLANNING           (continue)
                                                              │
                                                              ▼
                                                         CLOSED_WON
```

**Approval-Required Transitions (Enforced)**:
- Entering `LOI`
- Entering `CLOSING`
- Entering `EXIT_PLANNING`
- Entering `CLOSED_WON`

### 2.3 Event-Driven Architecture

The platform treats these as first-class events:

| Event Type | Trigger | Typical Actions |
|------------|---------|-----------------|
| `deal_created` | New opportunity identified | Schedule initial follow-up |
| `email_received` | Inbound email matched to deal | Update case file, classify attachments |
| `document_attached` | File added to deal folder | Trigger classification |
| `document_classified` | AI/rules classify document | Update checklist, maybe advance stage |
| `stage_changed` | Deal transitions stages | Schedule stage-appropriate actions |
| `ai_recommendation` | Agent produces insight | Log to case file, maybe schedule action |
| `action_scheduled` | Future action queued | Visible in dashboard |
| `action_executed` | Deferred action fired | Log result, maybe schedule follow-up |
| `action_failed` | Action execution failed | Alert operator |
| `checkpoint_created` | Long operation saved progress | Enables resume on crash |
| `quarantine_added` | Low-confidence match | Needs operator resolution |
| `quarantine_resolved` | Operator resolved item | Link to deal or discard |

---

## 3. Contracts First (Schemas + Policy-as-Code)

### 3.1 Deal Case File Schema

**Location**: `/home/zaks/DataRoom/.deal-registry/case_files/{deal_id}.json`

**Critical Principle**: Case file is a **projection** derived from events + agent updates. It must be safe to rebuild from event history.

#### Projection Rebuild + Backfill (Required)

Case files only work operationally if they are:
- **rebuildable** (event log remains authoritative)
- **backfillable** (can generate case files for existing deals)
- **idempotent** (rebuild does not create duplicates or drift)

**Deliverables**:
- `rebuild_case_file(deal_id)` (single deal) and `rebuild_all_case_files()` (batch)
- `reapply_stage_policy(deal_id)` to (re)generate eligible deferred actions from `stage_policies.yaml` without duplicating existing scheduled actions
- `rebuild_from_events --since <timestamp>` for incremental rebuilds (useful after schema/policy upgrades)

```json
{
  "deal_id": "acme-corp-2025",
  "summary": "SaaS company, $2.1M ARR, 85% gross margin",
  "key_facts": {
    "revenue": "$2.1M ARR",
    "ebitda": "$420K",
    "industry": "B2B SaaS",
    "employees": 12,
    "location": "Austin, TX",
    "asking_price": "$6.5M",
    "broker": "FE International",
    "broker_contact": "john@feint.com"
  },
  "buy_box_fit": {
    "score": 78,
    "meets_criteria": ["revenue", "margin", "industry"],
    "concerns": ["customer_concentration"]
  },
  "open_questions": [
    "Customer concentration breakdown?",
    "Key employee retention plan?"
  ],
  "next_actions": [
    {"action": "request_customer_list", "due": "2025-01-20"},
    {"action": "schedule_management_call", "due": "2025-01-25"}
  ],
  "risk_flags": ["single_customer_40_pct"],
  "last_updated": "2025-01-15T14:30:00Z",
  "updated_by": "underwriter_agent"
}
```

### 3.2 Event Schemas (Validated on Write)

**Location**: `/home/zaks/DataRoom/.deal-registry/schemas/event_schemas.yaml`

```yaml
event_schemas:
  deal_created:
    required: [source, broker]
    optional: [initial_summary, broker_contact]

  email_received:
    required: [from, subject, date]
    optional: [attachments, classification, matched_by, message_id]

  document_attached:
    required: [filename, path]
    optional: [size_bytes, mime_type]

  document_classified:
    required: [filename, doc_type, confidence]
    optional: [extracted_data, classifier, model_used]

  stage_changed:
    required: [from_stage, to_stage, reason]
    optional: [approved_by, auto_triggered]

  ai_recommendation:
    required: [agent, recommendation_type, summary]
    optional: [confidence, supporting_data, suggested_actions, model_used]

  action_scheduled:
    required: [action_type, deal_id, due_date]
    optional: [condition, recurring, data]

  action_executed:
    required: [action_type, result]
    optional: [duration_ms, error, next_action]

  action_failed:
    required: [action_type, error]
    optional: [retry_scheduled, stack_trace]

  checkpoint_created:
    required: [operation, step]
    optional: [data, resumable]

  quarantine_added:
    required: [reason, email_subject, from]
    optional: [candidates, confidence, attachments]

  quarantine_resolved:
    required: [resolution]
    optional: [deal_id, resolved_by]
```

### 3.3 Action Schemas (Validated on Schedule)

**Location**: `/home/zaks/DataRoom/.deal-registry/schemas/action_schemas.yaml`

```yaml
action_schemas:
  follow_up:
    required: [follow_up_type]  # materials, response, call
    optional: [message_template, contact, days_until_escalate]

  run_agent:
    required: [agent, task]
    optional: [task_params, timeout_minutes]

  stage_review:
    required: []
    optional: [check_stall, auto_advance, alert_if_stuck]

  dd_progress_check:
    required: []
    optional: [checklist_focus, alert_threshold_pct]

  quarterly_review:
    required: []
    optional: [kpi_focus, compare_to_baseline]

  annual_strategy:
    required: []
    optional: [planning_horizon_years]

  integration_milestone_check:
    required: [milestone_day]  # 30, 60, 90
    optional: [checklist_items]

  loi_expiration_warning:
    required: [expiration_date]
    optional: [days_before_alert]
```

### 3.4 Policy-as-Code (Single Source for Automation Rules)

**Location**: `/home/zaks/DataRoom/.deal-registry/policy/stage_policies.yaml`

```yaml
# Stage Policies - Drives all automation behavior
# Rule: Agents can suggest, but POLICY decides what auto-schedules

stage_policies:
  INBOUND:
    on_enter:
      - action: schedule_follow_up
        delay_days: 7
        type: request_materials
    on_document:
      CIM:
        advance_to: SCREENING
        schedule: initial_analysis
      TEASER:
        schedule: preliminary_review
    stall_alert_days: 14

  SCREENING:
    on_enter:
      - action: run_agent
        agent: underwriter
        task: initial_analysis
    on_analysis_complete:
      advance_to: QUALIFIED
      requires_approval: false
    stall_alert_days: 21

  QUALIFIED:
    on_enter:
      - action: schedule_follow_up
        delay_days: 14
        type: loi_discussion
    stall_alert_days: 30

  LOI:
    requires_approval: true
    on_enter:
      - action: schedule_action
        type: loi_expiration_warning
        delay_days: 25
      - action: run_agent
        agent: diligence_coordinator
        task: prepare_dd_checklist
    stall_alert_days: 45

  DILIGENCE:
    on_enter:
      - action: run_agent
        agent: diligence_coordinator
        task: initialize_checklist
      - action: schedule_recurring
        type: dd_progress_check
        frequency: weekly
    stall_alert_days: 60

  CLOSING:
    requires_approval: true
    on_enter:
      - action: schedule_follow_up
        delay_days: 7
        type: closing_checklist_review
    stall_alert_days: 30

  INTEGRATION:
    on_enter:
      - action: run_agent
        agent: portfolio_operator
        task: initialize_integration_plan
      - action: schedule_action
        type: integration_milestone_check
        milestone_day: 30
        delay_days: 30
      - action: schedule_action
        type: integration_milestone_check
        milestone_day: 60
        delay_days: 60
      - action: schedule_action
        type: integration_milestone_check
        milestone_day: 90
        delay_days: 90

  OPERATIONS:
    on_enter:
      - action: schedule_recurring
        type: quarterly_review
        frequency: quarterly
      - action: schedule_recurring
        type: annual_strategy
        frequency: yearly

  GROWTH:
    on_enter:
      - action: schedule_recurring
        type: quarterly_review
        frequency: quarterly

  EXIT_PLANNING:
    requires_approval: true
    on_enter:
      - action: run_agent
        agent: exit_strategist
        task: assess_exit_readiness

  CLOSED_WON:
    requires_approval: true
    terminal: true

  CLOSED_LOST:
    terminal: true
    on_enter:
      - action: run_agent
        agent: case_manager
        task: generate_post_mortem

# Global settings
global:
  quarantine_confidence_threshold: 0.70
  default_stall_alert_days: 30
  max_follow_up_attempts: 3
```

---

## 4. LLM Strategy (Local + Gemini, Swap Without Refactor)

### 4.1 Provider Abstraction (Mandatory)

**Location**: `/home/zaks/Zaks-llm/src/core/llm_provider.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    confidence: Optional[float] = None
    token_count: Optional[int] = None
    cost_estimate: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None

class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def invoke(self, prompt: str, system_prompt: str = None,
               temperature: float = 0.7, max_tokens: int = 4096) -> LLMResponse:
        pass

    @abstractmethod
    def classify(self, content: str, categories: list[str],
                 context: str = None) -> tuple[str, float]:
        """Classify content into one of the categories. Returns (category, confidence)."""
        pass

    @abstractmethod
    def extract_structured(self, content: str, schema: dict) -> dict:
        """Extract structured data according to schema."""
        pass

class LocalOpenAICompatibleProvider(LLMProvider):
    """Provider for local vLLM (Qwen2.5-32B-Instruct-AWQ)."""

    def __init__(self, base_url: str = "http://localhost:8000/v1",
                 model: str = "Qwen/Qwen2.5-32B-Instruct-AWQ"):
        self.base_url = base_url
        self.model = model
        # ... implementation

class GeminiProvider(LLMProvider):
    """Provider for Google Gemini API."""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-pro"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        # ... implementation

class LLMRouter:
    """Routes tasks to appropriate provider based on task type."""

    def __init__(self, local: LLMProvider, cloud: LLMProvider = None):
        self.local = local
        self.cloud = cloud
        self.task_routing = {
            "classification": "cloud",      # Gemini for classification
            "extraction": "cloud",          # Gemini for structured extraction
            "reasoning": "local",           # Local for complex reasoning
            "summarization": "local",       # Local for summaries
            "draft_generation": "local",    # Local for drafts
            "routing": "local",             # Local for orchestration
        }

    def get_provider(self, task_type: str) -> LLMProvider:
        preference = self.task_routing.get(task_type, "local")
        if preference == "cloud" and self.cloud:
            return self.cloud
        return self.local

    def invoke_with_fallback(self, task_type: str, prompt: str, **kwargs) -> LLMResponse:
        """Try preferred provider, fall back on failure."""
        provider = self.get_provider(task_type)
        try:
            return provider.invoke(prompt, **kwargs)
        except Exception as e:
            if provider != self.local:
                # Fall back to local
                logger.warning(f"Cloud provider failed, falling back to local: {e}")
                return self.local.invoke(prompt, **kwargs)
            raise
```

### 4.2 Task-to-Model Mapping (Recommended)

| Task Type | Preferred Provider | Rationale |
|-----------|-------------------|-----------|
| Document classification | Gemini (cloud) | High accuracy, narrow scope |
| Structured extraction | Gemini (cloud) | Better at schema adherence |
| Email/attachment understanding | Gemini (cloud) | Multimodal capabilities |
| Orchestration reasoning | Local vLLM | Cost/latency control |
| Summaries | Local vLLM | High volume, good enough quality |
| Draft generation | Local vLLM | Iterative, needs low latency |
| Routing decisions | Local vLLM | Fast, deterministic preferred |

### 4.3 Reliability / Fallback Rules

```python
FALLBACK_POLICY = {
    "cloud_timeout_seconds": 30,
    "cloud_retry_attempts": 2,
    "fallback_to_local": True,
    "quarantine_on_low_confidence": True,
    "low_confidence_threshold": 0.70,
}
```

**Rules**:
1. If Gemini fails/timeouts → fall back to local for "best-effort" + quarantine if low-confidence
2. Every LLM call must log:
   - `model` / `provider`
   - `input_hash` (not raw content if sensitive)
   - `output_summary`
   - `confidence`
   - `token_count` / `cost_estimate` if available
3. Never block on cloud failure - always have local fallback path

### 4.4 Configuration

**Location**: `/home/zaks/Zaks-llm/.env` (secrets) + `/home/zaks/Zaks-llm/config/llm_config.yaml` (routing)

```yaml
# llm_config.yaml
providers:
  local:
    type: openai_compatible
    base_url: http://vllm-qwen:8000/v1  # inside docker; use http://localhost:8000/v1 when running on host
    model: Qwen/Qwen2.5-32B-Instruct-AWQ
    enabled: true

  gemini:
    type: gemini
    model: gemini-1.5-pro
    enabled: true  # Set false to disable cloud

routing:
  classification: gemini
  extraction: gemini
  reasoning: local
  summarization: local
  draft_generation: local

fallback:
  enabled: true
  timeout_seconds: 30
  quarantine_low_confidence: true
```

### 4.5 Tracing, Evaluation, and Agent Builder (Optional but High Leverage)

This plan can be implemented fully without any cloud observability. If you enable LangSmith, do it in **safe mode** only:
- Inputs/outputs hidden by default; only metadata (deal_id, agent, stage, model/provider, hashes)
- No secrets in traces (secret scanning remains enforced on artifacts)

Recommended approach:
- Use **LangSmith Agent Builder** to iterate on prompts, tool surfaces, and structured schemas.
- Deploy only the **exported, versioned** prompt/tool configs into the runtime (do not make runtime depend on the builder UI).
- Keep an **offline eval path** (golden datasets + local eval runner) so the platform works without network access.

Reference: `/home/zaks/bookkeeping/docs/LANGSMITH-SAFE-TRACING.md`

---

## 5. Role-Based Agent Model

### 5.1 Design Principles

Agents must:
- Load deal context (registry + events + case file + doc inventory)
- Produce **structured outputs** (events + scheduled actions + case_file updates)
- **Never execute irreversible actions** without explicit approval
- Prefer deterministic policy over free-form decisions
- Log all invocations to run-ledger

### 5.2 Strict Allowed Actions (Tool Surface)

Agents can ONLY request actions from this curated set:

```python
ALLOWED_AGENT_ACTIONS = [
    "emit_event",              # Add event to deal's event log
    "update_case_file",        # Update case file projection
    "schedule_action",         # Queue a deferred action
    "recommend_stage_transition",  # Suggest (not execute) stage change
    "create_checkpoint",       # Save progress for long operations
    "create_draft",            # Comms agent only - create draft artifact
    "add_open_question",       # Add question to case file
    "add_risk_flag",           # Flag a risk in case file
    "request_additional_info", # Log info request (doesn't send)
]

# Explicitly forbidden:
# - No raw shell execution
# - No arbitrary file writes
# - No direct outbound email
# - No stage transitions without approval (for gated stages)
```

### 5.3 Agent Roster (v1)

| Agent | Mission | Inputs | Outputs | Hard Boundaries |
|-------|---------|--------|---------|-----------------|
| **Deal Case Manager** (NEW) | "Keep deal moving." Convert events into next actions; update case file; suggest stage transitions | New emails, doc arrivals, operator notes, due deferred-actions | Deal events, stage transitions, deferred actions, case-file summary | No sending emails, no destructive ops |
| **Underwriter** (NEW) | "Turn docs into financial picture." Extract metrics, buy-box score, risks, questions | Extracted docs + RAG + buy-box criteria | Analysis artifacts + `ai_recommendation` events | No LOI/price commitments without approval |
| **Diligence Coordinator** (NEW) | "Run DD playbook." Maintain checklist, missing docs, reminders, deadlines | Registry + doc inventory + events | Deferred actions + DD checklist artifacts + events | No contacting counterparties directly |
| **Portfolio Operator** (NEW) | "Post-close cadence." 30/60/90, quarterly KPI review, annual strategy | Events + scheduled actions | Deferred actions + ops artifacts + events | Never changes production systems |
| **Exit Strategist** (NEW, later) | "Exit readiness." Only invoked at EXIT_PLANNING stage | Deal context at EXIT_PLANNING | Exit plan artifacts + events | Advisory only |
| **Comms** (existing) | Produce drafts for operator approval | Deal context + operator intent | Draft artifacts only | **Never send** |
| **RAG Expert** (existing) | Grounded retrieval, summaries | RAG tools | Summaries, citations | Don't hallucinate sources |
| **SystemOps** (existing) | System maintenance, diagnostics | System state | Commands, reports | Safety-gated |
| **Deal Sourcing** (existing) | Lead generation, broker research | External sources | Lead lists | No outreach without approval |

### 5.4 Agent Invocation Pattern

```python
def invoke_role_agent(agent_name: str, deal_id: str, task: str,
                      llm_router: LLMRouter = None) -> AgentResult:
    """Standard pattern for invoking any role agent."""

    # 1. Load full deal context
    context = load_deal_context(deal_id)
    stage = get_deal_stage(deal_id)

    # 2. Get stage-appropriate system prompt
    system_prompt = get_agent_prompt(agent_name, stage)

    # 3. Build structured input
    agent_input = {
        "deal": context.deal,
        "recent_events": context.events[-50:],
        "case_file": context.case_file,
        "task": task,
        "allowed_actions": ALLOWED_AGENT_ACTIONS,
        "stage_policy": get_stage_policy(stage),
    }

    # 4. Select LLM provider based on task
    task_type = get_task_type(agent_name, task)
    provider = llm_router.get_provider(task_type) if llm_router else get_default_provider()

    # 5. Invoke with tracing
    with trace_context(deal_id=deal_id, agent=agent_name, model=provider.model):
        result = agent.invoke(agent_input, system_prompt=system_prompt, llm=provider)

    # 6. Validate and process structured output
    validate_agent_output(result, ALLOWED_AGENT_ACTIONS)

    for event in result.events:
        emit_event(deal_id, event.type, event.data, source=agent_name)

    for action in result.scheduled_actions:
        schedule_action(deal_id, action)

    if result.case_file_update:
        update_case_file(deal_id, result.case_file_update)

    # 7. Log to run ledger
    log_run(
        agent=agent_name,
        deal_id=deal_id,
        task=task,
        model=provider.model,
        result_summary=result.summary,
        confidence=result.confidence
    )

    return result
```

---

## 6. Email → Lifecycle: Minimum Rewrite, Maximum Shift

### 6.1 Keep Current Fetcher, Add Lifecycle Post-Step

**Keep**: `sync_acquisition_emails.py` for IMAP + attachments + OCR + manifest generation

**Add**: Post-ingest event emitter (integrate into script or as separate module)

```python
def process_email_lifecycle(email, attachments, manifest_path):
    """Post-step: Convert email into lifecycle events."""

    # 1. Match to deal (rules + optional Gemini assistance)
    match_result = match_email_to_deal(email, llm_router)

    # 2. Quarantine if low confidence
    if match_result.confidence < QUARANTINE_THRESHOLD:
        quarantine_id = add_to_quarantine(
            email=email,
            attachments=attachments,
            match_candidates=match_result.candidates,
            reason="low_confidence_match"
        )
        emit_event(None, "quarantine_added", {
            "quarantine_id": quarantine_id,
            "email_subject": email.subject,
            "from": email.sender,
            "candidates": match_result.candidates,
            "confidence": match_result.confidence
        })
        return  # STOP - needs human resolution

    deal_id = match_result.deal_id
    is_new_deal = match_result.is_new

    # 3. Create deal if new
    if is_new_deal:
        deal_id = create_deal(
            source="email",
            broker=extract_broker(email),
            initial_summary=extract_summary(email)
        )
        emit_event(deal_id, "deal_created", {
            "source": "email_sync",
            "broker": email.sender,
            "subject": email.subject
        })

    # 4. Emit email_received event
    emit_event(deal_id, "email_received", {
        "from": email.sender,
        "subject": email.subject,
        "date": email.date.isoformat(),
        "attachments": [a.filename for a in attachments],
        "message_id": email.message_id
    })

    # 5. Process and classify attachments
    for attachment in attachments:
        emit_event(deal_id, "document_attached", {
            "filename": attachment.filename,
            "size_bytes": attachment.size,
            "path": attachment.saved_path
        })

        # Classify (prefer Gemini)
        doc_type, confidence = classify_document(attachment, llm_router)

        emit_event(deal_id, "document_classified", {
            "filename": attachment.filename,
            "doc_type": doc_type,
            "confidence": confidence,
            "classifier": llm_router.last_provider
        })

        # 6. Apply stage policy based on document type
        apply_document_policy(deal_id, doc_type)

    # 7. Schedule follow-ups based on current stage
    schedule_stage_actions(deal_id)

    # 8. Invoke Case Manager to update case file
    invoke_role_agent("case_manager", deal_id, "process_new_email")
```

### 6.2 Quarantine as First-Class UX

Quarantine must be resolvable via:
- **CLI**: `python3 quarantine.py resolve <id> --action link --deal-id <deal>`
- **API**: `POST /api/quarantine/{id}/resolve`
- **Dashboard**: One-click resolution with deal picker

**Resolution Options**:
```python
def resolve_quarantine(quarantine_id: str, resolution: str, deal_id: str = None,
                       resolved_by: str = "operator"):
    """
    resolution: "link_to_deal" | "create_new_deal" | "discard"
    """
    item = get_quarantine_item(quarantine_id)

    if resolution == "link_to_deal":
        if not deal_id:
            raise ValueError("deal_id required for link_to_deal")
        process_quarantined_email(item, deal_id)
        emit_event(deal_id, "quarantine_resolved", {
            "quarantine_id": quarantine_id,
            "resolution": "linked",
            "resolved_by": resolved_by
        })

    elif resolution == "create_new_deal":
        deal_id = create_deal_from_quarantine(item)
        process_quarantined_email(item, deal_id)
        emit_event(deal_id, "quarantine_resolved", {
            "quarantine_id": quarantine_id,
            "resolution": "new_deal_created",
            "resolved_by": resolved_by
        })

    elif resolution == "discard":
        emit_event(None, "quarantine_resolved", {
            "quarantine_id": quarantine_id,
            "resolution": "discarded",
            "resolved_by": resolved_by,
            "reason": item.get("discard_reason", "not_relevant")
        })

    remove_from_quarantine(quarantine_id)
```

### 6.3 Email Idempotency + Deduplication (Required)

Email ingestion must be safe under cron retries, overlapping runs, and replays.

**Rules**:
1. Use RFC `message_id` as the primary idempotency key (when present).
2. If `message_id` is missing, compute a stable fallback key (e.g., hash of `from|date|subject|body_hash`).
3. Persist a dedupe ledger (append-only) and check it **before emitting any events**.
4. Attachment events must also be idempotent (hash content + filename), so the same PDF does not emit duplicate `document_attached`/`document_classified`.

Suggested storage:
- `/home/zaks/DataRoom/.deal-registry/dedupe/processed_emails.jsonl` (append-only; keys + timestamps + manifest_path)
- `/home/zaks/DataRoom/.deal-registry/dedupe/processed_attachments.jsonl` (append-only; sha256 + first_seen + deal_id)

---

## 7. Orchestration: Cron as Heartbeat, Actions as Workflow

### 7.1 Cron Purpose (Redefined)

Cron should ONLY:
1. Process due deferred actions
2. Scan for new events/manifests needing processing
3. Run health checks (and alert)

```cron
# /etc/cron.d/dataroom-automation

# Process deferred actions - every hour
0 * * * * zaks python3 /home/zaks/scripts/process_deferred_actions.py >> /home/zaks/logs/deferred_actions_cron.log 2>&1

# Scan for unprocessed manifests - every 15 minutes
*/15 * * * * zaks python3 /home/zaks/scripts/process_pending_manifests.py >> /home/zaks/logs/manifest_processor.log 2>&1

# Health check + alerts - every 30 minutes
*/30 * * * * zaks python3 /home/zaks/scripts/lifecycle_health_check.py >> /home/zaks/logs/health_check.log 2>&1
```

### 7.2 Idempotency (Required)

Every action execution MUST be idempotent (safe to retry):

```python
def execute_action_idempotent(action_id: str) -> ActionResult:
    """Execute action with idempotency guarantees."""

    # 1. Check if already executed
    if is_action_completed(action_id):
        return ActionResult(status="already_completed", skipped=True)

    # 2. Check if in-progress (another worker)
    if not acquire_action_lock(action_id):
        return ActionResult(status="locked", skipped=True)

    try:
        # 3. Load action details
        action = get_action(action_id)

        # 4. Check conditions still valid
        if not check_action_conditions(action):
            mark_action_skipped(action_id, reason="conditions_not_met")
            return ActionResult(status="skipped", reason="conditions_not_met")

        # 5. Execute with checkpoint
        checkpoint_id = create_checkpoint(action.deal_id, f"action_{action_id}")

        result = execute_action_handler(action)

        # 6. Mark completed + emit event
        mark_action_completed(action_id, result)
        emit_event(action.deal_id, "action_executed", {
            "action_id": action_id,
            "action_type": action.type,
            "result": result.summary
        })

        # 7. Schedule follow-up if recurring
        if action.recurring:
            schedule_next_occurrence(action)

        clear_checkpoint(checkpoint_id)
        return result

    except Exception as e:
        emit_event(action.deal_id, "action_failed", {
            "action_id": action_id,
            "action_type": action.type,
            "error": str(e)
        })
        # Don't mark completed - will retry on next run
        raise

    finally:
        release_action_lock(action_id)
```

### 7.3 Feature Flags / Kill Switches (Required)

To roll out safely without destabilizing what already works, add explicit flags:
- `DFP_LIFECYCLE_ENABLED` (master switch)
- `DFP_MANIFEST_PROCESSOR_ENABLED` (post-ingest event emitter)
- `DFP_AUTO_SCHEDULE_ENABLED` (policy auto-scheduling)
- `DFP_AUTO_STAGE_SUGGESTIONS_ENABLED` (allow stage *recommendations* only)
- `DFP_ACTION_EXECUTION_ENABLED` (deferred action processor execution; supports dry-run)
- `DFP_CLOUD_LLM_ENABLED` (Gemini provider)

**Rule**: Default to safe/off where behavior changes are irreversible or can cause spam/duplicate work.

### 7.4 Retention, Backup, and Restore (Required for “Years-Long” Operation)

Define and implement retention policies early so the system stays healthy over years:
- **Event logs** (`events/*.jsonl`): keep indefinitely; optionally compress older files (never delete without archive).
- **Run ledger** (`run-ledger.jsonl`): rotate + compress; keep a long tail (e.g., 90–180 days) plus aggregated metrics.
- **Checkpoints** (`checkpoints/*.json`): prune stale checkpoints (keep last N per deal or last X days).
- **Quarantine**: archive resolved items (do not grow unbounded).

Deliverables:
- A `backup_and_rotate.py` job (dry-run capable) plus a documented restore procedure.

---

## 8. API + Dashboard (Operator Control Plane)

### 8.1 Required API Endpoints

**Deals**
```
GET  /api/deals                      # List all (filter: ?stage=&broker=&age_gt=)
GET  /api/deals/{id}                 # Full deal with case file
GET  /api/deals/{id}/events          # Event history
GET  /api/deals/{id}/case-file       # Current case file
POST /api/deals/{id}/transition      # Stage transition (body: {to_stage, reason, approved_by})
POST /api/deals/{id}/note            # Add operator note (emits event)
```

**Actions**
```
GET  /api/actions                    # All scheduled actions
GET  /api/actions/due                # Due now
POST /api/actions/{id}/execute       # Manual trigger
POST /api/actions/{id}/cancel        # Cancel scheduled action
```

**Quarantine**
```
GET  /api/quarantine                 # Items needing resolution
GET  /api/quarantine/{id}            # Single item details
POST /api/quarantine/{id}/resolve    # Resolve item
```

**Pipeline**
```
GET  /api/pipeline                   # Summary by stage with counts/ages
GET  /api/alerts                     # Stuck deals, due actions, expiring items
```

**Agents**
```
POST /api/agents/{name}/invoke       # Manual agent invocation
GET  /api/agents/{name}/history      # Recent invocations
```

### 8.2 Dashboard Requirements (Minimum Viable)

**Location**: `/home/zaks/DataRoom/_dashboard/index.html`

Required components:
- **Pipeline funnel**: Count + average age per stage
- **Stuck deal alerts**: Deals exceeding 2x typical stage duration
- **Due actions list**: Actions due today/overdue
- **Quarantine inbox**: Items needing resolution
- **Quick actions**: Transition / Schedule / Resolve buttons
- **Agent activity log**: Recent agent invocations with outcomes

### 8.3 API Security + Approval Semantics (Required)

Minimum requirements before any non-local exposure:
- Bind to `localhost` by default; if remote access is needed, place behind an authenticated reverse proxy.
- Treat `approved_by` as an **audited operator identity** (record in `stage_changed` events).
- Enforce approval-required transitions in the state machine even if the API is misused.
- Avoid returning raw email bodies/attachments by default (return paths/hashes/metadata unless explicitly requested).

---

## 9. Execution Phases (Deliverables + Acceptance)

### Phase 0 — Contracts & Spine Validation (1 day)

**Deliverables**:
- Case file schema + storage path created
- Event schemas + action schemas as YAML
- Stage policies YAML (initial version)
- Validators implemented for event/action payloads
- CLI: `python3 deal_registry.py status <deal_id>` returns stage, summary, next actions

**Acceptance**:
- [ ] A new operator can answer "What's the status and what's next?" from one command
- [ ] Invalid events/actions are rejected with clear error messages
- [ ] Schema files exist at specified paths

---

### Phase 0.5 — LLM Provider Abstraction + Gemini (0.5-1 day)

**Deliverables**:
- `LLMProvider` abstraction implemented
- `LocalOpenAICompatibleProvider` working
- `GeminiProvider` working (if API key available)
- `LLMRouter` with task-to-model mapping
- Safe logging (no raw content, just hashes/summaries)
- Fallback logic tested

**Acceptance**:
- [ ] A classification call can run through Gemini and fall back to local safely
- [ ] LLM calls are logged with model, confidence, token count
- [ ] Config toggle can disable cloud provider

---

### Phase 1 — Deal Case Manager Agent (2-3 days)

**Deliverables**:
- `DealCaseManagerAgent` implemented with strict allowed actions
- Orchestrator routing to case manager
- CLI: `summarize` / `process-events` / `suggest-actions`
- Integration with LLM router

**Acceptance**:
- [ ] "Summarize DEAL-X and schedule a 30-day follow-up" emits events + creates action
- [ ] Case file is updated after agent invocation
- [ ] Agent respects allowed actions (rejects unauthorized)

---

### Phase 2 — Ingestion → Events + Actions (2 days)

**Deliverables**:
- Post-ingest event emitter wired into email sync
- Document classification using LLM router (Gemini preferred)
- Quarantine creation for low-confidence matches
- Quarantine resolution (CLI + API)
- "No silent drops" invariant enforced

**Acceptance**:
- [ ] Every email becomes deal-linked event OR quarantine item
- [ ] Documents are classified on arrival
- [ ] Stage policies auto-trigger (CIM → SCREENING)
- [ ] Quarantine resolution works via CLI

---

### Phase 3 — Underwriter + Diligence Coordinator (3-4 days)

**Deliverables**:
- `UnderwriterAgent`: financial memo + buy-box score + risks + questions
- `DiligenceCoordinatorAgent`: checklist initialization + progress tracking
- Stage-triggered invocation (SCREENING → Underwriter, DILIGENCE → Coordinator)
- Weekly DD progress checks scheduled

**Acceptance**:
- [ ] Underwriter produces structured analysis with confidence scores
- [ ] DD checklist created when deal enters DILIGENCE
- [ ] Missing items and deadlines tracked
- [ ] Weekly progress checks scheduled automatically

---

### Phase 5 — API + Dashboard (2 days)

> **Note**: Phase 5 before Phase 4 is intentional. Get visibility before expanding multi-year cadence.

**Deliverables**:
- REST endpoints implemented (all from Section 8.1)
- Dashboard shows pipeline, alerts, due actions, quarantine
- Quick actions functional (transition, schedule, resolve)
- Agent activity log visible

**Acceptance**:
- [ ] Operator can manage lifecycle without folder spelunking
- [ ] Pipeline view shows all deals by stage with age indicators
- [ ] Stuck deals highlighted
- [ ] One-click stage transitions with approval prompts

---

### Phase 4 — Portfolio Operator + Exit Strategist (2-3 days)

**Deliverables**:
- `PortfolioOperatorAgent`: 30/60/90 integration, quarterly reviews, annual strategy
- `ExitStrategistAgent`: exit readiness assessment (invoked at EXIT_PLANNING)
- Recurring action templates for multi-year cadence
- Integration milestone tracking

**Acceptance**:
- [ ] Closed deal automatically enters multi-year review cadence
- [ ] 30/60/90 milestones tracked in INTEGRATION
- [ ] Quarterly reviews fire for OPERATIONS deals
- [ ] Exit Strategist invocable at EXIT_PLANNING

---

### Phase 6 — Evaluation & Optimization (Ongoing)

**Deliverables**:
- Classification accuracy tracking (quarantine rate, resolution outcomes)
- Per-stage throughput metrics (time in stage, conversion rates)
- Quality audits (hallucination checks, RAG citation adherence)
- Cost tracking (LLM token usage, cloud vs local ratio)
- Offline eval runner + golden datasets (local-first) so quality can be measured without cloud access

**Acceptance**:
- [ ] Dashboard shows classification accuracy over time
- [ ] Stage duration anomalies are flagged
- [ ] Monthly quality audit report generated
- [ ] Cost per deal tracked

---

## 10. Guardrails (Must Be Enforced in Code)

| Rule | Implementation | Enforced In |
|------|----------------|-------------|
| No secrets in outputs | `zakops_secret_scan.py` gates all artifacts | Event emitter, file writers |
| Draft-only outbound comms | Comms agent cannot access send functions | Agent allowed actions |
| Approval gates for critical stages | State machine rejects unapproved transitions | `deal_state_machine.py` |
| Deterministic-first | Policy files drive behavior, not agent decisions | Stage policies YAML |
| Full audit trail | Every action → event + run-ledger | All action handlers |
| No silent drops | Email → event OR quarantine | Email processor |
| Email dedupe | `message_id`/hash ledger + attachment hashing | Email processor + event emitter |
| Idempotent actions | Lock + checkpoint + completion check | Action processor |
| LLM fallback | Cloud failure → local + quarantine if low-confidence | LLM router |
| Safe tracing (if enabled) | Hide inputs/outputs; log metadata only | Tracing layer + agent invocations |
| Retention/backup | Rotation + archive + restore procedure | Ops job + runbooks |

---

## 11. What This Plan Does NOT Do (Yet)

- Replace cron with Temporal/Dagster/Prefect (cron is heartbeat, not orchestrator)
- Build a full UI/CRM (dashboard is read + quick actions only)
- Auto-send emails (always draft-only)
- Auto-move/mass-rename legacy folders without human review
- Integrate external CRM/deal platforms
- Multi-tenant support

---

## 12. Operator Decisions Needed (Before Execution Starts)

1. **Confirm stage list and naming** (v1 recommended: 12 stages)
2. **Confirm approval gates** (LOI, CLOSING, EXIT_PLANNING, CLOSED_WON)
3. **Confirm quarantine threshold** (default 0.70)
4. **Confirm Gemini usage**:
   - Classification only?
   - Extraction + classification?
   - Full underwriting assistance?
5. **Confirm buy-box criteria location** (config file vs case file field)
6. **Gemini API key available?** (affects Phase 0.5)

---

## 13. Execution Order Summary

**Implement in this exact order**:

```
Phase 0   → Contracts & Spine Validation (schemas, validators, CLI)
Phase 0.5 → LLM Provider Abstraction + Gemini adapter
Phase 1   → Deal Case Manager Agent
Phase 2   → Ingestion → Events + Actions
Phase 3   → Underwriter + Diligence Coordinator
Phase 5   → API + Dashboard (visibility before expansion)
Phase 4   → Portfolio Operator + Exit Strategist
Phase 6   → Evaluation & Optimization (ongoing)
```

**Definition of "done" for each phase**: The acceptance criteria checkboxes above.

---

**Document Status**: Ready for operator review and approval.

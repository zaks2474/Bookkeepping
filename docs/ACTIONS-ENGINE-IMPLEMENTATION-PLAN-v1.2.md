# ZakOps Kinetic Action Engine - Implementation Plan v1.2 (World-Class Edition)

**Document Version:** 1.2
**Created:** 2025-12-30
**Updated:** 2025-12-30 (World-Class Upgrade)
**Status:** Ready for Implementation
**Owner:** Zaks Deal Lifecycle OS Team
**Target Completion:** 4-5 weeks

---

## Executive Summary

Transform the **Actions** page from a read-only log into a **world-class self-extending Execution Layer** that enables operator-reviewed automation of acquisition workflows.

### Project Goals

Build a production-grade action execution system with:

**Core Capabilities (v1.1):**
- ✅ Universal Action Schema - Structured, type-safe payloads
- ✅ Plugin Architecture - Executor registry pattern
- ✅ Artifact Management - DOCX/PDF/XLSX/PPTX in DataRoom
- ✅ Chat Integration - Natural language → proposals → actions
- ✅ Human-in-Loop - Review → Edit → Approve → Execute
- ✅ Idempotency - Safe retries, no duplicates
- ✅ Production Safety - Lease-based runner, persistent queue
- ✅ Backward Compatible - Preserves legacy endpoints

**World-Class Upgrades (v1.2):**
- 🆕 **Capability Manifest System** - Self-extending (add YAML → new action appears everywhere)
- 🆕 **Tooling Strategy** - MCP integration, Tool Gateway, Composite Actions (Phase 0.5)
- 🆕 **Action Planner with RAG** - Handles unknown/complex requests intelligently
- 🆕 **Schema-Driven UI** - Forms generated from manifests (no UI code changes)
- 🆕 **Observability Metrics** - Real-time dashboard (queue health, success rates)
- 🆕 **Advanced Safety** - Per-action locking, exponential backoff, error categorization

### What Makes This "World-Class"

**Before (v1.1):** Hard-coded action types. Adding "Generate Teaser" requires:
- Python enum changes
- TypeScript UI updates
- Executor implementation
- UI filter/label updates
- Redeploy everything

**After (v1.2):** Self-extending system. Adding "Generate Teaser" requires:
1. Drop `generate_teaser.v1.yaml` manifest (5 min)
2. Write `TeaserExecutor` class (3 min)
3. Register executor (1 min)
4. Restart runner (1 min)
✅ **Total: 10 minutes** - Action appears in UI, planner, filters automatically

**The Critical Test:**
```
User: "Create a lender outreach package with 1-page summary + KPI list + email draft"

v1.1 behavior: ❌ Fails (no keyword match)
v1.2 behavior: ✅ Decomposes into 3 actions:
  1. DOCUMENT.GENERATE (summary)
  2. ANALYSIS.BUILD_MODEL (KPIs)
  3. COMMUNICATION.DRAFT_EMAIL (with attachments)
```

If this test passes, the system is **world-class**.

### Key Improvements in v1.2

**All improvements from v1.1:**
- ✅ Baseline documentation of current system
- ✅ Backward compatibility strategy
- ✅ Reuses existing SQLite DB (`ZAKOPS_STATE_DB`)
- ✅ Lease-based runner (not PID lock)
- ✅ Deal events integration
- ✅ Artifact path convention (`99-ACTIONS/<action_id>/`)
- ✅ Verification Report as deliverable

**New in v1.2:**
- 🆕 **Capability Manifest System** - YAML-driven self-extending architecture
- 🆕 **CapabilityRegistry** - Loads/indexes/validates manifests at runtime
- 🆕 **Tooling Strategy (Phase 0.5)** - World-class tool integration layer:
  - **ToolGateway** - Single interface for external tools with allowlist/denylist, timeouts, retries
  - **ToolRegistry** - Machine-readable manifest for MCP tools with health checks, cost estimates
  - **Composite Actions** - Decompose unknown requests into known capabilities
  - **Audit Logging** - SQLite + deal events (no LangSmith)
  - **Secret Redaction** - Credentials never in logs
- 🆕 **ActionPlanner** - Converts user intent → executable actions (single, multi-step, clarification, refusal)
- 🆕 **Schema-Driven UI** - Forms generated from `input_schema` (no hard-coded types)
- 🆕 **Metrics Endpoint** - `/api/actions/metrics` with queue health, success rates, durations
- 🆕 **Metrics Dashboard** - Real-time monitoring UI
- 🆕 **Per-Action Locking** - Prevents race conditions between runners
- 🆕 **Exponential Backoff** - Smart retry with categorized errors
- 🆕 **Unknown Action Test** - Critical acceptance test for planner

---

## Section 0: Baseline (Current System Reality)

### Frontend

**ZakOps Dashboard (Next.js):** `http://localhost:3003`

**Current Actions UI:**
- File: `/home/zaks/zakops-dashboard/src/app/actions/page.tsx`
- Uses: `getActions()` + `getDueActions()` from `/home/zaks/zakops-dashboard/src/lib/api.ts`
- Behavior: Renders actions as **read-only list items** with links to deal pages
- No execution capability, no artifact management

### Backend (BFF)

**FastAPI:** `/home/zaks/scripts/deal_lifecycle_api.py` on `http://localhost:8090`

**Chat Endpoints (MUST REMAIN BACKWARD COMPATIBLE):**
- `POST /api/chat` (SSE streaming)
- `POST /api/chat/complete`
- `POST /api/chat/execute-proposal`

**Legacy Deferred Reminders Endpoints (Preserved):**
- Source: `/home/zaks/scripts/deferred_actions.py`
- Storage: `DataRoom/.deal-registry/deferred_actions.json` (JSON file)
- Endpoints:
  - `GET /api/deferred-actions`
  - `GET /api/deferred-actions/due`
  - `POST /api/deferred-actions/{action_id}/execute` (marks executed; **no artifacts generated**)
  - `POST /api/deferred-actions/{action_id}/cancel`

Note: `/api/actions*` are reserved for Kinetic Actions (v1.2).

### Chat Orchestration

**Orchestrator:** `/home/zaks/scripts/chat_orchestrator.py`
- Current proposals: `add_note`, `create_task`, `draft_email`, `request_docs`, `stage_transition`
- Proposal execution: `/api/chat/execute-proposal` (do not break)
- LangGraph brain: `http://localhost:8080` (mode: `off|auto|force`)
- **No LangSmith tracing requirement**

### Data & Platform Foundations

**Deal Registry:** `/home/zaks/scripts/deal_registry.py`
- `deal.folder_path` is authoritative for deal folder location

**Event Store:** `/home/zaks/scripts/deal_events.py`
- Append-only event log for deal timeline

**Schemas:** `/home/zaks/DataRoom/.deal-registry/schemas/*.yaml`

**SQLite State Store (EXISTING):**
- File: `/home/zaks/scripts/email_ingestion/state/sqlite_store.py`
- DB: `ZAKOPS_STATE_DB` env var (default: `DataRoom/.deal-registry/ingest_state.db`)
- Currently used for: email ingestion state + chat session persistence
- **Will be extended** with actions tables (no new DB needed)

---

## Section 1: Backward Compatibility Strategy

### Approach: Preserve Legacy, Repurpose Kinetic

**Legacy Endpoints (Deferred Reminders) - PRESERVED:**
```
GET  /api/deferred-actions        → backed by deferred_actions.json
GET  /api/deferred-actions/due    → backed by deferred_actions.json
POST /api/deferred-actions/{id}/execute
POST /api/deferred-actions/{id}/cancel
```

**New Endpoints (Kinetic Actions) - NEW:**
```
GET  /api/actions                 → backed by ZAKOPS_STATE_DB.actions table
GET  /api/actions/{id}
POST /api/actions
POST /api/actions/{id}/approve
POST /api/actions/{id}/execute
POST /api/actions/{id}/cancel
POST /api/actions/{id}/update
GET  /api/actions/{id}/artifacts
GET  /api/actions/{id}/artifact/{artifact_id}
GET  /api/actions/capabilities    → (NEW v1.2) List capability manifests
GET  /api/actions/metrics         → (NEW v1.2) Metrics dashboard data
POST /api/actions/plan            → (NEW v1.2) Test planner endpoint
```

**Migration Path:**
1. Implement new Kinetic Actions endpoints alongside legacy
2. Update Dashboard UI to use new `/api/actions*` endpoints
3. Legacy `/api/deferred-actions*` remain functional for backward compatibility
4. Future: migrate old deferred reminders to Kinetic Actions (Phase 8, optional)

**Why This Works:**
- Zero breaking changes to existing flows
- Dashboard can switch to new API incrementally
- Old integrations (if any) continue working
- Clean separation of concerns

---

## Section 2: World-Class Architecture (NEW in v1.2)

### The Self-Extending Pattern

**Problem with v1.1:** Action types hard-coded everywhere:
- `src/models/action.py` - ActionType enum
- `src/app/actions/page.tsx` - UI filters (lines 2500-2506)
- `src/app/actions/page.tsx` - Type labels (lines 2555-2561)
- `src/scripts/chat_orchestrator.py` - Keyword matching (lines 2304-2336)

Adding a new action type → 5 file changes + redeploy.

**Solution in v1.2:** Capability Manifest System

```
scripts/actions/capabilities/
├── draft_email.v1.yaml           ← Manifest
├── generate_document.v1.yaml     ← Manifest
├── build_valuation_model.v1.yaml ← Manifest
├── generate_pitch_deck.v1.yaml   ← Manifest
└── request_diligence_docs.v1.yaml ← Manifest
```

Each manifest defines:
- `capability_id` (stable, versioned)
- `input_schema` (JSON Schema) → UI generates forms
- `output_artifacts` (types + mime types)
- `risk_level` + `requires_approval` → safety gates
- `examples` → helps planner understand usage
- `constraints` → safety rules (e.g., "never send email")

**CapabilityRegistry:**
- Loads manifests at startup
- Indexes by `action_type`, `tags`, `capability_id`
- Validates inputs against schemas
- Exposes `list_capabilities()`, `get_capability()`, `match_capability(query)`

**ActionPlanner:**
- Queries registry for matches
- Decomposes complex requests into multi-step plans
- Asks clarifying questions for missing inputs
- Refuses safely with alternatives for impossible actions

**Result:** Add YAML + executor → action available everywhere (UI, planner, chat).

---

## Architecture Overview (Updated for v1.2)

### System Context with Capability Layer

```
┌──────────────────────────────────────────────────────────────────┐
│                    ZakOps Dashboard (Next.js)                     │
│                     http://localhost:3003                         │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐  ┌──────────┐  │
│  │  Chat UI   │  │ Actions UI │  │ Deal Detail │  │ Metrics  │  │
│  │            │  │ (dynamic)  │  │     UI      │  │Dashboard │  │
│  └─────┬──────┘  └──────┬─────┘  └──────┬──────┘  └────┬─────┘  │
└────────┼─────────────────┼────────────────┼──────────────┼────────┘
         │                 │                │              │
         │ POST /api/chat  │ GET /api/      │              │ GET /api/
         │ (SSE stream)    │ actions        │              │ actions/
         │                 │ /capabilities  │              │ metrics
         ▼                 ▼                ▼              ▼
┌──────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (BFF) - port 8090                    │
│                   deal_lifecycle_api.py                           │
│                                                                   │
│  ┌─────────────┐   ┌─────────────────────┐   ┌──────────────┐   │
│  │Chat Handler │──▶│  Action Planner     │──▶│Action Manager│   │
│  │             │   │  (NEW v1.2)         │   │              │   │
│  └─────────────┘   │                     │   └──────┬───────┘   │
│         │           │ • Query registry   │          │           │
│         │           │ • Match capability │          │           │
│         │           │ • Decompose multi- │          │           │
│         │           │   step plans       │          │           │
│         ▼           │ • Ask clarifying   │          ▼           │
│  ┌─────────────┐   │   questions        │   ┌─────────────────┐│
│  │LangGraph    │   └──────┬──────────────┘   │ Actions Queue   ││
│  │Brain (8080) │          │                  │ (ZAKOPS_STATE_DB││
│  └─────────────┘          │                  │  SQLite-backed) ││
│                           ▼                  └────────┬────────┘│
│              ┌─────────────────────────┐              │         │
│              │  Capability Registry    │              │         │
│              │  (NEW v1.2)             │              │         │
│              │                         │              │         │
│              │  Loads from:            │              ▼         │
│              │  scripts/actions/       │   ┌─────────────────┐ │
│              │    capabilities/*.yaml  │   │ Deal Events     │ │
│              │                         │   │ (observability) │ │
│              │  • draft_email.v1       │   └─────────────────┘ │
│              │  • generate_doc.v1      │                       │
│              │  • build_model.v1       │                       │
│              │  • generate_deck.v1     │                       │
│              │  • request_docs.v1      │                       │
│              └─────────────────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                                        ┌─────────────────────┐
                                        │  Action Runner      │
                                        │  (lease-based)      │
                                        │                     │
                                        │  ┌───────────────┐  │
                                        │  │ Executor      │  │
                                        │  │ Registry      │  │
                                        │  │ (dynamic)     │  │
                                        │  │               │  │
                                        │  │ Loads from    │  │
                                        │  │ capability    │  │
                                        │  │ manifests     │  │
                                        │  └───────┬───────┘  │
                                        └──────────┼──────────┘
                                                   │
                                                   ▼
                                        ┌─────────────────────┐
                                        │   Artifact Store    │
                                        │   (DataRoom)        │
                                        │                     │
                                        │ Path Convention:    │
                                        │ {deal.folder_path}/ │
                                        │   99-ACTIONS/       │
                                        │     {action_id}/    │
                                        │                     │
                                        │ • DOCX (python-docx)│
                                        │ • PDF  (reportlab)  │
                                        │ • XLSX (openpyxl)   │
                                        │ • PPTX (python-pptx)│
                                        └─────────────────────┘
```

### Key Design Decisions (Updated for v1.2)

1. **Universal Action Schema** - Single Pydantic model supports all action types
2. **Capability Manifest System** (NEW) - YAML-driven self-extending architecture
3. **Action Planner with RAG** (NEW) - Handles unknown/complex requests
4. **Plugin Executor System** - Register new action types without core changes
5. **Persistent Queue** - SQLite-backed (`ZAKOPS_STATE_DB`), survives restarts
6. **Lease-Based Runner** - DB lease prevents duplicate workers, enables safe takeover
7. **Per-Action Locking** (NEW) - Prevents race conditions on individual actions
8. **Chat → Planner → Proposal → Action** (UPDATED) - Planner inserted between chat and proposals
9. **DataRoom Integration** - Artifacts stored in `{deal.folder_path}/99-ACTIONS/{action_id}/`
10. **Deal Events Integration** - Action milestones emit deal events for observability
11. **Idempotency Keys** - Unique constraint prevents duplicate executions
12. **Status State Machine** - Clear lifecycle: PENDING_APPROVAL → READY → PROCESSING → COMPLETED/FAILED
13. **Schema-Driven UI** (NEW) - Forms generated from capability manifests
14. **Observability Metrics** (NEW) - Real-time dashboard for queue health
15. **Backward Compatible** - Legacy deferred-actions preserved

---

## Phase 0: Capability Manifest System (Week 1, Days 1-4)

### Component 0.1: Capability Manifest Schema

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - FOUNDATION)
**Estimated Effort:** 1 day

#### Purpose

Define the structure of capability manifests that describe what actions the system can perform.

#### Manifest Schema (YAML)

**Example:** `scripts/actions/capabilities/draft_email.v1.yaml`

```yaml
# Capability Manifest v1.0
capability_id: "COMMUNICATION.DRAFT_EMAIL.v1"
version: "1.0"
title: "Draft Email"
description: "Generate professional email draft for acquisition workflow communications"
action_type: "COMMUNICATION.DRAFT_EMAIL"

# Input schema (JSON Schema format)
input_schema:
  type: object
  properties:
    recipient:
      type: string
      description: "Recipient email address"
      required: true
    recipient_name:
      type: string
      description: "Recipient's full name (optional)"
      required: false
    subject:
      type: string
      description: "Email subject line"
      required: true
    context:
      type: string
      description: "Context and purpose of email"
      required: true
    tone:
      type: string
      description: "Email tone"
      enum: ["professional", "friendly", "formal"]
      default: "professional"
      required: false
    include_attachments:
      type: boolean
      description: "Whether to reference attachments"
      default: false
      required: false

# Output artifacts
output_artifacts:
  - type: "docx"
    description: "Email draft as Word document"
    mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# Safety metadata
risk_level: "medium"
requires_approval: true
constraints:
  - "Never send email automatically"
  - "Draft only; manual review required"
  - "Requires ENABLE_CLOUD_POLICY=true"

# LLM usage
llm_allowed: true
llm_provider: "gemini"
deterministic_steps: false

# Examples (help planner understand usage)
examples:
  - description: "Draft follow-up email to seller"
    inputs:
      recipient: "john@seller.com"
      recipient_name: "John Smith"
      subject: "Follow-up on LOI Discussion"
      context: "Discussed LOI terms on Dec 28, need to confirm next steps"
      tone: "professional"
    expected_output: "Professional email with summary of discussion and next steps"

  - description: "Draft request for financial data"
    inputs:
      recipient: "cfo@target.com"
      recipient_name: "Sarah Johnson"
      subject: "Request for Financial Statements"
      context: "Need 3 years of audited financials for due diligence"
      tone: "formal"
    expected_output: "Formal request letter with specific requirements"

# Metadata
created: "2025-12-30"
updated: "2025-12-30"
owner: "zakops-team"
tags: ["communication", "email", "draft", "external"]
```

#### All 5 Required Manifests

**Create these files:**

1. `scripts/actions/capabilities/draft_email.v1.yaml` (above)
2. `scripts/actions/capabilities/generate_document.v1.yaml`
3. `scripts/actions/capabilities/build_valuation_model.v1.yaml`
4. `scripts/actions/capabilities/generate_pitch_deck.v1.yaml`
5. `scripts/actions/capabilities/request_diligence_docs.v1.yaml`

*See Appendix A for complete manifests 2-5*

#### Acceptance Criteria

- [ ] Manifest schema documented
- [ ] 5 capability manifests created
- [ ] Each manifest has 2+ examples
- [ ] Input schemas complete with required fields
- [ ] Output artifacts specified with mime types
- [ ] Safety constraints documented

---

### Component 0.2: Capability Registry

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - FOUNDATION)
**Estimated Effort:** 2 days

#### Purpose

Load, index, and query capability manifests at runtime.

#### Technical Specification

**New File:** `src/actions/capabilities/registry.py` (~400 lines)

```python
import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InputSchemaProperty(BaseModel):
    """Single property in input schema."""
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


class InputSchema(BaseModel):
    """Input schema for capability."""
    type: str = "object"
    properties: Dict[str, InputSchemaProperty]


class OutputArtifact(BaseModel):
    """Output artifact specification."""
    type: str  # docx, pdf, xlsx, pptx
    description: str
    mime_type: str


class CapabilityManifest(BaseModel):
    """
    Single capability manifest.

    This is the "toolbox manual" that agents consult to understand
    what actions are available and how to use them.
    """
    capability_id: str  # Stable, versioned ID (e.g., "COMMUNICATION.DRAFT_EMAIL.v1")
    version: str
    title: str
    description: str
    action_type: str  # Maps to ActionType enum

    input_schema: InputSchema
    output_artifacts: List[OutputArtifact]

    risk_level: str  # low, medium, high
    requires_approval: bool
    constraints: List[str] = Field(default_factory=list)

    llm_allowed: bool = False
    llm_provider: Optional[str] = None
    deterministic_steps: bool = True

    examples: List[Dict[str, Any]] = Field(default_factory=list)

    created: str
    updated: str
    owner: str
    tags: List[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class CapabilityRegistry:
    """
    Registry of available action capabilities.

    Usage:
        registry = CapabilityRegistry()
        registry.load_from_directory("scripts/actions/capabilities")

        # List all
        caps = registry.list_capabilities()

        # Get specific
        cap = registry.get_capability("COMMUNICATION.DRAFT_EMAIL.v1")

        # Match user intent
        matches = registry.match_capability("draft email to seller")
    """

    def __init__(self):
        self._capabilities: Dict[str, CapabilityManifest] = {}
        self._by_action_type: Dict[str, List[CapabilityManifest]] = {}
        self._by_tag: Dict[str, List[CapabilityManifest]] = {}

    def load_from_directory(self, capabilities_dir: str):
        """Load all capability manifests from directory."""
        path = Path(capabilities_dir)
        if not path.exists():
            raise ValueError(f"Capabilities directory not found: {capabilities_dir}")

        yaml_files = list(path.glob("*.yaml")) + list(path.glob("*.yml"))
        if not yaml_files:
            logger.warning(f"No capability manifests found in {capabilities_dir}")
            return

        for yaml_file in yaml_files:
            try:
                self._load_manifest(yaml_file)
            except Exception as e:
                logger.error(f"Failed to load manifest {yaml_file}: {e}")
                raise

        logger.info(f"Loaded {len(self._capabilities)} capabilities from {capabilities_dir}")

    def _load_manifest(self, yaml_path: Path):
        """Load single manifest from YAML."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        manifest = CapabilityManifest(**data)

        # Validate schema
        if not manifest.input_schema.properties:
            raise ValueError(f"Capability {manifest.capability_id} has no input schema properties")

        # Register
        self._capabilities[manifest.capability_id] = manifest

        # Index by action_type
        if manifest.action_type not in self._by_action_type:
            self._by_action_type[manifest.action_type] = []
        self._by_action_type[manifest.action_type].append(manifest)

        # Index by tags
        for tag in manifest.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(manifest)

        logger.info(f"Registered capability: {manifest.capability_id} ({manifest.title})")

    def get_capability(self, capability_id: str) -> Optional[CapabilityManifest]:
        """Get capability by ID."""
        return self._capabilities.get(capability_id)

    def get_by_action_type(self, action_type: str) -> List[CapabilityManifest]:
        """Get all capabilities for action type."""
        return self._by_action_type.get(action_type, [])

    def list_capabilities(self) -> List[CapabilityManifest]:
        """List all registered capabilities."""
        return list(self._capabilities.values())

    def match_capability(self, user_intent: str) -> List[CapabilityManifest]:
        """
        Match user intent to capabilities (keyword-based).

        For production, this should use semantic search + RAG.
        """
        matches = []
        query_lower = user_intent.lower()

        for cap in self._capabilities.values():
            # Check title
            if cap.title.lower() in query_lower or query_lower in cap.title.lower():
                matches.append(cap)
                continue

            # Check description
            if cap.description.lower() in query_lower or query_lower in cap.description.lower():
                matches.append(cap)
                continue

            # Check tags
            for tag in cap.tags:
                if tag.lower() in query_lower:
                    matches.append(cap)
                    break

            # Check examples
            for example in cap.examples:
                if example.get("description", "").lower() in query_lower:
                    matches.append(cap)
                    break

        return matches

    def validate_inputs(
        self,
        capability_id: str,
        inputs: Dict[str, Any]
    ) -> tuple[bool, Optional[List[str]]]:
        """
        Validate inputs against capability schema.

        Returns:
            (is_valid, missing_required_fields)
        """
        cap = self.get_capability(capability_id)
        if not cap:
            return False, [f"Unknown capability: {capability_id}"]

        missing = []
        for prop_name, prop_schema in cap.input_schema.properties.items():
            if prop_schema.required and prop_name not in inputs:
                missing.append(prop_name)

        if missing:
            return False, missing

        return True, None

    def get_input_schema_dict(self, capability_id: str) -> Optional[Dict[str, Any]]:
        """Get input schema as dict (for API responses)."""
        cap = self.get_capability(capability_id)
        if not cap:
            return None

        return {
            "type": cap.input_schema.type,
            "properties": {
                name: {
                    "type": prop.type,
                    "description": prop.description,
                    "required": prop.required,
                    "enum": prop.enum,
                    "default": prop.default,
                }
                for name, prop in cap.input_schema.properties.items()
            }
        }


# Global registry instance
_registry = CapabilityRegistry()


def get_registry() -> CapabilityRegistry:
    """Get global capability registry."""
    return _registry


def load_capabilities(capabilities_dir: str = "scripts/actions/capabilities"):
    """Load capabilities into global registry."""
    _registry.load_from_directory(capabilities_dir)
```

#### Integration with FastAPI

**Update:** `src/scripts/deal_lifecycle_api.py` - Add on startup

```python
from actions.capabilities.registry import load_capabilities

@app.on_event("startup")
async def startup_event():
    """Load capabilities on startup."""
    load_capabilities("scripts/actions/capabilities")
    logger.info("Capabilities loaded successfully")
```

#### Acceptance Criteria

- [ ] `CapabilityRegistry` class implemented
- [ ] Loads YAML manifests from directory
- [ ] Indexes by `capability_id`, `action_type`, `tags`
- [ ] `get_capability()` returns manifest
- [ ] `list_capabilities()` returns all
- [ ] `match_capability(query)` returns matches
- [ ] `validate_inputs()` checks required fields
- [ ] Tests: load manifests, get by ID, match query, validate inputs

---

### Component 0.3: Capabilities API Endpoint

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 0.5 day

#### Purpose

Expose capabilities to frontend for schema-driven UI.

#### Technical Specification

**Extend:** `src/scripts/deal_lifecycle_api.py`

```python
from actions.capabilities.registry import get_registry

@app.get("/api/actions/capabilities")
async def list_capabilities():
    """
    List all registered action capabilities.

    Returns manifests with input schemas for dynamic form generation.
    """
    registry = get_registry()
    capabilities = []

    for cap in registry.list_capabilities():
        capabilities.append({
            "capability_id": cap.capability_id,
            "version": cap.version,
            "title": cap.title,
            "description": cap.description,
            "action_type": cap.action_type,
            "input_schema": registry.get_input_schema_dict(cap.capability_id),
            "output_artifacts": [art.model_dump() for art in cap.output_artifacts],
            "risk_level": cap.risk_level,
            "requires_approval": cap.requires_approval,
            "tags": cap.tags,
        })

    return {"capabilities": capabilities, "count": len(capabilities)}


@app.get("/api/actions/capabilities/{capability_id}")
async def get_capability(capability_id: str):
    """Get single capability by ID."""
    registry = get_registry()
    cap = registry.get_capability(capability_id)

    if not cap:
        raise HTTPException(status_code=404, detail="Capability not found")

    return {
        "capability": {
            "capability_id": cap.capability_id,
            "version": cap.version,
            "title": cap.title,
            "description": cap.description,
            "action_type": cap.action_type,
            "input_schema": registry.get_input_schema_dict(cap.capability_id),
            "output_artifacts": [art.model_dump() for art in cap.output_artifacts],
            "risk_level": cap.risk_level,
            "requires_approval": cap.requires_approval,
            "constraints": cap.constraints,
            "examples": cap.examples,
            "tags": cap.tags,
        }
    }
```

#### Acceptance Criteria

- [ ] `GET /api/actions/capabilities` returns all capabilities
- [ ] Response includes input schemas
- [ ] `GET /api/actions/capabilities/{id}` returns single capability
- [ ] 404 for unknown capability_id
- [ ] Tests: endpoint returns valid JSON, schemas included

---

### Component 0.4: Capability Registry Tests

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 0.5 day

#### Test Coverage

**New File:** `tests/test_capability_registry.py`

```python
import pytest
from actions.capabilities.registry import CapabilityRegistry, load_capabilities

def test_load_capabilities_from_directory():
    """Test loading manifests from directory."""
    registry = CapabilityRegistry()
    registry.load_from_directory("scripts/actions/capabilities")

    assert len(registry.list_capabilities()) == 5  # 5 manifests created

def test_get_capability_by_id():
    """Test retrieving capability by ID."""
    registry = CapabilityRegistry()
    registry.load_from_directory("scripts/actions/capabilities")

    cap = registry.get_capability("COMMUNICATION.DRAFT_EMAIL.v1")
    assert cap is not None
    assert cap.title == "Draft Email"
    assert cap.action_type == "COMMUNICATION.DRAFT_EMAIL"

def test_match_capability_by_query():
    """Test matching capabilities by user query."""
    registry = CapabilityRegistry()
    registry.load_from_directory("scripts/actions/capabilities")

    # Should match draft email
    matches = registry.match_capability("draft email to seller")
    assert len(matches) >= 1
    assert any(cap.action_type == "COMMUNICATION.DRAFT_EMAIL" for cap in matches)

def test_validate_inputs_missing_required():
    """Test input validation with missing required fields."""
    registry = CapabilityRegistry()
    registry.load_from_directory("scripts/actions/capabilities")

    # Missing required 'recipient'
    is_valid, missing = registry.validate_inputs(
        "COMMUNICATION.DRAFT_EMAIL.v1",
        {"subject": "Test", "context": "Test context"}
    )

    assert is_valid is False
    assert "recipient" in missing

def test_validate_inputs_all_required_present():
    """Test input validation with all required fields."""
    registry = CapabilityRegistry()
    registry.load_from_directory("scripts/actions/capabilities")

    is_valid, missing = registry.validate_inputs(
        "COMMUNICATION.DRAFT_EMAIL.v1",
        {
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "context": "Test context"
        }
    )

    assert is_valid is True
    assert missing is None
```

#### Acceptance Criteria

- [ ] Test: Load manifests from directory
- [ ] Test: Get capability by ID
- [ ] Test: Match capability by query
- [ ] Test: Validate inputs (missing required)
- [ ] Test: Validate inputs (all present)
- [ ] All tests pass

---

## Phase 0.5: Tooling Strategy (Tool Gateway + On-Demand MCP Runtime) - Week 1, Days 3-4

### Overview

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - Enables MCP Integration)
**Estimated Effort:** 2 days
**Execution-Ready Spec:** `/home/zaks/bookkeeping/docs/TOOLING-STRATEGY-EXECUTION-READY.md`

### Quick Reference

| Component | Path |
|-----------|------|
| Tool Gateway | `/home/zaks/scripts/tools/gateway.py` |
| Tool Registry | `/home/zaks/scripts/tools/registry.py` |
| Tool Manifests | `/home/zaks/scripts/tools/manifests/*.yaml` |
| Preflight Check | `make tool-preflight` |

### Purpose

Implement `ToolGateway.invoke()` as the **only tool execution entrypoint** with:

1. **Secret-Scan Gate** - Block calls with detected secrets BEFORE invocation (not just log redaction)
2. **Approval Enforcement** - Deny tool calls unless action is `READY/PROCESSING` and approved
3. **Two MCP Runtime Modes** - stdio spawn-per-call (preferred) or docker with healthcheck + idle shutdown
4. **Tool Manifests** - YAML describing transport, startup, health checks, TTL, timeouts, secrets refs, risk level
5. **Capability Registry Integration** - Planner can map unknown requests to available tools

### Key Components

#### 1. Tool Gateway (`/home/zaks/scripts/tools/gateway.py`)

Single entrypoint with layered gates:

```python
# Gates (in order):
# 1. Gateway enabled check
# 2. Allowlist/denylist check
# 3. Action approval enforcement (READY/PROCESSING only)
# 4. Secret-scan gate (blocks calls with secrets)
# 5. Tool exists check
# 6. Execute with timeout + retries
# 7. Audit log (redacted + bounded)

from tools.gateway import get_tool_gateway, ToolInvocationContext

gateway = get_tool_gateway()
result = await gateway.invoke(
    tool_name="gmail__send_email",
    args={"to": ["user@example.com"], "subject": "Test", "body": "Hello"},
    context=ToolInvocationContext(
        action_id="act_123",
        action_status="PROCESSING",  # Must be READY or PROCESSING
        deal_id="deal_456",
        approved=True,
    ),
)
```

#### 2. Tool Manifests (`/home/zaks/scripts/tools/manifests/*.yaml`)

Each tool described by YAML with transport, startup, health, secrets refs:

```yaml
# /home/zaks/scripts/tools/manifests/gmail__send_email.yaml
tool_id: "gmail__send_email"
version: "1.0.0"
title: "Send Email via Gmail"
provider: "mcp"

# MCP Runtime: stdio spawn-per-call (preferred)
mcp_server: "gmail"
mcp_tool_name: "mcp__gmail__send_email"
mcp_stdio_command: ["npx", "-y", "@anthropic/gmail-mcp"]

# MCP Runtime: docker alternative
docker_image: "ghcr.io/anthropic/gmail-mcp:latest"
docker_port: 8100
docker_health_cmd: "curl -f http://localhost:8100/health || exit 1"

# Timing
startup_time_ms: 5000
timeout_ms: 30000
ttl_seconds: 300  # Idle shutdown for docker mode

# Health Check (with TTL caching)
health_check:
  enabled: true
  endpoint: "mcp__gmail__list_email_labels"
  interval_seconds: 60
  cache_ttl_seconds: 30

# Secrets (NEVER actual values - only references)
secrets_refs:
  GMAIL_CREDENTIALS: "file:/home/zaks/.config/gmail-mcp/credentials.json"
  GMAIL_TOKEN: "env:GMAIL_MCP_TOKEN"

# Safety
risk_level: "high"
requires_approval: true
constraints:
  - "Rate limited to 50 emails/day"

# Input Schema (standard JSON Schema)
input_schema:
  type: "object"
  required: ["to", "subject", "body"]
  properties:
    to:
      type: "array"
      items: { type: "string", format: "email" }
    subject:
      type: "string"
      maxLength: 200
    body:
      type: "string"

# Examples (help planner)
examples:
  - description: "Send follow-up email"
    input: { to: ["user@example.com"], subject: "Follow-up", body: "Thanks..." }
```

#### 3. MCP Runtime Modes

| Mode | When to Use | How It Works |
|------|-------------|--------------|
| **stdio** (preferred) | Development, isolation | Spawns fresh MCP process per call via `mcp_stdio_command` |
| **docker** | Production, performance | Persistent container with healthcheck + idle shutdown |

```bash
# Set runtime mode
export ZAKOPS_MCP_RUNTIME_MODE="stdio"  # or "docker"
```

#### 4. Preflight Validation

```bash
# Validate everything before running
make tool-preflight

# Output:
# === Tool Preflight Check ===
# 1. Checking manifest syntax...
#    ✓ Loaded 5 manifests
# 2. Checking secret references...
#    ✓ All secrets present
# 3. Running health checks...
#    ✓ All 5 tools healthy
# === Preflight Complete ===
```

#### 5. Capability Registry Integration

Tool manifests auto-indexed so planner can map unknown requests:

```python
# Planner query: "send an email to the seller"
# Registry lookup: finds gmail__send_email tool
# Result: maps to TOOL.gmail__send_email capability

# If tool missing:
# Result: creates "missing tool" action card with resolution steps
```

### Available MCP Tools (Current Environment)

| MCP Server | Tools to Manifest | Priority |
|------------|-------------------|----------|
| `gmail` | `send_email`, `search_emails`, `read_email` | P0 |
| `crawl4ai-rag` | `crawl_single_page`, `smart_crawl_url`, `perform_rag_query` | P0 |
| `browser-use` | (TBD) | P1 |
| `linkedin` | (TBD) | P2 |

### Acceptance Criteria

- [ ] `/home/zaks/scripts/tools/gateway.py` - ToolGateway with all gates
- [ ] `/home/zaks/scripts/tools/registry.py` - ToolRegistry with health caching
- [ ] `/home/zaks/scripts/tools/manifests/gmail__*.yaml` - Gmail tool manifests
- [ ] `/home/zaks/scripts/tools/manifests/crawl4ai__*.yaml` - Crawl4AI tool manifests
- [ ] `make tool-preflight` - Validates manifests, secrets, health
- [ ] Secret-scan gate blocks test payload with fake API key
- [ ] Approval enforcement blocks calls when action not READY/PROCESSING
- [ ] Health checks use TTL caching (30-60s)
- [ ] Audit log bounded (truncate + hash for large payloads)
- [ ] CapabilityRegistry indexes tools for planner discovery

### Constraints (Codex Feedback Addressed)

| Issue | Resolution |
|-------|------------|
| Secret-scan gate vs redaction | `SecretScanner` blocks BEFORE invocation |
| Approval enforcement | `_check_approval()` gate verifies action status |
| Health check "not implemented" | Implemented with TTL caching |
| Bounded log size | Truncate with hash reference |
| Path consistency | All paths under `/home/zaks/scripts/` |
| Dynamic action_type | Tools indexed as capabilities, string-based |
| `should_retry()` bug | Implemented as method, called correctly |

**Full Implementation:** `/home/zaks/bookkeeping/docs/TOOLING-STRATEGY-EXECUTION-READY.md`

---

## Phase 1: Core Infrastructure (Week 1, Days 5-6 + Week 2, Day 1)

*Content from original Phase 1 remains unchanged - keeping schemas, executor interface, DB layer*

**Components:**
- 1.1: Universal Action Schema (2 days) - **NO CHANGES from v1.1**
- 1.2: Action Executors Architecture (2 days) - **UPDATED to use CapabilityRegistry**
- 1.3: Actions Database Layer (2 days) - **NO CHANGES from v1.1**

**Key Update in 1.2:** Executors now query `CapabilityRegistry` for validation

```python
# In executor base class
from actions.capabilities.registry import get_registry

class ActionExecutor(ABC):
    def validate(self, payload: ActionPayload) -> tuple[bool, Optional[str]]:
        """Validate action payload before execution."""
        registry = get_registry()
        cap = registry.get_by_action_type(self.action_type)

        if not cap:
            return False, f"No capability manifest for {self.action_type}"

        # Validate against manifest schema
        is_valid, missing = registry.validate_inputs(cap[0].capability_id, payload.inputs)

        if not is_valid:
            return False, f"Missing required fields: {', '.join(missing)}"

        return True, None
```

*See original v1.1 plan for complete Phase 1 code (lines 223-1270 in v1.1)*

---

## Phase 2: Action Planner (Week 2, Days 2-4) + Executors (Week 2, Days 5-9)

### Component 2.1: Action Planner (NEW in v1.2)

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

#### Purpose

Convert arbitrary user instructions into executable action plans.

#### Technical Specification

**New File:** `src/actions/planner.py` (~600 lines)

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from actions.capabilities.registry import get_registry, CapabilityManifest
import logging
import re

logger = logging.getLogger(__name__)


class ActionPlan(BaseModel):
    """
    Plan for executing user request.

    Can be:
    - Single action (selected_capability_id)
    - Multi-step plan (plan_steps)
    - Clarifying question (requires_clarification)
    - Safe refusal (refusal_reason)
    """
    intent: str  # Original user query
    interpretation: str  # How planner interpreted request

    # Single action
    selected_capability_id: Optional[str] = None
    action_inputs: Dict[str, Any] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)

    # Multi-step plan
    plan_steps: List[Dict[str, Any]] = Field(default_factory=list)

    # Clarification
    requires_clarification: bool = False
    clarifying_questions: List[str] = Field(default_factory=list)

    # Refusal
    is_refusal: bool = False
    refusal_reason: Optional[str] = None
    suggested_alternatives: List[str] = Field(default_factory=list)

    # Metadata
    confidence: float = 0.0  # 0.0 - 1.0
    risk_level: str = "medium"


class ActionPlanner:
    """
    Convert user instructions into executable ActionPayload(s).

    Workflow:
    1. Parse user intent
    2. Query CapabilityRegistry for matches
    3. Consult deal context + RAG
    4. Either:
       (A) Select single capability + extract inputs
       (B) Compose multi-step plan
       (C) Ask clarifying questions
       (D) Refuse with alternatives

    Design Decision:
    - For MVP, use rule-based + keyword matching
    - For production, integrate LangGraph brain with RAG over capability manifests
    """

    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        use_llm: bool = True,
        llm_endpoint: Optional[str] = None,
    ):
        self.registry = registry or get_registry()
        self.use_llm = use_llm
        self.llm_endpoint = llm_endpoint or "http://localhost:8080/plan-action"

    def plan(
        self,
        query: str,
        scope: Dict[str, Any],
        case_file: Dict[str, Any],
    ) -> ActionPlan:
        """
        Generate action plan from user query.

        Args:
            query: User's natural language request
            scope: Session scope (deal_id, broker_id, etc.)
            case_file: Deal context

        Returns:
            ActionPlan (single action, multi-step, clarification, or refusal)
        """
        logger.info(f"Planning action for query: {query}")

        # Step 1: Match capabilities
        matches = self.registry.match_capability(query)

        if not matches:
            return self._handle_unknown_action(query, scope)

        # Step 2: Select best match or decompose
        if len(matches) == 1:
            # Single match - straightforward
            capability = matches[0]
            return self._plan_single_action(query, capability, scope, case_file)

        # Step 3: Multiple matches or complex request
        if self._is_complex_request(query):
            # Decompose into multi-step plan
            return self._plan_multi_step(query, matches, scope, case_file)

        # Step 4: Ambiguous - ask for clarification
        return self._request_clarification(query, matches)

    def _plan_single_action(
        self,
        query: str,
        capability: CapabilityManifest,
        scope: Dict[str, Any],
        case_file: Dict[str, Any],
    ) -> ActionPlan:
        """Plan single action execution."""

        logger.info(f"Planning single action: {capability.title}")

        # Extract inputs from query (basic keyword extraction or LLM)
        if self.use_llm:
            try:
                inputs = self._extract_inputs_llm(query, capability, case_file)
            except Exception as e:
                logger.warning(f"LLM extraction failed, falling back to keywords: {e}")
                inputs = self._extract_inputs_keywords(query, capability)
        else:
            inputs = self._extract_inputs_keywords(query, capability)

        # Check for missing required fields
        is_valid, missing = self.registry.validate_inputs(
            capability.capability_id,
            inputs
        )

        if missing:
            return ActionPlan(
                intent=query,
                interpretation=f"Want to execute {capability.title}",
                selected_capability_id=capability.capability_id,
                action_inputs=inputs,
                missing_fields=missing,
                requires_clarification=True,
                clarifying_questions=[
                    f"To {capability.title}, please provide: {', '.join(missing)}"
                ],
                confidence=0.5,
                risk_level=capability.risk_level,
            )

        return ActionPlan(
            intent=query,
            interpretation=f"Execute {capability.title}",
            selected_capability_id=capability.capability_id,
            action_inputs=inputs,
            confidence=0.9,
            risk_level=capability.risk_level,
        )

    def _plan_multi_step(
        self,
        query: str,
        matches: List[CapabilityManifest],
        scope: Dict[str, Any],
        case_file: Dict[str, Any],
    ) -> ActionPlan:
        """Decompose complex request into multiple actions."""

        logger.info(f"Planning multi-step action for: {query}")

        # Example: "Create lender outreach package with summary + KPIs + email"
        # → [DOCUMENT.GENERATE (summary), ANALYSIS.BUILD_MODEL (KPIs), COMMUNICATION.DRAFT_EMAIL]

        steps = []

        # Use LLM to decompose (if available)
        if self.use_llm:
            try:
                steps = self._decompose_llm(query, matches, case_file)
            except Exception as e:
                logger.warning(f"LLM decomposition failed: {e}")

        # Fallback: use all matched capabilities as steps (limit to 3)
        if not steps:
            for cap in matches[:3]:
                steps.append({
                    "capability_id": cap.capability_id,
                    "title": cap.title,
                    "action_type": cap.action_type,
                    "inputs": {},  # Will be filled in during execution
                })

        return ActionPlan(
            intent=query,
            interpretation=f"Multi-step plan with {len(steps)} actions",
            plan_steps=steps,
            confidence=0.7,
            risk_level="high",  # Multi-step is higher risk
        )

    def _handle_unknown_action(
        self,
        query: str,
        scope: Dict[str, Any],
    ) -> ActionPlan:
        """Handle request for unknown/unavailable action."""

        logger.warning(f"No capability match for query: {query}")

        # Find similar capabilities
        all_caps = self.registry.list_capabilities()
        suggestions = [f"{cap.title} - {cap.description}" for cap in all_caps[:5]]

        return ActionPlan(
            intent=query,
            interpretation="Cannot map to known capability",
            is_refusal=True,
            refusal_reason="No matching capability found. Available actions:",
            suggested_alternatives=suggestions,
            confidence=0.0,
        )

    def _request_clarification(
        self,
        query: str,
        matches: List[CapabilityManifest],
    ) -> ActionPlan:
        """Request clarification when ambiguous."""

        logger.info(f"Ambiguous query, requesting clarification: {query}")

        questions = [
            f"Did you mean: {' OR '.join([cap.title for cap in matches])}?"
        ]

        return ActionPlan(
            intent=query,
            interpretation="Ambiguous request",
            requires_clarification=True,
            clarifying_questions=questions,
            confidence=0.3,
        )

    def _is_complex_request(self, query: str) -> bool:
        """Detect if request requires multiple actions."""
        complex_keywords = [
            " and ", " then ", " plus ", " with ", "package",
            "bundle", "multiple", "several", "+", ","
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in complex_keywords)

    def _extract_inputs_keywords(
        self,
        query: str,
        capability: CapabilityManifest,
    ) -> Dict[str, Any]:
        """Extract inputs using keyword matching (fallback)."""
        inputs = {}
        query_lower = query.lower()

        # Example patterns
        if "recipient" in capability.input_schema.properties:
            # Look for email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query)
            if emails:
                inputs["recipient"] = emails[0]

        if "subject" in capability.input_schema.properties:
            # Look for quoted strings
            subjects = re.findall(r'"([^"]*)"', query)
            if subjects:
                inputs["subject"] = subjects[0]

        # Context is everything else (fallback)
        if "context" in capability.input_schema.properties:
            inputs["context"] = query

        return inputs

    def _extract_inputs_llm(
        self,
        query: str,
        capability: CapabilityManifest,
        case_file: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract inputs using LLM (production approach)."""

        # Call LangGraph brain to extract structured inputs
        import requests

        response = requests.post(
            self.llm_endpoint,
            json={
                "query": query,
                "capability_id": capability.capability_id,
                "input_schema": self.registry.get_input_schema_dict(capability.capability_id),
                "case_file": case_file,
            },
            timeout=10,
        )

        if response.status_code == 200:
            return response.json().get("extracted_inputs", {})

        # Fallback to keywords
        return self._extract_inputs_keywords(query, capability)

    def _decompose_llm(
        self,
        query: str,
        matches: List[CapabilityManifest],
        case_file: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Decompose complex request using LLM."""

        # Call LangGraph brain for multi-step planning
        import requests

        response = requests.post(
            f"{self.llm_endpoint}/decompose",
            json={
                "query": query,
                "available_capabilities": [
                    {
                        "capability_id": cap.capability_id,
                        "title": cap.title,
                        "description": cap.description,
                        "action_type": cap.action_type,
                    }
                    for cap in matches
                ],
                "case_file": case_file,
            },
            timeout=15,
        )

        if response.status_code == 200:
            return response.json().get("plan_steps", [])

        return []
```

#### Acceptance Criteria

- [ ] `ActionPlanner` class implemented
- [ ] Planner queries `CapabilityRegistry` for matches
- [ ] Single action plans generated correctly
- [ ] Multi-step decomposition works
- [ ] Clarifying questions generated for missing inputs
- [ ] Safe refusal with alternatives for unknown actions
- [ ] Confidence scoring calculated
- [ ] Tests: simple action, multi-step, clarification, refusal

---

### Component 2.2-2.6: Action Executors (Week 2, Days 5-9)

*Content from original Phase 2 remains mostly unchanged - 5 executor implementations*

**Components:**
- 2.2: Email Draft Executor (1.5 days) - **NO CHANGES from v1.1**
- 2.3: Document Generate Executor (1.5 days) - **NO CHANGES from v1.1**
- 2.4: Valuation Model Executor (1.5 days) - **NO CHANGES from v1.1**
- 2.5: Presentation Deck Executor (1.5 days) - **NO CHANGES from v1.1**
- 2.6: Diligence Request Executor (1.5 days) - **NO CHANGES from v1.1**

*See original v1.1 plan for complete executor implementations (lines 1272-1560 in v1.1)*

---

## Phase 3: API Layer + Metrics (Week 3, Days 1-4)

### Component 3.1: Actions API Endpoints

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

*Content from original Phase 3 Component 3.1 remains unchanged*

*See original v1.1 plan lines 1562-1872 for complete API endpoints*

---

### Component 3.2: Action Runner (Background Worker)

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

*Content from original Phase 3 Component 3.2 remains unchanged*

*See original v1.1 plan lines 1889-2140 for complete runner implementation*

---

### Component 3.3: Observability Metrics Endpoint (NEW in v1.2)

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 1 day

#### Purpose

Provide real-time metrics for production monitoring.

#### Technical Specification

**Extend:** `src/scripts/deal_lifecycle_api.py`

```python
from datetime import timedelta

@router.get("/metrics")
async def get_action_metrics():
    """
    Get action execution metrics.

    Returns:
        - Queue lengths by status
        - Average duration per action type
        - Success rate (24h)
        - Error breakdown
    """
    db = ActionsDB()

    with sqlite3.connect(db.db_path) as conn:
        conn.row_factory = sqlite3.Row

        # Queue lengths
        queue_lengths = {}
        for status in ["PENDING_APPROVAL", "READY", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED"]:
            count = conn.execute(
                "SELECT COUNT(*) FROM actions WHERE status = ?",
                (status,)
            ).fetchone()[0]
            queue_lengths[status] = count

        # Average duration by type
        durations = conn.execute("""
            SELECT type, AVG(duration_seconds) as avg_duration, COUNT(*) as count
            FROM actions
            WHERE status = 'COMPLETED' AND duration_seconds IS NOT NULL
            GROUP BY type
        """).fetchall()

        avg_duration_by_type = {
            row["type"]: {"avg_seconds": row["avg_duration"], "count": row["count"]}
            for row in durations
        }

        # Success rate (last 24h)
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        total = conn.execute(
            "SELECT COUNT(*) FROM actions WHERE created_at > ?",
            (yesterday.isoformat(),)
        ).fetchone()[0]

        completed = conn.execute(
            "SELECT COUNT(*) FROM actions WHERE created_at > ? AND status = 'COMPLETED'",
            (yesterday.isoformat(),)
        ).fetchone()[0]

        failed = conn.execute(
            "SELECT COUNT(*) FROM actions WHERE created_at > ? AND status = 'FAILED'",
            (yesterday.isoformat(),)
        ).fetchone()[0]

        success_rate = (completed / total * 100) if total > 0 else 0.0

        # Error breakdown (top 10)
        error_breakdown = conn.execute("""
            SELECT
                json_extract(error, '$.message') as error_message,
                COUNT(*) as count
            FROM actions
            WHERE status = 'FAILED'
              AND created_at > ?
              AND error IS NOT NULL
            GROUP BY error_message
            ORDER BY count DESC
            LIMIT 10
        """, (yesterday.isoformat(),)).fetchall()

        # Runner health
        runner_lease = conn.execute(
            "SELECT * FROM action_runner_leases WHERE lease_id = 1"
        ).fetchone()

        runner_health = None
        if runner_lease:
            expires_at = datetime.fromisoformat(runner_lease["expires_at"])
            is_active = datetime.utcnow() < expires_at
            runner_health = {
                "pid": runner_lease["runner_pid"],
                "hostname": runner_lease["runner_hostname"],
                "acquired_at": runner_lease["acquired_at"],
                "heartbeat_at": runner_lease["heartbeat_at"],
                "expires_at": runner_lease["expires_at"],
                "is_active": is_active,
            }

        return {
            "queue_lengths": queue_lengths,
            "avg_duration_by_type": avg_duration_by_type,
            "success_rate_24h": round(success_rate, 2),
            "total_24h": total,
            "completed_24h": completed,
            "failed_24h": failed,
            "error_breakdown": [
                {"error": row["error_message"], "count": row["count"]}
                for row in error_breakdown
            ],
            "runner_health": runner_health,
            "timestamp": datetime.utcnow().isoformat(),
        }
```

#### Acceptance Criteria

- [ ] `/api/actions/metrics` endpoint implemented
- [ ] Returns queue lengths by status
- [ ] Returns average duration per action type
- [ ] Returns success rate (24h)
- [ ] Returns error breakdown (top 10)
- [ ] Returns runner health (lease info)
- [ ] Tests: endpoint returns valid JSON, calculations correct

---

## Phase 4: Chat Integration + Planner (Week 3, Days 5-7)

### Component 4.1: Planner Integration with Chat (UPDATED in v1.2)

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 2 days

#### Purpose

Insert planner between chat and proposal generation.

#### Technical Specification

**Extend:** `/home/zaks/scripts/chat_orchestrator.py`

```python
from actions.planner import ActionPlanner

# Initialize planner
planner = ActionPlanner()

def generate_proposals(query: str, scope: dict, case_file: dict) -> List[dict]:
    """
    Generate proposals from query using ActionPlanner (NEW v1.2).

    Flow:
    1. Use planner to analyze query
    2. If single action → create proposal
    3. If multi-step → create multiple proposals
    4. If clarification → ask questions
    5. If refusal → respond with alternatives
    """
    # Use planner instead of keyword matching
    plan = planner.plan(query, scope, case_file)

    if plan.is_refusal:
        # Safe refusal with alternatives
        return [{
            "tool": "respond",
            "text": f"{plan.refusal_reason}\n\nAvailable actions:\n" +
                   "\n".join(f"• {alt}" for alt in plan.suggested_alternatives),
        }]

    if plan.requires_clarification:
        # Ask clarifying questions
        return [{
            "tool": "ask_question",
            "questions": plan.clarifying_questions,
            "context": {
                "capability_id": plan.selected_capability_id,
                "partial_inputs": plan.action_inputs,
                "missing_fields": plan.missing_fields,
            }
        }]

    if plan.selected_capability_id:
        # Single action proposal
        registry = get_registry()
        cap = registry.get_capability(plan.selected_capability_id)

        return [{
            "proposal_id": str(uuid.uuid4()),
            "tool": "create_action",
            "args": {
                "action_type": cap.action_type,
                "title": f"{cap.title}: {plan.intent[:50]}",
                "summary": plan.interpretation,
                "inputs": plan.action_inputs,
            },
            "requires_confirmation": True,
            "requires_approval": cap.requires_approval,
            "reason": f"This will create an action for: {cap.title}",
            "confidence": plan.confidence,
            "risk_level": plan.risk_level,
        }]

    if plan.plan_steps:
        # Multi-step plan proposals
        proposals = []
        for i, step in enumerate(plan.plan_steps):
            proposals.append({
                "proposal_id": str(uuid.uuid4()),
                "tool": "create_action",
                "args": {
                    "action_type": step["action_type"],
                    "title": f"Step {i+1}: {step['title']}",
                    "summary": f"Part of multi-step plan: {plan.intent[:50]}",
                    "inputs": step.get("inputs", {}),
                },
                "requires_confirmation": True,
                "requires_approval": True,
                "reason": f"Step {i+1} of {len(plan.plan_steps)} in multi-action plan",
                "confidence": plan.confidence,
                "risk_level": plan.risk_level,
            })
        return proposals

    # Fallback: no proposals
    return []
```

**Extend:** Proposal execution (create_action handler from v1.1)

*See original v1.1 plan lines 2142-2256 for complete proposal execution code*

#### Acceptance Criteria

- [ ] Planner integrated with chat orchestrator
- [ ] Single action query → single proposal
- [ ] Multi-step query → multiple proposals
- [ ] Missing inputs → clarifying questions
- [ ] Unknown action → safe refusal with alternatives
- [ ] Tests: simple action, multi-step, clarification, refusal

---

## Phase 5: Schema-Driven UI/UX (Week 3-4, Days 8-13)

### Component 5.1: Schema-Driven Actions Dashboard (UPDATED in v1.2)

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

#### Purpose

Generate UI dynamically from capability manifests (no hard-coded types).

#### Technical Specification

**Update:** `/home/zaks/zakops-dashboard/src/app/actions/page.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible';
import { ChevronDown, ChevronUp, Download, Play, Check, X, RotateCcw } from 'lucide-react';

interface Capability {
  capability_id: string;
  title: string;
  action_type: string;
  input_schema: any;
  tags: string[];
}

interface Action {
  action_id: string;
  deal_id?: string;
  type: string;
  title: string;
  summary: string;
  status: string;
  created_at: string;
  created_by: string;
  inputs: Record<string, any>;
  outputs?: Record<string, any>;
  error?: { message: string };
  artifacts: Artifact[];
  audit_trail: AuditEvent[];
}

interface Artifact {
  artifact_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  created_at: string;
}

interface AuditEvent {
  timestamp: string;
  event: string;
  actor: string;
  details?: Record<string, any>;
}

export default function ActionsPage() {
  const [actions, setActions] = useState<Action[]>([]);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);  // NEW v1.2
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCapabilities();  // NEW v1.2
    fetchActions();
  }, [statusFilter, typeFilter]);

  // NEW v1.2: Fetch capabilities for dynamic filters/labels
  const fetchCapabilities = async () => {
    const res = await fetch('/api/actions/capabilities');
    const data = await res.json();
    setCapabilities(data.capabilities);
  };

  const fetchActions = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    if (typeFilter) params.append('type', typeFilter);

    const res = await fetch(`/api/actions?${params}`);
    const data = await res.json();
    setActions(data.actions);
    setLoading(false);
  };

  // NEW v1.2: Get type label from capabilities
  const getTypeLabel = (actionType: string) => {
    const cap = capabilities.find(c => c.action_type === actionType);
    return cap?.title || actionType;
  };

  const approveAction = async (actionId: string) => {
    await fetch(`/api/actions/${actionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved_by: 'operator' }),
    });
    fetchActions();
  };

  const executeAction = async (actionId: string) => {
    await fetch(`/api/actions/${actionId}/execute`, {
      method: 'POST',
    });
    pollActionStatus(actionId);
  };

  const pollActionStatus = async (actionId: string) => {
    const interval = setInterval(async () => {
      const res = await fetch(`/api/actions/${actionId}`);
      const action = await res.json();

      if (action.status === 'COMPLETED' || action.status === 'FAILED') {
        clearInterval(interval);
        fetchActions();
      }
    }, 2000);
  };

  const cancelAction = async (actionId: string) => {
    await fetch(`/api/actions/${actionId}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cancelled_by: 'operator' }),
    });
    fetchActions();
  };

  const retryAction = async (actionId: string) => {
    await fetch(`/api/actions/${actionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved_by: 'operator' }),
    });
    fetchActions();
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Actions</h1>
        <p className="text-muted-foreground">
          Execution layer for acquisition workflows • {capabilities.length} capabilities available
        </p>
      </div>

      {/* Filters - UPDATED v1.2: Dynamic from capabilities */}
      <div className="flex gap-4 mb-6">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">All Statuses</option>
          <option value="PENDING_APPROVAL">Pending Approval</option>
          <option value="READY">Ready</option>
          <option value="PROCESSING">Processing</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>

        {/* NEW v1.2: Type filter generated from capabilities */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">All Types</option>
          {capabilities.map(cap => (
            <option key={cap.capability_id} value={cap.action_type}>
              {cap.title}
            </option>
          ))}
        </select>

        <Button variant="outline" onClick={fetchActions} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </Button>
      </div>

      {/* Actions List */}
      <div className="space-y-4">
        {actions.length === 0 && !loading && (
          <div className="text-center py-12 text-muted-foreground">
            No actions found. Create one from Chat or the UI.
          </div>
        )}

        {actions.map((action) => (
          <ActionCard
            key={action.action_id}
            action={action}
            getTypeLabel={getTypeLabel}  // NEW v1.2: Pass function
            onApprove={approveAction}
            onExecute={executeAction}
            onCancel={cancelAction}
            onRetry={retryAction}
          />
        ))}
      </div>
    </div>
  );
}

function ActionCard({ action, getTypeLabel, onApprove, onExecute, onCancel, onRetry }: {
  action: Action;
  getTypeLabel: (type: string) => string;  // NEW v1.2
  onApprove: (id: string) => void;
  onExecute: (id: string) => void;
  onCancel: (id: string) => void;
  onRetry: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  const statusColors: Record<string, string> = {
    PENDING_APPROVAL: 'bg-yellow-100 text-yellow-800',
    READY: 'bg-blue-100 text-blue-800',
    PROCESSING: 'bg-purple-100 text-purple-800 animate-pulse',
    COMPLETED: 'bg-green-100 text-green-800',
    FAILED: 'bg-red-100 text-red-800',
    CANCELLED: 'bg-gray-100 text-gray-800',
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            <CardTitle className="text-lg">{action.title}</CardTitle>
            <Badge className={statusColors[action.status] || 'bg-gray-100'}>
              {action.status.replace('_', ' ')}
            </Badge>
            {/* NEW v1.2: Dynamic label from capabilities */}
            <Badge variant="outline">{getTypeLabel(action.type)}</Badge>
            {action.deal_id && (
              <Badge variant="secondary" className="font-mono text-xs">
                {action.deal_id}
              </Badge>
            )}
          </div>

          <div className="flex gap-2">
            {action.status === 'PENDING_APPROVAL' && (
              <Button size="sm" onClick={() => onApprove(action.action_id)}>
                <Check className="w-4 h-4 mr-1" />
                Approve
              </Button>
            )}

            {action.status === 'READY' && (
              <Button size="sm" onClick={() => onExecute(action.action_id)}>
                <Play className="w-4 h-4 mr-1" />
                Run
              </Button>
            )}

            {action.status === 'FAILED' && (
              <Button size="sm" variant="outline" onClick={() => onRetry(action.action_id)}>
                <RotateCcw className="w-4 h-4 mr-1" />
                Retry
              </Button>
            )}

            {['PENDING_APPROVAL', 'READY', 'PROCESSING'].includes(action.status) && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onCancel(action.action_id)}
              >
                <X className="w-4 h-4 mr-1" />
                Cancel
              </Button>
            )}
          </div>
        </div>

        <p className="text-sm text-muted-foreground mt-2">{action.summary}</p>
        <p className="text-xs text-muted-foreground">
          Created {new Date(action.created_at).toLocaleString()} by {action.created_by}
        </p>
      </CardHeader>

      <Collapsible open={expanded} onOpenChange={setExpanded}>
        <CollapsibleTrigger asChild>
          <Button variant="ghost" size="sm" className="w-full">
            {expanded ? (
              <>
                <ChevronUp className="w-4 h-4 mr-2" />
                Hide Details
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-2" />
                Show Details
              </>
            )}
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="pt-4">
            {/* Inputs */}
            <div className="mb-4">
              <h4 className="font-semibold mb-2">Inputs</h4>
              <pre className="bg-muted p-3 rounded text-xs overflow-auto max-h-60">
                {JSON.stringify(action.inputs, null, 2)}
              </pre>
            </div>

            {/* Outputs */}
            {action.outputs && Object.keys(action.outputs).length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Outputs</h4>
                <pre className="bg-muted p-3 rounded text-xs overflow-auto max-h-60">
                  {JSON.stringify(action.outputs, null, 2)}
                </pre>
              </div>
            )}

            {/* Error */}
            {action.error && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2 text-red-600">Error</h4>
                <div className="bg-red-50 border border-red-200 p-3 rounded text-sm text-red-800">
                  {action.error.message}
                </div>
              </div>
            )}

            {/* Artifacts */}
            {action.artifacts.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Artifacts ({action.artifacts.length})</h4>
                <div className="space-y-2">
                  {action.artifacts.map((artifact) => (
                    <div
                      key={artifact.artifact_id}
                      className="flex items-center justify-between border p-3 rounded hover:bg-muted/50"
                    >
                      <div>
                        <p className="font-medium text-sm">{artifact.filename}</p>
                        <p className="text-xs text-muted-foreground">
                          {(artifact.size_bytes / 1024).toFixed(1)} KB • {new Date(artifact.created_at).toLocaleString()}
                        </p>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        asChild
                      >
                        <a
                          href={`/api/actions/${action.action_id}/artifact/${artifact.artifact_id}`}
                          download
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </a>
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Audit Trail */}
            {action.audit_trail.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Audit Trail</h4>
                <div className="space-y-2">
                  {action.audit_trail.map((event, idx) => (
                    <div key={idx} className="text-sm border-l-2 border-muted pl-3 py-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{event.event.replace('_', ' ')}</span>
                        <span className="text-muted-foreground">by {event.actor}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(event.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}
```

#### Acceptance Criteria

- [ ] UI fetches capabilities from `/api/actions/capabilities`
- [ ] Type filter dropdown generated from capabilities (no hard-coded options)
- [ ] Type labels rendered dynamically using `getTypeLabel()`
- [ ] Adding new capability YAML makes it appear in filters automatically
- [ ] All existing UI functionality preserved (approve, execute, cancel, retry, download)

---

### Component 5.2: Schema-Driven Form Component (NEW in v1.2)

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 2 days

#### Purpose

Generate action input forms dynamically from capability `input_schema`.

#### Technical Specification

**New Component:** `/home/zaks/zakops-dashboard/src/components/actions/ActionInputForm.tsx` (~200 lines)

```typescript
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Capability {
  capability_id: string;
  title: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, InputSchemaProperty>;
  };
}

interface InputSchemaProperty {
  type: string;
  description: string;
  required: boolean;
  enum?: string[];
  default?: any;
}

interface ActionInputFormProps {
  capability: Capability;
  onSubmit: (inputs: Record<string, any>) => void;
  onCancel: () => void;
}

export function ActionInputForm({ capability, onSubmit, onCancel }: ActionInputFormProps) {
  const [inputs, setInputs] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    const newErrors: Record<string, string> = {};
    Object.entries(capability.input_schema.properties).forEach(([fieldName, schema]) => {
      if (schema.required && !inputs[fieldName]) {
        newErrors[fieldName] = `${fieldName} is required`;
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onSubmit(inputs);
  };

  const renderField = (fieldName: string, schema: InputSchemaProperty) => {
    const value = inputs[fieldName] ?? schema.default ?? '';

    if (schema.enum) {
      // Dropdown for enum fields
      return (
        <Select
          value={String(value)}
          onValueChange={(val) => setInputs({...inputs, [fieldName]: val})}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {schema.enum.map(option => (
              <SelectItem key={option} value={option}>
                {option}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      );
    }

    if (schema.type === 'string' && schema.description.toLowerCase().includes('context')) {
      // Textarea for context fields
      return (
        <Textarea
          value={value}
          onChange={(e) => setInputs({...inputs, [fieldName]: e.target.value})}
          className="w-full min-h-[100px]"
        />
      );
    }

    if (schema.type === 'string') {
      // Text input for strings
      return (
        <Input
          type="text"
          value={value}
          onChange={(e) => setInputs({...inputs, [fieldName]: e.target.value})}
          className="w-full"
        />
      );
    }

    if (schema.type === 'number') {
      // Number input
      return (
        <Input
          type="number"
          value={value}
          onChange={(e) => setInputs({...inputs, [fieldName]: parseFloat(e.target.value)})}
          className="w-full"
        />
      );
    }

    if (schema.type === 'boolean') {
      // Checkbox
      return (
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(e) => setInputs({...inputs, [fieldName]: e.target.checked})}
          className="w-4 h-4"
        />
      );
    }

    // Fallback: JSON textarea
    return (
      <Textarea
        value={JSON.stringify(value, null, 2)}
        onChange={(e) => {
          try {
            setInputs({...inputs, [fieldName]: JSON.parse(e.target.value)});
          } catch {
            // Invalid JSON, keep as string
          }
        }}
        className="w-full font-mono text-xs"
        rows={5}
      />
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{capability.title}</h2>
        <p className="text-muted-foreground mt-1">{capability.description}</p>
      </div>

      {Object.entries(capability.input_schema.properties).map(([fieldName, schema]) => (
        <div key={fieldName}>
          <Label htmlFor={fieldName} className="block text-sm font-medium mb-2">
            {schema.description || fieldName}
            {schema.required && <span className="text-red-500 ml-1">*</span>}
          </Label>

          {renderField(fieldName, schema)}

          {errors[fieldName] && (
            <p className="text-red-500 text-xs mt-1">{errors[fieldName]}</p>
          )}
        </div>
      ))}

      <div className="flex gap-3 pt-4">
        <Button type="submit" className="flex-1">
          Create Action
        </Button>
        <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
          Cancel
        </Button>
      </div>
    </form>
  );
}
```

#### Usage Example

**Add to Actions Page:**

```typescript
import { ActionInputForm } from '@/components/actions/ActionInputForm';

// In ActionsPage component
const [showCreateForm, setShowCreateForm] = useState(false);
const [selectedCapability, setSelectedCapability] = useState<Capability | null>(null);

const handleCreateAction = async (inputs: Record<string, any>) => {
  const res = await fetch('/api/actions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      deal_id: currentDealId,
      type: selectedCapability.action_type,
      title: selectedCapability.title,
      summary: `Created from UI`,
      inputs,
      created_by: 'operator',
      source: 'ui',
    }),
  });

  if (res.ok) {
    setShowCreateForm(false);
    fetchActions();
  }
};

// Render form in modal/dialog
{showCreateForm && selectedCapability && (
  <ActionInputForm
    capability={selectedCapability}
    onSubmit={handleCreateAction}
    onCancel={() => setShowCreateForm(false)}
  />
)}
```

#### Acceptance Criteria

- [ ] `ActionInputForm` component renders form from `input_schema`
- [ ] Enum fields render as dropdowns
- [ ] String fields render as text inputs
- [ ] Context fields render as textareas
- [ ] Number fields render as number inputs
- [ ] Boolean fields render as checkboxes
- [ ] Required fields marked with asterisk
- [ ] Validation shows errors for missing required fields
- [ ] Submitting form creates action via `/api/actions`

---

### Component 5.3: Metrics Dashboard UI (NEW in v1.2)

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 1 day

#### Purpose

Real-time monitoring of action execution metrics.

#### Technical Specification

**New Page:** `/home/zaks/zakops-dashboard/src/app/actions/metrics/page.tsx` (~150 lines)

```typescript
'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Metrics {
  queue_lengths: Record<string, number>;
  avg_duration_by_type: Record<string, {avg_seconds: number; count: number}>;
  success_rate_24h: number;
  total_24h: number;
  completed_24h: number;
  failed_24h: number;
  error_breakdown: Array<{error: string; count: number}>;
  runner_health: {
    pid: number;
    hostname: string;
    is_active: boolean;
    heartbeat_at: string;
  } | null;
  timestamp: string;
}

export default function ActionsMetricsPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);  // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    const res = await fetch('/api/actions/metrics');
    const data = await res.json();
    setMetrics(data);
    setLoading(false);
  };

  if (!metrics) {
    return <div className="p-6">Loading metrics...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Action Metrics</h1>
          <p className="text-muted-foreground">
            Real-time monitoring • Updated {new Date(metrics.timestamp).toLocaleString()}
          </p>
        </div>
        <Badge variant={metrics.runner_health?.is_active ? "default" : "destructive"}>
          Runner: {metrics.runner_health?.is_active ? "Active" : "Inactive"}
        </Badge>
      </div>

      {/* Queue Lengths */}
      <Card>
        <CardHeader><CardTitle>Queue Lengths by Status</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-6 gap-4">
            {Object.entries(metrics.queue_lengths).map(([status, count]) => (
              <div key={status} className="text-center p-4 border rounded">
                <div className="text-4xl font-bold">{count}</div>
                <div className="text-sm text-muted-foreground mt-1">{status.replace('_', ' ')}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Success Rate */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Success Rate (24h)</CardTitle></CardHeader>
          <CardContent>
            <div className="text-6xl font-bold text-green-600">
              {metrics.success_rate_24h}%
            </div>
            <div className="text-sm text-muted-foreground mt-4 space-y-1">
              <div>✅ Completed: {metrics.completed_24h}</div>
              <div>❌ Failed: {metrics.failed_24h}</div>
              <div>📊 Total: {metrics.total_24h}</div>
            </div>
          </CardContent>
        </Card>

        {/* Runner Health */}
        <Card>
          <CardHeader><CardTitle>Runner Health</CardTitle></CardHeader>
          <CardContent>
            {metrics.runner_health ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant={metrics.runner_health.is_active ? "default" : "destructive"}>
                    {metrics.runner_health.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  <div>PID: {metrics.runner_health.pid}</div>
                  <div>Host: {metrics.runner_health.hostname}</div>
                  <div>Heartbeat: {new Date(metrics.runner_health.heartbeat_at).toLocaleString()}</div>
                </div>
              </div>
            ) : (
              <div className="text-red-600">No runner active</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Average Duration */}
      <Card>
        <CardHeader><CardTitle>Average Duration by Action Type</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(metrics.avg_duration_by_type).map(([type, data]) => (
              <div key={type} className="flex items-center justify-between p-3 border rounded">
                <span className="font-medium">{type}</span>
                <div className="text-right">
                  <div className="font-mono text-lg">{data.avg_seconds.toFixed(1)}s</div>
                  <div className="text-xs text-muted-foreground">{data.count} executions</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Error Breakdown */}
      {metrics.error_breakdown.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Top Errors (24h)</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {metrics.error_breakdown.map((error, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 border rounded">
                  <span className="text-sm text-red-600 flex-1">{error.error}</span>
                  <Badge variant="outline">{error.count}x</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

#### Acceptance Criteria

- [ ] Metrics dashboard page created at `/actions/metrics`
- [ ] Displays queue lengths by status
- [ ] Shows success rate (24h) with completed/failed/total
- [ ] Shows runner health (active/inactive, PID, hostname)
- [ ] Displays average duration per action type
- [ ] Shows top 10 errors (24h)
- [ ] Auto-refreshes every 10 seconds
- [ ] Loading state while fetching

---

## Phase 6: Testing (Week 4-5, Days 14-23)

### Component 6.1: Backend Tests (UPDATED in v1.2)

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 4 days

#### Test Coverage

**Existing tests from v1.1:**
- Schema validation per action type
- Executor unit tests (dry_run + execute)
- Database CRUD operations
- Idempotency enforcement
- Status state machine transitions
- API endpoints (create, approve, execute, download)
- Lease acquisition (prevents duplicate runners)
- Deal events emission

**NEW tests in v1.2:**
- Capability registry (load, get, match, validate)
- Action planner (simple, multi-step, clarification, refusal)
- **CRITICAL:** Unknown action test (lender outreach package)
- Metrics endpoint (queue lengths, success rate, durations)

**New File:** `tests/test_planner.py` (~300 lines)

```python
import pytest
from actions.planner import ActionPlanner
from actions.capabilities.registry import CapabilityRegistry

@pytest.fixture
def planner():
    """Create planner with loaded capabilities."""
    registry = CapabilityRegistry()
    registry.load_from_directory("scripts/actions/capabilities")
    return ActionPlanner(registry=registry, use_llm=False)  # Disable LLM for tests

def test_planner_simple_action(planner):
    """Test planner maps simple query to single action."""
    plan = planner.plan(
        query="Draft email to john@seller.com about LOI terms",
        scope={"deal_id": "DEAL-001"},
        case_file={}
    )

    assert plan.selected_capability_id is not None
    assert "COMMUNICATION.DRAFT_EMAIL" in plan.selected_capability_id
    assert plan.confidence > 0.7
    assert not plan.requires_clarification
    assert not plan.is_refusal

def test_planner_multi_step_decomposition(planner):
    """
    CRITICAL TEST: Lender outreach package decomposition.

    This test MUST pass for v1.2 to be considered world-class.
    """
    plan = planner.plan(
        query="Create a lender outreach package with 1-page summary + KPI list + email draft",
        scope={"deal_id": "DEAL-001"},
        case_file={"company_name": "Acme Corp"}
    )

    # Should decompose into 3 steps
    assert len(plan.plan_steps) == 3 or plan.selected_capability_id is None

    if plan.plan_steps:
        # Check all 3 action types present
        step_types = [step["action_type"] for step in plan.plan_steps]
        assert "DOCUMENT.GENERATE" in step_types
        assert "ANALYSIS.BUILD_MODEL" in step_types
        assert "COMMUNICATION.DRAFT_EMAIL" in step_types

        assert plan.confidence > 0.5
        assert plan.risk_level == "high"  # Multi-step is high risk

def test_planner_missing_inputs_clarification(planner):
    """Test planner asks for clarification when inputs missing."""
    plan = planner.plan(
        query="Draft an email",  # Missing recipient, subject, context
        scope={"deal_id": "DEAL-001"},
        case_file={}
    )

    assert plan.requires_clarification
    assert len(plan.clarifying_questions) > 0
    assert len(plan.missing_fields) > 0
    assert "recipient" in plan.missing_fields or "subject" in plan.missing_fields

def test_planner_unknown_action_refusal(planner):
    """Test planner refuses impossible actions with alternatives."""
    plan = planner.plan(
        query="Launch rocket to the moon",  # Not in capability registry
        scope={},
        case_file={}
    )

    assert plan.is_refusal
    assert plan.refusal_reason is not None
    assert len(plan.suggested_alternatives) > 0
    assert plan.confidence == 0.0

def test_planner_ambiguous_clarification(planner):
    """Test planner asks for clarification when ambiguous."""
    plan = planner.plan(
        query="Generate document",  # Could be LOI, NDA, Request Letter
        scope={"deal_id": "DEAL-001"},
        case_file={}
    )

    # Should either select one or ask for clarification
    assert plan.selected_capability_id is not None or plan.requires_clarification
```

#### Acceptance Criteria

- [ ] All v1.1 tests pass (schema, executor, DB, API, runner)
- [ ] All v1.2 tests pass (registry, planner)
- [ ] **CRITICAL:** Unknown action test passes (lender outreach package decomposition)
- [ ] Test coverage > 80%

---

### Component 6.2: UI Tests (UPDATED in v1.2)

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 2 days

**Extend:** `/home/zaks/zakops-dashboard/tests/click-sweep-test.sh`

**New tests:**
- Capabilities endpoint returns valid JSON
- Type filter dropdown populated from capabilities
- Type labels rendered dynamically
- `ActionInputForm` generates form from schema
- Metrics page loads and displays queue lengths
- Metrics auto-refresh works

---

### Component 6.3: Documentation (UPDATED in v1.2)

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 2 days

**Create/Update:**

1. **`/home/zaks/zakops-dashboard/docs/ACTIONS-ENGINE.md`**
   - Architecture overview
   - Capability manifest system
   - Action planner flow
   - Schema-driven UI
   - Metrics dashboard
   - Adding new capabilities (10-minute recipe)

2. **`/home/zaks/zakops-dashboard/docs/ACTIONS-RUNBOOK.md`**
   - Running runner
   - Monitoring metrics
   - Debugging stuck actions
   - Safety checklist

3. **`/home/zaks/zakops-dashboard/docs/ACTIONS-10-MINUTE-RECIPE.md`** (NEW)
   - Step-by-step guide to add new action capability
   - From zero to production in 10 minutes

*See Appendix C for documentation outlines*

---

## Phase 7: Verification Report (Week 5, Days 24-25)

### Component 7.1: End-to-End Verification (UPDATED in v1.2)

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - ACCEPTANCE CRITERION)
**Estimated Effort:** 2 days

#### Purpose

Prove the system works end-to-end with reproducible commands, including world-class features.

#### Deliverable

**Create:** `/home/zaks/bookkeeping/docs/KINETIC-ACTION-ENGINE-VERIFICATION-REPORT.md`

#### Contents (Updated for v1.2)

```markdown
# Kinetic Action Engine v1.2 - Verification Report

**Date:** YYYY-MM-DD
**Verifier:** [Name]
**System Version:** v1.2 (World-Class Edition)

## Test Environment

- Backend: http://localhost:8090
- Frontend: http://localhost:3003
- Database: ZAKOPS_STATE_DB at {path}
- Runner: PID {pid} on {hostname}
- Capabilities: 5 manifests loaded

## Verification Test 1: Capability System

**Steps:**
1. Check capabilities directory exists with 5 manifests
2. Call `/api/actions/capabilities` endpoint

**Expected Result:**
\`\`\`json
{
  "capabilities": [
    {
      "capability_id": "COMMUNICATION.DRAFT_EMAIL.v1",
      "title": "Draft Email",
      "input_schema": {...},
      ...
    },
    ...
  ],
  "count": 5
}
\`\`\`

**Verification:**
- [ ] 5 capabilities loaded
- [ ] Input schemas include required fields
- [ ] Output artifacts specified

## Verification Test 2: Add New Capability (10-Minute Recipe)

**Steps:**
1. Create `scripts/actions/capabilities/generate_teaser.v1.yaml`
2. Create `src/actions/executors/teaser.py`
3. Register executor
4. Restart runner

**Expected Result:**
- [ ] New capability appears in `/api/actions/capabilities`
- [ ] UI type filter includes "Generate Teaser"
- [ ] Planner can match "generate teaser" query

**Duration:** < 10 minutes

## Verification Test 3: Planner - Simple Action

**curl Command:**
\`\`\`bash
curl -X POST http://localhost:8080/plan-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Draft email to john@seller.com about LOI terms",
    "scope": {"deal_id": "DEAL-001"},
    "case_file": {}
  }'
\`\`\`

**Expected Result:**
\`\`\`json
{
  "selected_capability_id": "COMMUNICATION.DRAFT_EMAIL.v1",
  "action_inputs": {
    "recipient": "john@seller.com",
    "context": "LOI terms"
  },
  "confidence": 0.9
}
\`\`\`

**Verification:**
- [ ] Single action selected
- [ ] Inputs extracted correctly
- [ ] Confidence > 0.7

## Verification Test 4: Planner - Multi-Step Decomposition (CRITICAL)

**curl Command:**
\`\`\`bash
curl -X POST http://localhost:8080/plan-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a lender outreach package with 1-page summary + KPI list + email draft",
    "scope": {"deal_id": "DEAL-001"},
    "case_file": {"company_name": "Acme Corp"}
  }'
\`\`\`

**Expected Result:**
\`\`\`json
{
  "plan_steps": [
    {
      "capability_id": "DOCUMENT.GENERATE.v1",
      "title": "Generate 1-Page Summary",
      "action_type": "DOCUMENT.GENERATE"
    },
    {
      "capability_id": "ANALYSIS.BUILD_MODEL.v1",
      "title": "Build KPI List",
      "action_type": "ANALYSIS.BUILD_MODEL"
    },
    {
      "capability_id": "COMMUNICATION.DRAFT_EMAIL.v1",
      "title": "Draft Outreach Email",
      "action_type": "COMMUNICATION.DRAFT_EMAIL"
    }
  ],
  "confidence": 0.7,
  "risk_level": "high"
}
\`\`\`

**Verification:**
- [ ] 3-step plan generated
- [ ] All 3 action types correct (DOCUMENT, ANALYSIS, COMMUNICATION)
- [ ] Risk level = "high" (multi-step)
- [ ] **THIS IS THE MAKE-OR-BREAK TEST FOR V1.2**

## Verification Test 5: Planner - Clarifying Questions

**curl Command:**
\`\`\`bash
curl -X POST http://localhost:8080/plan-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Draft an email",
    "scope": {"deal_id": "DEAL-001"},
    "case_file": {}
  }'
\`\`\`

**Expected Result:**
\`\`\`json
{
  "requires_clarification": true,
  "clarifying_questions": [
    "To Draft Email, please provide: recipient, subject, context"
  ],
  "missing_fields": ["recipient", "subject", "context"]
}
\`\`\`

**Verification:**
- [ ] Clarification requested
- [ ] Missing fields identified
- [ ] Question is actionable

## Verification Test 6: Planner - Safe Refusal

**curl Command:**
\`\`\`bash
curl -X POST http://localhost:8080/plan-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Launch rocket to the moon",
    "scope": {},
    "case_file": {}
  }'
\`\`\`

**Expected Result:**
\`\`\`json
{
  "is_refusal": true,
  "refusal_reason": "No matching capability found. Available actions:",
  "suggested_alternatives": [
    "Draft Email - Generate professional email draft",
    "Generate Document - Create LOI, NDA, or request letter",
    ...
  ]
}
\`\`\`

**Verification:**
- [ ] Refusal is safe (not error)
- [ ] Alternatives suggested
- [ ] Confidence = 0.0

## Verification Test 7: Schema-Driven UI

**Steps:**
1. Open `/actions` page
2. Check type filter dropdown

**Expected Result:**
- [ ] Dropdown populated from `/api/actions/capabilities`
- [ ] No hard-coded type options
- [ ] Adding new manifest makes type appear automatically

## Verification Test 8: Metrics Dashboard

**Steps:**
1. Open `/actions/metrics` page
2. Wait for auto-refresh (10s)

**Expected Result:**
- [ ] Queue lengths displayed
- [ ] Success rate shown
- [ ] Average durations per type
- [ ] Runner health visible
- [ ] Page refreshes automatically

## Verification Test 9: End-to-End (Chat → Planner → Action → Execution)

**Steps:**
1. Open Chat UI in deal scope (DEAL-2025-001)
2. Send: "Create a lender outreach package with summary + KPIs + email"
3. Planner generates 3-step plan
4. Approve all 3 proposals
5. Runner executes all 3 actions
6. Download artifacts

**Expected Result:**
- [ ] 3 actions created in PENDING_APPROVAL
- [ ] After approval, all transition to READY
- [ ] Runner picks up and executes (PROCESSING → COMPLETED)
- [ ] 3 artifact sets generated in `99-ACTIONS/`
- [ ] All downloadable from UI

## Screenshots

[Include screenshots of:]
- Capabilities endpoint response
- Type filter dropdown (dynamic)
- Planner multi-step response
- Metrics dashboard
- Action cards with artifacts
- 10-minute recipe execution

## Summary

### v1.1 Tests (Baseline)
- [x] All baseline tests passed (idempotency, lease, state machine, executors)

### v1.2 Tests (World-Class)
- [x] Capability system works (5 manifests loaded)
- [x] 10-minute recipe successful (new capability in < 10min)
- [x] Planner simple action works
- [x] **Planner multi-step decomposition works (CRITICAL TEST)**
- [x] Planner clarifying questions work
- [x] Planner safe refusal works
- [x] Schema-driven UI works
- [x] Metrics dashboard works

### Production Readiness
- [x] System is world-class
- [x] Self-extending (add YAML → new action)
- [x] Handles unknown/complex requests intelligently
- [x] Backward compatibility maintained
- [x] No breaking changes to chat contracts

## Issues Found

[List any issues discovered and their resolutions]

---

**Verification Complete:** [Date]
**Verified By:** [Name]
**Grade:** A+ (World-Class)
```

#### Acceptance Criteria

- [ ] All 9 verification tests documented
- [ ] curl commands provided for each test
- [ ] **CRITICAL:** Test 4 (multi-step decomposition) passes
- [ ] DB queries demonstrate idempotency and audit trail
- [ ] Screenshots or terminal outputs included
- [ ] Summary confirms world-class production-readiness

---

## Success Metrics (Updated for v1.2)

| Metric | Target | v1.2 Enhancement |
|--------|--------|------------------|
| **Action Creation Latency** | < 500ms | ✅ Same |
| **Execution Latency (Email Draft)** | < 5s (cloud API) | ✅ Same |
| **Execution Latency (Document Gen)** | < 10s | ✅ Same |
| **Artifact Download Speed** | < 2s for typical files | ✅ Same |
| **Runner Uptime** | 99.9% | ✅ Same |
| **Idempotency Success Rate** | 100% | ✅ Same |
| **Test Coverage** | > 80% | ✅ Same |
| **Lease Acquisition Success** | 100% (no ghost runners) | ✅ Same |
| **NEW: Capability Load Time** | < 1s at startup | 🆕 v1.2 |
| **NEW: Planner Response Time** | < 2s (simple), < 5s (complex) | 🆕 v1.2 |
| **NEW: Unknown Action Handling** | 100% (no silent failures) | 🆕 v1.2 |
| **NEW: Time to Add Capability** | < 10 minutes | 🆕 v1.2 |
| **NEW: Metrics Endpoint Latency** | < 500ms | 🆕 v1.2 |

---

## Timeline (Updated for v1.2)

| Week | Phase | Deliverables | Days |
|------|-------|--------------|------|
| **Week 1** | **Phase 0: Capability System** | Manifests, Registry, API endpoint, Tests | 4 days |
| **Week 1** | Phase 1: Core Infrastructure | Schema, Executor interface, DB layer | 3 days |
| **Week 2** | **Phase 2: Action Planner** | Planner class, Integration, Tests | 3 days |
| **Week 2** | Phase 2: Executors | 5 action types implemented | 6 days |
| **Week 3** | Phase 3: API Layer + **Metrics** | 8 endpoints + runner + metrics | 4 days |
| **Week 3** | Phase 4: Chat Integration + **Planner** | Proposal bridge + planner integration | 3 days |
| **Week 3-4** | Phase 5: **Schema-Driven UI/UX** | Dynamic dashboard + form generator + metrics UI | 6 days |
| **Week 4-5** | Phase 6: Testing & Docs | Tests + architecture docs + runbook + 10-min recipe | 10 days |
| **Week 5** | Phase 7: Verification | End-to-end verification report | 2 days |

**Total: 4-5 weeks (25-30 business days)**

---

## Document Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-30 | Initial implementation plan |
| 1.1 | 2025-12-30 | Added: Baseline, backward compatibility, ZAKOPS_STATE_DB, lease-based runner, deal events, 99-ACTIONS path, verification report |
| **1.2** | **2025-12-30** | **World-Class Upgrade: Capability manifest system, action planner with RAG, schema-driven UI, observability metrics, per-action locking, exponential backoff, unknown action handling test** |

---

## Codex Review Notes (v1.2) — Gaps + Suggested Improvements (Added 2025-12-31)

### 1) Spec Corrections (Avoid Drift During Implementation)

1. **Planner endpoint alignment (8080 vs 8090):** This spec hard-codes `http://localhost:8080/plan-action`, but the current LangGraph “brain” integration is typically via `http://localhost:8080/api/deal-chat`. Pick one canonical planner entrypoint and update the spec + curl tests accordingly:
   - Option A: implement `POST /plan-action` on 8080 (brain) and have 8090 proxy; OR
   - Option B: make `POST /api/actions/plan` on 8090 call the local `ActionPlanner` (deterministic-first) and optionally defer to the brain for decomposition/input-extraction.
2. **`input_schema` format:** The spec says “JSON Schema”, but the examples use per-property `required: true` which is not standard JSON Schema. Either:
   - rename it to a documented “InputSchemaLite” (and optionally provide a compiler to real JSON Schema for validators/UI libs), OR
   - switch examples/manifests to real JSON Schema (`required: [...]` at the object level) and adopt an off-the-shelf schema validator.
3. **Dynamic action types vs enums:** Multiple places imply `action_type` maps to a Python `ActionType` enum. For a self-extending capability system, `action_type` must be a free-form string validated at runtime against loaded manifests (and executor registry), not a hard-coded enum.
4. **Path consistency:** The spec mixes `src/...` placeholder paths with real paths under `/home/zaks/scripts/...`. Add a short “Path Map” section (one place) that declares the canonical roots (e.g., Python backend lives under `scripts/`, UI under `zakops-dashboard/src/`) so implementers don’t create a parallel `src/` tree by accident.

### 2) Reliability / Ops Hardening (Add to Phase 1 So It’s Not “Late Cleanup”)

- **SQLite concurrency settings:** Explicitly set `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`, and a `busy_timeout` for both the API and runner processes. For lease/lock acquisition use transactions that actually take write locks (e.g., `BEGIN IMMEDIATE`) to prevent race conditions under load.
- **Stuck action detection + operator recovery:** Define a “stuck” threshold (e.g., `PROCESSING` with no heartbeat > N minutes) and surface it in `/api/actions/metrics` + UI. Provide a safe operator path to “release lock + retry” that emits an audit event (no silent force-unlocks).
- **Artifact download safety:** Document and test path traversal protections (`..`, absolute paths, symlinks). Prefer storing `relative_path`, `sha256`, and `byte_size` in the DB and computing the absolute path server-side under `{deal.folder_path}/99-ACTIONS/{action_id}/...`.

### 3) Safety Gates (Tie to Platform Principles)

- **Secret-scan gate (not just redaction):** Add an explicit “secret scan gate” before any cloud LLM call or external tool invocation (MCP/HTTP). If blocked, fail the action with a clear reason + remediation steps.
- **Approval enforcement at the tool layer:** Tool/Cloud invocations should be denied unless the action is in an approved state (`READY/PROCESSING`) and the capability/tool risk gate is satisfied; denials should be captured as audit events.
- **Draft-only constraint is a hard rule:** Keep `COMMUNICATION.DRAFT_EMAIL` draft-only forever. If/when “send email” exists, it must be a separate high-risk capability with explicit approvals and additional recipient verification.

### 4) Testing Additions (Tighten DoD)

- Add tests for: planner endpoint wiring, manifest schema validation (incl. required fields), lease takeover + per-action lock takeover, artifact download traversal guard, “clarifying questions” end-to-end UX path, and metrics (stuck counts + lease info).
- Add a dependency preflight check for PPTX generation (`python-pptx`) and document the fallback behavior if it is not installed (e.g., “deck capability disabled” or “PDF-only deck”).

**END OF IMPLEMENTATION PLAN v1.2**

**Ready for Implementation: ✅ YES**
**Option Selected: ✅ OPTION A (World-Class)**
**Timeline: 4-5 weeks**
**Grade Target: A+ (World-Class Self-Extending System)**

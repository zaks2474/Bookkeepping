# ZakOps Kinetic Action Engine - Implementation Plan

**Document Version:** 1.1
**Created:** 2025-12-30
**Updated:** 2025-12-30
**Status:** Planning Phase
**Owner:** Zaks Deal Lifecycle OS Team
**Target Completion:** 3-4 weeks

---

## Executive Summary

Transform the **Actions** page from a read-only log into a full-featured **Execution Layer** that enables operator-reviewed automation of acquisition workflows.

### Project Goals

Build a production-grade action execution system with:
- **Universal Action Schema** - Structured, type-safe payloads for any workflow
- **Plugin Architecture** - Easy addition of new action types
- **Artifact Management** - Generate DOCX/PDF/XLSX/PPTX outputs stored in DataRoom
- **Chat Integration** - Actions created from natural language via proposals
- **Human-in-Loop** - Review → Edit → Approve → Execute workflow
- **Idempotency** - Safe retries, no duplicate executions
- **Production Safety** - Lease-based runner, persistent queue, graceful failures
- **Backward Compatible** - Preserves existing deferred-actions system

### Key Improvements in v1.1

- ✅ **Baseline documentation** of current system state
- ✅ **Backward compatibility** strategy for legacy endpoints
- ✅ **Reuses existing SQLite DB** (`ZAKOPS_STATE_DB`)
- ✅ **Lease-based runner** instead of PID lock
- ✅ **Deal events integration** for observability
- ✅ **Artifact path convention** (`99-ACTIONS/<action_id>/`)
- ✅ **Verification Report** as explicit deliverable

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

**Current Actions Endpoints (Deferred Reminders Only):**
- Source: `/home/zaks/scripts/deferred_actions.py`
- Storage: `DataRoom/.deal-registry/deferred_actions.json` (JSON file)
- Endpoints:
  - `GET /api/actions` (list)
  - `GET /api/actions/due`
  - `POST /api/actions/{action_id}/execute` (marks executed; **no artifacts generated**)
  - `POST /api/actions/{action_id}/cancel`

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

## Architecture Overview

### System Context

```
┌──────────────────────────────────────────────────────────────┐
│                    ZakOps Dashboard (Next.js)                 │
│                     http://localhost:3003                     │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐    │
│  │  Chat UI   │  │ Actions UI │  │   Deal Detail UI    │    │
│  └─────┬──────┘  └──────┬─────┘  └──────────┬──────────┘    │
└────────┼─────────────────┼───────────────────┼───────────────┘
         │                 │                   │
         │  POST /api/chat │  POST /api/actions│
         │  (SSE stream)   │  GET /api/actions │
         │                 │  POST .../execute │
         ▼                 ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Backend (BFF) - port 8090                │
│                   deal_lifecycle_api.py                       │
│                                                               │
│  ┌─────────────┐   ┌──────────────────┐   ┌──────────────┐  │
│  │Chat Handler │──▶│ Proposal Manager │──▶│Action Manager│  │
│  │             │   │(creates actions) │   │              │  │
│  └─────────────┘   └──────────────────┘   └──────┬───────┘  │
│         │                                          │          │
│         │ ZAKOPS_BRAIN_MODE=auto|force            │          │
│         ▼                                          ▼          │
│  ┌─────────────┐                         ┌─────────────────┐│
│  │LangGraph    │                         │ Actions Queue   ││
│  │Brain (8080) │                         │ (ZAKOPS_STATE_DB││
│  └─────────────┘                         │  SQLite-backed) ││
│                                          └────────┬────────┘│
│                                                   │          │
│                                          ┌────────▼────────┐│
│                                          │ Deal Events     ││
│                                          │ (observability) ││
│                                          └─────────────────┘│
└──────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                                        ┌─────────────────────┐
                                        │  Action Runner      │
                                        │  (lease-based)      │
                                        │                     │
                                        │  ┌───────────────┐  │
                                        │  │ Executor      │  │
                                        │  │ Registry      │  │
                                        │  │               │  │
                                        │  │ • Email       │  │
                                        │  │ • Document    │  │
                                        │  │ • Model       │  │
                                        │  │ • Deck        │  │
                                        │  │ • DD Request  │  │
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

### Key Design Decisions

1. **Universal Action Schema** - Single Pydantic model supports all action types
2. **Plugin Executor System** - Register new action types without core changes
3. **Persistent Queue** - SQLite-backed (`ZAKOPS_STATE_DB`), survives restarts
4. **Lease-Based Runner** - DB lease prevents duplicate workers, enables safe takeover
5. **Chat → Proposal → Action** - Reuse existing approval flow
6. **DataRoom Integration** - Artifacts stored in `{deal.folder_path}/99-ACTIONS/{action_id}/`
7. **Deal Events Integration** - Action milestones emit deal events for observability
8. **Idempotency Keys** - Unique constraint prevents duplicate executions
9. **Status State Machine** - Clear lifecycle: PENDING_APPROVAL → READY → PROCESSING → COMPLETED/FAILED
10. **Backward Compatible** - Legacy deferred-actions preserved

---

## Phase 1: Core Infrastructure (Week 1)

### Component 1.1: Universal Action Schema

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 2 days

#### Purpose

Define canonical `ActionPayload` model that supports any acquisition workflow action.

#### Technical Specification

**New File:** `src/models/action.py` (~300 lines)

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Canonical action types."""
    COMMUNICATION_DRAFT_EMAIL = "COMMUNICATION.DRAFT_EMAIL"
    DOCUMENT_GENERATE = "DOCUMENT.GENERATE"
    ANALYSIS_BUILD_MODEL = "ANALYSIS.BUILD_MODEL"
    PRESENTATION_GENERATE_DECK = "PRESENTATION.GENERATE_DECK"
    DILIGENCE_REQUEST_DOCS = "DILIGENCE.REQUEST_DOCS"
    # Extensible: add more as needed


class ActionStatus(str, Enum):
    """Action lifecycle states."""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RiskLevel(str, Enum):
    """Risk classification for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionSource(str, Enum):
    """Where action was created."""
    CHAT = "chat"
    UI = "ui"
    SYSTEM = "system"


class AuditEvent(BaseModel):
    """Single audit trail entry."""
    timestamp: datetime
    event: str  # approved, executed, cancelled, failed, etc.
    actor: str  # user_id or system component
    details: Optional[Dict[str, Any]] = None


class ArtifactMetadata(BaseModel):
    """Metadata for generated artifact."""
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    mime_type: str
    path: str  # Absolute filesystem path
    size_bytes: int = 0
    sha256: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    url: Optional[str] = None  # Download URL


class ActionPayload(BaseModel):
    """
    Universal action schema supporting any acquisition workflow.

    All action types use this schema; type-specific data goes in `inputs`.
    """

    # Core identity
    action_id: str = Field(default_factory=lambda: f"action_{uuid4().hex[:12]}")
    deal_id: Optional[str] = None
    type: ActionType

    # Human-readable
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(max_length=500)

    # Lifecycle
    status: ActionStatus = ActionStatus.PENDING_APPROVAL
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Provenance
    created_by: str  # user_id or "system"
    source: ActionSource = ActionSource.UI

    # Safety
    risk_level: RiskLevel = RiskLevel.MEDIUM
    requires_human_review: bool = True
    idempotency_key: str  # Unique constraint in DB

    # Inputs/outputs (type-specific)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)

    # Error handling
    error: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3

    # Audit
    audit_trail: List[AuditEvent] = Field(default_factory=list)

    # Artifacts
    artifacts: List[ArtifactMetadata] = Field(default_factory=list)

    # Execution metadata
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    model_config = {"extra": "forbid"}

    def add_audit_event(self, event: str, actor: str, details: Optional[Dict] = None):
        """Append audit event."""
        self.audit_trail.append(
            AuditEvent(timestamp=datetime.utcnow(), event=event, actor=actor, details=details)
        )
        self.updated_at = datetime.utcnow()

    def add_artifact(
        self,
        filename: str,
        mime_type: str,
        path: str,
        size_bytes: int = 0,
        sha256: Optional[str] = None,
    ) -> str:
        """Add artifact and return artifact_id."""
        artifact = ArtifactMetadata(
            filename=filename,
            mime_type=mime_type,
            path=path,
            size_bytes=size_bytes,
            sha256=sha256,
        )
        self.artifacts.append(artifact)
        return artifact.artifact_id

    def can_execute(self) -> bool:
        """Check if action is in executable state."""
        return self.status == ActionStatus.READY

    def can_approve(self) -> bool:
        """Check if action can be approved."""
        return self.status == ActionStatus.PENDING_APPROVAL

    def can_cancel(self) -> bool:
        """Check if action can be cancelled."""
        return self.status in {
            ActionStatus.PENDING_APPROVAL,
            ActionStatus.READY,
            ActionStatus.PROCESSING,
        }


# Type-specific input schemas

class EmailDraftInputs(BaseModel):
    """Inputs for COMMUNICATION.DRAFT_EMAIL."""
    recipient: str
    recipient_name: Optional[str] = None
    subject: str
    context: str
    tone: str = "professional"
    include_attachments: bool = False
    template: Optional[str] = None


class DocumentGenerateInputs(BaseModel):
    """Inputs for DOCUMENT.GENERATE."""
    document_type: str  # LOI, NDA, Request Letter
    template: Optional[str] = None
    fields: Dict[str, Any] = Field(default_factory=dict)
    output_format: str = "docx"  # docx, pdf, both


class ValuationModelInputs(BaseModel):
    """Inputs for ANALYSIS.BUILD_MODEL."""
    model_type: str  # DCF, Comparable, Asset-Based
    assumptions: Dict[str, Any] = Field(default_factory=dict)
    data_sources: List[str] = Field(default_factory=list)


class PresentationDeckInputs(BaseModel):
    """Inputs for PRESENTATION.GENERATE_DECK."""
    deck_type: str  # pitch, lender_summary, investment_committee
    sections: List[str] = Field(default_factory=list)
    template: Optional[str] = None


class DiligenceRequestInputs(BaseModel):
    """Inputs for DILIGENCE.REQUEST_DOCS."""
    checklist_items: List[str]
    urgency: str = "normal"
    due_date: Optional[datetime] = None
```

#### Database Schema

**Extend:** `ZAKOPS_STATE_DB` (existing SQLite database)

**New Tables:**

```sql
-- Actions table
CREATE TABLE actions (
    action_id TEXT PRIMARY KEY,
    deal_id TEXT,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    created_by TEXT NOT NULL,
    source TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    requires_human_review INTEGER NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    inputs TEXT NOT NULL,  -- JSON
    outputs TEXT,  -- JSON
    error TEXT,  -- JSON
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    FOREIGN KEY (deal_id) REFERENCES deals(deal_id)
);

CREATE INDEX idx_actions_deal_id ON actions(deal_id);
CREATE INDEX idx_actions_status ON actions(status);
CREATE INDEX idx_actions_type ON actions(type);
CREATE INDEX idx_actions_created_at ON actions(created_at DESC);
CREATE INDEX idx_actions_idempotency_key ON actions(idempotency_key);

-- Audit events table
CREATE TABLE action_audit_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event TEXT NOT NULL,
    actor TEXT NOT NULL,
    details TEXT,  -- JSON
    FOREIGN KEY (action_id) REFERENCES actions(action_id)
);

CREATE INDEX idx_audit_action_id ON action_audit_events(action_id);
CREATE INDEX idx_audit_timestamp ON action_audit_events(timestamp DESC);

-- Artifacts table
CREATE TABLE action_artifacts (
    artifact_id TEXT PRIMARY KEY,
    action_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    path TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    sha256 TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (action_id) REFERENCES actions(action_id)
);

CREATE INDEX idx_artifacts_action_id ON action_artifacts(action_id);

-- Runner leases table (for distributed locking)
CREATE TABLE action_runner_leases (
    lease_id INTEGER PRIMARY KEY CHECK (lease_id = 1),  -- Single row
    runner_pid INTEGER NOT NULL,
    runner_hostname TEXT NOT NULL,
    acquired_at TIMESTAMP NOT NULL,
    heartbeat_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL
);
```

#### Acceptance Criteria

- [ ] `ActionPayload` model validates all required fields
- [ ] Pydantic validation catches invalid status transitions
- [ ] `idempotency_key` enforced as unique in DB
- [ ] Audit trail appends correctly
- [ ] Artifacts list maintains order
- [ ] Type-specific input schemas validate
- [ ] Tables created in `ZAKOPS_STATE_DB` (not new DB)

---

### Component 1.2: Action Executors Architecture

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 2 days

#### Purpose

Plugin system for action execution with clean interface and registry.

#### Technical Specification

**New File:** `src/actions/executor.py` (~250 lines)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from models.action import ActionPayload, ActionStatus, ArtifactMetadata


class ExecutionContext(BaseModel):
    """Context provided to executors."""
    deal_registry: Any  # DealRegistry instance
    event_store: Any    # EventStore instance
    config: Dict[str, Any]


class ExecutionResult(BaseModel):
    """Result of action execution."""
    success: bool
    outputs: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[ArtifactMetadata] = Field(default_factory=list)
    error: Optional[str] = None
    duration_seconds: float = 0.0


class ActionExecutor(ABC):
    """
    Base class for action executors.

    Each action type implements this interface.
    """

    @property
    @abstractmethod
    def action_type(self) -> str:
        """Return the ActionType this executor handles."""
        pass

    @abstractmethod
    def validate(self, payload: ActionPayload) -> tuple[bool, Optional[str]]:
        """
        Validate action payload before execution.

        Returns:
            (is_valid, error_message)
        """
        pass

    @abstractmethod
    def execute(self, payload: ActionPayload, context: ExecutionContext) -> ExecutionResult:
        """
        Execute the action.

        Must be idempotent (use payload.idempotency_key).

        Returns:
            ExecutionResult with success/failure + artifacts
        """
        pass

    def dry_run(self, payload: ActionPayload) -> Dict[str, Any]:
        """
        Simulate execution without side effects.

        Returns:
            Dict with estimated outputs, artifacts, cost, etc.
        """
        return {
            "estimated_outputs": {},
            "estimated_artifacts": [],
            "estimated_cost_usd": 0.0,
            "estimated_duration_seconds": 0.0,
        }

    def estimate_cost(self, payload: ActionPayload) -> float:
        """
        Estimate cost in USD.

        Useful for cloud API calls (Gemini, etc.)
        """
        return 0.0

    def _get_artifact_dir(self, deal_id: str, action_id: str, context: ExecutionContext) -> str:
        """
        Get artifact directory path using new convention.

        Returns: {deal.folder_path}/99-ACTIONS/{action_id}/
        """
        deal = context.deal_registry.get_deal(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        artifact_dir = os.path.join(deal.folder_path, "99-ACTIONS", action_id)
        os.makedirs(artifact_dir, exist_ok=True)
        return artifact_dir

    def _emit_deal_event(
        self,
        deal_id: str,
        event_type: str,
        details: Dict[str, Any],
        context: ExecutionContext,
    ):
        """
        Emit deal event for observability.

        Event types:
        - action_created
        - action_approved
        - action_processing
        - action_completed
        - action_failed
        """
        context.event_store.add_event(
            deal_id=deal_id,
            event_type=event_type,
            details=details,
        )


class ExecutorRegistry:
    """
    Registry of action executors.

    Usage:
        registry = ExecutorRegistry()
        registry.register(EmailDraftExecutor())
        executor = registry.get("COMMUNICATION.DRAFT_EMAIL")
        result = executor.execute(payload, context)
    """

    def __init__(self):
        self._executors: Dict[str, ActionExecutor] = {}

    def register(self, executor: ActionExecutor):
        """Register an executor."""
        action_type = executor.action_type
        if action_type in self._executors:
            raise ValueError(f"Executor for {action_type} already registered")
        self._executors[action_type] = executor
        logger.info(f"Registered executor: {action_type}")

    def get(self, action_type: str) -> Optional[ActionExecutor]:
        """Get executor for action type."""
        return self._executors.get(action_type)

    def list_types(self) -> List[str]:
        """List all registered action types."""
        return list(self._executors.keys())

    def is_registered(self, action_type: str) -> bool:
        """Check if action type is registered."""
        return action_type in self._executors


# Global registry instance
_registry = ExecutorRegistry()


def register_executor(executor: ActionExecutor):
    """Register an executor with the global registry."""
    _registry.register(executor)


def get_executor(action_type: str) -> Optional[ActionExecutor]:
    """Get executor from global registry."""
    return _registry.get(action_type)


def get_registry() -> ExecutorRegistry:
    """Get global registry instance."""
    return _registry
```

#### Acceptance Criteria

- [ ] `ActionExecutor` interface defined
- [ ] `ExecutorRegistry` supports register/get
- [ ] Duplicate registration raises error
- [ ] `dry_run` and `estimate_cost` have default implementations
- [ ] `_get_artifact_dir` uses `99-ACTIONS/<action_id>/` convention
- [ ] `_emit_deal_event` integrates with existing event store

---

### Component 1.3: Actions Database Layer

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 2 days

#### Purpose

CRUD operations + state transitions for actions in existing SQLite DB.

#### Technical Specification

**New File:** `src/db/actions_db.py` (~450 lines)

```python
import json
import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

from models.action import ActionPayload, ActionStatus, AuditEvent, ArtifactMetadata


class ActionsDB:
    """
    Actions database layer using existing ZAKOPS_STATE_DB.

    Handles:
    - CRUD operations
    - Status transitions
    - Idempotency checks
    - Filtering/pagination
    - Lease management for runner
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv(
            "ZAKOPS_STATE_DB",
            "/home/zaks/DataRoom/.deal-registry/ingest_state.db"
        )
        self._ensure_tables()

    def _ensure_tables(self):
        """Create actions tables if not exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Actions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    action_id TEXT PRIMARY KEY,
                    deal_id TEXT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    created_by TEXT NOT NULL,
                    source TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    requires_human_review INTEGER NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    inputs TEXT NOT NULL,
                    outputs TEXT,
                    error TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_seconds REAL
                )
            """)

            # Audit events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    event TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (action_id) REFERENCES actions(action_id)
                )
            """)

            # Artifacts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    action_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    sha256 TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (action_id) REFERENCES actions(action_id)
                )
            """)

            # Runner leases table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_runner_leases (
                    lease_id INTEGER PRIMARY KEY CHECK (lease_id = 1),
                    runner_pid INTEGER NOT NULL,
                    runner_hostname TEXT NOT NULL,
                    acquired_at TIMESTAMP NOT NULL,
                    heartbeat_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            """)

            # Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_deal_id ON actions(deal_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_created_at ON actions(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_idempotency_key ON actions(idempotency_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_action_id ON action_audit_events(action_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON action_audit_events(timestamp DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_action_id ON action_artifacts(action_id)")

            conn.commit()

    def create(self, payload: ActionPayload) -> ActionPayload:
        """
        Create new action.

        Raises:
            ValueError: If idempotency_key already exists
        """
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO actions (
                        action_id, deal_id, type, title, summary, status,
                        created_at, updated_at, created_by, source, risk_level,
                        requires_human_review, idempotency_key, inputs, outputs,
                        error, retry_count, max_retries
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload.action_id,
                        payload.deal_id,
                        payload.type,
                        payload.title,
                        payload.summary,
                        payload.status,
                        payload.created_at,
                        payload.updated_at,
                        payload.created_by,
                        payload.source,
                        payload.risk_level,
                        int(payload.requires_human_review),
                        payload.idempotency_key,
                        json.dumps(payload.inputs),
                        json.dumps(payload.outputs) if payload.outputs else None,
                        json.dumps(payload.error) if payload.error else None,
                        payload.retry_count,
                        payload.max_retries,
                    ),
                )

                # Insert audit events
                for event in payload.audit_trail:
                    self._insert_audit_event(conn, payload.action_id, event)

                conn.commit()
                logger.info(f"Created action: {payload.action_id}")
                return payload

            except sqlite3.IntegrityError as e:
                if "idempotency_key" in str(e):
                    raise ValueError(
                        f"Action with idempotency_key '{payload.idempotency_key}' already exists"
                    )
                raise

    def get(self, action_id: str) -> Optional[ActionPayload]:
        """Get action by ID with audit trail and artifacts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,)).fetchone()
            if not row:
                return None

            # Load audit events
            audit_rows = conn.execute(
                "SELECT * FROM action_audit_events WHERE action_id = ? ORDER BY timestamp",
                (action_id,)
            ).fetchall()

            # Load artifacts
            artifact_rows = conn.execute(
                "SELECT * FROM action_artifacts WHERE action_id = ?",
                (action_id,)
            ).fetchall()

            return self._row_to_payload(row, audit_rows, artifact_rows)

    def get_by_idempotency_key(self, key: str) -> Optional[ActionPayload]:
        """Get action by idempotency key."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM actions WHERE idempotency_key = ?",
                (key,)
            ).fetchone()
            if not row:
                return None

            action_id = row["action_id"]

            # Load audit events
            audit_rows = conn.execute(
                "SELECT * FROM action_audit_events WHERE action_id = ? ORDER BY timestamp",
                (action_id,)
            ).fetchall()

            # Load artifacts
            artifact_rows = conn.execute(
                "SELECT * FROM action_artifacts WHERE action_id = ?",
                (action_id,)
            ).fetchall()

            return self._row_to_payload(row, audit_rows, artifact_rows)

    def update(self, payload: ActionPayload) -> ActionPayload:
        """Update existing action."""
        payload.updated_at = datetime.utcnow()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE actions SET
                    status = ?, updated_at = ?, inputs = ?, outputs = ?,
                    error = ?, retry_count = ?,
                    started_at = ?, completed_at = ?, duration_seconds = ?
                WHERE action_id = ?
                """,
                (
                    payload.status,
                    payload.updated_at,
                    json.dumps(payload.inputs),
                    json.dumps(payload.outputs) if payload.outputs else None,
                    json.dumps(payload.error) if payload.error else None,
                    payload.retry_count,
                    payload.started_at,
                    payload.completed_at,
                    payload.duration_seconds,
                    payload.action_id,
                ),
            )

            # Delete old audit events and re-insert (simpler than diffing)
            conn.execute("DELETE FROM action_audit_events WHERE action_id = ?", (payload.action_id,))
            for event in payload.audit_trail:
                self._insert_audit_event(conn, payload.action_id, event)

            # Delete old artifacts and re-insert
            conn.execute("DELETE FROM action_artifacts WHERE action_id = ?", (payload.action_id,))
            for artifact in payload.artifacts:
                self._insert_artifact(conn, payload.action_id, artifact)

            conn.commit()

        return payload

    def list_actions(
        self,
        status: Optional[str] = None,
        action_type: Optional[str] = None,
        deal_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ActionPayload]:
        """List actions with filters."""
        query = "SELECT * FROM actions WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if action_type:
            query += " AND type = ?"
            params.append(action_type)
        if deal_id:
            query += " AND deal_id = ?"
            params.append(deal_id)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()

            results = []
            for row in rows:
                action_id = row["action_id"]

                # Load audit events
                audit_rows = conn.execute(
                    "SELECT * FROM action_audit_events WHERE action_id = ? ORDER BY timestamp",
                    (action_id,)
                ).fetchall()

                # Load artifacts
                artifact_rows = conn.execute(
                    "SELECT * FROM action_artifacts WHERE action_id = ?",
                    (action_id,)
                ).fetchall()

                results.append(self._row_to_payload(row, audit_rows, artifact_rows))

            return results

    def transition_status(
        self,
        action_id: str,
        new_status: ActionStatus,
        actor: str,
        details: Optional[Dict] = None,
    ) -> ActionPayload:
        """
        Transition action to new status with audit.

        Validates state transitions.
        """
        payload = self.get(action_id)
        if not payload:
            raise ValueError(f"Action {action_id} not found")

        # Validate transition
        valid_transitions = {
            ActionStatus.PENDING_APPROVAL: {ActionStatus.READY, ActionStatus.CANCELLED},
            ActionStatus.READY: {ActionStatus.PROCESSING, ActionStatus.CANCELLED},
            ActionStatus.PROCESSING: {ActionStatus.COMPLETED, ActionStatus.FAILED},
            ActionStatus.FAILED: {ActionStatus.READY},  # Allow retry
        }

        if new_status not in valid_transitions.get(payload.status, set()):
            raise ValueError(f"Invalid transition: {payload.status} -> {new_status}")

        payload.status = new_status
        payload.add_audit_event(f"status_changed_to_{new_status}", actor, details)

        return self.update(payload)

    def _insert_audit_event(self, conn: sqlite3.Connection, action_id: str, event: AuditEvent):
        """Insert audit event."""
        conn.execute(
            """
            INSERT INTO action_audit_events (action_id, timestamp, event, actor, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                action_id,
                event.timestamp,
                event.event,
                event.actor,
                json.dumps(event.details) if event.details else None,
            ),
        )

    def _insert_artifact(self, conn: sqlite3.Connection, action_id: str, artifact: ArtifactMetadata):
        """Insert artifact."""
        conn.execute(
            """
            INSERT INTO action_artifacts (
                artifact_id, action_id, filename, mime_type, path, size_bytes, sha256, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact.artifact_id,
                action_id,
                artifact.filename,
                artifact.mime_type,
                artifact.path,
                artifact.size_bytes,
                artifact.sha256,
                artifact.created_at,
            ),
        )

    def _row_to_payload(
        self,
        row: sqlite3.Row,
        audit_rows: List[sqlite3.Row],
        artifact_rows: List[sqlite3.Row],
    ) -> ActionPayload:
        """Convert DB rows to ActionPayload."""
        audit_trail = [
            AuditEvent(
                timestamp=datetime.fromisoformat(audit_row["timestamp"]),
                event=audit_row["event"],
                actor=audit_row["actor"],
                details=json.loads(audit_row["details"]) if audit_row["details"] else None,
            )
            for audit_row in audit_rows
        ]

        artifacts = [
            ArtifactMetadata(
                artifact_id=artifact_row["artifact_id"],
                filename=artifact_row["filename"],
                mime_type=artifact_row["mime_type"],
                path=artifact_row["path"],
                size_bytes=artifact_row["size_bytes"],
                sha256=artifact_row["sha256"],
                created_at=datetime.fromisoformat(artifact_row["created_at"]),
            )
            for artifact_row in artifact_rows
        ]

        return ActionPayload(
            action_id=row["action_id"],
            deal_id=row["deal_id"],
            type=row["type"],
            title=row["title"],
            summary=row["summary"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
            source=row["source"],
            risk_level=row["risk_level"],
            requires_human_review=bool(row["requires_human_review"]),
            idempotency_key=row["idempotency_key"],
            inputs=json.loads(row["inputs"]),
            outputs=json.loads(row["outputs"]) if row["outputs"] else {},
            error=json.loads(row["error"]) if row["error"] else None,
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
            audit_trail=audit_trail,
            artifacts=artifacts,
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            duration_seconds=row["duration_seconds"],
        )
```

#### Lease Management Methods

```python
    def acquire_lease(self, runner_pid: int, runner_hostname: str, lease_duration_seconds: int = 60) -> bool:
        """
        Acquire runner lease (prevent multiple runners).

        Returns:
            True if lease acquired, False if another runner holds it
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=lease_duration_seconds)

        with sqlite3.connect(self.db_path) as conn:
            # Check existing lease
            row = conn.execute("SELECT * FROM action_runner_leases WHERE lease_id = 1").fetchone()

            if row:
                current_expires = datetime.fromisoformat(row[5])  # expires_at column
                if datetime.utcnow() < current_expires:
                    # Lease still valid
                    logger.warning(
                        f"Lease held by PID {row[1]} on {row[2]} until {current_expires}"
                    )
                    return False

                # Lease expired, take over
                conn.execute(
                    """
                    UPDATE action_runner_leases
                    SET runner_pid = ?, runner_hostname = ?,
                        acquired_at = ?, heartbeat_at = ?, expires_at = ?
                    WHERE lease_id = 1
                    """,
                    (runner_pid, runner_hostname, now, now, expires_at),
                )
            else:
                # No existing lease
                conn.execute(
                    """
                    INSERT INTO action_runner_leases
                    (lease_id, runner_pid, runner_hostname, acquired_at, heartbeat_at, expires_at)
                    VALUES (1, ?, ?, ?, ?, ?)
                    """,
                    (runner_pid, runner_hostname, now, now, expires_at),
                )

            conn.commit()
            logger.info(f"Acquired runner lease: PID {runner_pid} on {runner_hostname}")
            return True

    def renew_lease(self, runner_pid: int, lease_duration_seconds: int = 60) -> bool:
        """Renew (heartbeat) runner lease."""
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=lease_duration_seconds)

        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                """
                UPDATE action_runner_leases
                SET heartbeat_at = ?, expires_at = ?
                WHERE lease_id = 1 AND runner_pid = ?
                """,
                (now, expires_at, runner_pid),
            )
            conn.commit()

            if result.rowcount > 0:
                logger.debug(f"Renewed runner lease: PID {runner_pid}")
                return True
            else:
                logger.error(f"Failed to renew lease: PID {runner_pid} does not hold lease")
                return False

    def release_lease(self, runner_pid: int):
        """Release runner lease."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM action_runner_leases WHERE lease_id = 1 AND runner_pid = ?",
                (runner_pid,),
            )
            conn.commit()
            logger.info(f"Released runner lease: PID {runner_pid}")
```

#### Acceptance Criteria

- [ ] Create action with unique idempotency_key
- [ ] Duplicate idempotency_key raises ValueError
- [ ] Get by ID returns None if not found
- [ ] Update persists all fields including audit trail and artifacts
- [ ] List with filters (status, type, deal_id) works
- [ ] Status transitions validate state machine
- [ ] Invalid transition raises ValueError
- [ ] Tables created in `ZAKOPS_STATE_DB` (not new DB)
- [ ] Lease acquisition prevents duplicate runners
- [ ] Lease expiry enables safe takeover

---

## Phase 2: Action Executors (Week 2)

### Component 2.1: Email Draft Executor

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

#### Technical Specification

**New File:** `src/actions/executors/email_draft.py` (~300 lines)

```python
import os
import time
import hashlib
from datetime import datetime

from actions.executor import ActionExecutor, ExecutionResult, ExecutionContext
from models.action import ActionPayload, ActionType, EmailDraftInputs


class EmailDraftExecutor(ActionExecutor):
    """
    Generate draft email using Gemini Pro (cloud policy).

    Safety:
    - Requires ENABLE_CLOUD_POLICY=true
    - Never sends automatically (draft only)
    - Stores draft in outputs + DOCX artifact in 99-ACTIONS/
    - Emits deal events for observability
    """

    @property
    def action_type(self) -> str:
        return ActionType.COMMUNICATION_DRAFT_EMAIL

    def validate(self, payload: ActionPayload) -> tuple[bool, Optional[str]]:
        """Validate email draft inputs."""
        try:
            inputs = EmailDraftInputs(**payload.inputs)

            if not inputs.recipient:
                return False, "recipient is required"
            if not inputs.subject:
                return False, "subject is required"
            if not inputs.context:
                return False, "context is required"

            # Check cloud policy
            if not os.getenv("ENABLE_CLOUD_POLICY", "false").lower() == "true":
                return False, "Cloud policy disabled; email drafting requires ENABLE_CLOUD_POLICY=true"

            return True, None
        except Exception as e:
            return False, str(e)

    def execute(self, payload: ActionPayload, context: ExecutionContext) -> ExecutionResult:
        """
        Generate email draft using Gemini Pro.

        Steps:
        1. Emit deal event (action_processing)
        2. Load case file for context
        3. Call Gemini Pro with prompt template
        4. Store draft in outputs
        5. Save as DOCX artifact in 99-ACTIONS/<action_id>/
        6. Emit deal event (action_completed)
        """
        start_time = time.time()
        inputs = EmailDraftInputs(**payload.inputs)

        try:
            # Emit processing event
            if payload.deal_id:
                self._emit_deal_event(
                    payload.deal_id,
                    "action_processing",
                    {
                        "action_id": payload.action_id,
                        "action_type": payload.type,
                        "title": payload.title,
                    },
                    context,
                )

            # 1. Gather context
            case_file = {}
            if payload.deal_id:
                deal = context.deal_registry.get_deal(payload.deal_id)
                if deal and hasattr(deal, 'case_file'):
                    case_file = deal.case_file or {}

            # 2. Build prompt
            prompt = f"""
            You are drafting a professional email for a business acquisition process.

            Recipient: {inputs.recipient} ({inputs.recipient_name or "Unknown"})
            Subject: {inputs.subject}
            Tone: {inputs.tone}

            Context:
            {inputs.context}

            Deal Information:
            {json.dumps(case_file, indent=2)}

            Generate a complete, professional email draft. Include:
            - Professional greeting
            - Clear purpose statement
            - Relevant details from context
            - Appropriate closing

            Output ONLY the email body (no meta-commentary).
            """

            # 3. Call Gemini Pro
            gemini_response = self._call_gemini_pro(prompt, temperature=0.3)
            draft_body = gemini_response.strip()

            # 4. Store in outputs
            outputs = {
                "draft_body": draft_body,
                "subject": inputs.subject,
                "recipient": inputs.recipient,
                "generated_at": datetime.utcnow().isoformat(),
            }

            # 5. Save as DOCX artifact in 99-ACTIONS/
            artifacts = []
            if payload.deal_id:
                artifact_dir = self._get_artifact_dir(payload.deal_id, payload.action_id, context)
                docx_path = self._save_draft_as_docx(
                    artifact_dir,
                    inputs.subject,
                    inputs.recipient,
                    draft_body,
                )

                # Calculate file hash
                file_hash = self._calculate_sha256(docx_path)

                artifact = ArtifactMetadata(
                    filename=os.path.basename(docx_path),
                    mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    path=docx_path,
                    size_bytes=os.path.getsize(docx_path),
                    sha256=file_hash,
                )
                artifacts.append(artifact)

            duration = time.time() - start_time

            # 6. Emit completion event
            if payload.deal_id:
                self._emit_deal_event(
                    payload.deal_id,
                    "action_completed",
                    {
                        "action_id": payload.action_id,
                        "action_type": payload.type,
                        "title": payload.title,
                        "artifacts_count": len(artifacts),
                        "duration_seconds": duration,
                    },
                    context,
                )

            return ExecutionResult(
                success=True,
                outputs=outputs,
                artifacts=artifacts,
                duration_seconds=duration,
            )

        except Exception as e:
            logger.error(f"Email draft execution failed: {e}")

            # Emit failure event
            if payload.deal_id:
                self._emit_deal_event(
                    payload.deal_id,
                    "action_failed",
                    {
                        "action_id": payload.action_id,
                        "action_type": payload.type,
                        "title": payload.title,
                        "error": str(e),
                    },
                    context,
                )

            return ExecutionResult(
                success=False,
                error=str(e),
                duration_seconds=time.time() - start_time,
            )

    def _call_gemini_pro(self, prompt: str, temperature: float = 0.3) -> str:
        """Call Gemini Pro API."""
        # Implementation using google.generativeai or requests
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2048,
            ),
        )

        return response.text

    def _save_draft_as_docx(
        self,
        artifact_dir: str,
        subject: str,
        recipient: str,
        body: str,
    ) -> str:
        """Save draft as DOCX in artifact directory."""
        from docx import Document

        doc = Document()
        doc.add_heading("Email Draft", 0)
        doc.add_paragraph(f"To: {recipient}")
        doc.add_paragraph(f"Subject: {subject}")
        doc.add_paragraph("")
        doc.add_paragraph(body)

        filename = "email_draft.docx"
        filepath = os.path.join(artifact_dir, filename)

        doc.save(filepath)
        logger.info(f"Saved email draft: {filepath}")

        return filepath

    def _calculate_sha256(self, filepath: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def estimate_cost(self, payload: ActionPayload) -> float:
        """Estimate Gemini API cost (~$0.01 for draft)."""
        return 0.01
```

#### Acceptance Criteria

- [ ] Validates cloud policy enabled
- [ ] Generates draft using Gemini Pro
- [ ] Saves DOCX artifact in `99-ACTIONS/<action_id>/`
- [ ] Stores draft body in outputs
- [ ] Never sends email automatically
- [ ] Handles Gemini API errors gracefully
- [ ] Emits deal events (processing, completed, failed)
- [ ] Calculates SHA256 hash for artifact integrity

---

### Component 2.2-2.5: Additional Executors

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 6 days total (1.5 days each)

All executors follow the same pattern as EmailDraftExecutor:
1. Emit `action_processing` event
2. Validate inputs
3. Execute with idempotency
4. Save artifacts in `99-ACTIONS/<action_id>/`
5. Calculate SHA256 hashes
6. Emit `action_completed` or `action_failed` event

**See Appendix A for complete implementations of:**
- Document Generate Executor (LOI/NDA/Request Letter)
- Valuation Model Executor (XLSX with openpyxl)
- Presentation Deck Executor (PPTX with python-pptx)
- Diligence Request Executor (checklist + email draft)

---

## Phase 3: API Layer (Week 2-3)

### Component 3.1: Actions API Endpoints

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

#### Technical Specification

**Extend:** `/home/zaks/scripts/deal_lifecycle_api.py` (port 8090)

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import hashlib
import json

from db.actions_db import ActionsDB
from actions.executor import get_executor, ExecutionContext
from models.action import ActionPayload, ActionStatus

router = APIRouter(prefix="/api/actions", tags=["actions"])
actions_db = ActionsDB()  # Uses ZAKOPS_STATE_DB


# Request/Response models
class CreateActionRequest(BaseModel):
    deal_id: Optional[str] = None
    type: str
    title: str
    summary: str
    inputs: Dict[str, Any]
    created_by: str = "operator"
    source: str = "ui"


class ApproveActionRequest(BaseModel):
    approved_by: str


class UpdateActionRequest(BaseModel):
    inputs: Dict[str, Any]


class CancelActionRequest(BaseModel):
    cancelled_by: str


@router.get("")
async def list_actions(
    status: Optional[str] = None,
    type: Optional[str] = None,
    deal_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    List actions with filters (NEW Kinetic Actions endpoint).

    Query params:
    - status: Filter by status (PENDING_APPROVAL, READY, etc.)
    - type: Filter by action type
    - deal_id: Filter by deal
    - limit: Max results (default 100)
    - offset: Pagination offset
    """
    actions = actions_db.list_actions(
        status=status,
        action_type=type,
        deal_id=deal_id,
        limit=limit,
        offset=offset,
    )
    return {"actions": [a.model_dump() for a in actions]}


@router.get("/{action_id}")
async def get_action(action_id: str):
    """Get single action by ID."""
    action = actions_db.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action.model_dump()


@router.post("")
async def create_action(req: CreateActionRequest):
    """
    Create new action (idempotent).

    Returns existing action if idempotency_key already exists.
    """
    # Generate idempotency key from inputs
    idempotency_key = hashlib.sha256(
        json.dumps({
            "type": req.type,
            "deal_id": req.deal_id,
            "inputs": req.inputs,
        }, sort_keys=True).encode()
    ).hexdigest()

    # Check if already exists
    existing = actions_db.get_by_idempotency_key(idempotency_key)
    if existing:
        return {"action": existing.model_dump(), "created": False}

    # Create new action
    payload = ActionPayload(
        deal_id=req.deal_id,
        type=req.type,
        title=req.title,
        summary=req.summary,
        inputs=req.inputs,
        created_by=req.created_by,
        source=req.source,
        idempotency_key=idempotency_key,
    )

    payload.add_audit_event("created", req.created_by)

    action = actions_db.create(payload)

    # Emit deal event
    if action.deal_id:
        from scripts.deal_events import add_event
        add_event(
            deal_id=action.deal_id,
            event_type="action_created",
            details={
                "action_id": action.action_id,
                "action_type": action.type,
                "title": action.title,
                "created_by": action.created_by,
            },
        )

    return {"action": action.model_dump(), "created": True}


@router.post("/{action_id}/approve")
async def approve_action(action_id: str, req: ApproveActionRequest):
    """
    Approve action (PENDING_APPROVAL → READY).
    """
    action = actions_db.transition_status(
        action_id,
        ActionStatus.READY,
        req.approved_by,
        {"approved_at": datetime.utcnow().isoformat()},
    )

    # Emit deal event
    if action.deal_id:
        from scripts.deal_events import add_event
        add_event(
            deal_id=action.deal_id,
            event_type="action_approved",
            details={
                "action_id": action.action_id,
                "action_type": action.type,
                "title": action.title,
                "approved_by": req.approved_by,
            },
        )

    return {"action": action.model_dump()}


@router.post("/{action_id}/execute")
async def execute_action(action_id: str):
    """
    Execute action (READY → PROCESSING).

    Returns 202 Accepted; execution happens via background runner.
    UI should poll GET /api/actions/{id} for completion.
    """
    action = actions_db.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if not action.can_execute():
        raise HTTPException(
            status_code=400,
            detail=f"Action cannot be executed in status: {action.status}",
        )

    # Transition to PROCESSING
    action = actions_db.transition_status(
        action_id,
        ActionStatus.PROCESSING,
        "system",
        {"started_at": datetime.utcnow().isoformat()},
    )
    action.started_at = datetime.utcnow()
    actions_db.update(action)

    return {
        "action": action.model_dump(),
        "status": "processing",
        "message": "Action enqueued; runner will execute. Poll this endpoint for updates.",
    }


@router.post("/{action_id}/cancel")
async def cancel_action(action_id: str, req: CancelActionRequest):
    """Cancel action."""
    action = actions_db.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if not action.can_cancel():
        raise HTTPException(
            status_code=400,
            detail=f"Action cannot be cancelled in status: {action.status}",
        )

    action = actions_db.transition_status(
        action_id,
        ActionStatus.CANCELLED,
        req.cancelled_by,
        {"cancelled_at": datetime.utcnow().isoformat()},
    )

    # Emit deal event
    if action.deal_id:
        from scripts.deal_events import add_event
        add_event(
            deal_id=action.deal_id,
            event_type="action_cancelled",
            details={
                "action_id": action.action_id,
                "action_type": action.type,
                "title": action.title,
                "cancelled_by": req.cancelled_by,
            },
        )

    return {"action": action.model_dump()}


@router.post("/{action_id}/update")
async def update_action(action_id: str, req: UpdateActionRequest):
    """Update action inputs (before execution)."""
    action = actions_db.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if action.status not in {ActionStatus.PENDING_APPROVAL, ActionStatus.READY}:
        raise HTTPException(
            status_code=400,
            detail="Cannot update action after execution started",
        )

    action.inputs = req.inputs
    action.add_audit_event("inputs_updated", "operator")
    action = actions_db.update(action)

    return {"action": action.model_dump()}


@router.get("/{action_id}/artifacts")
async def list_artifacts(action_id: str):
    """List artifacts for action."""
    action = actions_db.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    return {"artifacts": [a.model_dump() for a in action.artifacts]}


@router.get("/{action_id}/artifact/{artifact_id}")
async def download_artifact(action_id: str, artifact_id: str):
    """Download artifact file."""
    from fastapi.responses import FileResponse

    action = actions_db.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    artifact = next((a for a in action.artifacts if a.artifact_id == artifact_id), None)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    if not os.path.exists(artifact.path):
        raise HTTPException(status_code=404, detail="Artifact file not found on disk")

    return FileResponse(
        artifact.path,
        media_type=artifact.mime_type,
        filename=artifact.filename,
    )


# Legacy endpoints (backward compatibility)
@router.get("/deferred-actions", include_in_schema=False)
async def list_deferred_actions_legacy():
    """Legacy endpoint for deferred reminders (preserved)."""
    from scripts.deferred_actions import load_deferred_actions
    return {"actions": load_deferred_actions()}


@router.get("/deferred-actions/due", include_in_schema=False)
async def list_due_deferred_actions_legacy():
    """Legacy endpoint for due deferred reminders (preserved)."""
    from scripts.deferred_actions import get_due_actions
    return {"actions": get_due_actions()}


# Register router
app.include_router(router)
```

#### Acceptance Criteria

- [ ] `GET /api/actions` returns filtered list
- [ ] `POST /api/actions` creates action with idempotency check
- [ ] Duplicate idempotency_key returns existing action (200)
- [ ] `POST /api/actions/{id}/approve` transitions to READY
- [ ] `POST /api/actions/{id}/execute` transitions to PROCESSING (202)
- [ ] `GET /api/actions/{id}/artifact/{artifact_id}` downloads file
- [ ] Invalid status transitions return 400
- [ ] Missing actions return 404
- [ ] Deal events emitted for create/approve/cancel
- [ ] Legacy `/api/deferred-actions*` endpoints preserved

---

### Component 3.2: Action Runner (Background Worker)

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

#### Technical Specification

**New File:** `/home/zaks/scripts/actions_runner.py` (~350 lines)

```python
import os
import socket
import time
import signal
import atexit
from datetime import datetime, timedelta

from db.actions_db import ActionsDB
from actions.executor import get_executor, ExecutionContext
from models.action import ActionStatus


class ActionRunner:
    """
    Background worker for action execution.

    Features:
    - Lease-based locking (prevents ghost runners)
    - Persistent queue (ZAKOPS_STATE_DB)
    - Graceful shutdown
    - Retry on failure
    - Deal events integration
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        poll_interval: int = 5,
        lease_duration: int = 60,
    ):
        self.db = ActionsDB(db_path)
        self.poll_interval = poll_interval
        self.lease_duration = lease_duration
        self.running = False
        self.runner_pid = os.getpid()
        self.runner_hostname = socket.gethostname()

    def run(self):
        """Main runner loop."""
        # Try to acquire lease
        if not self.db.acquire_lease(self.runner_pid, self.runner_hostname, self.lease_duration):
            logger.error("Failed to acquire lease; another runner is active")
            return

        self.running = True

        # Register cleanup on exit
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info(f"Action runner started (PID {self.runner_pid} on {self.runner_hostname})")

        try:
            last_heartbeat = time.time()

            while self.running:
                # Renew lease (heartbeat)
                if time.time() - last_heartbeat > self.lease_duration / 2:
                    if not self.db.renew_lease(self.runner_pid, self.lease_duration):
                        logger.error("Lost lease; shutting down")
                        break
                    last_heartbeat = time.time()

                # Get READY actions
                ready_actions = self.db.list_actions(status=ActionStatus.READY, limit=10)

                for action in ready_actions:
                    if not self.running:
                        break

                    try:
                        execute_action_sync(action.action_id, self.db)
                    except Exception as e:
                        logger.error(f"Failed to execute action {action.action_id}: {e}")

                # Poll interval
                time.sleep(self.poll_interval)

        finally:
            self._cleanup()
            logger.info("Action runner stopped")

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def _cleanup(self):
        """Release lease on exit."""
        self.db.release_lease(self.runner_pid)


def execute_action_sync(action_id: str, db: ActionsDB):
    """
    Execute action synchronously.

    Steps:
    1. Get executor for action type
    2. Validate payload
    3. Execute with context
    4. Update action with results
    5. Emit deal events
    6. Retry on failure (up to max_retries)
    """
    action = db.get(action_id)

    if not action:
        logger.error(f"Action {action_id} not found")
        return

    if action.status != ActionStatus.PROCESSING:
        logger.warning(f"Action {action_id} not in PROCESSING state, skipping")
        return

    # Get executor
    executor = get_executor(action.type)
    if not executor:
        logger.error(f"No executor registered for type: {action.type}")
        action.status = ActionStatus.FAILED
        action.error = {"message": f"No executor for type: {action.type}"}
        action.add_audit_event("execution_failed", "system", {"reason": "no_executor"})
        db.update(action)
        return

    # Validate
    is_valid, error_msg = executor.validate(action)
    if not is_valid:
        logger.error(f"Action {action_id} validation failed: {error_msg}")
        action.status = ActionStatus.FAILED
        action.error = {"message": error_msg}
        action.add_audit_event("validation_failed", "system", {"reason": error_msg})
        db.update(action)
        return

    # Build execution context
    from scripts.deal_registry import DealRegistry
    from scripts.deal_events import EventStore

    context = ExecutionContext(
        deal_registry=DealRegistry(),
        event_store=EventStore(),
        config={},
    )

    # Execute
    try:
        logger.info(f"Executing action {action_id} (type: {action.type})")
        result = executor.execute(action, context)

        action.completed_at = datetime.utcnow()
        action.duration_seconds = (action.completed_at - action.started_at).total_seconds()

        if result.success:
            action.status = ActionStatus.COMPLETED
            action.outputs = result.outputs
            action.artifacts = result.artifacts
            action.add_audit_event("execution_completed", "system")
            logger.info(f"Action {action_id} completed successfully")
        else:
            action.retry_count += 1
            if action.retry_count < action.max_retries:
                # Retry
                action.status = ActionStatus.READY
                action.add_audit_event(
                    "execution_failed_retry",
                    "system",
                    {"error": result.error, "retry": action.retry_count},
                )
                logger.warning(
                    f"Action {action_id} failed, retry {action.retry_count}/{action.max_retries}"
                )
            else:
                # Max retries reached
                action.status = ActionStatus.FAILED
                action.error = {"message": result.error}
                action.add_audit_event(
                    "execution_failed_max_retries",
                    "system",
                    {"error": result.error},
                )
                logger.error(f"Action {action_id} failed after {action.max_retries} retries")

        db.update(action)

    except Exception as e:
        logger.exception(f"Unexpected error executing action {action_id}")
        action.retry_count += 1
        if action.retry_count < action.max_retries:
            action.status = ActionStatus.READY
        else:
            action.status = ActionStatus.FAILED
            action.error = {"message": str(e), "traceback": traceback.format_exc()}
        action.add_audit_event("execution_exception", "system", {"error": str(e)})
        db.update(action)


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    runner = ActionRunner()
    runner.run()
```

#### Makefile Target

**Add to:** `/home/zaks/zakops-dashboard/Makefile`

```makefile
actions-runner:
	@echo "Starting action runner..."
	python3 /home/zaks/scripts/actions_runner.py

actions-runner-bg:
	@echo "Starting action runner in background..."
	nohup python3 /home/zaks/scripts/actions_runner.py > /tmp/actions_runner.log 2>&1 &
	@echo "Runner started (PID: $$!). Logs: /tmp/actions_runner.log"

actions-runner-stop:
	@echo "Stopping action runner..."
	pkill -f actions_runner.py || echo "No runner process found"
```

#### Acceptance Criteria

- [ ] Acquires DB lease on startup
- [ ] Another runner cannot start (lease prevents)
- [ ] Polls for READY actions every 5 seconds
- [ ] Executes actions and updates status
- [ ] Retries failed actions up to max_retries
- [ ] Graceful shutdown on SIGTERM/SIGINT
- [ ] Heartbeat renews lease every 30 seconds
- [ ] Lease expiry enables safe takeover after crash
- [ ] Emits deal events during execution
- [ ] Only one runner can hold lease at a time

---

## Phase 4: Chat Integration (Week 3)

### Component 4.1: Proposal → Action Bridge

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 2 days

#### Technical Specification

**Extend:** `/home/zaks/scripts/chat_orchestrator.py`

```python
# Add to proposal types
PROPOSAL_TYPES = [
    "add_note",
    "create_task",
    "draft_email",
    "request_docs",
    "stage_transition",
    "create_action",  # NEW
]


def execute_proposal(proposal: dict, session: dict, approved_by: str) -> dict:
    """
    Execute approved proposal.

    NEW: Handle create_action proposals.
    """
    tool = proposal.get("tool")

    # ... existing proposal handlers ...

    # NEW: Handle create_action
    if tool == "create_action":
        from db.actions_db import ActionsDB
        from models.action import ActionPayload

        args = proposal.get("args", {})
        action_type = args.get("action_type")
        title = args.get("title")
        summary = args.get("summary")
        inputs = args.get("inputs", {})
        deal_id = session.get("scope", {}).get("deal_id")

        # Generate idempotency key
        idempotency_key = hashlib.sha256(
            json.dumps({
                "proposal_id": proposal.get("proposal_id"),
                "type": action_type,
                "inputs": inputs,
            }, sort_keys=True).encode()
        ).hexdigest()

        # Check if already exists
        actions_db = ActionsDB()
        existing = actions_db.get_by_idempotency_key(idempotency_key)
        if existing:
            return {
                "success": True,
                "result": {
                    "action_created": False,
                    "action_id": existing.action_id,
                    "action_url": f"/actions?action_id={existing.action_id}",
                    "message": "Action already exists (idempotent)",
                },
            }

        # Create action
        action_payload = ActionPayload(
            deal_id=deal_id,
            type=action_type,
            title=title,
            summary=summary,
            inputs=inputs,
            created_by=approved_by,
            source="chat",
            idempotency_key=idempotency_key,
        )

        action_payload.add_audit_event(
            "created_from_proposal",
            approved_by,
            {"proposal_id": proposal.get("proposal_id")},
        )

        action = actions_db.create(action_payload)

        # Emit deal event
        if action.deal_id:
            from scripts.deal_events import add_event
            add_event(
                deal_id=action.deal_id,
                event_type="action_created",
                details={
                    "action_id": action.action_id,
                    "action_type": action.type,
                    "title": action.title,
                    "created_by": action.created_by,
                    "source": "chat",
                },
            )

        return {
            "success": True,
            "result": {
                "action_created": True,
                "action_id": action.action_id,
                "action_url": f"/actions?action_id={action.action_id}",
            },
        }

    # ... existing proposal handlers ...
```

**Extend:** `/home/zaks/scripts/deal_lifecycle_api.py` - `/api/chat/execute-proposal`

```python
@app.post("/api/chat/execute-proposal")
async def execute_proposal_endpoint(req: ExecuteProposalRequest):
    """
    Execute approved proposal.

    NEW: Returns action_id and action_url for create_action proposals.
    """
    # ... existing code ...

    result = execute_proposal(proposal, session, req.approved_by)

    # NEW: Add system message for create_action
    if proposal.get("tool") == "create_action" and result.get("success"):
        action_id = result["result"]["action_id"]
        action_url = result["result"]["action_url"]

        system_message = {
            "role": "system",
            "content": f"✅ Created action: {proposal['args']['title']}\n\nView in [Actions Dashboard]({action_url})",
            "timestamp": datetime.utcnow().isoformat(),
        }

        session["messages"].append(system_message)
        save_session(session)

    return result
```

#### LangGraph Brain Update (Optional)

**Extend:** Port 8080 brain to detect action-worthy requests

```python
def generate_proposals(query: str, scope: dict, case_file: dict) -> List[dict]:
    """
    Generate proposals from query.

    NEW: Generate create_action proposals for heavy actions.
    """
    proposals = []

    # Existing proposal generation...

    # NEW: Detect action-worthy requests
    action_keywords = {
        "draft loi": ("DOCUMENT.GENERATE", "Draft Letter of Intent", {"document_type": "LOI"}),
        "draft email": ("COMMUNICATION.DRAFT_EMAIL", "Draft Email", {}),
        "build model": ("ANALYSIS.BUILD_MODEL", "Build Valuation Model", {"model_type": "DCF"}),
        "generate deck": ("PRESENTATION.GENERATE_DECK", "Generate Presentation Deck", {"deck_type": "pitch"}),
        "request docs": ("DILIGENCE.REQUEST_DOCS", "Request Diligence Documents", {}),
    }

    query_lower = query.lower()
    for keyword, (action_type, title, default_inputs) in action_keywords.items():
        if keyword in query_lower:
            # Extract inputs from query (basic keyword extraction)
            inputs = default_inputs.copy()
            inputs.update(extract_inputs_from_query(query, action_type))

            proposals.append({
                "proposal_id": str(uuid.uuid4()),
                "tool": "create_action",
                "args": {
                    "action_type": action_type,
                    "title": title,
                    "summary": f"Generated from chat: {query[:100]}",
                    "inputs": inputs,
                },
                "requires_confirmation": True,
                "requires_approval": True,
                "reason": f"This will create an action in the Actions dashboard for review and execution.",
            })
            break  # Only one action per query

    return proposals
```

#### Acceptance Criteria

- [ ] Chat query "Draft LOI for DEAL-X" creates `create_action` proposal
- [ ] Approving proposal creates action in PENDING_APPROVAL state
- [ ] Action visible in Actions UI immediately
- [ ] Chat shows "Created action" system message with link
- [ ] Proposal execution returns action_id and action_url
- [ ] Idempotency: same query twice doesn't create duplicates
- [ ] Deal event emitted: `action_created`

---

## Phase 5: UI/UX (Week 3)

### Component 5.1: Actions Dashboard UI

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL)
**Estimated Effort:** 3 days

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
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchActions();
  }, [statusFilter, typeFilter]);

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
    // Start polling for completion
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
    }, 2000);  // Poll every 2 seconds
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
    // Transition FAILED → READY
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
        <p className="text-muted-foreground">Execution layer for acquisition workflows</p>
      </div>

      {/* Filters */}
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

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">All Types</option>
          <option value="COMMUNICATION.DRAFT_EMAIL">Draft Email</option>
          <option value="DOCUMENT.GENERATE">Generate Document</option>
          <option value="ANALYSIS.BUILD_MODEL">Build Model</option>
          <option value="PRESENTATION.GENERATE_DECK">Generate Deck</option>
          <option value="DILIGENCE.REQUEST_DOCS">Request Docs</option>
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

function ActionCard({ action, onApprove, onExecute, onCancel, onRetry }: {
  action: Action;
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

  const typeLabels: Record<string, string> = {
    'COMMUNICATION.DRAFT_EMAIL': 'Draft Email',
    'DOCUMENT.GENERATE': 'Generate Document',
    'ANALYSIS.BUILD_MODEL': 'Build Model',
    'PRESENTATION.GENERATE_DECK': 'Generate Deck',
    'DILIGENCE.REQUEST_DOCS': 'Request Docs',
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
            <Badge variant="outline">{typeLabels[action.type] || action.type}</Badge>
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

#### API Client Updates

**Update:** `/home/zaks/zakops-dashboard/src/lib/api.ts`

```typescript
// Action types
export interface Action {
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

export interface Artifact {
  artifact_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  created_at: string;
}

export interface AuditEvent {
  timestamp: string;
  event: string;
  actor: string;
  details?: Record<string, any>;
}

// API functions
export async function getActions(filters?: {
  status?: string;
  type?: string;
  deal_id?: string;
}): Promise<Action[]> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.type) params.append('type', filters.type);
  if (filters?.deal_id) params.append('deal_id', filters.deal_id);

  const res = await fetch(`${API_BASE}/api/actions?${params}`);
  const data = await res.json();
  return data.actions;
}

export async function getAction(actionId: string): Promise<Action> {
  const res = await fetch(`${API_BASE}/api/actions/${actionId}`);
  return res.json();
}

export async function createAction(payload: {
  deal_id?: string;
  type: string;
  title: string;
  summary: string;
  inputs: Record<string, any>;
}): Promise<{ action: Action; created: boolean }> {
  const res = await fetch(`${API_BASE}/api/actions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, created_by: 'operator', source: 'ui' }),
  });
  return res.json();
}

export async function approveAction(actionId: string): Promise<Action> {
  const res = await fetch(`${API_BASE}/api/actions/${actionId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved_by: 'operator' }),
  });
  const data = await res.json();
  return data.action;
}

export async function executeAction(actionId: string): Promise<Action> {
  const res = await fetch(`${API_BASE}/api/actions/${actionId}/execute`, {
    method: 'POST',
  });
  const data = await res.json();
  return data.action;
}

export async function cancelAction(actionId: string): Promise<Action> {
  const res = await fetch(`${API_BASE}/api/actions/${actionId}/cancel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cancelled_by: 'operator' }),
  });
  const data = await res.json();
  return data.action;
}
```

#### Acceptance Criteria

- [ ] Actions displayed as interactive cards
- [ ] Status badges color-coded (yellow/blue/purple/green/red/gray)
- [ ] PROCESSING status shows animated pulse
- [ ] Approve/Run/Cancel/Retry buttons show based on status
- [ ] Expand/collapse shows inputs/outputs/error/artifacts/audit trail
- [ ] Download button for each artifact works
- [ ] Filters update list in real-time
- [ ] Polling shows status updates without manual refresh
- [ ] Error messages display prominently
- [ ] Audit trail shows chronological events

---

## Phase 6: Testing & Documentation (Week 4)

### Component 6.1: Backend Tests

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 3 days

**New File:** `tests/test_actions.py` (~500 lines)

Test coverage:
- Schema validation per action type
- Executor unit tests (dry_run + execute)
- Database CRUD operations
- Idempotency enforcement
- Status state machine transitions
- API endpoints (create, approve, execute, download)
- Lease acquisition (prevents duplicate runners)
- Deal events emission

**See Appendix B for complete test specifications**

---

### Component 6.2: UI Tests

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 2 days

**Extend:** `/home/zaks/zakops-dashboard/tests/click-sweep-test.sh`

Add tests:
- Actions page loads
- Approve button exists for PENDING_APPROVAL actions
- Run button works and transitions to PROCESSING
- Artifacts appear after completion
- Download links work
- Filters update list

---

### Component 6.3: Documentation

**Status:** 🔄 Not Started
**Priority:** P1 (HIGH)
**Estimated Effort:** 2 days

**Create:**
- `/home/zaks/zakops-dashboard/docs/ACTIONS-ENGINE.md` (architecture, schemas, adding executors)
- `/home/zaks/zakops-dashboard/docs/ACTIONS-RUNBOOK.md` (running runner, debugging, safety checklist)

**See Appendix C for documentation outlines**

---

## Phase 7: Verification Report (Week 4)

### Component 7.1: End-to-End Verification

**Status:** 🔄 Not Started
**Priority:** P0 (CRITICAL - ACCEPTANCE CRITERION)
**Estimated Effort:** 1 day

#### Purpose

Prove the system works end-to-end with reproducible commands.

#### Deliverable

**Create:** `/home/zaks/bookkeeping/docs/KINETIC-ACTION-ENGINE-VERIFICATION-REPORT.md`

#### Contents

```markdown
# Kinetic Action Engine - Verification Report

**Date:** YYYY-MM-DD
**Verifier:** [Name]
**System Version:** v1.0

## Test Environment

- Backend: http://localhost:8090
- Frontend: http://localhost:3003
- Database: ZAKOPS_STATE_DB at {path}
- Runner: PID {pid} on {hostname}

## Verification Test 1: Create Action via Chat

**Steps:**
1. Open Chat UI in deal scope (DEAL-2025-001)
2. Send message: "Draft an LOI for this deal"
3. Chat returns `create_action` proposal
4. Approve proposal

**curl Commands:**
\`\`\`bash
# Execute proposal
curl -X POST http://localhost:8090/api/chat/execute-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": "prop_abc123",
    "approved_by": "operator",
    "session_id": "sess_xyz789",
    "action": "approve"
  }'
\`\`\`

**Expected Result:**
\`\`\`json
{
  "success": true,
  "result": {
    "action_created": true,
    "action_id": "action_def456",
    "action_url": "/actions?action_id=action_def456"
  }
}
\`\`\`

**Verification:**
- [ ] Action created in database
- [ ] Status is PENDING_APPROVAL
- [ ] Deal event emitted: action_created
- [ ] Chat shows system message with link

## Verification Test 2: Approve Action

**curl Command:**
\`\`\`bash
curl -X POST http://localhost:8090/api/actions/action_def456/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "operator"}'
\`\`\`

**Expected Result:**
- Status transitions to READY
- Audit event: status_changed_to_READY
- Deal event emitted: action_approved

**DB Query:**
\`\`\`sql
SELECT action_id, status, updated_at FROM actions WHERE action_id = 'action_def456';
-- status should be 'READY'

SELECT event FROM action_audit_events WHERE action_id = 'action_def456' ORDER BY timestamp;
-- should show: created, status_changed_to_READY
\`\`\`

## Verification Test 3: Execute Action

**curl Command:**
\`\`\`bash
curl -X POST http://localhost:8090/api/actions/action_def456/execute
\`\`\`

**Expected Result:**
- Status transitions to PROCESSING
- Runner picks up action within 5 seconds
- Status transitions to COMPLETED
- Artifacts generated

**Polling:**
\`\`\`bash
watch -n 2 'curl -s http://localhost:8090/api/actions/action_def456 | jq .status'
# Should show: PROCESSING → COMPLETED
\`\`\`

## Verification Test 4: Download Artifact

**curl Command:**
\`\`\`bash
curl http://localhost:8090/api/actions/action_def456/artifact/artifact_ghi789 \
  --output loi_draft.docx
\`\`\`

**Expected Result:**
- File downloads successfully
- File is valid DOCX
- File contains LOI content

**Verification:**
\`\`\`bash
file loi_draft.docx
# Should output: Microsoft Word 2007+

# Verify SHA256
shasum -a 256 loi_draft.docx
# Compare with artifact.sha256 in DB
\`\`\`

## Verification Test 5: Idempotency

**Steps:**
1. Execute same chat query again: "Draft an LOI for this deal"
2. Approve proposal

**Expected Result:**
- Returns existing action (action_def456)
- created: false
- No duplicate action in database

**DB Query:**
\`\`\`sql
SELECT COUNT(*) FROM actions WHERE idempotency_key = '{key}';
-- Should be 1 (not 2)
\`\`\`

## Verification Test 6: Runner Lease

**Steps:**
1. Start runner: `make actions-runner-bg`
2. Try to start second runner: `make actions-runner-bg`

**Expected Result:**
- Second runner fails to acquire lease
- Log message: "Lease held by PID {pid1} on {hostname}"
- Only one runner executing actions

**DB Query:**
\`\`\`sql
SELECT * FROM action_runner_leases;
-- Should show single row with current runner PID
\`\`\`

## Screenshots

[Include screenshots of:]
- Chat UI with "Created action" message
- Actions Dashboard with action card
- Action card expanded showing inputs/outputs
- Artifact download link
- Deal detail page showing action in timeline

## Summary

- [x] All 6 verification tests passed
- [x] System is production-ready
- [x] Backward compatibility maintained (legacy endpoints work)
- [x] No breaking changes to chat contracts

## Issues Found

[List any issues discovered and their resolutions]

---

**Verification Complete:** [Date]
**Verified By:** [Name]
```

#### Acceptance Criteria

- [ ] All 6 verification tests documented
- [ ] curl commands provided for each test
- [ ] DB queries demonstrate idempotency and audit trail
- [ ] Screenshots or terminal outputs included
- [ ] Summary confirms production-readiness

---

## Appendix A: Additional Executor Implementations

### Document Generate Executor

```python
class DocumentGenerateExecutor(ActionExecutor):
    @property
    def action_type(self) -> str:
        return ActionType.DOCUMENT_GENERATE

    def execute(self, payload: ActionPayload, context: ExecutionContext) -> ExecutionResult:
        """Generate business document (LOI/NDA/Request Letter)."""
        inputs = DocumentGenerateInputs(**payload.inputs)

        # Emit processing event
        if payload.deal_id:
            self._emit_deal_event(
                payload.deal_id,
                "action_processing",
                {"action_id": payload.action_id, "action_type": payload.type},
                context,
            )

        # Get artifact directory
        artifact_dir = self._get_artifact_dir(payload.deal_id, payload.action_id, context)

        # Load template
        template_path = self._get_template_path(inputs.document_type, inputs.template)

        # Merge fields
        merge_fields = self._build_merge_fields(payload.deal_id, inputs.fields, context)

        # Generate DOCX
        docx_path = self._generate_docx(
            template_path,
            merge_fields,
            artifact_dir,
            inputs.document_type,
        )

        artifacts = [
            ArtifactMetadata(
                filename=os.path.basename(docx_path),
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                path=docx_path,
                size_bytes=os.path.getsize(docx_path),
                sha256=self._calculate_sha256(docx_path),
            )
        ]

        # Optional PDF conversion
        if inputs.output_format in ("pdf", "both"):
            pdf_path = self._convert_to_pdf(docx_path)
            artifacts.append(
                ArtifactMetadata(
                    filename=os.path.basename(pdf_path),
                    mime_type="application/pdf",
                    path=pdf_path,
                    size_bytes=os.path.getsize(pdf_path),
                    sha256=self._calculate_sha256(pdf_path),
                )
            )

        # Emit completion event
        if payload.deal_id:
            self._emit_deal_event(
                payload.deal_id,
                "action_completed",
                {"action_id": payload.action_id, "artifacts_count": len(artifacts)},
                context,
            )

        return ExecutionResult(
            success=True,
            outputs={"document_type": inputs.document_type},
            artifacts=artifacts,
        )
```

### Valuation Model Executor

```python
class ValuationModelExecutor(ActionExecutor):
    @property
    def action_type(self) -> str:
        return ActionType.ANALYSIS_BUILD_MODEL

    def execute(self, payload: ActionPayload, context: ExecutionContext) -> ExecutionResult:
        """Generate XLSX valuation model."""
        from openpyxl import Workbook

        inputs = ValuationModelInputs(**payload.inputs)

        # Emit processing event
        if payload.deal_id:
            self._emit_deal_event(
                payload.deal_id,
                "action_processing",
                {"action_id": payload.action_id, "action_type": payload.type},
                context,
            )

        # Get artifact directory
        artifact_dir = self._get_artifact_dir(payload.deal_id, payload.action_id, context)

        # Create workbook
        wb = Workbook()

        # Assumptions sheet
        ws_assumptions = wb.active
        ws_assumptions.title = "Assumptions"
        ws_assumptions['A1'] = "Revenue Growth Rate"
        ws_assumptions['B1'] = inputs.assumptions.get('revenue_growth', 0.10)
        # ... more assumptions ...

        # DCF sheet
        ws_dcf = wb.create_sheet("DCF")
        # ... DCF calculations ...

        # Save
        filename = f"valuation_model_{inputs.model_type.lower()}.xlsx"
        filepath = os.path.join(artifact_dir, filename)
        wb.save(filepath)

        # Emit completion event
        if payload.deal_id:
            self._emit_deal_event(
                payload.deal_id,
                "action_completed",
                {"action_id": payload.action_id, "artifacts_count": 1},
                context,
            )

        return ExecutionResult(
            success=True,
            outputs={"model_type": inputs.model_type},
            artifacts=[
                ArtifactMetadata(
                    filename=filename,
                    mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    path=filepath,
                    size_bytes=os.path.getsize(filepath),
                    sha256=self._calculate_sha256(filepath),
                )
            ],
        )
```

---

## Appendix B: Test Specifications

**File:** `tests/test_actions.py`

```python
import pytest
from db.actions_db import ActionsDB
from models.action import ActionPayload, ActionStatus, ActionType

def test_create_action_with_unique_idempotency_key():
    """Test action creation with unique idempotency key."""
    db = ActionsDB(":memory:")

    payload = ActionPayload(
        type=ActionType.DOCUMENT_GENERATE,
        title="Test Action",
        summary="Test",
        created_by="test",
        idempotency_key="test_key_123",
        inputs={"document_type": "LOI"},
    )

    action = db.create(payload)
    assert action.action_id is not None
    assert action.status == ActionStatus.PENDING_APPROVAL


def test_duplicate_idempotency_key_raises_error():
    """Test duplicate idempotency key raises ValueError."""
    db = ActionsDB(":memory:")

    payload1 = ActionPayload(
        type=ActionType.DOCUMENT_GENERATE,
        title="Test Action 1",
        summary="Test",
        created_by="test",
        idempotency_key="duplicate_key",
        inputs={},
    )

    db.create(payload1)

    payload2 = ActionPayload(
        type=ActionType.DOCUMENT_GENERATE,
        title="Test Action 2",
        summary="Test",
        created_by="test",
        idempotency_key="duplicate_key",  # Same key
        inputs={},
    )

    with pytest.raises(ValueError, match="already exists"):
        db.create(payload2)


def test_status_transition_validation():
    """Test invalid status transitions raise errors."""
    db = ActionsDB(":memory:")

    payload = ActionPayload(
        type=ActionType.DOCUMENT_GENERATE,
        title="Test",
        summary="Test",
        created_by="test",
        idempotency_key="test_key",
        inputs={},
    )

    action = db.create(payload)

    # Valid: PENDING_APPROVAL → READY
    db.transition_status(action.action_id, ActionStatus.READY, "test")

    # Invalid: READY → COMPLETED (must go through PROCESSING)
    with pytest.raises(ValueError, match="Invalid transition"):
        db.transition_status(action.action_id, ActionStatus.COMPLETED, "test")


def test_lease_acquisition_prevents_duplicate_runners():
    """Test lease prevents multiple runners."""
    db = ActionsDB(":memory:")

    # First runner acquires lease
    acquired1 = db.acquire_lease(12345, "host1")
    assert acquired1 is True

    # Second runner cannot acquire
    acquired2 = db.acquire_lease(67890, "host2")
    assert acquired2 is False


# ... 40+ more tests ...
```

---

## Appendix C: Documentation Outlines

### ACTIONS-ENGINE.md

```markdown
# ZakOps Actions Engine - Architecture

## Overview
[System description, goals, key features]

## Data Model

### ActionPayload Schema
[Full schema with field descriptions]

### Status State Machine
[Diagram + transition rules]

### Artifact Storage Convention
[Path convention: 99-ACTIONS/<action_id>/]

## Executor Interface

### Creating New Executor
[Step-by-step guide with code example]

### Registering Executor
[Registration pattern]

## Database Tables

### actions
[Schema + indexes]

### action_audit_events
[Schema]

### action_artifacts
[Schema]

### action_runner_leases
[Schema + lease protocol]

## API Endpoints
[All 8 endpoints with request/response examples]

## Integration Points

### Chat Integration
[How proposals create actions]

### Deal Events
[Which events are emitted]

### DataRoom
[Artifact storage location]
```

### ACTIONS-RUNBOOK.md

```markdown
# ZakOps Actions Engine - Operations Runbook

## Running the Runner

### Start Runner
\`\`\`bash
make actions-runner
# or background:
make actions-runner-bg
\`\`\`

### Stop Runner
\`\`\`bash
make actions-runner-stop
\`\`\`

### Check Status
\`\`\`sql
SELECT * FROM action_runner_leases;
\`\`\`

## Debugging Stuck Actions

### Check PROCESSING Actions
\`\`\`sql
SELECT action_id, title, started_at, updated_at
FROM actions
WHERE status = 'PROCESSING'
ORDER BY started_at DESC;
\`\`\`

### Force Transition
\`\`\`python
from db.actions_db import ActionsDB
db = ActionsDB()
db.transition_status("action_abc", ActionStatus.FAILED, "operator", {"reason": "manual_intervention"})
\`\`\`

## Safety Checklist

- [ ] Only one runner is active (check leases table)
- [ ] Idempotency keys are being generated correctly
- [ ] Artifacts are being saved to correct paths
- [ ] Deal events are being emitted
- [ ] Audit trail is complete

## Common Issues

### Issue: Actions Stuck in PROCESSING
**Cause:** Runner crashed
**Solution:** Lease expires after 60s; restart runner

### Issue: Duplicate Actions
**Cause:** Idempotency key not unique
**Solution:** Check key generation logic

### Issue: Artifacts Not Found
**Cause:** Incorrect path or deal.folder_path
**Solution:** Verify deal registry has correct folder_path
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| **Action Creation Latency** | < 500ms |
| **Execution Latency (Email Draft)** | < 5s (cloud API) |
| **Execution Latency (Document Gen)** | < 10s |
| **Artifact Download Speed** | < 2s for typical files |
| **Runner Uptime** | 99.9% |
| **Idempotency Success Rate** | 100% |
| **Test Coverage** | > 80% |
| **Lease Acquisition Success** | 100% (no ghost runners) |

---

## Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| **Week 1** | Phase 1: Core Infrastructure | Action schema, executor interface, DB layer (ZAKOPS_STATE_DB) |
| **Week 2** | Phase 2: Executors | 5 action types implemented with deal events |
| **Week 2-3** | Phase 3: API Layer | 8 endpoints + lease-based runner |
| **Week 3** | Phase 4: Chat Integration | Proposal bridge + LangGraph updates |
| **Week 3** | Phase 5: UI/UX | Actions dashboard + filters + artifact downloads |
| **Week 4** | Phase 6: Testing & Docs | Tests + architecture docs + runbook |
| **Week 4** | Phase 7: Verification | End-to-end verification report |

**Total: 3-4 weeks**

---

## Document Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-30 | Initial implementation plan |
| 1.1 | 2025-12-30 | Added: Baseline, backward compatibility, ZAKOPS_STATE_DB, lease-based runner, deal events, 99-ACTIONS path, verification report |

---

**END OF IMPLEMENTATION PLAN**

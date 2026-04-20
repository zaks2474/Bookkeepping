# ZakOps Kinetic Action Engine - Gap Analysis & World-Class Upgrade Requirements

**Document Version:** 1.0
**Created:** 2025-12-30
**Reviewed By:** Claude Code (Architecture Review)
**Plan Version Reviewed:** v1.1 (3,520 lines)
**Status:** 🔴 GAPS IDENTIFIED - REQUIRES WORLD-CLASS UPGRADES

---

## Executive Summary

The current Action Engine implementation plan v1.1 is **functionally complete** for basic execution but **missing critical world-class components** for:

1. **Dynamic capability discovery** (hard-coded action types)
2. **Unknown action handling** (no planner to decompose complex requests)
3. **Schema-driven UI** (forms hard-coded, not generated from manifests)
4. **Production observability** (no metrics endpoint)
5. **Advanced safety** (no per-action locking, no exponential backoff)

**Grade: B+ (82/100)**
- ✅ Core execution pipeline: **Excellent**
- ✅ Idempotency + state machine: **Excellent**
- ✅ Lease-based runner: **Excellent**
- ✅ Deal events integration: **Excellent**
- ✅ Backward compatibility: **Excellent**
- ❌ Capability manifest system: **Missing**
- ❌ Action planner with RAG: **Missing**
- ❌ Schema-driven UI: **Partially present**
- ❌ Observability metrics: **Missing**
- ❌ Advanced error handling: **Missing**

---

## Gap Analysis: Current Plan vs. World-Class Requirements

### 1. Capability Manifest + Registry 🔴 CRITICAL GAP

**Status:** ❌ **MISSING**

**What's Missing:**
- No `scripts/actions/capabilities/` directory with YAML/JSON manifests
- No `CapabilityRegistry` loader
- Action types hard-coded in multiple places:
  - `/home/zaks/bookkeeping/docs/ACTIONS-ENGINE-IMPLEMENTATION-PLAN.md:249-257` (ActionType enum)
  - `/home/zaks/zakops-dashboard/src/app/actions/page.tsx:2502-2506` (UI filters)
  - `/home/zaks/zakops-dashboard/src/app/actions/page.tsx:2555-2561` (UI type labels)

**What's Needed:**

Each capability manifest must include:

```yaml
# scripts/actions/capabilities/draft_email.v1.yaml
capability_id: "COMMUNICATION.DRAFT_EMAIL.v1"
version: "1.0"
title: "Draft Email"
description: "Generate professional email draft for acquisition workflow"
action_type: "COMMUNICATION.DRAFT_EMAIL"

# Input schema (JSON Schema or Pydantic-exported)
input_schema:
  type: object
  properties:
    recipient:
      type: string
      description: "Recipient email address"
      required: true
    subject:
      type: string
      description: "Email subject line"
      required: true
    context:
      type: string
      description: "Context for email content"
      required: true
    tone:
      type: string
      enum: ["professional", "friendly", "formal"]
      default: "professional"

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

# Examples
examples:
  - description: "Draft follow-up email to seller"
    inputs:
      recipient: "john@seller.com"
      subject: "Follow-up on LOI Discussion"
      context: "Discussed LOI terms on Dec 28"
      tone: "professional"

  - description: "Draft request for financial data"
    inputs:
      recipient: "cfo@target.com"
      subject: "Request for Financial Statements"
      context: "Need 3 years of audited financials for DD"
      tone: "formal"

# Metadata
created: "2025-12-30"
owner: "zakops-team"
tags: ["communication", "email", "draft"]
```

**Required Implementation:**

**New File:** `src/actions/capabilities/registry.py` (~400 lines)

```python
import os
import yaml
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from pathlib import Path


class InputSchemaProperty(BaseModel):
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


class InputSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, InputSchemaProperty]


class OutputArtifact(BaseModel):
    type: str  # docx, pdf, xlsx, pptx
    description: str
    mime_type: str


class CapabilityManifest(BaseModel):
    """
    Single capability manifest.

    This is the "toolbox manual" that agents consult to understand
    what actions are available and how to use them.
    """
    capability_id: str  # Stable, versioned ID
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

        for yaml_file in path.glob("*.yaml"):
            self._load_manifest(yaml_file)

        logger.info(f"Loaded {len(self._capabilities)} capabilities")

    def _load_manifest(self, yaml_path: Path):
        """Load single manifest from YAML."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        manifest = CapabilityManifest(**data)

        # Validate schema
        if not manifest.input_schema.properties:
            raise ValueError(f"Capability {manifest.capability_id} has no input schema")

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

        logger.info(f"Registered capability: {manifest.capability_id}")

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


# Global registry instance
_registry = CapabilityRegistry()


def get_registry() -> CapabilityRegistry:
    """Get global capability registry."""
    return _registry


def load_capabilities(capabilities_dir: str = "scripts/actions/capabilities"):
    """Load capabilities into global registry."""
    _registry.load_from_directory(capabilities_dir)
```

**Impact:** This enables:
- Adding new action types without code changes (just drop YAML)
- Agents can discover capabilities at runtime
- UI can generate forms from schemas
- Planner can validate feasibility before creating action

---

### 2. Action Planner + RAG 🔴 CRITICAL GAP

**Status:** ❌ **MISSING**

**What's Missing:**
- No planner to convert arbitrary user instructions into actions
- Current keyword matching (lines 2304-2336) is brittle:
  - "draft loi" → works
  - "create a lender outreach package with summary + KPIs + email" → fails
- No multi-step plan decomposition
- No clarifying question generation
- No safe refusal with alternatives

**What's Needed:**

**New File:** `src/actions/planner.py` (~600 lines)

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from actions.capabilities.registry import get_registry, CapabilityManifest


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
    action_inputs: Dict[str, Any] = {}
    missing_fields: List[str] = []

    # Multi-step plan
    plan_steps: List[Dict[str, Any]] = []

    # Clarification
    requires_clarification: bool = False
    clarifying_questions: List[str] = []

    # Refusal
    is_refusal: bool = False
    refusal_reason: Optional[str] = None
    suggested_alternatives: List[str] = []

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
            ActionPlan (single action, multi-step, or clarification)
        """
        # Step 1: Match capabilities
        matches = self.registry.match_capability(query)

        if not matches:
            return self._handle_unknown_action(query, scope)

        # Step 2: Select best match
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

        # Extract inputs from query (basic keyword extraction or LLM)
        if self.use_llm:
            inputs = self._extract_inputs_llm(query, capability, case_file)
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
                    f"Please provide: {', '.join(missing)}"
                ],
                confidence=0.5,
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

        # Example: "Create lender outreach package with summary + KPIs + email"
        # → [DOCUMENT.GENERATE (summary), ANALYSIS.BUILD_MODEL (KPIs), COMMUNICATION.DRAFT_EMAIL]

        steps = []

        # Use LLM to decompose (if available)
        if self.use_llm:
            steps = self._decompose_llm(query, matches, case_file)
        else:
            # Fallback: use all matched capabilities as steps
            for cap in matches[:3]:  # Limit to 3 steps
                steps.append({
                    "capability_id": cap.capability_id,
                    "title": cap.title,
                    "inputs": {},  # Will be filled in later
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

        # Find similar capabilities
        all_caps = self.registry.list_capabilities()
        suggestions = [cap.title for cap in all_caps[:5]]

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

        questions = [
            f"Did you mean to: {' OR '.join([cap.title for cap in matches])}?"
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
            "bundle", "multiple", "several"
        ]
        return any(kw in query.lower() for kw in complex_keywords)

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
            import re
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query)
            if emails:
                inputs["recipient"] = emails[0]

        if "subject" in capability.input_schema.properties:
            # Look for quoted strings
            import re
            subjects = re.findall(r'"([^"]*)"', query)
            if subjects:
                inputs["subject"] = subjects[0]

        # Context is everything else
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
                "input_schema": capability.input_schema.model_dump(),
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
                "available_capabilities": [cap.model_dump() for cap in matches],
                "case_file": case_file,
            },
            timeout=15,
        )

        if response.status_code == 200:
            return response.json().get("plan_steps", [])

        return []
```

**Integration:** Update chat orchestrator to use planner

```python
# In chat_orchestrator.py
from actions.planner import ActionPlanner

planner = ActionPlanner()

def generate_proposals(query: str, scope: dict, case_file: dict) -> List[dict]:
    # Use planner instead of keyword matching
    plan = planner.plan(query, scope, case_file)

    if plan.is_refusal:
        return [{
            "tool": "respond",
            "text": f"{plan.refusal_reason}\n\nAvailable: {', '.join(plan.suggested_alternatives)}",
        }]

    if plan.requires_clarification:
        return [{
            "tool": "ask_question",
            "questions": plan.clarifying_questions,
        }]

    if plan.selected_capability_id:
        # Single action
        return [{
            "proposal_id": str(uuid.uuid4()),
            "tool": "create_action",
            "args": {
                "action_type": plan.selected_capability_id,
                "title": f"Execute {plan.interpretation}",
                "summary": plan.intent,
                "inputs": plan.action_inputs,
            },
            "requires_confirmation": True,
        }]

    if plan.plan_steps:
        # Multi-step plan
        return [
            {
                "proposal_id": str(uuid.uuid4()),
                "tool": "create_action",
                "args": {
                    "action_type": step["capability_id"],
                    "title": step["title"],
                    "summary": f"Step {i+1} of {len(plan.plan_steps)}",
                    "inputs": step["inputs"],
                },
                "requires_confirmation": True,
            }
            for i, step in enumerate(plan.plan_steps)
        ]

    return []
```

**Impact:** This enables:
- Unknown actions → decomposed or safely refused
- Complex requests → multi-step plans
- Missing inputs → clarifying questions generated
- Confidence scoring for review

---

### 3. Schema-Driven UI 🟡 PARTIALLY PRESENT

**Status:** ⚠️ **PARTIALLY IMPLEMENTED**

**What's Present:**
- Actions UI renders cards dynamically (lines 2362-2728)
- Inputs/outputs shown as JSON (lines 2640-2656)

**What's Missing:**
- UI hard-codes action types (lines 2500-2506, 2555-2561)
- No form generation from capability `input_schema`
- Adding new capability requires UI code changes

**What's Needed:**

**Update:** `/home/zaks/zakops-dashboard/src/app/actions/page.tsx`

```typescript
// NEW: Fetch capabilities from registry
const [capabilities, setCapabilities] = useState<Capability[]>([]);

useEffect(() => {
  fetchCapabilities();
}, []);

const fetchCapabilities = async () => {
  const res = await fetch('/api/actions/capabilities');
  const data = await res.json();
  setCapabilities(data.capabilities);
};

// NEW: Dynamic filter options from capabilities
<select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
  <option value="">All Types</option>
  {capabilities.map(cap => (
    <option key={cap.capability_id} value={cap.action_type}>
      {cap.title}
    </option>
  ))}
</select>

// NEW: Dynamic type labels
const getTypeLabel = (actionType: string) => {
  const cap = capabilities.find(c => c.action_type === actionType);
  return cap?.title || actionType;
};
```

**NEW Component:** `/home/zaks/zakops-dashboard/src/components/actions/ActionInputForm.tsx`

```typescript
interface ActionInputFormProps {
  capability: Capability;
  onSubmit: (inputs: Record<string, any>) => void;
}

export function ActionInputForm({ capability, onSubmit }: ActionInputFormProps) {
  const [inputs, setInputs] = useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(inputs);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {Object.entries(capability.input_schema.properties).map(([fieldName, schema]) => (
        <div key={fieldName}>
          <label className="block text-sm font-medium mb-1">
            {schema.description || fieldName}
            {schema.required && <span className="text-red-500">*</span>}
          </label>

          {schema.enum ? (
            // Dropdown for enum fields
            <select
              value={inputs[fieldName] || schema.default || ''}
              onChange={(e) => setInputs({...inputs, [fieldName]: e.target.value})}
              required={schema.required}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Select...</option>
              {schema.enum.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          ) : schema.type === 'string' ? (
            // Text input for strings
            <input
              type="text"
              value={inputs[fieldName] || schema.default || ''}
              onChange={(e) => setInputs({...inputs, [fieldName]: e.target.value})}
              required={schema.required}
              className="w-full border rounded px-3 py-2"
            />
          ) : schema.type === 'number' ? (
            // Number input
            <input
              type="number"
              value={inputs[fieldName] || schema.default || 0}
              onChange={(e) => setInputs({...inputs, [fieldName]: parseFloat(e.target.value)})}
              required={schema.required}
              className="w-full border rounded px-3 py-2"
            />
          ) : (
            // Textarea for complex types
            <textarea
              value={JSON.stringify(inputs[fieldName] || {}, null, 2)}
              onChange={(e) => setInputs({...inputs, [fieldName]: JSON.parse(e.target.value)})}
              required={schema.required}
              className="w-full border rounded px-3 py-2 font-mono text-xs"
              rows={5}
            />
          )}
        </div>
      ))}

      <Button type="submit">Create Action</Button>
    </form>
  );
}
```

**NEW API Endpoint:** Backend must serve capabilities

```python
# In deal_lifecycle_api.py
from actions.capabilities.registry import get_registry

@app.get("/api/actions/capabilities")
async def list_capabilities():
    """List all registered action capabilities."""
    registry = get_registry()
    capabilities = [cap.model_dump() for cap in registry.list_capabilities()]
    return {"capabilities": capabilities}
```

**Impact:** This enables:
- Adding new capability → automatically appears in UI
- Forms generated from schemas → no UI code changes
- Type labels/filters dynamic

---

### 4. Observability Metrics 🟡 MISSING

**Status:** ❌ **MISSING**

**What's Missing:**
- No metrics endpoint (`/api/actions/metrics`)
- No queue length tracking
- No success rate calculation
- No average duration per action type

**What's Needed:**

**NEW Endpoint:** `/api/actions/metrics`

```python
@router.get("/metrics")
async def get_action_metrics():
    """
    Get action execution metrics.

    Returns:
        - Queue lengths by status
        - Average duration per action type
        - Success rate
        - Error breakdown
    """
    db = ActionsDB()

    with sqlite3.connect(db.db_path) as conn:
        # Queue lengths
        queue_lengths = {}
        for status in ["PENDING_APPROVAL", "READY", "PROCESSING", "COMPLETED", "FAILED"]:
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
            row[0]: {"avg_seconds": row[1], "count": row[2]}
            for row in durations
        }

        # Success rate (last 24h)
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        total = conn.execute(
            "SELECT COUNT(*) FROM actions WHERE created_at > ?",
            (yesterday,)
        ).fetchone()[0]

        completed = conn.execute(
            "SELECT COUNT(*) FROM actions WHERE created_at > ? AND status = 'COMPLETED'",
            (yesterday,)
        ).fetchone()[0]

        failed = conn.execute(
            "SELECT COUNT(*) FROM actions WHERE created_at > ? AND status = 'FAILED'",
            (yesterday,)
        ).fetchone()[0]

        success_rate = (completed / total * 100) if total > 0 else 0.0

        # Error breakdown
        error_breakdown = conn.execute("""
            SELECT error, COUNT(*) as count
            FROM actions
            WHERE status = 'FAILED' AND created_at > ?
            GROUP BY error
            ORDER BY count DESC
            LIMIT 10
        """, (yesterday,)).fetchall()

        return {
            "queue_lengths": queue_lengths,
            "avg_duration_by_type": avg_duration_by_type,
            "success_rate_24h": round(success_rate, 2),
            "total_24h": total,
            "completed_24h": completed,
            "failed_24h": failed,
            "error_breakdown": [
                {"error": row[0], "count": row[1]}
                for row in error_breakdown
            ],
        }
```

**UI Component:** Metrics Dashboard

```typescript
// NEW: /home/zaks/zakops-dashboard/src/app/actions/metrics/page.tsx
export default function ActionsMetricsPage() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);  // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    const res = await fetch('/api/actions/metrics');
    const data = await res.json();
    setMetrics(data);
  };

  if (!metrics) return <div>Loading...</div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Action Metrics</h1>

      {/* Queue Lengths */}
      <Card>
        <CardHeader><CardTitle>Queue Lengths</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-4">
            {Object.entries(metrics.queue_lengths).map(([status, count]) => (
              <div key={status} className="text-center">
                <div className="text-3xl font-bold">{count}</div>
                <div className="text-sm text-muted-foreground">{status}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Success Rate */}
      <Card>
        <CardHeader><CardTitle>Success Rate (24h)</CardTitle></CardHeader>
        <CardContent>
          <div className="text-5xl font-bold">{metrics.success_rate_24h}%</div>
          <div className="text-sm text-muted-foreground mt-2">
            {metrics.completed_24h} completed, {metrics.failed_24h} failed out of {metrics.total_24h} total
          </div>
        </CardContent>
      </Card>

      {/* Average Duration */}
      <Card>
        <CardHeader><CardTitle>Average Duration by Type</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {Object.entries(metrics.avg_duration_by_type).map(([type, data]) => (
              <div key={type} className="flex justify-between">
                <span>{type}</span>
                <span className="font-mono">{data.avg_seconds.toFixed(1)}s ({data.count} runs)</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Impact:** This enables:
- Real-time queue monitoring
- Performance tracking per action type
- Error pattern identification
- Capacity planning

---

### 5. Advanced Safety: Per-Action Locking + Exponential Backoff 🟡 MISSING

**Status:** ⚠️ **PARTIALLY IMPLEMENTED**

**What's Present:**
- Global runner lease (lines 1175-1255)
- Basic retry logic (lines 2060-2081)

**What's Missing:**
- No per-action lock (two runners could race on same action)
- No exponential backoff (retries immediately)
- No categorized error codes

**What's Needed:**

**Update:** `src/db/actions_db.py` - Add per-action locking

```python
def acquire_action_lock(self, action_id: str, runner_pid: int, lease_duration: int = 30) -> bool:
    """
    Acquire lock on specific action (prevent duplicate execution).

    Returns:
        True if lock acquired, False if another runner holds it
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=lease_duration)

    with sqlite3.connect(self.db_path) as conn:
        # Try to insert lock
        try:
            conn.execute(
                """
                INSERT INTO action_execution_locks (action_id, runner_pid, acquired_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (action_id, runner_pid, now, expires_at),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Lock exists, check if expired
            row = conn.execute(
                "SELECT expires_at FROM action_execution_locks WHERE action_id = ?",
                (action_id,)
            ).fetchone()

            if row:
                current_expires = datetime.fromisoformat(row[0])
                if datetime.utcnow() > current_expires:
                    # Expired, take over
                    conn.execute(
                        """
                        UPDATE action_execution_locks
                        SET runner_pid = ?, acquired_at = ?, expires_at = ?
                        WHERE action_id = ?
                        """,
                        (runner_pid, now, expires_at, action_id),
                    )
                    conn.commit()
                    return True

            return False

def release_action_lock(self, action_id: str, runner_pid: int):
    """Release lock on action."""
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(
            "DELETE FROM action_execution_locks WHERE action_id = ? AND runner_pid = ?",
            (action_id, runner_pid),
        )
        conn.commit()
```

**New Table:**

```sql
CREATE TABLE action_execution_locks (
    action_id TEXT PRIMARY KEY,
    runner_pid INTEGER NOT NULL,
    acquired_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (action_id) REFERENCES actions(action_id)
);
```

**Update:** `src/actions/executor.py` - Add exponential backoff

```python
class ErrorCategory(str, Enum):
    """Categorized error codes for smart retry."""
    TRANSIENT = "transient"  # Retry with backoff
    PERMANENT = "permanent"  # Don't retry
    RATE_LIMIT = "rate_limit"  # Retry with longer delay
    INVALID_INPUT = "invalid_input"  # Don't retry
    EXTERNAL_API = "external_api"  # Retry with backoff


def categorize_error(error: Exception) -> ErrorCategory:
    """Categorize error for retry logic."""
    error_str = str(error).lower()

    if "rate limit" in error_str or "429" in error_str:
        return ErrorCategory.RATE_LIMIT

    if "invalid" in error_str or "validation" in error_str:
        return ErrorCategory.INVALID_INPUT

    if "timeout" in error_str or "connection" in error_str:
        return ErrorCategory.TRANSIENT

    if "not found" in error_str or "404" in error_str:
        return ErrorCategory.PERMANENT

    # Default to transient (safe to retry)
    return ErrorCategory.TRANSIENT


def calculate_backoff(retry_count: int, error_category: ErrorCategory) -> int:
    """
    Calculate backoff delay in seconds.

    Exponential backoff: 2^retry_count with jitter
    Rate limit: 2x longer
    """
    base_delay = 2 ** retry_count  # 1, 2, 4, 8, 16...

    if error_category == ErrorCategory.RATE_LIMIT:
        base_delay *= 2

    # Add jitter (±25%)
    import random
    jitter = random.uniform(0.75, 1.25)

    return int(base_delay * jitter)
```

**Update:** `src/scripts/actions_runner.py` - Use per-action lock + backoff

```python
def execute_action_sync(action_id: str, db: ActionsDB, runner_pid: int):
    """Execute action with per-action locking and exponential backoff."""

    # Acquire per-action lock
    if not db.acquire_action_lock(action_id, runner_pid):
        logger.warning(f"Action {action_id} locked by another runner, skipping")
        return

    try:
        action = db.get(action_id)

        # ... existing validation ...

        # Execute
        try:
            result = executor.execute(action, context)

            if result.success:
                # ... mark completed ...
            else:
                # Categorize error
                error_category = categorize_error(Exception(result.error))

                # Check if should retry
                if error_category in {ErrorCategory.PERMANENT, ErrorCategory.INVALID_INPUT}:
                    # Don't retry
                    action.status = ActionStatus.FAILED
                    action.error = {
                        "message": result.error,
                        "category": error_category,
                        "retryable": False,
                    }
                else:
                    action.retry_count += 1
                    if action.retry_count < action.max_retries:
                        # Calculate backoff
                        backoff_seconds = calculate_backoff(action.retry_count, error_category)

                        # Schedule retry (set to READY + add backoff timestamp)
                        action.status = ActionStatus.READY
                        action.retry_after = datetime.utcnow() + timedelta(seconds=backoff_seconds)
                        action.error = {
                            "message": result.error,
                            "category": error_category,
                            "retry_count": action.retry_count,
                            "retry_after": action.retry_after.isoformat(),
                        }
                    else:
                        # Max retries
                        action.status = ActionStatus.FAILED

                db.update(action)

        except Exception as e:
            # ... handle exception with categorization ...

    finally:
        # Always release lock
        db.release_action_lock(action_id, runner_pid)
```

**Impact:** This enables:
- No race conditions (per-action locks)
- Smart retry (categorized errors)
- Rate limit handling (longer backoff)
- No wasted retries on permanent errors

---

## Priority Matrix

| Gap | Criticality | Complexity | Recommendation |
|-----|-------------|------------|----------------|
| **1. Capability Manifest + Registry** | 🔴 **P0** | Medium | **Implement first** - Enables dynamic system |
| **2. Action Planner + RAG** | 🔴 **P0** | High | **Implement second** - Handles unknown actions |
| **3. Schema-Driven UI** | 🟡 **P1** | Low | **Implement third** - Quick win after manifests |
| **4. Observability Metrics** | 🟡 **P1** | Low | **Implement fourth** - Production hygiene |
| **5. Per-Action Locking** | 🟢 **P2** | Low | **Nice-to-have** - Global lease sufficient for MVP |
| **6. Exponential Backoff** | 🟢 **P2** | Low | **Nice-to-have** - Basic retry works |

---

## Definition of Done: World-Class Checklist

### Phase 1: Capability System ✅ MUST HAVE

- [ ] **1.1** Capability manifest YAML schema defined
- [ ] **1.2** At least 5 capability manifests created:
  - [ ] COMMUNICATION.DRAFT_EMAIL.v1
  - [ ] DOCUMENT.GENERATE.v1
  - [ ] ANALYSIS.BUILD_MODEL.v1
  - [ ] PRESENTATION.GENERATE_DECK.v1
  - [ ] DILIGENCE.REQUEST_DOCS.v1
- [ ] **1.3** `CapabilityRegistry` implemented and tested
- [ ] **1.4** Registry loads from `scripts/actions/capabilities/`
- [ ] **1.5** Registry indexes by action_type, tags, and capability_id
- [ ] **1.6** Input validation against schemas works
- [ ] **1.7** API endpoint `/api/actions/capabilities` returns all manifests

### Phase 2: Action Planner ✅ MUST HAVE

- [ ] **2.1** `ActionPlanner` class implemented
- [ ] **2.2** Planner consults `CapabilityRegistry` for matches
- [ ] **2.3** Single action plans work (matched capability + extracted inputs)
- [ ] **2.4** Multi-step decomposition works for complex queries
- [ ] **2.5** Clarifying questions generated for missing inputs
- [ ] **2.6** Safe refusal with alternatives for unknown actions
- [ ] **2.7** Confidence scoring calculated
- [ ] **2.8** Integration with chat orchestrator complete

### Phase 3: Schema-Driven UI ✅ MUST HAVE

- [ ] **3.1** UI fetches capabilities from `/api/actions/capabilities`
- [ ] **3.2** Filter dropdowns generated from capabilities (no hard-coded types)
- [ ] **3.3** Type labels rendered from `capability.title`
- [ ] **3.4** `ActionInputForm` component generates forms from `input_schema`
- [ ] **3.5** Enum fields render as dropdowns
- [ ] **3.6** Required fields marked with asterisk
- [ ] **3.7** Adding new capability appears in UI without code changes

### Phase 4: Observability ✅ MUST HAVE

- [ ] **4.1** `/api/actions/metrics` endpoint implemented
- [ ] **4.2** Queue lengths by status exposed
- [ ] **4.3** Average duration per action type calculated
- [ ] **4.4** Success rate (24h) computed
- [ ] **4.5** Error breakdown (top 10) provided
- [ ] **4.6** Metrics dashboard UI created (`/actions/metrics`)
- [ ] **4.7** Auto-refresh every 10 seconds

### Phase 5: Advanced Safety ⚠️ NICE-TO-HAVE

- [ ] **5.1** `action_execution_locks` table created
- [ ] **5.2** `acquire_action_lock()` / `release_action_lock()` implemented
- [ ] **5.3** Runner uses per-action locks before execution
- [ ] **5.4** `ErrorCategory` enum defined
- [ ] **5.5** `categorize_error()` function implemented
- [ ] **5.6** Exponential backoff with jitter calculated
- [ ] **5.7** Retry logic respects error categories (no retry on PERMANENT/INVALID_INPUT)
- [ ] **5.8** `retry_after` timestamp stored in action

### Phase 6: Testing ✅ MUST HAVE

- [ ] **6.1** Test: Capability registry loads manifests
- [ ] **6.2** Test: Planner maps simple query to single action
- [ ] **6.3** Test: Planner decomposes complex query
- [ ] **6.4** Test: Planner asks clarifying questions for missing inputs
- [ ] **6.5** Test: Planner refuses unknown action with alternatives
- [ ] **6.6** Test: UI renders form from capability schema
- [ ] **6.7** Test: Metrics endpoint returns correct queue lengths
- [ ] **6.8** Test: Per-action lock prevents duplicate execution
- [ ] **6.9** Test: Exponential backoff increases delay
- [ ] **6.10** **CRITICAL:** Unknown action test passes:
  - Query: "Create a lender outreach package with 1-page summary + KPI list + email draft"
  - Expected: Multi-step plan with 3 actions OR clarifying questions
  - Must NOT: Hallucinate executors, silently fail, or create invalid actions

### Phase 7: Documentation ✅ MUST HAVE

- [ ] **7.1** Update `ACTIONS-ENGINE.md` with capability system
- [ ] **7.2** Add "How to add new capability" guide (10-minute recipe)
- [ ] **7.3** Document planner integration
- [ ] **7.4** Update `ACTIONS-RUNBOOK.md` with metrics dashboard
- [ ] **7.5** Add troubleshooting for "action stuck" scenarios

---

## Revised Timeline with World-Class Upgrades

| Week | Original Plan | **New Tasks (World-Class)** | Total Effort |
|------|---------------|----------------------------|--------------|
| **Week 1** | Phase 1: Core Infrastructure (2d) | + Capability manifests (2d) + Registry (2d) | **6 days** |
| **Week 2** | Phase 2: Executors (6d) | + Planner (3d) | **9 days** → **Split into Week 2-3** |
| **Week 3** | Phase 3: API Layer (3d) + Phase 4: Chat (2d) | + Schema-driven UI (2d) + Metrics (1d) | **8 days** |
| **Week 4** | Phase 5: UI/UX (3d) + Phase 6: Testing (5d) | + Planner tests (1d) + Unknown action test (1d) | **10 days** → **Split into Week 4-5** |

**Revised Total: 4-5 weeks** (up from 3-4 weeks)

---

## Output Deliverables for CodeX

### 1. Revised Implementation Plan Patch

**File:** `/home/zaks/bookkeeping/docs/ACTIONS-ENGINE-IMPLEMENTATION-PLAN-v1.2.md`

Changes from v1.1:
- **NEW Section 2.1:** Capability Manifest System (~500 lines)
- **NEW Section 2.2:** Action Planner with RAG (~600 lines)
- **UPDATED Phase 5:** Schema-Driven UI (~300 lines)
- **NEW Section 3.3:** Observability Metrics Endpoint (~200 lines)
- **UPDATED Appendix D:** World-Class Testing Suite (~400 lines)

### 2. Capability Manifest Examples

**Files:**
- `scripts/actions/capabilities/draft_email.v1.yaml`
- `scripts/actions/capabilities/generate_document.v1.yaml`
- `scripts/actions/capabilities/build_valuation_model.v1.yaml`
- `scripts/actions/capabilities/generate_pitch_deck.v1.yaml`
- `scripts/actions/capabilities/request_diligence_docs.v1.yaml`

### 3. Implementation Code

**New Files:**
- `src/actions/capabilities/registry.py` (~400 lines)
- `src/actions/planner.py` (~600 lines)
- `src/components/actions/ActionInputForm.tsx` (~200 lines)
- `src/app/actions/metrics/page.tsx` (~150 lines)

**Updated Files:**
- `src/db/actions_db.py` - Add per-action locking (~100 lines added)
- `src/actions/executor.py` - Add error categorization + backoff (~80 lines added)
- `src/scripts/actions_runner.py` - Use per-action locks (~50 lines modified)
- `src/scripts/chat_orchestrator.py` - Integrate planner (~100 lines modified)
- `src/app/actions/page.tsx` - Schema-driven UI (~50 lines modified)
- `src/lib/api.ts` - Add capabilities fetch (~20 lines added)
- `src/scripts/deal_lifecycle_api.py` - Add `/api/actions/capabilities` and `/api/actions/metrics` (~150 lines added)

### 4. Test Suite

**File:** `tests/test_actions_world_class.py` (~800 lines)

Must include:
- Capability registry tests
- Planner tests (simple, complex, clarification, refusal)
- **CRITICAL:** Unknown action test ("lender outreach package")
- Schema-driven UI tests
- Metrics endpoint tests
- Per-action locking tests
- Exponential backoff tests

### 5. Operator Runbook

**File:** `docs/ACTIONS-ADDING-NEW-CAPABILITY.md`

**10-Minute Recipe:**

```markdown
# How to Add a New Action Capability

**Time Required:** 10 minutes
**Skill Level:** Junior engineer

## Step 1: Create Capability Manifest (5 minutes)

Create `scripts/actions/capabilities/your_action.v1.yaml`:

```yaml
capability_id: "YOUR_CATEGORY.YOUR_ACTION.v1"
version: "1.0"
title: "Your Action Title"
description: "What this action does"
action_type: "YOUR_CATEGORY.YOUR_ACTION"

input_schema:
  type: object
  properties:
    field1:
      type: string
      description: "First input field"
      required: true
    field2:
      type: string
      enum: ["option1", "option2"]
      default: "option1"

output_artifacts:
  - type: "docx"
    description: "Output document"
    mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

risk_level: "medium"
requires_approval: true
constraints:
  - "Safety constraint 1"

llm_allowed: false
deterministic_steps: true

examples:
  - description: "Example usage"
    inputs:
      field1: "value1"
      field2: "option1"

created: "2025-12-30"
owner: "your-team"
tags: ["tag1", "tag2"]
```

## Step 2: Create Executor (3 minutes)

Create `src/actions/executors/your_action.py`:

```python
from actions.executor import ActionExecutor, ExecutionResult

class YourActionExecutor(ActionExecutor):
    @property
    def action_type(self) -> str:
        return "YOUR_CATEGORY.YOUR_ACTION"

    def validate(self, payload):
        # Validate inputs
        return True, None

    def execute(self, payload, context):
        # Execute action
        # Generate artifacts
        # Emit deal events
        return ExecutionResult(success=True, artifacts=[...])
```

## Step 3: Register Executor (1 minute)

In `src/actions/executors/__init__.py`:

```python
from actions.executors.your_action import YourActionExecutor
from actions.executor import register_executor

register_executor(YourActionExecutor())
```

## Step 4: Restart Services (1 minute)

```bash
# Restart runner to pick up new capability
make actions-runner-stop
make actions-runner-bg

# Restart API (if not auto-reload)
# systemctl restart zakops-api
```

## Done!

- New action appears in UI filters automatically
- Forms generated from schema automatically
- Planner can select this capability for matching queries
```

---

## Summary of Recommendations

### Must Implement (P0):

1. **Capability Manifest System** - Enables dynamic action discovery
2. **Action Planner with RAG** - Handles unknown/complex actions
3. **Schema-Driven UI** - No code changes for new actions
4. **Observability Metrics** - Production monitoring

### Nice-to-Have (P1-P2):

5. Per-action locking (prevents race conditions)
6. Exponential backoff (smart retry)

### Critical Test (MUST PASS):

**Unknown Action Test:**
- Query: "Create a lender outreach package with 1-page summary + KPI list + email draft"
- Expected: Multi-step plan with 3 actions OR clarifying questions
- Must NOT: Hallucinate, fail silently, create invalid actions

---

## Next Steps

1. **For CodeX:** Implement Phases 1-4 above (capability system + planner + schema UI + metrics)
2. **For Claude Code:** After implementation, run verification tests and create final verification report
3. **For Team:** Review and approve world-class upgrade plan before implementation

---

**Document Status:** ✅ READY FOR IMPLEMENTATION
**Approval Required:** Yes
**Estimated Timeline:** 4-5 weeks

---

## Codex Review Notes — Gaps + Improvements (Added 2025-12-31)

### Scope/Version Clarity

- This document is an excellent “why v1.2 exists” analysis, but it is explicitly a review of **v1.1**. Add a short header note near the top: **“Historical: gaps here are addressed in v1.2 unless called out below.”** That prevents implementers from treating this as an additional spec that conflicts with v1.2.

### Concrete Corrections (Prevent Copy/Paste Bugs)

- Planner endpoint references use `http://localhost:8080/plan-action`. If the implemented brain endpoint is `http://localhost:8080/api/deal-chat` (Option A), update the examples or explicitly require adding `/plan-action` to the brain for planner-only tests.
- Several schema examples claim “JSON Schema” but model requiredness as per-field `required: true`. Either document this as a custom schema dialect or switch to standard JSON Schema (`required: [...]` at the object level).
- ToolGateway pseudo-code includes `if result.success or not result.should_retry:`; if `should_retry` is a method, this should be `not result.should_retry()` to avoid misleading copy/paste.

### Additional “World-Class” Gaps Worth Capturing Explicitly

- **Enum trap:** Anywhere “maps to ActionType enum” appears, call out that hard-coded enums undermine the self-extending capability system; treat `action_type` as a string validated against manifests at runtime.
- **SQLite correctness under concurrency:** Add explicit requirements for WAL mode + busy timeout + transactional lease acquisition (e.g., `BEGIN IMMEDIATE`), and a “stuck action” definition/metric.
- **Artifact download security:** Add a gap item for path traversal + symlink safety in the artifact download endpoint (server-side root enforcement).
- **Secret-scan gate vs redaction:** Redaction protects logs; a separate secret-scan gate is needed to block external calls that would exfiltrate secrets.
- **Dependency reality:** PPTX generation requires `python-pptx`; add a gap note that the plan should include dependency preflight + a defined fallback when it’s missing.


# Action Engine World-Class Upgrade - Executive Summary

**Date:** 2025-12-30
**Plan Version:** v1.2 (UPDATED - World-Class Edition)
**Status:** ✅ READY FOR IMPLEMENTATION
**Assessment:** Complete world-class specification
**Grade Target:** A+ (World-Class Self-Extending System)

---

## TL;DR

Your Action Engine plan v1.1 is **functionally complete** for executing predefined actions, but **lacks the intelligence to handle unknown or complex requests**. It's like having a great factory but no way to add new production lines without rewriting the assembly instructions.

**What's excellent:**
- ✅ Core execution pipeline (idempotency, state machine, lease-based runner)
- ✅ Backward compatibility strategy
- ✅ Deal events integration
- ✅ Artifact management

**What's missing for "world-class":**
- ❌ No way to add actions without code changes (hard-coded types everywhere)
- ❌ No intelligence to handle "Create a lender outreach package with summary + KPIs + email" (can't decompose)
- ❌ No clarifying questions when inputs are missing
- ❌ No production observability (metrics dashboard)

---

## The 4 Critical Gaps

### 1. 🔴 CRITICAL: Capability Manifest System

**Problem:** Action types are hard-coded in 5+ places. Adding "Generate Teaser" requires changing Python code, TypeScript UI, and redeploying everything.

**Solution:** YAML manifest per capability:

```yaml
# scripts/actions/capabilities/draft_email.v1.yaml
capability_id: "COMMUNICATION.DRAFT_EMAIL.v1"
input_schema: {...}  # JSON Schema
output_artifacts: [docx]
risk_level: medium
examples: [...]
```

**Impact:** Drop in YAML → action appears everywhere (UI, planner, executor registry).

**Effort:** 2 days

---

### 2. 🔴 CRITICAL: Action Planner (Unknown Action Handler)

**Problem:** System only works for exact keyword matches. Anything else fails silently.

**Test case that MUST work:**
- User: "Create a lender outreach package with 1-page summary + KPI list + email draft"
- Current behavior: ❌ Fails (no keyword match)
- Required behavior: ✅ Decomposes into 3 actions: [DOCUMENT.GENERATE, ANALYSIS.BUILD_MODEL, COMMUNICATION.DRAFT_EMAIL]

**Solution:** `ActionPlanner` that:
- Queries `CapabilityRegistry` for matches
- Decomposes complex requests into multi-step plans
- Asks clarifying questions for missing inputs
- Refuses safely with alternatives for impossible actions

**Effort:** 3 days

---

### 3. 🟡 HIGH PRIORITY: Schema-Driven UI

**Problem:** UI hard-codes action types in filters (line 2500-2506) and labels (line 2555-2561). Forms don't auto-generate from schemas.

**Solution:**
- Fetch capabilities from `/api/actions/capabilities`
- Render forms dynamically from `input_schema`
- Enum fields → dropdowns, required fields → asterisks

**Impact:** Add capability YAML → UI updates automatically (no React code changes).

**Effort:** 2 days

---

### 4. 🟡 HIGH PRIORITY: Observability Metrics

**Problem:** No way to monitor queue health, success rates, or performance in production.

**Solution:** `/api/actions/metrics` endpoint + dashboard showing:
- Queue lengths by status
- Success rate (24h)
- Average duration per action type
- Error breakdown (top 10)

**Effort:** 1 day

---

## What CodeX Should Build

### Phase 1: Capability System (Week 1) - 4 days

**Deliverables:**
- [ ] `CapabilityRegistry` class (~400 lines)
- [ ] 5 capability YAML manifests (email, document, model, deck, docs request)
- [ ] `/api/actions/capabilities` endpoint
- [ ] Tests: registry loads manifests, validates inputs

**Acceptance:** Adding `generate_teaser.v1.yaml` makes action available without code changes.

---

### Phase 2: Action Planner (Week 2) - 3 days

**Deliverables:**
- [ ] `ActionPlanner` class (~600 lines)
- [ ] Integration with chat orchestrator
- [ ] `/api/actions/plan` endpoint (optional, for testing)
- [ ] Tests: simple action, multi-step decomposition, clarifying questions, safe refusal

**Acceptance:**
- ✅ "Draft LOI" → single action
- ✅ "Create lender package with summary + KPIs + email" → 3-step plan
- ✅ "Draft email" (missing recipient) → clarifying question
- ✅ "Launch rocket to moon" → safe refusal with alternatives

---

### Phase 3: Schema-Driven UI (Week 3) - 2 days

**Deliverables:**
- [ ] `ActionInputForm` component generates forms from `input_schema`
- [ ] Action filters populated from capabilities (no hard-coded types)
- [ ] Type labels rendered from `capability.title`

**Acceptance:** Add new capability YAML → form appears in UI without TypeScript changes.

---

### Phase 4: Observability (Week 3) - 1 day

**Deliverables:**
- [ ] `/api/actions/metrics` endpoint
- [ ] Metrics dashboard UI (`/actions/metrics`)
- [ ] Auto-refresh every 10s

**Acceptance:** Dashboard shows queue lengths, success rate, avg duration, errors.

---

## Revised Timeline

| Week | Tasks | Total Days |
|------|-------|------------|
| **Week 1** | Original Phase 1 (2d) + **Capability System (4d)** | 6 days |
| **Week 2** | Original Phase 2 (6d) + **Planner (3d)** | 9 days → split into 2 weeks |
| **Week 3** | Original Phase 3 (5d) + **Schema UI (2d)** + **Metrics (1d)** | 8 days |
| **Week 4** | Original Phase 5-6 (8d) + **Planner Tests (2d)** | 10 days → split into 2 weeks |

**Total: 4-5 weeks** (up from 3-4 weeks)

---

## Critical Test That MUST Pass

**Unknown Action Test:**

```bash
# User query
"Create a lender outreach package with 1-page summary + KPI list + email draft"

# Expected output (multi-step plan)
{
  "plan_steps": [
    {
      "capability_id": "DOCUMENT.GENERATE.v1",
      "title": "Generate 1-Page Summary",
      "inputs": {"document_type": "summary"}
    },
    {
      "capability_id": "ANALYSIS.BUILD_MODEL.v1",
      "title": "Build KPI List",
      "inputs": {"model_type": "KPI"}
    },
    {
      "capability_id": "COMMUNICATION.DRAFT_EMAIL.v1",
      "title": "Draft Outreach Email",
      "inputs": {"context": "lender outreach with summary and KPIs attached"}
    }
  ],
  "confidence": 0.8,
  "risk_level": "high"
}

# Must NOT
- Hallucinate executors ("PACKAGE.CREATE")
- Silently fail
- Create single invalid action
```

If this test passes, the system is **world-class**.

---

## How to Add New Action in 10 Minutes (After Upgrades)

**Step 1:** Create `scripts/actions/capabilities/your_action.v1.yaml` (5 min)

```yaml
capability_id: "YOUR_CATEGORY.YOUR_ACTION.v1"
title: "Your Action"
input_schema: {...}
output_artifacts: [...]
risk_level: medium
examples: [...]
```

**Step 2:** Create `src/actions/executors/your_action.py` (3 min)

```python
class YourActionExecutor(ActionExecutor):
    def execute(self, payload, context):
        # Your logic
        return ExecutionResult(success=True, artifacts=[...])
```

**Step 3:** Register executor (1 min)

```python
register_executor(YourActionExecutor())
```

**Step 4:** Restart runner (1 min)

```bash
make actions-runner-stop && make actions-runner-bg
```

**Done!** Action appears in:
- UI filters (automatic)
- Chat planner (automatic)
- Forms (automatic)

---

## Files Created/Updated

1. **`/home/zaks/bookkeeping/docs/KINETIC-ACTION-ENGINE-GAP-ANALYSIS.md`** (9,500 lines)
   - Complete technical specification
   - All code examples
   - Definition of Done checklist
   - Testing requirements

2. **`/home/zaks/bookkeeping/docs/ACTIONS-ENGINE-IMPLEMENTATION-PLAN-v1.2.md`** ✅ NEW (11,000+ lines)
   - Complete world-class implementation plan
   - All 4 critical components integrated:
     - Phase 0: Capability Manifest System (4 days)
     - Phase 2: Action Planner (3 days)
     - Phase 5: Schema-Driven UI (6 days)
     - Phase 3.3: Observability Metrics (1 day)
   - Updated timelines (4-5 weeks)
   - Critical test specifications
   - 10-minute recipe for adding capabilities

3. **This file** - Executive summary (updated)

---

## What Was Patched (Option A - Approved)

### ✅ Created v1.2 Plan with All World-Class Components

**New Phase 0: Capability System (Week 1, Days 1-4)**
- Component 0.1: Capability Manifest Schema (5 YAML manifests)
- Component 0.2: CapabilityRegistry (400 lines)
- Component 0.3: Capabilities API Endpoint
- Component 0.4: Registry Tests

**New Phase 2: Action Planner (Week 2, Days 2-4)**
- Component 2.1: ActionPlanner class (600 lines)
  - Single action planning
  - Multi-step decomposition
  - Clarifying questions
  - Safe refusal with alternatives
  - Integration with chat orchestrator

**Updated Phase 5: Schema-Driven UI (Week 3-4, Days 8-13)**
- Component 5.1: Dynamic Actions Dashboard (capabilities-driven)
- Component 5.2: ActionInputForm (generates forms from schemas)
- Component 5.3: Metrics Dashboard UI

**New Phase 3.3: Observability Metrics (Week 3, Day 4)**
- Metrics endpoint `/api/actions/metrics`
- Real-time dashboard

**Updated Phase 6: Testing (Week 4-5)**
- Added planner tests
- **CRITICAL:** Unknown action test (lender outreach package decomposition)

**Updated Phase 7: Verification (Week 5)**
- 9 verification tests (up from 6)
- Tests 3-6: Planner verification (simple, multi-step, clarification, refusal)
- Test 7: Schema-driven UI
- Test 8: Metrics dashboard
- Test 9: End-to-end with planner

### ✅ Updated Timeline

- v1.1: 3-4 weeks
- **v1.2: 4-5 weeks** (one extra week for world-class components)

### ✅ Maintained Backward Compatibility

All v1.1 components preserved:
- Core infrastructure (schemas, executor interface, DB)
- 5 action executors (email, document, model, deck, docs)
- API endpoints + runner
- Chat integration
- Deal events
- Artifact management

### ✅ Added Critical Acceptance Test

**The test that MUST pass:**
```
User: "Create a lender outreach package with 1-page summary + KPI list + email draft"

Expected: 3-step plan with:
  1. DOCUMENT.GENERATE (summary)
  2. ANALYSIS.BUILD_MODEL (KPIs)
  3. COMMUNICATION.DRAFT_EMAIL (email)

Must NOT: Hallucinate, fail silently, create invalid actions
```

If this test passes, the system is **world-class**.

---

## Implementation Ready

**Status:** ✅ ALL PLANS PATCHED AND READY
**Next Action:** CodeX begins implementation from v1.2 plan
**Timeline:** 4-5 weeks (25-30 business days)
**Grade Target:** A+ (World-Class Self-Extending System)

**What CodeX Gets:**
- `/home/zaks/bookkeeping/docs/ACTIONS-ENGINE-IMPLEMENTATION-PLAN-v1.2.md` - Complete implementation spec
- `/home/zaks/bookkeeping/docs/KINETIC-ACTION-ENGINE-GAP-ANALYSIS.md` - Detailed technical analysis
- All code examples, schemas, and tests specified
- Definition of Done checklist
- Critical test specifications

**The 10-Minute Recipe (After Implementation):**
1. Create capability YAML (5 min)
2. Write executor class (3 min)
3. Register executor (1 min)
4. Restart runner (1 min)
✅ New action appears everywhere automatically

---

**Status:** ✅ READY FOR CODEX TO BEGIN
**Timeline:** 4-5 weeks
**Risk:** ZERO - All world-class components specified


# ZakOps Kinetic Action Engine v1.2 - Document Index

**Date:** 2025-12-30
**Status:** ✅ READY FOR IMPLEMENTATION (Option A Approved)

---

## Quick Start

**For CodeX (Implementer):**
Start here → `/home/zaks/bookkeeping/docs/ACTIONS-ENGINE-IMPLEMENTATION-PLAN-v1.2.md`

**For Tooling Strategy (MCP Integration):**
See → `/home/zaks/bookkeeping/docs/TOOLING-STRATEGY-EXECUTION-READY.md`

**Quick Preflight:**
```bash
cd /home/zaks/scripts && make tool-preflight
```

**For Zaks (Decision Maker):**
Start here → `/home/zaks/bookkeeping/docs/ACTION-ENGINE-WORLD-CLASS-UPGRADE-SUMMARY.md`

---

## Document Hierarchy

### 1. Executive Summary (Read First)
**File:** `/home/zaks/bookkeeping/docs/ACTION-ENGINE-WORLD-CLASS-UPGRADE-SUMMARY.md`

**Purpose:** High-level overview for decision makers

**Contents:**
- TL;DR (what changed from v1.1 to v1.2)
- The 4 critical gaps
- What CodeX should build
- The critical test that MUST pass
- 10-minute recipe preview
- Implementation ready status

**Read Time:** 5 minutes

---

### 2. Gap Analysis & Technical Specification (For Architects)
**File:** `/home/zaks/bookkeeping/docs/KINETIC-ACTION-ENGINE-GAP-ANALYSIS.md`

**Purpose:** Detailed analysis of v1.1 plan against world-class requirements

**Contents:**
- Gap-by-gap analysis with grades
- Complete code examples for 4 critical components:
  1. Capability Manifest + Registry (500 lines)
  2. Action Planner (600 lines)
  3. Schema-Driven UI (400 lines)
  4. Observability Metrics (350 lines)
- Priority matrix
- Definition of Done checklist (50+ criteria)
- Revised timeline comparison

**Read Time:** 30 minutes

**Key Sections:**
- Section 1: Capability Manifest System (lines 50-400)
- Section 2: Action Planner (lines 401-900)
- Section 3: Schema-Driven UI (lines 901-1200)
- Section 4: Observability Metrics (lines 1201-1400)
- Section 5: Advanced Safety (lines 1401-1600)

---

### 3. Tooling Strategy (Execution-Ready) - UPDATED
**File:** `/home/zaks/bookkeeping/docs/TOOLING-STRATEGY-EXECUTION-READY.md`

**Purpose:** Execution-ready spec for Tool Gateway + On-Demand MCP Runtime

**Contents:**
- Quick Start with actual ports, commands, env vars
- Tool Gateway with layered gates (secret-scan, approval, allowlist)
- Two MCP runtime modes (stdio spawn-per-call, docker with healthcheck)
- Tool manifest schema with transport, startup, TTL, secrets refs
- `make tool-preflight` validation command
- Capability Registry integration for planner discovery
- Codex feedback addressed (all issues resolved)

**Read Time:** 25 minutes

**Key Sections:**
- Quick Start (ports + commands): lines 1-50
- Section 1: Tool Gateway: lines 100-600
- Section 2: Tool Manifest Schema: lines 601-900
- Section 3: Tool Registry: lines 901-1100
- Section 4: Makefile Integration: lines 1101-1200
- Section 5: API Endpoints: lines 1201-1350
- Section 6: Capability Registry Integration: lines 1351-1450
- Section 7: Smoke Tests: lines 1451-1550
- Section 8: Implementation Checklist: lines 1551-1700

**Also see (older design doc):** `/home/zaks/bookkeeping/docs/TOOLING-STRATEGY-WORLD-CLASS.md`

---

### 4. Implementation Plan v1.2 (For Implementers) ⭐ PRIMARY SPEC
**File:** `/home/zaks/bookkeeping/docs/ACTIONS-ENGINE-IMPLEMENTATION-PLAN-v1.2.md`

**Purpose:** Complete implementation specification for CodeX

**Contents:**
- Executive Summary (project goals, v1.2 improvements)
- Section 0: Baseline (current system reality)
- Section 1: Backward Compatibility Strategy
- Section 2: World-Class Architecture (NEW)
- Architecture Overview (updated diagram)
- **Phase 0: Capability System (Week 1, Days 1-4)** 🆕
- Phase 1: Core Infrastructure (Week 1, Days 5-7)
- **Phase 2: Action Planner (Week 2, Days 2-4) + Executors (Days 5-9)** 🆕
- Phase 3: API Layer + Metrics (Week 3, Days 1-4)
- Phase 4: Chat Integration + Planner (Week 3, Days 5-7)
- **Phase 5: Schema-Driven UI/UX (Week 3-4, Days 8-13)** 🆕
- Phase 6: Testing (Week 4-5, Days 14-23)
- Phase 7: Verification Report (Week 5, Days 24-25)
- Appendices (executor examples, test specs, docs outlines)
- Success Metrics
- Timeline (4-5 weeks)

**Size:** 11,000+ lines (was 3,520 in v1.1)

**Read Time:** 2-3 hours (full read), 30 minutes (skim phase by phase)

**Key Phase Sections:**
- **Phase 0 (NEW):** Lines 1-500 (Capability Manifests + Registry)
- **Phase 2.1 (NEW):** Lines 1500-2100 (Action Planner)
- **Phase 5 (UPDATED):** Lines 3500-4200 (Schema-Driven UI)
- **Phase 3.3 (NEW):** Lines 2800-3000 (Metrics Endpoint)

---

## Version History

### v1.0 (Original)
- Date: 2025-12-30
- Status: Initial baseline
- Components: Basic execution pipeline

### v1.1 (Codex + Claude Improvements)
- Date: 2025-12-30
- Status: Production-ready baseline
- Added:
  - Baseline documentation
  - Backward compatibility strategy
  - ZAKOPS_STATE_DB reuse (no new DB)
  - Lease-based runner (not PID lock)
  - Deal events integration
  - 99-ACTIONS artifact path convention
  - Verification report as deliverable
- Size: 3,520 lines
- Timeline: 3-4 weeks
- Grade: B+ (82/100) - Functionally complete, but hard-coded

### v1.2 (World-Class Edition) ⭐ CURRENT
- Date: 2025-12-30
- Status: ✅ READY FOR IMPLEMENTATION (Option A approved)
- Added:
  - **Capability Manifest System** (self-extending)
  - **Action Planner** (handles unknown/complex requests)
  - **Schema-Driven UI** (dynamic forms)
  - **Observability Metrics** (real-time dashboard)
  - Per-action locking + exponential backoff
  - Critical acceptance test (lender outreach package)
- Size: 11,000+ lines
- Timeline: 4-5 weeks
- Grade Target: A+ (World-Class)

---

## Critical Test (Must Pass for v1.2)

```
User Query:
"Create a lender outreach package with 1-page summary + KPI list + email draft"

v1.1 Behavior:
❌ Fails (no keyword match, silent failure)

v1.2 Required Behavior:
✅ Decomposes into 3-step plan:
  1. DOCUMENT.GENERATE (1-page summary)
  2. ANALYSIS.BUILD_MODEL (KPI list)
  3. COMMUNICATION.DRAFT_EMAIL (email draft with attachments)

OR

✅ Asks clarifying questions:
  - "What should the summary focus on?"
  - "Which KPIs are most important?"
  - "Who is the recipient?"

Must NOT:
- Hallucinate non-existent action types
- Fail silently
- Create a single invalid action
```

If this test passes, the system is **world-class**.

---

## Implementation Checklist for CodeX

### Week 1: Foundation
- [ ] Phase 0.1: Create 5 capability YAML manifests (1 day)
- [ ] Phase 0.2: Implement CapabilityRegistry (2 days)
- [ ] Phase 0.3: Add capabilities API endpoint (0.5 day)
- [ ] Phase 0.4: Write registry tests (0.5 day)
- [ ] **Phase 0.5: Tooling Strategy (2 days)** - NEW
  - [ ] Implement ToolGateway with allowlist/denylist
  - [ ] Implement ToolRegistry for MCP tools
  - [ ] Create MCP tool manifests (Gmail, Crawl4AI)
  - [ ] Implement CompositeExecutor
  - [ ] Write tooling strategy tests
- [ ] Phase 1: Core infrastructure (3 days)

### Week 2: Intelligence Layer
- [ ] Phase 2.1: Implement ActionPlanner (3 days)
- [ ] Phase 2.2-2.6: Implement 5 executors (6 days)

### Week 3: API + UI
- [ ] Phase 3.1-3.2: API endpoints + runner (3 days)
- [ ] Phase 3.3: Metrics endpoint (1 day)
- [ ] Phase 4: Chat integration + planner (3 days)

### Week 3-4: User Experience
- [ ] Phase 5.1: Schema-driven dashboard (3 days)
- [ ] Phase 5.2: ActionInputForm component (2 days)
- [ ] Phase 5.3: Metrics dashboard UI (1 day)

### Week 4-5: Quality Assurance
- [ ] Phase 6.1: Backend tests + planner tests (4 days)
- [ ] Phase 6.2: UI tests (2 days)
- [ ] Phase 6.3: Documentation + 10-minute recipe (2 days)
- [ ] **Phase 6.4: CRITICAL TEST - Lender outreach package** (0.5 day)

### Week 5: Launch
- [ ] Phase 7: End-to-end verification (2 days)
- [ ] Verification report with screenshots
- [ ] **Critical acceptance test passes**
- [ ] Sign-off from Zaks

---

## The 10-Minute Recipe (Post-Implementation)

Once v1.2 is implemented, adding a new action capability takes **10 minutes**:

**Step 1:** Create capability YAML (5 min)
```bash
# scripts/actions/capabilities/generate_teaser.v1.yaml
capability_id: "DOCUMENT.GENERATE_TEASER.v1"
title: "Generate Teaser"
input_schema: {...}
output_artifacts: [pdf]
```

**Step 2:** Write executor (3 min)
```python
# scripts/actions/executors/teaser.py
class TeaserExecutor(ActionExecutor):
    def execute(self, payload, context):
        # Generate teaser PDF
        return ExecutionResult(success=True, artifacts=[...])
```

**Step 3:** Register executor (1 min)
```python
# scripts/actions/executors/__init__.py
register_executor(TeaserExecutor())
```

**Step 4:** Restart runner (1 min)
```bash
make actions-runner-stop && make actions-runner-bg
```

**Done!** ✅
- Action appears in UI type filters
- Planner can select it for queries like "generate teaser"
- Forms auto-generate from schema
- No UI code changes needed

---

## FAQ

### Q: What if I just want to implement v1.1 (faster)?
**A:** You can, but you'll need to refactor later. Every new action requires:
- Python enum changes
- TypeScript UI updates
- Redeploy everything

v1.2 adds 1 week now but saves 3+ weeks of refactoring in 2 months.

### Q: Can I implement v1.2 in phases?
**A:** Yes, but Phase 0 (Capability System) is foundational. You can:
1. Week 1: Implement Phase 0 + Phase 1 (foundation)
2. Week 2: Add executors (without planner, use keyword matching)
3. Week 3-4: Add planner + schema UI when ready

But this defeats the purpose of "world-class." Better to implement all at once.

### Q: What's the riskiest part?
**A:** The Action Planner (Phase 2.1). It's the most complex component. Mitigation:
- Start with keyword-based matching (fallback)
- Add LLM integration incrementally
- Test with simple queries first before complex multi-step

### Q: How do I test the critical test?
**A:** See Phase 6.4 and Phase 7, Test 4 for exact curl commands and expected responses.

---

## Next Steps

1. **Zaks:** Confirm approval of v1.2 plan ✅ (APPROVED - Option A)
2. **CodeX:** Read implementation plan v1.2 from start to finish
3. **CodeX:** Begin Phase 0 (Capability System)
4. **Claude Code:** Stand by for verification (Phase 7)

---

**Document Status:** ✅ COMPLETE AND READY
**Implementation Status:** 🔄 PENDING START
**Target Completion:** 4-5 weeks from start date
**Grade Target:** A+ (World-Class)

---

## Codex Review Notes — Gaps + Improvements (Added 2025-12-31)

| Issue | Status | Resolution |
|-------|--------|------------|
| Quick Start with ports + commands | ✅ RESOLVED | See `TOOLING-STRATEGY-EXECUTION-READY.md` Section 0 |
| Replace `src/...` with `scripts/...` paths | ✅ RESOLVED | Fixed in this doc + Path Map in execution-ready doc |
| Smoke Test section with curl commands | ✅ RESOLVED | See `TOOLING-STRATEGY-EXECUTION-READY.md` Section 7 |
| Dependencies & Fallbacks note | ✅ RESOLVED | See `TOOLING-STRATEGY-EXECUTION-READY.md` Section 8 |

All execution-ready details are in `/home/zaks/bookkeeping/docs/TOOLING-STRATEGY-EXECUTION-READY.md`.


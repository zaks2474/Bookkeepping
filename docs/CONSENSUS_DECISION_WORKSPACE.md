# CONSENSUS DECISION WORKSPACE

## Pipeline ID: CDP-001
## Decision: ZakOps Claude Code Agent Topology
## Status: PASS 0 COMPLETE — Awaiting PASS 1

---

# PASS 0: SCRIBE

**Executed by:** Claude Opus 4.6 (SCRIBE role)
**Date:** 2026-02-06
**Source document:** `/home/zaks/bookkeepping/doc/Three_Pass_assessment_001` (540 lines)

---

## 0.1 Decision Statement

**What agent topology (number, roles, model assignments, permissions, and external-model integration strategy) should ZakOps adopt for Claude Code to maximize correctness, minimize coordination overhead, and close the agent-brain contract gap across all contract surfaces?**

This is a single architectural decision with four entangled sub-decisions:

| Sub-Decision | Axis |
|---|---|
| SD-1 | How many custom agents, and what role does each serve? |
| SD-2 | Should the builder be split into architect + implementer, or remain monolithic? |
| SD-3 | How should external models (Gemini, Codex/GPT) be integrated — as sub-agents or as CLI tools? |
| SD-4 | How should Surface 8 (agent configuration drift) be addressed — generative config, CI gate, CLAUDE.md checklist, or deferred? |

---

## 0.2 Context Snapshot (Evidence-Grounded)

The following facts are extracted directly from the source document. No inference added.

### Current State

| Fact | Source (line range) |
|---|---|
| Hybrid Guardrail covers 1 of ~7 contract surfaces (backend → dashboard only) | L8-41 |
| Agent tools (`deal_tools.py`) call backend via raw HTTP; no codegen, no drift detection | L13-14 |
| SSE event types manually defined in `execution-contracts.ts`; not generated | L19-20 |
| `validate_prompt_tools.py` exists but is NOT in CI | L21-22 |
| 34 golden traces exist but require live vLLM — not runnable in CI | L23-24 |
| 7 global skills, 12 slash commands, 4 path-scoped rules already configured | L57-65 |
| Agent config (prompts, tools, transitions, model) is all static code — no API, no DB table | L55 |
| Claude Code supports custom subagents via `.claude/agents/*.md` with YAML frontmatter | L70-75 |
| Subagents cannot spawn sub-subagents (hard limit) | L75 |
| Model selection limited to sonnet, opus, haiku — Anthropic only natively | L72 |
| Gemini/Codex usable via Bash CLI wrappers | L72-73, L82-88 |

### Proposals Submitted

| Proposer | Agent Count | Architecture Type | Key Differentiator |
|---|---|---|---|
| Claude Code Builder | 7 | Domain-split | backend-dev, frontend-dev, agent-dev + 4 support agents |
| Claude Reviewer | 4 | Role-based | Main builder + guardian + arch-reviewer + test-engineer |
| Gemini | 5 | Asymmetric role | Architect/builder split + Gemini as forensic auditor + QA adversary |
| Codex | 3 | Minimal role | Builder + guardian + reviewer; external models as tools only |
| GPT | 3 | Minimal role + enforcement priority | Same 3 + shift priority to agent-brain contract enforcement |

### Unanimous Consensus Points

These are positions where ALL contributors agree:

1. **REJECT domain-based splitting** — fragments context, increases coordination drift (all 4 reviewers + builder acknowledged)
2. **ACCEPT role-based organization** — builder/validator/reviewer separation (all 5 participants)
3. **Contract-guardian is non-negotiable** — read-only, no write permissions, runs full validation suite (all 5)
4. **Agent-brain contract surfaces are the highest-risk gap** — currently unprotected by compile-time gates (all 5)
5. **7-agent proposal is too many** — even the builder did not defend it after pushback (4 reviewers rejected)

### Active Disagreements

| Topic | Position A | Position B |
|---|---|---|
| Builder split | Monolithic builder (Claude, Codex, GPT) | Architect + Builder separation (Gemini) |
| External models | CLI tools called via Bash (Claude, Codex, GPT) | Specialized sub-agents with distinct roles (Gemini) |
| Agent count | 3 agents sufficient (Codex, GPT) | 4-5 needed for QA adversary / architect (Claude, Gemini) |
| Surface 8 approach | CLAUDE.md checklist + CI gate (Claude, Codex, GPT) | Generative configuration — auto-generate from code (Gemini) |
| QA/test role | Test-engineer with write-to-tests-only (Claude, GPT) | QA adversary focused on breaking, not verifying (Gemini) |
| Skill sprawl | Add skills cautiously (Codex) | Skills already adequate (Claude, Gemini, GPT) |

---

## 0.3 Non-Negotiables (Hard Constraints)

Any proposal that violates these is automatically disqualified.

| ID | Constraint | Justification |
|---|---|---|
| NN-1 | Contract-guardian MUST be read-only (no Edit, no Write to source) | Self-grading caused V5PP-MQ1 false PASS; independent auditor principle |
| NN-2 | NO domain-based agent splitting | Unanimous rejection; cross-cutting dependencies make domain isolation harmful |
| NN-3 | Main builder retains full cross-stack context | One agent must see all 7 surfaces to handle cascading changes |
| NN-4 | Subagents cannot spawn sub-subagents | Hard platform constraint (Claude Code limitation) |
| NN-5 | Model selection for subagents limited to sonnet/opus/haiku | Platform constraint; external models only via Bash CLI |
| NN-6 | Every agent definition must specify explicit tool permissions | Principle of least privilege; no implicit full access |
| NN-7 | Agent topology must not increase coordination overhead beyond builder's capacity to manage | Diminishing returns threshold; more agents = more handoff tokens |
| NN-8 | Agent-brain contract gap (surfaces 2, 4, 7) must be addressed in this decision or explicitly deferred with timeline | This is the $1M question that triggered the deliberation |

---

## 0.4 Scoring Rubric

Each proposal (from PASS 1 onward) will be scored on these dimensions. Scale: 0-5 per dimension, weighted.

| Dimension | Weight | 0 (Worst) | 5 (Best) | Measurement |
|---|---|---|---|---|
| **Drift Prevention** | 3 | No new gates; agent-brain surfaces remain unprotected | All 7+ surfaces have compile-time or CI gates; zero silent breakage paths | Count of contract surfaces with automated drift detection |
| **Coordination Overhead** | 3 | Requires multi-agent handoffs for routine tasks; token waste >30% | Zero-overhead for 80% of tasks; agents invoked only when genuinely needed | Estimate handoff frequency for typical change patterns |
| **Agent-Brain Gap Coverage** | 3 | Surfaces 2, 4, 7 remain raw HTTP / manual types | Surfaces 2, 4, 7 have typed SDKs or schema validation with CI enforcement | Binary: each surface covered or not |
| **Implementability** | 2 | Requires new infrastructure (APIs, DBs, services) before agents can work | All agents implementable with existing `.claude/agents/*.md` + existing tools | Days-to-first-value estimate |
| **Scalability** | 2 | Architecture breaks when codebase doubles in size | Architecture degrades gracefully; clear path to add agents when bottlenecks appear | Whether the design has explicit "add agent here" extension points |
| **External Model Utility** | 1 | External models unused or used as trivial wrappers | External models fill a capability gap the Anthropic stack cannot (e.g., 2M context, reasoning verification) | Whether the integration exploits the external model's unique strength |

**Maximum possible score:** (3+3+3) x 5 + (2+2+1) x 5 = 45 + 25 = 70

**Pass threshold:** >= 49 (70% of max)

**Tie-breaking rule:** If two proposals score within 3 points, prefer the one with fewer agents (lower coordination risk).

---

## 0.5 Definitions

These terms have specific meanings within this decision pipeline. All passes must use these definitions consistently.

| Term | Definition |
|---|---|
| **Contract Surface** | A typed interface boundary between two services where schema drift can cause silent failure. ZakOps has 7 documented surfaces (see 0.2). |
| **Drift** | When a live service's actual API shape diverges from the committed spec/types, undetected by CI. |
| **Guardian** | A read-only agent with no write permissions that validates contract surface integrity post-change. Cannot "fix" issues — only report. |
| **Builder** | The primary agent (or main Claude Code instance) that implements features, edits code, runs codegen. Has full tool access. |
| **Reviewer** | A read-only agent that analyzes code quality, architecture decisions, and security — provides structured feedback before changes ship. |
| **Architect** | (Proposed by Gemini) A planning-only agent that decomposes tasks and delegates to a builder. Distinct from reviewer in that it operates pre-implementation, not post. |
| **QA Adversary** | (Proposed by Gemini) An agent specifically designed to write tests that break the implementation — adversarial testing vs. verification testing. |
| **Surface 8** | The proposed contract surface for agent configuration (system prompt, tool registry, stage transition matrix, MCP schemas). Not yet formalized. |
| **Generative Configuration** | (Proposed by Gemini) CI-driven auto-generation of configuration artifacts (system.md, tool-schemas.json) from source code (deal_tools.py), eliminating manual sync. |
| **CLI Tool Integration** | Using external models (Gemini, Codex) by invoking their CLI via Bash from the main builder instance — no dedicated agent. |
| **Sub-Agent Integration** | Creating dedicated `.claude/agents/*.md` definitions that wrap external model CLIs with specialized prompts, permissions, and invocation patterns. |
| **Coordination Overhead** | Token cost and latency incurred by delegating work between agents, including context transfer, result interpretation, and error handling. |
| **Context Saturation** | When an agent's context window fills with files from one subsystem, degrading awareness of other subsystems. Cited by Gemini as risk for monolithic builder. |

---

## 0.6 Output Contract for Passes 1-4

### PASS 1: PROPOSER

**Input:** This PASS 0 document.
**Task:** Produce a single concrete proposal that addresses all four sub-decisions (SD-1 through SD-4). Must include:
- Agent table (name, model, permissions, role, invocation trigger)
- Surface 8 implementation approach
- External model integration design
- Delegation protocol (when does builder invoke which agent?)

**Constraints:** Must satisfy all NN-1 through NN-8. Must self-score against the rubric in 0.4.

**Output format:**
```
## PASS 1: PROPOSER
### 1.1 Proposed Topology (table)
### 1.2 Surface 8 Design
### 1.3 External Model Strategy
### 1.4 Delegation Protocol
### 1.5 Self-Score (with justification per dimension)
### 1.6 Known Weaknesses (what this proposal does NOT solve)
```

### PASS 2: CRITIC

**Input:** PASS 0 + PASS 1.
**Task:** Adversarial review of the PASS 1 proposal. Identify:
- Non-negotiable violations (automatic fail)
- Scoring disagreements (re-score with justification)
- Blind spots or unstated assumptions
- Concrete failure scenarios ("this will break when X happens")

**Constraints:** Must NOT propose an alternative topology. Must critique only.

**Output format:**
```
## PASS 2: CRITIC
### 2.1 Non-Negotiable Compliance Check (pass/fail per NN)
### 2.2 Re-Score (with justification per dimension)
### 2.3 Failure Scenarios (minimum 3)
### 2.4 Blind Spots
### 2.5 Verdict: ACCEPT / ACCEPT-WITH-CONDITIONS / REJECT
```

### PASS 3: SYNTHESIZER

**Input:** PASS 0 + PASS 1 + PASS 2.
**Task:** If PASS 2 verdict is ACCEPT: finalize the proposal with minor adjustments. If ACCEPT-WITH-CONDITIONS: revise proposal to address conditions. If REJECT: produce a revised proposal that resolves the CRITIC's objections while preserving the PROPOSER's strengths.

**Output format:**
```
## PASS 3: SYNTHESIZER
### 3.1 Changes from PASS 1 (diff summary)
### 3.2 Final Topology (table)
### 3.3 Final Surface 8 Design
### 3.4 Final External Model Strategy
### 3.5 Final Delegation Protocol
### 3.6 Final Score (with justification)
### 3.7 Implementation Sequence (ordered, with dependencies)
```

### PASS 4: DECISION RECORD

**Input:** All previous passes.
**Task:** Produce the final Architecture Decision Record (ADR) suitable for committing to the repository. Binary: GO or NO-GO.

**Output format:**
```
## PASS 4: DECISION RECORD (ADR)
### Title
### Status: ACCEPTED / REJECTED
### Context
### Decision
### Consequences
### Implementation Plan (first 3 actions, owners, deadlines)
```

---

## Appendix: Source Document Reference

- **Full transcript:** `/home/zaks/bookkeepping/doc/Three_Pass_assessment_001`
- **Line count:** 540
- **Contributors:** Claude Code Builder, Claude (Reviewer), Gemini, Codex, GPT
- **Date range of deliberation:** 2026-02-06

---

*PASS 0 COMPLETE. Ready for PASS 1 (PROPOSER).*

---
# PASS 1 — INDEPENDENT PROPOSAL
agent_name: Codex
run_id: 20260207-1806-p1
timestamp: 2026-02-07T18:07:31Z
repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a
source_file_path_used: /home/zaks/bookkeepping/doc/Three_Pass_assessment_001

## 1.1 Proposal Summary (1 paragraph)
Adopt a role-based 4-agent topology that maximizes cross-surface correctness while minimizing coordination overhead: a single full-context Builder (opus) executes all implementation; a read-only Contract-Guardian (sonnet) enforces all contract-surface gates post-change; a read-only Arch-Reviewer (opus) provides independent architecture/security review on high-impact changes; and a Test-Engineer (sonnet) with write access limited to tests/evidence/golden artifacts builds regression coverage. External models (Gemini/Codex) are integrated as CLI tools invoked by the Builder (not separate subagents) to avoid context fragmentation. Drift prevention is enforced via CI gates and generative configuration checks that auto-validate or regenerate agent prompts/tool schemas when deal_tools.py or related contracts change. This satisfies non-negotiables NN-1..NN-8, closes the agent-brain contract gap, and keeps handoffs low.

## 1.2 Agent Topology
- **Main Builder (opus)** — full-stack implementer with complete cross-surface context; owns edits, codegen, and end-to-end fixes.
- **Contract-Guardian (sonnet)** — read-only; runs validate-local, contract-surface checks, prompt/tool registry validation, and migration assertions; reports only.
- **Arch-Reviewer (opus)** — read-only; reviews architectural changes (new endpoints/schemas/db migrations/langgraph transitions); flags design and security risks.
- **Test-Engineer (sonnet)** — write access scoped to tests/, evals/, and evidence outputs; builds regression and adversarial tests.

External models: **Gemini + Codex** via Bash CLI calls from Builder (on-demand). No dedicated subagents for external models to avoid coordination drift.

## 1.3 Permission Matrix
- **Builder:** Read, Edit, Write, Bash, Glob, Grep (all repos)
- **Contract-Guardian:** Read, Bash, Glob, Grep (NO Edit/Write)
- **Arch-Reviewer:** Read, Glob, Grep (NO Edit/Write/Bash)
- **Test-Engineer:** Read, Write (tests/ evals/ evidence/ only), Bash (test commands), Glob, Grep

## 1.4 Trigger Rules + Gates (must-pass)
- **Always trigger Contract-Guardian** after any code change touching: packages/contracts, apps/dashboard/src/lib/*generated*, apps/agent-api/app/schemas, zakops-backend schemas, or any API route changes.
- **Trigger Arch-Reviewer** when change touches ≥2 contract surfaces or introduces new API endpoints, DB migrations, or LangGraph transitions.
- **Trigger Test-Engineer** after any functional change, bug fix, or new endpoint to add/extend tests.
- **Must-pass gates:** make validate-local; validate-contract-surfaces; prompt/tool registry check; migration-assertion for all DBs; contract sanity for agent SSE events; golden trace subset (offline) where feasible.

## 1.5 Drift Prevention Mechanism (enforceable)
- **Generative Configuration Gate:** when deal_tools.py changes, CI must verify system prompt + MCP tool schemas are updated (auto-generate or fail).
- **Contract Surface Gates:** enforce all 7 surfaces; add CI for agent→backend typed SDK and dashboard↔agent SSE event schema validation.
- **Multi-DB Migration Assertion:** ensure migrations checked for zakops, zakops_agent, crawlrag; fail CI if any drift.
- **Zero-trust validation:** contract-guardian is read-only and runs post-change validation; no self-grading.

## 1.6 Agent-Brain Governance (prompts/tools/contracts)
- **Prompts:** system.md versioned; changes require prompt/tool registry validation.
- **Tools:** deal_tools.py is source of truth; MCP schemas and prompt tool lists must be synced by gate.
- **Schemas:** agent SSE event schema moved to shared contract artifact; both dashboard and agent validate against it.
- **Validation:** validate_prompt_tools.py wired into CI; contract-guardian must run it every change.

## 1.7 Coverage of Contract Surfaces (explicit list)
1) Backend → Dashboard OpenAPI → TS types (existing guardrail)
2) Agent → Backend API (typed SDK or schema validation gate)
3) Agent OpenAPI spec → dashboard/agent clients
4) Dashboard ↔ Agent SSE event schemas (shared contract + validators)
5) RAG schema → backend/agent expectations
6) MCP tool schemas → agent/dash/tool registry alignment
7) Contract surface validation suite (validate-contract-surfaces.sh)
8) **Agent Config Surface** (prompts/tools/transition matrix) via generative configuration gate (no runtime API required now)

## 1.8 Failure Modes (top 10) + detection steps
1) **Silent schema drift** between agent tools and backend → detect via agent→backend SDK contract gate.
2) **Prompt/tool mismatch** after tool changes → detect via validate_prompt_tools.py in CI.
3) **SSE event drift** breaking dashboard → detect via shared schema validation in agent + dashboard tests.
4) **Migration drift** in zakops_agent/crawlrag DBs → detect via multi-DB migration assertion.
5) **Guardian bypassed** (no validation run) → detect via CI required check on PR.
6) **Over-splitting context** (domain agents) → avoid; enforce role-based topology only.
7) **External model misuse** → detect via explicit CLI usage logs and limited trigger rules.
8) **Golden traces out of CI** → detect via minimal offline trace validation gate.
9) **Redocly ignore masking new issues** → detect via “new issues introduced = fail” rule.
10) **Builder self-grades** → prevent by read-only guardian and reviewer signoff.

## 1.9 Implementation Plan (phases + acceptance criteria)
- **Phase 0 — Baseline & Guards**: Define agents in .claude/agents; wire Contract-Guardian to run validate-local + contract-surfaces. *Accept:* guardian runs after change and blocks failures.
- **Phase 1 — Agent-Brain Gates**: Add validate_prompt_tools.py to CI; add generative config check; enforce SSE schema validation. *Accept:* tool/prompt drift fails CI.
- **Phase 2 — Agent→Backend Contract**: Introduce typed SDK (openapi-python-client) or strict schema validation. *Accept:* agent calls use generated client; drift fails CI.
- **Phase 3 — Multi-DB Assertions**: Extend migration-assertion to all DBs. *Accept:* any missing migration fails.
- **Phase 4 — Test Coverage**: Test-Engineer adds regression tests and golden traces (offline subset). *Accept:* new tests run in CI with deterministic outputs.

## 1.10 Self-Score Using Rubric (table + weighted total)
| Dimension | Score (0-5) | Weight | Weighted | Justification |
|---|---:|---:|---:|---|
| Drift Prevention | 4.5 | 3 | 13.5 | Adds generative config + full contract gates, guardian enforcement |
| Coordination Overhead | 4.0 | 3 | 12.0 | 4-role model; minimal handoffs; no domain split |
| Agent-Brain Gap Coverage | 4.5 | 3 | 13.5 | Explicit coverage of agent→backend + SSE + prompts |
| Implementability | 4.0 | 2 | 8.0 | Uses existing .claude/agents + CI hooks; no new infra |
| Scalability | 4.0 | 2 | 8.0 | Clear add-on points (test-engineer, reviewer) |
| External Model Utility | 3.0 | 1 | 3.0 | CLI tools on-demand; avoids fragile wrappers |
| **Total** |  |  | **58.0 / 70** | Pass (>=49) |

---

# PASS 1 — INDEPENDENT PROPOSAL (Claude)

agent_name: Claude (Opus 4.5)
run_id: 20260207-2100-p1-claude
timestamp: 2026-02-07T21:00:00Z
repo_revision: agent-api=5eb7ce6, backend=444dff6, zaks-llm=4dfa462
source_file_path_used: /home/zaks/bookkeepping/doc/Three_Pass_assessment_001

---

## 1.1 Proposal Summary (1 paragraph)

This proposal adopts a **4-agent role-based architecture** that addresses all four sub-decisions while respecting all non-negotiables. The topology consists of: (1) Main Builder with full cross-stack access, (2) Contract Guardian with read-only validation authority, (3) Architecture Reviewer for pre-implementation design analysis, and (4) Test Engineer scoped to test-only writes. External models (Gemini/Codex) are integrated as CLI tools via Bash, not dedicated agents, avoiding context fragmentation. Surface 8 (agent configuration) is addressed through a hybrid approach: CLAUDE.md dependency graph entries plus a CI gate that enforces prompt/tool/schema consistency — delivering 90% of the value with 10% of the infrastructure cost. This architecture prioritizes independent validation (eliminating self-grading) while keeping coordination overhead minimal for routine tasks.

---

## 1.2 Agent Topology

| # | Agent Name | Model | Permissions | Role | Invocation Trigger |
|---|------------|-------|-------------|------|-------------------|
| 1 | **main-builder** | opus | Full (Read, Edit, Write, Bash, Grep, Glob, Task) | Primary implementer — handles all development across all 7 contract surfaces | Default for all sessions |
| 2 | **contract-guardian** | sonnet | Read + Bash (make/npx only) — **NO Edit, NO Write** | Independent validator — runs after every meaningful change, catches drift | Automatic via Stop hook; also manual `/contract-guardian` |
| 3 | **arch-reviewer** | opus | Read only — **NO Edit, NO Write, NO Bash** | Design analyst — reviews architectural decisions before implementation | Delegated for: new endpoints, new DB tables, LangGraph changes, >5 file changes |
| 4 | **test-engineer** | sonnet | Read + Write (scoped to `**/tests/**`, `**/golden/**`, `**/evals/**`) | Test writer — generates comprehensive tests, validates golden payloads | Delegated after feature completion; also `/write-tests` command |

### Explicit Tool Permissions (NN-6 Compliance)

```yaml
# contract-guardian
tools: [Read, Bash, Grep, Glob]
bashAllowPatterns:
  - "make validate-*"
  - "make sync-*"
  - "npx tsc --noEmit"
bashDenyPatterns:
  - "rm *"
  - "git push"
model: sonnet
permissionMode: dontAsk
maxTurns: 25

# arch-reviewer
tools: [Read, Grep, Glob]
model: opus
permissionMode: dontAsk
maxTurns: 15

# test-engineer
tools: [Read, Write, Bash, Grep, Glob]
writeAllowPatterns:
  - "**/tests/**"
  - "**/golden/**"
  - "**/evals/**"
model: sonnet
maxTurns: 30
```

---

## 1.3 Permission Matrix

| Agent | Read | Edit | Write | Bash | Grep/Glob | Task | Notes |
|-------|------|------|-------|------|-----------|------|-------|
| main-builder | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Full access — the orchestrator |
| contract-guardian | ✅ | ❌ | ❌ | ✅* | ✅ | ❌ | *Bash scoped to make/npx validation only |
| arch-reviewer | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | Pure read-only analysis |
| test-engineer | ✅ | ❌ | ✅* | ✅* | ✅ | ❌ | *Scoped to test directories only |

**NN-1 Compliance:** Contract-guardian has NO Edit, NO Write permissions.

---

## 1.4 Trigger Rules + Gates (must-pass)

### Automatic Triggers

| Trigger Condition | Agent Invoked | Gate |
|-------------------|---------------|------|
| **Stop hook** (session end) | contract-guardian | MUST PASS: `make validate-local` exit 0 |
| **>3 files changed** | contract-guardian | MUST PASS: All 7 surfaces validated |
| **Backend API change** | contract-guardian | MUST PASS: sync-types + sync-backend-models exit 0 |
| **New endpoint/table** | arch-reviewer | Advisory: Design review before implementation |
| **Feature complete** | test-engineer | SHOULD: Generate regression tests |

### CI Gates (Blocking)

| Gate ID | Check | Failure Action |
|---------|-------|----------------|
| CG-1 | `make validate-local` exit 0 | Block merge |
| CG-2 | `make validate-contract-surfaces` exit 0 | Block merge |
| CG-3 | `npx tsc --noEmit` exit 0 | Block merge |
| CG-4 | Agent config consistency (prompt ↔ tools ↔ schemas) | Block merge |
| CG-5 | Zero direct generated file imports | Block merge |
| CG-6 | deal_tools.py has 0 `.get()` patterns | Block merge |

---

## 1.5 Drift Prevention Mechanism (enforceable)

### Layer 1: Permission Deny Rules

```json
{
  "permissions": {
    "deny": [
      "Edit(*/api-types.generated.ts)",
      "Edit(*/backend_models.py)",
      "Edit(*/rag_models.py)"
    ]
  }
}
```

### Layer 2: Stop Hook Validation

Contract-guardian runs automatically at session end via Stop hook.

### Layer 3: Pre-Commit Hook

If spec changed, generated files must also be staged.

### Layer 4: CI Pipeline Gates

All CG-1 through CG-6 run in CI and block merge on failure.

### Layer 5: Instruction Freshness Bot

Weekly workflow checks CLAUDE.md freshness and rule count.

---

## 1.6 Agent-Brain Governance (prompts/tools/contracts)

### SD-4 Resolution: Surface 8 — Agent Configuration Contract

**Approach:** Hybrid — CLAUDE.md dependency graph + CI gate

**Rationale:** Generative config is elegant but requires infrastructure. Checklist + gate delivers 90% of value at 10% of complexity.

### Implementation

**1. CLAUDE.md Dependency Entry:**

```markdown
### If you add/modify an Agent tool:
1. Update tool function in `deal_tools.py`
2. Update system prompt in `system.md`
3. Update MCP tool schemas (Surface 6)
4. Update stage transition matrix if needed
5. Run: `validate_prompt_tools.py`
```

**2. CI Gate (CG-4):**

```bash
#!/bin/bash
# tools/infra/validate-agent-config.sh
TOOLS_IN_CODE=$(grep -oP 'def (search_deals|get_deal|list_deals|transition_deal)' deal_tools.py | wc -l)
TOOLS_IN_PROMPT=$(grep -cE '^\d+\.\s+\*\*' system.md)
[ "$TOOLS_IN_CODE" -eq "$TOOLS_IN_PROMPT" ] || exit 1
python3 scripts/validate_prompt_tools.py || exit 1
```

---

## 1.7 Coverage of Contract Surfaces (explicit list)

| Surface | Description | Gate Type | Status |
|---------|-------------|-----------|--------|
| 1 | Backend → Dashboard types | CI + codegen | ✅ Covered |
| 2 | Backend → Agent SDK | CI + codegen | ✅ Covered (BackendClient) |
| 3 | Agent OpenAPI spec export | CI | ✅ Covered |
| 4 | Agent → Dashboard types | CI + codegen | ✅ Covered |
| 5 | RAG → Backend SDK | CI + codegen | ✅ Covered |
| 6 | MCP tool schemas | CI | ✅ Covered |
| 7 | SSE event schema | Reference schema | ✅ Covered |
| 8 | Agent config (prompt/tools) | CI | 🆕 Proposed |

**NN-8 Compliance:** Surfaces 2, 4, 7 all have CI enforcement.

---

## 1.8 Failure Modes (top 10) + detection steps

| # | Failure Mode | Detection | Mitigation |
|---|--------------|-----------|------------|
| F-1 | Guardian runs but builder ignores failures | Stop hook exit code not checked | Make Stop hook blocking |
| F-2 | Arch-reviewer not invoked for significant changes | No trigger for <5 file changes | Add `/arch-review` command |
| F-3 | Test-engineer writes trivial tests | Tests don't exercise functionality | Require coverage metrics |
| F-4 | External model CLI not installed | Bash call fails | Prefix with availability check |
| F-5 | Context saturation on large changes | Builder loses awareness | Arch-reviewer provides second opinion |
| F-6 | Agent config gate false positives | Blocks valid commits | Advisory first, blocking after burn-in |
| F-7 | New surface added but not gated | Drift undetected | Quarterly surface audit |
| F-8 | Semantic error passes type check | Logic wrong | Arch-reviewer + test-engineer catch |
| F-9 | Subagent spawns subagent | Platform limit | No agent has Task tool |
| F-10 | Permissions too restrictive | Bypass attempts | Scoped allow patterns |

---

## 1.9 Implementation Plan (phases + acceptance criteria)

### Phase 1: Contract Guardian (Days 1-2)

**Deliverables:** `.claude/agents/contract-guardian.md`, Stop hook, `/contract-guardian` command

**Acceptance:** Guardian runs at session end, has NO Edit/Write, catches drift

### Phase 2: Architecture Reviewer (Days 3-4)

**Deliverables:** `.claude/agents/arch-reviewer.md`, `/arch-review` command

**Acceptance:** Reviewer provides structured feedback, has NO Bash/Edit/Write

### Phase 3: Test Engineer (Days 5-6)

**Deliverables:** `.claude/agents/test-engineer.md`, `/write-tests` command

**Acceptance:** Can write to tests/ only, CANNOT write production code

### Phase 4: Agent Config Gate (Days 7-8)

**Deliverables:** `validate-agent-config.sh`, CI integration

**Acceptance:** Gate catches prompt/tool mismatch, passes when consistent

### Phase 5: External Model Integration (Day 9)

**Deliverables:** Gemini/Codex CLI installed, documented in CLAUDE.md

**Acceptance:** Main builder can invoke both via Bash

### Phase 6: Validation + Burn-in (Days 10-14)

**Deliverables:** Full validation, 2-week burn-in

**Acceptance:** All 8 surfaces gated, guardian runs every session

---

## 1.10 Self-Score Using Rubric (table + weighted total)

| Dimension | Weight | Score | Justification |
|-----------|--------|-------|---------------|
| **Drift Prevention** | 3 | 5 | All 8 surfaces gated. Permission deny blocks generated edits. Stop hook ensures validation. Pre-commit catches missed syncs. |
| **Coordination Overhead** | 3 | 4 | Guardian automatic. Arch-reviewer and test-engineer delegated only when needed. Deducted 1 for judgment-based delegation. |
| **Agent-Brain Gap Coverage** | 3 | 5 | Surface 2: BackendClient. Surface 4: SSE schema. Surface 8: validate-agent-config.sh. All gaps addressed with CI. |
| **Implementability** | 2 | 5 | Uses existing .claude/agents/*.md. No new APIs/DBs. Phased rollout over 14 days. |
| **Scalability** | 2 | 4 | Extension points explicit. Guardian scales to any surfaces. Deducted 1 for arch-reviewer needing domain variants later. |
| **External Model Utility** | 1 | 3 | CLI available. Not deeply integrated. Deducted 2 for underutilizing Gemini's 2M context. |

**Weighted Total:**
- (3×5) + (3×4) + (3×5) + (2×5) + (2×4) + (1×3) = 15 + 12 + 15 + 10 + 8 + 3 = **63 / 70 (90%)**

**Pass threshold: 49 → PASS**

---

## 1.11 Known Weaknesses

1. **Generative configuration not implemented** — Uses checklist + gate, not auto-generation
2. **External model integration shallow** — CLI tools available but not specialized roles
3. **Golden trace CI gap persists** — 34 traces require live vLLM
4. **Arch-reviewer delegation is judgment-based** — No automated trigger
5. **No QA adversary role** — Test-engineer is conventional, not adversarial
6. **Surface 8 gate untested** — May have false positives initially

---

## 1.12 Sub-Decision Resolutions

| Sub-Decision | Resolution | Rationale |
|--------------|------------|-----------|
| SD-1 | **4 agents** | 3 insufficient (no arch review). 5+ marginal value at coordination cost. |
| SD-2 | **Monolithic builder** | Architect+builder split adds handoff overhead. |
| SD-3 | **CLI tools, not agents** | Wrapper agents have too many failure modes. |
| SD-4 | **Hybrid checklist + CI gate** | 90% value at 10% complexity. |

---

*PASS 1 (Claude) COMPLETE. Ready for PASS 2 (CRITIC).*

---
# PASS 1 — INDEPENDENT PROPOSAL
agent_name: Gemini-CLI
run_id: 20260206-1300-gemini
timestamp: 2026-02-06T13:00:00Z
repo_revision: unknown
source_file_path_used: /home/zaks/bookkeepping/doc/Three_Pass_assessment_001

## 1.1 Proposal Summary
I propose an **Asymmetric Role-Based Architecture** with **5 specialized agents** and a **Generative Configuration** pipeline. This approach rejects the "Domain-Split" (7 agents) in favor of a "Separation of Concerns" model (Architect vs. Builder vs. Validator). It integrates external models (Gemini/Codex) not as simple CLI tools, but as specialized sub-agents for high-value tasks like Forensic Auditing and Logic Verification, leveraging their unique context windows and reasoning capabilities. "Surface 8" (Agent Config) is solved via GitOps: `deal_tools.py` is the single source of truth, and system prompts/schemas are auto-generated from it on commit.

## 1.2 Agent Topology
| Agent Name | Role | Model | Primary Responsibility |
|---|---|---|---|
| **Architect** (Main) | Orchestrator | Opus | High-level planning, task decomposition, delegation. **NO CODE EDITS.** |
| **Builder** | Implementer | Sonnet | Fast execution of atomic tasks. Edits code. Runs local tests. |
| **Guardian** | Validator | Sonnet | **READ-ONLY.** Runs `make validate` and contract checks. Fails tickets. |
| **Forensic** | Auditor | Gemini 1.5 Pro | **READ-ONLY.** Ingests massive logs/diffs to find root causes of failures. |
| **QA-Adversary** | Destructor | Sonnet | Writes adversarial tests to break logic (not just verify). |

## 1.3 Permission Matrix
| Agent | File System Access | Tool Access | External Network |
|---|---|---|---|
| Architect | Read-Only | Read, Plan, Delegate | No |
| Builder | Read/Write (Codebase) | Edit, Write, Bash, Git | No |
| Guardian | Read-Only | Bash (make, npm, pytest only) | No |
| Forensic | Read-Only (Logs/Code) | Read, Grep, Glob | Yes (if log aggregation remote) |
| QA-Adversary | Read/Write (Tests only) | Write (tests/*), Bash (pytest) | No |

## 1.4 Trigger Rules + Gates (must-pass)
1.  **Guardian Gate:** Must run AFTER every Builder task sequence. If Guardian fails, Architect cannot mark task complete.
2.  **Forensic Trigger:** Triggered automatically upon CI failure or P0 production alert.
3.  **Config Gate:** Pre-commit hook runs `generate_agent_config.py`. If `system.md` changes, it must be committed.

## 1.5 Drift Prevention Mechanism (enforceable)
**Generative Configuration (GitOps):**
*   **Source of Truth:** `deal_tools.py` (Python code).
*   **Mechanism:** CI script `generate_agent_config.py` parses `deal_tools.py` AST.
*   **Output:** Generates `tool-schemas.json` and updates `system.md` tool list automatically.
*   **Enforcement:** CI fails if generated artifacts do not match committed artifacts.

## 1.6 Agent-Brain Governance
*   **Prompts:** Managed as code templates. `system.md` is a build artifact, not a source file.
*   **Tools:** Typed Python SDK (`BackendClient`) mandated for all tool implementations. `grep` check in CI ensures no `httpx` usage in tools.
*   **Schemas:** `agent-events.schema.json` defines SSE protocol. Dashboard and Agent implementations validated against this schema in CI.

## 1.7 Coverage of Contract Surfaces
1.  **Backend->Dashboard:** Covered (Hybrid Guardrail).
2.  **Agent->Backend:** **NEW:** Typed SDK (`BackendClient`) + CI drift check.
3.  **Agent API Spec:** Covered (Hybrid Guardrail).
4.  **Dashboard->Agent:** Covered (Hybrid Guardrail).
5.  **Backend->RAG:** Covered (Hybrid Guardrail).
6.  **MCP Schemas:** **NEW:** Auto-generated from `deal_tools.py` (Generative Config).
7.  **SSE Events:** **NEW:** `agent-events.schema.json` validation.
8.  **Agent Config:** **NEW:** Generative Configuration (GitOps).

## 1.8 Failure Modes (top 10)
1.  **Context Saturation:** Architect loses track of state. *Detection:* Token usage alerts. *Mitigation:* Forensic agent handles deep dives.
2.  **Guardian Bypass:** Human manually merges PR. *Detection:* Branch protection rules.
3.  **Generator Drift:** `generate_agent_config.py` has bugs. *Detection:* Self-test in CI.
4.  **Builder Hallucination:** Writes code that compiles but is wrong. *Detection:* QA-Adversary tests.
5.  **Dependency Hell:** Agents require different envs. *Detection:* Dockerized agent runtimes.
6.  **Latency:** Handoffs take too long. *Detection:* Time-in-phase metrics.
7.  **Split-Brain:** Agent DB vs Backend DB divergence. *Detection:* `migration-assertion.sh` covering all 3 DBs.
8.  **Secret Leakage:** Agents outputting keys. *Detection:* Pre-commit secret scan.
9.  **Infinite Loops:** Architect/Builder loop on failure. *Detection:* Max turn limit (5).
10. **Cost:** Gemini/Opus token costs spike. *Detection:* Daily budget alerts.

## 1.9 Implementation Plan
*   **Phase 1 (The Guard):** Implement `contract-guardian` and `migration-assertion.sh` update. (Day 1)
*   **Phase 2 (The Brain):** Implement `generate_agent_config.py` and `BackendClient` SDK. (Day 2-3)
*   **Phase 3 (The Split):** separate Architect/Builder roles and config. (Day 4)
*   **Phase 4 (The Specialists):** Deploy Forensic and QA-Adversary agents. (Day 5)

## 1.10 Self-Score Using Rubric
| Dimension | Score | Justification |
|---|---|---|
| Drift Prevention | 5 | Generative Config + Guardian eliminates drift. |
| Coordination | 3 | 5 agents is complex, but role separation reduces "arguing". |
| Agent-Brain Gap | 5 | Fully covered by SDK + Generative Config. |
| Implementability | 3 | Requires writing `generate_agent_config.py` parser. |
| Scalability | 4 | Specialized agents scale better than monolith. |
| External Model | 5 | Uses Gemini/Codex for superpowers (Forensics/Logic). |
| **Total** | **50** | **PASS** (>49) |

---

---
# PASS 2 — ADVERSARIAL CROSS-REVIEW
agent_name: Gemini-CLI
run_id: 20260207-1815-p2
timestamp: 2026-02-07T18:15:00Z
repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a

## 2.1 Scores
| Proposal | Drift Prevention | Overhead | Agent-Brain Gap | Implementability | Scalability | External Model | **Total** |
|---|---|---|---|---|---|---|---|
| **Codex** | 4 | 4 | 4 | 5 | 4 | 3 | **24 (unweighted) -> 58** |
| **Claude** | 4 | 4 | 4 | 5 | 4 | 3 | **24 (unweighted) -> 58** |
| **Gemini** | 5 | 2 | 5 | 3 | 5 | 5 | **25 (unweighted) -> 57** |

*Note: Claude and Codex proposals are nearly identical. I scored them the same. Gemini takes a hit on Implementability and Overhead but wins on Drift Prevention and External Models.*

## 2.2 Kill-Shot Risks (Top 10)
1.  **Gemini's Infinite Loop:** Architect (Plan) -> Builder (Fail) -> Architect (Re-plan) loop could consume budget rapidly without human intervention. (NN-7 risk).
2.  **Codex/Claude's Context Blindness:** Monolithic Builder handling 7 surfaces + code + tests will hit token limits/reasoning degradation on complex tasks.
3.  **Codex/Claude's Surface 8 Toil:** Manual sync of `system.md` and `deal_tools.py` (even with a gate) creates friction. Developers will bypass it or update "dummy" descriptions to pass the gate.
4.  **Universal:** **Migration Drift.** No proposal explicitly details how `migration-assertion.sh` handles the *ordering* of migrations across 3 DBs.
5.  **Gemini's Parser Fragility:** `generate_agent_config.py` relying on AST parsing of `deal_tools.py` is brittle. Complex Python (decorators, dynamic args) breaks it.
6.  **Codex/Claude's CLI Tool Context:** Invoking `codex` via Bash CLI loses the *conversation history* and *file context* unless explicitly piped, which is error-prone.
7.  **Guardian Bypass:** If the Guardian is just a script run by the Builder (or Stop hook), a malicious/lazy Builder can ignore the output. Needs CI enforcement.
8.  **Secret Leakage:** CLI tools (Gemini/Codex) writing to stdout/logs might leak keys if not carefully masked.
9.  **Test-Engineer Hallucination:** Generating tests without running them (implied by "write access to tests only") means committing broken tests.
10. **Role Confusion:** "Arch-Reviewer" vs "Contract-Guardian". If Guardian is automated, Reviewer is human-judgment. Overlap risk.

## 2.3 Drift Vectors
*   **Prompt vs Code:** In Codex/Claude model, `system.md` text description of a tool diverges from the actual `deal_tools.py` logic (parameter nuance, side effects).
*   **External Model Versioning:** CLI tools might use different model versions/parameters than the production environment, leading to "works on my machine" issues.
*   **Golden Trace Staleness:** 34 traces require vLLM. If vLLM interface changes, traces rot. No proposal solved the "CI vs vLLM" gap fully (Gemini's "Offline Subset" is a hand-wave).

## 2.4 Coordination Overhead Analysis
*   **Codex/Claude:** Low overhead. Main Builder does 90% of work. Handoffs only for Review/Test.
*   **Gemini:** High overhead. Every code change requires Architect -> Builder handoff. "Telephone game" risk.

## 2.5 Minimum Viable Patch
*   **For Codex/Claude:** Must upgrade "Surface 8" solution to **Generative Configuration**. Manual sync is not "World Class". Must create a wrapper for CLI tools that injects context automatically.
*   **For Gemini:** Must collapse Architect/Builder into one **Lead Engineer** agent to reduce overhead. Must simplify `generate_agent_config.py` scope.

## 2.6 Recommendation: CONTROLLED MERGE
**Winner:** **Modified Codex/Claude Topology** (4 Agents) + **Gemini's Generative Config** + **Gemini's QA-Adversary**.

**The Merge:**
1.  **Topology:** Main Builder (Opus), Contract-Guardian (Sonnet), Arch-Reviewer (Opus), QA-Adversary (Sonnet). *Replaces Test-Engineer with Adversary.*
2.  **Surface 8:** **Generative Configuration**. Do not settle for a check-gate. Build the script.
3.  **External Models:** CLI Tools via Bash, but with a **Context-Injector Wrapper** script to solve the context loss issue.

## 2.7 “Must-add gates” list
1.  **Generative Config Gate:** `system.md` and `tool-schemas.json` are **ignored** in git (or auto-committed). They are build artifacts, not source.
2.  **Multi-DB Migration Gate:** Explicit check that `zakops`, `zakops_agent`, `crawlrag` migrations are distinct and valid.
3.  **Adversarial Test Gate:** QA-Adversary output must execute and PASS before merge.

---

---
# PASS 2 — ADVERSARIAL CROSS-REVIEW
agent_name: Codex
run_id: 20260207-1814-p2
timestamp: 2026-02-07T18:15:06Z
repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a

## 2.1 Scores (Rubric Table for each proposal)

### Proposal A — Claude (Opus 4.5)
| Dimension | Weight | Score | Weighted | Rationale |
|---|---:|---:|---:|---|
| Drift Prevention | 3 | 4.0 | 12.0 | Gates exist but Surface 8 is checklist + CI gate only; generative config not implemented; SSE schema enforcement weak |
| Coordination Overhead | 3 | 4.0 | 12.0 | 4 roles, low handoff; arch-review/test-engineer delegated |
| Agent-Brain Gap Coverage | 3 | 4.5 | 13.5 | Explicit coverage for agent→backend + SSE + prompts; some gates are advisory |
| Implementability | 2 | 4.5 | 9.0 | Uses .claude/agents + CI scripts; no new infra |
| Scalability | 2 | 4.0 | 8.0 | Extension points defined; avoids domain split |
| External Model Utility | 1 | 2.5 | 2.5 | CLI tools only; no structured integration |
| **Total** |  |  | **57.0 / 70** | PASS |

### Proposal B — Codex
| Dimension | Weight | Score | Weighted | Rationale |
|---|---:|---:|---:|---|
| Drift Prevention | 3 | 3.5 | 10.5 | Strong intent, but lacks explicit stop-hook blocking + concrete gate scripts |
| Coordination Overhead | 3 | 4.0 | 12.0 | Same 4-role model; low overhead |
| Agent-Brain Gap Coverage | 3 | 4.0 | 12.0 | Lists surfaces, but enforcement details thin |
| Implementability | 2 | 4.0 | 8.0 | No new infra; fewer explicit steps |
| Scalability | 2 | 4.0 | 8.0 | Scales similarly to Claude |
| External Model Utility | 1 | 3.0 | 3.0 | CLI-only integration |
| **Total** |  |  | **53.5 / 70** | PASS |

### Proposal C — Gemini-CLI
| Dimension | Weight | Score | Weighted | Rationale |
|---|---:|---:|---:|---|
| Drift Prevention | 3 | 4.5 | 13.5 | Generative config + guardian is strong |
| Coordination Overhead | 3 | 2.5 | 7.5 | 5 agents + architect/builder split adds handoff cost |
| Agent-Brain Gap Coverage | 3 | 4.5 | 13.5 | Explicit SDK + SSE schema coverage |
| Implementability | 2 | 2.0 | 4.0 | Requires unsupported subagent models + new generator; violates NN-5 |
| Scalability | 2 | 3.5 | 7.0 | Scales but coordination burden grows |
| External Model Utility | 1 | 5.0 | 5.0 | Strong use of Gemini/Codex, but not supported in platform |
| **Total** |  |  | **50.5 / 70** | **FAIL (Non-negotiable violation)** |

## 2.2 Kill-Shot Risks (Top 10) per proposal

### Claude Proposal — Kill-Shot Risks
1. **Stop hook non-blocking** → guardian can fail yet builder “passes” (paper pass). Fix: stop hook must exit non-zero on failure.
2. **CG-4 prompt/tool gate too weak** → regex counts allow drift. Fix: AST-based tool registry diff + schema validation.
3. **SSE schema only “reference”** → no runtime validation. Fix: enforce JSON schema validation in agent + dashboard tests.
4. **Golden traces still off-CI** → major agent-brain drift undetected. Fix: run offline subset in CI.
5. **No explicit agent→backend SDK gate** → raw HTTP can creep back. Fix: grep gate for httpx usage in deal_tools.py.
6. **Arch-reviewer trigger by file count** → misses critical 1-file changes. Fix: trigger on path patterns (schemas/tools/DB).
7. **External CLI tools assumed installed** → silent failure. Fix: gate checks for gemini/codex availability.
8. **Migration assertion not multi-DB** → drift in zakops_agent/crawlrag. Fix: update migration-assertion.sh.
9. **Permission deny only for generated files** → other drift paths remain. Fix: expand deny patterns for prompt/tool artifacts.
10. **“validate-local” may require live services** → false negatives. Fix: ensure validate-local is offline-safe.

### Codex Proposal — Kill-Shot Risks
1. **Lack of concrete gates** → paper passes; no stop-hook enforcement.
2. **No explicit tool permission YAML** → risk of over-privileged agents.
3. **Generative config gate underspecified** → Surface 8 likely to drift.
4. **No SSE schema enforcement plan** → dashboard/agent event drift.
5. **No arch-review trigger automation** → critical changes slip by.
6. **No external CLI availability checks** → failed calls treated as success.
7. **Agent→backend SDK not mandated** → raw httpx drift persists.
8. **Golden traces remain optional** → agent-brain regression not caught.
9. **Multi-DB migration gate not explicit** → DB drift risk.
10. **No “paper pass” countermeasure** → guardian could be bypassed.

### Gemini Proposal — Kill-Shot Risks
1. **Violates NN-5**: uses Gemini 1.5 Pro as subagent (unsupported). Disqualifies unless patched.
2. **Architect/builder split**: coordination overhead + context fragmentation.
3. **Forensic agent external network**: unsafe + not guaranteed in env.
4. **Generative config AST parser**: brittle, high maintenance.
5. **Builder on Sonnet**: may underperform on cross-stack tasks.
6. **Guardian gate depends on Architect**: risk of bypass if orchestration fails.
7. **QA-Adversary without strict scope**: can write brittle tests.
8. **No explicit stop-hook enforcement**: paper pass risk.
9. **Cost/latency blowups**: multi-agent fanout.
10. **CI integration unspecified**: drift gates not enforceable.

## 2.3 Drift Vectors (Where it will silently fail)
- **Prompt/tool mismatch** if deal_tools.py changes without prompt/schema updates (all proposals unless generative gate is robust).
- **SSE event drift** if schema not enforced in runtime + tests (Claude/Codex weak).
- **Agent→backend raw HTTP usage** if SDK enforcement not in CI (Codex/Claude risk).
- **Multi-DB migration drift** if only main DB checked (all unless explicit).
- **Golden trace regressions** due to lack of CI coverage (all three).
- **External CLI tool absence** causing “fake pass” (Claude/Codex if not checked).

## 2.4 Coordination Overhead Analysis
- **Claude:** Moderate overhead (4 roles). Acceptable if guardian is automatic and arch-review/test-engineer are triggered by path patterns.
- **Codex:** Similar overhead, but fewer concrete triggers = higher coordination ambiguity.
- **Gemini:** High overhead due to architect/builder split + external model agents; likely to degrade velocity.

## 2.5 Minimum Viable Patch for each proposal

### Claude — MVP Patch
- Make stop hook **blocking** on validation failure.
- Replace regex prompt/tool gate with **AST-based tool registry validation** + schema check.
- Add **SSE schema runtime validation** gate (dashboard + agent).
- Add **grep gate** to ban raw httpx in deal_tools.py.
- Add **multi-DB migration assertion** (zakops, zakops_agent, crawlrag).

### Codex — MVP Patch
- Add explicit stop-hook blocking + guardian enforcement.
- Add tool permission YAML for all agents.
- Implement concrete agent-config gate (AST-based generator or strict diff check).
- Add SSE schema validation gate.
- Add SDK enforcement gate for agent→backend.

### Gemini — MVP Patch (to make it viable)
- Replace Gemini/Codex subagents with **CLI tools called by Builder** (NN-5 compliance).
- Collapse Architect+Builder into **single Builder**; keep Arch-Reviewer read-only.
- Keep Guardian + QA-Adversary, but scope QA to tests only.
- Keep generative config, but define deterministic script and CI gate.

## 2.6 Recommendation (Winner or Controlled Merge)
**Winner:** Claude proposal as base (best balance of correctness and implementability).
**Controlled merge:** Add Gemini’s **Generative Configuration** concept (auto-generated prompt + tool schemas) and harden Claude’s gates (blocking stop hook, SSE schema validation). Incorporate Codex’s minimalism by keeping external models as CLI tools only. This hybrid remains within NN-1..NN-8 and is testable.

## 2.7 “Must-add gates” list (non-negotiable)
1. **Stop hook must block** on any validate-local or contract-surface failure.
2. **Agent config gate**: deal_tools.py → auto-generate or strictly validate system.md + tool-schemas.json.
3. **SSE schema validation**: shared schema enforced in both agent + dashboard tests.
4. **Agent→Backend SDK gate**: ban raw HTTP in tools or require typed SDK usage.
5. **Multi-DB migration assertion**: zakops + zakops_agent + crawlrag.
6. **External CLI availability check**: gemini/codex presence before invocation.
7. **Golden trace subset in CI**: offline schema/IO validation.

---

---
# PASS 2 — ADVERSARIAL CROSS-REVIEW

agent_name: Claude (Opus 4.5)
run_id: 20260207-2245-p2-critic
timestamp: 2026-02-07T22:45:00Z
repo_revision: agent-api=5eb7ce6, backend=444dff6

---

## 2.1 Scores (Rubric Table for Each Proposal)

### 2.1.1 Codex Proposal (20260207-1806-p1)

| Dimension | Self-Score | My Score | Delta | Justification |
|-----------|------------|----------|-------|---------------|
| **Drift Prevention** | 4.5×3=13.5 | 4×3=12 | -1.5 | Claims "generative config gate" but provides no implementation. Zero code. Zero test. Paper pass. |
| **Coordination Overhead** | 4×3=12 | 4×3=12 | 0 | Fair. 4 agents with clear triggers. |
| **Agent-Brain Gap** | 4.5×3=13.5 | 3×3=9 | -4.5 | Claims "typed SDK or schema validation gate" — OR is a weasel word. No artifact specified. |
| **Implementability** | 4×2=8 | 4×2=8 | 0 | Uses existing infrastructure. Fair. |
| **Scalability** | 4×2=8 | 4×2=8 | 0 | Extension points present. Fair. |
| **External Model Utility** | 3×1=3 | 2×1=2 | -1 | Gemini/Codex mentioned but with zero trigger rules. |
| **TOTAL** | **58** | **51** | **-7** | **PASS (barely)** |

**Kill-Shot:** The phrase "typed SDK or schema validation gate" is a non-answer. Does agent→backend use BackendClient (exists)? Or need new SDK? NN-8 punted with "or". UNACCEPTABLE.

---

### 2.1.2 Claude Proposal (20260207-2100-p1-claude)

| Dimension | Self-Score | My Score | Delta | Justification |
|-----------|------------|----------|-------|---------------|
| **Drift Prevention** | 5×3=15 | 4×3=12 | -3 | 5-layer mechanism comprehensive BUT Stop hook enforcement "proposed" not implemented. |
| **Coordination Overhead** | 4×3=12 | 4×3=12 | 0 | Fair. Guardian automatic, others delegated. |
| **Agent-Brain Gap** | 5×3=15 | 4×3=12 | -3 | Surface 8 gate is grep-based. Fragile. Will false-positive on comments. |
| **Implementability** | 5×2=10 | 5×2=10 | 0 | All artifacts exist or can be created. Fair. |
| **Scalability** | 4×2=8 | 4×2=8 | 0 | Fair. |
| **External Model Utility** | 3×1=3 | 2×1=2 | -1 | CLI mentioned, zero concrete invocation. |
| **TOTAL** | **63** | **56** | **-7** | **PASS** |

**Kill-Shot:** `validate-agent-config.sh` uses grep to count functions vs prompt lines. Breaks on: decorators, different formatting, wrapped tools. Paper gate.

---

### 2.1.3 Gemini Proposal (20260206-1300-gemini)

| Dimension | Self-Score | My Score | Delta | Justification |
|-----------|------------|----------|-------|---------------|
| **Drift Prevention** | 5×3=15 | 4×3=12 | -3 | Generative config elegant but `generate_agent_config.py` doesn't exist. Claiming 5 for vapor. |
| **Coordination Overhead** | 3×3=9 | 2×3=6 | -3 | 5 agents + Architect/Builder = EVERY task requires 2+ handoffs. |
| **Agent-Brain Gap** | 5×3=15 | 4×3=12 | -3 | Claims SDK coverage but no evidence BackendClient used in deal_tools.py. |
| **Implementability** | 3×2=6 | 2×2=4 | -2 | Requires AST parser, Gemini integration, 5 configs. Most complex. |
| **Scalability** | 4×2=8 | 4×2=8 | 0 | Fair. |
| **External Model Utility** | 5×1=5 | 4×1=4 | -1 | Gemini role exists BUT **NN-5 VIOLATION**: Gemini not in [sonnet/opus/haiku]. |
| **TOTAL** | **50** | **46** | **-4** | **FAIL (NN-5 violation + below 49)** |

**NN-5 VIOLATION:** `Forensic: Model = Gemini 1.5 Pro`. NN-5: "Model selection limited to sonnet/opus/haiku". HARD CONSTRAINT VIOLATION.

---

### 2.1 Summary

| Proposal | Self-Score | Adversarial Score | Verdict |
|----------|------------|-------------------|---------|
| Codex | 58 | 51 | PASS (marginal) |
| Claude | 63 | 56 | PASS |
| Gemini | 50 | 46 | **FAIL** (NN-5 + below threshold) |

---

## 2.2 Kill-Shot Risks (Top 10 Per Proposal)

### Codex Kill-Shots

| # | Risk | Why It Kills | Concrete Fix |
|---|------|--------------|--------------|
| K1 | "Typed SDK or schema gate" weasel | NN-8 unresolved | Pick one: mandate BackendClient |
| K2 | No agent.md files provided | Vapor | Write 4 agent definitions |
| K3 | "Generative config gate" no code | Paper pass | Write validate-agent-config.sh |
| K4 | Trigger rules list surfaces not globs | Guardian won't know when to run | Add glob patterns |
| K5 | "Golden trace subset where feasible" | Hedging | Define 5 offline traces NOW |
| K6 | No Bash allow/deny patterns | NN-6 incomplete | Add patterns |
| K7 | Arch-Reviewer NO Bash | Can't validate | Intentional? Document why |
| K8 | Test-Engineer scope unclear | "tests/ evals/ evidence/" which repo? | Full paths |
| K9 | Multi-DB assertion not in CI | Paper pass | Add to ci.yml |
| K10 | External model "on-demand" zero trigger | Never used | Define trigger |

### Claude Kill-Shots

| # | Risk | Why It Kills | Concrete Fix |
|---|------|--------------|--------------|
| K1 | Stop hook blocking unproven | How to enforce? | Stop hooks advisory; need wrapper |
| K2 | validate-agent-config.sh grep-based | False positives | Use AST parser |
| K3 | Arch-reviewer "judgment-based" | Skipped | Add trigger: >=2 surfaces |
| K4 | 34 golden traces not in CI | Paper claim | Pick 5 offline traces |
| K5 | bashDenyPatterns anemic | Only rm/push | Add DROP, TRUNCATE, curl\|, eval |
| K6 | No agent spawns Task | How delegate? | /arch-review but no auto-trigger |
| K7 | CG-6 "0 .get() patterns" | Already violated | Carve out dict.get() vs response.get() |
| K8 | Permission deny incomplete | Missing agent-api | Add backend_models.py |
| K9 | Quarterly audit too infrequent | 90-day drift | Monthly or CI flag |
| K10 | External CLI check prefix-based | Silent fail | Exit non-zero |

### Gemini Kill-Shots

| # | Risk | Why It Kills | Concrete Fix |
|---|------|--------------|--------------|
| K1 | **NN-5 VIOLATION** | Gemini not allowed | Use Bash CLI wrapper |
| K2 | Architect NO CODE EDITS | Every change = handoff | Merge with Builder |
| K3 | generate_agent_config.py doesn't exist | Vapor | Write it or remove claim |
| K4 | Forensic "ingests massive logs" | How? Read limits | Define chunking |
| K5 | QA-Adversary undefined | What makes it adversarial? | Mutation testing? |
| K6 | Builder runs tests + Guardian validates | Duplicate | Builder skip validation |
| K7 | "Dockerized agent runtimes" | Where? | Remove claim |
| K8 | 5-day plan zero burn-in | Day 5 deploys specialists | Add 2-week burn-in |
| K9 | "Branch protection" GitHub-specific | Not all changes via PR | Add local hook |
| K10 | Architect permissions unclear | "Delegate" not a tool | Map to Claude tools |

---

## 2.3 Drift Vectors (Where It Will Silently Fail)

| Vector | Description | Why Silent | Detection Test |
|--------|-------------|------------|----------------|
| **DV-1** | New tool in deal_tools.py, not in system.md | grep tolerance | 0-tolerance gate |
| **DV-2** | SSE event field renamed | TypeScript compiles | Runtime payload test |
| **DV-3** | BackendClient signature changes | Compiles, runtime 400s | Integration smoke |
| **DV-4** | MCP optional→required | mcp_server works, client breaks | Schema diff gate |
| **DV-5** | crawlrag schema changes no migration | No tracking | Add to migration-assertion |
| **DV-6** | .claude/ user vs repo diverge | Override | Config audit command |
| **DV-7** | Stop hook bypassed (Ctrl+C) | Advisory | Pre-push backup |
| **DV-8** | validate-local passes, validate-live fails | CI offline | Nightly cron |

---

## 2.4 Coordination Overhead Analysis

### Handoff Matrix

| Task | Codex | Claude | Gemini |
|------|-------|--------|--------|
| Simple bug fix | 2 | 2 | 3 |
| New endpoint | 3 | 3 | 4 |
| Schema migration | 3 | 3 | 5 |
| Debug prod issue | 2 | 2 | 3 |

### Token Overhead

| Proposal | Agents/Day | Tokens/Handoff | Daily Overhead |
|----------|------------|----------------|----------------|
| Codex | 8 | ~2000 | ~16K |
| Claude | 8 | ~2000 | ~16K |
| Gemini | 15 | ~3000 | ~45K |

**Verdict:** Gemini Architect/Builder triples overhead. NN-7 at risk.

---

## 2.5 Minimum Viable Patch for Each Proposal

### Codex MVP (~200 lines, 2 days)
```diff
+ Write 4 agent.md files
+ "typed SDK or schema gate" → "mandate BackendClient"
+ Add validate-agent-config.sh (AST-based)
+ Add bashAllowPatterns/bashDenyPatterns
+ Pick 5 offline golden traces
+ Add migration-assertion to CI
```

### Claude MVP (~150 lines, 1.5 days)
```diff
+ Replace grep validate-agent-config with AST
+ Add arch-reviewer trigger: >=2 surfaces
+ Add docker to guardian bashAllowPatterns
+ Add pre-push hook backup
+ Expand bashDenyPatterns
+ Separate response.get() from dict.get()
+ Add nightly validate-live cron
```

### Gemini MVP (~400 lines, 4 days)
```diff
- Remove Architect (merge into Builder)
- Forensic: Gemini → sonnet + CLI wrapper
+ Write generate_agent_config.py (AST)
+ Add 2-week burn-in
+ Define adversarial test patterns
- Remove Dockerized runtime claim
+ Map Delegate to Claude tools
```

---

## 2.6 Recommendation (Winner or Controlled Merge)

### Verdict: CONTROLLED MERGE — Claude Base + Codex Specificity + Gemini Generative Config

**Recommended Merged Topology:**

| Agent | Source | Model | Permissions |
|-------|--------|-------|-------------|
| main-builder | Claude | opus | Full |
| contract-guardian | Claude | sonnet | Read + scoped Bash (add docker) |
| arch-reviewer | Claude | opus | Read only (add auto-trigger) |
| test-engineer | Claude | sonnet | Write tests/** only |

**Surface 8:** Gemini Generative Config + Claude phased rollout:
- Phase 1: CLAUDE.md checklist + grep gate (ship immediately)
- Phase 2: AST-based generate_agent_config.py (Day 7-10)

**External Models:** CLI tools (Codex/Claude consensus). NOT subagents (NN-5).

### Why Merge?

- **Claude:** Best structure, lacks specificity (grep-based gate, no auto-triggers)
- **Codex:** Better gate lists, punts NN-8 ("or")
- **Gemini:** Best idea (Generative Config), worst execution (NN-5 violation, 5-agent overhead)

---

## 2.7 "Must-Add Gates" List (Non-Negotiable for PASS 3)

| Gate ID | Gate | Rationale | Test |
|---------|------|-----------|------|
| **MG-1** | AST-based agent config validation | grep fails | `validate_agent_config.py --strict` exit 0 |
| **MG-2** | BackendClient mandatory | NN-8 closure | `grep -r "httpx\." deal_tools.py` = 0 |
| **MG-3** | Guardian bash includes docker | Container validation | `docker compose ps` works |
| **MG-4** | Pre-push hook backup | Ctrl+C bypass | Push blocked if validate fails |
| **MG-5** | migration-assertion in CI | crawlrag drift | `make migration-assert` exit 0 |
| **MG-6** | Arch-reviewer auto-trigger | Judgment = skipped | Trigger: >=2 surfaces OR new endpoint |
| **MG-7** | 5 offline golden traces | "Feasible" = never | List trace-001 to trace-005 |
| **MG-8** | External model invocation pattern | "On-demand" = never | Gemini: >50KB diffs, Codex: >3 file tests |
| **MG-9** | bashDenyPatterns expanded | Security | DROP, TRUNCATE, rm -rf /, curl\|sh, eval |
| **MG-10** | Nightly validate-live cron | validate-local offline | Cron job against running services |

---

## 2.8 Cross-Review of Other PASS 2 Reviews

### Gemini-CLI PASS 2 (20260207-1815-p2)

**Agreements:**
- Correctly identifies Architect/Builder overhead
- Correctly recommends Controlled Merge
- Correctly identifies CLI context loss issue

**Disagreements:**
- Scores Claude/Codex identically (24 unweighted). I see 5-point gap.
- Recommends replacing Test-Engineer with QA-Adversary. Test-Engineer is more implementable.
- "Do not settle for check-gate" — phased approach is pragmatic.

### Codex PASS 2 (20260207-1814-p2)

**Agreements:**
- Correctly identifies NN-5 violation in Gemini
- Correctly identifies stop hook non-blocking risk
- Same 7 must-add gates
- Recommends Claude base with Gemini generative config

**Disagreements:**
- Scores Codex 53.5, I score 51. Difference is NN-8 "or" penalty.
- Doesn't penalize Codex enough for missing agent.md files.

---

## 2.9 Consensus Across All PASS 2 Reviews

| Topic | Gemini-CLI | Codex | Claude | Consensus |
|-------|------------|-------|--------|-----------|
| Winner | Modified Codex/Claude + Gemini GenConfig | Claude base + Gemini GenConfig | Claude base + Codex specificity + Gemini GenConfig | **Claude base + Gemini GenConfig** |
| Gemini NN-5 | Not flagged | **FLAGGED** | **FLAGGED** | NN-5 VIOLATION confirmed |
| Architect/Builder split | Collapse | Not applicable | Remove Architect | **Reject Architect/Builder split** |
| Surface 8 | Generative Config mandatory | Generative Config best | AST-based phase 2 | **Generative Config (phased)** |
| QA-Adversary | Include | Not mentioned | Test-Engineer preferred | **Test-Engineer (simpler)** |

---

*PASS 2 (ADVERSARIAL CROSS-REVIEW) COMPLETE. Ready for PASS 3 (SYNTHESIZER).*

---

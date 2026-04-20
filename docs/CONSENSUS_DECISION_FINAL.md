# CONSENSUS DECISION — FINAL
agent_name: Codex
run_id: 20260207-1820-80c8
timestamp: 2026-02-07T18:20:00Z
repo_revision: unknown

## 3.1 Decision Summary (What we are adopting)
Adopt a **role‑based 4‑agent topology** with a single full‑context Builder and three specialized support agents (Contract‑Guardian, Arch‑Reviewer, Test‑Engineer). Reject domain‑split agents and Architect/Builder split. Integrate external models (Gemini/Codex) **only as CLI tools** invoked by the Builder. Close the agent‑brain contract gap by implementing a **phased Generative Configuration** gate for Surface 8 (prompt/tool/schema alignment) and mandatory CI/Stop‑hook validation. This is a controlled merge: **Claude’s 4‑agent topology as base + Gemini’s generative config idea + Codex’s gate specificity**.

## 3.2 Why (Rubric-based reasoning + totals)
**Rubric score (final decision): 60 / 70**

| Dimension | Weight | Score | Weighted | Rationale |
|---|---:|---:|---:|---|
| Drift Prevention | 3 | 4.5 | 13.5 | Adds generative config + CI/Stop gates across 8 surfaces; avoids paper pass |
| Coordination Overhead | 3 | 4.0 | 12.0 | 4 agents; no domain split; handoffs only on triggers |
| Agent‑Brain Gap Coverage | 3 | 4.5 | 13.5 | Explicit gating for agent→backend SDK, SSE schema, prompt/tool alignment |
| Implementability | 2 | 5.0 | 10.0 | Tiered stop‑hook + CI gating reduces performance risk |
| Scalability | 2 | 4.0 | 8.0 | Add agents only when bottlenecks appear |
| External Model Utility | 1 | 3.0 | 3.0 | CLI tools provide optional second opinions without coordination drag |

**Why this beats alternatives**
- Beats 7‑agent domain split: avoids coordination drift (NN‑2, NN‑7).
- Beats 5‑agent Gemini: avoids NN‑5 violation, reduces overhead.
- Beats 3‑agent minimal: adds needed Arch‑Reviewer/Test‑Engineer without large overhead.

## 3.3 Adopted Agent Topology + Roles
| Agent | Model | Role | Invocation Trigger |
|---|---|---|---|
| **main‑builder** | opus | Full‑stack implementer; owns all edits, codegen, and fixes | Default for all tasks |
| **contract‑guardian** | sonnet | Read‑only validator; runs gates and reports only | Auto‑trigger after changes; Stop hook + CI |
| **arch‑reviewer** | opus | Read‑only architecture/security reviewer | Trigger on ≥2 contract surfaces **OR** any change to Pydantic response models, middleware, DB migrations, LangGraph nodes/edges/state, or error response schemas |
| **test‑engineer** | sonnet | Writes tests only; regression + adversarial coverage | Trigger after functional change or new endpoint |

External models:
- **Gemini CLI** and **Codex CLI** available to main‑builder via Bash for alternative reasoning/boilerplate. **No dedicated subagents.**

## 3.4 Permission Matrix
| Agent | Read | Edit | Write | Bash | Scope |
|---|---|---|---|---|---|
| main‑builder | ✅ | ✅ | ✅ | ✅ | All repos |
| contract‑guardian | ✅ | ❌ | ❌ | ✅ (validation only) | make/npx/rg/psql commands only |
| arch‑reviewer | ✅ | ❌ | ❌ | ❌ | Read‑only analysis |
| test‑engineer | ✅ | ❌ | ✅ (tests only) | ✅ (test commands only) | `**/tests/**`, `**/evals/**`, `**/golden/**`, evidence dirs |

**NN‑1 satisfied**: Guardian has NO Edit/Write.

## 3.5 Enforcement Model (Trigger rules + must-pass gates)
**Trigger Rules (hard):**
- **Contract‑Guardian** runs after any change touching: `packages/contracts/**`, `apps/dashboard/src/lib/*generated*`, `apps/agent-api/app/schemas/**`, `zakops-backend/src/schemas/**`, any API routes.
- **Arch‑Reviewer** runs when ≥2 contract surfaces **OR** any change to Pydantic response models, middleware, DB migrations, LangGraph nodes/edges/state, or error response schemas.
- **Test‑Engineer** runs after any functional change; must produce tests that run green.

**Must‑Pass Gates (runnable commands):**
1) **Gate A — Offline Validation**
```bash
cd /home/zaks/zakops-agent-api
make validate-local
```
2) **Gate B — Contract Surfaces**
```bash
cd /home/zaks/zakops-agent-api
bash tools/infra/validate-contract-surfaces.sh
```
3) **Gate C — Agent Config (Surface 8, Generative Config)**
```bash
cd /home/zaks/zakops-agent-api
bash tools/infra/validate-agent-config.sh
```
4) **Gate D — SSE Schema Validation**
```bash
cd /home/zaks/zakops-agent-api
python3 tools/infra/validate_sse_schema.py
```
5) **Gate E — Agent→Backend SDK Enforcement**
```bash
cd /home/zaks/zakops-agent-api
rg -n "httpx\\.(AsyncClient|get|post|put|patch|delete)" apps/agent-api/app/core/langgraph/tools/deal_tools.py
# Must return 0 lines (BackendClient only; httpx exceptions are allowed)
```
6) **Gate F — Multi‑DB Migration Assertion**
```bash
cd /home/zaks/zakops-agent-api
bash tools/infra/migration-assertion.sh
```
7) **Gate G — External CLI Availability (informational, non‑blocking)**
```bash
command -v gemini && command -v codex
```
8) **Gate H — Stop Hook Must Block**
```bash
/home/zaks/.claude/hooks/stop.sh
# Must exit non‑zero on any **Fast Tier** gate failure
```

**Gate Tiers (speed vs depth):**
- **Fast Tier (Stop hook):** Gates **A, B, E**. Must block on failure.
- **Full Tier (CI + manual):** Gates **A through H**. Gate G is **informational only** and must not block.

## 3.6 Drift Prevention (How we guarantee alignment)
- **Surface 1 (Backend→Dashboard):** OpenAPI → TypeScript codegen + `tsc --noEmit` gate.
- **Surface 2 (Agent→Backend):** Mandate BackendClient; ban raw httpx via Gate E.
- **Surface 3 (Agent OpenAPI):** Spec existence + freshness in contract‑surface gate.
- **Surface 4 (Dashboard↔Agent SSE):** Shared schema + Gate D validation.
- **Surface 5 (RAG):** RAG schema + migration assertion for crawlrag.
- **Surface 6 (MCP Tool Schemas):** Tool schema generation + contract surface validation.
- **Surface 7 (Contract Suite):** validate‑contract‑surfaces.sh.
- **Surface 8 (Agent Config):** Generative config gate, AST‑based alignment of deal_tools.py → system.md + tool‑schemas.json.

## 3.7 Agent-Brain Governance (prompts/tools/contracts)
- **System prompt** is versioned; any tool change requires prompt update.
- **deal_tools.py** is the single source of truth for tool definitions.
- **Generative Config** auto‑generates or validates:
  - `system.md` tool list
  - MCP tool schemas JSON
  - Stage transition matrix (if extracted)
- **Prompt/Tool Registry Validation** is **CI‑mandatory** (Gate C).

## 3.8 Contract Surface Coverage Plan (what is gated)
| Surface | Boundary | Gate | Command |
|---|---|---|---|
| S1 | Backend → Dashboard | Gate A + TS compile | `make validate-local` + `tsc --noEmit` |
| S2 | Agent → Backend | Gate E | `rg httpx` (must be 0) |
| S3 | Agent OpenAPI | Gate B | `validate-contract-surfaces.sh` |
| S4 | Dashboard ↔ Agent SSE | Gate D | `validate_sse_schema.py` |
| S5 | RAG → Backend | Gate F | `migration-assertion.sh` (multi‑DB) |
| S6 | MCP schemas | Gate B/C | `validate-contract-surfaces.sh` + config gen |
| S7 | Contract suite | Gate B | `validate-contract-surfaces.sh` |
| S8 | Agent config | Gate C | `validate-agent-config.sh` |

## 3.9 Implementation Phases (with acceptance + evidence)
**Phase 0 — Baseline**
- Create `.claude/agents/*.md` for 4 agents.
- Evidence: agent files listed; permissions validated.

**Phase 1 — Guardian Enforcement**
- Stop hook runs **Fast Tier** (Gate A) and blocks on failure.
- Evidence: stop hook exit non‑zero when gate fails.

**Phase 2 — Create Missing Gate Scripts**
- Implement `generate_agent_config.py`, `validate_sse_schema.py`, and extend `migration-assertion.sh`.
- Evidence: Gates C/D/F pass; intentional mismatch fails.

**Phase 3 — Verify SDK Enforcement Still Clean**
- Run Gate E and confirm 0 matches (no raw httpx client usage).
- Evidence: Gate E returns 0 matches.

**Phase 4 — Validate‑Live Automation**
- Automate `make validate-live` (CI job + nightly cron).
- Evidence: CI run logs + scheduled run logs stored.

**Phase 5 — Test Coverage**
- Test‑Engineer adds regression/adversarial tests.
- Evidence: CI green + test reports stored.

## 3.10 Residual Risks + Monitoring
**Residual Risks**
- Golden traces still require vLLM; offline subset only.
- Generative config AST parser brittleness on complex Python patterns.
- External CLI availability variability.

**Monitoring**
- Nightly `make validate-live` workflow (self‑hosted) to catch runtime drift. (NEEDS VERIFICATION: runner availability)
- CI required checks: Gates A–H (Gate G informational only).
- Monthly contract surface audit (document in CHANGES.md).

## 3.11 Builder Delegation Protocol

After completing any code change:  
→ `/contract-guardian` runs automatically (stop hook)

Before implementing changes that touch ≥2 surfaces, new endpoints,  
DB migrations, LangGraph modifications, Pydantic models, or middleware:  
→ Delegate to `/arch-review` with a description of proposed change

After completing any new feature or endpoint:  
→ Delegate to `/write-tests` targeting the new code

For alternative architectural analysis or rapid boilerplate:  
→ Use `gemini`/`codex` CLI directly (no delegation needed)

## 3.12 MCP Servers & Skills Configuration

### MCP Servers to Activate (2 of 13 available)
| Server | Why | Priority |
|--------|-----|----------|
| GitHub | Cross‑repo search, PR management, issue tracking — essential for a 4‑repo project | P0 — activate immediately |
| Playwright | Browser‑based dashboard testing — catches rendering issues that tsc misses | P1 — activate in Phase 6 |

All other MCP servers (Slack, Linear, etc.) remain disabled until team tooling requires them.

### Existing Skills (verified, no changes needed)
7 global skills already configured at `~/.claude/skills/`:
1. api-conventions — Backend/Dashboard/Agent API patterns
2. atomic-workflow — GOAL/FILES/VERIFY/EVIDENCE/ROLLBACK structure
3. code-style — Python + TypeScript conventions
4. debugging-playbook — Debugging procedures
5. project-context — Service map, DB topology, data flow
6. security-and-data — Security patterns
7. verification-standards — Evidence requirements, health checks

Plus 12 slash commands and 4 path‑scoped rules. No additions needed — the skills layer is well‑populated.

### Skill Preloads per Agent
| Agent | Preloaded Skills |
|-------|-----------------|
| main-builder | All 7 skills |
| contract-guardian | verification-standards, api-conventions |
| arch-reviewer | api-conventions, security-and-data, project-context |
| test-engineer | verification-standards, debugging-playbook |

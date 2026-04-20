# Frontend Infrastructure Audit — Full Findings

**Date:** 2026-02-10
**Scope:** Claude Code frontend tooling, contract surfaces, design system, skills, agents, plugins
**Auditor:** Claude Opus 4.6 (interactive session with operator)
**Purpose:** Structured foundation for mission prompt to drive resolution of all identified gaps

---

## Table of Contents

1. [Q1: Frontend Plugin Auto-Discovery](#q1-frontend-plugin-auto-discovery)
2. [Q2–Q5: Surface Registration State (Group A Round 1)](#q2-q5-surface-registration-state)
3. [Q6–Q8: Surfaces 10-14 Specifics (Group B Round 1)](#q6-q8-surfaces-10-14-specifics)
4. [Q9–Q11: Design System / Frontend Plugin (Group C Round 1)](#q9-q11-design-system--frontend-plugin)
5. [Q12–Q14: Wiring Integrity (Group D Round 1)](#q12-q14-wiring-integrity)
6. [Q15–Q18: What Claude Code Actually Has (Group A Round 2)](#q15-q18-what-claude-code-actually-has)
7. [Q19–Q21: Design System Rule Effectiveness (Group B Round 2)](#q19-q21-design-system-rule-effectiveness)
8. [Q22–Q24: Capability Awareness (Group C Round 2)](#q22-q24-capability-awareness)
9. [Q25–Q27: Gap Discovery (Group D Round 2)](#q25-q27-gap-discovery)
10. [Q28–Q30: Local Skills Inventory (Follow-Up 1)](#q28-q30-local-skills-inventory)
11. [Q31–Q34: The Inert Frontend-Design Plugin (Follow-Up 2)](#q31-q34-the-inert-frontend-design-plugin)
12. [Q35–Q37: Missing Agents Directory (Follow-Up 3)](#q35-q37-missing-agents-directory)
13. [Master Gap Registry](#master-gap-registry)
14. [Recommended Mission Structure](#recommended-mission-structure)

---

## Q1: Frontend Plugin Auto-Discovery

**Question:** "Does Claude Code have access to use front-end plugins anytime that is doing front-end or UI work? Did we set it up that way that Claude Code is going to discover the front-end plugins any time that is doing a dashboard or front-end work?"

### Evidence

- Two path-scoped rules auto-load when editing dashboard files: `design-system.md` and `dashboard-types.md`.
- No MCP plugins are active for frontend work. Playwright MCP exists in settings.json but is set to `"disabled": true`.
- No Figma, Storybook, accessibility checker, visual regression, or component library MCP plugins are configured.
- The `frontend-design` plugin from the official Anthropic marketplace is present on disk but has never been activated.

### Path

- Rules: `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`, `dashboard-types.md`
- Settings: `/home/zaks/.claude/settings.json` (line 36-38: Playwright disabled)
- Inert plugin: `/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/`

### Artifact

- `design-system.md`: 91 lines, glob-triggers on `apps/dashboard/src/components/**`, `src/app/**`, `src/styles/**`
- `dashboard-types.md`: 27 lines, glob-triggers on `src/types/**`, `src/lib/**`, `src/components/**`, `src/hooks/**`

### Status

Claude Code receives **architectural rules and design guidelines** when touching dashboard files (auto-injected by path-scoped rules). It does **not** receive frontend-specific tools, plugins, or skills. There is no mechanism for auto-discovering or auto-loading the frontend-design plugin.

### Gap

1. The `frontend-design` SKILL.md (42 lines of rich design guidance) sits inert on disk — never loaded.
2. Playwright MCP is installed but disabled — no visual testing capability.
3. No auto-discovery mechanism links plugin skills to path-scoped rule triggers.
4. The design-system.md rule was derived from the plugin SKILL.md but lost ~30% of the content in condensation.

### Recommended Fix

1. Copy or symlink the frontend-design skill into the local skills directory.
2. Add a "Skill Preloads" section to `design-system.md` pointing to the frontend-design SKILL.md.
3. Enable Playwright MCP for visual verification.
4. Evaluate whether the design-system.md Category B should be replaced with a direct skill reference to avoid content drift.

---

## Q2-Q5: Surface Registration State

### Q2: How many contract surfaces are registered in contract-surfaces.md?

**Evidence:** The file header states "The 9 Contract Surfaces (Hybrid Guardrail)". Sections are numbered Surface 1 through Surface 9.

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` (lines 11-64)

**Artifact:** 9 surfaces listed:

| # | Surface Name | Sync Command |
|---|-------------|-------------|
| 1 | Backend → Dashboard (TypeScript) | `make sync-types` |
| 2 | Backend → Agent SDK (Python) | `make sync-backend-models` |
| 3 | Agent API OpenAPI Spec | `make update-agent-spec` |
| 4 | Agent → Dashboard (TypeScript) | `make sync-agent-types` |
| 5 | RAG → Backend SDK (Python) | `make sync-rag-models` |
| 6 | MCP Tool Schemas | (export from tool_schemas.py) |
| 7 | SSE Event Schema | (reference schema) |
| 8 | Agent Configuration | `make validate-agent-config` |
| 9 | Component Design System → Dashboard | `bash tools/infra/validate-surface9.sh` |

**Status:** 9 surfaces are formally registered and documented.

**Gap:** None for this specific question — the registration itself is complete.

**Recommended Fix:** N/A (baseline established).

---

### Q3: Does make validate-contract-surfaces check all registered surfaces?

**Evidence:** The script header on line 3 says "Validates all 7 contract surfaces". It checks:
- Freshness: S1, S2, S4, S5 (generated file timestamp vs spec timestamp)
- Existence: S3, S6, S7 (schema file exists)
- Bridge import enforcement (S1/S4 related)
- Typed SDK enforcement (S2 related)

It does NOT check S8 (Agent Config) or S9 (Design System).

**Path:** `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` (145 lines)

**Artifact:** Script line 3: `# Validates all 7 contract surfaces: freshness, bridge imports, typed SDK, TypeScript`

**Status:** Validates 7 of 9 surfaces. S8 and S9 are validated by separate scripts (`validate-agent-config.sh` and `validate-surface9.sh` respectively).

**Gap:** The script claims "all 7" but the project has 9 surfaces. The two missing surfaces have standalone validators but are not unified. `validate-surface9.sh` is not wired into ANY Makefile target — it exists but is never called automatically.

**Recommended Fix:**
1. Update the script header comment from "7" to "9".
2. Add calls to `validate-agent-config.sh` and `validate-surface9.sh` inside the script, OR
3. Wire `validate-surface9.sh` into `make validate-full` (S8 is already there via `validate-agent-config`).

---

### Q4: How many surfaces appear in the infra-snapshot manifest?

**Evidence:** The manifest's "Contract Surfaces (Hybrid Guardrail)" section (lines 962-967) lists 5 surfaces — Backend API, Agent API, RAG API, MCP Tools, SSE Events — ALL marked "NOT FOUND".

**Path:** `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md` (lines 962-967)

**Artifact:**
```
## Contract Surfaces (Hybrid Guardrail)
- Backend API: NOT FOUND
- Agent API: NOT FOUND
- RAG API: NOT FOUND
- MCP Tools: NOT FOUND
- SSE Events: NOT FOUND
```

**Status:** The snapshot generator is stale. It attempts to detect 5 surfaces (S1-S5 mapped by broad name), finds none (likely a detection logic bug), and knows nothing about S6-S9.

**Gap:**
1. 5 of 9 surfaces listed, 0 detected — the generator doesn't find actual spec files.
2. S6 (MCP Tools), S7 (SSE Events), S8 (Agent Config), S9 (Design System) completely absent.
3. The manifest also shows "Rules: 0" despite 5 rules existing — the generator has stale discovery logic.

**Recommended Fix:** Rewrite the contract surfaces section of `tools/ops/generate-manifest.sh` (or equivalent) to:
1. Check actual file paths from `contract-surfaces.md`
2. Include all 9 surfaces
3. Report freshness status (current/stale/missing) for each

---

### Q5: What count does CLAUDE.md state?

**Evidence:** CLAUDE.md line 30 says "Contract Surfaces (9 Total)". The table on lines 34-44 lists all 9 with their sync commands.

**Path:** `/home/zaks/zakops-agent-api/CLAUDE.md` (lines 30-44)

**Artifact:** Section header: `## Contract Surfaces (9 Total)` followed by a complete 9-row table matching `contract-surfaces.md`.

**Status:** CLAUDE.md is accurate and consistent with `contract-surfaces.md`.

**Gap:** CLAUDE.md says 9, `contract-surfaces.md` says 9, but `validate-contract-surfaces.sh` says 7 and the manifest shows 5. There is a 3-way count inconsistency across artifacts.

**Recommended Fix:** Align all artifacts to 9:
- `validate-contract-surfaces.sh` header → "9"
- Manifest generator → detect all 9
- Add a boot diagnostic check for surface count consistency (this already exists as CHECK 2 but only checks 3 locations)

---

## Q6-Q8: Surfaces 10-14 Specifics

### Q6: Do Dependency Health, Secret/Env Registry, Error Taxonomy, Test Coverage Contract, or Performance Budget have formal entries?

**Evidence:** `contract-surfaces.md` lists exactly 9 surfaces. None of the proposed topics appear. Searched the file for "Dependency", "Secret", "Environment", "Error Taxonomy", "Test Coverage", "Performance Budget" — zero matches.

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` (complete file, 85 lines)

**Artifact:** No entries for any proposed Surface 10-14.

**Status:** There are exactly 9 registered surfaces. No surfaces 10-14 exist.

**Gap:** These operational concerns have no formal enforcement:
- Environment variable alignment across services (no automated check)
- Error response shape consistency (documented but not validated)
- Test coverage thresholds (documented but not gated)
- Dependency health and performance budgets (completely undocumented)

**Recommended Fix:** Evaluate which of these warrant formal surface registration. At minimum:
- Error shapes across services could be Surface 10 (3 services, 6 distinct shapes documented)
- Environment variable cross-reference could be Surface 11 (cross-service vars need alignment checks)

---

### Q7: For Surfaces 10-14 that exist — what validation mechanisms exist?

**Evidence:** N/A — none exist. No make targets, gate scripts, or lint rules enforce any of these concerns.

**Path:** N/A

**Artifact:** N/A

**Status:** Zero validation for any proposed Surface 10-14 topic.

**Gap:** Same as Q6 — no enforcement for env vars, error shapes, test coverage, dependency health, or performance budgets.

**Recommended Fix:** If surfaces are registered, each needs:
- A validation script in `tools/infra/`
- A Makefile target
- Integration into `make validate-full`

---

### Q8: Were QA-SR-VERIFY-001 artifacts registered as formal surface documents?

**Evidence:** Four documents exist in bookkeeping:

| Document | Path | Created By |
|----------|------|-----------|
| SERVICE-TOPOLOGY.md | `/home/zaks/bookkeeping/docs/` | SURFACE-REMEDIATION-001 |
| ENV-CROSSREF.md | `/home/zaks/bookkeeping/docs/` | SURFACE-REMEDIATION-001 |
| ERROR-SHAPES.md | `/home/zaks/bookkeeping/docs/` | SURFACE-REMEDIATION-001 |
| TEST-COVERAGE-GAPS.md | `/home/zaks/bookkeeping/docs/` | SURFACE-REMEDIATION-001 |

All four live in `bookkeeping/docs/`, NOT in the monorepo's `packages/contracts/` or `.claude/rules/`.

**Path:** `/home/zaks/bookkeeping/docs/` (all four files)

**Artifact:** Each file's header confirms: "Generated by SURFACE-REMEDIATION-001 from FORENSIC-AUDIT-SURFACES-002 findings."

**Status:** These are **reference documents only** — informational, not enforceable. They have no make target, no validation gate, and no contract-surfaces.md entry.

**Gap:** The knowledge captured in these documents is valuable but has no automated enforcement loop. ENV-CROSSREF.md in particular documents cross-service variables that could cause silent drift.

**Recommended Fix:** Decide which documents should graduate to formal surfaces. For those that stay as reference docs, add a freshness check (compare document date to last schema change).

---

## Q9-Q11: Design System / Frontend Plugin

### Q9: Does design-system.md exist? Line count and sections?

**Evidence:** File exists at `.claude/rules/design-system.md`, 91 lines, 4126 bytes.

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`

**Artifact:** Two-category structure:

**Category A — ZakOps Architectural Conventions (7 sections):**
- A1: Data Fetching (Promise.allSettled mandatory, Promise.all banned)
- A2: Error Handling (console.warn for degradation, console.error for unexpected)
- A3: CSS Architecture (@layer base, caret-color, CSS variables)
- A4: Data Aggregation (server-side counts only)
- A5: Stage Definitions (PIPELINE_STAGES single source of truth)
- A6: API Communication (middleware proxy, JSON 502 never HTML 500)
- A7: Import Discipline (bridge files only, never generated files)

**Category B — Frontend Design Quality Standards (7 sections + Critical Principle):**
- B1: Design Thinking
- B2: Typography
- B3: Color and Theme
- B4: Motion and Micro-Interactions
- B5: Spatial Composition
- B6: Backgrounds and Visual Depth
- B7: Anti-Patterns to Avoid
- Critical Principle (match complexity to vision)

**Status:** Complete and well-structured. Auto-loads for dashboard component work.

**Gap:** Category B was condensed from the marketplace `frontend-design` SKILL.md and lost ~30% of the original's specificity (see Q32 for detailed comparison).

**Recommended Fix:** Either enrich Category B with the missing content, or add a skill preload reference to the full SKILL.md.

---

### Q10: Does design-system.md contain specific, actionable guidance or only ZakOps conventions?

**Evidence:** It contains BOTH. Category A is ZakOps-specific (Promise.allSettled, console.warn, PIPELINE_STAGES). Category B is genuine frontend design quality guidance with:
- Named fonts to avoid: Arial, Inter, Roboto
- Named anti-pattern: purple gradients on white backgrounds
- Specific CSS techniques: gradient meshes, layered transparencies
- Specific motion patterns: staggered reveals, scroll-triggered effects
- Specific compositional guidance: asymmetry, overlap, diagonal flow

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` (lines 49-91)

**Artifact:** Category B sections B1-B7 plus Critical Principle — all contain named examples and specific techniques, not vague advice.

**Status:** Category B is actionable and specific. It is substantially more than "make it look good."

**Gap:** Compared to the source material (marketplace SKILL.md), Category B is missing:
1. 12+ specific aesthetic tone directions (retro-futuristic, brutalist, art deco, etc.)
2. Anti-convergence rule ("NEVER converge on common choices like Space Grotesk")
3. Variation instruction ("vary between light and dark themes across designs")
4. Additional texture techniques (noise textures, dramatic shadows, custom cursors, grain overlays)
5. Motion library recommendation (Motion for React)

**Recommended Fix:** Supplement Category B with the missing specifics, or add a preload reference to the full SKILL.md alongside the rule.

---

### Q11: Does design-system.md auto-load for dashboard component files?

**Evidence:** YAML frontmatter contains glob patterns:
```yaml
paths:
  - "apps/dashboard/src/components/**"
  - "apps/dashboard/src/app/**"
  - "apps/dashboard/src/styles/**"
```

Claude Code's path-scoped rule system injects the rule content into context when the target file matches any glob.

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` (lines 1-6, frontmatter)

**Artifact:** Three glob patterns covering components, app pages, and styles directories.

**Status:** Working as designed. Any edit to a file under `apps/dashboard/src/components/`, `src/app/`, or `src/styles/` triggers auto-injection of design-system.md.

**Gap:** The `src/hooks/` directory is NOT covered by design-system.md (it IS covered by dashboard-types.md). This is intentional — hooks are data-layer, not presentation-layer.

**Recommended Fix:** None needed — the glob coverage is correct for design-related files.

---

## Q12-Q14: Wiring Integrity

### Q12: Adding a new env var to Agent API — which surface, what validation?

**Evidence:** There is no formal surface governing environment variables. ENV-CROSSREF.md documents cross-service variables but has no validation gate. The closest formal surface is S8 (Agent Configuration) if the env var affects agent config files.

**Path:**
- ENV-CROSSREF.md: `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md` (reference only)
- Surface 8: `.claude/rules/contract-surfaces.md` (lines 49-56)

**Artifact:** ENV-CROSSREF.md documents cross-service variables with a table: Variable | Services | Sensitivity | Notes.

**Status:** No automated validation exists. Adding an env var is entirely manual — update the .env file, optionally update ENV-CROSSREF.md, no gate catches misalignment.

**Gap:** Cross-service environment variables can drift silently. If Backend adds `FEATURE_FLAG_X=true` and Agent API needs it but doesn't get it, no validation catches this.

**Recommended Fix:** Either:
1. Register env vars as a formal surface with a validation script that checks all .env.example files for cross-service alignment, OR
2. At minimum, add a check to `make validate-live` that verifies critical cross-service env vars are set in all required services.

---

### Q13: Adding a new error response shape to Backend API — which surface, what artifact?

**Evidence:** Error response shapes are governed by Surface 1 (Backend → Dashboard) and Surface 2 (Backend → Agent SDK) through the OpenAPI spec. ERROR-SHAPES.md documents 6 distinct error shapes across services but is informational only.

**Path:**
- Surface 1/2: `packages/contracts/openapi/zakops-api.json`
- ERROR-SHAPES.md: `/home/zaks/bookkeeping/docs/ERROR-SHAPES.md`

**Artifact:** ERROR-SHAPES.md documents Shape 1 (Backend Structured ErrorResponse) through Shape 6, with service, source file, and example payload for each.

**Status:** Adding a new error shape requires:
1. Define in Backend Pydantic models
2. Run `make update-spec && make sync-types && make sync-backend-models`
3. Manually update ERROR-SHAPES.md
Step 3 has no enforcement — ERROR-SHAPES.md can go stale.

**Gap:** No validation checks that ERROR-SHAPES.md matches actual error shapes in the codebase. The document is manually maintained.

**Recommended Fix:** Add a freshness sentinel to ERROR-SHAPES.md, or create a script that extracts error shapes from backend source and compares to the document.

---

### Q14: grep -c "Surface" in contract-surfaces.md — what's the count?

**Evidence:** `grep -c "Surface"` returns **12**.

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`

**Artifact:** 12 occurrences of the word "Surface" — 9 in surface headings, 1 in the section header "The 9 Contract Surfaces", 1 in "Surface 5" within the freshness note, 1 in "Surface 9" scope note.

**Status:** Factual result, no action needed.

**Gap:** N/A

**Recommended Fix:** N/A

---

## Q15-Q18: What Claude Code Actually Has

### Q15: List every file in .claude/rules/ with filename, line count, glob patterns.

**Evidence:** 5 rule files, all with YAML frontmatter containing glob patterns.

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/`

**Artifact:**

| File | Lines | Glob Patterns |
|------|-------|---------------|
| `agent-tools.md` | 41 | `apps/agent-api/app/core/langgraph/tools/**`, `apps/agent-api/app/services/**` |
| `backend-api.md` | 36 | `zakops-backend/src/api/**`, `zakops-backend/src/schemas/**`, `zakops-backend/src/services/**` |
| `contract-surfaces.md` | 85 | `packages/contracts/**`, `apps/dashboard/src/lib/*generated*`, `apps/agent-api/app/schemas/*_models.py`, `zakops-backend/src/schemas/*_models.py` |
| `dashboard-types.md` | 27 | `apps/dashboard/src/types/**`, `apps/dashboard/src/lib/**`, `apps/dashboard/src/components/**`, `apps/dashboard/src/hooks/**` |
| `design-system.md` | 91 | `apps/dashboard/src/components/**`, `apps/dashboard/src/app/**`, `apps/dashboard/src/styles/**` |

**Status:** All 5 rules are active and have glob patterns that trigger correctly.

**Gap:** None for the rules themselves. The MEMORY.md AUTOSYNC marker says "5 path-scoped rules" which is accurate.

**Recommended Fix:** N/A

---

### Q16: List every file in .claude/commands/ with filename and first content line.

**Evidence:** 15 command files.

**Path:** `/home/zaks/zakops-agent-api/.claude/commands/`

**Artifact:**

| File | First Content Line |
|------|-------------------|
| `after-change.md` | After-Change Validation |
| `before-task.md` | Before Task — Surface Integrity Gate |
| `check-drift.md` | Check Spec Drift |
| `contract-checker.md` | Contract Surface Checker |
| `hooks-check.md` | Hooks Check |
| `infra-check.md` | Infrastructure Check |
| `permissions-audit.md` | Permissions Audit |
| `prune-allows.md` | Prune Allow Rules — Clean Root Settings |
| `scaffold-feature.md` | Scaffold New Feature |
| `sync-agent-types.md` | Sync Agent Types |
| `sync-all.md` | Sync All Types |
| `sync-backend-types.md` | Sync Backend Types |
| `tripass.md` | TriPass Multi-Agent Pipeline |
| `update-memory.md` | Run the memory sync engine |
| `validate.md` | Full Validation Suite |

**Status:** All 15 commands are present. 6 of them reference local skills via `/home/zaks/.claude/skills/` paths.

**Gap:** The commands that reference skills use the correct `/home/zaks/` path (not `~/`), so they work correctly. However, none reference the frontend-design skill because it doesn't exist in the local skills directory.

**Recommended Fix:** If frontend-design skill is installed, update `scaffold-feature.md` and `implement-feature.md` (in `~/.claude/commands/`) to reference it.

---

### Q17: List every file in ~/.claude/agents/ with filename and target model.

**Evidence:** Initial `ls ~/.claude/agents/` returned "No such file or directory" because Claude runs as root (`~` = `/root/`). Subsequent `find` located the agents at `/home/zaks/.claude/agents/`.

**Path:** `/home/zaks/.claude/agents/` (NOT `/root/.claude/agents/`)

**Artifact:**

| File | Model | Role | Owner |
|------|-------|------|-------|
| `arch-reviewer.md` | opus | Read-only architecture & security reviewer | root:root (BUG) |
| `contract-guardian.md` | sonnet | Read-only contract surface validator | zaks:zaks |
| `test-engineer.md` | sonnet | Writes tests to test dirs only | zaks:zaks |

**Status:** 3 agents exist and are referenced by CLAUDE.md (line 68). All have proper YAML frontmatter with `name`, `description`, `model`, `tools`, `disallowedTools`.

**Gap:**
1. `arch-reviewer.md` is root-owned instead of zaks:zaks.
2. All 3 agents reference skills via `~/.claude/skills/` which resolves to `/root/.claude/skills/` when running as root — **skill preloads are broken**.

**Recommended Fix:**
1. `chown zaks:zaks /home/zaks/.claude/agents/arch-reviewer.md`
2. In all 3 agent files, replace `~/.claude/skills/` with `/home/zaks/.claude/skills/`

---

### Q18: Does /mnt/skills/ exist?

**Evidence:** `ls /mnt/skills/` returns "No such file or directory" (exit code 2).

**Path:** `/mnt/skills/` — does not exist on this WSL machine.

**Artifact:** This path is a convention from hosted/cloud Claude Code environments (Windsurf-style). A reference to it was found in a paste-cache file (old Phase 4 mission prompt). During V6-GUIDE-REGEN-001, all `/mnt/skills/` references were removed from active configs and replaced with `.claude/rules/design-system.md` references. The paste-cache retains the stale reference but it's inert.

**Status:** Dead path. No active configuration references it.

**Gap:** The paste-cache file at `/home/zaks/.claude/paste-cache/499d9d8a8e12174d.txt` still contains `Read /mnt/skills/public/frontend-design/SKILL.md before starting.` — this is a stale reference that could confuse if the paste is reused.

**Recommended Fix:** Delete or update the paste-cache entry. Low priority since paste-cache entries are inert unless manually pasted.

---

## Q19-Q21: Design System Rule Effectiveness

### Q19: Which rules auto-load when editing DealCard.tsx?

**Evidence:** For a file at `apps/dashboard/src/components/deals/DealCard.tsx`:
- `design-system.md` triggers on `apps/dashboard/src/components/**` — MATCH
- `dashboard-types.md` triggers on `apps/dashboard/src/components/**` — MATCH
- `contract-surfaces.md` triggers on `packages/contracts/**` — NO MATCH
- `agent-tools.md` triggers on `apps/agent-api/...` — NO MATCH
- `backend-api.md` triggers on `zakops-backend/...` — NO MATCH

**Path:** Both rules' frontmatter glob patterns (see Q15 artifact).

**Artifact:** 2 rules auto-load: `design-system.md` (design conventions + quality standards) and `dashboard-types.md` (import discipline + type handling).

**Status:** Working correctly. A dashboard component edit gets both architectural convention guidance and type safety rules.

**Gap:** No rule auto-loads the frontend-design SKILL.md or any accessibility/responsive guidance.

**Recommended Fix:** If the frontend-design skill is installed, add a "Skill Preloads" section to `design-system.md` that instructs Claude to read the skill before starting component work.

---

### Q20: Is Category B specific and actionable, or vague?

**Evidence:** Category B contains specific, named guidance across all 7 sections:
- B2 names fonts to avoid (Arial, Inter, Roboto) and prescribes font pairing
- B3 names an anti-pattern (purple gradients on white) and prescribes CSS variables
- B4 names techniques (staggered reveals, scroll-triggered effects, CSS-only preference)
- B5 names patterns (asymmetry, overlap, diagonal flow, grid-breaking)
- B6 names techniques (gradient meshes, subtle textures, layered transparencies)
- B7 lists specific anti-patterns (overused fonts, purple-on-white, cookie-cutter layouts)

**Path:** `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` (lines 49-91)

**Artifact:** 42 lines of design quality guidance within the 91-line file.

**Status:** Specific and actionable — not vague advice.

**Gap:** Compared to the marketplace SKILL.md source, missing:
1. Twelve specific aesthetic tone directions
2. Anti-convergence rule (Space Grotesk example)
3. Light/dark variation instruction
4. Additional texture techniques
5. Motion library recommendation

**Recommended Fix:** Enrich Category B or add skill preload reference (see Q9).

---

### Q21: What design principles would you apply right now without reading files?

**Evidence:** This question tests what's in active context. From the rules that loaded during this session (via prior reads), the following was available:

**Category A (already in context):**
- Promise.allSettled mandatory, Promise.all banned
- Bridge file imports only (@/types/api)
- PIPELINE_STAGES from execution-contracts.ts
- Server-side deal counts
- console.warn for degradation, console.error for unexpected

**Category B (already in context):**
- Avoid Arial/Inter/Roboto
- Cohesive color palette via CSS variables
- Purposeful animations, CSS-only preferred
- Staggered reveals for page loads
- Asymmetry and spatial composition
- No purple-on-white cliches

**Path:** Design-system.md content was in context from prior reads during this audit session.

**Artifact:** N/A (context-awareness test, not a file)

**Status:** Rules are effective at injecting design guidance into active context. Once read (either by auto-load trigger or explicit read), the principles persist in context for the session.

**Gap:** If the first tool call in a session is NOT to a dashboard file, design-system.md doesn't auto-load. The rule is reactive (triggered by file access), not proactive (loaded at session start).

**Recommended Fix:** Consider adding a "design system awareness" note to CLAUDE.md so the principles are always available, or ensure `/before-task` reads design-system.md when dashboard work is anticipated.

---

## Q22-Q24: Capability Awareness

### Q22: What are "frontend plugins" or "skills"? Any reference to /mnt/skills/public/frontend-design/SKILL.md?

**Evidence:** Two systems exist:

1. **Local skills** (`/home/zaks/.claude/skills/*/SKILL.md`): 7 directories, each with a single SKILL.md. Plain markdown, no YAML frontmatter, no trigger conditions. Referenced by commands and agent definitions.

2. **Plugin marketplace** (`/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/`): Cloned from `anthropics/claude-plugins-official` on Jan 12, 2026. Contains `frontend-design` plugin with proper frontmatter. NOT activated.

The `/mnt/skills/public/frontend-design/SKILL.md` reference was found in a single paste-cache file — a Phase 4 mission prompt from a prior session. This path convention is for hosted Claude Code environments and does not exist on this machine.

**Path:**
- Local skills: `/home/zaks/.claude/skills/`
- Marketplace: `/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/`
- Dead reference: `/home/zaks/.claude/paste-cache/499d9d8a8e12174d.txt` (line 24)

**Artifact:** The paste-cache line: `**Read /mnt/skills/public/frontend-design/SKILL.md before starting.**`

**Status:** The `/mnt/skills/` path is dead. The marketplace plugin is inert. Local skills work but lack a frontend-design entry.

**Gap:** No active mechanism delivers frontend-design skill content to Claude Code sessions. The knowledge exists in two places (marketplace SKILL.md and design-system.md Category B) but neither is fully utilized.

**Recommended Fix:** Install the frontend-design skill to the local skills directory and reference it from design-system.md and relevant commands.

---

### Q23: Search for /mnt/skills references in config files.

**Evidence:** `grep -r "/mnt/skills" ~/.claude/ .claude/` found:
- `/home/zaks/.claude/paste-cache/499d9d8a8e12174d.txt` (line 24) — stale mission prompt
- Several lines in conversation JSONL logs (prior session history) — not active config

Zero matches in active configuration files (settings.json, CLAUDE.md, rules, commands, agents).

**Path:** Only in paste-cache and conversation logs.

**Artifact:** CHANGES.md confirms cleanup: "Removed all `/mnt/skills/` references from: tripass.sh, TRIPASS_SOP.md, tripass.md command, MEMORY.md" during V6-GUIDE-REGEN-001.

**Status:** All active references were removed. Only inert residue remains in paste-cache and conversation logs.

**Gap:** Paste-cache entry still exists. Very low risk but could cause confusion if reused.

**Recommended Fix:** Optional: delete the paste-cache entry. Not urgent.

---

### Q24: Search for "frontend-design" or "SKILL.md" references.

**Evidence:** Grep found references in three categories:

1. **Commands referencing local skills** (ACTIVE):
   - `implement-feature.md` → `~/.claude/skills/api-conventions/SKILL.md`, `code-style/SKILL.md`
   - `fix-bug.md` → `~/.claude/skills/debugging-playbook/SKILL.md`
   - `add-endpoint.md` → `~/.claude/skills/api-conventions/SKILL.md`
   - `investigate.md` → `~/.claude/skills/debugging-playbook/SKILL.md`
   - `audit-code.md` → `~/.claude/skills/code-style/SKILL.md`, `api-conventions`, `security-and-data`

2. **Marketplace plugin files** (INERT):
   - `marketplace.json` entry for `frontend-design`
   - `plugin.json` for `frontend-design`
   - `SKILL.md` at `plugins/frontend-design/skills/frontend-design/SKILL.md`

3. **Paste-cache** (STALE):
   - Single reference to `/mnt/skills/public/frontend-design/SKILL.md`

**Path:** Commands in `/home/zaks/.claude/commands/`, marketplace in `/home/zaks/.claude/plugins/marketplaces/`

**Artifact:** 6 commands reference 4 different local skills. Zero commands reference `frontend-design`.

**Status:** The command → skill wiring works for existing skills. Frontend-design has no wiring anywhere.

**Gap:** `frontend-design` exists in the marketplace but has zero references from any active command, rule, or agent definition. It is completely disconnected from the workflow.

**Recommended Fix:** After installing to local skills, add references from `scaffold-feature.md` and any future frontend-specific commands.

---

## Q25-Q27: Gap Discovery

### Q25: Do you have guidance on accessibility, responsive breakpoints, Tailwind conventions, component composition, state management?

**Evidence:**

| Area | Guidance? | Source |
|------|-----------|--------|
| Accessibility standards | **No** | No rule, no skill. General knowledge from training only. |
| Responsive breakpoints | **No** | `tailwind.config.ts` exists but no rule documents the breakpoints. |
| Tailwind utility conventions | **Partial** | No explicit rule. Observed from existing codebase patterns. |
| Component composition | **Partial** | design-system.md covers data-fetching and imports but NOT component splitting (server vs client), prop drilling, or context patterns. |
| State management | **No** | No rule. Training knowledge + codebase observation only. |

**Path:** Not applicable — these are areas where no path exists.

**Artifact:** N/A

**Status:** For these 5 frontend concerns, Claude Code operates primarily from training knowledge and codebase pattern-matching, with only partial guidance from design-system.md on data-fetching patterns.

**Gap:** All 5 are gaps. The most impactful are:
1. Accessibility — no WCAG compliance guidance, no contrast ratio rules, no ARIA patterns
2. Component composition — no guidance on server/client component boundaries, a common source of Next.js bugs
3. Responsive breakpoints — Tailwind config exists but isn't surfaced in rules

**Recommended Fix:**
1. Create `accessibility.md` rule scoped to dashboard component paths
2. Add component composition patterns to design-system.md or a new `component-patterns.md` rule
3. Add Tailwind breakpoint reference to design-system.md Category A

---

### Q26: Do you have guidance on animation performance, color contrast, dark mode, z-index management?

**Evidence:**

| Area | Guidance? | Source |
|------|-----------|--------|
| Animation performance (GPU vs layout) | **Partial** | design-system.md says "prefer CSS-only solutions." No guidance on `transform`/`opacity` (GPU-composited) vs `width`/`height` (layout-triggering). Training knowledge fills the gap. |
| Color contrast ratios | **No** | No WCAG contrast guidance anywhere in rules or skills. |
| Dark mode implementation | **No** | design-system.md mentions "CSS variables for theme" but no dark mode strategy, variable naming convention, or toggle mechanism. |
| z-index management | **No** | No z-index scale, layering system, or stacking context documentation. |

**Path:** design-system.md (B4) for animation; nothing else.

**Artifact:** design-system.md line 69: "Prefer CSS-only solutions where possible for performance" — the only animation performance guidance.

**Status:** 1 of 4 areas has partial coverage. The rest are completely uncovered.

**Gap:** These are common sources of frontend bugs:
- Layout-triggering animations cause jank
- Failing contrast ratios make UI inaccessible
- Dark mode without a strategy creates inconsistent experiences
- z-index wars across components cause overlapping/hidden elements

**Recommended Fix:**
1. Add GPU-composited property list to design-system.md B4 (`transform`, `opacity`, `filter` — prefer these for animations)
2. Add WCAG AA contrast requirement to accessibility rule (when created)
3. Add dark mode strategy section to design-system.md
4. Define a z-index scale (e.g., base: 0, dropdown: 100, modal: 200, toast: 300, overlay: 400)

---

### Q27: What do you wish you had access to for frontend work?

**Evidence:** Based on this audit, the following gaps are identified with specificity:

| Gap | Impact | What Would Fix It |
|-----|--------|-------------------|
| `frontend-design` plugin not activated | Design quality guidance is condensed/partial | Copy to `~/.claude/skills/frontend-design/` |
| No accessibility rule | Accessible code depends on training, not project-specific standards | Create `accessibility.md` rule |
| No responsive/breakpoint rule | Tailwind breakpoints exist in config but not in rules | Add to design-system.md |
| Playwright MCP disabled | No visual verification of UI work | Set `"disabled": false` in settings.json |
| No component pattern guide | Server/client split, loading states, error boundaries improvised | Create `component-patterns.md` rule |
| Stale infra-snapshot | Manifest shows 0/5 surfaces, doesn't know about S8/S9 | Update manifest generator |
| No z-index scale | Stacking context conflicts go undetected | Add to design-system.md |
| No dark mode strategy | Theme implementation is ad-hoc | Add to design-system.md |

**Path:** Various (see individual gap entries above)

**Artifact:** This audit document serves as the artifact.

**Status:** Multiple gaps exist across frontend tooling, rules, and validation.

**Gap:** See table above — 8 distinct gaps identified.

**Recommended Fix:** A mission prompt addressing all 8 gaps in priority order. See [Recommended Mission Structure](#recommended-mission-structure).

---

## Q28-Q30: Local Skills Inventory

### Q28: Full directory listing of ~/.claude/skills/

**Evidence:** 7 directories, each containing a single `SKILL.md` file. All owned by `zaks:zaks`. All created within a 90-second window on Feb 1, 2026.

**Path:** `/home/zaks/.claude/skills/`

**Artifact:**

| Skill | Modified | Size | Owner | Contents |
|-------|----------|------|-------|----------|
| `api-conventions` | 2026-02-01 19:35:31 | 2537B | zaks:zaks | SKILL.md only |
| `atomic-workflow` | 2026-02-01 19:34:43 | 1983B | zaks:zaks | SKILL.md only |
| `code-style` | 2026-02-01 19:35:45 | 2313B | zaks:zaks | SKILL.md only |
| `debugging-playbook` | 2026-02-01 19:35:15 | 3237B | zaks:zaks | SKILL.md only |
| `project-context` | 2026-02-01 19:34:30 | 2738B | zaks:zaks | SKILL.md only |
| `security-and-data` | 2026-02-01 19:35:58 | 2070B | zaks:zaks | SKILL.md only |
| `verification-standards` | 2026-02-01 19:34:56 | 2110B | zaks:zaks | SKILL.md only |

No subdirectories, no config files, no symlinks.

**Status:** All 7 skills are present and referenced by commands and agent definitions.

**Gap:** No `frontend-design` skill in this directory despite the plugin existing on disk.

**Recommended Fix:** Install frontend-design as the 8th skill (see Q34).

---

### Q29: First 5 lines of each SKILL.md — what's the structure pattern?

**Evidence:** All 7 skills follow the same pattern: plain markdown with `# Title` → `## First Section`. None have YAML frontmatter (`---` delimiters with `name:`, `description:`, `trigger:`).

**Artifact:**

| Skill | Line 1 | Line 3 (first section) | Has Frontmatter? |
|-------|--------|----------------------|-----------------|
| `api-conventions` | `# API Conventions` | `## Backend API (FastAPI, port 8091)` | No |
| `atomic-workflow` | `# Atomic Workflow` | `## Atomic Task Block (required before every edit)` | No |
| `code-style` | `# Code Style` | `## Python (Backend + Agent API)` | No |
| `debugging-playbook` | `# Debugging Playbook` | `## "Is It Running?" Diagnostic Sequence` | No |
| `project-context` | `# Project Context — ZakOps` | `## What ZakOps Is` | No |
| `security-and-data` | `# Security and Data` | `## Secret Files (NEVER edit, commit, or print contents)` | No |
| `verification-standards` | `# Verification Standards` | `## What Counts as Evidence` | No |

Compare to the marketplace `frontend-design/SKILL.md` which HAS frontmatter:
```yaml
---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces...
license: Complete terms in LICENSE.txt
---
```

**Status:** Local skills are reference documents, not self-describing skills. They lack metadata that would enable automated discovery or trigger conditions.

**Gap:** No self-describing metadata means skills can only be loaded by explicit path reference. There's no mechanism for automatic skill selection based on task context.

**Recommended Fix:** Low priority — the current explicit-reference model works. If automated discovery is desired later, add frontmatter to all skills.

---

### Q30: How were the 7 skills installed?

**Evidence:** All 7 skills were created on Feb 1, 2026, within a 90-second window (19:34:30 to 19:35:58). All owned by `zaks:zaks`. No install log, no marketplace pull, no package manager command. No reference in MEMORY.md.

**Path:** `/home/zaks/.claude/skills/` (all files, `stat` timestamps)

**Artifact:** Timestamps confirm batch creation. CHANGES.md has a matching entry from that date referencing skill creation during a Claude Code session.

**Status:** Manually created by Claude Code during a development session on Feb 1. The creation pattern (7 files in 90 seconds, all markdown, consistent structure) indicates a single Claude Code session generated them all.

**Gap:** No install mechanism, no version tracking, no update path. If the skills need to be updated, there's no way to sync them from a source of truth.

**Recommended Fix:** Low priority — skills change infrequently. Consider adding a `skills-manifest.json` if version tracking becomes important.

---

## Q31-Q34: The Inert Frontend-Design Plugin

### Q31: Exact path and directory listing of frontend-design SKILL.md.

**Evidence:** Full path:
```
/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md
```

Directory listing:
```
drwxrwxr-x 2 zaks zaks 4096 Jan 12 00:11 .
drwxrwxr-x 3 zaks zaks 4096 Jan 12 00:11 ..
-rw-rw-r-- 1 zaks zaks 4274 Jan 12 00:11 SKILL.md
```

Parent structure:
```
frontend-design/
├── .claude-plugin/plugin.json
├── README.md
└── skills/frontend-design/SKILL.md
```

**Path:** See above.

**Artifact:** Single file, 4274 bytes, 42 lines, created Jan 12 as part of marketplace clone.

**Status:** Present on disk, never activated.

**Gap:** Plugin activation mechanism is unclear — no `plugins.json`, no activation flag found anywhere.

**Recommended Fix:** Copy the SKILL.md to local skills (see Q34).

---

### Q32: Full contents of the marketplace SKILL.md.

**Evidence:** 42 lines with YAML frontmatter. Full structure:

1. **Frontmatter** (lines 1-5): name, description, license
2. **Intro** (lines 7-9): "distinctive, production-grade frontend interfaces that avoid generic AI slop aesthetics"
3. **Design Thinking** (lines 11-19): Purpose, Tone (12+ directions), Constraints, Differentiation. CRITICAL principle.
4. **Implementation list** (lines 21-25): production-grade, visually striking, cohesive, meticulously refined
5. **Frontend Aesthetics Guidelines** (lines 27-34): Typography, Color & Theme, Motion, Spatial Composition, Backgrounds & Visual Details
6. **Anti-pattern block** (line 36): Inter, Roboto, Arial banned; purple gradients banned
7. **Anti-convergence** (line 38): "NEVER converge on common choices (Space Grotesk)"
8. **Complexity matching** (line 40): maximalist = elaborate code; minimalist = precision + restraint
9. **Closing** (line 42): "Claude is capable of extraordinary creative work"

**Path:** `/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`

**Artifact:** Full file read and verified.

**Status:** Complete, well-structured, production-quality skill definition.

**Gap:** Not accessible to Claude Code during sessions.

**Recommended Fix:** Install to local skills directory.

---

### Q33: Comparison — marketplace SKILL.md vs design-system.md Category B.

**Evidence:** Detailed line-by-line comparison:

| Topic | Marketplace SKILL.md | design-system.md Category B | Delta |
|-------|---------------------|---------------------------|-------|
| Typography | Avoid Arial, Inter; pair distinctive display + refined body | Avoid Arial, Inter, Roboto; pair display + complementary body | **Near-identical** |
| Color | CSS variables, dominant colors + sharp accents | CSS variables, dominant colors + purposeful accents | **Near-identical** |
| Motion | animation-delay, scroll-triggering, **Motion library for React** | staggered reveals, scroll-triggered, CSS-only preferred | Category B misses **Motion library** |
| Spatial | Asymmetry, Overlap, Diagonal flow, Grid-breaking | Same list but hedged with "Consider" | **Near-identical** (SKILL.md more assertive) |
| Backgrounds | gradient meshes, **noise textures**, geometric patterns, layered transparencies, **dramatic shadows**, **decorative borders**, **custom cursors**, **grain overlays** | gradient meshes, subtle textures, layered transparencies | Category B misses **5 specific techniques** |
| Tone directions | **12+ named options**: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian | "Commit to an aesthetic direction" — no specific options | **Major gap** in Category B |
| Anti-convergence | "NEVER converge on common choices (Space Grotesk, for example) across generations" | Not present | **Missing from Category B** |
| Variation | "No design should be the same. Vary between light and dark themes, different fonts, different aesthetics" | Not present | **Missing from Category B** |
| AI slop framing | Explicit "avoid generic AI slop aesthetics" | "should not look like they came from the same template" | SKILL.md more forceful |
| Closing motivation | "Claude is capable of extraordinary creative work. Don't hold back" | "Match implementation complexity to the aesthetic vision" | Both present, different emphasis |

**Summary:** ~70% overlap. Category B is a condensed, restructured derivative. The marketplace SKILL.md has **4 items Category B completely lacks** and is more assertive in its language.

**Status:** Category B is functional but incomplete relative to its source.

**Gap:** Category B lacks tone palette, anti-convergence, variation instruction, and several specific techniques.

**Recommended Fix:** Either:
1. **Option A:** Enrich Category B with the missing content (adds ~15 lines, keeps everything in one place)
2. **Option B:** Install the skill and add a preload reference to design-system.md (keeps rule lean, skill has full content)
3. **Option C:** Both — install skill AND enrich Category B with critical items (belt and suspenders)

---

### Q34: What would it take to activate the frontend-design skill?

**Evidence:** There is no plugin activation registry on this machine. No `plugins.json`, no `plugin-state.json`, no activation flag in settings.json. The marketplace was cloned but no plugin was ever formally activated from it.

**Path:** No activation mechanism found at:
- `/home/zaks/.claude/plugins.json` — doesn't exist
- `/home/zaks/.claude/installed-plugins*` — doesn't exist
- `/home/zaks/.claude/plugin-state*` — doesn't exist
- `/home/zaks/.claude/settings.json` — no plugin references

**Artifact:** `known_marketplaces.json` confirms the marketplace is cloned, but it's just a repository — not an activation registry.

**Status:** The simplest activation is to copy the skill to the local directory:

```bash
cp -r /home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design \
      /home/zaks/.claude/skills/frontend-design
chown -R zaks:zaks /home/zaks/.claude/skills/frontend-design
```

Then reference it from design-system.md:
```markdown
## Skill Preloads
Read `/home/zaks/.claude/skills/frontend-design/SKILL.md` before starting component work.
```

**Gap:** No action has been taken. The skill remains inert.

**Recommended Fix:** Execute the copy command and add the preload reference. Takes 2 commands and 1 rule edit.

---

## Q35-Q37: Missing Agents Directory

### Q35: Was ~/.claude/agents/ ever created?

**Evidence:** The directory exists at `/home/zaks/.claude/agents/`, NOT at `/root/.claude/agents/` (which is what `~/.claude/agents/` resolves to when Claude runs as root).

The initial `ls ~/.claude/agents/` returned "No such file or directory" — a false negative caused by root user context. `find /home/zaks -name "arch-reviewer.md"` located the files correctly.

3 agent files exist:
- `arch-reviewer.md` — created 2026-02-09 18:31, root-owned
- `contract-guardian.md` — created 2026-02-09 17:46, zaks-owned
- `test-engineer.md` — created 2026-02-09 17:49, zaks-owned

**Path:** `/home/zaks/.claude/agents/`

**Artifact:** All three agents have full YAML frontmatter and structured markdown bodies. Created during V6-GUIDE-REGEN-001 on Feb 9, 2026.

**Status:** The directory and agents exist. The false negative was a root-user path resolution issue, not a missing directory.

**Gap:** The root vs zaks home directory confusion is a recurring WSL hazard. `~/.claude/` resolves differently for root (Claude) vs zaks (the user).

**Recommended Fix:** In all documentation and agent definitions, use absolute paths (`/home/zaks/.claude/`) instead of `~/`.

---

### Q36: Did TriPass or V6-GUIDE-REGEN-001 create these agent files?

**Evidence:** All three agents were created on Feb 9, 2026 — the same day as V6-GUIDE-REGEN-001 and related missions. CLAUDE.md (line 68) references all three: `/contract-guardian` (sonnet), `/arch-reviewer` (opus), `/test-engineer` (sonnet).

`find` confirmed the files exist at `/home/zaks/.claude/agents/`:
```
/home/zaks/.claude/agents/arch-reviewer.md
/home/zaks/.claude/agents/contract-guardian.md
/home/zaks/.claude/agents/test-engineer.md
```

**Path:** `/home/zaks/.claude/agents/`

**Artifact:** 3 fully-formed agent definitions with:
- YAML frontmatter (name, description, model, tools, disallowedTools)
- Structured body (purpose, what to analyze, output format, rules, skill preloads)
- Tool restrictions (arch-reviewer and contract-guardian are read-only; test-engineer can write to test dirs)

**Status:** Agents are correctly located and properly defined.

**Gap:** None for file location. But see Q37 for skill preload path bug.

**Recommended Fix:** N/A for location (resolved).

---

### Q37: Are there dead references to ~/.claude/agents/ in active config?

**Evidence:** CLAUDE.md (line 68) references agents as `/contract-guardian`, `/arch-reviewer`, `/test-engineer` — these are slash-command invocations, not path references. Claude Code resolves them by looking in `.claude/agents/` relative to the project root or user home.

`settings.json` has no reference to the agents directory.

However, all 3 agent definitions contain broken skill preload paths:

```markdown
## Skill Preloads
Read these skills before starting:
- ~/.claude/skills/api-conventions
- ~/.claude/skills/security-and-data
- ~/.claude/skills/project-context
```

Since agents run as root, `~/.claude/skills/` resolves to `/root/.claude/skills/` which does NOT exist. Skills are at `/home/zaks/.claude/skills/`.

**Path:**
- `/home/zaks/.claude/agents/arch-reviewer.md` (lines 94-97)
- `/home/zaks/.claude/agents/contract-guardian.md` (lines 64-66)
- `/home/zaks/.claude/agents/test-engineer.md` (lines 94-96)

**Artifact:** All three agent files contain `~/.claude/skills/` references that resolve to the wrong directory.

**Status:** Skill preloads in all 3 agent definitions are **broken**. When an agent is invoked, it's told to read skills from a non-existent path.

**Gap:** Critical path bug affecting all 3 agents. Agents cannot access their designated skills.

**Recommended Fix:**
1. Replace `~/.claude/skills/` with `/home/zaks/.claude/skills/` in all 3 agent files.
2. Fix `arch-reviewer.md` ownership: `chown zaks:zaks /home/zaks/.claude/agents/arch-reviewer.md`

---

## Master Gap Registry

All gaps identified in this audit, consolidated and prioritized:

### Priority 1 — Broken Functionality

| # | Gap | Affected | Impact | Fix |
|---|-----|----------|--------|-----|
| G1 | Agent skill preload paths use `~/` (resolves to `/root/`) | All 3 agents | Agents can't read skills | Replace with `/home/zaks/.claude/skills/` in 3 files |
| G2 | `arch-reviewer.md` root-owned | arch-reviewer agent | Potential permission issues | `chown zaks:zaks` |
| G3 | `validate-contract-surfaces.sh` says "7" but project has 9 | Surface validation | Misleading, S8/S9 not checked in unified script | Update script or wire S9 into Makefile |
| G4 | `validate-surface9.sh` not in any Makefile target | Surface 9 | Never runs automatically | Add to `make validate-full` |
| G5 | Infra-snapshot shows 0/5 surfaces, says "Rules: 0" | Manifest | Completely stale, misleading | Rewrite manifest generator |

### Priority 2 — Missing Capability

| # | Gap | Affected | Impact | Fix |
|---|-----|----------|--------|-----|
| G6 | `frontend-design` skill not installed | Frontend work quality | Design guidance is condensed/partial | Copy to `/home/zaks/.claude/skills/` |
| G7 | Playwright MCP disabled | Visual testing | Can't verify UI output | Set `"disabled": false` in settings.json |
| G8 | No accessibility rule | Dashboard a11y | No WCAG guidance, no contrast rules | Create `accessibility.md` rule |
| G9 | No component pattern guide | Dashboard components | Server/client split, loading states improvised | Create `component-patterns.md` rule or add to design-system.md |
| G10 | No responsive breakpoint documentation in rules | Responsive design | Tailwind config not surfaced to Claude | Add breakpoint reference to design-system.md |

### Priority 3 — Incomplete Coverage

| # | Gap | Affected | Impact | Fix |
|---|-----|----------|--------|-----|
| G11 | design-system.md Category B missing 4 items from source | Design quality | Tone palette, anti-convergence, variation, textures lost | Enrich or add skill preload |
| G12 | No z-index management scale | CSS layering | Stacking context conflicts | Define scale in design-system.md |
| G13 | No dark mode strategy | Theme implementation | Ad-hoc theme switching | Add strategy to design-system.md |
| G14 | No animation performance guidance (GPU vs layout) | Performance | Layout-triggering animations cause jank | Add to design-system.md B4 |
| G15 | ENV-CROSSREF.md not validated | Cross-service env vars | Silent env drift | Consider formal surface or validation script |
| G16 | ERROR-SHAPES.md not validated | Error shape consistency | Can go stale | Consider freshness sentinel |
| G17 | Surface count inconsistency (9/7/5 across artifacts) | Trust in validation | Misleading counts | Align all artifacts to 9 |
| G18 | No state management pattern guide | Dashboard state | Context vs hooks improvised | Add guidance |

### Priority 4 — Cosmetic / Low Risk

| # | Gap | Affected | Impact | Fix |
|---|-----|----------|--------|-----|
| G19 | Stale `/mnt/skills/` ref in paste-cache | Paste reuse | Could confuse if pasted | Delete paste-cache entry |
| G20 | Skills lack YAML frontmatter | Skill discovery | No automated trigger matching | Add frontmatter if auto-discovery wanted |
| G21 | No skill version tracking | Skill updates | No way to detect drift | Add `skills-manifest.json` if needed |

---

## Recommended Mission Structure

Based on this audit, the following mission phases address the gaps in priority order:

### Phase 1: Fix Broken (G1-G5)
- Fix 3 agent skill preload paths → `/home/zaks/.claude/skills/`
- Fix `arch-reviewer.md` ownership
- Wire `validate-surface9.sh` into `make validate-full`
- Update `validate-contract-surfaces.sh` header to say "9"
- Rewrite manifest generator's surface detection for all 9

### Phase 2: Install Frontend Tooling (G6-G7)
- Copy `frontend-design` skill to local skills directory
- Enable Playwright MCP
- Add skill preload reference to `design-system.md`

### Phase 3: Create Missing Rules (G8-G10)
- Create `accessibility.md` rule (WCAG AA, contrast, ARIA, focus management)
- Create `component-patterns.md` rule (server/client split, loading states, error boundaries)
- Add responsive breakpoint reference to `design-system.md`

### Phase 4: Enrich Design System (G11-G14)
- Add tone palette to design-system.md B1
- Add anti-convergence rule to B7
- Add z-index scale
- Add dark mode strategy
- Add GPU-composited animation guidance to B4

### Phase 5: Strengthen Validation (G15-G18)
- Add env var cross-reference check to `make validate-live`
- Add error shape freshness sentinel
- Align surface count across all artifacts
- Add state management patterns

### Acceptance Criteria
- [ ] All 3 agents can resolve their skill preloads
- [ ] `make validate-full` checks all 9 surfaces
- [ ] `make infra-snapshot` detects all 9 surfaces accurately
- [ ] `frontend-design` skill installed and referenced
- [ ] Playwright MCP enabled
- [ ] New rules auto-load for dashboard component paths
- [ ] Boot diagnostics CHECK 2 verifies surface count in validation scripts too
- [ ] All file ownership is `zaks:zaks`

---

*Document generated by Claude Opus 4.6 during interactive audit session, 2026-02-10.*
*Place: /home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md*

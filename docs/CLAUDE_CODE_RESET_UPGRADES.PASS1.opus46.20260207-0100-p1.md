# CLAUDE CODE BRAIN RESET — Best-in-Class Upgrade Pack (PASS 1)

```
AGENT IDENTITY
agent_name:    opus46
run_id:        20260207-0100-p1
date_time:     2026-02-07T01:00:00Z
pass:          1 of 3 (Research & Benchmark)
input:         MISSION-INFRA-AWARENESS-V5-CLAUDE-CODE-RESET.md (1,113 lines)
repos_scanned: zakops-backend, zakops-agent-api, Zaks-llm, ~/.claude/
```

---

## 1. WHAT THE V5 MISSION DOES WELL

The V5 mission prompt is **remarkably thorough** in its domain-specific infrastructure awareness. Credit where due:

| # | Strength | Why It Matters |
|---|----------|---------------|
| S-1 | **All 7 contract surfaces documented** | Complete enumeration: Backend→Dashboard, Agent→Backend SDK, Agent OpenAPI, Dashboard←Agent, Backend→RAG SDK, MCP Tool Schemas, SSE Event Schema. No codegen surface is missing. |
| S-2 | **Makefile-as-contract philosophy** | `sync-types`, `sync-backend-models`, `sync-agent-types`, `sync-rag-models`, `sync-all-types`, `validate-local`, `validate-live` — composable, CI-friendly targets. |
| S-3 | **CLAUDE.md template is comprehensive** | Services table, databases table, 7 contract surfaces table, dependency graph, pre/post task protocols, non-negotiable rules — all in one CLAUDE.md rewrite. |
| S-4 | **Bridge file + ESLint enforcement pattern** | `types/api.ts` and `types/agent-api.ts` bridge pattern with ESLint `no-restricted-imports` is a solid architectural decision from EXEC-001. |
| S-5 | **Pre/post task protocol** | "Before ANY change, run `make validate-local`; After ANY change, run affected `sync-*` target then `make validate-local` again" — disciplined feedback loop. |
| S-6 | **Cross-layer validation expansion** | Expanding from 1/7 to 7/7 contract surface coverage is the correct scope. |
| S-7 | **deal_tools.py migration tracked** | 39→0 `.get()` patterns, 8→0 `response.json()` — the typed SDK migration is documented as fait accompli. |
| S-8 | **Dependency graph with parallel tracks** | Recognizes Backend→Dashboard and Agent→Dashboard are parallel but share a consumer. |
| S-9 | **spec-freshness-bot as CI automation** | Concept of automated spec drift detection via GitHub Actions is forward-thinking. |
| S-10 | **Explicit file-by-file output spec** | Every fix lists exact files to create/modify. No ambiguity about deliverables. |

**Overall Grade: B+** — Excellent domain awareness, but treats Claude Code as a dumb text editor that only reads CLAUDE.md. Misses the entire 2026 Claude Code capability stack.

---

## 2. GAPS — What V5 Misses

### 2.1 Critical Gaps (V5 literally doesn't know these features exist)

| # | Gap | Impact | Evidence |
|---|-----|--------|----------|
| G-1 | **No contract-specific subagents** | 4 agents exist in `Zaks-llm/.claude/agents/` (zakops-prime, agent-config-consultant, log-monitor, research-gemini) but NONE are infrastructure/contract-aware. Main project scope (`/home/zaks/.claude/agents/`) is EMPTY. No agent knows about 7 contract surfaces, codegen pipelines, or drift detection. V5 doesn't propose any. | `ls /home/zaks/.claude/agents/` → empty; Zaks-llm has 4 agents (583 lines) but domain-specific (deals, config, logs, research) |
| G-2 | **No project-level MCP configuration** | ZakOps MCP server runs on port 9100. Gmail MCP and Crawl4AI RAG MCP are configured in `settings.local.json`. But no project `.mcp.json` exists to give Claude Code direct tool access to the ZakOps MCP or PostgreSQL for schema inspection. V5 doesn't mention MCP integration. | `settings.local.json` has mcp__gmail__* and mcp__crawl4ai-rag__* but no ZakOps MCP or PostgreSQL MCP |
| G-3 | **No permission DENY rules for generated files** | `settings.local.json` has extensive ALLOW rules (50+ Bash commands, WebSearch, WebFetch, MCP) but zero DENY rules. Generated files (`*.generated.ts`, `*_models.py`) can be hand-edited, causing drift. V5 doesn't address this. | Current settings: allow-only, no deny |
| G-4 | **No LSP/Code Intelligence configuration** | Claude Code 2026 has built-in LSP tool for jump-to-definition, find-references, and real-time type errors. `typescript-lsp` plugin IS installed in marketplace but not enabled/configured for ZakOps. Essential for a typed codebase with 7 codegen surfaces. V5 doesn't mention it. | `typescript-lsp` plugin present in `/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/` but not activated |
| G-5 | **Plugins installed but not leveraged** | 10+ plugins installed (agent-sdk-dev, typescript-lsp, frontend-design, hookify, etc.) but V5 doesn't acknowledge or build on them. Hookify plugin alone has 60+ files for rule-engine hooks management. | `ls .claude/plugins/marketplaces/claude-plugins-official/` → 10+ plugins |

### 2.2 Structural Gaps (V5 has the concept but the approach is suboptimal)

| # | Gap | V5 Approach | Better Approach |
|---|-----|-------------|-----------------|
| G-6 | **CLAUDE.md too long (~300 lines proposed)** | Puts everything in one CLAUDE.md — services, databases, contracts, dependency graph, protocols, rules | 2026 best practice: CLAUDE.md as "Project Constitution" (~100-150 lines) pointing to skill files for details. V5's template would hit the 200-line read truncation limit. |
| G-7 | **Skills system exists but V5 ignores it** | V5 doesn't acknowledge the existing 7 skills (720 lines). Its CLAUDE.md rewrite would duplicate `project-context/SKILL.md` content. | Should extend skills, not duplicate them. Add `contract-surfaces/SKILL.md`, `codegen-pipeline/SKILL.md`. |
| G-8 | **Commands exist but V5 only adds 1** | V5 adds `.claude/commands/infra-check.md` update. 12 commands already exist (254 lines). No new commands for `sync-types`, `validate-contracts`, `check-drift`. | Add 4-5 new commands: `/sync-types`, `/validate`, `/contract-drift`, `/topology`, `/pre-flight`. |
| G-9 | **Hooks underutilized (2 of ~4 patterns)** | V5 only mentions git pre-commit hook. 2 hooks exist (pre-edit secret blocker, post-edit formatter). | Add: PostToolUse hook on contract file edits → auto-validate. PreToolUse for Bash → block destructive docker commands. |
| G-10 | **No sandbox configuration** | V5 doesn't address sandbox settings at all. | Configure sandbox with `allowedDomains` for GitHub/npm, exclude `docker` from sandbox, enable `autoAllowBashIfSandboxed`. |

### 2.3 Missing Modern Features

| # | Gap | What It Is | ZakOps Benefit |
|---|-----|-----------|---------------|
| G-11 | **No `fileSuggestion` configuration** | Custom @ autocomplete for file picker. | Prioritize contract files, bridge files, and generated types in autocomplete suggestions. |
| G-12 | **No `statusLine` configuration** | Terminal status line showing context during work. | Show current branch, contract drift status, service health in real-time. |
| G-13 | **No compaction instructions** | Custom summarization prompt for long sessions. | Ensure contract surface knowledge survives context compaction. |
| G-14 | **No `additionalDirectories`** | Claude Code can be granted access to directories outside CWD. | When working in zakops-agent-api, also need access to zakops-backend and Zaks-llm. |
| G-15 | **Memory files not leveraged** | `/root/.claude/projects/*/memory/MEMORY.md` persists across sessions. | Should include contract surface state, last validated timestamps, known drift status. |

---

## 3. 2026 BEST PRACTICES — What the Community Does

### 3.1 CLAUDE.md as Constitution (Progressive Disclosure)

**Source:** [builder.io/blog/claude-code-best-practices](https://www.builder.io/blog/claude-code-best-practices), [code.claude.com/docs](https://code.claude.com/docs/en/memory)

The 2026 consensus is: **CLAUDE.md should be a constitution, not an encyclopedia**.

```
CLAUDE.md (~100-150 lines)
├── Identity: What this project IS (3-5 lines)
├── Architecture: Service map table (10 lines)
├── Non-negotiable rules (10 lines)
├── Pointers to skills: "See .claude/skills/X for details"
├── Pre/post task protocol (5 lines)
└── Contract surface quick-reference table (15 lines)

.claude/skills/ (detailed knowledge, loaded on demand)
├── project-context/SKILL.md — Full service topology
├── contract-surfaces/SKILL.md — 7 surfaces + codegen details
├── codegen-pipeline/SKILL.md — Makefile targets + how they work
└── debugging-playbook/SKILL.md — Troubleshooting guides
```

Why: Claude Code reads ALL CLAUDE.md content into the system prompt every turn. A 300-line CLAUDE.md wastes ~3,000 tokens per turn. Skills are loaded on demand.

### 3.2 Custom Subagents for Specialized Tasks

**Source:** [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents), [pubnub.com/blog/best-practices-for-claude-code-sub-agents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)

Subagents run in isolated context windows with custom system prompts and tool access. Best-in-class setups include:

```yaml
# .claude/agents/contract-checker.md
---
name: contract-checker
description: Validate that all 7 contract surfaces are aligned after code changes
model: haiku  # Fast, cheap for validation
---
You are a contract surface validation agent for ZakOps.
Run `make validate-local` and report any failures...
```

**Pipeline architecture** (from pubnub.com):
1. **Explorer agent** (haiku) — Reads codebase, identifies affected surfaces
2. **Implementer agent** (opus) — Makes changes
3. **Validator agent** (haiku) — Runs `make validate-local`, checks drift
4. **Reviewer agent** (sonnet) — Reviews diff against patterns

### 3.3 MCP Server Integration

**Source:** [builder.io/blog/best-mcp-servers-2026](https://www.builder.io/blog/best-mcp-servers-2026), [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

ZakOps should configure 3 MCP servers:

1. **ZakOps MCP Server** (already running on port 9100!) — Give Claude Code direct tool access to deal operations, bypassing HTTP round-trips for exploration tasks.

2. **PostgreSQL MCP** (read-only) — Direct schema inspection for all 3 databases. Enables Claude to verify migration state, check table schemas, validate contract alignment without running separate SQL commands.
   - Source: [github.com/crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp)

3. **GitHub MCP** — PR creation, issue tracking, code review directly from Claude Code.
   - Source: Official Anthropic marketplace plugin

### 3.4 Hooks as Contract Enforcement

**Source:** [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks), [Claude Code Infrastructure Showcase (diet103)](https://github.com/diet103/claude-code-infrastructure)

Current hooks (2 scripts) are basic. 2026 best practice:

| Hook | Trigger | Action |
|------|---------|--------|
| PreToolUse: Edit/Write | Any file edit | Block direct edits to `*.generated.ts`, `*_models.py` (codegen output). Block edits to `*.schema.json` directly. |
| PostToolUse: Edit/Write | Contract file edited | If file matches `packages/contracts/**`, `src/api/**/*.py`, `apps/agent-api/app/core/**` → auto-run `make validate-local` |
| PreToolUse: Bash | Destructive commands | Block `docker rm`, `docker system prune`, `dropdb`, `DROP TABLE` |
| Notification: Stop | Session ending | Auto-update memory file with last validated state |

### 3.5 Permission Rules for Generated Files

**Source:** [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)

```json
{
  "permissions": {
    "deny": [
      "Edit(*/api-types.generated.ts)",
      "Edit(*/agent-api-types.generated.ts)",
      "Edit(*/backend_models.py)",
      "Edit(*/rag_models.py)",
      "Edit(.env)",
      "Edit(.env.*)"
    ],
    "allow": [
      "Bash(make sync-*)",
      "Bash(make validate-*)",
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(pytest *)"
    ],
    "additionalDirectories": [
      "/home/zaks/zakops-backend/",
      "/home/zaks/zakops-agent-api/",
      "/home/zaks/Zaks-llm/"
    ]
  }
}
```

This prevents Claude from accidentally hand-editing generated files (a common mistake that causes drift).

### 3.6 Slash Commands for Contract Operations

**Source:** [code.claude.com/docs/en/custom-commands](https://code.claude.com/docs/en/custom-commands)

```markdown
# .claude/commands/sync-types.md
Run the full type synchronization pipeline:
1. `make sync-all-types` (all 7 contract surfaces)
2. `make validate-local` (verify alignment)
3. Report which surfaces changed and which are clean.
```

Community examples show 5-10 domain-specific commands as the sweet spot.

### 3.7 Plugin Marketplace

**Source:** [code.claude.com/docs/en/discover-plugins](https://code.claude.com/docs/en/discover-plugins)

Relevant plugins from the official marketplace:
- **Context7** — Enhanced context management for large codebases
- **GitHub** — Native PR/issue management
- **Playwright** — E2E test automation
- **TypeScript Quality Hooks** — Compilation and lint validation (community)

---

## 4. INNOVATION ACCELERATORS — Ideas Beyond Best Practices

| # | Accelerator | Description | Effort | Impact |
|---|------------|-------------|--------|--------|
| I-1 | **Contract Surface Subagent Pipeline** | 4 specialized subagents (explorer→implementer→validator→reviewer) that form an automated pipeline for any change touching contract surfaces. Explorer identifies affected surfaces, implementer makes changes, validator runs syncs and checks, reviewer verifies patterns. | Medium | Very High |
| I-2 | **PostToolUse Contract Auto-Sync** | Hook that detects when a contract source file is edited (e.g., a new endpoint in `main.py`) and automatically runs the relevant `sync-*` target + validation. Zero manual steps. | Low | High |
| I-3 | **PostgreSQL MCP for Schema Verification** | Direct DB access lets Claude verify migration state, check live schema vs contract, and detect drift in real-time without running shell commands. | Low | High |
| I-4 | **Status Line with Drift Indicator** | Terminal status line showing: branch name, service health (green/red), contract drift status from last `validate-local` run. Developer sees drift at a glance. | Low | Medium |
| I-5 | **Memory-Based Contract State** | Auto-memory file that records: last successful `validate-all` timestamp, known drift status per surface, last codegen run hash. Survives context compaction. | Low | Medium |
| I-6 | **`fileSuggestion` for Contracts** | Custom file autocomplete that, when typing `@`, prioritizes contract files (`packages/contracts/**`), bridge files (`types/api.ts`), and generated types. | Low | Medium |
| I-7 | **Compaction Instructions** | Custom compaction prompt: "When summarizing, always preserve: (1) which contract surfaces were modified, (2) which sync targets were run, (3) current drift status, (4) active branch and PR." | Low | High |
| I-8 | **Scaffold-Aware Commands** | Extend the existing scaffolder (`make new-feature`) with Claude Code commands that auto-generate the feature spec, run scaffold, then validate all affected surfaces. | Medium | Medium |
| I-9 | **Cross-Repo Workspace** | Use `additionalDirectories` to give Claude Code simultaneous access to all 3 repos from any CWD. Currently, working in one repo means blind to the others. | Trivial | High |
| I-10 | **Generated File Protection via Permissions** | Use `permissions.deny` to make it impossible for Claude to hand-edit generated files. Forces the correct workflow: edit source → run codegen → generated files update automatically. | Trivial | Very High |

---

## 5. CONCRETE PATCH LIST — Changes to the V5 Mission

| # | Patch | V5 Section Affected | What to Change | Priority |
|---|-------|---------------------|----------------|----------|
| P-01 | **Split CLAUDE.md into Constitution + Skills** | Fix 1 (CLAUDE.md Rewrite) | Keep CLAUDE.md under 150 lines. Move contract surface details to `.claude/skills/contract-surfaces/SKILL.md`. Move codegen pipeline to `.claude/skills/codegen-pipeline/SKILL.md`. | P0 |
| P-02 | **Add `.claude/agents/` subagent specs** | NEW SECTION (Fix 2.5) | Create 4 subagent definitions: `contract-checker.md`, `type-syncer.md`, `topology-explorer.md`, `code-reviewer.md` in `.claude/agents/`. | P0 |
| P-03 | **Add `.mcp.json` for ZakOps MCP + PostgreSQL** | NEW SECTION (Fix 2.6) | Create project `.mcp.json` configuring the existing port 9100 MCP server + read-only PostgreSQL MCP for schema inspection. | P0 |
| P-04 | **Add permission rules to `settings.json`** | Fix 1 or NEW SECTION | Add `permissions.deny` for all generated files. Add `permissions.allow` for make targets. Add `additionalDirectories` for cross-repo access. | P0 |
| P-05 | **Expand hooks from 2 to 5** | Fix 6 (Pre-Commit Hook) | Keep existing 2 hooks. ADD: (a) PreToolUse block generated file edits, (b) PostToolUse auto-validate on contract file changes, (c) PreToolUse block destructive Docker commands. | P1 |
| P-06 | **Add 5 new slash commands** | Fix 2 (.claude/commands/) | Add: `/sync-types`, `/validate`, `/contract-drift`, `/topology`, `/pre-flight`. V5 only updates `infra-check.md`. | P1 |
| P-07 | **Extend existing skills (don't duplicate)** | Fix 1, Fix 3 | V5's CLAUDE.md includes project-context info that already exists in `skills/project-context/SKILL.md`. UPDATE the skill instead of duplicating in CLAUDE.md. | P1 |
| P-08 | **Add `additionalDirectories`** | Settings.json section | Configure `/home/zaks/zakops-backend/`, `/home/zaks/zakops-agent-api/`, `/home/zaks/Zaks-llm/` so Claude Code can access all repos regardless of CWD. | P1 |
| P-09 | **Add `fileSuggestion` script** | NEW SECTION | Script that prioritizes contract files, bridge files, and generated types in @ autocomplete. | P2 |
| P-10 | **Add `statusLine` for contract drift** | NEW SECTION | Status line script showing branch, service health, last validation status. | P2 |
| P-11 | **Add custom compaction instructions** | NEW SECTION | Custom compaction prompt preserving contract surface state across context windows. | P2 |
| P-12 | **Memory file contract state** | Fix 1 or NEW | Auto-memory structure tracking per-surface validation state. | P2 |
| P-13 | **Enable sandbox with allowedDomains** | NEW SECTION | Configure sandbox for security with allowed domains (github.com, npm, pypi). | P2 |
| P-14 | **Plugin marketplace integration** | NEW SECTION | Evaluate and configure relevant plugins (Context7, GitHub). | P3 |
| P-15 | **LSP configuration** | NEW SECTION | Enable LSP tool for TypeScript and Python type checking. | P3 |

---

## 6. RISK REGISTER

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| R-1 | **CLAUDE.md over 200 lines hits truncation** | Memory file read after 200 lines is truncated. V5's proposed CLAUDE.md is ~300 lines. | P-01: Split into constitution + skills. |
| R-2 | **MCP server on port 9100 may not be running** | If MCP server is down, Claude Code can't use it. | Health check in PreToolUse hook. Fallback to HTTP. |
| R-3 | **PostToolUse auto-validate slows iteration** | Running `make validate-local` after every edit adds latency. | Make it async. Only trigger on contract-adjacent files. |
| R-4 | **Permission deny on generated files could block legitimate debugging** | Developer may need to read generated files for debugging. | Use `deny` for Edit/Write only, not Read. |
| R-5 | **Subagent context isolation loses project state** | Subagents don't share context with main agent. | Give each subagent a focused SKILL.md and memory directory. |
| R-6 | **Too many hooks slow down every tool call** | Each hook runs on every matching tool use. | Use tight matchers (specific file patterns, not `*`). Keep hooks under 5 seconds. |
| R-7 | **Plugin marketplace plugins may conflict with custom hooks** | Third-party plugins may have their own hooks. | Enable one at a time. Test for conflicts. |
| R-8 | **Cross-repo `additionalDirectories` exposes full codebase** | Claude can read/edit any file in all 3 repos. | Combine with permission deny rules for sensitive paths. |

---

## 7. PROPOSED V5++ OUTLINE

The V5 mission should be restructured as follows:

```
MISSION-INFRA-AWARENESS-V5-PLUS-PLUS
├── Section 0: Discovery (KEEP from V5)
│   └── Snapshot current state of all Claude Code config
│
├── Section 1: CLAUDE.md Constitution (MODIFIED from V5 Fix 1)
│   ├── 1.1: Write CLAUDE.md (max 150 lines, constitution style)
│   ├── 1.2: Create/update .claude/skills/contract-surfaces/SKILL.md
│   ├── 1.3: Create/update .claude/skills/codegen-pipeline/SKILL.md
│   ├── 1.4: Update .claude/skills/project-context/SKILL.md
│   └── GATE: CLAUDE.md under 150 lines + all skills readable
│
├── Section 2: Settings & Permissions (NEW)
│   ├── 2.1: Add permissions.deny for generated files
│   ├── 2.2: Add permissions.allow for make targets
│   ├── 2.3: Add additionalDirectories for cross-repo access
│   ├── 2.4: Configure sandbox with allowedDomains
│   └── GATE: Settings valid JSON + permission deny blocks generated file edit
│
├── Section 3: Subagents (NEW)
│   ├── 3.1: contract-checker.md (haiku, validate surfaces)
│   ├── 3.2: type-syncer.md (haiku, run codegen pipelines)
│   ├── 3.3: topology-explorer.md (haiku, discover services)
│   ├── 3.4: code-reviewer.md (sonnet, review against patterns)
│   └── GATE: Each subagent invocable by name
│
├── Section 4: MCP Configuration (NEW)
│   ├── 4.1: Create .mcp.json with ZakOps MCP (port 9100)
│   ├── 4.2: Add PostgreSQL MCP (read-only, 3 databases)
│   └── GATE: Claude Code can call MCP tools
│
├── Section 5: Hooks Expansion (MODIFIED from V5 Fix 6)
│   ├── 5.1: Keep existing pre-edit.sh (secrets + branch blocker)
│   ├── 5.2: Expand post-edit.sh (add contract file detection + auto-validate)
│   ├── 5.3: Add pre-bash.sh (block destructive commands)
│   └── GATE: Editing generated file → blocked. Editing contract file → auto-validates.
│
├── Section 6: Commands & Workflows (MODIFIED from V5 Fix 2)
│   ├── 6.1: Update infra-check.md (all 7 surfaces)
│   ├── 6.2: Add sync-types.md
│   ├── 6.3: Add validate.md
│   ├── 6.4: Add contract-drift.md
│   ├── 6.5: Add pre-flight.md
│   └── GATE: All commands executable via /command-name
│
├── Section 7: Infrastructure Tooling (KEEP from V5 Fixes 3-5, 7-9)
│   ├── 7.1: Manifest generator (all 7 surfaces) — V5 Fix 3
│   ├── 7.2: Cross-layer validation — V5 Fix 4
│   ├── 7.3: Dependency graph — V5 Fix 5
│   ├── 7.4: Makefile portability — V5 Fix 7
│   ├── 7.5: spec-freshness-bot (real, not placeholder) — V5 Fix 8
│   ├── 7.6: validate-enforcement — V5 Fix 9
│   └── GATE: make validate-local EXIT 0
│
├── Section 8: Quality-of-Life (NEW)
│   ├── 8.1: fileSuggestion script for contract files
│   ├── 8.2: statusLine with drift indicator
│   ├── 8.3: Custom compaction instructions
│   ├── 8.4: Memory file contract state structure
│   └── GATE: Status line shows, @ autocomplete prioritizes contracts
│
└── Section 9: Final Validation (MODIFIED from V5)
    ├── 9.1: validate-local EXIT 0
    ├── 9.2: All subagents invocable
    ├── 9.3: Generated file edit → blocked
    ├── 9.4: Contract file edit → auto-validates
    ├── 9.5: MCP tools callable
    ├── 9.6: All 5 new commands working
    └── GATE: Full-stack proof
```

---

## 8. SOURCES

### Official Documentation
- [Claude Code Settings Reference](https://code.claude.com/docs/en/settings) — Complete settings.json schema
- [Claude Code Hooks](https://code.claude.com/docs/en/hooks) — PreToolUse, PostToolUse, Notification, Stop
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents) — Custom agent definitions
- [Claude Code Commands](https://code.claude.com/docs/en/custom-commands) — Slash command system
- [Claude Code Plugins](https://code.claude.com/docs/en/discover-plugins) — Marketplace and plugin system
- [Claude Code Memory](https://code.claude.com/docs/en/memory) — CLAUDE.md and auto-memory
- [API Compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) — Context management beta

### Community & Best Practices
- [awesome-claude-code](https://github.com/anthropics/awesome-claude-code) — 23k+ stars, 100+ tools/plugins/workflows curated
- [Builder.io — CLAUDE.md Best Practices](https://www.builder.io/blog/claude-code-best-practices) — Progressive disclosure pattern
- [PubNub — Subagent Best Practices Part I & II](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/) — Pipeline architecture
- [Shrivu Shankar — How I Use Every Claude Code Feature](https://blog.sshh.io/p/how-i-use-every-claude-code-feature) — Practitioner field report
- [VoltAgent — 100+ Claude Code Subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — Subagent collection
- [Jitendra Zaa — Complete Guide 2026](https://www.jitendrazaa.com/blog/ai/claude-code-complete-guide-2026-from-basics-to-advanced-mcp-2/) — MCP + agents comprehensive guide
- [Context Priming (disler)](https://github.com/disler/context-priming) — Project initialization pattern
- [Claude Code Infrastructure Showcase (diet103)](https://github.com/diet103/claude-code-infrastructure) — Hook-based skill selection

### MCP Servers
- [PostgreSQL MCP Pro](https://github.com/crystaldba/postgres-mcp) — Read/write access + performance analysis
- [PostgreSQL MCP (sgaunet)](https://github.com/sgaunet/postgresql-mcp) — Read-only with safety constraints
- [MCP Server Directory](https://github.com/modelcontextprotocol/servers) — Official repository
- [Top 10 MCP Servers for Claude Code](https://apidog.com/blog/top-10-mcp-servers-for-claude-code/) — Curated ranking
- [Best MCP Servers 2026 (Builder.io)](https://www.builder.io/blog/best-mcp-servers-2026) — Detailed comparison

---

## 9. SUMMARY STATISTICS

| Metric | Count |
|--------|-------|
| Strengths identified | 10 |
| Gaps found (critical) | 5 |
| Gaps found (structural) | 5 |
| Gaps found (missing features) | 5 |
| Innovation accelerators | 10 |
| Concrete patches | 15 |
| Risks identified | 8 |
| External sources cited | 17 |
| V5++ outline sections | 9 (was 10 fixes) |

**PASS 1 VERDICT: V5 mission is solid on WHAT to teach Claude Code about infrastructure, but weak on HOW to teach it. It treats Claude Code as a 2024-era LLM that only reads CLAUDE.md. The 2026 Claude Code capability stack (subagents, MCP, plugins, hooks, permissions, skills, settings) provides dramatically better mechanisms for the same goals.**

---

## ADDENDUM: FULL CODEBASE SCAN CORRECTIONS

The deep scan agent (`acbd537`) completed a comprehensive 61-tool-call audit revealing the ZakOps Claude Code setup is more extensive than initially assessed. Key corrections:

### Corrected Asset Inventory

| Asset | Initial Count | Corrected Count | Details |
|-------|--------------|-----------------|---------|
| CLAUDE.md files | 1 (root) | **6** | root, .claude/, zakops-agent-api/, zakops-backend/, Zaks-llm/, bookkeeping/ (total ~334 lines) |
| Custom agents | 0 | **4** (in Zaks-llm) | zakops-prime (172L), agent-config-consultant (258L), log-monitor (88L), research-gemini (65L) — but NONE are contract/infra-aware |
| Installed plugins | 0 | **10+** | agent-sdk-dev, typescript-lsp, frontend-design, hookify (60+ files), gopls-lsp, jdtls-lsp, php-lsp, code-simplifier, feature-dev, example-plugin |
| MCP resources | 0 | **5** | Gmail (search, read, download), Crawl4AI RAG (crawl, query, sources) — via settings.local.json |
| Permission ALLOW rules | 0 | **50+** | Bash commands (docker, git, make, npm, python3, etc.), WebSearch, WebFetch (github.com), MCP |
| settings.local.json | not scanned | **70 lines** | Extensive allow list in `/home/zaks/.claude/settings.local.json` |
| Lab Loop | not found | **Active** | `/home/zaks/bookkeeping/labloop/` — automated validation with email notifications |

### Impact on Gap Analysis

| Gap | Impact of Correction |
|-----|---------------------|
| G-1 (Subagents) | **Partially mitigated** — 4 agents exist but in wrong scope (Zaks-llm, not main project) and none are contract-aware. Gap still valid: need contract-specific agents in main `.claude/agents/`. |
| G-2 (MCP) | **Partially mitigated** — Gmail + RAG MCP configured. Gap still valid: ZakOps MCP (port 9100) and PostgreSQL MCP not configured. |
| G-3 (Permissions) | **Refined** — Extensive ALLOW exists. Gap still valid: zero DENY rules for generated files. |
| G-5 (Plugins) | **Corrected** — 10+ plugins installed. Gap refined: plugins exist but V5 doesn't leverage them (especially typescript-lsp and hookify). |

### Additional Discoveries

| # | Discovery | Significance |
|---|-----------|-------------|
| AD-1 | `settings.local.json` allows `spinnerTipsEnabled: true` | Minor — already configured |
| AD-2 | Zaks-llm CLAUDE.md lists 9 services (incl. Desktop Commander MCP 3001, ZakOps MCP 3002, Google Workspace MCP 8010, Browser Use MCP 8020, LinkedIn MCP 8030) | V5 mission undercounts services — infra layer has more MCP servers than documented |
| AD-3 | `hookify` plugin has 60+ files for rule-engine hooks | Could replace custom hook scripts with declarative rule system |
| AD-4 | Lab Loop automation exists for gated validation runs | V5 doesn't mention Lab Loop — could integrate with validate-local/validate-live |
| AD-5 | 18 mission reports in `zakops-dashboard/.claude/reports/` | Historical evidence of phased development (phases 1-19) |
| AD-6 | `.claude/CLAUDE.md` (67 lines) has Infrastructure Awareness Protocol V5 reference | Already mentions `make sync-types` pre/post task — V5 rewrite should not regress this |
| AD-7 | Total Claude Code configuration: **~2,500+ lines** across all assets | V5 mission must account for this existing investment, not overwrite it |

---

## ADDENDUM 2: DEEP FEATURE RESEARCH (Agent a6a55b0)

Research agent completed with 25 tool calls across official docs, SDK repos, and community sources. Key findings that affect the V5++ plan:

### Hook System is Far More Powerful Than Assumed

| Discovery | Impact on V5++ |
|-----------|---------------|
| **14 hook event types** (not ~4-5): SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, Notification, SubagentStart, SubagentStop, Stop, TeammateIdle, TaskCompleted, **PreCompact**, SessionEnd | V5++ can use PreCompact to preserve contract state during compaction. SessionStart can auto-run `make validate-local`. Stop can auto-update memory. |
| **Three hook handler types**: `command` (shell), `prompt` (single-turn LLM eval), `agent` (subagent with Read/Grep/Glob) | ZakOps only uses `command`. A `prompt` hook could evaluate "does this edit affect a contract surface?" without a shell script. An `agent` hook could run multi-file validation. |
| **PreCompact hook** intercepts auto-compaction | Can inject contract surface state into the compaction summary automatically. This is the RIGHT mechanism for I-7 (Compaction Instructions). |
| **TaskCompleted hook** can validate before task resolution | Ensures `make validate-local` passes before any task is marked done. |

### Skills System Has YAML Frontmatter Powers

Skills support frontmatter with `allowed-tools` and inline `hooks`:

```yaml
---
name: sync-contracts
description: Synchronize all 7 contract surfaces
allowed-tools:
  - Bash
  - Read
hooks:
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: ".claude/hooks/validate-after-sync.sh"
---
```

This means skills can be self-contained enforcement units — each skill brings its own hooks. V5++ should use this for contract-aware skills.

### `--add-dir` is Better Than `additionalDirectories`

```bash
claude --add-dir /home/zaks/zakops-backend --add-dir /home/zaks/Zaks-llm
```

Plus env var `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` loads CLAUDE.md from all added dirs. This means Claude Code can read ALL 6 CLAUDE.md files automatically. V5++ should configure this.

### Official GitHub Action Could Replace spec-freshness-bot

`anthropics/claude-code-action@v1` (5.5k+ stars) supports:
- Automatic PR review on `pull_request` events
- `@claude` mentions in PR/issue comments
- Structured JSON outputs as Action outputs
- **Can push commits** (not just review)

This is a production-grade replacement for the current PLACEHOLDER `spec-freshness-bot.yml`. Instead of echo statements, use the official action to verify spec drift on every PR.

### Claude Agent SDK for Custom Automation

The SDK (now called "Claude Agent SDK") enables programmatic Claude Code:

```bash
pip install claude-agent-sdk
# or
npm install @anthropic-ai/claude-agent-sdk
```

Could build a custom `validate-all-surfaces` script that runs Claude Code as a library, with full tool access, to verify each contract surface programmatically.

### Updated Patch Priorities

| Patch | Previous | Updated | Reason |
|-------|----------|---------|--------|
| P-05 (Expand hooks) | P1 | **P0** | 14 event types available, including PreCompact and TaskCompleted — much more impactful than initially assessed |
| P-11 (Compaction instructions) | P2 | **P1** | PreCompact hook provides proper mechanism, not just instructions string |
| NEW P-16 | — | **P1** | Replace spec-freshness-bot PLACEHOLDER with `claude-code-action@v1` |
| NEW P-17 | — | **P2** | Configure `--add-dir` + `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` for multi-repo CLAUDE.md loading |
| NEW P-18 | — | **P2** | Use `prompt` type hooks for lightweight contract surface detection (no shell scripts needed) |
| NEW P-19 | — | **P1** | Use `.claude/rules/` with path-scoped frontmatter for stack-specific rules |
| NEW P-20 | — | **P2** | Use skills `context: fork` for destructive operations (sync, codegen) |

### `.claude/rules/` with Path-Scoped Frontmatter (Agent ac15978)

A powerful feature V5 completely ignores. All `.md` files in `.claude/rules/` are **automatically loaded**. With YAML frontmatter, rules can be scoped to specific file paths:

```yaml
# .claude/rules/backend-contracts.md
---
paths:
  - "zakops-backend/src/api/**/*.py"
  - "apps/agent-api/app/core/**/*.py"
---
When modifying API endpoints:
1. Run `make sync-types` after any response model change
2. Check that all 7 contract surfaces still align
3. Never use .get() on typed SDK responses
```

```yaml
# .claude/rules/generated-files.md
---
paths:
  - "**/*.generated.ts"
  - "**/backend_models.py"
  - "**/rag_models.py"
---
NEVER edit these files directly. They are generated by codegen.
To update them, modify the source OpenAPI spec and run `make sync-all-types`.
```

This is **better than CLAUDE.md** for contract surface rules because:
1. Rules load automatically (no need to remember)
2. Path scoping means backend rules don't pollute frontend context
3. Committed to git (team-shared)
4. Modular (one concern per file)

### Skills `context: fork` for Side-Effect Operations

Skills with `context: fork` run in an isolated subagent context:

```yaml
---
name: sync-contracts
description: Synchronize all 7 contract surfaces
context: fork
allowed-tools:
  - Bash
  - Read
---
Run `make sync-all-types` and report results.
```

This prevents long-running codegen from polluting the main conversation context.

---

*Generated: 2026-02-07T01:00:00Z*
*Addendum 1 appended: 2026-02-07T01:15:00Z (post-scan correction)*
*Addendum 2 appended: 2026-02-07T01:30:00Z (deep feature research)*
*Addendum 3 appended: 2026-02-07T01:45:00Z (path-scoped rules + forked skills)*
*Auditor: Claude Code (Opus 4.6)*
*Protocol: PASS 1 (Research & Benchmark)*

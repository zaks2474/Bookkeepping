# CLAUDE CODE RESET V5→V5PP — PASS 1 Individual Report

```
AGENT IDENTITY
agent_name:    Claude (opus46)
run_id:        20260207-0200-opus46-v5pp
timestamp:     2026-02-07T02:00:00Z
pass:          1 of 3 (Research & Idea Generation)
input:         MISSION-INFRA-AWARENESS-V5-CLAUDE-CODE-RESET.md (1,112 lines)
repos_scanned: zakops-agent-api (5eb7ce6), zakops-backend (444dff6), Zaks-llm (4dfa462)
```

---

## Executive Summary

V5 is a **B+ mission prompt** — excellent on WHAT to teach Claude Code (7 contract surfaces, codegen pipelines, dependency graphs) but fundamentally weak on HOW. V5 treats Claude Code as a 2024-era text editor that only reads CLAUDE.md. The 2026 capability stack — subagents, MCP, hooks (14 events/3 handlers), permissions (deny/allow/ask), path-scoped rules, skills frontmatter, persistent memory, compaction control — offers dramatically better mechanisms.

**Central thesis**: V5's domain knowledge should be delivered through 2026 Claude Code infrastructure (rules, skills, hooks, agents, permissions) instead of being dumped into a 300-line CLAUDE.md that risks truncation.

---

## Current ZakOps Claude Code Inventory (Fresh Scan)

| Asset | Count | Lines | Notes |
|-------|-------|-------|-------|
| CLAUDE.md files | 5 | 275 | root(64), .claude/(66), agent-api(65), backend(42), bookkeeping(38) |
| .claude/commands/ | 12 | ~254 | Comprehensive set including after-change, sync-*, validate |
| .claude/skills/ | 7 | 466 | api-conventions, atomic-workflow, code-style, debugging-playbook, project-context, security-and-data, verification-standards |
| .claude/hooks/ | 2 | ~55 | pre-edit.sh (secrets+branch), post-edit.sh (auto-format) |
| .claude/agents/ | 0 | 0 | EMPTY at main scope |
| .claude/rules/ | 0 | 0 | Does not exist |
| .mcp.json | 0 | 0 | No project-level MCP config |
| settings.json | 1 | ~30 | Hooks only — no deny/allow permissions |
| settings.local.json | 2 | large | 50+ Bash allow, MCP (Gmail, Crawl4AI RAG) |
| Plugins | 10+ | large | typescript-lsp, hookify, agent-sdk-dev, etc. |

---

## Top 15 Ideas (Ranked by Impact × Feasibility)

| # | Idea | Impact | Effort | Source |
|---|------|--------|--------|--------|
| 1 | Permission deny for generated files | Very High | Trivial | code.claude.com/docs/en/settings |
| 2 | Path-scoped rules (.claude/rules/) | Very High | Low | code.claude.com/docs/en/rules |
| 3 | PostToolUse auto-validate (verification feedback loop) | Very High | Low | Boris Cherny's workflow pattern |
| 4 | CLAUDE.md constitution split (max 150 lines) | High | Medium | builder.io/blog/claude-code-best-practices |
| 5 | Contract-checker subagent (haiku + memory) | High | Low | code.claude.com/docs/en/sub-agents |
| 6 | PreToolUse hook blocking generated file edits | Very High | Low | github.com/diet103/tdd-guard |
| 7 | PostgreSQL MCP for DB schema inspection | High | Low | github.com/crystaldba/postgres-mcp |
| 8 | additionalDirectories for cross-repo access | High | Trivial | code.claude.com/docs/en/settings |
| 9 | PreCompact memory preservation hook | High | Low | code.claude.com/docs/en/hooks |
| 10 | Custom compaction instructions | High | Low | code.claude.com/docs/en/memory |
| 11 | SessionStart status display | Medium | Low | code.claude.com/docs/en/hooks |
| 12 | Two-tier persistent memory | Medium | Medium | github.com/yuvalsuede/memory-mcp |
| 13 | GitHub Action for CI validation | Medium | Low | github.com/anthropics/claude-code-action |
| 14 | cc-hooks-ts type-safe hooks | Medium | Low | github.com/sushichan044/cc-hooks-ts |
| 15 | Enterprise managed settings pattern | Medium | Low | managed-settings.com |

---

## 7 Concrete Patches to V5 Mission Prompt

### PATCH-01: Add Fix 1.5 — Path-Scoped Rules (P0)
Create 3+ `.claude/rules/*.md` files with `paths:` frontmatter:
- contract-surfaces.md → packages/contracts/**, generated files
- backend-api.md → zakops-backend/src/api/**
- agent-api.md → apps/agent-api/app/**

### PATCH-02: Add Fix 1.6 — Permissions & Settings (P0)
Add deny rules (6 generated files + .env), allow rules (make sync-*, validate-*, infra-*), additionalDirectories (3 repos).

### PATCH-03: Add Fix 2.5 — Contract-Aware Subagents (P0)
contract-checker.md (haiku, validation, memory: project), type-syncer.md (haiku, codegen), topology-explorer.md (haiku, discovery).

### PATCH-04: Modify Fix 1 — CLAUDE.md Max 150 Lines (P0)
Replace 300-line template with 120-line constitution. Move details to new skills: contract-surfaces/SKILL.md and codegen-pipeline/SKILL.md.

### PATCH-05: Expand Fix 6 — Claude Code Hooks (P1)
Add 5 hooks: PreToolUse block generated edits, PostToolUse auto-validate, PreToolUse block destructive commands, PreCompact save state, SessionStart show status.

### PATCH-06: Add Fix 10 — Compaction & Memory (P2)
Compaction instructions preserving contract state. Memory file for cross-session persistence.

### PATCH-07: Add Step 0.8 — Config Audit (P0)
Audit Claude Code configuration: commands, skills, rules, agents, hooks, permissions, MCP.

---

## 10 Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R-1 | CLAUDE.md > 200 lines truncation | HIGH | Max 150 lines + skills |
| R-2 | Auto-validate slows iteration | MEDIUM | Contract-adjacent only; async |
| R-3 | Deny blocks debugging | LOW | Deny Edit only, not Read |
| R-4 | Subagent context isolation | MEDIUM | Skills preload + project memory |
| R-5 | Hooks slow tool calls | MEDIUM | <5s, tight matchers, max 7 |
| R-6 | MCP not running | MEDIUM | npx auto-start; DBs already up |
| R-7 | Wrong rules loaded | LOW | Specific path patterns |
| R-8 | additionalDirs exposure | LOW | Combine with deny rules |
| R-9 | Compaction loses state | HIGH | PreCompact hook + instructions |
| R-10 | Deny breaks codegen | LOW | Allow for make sync-* |

---

## Cross-Reference with Other Agents

**Ideas unique to this report (not in Codex or Gemini)**:
- Path-scoped rules (.claude/rules/) — neither agent mentions this
- Subagent YAML frontmatter (skills, mcpServers, hooks, memory fields) — deeper than any prior report
- Boris Cherny's workflow pattern as validation for V5's feedback loop
- cc-hooks-ts and TDD Guard as concrete patterns
- Two-tier persistent memory architecture
- 14 hook event types enumerated (others say "hooks" generically)

**Complementary ideas from other agents to incorporate in Pass 2**:
- Codex: OWASP LLM01/LLM02, eval gates, CLI discipline flags
- Gemini: Dynamic context generation, @generated headers, make auto-fix, impact analysis tool

---

## Sources

1. https://code.claude.com/docs/en/sub-agents — Subagent documentation
2. https://code.claude.com/docs/en/rules — Path-scoped rules
3. https://code.claude.com/docs/en/settings — Permissions, additionalDirectories
4. https://code.claude.com/docs/en/hooks — 14 event types, 3 handler types
5. https://code.claude.com/docs/en/memory — Compaction, MEMORY.md
6. https://code.claude.com/docs/en/mcp — MCP server configuration
7. https://github.com/crystaldba/postgres-mcp — PostgreSQL MCP
8. https://github.com/yuvalsuede/memory-mcp — Two-tier memory
9. https://github.com/diet103/tdd-guard — Hook enforcement pattern
10. https://github.com/sushichan044/cc-hooks-ts — Type-safe hooks
11. https://github.com/anthropics/claude-code-action — GitHub Action
12. https://x.com/bcherny/status/2007179832300581177 — Boris Cherny's setup
13. https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are — Analysis of Cherny's workflow
14. https://managed-settings.com/ — Enterprise managed settings
15. https://builder.io/blog/claude-code-best-practices — CLAUDE.md best practices
16. https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/ — Subagent patterns
17. https://www.eesel.ai/blog/claude-code-permissions — Permission guide

---

*Generated: 2026-02-07T02:00:00Z by opus46*
*Pipeline: CLAUDE_CODE_RESET_V5PP, Pass 1 of 3*

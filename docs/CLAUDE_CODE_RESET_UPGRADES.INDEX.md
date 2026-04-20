# CLAUDE_CODE_RESET_UPGRADES Master Index

This file tracks the "Best-in-Class Setup" upgrade pipeline runs.

---

## Run Entry: 20260207-1200-pass1

- **Agent:** Gemini-CLI
- **Run ID:** 20260207-1200-pass1
- **Timestamp:** 2026-02-07T12:00:00Z
- **Report Path:** /home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.Gemini-CLI.20260207-1200-pass1.md

### Top 10 Upgrades
- Dynamic Context Generator (`context.sh`) instead of static file.
- "DriftOps" auto-commits for generated files.
- `make auto-fix` composite target.
- "Impact Analysis" script (`tools/impact.sh`).
- Automated `CLAUDE.md` rotation via CI.
- Scope-locked agent modes (e.g., frontend-only).
- Epistemic markers (`@generated`) in file headers.
- Enhanced Hook Verification (permissions check).
- Token Budget estimation in manifest.
- "Doctor Auto" for self-healing environment.

### Top 5 Risks
- **Context Bloat:** Instructions getting lost in large `CLAUDE.md`.
- **Make Reliance:** Single point of failure if `make` breaks.
- **False Green:** Validation passing but logic failing.
- **Hook Bypass:** Developers ignoring local hooks.
- **Documentation Drift:** Docs getting out of sync with code (mitigated by auto-rotation).

### Top 5 "Hybrid Accelerators"
- **Policy-Driven Permissions:** Code-level enforcement of architecture.
- **Auto-Generated Audits:** Daily snapshots of system health.
- **Slash Commands:** `/fix-types`, `/deploy-dev` macros for Claude.
- **Staged Autonomy:** Graduated permission levels for the agent.
- **Semantic Code Search:** RAG for codebase navigation.

---

## Run Entry: 20260207-0100-p1

- **Agent:** opus46
- **Run ID:** 20260207-0100-p1
- **Timestamp:** 2026-02-07T01:00:00Z
- **Report Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.opus46.20260207-0100-p1.md`
- **JSON Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.opus46.20260207-0100-p1.json`
- **Verdict:** V5 is B+ on domain knowledge, weak on Claude Code capability utilization

### Current ZakOps Claude Code State (Scanned)

| Asset | Count | Lines |
|-------|-------|-------|
| CLAUDE.md | 1 | 65 |
| .claude/commands/ | 12 | 254 |
| .claude/skills/ | 7 | 466 |
| .claude/hooks/ | 2 | ~55 |
| .claude/agents/ | 0 | 0 |
| settings.json hooks | 2 | 30 |
| Permission rules | 0 | 0 |
| .mcp.json | 0 | 0 |

### Top 10 Upgrades

| # | Upgrade | Priority |
|---|---------|----------|
| 1 | Custom subagents in `.claude/agents/` (contract-checker, type-syncer, topology-explorer, code-reviewer) | P0 |
| 2 | MCP server configuration (ZakOps port 9100 + PostgreSQL read-only + GitHub) | P0 |
| 3 | Permission rules denying edits to generated files (`*.generated.ts`, `*_models.py`) | P0 |
| 4 | Split CLAUDE.md into Constitution (~150 lines) + Skills (progressive disclosure) | P0 |
| 5 | Expand hooks: PostToolUse contract auto-validate, PreToolUse block destructive commands | P1 |
| 6 | 5 new slash commands: `/sync-types`, `/validate`, `/contract-drift`, `/topology`, `/pre-flight` | P1 |
| 7 | `additionalDirectories` for cross-repo access (all 3 repos from any CWD) | P1 |
| 8 | Custom compaction instructions preserving contract surface state | P2 |
| 9 | `statusLine` with drift indicator + branch + service health | P2 |
| 10 | `fileSuggestion` prioritizing contract/bridge/generated files | P2 |

### Top 5 Gaps (Critical)

| # | Gap | Why Critical |
|---|-----|-------------|
| 1 | No `.claude/agents/` | 2026 standard feature. 7 parallel subagents possible. ZakOps has ZERO. |
| 2 | No MCP config | Port 9100 MCP server ALREADY RUNNING but Claude Code can't use it. |
| 3 | No permission rules | Generated files can be hand-edited, causing drift. |
| 4 | CLAUDE.md truncation risk | V5 proposes ~300 lines. Memory file truncation at 200 lines. |
| 5 | No LSP/Code Intelligence | Typed codebase with 7 codegen surfaces but no jump-to-definition. |

### Top 5 Risks

| # | Risk | Severity |
|---|------|----------|
| 1 | CLAUDE.md over 200 lines hits truncation | High |
| 2 | PostToolUse auto-validate slows iteration | Medium |
| 3 | Subagent context isolation loses project state | Medium |
| 4 | Too many hooks slow every tool call | Medium |
| 5 | MCP server may not be running when needed | Medium |

### Key Thesis

> V5 is excellent on WHAT to teach Claude Code (7 contract surfaces, codegen pipelines, dependency graphs). It is weak on HOW. V5 treats Claude Code as a 2024-era LLM that only reads CLAUDE.md. The 2026 capability stack — subagents, MCP, plugins, hooks, permissions, skills, settings — provides dramatically better mechanisms.

### Statistics

| Metric | Count |
|--------|-------|
| Strengths identified | 10 |
| Gaps found | 15 (5 critical, 5 structural, 5 missing) |
| Innovation accelerators | 10 |
| Concrete patches | 15 |
| Risks identified | 8 |
| Sources cited | 17 |

---

## Run Entry: 20260205-1848-ccreset (SUPERSEDED)

- **Agent:** Codex
- **Run ID:** 20260205-1848-ccreset
- **Timestamp:** 2026-02-05T18:48:00Z
- **Report Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.Codex.20260205-1848-ccreset.md`
- **JSON Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.Codex.20260205-1848-ccreset.json`
- **Verdict:** PARTIAL — Mission file not found; all findings flagged "NEEDS VERIFICATION"
- **Superseded by:** `20260207-0117-ccreset2`

---

## Run Entry: 20260207-0110-ccreset (SUPERSEDED)

- **Agent:** Codex
- **Run ID:** 20260207-0110-ccreset
- **Timestamp:** 2026-02-07T01:10:00Z
- **Report Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.Codex.20260207-0110-ccreset.md`
- **JSON Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.Codex.20260207-0110-ccreset.json`
- **Verdict:** PARTIAL — Mission file still not found; same blind template
- **Superseded by:** `20260207-0117-ccreset2`

---

## Run Entry: 20260207-0117-ccreset2 (CANONICAL Codex Pass 1)

- **Agent:** Codex
- **Run ID:** 20260207-0117-ccreset2
- **Timestamp:** 2026-02-07T01:17:00Z
- **Report Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.Codex.20260207-0117-ccreset2.md`
- **JSON Path:** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_RESET_UPGRADES.PASS1.Codex.20260207-0117-ccreset2.json`
- **Mission Prompt:** Found (1,112 lines) — fully grounded audit
- **Supersedes:** `20260205-1848-ccreset`, `20260207-0110-ccreset`

### Top 10 Upgrades
- Add Claude Code settings & managed policy section with explicit deny/allow rules
- Add hooks-based runtime guardrails (PreToolUse) for tool authorization
- Require CLI automation flags for deterministic runs
- Add mandatory eval gate (OpenAI Evals or equivalent)
- Add prompt-injection defense section aligned to OWASP LLM01/LLM02
- Add staged autonomy rules (plan -> execute)
- Add slash-command macros for evidence capture
- Add drift checks for CLAUDE.md/instructions
- Add contract-diff gate for tool outputs
- Add risk register + rollback template

### Top 5 Risks
- Permissions too strict can block needed actions
- Hooks can over-block without staged rollout
- Eval gate adds friction without fast smoke suite
- Prompt-injection remains possible without strict validation
- Managed policy misconfiguration causes inconsistent behavior

### Top 5 "Hybrid Accelerators"
- Policy-driven permissions (managed settings)
- Hooks-based tool firewall
- Slash-command macros for evidence collection
- Staged autonomy modes
- CI bot for drift detection

### Key Differentiator (vs Opus/Gemini)
- **Section-mapped patches**: Patches reference exact V5 section headers (SECTION 0, Pre-Task Protocol, Non-Negotiable Rules, FIX 2, FIX 4, FIX 9, AUTONOMY RULES, OUTPUT FORMAT)
- **OWASP LLM01/LLM02**: Only agent to propose prompt-injection defense
- **Eval gate concept**: Only agent to propose regression eval harness for prompt/tool changes

### Sources (8)
- Anthropic docs: settings, hooks, CLI usage, CLI reference, team
- OWASP LLM Top 10
- OpenAI Evals
- YouTube: Claude Code best practices

---

## Pipeline Status

| Pass | Agent | Status | Contribution |
|------|-------|--------|-------------|
| Pass 1 (Codex v1-v2) | Codex | SUPERSEDED | 2 blind runs — mission file missing |
| Pass 1 (Codex v3) | Codex | **COMPLETE** | 10 upgrades, 5 risks, 5 accelerators, 8 section-mapped patches |
| Pass 1 (Gemini) | Gemini-CLI | **COMPLETE** | 10 upgrades, 5 risks, 5 accelerators |
| Pass 1 (Opus) | opus46 | **COMPLETE** | 15 gaps, 20 patches, 10 accelerators, 8 risks |
| Pass 2 | TBD | PENDING | Will produce patched V5++ mission prompt |
| Pass 3 | TBD | PENDING | Will produce implementation-ready prompt |

---

*Master file created: 2026-02-07 (Gemini-CLI)*
*Codex Pass 1 (3 runs) indexed: 2026-02-07 (opus46)*
*Opus46 Pass 1 appended: 2026-02-07*
*Pipeline status: Pass 1 COMPLETE (3 agents, 5 runs) — Awaiting Pass 2*


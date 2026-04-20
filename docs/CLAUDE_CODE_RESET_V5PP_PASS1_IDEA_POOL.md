# CLAUDE_CODE_RESET_V5PP_PASS1_IDEA_POOL

---
## PASS1 CONTRIBUTION
agent_name: Codex
run_id: 20260207-0135-v5ppp1
timestamp: 2026-02-07T01:35:00Z
repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a

### 1) Snapshot of what V5 currently does (brief)
- Enumerates 7 contract surfaces with specs, codegen targets, and outputs; mandates sync steps per change.
- Requires discovery-first workflow with explicit commands.
- Defines pre/post task protocols and non‑negotiable rules to prevent drift.
- Specifies verification sequence and a standardized completion report.

### 2) Best-in-class ideas found (with links)
- Managed settings + precedence for permissions and policy enforcement. citeturn1search2turn1search0
- Hooks-based runtime guardrails (PreToolUse/PostToolUse). citeturn1search1
- CLI determinism flags (`--permission-mode`, `--max-turns`, `--output-format`). citeturn1search4
- OWASP LLM Top 10 prompt-injection defenses. citeturn0search0
- Eval gates with OpenAI Evals or equivalent. citeturn1search0

Links:
```
https://docs.anthropic.com/en/docs/claude-code/settings
https://docs.anthropic.com/en/docs/claude-code/hooks
https://docs.anthropic.com/en/docs/claude-code/cli-reference
https://docs.anthropic.com/en/docs/claude-code/team
https://owasp.org/www-project-top-10-for-large-language-model-applications/
https://github.com/openai/evals
```

### 3) High-leverage “innovation accelerators” (self-hostable)
- Permissions audit command to print effective settings + deny rules.
- Hook firewall that blocks dangerous Bash/Write/WebFetch patterns.
- Drift bot that diffs CLAUDE.md + mission prompt vs repo changes nightly.
- Contract diff gate: UI routes vs backend OpenAPI.
- Autonomy ladder: plan-mode required before edits.

### 4) Concrete patch suggestions to the mission prompt
Additions to specific sections (exact text blocks):

**SECTION 0: DISCOVERY — VERIFY CURRENT STATE**
```
# STEP 0.8: Claude Code settings & policies
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "*.json" -o -name "*.md" | sort
if [ -f "$MONOREPO_ROOT/.claude/settings.json" ]; then cat "$MONOREPO_ROOT/.claude/settings.json"; fi

# STEP 0.9: Claude Code hooks
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "hooks*.json" -o -name "hooks*.md" | sort
```

**Pre-Task Protocol (MANDATORY)**
```
5. Confirm permission mode and settings source order.
6. Verify .claude/settings.json + managed settings are loaded.
```

**Non-Negotiable Rules**
```
9. NEVER use bypassPermissions in production.
10. ALWAYS require PreToolUse hooks for Bash/Write/WebFetch.
11. ALWAYS report permission mode + settings path(s) in output.
```

**FIX 2 (P0): UPDATE .claude/commands/**
Add command files:
- permissions-audit.md
- hooks-check.md
- eval-smoke.md

### 5) Risks + mitigations
- Strict permissions can block work → staged allowlists. citeturn1search0
- Hooks can over-block → staged rollout + hook tests. citeturn1search1
- Eval gate adds friction → smoke evals for small changes. citeturn1search0
- Prompt injection risk remains → OWASP-aligned guardrails. citeturn0search0
- Policy misconfig across team → enforce managed settings. citeturn1search0

### 6) “If we only do 5 things” (top 5)
1) Add `.claude/settings.json` + managed policy rules. citeturn1search2turn1search0
2) Add PreToolUse hooks for Bash/Write/WebFetch. citeturn1search1
3) Enforce CLI deterministic flags. citeturn1search4
4) Add eval gate for prompt/tool changes. citeturn1search0
5) Add OWASP LLM Top 10 guardrails. citeturn0search0

---

---
## PASS1 CONTRIBUTION
agent_name: Codex
run_id: 20260207-0138-v5ppp1b
timestamp: 2026-02-07T01:38:00Z
repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a
supersedes_run_id: 20260207-0135-v5ppp1

### 1) Snapshot of what V5 currently does (brief)
- 7 contract surfaces + codegen targets; explicit sync/validate sequences per change.
- Discovery-first workflow, pre/post protocols, non‑negotiable rules.
- Fixed-plan structure with CLAUDE.md rewrite + infra validation + enforcement checks.

### 2) Best-in-class ideas found (with links)
- Managed settings + precedence for org-wide permission control. citeturn2search1turn2search2
- Hooks-based runtime guardrails (PreToolUse/PostToolUse). citeturn2search0
- CLI discipline per official CLI reference. citeturn3search0
- OWASP LLM Top 10 prompt-injection defenses. citeturn0search0
- Eval gates with OpenAI Evals or equivalent. citeturn1search0

Links:
```
https://docs.anthropic.com/en/docs/claude-code/settings
https://docs.anthropic.com/en/docs/claude-code/hooks
https://docs.anthropic.com/en/docs/claude-code/cli-reference
https://docs.anthropic.com/en/docs/claude-code/team
https://owasp.org/www-project-top-10-for-large-language-model-applications/
https://github.com/openai/evals
```

### 3) High-leverage “innovation accelerators” (self-hostable)
- Permissions audit command to show effective settings + deny rules.
- Hook firewall for dangerous Bash/Write/WebFetch patterns.
- Instruction drift bot for CLAUDE.md/mission prompt.
- Contract diff gate (frontend API calls vs backend OpenAPI).
- Autonomy ladder (plan → execute).

### 4) Concrete patch suggestions to the mission prompt
Additions (exact text blocks):

**SECTION 0: DISCOVERY — VERIFY CURRENT STATE**
```
# STEP 0.8: Claude Code settings & policies
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "*.json" -o -name "*.md" | sort
if [ -f "$MONOREPO_ROOT/.claude/settings.json" ]; then cat "$MONOREPO_ROOT/.claude/settings.json"; fi

# STEP 0.9: Claude Code hooks
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "hooks*.json" -o -name "hooks*.md" | sort
```

**Pre-Task Protocol (MANDATORY)**
```
5. Confirm permission mode and settings source order.
6. Verify .claude/settings.json and managed settings are loaded.
```

**Non-Negotiable Rules**
```
9. NEVER use bypassPermissions in production.
10. ALWAYS require PreToolUse hooks for Bash/Write/WebFetch.
11. ALWAYS report permission mode + settings path(s) in outputs.
```

**FIX 2 (P0): UPDATE .claude/commands/**
Add command files:
- permissions-audit.md
- hooks-check.md
- eval-smoke.md

### 5) Risks + mitigations
- Strict permissions block work → staged allowlists. citeturn2search1
- Hooks over-block → staged rollout + tests. citeturn2search0
- Eval gate adds friction → smoke evals for small changes. citeturn1search0
- Prompt injection risk → OWASP-aligned guardrails. citeturn0search0
- Team policy misconfig → managed settings precedence. citeturn2search2

### 6) “If we only do 5 things” (top 5)
1) Add .claude/settings.json + managed policy rules. citeturn2search1turn2search2
2) Add PreToolUse hooks for Bash/Write/WebFetch. citeturn2search0
3) Standardize CLI automation per CLI reference. citeturn3search0
4) Add eval gate for prompt/tool changes. citeturn1search0
5) Add OWASP LLM Top 10 guardrails. citeturn0search0

---


--- 
## PASS1 CONTRIBUTION
agent_name: Gemini-CLI
run_id: 20260207-1230-pass1
timestamp: 2026-02-07T12:30:00Z
repo_revision: unknown

### 1) Snapshot of what V5 currently does (brief)
The V5 mission *intended* a "Total Recall" reset with 7 contract surfaces. However, the *actual* `CLAUDE.md` is a sparse cheat sheet (~50 lines) missing these elements. The system is aspiring to V5 but stuck in V3.

### 2) Best-in-class ideas found (with links)
*   **Dynamic Context Generation**: Use a `.claude/context_script.sh` to generate session-specific context (ports, git status).
*   **DriftOps**: Automated PRs that fix configuration drift (GitOps style).
*   **Epistemic Markers**: Explicit file headers (`@generated`, `@manual`) enforced by hooks.

### 3) High-leverage “innovation accelerators” (self-hostable)
*   **`make auto-fix`**: Composite target for linting, formatting, and type-syncing.
*   **"Impact Analysis" Tool**: Script to predict blast radius of changes.
*   **Scope-Locked Modes**: Slash commands to restrict agent focus (e.g., `/mode frontend`).

### 4) Concrete patch suggestions to the mission prompt
> **Add to "Pre-Task Protocol":**
> "0. Run `tools/context.sh` to generate `SESSION_CONTEXT.md`. Read it."

### 5) Risks + mitigations
*   **Risk:** Context Bloat. **Mitigation:** Pointer pattern (summary + links).
*   **Risk:** Make Dependency. **Mitigation:** Robust `make doctor` check.

### 6) “If we only do 5 things” (top 5)
1.  **Replace** static `CLAUDE.md` with dynamic context (`context.sh`).
2.  **Implement** the missing "7 Contract Surfaces" doc.
3.  **Add** `make auto-fix`.
4.  **Enforce** `@generated` headers.
5.  **Create** `tools/impact.sh`.

---

---

## PASS1 CONTRIBUTION
agent_name: Claude (opus46)
run_id: 20260207-0200-opus46-v5pp
timestamp: 2026-02-07T02:00:00Z
repo_revision: agent-api=5eb7ce6, backend=444dff6, zaks-llm=4dfa462

### 1) Snapshot of what V5 currently does (brief)

V5 is a 1,112-line mission prompt resetting Claude Code's brain to cover 7 Hybrid Guardrail contract surfaces added since V4 via 10 fixes (Fix 0-9): Discovery, CLAUDE.md rewrite, commands, manifest generator, cross-layer validation, dependency graph, pre-commit hook, Makefile portability, spec-freshness-bot, enforcement validator.

**Does well**: Comprehensive 7-surface domain knowledge, Makefile-as-contract, gate-based progression, actionable dependency graphs, discovery-first workflow.

**Fundamentally misses**: Treats Claude Code as a 2024-era text editor. The entire 2026 capability stack — subagents, MCP, hooks (14 events/3 handlers), permissions (deny/allow/ask), path-scoped rules, skills frontmatter, persistent memory, compaction control — is ignored.

**Current ZakOps inventory**: 5 CLAUDE.md (275 lines), 12 commands (254 lines), 7 skills (466 lines), 2 hooks (55 lines), 0 agents, 0 rules, 0 .mcp.json, 0 deny permissions. 10+ plugins installed but unused.

### 2) Best-in-class ideas found (with links)

**IDEA-01: Subagent Pipeline** — https://code.claude.com/docs/en/sub-agents
Full YAML frontmatter: name, description, tools, model, permissionMode, maxTurns, skills (preloaded), mcpServers, hooks, memory (user/project/local). ZakOps: contract-checker (haiku, validates surfaces, memory: project), type-syncer (haiku, runs codegen), topology-explorer (haiku, read-only).

**IDEA-02: Path-Scoped Rules** — https://code.claude.com/docs/en/rules
`.claude/rules/*.md` with `paths:` frontmatter auto-load when Claude works with matching files. ZakOps: contract-surfaces.md, backend-api.md, agent-api.md.

**IDEA-03: Permission Deny for Generated Files** — https://code.claude.com/docs/en/settings
`permissions.deny` blocks Edit to *.generated.ts, *_models.py. `permissions.allow` for Bash(make sync-*). additionalDirectories for cross-repo access.

**IDEA-04: PostgreSQL MCP** — https://github.com/crystaldba/postgres-mcp
Direct DB schema inspection for all 3 databases via .mcp.json. Replaces manual docker exec psql.

**IDEA-05: Two-Tier Persistent Memory** — https://github.com/yuvalsuede/memory-mcp
CLAUDE.md (Tier 1, fast) + .memory/state.json (Tier 2, searchable). Hooks on Stop/PreCompact/SessionEnd persist contract state.

**IDEA-06: Boris Cherny's Pattern** — https://x.com/bcherny/status/2007179832300581177
Creator of Claude Code: "Give Claude a way to verify its work — it 2-3x the quality." 5 parallel sessions, Plan Mode, shared CLAUDE.md in git.

**IDEA-07: TDD Guard** — https://github.com/diet103/tdd-guard
Hook-based enforcement pattern. Adapt for contract guard: block generated edits, auto-validate on contract changes.

**IDEA-08: cc-hooks-ts** — https://github.com/sushichan044/cc-hooks-ts
TypeScript SDK for type-safe hook definitions with defineHook() and typed context.input.tool_input.

**IDEA-09: Enterprise Managed Settings** — https://managed-settings.com/
managed-settings.json hierarchy: managed > user > project > local. Non-overridable org-wide policies.

**IDEA-10: GitHub Action** — https://github.com/anthropics/claude-code-action (5.5k+ stars)
claude-code-action@v1 for CI. Replace placeholder spec-freshness-bot.

**IDEA-11: 14 Hook Event Types** — https://code.claude.com/docs/en/hooks
SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, Notification, SubagentStart, SubagentStop, Stop, TeammateIdle, TaskCompleted, PreCompact, SessionEnd. Three handler types: command, prompt, agent.

**IDEA-12: additionalDirectories** — https://code.claude.com/docs/en/settings
3-line JSON for cross-repo access. With CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1, loads CLAUDE.md from additional dirs.

### 3) High-leverage "innovation accelerators" (self-hostable)

| # | Accelerator | Effort | Impact |
|---|------------|--------|--------|
| A-01 | Contract Guard Hook (PreToolUse blocks generated file edits) | Low | Very High |
| A-02 | Path-Scoped Rules (3-4 .claude/rules/*.md auto-inject context) | Low | Very High |
| A-03 | Permission Deny for Codegen (8 deny rules in settings.json) | Trivial | Very High |
| A-04 | Contract-Checker Subagent (haiku + persistent memory) | Low | High |
| A-05 | PostgreSQL MCP (direct DB schema inspection for 3 databases) | Low | High |
| A-06 | CLAUDE.md Constitution Split (120-line max + skills) | Medium | High |
| A-07 | PreCompact Memory Preservation (hook saves contract state) | Low | High |
| A-08 | Cross-Repo additionalDirectories (3-line JSON) | Trivial | High |
| A-09 | Session Start Status Display (branch, health, drift) | Low | Medium |
| A-10 | PostToolUse Auto-Validate (Boris Cherny's verification loop) | Low | Very High |

### 4) Concrete patch suggestions to the mission prompt

**PATCH-01: Add Fix 1.5 — Path-Scoped Rules (P0)**
Create `.claude/rules/contract-surfaces.md` with `paths:` frontmatter matching packages/contracts/**, generated files, *_models.py. Auto-injects 7-surface table + sync commands.
```yaml
---
paths:
  - "packages/contracts/**"
  - "apps/dashboard/src/lib/*generated*"
  - "apps/agent-api/app/schemas/*_models.py"
  - "zakops-backend/src/schemas/*_models.py"
---
```
Create `backend-api.md` (paths: zakops-backend/src/api/**) and `agent-api.md` (paths: apps/agent-api/app/**).
Gate: At least 3 .claude/rules/ files with paths frontmatter.

**PATCH-02: Add Fix 1.6 — Permissions & Settings (P0)**
```json
{
  "permissions": {
    "deny": [
      "Edit(*/api-types.generated.ts)",
      "Edit(*/agent-api-types.generated.ts)",
      "Edit(*/backend_models.py)",
      "Edit(*/rag_models.py)",
      "Edit(.env)", "Edit(.env.*)"
    ],
    "allow": [
      "Bash(make sync-*)",
      "Bash(make validate-*)",
      "Bash(make infra-*)"
    ]
  },
  "additionalDirectories": [
    "/home/zaks/zakops-backend/",
    "/home/zaks/zakops-agent-api/",
    "/home/zaks/Zaks-llm/"
  ]
}
```
Gate: Edit generated file → denied. make sync-* → allowed. All repos accessible.

**PATCH-03: Add Fix 2.5 — Contract-Aware Subagents (P0)**
```yaml
# .claude/agents/contract-checker.md
---
name: contract-checker
description: Validate all 7 contract surfaces. Use proactively after API changes.
tools: Bash, Read, Grep, Glob
model: haiku
permissionMode: dontAsk
maxTurns: 15
skills:
  - verification-standards
memory: project
---
Run `make validate-local` and report failures with remediation commands.
```
Also: type-syncer.md (runs codegen), topology-explorer.md (discovers state).
Gate: contract-checker invocable, runs validate-local successfully.

**PATCH-04: Modify Fix 1 — CLAUDE.md Max 150 Lines (P0)**
Replace 300-line template with 120-line constitution pointing to skills:
- `For contract surface details → .claude/skills/contract-surfaces/`
- `For codegen pipeline → .claude/skills/codegen-pipeline/`
- `Rules auto-load based on file context`
Create 2 new skills: contract-surfaces/SKILL.md (~100 lines), codegen-pipeline/SKILL.md (~80 lines).
Gate: CLAUDE.md < 150 lines + skills cover all V5 content.

**PATCH-05: Expand Fix 6 — Claude Code Hooks (P1)**
Add 5 hooks beyond existing 2:
1. PreToolUse (Edit|Write): Block generated file edits → exit 2
2. PostToolUse (Edit|Write): Auto-validate if file in contracts/api paths
3. PreToolUse (Bash): Block `docker rm`, `dropdb`, `DROP TABLE`
4. PreCompact: Save contract state to memory file
5. SessionStart: Show branch + drift status + service health

**PATCH-06: Add Fix 10 — Compaction & Memory (P2)**
Compaction instructions in CLAUDE.md: preserve modified surfaces, sync targets run, drift status, branch, debt ceilings. Memory file tracks per-surface validation state.

**PATCH-07: Add Step 0.8 — Claude Code Config Audit (P0)**
```bash
echo "=== CLAUDE CODE CONFIG ==="
echo "Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l)"
echo "Skills: $(ls -d .claude/skills/*/ 2>/dev/null | wc -l)"
echo "Rules: $(ls .claude/rules/*.md 2>/dev/null | wc -l)"
echo "Agents: $(ls .claude/agents/*.md 2>/dev/null | wc -l)"
echo "Hooks: $(ls .claude/hooks/* 2>/dev/null | wc -l)"
cat .claude/settings.json 2>/dev/null | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('Deny:', len(d.get('permissions',{}).get('deny',[]))); print('Allow:', len(d.get('permissions',{}).get('allow',[])))" 2>/dev/null
```

### 5) Risks + mitigations

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R-1 | CLAUDE.md > 200 lines hits truncation | HIGH | PATCH-04: Max 150 lines + skills |
| R-2 | PostToolUse auto-validate slows iteration | MEDIUM | Contract-adjacent files only; async |
| R-3 | Permission deny blocks debugging | LOW | Deny Edit/Write only, not Read |
| R-4 | Subagent loses project state | MEDIUM | skills preload + memory: project |
| R-5 | Too many hooks slow tool calls | MEDIUM | <5s, tight matchers, max 7 hooks |
| R-6 | MCP server not running | MEDIUM | npx auto-starts; DB already running |
| R-7 | Wrong rules loaded | LOW | Specific path patterns; --debug |
| R-8 | additionalDirs exposes everything | LOW | Combine with deny rules |
| R-9 | Compaction loses contract state | HIGH | PreCompact hook + instructions |
| R-10 | Deny breaks codegen workflow | LOW | Allow for Bash(make sync-*) |

### 6) "If we only do 5 things" (top 5)

1. **Permission deny for generated files** — Trivial effort, very high impact. Drift impossible by construction.
2. **Path-scoped rules** — Low effort, very high impact. Auto-inject contract knowledge.
3. **CLAUDE.md constitution split** — Medium effort, high impact. Eliminates truncation.
4. **Contract-checker subagent** — Low effort, high impact. Haiku validation + memory.
5. **PreToolUse hook for generated files** — Low effort, very high impact. Defense in depth.

Total for all 5: ~2 hours. Result: Cannot hand-edit generated files (2 layers), auto-context for contract files, subagent validation, fits context limits.

---

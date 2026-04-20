Agent Identity
- agent_name: Codex
- run_id: 20260207-0138-v5ppp1b
- timestamp: 2026-02-07T01:38:00Z
- repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a
- mission_prompt_path: /home/zaks/bookkeeping/docs/MISSION-INFRA-AWARENESS-V5-CLAUDE-CODE-RESET.md (1112 lines)

## 1) Snapshot of what V5 currently does (brief)
- Enumerates seven contract surfaces with specs, codegen targets, and outputs; mandates sync/validate sequences per change.
- Defines discovery-first workflow with explicit commands.
- Requires pre-task and post-task protocols, and non-negotiable rules to prevent type/contract drift.
- Specifies a multi-fix plan (CLAUDE.md rewrite, .claude/commands expansion, manifest + validation updates, dependency graph, pre-commit, portability checks).
- Provides verification sequence and a standardized completion report.

## 2) Best-in-class ideas found (with links)
- **Managed settings + precedence**: Use Claude Code settings files and managed policies to enforce allow/deny rules org-wide. citeturn2search1turn2search2
- **Hooks for runtime guardrails**: Use PreToolUse/PostToolUse hooks to enforce safety checks before tool execution. citeturn2search0
- **CLI discipline**: Standardize automation on officially documented CLI invocations and permission modes. citeturn3search0
- **Prompt‑injection defenses**: Align tool-use safety to OWASP LLM Top 10 (LLM01/LLM02). citeturn0search0
- **Eval gates**: Require evaluation harness (e.g., OpenAI Evals) for prompt/tool changes. citeturn1search0

Links (sources):
```
https://docs.anthropic.com/en/docs/claude-code/settings
https://docs.anthropic.com/en/docs/claude-code/hooks
https://docs.anthropic.com/en/docs/claude-code/cli-reference
https://docs.anthropic.com/en/docs/claude-code/team
https://owasp.org/www-project-top-10-for-large-language-model-applications/
https://github.com/openai/evals
```

## 3) High-leverage “innovation accelerators” (self-hostable)
- **Permissions audit**: `.claude/commands/permissions-audit.md` to print effective settings, deny rules, and managed policy source.
- **Hook firewall**: PreToolUse hook that blocks dangerous shell patterns and sensitive file access.
- **Instruction drift bot**: nightly CI job that diffs CLAUDE.md/mission prompt against repo changes.
- **Contract diff gate**: script that compares frontend API call map to backend OpenAPI.
- **Autonomy ladder**: start in plan mode, unlock edits only after evidence snapshot.

## 4) Concrete patch suggestions to the mission prompt

### SECTION 0: DISCOVERY — VERIFY CURRENT STATE
Add:
```
# STEP 0.8: Claude Code settings & policies
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "*.json" -o -name "*.md" | sort
if [ -f "$MONOREPO_ROOT/.claude/settings.json" ]; then cat "$MONOREPO_ROOT/.claude/settings.json"; fi

# STEP 0.9: Claude Code hooks
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "hooks*.json" -o -name "hooks*.md" | sort
```
Rationale: make governance visible and auditable. citeturn2search1turn2search0

### Pre-Task Protocol (MANDATORY)
Add:
```
5. Confirm permission mode and settings source order.
6. Verify .claude/settings.json and any managed settings are loaded.
```
Rationale: enforce safe default permissions. citeturn3search0turn2search2

### Non-Negotiable Rules
Add:
```
9. NEVER use bypassPermissions in production; enforce via managed settings.
10. ALWAYS require PreToolUse hooks for Bash/Write/WebFetch.
11. ALWAYS report permission mode + settings path(s) in outputs.
```
Rationale: runtime guardrails + governance enforcement. citeturn2search2turn2search0

### FIX 2 (P0): UPDATE .claude/commands/ WITH ALL OPERATIONS
Add command files:
- `permissions-audit.md`
- `hooks-check.md`
- `eval-smoke.md`
Rationale: operationalizes settings, hooks, eval gates. citeturn2search1turn2search0turn1search0

### FIX 4 (P1): UPDATE CROSS-LAYER VALIDATION
Add checks:
- `.claude/settings.json` exists
- PreToolUse hooks present for Bash/Write/WebFetch
Rationale: cross-layer validation must include governance. citeturn2search0

### FIX 9 (P2): UPDATE validate-enforcement.sh
Add checks:
- fail if bypassPermissions enabled
- fail if hooks missing
Rationale: enforce safety via CI. citeturn2search1turn2search0

## 5) Risks + mitigations
- **Risk**: stricter permissions block work. **Mitigation**: staged allowlists + plan-mode approvals. citeturn2search1
- **Risk**: hooks over-block. **Mitigation**: staged rollout + hook tests. citeturn2search0
- **Risk**: eval gate slows delivery. **Mitigation**: smoke evals for small changes. citeturn1search0
- **Risk**: prompt injection remains possible. **Mitigation**: OWASP-aligned guardrails + strict validation. citeturn0search0
- **Risk**: policy misconfig across team. **Mitigation**: managed settings with precedence. citeturn2search2

## 6) If we only do 5 things
1) Add `.claude/settings.json` + managed policy rules. citeturn2search1turn2search2
2) Add PreToolUse hooks for Bash/Write/WebFetch. citeturn2search0
3) Standardize CLI automation per official CLI reference. citeturn3search0
4) Add eval gate for prompt/tool changes. citeturn1search0
5) Add OWASP LLM Top 10 guardrails. citeturn0search0


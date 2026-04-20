Agent Identity
- agent_name: Codex
- run_id: 20260207-0135-v5ppp1
- timestamp: 2026-02-07T01:35:00Z
- repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a
- mission_prompt_path: /home/zaks/bookkeeping/docs/MISSION-INFRA-AWARENESS-V5-CLAUDE-CODE-RESET.md (1112 lines)

## 1) Snapshot of what V5 currently does (brief)
- Enumerates seven contract surfaces with specs, codegen targets, and outputs; mandates sync/validate sequences per change.
- Defines a discovery-first workflow (Section 0) with explicit commands.
- Provides pre-task and post-task protocols plus non-negotiable rules that prevent drift in generated types and raw HTTP usage.
- Adds multiple P0–P2 fixes for CLAUDE.md, .claude/commands, manifest generator, validation, dependency graph, pre-commit, Makefile portability, spec-freshness-bot, and enforcement.
- Specifies a verification sequence and a standardized completion report.

## 2) Best-in-class ideas found (with links)
- **Managed settings + precedence**: Use `.claude/settings.json`, `.claude/settings.local.json`, `~/.claude/settings.json`, and enterprise managed settings with explicit precedence to enforce org-wide permissions and deny rules. citeturn1search2turn1search0
- **Hooks for runtime guardrails**: Use PreToolUse/PostToolUse hooks to block unsafe operations and enforce allowlists before tool execution. citeturn1search1turn0search2
- **CLI determinism**: Use `--permission-mode plan`, `--max-turns`, and `--output-format json` for deterministic automation in non-interactive runs. citeturn1search4
- **Prompt‑injection defense**: Align safety guidance with OWASP LLM Top 10 (Prompt Injection, Insecure Output Handling) for tool-use safety. citeturn0search0
- **Eval gates for prompt/tool changes**: Adopt a formal eval harness (e.g., OpenAI Evals) to prevent regressions in prompt/tool behavior. citeturn1search0

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
- **Permissions audit command**: `.claude/commands/permissions-audit.md` that prints settings sources + effective rules.
- **Hook firewall**: PreToolUse hook that blocks dangerous Bash patterns (`rm -rf`, `git push --force`) and sensitive file access.
- **Instruction drift bot**: nightly diff of CLAUDE.md + mission prompt vs repo changes; fails CI if stale.
- **Contract diff gate**: script that compares frontend API calls to backend OpenAPI (prevents drift).
- **Autonomy ladder**: plan‑mode required for risky tasks, auto-unlock after evidence snapshot.

## 4) Concrete patch suggestions to the mission prompt

### Add to “SECTION 0: DISCOVERY — VERIFY CURRENT STATE”
```
# STEP 0.8: Claude Code settings & policies
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "*.json" -o -name "*.md" | sort
if [ -f "$MONOREPO_ROOT/.claude/settings.json" ]; then cat "$MONOREPO_ROOT/.claude/settings.json"; fi

# STEP 0.9: Claude Code hooks
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "hooks*.json" -o -name "hooks*.md" | sort
```
Rationale: make permission policy + hooks visible. citeturn1search2turn1search1

### Add to “Pre-Task Protocol (MANDATORY)”
```
5. Confirm permission mode (plan/acceptEdits/default) and settings source order.
6. Verify `.claude/settings.json` and any managed settings are loaded.
```
Rationale: enforce safe defaults. citeturn1search4turn1search0

### Add to “Non-Negotiable Rules”
```
9. NEVER use bypassPermissions in production; enforce via managed settings.
10. ALWAYS require hooks for dangerous tools (Bash, Write, WebFetch).
11. ALWAYS report permission mode + settings path(s) in final output.
```
Rationale: governance enforcement. citeturn1search0turn1search1

### Add new section: “Governance: Settings & Hooks”
```
Claude Code must be governed by .claude/settings.json and hooks. PreToolUse hooks must validate sensitive operations and can block or require confirmation.
```
Rationale: runtime guardrails. citeturn1search1

### Add to “FIX 2 (P0): UPDATE .claude/commands/ WITH ALL OPERATIONS”
Add command files:
- `permissions-audit.md` (prints effective settings + deny rules)
- `hooks-check.md` (verifies PreToolUse hooks are configured)
- `eval-smoke.md` (runs minimal prompt/tool eval suite)
Rationale: operationalizes governance. citeturn1search2turn1search1turn1search0

### Add to “FIX 4 (P1): UPDATE CROSS-LAYER VALIDATION”
Add checks:
- `.claude/settings.json` exists
- PreToolUse hook configured for Bash/Write/WebFetch
Rationale: cross-layer validation must include tool governance. citeturn1search1

### Add to “FIX 9 (P2): UPDATE validate-enforcement.sh”
Add checks:
- fail if bypassPermissions enabled
- fail if hooks missing
Rationale: enforce safety via CI. citeturn1search0turn1search1

## 5) Risks + mitigations
- **Risk**: stricter permissions block needed work. **Mitigation**: staged allowlists + plan‑mode approvals. citeturn1search0
- **Risk**: hooks over‑block legitimate actions. **Mitigation**: staged rollout + test hooks in CI. citeturn1search1
- **Risk**: eval gate adds friction. **Mitigation**: smoke evals for small changes, full suite for major. citeturn1search0
- **Risk**: prompt‑injection remains possible. **Mitigation**: OWASP‑aligned defenses and strict output validation. citeturn0search0
- **Risk**: policy misconfiguration across team. **Mitigation**: managed settings with precedence. citeturn1search0

## 6) If we only do 5 things
1) Add `.claude/settings.json` with explicit allow/deny + managed policy rules. citeturn1search2turn1search0
2) Add PreToolUse hooks for Bash/Write/WebFetch. citeturn1search1
3) Enforce CLI deterministic flags in automation (`--permission-mode plan`, `--output-format json`). citeturn1search4
4) Add an eval gate for prompt/tool changes. citeturn1search0
5) Add OWASP LLM Top 10 prompt‑injection guardrails. citeturn0search0


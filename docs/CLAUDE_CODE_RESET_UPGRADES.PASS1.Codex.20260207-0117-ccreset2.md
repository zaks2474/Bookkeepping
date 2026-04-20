Agent Identity
- agent_name: Codex
- run_id: 20260207-0117-ccreset2
- timestamp: 2026-02-07T01:17:00Z
- repo_commit_if_any: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a
- mission_prompt_path: /home/zaks/bookkeeping/docs/MISSION-INFRA-AWARENESS-V5-CLAUDE-CODE-RESET.md
- mission_prompt_line_count: 1112 (verified via `wc -l`)
- supersedes_run_id: 20260207-0110-ccreset (prompt missing at that time)

## 1) What the current mission does well (grounded in the prompt)
- Provides a clear delta from V4 with explicit contract surfaces, specs, codegen targets, and outputs, reducing ambiguity for infra alignment.
- Defines concrete Makefile targets and a dependency graph for changes, so engineers know exactly which sync/validate steps to run.
- Enforces discovery-first workflow with explicit commands before modification.
- Includes explicit Pre-Task and Post-Task protocols, which operationalize repeatability.
- Codifies Non-Negotiable Rules that prevent common drift (generated types, raw HTTP in agent tools, etc.).
- Provides a verification sequence and output format that standardizes reporting.
- Enumerates gates per fix (GATE 1–9), which anchors acceptance criteria.

## 2) Gaps / missing pieces in the mission prompt (brutally honest)
- **Claude Code settings and permissions** are not mentioned at all (no `.claude/settings.json`, managed settings, allow/deny rules). This is now a best practice for safe, repeatable operation. citeturn0search2
- **Hooks-based runtime guardrails** are absent (PreToolUse/PostToolUse), which limits enforcement of tool safety at execution time. citeturn0search0
- **CLI discipline for automation** is missing. The prompt doesn’t define required CLI flags (`--permission-mode`, `--max-turns`, `--output-format`) for deterministic automation. citeturn2view0turn2view1
- **Team/managed policy guidance** is absent (org-wide policies, permission inheritance), which is critical in multi-user environments. citeturn2view2
- **Prompt injection defenses** are not spelled out. OWASP LLM Top 10 (LLM01/LLM02) should be referenced as a baseline. citeturn1search3
- **Evaluation gate** for prompt/tool changes is missing; no regression eval harness is required (OpenAI Evals or equivalent). citeturn1search0
- **Automated drift detection for instructions** (CLAUDE.md vs repo changes) is not enforced, only specs. This leaves instruction drift unprotected.

## 3) 2026 best practices for Claude Code project setup (researched)
- Use hierarchical settings scopes and project-level settings files to enforce permissions and policies. citeturn0search2
- Use managed settings for non-overridable org-wide policy (permission mode, allow/deny). citeturn2view2
- Enforce tool guardrails with hooks (PreToolUse/PostToolUse) to prevent unsafe commands. citeturn0search0
- Require CLI flags for deterministic automation: `--permission-mode`, `--max-turns`, `--output-format`. citeturn2view0turn2view1
- Adopt OWASP LLM Top 10 mitigations for prompt-injection and data leakage. citeturn1search3
- Require evaluation gates with a standardized eval harness (e.g., OpenAI Evals) for prompt/tool changes. citeturn1search0

## 4) Innovation accelerators (hybrid options)
- Policy-driven tool permissions using managed settings. citeturn0search2turn2view2
- Hooks-based “tool firewall” for dangerous operations (PreToolUse checks). citeturn0search0
- Slash-command macros (e.g., `/baseline`, `/contract-diff`, `/evidence`) to enforce evidence-first workflows.
- Staged autonomy: start in plan mode, require evidence snapshot, then unlock execution.
- CI bot that diffs CLAUDE.md and instruction files against repository changes for drift.

## 5) Concrete patch list for the mission prompt (exact sections + proposed text)

### Section: “SECTION 0: DISCOVERY — VERIFY CURRENT STATE”
Add steps after Step 0.7:
```
# STEP 0.8: Claude Code settings & policies
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "*.json" -o -name "*.md" | sort
if [ -f "$MONOREPO_ROOT/.claude/settings.json" ]; then cat "$MONOREPO_ROOT/.claude/settings.json"; fi

# STEP 0.9: Claude Code hooks
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "hooks*.json" -o -name "hooks*.md" | sort
```
Rationale: enforce visibility into tool permissions and hooks. citeturn0search2turn0search0

### Section: “Pre-Task Protocol (MANDATORY)”
Append:
```
5. Confirm Claude Code permission mode is explicit (plan mode for high-risk tasks).
6. Verify `.claude/settings.json` and any managed settings are loaded.
```
Rationale: ensures safe default permissions. citeturn2view0turn0search2

### Section: “Non-Negotiable Rules”
Add rules:
```
9. NEVER run with bypass permissions in production. Use managed settings to enforce this.
10. ALWAYS validate tool calls via hooks for sensitive operations.
11. ALWAYS document permission mode and settings file path in output report.
```
Rationale: aligns with settings + hooks best practice. citeturn0search2turn0search0turn2view2

### Section: “FIX 2 (P0): UPDATE .claude/commands/ WITH ALL OPERATIONS”
Add commands:
- `permissions-audit.md` (prints settings + hook status)
- `hooks-check.md` (validates PreToolUse and PostToolUse coverage)
- `eval-smoke.md` (runs a minimal eval suite for prompt/tool changes)
Rationale: operationalizes permission and eval gates. citeturn0search2turn1search0

### Section: “FIX 4 (P1): UPDATE CROSS-LAYER VALIDATION”
Add validation checks:
- Ensure `.claude/settings.json` exists.
- Ensure hooks files exist and include PreToolUse safeguards.
Rationale: cross-layer validation should include tooling governance. citeturn0search0turn0search2

### Section: “FIX 9 (P2): UPDATE validate-enforcement.sh”
Add checks:
- fail if `.claude/settings.json` missing
- fail if bypass permissions enabled
- fail if hooks missing or empty
Rationale: enforce security posture via CI. citeturn0search2turn0search0

### Section: “AUTONOMY RULES”
Add:
```
11. If a task modifies security policies or permissions, require plan-mode approval.
12. If hooks or settings are missing, STOP and generate remediation checklist.
```
Rationale: staged autonomy + safety. citeturn2view0turn0search0

### Section: “OUTPUT FORMAT”
Add to report:
- Claude Code settings file path(s)
- Permission mode used
- Hook status (present/absent)
Rationale: evidence of governance state.

## 6) Risk register
- **Risk**: stricter permissions block needed operations. **Mitigation**: staged allowlists + explicit plan-mode override. citeturn0search2
- **Risk**: hooks over-block expected tool usage. **Mitigation**: staged rollout + hook tests. citeturn0search0
- **Risk**: eval gates slow delivery. **Mitigation**: smoke eval for small changes, full suite for large. citeturn1search0
- **Risk**: prompt injection remains possible. **Mitigation**: OWASP-aligned safety checks and tight tool scopes. citeturn1search3
- **Risk**: managed policy misconfiguration causes inconsistent behavior. **Mitigation**: central policy ownership + CI checks. citeturn2view2

## 7) Proposed “V5++ mission prompt outline” (high-level only)
1) Identity + scope
2) Evidence snapshot (mandatory commands)
3) Claude Code settings & permissions
4) Hooks & runtime guardrails
5) Plan‑mode + staged autonomy
6) Execution rules (no edits before evidence)
7) Verification + eval gates
8) Deliverables + index append
9) Risk register + rollback
10) Post‑run cleanup


## Sources (links)
```
https://docs.anthropic.com/en/docs/claude-code/settings
https://docs.anthropic.com/en/docs/claude-code/hooks
https://docs.anthropic.com/en/docs/claude-code/cli-usage
https://docs.anthropic.com/en/docs/claude-code/cli-reference
https://docs.anthropic.com/en/docs/claude-code/team
https://owasp.org/www-project-top-10-for-large-language-model-applications/
https://github.com/openai/evals
https://www.youtube.com/watch?v=7EJrsyZ4jUI
```

# PASS2 REVIEW — Claude Code Brain Reset (V5→V5PP)

agent_name: Codex
run_id: 20260207-0148-v5ppp2
timestamp: 2026-02-07T01:48:00Z
repo_revision: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a

## 1) What ideas are strongest (keep)
- **Managed settings with allow/deny and precedence**: core governance layer; must be explicit and enforced. citeturn0search2
- **Hooks-based guardrails (PreToolUse/PostToolUse)**: runtime safety before tool execution. citeturn0search0
- **CLI determinism** for automation (`--permission-mode`, `--max-turns`, `--output-format`). citeturn2view0turn2view1
- **Eval gate** for prompt/tool changes (OpenAI Evals or equivalent). citeturn1search0
- **OWASP LLM Top 10 alignment** for prompt-injection and unsafe outputs. citeturn1search3
- **Instruction drift bot** for CLAUDE.md / mission prompt vs repo state (good for long-term integrity).

## 2) What ideas are dangerous/traps (reject) + why
- **Auto-fix mega target (`make auto-fix`)**: high risk of hidden changes; can obscure causality and break determinism. Keep as manual, not default in CI.
- **DriftOps auto-PRs**: good in principle, but can amplify failures if not gated; must require human approval and validation gates.
- **Dynamic context script without snapshot**: introduces nondeterminism; must freeze outputs in a timestamped artifact or disable in CI.
- **Scope-locked modes without override**: can block legitimate cross-layer tasks; require explicit escape hatch with logged approval.

## 3) Conflicts detected between agents’ proposals + resolution
- **FULL EXECUTION authority vs strict permission gates**: resolve by requiring managed policies with safe defaults and explicit, logged overrides for high-risk tasks.
- **Dynamic context generation vs deterministic build**: resolve by snapshotting context into versioned artifacts and never regenerating in CI without pinning.
- **Force SQL fallback (chat truth) vs RAG-first** (from earlier proposals): resolve by hybrid search with freshness checks, not permanent fallback.

## 4) Determinism audit
- **High risk**: `make update-agent-spec` and `validate-live` depend on running services → non-reproducible in CI.
- **Risk**: dynamic context scripts that read live system state → drift between runs.
- **Mitigation**: enforce `validate-local` as CI default; only allow `validate-live` in manual runs with recorded outputs.

## 5) Safety audit
- Require `.claude/settings.json` deny rules for secrets and sensitive files. citeturn0search2
- Require hooks to block dangerous shell patterns. citeturn0search0
- Forbid bypassPermissions in production; require explicit plan-mode review. citeturn0search2
- Add redaction rules for outputs to avoid leaking secrets.

## 6) Missing pieces
- **Redaction policy** for outputs (avoid printing secrets or tokens).
- **Spec export determinism**: freeze `agent-api.json` export with version stamp and store artifacts.
- **Hook tests**: automated tests to confirm hooks are active and effective.
- **Managed settings path discovery**: ensure settings precedence is visible in outputs.
- **CI gate for instruction drift**: compare CLAUDE.md and mission prompt against repo state.

## 7) Concrete patch set (surgical edits)

### Add to SECTION 0 (Discovery)
```
# STEP 0.8: Claude Code settings
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "settings*.json" | sort

# STEP 0.9: Claude Code hooks
find "$MONOREPO_ROOT/.claude" -maxdepth 2 -type f -name "hooks*.json" -o -name "hooks*.md" | sort
```

### Add to Pre-Task Protocol
```
5. Confirm permission mode and managed settings are loaded.
6. Record settings source precedence in the report.
```

### Add to Non-Negotiable Rules
```
9. NEVER use bypassPermissions in production; enforce via managed settings.
10. ALWAYS require PreToolUse hooks for Bash/Write/WebFetch.
11. ALWAYS redact secrets from logs and outputs.
```

### Add new subsection under FIX 2 (.claude/commands)
```
permissions-audit.md   # prints effective settings + deny rules
hooks-check.md         # verifies hooks presence and effect
```

### Add to FIX 4 (cross-layer validation)
```
- verify .claude/settings.json exists
- verify hooks configured for Bash/Write/WebFetch
```

### Add to FIX 9 (validate-enforcement)
```
- fail if bypassPermissions enabled
- fail if hooks missing
```

### Add to VERIFICATION SEQUENCE
```
- permissions-audit: outputs settings paths and deny rules
- hooks-check: confirms PreToolUse in effect
```

## 8) Recommended “final shape” outline for V5PP
1) Identity + scope
2) Evidence snapshot (discovery)
3) Governance: settings, managed policies, hooks
4) Contract surfaces + dependency graph
5) Plan/execute stages with gates
6) Validation (local vs live determinism rules)
7) Outputs + redaction policy
8) Risk register + rollback


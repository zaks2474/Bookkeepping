# CODEX-ALIGN-001 — Permanent Capability Gap Register
## Date: 2026-02-12

## Purpose
Documents features in Claude Code's V7PP environment that **cannot** be replicated
in Codex CLI due to architectural differences. Each gap includes a mitigation strategy.

---

## Gap Register

| # | Claude Code Feature | Codex Equivalent | Gap Severity | Mitigation |
|---|---|---|---|---|
| G1 | **Pre-tool hooks** (exit 2 blocks before execution) | No PreToolUse event | HIGH | Default `read-only` sandbox. AGENTS.md lists protected files. Only `builder` profile enables writes |
| G2 | **Persistent memory** (MEMORY.md with AUTOSYNC sentinels) | No memory persistence between sessions | HIGH | AGENTS.md instructs "read MEMORY.md first". For `codex exec` mode, caller must prepend context manually — no automatic injection exists |
| G3 | **Sub-agent delegation** (contract-guardian, arch-reviewer, test-engineer) | Single-model, single-session | MEDIUM | Inline agent checklists in monorepo AGENTS.md (14-surface audit, architecture review, test planning) |
| G4 | **Compaction awareness** (PreCompact + compact-recovery hooks) | No compaction hook | MEDIUM | No mitigation possible. Long sessions may lose early context |
| G5 | **Post-edit formatting** (async file cleanup via PostToolUse) | No PostToolUse hook | LOW | No mitigation. Manual cleanup if needed |
| G6 | **Task completion quality gates** (TaskCompleted hook) | No TaskCompleted hook | MEDIUM | Manual `codex-stop.sh` invocation. `codex-wrapper.sh` runs it automatically at session end |
| G7 | **Health log trend detection across sessions** | No session history analysis | LOW | Manual review of `codex-events.log`. Boot script appends to shared `health-log.md` |

## Coverage Summary

| Category | Claude Code | Codex | Parity |
|----------|-------------|-------|--------|
| Instructions (CLAUDE.md / AGENTS.md) | Root + monorepo + backend | Global + monorepo + backend | FULL |
| Skills / Commands | 8 knowledge + 16 commands | 8 knowledge + 11 action + 7 project | FULL |
| Sandbox / Deny rules | 12 deny + 4 allow | 40 prefix_rules + read-only default | ADAPTED |
| MCP servers | 4 (github, playwright, gmail, crawl4ai-rag) | 4 (same) | FULL |
| Boot diagnostics | session-start.sh (6 checks) | codex-boot.sh (6 checks) | FULL |
| Post-session validation | stop.sh (validate-local) | codex-stop.sh (validate-local) | FULL |
| Profiles | N/A | 5 (default, labloop-qa, builder, review, forensic) | ENHANCED |
| Pre-tool enforcement | Hook exit 2 | Sandbox mode only | PARTIAL (G1) |
| Persistent memory | AUTOSYNC + sentinels | Instruction-based only | PARTIAL (G2) |
| Sub-agents | 3 specialized agents | Inline checklists | ADAPTED (G3) |
| Compaction recovery | PreCompact hook | None | MISSING (G4) |
| Post-edit hooks | PostToolUse | None | MISSING (G5) |
| Task completion gates | TaskCompleted hook | Wrapper stop script | ADAPTED (G6) |
| Session trend analysis | Health log parsing | Manual log review | PARTIAL (G7) |

## Risk Assessment

- **HIGH gaps (G1, G2)**: Mitigated by sandbox defaults and AGENTS.md behavioral instructions.
  Codex in `read-only` sandbox cannot accidentally modify protected files even without pre-tool hooks.
  Memory gap is partially addressed by boot script reading MEMORY.md state.
- **MEDIUM gaps (G3, G4, G6)**: Acceptable for current usage patterns. Sub-agent checklists
  provide 80% of the value. Wrapper script captures stop-gate functionality.
- **LOW gaps (G5, G7)**: Negligible operational impact.

## Acceptance
This gap register is complete and no further gaps are expected to be discoverable
without changes to Codex CLI's architecture (hook system, memory layer, or multi-agent support).

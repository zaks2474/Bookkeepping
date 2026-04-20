# CLAUDE-CODE-ENHANCE-002 — Baseline Document
## Date: 2026-02-11
## Source: QA-CCE-VERIFY-001 FULL PASS (41/41 required, 50 evidence files)

---

## Hook Contract Snapshot (from settings.json)

| Event | Matcher | Command | Timeout | Async |
|-------|---------|---------|---------|-------|
| PreToolUse | `Edit\|Write` | pre-edit.sh | 10 | false |
| PreToolUse | `Bash` | pre-bash.sh | 10 | false |
| PostToolUse | `Edit\|Write` | post-edit.sh | 30 | true |
| SessionStart | `""` | session-boot.sh | 30 | false |
| SessionStart | `compact` | compact-recovery.sh | 15 | false |
| Stop | `""` | stop.sh | 60 | false |
| PreCompact | `""` | pre-compact.sh | 15 | true |
| TaskCompleted | `""` | task-completed.sh | 30 | false |

---

## Hook Script Snapshots (3 target scripts)

### pre-compact.sh
- Path: `/home/zaks/.claude/hooks/pre-compact.sh`
- Owner: zaks:zaks
- Perms: 755
- Line endings: LF (Bourne-Again shell script)
- Syntax: OK (`bash -n`)
- Size: 1565 bytes
- Retention: hardcoded `10` (line 51-54)

### task-completed.sh
- Path: `/home/zaks/.claude/hooks/task-completed.sh`
- Owner: zaks:zaks
- Perms: 755
- Line endings: LF (Bourne-Again shell script)
- Syntax: OK (`bash -n`)
- Size: 1771 bytes
- Gates: 3 (CRLF, root ownership, tsc)
- Fixture mode: none (hardcoded paths)
- Gate markers: none (human-readable only)

### compact-recovery.sh
- Path: `/home/zaks/.claude/hooks/compact-recovery.sh`
- Owner: zaks:zaks
- Perms: 755
- Line endings: LF (Bourne-Again shell script)
- Syntax: OK (`bash -n`)
- Size: 2457 bytes
- Quality assertions: none (outputs context without validation)

---

## Enhancement Closure Checklist

| ENH | Description | Baseline State | Target |
|-----|-------------|---------------|--------|
| ENH-1 | Dedicated `make qa-cce-verify` | No target exists | Makefile target + runner script |
| ENH-2 | Hook contract lint (`validate-claude-hook-config.py`) | No validator exists | Python validator for settings.json |
| ENH-3 | Compact-recovery JSON test harness | No harness exists | Shell test script |
| ENH-4 | Deterministic fixture mode in `task-completed.sh` | Hardcoded paths only | `TASK_COMPLETED_TARGETS` env var |
| ENH-5 | Machine-readable gate markers in `task-completed.sh` | Human text only | `GATE_RESULT:*` lines |
| ENH-7 | Configurable snapshot retention in `pre-compact.sh` | Hardcoded `10` | `SNAPSHOT_RETENTION` env var (default 10) |
| ENH-10 | Objective post-compact context quality assertions | No validation | Non-empty + key paths + changes markers |

---

*Baseline captured at 2026-02-11. All 3 hook scripts verified: syntax OK, LF, zaks:zaks, 755.*

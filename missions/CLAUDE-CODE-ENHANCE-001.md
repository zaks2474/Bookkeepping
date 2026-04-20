# MISSION: CLAUDE-CODE-ENHANCE-001
## Five Session-Surviving Claude Code Feature Additions
## Date: 2026-02-11
## Classification: Infrastructure Enhancement
## Prerequisite: None — standalone mission
## Successor: None — features are immediately available after completion

---

## File Paths

| Action | Path |
|--------|------|
| Create | `/home/zaks/.claude/hooks/pre-compact.sh` |
| Create | `/home/zaks/.claude/hooks/task-completed.sh` |
| Create | `/home/zaks/.claude/hooks/compact-recovery.sh` |
| Modify | `/home/zaks/.claude/settings.json` |
| Update | `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md` |
| Update | `/home/zaks/bookkeeping/CHANGES.md` |

---

## 1. Mission Objective

Add 5 permanent, session-surviving features to the Claude Code environment that address context loss during compaction, quality enforcement on task completion, and tool loading efficiency. All changes are **additive only** — no existing hooks, settings, or scripts are modified.

**What this is:** An infrastructure enhancement mission that creates 3 new hook scripts and adds 5 configuration entries to `settings.json`.

**What this is NOT:** This is not a dashboard, backend, or API change. No application code is touched. No contract surfaces are affected. No `make sync-*` or `make validate-local` is required (no application files change).

**Source material:** Pre-implementation audit conducted 2026-02-11 showing all 5 features at NOT IMPLEMENTED or PARTIAL status.

| # | Feature | Current Status | Target |
|---|---------|---------------|--------|
| 1 | `ENABLE_TOOL_SEARCH` | Not configured | `"auto:5"` in settings.json env |
| 2 | `PreCompact` hook | No hook exists | `pre-compact.sh` saves session snapshot before compaction |
| 3 | `TaskCompleted` hook | No hook exists | `task-completed.sh` enforces quality gates on task close |
| 4 | `alwaysThinkingEnabled` | Not explicitly set | `true` in settings.json |
| 5 | `SessionStart` compact matcher | No compact-specific hook | `compact-recovery.sh` re-injects context post-compaction |

---

## 2. Context

Claude Code conversation compaction aggressively drops all prior messages, leaving only a summary. This causes the builder to lose all visible conversation history and working context. Additionally, MCP tool definitions (Gmail: 19 tools, Playwright: 22 tools) consume context on every request, accelerating compaction. These 5 features address the problem from 3 angles:

- **Before compaction:** Snapshot critical state (`pre-compact.sh`)
- **After compaction:** Re-inject essential context (`compact-recovery.sh` via `SessionStart` with `"compact"` matcher)
- **Reduce compaction frequency:** Lazy-load MCP tools instead of loading all 41+ tool definitions into every request (`ENABLE_TOOL_SEARCH`)
- **Quality enforcement:** Block task completion if WSL hazards are present (`task-completed.sh`)
- **Better reasoning:** Enable extended thinking by default (`alwaysThinkingEnabled`)

### Current Hook Inventory (DO NOT MODIFY)

| Hook | Script | Event |
|------|--------|-------|
| pre-edit.sh | PreToolUse (Edit\|Write) | Blocks edits to generated files |
| pre-bash.sh | PreToolUse (Bash) | Blocks destructive commands |
| post-edit.sh | PostToolUse (Edit\|Write) | Post-edit tracking |
| session-boot.sh | SessionStart ("") | Boot diagnostics |
| stop.sh | Stop ("") | End-of-session validation |
| memory-sync.sh | (called by stop.sh) | Memory fact sync |
| validate-contract-surfaces.sh | (called by Makefile) | Contract validation |

---

## 3. Architectural Constraints

- **Additive only** — Do NOT modify any existing hook script, settings entry, or permission rule. Only add new entries.
- **Hook script standards** — All `.sh` files must: have `#!/usr/bin/env bash` shebang, be `chmod +x`, be owned by `zaks:zaks`, have no CRLF line endings (WSL hazard).
- **settings.json is `/home/zaks/.claude/settings.json`** — This is the user-level settings file. Do NOT touch `/root/.claude/settings.json` or `/root/.claude.json`.
- **Exit code contract** — Hook scripts use: exit 0 = allow/pass, exit 2 = block (stderr message shown to builder). Never exit 1 (treated as error, not block).
- **JSON validity** — `settings.json` must remain valid JSON after edits. Verify with `python3 -c "import json; json.load(open(...))"`.
- **Async hooks** — `pre-compact.sh` MUST be async (cannot block compaction). `compact-recovery.sh` is sync (output is consumed).
- **Snapshot directory** — Pre-compact snapshots go to `/home/zaks/bookkeeping/snapshots/`. Create directory if it doesn't exist.
- **MEMORY.md hook count** — After adding 3 new hooks, update the hook count from 7 to 10 in `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md`.

### Anti-Pattern Examples

```
### WRONG: Modifying existing hook
  # In session-boot.sh, adding compact recovery logic
  if [ "$SOURCE" = "compact" ]; then ...  # NO — create separate script

### RIGHT: Separate script per concern
  # compact-recovery.sh handles compact recovery
  # session-boot.sh unchanged

### WRONG: Exit 1 for blocking
  echo "CRLF detected" >&2
  exit 1  # Treated as error, not block — builder sees generic error

### RIGHT: Exit 2 for blocking
  echo "CRLF detected in $file — run: sed -i 's/\r$//' $file" >&2
  exit 2  # Builder sees the specific message and can fix it

### WRONG: ENABLE_TOOL_SEARCH without refresh interval
  "env": { "ENABLE_TOOL_SEARCH": "auto" }  # Missing refresh interval

### RIGHT: ENABLE_TOOL_SEARCH with refresh interval
  "env": { "ENABLE_TOOL_SEARCH": "auto:5" }  # Refresh every 5 minutes
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | CRLF in new .sh files causes `bash\r: not found` on next session | HIGH | Hooks silently fail or crash | Phase 2 WSL safety step is mandatory — V2 verification catches it |
| 2 | settings.json becomes invalid JSON, breaking Claude Code startup | MEDIUM | Cannot start Claude Code at all | Phase 2 JSON validation step. Rollback: `git checkout` the file |
| 3 | `pre-compact.sh` blocks compaction (exit non-zero or hangs) | MEDIUM | Context window fills, session degrades | Script is async + always exits 0 + has timeout in settings |
| 4 | `task-completed.sh` false-positive blocks legitimate task completion | LOW | Builder frustrated, task stuck | Gate checks are narrow (CRLF, ownership) with clear stderr messages |
| 5 | `compact-recovery.sh` outputs malformed JSON, confusing the builder | MEDIUM | Post-compact context injection fails silently | V8 verification dry-runs the script and validates JSON output |

---

## 4. Phases

### Phase 1 — Create Hook Scripts
**Complexity:** M
**Estimated touch points:** 3 new files

**Purpose:** Create the 3 new hook scripts that implement pre-compact snapshot, task quality gates, and compact recovery.

#### Tasks

- P1-01: **Create `/home/zaks/.claude/hooks/pre-compact.sh`**
  - Reads hook input JSON from stdin (trigger, session_id)
  - Saves timestamped snapshot to `/home/zaks/bookkeeping/snapshots/pre-compact-{timestamp}.md`
  - Captures: recent CHANGES.md (30 lines), git status of monorepo and backend repos, active task list
  - Auto-cleans old snapshots (keeps last 10)
  - MUST exit 0 always — cannot block compaction
  - **Checkpoint:** Script exists and is syntactically valid (`bash -n pre-compact.sh`)

- P1-02: **Create `/home/zaks/.claude/hooks/task-completed.sh`**
  - Gate 1: CRLF detection — scan files modified in the last hour under `/home/zaks/` for `\r\n` line endings
  - Gate 2: Root ownership — check for root-owned files in `/home/zaks/.claude/hooks/` created in last hour
  - Gate 3: TypeScript check — if any `.ts`/`.tsx` files changed in monorepo, run `npx tsc --noEmit` with 10s timeout
  - Exit 0 = all gates pass (allow completion). Exit 2 = gate failed (stderr tells builder what to fix)
  - **Checkpoint:** Script exists and is syntactically valid (`bash -n task-completed.sh`)

- P1-03: **Create `/home/zaks/.claude/hooks/compact-recovery.sh`**
  - Reads latest pre-compact snapshot from `/home/zaks/bookkeeping/snapshots/` (most recent file)
  - Reads recent CHANGES.md entries (25 lines)
  - Injects key project paths and operating reminders
  - Outputs JSON with `hookSpecificOutput.additionalContext` structure (same pattern as `session-boot.sh`)
  - MUST exit 0 always
  - **Checkpoint:** Script exists and is syntactically valid (`bash -n compact-recovery.sh`)

#### Rollback
Delete the 3 scripts: `rm /home/zaks/.claude/hooks/{pre-compact,task-completed,compact-recovery}.sh`

---

### Phase 2 — WSL Safety + Permissions
**Complexity:** S
**Estimated touch points:** 3 files (same scripts from Phase 1)

**Purpose:** Apply mandatory WSL safety fixes to all new scripts before they can be registered in settings.

#### Tasks

- P2-01: **Strip CRLF** from all 3 scripts
  ```bash
  sed -i 's/\r$//' /home/zaks/.claude/hooks/{pre-compact,task-completed,compact-recovery}.sh
  ```

- P2-02: **Set executable permission**
  ```bash
  chmod +x /home/zaks/.claude/hooks/{pre-compact,task-completed,compact-recovery}.sh
  ```

- P2-03: **Fix ownership**
  ```bash
  sudo chown zaks:zaks /home/zaks/.claude/hooks/{pre-compact,task-completed,compact-recovery}.sh
  ```

- P2-04: **Verify no CRLF**
  ```bash
  file /home/zaks/.claude/hooks/{pre-compact,task-completed,compact-recovery}.sh
  # Each must say "Bourne-Again shell script" or "ASCII text executable" — NOT "with CRLF"
  ```

### Gate P2: WSL Safety
All 3 scripts must pass: exists + executable + zaks-owned + no CRLF. Do NOT proceed to Phase 3 until P2-04 passes.

#### Rollback
Re-run the sed/chmod/chown commands.

---

### Phase 3 — Configure settings.json
**Complexity:** M
**Estimated touch points:** 1 file (`/home/zaks/.claude/settings.json`)

**Purpose:** Register the 3 new hooks and add the 2 top-level settings to Claude Code's configuration.

#### Tasks

- P3-01: **Add `alwaysThinkingEnabled: true`** — top-level key alongside `permissions`

- P3-02: **Add `env` object with `ENABLE_TOOL_SEARCH`** — top-level key:
  ```json
  "env": { "ENABLE_TOOL_SEARCH": "auto:5" }
  ```

- P3-03: **Add `PreCompact` hook entry** to the `hooks` object:
  ```json
  "PreCompact": [{
    "matcher": "",
    "hooks": [{
      "type": "command",
      "command": "/home/zaks/.claude/hooks/pre-compact.sh",
      "timeout": 15,
      "async": true
    }]
  }]
  ```

- P3-04: **Add `TaskCompleted` hook entry** to the `hooks` object:
  ```json
  "TaskCompleted": [{
    "matcher": "",
    "hooks": [{
      "type": "command",
      "command": "/home/zaks/.claude/hooks/task-completed.sh",
      "timeout": 30,
      "statusMessage": "Running task quality gates..."
    }]
  }]
  ```

- P3-05: **Add second `SessionStart` array entry** (append to existing array, do NOT replace):
  ```json
  {
    "matcher": "compact",
    "hooks": [{
      "type": "command",
      "command": "/home/zaks/.claude/hooks/compact-recovery.sh",
      "timeout": 15,
      "statusMessage": "Recovering context after compaction..."
    }]
  }
  ```

- P3-06: **Validate JSON**
  ```bash
  python3 -c "import json; d=json.load(open('/home/zaks/.claude/settings.json')); print('OK:', list(d['hooks'].keys()))"
  ```

### Gate P3: Configuration Valid
`settings.json` must be valid JSON. Hook events listed must include: `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `PreCompact`, `TaskCompleted`. Do NOT proceed to Phase 4 until P3-06 passes.

#### Rollback
Remove the added entries from `settings.json`. The file structure is unchanged — only new keys/array entries were added.

---

### Phase 4 — Verification + Bookkeeping
**Complexity:** S
**Estimated touch points:** 2 files (MEMORY.md, CHANGES.md)

**Purpose:** Run all verification checks and update bookkeeping artifacts.

#### Tasks

- P4-01: **Dry-run pre-compact.sh**
  ```bash
  mkdir -p /home/zaks/bookkeeping/snapshots
  echo '{"trigger":"manual","session_id":"test-123"}' | bash /home/zaks/.claude/hooks/pre-compact.sh && echo "pre-compact: OK"
  ls -la /home/zaks/bookkeeping/snapshots/
  ```

- P4-02: **Dry-run compact-recovery.sh**
  ```bash
  bash /home/zaks/.claude/hooks/compact-recovery.sh | python3 -c "import sys,json; d=json.load(sys.stdin); print('compact-recovery: OK' if 'hookSpecificOutput' in d else 'FAIL')"
  ```

- P4-03: **Verify alwaysThinkingEnabled**
  ```bash
  python3 -c "import json; d=json.load(open('/home/zaks/.claude/settings.json')); print('Thinking:', d.get('alwaysThinkingEnabled'))"
  ```

- P4-04: **Verify ENABLE_TOOL_SEARCH**
  ```bash
  python3 -c "import json; d=json.load(open('/home/zaks/.claude/settings.json')); print('ToolSearch:', d.get('env',{}).get('ENABLE_TOOL_SEARCH'))"
  ```

- P4-05: **Verify hook count is 10**
  ```bash
  echo "Hook count: $(ls /home/zaks/.claude/hooks/*.sh | wc -l)"
  ```

- P4-06: **Update MEMORY.md** — Change hook count from 7 to 10 in `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md`

- P4-07: **Record in CHANGES.md** — Add entry for CLAUDE-CODE-ENHANCE-001 in `/home/zaks/bookkeeping/CHANGES.md`

### Gate P4: All Verifications Pass
All 5 verification commands (P4-01 through P4-05) must pass. MEMORY.md must show "Hooks: 10". CHANGES.md must contain "CLAUDE-CODE-ENHANCE-001".

---

## 5. Guardrails

- **DO NOT** modify any existing hook script (`pre-edit.sh`, `pre-bash.sh`, `post-edit.sh`, `session-boot.sh`, `stop.sh`, `memory-sync.sh`, `validate-contract-surfaces.sh`)
- **DO NOT** modify existing `settings.json` entries — only ADD new entries
- **DO NOT** touch any application code (dashboard, backend, agent-api, RAG)
- **DO NOT** modify `.claude/rules/`, `.claude/commands/`, or `CLAUDE.md`
- **DO NOT** run `make sync-*` or `make validate-local` — no contract surfaces are affected
- **DO NOT** create hooks that exit 1 — use exit 0 (allow) or exit 2 (block with message)
- **ALL new `.sh` files** must pass the WSL safety checklist (CRLF, chmod, chown) before registration

---

## 6. Stop Conditions

**STOP and ask the user if:**
- `settings.json` fails JSON validation after edits
- Any existing hook stops working after changes
- You are unsure whether a `SessionStart` matcher value is correct
- The `pre-compact.sh` dry-run creates files outside `/home/zaks/bookkeeping/snapshots/`
- Hook count after completion is not exactly 10

---

## 7. Acceptance Criteria

| AC | Description | Verification |
|----|-------------|-------------|
| AC-1 | `ENABLE_TOOL_SEARCH=auto:5` in settings.json env | P4-04 prints `ToolSearch: auto:5` |
| AC-2 | PreCompact hook creates snapshot file on compaction | P4-01 dry-run produces file in `snapshots/` |
| AC-3 | TaskCompleted hook blocks on CRLF violations | Create CRLF test file, trigger hook, verify exit 2 |
| AC-4 | `alwaysThinkingEnabled=true` in settings.json | P4-03 prints `Thinking: True` |
| AC-5 | Compact recovery injects context via `additionalContext` JSON | P4-02 prints `compact-recovery: OK` |
| AC-6 | All scripts: no CRLF, executable, zaks-owned | P2-04 shows no CRLF, `ls -la` shows `zaks zaks` and `x` bit |
| AC-7 | settings.json is valid JSON with 6 hook events | P3-06 prints OK with all 6 event names |
| AC-8 | MEMORY.md hook count updated to 10 | `grep "Hooks: 10" MEMORY.md` |
| AC-9 | CHANGES.md entry recorded | `grep "CLAUDE-CODE-ENHANCE-001" CHANGES.md` |

---

## 8. Rollback

All changes are additive. To disable any feature:
- **Single hook:** Remove its entry from `settings.json` hooks object
- **ENABLE_TOOL_SEARCH:** Remove `env` key from `settings.json`
- **alwaysThinkingEnabled:** Remove the key from `settings.json`
- **All hooks at once:** Add `"disableAllHooks": true` to `settings.json`
- **Delete scripts:** `rm /home/zaks/.claude/hooks/{pre-compact,task-completed,compact-recovery}.sh`

---

## Self-Check Prompts (Builder reads before starting)

- [ ] "Am I ONLY creating new files and adding new entries? I must not modify any existing hook or setting."
- [ ] "Did I strip CRLF from every .sh file I created?" (WSL hazard — DWR-001 lesson)
- [ ] "Did I use exit 2 (not exit 1) for blocking in task-completed.sh?"
- [ ] "Is pre-compact.sh marked async in settings.json? It must not block compaction."
- [ ] "Does my settings.json edit APPEND to the SessionStart array, not replace it?"
- [ ] "Is the ENABLE_TOOL_SEARCH value `auto:5` with the refresh interval, not just `auto`?"

# ZakOps Agentic AI OS — Infrastructure Reference Patch

## V6PP → V7PP: SELF-HEAL-001 (Boot Diagnostics & Self-Healing Infrastructure)

**Date:** February 9–10, 2026

**Status:** Production-Verified (6 independent QA sessions, 11 iterations)

**Applies to:** ZakOps-V6PP-Claude-Code-Infrastructure-Reference.docx (February 9, 2026)

**Mission:** SELF-HEAL-001 — Closed-loop self-diagnostic system with automatic boot checks, HALT enforcement, constraint verification, and health logging.

---

## Section-by-Section Patch Instructions

### Section 1: Executive Summary — Count Updates

Update the summary table:

| Component | V6PP Value | V7PP Value | Change |
|-----------|-----------|-----------|--------|
| Hook Scripts | 5 | 7 | +2 (session-start.sh, session-boot.sh) |
| Completed Missions | 10 | 11 | +1 (SELF-HEAL-001) |
| Slash Commands | 13 | 15 | +2 (/before-task, /prune-allows) |
| AUTOSYNC Sentinels | 6 | 7 | +1 (health_log_entries) |

Add to summary table:

| Component | Count | Status |
|-----------|-------|--------|
| Boot Diagnostic Checks | 6 + 1 bonus | All verified at session start |
| Constraint Registry Entries | 10 | All verified by CHECK 6 |
| Health Log | Active | Trend detection enabled |

---

### Section 2: Configuration Hierarchy — No Changes

No structural changes. The three-tier architecture remains the same.

---

### Section 4: Permission System — Add Section 4.3

Add the following after Section 4.2 (Allow Rules — Two Tiers):

#### 4.3 dangerouslySkipPermissions

The root-level settings file (`/root/.claude/settings.json`) has `dangerouslySkipPermissions: true` set at the **top level** (not under `permissions`). This bypasses the entire allow/deny permission system at runtime. Consequences:

- All 12 deny rules in the user-level settings are not enforced by the permission system (hooks enforce them instead).
- All allow patterns (both user-level designed and root-level accumulated) are ignored.
- The root-level allow array (~132 Bash entries) is dead weight — it cannot be meaningfully pruned because it has no runtime effect.
- The B1 boot diagnostic check (allow array size) correctly skips when this flag is true.

**Hooks are the only enforcement layer.** The pre-edit.sh hook independently blocks edits to generated files, .env files, and main branch edits. The pre-bash.sh hook independently blocks destructive commands, force-push, and DROP/TRUNCATE operations. These hooks use exit code 2 which cannot be bypassed by `dangerouslySkipPermissions`.

---

### Section 5: Hook System — Replace Entirely

Replace Section 5 with the following. The hook system has been significantly expanded from 5 to 7 scripts with a new boot diagnostics subsystem.

#### 5.1 Hook Registration (settings.json)

Seven hook scripts are registered in the user-level settings file at `/home/zaks/.claude/settings.json`. All hooks are located at `/home/zaks/.claude/hooks/`.

| Hook | Event Trigger | Behavior |
|------|---------------|----------|
| pre-edit.sh | PreToolUse (Edit\|Write) | Boot diagnostics display + HALT enforcement. Blocks edits to generated files, .env/secrets files, and main/master branch. |
| pre-bash.sh | PreToolUse (Bash) | Boot diagnostics display + HALT enforcement. Blocks destructive commands (`rm -rf /`, `DROP TABLE`, `TRUNCATE`, force-push main/master). |
| session-boot.sh | SessionStart | Runs boot diagnostics at session start. Outputs verdict as `additionalContext` JSON. Fires once on session creation. |
| post-edit.sh | PostToolUse (Edit\|Write) | Async post-edit validation checks. Verifies edit results after completion. |
| stop.sh | Stop | Session-end validation. Triggers memory-sync.sh for cleanup. |
| memory-sync.sh | Stop (via stop.sh) | Dynamic memory sentinel updates. Gathers live facts, patches MEMORY.md AUTOSYNC tags. Auto-prunes allow array. Trims health log. |
| session-start.sh | Not registered directly | Boot diagnostics engine. Called by pre-bash.sh, pre-edit.sh, and session-boot.sh. Runs 6 checks + 1 bonus, writes verdict file. |

**Settings.json event types:**

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write", "hooks": [{ "command": "pre-edit.sh" }] },
      { "matcher": "Bash", "hooks": [{ "command": "pre-bash.sh" }] }
    ],
    "SessionStart": [
      { "matcher": "", "hooks": [{ "command": "session-boot.sh" }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write", "hooks": [{ "command": "post-edit.sh" }] }
    ],
    "Stop": [
      { "matcher": "", "hooks": [{ "command": "stop.sh" }] }
    ]
  }
}
```

#### 5.2 Hook Output Channels (Critical Architecture)

PreToolUse hooks have two distinct output channels depending on exit code. This was the key architectural discovery of SELF-HEAL-001 (resolved after 10 iterations):

| Exit Code | stdout | stderr | Claude Model Sees? | Tool Executes? |
|-----------|--------|--------|-------------------|----------------|
| **0** (allow) | Parsed as JSON. `hookSpecificOutput.additionalContext` injected into Claude's context. | **DISCARDED** (verbose mode only) | Only via `additionalContext` JSON field | Yes |
| **2** (block) | **IGNORED** | Fed to Claude as system-reminder | Yes (stderr becomes blocking error) | No |
| **1, 3+** (error) | Ignored | Verbose mode only | No | Yes |

**Key rule:** To surface information to Claude without blocking, use JSON stdout with `additionalContext` on exit 0. Never use stderr on exit 0 — it is invisible to the model.

**JSON format for non-blocking context injection (exit 0):**

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "Your text injected into Claude's context"
  }
}
```

**Format for blocking (exit 2):** Plain text or JSON to stderr.

#### 5.3 memory-sync.sh Expansions

memory-sync.sh now performs three additional tasks at session end:

1. **Auto-pruning:** Calls `prune-allows.py --quiet` to remove redundant root-level allow entries. Creates backup before modification.
2. **Health log trimming:** Keeps the most recent 100 entries in `health-log.md`, removing older entries.
3. **health_log_entries sentinel:** Gathers current health log line count and updates the AUTOSYNC tag in MEMORY.md.

---

### New Section 5A: Boot Diagnostics System (Insert After Section 5)

#### 5A.1 Overview

The boot diagnostics system is a closed-loop self-diagnosis mechanism that runs at session start and on every mutation tool call. It performs 6 infrastructure health checks plus 1 conditional bonus check, produces a verdict (ALL CLEAR / PROCEED WITH CAUTION / HALT — FIX FIRST), and enforces the verdict through tool blocking and context injection.

**Design goals:**
- Claude sees the infrastructure state before making any changes
- HALT conditions mechanically block mutation tools (Bash, Edit, Write)
- Non-HALT verdicts are injected into Claude's context as actionable information
- Health history is logged for trend detection

#### 5A.2 Execution Flow

```
Session Start
  └─ session-boot.sh (SessionStart hook)
       └─ calls session-start.sh → verdict file → additionalContext JSON → Claude sees it

First Bash/Edit/Write Call
  └─ pre-bash.sh / pre-edit.sh (PreToolUse hook)
       └─ calls session-start.sh (30s TTL dedup)
       └─ reads verdict file
       └─ HALT? → exit 2 (block) + stderr + additionalContext
       └─ Non-HALT? → exit 0 + additionalContext JSON (hash dedup)
       └─ Same hash? → silent, proceed

Subsequent Calls (within 30s)
  └─ session-start.sh exits early (sentinel fresh)
  └─ HALT? → additionalContext injected (stays visible), but allowed (so Claude can fix)
  └─ Non-HALT? → silent (hash unchanged)

After 30s
  └─ session-start.sh re-runs diagnostics
  └─ Invalidates display hash + halt marker + health sentinel
  └─ Fresh verdict → shown again if content changed
  └─ If still HALT → blocks first call again
```

#### 5A.3 The 6 Checks + 1 Bonus

| Check | Name | What It Verifies | Failure Level |
|-------|------|-----------------|---------------|
| CHECK 1 | Memory Integrity | MEMORY.md exists at canonical path, symlink from -mnt-c-Users-mzsai is intact | FAIL |
| CHECK 2 | Surface Count Consistency | Surface count in CLAUDE.md matches MEMORY.md | FAIL on mismatch |
| CHECK 3 | Sentinel Freshness | AUTOSYNC values in MEMORY.md match actual filesystem counts (CLAUDE.md lines, hook count, rule count, V6PP guide lines) | WARN on stale |
| CHECK 4 | Generated Files Exist | All 4 generated files are present and non-empty (api-types.generated.ts, agent-api-types.generated.ts, backend_models.py, rag_models.py) | FAIL on missing |
| CHECK 5 | Generated File Freshness | OpenAPI spec timestamps are not newer than generated files (detects stale codegen) | WARN on stale |
| CHECK 6 | Constraint Registry | All 10 entries in CONSTRAINT_REGISTRY.md have corresponding rule files with required search strings | FAIL on missing |
| BONUS B1 | Root Allow Array Size | Root settings allow array has >100 entries (suggests bloat) | WARN; **skipped** when `dangerouslySkipPermissions: true` |

#### 5A.4 Verdict Levels

| Verdict | Condition | Effect |
|---------|-----------|--------|
| ALL CLEAR | 0 warnings, 0 failures | Injected as context. No blocking. |
| PROCEED WITH CAUTION | 1+ warnings, 0 failures | Injected as context. No blocking. Action note shown. |
| HALT — FIX FIRST | 1+ failures | Blocks first Bash/Edit/Write call (exit 2). Injects as context on subsequent calls. Re-checks every 30s. |

**HALT enforcement lifecycle:**
1. First mutation tool call → blocked (exit 2 + stderr). Claude sees verdict and is forced to acknowledge.
2. Subsequent calls → allowed (Claude can investigate and fix). Verdict stays in context via `additionalContext`.
3. After 30 seconds → fresh diagnostics run. If still HALT → blocks again. If fixed → clears to ALL CLEAR.

**HALT gating coverage:**

| Tool | HALT Gated? | Mechanism |
|------|-------------|-----------|
| Bash | Yes (hard block) | pre-bash.sh exit 2 |
| Edit/Write | Yes (hard block) | pre-edit.sh exit 2 |
| Read/Glob/Grep | No | No hooks — read-only, harmless. Claude needs these to diagnose issues. |

#### 5A.5 Sentinel and Dedup Architecture

Six temporary files manage the boot diagnostics lifecycle:

| File | Purpose | TTL/Lifecycle |
|------|---------|---------------|
| `/tmp/claude-session-boot` | Diagnostics sentinel. Prevents re-running checks within TTL. | 30 seconds |
| `/tmp/claude-boot-verdict.md` | Verdict file. Written by session-start.sh, read by pre-bash/pre-edit/session-boot. | Persists between runs; overwritten on fresh diagnostics |
| `/tmp/claude-boot-verdict-shown-hash` | Content hash (md5sum) of last shown verdict. Prevents re-displaying identical verdicts. | Deleted on fresh diagnostics run |
| `/tmp/claude-halt-enforced` | Halt enforcement marker. Prevents blocking more than once per fresh diagnostics run. | Deleted on fresh diagnostics run |
| `/tmp/claude-health-logged` | Health log append sentinel. Prevents flooding the health log. | 300 seconds |
| `/tmp/claude-boot-evidence` | Execution evidence. Proves session-start.sh ran even if output is invisible. | Overwritten each run |

**On fresh diagnostics run (sentinel stale > 30s),** session-start.sh deletes: shown-hash, halt-enforced, and health-logged markers. This ensures:
- Verdict is re-displayed (even if content is identical to prior session)
- HALT blocks the first call again (if still HALT)
- Health log gets a new entry

#### 5A.6 Trend Detection

The health log (`/home/zaks/bookkeeping/health-log.md`) records one entry per diagnostics run (300s dedup). Each entry includes timestamp, session ID, verdict, warning count, and failure count.

When 3+ consecutive entries have the same non-ALL-CLEAR verdict, a RECURRING ISSUE warning is appended to the verdict file:

```
RECURRING ISSUE (4 sessions): Same non-clear verdict in last 4 sessions.
Root cause investigation needed — auto-remediation may not be working.
```

---

### New Section 5B: Constraint Registry (Insert After Section 5A)

#### 5B.1 Purpose

The constraint registry maps architectural constraints to their enforcement locations. Boot CHECK 6 verifies at session start that every registered constraint has a corresponding rule file containing the expected search string.

#### 5B.2 File Location

`/home/zaks/zakops-agent-api/.claude/CONSTRAINT_REGISTRY.md`

#### 5B.3 Format

Pipe-delimited, 3 columns:

```
CONSTRAINT_NAME | RULE_FILE | SEARCH_STRING
```

Example entries:

```
transition_deal_state choke point | backend-api.md | transition_deal_state
Promise.allSettled mandatory | design-system.md | Promise.allSettled
PIPELINE_STAGES authority | contract-surfaces.md | PIPELINE_STAGES
```

#### 5B.4 Current Entries: 10

All 10 entries are verified at boot by CHECK 6. If a rule file is missing or the search string is not found in the rule file, CHECK 6 reports a FAIL and the verdict becomes HALT.

---

### New Section 5C: Allow Array Pruning (Insert After Section 5B)

#### 5C.1 Purpose

The pruner removes redundant entries from the root-level allow array in `/root/.claude/settings.json`. It identifies root entries that are covered by user-level wildcard patterns.

#### 5C.2 Components

| Component | Path | Purpose |
|-----------|------|---------|
| prune-allows.py | /home/zaks/zakops-agent-api/tools/infra/prune-allows.py | Pruning logic. Compares root entries against 4 user-level patterns. Creates `.bak` before modification. |
| /prune-allows command | .claude/commands/prune-allows.md | Manual trigger for pruning |
| memory-sync.sh | Integration | Auto-runs `prune-allows.py --quiet` at session end |

#### 5C.3 Current State

Under `dangerouslySkipPermissions: true`, the entire allow array is dead weight. The pruner correctly finds 0 redundant entries (root has `Bash(make:*)` universal wildcard, not specific `make sync-*` patterns). A backup exists at `/root/.claude/settings.json.bak.20260209`.

---

### Section 8: Slash Commands — Add 2 Commands

Update the command count from 13 to 15. Add:

| # | Command File | Purpose |
|---|-------------|---------|
| 14 | before-task.md | Pre-task surface validation gate. Runs sync-all-types, validates contract surfaces, checks for drift. |
| 15 | prune-allows.md | Manual allow array pruning trigger. Runs prune-allows.py with verbose output. |

---

### Section 11: Persistent Memory System — Updates

#### 11.3 AUTOSYNC Sentinel Tags — Add 1 Tag

Update from 6 to 7 auto-synced facts. Add:

| Sentinel | Source |
|----------|--------|
| `health_log_entries` | Line count of `/home/zaks/bookkeeping/health-log.md` |

---

### Section 12: Completed Missions — Add 1 Mission

Update from 10 to 11 missions. Add:

| # | Mission ID | Date | Outcome |
|---|-----------|------|---------|
| 11 | SELF-HEAL-001 | 2026-02-09/10 | Self-healing infrastructure. 11 iterations (V1–V11). Boot diagnostics with 6 checks, HALT enforcement via exit 2, additionalContext JSON injection (key architectural discovery), constraint registry (10 entries), health log with trend detection, allow pruning. |

---

### Section 15: Service Map — No Changes

No service changes.

---

### Section 17: Key File Paths Reference — Add Entries

Add the following paths:

| Category | Path |
|----------|------|
| Boot diagnostics engine | /home/zaks/.claude/hooks/session-start.sh |
| SessionStart hook | /home/zaks/.claude/hooks/session-boot.sh |
| Constraint registry | /home/zaks/zakops-agent-api/.claude/CONSTRAINT_REGISTRY.md |
| Health log | /home/zaks/bookkeeping/health-log.md |
| Allow pruner | /home/zaks/zakops-agent-api/tools/infra/prune-allows.py |
| Allow backup | /root/.claude/settings.json.bak.20260209 |
| Before-task command | .claude/commands/before-task.md |
| Prune-allows command | .claude/commands/prune-allows.md |

Update existing entry:

| Category | V6PP Value | V7PP Value |
|----------|-----------|-----------|
| Hook scripts | /home/zaks/.claude/hooks/ (5 scripts) | /home/zaks/.claude/hooks/ (7 scripts) |
| Slash commands | .claude/commands/ (13 files) | .claude/commands/ (15 files) |

---

### Section 18: Document Information — Updates

| Field | V6PP Value | V7PP Value |
|-------|-----------|-----------|
| Version | V6PP (February 9, 2026) | V7PP (February 10, 2026) |
| Supersedes | V5PP-DMS (February 7, 2026) | V6PP (February 9, 2026) |
| Verification | 4 independent session diagnostics | 6 QA sessions, 11 iterations, automated boot verification |
| Total Gates Passed | 82 + 12 remediations | 82 + 12 remediations + SELF-HEAL-001 11-iteration convergence |

Update "Next: In Flight":

| Field | Value |
|-------|-------|
| Next: In Flight | FORENSIC-AUDIT-SURFACES-002 — ground truth discovery for Surfaces 10–14 |
| Next: Planned | Implementation mission for Surfaces 10–14 |

---

## Appendix A: SELF-HEAL-001 Iteration History

The boot diagnostics system required 11 iterations to reach production. This history documents every approach tried and the architectural lessons learned.

### Hook Registration Approaches

| Version | Approach | Result |
|---------|----------|--------|
| V1 | PreToolUse with empty matcher `""` | DIDN'T FIRE — empty matcher matches nothing |
| V2 | `SessionStart` event type (standalone) | DIDN'T FIRE — may have been a version issue |
| V3 | Dual registration (PreToolUse + SessionStart) | DIDN'T FIRE |
| V4 | Piggyback: pre-bash.sh calls session-start.sh | WORKS — reliable on every Bash call |
| V8 | Also added to pre-edit.sh | WORKS — covers Edit/Write first-tool |
| V10 | Added session-boot.sh under SessionStart | WORKS — fires at session creation |

### Output Visibility Approaches

| Version | Approach | Result |
|---------|----------|--------|
| V4 | Child process stdout/stderr | INVISIBLE — child output not propagated |
| V4 | `exec 1>&2` redirect | BROKE hook processing |
| V4 | `>&2 2>/dev/null` | SUPPRESSED all output |
| V5 | Verdict file → parent reads → `cat >&2` | APPEARS in tool output but Claude doesn't process it |
| V10 | `additionalContext` JSON on stdout (exit 0) | **WORKS — injected into Claude's context** |

### Session Dedup Approaches

| Version | Approach | Result |
|---------|----------|--------|
| V1 | `$$` (PID) | FAILED — unique per hook invocation |
| V2 | `$PPID` | FAILED — unique (ephemeral intermediate) |
| V3 | `/proc/PID/comm` walk | FAILED — matched wrong process |
| V3 | "fallback" sentinel | BROKE — persisted forever |
| V4 | TTL 300s | WORKED but too long for cross-session |
| V7 | TTL 30s + content-hash dedup | WORKS |
| V8 | Hash invalidation on fresh diagnostics | WORKS — solves cross-session same-content |

### Key Architectural Lesson

**stderr on exit 0 is invisible to the Claude model by design.** This is the single most important finding of the entire mission. Ten iterations and 5 QA sessions were spent trying to surface hook output via stderr before discovering the `additionalContext` JSON mechanism. The correct pattern:

- **To inform Claude without blocking:** JSON stdout with `hookSpecificOutput.additionalContext`, exit 0
- **To block Claude with a message:** stderr, exit 2
- **Never use stderr on exit 0** — it is discarded

---

## Appendix B: Temporary File Inventory

All boot diagnostics temporary files are in `/tmp/` and do not survive system reboot.

| File | Owner | Purpose | Created By | Consumed By |
|------|-------|---------|-----------|------------|
| claude-session-boot | root | 30s TTL diagnostics sentinel | session-start.sh | session-start.sh |
| claude-boot-verdict.md | root | Verdict text | session-start.sh | pre-bash.sh, pre-edit.sh, session-boot.sh |
| claude-boot-verdict-shown-hash | root | md5sum of last shown verdict | pre-bash.sh / pre-edit.sh | pre-bash.sh / pre-edit.sh |
| claude-halt-enforced | root | HALT block-once marker | pre-bash.sh / pre-edit.sh | pre-bash.sh / pre-edit.sh |
| claude-health-logged | root | 300s health log sentinel | session-start.sh | session-start.sh |
| claude-boot-evidence | root | Execution proof | session-start.sh | QA verification |

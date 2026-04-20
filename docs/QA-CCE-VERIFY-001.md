# MISSION: QA-CCE-VERIFY-001
## Independent QA Verification and Remediation - CLAUDE-CODE-ENHANCE-001
## Date: 2026-02-11
## Classification: QA Verification and Remediation
## Prerequisite: /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md implementation complete (or partially complete with runnable artifacts)
## Successor: Hook lifecycle hardening and observability improvements only after FULL PASS

---

## Preamble: Builder Operating Context

The builder already loads `CLAUDE.md`, canonical memory, hooks, path-scoped rules, and deny rules. This QA mission does not restate those systems. It independently verifies and remediates execution outcomes for `CLAUDE-CODE-ENHANCE-001` using evidence-backed checks.

---

## 1. Mission Objective

Perform independent QA verification and in-scope remediation for:
- `/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md`
- Expected source shape: 361 lines, 4 phases, 9 acceptance criteria (`AC-1` through `AC-9`)

This QA mission verifies, cross-checks, stress-tests, and remediates the 5 feature additions introduced by the source mission:
1. `ENABLE_TOOL_SEARCH=auto:5`
2. `PreCompact` hook + `pre-compact.sh`
3. `TaskCompleted` hook + `task-completed.sh`
4. `alwaysThinkingEnabled=true`
5. `SessionStart` `"compact"` matcher + `compact-recovery.sh`

Expected execution evidence footprint:
- Runtime wiring in `/home/zaks/.claude/settings.json`
- Hook scripts in `/home/zaks/.claude/hooks/`
- Bookkeeping updates in `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md` and `/home/zaks/bookkeeping/CHANGES.md`
- Snapshot artifacts under `/home/zaks/bookkeeping/snapshots/`

QA scope:
- Verify all `AC-1` through `AC-9` with concrete evidence.
- Remediate only what is required to satisfy source ACs.
- Preserve existing hook chain behavior.

Out of scope:
- New product features.
- Dashboard/backend/API code changes.
- Contract surface redesign.

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md
  rg -n '^### Phase [0-9]+' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md
  rg -n '^\| AC-[0-9]+' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md')
t=p.read_text()
phase_count=len(re.findall(r'^### Phase [0-9]+', t, flags=re.M))
ac_count=len(re.findall(r'^\| AC-[0-9]+ \|', t, flags=re.M))
line_count=len(t.splitlines())
print('phase_count=', phase_count)
print('ac_count=', ac_count)
print('line_count=', line_count)
raise SystemExit(0 if (phase_count==4 and ac_count==9 and line_count==361) else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** line/phase/AC counts match expected shape (361, 4, 9).

### PF-2: Execution Footprint Presence

```bash
{
  echo "=== PF-2 EXECUTION FOOTPRINT ==="
  ls -l /home/zaks/.claude/settings.json
  ls -l /home/zaks/.claude/hooks/pre-compact.sh
  ls -l /home/zaks/.claude/hooks/task-completed.sh
  ls -l /home/zaks/.claude/hooks/compact-recovery.sh
  ls -ld /home/zaks/bookkeeping/snapshots || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/PF-2-execution-footprint.txt
```

**PASS if:** settings + all 3 hook scripts exist. Snapshot dir may be created during runtime checks.

### PF-3: settings.json Parse and Baseline Snapshot

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/PF-3-settings-baseline.txt
import json
p='/home/zaks/.claude/settings.json'
d=json.load(open(p))
print('top_level_keys=', sorted(d.keys()))
print('hook_events=', sorted(d.get('hooks',{}).keys()))
print('alwaysThinkingEnabled=', d.get('alwaysThinkingEnabled'))
print('ENABLE_TOOL_SEARCH=', d.get('env',{}).get('ENABLE_TOOL_SEARCH'))
print('SessionStart_entries=', len(d.get('hooks',{}).get('SessionStart',[])))
print('PreCompact_entries=', len(d.get('hooks',{}).get('PreCompact',[])))
print('TaskCompleted_entries=', len(d.get('hooks',{}).get('TaskCompleted',[])))
PY
```

**PASS if:** JSON parses and hook/event structure is readable.

### PF-4: Hook Syntax + Executable Baseline

```bash
{
  echo "=== PF-4 HOOK SYNTAX + EXECUTABLE ==="
  for f in /home/zaks/.claude/hooks/pre-compact.sh /home/zaks/.claude/hooks/task-completed.sh /home/zaks/.claude/hooks/compact-recovery.sh; do
    echo "-- $f"
    ls -l "$f"
    bash -n "$f"
    file "$f"
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/PF-4-hook-syntax-exec.txt
```

**PASS if:** all 3 scripts parse and are executable shell files with no CRLF marker.

### PF-5: Bookkeeping Read Access Baseline

```bash
{
  echo "=== PF-5 BOOKKEEPING ACCESS ==="
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'CLAUDE-CODE-ENHANCE-001|pre-compact|task-completed|compact-recovery|ENABLE_TOOL_SEARCH|alwaysThinkingEnabled' /home/zaks/bookkeeping/CHANGES.md || true
  else
    echo "CHANGES.md not directly readable; trying sudo"
    sudo rg -n 'CLAUDE-CODE-ENHANCE-001|pre-compact|task-completed|compact-recovery|ENABLE_TOOL_SEARCH|alwaysThinkingEnabled' /home/zaks/bookkeeping/CHANGES.md || true
  fi

  if [ -r /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md ]; then
    rg -n 'Hooks:|hook_count|scripts in ~/.claude/hooks' /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md || true
  else
    echo "MEMORY.md not directly readable; trying sudo"
    sudo rg -n 'Hooks:|hook_count|scripts in ~/.claude/hooks' /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md || true
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/PF-5-bookkeeping-access.txt
```

**PASS if:** both files are readable either directly or via `sudo`.

**If PF-5 fails:** continue verification, but classify bookkeeping checks as `PARTIAL` until read access is restored.

---

## 3. Verification Families (VF)

## Verification Family 01 - AC Coverage Matrix and Execution Evidence (AC-1..AC-9)

### VF-01.1: AC Matrix Completeness

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-01.1-ac-matrix.txt
ac_map={
  "AC-1":"ENABLE_TOOL_SEARCH",
  "AC-2":"PreCompact hook runtime",
  "AC-3":"TaskCompleted blocking behavior",
  "AC-4":"alwaysThinkingEnabled",
  "AC-5":"compact recovery additionalContext",
  "AC-6":"script standards (CRLF/exec/owner)",
  "AC-7":"settings JSON + 6 hook events",
  "AC-8":"MEMORY hook count",
  "AC-9":"CHANGES entry",
}
for k,v in ac_map.items():
  print(k, "=>", v)
print("AC_count=", len(ac_map))
raise SystemExit(0 if len(ac_map)==9 else 1)
PY
```

**PASS if:** all 9 ACs are mapped to concrete verification targets.

### VF-01.2: Source Mission Artifact Check (informational)

```bash
{
  echo "=== VF-01.2 SOURCE ARTIFACT CHECK ==="
  ls -l /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-001-BASELINE.md 2>/dev/null || echo "INFO: baseline artifact not found"
  ls -l /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-001-COMPLETION.md 2>/dev/null || echo "INFO: completion artifact not found"
  ls -l /home/zaks/bookkeeping/mission-checkpoints/CLAUDE-CODE-ENHANCE-001.md 2>/dev/null || echo "INFO: checkpoint artifact not found"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-01.2-source-artifacts.txt
```

**PASS if:** informational only. Missing source artifacts are `INFO`, not FAIL, unless your governance policy requires them.

### VF-01.3: Core Files Last-Modified Snapshot

```bash
{
  echo "=== VF-01.3 CORE FILE MTIME SNAPSHOT ==="
  stat /home/zaks/.claude/settings.json
  stat /home/zaks/.claude/hooks/pre-compact.sh
  stat /home/zaks/.claude/hooks/task-completed.sh
  stat /home/zaks/.claude/hooks/compact-recovery.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-01.3-core-mtime.txt
```

**PASS if:** all core files are present with valid metadata.

### VF-01.4: Bookkeeping Target Presence

```bash
{
  echo "=== VF-01.4 BOOKKEEPING TARGET PRESENCE ==="
  ls -l /home/zaks/bookkeeping/CHANGES.md
  ls -l /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md 2>/dev/null || echo "INFO: MEMORY.md path exists but requires elevated read"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-01.4-bookkeeping-presence.txt
```

**PASS if:** target files exist. Readability is handled in VF-06.

**Gate VF-01:** All required checks pass. QA has complete AC targeting and evidence scaffold.

---

## Verification Family 02 - settings.json Contract Wiring (AC-1, AC-4, AC-7)

### VF-02.1: `alwaysThinkingEnabled=true`

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-02.1-thinking-enabled.txt
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
v=d.get('alwaysThinkingEnabled')
print('alwaysThinkingEnabled=', v)
raise SystemExit(0 if v is True else 1)
PY
```

**PASS if:** value is exactly boolean `true`.

### VF-02.2: `ENABLE_TOOL_SEARCH=auto:5`

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-02.2-tool-search.txt
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
v=d.get('env',{}).get('ENABLE_TOOL_SEARCH')
print('ENABLE_TOOL_SEARCH=', v)
raise SystemExit(0 if v=='auto:5' else 1)
PY
```

**PASS if:** value is exactly `auto:5`.

### VF-02.3: Hook Event Set Includes All 6 Events

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-02.3-hook-event-set.txt
import json
required={'PreToolUse','PostToolUse','SessionStart','Stop','PreCompact','TaskCompleted'}
d=json.load(open('/home/zaks/.claude/settings.json'))
events=set(d.get('hooks',{}).keys())
missing=sorted(required-events)
extra=sorted(events-required)
print('events=', sorted(events))
print('missing=', missing)
print('extra=', extra)
raise SystemExit(0 if not missing else 1)
PY
```

**PASS if:** all required events are present.

### VF-02.4: `PreCompact` Hook Contract

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-02.4-precompact-contract.txt
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
arr=d.get('hooks',{}).get('PreCompact',[])
ok=False
for entry in arr:
  for h in entry.get('hooks',[]):
    if h.get('type')=='command' and h.get('command')=='/home/zaks/.claude/hooks/pre-compact.sh':
      print('matcher=', entry.get('matcher'))
      print('timeout=', h.get('timeout'))
      print('async=', h.get('async'))
      ok=(entry.get('matcher','')=='' and h.get('timeout')==15 and h.get('async') is True)
print('ok=', ok)
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** command path, matcher, timeout, and async semantics match AC contract.

### VF-02.5: `TaskCompleted` and compact `SessionStart` Wiring

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-02.5-taskcompleted-sessionstart.txt
import json
d=json.load(open('/home/zaks/.claude/settings.json'))

tc_ok=False
for entry in d.get('hooks',{}).get('TaskCompleted',[]):
  for h in entry.get('hooks',[]):
    if h.get('command')=='/home/zaks/.claude/hooks/task-completed.sh':
      tc_ok=(entry.get('matcher','')=='' and h.get('timeout')==30)
      print('taskcompleted_statusMessage=', h.get('statusMessage'))

compact_ok=False
for entry in d.get('hooks',{}).get('SessionStart',[]):
  if entry.get('matcher')=='compact':
    for h in entry.get('hooks',[]):
      if h.get('command')=='/home/zaks/.claude/hooks/compact-recovery.sh':
        compact_ok=(h.get('timeout')==15)
        print('compact_statusMessage=', h.get('statusMessage'))

print('tc_ok=', tc_ok)
print('compact_ok=', compact_ok)
raise SystemExit(0 if (tc_ok and compact_ok) else 1)
PY
```

**PASS if:** both hooks are correctly wired and parameterized.

**Gate VF-02:** All 5 checks pass. `settings.json` contract wiring is correct.

---

## Verification Family 03 - Hook Script Standards and WSL Safety (AC-6)

### VF-03.1: Presence + Shebang

```bash
{
  echo "=== VF-03.1 PRESENCE + SHEBANG ==="
  for f in /home/zaks/.claude/hooks/pre-compact.sh /home/zaks/.claude/hooks/task-completed.sh /home/zaks/.claude/hooks/compact-recovery.sh; do
    test -f "$f" || exit 1
    head -n 1 "$f"
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-03.1-presence-shebang.txt
```

**PASS if:** all files exist and line 1 is `#!/usr/bin/env bash`.

### VF-03.2: Executable + Ownership

```bash
{
  echo "=== VF-03.2 EXEC + OWNERSHIP ==="
  ls -l /home/zaks/.claude/hooks/pre-compact.sh
  ls -l /home/zaks/.claude/hooks/task-completed.sh
  ls -l /home/zaks/.claude/hooks/compact-recovery.sh
  stat -c '%U:%G %a %n' /home/zaks/.claude/hooks/pre-compact.sh /home/zaks/.claude/hooks/task-completed.sh /home/zaks/.claude/hooks/compact-recovery.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-03.2-exec-ownership.txt
```

**PASS if:** each file is executable and owned by `zaks:zaks`.

### VF-03.3: No CRLF

```bash
{
  echo "=== VF-03.3 CRLF CHECK ==="
  file /home/zaks/.claude/hooks/pre-compact.sh
  file /home/zaks/.claude/hooks/task-completed.sh
  file /home/zaks/.claude/hooks/compact-recovery.sh
  ! file /home/zaks/.claude/hooks/pre-compact.sh | grep -q 'CRLF'
  ! file /home/zaks/.claude/hooks/task-completed.sh | grep -q 'CRLF'
  ! file /home/zaks/.claude/hooks/compact-recovery.sh | grep -q 'CRLF'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-03.3-no-crlf.txt
```

**PASS if:** no script reports `CRLF`.

### VF-03.4: Syntax Validity

```bash
{
  echo "=== VF-03.4 SYNTAX VALIDITY ==="
  bash -n /home/zaks/.claude/hooks/pre-compact.sh
  bash -n /home/zaks/.claude/hooks/task-completed.sh
  bash -n /home/zaks/.claude/hooks/compact-recovery.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-03.4-syntax-validity.txt
```

**PASS if:** all scripts pass `bash -n`.

### VF-03.5: Exit Code Contract in `task-completed.sh`

```bash
{
  echo "=== VF-03.5 EXIT CODE CONTRACT ==="
  rg -n 'exit 0|exit 2|exit 1' /home/zaks/.claude/hooks/task-completed.sh || true
  ! rg -n 'exit 1' /home/zaks/.claude/hooks/task-completed.sh
  rg -n 'exit 2' /home/zaks/.claude/hooks/task-completed.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-03.5-exit-code-contract.txt
```

**PASS if:** script uses `exit 0` and `exit 2`, and does not use `exit 1`.

**Gate VF-03:** All 5 checks pass. Script hygiene and WSL safety requirements are satisfied.

---

## Verification Family 04 - Runtime Behavior: PreCompact and Compact Recovery (AC-2, AC-5)

### VF-04.1: Dry-Run `pre-compact.sh` Returns 0 and Creates Snapshot

```bash
{
  echo "=== VF-04.1 PRE-COMPACT DRY RUN ==="
  mkdir -p /home/zaks/bookkeeping/snapshots
  BEFORE=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md 2>/dev/null | wc -l)
  echo '{"trigger":"manual","session_id":"qa-cce-verify"}' | bash /home/zaks/.claude/hooks/pre-compact.sh
  RC=$?
  AFTER=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md 2>/dev/null | wc -l)
  echo "before=$BEFORE after=$AFTER rc=$RC"
  test "$RC" -eq 0
  test "$AFTER" -ge "$BEFORE"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-04.1-precompact-dry-run.txt
```

**PASS if:** exit code is 0 and snapshot count is not reduced unexpectedly.

### VF-04.2: Snapshot Content Structure

```bash
{
  echo "=== VF-04.2 SNAPSHOT STRUCTURE ==="
  LATEST=$(ls -1t /home/zaks/bookkeeping/snapshots/pre-compact-*.md | head -1)
  echo "latest=$LATEST"
  test -f "$LATEST"
  rg -n '^# Pre-Compact Snapshot|^## Recent Changes|^## Monorepo Git Status|^## Backend Git Status|^## Recent Bookkeeping Snapshots' "$LATEST"
  head -n 80 "$LATEST"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-04.2-snapshot-structure.txt
```

**PASS if:** latest snapshot exists and contains required sections.

### VF-04.3: Dry-Run `compact-recovery.sh` Returns Valid JSON

```bash
bash /home/zaks/.claude/hooks/compact-recovery.sh | python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-04.3-compact-recovery-json.txt
import json,sys
d=json.load(sys.stdin)
h=d.get('hookSpecificOutput',{})
ctx=h.get('additionalContext','')
print('hookEventName=', h.get('hookEventName'))
print('context_len=', len(ctx))
print('has_key_paths=', 'Key Paths Reminder' in ctx)
print('has_operating_reminders=', 'Operating Reminders' in ctx)
raise SystemExit(0 if (h.get('hookEventName')=='SessionStart' and len(ctx)>0) else 1)
PY
```

**PASS if:** valid JSON is emitted and `additionalContext` is non-empty.

### VF-04.4: Compact Matcher Additional Wiring Integrity

```bash
{
  echo "=== VF-04.4 COMPACT MATCHER INTEGRITY ==="
  python3 - <<'PY'
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
entries=d.get('hooks',{}).get('SessionStart',[])
for i,e in enumerate(entries):
  print('idx=',i,'matcher=',e.get('matcher'))
  for h in e.get('hooks',[]):
    print('  cmd=',h.get('command'),'timeout=',h.get('timeout'))
compact=[e for e in entries if e.get('matcher')=='compact']
raise SystemExit(0 if compact else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-04.4-compact-matcher-wiring.txt
```

**PASS if:** `SessionStart` includes a `compact` matcher entry.

### VF-04.5: PreCompact Remains Non-Blocking by Contract

```bash
{
  echo "=== VF-04.5 PRE-COMPACT NON-BLOCKING CONTRACT ==="
  python3 - <<'PY'
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
ok=False
for e in d.get('hooks',{}).get('PreCompact',[]):
  for h in e.get('hooks',[]):
    if h.get('command')=='/home/zaks/.claude/hooks/pre-compact.sh':
      ok=(h.get('async') is True and h.get('timeout')==15)
print('ok=',ok)
raise SystemExit(0 if ok else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-04.5-precompact-nonblocking.txt
```

**PASS if:** hook registration is `async: true` with timeout `15`.

**Gate VF-04:** All 5 checks pass. Compaction pre/post lifecycle behavior is functionally correct.

---

## Verification Family 05 - TaskCompleted Gate Behavior (AC-3)

### VF-05.1: Static Gate Marker Presence

```bash
{
  echo "=== VF-05.1 STATIC GATE MARKERS ==="
  rg -n 'Gate 1: CRLF|Gate 2: Root ownership|Gate 3: TypeScript check|Task quality gates FAILED|exit 2' /home/zaks/.claude/hooks/task-completed.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-05.1-static-gate-markers.txt
```

**PASS if:** all three gate markers and failure contract are present.

### VF-05.2: Baseline Clean Run Returns Allow (exit 0)

```bash
{
  echo "=== VF-05.2 BASELINE RUN ==="
  bash /home/zaks/.claude/hooks/task-completed.sh
  RC=$?
  echo "rc=$RC"
  test "$RC" -eq 0
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-05.2-baseline-run.txt
```

**PASS if:** returns `0`. If it returns `2`, classify and remediate detected issue, then rerun.

### VF-05.3: Injected CRLF Causes Block (exit 2)

```bash
{
  echo "=== VF-05.3 CRLF INJECTION BLOCK TEST ==="
  TEST_FILE=/home/zaks/.claude/hooks/qa-cce-crlf-test.sh
  printf '#!/usr/bin/env bash\r\necho test\r\n' > "$TEST_FILE"
  chmod +x "$TEST_FILE"
  touch "$TEST_FILE"

  set +e
  ERR_OUT=$(bash /home/zaks/.claude/hooks/task-completed.sh 2>&1)
  RC=$?
  set -e
  echo "rc=$RC"
  echo "$ERR_OUT"
  test "$RC" -eq 2
  echo "$ERR_OUT" | rg -n 'GATE 1 FAIL|CRLF detected'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-05.3-crlf-block.txt
```

**PASS if:** script returns `2` and reports Gate 1 CRLF failure.

### VF-05.4: Cleanup and Recovery to Allow (exit 0)

```bash
{
  echo "=== VF-05.4 CRLF CLEANUP RECOVERY ==="
  TEST_FILE=/home/zaks/.claude/hooks/qa-cce-crlf-test.sh
  sed -i 's/\r$//' "$TEST_FILE"
  bash /home/zaks/.claude/hooks/task-completed.sh
  RC=$?
  rm -f "$TEST_FILE"
  echo "rc=$RC"
  test "$RC" -eq 0
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-05.4-cleanup-recovery.txt
```

**PASS if:** after CRLF remediation, gate returns `0`.

### VF-05.5: TypeScript Gate Command Contract

```bash
{
  echo "=== VF-05.5 TYPESCRIPT GATE CONTRACT ==="
  rg -n 'npx tsc --noEmit|timeout 10|TS_CHANGED|apps/dashboard' /home/zaks/.claude/hooks/task-completed.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-05.5-ts-gate-contract.txt
```

**PASS if:** TypeScript gate wiring is present as defined by source mission.

**Gate VF-05:** All 5 checks pass. Task completion blocking behavior is correct and recoverable.

---

## Verification Family 06 - Bookkeeping Outcomes (AC-8, AC-9)

### VF-06.1: CHANGES Entry Integrity

```bash
{
  echo "=== VF-06.1 CHANGES ENTRY ==="
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'CLAUDE-CODE-ENHANCE-001|pre-compact|task-completed|compact-recovery|ENABLE_TOOL_SEARCH|alwaysThinkingEnabled' /home/zaks/bookkeeping/CHANGES.md
  else
    sudo rg -n 'CLAUDE-CODE-ENHANCE-001|pre-compact|task-completed|compact-recovery|ENABLE_TOOL_SEARCH|alwaysThinkingEnabled' /home/zaks/bookkeeping/CHANGES.md
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-06.1-changes-entry.txt
```

**PASS if:** mission entry and feature references are present.

### VF-06.2: MEMORY Hook Count Entry

```bash
{
  echo "=== VF-06.2 MEMORY HOOK COUNT ==="
  if [ -r /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md ]; then
    rg -n 'Hooks: 10|hook_count|scripts in ~/.claude/hooks' /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md
  else
    sudo rg -n 'Hooks: 10|hook_count|scripts in ~/.claude/hooks' /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-06.2-memory-hook-count.txt
```

**PASS if:** memory contains hook count fact with value `10`.

### VF-06.3: Actual Hook Script Count Cross-Check

```bash
{
  echo "=== VF-06.3 ACTUAL HOOK COUNT ==="
  COUNT=$(ls /home/zaks/.claude/hooks/*.sh | wc -l | tr -d ' ')
  echo "actual_hook_count=$COUNT"
  test "$COUNT" -eq 10
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-06.3-actual-hook-count.txt
```

**PASS if:** actual hook script count is `10`.

### VF-06.4: New Hook Files Included in Count

```bash
{
  echo "=== VF-06.4 NEW HOOK PRESENCE ==="
  ls -1 /home/zaks/.claude/hooks/*.sh | rg -n 'pre-compact\.sh|task-completed\.sh|compact-recovery\.sh'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-06.4-new-hook-presence.txt
```

**PASS if:** all three new scripts are present in the hook inventory.

**Gate VF-06:** All 4 checks pass. Bookkeeping outcomes are consistent with source ACs.

---

## Verification Family 07 - No Regression and Additive-Only Integrity

### VF-07.1: Core Existing Hook Files Still Present

```bash
{
  echo "=== VF-07.1 CORE HOOK PRESENCE ==="
  for f in pre-edit.sh pre-bash.sh post-edit.sh session-boot.sh stop.sh memory-sync.sh session-start.sh; do
    test -f "/home/zaks/.claude/hooks/$f" || exit 1
    ls -l "/home/zaks/.claude/hooks/$f"
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-07.1-core-hook-presence.txt
```

**PASS if:** all existing core hook files remain present.

### VF-07.2: settings.json Still References Existing Hook Chain

```bash
{
  echo "=== VF-07.2 SETTINGS EXISTING CHAIN ==="
  python3 - <<'PY'
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
cmds=[]
for evt,arr in d.get('hooks',{}).items():
  for e in arr:
    for h in e.get('hooks',[]):
      c=h.get('command')
      if c: cmds.append(c)
for required in [
  '/home/zaks/.claude/hooks/pre-edit.sh',
  '/home/zaks/.claude/hooks/pre-bash.sh',
  '/home/zaks/.claude/hooks/post-edit.sh',
  '/home/zaks/.claude/hooks/session-boot.sh',
  '/home/zaks/.claude/hooks/stop.sh',
]:
  print(required, '=>', required in cmds)
  if required not in cmds:
    raise SystemExit(1)
print('PASS')
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-07.2-settings-existing-chain.txt
```

**PASS if:** existing hook commands remain wired.

### VF-07.3: settings.json Remains Valid JSON

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-07.3-settings-json-valid.txt
import json
json.load(open('/home/zaks/.claude/settings.json'))
print('settings_json=PASS')
PY
```

**PASS if:** JSON parses successfully after runtime tests.

### VF-07.4: New Hook Scripts Do Not Use Forbidden Exit 1 Blocking Pattern

```bash
{
  echo "=== VF-07.4 NEW HOOK EXIT CONTRACT ==="
  rg -n 'exit 1' /home/zaks/.claude/hooks/pre-compact.sh /home/zaks/.claude/hooks/task-completed.sh /home/zaks/.claude/hooks/compact-recovery.sh || true
  ! rg -n 'exit 1' /home/zaks/.claude/hooks/pre-compact.sh /home/zaks/.claude/hooks/task-completed.sh /home/zaks/.claude/hooks/compact-recovery.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/VF-07.4-no-exit1.txt
```

**PASS if:** no new hook script uses `exit 1`.

**Gate VF-07:** All 4 checks pass. Additive-only integrity preserved and no critical regression detected.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Hook Paths in settings.json Must Exist on Disk

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/XC-1-hook-paths-exist.txt
import json, os
d=json.load(open('/home/zaks/.claude/settings.json'))
missing=[]
for evt,arr in d.get('hooks',{}).items():
  for e in arr:
    for h in e.get('hooks',[]):
      c=h.get('command')
      if c and c.startswith('/home/zaks/.claude/hooks/') and not os.path.exists(c):
        missing.append((evt,c))
print('missing=', missing)
raise SystemExit(0 if not missing else 1)
PY
```

### XC-2: `PreCompact` Command Matches Script Inventory

```bash
{
  echo "=== XC-2 PRECOMPACT PATH CONSISTENCY ==="
  rg -n '/home/zaks/.claude/hooks/pre-compact.sh' /home/zaks/.claude/settings.json
  test -f /home/zaks/.claude/hooks/pre-compact.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/XC-2-precompact-path-consistency.txt
```

### XC-3: `TaskCompleted` Command Matches Script Inventory

```bash
{
  echo "=== XC-3 TASKCOMPLETED PATH CONSISTENCY ==="
  rg -n '/home/zaks/.claude/hooks/task-completed.sh' /home/zaks/.claude/settings.json
  test -f /home/zaks/.claude/hooks/task-completed.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/XC-3-taskcompleted-path-consistency.txt
```

### XC-4: Compact `SessionStart` Path Matches Script Inventory

```bash
{
  echo "=== XC-4 COMPACT SESSIONSTART PATH CONSISTENCY ==="
  rg -n '/home/zaks/.claude/hooks/compact-recovery.sh' /home/zaks/.claude/settings.json
  test -f /home/zaks/.claude/hooks/compact-recovery.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/XC-4-compact-path-consistency.txt
```

### XC-5: MEMORY Hook Count vs Actual Hook Count

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/XC-5-memory-vs-actual-hook-count.txt
import subprocess, re
actual=int(subprocess.check_output("ls /home/zaks/.claude/hooks/*.sh | wc -l", shell=True, text=True).strip())
print('actual_hook_count=', actual)
mem_text=""
for cmd in [
  "cat /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md",
  "sudo cat /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
]:
  try:
    mem_text=subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
    break
  except Exception:
    pass
if not mem_text:
  print('memory_read=FAILED')
  raise SystemExit(1)
m=re.search(r'Hooks:\s*(\d+)', mem_text)
if not m:
  print('memory_hook_fact=NOT_FOUND')
  raise SystemExit(1)
mem_count=int(m.group(1))
print('memory_hook_count=', mem_count)
raise SystemExit(0 if mem_count==actual else 1)
PY
```

### XC-6: AC-1/AC-4 Values in settings vs CHANGES Narrative

```bash
{
  echo "=== XC-6 SETTINGS VS CHANGES NARRATIVE ==="
  python3 - <<'PY'
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
print('alwaysThinkingEnabled=', d.get('alwaysThinkingEnabled'))
print('ENABLE_TOOL_SEARCH=', d.get('env',{}).get('ENABLE_TOOL_SEARCH'))
PY
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'CLAUDE-CODE-ENHANCE-001|alwaysThinkingEnabled|ENABLE_TOOL_SEARCH|auto:5' /home/zaks/bookkeeping/CHANGES.md || true
  else
    sudo rg -n 'CLAUDE-CODE-ENHANCE-001|alwaysThinkingEnabled|ENABLE_TOOL_SEARCH|auto:5' /home/zaks/bookkeeping/CHANGES.md || true
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/XC-6-settings-vs-changes.txt
```

**XC Gate:** All 6 checks pass. Configuration, inventory, and bookkeeping narratives are consistent.

---

## 5. Stress Tests (ST)

### ST-1: Repeated PreCompact Runs Remain Stable

```bash
{
  echo "=== ST-1 REPEATED PRECOMPACT ==="
  for i in 1 2 3; do
    echo "{\"trigger\":\"stress-$i\",\"session_id\":\"qa-cce-st-$i\"}" | bash /home/zaks/.claude/hooks/pre-compact.sh
  done
  COUNT=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "snapshot_count=$COUNT"
  test "$COUNT" -le 10
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/ST-1-repeated-precompact.txt
```

### ST-2: PreCompact Auto-Cleanup Enforcement

```bash
{
  echo "=== ST-2 PRECOMPACT AUTO-CLEANUP ==="
  mkdir -p /home/zaks/bookkeeping/snapshots
  for i in $(seq 1 12); do
    echo "{\"trigger\":\"cleanup-$i\",\"session_id\":\"qa-cce-cleanup-$i\"}" | bash /home/zaks/.claude/hooks/pre-compact.sh
  done
  COUNT=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "snapshot_count_after_12_runs=$COUNT"
  test "$COUNT" -le 10
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/ST-2-precompact-cleanup.txt
```

### ST-3: Repeated Compact-Recovery JSON Stability

```bash
{
  echo "=== ST-3 REPEATED COMPACT RECOVERY ==="
  for i in 1 2 3; do
    bash /home/zaks/.claude/hooks/compact-recovery.sh | python3 - <<'PY'
import json,sys
d=json.load(sys.stdin)
ctx=d.get('hookSpecificOutput',{}).get('additionalContext','')
print('ctx_len=', len(ctx))
raise SystemExit(0 if len(ctx)>0 else 1)
PY
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/ST-3-repeated-compact-recovery.txt
```

### ST-4: TaskCompleted CRLF Block-Recover Cycle

```bash
{
  echo "=== ST-4 TASKCOMPLETED BLOCK-RECOVER CYCLE ==="
  TEST_FILE=/home/zaks/.claude/hooks/qa-cce-st4-crlf.sh
  printf '#!/usr/bin/env bash\r\necho st4\r\n' > "$TEST_FILE"
  chmod +x "$TEST_FILE"

  set +e
  bash /home/zaks/.claude/hooks/task-completed.sh >/tmp/qa-cce-st4.out 2>&1
  RC_BLOCK=$?
  set -e
  echo "rc_block=$RC_BLOCK"
  test "$RC_BLOCK" -eq 2

  sed -i 's/\r$//' "$TEST_FILE"
  bash /home/zaks/.claude/hooks/task-completed.sh >/tmp/qa-cce-st4.out 2>&1
  RC_RECOVER=$?
  echo "rc_recover=$RC_RECOVER"
  rm -f "$TEST_FILE" /tmp/qa-cce-st4.out
  test "$RC_RECOVER" -eq 0
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/ST-4-taskcompleted-cycle.txt
```

### ST-5: Root Ownership Gate Probe (Conditional)

```bash
{
  echo "=== ST-5 ROOT OWNERSHIP PROBE ==="
  if [ "$(id -u)" -eq 0 ]; then
    TEST_FILE=/home/zaks/.claude/hooks/qa-cce-st5-root.sh
    printf '#!/usr/bin/env bash\necho root-test\n' > "$TEST_FILE"
    chmod +x "$TEST_FILE"
    chown root:root "$TEST_FILE"
    touch "$TEST_FILE"
    set +e
    OUT=$(bash /home/zaks/.claude/hooks/task-completed.sh 2>&1)
    RC=$?
    set -e
    echo "rc=$RC"
    echo "$OUT"
    test "$RC" -eq 2
    echo "$OUT" | rg -n 'GATE 2 FAIL|Root-owned hook files'
    chown zaks:zaks "$TEST_FILE"
    rm -f "$TEST_FILE"
  else
    echo "INFO: Non-root session - ST-5 downgraded to static verification"
    rg -n 'Gate 2: Root ownership|-user root|-mmin -60' /home/zaks/.claude/hooks/task-completed.sh
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/ST-5-root-ownership-probe.txt
```

### ST-6: settings.json Parse Repeatability

```bash
{
  echo "=== ST-6 SETTINGS PARSE REPEATABILITY ==="
  for i in $(seq 1 10); do
    python3 - <<'PY'
import json
json.load(open('/home/zaks/.claude/settings.json'))
print('ok')
PY
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/ST-6-settings-parse-repeatability.txt
```

### ST-7: Existing Hook Chain Coexists with New Hooks

```bash
{
  echo "=== ST-7 EXISTING + NEW HOOK COEXISTENCE ==="
  python3 - <<'PY'
import json
d=json.load(open('/home/zaks/.claude/settings.json'))
hooks=d.get('hooks',{})
required_existing=['PreToolUse','PostToolUse','SessionStart','Stop']
required_new=['PreCompact','TaskCompleted']
for k in required_existing + required_new:
  print(k, '=>', k in hooks)
  if k not in hooks:
    raise SystemExit(1)
print('PASS')
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/ST-7-hook-coexistence.txt
```

**ST Gate:** All 7 stress tests pass (or are justified as INFO where explicitly allowed by conditional logic).

---

## 6. Remediation Protocol

For any FAIL:

1. Read the failing evidence file in `/home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/evidence/`.
2. Classify the failure:
   - `MISSING_FIX`
   - `REGRESSION`
   - `SCOPE_GAP`
   - `FALSE_POSITIVE`
   - `NOT_IMPLEMENTED`
   - `PARTIAL`
   - `VIOLATION`
3. Apply a surgical fix only within source mission scope (`settings.json`, 3 hook scripts, MEMORY hook count line, CHANGES entry).
4. Re-run only the failing check until PASS.
5. Re-run dependent family gate and all XC checks.
6. Re-run `VF-07.3` JSON parse and `ST-7` coexistence check before declaring closure.
7. Record remediation in final completion report with:
   - failing check ID
   - root cause
   - fix path(s)
   - rerun evidence file

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Add dedicated `qa-cce-verify` Make target
Wrap PF/VF/XC/ST command groups in a repeatable target.

### ENH-2: Add hook schema lint for `settings.json`
Validate hook event contracts automatically (matcher, timeout, async fields).

### ENH-3: Add unit tests for `compact-recovery.sh` JSON shape
Codify expected `hookSpecificOutput.additionalContext` schema.

### ENH-4: Add deterministic fixture mode to `task-completed.sh`
Support targeted test paths to avoid broad filesystem scans during QA.

### ENH-5: Add explicit gate result summary output in hook scripts
Emit machine-parseable PASS/FAIL markers for easier QA parsing.

### ENH-6: Promote hook ownership policy into a reusable validator
Avoid repeating ownership checks across missions.

### ENH-7: Add snapshot retention policy config
Allow retention count to be configured via env instead of hardcoded `10`.

### ENH-8: Add CHANGES write-readability standardization
Avoid mixed ownership scenarios that require elevated reads for QA.

### ENH-9: Add mission artifact convention for all infra missions
Require baseline/completion/checkpoint docs to simplify downstream QA.

### ENH-10: Add post-compact context quality assertion
Validate that injected context includes active mission/task metadata, not only static reminders.

---

## 8. Scorecard Template

```text
QA-CCE-VERIFY-001 - Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (AC Coverage + Evidence): __ / 4 PASS
  VF-02 (settings Contract Wiring): __ / 5 PASS
  VF-03 (Script Standards + WSL): __ / 5 PASS
  VF-04 (PreCompact + Recovery Runtime): __ / 5 PASS
  VF-05 (TaskCompleted Behavior): __ / 5 PASS
  VF-06 (Bookkeeping Outcomes): __ / 4 PASS
  VF-07 (No Regression + Additive Integrity): __ / 4 PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 PASS

Total:
  41 / 41 required checks PASS
  FAIL: __
  INFO: __

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not build new features. This is a QA verify/remediate mission only.
2. Remediate, do not redesign.
3. Evidence-based only. Every PASS must have a corresponding evidence file.
4. Keep fixes in scope: `settings.json`, the 3 new hook scripts, MEMORY hook-count line, CHANGES entry.
5. Preserve existing hook chain behavior (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`).
6. Do not remove or weaken blocking semantics in `task-completed.sh`.
7. Do not use destructive git commands (`git reset --hard`, history rewrite).
8. If a test requires root and session is non-root, classify as `INFO` when conditional branch is explicitly defined.
9. If bookkeeping files are permission-restricted, use read-elevation only; do not relax file permissions as a QA shortcut.
10. After any remediation, re-run affected gate plus XC checks before closure.

---

## 10. Stop Condition

Stop when all 41 required checks are PASS (or explicitly justified as INFO in conditional tests), all remediations are applied and re-verified, and the scorecard is complete with evidence references.

Do not proceed to follow-on enhancement missions until:
- `VF-02` through `VF-07` gates are all PASS,
- XC gate is PASS,
- ST gate is PASS,
- and overall verdict is `FULL PASS`.

---
*End of Mission Prompt - QA-CCE-VERIFY-001*


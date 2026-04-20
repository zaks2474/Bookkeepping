# QA-V6GR-VERIFY-001: V6-GUIDE-REGEN-001 Verification & Remediation

## Date: 2026-02-09
## Predecessor: V6-GUIDE-REGEN-001 (4-phase capstone mission)
## Classification: Post-Mission QA — Verification, Remediation, Enhancement Discovery

---

## Verification Framework

### Verdict Rules
- **PASS**: Evidence confirms the requirement is met exactly as specified
- **FAIL**: Evidence shows a gap, error, or missing artifact. Remediation section follows
- **SKIP**: Gate not applicable in current context (documented why)

### Evidence Standard
Every gate captures evidence via `bash` commands piped through `tee` to an evidence file. No subjective assessments — only filesystem-verifiable facts.

### Execution Discipline
1. Run gates in document order (VF-01 through VF-10, then ST, XC, ENH)
2. Capture ALL evidence before rendering ANY verdict
3. If a gate FAILs, execute its **FIX** section immediately, then re-run the gate
4. Do not skip failed gates — fix forward

### Fix Protocol
Each FIX section contains exact commands or edits. After applying a fix:
1. Re-run the specific gate that failed
2. Confirm PASS
3. Record the remediation in the final scorecard

---

## Pre-Flight Baseline

Capture environment snapshot before any verification. All output to evidence file.

```bash
EVIDENCE="/tmp/qa-v6gr-evidence.txt"
echo "=== QA-V6GR-VERIFY-001 Pre-Flight ===" | tee "$EVIDENCE"
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" | tee -a "$EVIDENCE"

# V6PP guide existence and line count
echo "--- V6PP Guide ---" | tee -a "$EVIDENCE"
wc -l /home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md 2>&1 | tee -a "$EVIDENCE"

# Settings.json counts
echo "--- Settings.json ---" | tee -a "$EVIDENCE"
DENY_COUNT=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(len(d.get('permissions',{}).get('deny',[])))")
ALLOW_COUNT=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(len(d.get('permissions',{}).get('allow',[])))")
echo "Deny rules: $DENY_COUNT" | tee -a "$EVIDENCE"
echo "Allow rules: $ALLOW_COUNT" | tee -a "$EVIDENCE"

# MCP servers
echo "--- MCP Servers ---" | tee -a "$EVIDENCE"
python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(list(d.get('mcpServers',{}).keys()))" | tee -a "$EVIDENCE"

# Hooks
echo "--- Hooks ---" | tee -a "$EVIDENCE"
ls /home/zaks/.claude/hooks/*.sh 2>&1 | tee -a "$EVIDENCE"
HOOK_COUNT=$(ls /home/zaks/.claude/hooks/*.sh 2>/dev/null | wc -l)
echo "Hook count: $HOOK_COUNT" | tee -a "$EVIDENCE"

# Rules
echo "--- Rules ---" | tee -a "$EVIDENCE"
ls /home/zaks/zakops-agent-api/.claude/rules/*.md 2>&1 | tee -a "$EVIDENCE"
RULE_COUNT=$(ls /home/zaks/zakops-agent-api/.claude/rules/*.md 2>/dev/null | wc -l)
echo "Rule count: $RULE_COUNT" | tee -a "$EVIDENCE"

# Commands
echo "--- Commands ---" | tee -a "$EVIDENCE"
ls /home/zaks/zakops-agent-api/.claude/commands/*.md 2>&1 | tee -a "$EVIDENCE"
CMD_COUNT=$(ls /home/zaks/zakops-agent-api/.claude/commands/*.md 2>/dev/null | wc -l)
echo "Command count: $CMD_COUNT" | tee -a "$EVIDENCE"

# CLAUDE.md line counts
echo "--- CLAUDE.md ---" | tee -a "$EVIDENCE"
wc -l /home/zaks/zakops-agent-api/CLAUDE.md 2>&1 | tee -a "$EVIDENCE"
wc -l /home/zaks/CLAUDE.md 2>&1 | tee -a "$EVIDENCE"

# MEMORY.md
echo "--- MEMORY.md ---" | tee -a "$EVIDENCE"
wc -l /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md 2>&1 | tee -a "$EVIDENCE"
wc -l /root/.claude/projects/-home-zaks/memory/MEMORY.md 2>&1 | tee -a "$EVIDENCE"

# Agent definitions
echo "--- Agent Definitions ---" | tee -a "$EVIDENCE"
ls /home/zaks/.claude/agents/*.md 2>&1 | tee -a "$EVIDENCE"

# TriPass script
echo "--- TriPass ---" | tee -a "$EVIDENCE"
wc -l /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>&1 | tee -a "$EVIDENCE"

echo "=== Pre-Flight Complete ===" | tee -a "$EVIDENCE"
```

---

## VF-01: TriPass QA Enhancements (Mission Gate V-1)

**Mission Requirement:** All 5 enhancements (ENH-1, ENH-2, ENH-3, ENH-8, ENH-9) applied to TriPass pipeline.

### VF-01.1: ENH-3 — Trap Handler Present

```bash
echo "=== VF-01.1: Trap handler ===" | tee -a "$EVIDENCE"
grep -n "^trap\b\|^[[:space:]]*trap\b" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>&1 | tee -a "$EVIDENCE"
TRAP_LINE=$(grep -c "trap.*release_lock.*EXIT.*ERR.*INT.*TERM" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || TRAP_LINE=0
echo "Trap with all 4 signals: $TRAP_LINE" | tee -a "$EVIDENCE"
```

**Expected:** At least 1 trap statement catching EXIT, ERR, INT, TERM that calls `release_lock`.
**Verdict:** `[ "$TRAP_LINE" -ge 1 ]` → PASS / FAIL

**FIX (if FAIL):** Add `trap 'release_lock' EXIT ERR INT TERM` after the `acquire_lock` call in the orchestrator's run command function.

### VF-01.2: ENH-3 — release_lock Function Exists

```bash
echo "=== VF-01.2: release_lock function ===" | tee -a "$EVIDENCE"
grep -n "release_lock" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>&1 | tee -a "$EVIDENCE"
HAS_RELEASE=$(grep -c "release_lock()" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || HAS_RELEASE=0
HAS_RM_LOCK=$(grep -A3 "release_lock()" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null | grep -c "rm -f.*LOCKFILE" 2>/dev/null) || HAS_RM_LOCK=0
echo "release_lock defined: $HAS_RELEASE, removes lockfile: $HAS_RM_LOCK" | tee -a "$EVIDENCE"
```

**Expected:** `release_lock()` defined AND contains `rm -f` of LOCKFILE.
**Verdict:** `[ "$HAS_RELEASE" -ge 1 ] && [ "$HAS_RM_LOCK" -ge 1 ]` → PASS / FAIL

### VF-01.3: ENH-1 — T-3 SKIP on Generate-Only

```bash
echo "=== VF-01.3: T-3 SKIP logic ===" | tee -a "$EVIDENCE"
grep -n "generate-only\|placeholder\|SKIP.*Generate" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>&1 | tee -a "$EVIDENCE"
T3_SKIP=$(grep -c "SKIP.*[Gg]enerate" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || T3_SKIP=0
echo "T-3 SKIP on generate-only: $T3_SKIP" | tee -a "$EVIDENCE"
```

**Expected:** At least 1 line writing SKIP to gates.md when generate-only placeholder detected.
**Verdict:** `[ "$T3_SKIP" -ge 1 ]` → PASS / FAIL

**FIX (if FAIL):** In `run_all_gates()`, add generate-only detection before T-3 execution: check FINAL_MASTER.md for "placeholder" or "generate-only" keywords, write SKIP to gates.md if found.

### VF-01.4: ENH-2 — T-6 Idempotency

```bash
echo "=== VF-01.4: T-6 idempotency ===" | tee -a "$EVIDENCE"
grep -n "CHANGES.*already\|idempoten\|SKIP.*CHANGES" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>&1 | tee -a "$EVIDENCE"
T6_IDEMP=$(grep -c "grep.*run_id.*CHANGES\|grep -q.*CHANGES" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || T6_IDEMP=0
echo "T-6 idempotency check: $T6_IDEMP" | tee -a "$EVIDENCE"
```

**Expected:** At least 1 grep check for existing run_id in CHANGES.md before writing.
**Verdict:** `[ "$T6_IDEMP" -ge 1 ]` → PASS / FAIL

**FIX (if FAIL):** In `gate_t6_memory_sync()`, before the CHANGES.md append: `if grep -q "$run_id" "$CHANGES_LOG" 2>/dev/null; then echo "SKIP: already recorded"; else <append>; fi`

### VF-01.5: ENH-9 — File Ownership Fix

```bash
echo "=== VF-01.5: ENH-9 chown ===" | tee -a "$EVIDENCE"
grep -n "chown.*zaks" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>&1 | tee -a "$EVIDENCE"
CHOWN_COUNT=$(grep -c "chown.*zaks:zaks" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || CHOWN_COUNT=0
echo "chown zaks:zaks calls: $CHOWN_COUNT" | tee -a "$EVIDENCE"
```

**Expected:** At least 2 chown calls (run_dir + templates_dir minimum).
**Verdict:** `[ "$CHOWN_COUNT" -ge 2 ]` → PASS / FAIL

### VF-01.6: ENH-9 — Root Safety Check

```bash
echo "=== VF-01.6: ENH-9 root check ===" | tee -a "$EVIDENCE"
grep -B2 "chown.*zaks" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh | head -10 2>&1 | tee -a "$EVIDENCE"
ROOT_CHECK=$(grep -c 'id -u.*-eq 0\|$(id -u).*0' /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || ROOT_CHECK=0
echo "Root user check before chown: $ROOT_CHECK" | tee -a "$EVIDENCE"
```

**Expected:** Chown block is guarded by a root user check (`id -u == 0`).
**Verdict:** `[ "$ROOT_CHECK" -ge 1 ]` → PASS / FAIL

### VF-01.7: ENH-8 — Gates Line in MEMORY.md

```bash
echo "=== VF-01.7: Gates in MEMORY.md ===" | tee -a "$EVIDENCE"
MEMORY_FILE="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
grep -n "T-1.*append\|T-2.*complete\|T-3.*structural\|T-4.*drift\|T-5.*no-drop\|T-6.*memory" "$MEMORY_FILE" 2>&1 | tee -a "$EVIDENCE"
GATES_LINE=$(grep -c "T-1.*T-2.*T-3\|T-1.*append.*T-2.*complete" "$MEMORY_FILE" 2>/dev/null) || GATES_LINE=0
# Alternative: check if at least T-1 and T-6 are on same line
GATES_SINGLE=$(grep -c "T-1.*T-6\|Gates:.*T-1" "$MEMORY_FILE" 2>/dev/null) || GATES_SINGLE=0
echo "Gates line (single line with T-1 through T-6): $GATES_SINGLE" | tee -a "$EVIDENCE"
```

**Expected:** At least 1 line listing all 6 gates (T-1 through T-6) in the TriPass section.
**Verdict:** `[ "$GATES_SINGLE" -ge 1 ]` → PASS / FAIL

### VF-01.8: ENH-3 — Lock File Path Consistent

```bash
echo "=== VF-01.8: Lock file path ===" | tee -a "$EVIDENCE"
LOCKPATH=$(grep -m1 'LOCKFILE=' /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null)
echo "Lock file declaration: $LOCKPATH" | tee -a "$EVIDENCE"
LOCK_REFS=$(grep -c 'LOCKFILE\|tripass\.lock' /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || LOCK_REFS=0
echo "Total LOCKFILE references: $LOCK_REFS" | tee -a "$EVIDENCE"
# Verify no hardcoded /tmp/tripass.lock outside the declaration
HARDCODED=$(grep -c '/tmp/tripass\.lock' /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || HARDCODED=0
echo "Hardcoded path references (should be 1 declaration only): $HARDCODED" | tee -a "$EVIDENCE"
```

**Expected:** Lock file path declared once as variable, used via `$LOCKFILE` everywhere else.
**Verdict:** `[ "$HARDCODED" -le 1 ] && [ "$LOCK_REFS" -ge 3 ]` → PASS / FAIL

---

## VF-02: Phantom Plugin Cleanup (Mission Gate V-2)

**Mission Requirement:** Zero occurrences of `/mnt/skills/` in any TriPass artifact, MEMORY.md, V6PP guide, or rule files.

### VF-02.1: SOP Clean

```bash
echo "=== VF-02.1: SOP phantom check ===" | tee -a "$EVIDENCE"
PHANTOM_SOP=$(grep -c "/mnt/skills/" /home/zaks/bookkeeping/docs/TRIPASS_SOP.md 2>/dev/null) || PHANTOM_SOP=0
echo "Phantom refs in SOP: $PHANTOM_SOP" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$PHANTOM_SOP" -eq 0 ]` → PASS / FAIL

**FIX (if FAIL):** Replace all `/mnt/skills/public/frontend-design/SKILL.md` references with `.claude/rules/design-system.md` in TRIPASS_SOP.md. Update "Prerequisites by Mode" section for design-mode.

### VF-02.2: Templates Clean

```bash
echo "=== VF-02.2: Templates phantom check ===" | tee -a "$EVIDENCE"
PHANTOM_TMPL=$(grep -rc "/mnt/skills/" /home/zaks/bookkeeping/docs/_tripass_templates/ 2>/dev/null | awk -F: '{s+=$2}END{print s+0}')
echo "Phantom refs in templates: $PHANTOM_TMPL" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$PHANTOM_TMPL" -eq 0 ]` → PASS / FAIL

### VF-02.3: Orchestrator Script Clean

```bash
echo "=== VF-02.3: tripass.sh phantom check ===" | tee -a "$EVIDENCE"
PHANTOM_SH=$(grep -c "/mnt/skills/" /home/zaks/zakops-agent-api/tools/tripass/tripass.sh 2>/dev/null) || PHANTOM_SH=0
echo "Phantom refs in tripass.sh: $PHANTOM_SH" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$PHANTOM_SH" -eq 0 ]` → PASS / FAIL

### VF-02.4: MEMORY.md Clean (Loaded Copy)

```bash
echo "=== VF-02.4: MEMORY.md phantom check ===" | tee -a "$EVIDENCE"
MEMORY_LOADED="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
PHANTOM_MEM=$(grep -c "/mnt/skills/" "$MEMORY_LOADED" 2>/dev/null) || PHANTOM_MEM=0
echo "Phantom refs in MEMORY.md (loaded): $PHANTOM_MEM" | tee -a "$EVIDENCE"
if [ "$PHANTOM_MEM" -gt 0 ]; then
  grep -n "/mnt/skills/" "$MEMORY_LOADED" 2>&1 | tee -a "$EVIDENCE"
fi
```

**Expected:** 0
**Verdict:** `[ "$PHANTOM_MEM" -eq 0 ]` → PASS / FAIL

**FIX (if FAIL):** In the TriPass section of MEMORY.md, replace the phantom plugin line with:
`- Design standards: .claude/rules/design-system.md (auto-loaded for dashboard component paths)`

### VF-02.5: V6PP Guide Clean

```bash
echo "=== VF-02.5: V6PP guide phantom check ===" | tee -a "$EVIDENCE"
PHANTOM_GUIDE=$(grep -c "/mnt/skills/" /home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md 2>/dev/null) || PHANTOM_GUIDE=0
echo "Phantom refs in V6PP guide: $PHANTOM_GUIDE" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$PHANTOM_GUIDE" -eq 0 ]` → PASS / FAIL

### VF-02.6: Rule Files Clean

```bash
echo "=== VF-02.6: Rules phantom check ===" | tee -a "$EVIDENCE"
PHANTOM_RULES=$(grep -rc "/mnt/skills/" /home/zaks/zakops-agent-api/.claude/rules/ 2>/dev/null | awk -F: '{s+=$2}END{print s+0}')
echo "Phantom refs in .claude/rules/: $PHANTOM_RULES" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$PHANTOM_RULES" -eq 0 ]` → PASS / FAIL

### VF-02.7: No "frontend-design plugin" Phrase

```bash
echo "=== VF-02.7: Plugin phrase check ===" | tee -a "$EVIDENCE"
PHRASE_COUNT=0
for f in /home/zaks/bookkeeping/docs/TRIPASS_SOP.md \
         /home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md \
         /home/zaks/zakops-agent-api/tools/tripass/tripass.sh \
         /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md; do
  C=$(grep -ci "frontend-design plugin" "$f" 2>/dev/null) || C=0
  if [ "$C" -gt 0 ]; then
    echo "FOUND in $f: $C" | tee -a "$EVIDENCE"
    PHRASE_COUNT=$((PHRASE_COUNT + C))
  fi
done
echo "Total 'frontend-design plugin' phrases: $PHRASE_COUNT" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$PHRASE_COUNT" -eq 0 ]` → PASS / FAIL

### VF-02.8: SOP Design-Mode References design-system.md

```bash
echo "=== VF-02.8: SOP design-mode references ===" | tee -a "$EVIDENCE"
grep -n "design-system\|design.system" /home/zaks/bookkeeping/docs/TRIPASS_SOP.md 2>&1 | tee -a "$EVIDENCE"
DS_REF=$(grep -c "design-system\.md\|\.claude/rules/design-system" /home/zaks/bookkeeping/docs/TRIPASS_SOP.md 2>/dev/null) || DS_REF=0
echo "design-system.md references in SOP: $DS_REF" | tee -a "$EVIDENCE"
```

**Expected:** At least 1 reference to `.claude/rules/design-system.md` in SOP.
**Verdict:** `[ "$DS_REF" -ge 1 ]` → PASS / FAIL

---

## VF-03: Surface 9 Artifacts (Mission Gate V-3)

**Mission Requirement:** Design system manifest, path-scoped rule, contract-surfaces entry, and validation mechanism all exist.

### VF-03.1: Manifest File Exists

```bash
echo "=== VF-03.1: Manifest existence ===" | tee -a "$EVIDENCE"
MANIFEST="/home/zaks/zakops-agent-api/apps/dashboard/src/types/design-system-manifest.ts"
ls -la "$MANIFEST" 2>&1 | tee -a "$EVIDENCE"
MANIFEST_EXISTS=$([ -f "$MANIFEST" ] && echo 1 || echo 0)
MANIFEST_LINES=$(wc -l < "$MANIFEST" 2>/dev/null || echo 0)
echo "Manifest exists: $MANIFEST_EXISTS, lines: $MANIFEST_LINES" | tee -a "$EVIDENCE"
```

**Expected:** File exists with >50 lines.
**Verdict:** `[ "$MANIFEST_EXISTS" -eq 1 ] && [ "$MANIFEST_LINES" -gt 50 ]` → PASS / FAIL

### VF-03.2: Manifest Declares All 7 Category A Conventions

```bash
echo "=== VF-03.2: Manifest conventions ===" | tee -a "$EVIDENCE"
MANIFEST="/home/zaks/zakops-agent-api/apps/dashboard/src/types/design-system-manifest.ts"
for KW in "allSettled\|data.fetching\|DATA_FETCHING" \
           "console.warn\|error.handling\|ERROR_HANDLING" \
           "caret-color\|css\|CSS_ARCHITECTURE" \
           "server.side\|aggregation\|DATA_AGGREGATION" \
           "PIPELINE_STAGES\|stage.definition\|STAGE_DEFINITIONS" \
           "middleware\|api.communication\|API_COMMUNICATION" \
           "bridge\|import.discipline\|IMPORT_DISCIPLINE"; do
  C=$(grep -ci "$KW" "$MANIFEST" 2>/dev/null) || C=0
  echo "Convention '$KW': $C matches" | tee -a "$EVIDENCE"
done
CONVENTION_EXPORTS=$(grep -c "export\|CONVENTIONS" "$MANIFEST" 2>/dev/null) || CONVENTION_EXPORTS=0
echo "Export/convention declarations: $CONVENTION_EXPORTS" | tee -a "$EVIDENCE"
```

**Expected:** All 7 conventions referenced, multiple exports.
**Verdict:** All convention checks > 0 → PASS / FAIL

### VF-03.3: design-system.md Rule Exists with YAML Frontmatter

```bash
echo "=== VF-03.3: design-system.md ===" | tee -a "$EVIDENCE"
DS_RULE="/home/zaks/zakops-agent-api/.claude/rules/design-system.md"
ls -la "$DS_RULE" 2>&1 | tee -a "$EVIDENCE"
head -6 "$DS_RULE" 2>&1 | tee -a "$EVIDENCE"
HAS_YAML=$(head -1 "$DS_RULE" 2>/dev/null | grep -c "^---$") || HAS_YAML=0
DS_LINES=$(wc -l < "$DS_RULE" 2>/dev/null || echo 0)
echo "YAML frontmatter: $HAS_YAML, lines: $DS_LINES" | tee -a "$EVIDENCE"
```

**Expected:** Starts with `---`, has >50 lines.
**Verdict:** `[ "$HAS_YAML" -eq 1 ] && [ "$DS_LINES" -gt 50 ]` → PASS / FAIL

### VF-03.4: Rule Triggers on Correct Paths

```bash
echo "=== VF-03.4: Trigger paths ===" | tee -a "$EVIDENCE"
DS_RULE="/home/zaks/zakops-agent-api/.claude/rules/design-system.md"
grep "components\|app/\|styles" "$DS_RULE" | head -5 2>&1 | tee -a "$EVIDENCE"
HAS_COMPONENTS=$(grep -c "components/\*\*\|components" "$DS_RULE" 2>/dev/null) || HAS_COMPONENTS=0
HAS_APP=$(grep -c "app/\*\*\|/app/" "$DS_RULE" 2>/dev/null) || HAS_APP=0
HAS_STYLES=$(grep -c "styles/\*\*\|/styles/" "$DS_RULE" 2>/dev/null) || HAS_STYLES=0
echo "Triggers — components: $HAS_COMPONENTS, app: $HAS_APP, styles: $HAS_STYLES" | tee -a "$EVIDENCE"
```

**Expected:** All three paths present.
**Verdict:** `[ "$HAS_COMPONENTS" -ge 1 ] && [ "$HAS_APP" -ge 1 ] && [ "$HAS_STYLES" -ge 1 ]` → PASS / FAIL

### VF-03.5: Category A — All 7 Architectural Conventions

```bash
echo "=== VF-03.5: Category A conventions ===" | tee -a "$EVIDENCE"
DS_RULE="/home/zaks/zakops-agent-api/.claude/rules/design-system.md"
CAT_A=0
for PATTERN in "Promise.allSettled\|allSettled" \
               "console\.warn\|console\.error" \
               "caret-color\|@layer base" \
               "server-side\|server.side\|\.length" \
               "PIPELINE_STAGES\|execution-contracts" \
               "middleware\|JSON 502\|/api/" \
               "bridge\|import discipline\|generated.*direct"; do
  C=$(grep -ci "$PATTERN" "$DS_RULE" 2>/dev/null) || C=0
  echo "Cat A '$PATTERN': $C" | tee -a "$EVIDENCE"
  [ "$C" -gt 0 ] && CAT_A=$((CAT_A + 1))
done
echo "Category A conventions found: $CAT_A / 7" | tee -a "$EVIDENCE"
```

**Expected:** 7 / 7
**Verdict:** `[ "$CAT_A" -eq 7 ]` → PASS / FAIL

### VF-03.6: Category B — Design Quality Standards

```bash
echo "=== VF-03.6: Category B standards ===" | tee -a "$EVIDENCE"
DS_RULE="/home/zaks/zakops-agent-api/.claude/rules/design-system.md"
CAT_B=0
for PATTERN in "Typography\|typography\|font" \
               "Color\|color\|palette" \
               "Motion\|animation\|micro-interaction" \
               "Spatial\|composition\|layout\|asymmetry" \
               "Anti-[Pp]attern\|anti.pattern\|cookie-cutter"; do
  C=$(grep -ci "$PATTERN" "$DS_RULE" 2>/dev/null) || C=0
  echo "Cat B '$PATTERN': $C" | tee -a "$EVIDENCE"
  [ "$C" -gt 0 ] && CAT_B=$((CAT_B + 1))
done
echo "Category B areas found: $CAT_B / 5" | tee -a "$EVIDENCE"
```

**Expected:** 5 / 5
**Verdict:** `[ "$CAT_B" -eq 5 ]` → PASS / FAIL

### VF-03.7: contract-surfaces.md Has Surface 9

```bash
echo "=== VF-03.7: Surface 9 in contract-surfaces.md ===" | tee -a "$EVIDENCE"
CS_FILE="/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md"
grep -n "Surface 9\|surface 9" "$CS_FILE" 2>&1 | tee -a "$EVIDENCE"
S9_ENTRY=$(grep -c "Surface 9" "$CS_FILE" 2>/dev/null) || S9_ENTRY=0
S9_BOUNDARY=$(grep -c "Design.*Dashboard\|design.*manifest\|validate-surface9" "$CS_FILE" 2>/dev/null) || S9_BOUNDARY=0
echo "Surface 9 entry: $S9_ENTRY, boundary/validation refs: $S9_BOUNDARY" | tee -a "$EVIDENCE"
```

**Expected:** Surface 9 entry present with boundary definition and validation reference.
**Verdict:** `[ "$S9_ENTRY" -ge 1 ] && [ "$S9_BOUNDARY" -ge 1 ]` → PASS / FAIL

### VF-03.8: Validation Script Exists and Is Executable

```bash
echo "=== VF-03.8: validate-surface9.sh ===" | tee -a "$EVIDENCE"
VAL_SCRIPT="/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh"
ls -la "$VAL_SCRIPT" 2>&1 | tee -a "$EVIDENCE"
EXEC=$([ -x "$VAL_SCRIPT" ] && echo 1 || echo 0)
echo "Executable: $EXEC" | tee -a "$EVIDENCE"
```

**Expected:** File exists and is executable.
**Verdict:** `[ "$EXEC" -eq 1 ]` → PASS / FAIL

### VF-03.9: Validation Checks Critical Conventions

```bash
echo "=== VF-03.9: Validation coverage ===" | tee -a "$EVIDENCE"
VAL_SCRIPT="/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh"
CHECKS=0
for KW in "import\|generated" "PIPELINE_STAGES\|stage" "allSettled\|Promise"; do
  C=$(grep -ci "$KW" "$VAL_SCRIPT" 2>/dev/null) || C=0
  echo "Validation check '$KW': $C" | tee -a "$EVIDENCE"
  [ "$C" -gt 0 ] && CHECKS=$((CHECKS + 1))
done
echo "Critical validation checks: $CHECKS / 3" | tee -a "$EVIDENCE"
```

**Expected:** 3 / 3 (imports, stages, Promise.allSettled)
**Verdict:** `[ "$CHECKS" -eq 3 ]` → PASS / FAIL

---

## VF-04: Guide Completeness (Mission Gate V-4)

**Mission Requirement:** All 9 Parts, all 5 Appendices, "What Changed" section, Document Information, no TBD placeholders.

### VF-04.1: All 9 Parts Present

```bash
echo "=== VF-04.1: Parts check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
for P in "Part 1" "Part 2" "Part 3" "Part 4" "Part 5" "Part 6" "Part 7" "Part 8" "Part 9"; do
  LINE=$(grep -n "## $P" "$GUIDE" 2>/dev/null | head -1)
  echo "$P: $LINE" | tee -a "$EVIDENCE"
done
PART_COUNT=$(grep -c "^## Part [0-9]" "$GUIDE" 2>/dev/null) || PART_COUNT=0
echo "Total Parts: $PART_COUNT" | tee -a "$EVIDENCE"
```

**Expected:** 9 parts
**Verdict:** `[ "$PART_COUNT" -eq 9 ]` → PASS / FAIL

### VF-04.2: All 5 Appendices Present

```bash
echo "=== VF-04.2: Appendices check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
for A in "Appendix A" "Appendix B" "Appendix C" "Appendix D" "Appendix E"; do
  LINE=$(grep -n "## $A" "$GUIDE" 2>/dev/null | head -1)
  echo "$A: $LINE" | tee -a "$EVIDENCE"
done
APP_COUNT=$(grep -c "^## Appendix [A-E]" "$GUIDE" 2>/dev/null) || APP_COUNT=0
echo "Total Appendices: $APP_COUNT" | tee -a "$EVIDENCE"
```

**Expected:** 5 appendices
**Verdict:** `[ "$APP_COUNT" -eq 5 ]` → PASS / FAIL

### VF-04.3: "What Changed Since V5PP-DMS" Section

```bash
echo "=== VF-04.3: What Changed section ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
CHANGED=$(grep -c "What Changed Since V5PP" "$GUIDE" 2>/dev/null) || CHANGED=0
CHANGED_LINE=$(grep -n "What Changed" "$GUIDE" | head -1)
echo "What Changed section: $CHANGED (at $CHANGED_LINE)" | tee -a "$EVIDENCE"
```

**Expected:** 1 section present
**Verdict:** `[ "$CHANGED" -ge 1 ]` → PASS / FAIL

### VF-04.4: No TBD or Placeholder Text

```bash
echo "=== VF-04.4: No placeholders ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
TBD=$(grep -ci "TBD\|TODO\|PLACEHOLDER\|FIXME\|coming soon" "$GUIDE" 2>/dev/null) || TBD=0
echo "Placeholder text count: $TBD" | tee -a "$EVIDENCE"
if [ "$TBD" -gt 0 ]; then
  grep -in "TBD\|TODO\|PLACEHOLDER\|FIXME\|coming soon" "$GUIDE" 2>&1 | tee -a "$EVIDENCE"
fi
```

**Expected:** 0
**Verdict:** `[ "$TBD" -eq 0 ]` → PASS / FAIL

### VF-04.5: Document Information Section

```bash
echo "=== VF-04.5: Document Information ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
DOC_INFO=$(grep -c "Document Information" "$GUIDE" 2>/dev/null) || DOC_INFO=0
grep -A8 "Document Information" "$GUIDE" 2>&1 | tee -a "$EVIDENCE"
HAS_VERSION=$(grep -c "Version\|V6PP" "$GUIDE" | head -1)
HAS_SUPERSEDES=$(grep -c "Supersedes\|V5PP" "$GUIDE" | head -1)
echo "Doc Info: $DOC_INFO, Version: $HAS_VERSION, Supersedes: $HAS_SUPERSEDES" | tee -a "$EVIDENCE"
```

**Expected:** Document Information section with version, date, and supersedes fields.
**Verdict:** `[ "$DOC_INFO" -ge 1 ]` → PASS / FAIL

### VF-04.6: Each Part Has Substantive Content

```bash
echo "=== VF-04.6: Part content depth ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
TOTAL_LINES=$(wc -l < "$GUIDE")
PART_LINES=$(grep -n "^## Part\|^## Appendix\|^## Document\|^## What Changed" "$GUIDE" | awk -F: '{print $1}')
echo "Section start lines: $PART_LINES" | tee -a "$EVIDENCE"
echo "Guide total: $TOTAL_LINES lines" | tee -a "$EVIDENCE"
# Each part should have >10 lines — check by confirming total covers 9 parts + 5 appendices + extras in 1000+ lines
GUIDE_TOTAL=$(wc -l < "$GUIDE" 2>/dev/null || echo 0)
echo "Guide line count: $GUIDE_TOTAL" | tee -a "$EVIDENCE"
```

**Expected:** Total >1000 lines (ensures parts have substance).
**Verdict:** `[ "$GUIDE_TOTAL" -gt 1000 ]` → PASS / FAIL

### VF-04.7: Line Count Within Target Range

```bash
echo "=== VF-04.7: Line count range ===" | tee -a "$EVIDENCE"
GUIDE_LINES=$(wc -l < /home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md 2>/dev/null || echo 0)
echo "V6PP guide lines: $GUIDE_LINES (target: 1000-1500)" | tee -a "$EVIDENCE"
```

**Expected:** Between 1000 and 1500 lines.
**Verdict:** `[ "$GUIDE_LINES" -ge 1000 ] && [ "$GUIDE_LINES" -le 1500 ]` → PASS / FAIL

---

## VF-05: Guide Accuracy — Critical Facts (Mission Gate V-5)

**Mission Requirement:** Every factual claim in the guide matches the live filesystem.

### VF-05.1: PostgreSQL Port Accuracy

```bash
echo "=== VF-05.1: PostgreSQL port ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
grep -n "5432\|5435" "$GUIDE" 2>&1 | tee -a "$EVIDENCE"
PORT_5432=$(grep -c "5432" "$GUIDE" 2>/dev/null) || PORT_5432=0
PORT_5435_VALID=$(grep "5435" "$GUIDE" 2>/dev/null | grep -cv "does not exist\|DECOMMISSIONED\|never\|not valid" 2>/dev/null) || PORT_5435_VALID=0
echo "Port 5432 refs: $PORT_5432, Port 5435 presented as valid: $PORT_5435_VALID" | tee -a "$EVIDENCE"
```

**Expected:** Port 5432 referenced, port 5435 NOT presented as valid.
**Verdict:** `[ "$PORT_5432" -ge 1 ] && [ "$PORT_5435_VALID" -eq 0 ]` → PASS / FAIL

### VF-05.2: Deny Rule Count

```bash
echo "=== VF-05.2: Deny rule count ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_DENY=$(grep -o "Deny Rules ([0-9]*)" "$GUIDE" 2>/dev/null | grep -o "[0-9]*")
LIVE_DENY=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(len(d.get('permissions',{}).get('deny',[])))")
echo "Guide says: $GUIDE_DENY, Live: $LIVE_DENY" | tee -a "$EVIDENCE"
```

**Expected:** Guide count matches live count (12).
**Verdict:** `[ "$GUIDE_DENY" = "$LIVE_DENY" ]` → PASS / FAIL

### VF-05.3: All 12 Deny Rules Listed

```bash
echo "=== VF-05.3: Deny rules complete list ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
DENY_PATTERNS=("api-types.generated.ts" "agent-api-types.generated.ts" "backend_models.py" "rag_models.py" ".env)" ".env.*)")
FOUND=0
for P in "${DENY_PATTERNS[@]}"; do
  C=$(grep -c "$P" "$GUIDE" 2>/dev/null) || C=0
  echo "Pattern '$P': $C occurrences" | tee -a "$EVIDENCE"
  [ "$C" -gt 0 ] && FOUND=$((FOUND + 1))
done
echo "Deny patterns found in guide: $FOUND / 6 (each has Edit+Write = 12 total)" | tee -a "$EVIDENCE"
```

**Expected:** All 6 patterns found (each appears twice for Edit+Write = 12 total rules).
**Verdict:** `[ "$FOUND" -eq 6 ]` → PASS / FAIL

### VF-05.4: Allow Rule Count Accuracy

```bash
echo "=== VF-05.4: Allow rule count ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_ALLOW=$(grep -o "Allow Rules ([0-9]*)" "$GUIDE" 2>/dev/null | grep -o "[0-9]*")
LIVE_ALLOW=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(len(d.get('permissions',{}).get('allow',[])))")
echo "Guide says: $GUIDE_ALLOW, Live: $LIVE_ALLOW" | tee -a "$EVIDENCE"
```

**Expected:** Guide count should accurately reflect live allow rule count (144), or if summarized, must clearly state it shows key patterns and note the actual total.
**Verdict:** Guide count matches live OR guide explicitly notes "X key patterns shown, Y total" → PASS / FAIL

**FIX (if FAIL):** Update the Allow Rules section heading to `**Allow Rules (144 total, key patterns shown):**` and add a note: "The full allow list contains 144 rules. The 4 patterns below cover the most commonly used make-related permissions."

### VF-05.5: Slash Command Count

```bash
echo "=== VF-05.5: Command count ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_CMD=$(grep -o "Total: [0-9]* commands" "$GUIDE" 2>/dev/null | grep -o "[0-9]*")
LIVE_CMD=$(ls /home/zaks/zakops-agent-api/.claude/commands/*.md 2>/dev/null | wc -l)
echo "Guide says: $GUIDE_CMD, Live: $LIVE_CMD" | tee -a "$EVIDENCE"
```

**Expected:** Match (expected: 13).
**Verdict:** `[ "$GUIDE_CMD" = "$LIVE_CMD" ]` → PASS / FAIL

### VF-05.6: Hook Script Count

```bash
echo "=== VF-05.6: Hook count ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_HOOKS=$(grep -o "Total: [0-9]* hooks" "$GUIDE" 2>/dev/null | grep -o "[0-9]*")
LIVE_HOOKS=$(ls /home/zaks/.claude/hooks/*.sh 2>/dev/null | wc -l)
echo "Guide says: $GUIDE_HOOKS, Live: $LIVE_HOOKS" | tee -a "$EVIDENCE"
```

**Expected:** Match (expected: 5).
**Verdict:** `[ "$GUIDE_HOOKS" = "$LIVE_HOOKS" ]` → PASS / FAIL

### VF-05.7: MCP Server Accuracy

```bash
echo "=== VF-05.7: MCP servers ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
LIVE_MCP=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(sorted(d.get('mcpServers',{}).keys()))")
echo "Live MCP servers: $LIVE_MCP" | tee -a "$EVIDENCE"
# Check guide mentions the correct servers
for SERVER in "gmail" "crawl4ai-rag"; do
  C=$(grep -c "$SERVER" "$GUIDE" 2>/dev/null) || C=0
  echo "Guide mentions '$SERVER': $C" | tee -a "$EVIDENCE"
done
# Check for wrong servers
for WRONG in "github.*mcp\|modelcontextprotocol" "playwright.*mcp"; do
  W=$(grep -c "$WRONG" "$GUIDE" 2>/dev/null) || W=0
  echo "Guide mentions wrong server pattern '$WRONG': $W" | tee -a "$EVIDENCE"
done
```

**Expected:** Guide lists `gmail` and `crawl4ai-rag`. Does NOT list `github` or `playwright` as active MCP servers.
**Verdict:** Both correct servers present AND no wrong servers → PASS / FAIL

**FIX (if FAIL):** Replace the MCP Servers section in the guide:
```
**MCP Servers:**
- `gmail` — `@gongrzhe/server-gmail-autoauth-mcp` (enabled)
- `crawl4ai-rag` — Docker-based RAG crawler service (enabled)
```

### VF-05.8: Contract Surface Count

```bash
echo "=== VF-05.8: Surface count ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
SURFACE_COUNT=$(grep -c "^### Surface [0-9]" "$GUIDE" 2>/dev/null) || SURFACE_COUNT=0
echo "Surfaces in guide: $SURFACE_COUNT" | tee -a "$EVIDENCE"
S9=$(grep -c "Surface 9" "$GUIDE" 2>/dev/null) || S9=0
echo "Surface 9 mentions: $S9" | tee -a "$EVIDENCE"
```

**Expected:** 9 surfaces, Surface 9 mentioned.
**Verdict:** `[ "$SURFACE_COUNT" -eq 9 ] && [ "$S9" -ge 1 ]` → PASS / FAIL

### VF-05.9: TriPass QA Enhancements Documented

```bash
echo "=== VF-05.9: TriPass enhancements in guide ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
ENH_FOUND=0
for ENH in "ENH-1\|T-3.*SKIP\|SKIP.*generate" \
           "ENH-2\|T-6.*[Ii]dempoten\|idempoten" \
           "ENH-3\|trap.*handler\|trap.*release" \
           "ENH-8\|gates.*MEMORY\|MEMORY.*gates" \
           "ENH-9\|chown.*zaks\|ownership.*WSL\|file ownership"; do
  C=$(grep -ci "$ENH" "$GUIDE" 2>/dev/null) || C=0
  echo "Enhancement '$ENH': $C" | tee -a "$EVIDENCE"
  [ "$C" -gt 0 ] && ENH_FOUND=$((ENH_FOUND + 1))
done
echo "Enhancements documented: $ENH_FOUND / 5" | tee -a "$EVIDENCE"
```

**Expected:** 5 / 5
**Verdict:** `[ "$ENH_FOUND" -eq 5 ]` → PASS / FAIL

### VF-05.10: Port 8090 Decommissioned

```bash
echo "=== VF-05.10: Port 8090 ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
grep -in "8090" "$GUIDE" 2>&1 | tee -a "$EVIDENCE"
DECOM=$(grep "8090" "$GUIDE" 2>/dev/null | grep -ci "decommission\|never\|forbidden" 2>/dev/null) || DECOM=0
echo "8090 marked decommissioned: $DECOM" | tee -a "$EVIDENCE"
```

**Expected:** 8090 only appears with decommissioned/never-use context.
**Verdict:** `[ "$DECOM" -ge 1 ]` → PASS / FAIL

### VF-05.11: Agent Definitions Path

```bash
echo "=== VF-05.11: Agent definitions path ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
grep -n "agents/" "$GUIDE" | head -5 2>&1 | tee -a "$EVIDENCE"
# Actual location
ACTUAL_AGENTS="/home/zaks/.claude/agents/"
ls "$ACTUAL_AGENTS" 2>&1 | tee -a "$EVIDENCE"
GUIDE_PATH=$(grep -o '`[^`]*agents/[^`]*`' "$GUIDE" | head -1)
echo "Guide says: $GUIDE_PATH, Actual: $ACTUAL_AGENTS" | tee -a "$EVIDENCE"
```

**Expected:** Guide's agent path resolves to actual location (`/home/zaks/.claude/agents/`). Note: `~/.claude/agents/` is ambiguous when Claude runs as root (`~` → `/root/`).
**Verdict:** Guide path matches actual OR uses explicit `/home/zaks/.claude/agents/` → PASS / FAIL

### VF-05.12: No Stale "8 Contract Surfaces" Reference

```bash
echo "=== VF-05.12: Stale 8-surface references ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
STALE_8=$(grep -c "all 8 contract\|8 contract surface\|8 surfaces" "$GUIDE" 2>/dev/null) || STALE_8=0
echo "Stale '8 surfaces' references: $STALE_8" | tee -a "$EVIDENCE"
if [ "$STALE_8" -gt 0 ]; then
  grep -n "8 contract\|8 surface" "$GUIDE" 2>&1 | tee -a "$EVIDENCE"
fi
```

**Expected:** 0 stale references to 8 surfaces (should be 9 everywhere).
**Verdict:** `[ "$STALE_8" -eq 0 ]` → PASS / FAIL

---

## VF-06: Guide Accuracy — Metrics (Mission Gate V-6)

**Mission Requirement:** All numeric claims in the guide match live `wc -l` / `ls` / JSON counts.

### VF-06.1: CLAUDE.md Monorepo Line Count

```bash
echo "=== VF-06.1: CLAUDE.md monorepo ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
LIVE_LINES=$(wc -l < /home/zaks/zakops-agent-api/CLAUDE.md 2>/dev/null || echo 0)
GUIDE_CLAIM=$(grep -o "zakops-agent-api/CLAUDE.md.*([0-9]* lines\|CLAUDE.md.*| [0-9]*" "$GUIDE" | grep -o "[0-9]*" | head -1)
echo "Live: $LIVE_LINES, Guide claims: $GUIDE_CLAIM" | tee -a "$EVIDENCE"
```

**Expected:** Match (expected: 143).
**Verdict:** `[ "$GUIDE_CLAIM" = "$LIVE_LINES" ]` → PASS / FAIL

### VF-06.2: CLAUDE.md Root Line Count

```bash
echo "=== VF-06.2: CLAUDE.md root ===" | tee -a "$EVIDENCE"
LIVE_ROOT=$(wc -l < /home/zaks/CLAUDE.md 2>/dev/null || echo 0)
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_ROOT=$(grep "/home/zaks/CLAUDE.md" "$GUIDE" | grep -o "[0-9]*" | head -1)
echo "Live: $LIVE_ROOT, Guide claims: $GUIDE_ROOT" | tee -a "$EVIDENCE"
```

**Expected:** Match (expected: 64).
**Verdict:** `[ "$GUIDE_ROOT" = "$LIVE_ROOT" ]` → PASS / FAIL

### VF-06.3: Hook Script Count Match

```bash
echo "=== VF-06.3: Hook count ===" | tee -a "$EVIDENCE"
LIVE=$(ls /home/zaks/.claude/hooks/*.sh 2>/dev/null | wc -l)
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_VAL=$(grep -o "Total: [0-9]* hooks" "$GUIDE" | grep -o "[0-9]*")
echo "Live: $LIVE, Guide: $GUIDE_VAL" | tee -a "$EVIDENCE"
```

**Expected:** 5 = 5
**Verdict:** `[ "$LIVE" = "$GUIDE_VAL" ]` → PASS / FAIL

### VF-06.4: Rule File Count Match

```bash
echo "=== VF-06.4: Rule count ===" | tee -a "$EVIDENCE"
LIVE=$(ls /home/zaks/zakops-agent-api/.claude/rules/*.md 2>/dev/null | wc -l)
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_VAL=$(grep -o "[0-9]* rules\|rules ([0-9]*\|5 rules\|5 files" "$GUIDE" | grep -o "[0-9]*" | head -1)
echo "Live: $LIVE, Guide: $GUIDE_VAL" | tee -a "$EVIDENCE"
```

**Expected:** 5 = 5
**Verdict:** `[ "$LIVE" = "$GUIDE_VAL" ]` → PASS / FAIL

### VF-06.5: Command File Count Match

```bash
echo "=== VF-06.5: Command count ===" | tee -a "$EVIDENCE"
LIVE=$(ls /home/zaks/zakops-agent-api/.claude/commands/*.md 2>/dev/null | wc -l)
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_VAL=$(grep -o "Total: [0-9]* commands" "$GUIDE" | grep -o "[0-9]*")
echo "Live: $LIVE, Guide: $GUIDE_VAL" | tee -a "$EVIDENCE"
```

**Expected:** 13 = 13
**Verdict:** `[ "$LIVE" = "$GUIDE_VAL" ]` → PASS / FAIL

### VF-06.6: Deny Rule Count Match

```bash
echo "=== VF-06.6: Deny count ===" | tee -a "$EVIDENCE"
LIVE=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(len(d.get('permissions',{}).get('deny',[])))")
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_VAL=$(grep -o "Deny Rules ([0-9]*)" "$GUIDE" | grep -o "[0-9]*")
echo "Live: $LIVE, Guide: $GUIDE_VAL" | tee -a "$EVIDENCE"
```

**Expected:** 12 = 12
**Verdict:** `[ "$LIVE" = "$GUIDE_VAL" ]` → PASS / FAIL

### VF-06.7: Allow Rule Count Accuracy

```bash
echo "=== VF-06.7: Allow count ===" | tee -a "$EVIDENCE"
LIVE=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(len(d.get('permissions',{}).get('allow',[])))")
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_VAL=$(grep -o "Allow Rules ([0-9]*)" "$GUIDE" | grep -o "[0-9]*")
echo "Live: $LIVE, Guide: $GUIDE_VAL" | tee -a "$EVIDENCE"
```

**Expected:** Guide must accurately reflect the live count (144), not a subset count.
**Verdict:** Guide value = live value OR guide explicitly notes it's a summary → PASS / FAIL

**FIX (if FAIL):** Change `**Allow Rules (4):**` to `**Allow Rules (144 total — key patterns below):**` and add a footnote: "Full list includes WebSearch, WebFetch, Bash patterns for docker/npm/pip/curl/make, and MCP tool permissions."

### VF-06.8: MEMORY.md Line Count Plausible

```bash
echo "=== VF-06.8: MEMORY.md line count ===" | tee -a "$EVIDENCE"
LIVE=$(wc -l < /root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md 2>/dev/null || echo 0)
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_VAL=$(grep -o "MEMORY.md.*([0-9]* lines\|memory.*[0-9]* lines" "$GUIDE" | grep -o "[0-9]*" | head -1)
echo "Live: $LIVE, Guide: $GUIDE_VAL" | tee -a "$EVIDENCE"
```

**Expected:** Within 10 lines of live value (MEMORY.md may change between sessions).
**Verdict:** Difference < 10 → PASS / FAIL

---

## VF-07: No Duplication (Mission Gate V-7)

### VF-07.1: Total Line Count in Range

```bash
echo "=== VF-07.1: Line count range ===" | tee -a "$EVIDENCE"
LINES=$(wc -l < /home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md)
echo "Total lines: $LINES (target: 1000-1500)" | tee -a "$EVIDENCE"
```

**Expected:** 1000 ≤ lines ≤ 1500
**Verdict:** `[ "$LINES" -ge 1000 ] && [ "$LINES" -le 1500 ]` → PASS / FAIL

### VF-07.2: No Consecutive Duplicate Paragraphs

```bash
echo "=== VF-07.2: Duplicate paragraphs ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
# Check for consecutive identical non-empty lines (paragraph starts)
DUPES=$(awk 'NF && prev==$0 {print NR": "$0} {prev=$0}' "$GUIDE" | grep -v "^$\|---\|^\|" | head -5)
DUPE_COUNT=$(echo "$DUPES" | grep -c "." 2>/dev/null) || DUPE_COUNT=0
echo "Consecutive duplicate lines: $DUPE_COUNT" | tee -a "$EVIDENCE"
if [ "$DUPE_COUNT" -gt 0 ]; then echo "$DUPES" | tee -a "$EVIDENCE"; fi
```

**Expected:** 0 (or only expected duplicates like table separators).
**Verdict:** `[ "$DUPE_COUNT" -le 2 ]` → PASS / FAIL

### VF-07.3: Service Map Table Appears Once

```bash
echo "=== VF-07.3: Service map uniqueness ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
SVC_MAP=$(grep -c "Dashboard.*3003\|Agent API.*8095\|Backend API.*8091" "$GUIDE" 2>/dev/null) || SVC_MAP=0
echo "Service map row appearances: $SVC_MAP (expect 1 each)" | tee -a "$EVIDENCE"
```

**Expected:** Each service appears exactly once in a service table.
**Verdict:** `[ "$SVC_MAP" -le 3 ]` → PASS / FAIL

### VF-07.4: Deny Rules Table Appears Once

```bash
echo "=== VF-07.4: Deny rules table uniqueness ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
DENY_HEADERS=$(grep -c "Deny Rules Detail\|Deny Rules (" "$GUIDE" 2>/dev/null) || DENY_HEADERS=0
echo "Deny rules section headers: $DENY_HEADERS" | tee -a "$EVIDENCE"
```

**Expected:** ≤ 2 (one summary mention + one detail table).
**Verdict:** `[ "$DENY_HEADERS" -le 2 ]` → PASS / FAIL

---

## VF-08: Cross-Document Consistency (Mission Gate V-8)

### VF-08.1: Guide Service Map vs CLAUDE.md

```bash
echo "=== VF-08.1: Service map cross-check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
ROOT_CMD="/home/zaks/CLAUDE.md"
# Check key port/service pairs exist in both
for PAIR in "3003" "8091" "8095" "8052" "5432"; do
  G=$(grep -c "$PAIR" "$GUIDE" 2>/dev/null) || G=0
  R=$(grep -c "$PAIR" "$ROOT_CMD" 2>/dev/null) || R=0
  echo "Port $PAIR — Guide: $G, CLAUDE.md: $R" | tee -a "$EVIDENCE"
done
```

**Expected:** Key ports present in both documents.
**Verdict:** All ports present in guide → PASS / FAIL

### VF-08.2: Guide Surfaces vs contract-surfaces.md

```bash
echo "=== VF-08.2: Surface cross-check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
CS="/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md"
GUIDE_SURFACES=$(grep -c "^### Surface [0-9]" "$GUIDE" 2>/dev/null) || GUIDE_SURFACES=0
CS_SURFACES=$(grep -c "Surface [0-9]" "$CS" 2>/dev/null) || CS_SURFACES=0
echo "Guide surfaces: $GUIDE_SURFACES, contract-surfaces.md mentions: $CS_SURFACES" | tee -a "$EVIDENCE"
```

**Expected:** Both show 9 surfaces.
**Verdict:** `[ "$GUIDE_SURFACES" -ge 9 ]` → PASS / FAIL

### VF-08.3: Guide Commands vs Directory

```bash
echo "=== VF-08.3: Command cross-check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
CMD_DIR="/home/zaks/zakops-agent-api/.claude/commands/"
LIVE_CMDS=$(ls "$CMD_DIR"*.md 2>/dev/null | xargs -I{} basename {} .md | sort)
echo "Live commands:" | tee -a "$EVIDENCE"
echo "$LIVE_CMDS" | tee -a "$EVIDENCE"
MISSING=0
for CMD in $LIVE_CMDS; do
  C=$(grep -c "/$CMD\b\|$CMD" "$GUIDE" 2>/dev/null) || C=0
  if [ "$C" -eq 0 ]; then
    echo "MISSING from guide: $CMD" | tee -a "$EVIDENCE"
    MISSING=$((MISSING + 1))
  fi
done
echo "Commands missing from guide: $MISSING" | tee -a "$EVIDENCE"
```

**Expected:** 0 missing.
**Verdict:** `[ "$MISSING" -eq 0 ]` → PASS / FAIL

### VF-08.4: Guide Hooks vs Settings Hook Registrations

```bash
echo "=== VF-08.4: Hook cross-check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
# Live hooks from project settings
LIVE_HOOKS=$(python3 -c "
import json
with open('/home/zaks/.claude/settings.json') as f:
    d = json.load(f)
hooks = d.get('hooks', {})
scripts = set()
for event, handlers in hooks.items():
    for h in handlers:
        for hook in h.get('hooks', []):
            cmd = hook.get('command', '')
            if cmd:
                scripts.add(cmd.split('/')[-1])
print(sorted(scripts))
")
echo "Live hook scripts: $LIVE_HOOKS" | tee -a "$EVIDENCE"
# Check guide mentions each
for HOOK in "pre-edit.sh" "pre-bash.sh" "post-edit.sh" "stop.sh" "memory-sync.sh"; do
  C=$(grep -c "$HOOK" "$GUIDE" 2>/dev/null) || C=0
  echo "Guide mentions $HOOK: $C" | tee -a "$EVIDENCE"
done
```

**Expected:** All 5 hooks (pre-edit, pre-bash, post-edit, stop, memory-sync) mentioned in guide.
**Verdict:** All 5 present → PASS / FAIL

### VF-08.5: Guide MEMORY.md Path vs Loaded Path

```bash
echo "=== VF-08.5: MEMORY.md path cross-check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_PATH=$(grep -o '/root/.claude/projects/[^ ]*MEMORY.md' "$GUIDE" | head -1)
LOADED_PATH="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
echo "Guide path: $GUIDE_PATH" | tee -a "$EVIDENCE"
echo "Loaded path: $LOADED_PATH" | tee -a "$EVIDENCE"
MATCH=$([ "$GUIDE_PATH" = "$LOADED_PATH" ] && echo "YES" || echo "NO")
echo "Match: $MATCH" | tee -a "$EVIDENCE"
```

**Expected:** Guide path matches the actually loaded MEMORY.md path (`-mnt-c-Users-mzsai`, not `-home-zaks`).
**Verdict:** `[ "$MATCH" = "YES" ]` → PASS / FAIL

**FIX (if FAIL):** The guide claims `/root/.claude/projects/-home-zaks/memory/MEMORY.md` is the authoritative path, but Claude Code actually loads from `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md`. Update all MEMORY.md path references in the guide to the correct loaded path, or document both copies and clarify which is loaded for which working directory.

### VF-08.6: Guide TriPass vs TRIPASS_SOP.md

```bash
echo "=== VF-08.6: TriPass cross-check ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
SOP="/home/zaks/bookkeeping/docs/TRIPASS_SOP.md"
# Both should document 4 passes, 3 modes, 6 gates
for KW in "forensic\|design\|implement" "T-1\|T-2\|T-3\|T-4\|T-5\|T-6" "autonomous\|generate-only"; do
  G=$(grep -ci "$KW" "$GUIDE" 2>/dev/null) || G=0
  S=$(grep -ci "$KW" "$SOP" 2>/dev/null) || S=0
  echo "Pattern '$KW' — Guide: $G, SOP: $S" | tee -a "$EVIDENCE"
done
```

**Expected:** Both documents cover the same TriPass concepts.
**Verdict:** Both have non-zero counts for all patterns → PASS / FAIL

### VF-08.7: Guide Deny Rules vs settings.json

```bash
echo "=== VF-08.7: Deny rules cross-check ===" | tee -a "$EVIDENCE"
# Already covered by VF-05.2 and VF-05.3 — verify both gave same conclusion
echo "See VF-05.2 and VF-05.3 for deny rule verification" | tee -a "$EVIDENCE"
```

**Verdict:** Inherit from VF-05.2 + VF-05.3.

### VF-08.8: Guide MCP Servers vs settings.json

```bash
echo "=== VF-08.8: MCP cross-check ===" | tee -a "$EVIDENCE"
# Already covered by VF-05.7 — verify consistency
echo "See VF-05.7 for MCP server verification" | tee -a "$EVIDENCE"
```

**Verdict:** Inherit from VF-05.7.

---

## VF-09: Memory Update (Mission Gate V-9)

### VF-09.1: V6-GUIDE-REGEN-001 in MEMORY.md

```bash
echo "=== VF-09.1: Mission entry ===" | tee -a "$EVIDENCE"
MEMORY="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
grep -n "V6-GUIDE-REGEN-001\|V6.*GUIDE.*REGEN" "$MEMORY" 2>&1 | tee -a "$EVIDENCE"
ENTRY=$(grep -c "V6-GUIDE-REGEN-001" "$MEMORY" 2>/dev/null) || ENTRY=0
echo "V6-GUIDE-REGEN-001 entries: $ENTRY" | tee -a "$EVIDENCE"
```

**Expected:** At least 1 entry in completed missions.
**Verdict:** `[ "$ENTRY" -ge 1 ]` → PASS / FAIL

**FIX (if FAIL):** Add to the Completed Missions section:
`- V6-GUIDE-REGEN-001: Complete (2026-02-09) — Surface 9, TriPass QA hardening, phantom plugin fix, V6PP guide`

### VF-09.2: Entry Notes Key Deliverables

```bash
echo "=== VF-09.2: Entry content ===" | tee -a "$EVIDENCE"
MEMORY="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
ENTRY_LINE=$(grep "V6-GUIDE-REGEN-001" "$MEMORY" 2>/dev/null)
echo "Entry: $ENTRY_LINE" | tee -a "$EVIDENCE"
for KW in "Surface 9\|surface.9" "TriPass\|tripass" "V6PP\|guide"; do
  C=$(echo "$ENTRY_LINE" | grep -ci "$KW" 2>/dev/null) || C=0
  echo "Entry mentions '$KW': $C" | tee -a "$EVIDENCE"
done
```

**Expected:** Entry mentions Surface 9, TriPass, and V6PP/guide.
**Verdict:** All 3 keywords present → PASS / FAIL

### VF-09.3: Sentinel Tags Current

```bash
echo "=== VF-09.3: Sentinel tags ===" | tee -a "$EVIDENCE"
MEMORY="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
grep "AUTOSYNC" "$MEMORY" 2>&1 | tee -a "$EVIDENCE"
TAG_COUNT=$(grep -c "AUTOSYNC" "$MEMORY" 2>/dev/null) || TAG_COUNT=0
echo "Sentinel tags: $TAG_COUNT" | tee -a "$EVIDENCE"
```

**Expected:** At least 5 sentinel tags present.
**Verdict:** `[ "$TAG_COUNT" -ge 5 ]` → PASS / FAIL

### VF-09.4: MEMORY.md Under 200 Lines

```bash
echo "=== VF-09.4: MEMORY.md size ===" | tee -a "$EVIDENCE"
MEMORY="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
LINES=$(wc -l < "$MEMORY" 2>/dev/null || echo 0)
echo "MEMORY.md lines: $LINES (limit: 200)" | tee -a "$EVIDENCE"
```

**Expected:** ≤ 200 lines.
**Verdict:** `[ "$LINES" -le 200 ]` → PASS / FAIL

---

## VF-10: V5PP-DMS Supersession (Mission Gate V-10)

### VF-10.1: V6PP Declares Supersession

```bash
echo "=== VF-10.1: Supersession declaration ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
grep -n "Supersedes\|supersedes" "$GUIDE" 2>&1 | tee -a "$EVIDENCE"
SUPER=$(grep -c "Supersedes.*V5PP\|supersedes.*V5PP" "$GUIDE" 2>/dev/null) || SUPER=0
echo "Supersession declarations: $SUPER" | tee -a "$EVIDENCE"
```

**Expected:** At least 1 explicit supersession statement.
**Verdict:** `[ "$SUPER" -ge 1 ]` → PASS / FAIL

### VF-10.2: V6PP Is Clearly Current

```bash
echo "=== VF-10.2: Current guide clarity ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
head -3 "$GUIDE" 2>&1 | tee -a "$EVIDENCE"
grep -c "V6PP\|Version.*6\|current" "$GUIDE" | head -1 2>&1 | tee -a "$EVIDENCE"
```

**Expected:** Title clearly indicates V6PP as the current version.
**Verdict:** Title contains "V6PP" → PASS / FAIL

### VF-10.3: V5PP Files Still Exist for History

```bash
echo "=== VF-10.3: V5PP historical files ===" | tee -a "$EVIDENCE"
ls -la /home/zaks/bookkeeping/docs/V5PP-*.md 2>&1 | tee -a "$EVIDENCE"
V5_EXISTS=$(ls /home/zaks/bookkeeping/docs/V5PP-*.md 2>/dev/null | wc -l)
echo "V5PP files on disk: $V5_EXISTS" | tee -a "$EVIDENCE"
```

**Expected:** V5PP files exist (not deleted) for historical reference.
**Verdict:** `[ "$V5_EXISTS" -ge 1 ]` → PASS / FAIL

### VF-10.4: No V5PP Referenced as Current

```bash
echo "=== VF-10.4: No V5PP-as-current ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
CURRENT_V5=$(grep -ci "current.*V5PP\|latest.*V5PP\|use V5PP" "$GUIDE" 2>/dev/null) || CURRENT_V5=0
echo "V5PP referenced as current: $CURRENT_V5" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$CURRENT_V5" -eq 0 ]` → PASS / FAIL

---

## Stress Tests

### ST-1: validate-surface9.sh Executes Without Error

```bash
echo "=== ST-1: Surface 9 validation execution ===" | tee -a "$EVIDENCE"
cd /home/zaks/zakops-agent-api && bash tools/infra/validate-surface9.sh 2>&1 | tee -a "$EVIDENCE"
S9_EXIT=$?
echo "Exit code: $S9_EXIT" | tee -a "$EVIDENCE"
cd /mnt/c/Users/mzsai
```

**Expected:** Exit code 0 (all checks pass).
**Verdict:** `[ "$S9_EXIT" -eq 0 ]` → PASS / FAIL

### ST-2: MEMORY.md Two-Copy Divergence

```bash
echo "=== ST-2: MEMORY.md copy divergence ===" | tee -a "$EVIDENCE"
COPY_A="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
COPY_B="/root/.claude/projects/-home-zaks/memory/MEMORY.md"
LINES_A=$(wc -l < "$COPY_A" 2>/dev/null || echo 0)
LINES_B=$(wc -l < "$COPY_B" 2>/dev/null || echo 0)
echo "Copy A (-mnt-c-Users-mzsai): $LINES_A lines" | tee -a "$EVIDENCE"
echo "Copy B (-home-zaks): $LINES_B lines" | tee -a "$EVIDENCE"
if [ -f "$COPY_A" ] && [ -f "$COPY_B" ]; then
  DIFF_COUNT=$(diff "$COPY_A" "$COPY_B" 2>/dev/null | grep -c "^[<>]") || DIFF_COUNT=0
  echo "Divergent lines: $DIFF_COUNT" | tee -a "$EVIDENCE"
else
  echo "One copy missing" | tee -a "$EVIDENCE"
fi
```

**Expected:** Both copies exist. If both are maintained, they should be reasonably aligned (diff < 10 lines). If only one is authoritative, the other should be deprecated or symlinked.
**Verdict:** INFORMATIONAL — flag divergence for enhancement consideration.

### ST-3: CRLF Check on Hook Scripts

```bash
echo "=== ST-3: CRLF check ===" | tee -a "$EVIDENCE"
CRLF_COUNT=0
for F in /home/zaks/.claude/hooks/*.sh; do
  CR=$(grep -cP '\r$' "$F" 2>/dev/null) || CR=0
  if [ "$CR" -gt 0 ]; then
    echo "CRLF found in $F: $CR lines" | tee -a "$EVIDENCE"
    CRLF_COUNT=$((CRLF_COUNT + 1))
  fi
done
echo "Files with CRLF: $CRLF_COUNT" | tee -a "$EVIDENCE"
```

**Expected:** 0
**Verdict:** `[ "$CRLF_COUNT" -eq 0 ]` → PASS / FAIL

### ST-4: File Ownership on TriPass Artifacts

```bash
echo "=== ST-4: TriPass file ownership ===" | tee -a "$EVIDENCE"
ROOT_OWNED=0
for D in /home/zaks/bookkeeping/docs/_tripass_templates/ \
         /home/zaks/bookkeeping/docs/TRIPASS_SOP.md \
         /home/zaks/bookkeeping/docs/TRIPASS_LATEST_RUN.md; do
  if [ -e "$D" ]; then
    OWNER=$(stat -c '%U' "$D" 2>/dev/null)
    echo "$D: $OWNER" | tee -a "$EVIDENCE"
    [ "$OWNER" = "root" ] && ROOT_OWNED=$((ROOT_OWNED + 1))
  fi
done
echo "Root-owned TriPass artifacts: $ROOT_OWNED" | tee -a "$EVIDENCE"
```

**Expected:** 0 root-owned files under `/home/zaks/`.
**Verdict:** `[ "$ROOT_OWNED" -eq 0 ]` → PASS / FAIL

### ST-5: Contract Guardian Agent Description Updated

```bash
echo "=== ST-5: Contract Guardian surface count ===" | tee -a "$EVIDENCE"
AGENT_FILE="/home/zaks/.claude/agents/contract-guardian.md"
grep -i "surface\|contract" "$AGENT_FILE" 2>&1 | tee -a "$EVIDENCE"
STALE_8=$(grep -c "8 contract\|all 8\|8 surface" "$AGENT_FILE" 2>/dev/null) || STALE_8=0
echo "Stale '8 surfaces' in agent def: $STALE_8" | tee -a "$EVIDENCE"
```

**Expected:** 0 references to "8" surfaces (should be 9 or unspecified).
**Verdict:** `[ "$STALE_8" -eq 0 ]` → PASS / FAIL

**FIX (if FAIL):** Update contract-guardian.md description from "all 8 contract surfaces" to "all 9 contract surfaces" (or "all contract surfaces").

### ST-6: Guide Cross-References Valid

```bash
echo "=== ST-6: Cross-reference validity ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
XREFS=$(grep -oi "see Part [0-9]*\|see Appendix [A-E]" "$GUIDE" 2>/dev/null | sort -u)
echo "Cross-references found:" | tee -a "$EVIDENCE"
echo "$XREFS" | tee -a "$EVIDENCE"
INVALID=0
for XREF in $XREFS; do
  TARGET=$(echo "$XREF" | grep -o "Part [0-9]*\|Appendix [A-E]")
  FOUND=$(grep -c "## $TARGET" "$GUIDE" 2>/dev/null) || FOUND=0
  if [ "$FOUND" -eq 0 ]; then
    echo "INVALID xref: $XREF" | tee -a "$EVIDENCE"
    INVALID=$((INVALID + 1))
  fi
done
echo "Invalid cross-references: $INVALID" | tee -a "$EVIDENCE"
```

**Expected:** 0 invalid cross-references.
**Verdict:** `[ "$INVALID" -eq 0 ]` → PASS / FAIL

### ST-7: Project-Level Settings Hooks vs Guide Description

```bash
echo "=== ST-7: Hook registration location ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
# Hooks are in /home/zaks/.claude/settings.json (project-level)
# Guide says hooks are in ~/.claude/settings.json (line 84)
# For root user, ~ = /root, but hooks are at /home/zaks/.claude/settings.json
HOOK_CONFIG="/home/zaks/.claude/settings.json"
echo "Hook config file: $HOOK_CONFIG" | tee -a "$EVIDENCE"
HAS_HOOKS=$(python3 -c "import json; d=json.load(open('$HOOK_CONFIG')); print(len(d.get('hooks',{})))" 2>/dev/null || echo 0)
echo "Hook events in project settings: $HAS_HOOKS" | tee -a "$EVIDENCE"
# Check if guide describes the correct config tier
grep -n "hooks.*settings\|settings.*hooks" "$GUIDE" | head -3 2>&1 | tee -a "$EVIDENCE"
```

**Expected:** Guide accurately describes where hooks are registered (project-level `/home/zaks/.claude/settings.json`, not user-level `~/.claude/settings.json` which is `/root/.claude/settings.json`).
**Verdict:** INFORMATIONAL — flag if guide's hook registration location is ambiguous.

---

## Cross-Consistency Checks

### XC-1: MEMORY.md Path Consistency

```bash
echo "=== XC-1: MEMORY.md path consistency ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_MEM_PATH=$(grep -o '/root/.claude/projects/[^`]*memory/MEMORY.md' "$GUIDE" | head -1)
LOADED_PATH="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
echo "Guide says: $GUIDE_MEM_PATH" | tee -a "$EVIDENCE"
echo "Actually loaded: $LOADED_PATH" | tee -a "$EVIDENCE"
CONSISTENT=$([ "$GUIDE_MEM_PATH" = "$LOADED_PATH" ] && echo "YES" || echo "NO")
echo "Consistent: $CONSISTENT" | tee -a "$EVIDENCE"
```

**Verdict:** `$CONSISTENT = YES` → PASS / FAIL

### XC-2: Allow Rule Documentation Accuracy

```bash
echo "=== XC-2: Allow rules documentation ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_ALLOW=$(grep -o "Allow Rules ([0-9]*)" "$GUIDE" | grep -o "[0-9]*")
LIVE_ALLOW=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(len(d.get('permissions',{}).get('allow',[])))")
echo "Guide: $GUIDE_ALLOW, Live: $LIVE_ALLOW" | tee -a "$EVIDENCE"
DELTA=$((LIVE_ALLOW - GUIDE_ALLOW))
echo "Delta: $DELTA (off by $(echo $DELTA | tr -d '-'))" | tee -a "$EVIDENCE"
```

**Verdict:** Delta = 0 or guide explicitly notes summary → PASS / FAIL

### XC-3: MCP Server Documentation Accuracy

```bash
echo "=== XC-3: MCP server accuracy ===" | tee -a "$EVIDENCE"
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
grep "MCP\|mcp\|gmail\|crawl4ai\|github.*mcp\|playwright.*mcp" "$GUIDE" | head -10 2>&1 | tee -a "$EVIDENCE"
LIVE_SERVERS=$(python3 -c "import json; d=json.load(open('/root/.claude/settings.json')); print(sorted(d.get('mcpServers',{}).keys()))")
echo "Live servers: $LIVE_SERVERS" | tee -a "$EVIDENCE"
```

**Verdict:** Guide servers match live servers exactly → PASS / FAIL

### XC-4: MEMORY.md Phantom Plugin Line

```bash
echo "=== XC-4: MEMORY.md phantom after Phase 2 ===" | tee -a "$EVIDENCE"
MEMORY="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
PHANTOM=$(grep -c "/mnt/skills/" "$MEMORY" 2>/dev/null) || PHANTOM=0
echo "Phantom /mnt/skills/ in loaded MEMORY.md: $PHANTOM" | tee -a "$EVIDENCE"
if [ "$PHANTOM" -gt 0 ]; then
  grep -n "/mnt/skills/" "$MEMORY" 2>&1 | tee -a "$EVIDENCE"
fi
```

**Verdict:** `$PHANTOM = 0` → PASS / FAIL (Phase 2 requires all phantom references removed from MEMORY.md)

### XC-5: Contract Guardian "8 Surfaces" Stale Reference

```bash
echo "=== XC-5: Agent defs surface count ===" | tee -a "$EVIDENCE"
for F in /home/zaks/.claude/agents/*.md; do
  STALE=$(grep -c "8 contract\|all 8\|8 surface" "$F" 2>/dev/null) || STALE=0
  if [ "$STALE" -gt 0 ]; then
    echo "STALE in $(basename $F): $(grep "8 contract\|all 8\|8 surface" "$F")" | tee -a "$EVIDENCE"
  fi
done
GUIDE="/home/zaks/bookkeeping/docs/V6PP-SETUP-GUIDE.md"
GUIDE_STALE=$(grep -c "all 8 contract" "$GUIDE" 2>/dev/null) || GUIDE_STALE=0
echo "Guide stale '8 surfaces': $GUIDE_STALE" | tee -a "$EVIDENCE"
```

**Verdict:** 0 stale "8 surfaces" across agent defs and guide → PASS / FAIL

---

## Enhancement Opportunities

These are not blocking issues — all mission gates may pass while these enhancements remain. They represent improvement opportunities discovered during verification.

### ENH-1: validate-surface9 Makefile Target (HIGH)

**Observation:** `validate-surface9.sh` exists at `tools/infra/validate-surface9.sh` and is referenced in `contract-surfaces.md`, but there is no dedicated `make validate-surface9` target in the Makefile. The script must be invoked manually with `bash tools/infra/validate-surface9.sh`.

**Impact:** Inconsistent with other validation targets (`make validate-agent-config`, `make validate-sse-schema`). Operators expect `make validate-<surface>` pattern for all surfaces.

**Recommendation:** Add a `validate-surface9` target to the Makefile that runs `bash tools/infra/validate-surface9.sh`. Also add it to the `validate-local` dependency list so Surface 9 is checked during CI validation.

**Risk:** LOW — additive Makefile change, no behavior modification.

### ENH-2: Dual MEMORY.md Copy Consolidation (HIGH)

**Observation:** Two MEMORY.md copies exist at different paths:
- `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md` (127 lines, loaded when cwd is `/mnt/c/Users/mzsai`)
- `/root/.claude/projects/-home-zaks/memory/MEMORY.md` (130 lines, loaded when cwd is `/home/zaks`)

These copies have diverged (3-line difference). The V6PP guide points to the `-home-zaks` path as authoritative, but Claude Code sessions started from `/mnt/c/Users/mzsai` load the other copy and never see updates made to the `-home-zaks` copy.

**Impact:** Knowledge drift between sessions depending on working directory. A session starting from `/mnt/c/` may have stale facts while `-home-zaks` sessions have current ones, or vice versa.

**Recommendation:** Choose one canonical path and symlink the other, OR ensure `memory-sync.sh` updates BOTH copies. The guide should document whichever approach is chosen.

**Risk:** MEDIUM — incorrect symlink could cause Claude to load empty memory.

### ENH-3: Guide MCP Server Accuracy (CRITICAL — likely fails VF-05.7)

**Observation:** The V6PP guide lists MCP servers as `github` (modelcontextprotocol/server-github) and `playwright` (@playwright/mcp). The actual live `settings.json` has `gmail` (@gongrzhe/server-gmail-autoauth-mcp) and `crawl4ai-rag` (Docker RAG service).

**Impact:** Any operator following the guide for MCP server configuration would reference non-existent servers. Future sessions consulting the guide would have wrong expectations.

**Recommendation:** If this isn't caught by VF-05.7, update the guide's MCP Servers section to match live settings.json.

**Risk:** LOW — documentation-only change.

### ENH-4: Guide Allow Rule Count Transparency (MEDIUM)

**Observation:** The guide says "Allow Rules (4)" and lists 4 make-related patterns. The actual settings.json has 144 allow rules covering WebSearch, WebFetch, Bash patterns for docker/npm/pip/curl, MCP tool permissions, and more.

**Impact:** Misleading — an operator reading "4 allow rules" would not know 140 additional permissions exist. Security auditors would see a discrepancy.

**Recommendation:** Change heading to "Allow Rules (144 total — key patterns):" and add a note explaining the full scope. Alternatively, add a collapsed/appendix section with the complete list.

**Risk:** LOW — documentation-only change.

### ENH-5: Guide Hook Registration Location Clarity (MEDIUM)

**Observation:** The guide's Part 2 says hooks are configured in "User-level settings — `~/.claude/settings.json`" (line 84). But hooks are actually registered in `/home/zaks/.claude/settings.json` (project-level settings), while user-level settings (`/root/.claude/settings.json`) has no hooks. The guide also says "Project-level settings — `.claude/settings.json` (if exists; not used in ZakOps)" which is incorrect — it IS used for hooks.

**Impact:** An operator trying to find or modify hook registrations would look in the wrong file.

**Recommendation:** Correct the configuration loading order to show:
1. User-level: `~/.claude/settings.json` — permissions (deny/allow rules), MCP servers
2. Project-level: `/home/zaks/.claude/settings.json` — **hooks** (4 event types, 5 scripts)

**Risk:** LOW — documentation-only change.

### ENH-6: Guide Contract Guardian "8 Surfaces" Update (MEDIUM)

**Observation:** The Contract Guardian agent definition (`/home/zaks/.claude/agents/contract-guardian.md`) may still describe itself as validating "all 8 contract surfaces." With Surface 9 added, this should be "all 9 contract surfaces" (or "all contract surfaces" for future-proofing).

**Impact:** The agent's self-description would be stale. The V6PP guide's Appendix D quotes the agent definition verbatim, so both would show the wrong number.

**Recommendation:** Update the contract-guardian.md description and the guide's Appendix D quote.

**Risk:** LOW — description-only change.

### ENH-7: Guide Makefile Target Count (LOW)

**Observation:** The guide says "~112 targets" (line 75) but a live count may differ. Target counts change as missions add new targets.

**Recommendation:** Use `make -qp | awk -F: '/^[a-zA-Z]/ {print $1}' | sort -u | wc -l` to get the exact count and update the guide. Alternatively, use "~80+" as an approximate that won't go stale quickly.

**Risk:** LOW — cosmetic accuracy.

### ENH-8: Surface 9 in validate-local Dependency Chain (MEDIUM)

**Observation:** `validate-surface9.sh` exists but may not be part of the `validate-local` make target's dependency chain. If Surface 9 validation runs separately from CI validation, convention drift could go undetected.

**Recommendation:** Add `validate-surface9` as a dependency of `validate-local` (or `validate-full`), ensuring Surface 9 is checked alongside Surfaces 1-8 during standard validation.

**Risk:** LOW — if the script has bugs, it could block validate-local. Test the script first.

### ENH-9: Guide Version Hash for Traceability (LOW)

**Observation:** The guide's Document Information section records version and date but not a hash of the source files used to generate it. If the environment changes after generation, there's no way to verify whether the guide is still current without re-running every check.

**Recommendation:** Add a `Source Hash` field computed from key config files: `sha256sum settings.json CLAUDE.md MEMORY.md | sha256sum`. A future session can recompute and compare to detect drift.

**Risk:** LOW — additive, no behavior change.

### ENH-10: Completed Missions in V6PP Guide vs MEMORY.md Alignment (LOW)

**Observation:** The V6PP guide's Appendix E lists 9 completed missions (including QA missions). MEMORY.md lists 6 completed missions (excluding QA runs). The two registries have different scopes — the guide includes QA verification runs, MEMORY.md doesn't.

**Recommendation:** Add a note in the guide explaining the scope difference: "Appendix E includes QA verification runs; MEMORY.md lists primary missions only." This prevents future confusion about why the counts differ.

**Risk:** LOW — documentation clarity.

---

## Final Scorecard

| Gate | Description | Verdict | Remediation |
|------|-------------|---------|-------------|
| VF-01.1 | ENH-3 trap handler | | |
| VF-01.2 | release_lock function | | |
| VF-01.3 | ENH-1 T-3 SKIP | | |
| VF-01.4 | ENH-2 T-6 idempotency | | |
| VF-01.5 | ENH-9 chown calls | | |
| VF-01.6 | ENH-9 root safety check | | |
| VF-01.7 | ENH-8 gates in MEMORY.md | | |
| VF-01.8 | Lock file path consistent | | |
| VF-02.1 | SOP no phantom refs | | |
| VF-02.2 | Templates no phantom refs | | |
| VF-02.3 | tripass.sh no phantom refs | | |
| VF-02.4 | MEMORY.md no phantom refs | | |
| VF-02.5 | V6PP guide no phantom refs | | |
| VF-02.6 | Rules no phantom refs | | |
| VF-02.7 | No "frontend-design plugin" phrase | | |
| VF-02.8 | SOP references design-system.md | | |
| VF-03.1 | Manifest file exists | | |
| VF-03.2 | Manifest declares 7 conventions | | |
| VF-03.3 | design-system.md with YAML | | |
| VF-03.4 | Rule trigger paths correct | | |
| VF-03.5 | Category A — 7 conventions | | |
| VF-03.6 | Category B — design quality | | |
| VF-03.7 | contract-surfaces.md Surface 9 | | |
| VF-03.8 | validate-surface9.sh executable | | |
| VF-03.9 | Validation checks 3 conventions | | |
| VF-04.1 | 9 Parts present | | |
| VF-04.2 | 5 Appendices present | | |
| VF-04.3 | What Changed section | | |
| VF-04.4 | No TBD/placeholder text | | |
| VF-04.5 | Document Information section | | |
| VF-04.6 | Parts have substance | | |
| VF-04.7 | Line count 1000-1500 | | |
| VF-05.1 | PostgreSQL port accuracy | | |
| VF-05.2 | Deny rule count (12) | | |
| VF-05.3 | All 12 deny rules listed | | |
| VF-05.4 | Allow rule count accurate | | |
| VF-05.5 | Command count (13) | | |
| VF-05.6 | Hook count (5) | | |
| VF-05.7 | MCP servers match live | | |
| VF-05.8 | 9 contract surfaces | | |
| VF-05.9 | 5 TriPass enhancements documented | | |
| VF-05.10 | Port 8090 decommissioned | | |
| VF-05.11 | Agent definitions path | | |
| VF-05.12 | No stale "8 surfaces" | | |
| VF-06.1 | CLAUDE.md monorepo lines | | |
| VF-06.2 | CLAUDE.md root lines | | |
| VF-06.3 | Hook count metric | | |
| VF-06.4 | Rule count metric | | |
| VF-06.5 | Command count metric | | |
| VF-06.6 | Deny rule count metric | | |
| VF-06.7 | Allow rule count metric | | |
| VF-06.8 | MEMORY.md line count | | |
| VF-07.1 | Line count range | | |
| VF-07.2 | No duplicate paragraphs | | |
| VF-07.3 | Service map appears once | | |
| VF-07.4 | Deny rules table once | | |
| VF-08.1 | Service map vs CLAUDE.md | | |
| VF-08.2 | Surfaces vs contract-surfaces.md | | |
| VF-08.3 | Commands vs directory | | |
| VF-08.4 | Hooks vs settings.json | | |
| VF-08.5 | MEMORY.md path accuracy | | |
| VF-08.6 | TriPass vs TRIPASS_SOP.md | | |
| VF-08.7 | Deny rules vs settings.json | | |
| VF-08.8 | MCP servers vs settings.json | | |
| VF-09.1 | V6-GUIDE-REGEN-001 entry | | |
| VF-09.2 | Entry notes deliverables | | |
| VF-09.3 | Sentinel tags current | | |
| VF-09.4 | MEMORY.md under 200 lines | | |
| VF-10.1 | Supersession declaration | | |
| VF-10.2 | V6PP clearly current | | |
| VF-10.3 | V5PP files preserved | | |
| VF-10.4 | No V5PP-as-current refs | | |
| **ST-1** | validate-surface9.sh runs | | |
| **ST-2** | MEMORY.md copy divergence | | |
| **ST-3** | CRLF in hooks | | |
| **ST-4** | TriPass file ownership | | |
| **ST-5** | Contract Guardian surface count | | |
| **ST-6** | Cross-reference validity | | |
| **ST-7** | Hook registration location | | |
| **XC-1** | MEMORY.md path consistency | | |
| **XC-2** | Allow rule count accuracy | | |
| **XC-3** | MCP server accuracy | | |
| **XC-4** | MEMORY.md phantom cleanup | | |
| **XC-5** | Agent defs surface count | | |

**Total Gates: 81** (68 verification + 7 stress + 5 cross-consistency + 1 inherited)

**Enhancements Identified: 10** (ENH-1 through ENH-10)

---

## Execution Notes

- Execute all bash blocks in order
- Use `$EVIDENCE` variable throughout (set in Pre-Flight)
- Fill in scorecard verdicts as you go
- Apply FIX sections immediately on FAIL, re-verify, then continue
- After all gates complete, summarize: total PASS / FAIL / SKIP / remediated
- List all applied enhancements (if user approves any)

---

*End of QA Document — QA-V6GR-VERIFY-001*

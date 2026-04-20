# QA VERIFICATION & REMEDIATION — TRIPASS-INTEGRATE-002
## Codename: `QA-TP-VERIFY-001`
## Version: V1 | Date: 2026-02-09
## Executor: Claude Code (Opus 4.6)
## Authority: FULL EXECUTION — Verify everything, fix what fails, enhance what's weak, defer nothing
## Predecessor: TRIPASS-INTEGRATE-002 (9 acceptance criteria, completed 2026-02-09)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   QA DIRECTIVE: VERIFY. STRESS-TEST. ENHANCE.                                ║
║                                                                              ║
║   TRIPASS-INTEGRATE-002 delivered a multi-agent pipeline orchestrator         ║
║   with 4 passes, 6 gates, and a proof-of-life run. This QA mission          ║
║   does three things:                                                         ║
║                                                                              ║
║   1. VERIFY — Every acceptance criterion is re-checked from raw              ║
║      filesystem state. Claims are tested against actual files,               ║
║      actual hashes, actual outputs. Nothing taken on faith.                  ║
║                                                                              ║
║   2. STRESS-TEST — Edge cases the mission didn't exercise:                   ║
║      What happens when CLIs crash? When templates are malformed?             ║
║      When the lock file persists after a crash? When gates run               ║
║      on placeholder content? These are the cracks.                           ║
║                                                                              ║
║   3. ENHANCE — Even where everything works, identify opportunities           ║
║      to make it more robust, more observable, more maintainable.             ║
║      Enhancements are REPORTED, not applied. Operator decides.               ║
║                                                                              ║
║   SCOPE: 9 ACs → 72 verification gates + enhancement report                 ║
║   DEFERRALS: ZERO on verification. Enhancements are advisory.               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## VERDICT RULES

```
VERIFICATION GATES: PASS or FAIL. Nothing else. Zero deferrals.
Every gate must:
  1. Be checked against the ACTUAL FILE (read it, hash it, count it)
  2. Match the EXACT expected value (not "looks about right")
  3. Be evidenced (command output captured to evidence directory)
  4. Cross-check at BOTH endpoints where applicable

ENHANCEMENT OPPORTUNITIES: REPORT or SKIP.
  - Enhancements are NOT gates — they cannot cause a FAIL verdict
  - Each enhancement is tagged with severity (HIGH / MEDIUM / LOW)
  - Each includes: what it improves, how to implement it, and risk if skipped
  - Operator reviews and decides which to apply
  - Enhancements that ARE applied get re-verified before final scorecard
```

---

## EVIDENCE STRUCTURE

```
/home/zaks/bookkeeping/qa-verifications/QA-TP-VERIFY-001/
├── evidence/
│   ├── AC-1-pipeline-structure/
│   ├── AC-2-autonomous-execution/
│   ├── AC-3-graceful-degradation/
│   ├── AC-4-append-only-proof/
│   ├── AC-5-deliverable-quality/
│   ├── AC-6-memory-integration/
│   ├── AC-7-makefile-integration/
│   ├── AC-8-documentation/
│   ├── AC-9-proof-of-life/
│   ├── stress-tests/
│   ├── enhancements/
│   ├── regression/
│   └── FINAL/
│       └── final_report.txt
└── completion-report.md
```

---

## PRE-FLIGHT: ESTABLISH BASELINE

```bash
# ═══════════════════════════════════════════════════════════
# PRE-FLIGHT: Paths, directories, baseline
# ═══════════════════════════════════════════════════════════

MONOREPO="/home/zaks/zakops-agent-api"
QA_ROOT="/home/zaks/bookkeeping/qa-verifications/QA-TP-VERIFY-001"
TRIPASS_TOOL="$MONOREPO/tools/tripass/tripass.sh"
TEMPLATES_DIR="/home/zaks/bookkeeping/docs/_tripass_templates"
RUNS_DIR="/home/zaks/bookkeeping/docs/_tripass_runs"
SOP_PATH="/home/zaks/bookkeeping/docs/TRIPASS_SOP.md"
LATEST_RUN="/home/zaks/bookkeeping/docs/TRIPASS_LATEST_RUN.md"
CHANGES_MD="/home/zaks/bookkeeping/CHANGES.md"
MEMORY_ACTIVE="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
HOOKS_DIR="/home/zaks/.claude/hooks"
MAKEFILE="$MONOREPO/Makefile"

# Create evidence directories
mkdir -p "$QA_ROOT/evidence"/{AC-1-pipeline-structure,AC-2-autonomous-execution,AC-3-graceful-degradation,AC-4-append-only-proof,AC-5-deliverable-quality,AC-6-memory-integration,AC-7-makefile-integration,AC-8-documentation,AC-9-proof-of-life,stress-tests,enhancements,regression,FINAL}

# Baseline validation
cd "$MONOREPO"
make validate-local 2>&1 | tee "$QA_ROOT/evidence/regression/validate-local-pre.log"
echo "EXIT_CODE=$?" >> "$QA_ROOT/evidence/regression/validate-local-pre.log"
# ── STOP IF EXIT CODE != 0 ──
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-1: PIPELINE STRUCTURE
# Claim: init creates templates + SOP; run creates correct directory structure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC1="$QA_ROOT/evidence/AC-1-pipeline-structure"

# ── Gate A1.1: Orchestrator script exists and is executable ──
ls -la "$TRIPASS_TOOL" | tee "$AC1/tripass_tool_exists.txt"
file "$TRIPASS_TOOL" >> "$AC1/tripass_tool_exists.txt"
# Expected: exists, executable, Bash script

# ── Gate A1.2: Orchestrator script line count is substantial ──
wc -l "$TRIPASS_TOOL" | tee "$AC1/tripass_line_count.txt"
# Expected: > 500 lines (actual ~1037)

# ── Gate A1.3: All 4 templates exist ──
for t in pass1.md pass2.md pass3.md pass4_metaqa.md; do
  if [ -f "$TEMPLATES_DIR/$t" ]; then
    LINES=$(wc -l < "$TEMPLATES_DIR/$t")
    echo "FOUND: $t ($LINES lines)"
  else
    echo "MISSING: $t"
  fi
done | tee "$AC1/templates_audit.txt"
# Expected: all 4 FOUND, each > 50 lines

# ── Gate A1.4: Templates are parameterized (contain {{VARIABLE}} placeholders) ──
for t in pass1.md pass2.md pass3.md pass4_metaqa.md; do
  COUNT=$(grep -c '{{' "$TEMPLATES_DIR/$t" 2>/dev/null) || COUNT=0
  echo "$t: $COUNT template variables"
done | tee "$AC1/template_variables.txt"
# Expected: each template has >= 5 variables

# ── Gate A1.5: Run directory structure follows contract ──
# Find most recent run
LATEST_ID=$(ls -1 "$RUNS_DIR" | sort | tail -1)
LATEST_PATH="$RUNS_DIR/$LATEST_ID"
echo "LATEST_RUN=$LATEST_ID" | tee "$AC1/latest_run_structure.txt"
for dir in 00_context 01_pass1 02_pass2 03_pass3 04_metaqa EVIDENCE; do
  if [ -d "$LATEST_PATH/$dir" ]; then
    echo "DIR EXISTS: $dir/ ($(ls -1 "$LATEST_PATH/$dir" | wc -l) files)"
  else
    echo "DIR MISSING: $dir/"
  fi
done >> "$AC1/latest_run_structure.txt"
# Expected: all 6 directories exist

# ── Gate A1.6: Required run files exist ──
for f in WORKSPACE.md MASTER_LOG.md FINAL_MASTER.md; do
  if [ -f "$LATEST_PATH/$f" ]; then
    SIZE=$(wc -c < "$LATEST_PATH/$f")
    echo "FOUND: $f ($SIZE bytes)"
  else
    echo "MISSING: $f"
  fi
done | tee "$AC1/run_files_audit.txt"
# Expected: all 3 FOUND, all > 0 bytes

# ── Gate A1.7: SOP document exists ──
wc -l "$SOP_PATH" | tee "$AC1/sop_exists.txt"
# Expected: exists, > 100 lines
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A1.1 | Orchestrator exists and is executable | yes + executable | |
| A1.2 | Script line count | > 500 | |
| A1.3 | All 4 templates exist and are substantial | 4 found, each > 50 lines | |
| A1.4 | Templates are parameterized | each >= 5 variables | |
| A1.5 | Run directory has all 6 required subdirectories | all 6 present | |
| A1.6 | Run has WORKSPACE.md, MASTER_LOG.md, FINAL_MASTER.md | all 3 present, > 0 bytes | |
| A1.7 | SOP exists and is substantial | > 100 lines | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-2: AUTONOMOUS EXECUTION
# Claim: Pipeline executes all passes with no human intervention when CLIs available
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC2="$QA_ROOT/evidence/AC-2-autonomous-execution"

# ── Gate A2.1: Script has agent execution functions for all 3 agents ──
for agent in claude gemini codex; do
  grep -n "run_agent_${agent}()" "$TRIPASS_TOOL" | head -1
done | tee "$AC2/agent_functions.txt"
# Expected: all 3 functions defined

# ── Gate A2.2: CLI discovery logic exists and checks all 3 CLIs ──
grep -n "discover_clis\|GEMINI_CLI\|CODEX_CLI\|CLAUDE_CLI" "$TRIPASS_TOOL" | tee "$AC2/cli_discovery_code.txt"
# Expected: discovery function + 3 CLI variables

# ── Gate A2.3: Gemini CLI is actually available ──
ls -la /root/.npm-global/bin/gemini 2>&1 | tee "$AC2/gemini_cli_check.txt"
# Expected: symlink exists

# ── Gate A2.4: Codex CLI is actually available ──
ls -la /root/.npm-global/bin/codex 2>&1 | tee "$AC2/codex_cli_check.txt"
# Expected: symlink exists

# ── Gate A2.5: CLI discovery output exists in proof-of-life run ──
cat "$LATEST_PATH/00_context/cli_discovery.md" | tee "$AC2/cli_discovery_output.txt"
# Expected: shows all 3 CLIs with availability status

# ── Gate A2.6: Agent execution has timeout protection ──
grep -n "timeout\|TIMEOUT" "$TRIPASS_TOOL" | tee "$AC2/timeout_protection.txt"
# Expected: timeout mechanism present (900s default)

# ── Gate A2.7: Pipeline runs all 4 passes in sequence ──
grep -n "PASS [1-4].*START\|pass.*1.*start\|pass.*2.*start\|pass.*3.*start\|pass.*4" "$TRIPASS_TOOL" | tee "$AC2/pass_sequence.txt"
# Expected: evidence of Pass 1→2→3→4 sequencing in script
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A2.1 | Agent execution functions for all 3 agents | 3 functions defined | |
| A2.2 | CLI discovery logic for all 3 CLIs | discovery + 3 variables | |
| A2.3 | Gemini CLI available at /root/.npm-global/bin/ | symlink exists | |
| A2.4 | Codex CLI available at /root/.npm-global/bin/ | symlink exists | |
| A2.5 | CLI discovery output in proof-of-life run | shows all 3 CLIs | |
| A2.6 | Timeout protection on agent execution | timeout present | |
| A2.7 | Pipeline sequences all passes correctly | 4 passes in order | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-3: GRACEFUL DEGRADATION
# Claim: Pipeline detects missing CLIs and degrades to generate-only mode
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC3="$QA_ROOT/evidence/AC-3-graceful-degradation"

# ── Gate A3.1: Script supports --generate-only flag ──
grep -n "\-\-generate-only" "$TRIPASS_TOOL" | tee "$AC3/generate_only_flag.txt"
# Expected: flag parsed and handled

# ── Gate A3.2: Per-agent degradation when CLI unavailable ──
grep -n "not available.*generate\|generate.*only.*for\|generate-only" "$TRIPASS_TOOL" | tee "$AC3/per_agent_degradation.txt"
# Expected: per-agent fallback logic

# ── Gate A3.3: Proof-of-life run produced prompts even in generate-only mode ──
ls -la "$LATEST_PATH/01_pass1/"*prompt* 2>/dev/null | tee "$AC3/pass1_prompts.txt"
# Expected: 3 prompt files exist (claude_prompt.md, gemini_prompt.md, codex_prompt.md)

# ── Gate A3.4: Proof-of-life run produced placeholder reports ──
ls -la "$LATEST_PATH/01_pass1/"*report* 2>/dev/null | tee "$AC3/pass1_reports.txt"
# Expected: 3 report files exist (placeholders, but files exist)

# ── Gate A3.5: Pipeline did NOT crash on missing execution ──
grep -i "error\|crash\|abort\|FAIL" "$LATEST_PATH/MASTER_LOG.md" | tee "$AC3/no_crash.txt"
# Expected: no crash/error/abort entries (PIPELINE COMPLETE present)

# ── Gate A3.6: MASTER_LOG.md shows pipeline completed ──
grep "PIPELINE COMPLETE" "$LATEST_PATH/MASTER_LOG.md" | tee "$AC3/pipeline_complete.txt"
# Expected: at least 1 match

# ── Gate A3.7: Generate-only mode logged in discovery output ──
grep -i "generate\|unavail\|available" "$LATEST_PATH/00_context/cli_discovery.md" | tee "$AC3/discovery_mode.txt"
# Expected: CLI availability documented
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A3.1 | --generate-only flag supported | flag parsed | |
| A3.2 | Per-agent degradation logic | fallback for each agent | |
| A3.3 | Pass 1 prompts generated | 3 prompt files | |
| A3.4 | Pass 1 reports exist (even as placeholders) | 3 report files | |
| A3.5 | No crash/error/abort in MASTER_LOG | 0 crash entries | |
| A3.6 | Pipeline completed successfully | PIPELINE COMPLETE present | |
| A3.7 | CLI availability documented in discovery | availability logged | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-4: APPEND-ONLY PROOF
# Claim: WORKSPACE.md and MASTER_LOG.md have cryptographic evidence proving
#        no content was removed or truncated
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC4="$QA_ROOT/evidence/AC-4-append-only-proof"

# ── Gate A4.1: Append-only log file exists in EVIDENCE/ ──
ls -la "$LATEST_PATH/EVIDENCE/append_only_log.txt" | tee "$AC4/log_exists.txt"
# Expected: file exists, non-empty

# ── Gate A4.2: Log uses SHA256 (not MD5 or weaker) ──
grep -c "sha256=" "$LATEST_PATH/EVIDENCE/append_only_log.txt" | tee "$AC4/hash_algorithm.txt"
grep "sha256=" "$LATEST_PATH/EVIDENCE/append_only_log.txt" | head -3 >> "$AC4/hash_algorithm.txt"
# Expected: >= 1 sha256 entries

# ── Gate A4.3: WORKSPACE.md size never decreases (monotonic growth) ──
python3 -c "
import re
prev_size = 0
violations = 0
with open('$LATEST_PATH/EVIDENCE/append_only_log.txt') as f:
    for line in f:
        if 'WORKSPACE' in line:
            m = re.search(r'size=(\d+)', line)
            if m:
                size = int(m.group(1))
                if size < prev_size:
                    violations += 1
                    print(f'VIOLATION: {prev_size} -> {size} in: {line.strip()}')
                prev_size = size
print(f'WORKSPACE_VIOLATIONS={violations}')
print(f'FINAL_SIZE={prev_size}')
" | tee "$AC4/workspace_monotonic.txt"
# Expected: WORKSPACE_VIOLATIONS=0

# ── Gate A4.4: MASTER_LOG.md size never decreases ──
python3 -c "
import re
prev_size = 0
violations = 0
with open('$LATEST_PATH/EVIDENCE/append_only_log.txt') as f:
    for line in f:
        if 'MASTER_LOG' in line:
            m = re.search(r'size=(\d+)', line)
            if m:
                size = int(m.group(1))
                if size < prev_size:
                    violations += 1
                    print(f'VIOLATION: {prev_size} -> {size} in: {line.strip()}')
                prev_size = size
print(f'MASTER_LOG_VIOLATIONS={violations}')
print(f'FINAL_SIZE={prev_size}')
" | tee "$AC4/masterlog_monotonic.txt"
# Expected: MASTER_LOG_VIOLATIONS=0

# ── Gate A4.5: BEFORE/AFTER hash continuity ──
# Every "BEFORE" hash of step N should match the "AFTER" hash of step N-1
# This proves no external modification occurred between tracked operations
python3 -c "
import re
last_ws_hash = None
last_ml_hash = None
gaps = 0
with open('$LATEST_PATH/EVIDENCE/append_only_log.txt') as f:
    for line in f:
        m = re.search(r'sha256=([a-f0-9]+)', line)
        if not m:
            continue
        h = m.group(1)
        if 'WORKSPACE' in line:
            if 'BEFORE' in line and last_ws_hash and h != last_ws_hash:
                gaps += 1
                print(f'GAP: WORKSPACE hash mismatch at: {line.strip()[:80]}')
            if 'AFTER' in line or 'INIT' in line:
                last_ws_hash = h
        elif 'MASTER_LOG' in line:
            if 'BEFORE' in line and last_ml_hash and h != last_ml_hash:
                gaps += 1
                print(f'GAP: MASTER_LOG hash mismatch at: {line.strip()[:80]}')
            if 'AFTER' in line or 'INIT' in line:
                last_ml_hash = h
print(f'HASH_GAPS={gaps}')
" | tee "$AC4/hash_continuity.txt"
# Expected: HASH_GAPS=0

# ── Gate A4.6: Current file hashes match last recorded hashes ──
# Verify no modification occurred after pipeline completed
CURRENT_WS_HASH=$(sha256sum "$LATEST_PATH/WORKSPACE.md" | cut -d' ' -f1)
LAST_WS_HASH=$(grep "WORKSPACE" "$LATEST_PATH/EVIDENCE/append_only_log.txt" | tail -1 | grep -oP 'sha256=\K[a-f0-9]+')
echo "CURRENT_WS=$CURRENT_WS_HASH" | tee "$AC4/post_completion_integrity.txt"
echo "LAST_RECORDED_WS=$LAST_WS_HASH" >> "$AC4/post_completion_integrity.txt"
if [ "$CURRENT_WS_HASH" = "$LAST_WS_HASH" ]; then
  echo "WORKSPACE_INTEGRITY=PASS"
else
  echo "WORKSPACE_INTEGRITY=FAIL (file modified after pipeline)"
fi >> "$AC4/post_completion_integrity.txt"

CURRENT_ML_HASH=$(sha256sum "$LATEST_PATH/MASTER_LOG.md" | cut -d' ' -f1)
LAST_ML_HASH=$(grep "MASTER_LOG" "$LATEST_PATH/EVIDENCE/append_only_log.txt" | tail -1 | grep -oP 'sha256=\K[a-f0-9]+')
echo "CURRENT_ML=$CURRENT_ML_HASH" >> "$AC4/post_completion_integrity.txt"
echo "LAST_RECORDED_ML=$LAST_ML_HASH" >> "$AC4/post_completion_integrity.txt"
if [ "$CURRENT_ML_HASH" = "$LAST_ML_HASH" ]; then
  echo "MASTERLOG_INTEGRITY=PASS"
else
  echo "MASTERLOG_INTEGRITY=FAIL (file modified after pipeline)"
fi >> "$AC4/post_completion_integrity.txt"
# Expected: both PASS

# ── Gate A4.7: Gate T-1 implementation in script verifies both files ──
grep -A20 "gate_t1_append_only" "$TRIPASS_TOOL" | head -25 | tee "$AC4/gate_t1_code.txt"
# Expected: function exists and checks both WORKSPACE and MASTER_LOG
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A4.1 | Append-only log exists | non-empty file | |
| A4.2 | Uses SHA256 hashing | sha256= entries | |
| A4.3 | WORKSPACE.md size monotonically increases | VIOLATIONS=0 | |
| A4.4 | MASTER_LOG.md size monotonically increases | VIOLATIONS=0 | |
| A4.5 | Hash continuity between BEFORE/AFTER pairs | GAPS=0 | |
| A4.6 | Current file hashes match last recorded | both PASS | |
| A4.7 | Gate T-1 code checks both files | function verifies both | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-5: FINAL DELIVERABLE QUALITY
# Claim: FINAL_MASTER.md has deduplicated findings with 5 required fields,
#        agent attribution, and builder-ready gates
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC5="$QA_ROOT/evidence/AC-5-deliverable-quality"

# ── Gate A5.1: FINAL_MASTER.md exists ──
ls -la "$LATEST_PATH/FINAL_MASTER.md" | tee "$AC5/final_master_exists.txt"
wc -c "$LATEST_PATH/FINAL_MASTER.md" >> "$AC5/final_master_exists.txt"
# Expected: exists, non-empty

# ── Gate A5.2: Check if FINAL_MASTER.md is a placeholder or real content ──
grep -c "placeholder\|Generate-Only\|generate-only\|manually" "$LATEST_PATH/FINAL_MASTER.md" | tee "$AC5/placeholder_check.txt"
cat "$LATEST_PATH/FINAL_MASTER.md" >> "$AC5/placeholder_check.txt"
# NOTE: If generate-only mode, this will be a placeholder — that is ACCEPTABLE
# for AC-5 IF the consolidation PROMPT specifies the 5-field requirement

# ── Gate A5.3: Consolidation prompt enforces 5 required fields ──
REQUIRED_FIELDS=("Root Cause" "Fix Approach" "Industry Standard" "System Fit" "Enforcement")
FOUND=0
PROMPT_FILE="$LATEST_PATH/03_pass3/consolidation_prompt.md"
for field in "${REQUIRED_FIELDS[@]}"; do
  if grep -qi "$field" "$PROMPT_FILE" 2>/dev/null; then
    echo "FOUND: $field"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: $field"
  fi
done | tee "$AC5/five_fields_in_prompt.txt"
echo "FOUND=$FOUND/5" >> "$AC5/five_fields_in_prompt.txt"
# Expected: 5/5

# ── Gate A5.4: Pass 1 template enforces 5 required fields ──
FOUND=0
for field in "${REQUIRED_FIELDS[@]}"; do
  if grep -qi "$field" "$TEMPLATES_DIR/pass1.md" 2>/dev/null; then
    echo "FOUND: $field"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: $field"
  fi
done | tee "$AC5/five_fields_in_pass1_template.txt"
echo "FOUND=$FOUND/5" >> "$AC5/five_fields_in_pass1_template.txt"
# Expected: 5/5

# ── Gate A5.5: Gate T-3 (structural validity) checks for required fields ──
grep -A30 "gate_t3_structural" "$TRIPASS_TOOL" | head -35 | tee "$AC5/gate_t3_code.txt"
# Expected: function checks for presence of required fields in FINAL_MASTER.md

# ── Gate A5.6: Templates instruct agents to include identity headers ──
grep -n "identity\|header\|agent.*name\|AGENT_NAME" "$TEMPLATES_DIR/pass1.md" | tee "$AC5/identity_header_instruction.txt"
# Expected: agents told to begin with identity header
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A5.1 | FINAL_MASTER.md exists and is non-empty | yes | |
| A5.2 | Placeholder status documented | noted (generate-only OK) | |
| A5.3 | Consolidation prompt enforces all 5 fields | 5/5 | |
| A5.4 | Pass 1 template enforces all 5 fields | 5/5 | |
| A5.5 | Gate T-3 code verifies field presence | function checks fields | |
| A5.6 | Templates require identity headers | instruction present | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-6: MEMORY INTEGRATION
# Claim: Successful runs recorded in MEMORY.md, LATEST_RUN.md, CHANGES.md
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC6="$QA_ROOT/evidence/AC-6-memory-integration"

# ── Gate A6.1: MEMORY.md has TriPass mission entry ──
grep -n -i "TRIPASS-INTEGRATE\|tripass.*complete\|TriPass Pipeline" "$MEMORY_ACTIVE" | tee "$AC6/memory_tripass_entry.txt"
# Expected: at least 1 completed mission entry

# ── Gate A6.2: MEMORY.md documents TriPass key paths ──
grep -n "tripass" "$MEMORY_ACTIVE" | tee "$AC6/memory_tripass_paths.txt"
# Expected: run directory, templates, SOP paths documented

# ── Gate A6.3: MEMORY.md documents Makefile targets ──
grep -n "tripass-init\|tripass-run\|tripass-status\|tripass-gates" "$MEMORY_ACTIVE" | tee "$AC6/memory_make_targets.txt"
# Expected: at least 2 make targets mentioned

# ── Gate A6.4: TRIPASS_LATEST_RUN.md exists and points to valid run ──
cat "$LATEST_RUN" | tee "$AC6/latest_run_pointer.txt"
# Extract the run path and verify it exists
RUN_PATH=$(grep -oP '(?<=Path:\*\*|Path: ).*' "$LATEST_RUN" | head -1 | xargs)
if [ -d "$RUN_PATH" ]; then
  echo "POINTER_VALID=true (directory exists)"
else
  echo "POINTER_VALID=false (directory does not exist)"
fi >> "$AC6/latest_run_pointer.txt"
# Expected: POINTER_VALID=true

# ── Gate A6.5: CHANGES.md has TriPass entry ──
grep -n -i "tripass\|TP-" "$CHANGES_MD" | head -5 | tee "$AC6/changes_tripass.txt"
# Expected: at least 1 entry

# ── Gate A6.6: Gate T-6 implementation updates all 3 locations ──
grep -A40 "gate_t6_memory_sync" "$TRIPASS_TOOL" | head -45 | tee "$AC6/gate_t6_code.txt"
# Expected: function updates LATEST_RUN.md and CHANGES.md

# ── Gate A6.7: memory-sync.sh gathers TriPass metadata ──
grep -n "tripass" "$HOOKS_DIR/memory-sync.sh" | tee "$AC6/memory_sync_tripass.txt"
# Expected: gathers run count and/or latest run ID
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A6.1 | MEMORY.md has TriPass mission entry | >= 1 match | |
| A6.2 | MEMORY.md documents key paths | paths present | |
| A6.3 | MEMORY.md documents make targets | >= 2 targets | |
| A6.4 | LATEST_RUN.md points to valid directory | POINTER_VALID=true | |
| A6.5 | CHANGES.md has TriPass entry | >= 1 entry | |
| A6.6 | Gate T-6 updates LATEST_RUN + CHANGES | both updated | |
| A6.7 | memory-sync.sh gathers TriPass metadata | tripass references | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-7: MAKEFILE INTEGRATION
# Claim: At least 3 make targets (init, run, status) exist
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC7="$QA_ROOT/evidence/AC-7-makefile-integration"

# ── Gate A7.1: tripass-init target exists ──
grep -n "^tripass-init:" "$MAKEFILE" | tee "$AC7/target_init.txt"
# Expected: 1 match

# ── Gate A7.2: tripass-run target exists ──
grep -n "^tripass-run:" "$MAKEFILE" | tee "$AC7/target_run.txt"
# Expected: 1 match

# ── Gate A7.3: tripass-status target exists ──
grep -n "^tripass-status:" "$MAKEFILE" | tee "$AC7/target_status.txt"
# Expected: 1 match

# ── Gate A7.4: tripass-gates target exists (bonus — AC required 3, mission delivered 4) ──
grep -n "^tripass-gates:" "$MAKEFILE" | tee "$AC7/target_gates.txt"
# Expected: 1 match (exceeded requirement)

# ── Gate A7.5: Targets reference the correct tool path ──
grep -n "TRIPASS_TOOL\|tools/tripass/tripass.sh" "$MAKEFILE" | tee "$AC7/tool_path_ref.txt"
# Expected: variable defined and used by targets

# ── Gate A7.6: tripass-run accepts MISSION parameter ──
grep "MISSION" "$MAKEFILE" | grep tripass | tee "$AC7/mission_param.txt"
# Expected: $(MISSION) used in tripass-run

# ── Gate A7.7: tripass-run accepts MODE parameter ──
grep "MODE" "$MAKEFILE" | grep tripass | tee "$AC7/mode_param.txt"
# Expected: $(MODE) or $(or $(MODE),forensic) used

# ── Gate A7.8: Targets have help comments (## annotation) ──
grep "^tripass-.*:.*##" "$MAKEFILE" | tee "$AC7/help_annotations.txt"
# Expected: at least 3 targets with ## help text
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A7.1 | tripass-init target exists | 1 match | |
| A7.2 | tripass-run target exists | 1 match | |
| A7.3 | tripass-status target exists | 1 match | |
| A7.4 | tripass-gates target exists | 1 match | |
| A7.5 | Targets use correct tool path | reference present | |
| A7.6 | tripass-run accepts MISSION parameter | $(MISSION) used | |
| A7.7 | tripass-run accepts MODE parameter | $(MODE) used | |
| A7.8 | Targets have help annotations | >= 3 with ## | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-8: DOCUMENTATION
# Claim: TRIPASS_SOP.md covers all required topics
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC8="$QA_ROOT/evidence/AC-8-documentation"

# ── Gate A8.1: SOP covers "how to run the pipeline" ──
grep -n -i "how to run\|running.*pipeline\|quick.*start\|prerequisites" "$SOP_PATH" | head -5 | tee "$AC8/sop_how_to_run.txt"
# Expected: at least 1 match

# ── Gate A8.2: SOP covers "how to interpret outputs" ──
grep -n -i "interpret\|output\|directory.*structure\|reading.*result\|key.*file" "$SOP_PATH" | head -5 | tee "$AC8/sop_interpret.txt"
# Expected: at least 1 match

# ── Gate A8.3: SOP covers "how to add a new pipeline mode" ──
grep -n -i "new.*mode\|add.*mode\|template.*mechanism\|custom.*mode" "$SOP_PATH" | head -5 | tee "$AC8/sop_new_mode.txt"
# Expected: at least 1 match

# ── Gate A8.4: SOP covers "how to rerun a failed pass" ──
grep -n -i "rerun\|re-run\|failed.*pass\|recovery\|resume" "$SOP_PATH" | head -5 | tee "$AC8/sop_rerun.txt"
# Expected: at least 1 match

# ── Gate A8.5: SOP covers V5PP integration points ──
grep -n -i "V5PP\|integration\|gate.*system\|memory.*system\|hook" "$SOP_PATH" | head -5 | tee "$AC8/sop_v5pp.txt"
# Expected: at least 1 match

# ── Gate A8.6: SOP mentions frontend-design plugin ──
grep -n -i "frontend-design\|design.*plugin\|SKILL.md" "$SOP_PATH" | head -5 | tee "$AC8/sop_frontend_plugin.txt"
# Expected: at least 1 match (AC-8 explicit requirement)

# ── Gate A8.7: SOP documents all 3 pipeline modes ──
grep -n -i "forensic\|design\|implement" "$SOP_PATH" | tee "$AC8/sop_modes.txt"
# Expected: all 3 modes mentioned

# ── Gate A8.8: SOP documents the 6 TriPass gates (T-1 through T-6) ──
for gate in "T-1" "T-2" "T-3" "T-4" "T-5" "T-6"; do
  grep -c "$gate" "$SOP_PATH"
done | tee "$AC8/sop_gates.txt"
# Expected: all 6 return >= 1
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A8.1 | SOP: how to run | >= 1 match | |
| A8.2 | SOP: how to interpret outputs | >= 1 match | |
| A8.3 | SOP: how to add new mode | >= 1 match | |
| A8.4 | SOP: how to rerun failed pass | >= 1 match | |
| A8.5 | SOP: V5PP integration | >= 1 match | |
| A8.6 | SOP: frontend-design plugin | >= 1 match | |
| A8.7 | SOP: all 3 modes documented | forensic + design + implement | |
| A8.8 | SOP: all 6 gates documented | 6 gates referenced | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AC-9: PROOF OF LIFE
# Claim: At least one completed run exists with passing gates
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
AC9="$QA_ROOT/evidence/AC-9-proof-of-life"

# ── Gate A9.1: At least one completed run directory exists ──
RUN_COUNT=$(ls -1 "$RUNS_DIR" 2>/dev/null | wc -l)
echo "RUN_COUNT=$RUN_COUNT" | tee "$AC9/run_count.txt"
ls -la "$RUNS_DIR/" >> "$AC9/run_count.txt"
# Expected: >= 1

# ── Gate A9.2: The run has a gates.md file with results ──
GATES_FILE="$LATEST_PATH/EVIDENCE/gates.md"
if [ -f "$GATES_FILE" ]; then
  cat "$GATES_FILE" | tee "$AC9/gates_results.txt"
else
  echo "MISSING: gates.md" | tee "$AC9/gates_results.txt"
fi
# Expected: file exists with gate results

# ── Gate A9.3: All non-skipped gates PASS ──
FAIL_COUNT=$(grep -c "FAIL" "$GATES_FILE" 2>/dev/null) || FAIL_COUNT=0
echo "FAIL_COUNT=$FAIL_COUNT" | tee "$AC9/gate_failures.txt"
# Expected: 0

# ── Gate A9.4: MASTER_LOG.md records the full pipeline lifecycle ──
grep -c "PIPELINE START\|PASS.*START\|PASS.*COMPLETE\|PIPELINE COMPLETE" "$LATEST_PATH/MASTER_LOG.md" | tee "$AC9/lifecycle_events.txt"
# Expected: >= 6 (start + 3 passes + end = at least 6 events)

# ── Gate A9.5: Run ID follows naming convention (TP-YYYYMMDD-HHMMSS) ──
LATEST_ID=$(basename "$LATEST_PATH")
echo "RUN_ID=$LATEST_ID" | tee "$AC9/run_id_format.txt"
if [[ "$LATEST_ID" =~ ^TP-[0-9]{8}-[0-9]{6}$ ]]; then
  echo "FORMAT=VALID"
else
  echo "FORMAT=INVALID"
fi >> "$AC9/run_id_format.txt"
# Expected: FORMAT=VALID

# ── Gate A9.6: Run directory is self-contained (has everything needed) ──
EXPECTED_FILES=(
  "00_context/mission.md"
  "00_context/cli_discovery.md"
  "01_pass1/claude_report.md"
  "01_pass1/gemini_report.md"
  "01_pass1/codex_report.md"
  "02_pass2/claude_review.md"
  "02_pass2/gemini_review.md"
  "02_pass2/codex_review.md"
  "EVIDENCE/append_only_log.txt"
  "EVIDENCE/gates.md"
  "WORKSPACE.md"
  "MASTER_LOG.md"
  "FINAL_MASTER.md"
)
FOUND=0
MISSING=0
for f in "${EXPECTED_FILES[@]}"; do
  if [ -f "$LATEST_PATH/$f" ]; then
    echo "FOUND: $f"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: $f"
    MISSING=$((MISSING + 1))
  fi
done | tee "$AC9/self_contained_check.txt"
echo "FOUND=$FOUND MISSING=$MISSING" >> "$AC9/self_contained_check.txt"
# Expected: FOUND=13 MISSING=0
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| A9.1 | At least 1 completed run exists | >= 1 | |
| A9.2 | Gates file exists with results | present | |
| A9.3 | All non-skipped gates PASS | FAIL_COUNT=0 | |
| A9.4 | MASTER_LOG records full lifecycle | >= 6 events | |
| A9.5 | Run ID follows TP-YYYYMMDD-HHMMSS convention | FORMAT=VALID | |
| A9.6 | Run directory is self-contained (13 required files) | FOUND=13 MISSING=0 | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STRESS TESTS
# Edge cases the mission didn't exercise
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
STRESS="$QA_ROOT/evidence/stress-tests"

# ── ST-1: Lock file cleanup ──
# If tripass.sh crashes mid-run, does the lock file get cleaned up?
grep -n "trap\|cleanup\|release_lock\|LOCK\|lock" "$TRIPASS_TOOL" | tee "$STRESS/lock_cleanup.txt"
# VERIFY: script has a trap handler that releases lock on EXIT/ERR/INT
# If no trap: ENHANCEMENT OPPORTUNITY

# ── ST-2: CRLF safety ──
# The script runs in WSL. Does it have CRLF line endings?
file "$TRIPASS_TOOL" | tee "$STRESS/crlf_check.txt"
xxd "$TRIPASS_TOOL" | grep "0d0a" | head -3 >> "$STRESS/crlf_check.txt"
# Expected: no \r\n (CRLF) — only \n (LF)

# ── ST-3: Template rendering handles missing variables ──
# Does render_template() fail gracefully when a {{VARIABLE}} has no value?
grep -A15 "render_template" "$TRIPASS_TOOL" | head -20 | tee "$STRESS/template_rendering.txt"
# VERIFY: unreplaced {{VAR}} either causes error or is handled
# If no validation: ENHANCEMENT OPPORTUNITY

# ── ST-4: Concurrent run prevention ──
# Can two runs execute simultaneously?
grep -n "acquire_lock\|release_lock\|LOCKFILE\|flock" "$TRIPASS_TOOL" | tee "$STRESS/concurrency_check.txt"
# Expected: lock mechanism prevents concurrent runs

# ── ST-5: Gate T-3 behavior on placeholder content ──
# Does Gate T-3 (structural validity) pass on placeholder FINAL_MASTER.md?
# This tests if the gate is too lenient
grep -c "Root Cause\|Fix Approach\|Industry Standard\|System Fit\|Enforcement" "$LATEST_PATH/FINAL_MASTER.md" | tee "$STRESS/t3_on_placeholder.txt"
# If returns 0 but gate passed: gate may be too lenient on generate-only
# DOCUMENT as enhancement opportunity

# ── ST-6: stop.sh awareness of active runs ──
grep -n "tripass\|TRIPASS\|tripass.lock" "$HOOKS_DIR/stop.sh" | tee "$STRESS/stop_hook_awareness.txt"
# Expected: stop.sh detects active runs via lock file

# ── ST-7: Ownership of created files ──
ls -la "$TRIPASS_TOOL" "$TEMPLATES_DIR/"*.md "$SOP_PATH" "$LATEST_RUN" 2>/dev/null | tee "$STRESS/file_ownership.txt"
# VERIFY: files under /home/zaks/ owned by zaks:zaks (not root)
```

### Stress Test Results

| # | Test | What it checks | Verdict |
|---|------|----------------|---------|
| ST-1 | Lock file cleanup | trap handler releases lock on crash | |
| ST-2 | CRLF safety | no Windows line endings in script | |
| ST-3 | Template variable validation | missing vars handled | |
| ST-4 | Concurrent run prevention | lock mechanism exists | |
| ST-5 | Gate T-3 leniency on placeholders | gate strictness check | |
| ST-6 | stop.sh TriPass awareness | active run detection | |
| ST-7 | File ownership | correct user:group | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CROSS-CONSISTENCY VERIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
CROSS="$QA_ROOT/evidence/cross-consistency"

# ── XC-1: MEMORY.md TriPass section matches actual Makefile targets ──
MEMORY_TARGETS=$(grep -oP "tripass-\w+" "$MEMORY_ACTIVE" | sort -u)
MAKE_TARGETS=$(grep -oP "^tripass-\w+" "$MAKEFILE" | sort -u)
echo "MEMORY: $MEMORY_TARGETS" | tee "$CROSS/target_parity.txt"
echo "MAKEFILE: $MAKE_TARGETS" >> "$CROSS/target_parity.txt"
# Expected: same set of targets

# ── XC-2: LATEST_RUN.md pointer matches most recent run directory ──
POINTER_ID=$(grep -oP 'TP-\d{8}-\d{6}' "$LATEST_RUN" | head -1)
NEWEST_DIR=$(ls -1 "$RUNS_DIR" | sort | tail -1)
echo "POINTER=$POINTER_ID NEWEST=$NEWEST_DIR" | tee "$CROSS/pointer_matches_newest.txt"
if [ "$POINTER_ID" = "$NEWEST_DIR" ]; then echo "MATCH=true"; else echo "MATCH=false"; fi >> "$CROSS/pointer_matches_newest.txt"
# Expected: MATCH=true

# ── XC-3: Template count matches pipeline expectations ──
TEMPLATE_COUNT=$(ls -1 "$TEMPLATES_DIR"/*.md 2>/dev/null | wc -l)
echo "TEMPLATE_COUNT=$TEMPLATE_COUNT" | tee "$CROSS/template_count.txt"
# Expected: 4 (pass1, pass2, pass3, pass4_metaqa)

# ── XC-4: CHANGES.md entry count (no duplicates) ──
TRIPASS_ENTRIES=$(grep -c -i "tripass.*run\|TP-" "$CHANGES_MD" 2>/dev/null) || TRIPASS_ENTRIES=0
echo "CHANGES_ENTRIES=$TRIPASS_ENTRIES" | tee "$CROSS/changes_entry_count.txt"
# NOTE: if > number_of_runs, there may be duplicates (gate T-6 ran twice?)
# DOCUMENT as enhancement opportunity if duplicates found

# ── XC-5: Script version matches what SOP references ──
SCRIPT_VERSION=$(grep -oP 'VERSION="[^"]*"' "$TRIPASS_TOOL" | head -1)
echo "SCRIPT: $SCRIPT_VERSION" | tee "$CROSS/version_check.txt"
grep -n "version\|1\.0" "$SOP_PATH" | head -3 >> "$CROSS/version_check.txt"
# Expected: version referenced consistently
```

### Cross-Consistency Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| XC-1 | MEMORY.md targets match Makefile targets | same set | |
| XC-2 | LATEST_RUN pointer matches newest directory | MATCH=true | |
| XC-3 | Template count is exactly 4 | 4 | |
| XC-4 | CHANGES.md entries match run count (no dupes) | entries == runs | |
| XC-5 | Script version consistent across docs | consistent | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENHANCEMENT OPPORTUNITY DETECTION
# Everything below is ADVISORY — not gates, not blocking
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
ENH="$QA_ROOT/evidence/enhancements"

# Collect data for each potential enhancement
# These are NOT pass/fail — they are observations for operator review

# ── ENH-1: Gate T-3 strictness on generate-only runs ──
# Does Gate T-3 (structural validity) distinguish between real findings
# and placeholder content? If it passes on "This is a placeholder", it
# cannot catch structural issues in real runs.
echo "=== ENH-1: Gate T-3 strictness ===" | tee "$ENH/enh_report.md"
PLACEHOLDER_FIELDS=$(grep -c "Root Cause\|Fix Approach\|Industry Standard\|System Fit\|Enforcement" "$LATEST_PATH/FINAL_MASTER.md" 2>/dev/null) || PLACEHOLDER_FIELDS=0
echo "Required fields found in FINAL_MASTER.md: $PLACEHOLDER_FIELDS" >> "$ENH/enh_report.md"
T3_RESULT=$(grep "T-3" "$LATEST_PATH/EVIDENCE/gates.md" 2>/dev/null)
echo "T-3 gate result: $T3_RESULT" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-2: Duplicate CHANGES.md entries ──
echo "=== ENH-2: CHANGES.md duplicate entries ===" >> "$ENH/enh_report.md"
grep -n -i "tripass" "$CHANGES_MD" | head -10 >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-3: Lock file trap handler ──
echo "=== ENH-3: Lock file cleanup on crash ===" >> "$ENH/enh_report.md"
grep -n "trap " "$TRIPASS_TOOL" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-4: Template variable validation ──
echo "=== ENH-4: Unreplaced template variables ===" >> "$ENH/enh_report.md"
# Check if any prompt file in the run still has {{UNREPLACED}} variables
UNREPLACED=0
for f in "$LATEST_PATH"/0{1,2,3}_*/*.md; do
  COUNT=$(grep -c '{{' "$f" 2>/dev/null) || COUNT=0
  if [ "$COUNT" -gt 0 ]; then
    echo "UNREPLACED in $(basename $f): $COUNT variables" >> "$ENH/enh_report.md"
    UNREPLACED=$((UNREPLACED + COUNT))
  fi
done
echo "TOTAL_UNREPLACED=$UNREPLACED" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-5: No --dry-run mode ──
echo "=== ENH-5: Dry-run mode availability ===" >> "$ENH/enh_report.md"
DRY_RUN=$(grep -c "dry.run\|dry_run\|\-\-dry" "$TRIPASS_TOOL" 2>/dev/null) || DRY_RUN=0
echo "Dry-run references in script: $DRY_RUN" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-6: Agent timeout configurability ──
echo "=== ENH-6: Timeout configurability ===" >> "$ENH/enh_report.md"
grep -n "timeout\|TIMEOUT\|900" "$TRIPASS_TOOL" | head -10 >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-7: Hash continuity verification in T-1 ──
echo "=== ENH-7: Hash continuity (not just size) ===" >> "$ENH/enh_report.md"
# T-1 checks size monotonicity. Does it also verify hash continuity?
grep -A30 "verify_append_only\|gate_t1" "$TRIPASS_TOOL" | grep -i "hash\|sha256" | head -5 >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-8: MEMORY.md TriPass gate documentation ──
echo "=== ENH-8: Gates documented in MEMORY.md ===" >> "$ENH/enh_report.md"
grep -c "T-1\|T-2\|T-3\|T-4\|T-5\|T-6" "$MEMORY_ACTIVE" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-9: File ownership audit ──
echo "=== ENH-9: File ownership ===" >> "$ENH/enh_report.md"
ls -la "$TRIPASS_TOOL" >> "$ENH/enh_report.md"
ls -la "$TEMPLATES_DIR/"*.md >> "$ENH/enh_report.md" 2>/dev/null
ls -la "$SOP_PATH" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-10: Real autonomous execution test ──
echo "=== ENH-10: Autonomous execution evidence ===" >> "$ENH/enh_report.md"
grep -c "Generate-Only\|placeholder\|generate-only" "$LATEST_PATH/FINAL_MASTER.md" >> "$ENH/enh_report.md"
echo "NOTE: If proof-of-life is generate-only, autonomous execution is untested" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-11: Error reporting granularity ──
echo "=== ENH-11: Error message quality ===" >> "$ENH/enh_report.md"
grep -c "log_err\|log_warn" "$TRIPASS_TOOL" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"

# ── ENH-12: WORKSPACE.md section separators ──
echo "=== ENH-12: Workspace readability ===" >> "$ENH/enh_report.md"
grep -c "^---" "$LATEST_PATH/WORKSPACE.md" >> "$ENH/enh_report.md"
echo "" >> "$ENH/enh_report.md"
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUTION ORDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
PRE-FLIGHT ━━━━ validate-local baseline, create evidence dirs
    ↓
AC-1 ━━━━━━━━━ Pipeline structure (foundation — others depend on this)
    ↓
┌─────────────────────────────────────────────────┐
│ PARALLEL BLOCK (independent of each other):      │
│   AC-2  Autonomous execution                     │
│   AC-3  Graceful degradation                     │
│   AC-7  Makefile integration                     │
│   AC-8  Documentation                            │
└─────────────────────────────────────────────────┘
    ↓
AC-4 ━━━━━━━━━ Append-only proof (needs run data from AC-1)
    ↓
AC-5 ━━━━━━━━━ Deliverable quality (needs run data)
    ↓
AC-9 ━━━━━━━━━ Proof of life (comprehensive — needs AC-4, AC-5)
    ↓
AC-6 ━━━━━━━━━ Memory integration (run after proof-of-life verified)
    ↓
STRESS TESTS ━━ ST-1 through ST-7 (after all ACs verified)
    ↓
CROSS-CONSISTENCY ━━ XC-1 through XC-5
    ↓
ENHANCEMENT DETECTION ━━ ENH-1 through ENH-12
    ↓
FINAL VERIFICATION ━━ Scorecard + regression + enhancement report
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FINAL VERIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
FINAL="$QA_ROOT/evidence/FINAL"

# ── Regression: make validate-local still passes ──
cd "$MONOREPO"
make validate-local 2>&1 | tee "$QA_ROOT/evidence/regression/validate-local-final.log"
echo "EXIT_CODE=$?" >> "$QA_ROOT/evidence/regression/validate-local-final.log"

# ── Scorecard ──
cat <<'SCORECARD' | tee "$FINAL/final_report.txt"
╔══════════════════════════════════════════════════════════════╗
║          QA-TP-VERIFY-001 — FINAL SCORECARD                  ║
╚══════════════════════════════════════════════════════════════╝

SECTION        | GATES | PASS | FAIL | STATUS
---------------|-------|------|------|-------
AC-1 Structure |  7    |      |      |
AC-2 Autonomous|  7    |      |      |
AC-3 Degradation| 7    |      |      |
AC-4 Append-Only| 7    |      |      |
AC-5 Quality   |  6    |      |      |
AC-6 Memory    |  7    |      |      |
AC-7 Makefile  |  8    |      |      |
AC-8 Docs      |  8    |      |      |
AC-9 Proof     |  6    |      |      |
Stress Tests   |  7    |      |      |
Cross-Consist  |  5    |      |      |
---------------|-------|------|------|-------
SUBTOTAL       |  75   |      |      |

DEFERRALS: 0
REMEDIATIONS: [count]

VERDICT: [PASS / FAIL]
SCORECARD

echo "" >> "$FINAL/final_report.txt"
echo "REGRESSION: validate-local exit code = $(tail -1 "$QA_ROOT/evidence/regression/validate-local-final.log")" >> "$FINAL/final_report.txt"
echo "TIMESTAMP: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$FINAL/final_report.txt"

# ── Enhancement Report ──
cat <<'ENH_HEADER' >> "$FINAL/final_report.txt"

══════════════════════════════════════════════════════
 ENHANCEMENT OPPORTUNITIES (Advisory — Operator Review)
══════════════════════════════════════════════════════

ENH_HEADER

cat <<'ENH_TABLE' >> "$FINAL/final_report.txt"
| # | Enhancement | Severity | What It Improves | Implementation | Risk If Skipped |
|---|-------------|----------|------------------|----------------|-----------------|
| ENH-1 | Gate T-3 should skip or warn on generate-only runs | MEDIUM | Gate accuracy | Add a generate-only check in gate_t3; return SKIP instead of PASS when content is placeholder | False confidence in structural validity |
| ENH-2 | Gate T-6 idempotency — prevent duplicate CHANGES.md entries | MEDIUM | Data hygiene | Check if entry already exists before prepending; use run ID as dedup key | Duplicate bookkeeping entries accumulate |
| ENH-3 | Trap handler for lock file cleanup on crash | HIGH | Crash recovery | Add `trap 'release_lock; exit 1' EXIT ERR INT TERM` after lock acquisition | Stale lock blocks all future runs until manually deleted |
| ENH-4 | Template variable validation — warn on unreplaced {{VAR}} | LOW | Prompt quality | After render_template, grep for remaining {{ and warn/fail if found | Agents receive malformed prompts with literal {{VAR}} |
| ENH-5 | Add --dry-run mode to preview pipeline without executing | LOW | Operator confidence | New cmd_dryrun() that creates directory structure and renders prompts but skips agent execution and gates | Operators must commit to a full run to verify setup |
| ENH-6 | Make agent timeout configurable via --timeout flag | LOW | Flexibility | Add TIMEOUT env var or --timeout flag; default 900s | Long-running missions may hit timeout with no recourse except code edit |
| ENH-7 | Gate T-1 should verify hash continuity, not just size | MEDIUM | Integrity proof | After size check, verify that BEFORE hash of step N matches AFTER hash of step N-1 | Append-only proof incomplete — content could change while maintaining size |
| ENH-8 | MEMORY.md should document the 6 TriPass gates | LOW | Future session context | Add T-1 through T-6 names to TriPass section in MEMORY.md | Future sessions lack gate reference without reading SOP |
| ENH-9 | Fix file ownership on created files (WSL hazard) | MEDIUM | User operability | Add chown zaks:zaks to script or Makefile targets | User gets EACCES when running make targets directly |
| ENH-10 | Run a real autonomous execution as proof-of-life | HIGH | Confidence | Execute a real (non-generate-only) run with at least Claude CLI | Autonomous execution path is completely untested |
| ENH-11 | Structured error codes for pipeline failures | LOW | Debuggability | Define exit codes: 1=gate fail, 2=CLI error, 3=lock error, 4=template error | All failures return generic exit 1 |
| ENH-12 | Add run summary to WORKSPACE.md at end | LOW | Readability | Append a statistics block (total findings, duplicates, unique, drift count) | Workspace ends abruptly without summary |
ENH_TABLE

echo "" >> "$FINAL/final_report.txt"
echo "TOTAL ENHANCEMENTS: 12" >> "$FINAL/final_report.txt"
echo "HIGH: 2 (ENH-3, ENH-10)" >> "$FINAL/final_report.txt"
echo "MEDIUM: 3 (ENH-1, ENH-2, ENH-7, ENH-9)" >> "$FINAL/final_report.txt"
echo "LOW: 6 (ENH-4, ENH-5, ENH-6, ENH-8, ENH-11, ENH-12)" >> "$FINAL/final_report.txt"
echo "" >> "$FINAL/final_report.txt"
echo "OPERATOR ACTION: Review enhancements. Apply any deemed valuable." >> "$FINAL/final_report.txt"
echo "Applied enhancements must be re-verified before closing." >> "$FINAL/final_report.txt"
```

---

## REMEDIATION PROTOCOL

If any verification gate FAILS:

1. **Identify the root cause** — read the evidence file
2. **Fix the specific issue** — modify the appropriate file (tripass.sh, templates, SOP, Makefile, hooks, MEMORY.md)
3. **Re-run ONLY the affected verification section**
4. **Update the scorecard**
5. **Capture remediation evidence**

If any enhancement is APPLIED by operator decision:

1. **Implement the enhancement**
2. **Re-run the related verification gates** to confirm no regression
3. **Add the enhancement to the scorecard** as an applied enhancement
4. **Update MEMORY.md** if the enhancement changes documented facts

```
REMEDIATION GUARDRAILS:
  - Do NOT modify application code (.ts, .py, .tsx, .css)
  - Do NOT modify settings.json permissions
  - Do NOT modify existing hooks behavior (extending is OK)
  - DO fix: tripass.sh, templates, SOP, Makefile targets, MEMORY.md
  - EVERY remediation must be re-verified with the same gate commands
  - EVERY applied enhancement must be re-verified
```

---

## PIPELINE MASTER LOG ENTRY

Upon completion, append to `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_PIPELINE_MASTER_LOG.md`:

```
[TIMESTAMP] | QA-TP-VERIFY-001 COMPLETE | Agent=Claude Opus 4.6 | RunID=QA-TP-VERIFY-001 | STATUS=[PASS/FAIL] | 9 ACs verified | [N]/75 gates PASS | [N] remediations | [N] enhancements reported ([N] applied) | Report=/home/zaks/bookkeeping/qa-verifications/QA-TP-VERIFY-001/evidence/FINAL/final_report.txt
```

---

## STOP CONDITION

Stop when:
1. All 75 verification gates are evaluated
2. All FAILed gates have been remediated and re-verified to PASS
3. Stress tests (ST-1 through ST-7) all evaluated
4. Cross-consistency gates (XC-1 through XC-5) all PASS
5. Enhancement report generated with all 12 opportunities assessed
6. `make validate-local` passes (final regression check)
7. Scorecard is complete with VERDICT
8. Pipeline master log entry appended

Do NOT apply enhancements without operator approval. Report them and wait.

---

*End of QA Mission Prompt — QA-TP-VERIFY-001*

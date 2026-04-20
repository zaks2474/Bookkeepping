# QA VERIFICATION & REMEDIATION — CONFIG-STABILIZE-001
## Codename: `QA-CS-VERIFY-001`
## Version: V1 | Date: 2026-02-09
## Executor: Claude Code (Opus 4.6)
## Authority: FULL EXECUTION — Verify everything, fix what fails, defer nothing
## Predecessor: CONFIG-STABILIZE-001 (14 findings, 8 gates, completed 2026-02-09)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   QA DIRECTIVE: TRUST NOTHING. VERIFY EVERYTHING.                            ║
║                                                                              ║
║   CONFIG-STABILIZE-001 claimed to remediate 14 findings across              ║
║   configuration, memory, rules, and documentation.                           ║
║                                                                              ║
║   This QA mission does not take the executor's word for it.                  ║
║   Every claimed fix is re-verified from raw filesystem state.                ║
║   Every gate is checked with concrete commands, not assertions.              ║
║   Every cross-reference is followed to both endpoints.                       ║
║                                                                              ║
║   SCOPE: 14 findings → 62 verification gates. Zero deferrals.               ║
║   APPROACH: Read the actual files. Count the actual lines. Match             ║
║   the actual strings. If reality disagrees with the claim, FAIL.             ║
║                                                                              ║
║   THE EXECUTOR KNOWS THIS ENVIRONMENT INTIMATELY.                            ║
║   THAT KNOWLEDGE IS WEAPONIZED INTO EXACT-MATCH GATES.                       ║
║   APPROXIMATE FIXES WILL NOT PASS.                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## VERDICT RULES

```
PASS or FAIL. Nothing else. Zero deferrals. Zero "close enough."
Every verification must:
  1. Be checked against the ACTUAL FILE (not cached knowledge or claims)
  2. Match the EXACT expected value (not approximately correct)
  3. Be evidenced (command output captured to evidence directory)
  4. Cross-check at BOTH endpoints (if guide says X, file must say X; if file says Y, guide must say Y)
  5. Pass regression — no existing correct configuration was broken

A single FAIL gate means the finding is NOT remediated.
All FAIL findings must be fixed in-session before the mission can close.
```

---

## EVIDENCE STRUCTURE

```
/home/zaks/bookkeeping/qa-verifications/QA-CS-VERIFY-001/
├── evidence/
│   ├── VF-01-deny-allow-rules/
│   ├── VF-02-port-5435-eradication/
│   ├── VF-03-slash-commands/
│   ├── VF-04-surface-8/
│   ├── VF-05-claude-md-split/
│   ├── VF-06-mcp-servers/
│   ├── VF-07-hooks/
│   ├── VF-08-deal-integrity-memory/
│   ├── VF-09-memory-path-resolution/
│   ├── VF-10-makefile-target/
│   ├── VF-11-skills-vs-commands/
│   ├── VF-12-agent-file-location/
│   ├── VF-13-memory-sync-dryrun/
│   ├── VF-14-guide-deduplication/
│   ├── cross-consistency/
│   ├── regression/
│   └── FINAL/
│       └── final_report.txt
└── completion-report.md
```

---

## PRE-FLIGHT: ESTABLISH BASELINE

Before verifying anything, confirm the environment is healthy and set up evidence capture.

```bash
# ═══════════════════════════════════════════════════════════
# PRE-FLIGHT: Paths, directories, baseline
# ═══════════════════════════════════════════════════════════

MONOREPO="/home/zaks/zakops-agent-api"
QA_ROOT="/home/zaks/bookkeeping/qa-verifications/QA-CS-VERIFY-001"
GUIDE_PATH="/home/zaks/bookkeeping/docs/ClaudeCode_Setup_ZakOps_V5PP_Guide.md"
MEMORY_ACTIVE="/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md"
MEMORY_LEGACY="/root/.claude/projects/-home-zaks/memory/MEMORY.md"
SETTINGS_USER="/home/zaks/.claude/settings.json"
SETTINGS_SYSTEM="/root/.claude/settings.json"
SURFACES_RULE="$MONOREPO/.claude/rules/contract-surfaces.md"
HOOKS_DIR="/home/zaks/.claude/hooks"
COMMANDS_DIR="$MONOREPO/.claude/commands"
CLAUDE_MD_ROOT="/home/zaks/CLAUDE.md"
CLAUDE_MD_MONO="$MONOREPO/CLAUDE.md"
MAKEFILE="$MONOREPO/Makefile"

# Create evidence directories
mkdir -p "$QA_ROOT/evidence"/{VF-01-deny-allow-rules,VF-02-port-5435-eradication,VF-03-slash-commands,VF-04-surface-8,VF-05-claude-md-split,VF-06-mcp-servers,VF-07-hooks,VF-08-deal-integrity-memory,VF-09-memory-path-resolution,VF-10-makefile-target,VF-11-skills-vs-commands,VF-12-agent-file-location,VF-13-memory-sync-dryrun,VF-14-guide-deduplication,cross-consistency,regression,FINAL}

# Baseline validation
cd "$MONOREPO"
make validate-local 2>&1 | tee "$QA_ROOT/evidence/regression/validate-local-pre.log"
echo "EXIT_CODE=$?" >> "$QA_ROOT/evidence/regression/validate-local-pre.log"
# ── STOP IF EXIT CODE != 0 ──
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-01: DENY/ALLOW RULE COUNTS & CONTENT
# Original Finding: 1 (CRITICAL) — Gate B-1
# Claim: Guide updated to reflect 12 deny, 4 allow with actual rule list
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

The guide claimed 6 deny / 3 allow when the actual settings.json had 12 deny / 4 allow. The rule list was incomplete.

## What CONFIG-STABILIZE-001 should have fixed

Updated the V5PP-DMS guide to reflect the exact 12 deny rules (4 Edit generated + 4 Edit .env + 4 Write generated) and 4 allow rules (sync-*, validate-*, infra-*, update-*).

## Verification

```bash
VF01="$QA_ROOT/evidence/VF-01-deny-allow-rules"

# ── Gate V1.1: Extract ACTUAL deny rules from settings.json ──
python3 -c "
import json
with open('$SETTINGS_USER') as f:
    data = json.load(f)
deny = data.get('permissions', {}).get('deny', [])
allow = data.get('permissions', {}).get('allow', [])
print(f'DENY_COUNT={len(deny)}')
for r in deny:
    print(f'  DENY: {r}')
print(f'ALLOW_COUNT={len(allow)}')
for r in allow:
    print(f'  ALLOW: {r}')
" | tee "$VF01/settings_actual_rules.txt"
# Expected: DENY_COUNT=12, ALLOW_COUNT=4

# ── Gate V1.2: Count deny rules mentioned in guide ──
grep -c -i "deny" "$GUIDE_PATH" | tee "$VF01/guide_deny_mentions.txt"
# Context: verify guide has a deny rules section

# ── Gate V1.3: Verify guide contains the EXACT string "12 deny" ──
grep -n "12 deny" "$GUIDE_PATH" | tee "$VF01/guide_12_deny.txt"
# Expected: at least 1 match

# ── Gate V1.4: Verify guide contains the EXACT string "4 allow" ──
grep -n "4 allow" "$GUIDE_PATH" | tee "$VF01/guide_4_allow.txt"
# Expected: at least 1 match

# ── Gate V1.5: Verify guide lists ALL 12 specific deny rules ──
# Each of these EXACT strings must appear in the guide:
DENY_RULES=(
  "Edit(*/api-types.generated.ts)"
  "Edit(*/agent-api-types.generated.ts)"
  "Edit(*/backend_models.py)"
  "Edit(*/rag_models.py)"
  "Edit(.env)"
  "Edit(.env.*)"
  "Edit(*/.env)"
  "Edit(*/.env.*)"
  "Write(*/api-types.generated.ts)"
  "Write(*/agent-api-types.generated.ts)"
  "Write(*/backend_models.py)"
  "Write(*/rag_models.py)"
)
FOUND=0
MISSING=0
for rule in "${DENY_RULES[@]}"; do
  if grep -qF "$rule" "$GUIDE_PATH"; then
    echo "FOUND: $rule"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: $rule"
    MISSING=$((MISSING + 1))
  fi
done | tee "$VF01/guide_deny_rule_audit.txt"
echo "FOUND=$FOUND MISSING=$MISSING" >> "$VF01/guide_deny_rule_audit.txt"
# Expected: FOUND=12 MISSING=0

# ── Gate V1.6: Verify guide lists ALL 4 specific allow rules ──
ALLOW_RULES=(
  "Bash(make sync-*)"
  "Bash(make validate-*)"
  "Bash(make infra-*)"
  "Bash(make update-*)"
)
FOUND=0
MISSING=0
for rule in "${ALLOW_RULES[@]}"; do
  if grep -qF "$rule" "$GUIDE_PATH"; then
    echo "FOUND: $rule"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: $rule"
    MISSING=$((MISSING + 1))
  fi
done | tee "$VF01/guide_allow_rule_audit.txt"
echo "FOUND=$FOUND MISSING=$MISSING" >> "$VF01/guide_allow_rule_audit.txt"
# Expected: FOUND=4 MISSING=0

# ── Gate V1.7: Cross-check — MEMORY.md sentinel matches actual count ──
grep "AUTOSYNC:deny_rules" "$MEMORY_ACTIVE" | tee "$VF01/memory_deny_sentinel.txt"
# Expected: contains "12 deny rules"
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V1.1 | settings.json deny count | DENY_COUNT=12 | |
| V1.2 | settings.json allow count | ALLOW_COUNT=4 | |
| V1.3 | Guide contains "12 deny" | >= 1 match | |
| V1.4 | Guide contains "4 allow" | >= 1 match | |
| V1.5 | Guide lists all 12 specific deny rules verbatim | FOUND=12 MISSING=0 | |
| V1.6 | Guide lists all 4 specific allow rules verbatim | FOUND=4 MISSING=0 | |
| V1.7 | MEMORY.md AUTOSYNC:deny_rules sentinel says 12 | Contains "12 deny" | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-02: PORT 5435 TOTAL ERADICATION
# Original Finding: 2 (CRITICAL) — Gate G-2
# Claim: Port 5435 removed from guide, does not appear anywhere as valid
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Guide listed PostgreSQL on port 5435. That port was destroyed during Deal Integrity (rogue split-brain DB). All databases are on 5432.

## What CONFIG-STABILIZE-001 should have fixed

Eradicated port 5435 from the guide and all configuration/documentation files.

## Verification

```bash
VF02="$QA_ROOT/evidence/VF-02-port-5435-eradication"

# ── Gate V2.1: Guide does NOT contain "5435" as a valid port ──
# We search for 5435 in any context. Historical/narrative mentions
# (e.g., "port 5435 was destroyed") are acceptable.
# Active configuration references (e.g., "PostgreSQL | 5435") are FAIL.
grep -n "5435" "$GUIDE_PATH" | tee "$VF02/guide_5435_search.txt"
# Expected: ZERO matches, OR only historical/narrative references (manually verify)

# ── Gate V2.2: Guide contains port 5432 for PostgreSQL ──
grep -n "5432" "$GUIDE_PATH" | tee "$VF02/guide_5432_search.txt"
# Expected: at least 1 match showing PostgreSQL on 5432

# ── Gate V2.3: MEMORY.md does NOT contain 5435 as valid ──
grep -n "5435" "$MEMORY_ACTIVE" | tee "$VF02/memory_5435_search.txt"
# Expected: ZERO matches or only historical reference

# ── Gate V2.4: Monorepo CLAUDE.md does NOT contain 5435 ──
grep -n "5435" "$CLAUDE_MD_MONO" | tee "$VF02/claude_md_mono_5435.txt"
# Expected: ZERO matches

# ── Gate V2.5: Root CLAUDE.md does NOT contain 5435 ──
grep -n "5435" "$CLAUDE_MD_ROOT" | tee "$VF02/claude_md_root_5435.txt"
# Expected: ZERO matches

# ── Gate V2.6: No .claude/rules/ file contains 5435 ──
grep -rn "5435" "$MONOREPO/.claude/rules/" | tee "$VF02/rules_5435.txt"
# Expected: ZERO matches

# ── Gate V2.7: No .claude/commands/ file contains 5435 ──
grep -rn "5435" "$COMMANDS_DIR/" | tee "$VF02/commands_5435.txt"
# Expected: ZERO matches

# ── Gate V2.8: Guide references ADR-002 (Canonical Database) ──
grep -n "ADR-002" "$GUIDE_PATH" | tee "$VF02/guide_adr002_ref.txt"
# Expected: at least 1 match
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V2.1 | Guide: zero active 5435 references | 0 active config refs | |
| V2.2 | Guide: PostgreSQL shown on 5432 | >= 1 match | |
| V2.3 | MEMORY.md: no active 5435 | 0 active refs | |
| V2.4 | Monorepo CLAUDE.md: no 5435 | 0 matches | |
| V2.5 | Root CLAUDE.md: no 5435 | 0 matches | |
| V2.6 | .claude/rules/: no 5435 | 0 matches | |
| V2.7 | .claude/commands/: no 5435 | 0 matches | |
| V2.8 | Guide references ADR-002 | >= 1 match | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-03: SLASH COMMAND INVENTORY COMPLETENESS
# Original Finding: 3 (CRITICAL) — Gate A-3
# Claim: Guide updated with all 12 commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Guide listed 6 commands. Actual directory has 12.

## What CONFIG-STABILIZE-001 should have fixed

Guide now lists all 12 commands with filenames and purposes.

## Verification

```bash
VF03="$QA_ROOT/evidence/VF-03-slash-commands"

# ── Gate V3.1: Count actual command files ──
ls -1 "$COMMANDS_DIR/" | tee "$VF03/actual_commands.txt"
ACTUAL_COUNT=$(ls -1 "$COMMANDS_DIR/" | wc -l)
echo "ACTUAL_COMMAND_COUNT=$ACTUAL_COUNT" >> "$VF03/actual_commands.txt"
# Expected: 12

# ── Gate V3.2: Every command file is non-empty ──
for f in "$COMMANDS_DIR"/*.md; do
  SIZE=$(wc -c < "$f")
  NAME=$(basename "$f")
  echo "$NAME: $SIZE bytes"
done | tee "$VF03/command_sizes.txt"
# Expected: all > 0 bytes

# ── Gate V3.3: Guide mentions each command by name ──
# Extract basenames (without .md) and search for each in guide
FOUND=0
MISSING=0
for f in "$COMMANDS_DIR"/*.md; do
  NAME=$(basename "$f" .md)
  if grep -qi "$NAME" "$GUIDE_PATH"; then
    echo "FOUND: /$NAME"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: /$NAME"
    MISSING=$((MISSING + 1))
  fi
done | tee "$VF03/guide_command_audit.txt"
echo "FOUND=$FOUND MISSING=$MISSING" >> "$VF03/guide_command_audit.txt"
# Expected: FOUND=12 MISSING=0

# ── Gate V3.4: Guide explicitly states "12" for command count ──
grep -n "12.*command\|command.*12" "$GUIDE_PATH" | tee "$VF03/guide_12_commands.txt"
# Expected: at least 1 match

# ── Gate V3.5: No phantom commands in guide (guide doesn't list commands that don't exist) ──
# Extract command names from guide's commands section and verify each exists as a file
# This is a manual check — read the commands section and cross-reference
grep -A1 "validate\|sync-all\|sync-agent\|sync-backend\|contract-checker\|check-drift\|infra-check\|after-change\|hooks-check\|permissions-audit\|update-memory\|scaffold-feature" "$GUIDE_PATH" | head -30 | tee "$VF03/guide_commands_section_sample.txt"
# Expected: no command listed in guide that lacks a matching .md file
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V3.1 | Actual command file count | 12 | |
| V3.2 | All command files non-empty | all > 0 bytes | |
| V3.3 | Guide mentions every command by name | FOUND=12 MISSING=0 | |
| V3.4 | Guide states count is 12 | >= 1 match | |
| V3.5 | No phantom commands in guide | 0 phantoms | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-04: CONTRACT SURFACE 8 IN RULE FILE
# Original Finding: 4 (CRITICAL) — Gate A-2/D-4
# Claim: Surface 8 added to .claude/rules/contract-surfaces.md
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

`contract-surfaces.md` rule file only documented 7 surfaces. Surface 8 (Agent Configuration: deal_tools.py <-> system.md <-> tool-schemas.json) was missing.

## What CONFIG-STABILIZE-001 should have fixed

Added Surface 8 with boundary definition, validation gate reference, and sync protocol.

## Verification

```bash
VF04="$QA_ROOT/evidence/VF-04-surface-8"

# ── Gate V4.1: Rule file contains "Surface 8" or "8." header ──
grep -n -i "surface 8\|8\." "$SURFACES_RULE" | tee "$VF04/surface_8_header.txt"
# Expected: at least 1 match

# ── Gate V4.2: Rule file mentions deal_tools.py ──
grep -n "deal_tools.py" "$SURFACES_RULE" | tee "$VF04/deal_tools_ref.txt"
# Expected: at least 1 match

# ── Gate V4.3: Rule file mentions system.md (agent prompt) ──
grep -n "system.md" "$SURFACES_RULE" | tee "$VF04/system_md_ref.txt"
# Expected: at least 1 match

# ── Gate V4.4: Rule file mentions tool-schemas.json ──
grep -n "tool-schemas.json" "$SURFACES_RULE" | tee "$VF04/tool_schemas_ref.txt"
# Expected: at least 1 match

# ── Gate V4.5: Rule file mentions a validation gate for Surface 8 ──
grep -n -i "validate-agent-config\|gate.*[cC]\|validation" "$SURFACES_RULE" | tail -5 | tee "$VF04/validation_gate_ref.txt"
# Expected: at least 1 reference to a validation mechanism

# ── Gate V4.6: Surfaces 1-7 are STILL present (no regression) ──
for i in 1 2 3 4 5 6 7; do
  grep -c -i "surface $i\|${i}\." "$SURFACES_RULE" || echo "0"
done | tee "$VF04/surfaces_1_to_7_check.txt"
# Expected: all 7 return >= 1

# ── Gate V4.7: Total surface count in file ──
grep -c -i "^##.*surface\|^[0-9]\." "$SURFACES_RULE" | tee "$VF04/total_surface_count.txt"
# Expected: 8

# ── Gate V4.8: MEMORY.md sentinel for rule_count reflects 4 rules ──
grep "AUTOSYNC:rule_count" "$MEMORY_ACTIVE" | tee "$VF04/memory_rule_count.txt"
# Expected: contains "4 path-scoped rules"

# ── Gate V4.9: Guide also documents 8 surfaces ──
grep -n -i "8.*surface\|surface.*8\|agent configuration" "$GUIDE_PATH" | tee "$VF04/guide_surface_8.txt"
# Expected: at least 1 match
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V4.1 | Rule file has Surface 8 header | >= 1 match | |
| V4.2 | Rule file references deal_tools.py | >= 1 match | |
| V4.3 | Rule file references system.md | >= 1 match | |
| V4.4 | Rule file references tool-schemas.json | >= 1 match | |
| V4.5 | Rule file has validation gate for Surface 8 | >= 1 match | |
| V4.6 | Surfaces 1-7 still present (regression check) | all 7 present | |
| V4.7 | Total surface count in file | 8 | |
| V4.8 | MEMORY.md rule_count sentinel accurate | "4 path-scoped rules" | |
| V4.9 | Guide documents 8 surfaces | >= 1 match | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-05: CLAUDE.md SPLIT DOCUMENTATION
# Original Finding: 5 (MODERATE) — Gate A-1
# Claim: Guide documents the two-file split with purpose of each
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Guide assumed a single CLAUDE.md. Actually two: root (64 lines, operational) and monorepo (143 lines, full constitution).

## What CONFIG-STABILIZE-001 should have fixed

Guide now documents the split, clarifies which serves which purpose, and neither file contains stale references.

## Verification

```bash
VF05="$QA_ROOT/evidence/VF-05-claude-md-split"

# ── Gate V5.1: Both CLAUDE.md files exist ──
ls -la "$CLAUDE_MD_ROOT" "$CLAUDE_MD_MONO" | tee "$VF05/both_files_exist.txt"
# Expected: both files exist

# ── Gate V5.2: Root CLAUDE.md line count ──
wc -l "$CLAUDE_MD_ROOT" | tee "$VF05/root_line_count.txt"
# Expected: ~64 lines

# ── Gate V5.3: Monorepo CLAUDE.md line count ──
wc -l "$CLAUDE_MD_MONO" | tee "$VF05/mono_line_count.txt"
# Expected: ~143 lines (ceiling 150)

# ── Gate V5.4: Guide mentions BOTH file paths ──
grep -n "/home/zaks/CLAUDE.md\|zakops-agent-api/CLAUDE.md" "$GUIDE_PATH" | tee "$VF05/guide_both_paths.txt"
# Expected: at least 2 matches (one for each path)

# ── Gate V5.5: Guide explains the PURPOSE of each file ──
grep -B2 -A2 -i "root.*claude\|operational.*reference\|constitution\|monorepo.*claude" "$GUIDE_PATH" | head -20 | tee "$VF05/guide_purpose_explanation.txt"
# Expected: distinguishes the two files' roles

# ── Gate V5.6: Monorepo CLAUDE.md does not exceed 150-line ceiling ──
LINES=$(wc -l < "$CLAUDE_MD_MONO")
echo "LINES=$LINES CEILING=150" | tee "$VF05/ceiling_check.txt"
if [ "$LINES" -gt 150 ]; then echo "FAIL: EXCEEDS CEILING"; else echo "PASS: WITHIN CEILING"; fi >> "$VF05/ceiling_check.txt"
# Expected: PASS

# ── Gate V5.7: MEMORY.md sentinel for CLAUDE.md lines is accurate ──
grep "AUTOSYNC:claude_md_lines" "$MEMORY_ACTIVE" | tee "$VF05/memory_claude_sentinel.txt"
SENTINEL_LINES=$(grep "AUTOSYNC:claude_md_lines" "$MEMORY_ACTIVE" | grep -oP '\d+' | head -1)
echo "SENTINEL=$SENTINEL_LINES ACTUAL=$LINES" >> "$VF05/memory_claude_sentinel.txt"
# Expected: SENTINEL matches ACTUAL (both ~143)
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V5.1 | Both CLAUDE.md files exist | both present | |
| V5.2 | Root CLAUDE.md line count | ~64 | |
| V5.3 | Monorepo CLAUDE.md line count | ~143 (under 150) | |
| V5.4 | Guide mentions both file paths | >= 2 matches | |
| V5.5 | Guide explains purpose of each | distinguishes roles | |
| V5.6 | Monorepo CLAUDE.md under 150-line ceiling | PASS | |
| V5.7 | MEMORY.md AUTOSYNC:claude_md_lines accurate | sentinel == actual | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-06: MCP SERVER DOCUMENTATION
# Original Finding: 6 (MODERATE) — Gate F-1
# Claim: Guide documents all 4 MCP servers across 2 config tiers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Guide documented 2 MCP servers. Actual: 4 across user config (github, playwright) and system config (gmail, crawl4ai-rag).

## What CONFIG-STABILIZE-001 should have fixed

Guide now documents all 4 servers, their config tier, priority, status, and purpose. Two-tier model explained.

## Verification

```bash
VF06="$QA_ROOT/evidence/VF-06-mcp-servers"

# ── Gate V6.1: Extract ACTUAL MCP servers from user settings ──
python3 -c "
import json
with open('$SETTINGS_USER') as f:
    data = json.load(f)
servers = data.get('mcpServers', {})
for name, cfg in servers.items():
    status = 'DISABLED' if cfg.get('disabled') else 'ENABLED'
    print(f'USER: {name} [{status}]')
" | tee "$VF06/user_mcp_actual.txt"
# Expected: github [ENABLED], playwright [DISABLED]

# ── Gate V6.2: Extract ACTUAL MCP servers from system settings ──
python3 -c "
import json
with open('$SETTINGS_SYSTEM') as f:
    data = json.load(f)
servers = data.get('mcpServers', {})
for name, cfg in servers.items():
    status = 'DISABLED' if cfg.get('disabled') else 'ENABLED'
    print(f'SYSTEM: {name} [{status}]')
" | tee "$VF06/system_mcp_actual.txt"
# Expected: gmail [ENABLED], crawl4ai-rag [ENABLED]

# ── Gate V6.3: Guide mentions "github" MCP server ──
grep -n -i "github" "$GUIDE_PATH" | grep -i "mcp\|server\|enabled" | head -3 | tee "$VF06/guide_github.txt"
# Expected: at least 1 match

# ── Gate V6.4: Guide mentions "playwright" MCP server ──
grep -n -i "playwright" "$GUIDE_PATH" | grep -i "mcp\|server\|disabled" | head -3 | tee "$VF06/guide_playwright.txt"
# Expected: at least 1 match

# ── Gate V6.5: Guide mentions "gmail" MCP server ──
grep -n -i "gmail" "$GUIDE_PATH" | head -3 | tee "$VF06/guide_gmail.txt"
# Expected: at least 1 match

# ── Gate V6.6: Guide mentions "crawl4ai" MCP server ──
grep -n -i "crawl4ai" "$GUIDE_PATH" | head -3 | tee "$VF06/guide_crawl4ai.txt"
# Expected: at least 1 match

# ── Gate V6.7: Guide distinguishes user-level vs system-level config tiers ──
grep -n -i "user.*level\|system.*level\|user.*config\|system.*config\|two.*tier\|config.*tier" "$GUIDE_PATH" | head -5 | tee "$VF06/guide_two_tier.txt"
# Expected: at least 1 match explaining the two-tier model
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V6.1 | User settings: github + playwright | 2 servers | |
| V6.2 | System settings: gmail + crawl4ai-rag | 2 servers | |
| V6.3 | Guide documents github | >= 1 match | |
| V6.4 | Guide documents playwright | >= 1 match | |
| V6.5 | Guide documents gmail | >= 1 match | |
| V6.6 | Guide documents crawl4ai-rag | >= 1 match | |
| V6.7 | Guide explains two-tier config model | >= 1 match | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-07: HOOK DOCUMENTATION COMPLETENESS
# Original Finding: 7 (MODERATE) — Gate B-2
# Claim: Guide documents all 5 hooks with triggers, behavior, exit codes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Guide documented 2 hooks (pre-edit.sh, stop.sh) with 2 others mentioned in passing. Actual: 5 hooks, all executable, all registered.

## What CONFIG-STABILIZE-001 should have fixed

Guide now documents all 5 hooks with event triggers, behavior, and exit codes.

## Verification

```bash
VF07="$QA_ROOT/evidence/VF-07-hooks"

# ── Gate V7.1: Count actual hook files ──
ls -la "$HOOKS_DIR"/*.sh | tee "$VF07/actual_hooks.txt"
HOOK_COUNT=$(ls -1 "$HOOKS_DIR"/*.sh | wc -l)
echo "HOOK_COUNT=$HOOK_COUNT" >> "$VF07/actual_hooks.txt"
# Expected: 5

# ── Gate V7.2: All hooks are executable ──
NONEXEC=0
for f in "$HOOKS_DIR"/*.sh; do
  if [ -x "$f" ]; then
    echo "EXEC: $(basename $f)"
  else
    echo "NOT_EXEC: $(basename $f)"
    NONEXEC=$((NONEXEC + 1))
  fi
done | tee "$VF07/executable_check.txt"
echo "NON_EXECUTABLE=$NONEXEC" >> "$VF07/executable_check.txt"
# Expected: NON_EXECUTABLE=0

# ── Gate V7.3: All 5 hooks registered in settings.json ──
python3 -c "
import json
with open('$SETTINGS_USER') as f:
    data = json.load(f)
hooks = data.get('hooks', {})
scripts = set()
for event, handlers in hooks.items():
    for h in handlers:
        cmd = h.get('command', '')
        scripts.add(cmd.split('/')[-1] if '/' in cmd else cmd)
        print(f'{event}: {cmd}')
print(f'REGISTERED_SCRIPTS: {sorted(scripts)}')
" | tee "$VF07/settings_hook_registration.txt"
# Expected: all 5 scripts appear (pre-edit.sh, pre-bash.sh, post-edit.sh, stop.sh, memory-sync.sh)
# NOTE: memory-sync.sh may be called from within stop.sh rather than directly registered

# ── Gate V7.4: Guide mentions each hook by filename ──
HOOK_NAMES=("pre-edit.sh" "pre-bash.sh" "post-edit.sh" "stop.sh" "memory-sync.sh")
FOUND=0
MISSING=0
for hook in "${HOOK_NAMES[@]}"; do
  if grep -q "$hook" "$GUIDE_PATH"; then
    echo "FOUND: $hook"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: $hook"
    MISSING=$((MISSING + 1))
  fi
done | tee "$VF07/guide_hook_audit.txt"
echo "FOUND=$FOUND MISSING=$MISSING" >> "$VF07/guide_hook_audit.txt"
# Expected: FOUND=5 MISSING=0

# ── Gate V7.5: Guide states "5 hooks" or "5 total" ──
grep -n "5.*hook\|hook.*5" "$GUIDE_PATH" | head -5 | tee "$VF07/guide_5_hooks.txt"
# Expected: at least 1 match

# ── Gate V7.6: MEMORY.md AUTOSYNC:hook_count sentinel is accurate ──
grep "AUTOSYNC:hook_count" "$MEMORY_ACTIVE" | tee "$VF07/memory_hook_sentinel.txt"
# Expected: contains "5 scripts"

# ── Gate V7.7: Guide documents event triggers (PreToolUse, PostToolUse, Stop) ──
grep -n -i "PreToolUse\|PostToolUse\|Stop.*event\|event.*trigger" "$GUIDE_PATH" | head -5 | tee "$VF07/guide_event_triggers.txt"
# Expected: at least 1 match for each of the 3 event types
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V7.1 | Actual hook file count | 5 | |
| V7.2 | All hooks executable | NON_EXECUTABLE=0 | |
| V7.3 | All hooks registered in settings.json | 5 scripts referenced | |
| V7.4 | Guide mentions all 5 hooks by name | FOUND=5 MISSING=0 | |
| V7.5 | Guide states total count of 5 | >= 1 match | |
| V7.6 | MEMORY.md hook_count sentinel accurate | "5 scripts" | |
| V7.7 | Guide documents 3 event types | >= 1 per type | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-08: DEAL-INTEGRITY-UNIFIED-001 IN MEMORY
# Original Finding: 8 (MODERATE) — Gate C-1
# Claim: MEMORY.md records DEAL-INTEGRITY-UNIFIED-001 with 7 architectural patterns
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

MEMORY.md had no record of the Deal Integrity mission or its architectural patterns. Future sessions would lack critical knowledge.

## What CONFIG-STABILIZE-001 should have fixed

Added DEAL-INTEGRITY-UNIFIED-001 as a completed mission with all 7 mandatory architectural patterns.

## Verification

```bash
VF08="$QA_ROOT/evidence/VF-08-deal-integrity-memory"

# ── Gate V8.1: MEMORY.md mentions DEAL-INTEGRITY-UNIFIED-001 ──
grep -n "DEAL-INTEGRITY-UNIFIED-001\|DEAL-INTEGRITY-UNIFIED" "$MEMORY_ACTIVE" | tee "$VF08/mission_mention.txt"
# Expected: at least 1 match

# ── Gate V8.2: Pattern 1 — transition_deal_state() as choke point ──
grep -n "transition_deal_state" "$MEMORY_ACTIVE" | tee "$VF08/pattern_1_fsm.txt"
# Expected: at least 1 match

# ── Gate V8.3: Pattern 2 — Promise.allSettled mandatory / Promise.all banned ──
grep -n -i "Promise.allSettled\|Promise.all.*banned\|allSettled" "$MEMORY_ACTIVE" | tee "$VF08/pattern_2_allsettled.txt"
# Expected: at least 1 match

# ── Gate V8.4: Pattern 3 — Middleware proxies /api/* with JSON 502 ──
grep -n -i "middleware.*proxy\|JSON 502\|502" "$MEMORY_ACTIVE" | tee "$VF08/pattern_3_middleware.txt"
# Expected: at least 1 match

# ── Gate V8.5: Pattern 4 — PIPELINE_STAGES single source of truth ──
grep -n -i "PIPELINE_STAGES\|single source.*truth.*stage\|execution-contracts" "$MEMORY_ACTIVE" | tee "$VF08/pattern_4_stages.txt"
# Expected: at least 1 match

# ── Gate V8.6: Pattern 5 — Server-side deal counts only ──
grep -n -i "server-side.*count\|no client-side.*length\|server.*count" "$MEMORY_ACTIVE" | tee "$VF08/pattern_5_counts.txt"
# Expected: at least 1 match

# ── Gate V8.7: Pattern 6 — caret-color transparent ──
grep -n -i "caret-color\|caret.*transparent" "$MEMORY_ACTIVE" | tee "$VF08/pattern_6_caret.txt"
# Expected: at least 1 match

# ── Gate V8.8: Pattern 7 — 3 ADRs documented ──
grep -n "ADR-001\|ADR-002\|ADR-003" "$MEMORY_ACTIVE" | tee "$VF08/pattern_7_adrs.txt"
# Expected: all 3 ADRs mentioned (3 lines or combined)

# ── Gate V8.9: Existing missions NOT deleted (regression) ──
grep -n "RT-HARDEN-001\|HYBRID-GUARDRAIL\|QA-HG-VERIFY" "$MEMORY_ACTIVE" | tee "$VF08/existing_missions_preserved.txt"
# Expected: at least 3 matches (one per pre-existing mission)
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V8.1 | MEMORY.md mentions mission ID | >= 1 match | |
| V8.2 | Pattern: transition_deal_state() | >= 1 match | |
| V8.3 | Pattern: Promise.allSettled | >= 1 match | |
| V8.4 | Pattern: JSON 502 middleware | >= 1 match | |
| V8.5 | Pattern: PIPELINE_STAGES SSoT | >= 1 match | |
| V8.6 | Pattern: server-side counts | >= 1 match | |
| V8.7 | Pattern: caret-color transparent | >= 1 match | |
| V8.8 | Pattern: 3 ADRs | all 3 mentioned | |
| V8.9 | Pre-existing missions preserved | >= 3 matches | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-09: MEMORY PATH RESOLUTION
# Original Finding: 9 (MODERATE) — Gate C-1
# Claim: Single authoritative MEMORY.md path established, legacy reconciled
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Two MEMORY.md files: legacy at `-home-zaks` (22 lines, stale) and active at `-mnt-c-Users-mzsai` (100+ lines, current). Claude Code was loading the stale one.

## What CONFIG-STABILIZE-001 should have fixed

Reconciled the two files. The active copy's content is what Claude Code loads. A single authoritative path established.

## Verification

```bash
VF09="$QA_ROOT/evidence/VF-09-memory-path-resolution"

# ── Gate V9.1: Active MEMORY.md exists and is substantial ──
wc -l "$MEMORY_ACTIVE" | tee "$VF09/active_memory_lines.txt"
# Expected: > 100 lines

# ── Gate V9.2: Check legacy MEMORY.md state ──
if [ -f "$MEMORY_LEGACY" ]; then
  wc -l "$MEMORY_LEGACY" | tee "$VF09/legacy_memory_state.txt"
  echo "FILE_EXISTS=true" >> "$VF09/legacy_memory_state.txt"
else
  echo "FILE_EXISTS=false" | tee "$VF09/legacy_memory_state.txt"
fi
# Expected: either file doesn't exist, or it has been updated to match active

# ── Gate V9.3: If legacy exists, compare content with active ──
if [ -f "$MEMORY_LEGACY" ]; then
  diff "$MEMORY_ACTIVE" "$MEMORY_LEGACY" | head -30 | tee "$VF09/memory_diff.txt"
  if diff -q "$MEMORY_ACTIVE" "$MEMORY_LEGACY" > /dev/null 2>&1; then
    echo "CONTENT_MATCH=true" >> "$VF09/memory_diff.txt"
  else
    echo "CONTENT_MATCH=false" >> "$VF09/memory_diff.txt"
  fi
else
  echo "LEGACY_REMOVED — no comparison needed" | tee "$VF09/memory_diff.txt"
fi
# Expected: CONTENT_MATCH=true OR LEGACY_REMOVED

# ── Gate V9.4: Active MEMORY.md has AUTOSYNC sentinel tags ──
grep -c "AUTOSYNC:" "$MEMORY_ACTIVE" | tee "$VF09/active_autosync_count.txt"
# Expected: >= 5 sentinel tags

# ── Gate V9.5: Legacy MEMORY.md (if exists) is NOT a stale 22-line stub ──
if [ -f "$MEMORY_LEGACY" ]; then
  LEGACY_LINES=$(wc -l < "$MEMORY_LEGACY")
  if [ "$LEGACY_LINES" -le 30 ]; then
    echo "FAIL: Legacy is still a stale stub ($LEGACY_LINES lines)" | tee "$VF09/stale_stub_check.txt"
  else
    echo "PASS: Legacy is substantive ($LEGACY_LINES lines)" | tee "$VF09/stale_stub_check.txt"
  fi
else
  echo "PASS: Legacy removed" | tee "$VF09/stale_stub_check.txt"
fi
# Expected: PASS
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V9.1 | Active MEMORY.md > 100 lines | > 100 | |
| V9.2 | Legacy MEMORY.md state determined | exists or removed | |
| V9.3 | Content match or legacy removed | MATCH=true or REMOVED | |
| V9.4 | Active MEMORY.md has >= 5 AUTOSYNC tags | >= 5 | |
| V9.5 | Legacy is NOT a stale 22-line stub | PASS | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-10: MAKEFILE TARGET NAMING CONSISTENCY
# Original Finding: 10 (MODERATE) — Gate H-1
# Claim: sync-all alias exists OR all docs use sync-all-types
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Guide referenced `make sync-all`. Actual target is `make sync-all-types`. Inconsistency causes confusion and command failures.

## What CONFIG-STABILIZE-001 should have fixed

Either added a `sync-all` alias in Makefile, or updated all docs to use `sync-all-types`. One canonical name everywhere.

## Verification

```bash
VF10="$QA_ROOT/evidence/VF-10-makefile-target"

# ── Gate V10.1: Check if sync-all-types target exists in Makefile ──
grep -n "^sync-all-types:" "$MAKEFILE" | tee "$VF10/sync_all_types_target.txt"
# Expected: at least 1 match

# ── Gate V10.2: Check if sync-all alias target exists in Makefile ──
grep -n "^sync-all:" "$MAKEFILE" | tee "$VF10/sync_all_alias.txt"
# Expected: either (a) exists as alias, or (b) doesn't exist and all docs use sync-all-types

# ── Gate V10.3: Determine which approach was taken ──
HAS_ALIAS=$(grep -c "^sync-all:" "$MAKEFILE" 2>/dev/null) || HAS_ALIAS=0
if [ "$HAS_ALIAS" -gt 0 ]; then
  echo "APPROACH=alias (sync-all target exists)" | tee "$VF10/approach.txt"
else
  echo "APPROACH=canonical-name (all docs must use sync-all-types)" | tee "$VF10/approach.txt"
fi

# ── Gate V10.4: If no alias, guide must NOT contain "sync-all" without "-types" ──
# Match "sync-all" but exclude "sync-all-types" and "sync-all-models" etc.
grep -n "sync-all[^-]" "$GUIDE_PATH" | tee "$VF10/guide_sync_all_bare.txt"
# Expected: ZERO matches (or approach is alias)

# ── Gate V10.5: If no alias, CLAUDE.md files must NOT contain bare "sync-all" ──
grep -n "sync-all[^-]" "$CLAUDE_MD_ROOT" "$CLAUDE_MD_MONO" | tee "$VF10/claude_sync_all_bare.txt"
# Expected: ZERO matches (or approach is alias)

# ── Gate V10.6: If no alias, MEMORY.md must NOT contain bare "sync-all" ──
grep -n "sync-all[^-]" "$MEMORY_ACTIVE" | tee "$VF10/memory_sync_all_bare.txt"
# Expected: ZERO matches (or approach is alias)
# NOTE: The /sync-all command file exists — that's a slash command, not a make target.
# Verify the command file itself calls `make sync-all-types` (not bare `sync-all`)
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V10.1 | sync-all-types target exists | yes | |
| V10.2 | sync-all alias: exists or intentionally absent | determined | |
| V10.3 | Approach documented | alias OR canonical-name | |
| V10.4 | Guide: no bare "sync-all" (if no alias) | 0 matches | |
| V10.5 | CLAUDE.md: no bare "sync-all" (if no alias) | 0 matches | |
| V10.6 | MEMORY.md: no bare "sync-all" (if no alias) | 0 matches | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-11: SKILLS VS COMMANDS DISTINCTION
# Original Finding: 11 (LOW)
# Claim: Guide clarifies skills (built-in) vs commands (project-scoped)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
VF11="$QA_ROOT/evidence/VF-11-skills-vs-commands"

# ── Gate V11.1: Guide distinguishes skills from commands ──
grep -n -i "skill.*command\|command.*skill\|built-in.*skill\|project.*command\|project.*scoped" "$GUIDE_PATH" | head -5 | tee "$VF11/distinction_check.txt"
# Expected: at least 1 match explaining the difference
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V11.1 | Guide distinguishes skills from commands | >= 1 explanatory match | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-12: AGENT FILE LOCATION DOCUMENTATION
# Original Finding: 12 (LOW)
# Claim: Guide notes agents are user-scoped at ~/.claude/agents/
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
VF12="$QA_ROOT/evidence/VF-12-agent-file-location"

# ── Gate V12.1: Actual agent directory exists ──
ls -la /home/zaks/.claude/agents/ 2>&1 | tee "$VF12/agent_dir.txt"
# Expected: directory exists (may be empty)

# ── Gate V12.2: Guide mentions agent file location ──
grep -n -i "agent.*definition\|\.claude/agents\|user.*scoped.*agent\|agent.*user.*level" "$GUIDE_PATH" | head -5 | tee "$VF12/guide_agent_location.txt"
# Expected: at least 1 match
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V12.1 | Agent directory exists | yes | |
| V12.2 | Guide documents agent location | >= 1 match | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-13: MEMORY-SYNC DRY-RUN MODE
# Original Finding: 13 (LOW)
# Claim: memory-sync.sh has a --dry-run flag
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification

```bash
VF13="$QA_ROOT/evidence/VF-13-memory-sync-dryrun"

# ── Gate V13.1: memory-sync.sh contains --dry-run handling ──
grep -n "dry.run\|dry_run\|DRY_RUN\|\-\-dry" "$HOOKS_DIR/memory-sync.sh" | tee "$VF13/dryrun_code.txt"
# Expected: at least 1 match

# ── Gate V13.2: Dry-run produces output without modifying MEMORY.md ──
# Capture MEMORY.md hash before, run dry-run, capture hash after
MD5_BEFORE=$(md5sum "$MEMORY_ACTIVE" | awk '{print $1}')
echo "BEFORE: $MD5_BEFORE" | tee "$VF13/dryrun_test.txt"
bash "$HOOKS_DIR/memory-sync.sh" --dry-run 2>&1 | head -30 >> "$VF13/dryrun_test.txt"
MD5_AFTER=$(md5sum "$MEMORY_ACTIVE" | awk '{print $1}')
echo "AFTER: $MD5_AFTER" >> "$VF13/dryrun_test.txt"
if [ "$MD5_BEFORE" = "$MD5_AFTER" ]; then
  echo "PASS: File unchanged" >> "$VF13/dryrun_test.txt"
else
  echo "FAIL: File was modified during dry-run" >> "$VF13/dryrun_test.txt"
fi
# Expected: PASS (file unchanged)
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V13.1 | Script contains --dry-run code | >= 1 match | |
| V13.2 | Dry-run does not modify MEMORY.md | PASS (hash unchanged) | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VF-14: GUIDE DEDUPLICATION
# Original Finding: 14 (LOW)
# Claim: Guide deduplicated from ~1800 to ~900-1000 lines, zero info loss
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem (as found by audit)

Nearly every paragraph was duplicated (conversion artifact). Guide was ~1800 lines; should be ~900-1000 after dedup.

## Verification

```bash
VF14="$QA_ROOT/evidence/VF-14-guide-deduplication"

# ── Gate V14.1: Guide line count is under 1100 ──
LINES=$(wc -l < "$GUIDE_PATH")
echo "LINE_COUNT=$LINES" | tee "$VF14/line_count.txt"
if [ "$LINES" -le 1100 ]; then
  echo "PASS: Under 1100 ceiling"
else
  echo "FAIL: Still $LINES lines (expected <= 1100)"
fi >> "$VF14/line_count.txt"
# Expected: PASS

# ── Gate V14.2: No consecutive duplicate paragraphs ──
# Extract non-empty, non-header lines and look for consecutive duplicates
python3 -c "
import re
with open('$GUIDE_PATH') as f:
    lines = f.readlines()
prev = ''
dupes = 0
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if len(stripped) > 30 and stripped == prev:
        print(f'DUPE at line {i}: {stripped[:80]}...')
        dupes += 1
    if stripped:
        prev = stripped
print(f'TOTAL_CONSECUTIVE_DUPES={dupes}')
" | tee "$VF14/consecutive_dupes.txt"
# Expected: TOTAL_CONSECUTIVE_DUPES=0

# ── Gate V14.3: Key content sections still present (no info loss) ──
SECTIONS=(
  "Service Map"
  "Deny"
  "Allow"
  "Hook"
  "MCP"
  "Contract Surface"
  "Slash Command"
  "CLAUDE.md"
  "Makefile"
  "Pre-Task"
  "Post-Task"
)
FOUND=0
MISSING=0
for section in "${SECTIONS[@]}"; do
  if grep -qi "$section" "$GUIDE_PATH"; then
    echo "FOUND: $section"
    FOUND=$((FOUND + 1))
  else
    echo "MISSING: $section"
    MISSING=$((MISSING + 1))
  fi
done | tee "$VF14/content_preservation.txt"
echo "FOUND=$FOUND MISSING=$MISSING" >> "$VF14/content_preservation.txt"
# Expected: FOUND=11 MISSING=0
```

### Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| V14.1 | Guide line count <= 1100 | PASS | |
| V14.2 | Zero consecutive duplicate paragraphs | TOTAL=0 | |
| V14.3 | All 11 key content sections present | FOUND=11 MISSING=0 | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CROSS-CONSISTENCY VERIFICATION
# These gates verify that changes across files are mutually consistent
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
CROSS="$QA_ROOT/evidence/cross-consistency"

# ── Gate XC-1: MEMORY.md sentinel tags match filesystem reality ──
# Run memory-sync.sh and verify it produces no patches (all sentinels current)
bash "$HOOKS_DIR/memory-sync.sh" 2>&1 | tee "$CROSS/memory_sync_output.txt"
# Then check for "PATCHED" or "UPDATED" lines — should be 0 if sentinels are current

# ── Gate XC-2: Guide deny rule count matches settings.json ──
GUIDE_DENY=$(grep -c -F "Edit(" "$GUIDE_PATH" 2>/dev/null) || GUIDE_DENY=0
GUIDE_WRITE=$(grep -c -F "Write(" "$GUIDE_PATH" 2>/dev/null) || GUIDE_WRITE=0
SETTINGS_DENY=$(python3 -c "
import json
with open('$SETTINGS_USER') as f:
    print(len(json.load(f).get('permissions',{}).get('deny',[])))
")
echo "GUIDE_DENY_EDIT=$GUIDE_DENY GUIDE_DENY_WRITE=$GUIDE_WRITE SETTINGS_DENY=$SETTINGS_DENY" | tee "$CROSS/deny_parity.txt"
# Expected: GUIDE totals add up to SETTINGS_DENY (12)

# ── Gate XC-3: Guide surface count matches rule file surface count ──
RULE_SURFACES=$(grep -c -i "^##.*surface\|^[0-9]\." "$SURFACES_RULE" 2>/dev/null) || RULE_SURFACES=0
GUIDE_SURFACES=$(grep -c -i "surface [0-9]" "$GUIDE_PATH" 2>/dev/null) || GUIDE_SURFACES=0
echo "RULE_FILE=$RULE_SURFACES GUIDE=$GUIDE_SURFACES" | tee "$CROSS/surface_parity.txt"
# Expected: both = 8

# ── Gate XC-4: Guide hook count matches filesystem hook count ──
FS_HOOKS=$(ls -1 "$HOOKS_DIR"/*.sh | wc -l)
GUIDE_HOOK_MENTIONS=0
for h in pre-edit.sh pre-bash.sh post-edit.sh stop.sh memory-sync.sh; do
  if grep -q "$h" "$GUIDE_PATH"; then GUIDE_HOOK_MENTIONS=$((GUIDE_HOOK_MENTIONS+1)); fi
done
echo "FILESYSTEM=$FS_HOOKS GUIDE=$GUIDE_HOOK_MENTIONS" | tee "$CROSS/hook_parity.txt"
# Expected: both = 5

# ── Gate XC-5: Guide command count matches filesystem command count ──
FS_CMDS=$(ls -1 "$COMMANDS_DIR"/*.md | wc -l)
GUIDE_CMD_MENTIONS=0
for f in "$COMMANDS_DIR"/*.md; do
  NAME=$(basename "$f" .md)
  if grep -qi "$NAME" "$GUIDE_PATH"; then GUIDE_CMD_MENTIONS=$((GUIDE_CMD_MENTIONS+1)); fi
done
echo "FILESYSTEM=$FS_CMDS GUIDE=$GUIDE_CMD_MENTIONS" | tee "$CROSS/command_parity.txt"
# Expected: both = 12

# ── Gate XC-6: Zero 5435 references in ANY Claude Code config file ──
echo "=== Scanning all Claude Code config for port 5435 ===" | tee "$CROSS/global_5435_scan.txt"
grep -rn "5435" \
  "$SETTINGS_USER" \
  "$SETTINGS_SYSTEM" \
  "$MEMORY_ACTIVE" \
  "$MEMORY_LEGACY" \
  "$CLAUDE_MD_ROOT" \
  "$CLAUDE_MD_MONO" \
  "$SURFACES_RULE" \
  "$GUIDE_PATH" \
  "$COMMANDS_DIR/" \
  "$MONOREPO/.claude/rules/" \
  2>/dev/null | tee -a "$CROSS/global_5435_scan.txt"
COUNT_5435=$(grep -c "5435" "$CROSS/global_5435_scan.txt" 2>/dev/null) || COUNT_5435=0
# Subtract the header line
COUNT_5435=$((COUNT_5435 > 0 ? COUNT_5435 - 1 : 0))
echo "TOTAL_5435_REFS=$COUNT_5435" >> "$CROSS/global_5435_scan.txt"
# Expected: 0 (or only historical/narrative — manually verify)
```

### Cross-Consistency Gates

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| XC-1 | memory-sync.sh produces no patches | 0 patches | |
| XC-2 | Guide deny count == settings.json deny count | both = 12 | |
| XC-3 | Guide surface count == rule file surface count | both = 8 | |
| XC-4 | Guide hook count == filesystem hook count | both = 5 | |
| XC-5 | Guide command count == filesystem command count | both = 12 | |
| XC-6 | Zero active 5435 refs across all config files | 0 | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUTION ORDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
PRE-FLIGHT ━━━━ Validate baseline, create evidence directories
    ↓
VF-09 ━━━━━━━━ Memory path resolution (MUST be first — affects all memory checks)
    ↓
VF-08 ━━━━━━━━ Deal Integrity in memory (depends on VF-09 path being resolved)
    ↓
┌─────────────────────────────────────────────────┐
│ PARALLEL BLOCK (no dependencies between these): │
│   VF-01  Deny/allow rules                       │
│   VF-02  Port 5435 eradication                  │
│   VF-03  Slash commands                          │
│   VF-04  Surface 8                               │
│   VF-05  CLAUDE.md split                         │
│   VF-06  MCP servers                             │
│   VF-07  Hooks                                   │
│   VF-10  Makefile target                         │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ LOW PRIORITY (after all above pass):             │
│   VF-11  Skills vs commands                      │
│   VF-12  Agent file location                     │
│   VF-13  memory-sync dry-run                     │
│   VF-14  Guide deduplication                     │
└─────────────────────────────────────────────────┘
    ↓
CROSS-CONSISTENCY ━━━━ XC-1 through XC-6 (depends on all above)
    ↓
FINAL VERIFICATION ━━━━ Scorecard + regression
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
║            QA-CS-VERIFY-001 — FINAL SCORECARD               ║
╚══════════════════════════════════════════════════════════════╝

FINDING  | GATES  | PASS | FAIL | STATUS
---------|--------|------|------|-------
VF-01    |  7     |      |      |
VF-02    |  8     |      |      |
VF-03    |  5     |      |      |
VF-04    |  9     |      |      |
VF-05    |  7     |      |      |
VF-06    |  7     |      |      |
VF-07    |  7     |      |      |
VF-08    |  9     |      |      |
VF-09    |  5     |      |      |
VF-10    |  6     |      |      |
VF-11    |  1     |      |      |
VF-12    |  2     |      |      |
VF-13    |  2     |      |      |
VF-14    |  3     |      |      |
XC       |  6     |      |      |
---------|--------|------|------|-------
TOTAL    |  84    |      |      |

DEFERRALS: 0

VERDICT: [PASS / FAIL]
SCORECARD

echo "" >> "$FINAL/final_report.txt"
echo "REGRESSION: validate-local exit code = $(tail -1 "$QA_ROOT/evidence/regression/validate-local-final.log")" >> "$FINAL/final_report.txt"
echo "TIMESTAMP: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$FINAL/final_report.txt"
```

---

## REMEDIATION PROTOCOL

If any gate FAILS during verification:

1. **Identify the root cause** — read the evidence file to understand WHY it failed
2. **Fix the specific issue** — modify the appropriate file (guide, MEMORY.md, rule file, Makefile)
3. **Re-run ONLY the affected verification section** — do not re-run the entire QA
4. **Update the scorecard** — mark the gate as PASS after successful re-verification
5. **Capture remediation evidence** — save the fix diff and re-verification output
6. **Check cross-consistency** — any fix that changes a count or reference must pass XC gates

```
REMEDIATION GUARDRAILS:
  - Do NOT modify application code (.ts, .py, .tsx, .css)
  - Do NOT modify settings.json permissions (already correct)
  - Do NOT modify hook scripts (already working)
  - Do NOT modify CLAUDE.md files (already operational)
  - DO fix: V5PP-DMS guide, MEMORY.md, contract-surfaces.md, Makefile alias
  - EVERY remediation must be re-verified with the same gate commands
```

---

## PIPELINE MASTER LOG ENTRY

Upon completion, append to `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_PIPELINE_MASTER_LOG.md`:

```
[TIMESTAMP] | QA-CS-VERIFY-001 COMPLETE | Agent=Claude Opus 4.6 | RunID=QA-CS-VERIFY-001 | STATUS=[PASS/FAIL] | 14 findings verified | [N]/84 gates PASS | [N] remediations applied | Report=/home/zaks/bookkeeping/qa-verifications/QA-CS-VERIFY-001/evidence/FINAL/final_report.txt
```

---

## STOP CONDITION

Stop when:
1. All 84 gates are evaluated
2. All FAILed gates have been remediated and re-verified to PASS
3. Cross-consistency gates (XC-1 through XC-6) all PASS
4. `make validate-local` passes (final regression check)
5. Scorecard is complete with VERDICT
6. Pipeline master log entry appended

Do NOT proceed to any other mission. This QA's sole purpose is to verify CONFIG-STABILIZE-001 was executed correctly and completely.

---

*End of QA Mission Prompt — QA-CS-VERIFY-001*

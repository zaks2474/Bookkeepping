# Lab Loop Guide

**Version:** 3.0.0 (Stabilization Release)
**Last Updated:** 2026-01-24

## Overview

Lab Loop is an automated QA/Builder cycle that:
1. Uses Claude Code (headless) as the **Builder** agent - implements fixes
2. Uses Codex (headless) as the **QA** agent (primary) - evaluates results
3. Uses Gemini (headless) as the **QA** agent (fallback) - when Codex unavailable
4. Runs verification gates between cycles
5. Continues until PASS or max cycles reached

**v3.0 Features:**
- Project profiles (`.labloop.yaml`) for per-project settings
- Health check tool (`labloop-doctor`) for diagnostics
- Auto-commit artifacts to prevent diff limit violations
- Enhanced preflight checks and error recovery

```
QA JSON report (Codex/Gemini) → Builder fixes (Claude) → Controller runs gates → QA re-verifies → repeat
```

## Installation

### 1. Add Lab Loop to PATH

Add to `~/.bashrc` or `~/.zshrc`:

```bash
source /home/zaks/bookkeeping/labloop/labloop.profile.sh
```

Or manually:

```bash
export PATH="$PATH:/home/zaks/bookkeeping/labloop/bin"
```

### 2. Verify Installation

```bash
labloop help
```

### 3. Run Self-Test

```bash
/home/zaks/bookkeeping/labloop/tasks/labloop_selftest/verify.sh
```

## Quick Start

### Create a New Task

```bash
labloop new phase18_auth \
  --repo /home/zaks/zakops-backend \
  --gate "pytest tests/"
```

This creates:
```
tasks/phase18_auth/
├── config.env          # Task configuration
├── mission.md          # What to build (EDIT THIS)
├── acceptance.md       # How to verify (EDIT THIS)
├── BUILDER_REPORT.md   # Builder's report
├── history/            # Cycle history
└── artifacts/          # Gate artifacts
```

### Edit Task Files

1. **mission.md** - Describe what needs to be built
2. **acceptance.md** - Define acceptance criteria and verification steps

### Run the Loop

```bash
labloop run phase18_auth
```

Or with options:

```bash
labloop run phase18_auth --dry-run        # Simulate without running agents
labloop run phase18_auth --max-cycles 10  # Limit cycles
```

### Check Status

```bash
labloop status phase18_auth
labloop list
```

## Task Configuration

### config.env

```bash
# Required
REPO_DIR="/home/zaks/zakops-backend"    # Repository to work in
GATE_CMD="pytest tests/"                 # Verification command (exit 0 = pass)

# Optional
CLAUDE_ADD_DIRS="/home/zaks/docs"        # Extra dirs for Claude to read
MAX_CYCLES=20                            # Max cycles before giving up
```

### mission.md Template

```markdown
# Mission: [Task Title]

## Objective
[What needs to be built or fixed]

## Background
[Context and why this is needed]

## Scope
### In Scope
- [Item 1]
### Out of Scope
- [Item 1]

## Technical Requirements
[Specific requirements]
```

### acceptance.md Template

```markdown
# Acceptance Criteria

## Definition of Done
- [ ] [Requirement 1]
- [ ] [Requirement 2]

## Verification Steps
1. [Step 1]
2. [Step 2]

## Gate Command
The verification gate command must exit with code 0.
```

## How It Works

### The Loop

1. **Compose Bundle** - Combines protocol, mission, acceptance, and QA report
2. **Run Builder** - Claude Code reads bundle, makes changes, writes report
3. **Run Gates** - Controller runs verification command
4. **Run QA** - Codex reads all artifacts, produces JSON verdict
5. **Check Verdict** - If PASS, exit. Otherwise, continue.
6. **Stuck Detection** - If QA report unchanged, exit for human intervention.

### Builder Protocol

The Builder (Claude Code):
- Reads the task bundle from stdin
- Makes the smallest safe change set
- Runs verification commands
- Writes `BUILDER_REPORT.md`
- Outputs JSON: `{"status":"READY_FOR_QA","changed_files":[...],"commands_run":[...],"notes_for_QA":[...]}`

### QA Protocol

The QA (Codex):
- Is read-only (cannot modify repo)
- Receives task bundle, builder report, and gate output
- Produces JSON matching the schema
- Sets verdict to PASS only if all gates pass AND spec compliance is met

### QA Report Schema (v2.1.1)

```json
{
  "verdict": "PASS" | "FAIL",
  "cycle": 1,
  "early_exit": false,
  "summary": "...",
  "blockers": [...],
  "majors": [...],
  "minors": [...],
  "spec_compliance": {
    "endpoints_match": true,
    "schemas_match": true,
    ...
  },
  "next_actions_for_builder": [...],
  "evidence": [...]
}
```

## File Structure

```
/home/zaks/bookkeeping/labloop/
├── bin/
│   ├── labloop           # Main CLI
│   ├── labloop.sh        # Orchestrator
│   └── labloop-new.sh    # Task generator
├── schemas/
│   └── qa_report.schema.json
├── templates/
│   ├── builder_protocol.txt
│   └── qa_protocol.txt
└── tasks/
    └── <TASK_ID>/
        ├── config.env
        ├── mission.md
        ├── acceptance.md
        ├── BUILDER_REPORT.md
        ├── QA_REPORT.json
        ├── gate_output.log
        ├── gate_rc.txt
        ├── history/
        │   ├── builder_stdout_cycle_N.json
        │   ├── gate_output_cycle_N.log
        │   └── qa_report_cycle_N.json
        └── artifacts/
```

## PowerShell Usage

From Windows PowerShell:

```powershell
.\labloop.ps1 list
.\labloop.ps1 new phase18_auth --repo /home/zaks/zakops-backend
.\labloop.ps1 run phase18_auth
```

## Troubleshooting

### "claude CLI not available"

Install Claude Code:
```bash
npm install -g @anthropic/claude-code
```

### "codex CLI not available"

Install Codex:
```bash
npm install -g @openai/codex
```

### "STUCK: QA report unchanged"

The QA is producing the same report. This usually means:
1. The Builder isn't making effective changes
2. The gate is failing for the same reason
3. Human intervention is needed

Check:
- `BUILDER_REPORT.md` - What did the Builder do?
- `gate_output.log` - What's failing?
- `QA_REPORT.json` - What issues remain?

### "MAX CYCLES reached"

The loop ran out of cycles. Either:
1. The task is too complex for automatic fixing
2. The acceptance criteria are too strict
3. Increase `MAX_CYCLES` in config.env

### Empty QA_REPORT.json (v2.1.1 Fix)

If `QA_REPORT.json` is empty (0 bytes), the loop will now:
1. Detect the empty file
2. Generate a fallback QA report
3. Continue the loop with a FAIL verdict

Check `history/codex_output_cycle_N.log` for Codex errors.

### JSON Extraction Failed (v2.1.1 Fix)

If Builder output contains JSON in markdown blocks:
```markdown
Some text here...
```json
{"status": "READY_FOR_QA", ...}
```
More text...
```

The controller now handles JSON blocks anywhere in output (not just at the end).

### Codex Timeout (v2.1.1 Fix)

Codex has a 15-minute timeout. If it times out:
1. A fallback QA report is generated with FAIL verdict
2. The loop continues
3. Check `history/codex_output_cycle_N.log` for partial output

### Gemini Fallback Issues (v2.1.2)

When Codex fails, Lab Loop tries Gemini as fallback. If you see:
```
Primary QA agent (codex) failed, trying fallback (gemini)...
```

This is normal. If Gemini also fails:

1. **Check Gemini CLI is installed**: `which gemini`
2. **Check API key**: `GEMINI_API_KEY` environment variable
3. **Check logs for prompt size**: Should be ~10KB, not 48KB+
4. **Check raw output**: Look for "Gemini raw output" in `loop.log`

v2.1.2 fixed a bug where large prompts caused hangs:
- Prompts now passed via stdin (not CLI argument)
- Prompts condensed from 48KB to ~10KB

### Bash Arithmetic in Gate Scripts

When writing gate scripts with `set -e`, avoid:
```bash
((COUNTER++))  # Returns exit code 1 when incrementing from 0
```

Use instead:
```bash
COUNTER=$((COUNTER + 1))  # Always returns exit code 0
```

## Best Practices

1. **Keep gates executable** - A script that exits 0 on success
2. **Be specific in acceptance.md** - Clear, testable criteria
3. **Start with dry-run** - `labloop run TASK --dry-run`
4. **Check history** - Review `history/` for debugging
5. **Use decision locks** - Reference `/home/zaks/bookkeeping/docs/` for constraints

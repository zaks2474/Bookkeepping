# LAB LOOP STANDARD (MANDATORY)

**Version:** 2.1.1 (Stability Fixes)
**Last Updated:** 2026-01-24

This document defines the authoritative protocol for Lab Loop automation.
All agents (Builder and QA) MUST adhere to this standard.

## Overview

Lab Loop is an automated QA/Builder cycle that:
- Uses **Claude Code** as Builder (implements changes)
- Uses **Codex** as QA (verifies compliance, read-only)
- Runs verification gates between cycles
- Continues until PASS verdict or max cycles reached

## Shared Workspace

```
TASK_DIR = /home/zaks/bookkeeping/labloop/tasks/<TASK_ID>/
AUTHORITATIVE_DOCS = /home/zaks/bookkeeping/docs/
```

### Task Directory Structure

```
TASK_DIR/
  config.env          # Task configuration (REPO_DIR, GATE_CMD)
  mission.md          # What to build (objective, scope, requirements)
  acceptance.md       # How to verify (acceptance criteria, gates)
  BUILDER_REPORT.md   # Builder's human-readable report
  QA_REPORT.json      # QA's schema-valid verdict
  gate_output.log     # Gate command output
  gate_rc.txt         # Gate exit code
  history/            # Cycle history (reports, logs per cycle)
  artifacts/          # Gate artifacts
  escalation_*.zip    # Stuck escalation packets (if triggered)
```

## Handoff Protocol

### Step 1: Builder Phase

Builder (Claude Code) receives:
- Task bundle with mission, acceptance criteria, and latest QA report
- Access to REPO_DIR for making changes
- Access to AUTHORITATIVE_DOCS for decision constraints

Builder MUST:
1. Read and understand the QA report's `next_actions_for_builder`
2. Address ALL Blockers first, then Majors, then Minors
3. Make the smallest safe change set
4. Run verification commands as specified
5. Write `TASK_DIR/BUILDER_REPORT.md` (human-readable)
6. Output ONLY a JSON summary to stdout:

```json
{
  "status": "READY_FOR_QA",
  "changed_files": ["path/to/file1.py", "path/to/file2.py"],
  "commands_run": ["pytest tests/", "ruff check ."],
  "notes_for_QA": ["Fixed auth bug in line 42", "Added missing test"]
}
```

### Step 2: Gate Phase

Controller runs `GATE_CMD` from config.env:
- Captures stdout/stderr to `gate_output.log`
- Captures exit code to `gate_rc.txt`
- Gate MUST exit 0 for task to pass

### Step 3: QA Phase

QA (Codex) receives:
- Task bundle with mission and acceptance criteria
- BUILDER_REPORT.md from Builder
- Gate output and exit code
- JSON Schema for output format

QA MUST:
1. Verify gate passed (exit code 0)
2. Verify spec compliance against acceptance.md
3. Cross-reference with AUTHORITATIVE_DOCS
4. Produce schema-valid `QA_REPORT.json`

Verdict rules:
- `PASS` ONLY if: gates pass AND all spec compliance checks pass
- `FAIL` if: any blocker exists OR gates fail OR spec non-compliance

### Step 4: Loop Decision

- If QA verdict = `PASS` AND gate exit code = 0: **TASK COMPLETE**
- If QA verdict = `FAIL`: Builder addresses issues and repeats from Step 1
- If stuck (same QA report twice): Creates escalation packet, requires human intervention

## Timeouts (v2.1.1)

| Agent | Timeout | Behavior on Timeout |
|-------|---------|---------------------|
| Builder (Claude Code) | 20 minutes | Kill and retry |
| QA (Codex) | 15 minutes | Generate fallback report |
| Gate Command | Per config | Fail cycle |

## Diff Limits (v2.1.1)

To prevent context exhaustion, Builder output is limited:

| Limit Type | Value | Behavior |
|------------|-------|----------|
| Max diff lines (BUILDER_REPORT.md) | 1000 | Truncate with warning |
| Max lines per file diff | 500 | Truncate individual files |

## JSON Output Format (v2.1.1)

Builder MUST output valid JSON. The controller handles:
- JSON wrapped in markdown code blocks (```json ... ```)
- JSON anywhere in the output (not just at end)
- Raw JSON objects

**Best Practice:** Output clean JSON without markdown wrapping.

## Critical Rules

1. **Do not declare success early** - Only the QA verdict determines completion
2. **Do not bypass the loop** - All changes must go through Builder → Gate → QA
3. **Obey authoritative docs** - All decisions must align with `/home/zaks/bookkeeping/docs/`
4. **Smallest change set** - Make minimal changes to fix issues
5. **No scope creep** - Only address what's in mission.md and acceptance.md
6. **Valid JSON output** - Builder must output schema-valid JSON summary
7. **Respect diff limits** - Keep diffs under 1000 lines total

## Severity Definitions

| Severity | Definition | Action Required |
|----------|------------|-----------------|
| BLOCKER  | Prevents task completion, gates fail | Must fix immediately |
| MAJOR    | Significant issue, may cause failures | Must fix before PASS |
| MINOR    | Small issue, doesn't block completion | Should fix if time permits |

## Evidence Requirements

QA must provide evidence for all findings:
- File paths and line numbers
- Command outputs
- Spec references
- Clear reproduction steps

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | PASS - Task completed successfully |
| 1    | General error |
| 2    | STUCK - Human intervention required |
| 3    | MAX_CYCLES reached without PASS |

## QA Report Schema (v2.1.1)

The `early_exit` field is required:

```json
{
  "verdict": "PASS" | "FAIL",
  "cycle": 1,
  "early_exit": false,
  "summary": "...",
  "blockers": [...],
  "majors": [...],
  "minors": [...],
  "spec_compliance": {...},
  "next_actions_for_builder": [...],
  "evidence": [...]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `verdict` | Yes | PASS or FAIL |
| `cycle` | Yes | Current cycle number |
| `early_exit` | Yes | Set true if QA cannot continue (fatal error) |
| `summary` | Yes | Human-readable summary |
| `blockers` | Yes | Array of blocking issues |
| `majors` | Yes | Array of major issues |
| `minors` | Yes | Array of minor issues |
| `spec_compliance` | Yes | Object with compliance checks |
| `next_actions_for_builder` | Yes | Array of prioritized actions |
| `evidence` | Yes | Array of evidence items |

## Fallback QA Report

If QA times out or produces invalid output, the controller generates:

```json
{
  "verdict": "FAIL",
  "cycle": N,
  "early_exit": false,
  "summary": "QA agent timed out or failed to produce valid output",
  "blockers": [{
    "severity": "BLOCKER",
    "title": "QA agent failure",
    "details": "Codex failed to produce valid QA report...",
    "recommended_fix": "Check Codex logs and retry"
  }],
  "majors": [],
  "minors": [],
  "spec_compliance": {},
  "next_actions_for_builder": [{
    "priority": 1,
    "severity": "BLOCKER",
    "summary": "Investigate QA failure and retry"
  }],
  "evidence": []
}
```

# Lab Loop v3.0: Complete Setup & Implementation Guide

> **Version**: 3.0.0
> **Author**: ZakOps Engineering
> **Last Updated**: January 24, 2026
> **License**: MIT

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [Prerequisites](#3-prerequisites)
4. [Installation](#4-installation)
5. [Configuration](#5-configuration)
6. [Usage](#6-usage)
7. [Agent Configuration](#7-agent-configuration)
8. [Safety Guardrails](#8-safety-guardrails)
9. [2-Tier Gate System](#9-2-tier-gate-system)
10. [Environment Reproducibility](#10-environment-reproducibility)
11. [Persistence Modes](#11-persistence-modes)
12. [Email & Webhook Notifications](#12-email--webhook-notifications)
13. [Definition of PASS](#13-definition-of-pass)
14. [Writing Good acceptance.md](#14-writing-good-acceptancemd)
15. [When to Intervene](#15-when-to-intervene)
16. [Troubleshooting](#16-troubleshooting)
17. [API Reference](#17-api-reference)
18. [Best Practices](#18-best-practices)
19. [Contributing](#19-contributing)
20. [E2E Validation Scenario (MathLib)](#20-e2e-validation-scenario-mathlib)
21. [v2.1 Technical Details](#21-v21-technical-details)
22. [v2.1.2 Technical Details (Gemini QA Fallback)](#22-v212-technical-details-gemini-qa-fallback)
23. [v3.0 Stabilization Features](#23-v30-stabilization-features)

---

## 1. Introduction

### What is Lab Loop?

Lab Loop is an automated QA/Builder feedback loop that uses AI agents to implement and verify code changes. It combines:

- **Builder Agent** (Claude Code): Implements code changes based on requirements
- **QA Agent** (Codex): Verifies implementations against acceptance criteria
- **Verification Gates**: Automated tests that must pass for completion
- **Safety Guardrails**: Protects against runaway changes and security issues

### What's New in v2.0

| Feature | Description |
|---------|-------------|
| **Schema-Enforced Builder** | Builder output now validated against JSON schema |
| **Task Locking** | Prevents concurrent runs on same task (flock) |
| **Safety Guardrails** | Protected paths, diff limits, command denylist |
| **Environment Snapshots** | Full reproducibility with git state, tool versions |
| **Secrets Redaction** | Automatic in escalation packets |
| **2-Tier Gates** | Fast (iteration) vs Full (release) validation |
| **Smart Dry-Run** | Single-cycle demo without stuck detection |

### What's New in v2.1 (Stability & Reliability Fixes)

| Feature | Description |
|---------|-------------|
| **Improved JSON Extraction** | Handles markdown code blocks anywhere in output (not just at line start) |
| **QA Early Exit Field** | Added `early_exit` boolean to QA schema for proper failure tracking |
| **Agent Timeouts** | Builder: 20 min, QA: 15 min - prevents infinite hangs |
| **Codex Fallback Report** | Creates valid QA report if Codex fails/times out |
| **Bash Arithmetic Fix** | Fixed `((var++))` causing exit on first increment with `set -e` |
| **Protected Path Matching** | Uses glob-only matching (no substring false positives) |
| **Retry Bundle Race Fix** | Uses temp file to prevent clobbering during read |
| **Diff Limit Increase** | MAX_LINES_PER_CYCLE default increased from 500 to 1000 |
| **E2E Validation Scenario** | MathLib test scenario for validating loop mechanics |

### What's New in v2.1.2 (Gemini QA Fallback)

| Feature | Description |
|---------|-------------|
| **Gemini QA Agent** | Alternative QA agent when Codex is unavailable (rate limits, outages) |
| **Stdin Prompt Delivery** | Prompts passed via stdin pipe instead of CLI arguments (handles large prompts) |
| **Condensed QA Prompts** | Gemini receives ~10KB condensed prompt instead of full 48KB bundle |
| **Prompt Size Logging** | Debug logging shows prompt sizes for troubleshooting |
| **Auto early_exit Field** | Automatically adds `early_exit: false` if missing from Gemini output |
| **Robust JSON Extraction** | Multiple fallback methods for extracting JSON from Gemini responses |

### What's New in v3.0.0 (Stabilization Release)

| Feature | Description |
|---------|-------------|
| **Project Profiles** | `.labloop.yaml` files per-project with custom limits, auto-commit, skip_tests |
| **Health Check Tool** | `labloop-doctor` diagnoses issues before running (CLI tools, locks, services) |
| **Auto-Commit Artifacts** | Automatically commits gate artifacts after each cycle (prevents diff limit violations) |
| **Enhanced Preflight** | Python syntax validation, venv detection, stale lock cleanup |
| **Error Recovery** | Automatic recovery attempts for diff_limit, stale_lock, builder_timeout errors |
| **Builder Hang Fix** | Fixed dual-input confusion that caused Claude CLI to hang indefinitely |

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Automation** | No manual intervention required once started |
| **Quality Assurance** | Every change verified by independent QA agent |
| **Safety** | Blast-radius controls prevent runaway changes |
| **Reproducibility** | Environment snapshots for debugging |
| **Persistence** | Runs in background via tmux/nohup/systemd |
| **Auditability** | Full history of cycles, reports, and gate outputs |

### How It Works

```
+------------------------------------------------------------------+
|                    LAB LOOP v2.0 CYCLE                            |
+------------------------------------------------------------------+
|                                                                   |
|  +----------+   +--------+   +--------+   +--------+   +-------+  |
|  | Snapshot |-->| Builder|-->| Safety |-->|  Gate  |-->|  QA   |  |
|  | Capture  |   | (Claude)|   | Checks |   | (Tests)|   |(Codex)|  |
|  +----------+   +--------+   +--------+   +--------+   +-------+  |
|       |              |            |            |            |      |
|       |              |            |            |            v      |
|       |              |            |            |     +-----------+ |
|       |              |            |            |     | Decision  | |
|       |              |            |            |     +-----------+ |
|       |              |            |            |            |      |
|       |              |            |            |            v      |
|       |              |            |     +------------------------+ |
|       |              |            |     | PASS --> Done! Notify  | |
|       |              |            |     | FAIL --> Loop back     | |
|       |              |            |     | STUCK --> Escalate     | |
|       |              |            |     | SAFETY --> Stop!       | |
|       |              |            |     +------------------------+ |
|       |              |            |                                |
|       +<-------------+<-----------+<-------------------------------+
|                                                                   |
+------------------------------------------------------------------+
```

---

## 2. Architecture Overview

### Directory Structure

```
/home/zaks/bookkeeping/labloop/
+-- bin/                          # Executable scripts
|   +-- labloop                   # Main CLI entry point
|   +-- labloop.sh                # Orchestrator script (v2.0)
|   +-- labloop-new.sh            # Task creation script
+-- config/                       # Configuration files
|   +-- safety.conf               # Safety guardrails config
+-- docs/                         # Documentation
|   +-- LABLOOP_COMPLETE_GUIDE.md # This file
+-- profiles/                     # Gate profiles (presets)
|   +-- gate-python-fast.sh       # Quick Python checks
|   +-- gate-python-full.sh       # Full Python validation
|   +-- gate-nextjs.sh            # Next.js/React projects
|   +-- gate-go.sh                # Go projects
|   +-- gate-rust.sh              # Rust projects
|   +-- gate-docker.sh            # Docker-based testing
+-- schemas/                      # JSON schemas
|   +-- qa_report.schema.json     # QA report format
|   +-- builder_report.schema.json # Builder report format (NEW)
|   +-- safety_config.schema.json # Safety config format (NEW)
+-- templates/                    # Protocol templates
|   +-- builder_protocol.txt      # Instructions for Builder
|   +-- qa_protocol.txt           # Instructions for QA
+-- tasks/                        # Task directories
    +-- <task_id>/                # Individual task
        +-- config.env            # Task configuration
        +-- mission.md            # What to build
        +-- acceptance.md         # How to verify
        +-- BUILDER_REPORT.md     # Builder's report
        +-- QA_REPORT.json        # QA's verdict
        +-- gate_output.log       # Gate command output
        +-- history/              # Cycle history
        +-- snapshots/            # Environment snapshots (NEW)
        +-- artifacts/            # Gate artifacts
        +-- .lock                 # Task lock file (NEW)
        +-- .pid                  # Running PID (NEW)
```

### Component Responsibilities

| Component | Technology | Role |
|-----------|------------|------|
| **Orchestrator** | Bash (labloop.sh) | Manages loop, calls agents, runs gates, safety checks |
| **Builder** | Claude Code (headless) | Implements code changes, outputs schema-validated JSON |
| **QA (Primary)** | Codex (headless) | Verifies implementations, outputs schema-enforced JSON |
| **QA (Fallback)** | Gemini CLI (headless) | Alternative QA when Codex unavailable (v2.1.2+) |
| **Gates** | Shell scripts | Run tests, linting, type checking |
| **Safety** | Bash functions | Protected paths, diff limits, command filtering |
| **Notifications** | Python/SMTP | Send email/webhook alerts |

---

## 3. Prerequisites

### Required Software

| Software | Minimum Version | Installation |
|----------|-----------------|--------------|
| **Node.js** | 18.x | `apt install nodejs` or `nvm install 18` |
| **Python** | 3.8+ | Usually pre-installed on Linux |
| **Bash** | 4.0+ | Usually pre-installed on Linux |
| **Git** | 2.x | `apt install git` |
| **jq** | 1.6+ | `apt install jq` (for JSON validation) |
| **Claude Code CLI** | Latest | `npm install -g @anthropic-ai/claude-code` |
| **Codex CLI** | Latest | `npm install -g @openai/codex` |
| **Gemini CLI** | Latest (optional) | `npm install -g @anthropic/gemini-cli` (QA fallback) |

### API Keys Required

| Service | Environment Variable | Get From |
|---------|---------------------|----------|
| **Anthropic** | `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| **OpenAI** | `OPENAI_API_KEY` | https://platform.openai.com/ |
| **Google** (optional) | `GEMINI_API_KEY` | https://makersuite.google.com/app/apikey (for QA fallback) |

---

## 4. Installation

### Step 1: Clone or Create Directory Structure

```bash
mkdir -p /home/$USER/bookkeeping/labloop/{bin,config,docs,profiles,schemas,templates,tasks}
mkdir -p ~/.labloop
```

### Step 2: Install CLI Tools

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH="$HOME/.npm-global/bin:$PATH"

npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex

# Verify
claude --version
codex --version
```

### Step 3: Add to PATH

Add to `~/.bashrc`:

```bash
# Lab Loop automation
export PATH="$PATH:/home/$USER/bookkeeping/labloop/bin"
export PATH="$HOME/.npm-global/bin:$PATH"
```

Reload: `source ~/.bashrc`

### Step 4: Verify Installation

```bash
labloop --version
labloop help
```

---

## 5. Configuration

### Global Configuration (`~/.labloop/config`)

```bash
# Lab Loop Configuration
# ======================

# Email notifications
LABLOOP_EMAIL="your.email@gmail.com"

# Gmail SMTP settings
LABLOOP_SMTP_USER="your.email@gmail.com"
LABLOOP_SMTP_PASS="your-16-char-app-password"
LABLOOP_SMTP_HOST="smtp.gmail.com"
LABLOOP_SMTP_PORT="587"

# Webhook (optional)
# LABLOOP_WEBHOOK="https://hooks.slack.com/services/xxx"

# Default settings
MAX_CYCLES=50
```

### Safety Configuration (`config/safety.conf`)

```bash
# Protected paths (glob patterns)
PROTECTED_PATHS=(
    ".env"
    ".env.*"
    "**/secrets/**"
    "**/credentials/**"
    "**/*.pem"
    "**/*.key"
)

# Diff limits (v2.1: increased defaults)
MAX_FILES_PER_CYCLE=20
MAX_LINES_PER_CYCLE=1000      # Increased from 500 in v2.1
MAX_LINES_PER_FILE=500        # Increased from 300 in v2.1
DIFF_LIMIT_ACTION="escalate"  # or "warn"

# Repo cleanliness
REQUIRE_CLEAN_START=false
AUTO_STASH=false
MAX_UNCOMMITTED_FILES=50

# Secrets redaction
REDACT_SECRETS=true
```

### Task Configuration (`tasks/<task_id>/config.env`)

```bash
# Task: my_task
REPO_DIR="/home/user/my-project"

# Single gate (legacy)
GATE_CMD="pytest tests/ -v"

# 2-tier gates (recommended)
GATE_FAST_CMD="pytest tests/ -x -q"
GATE_FULL_CMD="pytest tests/ --cov=src --cov-fail-under=80"

# Additional directories for Claude
CLAUDE_ADD_DIRS="/home/user/docs"
```

---

## 6. Usage

### Creating a New Task

```bash
# Basic
labloop new my_task --repo /path/to/repo --gate "pytest tests/"

# With profile
labloop new my_task --repo /path/to/repo --profile python-fast

# With 2-tier gates
labloop new my_task --repo /path/to/repo \
  --gate-fast "pytest tests/ -x" \
  --gate-full "pytest tests/ --cov=src --cov-fail-under=80"

# List profiles
labloop new --list-profiles
```

### Running a Task

```bash
# Standard run (fast tier)
labloop run my_task

# With full validation
labloop run my_task --tier full

# Dry run (1 cycle demo)
labloop run my_task --dry-run

# With all features
labloop run my_task \
  --incremental \
  --email user@gmail.com \
  --tier fast
```

### Monitoring

```bash
# Check status
labloop status my_task

# List all tasks
labloop list

# Watch live log
tail -f tasks/my_task/loop.log
```

---

## 7. Agent Configuration

### Claude Code (`~/.claude/CLAUDE.md`)

```markdown
## Lab Loop Auto-Detection

When input contains "=== BUILDER PROTOCOL ===":
1. You are running NON-INTERACTIVELY
2. Address issues: BLOCKERS -> MAJORS -> MINORS
3. Output schema-validated JSON
4. Required fields: status, cycle, summary, issues_addressed,
   changed_files, commands_run, gate_pre_check, notes_for_qa
```

### Codex (`~/.codex/config.toml`)

```toml
model = "o3"
sandbox = "read-only"
ask_for_approval = "never"

[profiles.labloop-qa]
model = "o3"
sandbox = "read-only"
ask_for_approval = "never"
```

---

## 8. Safety Guardrails

### Protected Paths

Builder will be **immediately stopped** if it modifies:
- `.env` files
- `secrets/**` directories
- `credentials/**` directories
- `*.pem`, `*.key` files
- Any path matching patterns in `PROTECTED_PATHS`

### Diff Limits

| Limit | Default (v2.1) | Description |
|-------|----------------|-------------|
| `MAX_FILES_PER_CYCLE` | 20 | Max files modified per cycle |
| `MAX_LINES_PER_CYCLE` | 1000 | Max total lines changed (was 500 in v2.0) |
| `MAX_LINES_PER_FILE` | 500 | Max lines in single file (was 300 in v2.0) |

When exceeded:
- `DIFF_LIMIT_ACTION=escalate`: Stop immediately
- `DIFF_LIMIT_ACTION=warn`: Log warning, continue

### Command Denylist

Blocked commands (regex patterns):
```
^rm\s+-rf\s+/          # rm -rf /
^sudo\s+rm             # sudo rm
^chmod\s+777           # chmod 777
^curl.*\|.*sh          # curl | sh
^git\s+push.*--force   # force push
```

### Task Locking

Uses `flock` to prevent concurrent runs:
```bash
# If task is already running:
ERROR: Task 'my_task' is already running (PID: 12345)
If this is stale, remove: .lock and .pid
```

### Secrets Redaction

Before creating escalation packets:
1. API keys are replaced with `[REDACTED]`
2. Passwords/secrets are replaced
3. Tokens (GitHub, OpenAI, Slack) are replaced
4. Private keys are replaced

---

## 9. 2-Tier Gate System

### Concept

| Tier | Purpose | Speed | Rigor |
|------|---------|-------|-------|
| **Fast** | Iterative development | 1-5 min | Basic checks |
| **Full** | Release validation | 5-30 min | Comprehensive |

### Configuration

In `config.env`:
```bash
GATE_FAST_CMD="pytest tests/ -x -q && ruff check ."
GATE_FULL_CMD="pytest tests/ --cov=src --cov-fail-under=80 && mypy src/ --strict"
```

### Usage

```bash
# Development iteration (default)
labloop run my_task --tier fast

# Before release
labloop run my_task --tier full
```

### Profile Examples

**Python Fast** (`profiles/gate-python-fast.sh`):
```bash
# Parallel lint + typecheck, then quick tests
ruff check . &
mypy src/ &
wait
pytest tests/ -x -q
```

**Python Full** (`profiles/gate-python-full.sh`):
```bash
# Strict validation + coverage
ruff check . --select=ALL &
mypy src/ --strict &
wait
pytest tests/ --cov=src --cov-fail-under=70 --cov-report=term
```

---

## 10. Environment Reproducibility

### Per-Cycle Snapshots

Each cycle captures:
```
snapshots/cycle_N/
+-- git_commit_before.txt    # HEAD before Builder
+-- git_commit_after.txt     # HEAD after Builder
+-- git_status_before.txt    # Working tree state
+-- git_branch.txt           # Current branch
+-- git_diff_stat.txt        # Diff statistics
+-- tool_versions.txt        # Claude, Codex, Python, Node versions
+-- pip_freeze.txt           # Python dependencies (if applicable)
+-- npm_ls.txt               # Node dependencies (if applicable)
+-- run_metadata.txt         # Timestamp, task ID, config
```

### Debugging "Why did it fail today?"

```bash
# Compare snapshots
diff snapshots/cycle_5/pip_freeze.txt snapshots/cycle_1/pip_freeze.txt

# Check tool versions
cat snapshots/cycle_5/tool_versions.txt

# See git state
cat snapshots/cycle_5/git_commit_before.txt
```

---

## 11. Persistence Modes

**Important**: Lab Loop does NOT persist automatically. Use one of these methods:

### Method 1: tmux (Recommended)

```bash
# Start in detached tmux session
tmux new-session -d -s labloop 'labloop run my_task'

# Attach to see output
tmux attach -t labloop

# Detach: Ctrl+B, D
# Kill: tmux kill-session -t labloop
```

### Method 2: nohup

```bash
# Start in background
nohup labloop run my_task > ~/labloop.log 2>&1 &

# Get PID
echo $!

# Monitor
tail -f ~/labloop.log

# Kill
kill $(cat tasks/my_task/.pid)
```

### Method 3: systemd User Service

Create `~/.config/systemd/user/labloop@.service`:
```ini
[Unit]
Description=Lab Loop Task %i
After=network.target

[Service]
Type=simple
ExecStart=/home/zaks/bookkeeping/labloop/bin/labloop run %i
WorkingDirectory=/home/zaks/bookkeeping/labloop
Restart=no
StandardOutput=append:/home/zaks/bookkeeping/labloop/tasks/%i/loop.log
StandardError=append:/home/zaks/bookkeeping/labloop/tasks/%i/loop.log

[Install]
WantedBy=default.target
```

Usage:
```bash
systemctl --user daemon-reload
systemctl --user start labloop@my_task
systemctl --user status labloop@my_task
journalctl --user -u labloop@my_task -f
```

### Method 4: Screen

```bash
screen -dmS labloop labloop run my_task
screen -r labloop  # Reattach
# Detach: Ctrl+A, D
```

---

## 12. Email & Webhook Notifications

### Email Events

| Event | Trigger | Email Sent |
|-------|---------|------------|
| STARTED | Loop begins | Yes |
| PASS | Task completed | Yes |
| STUCK | Loop stuck | Yes |
| MAX_CYCLES | Limit reached | Yes |
| PREFLIGHT_FAIL | Pre-flight failed | Yes |
| SAFETY_VIOLATION | Safety check failed | Yes |
| BUILDER_SCHEMA_FAIL | Builder JSON invalid | Yes |
| FAIL | Cycle failed | Every 5th cycle |

### Gmail Setup

1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Configure in `~/.labloop/config`:
   ```bash
   LABLOOP_EMAIL="you@gmail.com"
   LABLOOP_SMTP_USER="you@gmail.com"
   LABLOOP_SMTP_PASS="abcdefghijklmnop"  # 16-char app password
   ```

### Webhook Payload

```json
{
  "task_id": "my_task",
  "event": "PASS",
  "cycle": 5,
  "timestamp": "2026-01-23T21:00:00Z",
  "repo": "/home/user/my-project",
  "details": "Task completed successfully"
}
```

---

## 13. Definition of PASS

**PASS requires ALL of the following:**

```
+--------------------------------------------------+
|              DEFINITION OF PASS                   |
+--------------------------------------------------+
| 1. Gate exit code = 0                            |
| 2. All spec_compliance fields = true             |
| 3. Zero BLOCKERS                                 |
| 4. Zero MAJORS                                   |
+--------------------------------------------------+
| FAIL if ANY condition above is not met           |
+--------------------------------------------------+
```

This is the **canonical** definition. It appears in:
- QA protocol template
- QA input bundle
- This documentation

**Do not** lower standards by accepting tasks with MAJORS.

---

## 14. Writing Good acceptance.md

### Good Example

```markdown
# Acceptance Criteria: User Authentication

## Definition of Done

### Functional Requirements
- [ ] POST /api/auth/login returns 200 with valid credentials
- [ ] POST /api/auth/login returns 401 with invalid credentials
- [ ] JWT token expires after 24 hours
- [ ] Refresh token endpoint works correctly

### Quality Gates
- [ ] All tests pass (`pytest tests/auth/`)
- [ ] No linting errors (`ruff check src/auth/`)
- [ ] Type coverage > 90% (`mypy src/auth/`)

### Spec Compliance
- [ ] Matches OpenAPI spec in docs/api.yaml
- [ ] Error responses match error schema

## Gate Command
```bash
pytest tests/auth/ -v && ruff check src/auth/ && mypy src/auth/
```

### Bad Example (Don't Do This)

```markdown
# Acceptance Criteria

- Make the login work
- Fix the bugs
- Tests should pass
```

**Why it's bad:**
- Vague ("make it work")
- No specific endpoints or behaviors
- No measurable criteria
- No gate command

### Acceptance Criteria Checklist

- [ ] Each requirement is testable
- [ ] Specific file paths mentioned where relevant
- [ ] Gate command is explicit
- [ ] Success is measurable (exit codes, coverage numbers)
- [ ] Error cases are specified

---

## 15. When to Intervene

### Intervention Flowchart

```
                    +------------------+
                    | Exit Code Check  |
                    +------------------+
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
       Exit 0          Exit 2          Exit 3
       (PASS)          (STUCK)       (MAX_CYCLES)
            |               |               |
            v               v               v
       +-------+    +--------------+  +-----------+
       | Done! |    | Review       |  | Review    |
       +-------+    | Escalation   |  | History   |
                    | Packet       |  | & Logs    |
                    +--------------+  +-----------+
                            |               |
                            v               v
                    +------------------------------+
                    |    Intervention Required     |
                    +------------------------------+
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
    +-----------+   +-------------+   +----------+
    | Clarify   |   | Fix Blocker |   | Split    |
    | Mission   |   | Manually    |   | Task     |
    +-----------+   +-------------+   +----------+
```

### When to Intervene

| Situation | Action |
|-----------|--------|
| **STUCK after 2 cycles** | Review escalation packet, clarify requirements |
| **Same BLOCKER 3+ times** | Manual fix or architecture change needed |
| **SAFETY_VIOLATION** | Review what Builder tried to do, adjust constraints |
| **Builder schema fails** | Check if Builder is outputting non-JSON |
| **Gate timeout** | Optimize tests or increase timeout |
| **MAX_CYCLES reached** | Task too complex, split into smaller tasks |

### Reading Escalation Packets

```bash
# Unzip packet
unzip escalation_20260123_210000.zip -d /tmp/escalation

# Review contents
cat /tmp/escalation/ESCALATION_SUMMARY.md
cat /tmp/escalation/current_qa_report.json | jq
diff /tmp/escalation/qa_report_cycle_*.json
```

---

## 16. Troubleshooting

### "claude: command not found"

```bash
npm config get prefix
export PATH="$HOME/.npm-global/bin:$PATH"
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
```

### "Task already running"

```bash
# Check if actually running
ps aux | grep labloop

# If stale, remove lock files
rm tasks/my_task/.lock tasks/my_task/.pid
```

### "Email failed: Username and Password not accepted"

You're using regular password instead of App Password:
1. https://myaccount.google.com/security - Enable 2FA
2. https://myaccount.google.com/apppasswords - Create app password
3. Update `~/.labloop/config` with 16-char password

### "Builder output failed schema validation"

Builder didn't output proper JSON. Check:
```bash
cat tasks/my_task/_builder_stdout.json
```

Common causes:
- Builder output text before/after JSON
- Missing required fields
- Invalid status value

**v2.1 Fix**: The JSON extraction now handles markdown code blocks anywhere in output:
```bash
# v2.0 only matched: ^```json (start of line)
# v2.1 matches: ```json anywhere in text
```

### "QA_REPORT.json is empty or missing"

Codex failed to produce valid output. In v2.1, a fallback report is automatically created:
```json
{
  "verdict": "FAIL",
  "cycle": N,
  "early_exit": true,
  "summary": "QA (Codex) failed to produce valid output - check logs",
  "blockers": [{"severity": "BLOCKER", "title": "QA system failure"}],
  ...
}
```

Check:
```bash
cat tasks/my_task/loop.log | grep -A 20 "Running QA"
```

### "Builder/QA timed out"

v2.1 added timeouts to prevent infinite hangs:
- Builder (Claude): 20 minutes
- QA (Codex): 15 minutes
- QA (Gemini): 10 minutes

If tasks consistently timeout:
1. Split into smaller, more focused tasks
2. Simplify the gate command
3. Check if external services are slow/unavailable

### "Primary QA agent (codex) failed, trying fallback (gemini)..."

This message indicates Codex failed (rate limit, timeout, error) and Lab Loop is using Gemini as fallback.

**Common causes:**
- Codex rate limits exceeded
- Codex API unavailable
- Codex output validation failed

**What happens:**
1. Gemini receives a condensed ~10KB prompt (not the full 48KB bundle)
2. Prompt is passed via stdin pipe (not CLI arguments)
3. Gemini produces QA report with same schema

**If Gemini also fails:**
- Check `loop.log` for "Gemini prompt size" and "Gemini raw output"
- Verify `GEMINI_API_KEY` is set (or Gemini CLI is authenticated)
- Check Gemini CLI is installed: `which gemini`

### "Gemini taking too long / timing out"

v2.1.2 fixed a bug where large prompts were passed as CLI arguments causing hangs.

**Fixed behavior:**
```bash
# Old (broken): prompt as argument - could exceed shell limits
gemini --yolo "$(cat prompt.txt)"

# New (fixed): prompt via stdin pipe
cat prompt.txt | gemini --yolo
```

If still timing out:
1. Check prompt size in logs: "Gemini prompt size: X bytes"
2. Condensed prompts should be ~10KB (not 48KB+)
3. Increase timeout: `GEMINI_TIMEOUT` environment variable

### "Script exits unexpectedly after first increment"

v2.1 fixed a bash arithmetic issue where `((var++))` returns exit code 1 when incrementing from 0 with `set -e`:
```bash
# v2.0 (broken with set -e):
((GATES_SKIPPED++))

# v2.1 (fixed):
GATES_SKIPPED=$((GATES_SKIPPED + 1))
```

### "SAFETY VIOLATION: Protected paths modified"

Builder tried to modify a protected file. Options:
1. Remove path from `PROTECTED_PATHS` if intentional
2. Clarify mission to avoid that file
3. Manually make the change

---

## 17. API Reference

### CLI Commands

```
labloop new <TASK_ID> [options]
  --repo PATH            Repository path (required)
  --gate CMD             Gate command
  --gate-fast CMD        Fast tier gate
  --gate-full CMD        Full tier gate
  --profile NAME         Use gate profile
  --list-profiles        Show profiles

labloop run <TASK_ID> [options]
  --dry-run              Simulate (1 cycle)
  --max-cycles N         Maximum iterations
  --tier fast|full       Gate tier (default: fast)
  --incremental          Track file changes
  --webhook URL          Webhook notifications
  --email ADDRESS        Email notifications
  --skip-preflight       Skip validation
  --version              Show version

labloop status <TASK_ID>
labloop list
labloop help
labloop version
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PASS - Task completed |
| 1 | ERROR - General error |
| 2 | STUCK - Human intervention needed |
| 3 | MAX_CYCLES - Limit reached |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_CYCLES` | 50 | Maximum loop iterations |
| `LABLOOP_EMAIL` | - | Default email recipient |
| `LABLOOP_WEBHOOK` | - | Default webhook URL |
| `LABLOOP_SMTP_USER` | - | SMTP username |
| `LABLOOP_SMTP_PASS` | - | SMTP password |
| `LABLOOP_SMTP_HOST` | smtp.gmail.com | SMTP server |
| `LABLOOP_SMTP_PORT` | 587 | SMTP port |
| `LABLOOP_CONFIG` | ~/.labloop/config | Config file path |
| `SAFETY_CONF` | config/safety.conf | Safety config path |

### Builder Report Schema

```json
{
  "status": "READY_FOR_QA|BLOCKED|ERROR",
  "cycle": 1,
  "summary": "Brief description",
  "issues_addressed": [
    {
      "severity": "BLOCKER",
      "original_title": "Issue title",
      "resolution": "How it was fixed",
      "files_modified": ["path/to/file"],
      "verified": true
    }
  ],
  "changed_files": [
    {"path": "file.py", "action": "modified", "lines_changed": 10}
  ],
  "commands_run": [
    {"command": "pytest", "exit_code": 0, "success": true}
  ],
  "gate_pre_check": {
    "ran_gate": true,
    "gate_passed": true,
    "gate_exit_code": 0
  },
  "notes_for_qa": ["Important note"],
  "confidence": "high|medium|low"
}
```

---

## 18. Best Practices

### Task Sizing

| Size | Cycles | Example |
|------|--------|---------|
| Small | 1-3 | Fix typo, add test |
| Medium | 3-10 | Implement feature, fix bug |
| Large | 10-20 | Refactor module |
| Too Large | 20+ | Split into smaller tasks |

### Gate Command Design

```bash
# Good: Fast feedback
pytest tests/ -x -q

# Good: Comprehensive
pytest tests/ --cov=src --cov-fail-under=80

# Bad: Too slow for iteration
pytest tests/ -v --cov-report=html --cov-report=xml
```

### Mission Writing

**Do:**
- Be specific about what needs to change
- Include file paths when known
- Reference existing tests
- Define clear acceptance criteria

**Don't:**
- Be vague ("make it better")
- Include multiple unrelated tasks
- Skip acceptance criteria
- Forget gate command

### Running in Production

1. Use `--tier full` for final validation
2. Always use persistence (tmux/systemd)
3. Enable email notifications
4. Keep `MAX_CYCLES` reasonable (20-50)
5. Review escalation packets promptly

---

## 19. Contributing

### Adding Gate Profiles

1. Create `profiles/gate-<name>.sh`
2. Make executable: `chmod +x profiles/gate-<name>.sh`
3. Follow pattern:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   echo "=== Gate: <Name> ==="
   # Validation logic
   echo "=== Gate: <Name> PASSED ==="
   ```

### Reporting Issues

File issues at the repository with:
- Lab Loop version (`labloop version`)
- Error message
- Steps to reproduce
- Relevant log snippets

---

## 20. E2E Validation Scenario (MathLib)

Before using Lab Loop on production tasks, validate the loop mechanics with a deterministic test scenario.

### Purpose

The MathLib E2E test creates a simple repo with **intentional bugs** that converge to PASS in 1-2 cycles. This validates:
- Builder can read QA reports and fix issues
- Gate verification runs correctly
- QA (Codex) produces valid reports
- Loop terminates on success

### Setup

```bash
# Create MathLib scenario directory
mkdir -p /home/$USER/bookkeeping/labloop_scenarios/mathlib_e2e

# Create intentionally buggy mathlib/core.py
cat > mathlib_e2e/mathlib/core.py << 'EOF'
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b):
    if b == 0: raise ZeroDivisionError("Cannot divide by zero")
    return a // b  # BUG: should be a / b (true division)
# NOTE: gcd function intentionally missing
EOF

# Create tests that will fail
cat > mathlib_e2e/tests/test_core.py << 'EOF'
import pytest
from mathlib.core import add, subtract, multiply, divide

class TestDivide:
    def test_divide_float(self):
        assert divide(5, 2) == 2.5  # Will fail: returns 2

class TestGcd:
    def test_gcd_exists(self):
        from mathlib.core import gcd  # Will fail: ImportError
EOF
```

### Create Lab Loop Task

```bash
labloop new e2e_mathlib_phase1 \
  --repo /home/$USER/bookkeeping/labloop_scenarios/mathlib_e2e \
  --gate "pytest tests/ -v"
```

### Expected Behavior

1. **Cycle 1**: Builder fixes `divide()` (change `//` to `/`) and implements `gcd()`
2. **Cycle 1-2**: QA verifies all tests pass
3. **Result**: PASS in ≤2 cycles

### Phase 2 (Chained Mission)

After Phase 1 passes, test chained missions:
```bash
# Phase 2: Add lcm() function
labloop new e2e_mathlib_phase2 \
  --repo /home/$USER/bookkeeping/labloop_scenarios/mathlib_e2e \
  --gate "pytest tests/ -v"

# Write mission to add lcm() using gcd()
```

---

## 21. v2.1 Technical Details

### JSON Extraction Algorithm

```bash
# v2.1 JSON extraction from Builder output
if echo "$file_content" | grep -q '```json'; then
  # Extract content between ```json and ``` (anywhere in text)
  json_content=$(echo "$file_content" | sed -n '/```json/,/```/p' | sed '1d;$d')
elif echo "$file_content" | grep -q '```'; then
  # Try generic code block
  json_content=$(echo "$file_content" | sed -n '/```/,/```/p' | sed '1d;$d')
else
  # Raw JSON object extraction
  json_content=$(echo "$file_content" | grep -Pzo '\{[\s\S]*\}' | tr '\0' '\n')
fi
```

### QA Report Schema (v2.1)

Required fields now include `early_exit`:
```json
{
  "required": [
    "verdict",
    "cycle",
    "early_exit",      // NEW in v2.1
    "summary",
    "blockers",
    "majors",
    "minors",
    "spec_compliance",
    "next_actions_for_builder",
    "evidence"
  ]
}
```

### Agent Timeout Implementation

```bash
# Builder (Claude) - 20 minute timeout
timeout 1200 bash -c "cat '$bundle' | claude $claude_opts '$prompt'" > "$output"

# QA (Codex) - 15 minute timeout
timeout 900 /root/.npm-global/bin/codex exec \
  --cd "$REPO_DIR" \
  --output-schema "$SCHEMA" \
  --output-last-message "$REPORT" \
  - < "$qa_input"
```

### Codex Fallback Report

When Codex fails/times out, Lab Loop creates a valid fallback:
```json
{
  "verdict": "FAIL",
  "cycle": N,
  "early_exit": true,
  "summary": "QA (Codex) failed to produce valid output - check logs",
  "blockers": [{
    "severity": "BLOCKER",
    "title": "QA system failure",
    "details": "Codex did not produce valid output"
  }],
  "majors": [],
  "minors": [],
  "spec_compliance": {},
  "next_actions_for_builder": [],
  "evidence": []
}
```

---

## 22. v2.1.2 Technical Details (Gemini QA Fallback)

### QA Agent Cascade

Lab Loop v2.1.2 implements a fallback cascade for QA:

```
+--------------------------------------------------+
|               QA AGENT CASCADE                    |
+--------------------------------------------------+
|                                                   |
|  1. Try Codex (primary)                          |
|     - 15 min timeout                             |
|     - Full QA input bundle                       |
|     - Schema-enforced output                     |
|                    |                             |
|                    v                             |
|     +------- Success? -------+                   |
|     |                        |                   |
|    YES                       NO                  |
|     |                        |                   |
|     v                        v                   |
|  Use Codex            2. Try Gemini (fallback)  |
|  report                  - 10 min timeout        |
|                          - Condensed prompt      |
|                          - stdin delivery        |
|                                 |                |
|                                 v                |
|                    +------- Success? -------+    |
|                    |                        |    |
|                   YES                       NO   |
|                    |                        |    |
|                    v                        v    |
|                 Use Gemini            3. Generate|
|                 report                fallback   |
|                                       report     |
+--------------------------------------------------+
```

### Gemini Prompt Condensation

Instead of the full 48KB QA input bundle, Gemini receives a condensed ~10KB prompt:

```bash
# Condensed prompt structure
{
  "role": "QA agent evaluating software changes",
  "gate_result": {
    "exit_code": 0|1,
    "output": "last 100 lines of gate output"
  },
  "builder_report": "first 100 lines of BUILDER_REPORT.md",
  "acceptance_criteria": "first 80 lines of acceptance.md",
  "instructions": "Produce JSON with verdict, blockers, majors, minors..."
}
```

### Stdin Prompt Delivery

Large prompts cannot be passed as shell arguments (ARG_MAX limit ~2MB, but causes issues earlier).

**v2.1.2 Implementation:**
```bash
# Create temp prompt file
gemini_prompt=$(mktemp)
generate_condensed_prompt > "$gemini_prompt"

# Log prompt size for debugging
log "Gemini prompt size: $(wc -c < "$gemini_prompt") bytes"

# Pass via stdin pipe (not argument)
timeout "$GEMINI_TIMEOUT" bash -c "cat '$gemini_prompt' | '$GEMINI_CLI_PATH' --yolo"
```

### Auto early_exit Field

If Gemini output is missing the required `early_exit` field:
```bash
# Check and add if missing
if ! echo "$json_content" | jq -e '.early_exit' > /dev/null 2>&1; then
  json_content=$(echo "$json_content" | jq '. + {"early_exit": false}')
fi
```

### Debugging Gemini Issues

Enable debug output in loop.log:
```bash
# Look for these log entries:
[DEBUG] Gemini prompt size: 10234 bytes
[DEBUG] Gemini raw output (first 500 chars): ...
[DEBUG] Extracted JSON: {"verdict": "FAIL", ...}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_CLI_PATH` | `$(which gemini)` | Path to Gemini CLI |
| `GEMINI_TIMEOUT` | `600` | Gemini timeout in seconds (10 min) |
| `GEMINI_API_KEY` | (required) | Google API key for Gemini |

---

## 23. v3.0 Stabilization Features

### Overview

v3.0 focuses on stability and reliability to prevent common failures that occurred during development.

### Project Profile System (`.labloop.yaml`)

Each project can have a `.labloop.yaml` file in its root directory that customizes Lab Loop behavior:

```yaml
# Example: /home/zaks/zakops-backend/.labloop.yaml
project:
  name: zakops-backend
  description: "ZakOps Backend API and Services"

# Environment setup
environment:
  venv_path: "./venv"
  python_version: "3.12"
  auto_activate_venv: true
  working_dir: "/home/zaks/zakops-backend"

# Gate configuration
gates:
  default_cmd: "./scripts/bring_up_tests.sh"
  timeout_seconds: 300

# Safety limits (tuned for this project)
limits:
  max_files_per_cycle: 30
  max_lines_per_cycle: 2000
  max_uncommitted_files: 100
  stuck_consecutive_cycles: 3

# Auto-management
auto:
  commit_artifacts: true
  artifact_patterns:
    - "gate_artifacts/**/*.json"
    - "gate_artifacts/**/*.log"
  commit_message: "chore(gates): Auto-commit gate artifacts [skip ci]"

# Known flaky tests to skip
skip_tests:
  - "tests/contract/test_sse_contract.py::TestSSEContract"
  - "tests/e2e/test_event_streaming.py::TestSSEEvents"

# Services that should be running
required_services:
  - name: "Deal API"
    health_url: "http://localhost:8090/health"
    optional: false
  - name: "Langfuse"
    health_url: "http://localhost:3001/api/public/health"
    optional: true

# QA configuration
qa:
  primary_agent: "codex"
  fallback_agent: "gemini"
  strict_mode: true

# Notifications
notifications:
  email: "user@example.com"
  on_pass: true
  on_fail: true
  on_stuck: true
```

Profile settings override global defaults when loaded.

### Health Check Tool (`labloop-doctor`)

Run before Lab Loop to diagnose and fix issues:

```bash
# Basic health check
labloop-doctor

# Check specific task
labloop-doctor phase2_mvp_build

# Auto-fix issues
labloop-doctor phase2_mvp_build --fix
```

**Checks performed:**
- Claude CLI installed and version
- Codex CLI availability
- Gemini CLI and API key
- jq/yq installed
- Stale lock files (>60 minutes old)
- Stuck Claude processes from previous days
- Task-specific: config.env, REPO_DIR, venv, git status, gate script
- Service health: Deal API, Langfuse, etc.

**Example output:**
```
========================================
Lab Loop Doctor v3.0.0
========================================

Checking Claude CLI...
[OK] Claude CLI installed: 2.1.19 (Claude Code)
Checking Codex CLI...
[OK] Codex CLI available
Checking Gemini CLI...
[OK] Gemini CLI available with API key
Checking jq...
[OK] jq installed
Checking for stale locks...
[OK] No stale locks found

Task-specific checks for: phase2_mvp_build
----------------------------------------
[OK] Task directory exists
[OK] config.env exists
[OK] REPO_DIR exists: /home/zaks/zakops-backend
[OK] Project profile found: /home/zaks/zakops-backend/.labloop.yaml
[OK] Virtual environment found
[WARN] 13 uncommitted changes (within limits)
[OK] Gate script exists
[OK] No active lock

Service health checks...
----------------------------------------
[OK] Deal API (localhost:8090) is healthy
[OK] Langfuse (localhost:3001) is healthy

========================================
Summary
========================================
[OK] All checks passed! Lab Loop is ready to run.
```

### Auto-Commit Artifacts

When `auto.commit_artifacts: true` in project profile, Lab Loop automatically commits gate artifacts after each cycle:

```bash
# After gates run successfully
[2026-01-24T20:12:06Z] Auto-committing 12 artifact changes...
[main 8185743] chore(gates): Auto-commit gate artifacts [skip ci]
 12 files changed, 16 insertions(+), 16 deletions(-)
[2026-01-24T20:12:06Z] Artifacts committed successfully
```

This prevents diff limit violations caused by accumulating artifact files.

### Enhanced Preflight Checks

v3.0 adds enhanced preflight checks beyond the standard ones:

1. **Virtual environment detection** - Finds `venv/` or `.venv/`
2. **Python syntax validation** - Runs `py_compile` on source files
3. **Stale lock cleanup** - Removes locks from dead processes
4. **Uncommitted change warning** - Alerts if exceeding threshold

### Error Recovery

v3.0 automatically attempts recovery for common errors:

```bash
# Diff limit exceeded
[2026-01-24T20:10:00Z] SAFETY WARNING: Diff limits exceeded - attempting recovery...
[2026-01-24T20:10:00Z] Attempting recovery: Auto-committing to reset diff baseline...
[2026-01-24T20:10:01Z] Recovery successful - diff limits now within bounds

# Stale lock
[2026-01-24T20:10:00Z] Attempting recovery: Removing stale lock...

# Builder timeout
[2026-01-24T20:10:00Z] Attempting recovery: Builder timed out, will retry with fresh context...
```

### Builder Hang Fix (v2.1.4)

Fixed critical bug where Claude CLI would hang indefinitely:

**Root cause:** Dual-input confusion - piping stdin AND passing prompt argument:
```bash
# BROKEN (v2.1.3 and earlier)
cat bundle | claude -p "follow instructions above"
```

**Fix:** Combined into single stdin input:
```bash
# FIXED (v2.1.4+)
{
  cat "$bundle"
  echo "=== BUILDER INSTRUCTIONS ==="
  echo "Follow the instructions above..."
} > "$combined_input"

claude -p < "$combined_input"
```

### Recommended Workflow

```bash
# 1. Run doctor first
labloop-doctor my_task --fix

# 2. Start the loop
./bin/labloop.sh my_task

# 3. Monitor progress
tail -f tasks/my_task/loop.log

# 4. Check status
labloop status my_task
```

---

## Acknowledgments

- **Claude Code** by Anthropic - Builder agent
- **Codex** by OpenAI - QA agent (primary)
- **Gemini** by Google - QA agent (fallback)
- **ZakOps Engineering** - Architecture and implementation

---

*Lab Loop v3.0.0 - World-class automated QA/Builder feedback loop with project profiles, health checks, and error recovery*

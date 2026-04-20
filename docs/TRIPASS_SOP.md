# TriPass Pipeline — Standard Operating Procedure

## Version: 1.0.0
## Date: 2026-02-09

---

## What Is TriPass?

TriPass is a multi-agent pipeline orchestrator that runs three AI agents (Claude Code, Gemini CLI, Codex CLI) in parallel for independent investigation, followed by structured cross-review and consolidation. It is a native V5PP capability integrated with the existing gate system, memory system, hooks, and bookkeeping infrastructure.

**Core value:** Three independent perspectives on the same problem, with cryptographic proof that no information is lost during consolidation.

---

## How to Run the Pipeline

### Prerequisites

1. At least one CLI agent available (Claude, Gemini, or Codex)
2. Templates initialized: `make tripass-init`
3. A mission file (Markdown) describing the investigation task
4. API keys set: `GEMINI_API_KEY` in environment (via `~/.bashrc`)
5. Model config: `~/.tripass/models.conf` (created automatically, edit to change models)

### Quick Start

```bash
# From monorepo root (/home/zaks/zakops-agent-api)

# 1. Initialize (first time only)
make tripass-init

# 2. Run a forensic pipeline
make tripass-run MISSION=/path/to/mission.md MODE=forensic

# 3. Check status
make tripass-status

# 4. View a specific run
make tripass-status RUN_ID=TP-20260209-143000

# 5. Re-run gates on a completed run
make tripass-gates RUN_ID=TP-20260209-143000
```

### Direct Script Usage

```bash
# Full help
bash tools/tripass/tripass.sh help

# Run with options
bash tools/tripass/tripass.sh run mission.md --mode design --repos /home/zaks/zakops-agent-api

# Generate-only mode (creates prompts without executing agents)
bash tools/tripass/tripass.sh run mission.md --generate-only

# Skip Meta-QA pass
bash tools/tripass/tripass.sh run mission.md --skip-pass4

# Override models for a single run
bash tools/tripass/tripass.sh run mission.md \
  --claude-model opus \
  --gemini-model gemini-3-pro-preview \
  --codex-model gpt-5.3-codex
```

### Model & Timeout Configuration

Models and timeouts are configured in `~/.tripass/models.conf`:

```bash
# === Models ===
CLAUDE_MODEL=opus
GEMINI_MODEL=gemini-3-pro-preview
CODEX_MODEL=gpt-5.3-codex

# === Timeouts (seconds) ===
DESIGN_TIMEOUT=30000    # 8h 20m — deep architectural reviews
FORENSIC_TIMEOUT=1800   # 30m — focused codebase investigation
IMPLEMENT_TIMEOUT=1800  # 30m — code generation tasks
```

**Priority order** (highest wins):
1. CLI flags (`--claude-model`, `--gemini-model`, `--codex-model`)
2. Config file (`~/.tripass/models.conf`)
3. Hardcoded fallbacks in script

When new models are released, update `~/.tripass/models.conf` — no script changes needed.

### Content Pre-Loading (Design Mode)

For design-mode runs reviewing large specs, pre-load key documents directly into prompts:

```bash
# Pre-load spec + innovation master into all agent prompts
make tripass-run MISSION=mission.md MODE=design \
  INLINE_FILES=/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md,/home/zaks/bookkeeping/docs/COL-DESIGN-INNOVATION-MASTER.md

# Direct script usage
bash tools/tripass/tripass.sh run mission.md --mode design \
  --inline-files /path/to/spec.md,/path/to/other.md
```

**Why**: Agents (especially Codex) may not have read access to files outside their sandbox. Pre-loading inlines the file content directly into the prompt, eliminating file I/O timeout waste.

---

## Prerequisites by Mode

### Forensic Mode
- **Required:** At least one CLI agent (Claude, Gemini, or Codex)
- **Optional:** None — forensic mode works with all default tools

### Design Mode
- **Required:** At least one CLI agent
- **Timeout:** 30000s (8h 20m) per agent per pass — design reviews of large specs need this
- **Recommended:** Use `--inline-files` to pre-load key documents into prompts (avoids Codex sandbox file access issues and saves all agents time)
- Design-mode runs benefit from the frontend design standards embedded in `.claude/rules/design-system.md`. This rule is automatically loaded when Claude Code works on dashboard component files. No additional prerequisites are required
  - **What it adds:** Project-specific architectural conventions (Promise.allSettled, import discipline, CSS layer rules) and general frontend design quality standards (typography, color, motion, spatial composition)
  - **Impact:** When present, Claude Code produces richer design analysis for frontend-focused missions. If the rule file is missing, the orchestrator logs a warning in MASTER_LOG.md

### Implement Mode
- **Required:** At least one CLI agent
- **Optional:** None — implementation planning uses standard codebase analysis

### All Modes
- CLI availability is verified at pipeline start and recorded in `00_context/cli_discovery.md`
- Missing CLIs trigger graceful degradation to generate-only mode for that agent
- The pipeline never fails due to a missing CLI — it degrades

---

## How to Interpret Outputs

### Run Directory Structure

```
_tripass_runs/<RUN_ID>/
├── 00_context/          # Mission copy, CLI versions, inline context (if pre-loaded)
├── 01_pass1/            # 3 independent agent reports + prompts
├── 02_pass2/            # 3 cross-reviews + prompts
├── 03_pass3/            # Consolidation prompt + copy of final master
├── 04_metaqa/           # Meta-QA verdict (if Pass 4 ran)
├── EVIDENCE/            # Hashes, gate results, append-only log
├── WORKSPACE.md         # All pass outputs appended in order
├── MASTER_LOG.md        # Timestamped event log
└── FINAL_MASTER.md      # The actionable deliverable
```

### Key Files

| File | Purpose |
|------|---------|
| `FINAL_MASTER.md` | The consolidated deliverable — read this first |
| `EVIDENCE/gates.md` | Gate results (T-1 through T-6) |
| `MASTER_LOG.md` | Timeline of pipeline events |
| `WORKSPACE.md` | Complete append-only record of all agent outputs |
| `00_context/cli_discovery.md` | Which agents and plugins were available |

### Reading the Final Master

The final master contains:
- **CONSOLIDATED FINDINGS** — Deduplicated issues with all 5 required fields and agent attribution
- **DISCARDED ITEMS** — Findings intentionally excluded with documented reasons
- **DRIFT LOG** — Out-of-scope observations (not actionable in this mission)
- **ACCEPTANCE GATES** — Builder-enforceable gates for implementing findings

### Gate Results

| Gate | What It Checks |
|------|---------------|
| T-1 | Append-only integrity (no data removed from workspace/log) |
| T-2 | Output completeness (all expected files exist) |
| T-3 | Structural validity (headers, required fields) |
| T-4 | Drift detection (out-of-scope findings below threshold) |
| T-5 | No-drop verification (Meta-QA confirms nothing lost) |
| T-6 | Memory sync (pointers and change log updated) |

---

## How to Add a New Pipeline Mode

1. Templates are at `/home/zaks/bookkeeping/docs/_tripass_templates/`
2. The mode name is passed as `{{MODE}}` in all templates
3. To add a new mode (e.g., `security`):
   - The existing templates handle any mode — they pass the mode name through to agents
   - If you need mode-specific prompt instructions, edit the templates to add conditional sections based on `{{MODE}}`
   - Add the new mode name to the `case` validation in `tripass.sh` (search for `forensic|design|implement`)
4. If the new mode has a recommended plugin, document it in the "Prerequisites by Mode" section above

---

## How to Rerun a Failed Pass

### If an agent failed during Pass 1:
1. The prompt is saved at `01_pass1/<agent>_prompt.md`
2. Run the agent manually with the prompt
3. Save output to `01_pass1/<agent>_report.md`
4. Re-run gates: `make tripass-gates RUN_ID=<id>`

### If Pass 3 consolidation was incomplete:
1. The full workspace with all prior outputs is in `WORKSPACE.md`
2. The consolidation prompt is at `03_pass3/consolidation_prompt.md`
3. Run Claude manually with the prompt
4. Save output to `FINAL_MASTER.md`
5. Re-run gates: `make tripass-gates RUN_ID=<id>`

### If the pipeline was interrupted mid-run:
1. Check `MASTER_LOG.md` to see which pass completed last
2. The lock file at `/tmp/tripass.lock` may need manual removal
3. Prompts for incomplete passes are already generated — execute them manually
4. The stop hook logs interrupted runs to the session log for next-session pickup

---

## V5PP Integration Points

### Gate System
- TriPass gates (T-1 through T-6) are a new gate group alongside existing Gates A-H
- They follow the same tiered convention (checked during and after pipeline)
- Gate results are written to `EVIDENCE/gates.md` in the same tabular format

### Memory System
- Completed runs are recorded via Gate T-6 (updates TRIPASS_LATEST_RUN.md)
- memory-sync.sh gathers TriPass metadata (run count, latest run ID) in its fact pass
- Session log entries include TriPass state

### Hook Pipeline
- The stop hook checks for active TriPass runs (lock file at `/tmp/tripass.lock`)
- If a session ends mid-pipeline, the stop hook logs the interrupted state
- memory-sync captures TriPass metadata alongside existing facts

### Bookkeeping
- All outputs are under `/home/zaks/bookkeeping/docs/_tripass_runs/`
- CHANGES.md is updated by Gate T-6 after successful runs
- TRIPASS_LATEST_RUN.md provides quick access to the most recent run

### Makefile
- `make tripass-init` — Initialize templates and verify CLIs
- `make tripass-run MISSION=<file>` — Execute a pipeline
- `make tripass-status` — Show all runs or a specific run
- `make tripass-gates RUN_ID=<id>` — Re-run gates

---

## Guardrails

1. TriPass produces Markdown only — no production code modifications
2. Gemini and Codex have no write access — they receive prompts and produce text
3. Append-only discipline on WORKSPACE.md and MASTER_LOG.md with SHA256 verification
4. The existing 4-agent topology is unchanged — TriPass extends, not replaces
5. All paths use `/home/zaks/...` — WSL-safe

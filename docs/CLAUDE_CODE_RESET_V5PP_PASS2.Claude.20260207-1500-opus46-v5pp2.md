# CLAUDE CODE RESET V5→V5PP — PASS 2 Red-Team Review

```
AGENT IDENTITY
agent_name:    Claude (opus46)
run_id:        20260207-1500-opus46-v5pp2
timestamp:     2026-02-07T15:00:00Z
pass:          2 of 3 (Red-Team Review & Synthesis)
inputs_read:   MISSION-INFRA-AWARENESS-V5-CLAUDE-CODE-RESET.md (1,112 lines)
               CLAUDE_CODE_RESET_V5PP_PASS1_IDEA_POOL.md (399 lines, 4 contributions)
               CLAUDE_CODE_RESET_V5PP_PASS2_REVIEW_LEDGER.md (152 lines, 2 Codex reviews)
repo_verified: YES — actual filesystem state checked against all claims
```

---

## Executive Summary

Pass 1 produced strong directional ideas but contains **4 critical structural errors** that would cause implementation failure:

1. **Config location mismatch**: ALL proposals assume repo-level `.claude/` but ZakOps config lives at `~/.claude/` (user-level). No repo has its own `.claude/` directory.
2. **CLAUDE.md truncation myth**: The "200-line truncation" applies to `MEMORY.md`, NOT `CLAUDE.md`. CLAUDE.md files are loaded hierarchically without documented truncation. The "max 150 lines" constraint is cargo-culted from the wrong file type.
3. **Managed settings overkill**: ZakOps is a single-developer project. `/etc/claude-code/managed-settings.json` is enterprise infrastructure for enforcing org-wide policy across teams. It adds zero value here and adds operational complexity.
4. **PostToolUse auto-validate would be catastrophic**: Running `make validate-all` after every Edit/Write would trigger `validate-live` (which requires ALL services running) on every file save. Average latency: 15-30 seconds per tool call. The mission would grind to a halt.

---

## Verified Ground Truth (Filesystem Scan 2026-02-07)

| Asset | Actual State | Notes |
|-------|-------------|-------|
| Config location | `/home/zaks/.claude/` | **USER-LEVEL, not repo-level** |
| CLAUDE.md files | 6 files, 42-66 lines each | /home/zaks/, zakops-agent-api/, zakops-backend/, .claude/, bookkeeping/, Zaks-llm/ |
| .claude/commands/ | 12 files (254 lines) | All at ~/.claude/commands/ |
| .claude/skills/ | 7 dirs (466 lines) | All at ~/.claude/skills/ |
| .claude/hooks/ | 2 scripts (53 lines) | pre-edit.sh + post-edit.sh |
| .claude/agents/ | **0** at user level | 4 exist in Zaks-llm/.claude/agents/ (no one referenced these) |
| .claude/rules/ | **DOES NOT EXIST** | — |
| .mcp.json | **DOES NOT EXIST** | Anywhere in any repo |
| settings.json | Hooks only (30 lines) | PreToolUse + PostToolUse for Edit/Write |
| settings.local.json | 69 lines | **50+ Bash allow patterns, ZERO deny rules** |
| Deny rules | **ZERO** | Empty array in settings.local.json |
| Generated .ts files | 2 files, 7,731 lines | api-types.generated.ts (5,502), agent-api-types.generated.ts (2,229) |
| packages/contracts/ | EXISTS, 4 OpenAPI specs | zakops-api.json (180KB), agent-api.json (74KB), rag-api.json (7KB), agent-events.schema.json (4KB) |
| Makefile sync targets | ALL EXIST | sync-types, sync-backend-models, sync-agent-types, sync-rag-models, sync-all-types, validate-local, validate-live, validate-all |

---

## Section 1: Ideas to KEEP (with corrections)

### KEEP-1: Permission Deny for Generated Files (All agents agree)
**Verdict: STRONG KEEP — highest ROI single change.**
Currently ZERO deny rules protect 7,731 lines of generated code. One JSON edit fixes this.
**Correction**: Must go in `~/.claude/settings.json` (user-level), NOT repo-level `.claude/settings.json` which doesn't exist.

### KEEP-2: Path-Scoped Rules (Claude)
**Verdict: KEEP — correct 2026 pattern.**
**Correction**: Must create `~/.claude/rules/` directory first. OR create repo-level `.claude/` directories (which requires a decision about config architecture that no one has addressed).

### KEEP-3: PreToolUse Hook Blocking Generated File Edits (Claude)
**Verdict: KEEP as defense-in-depth alongside deny rules.**
Already have pre-edit.sh (28 lines) as a foundation — extend it, don't create a parallel system.

### KEEP-4: CLAUDE.md Content Restructure (All agents agree on principle)
**Verdict: KEEP the idea of moving domain knowledge into skills/rules, but REJECT the 150-line hard limit.**
The truncation concern is about MEMORY.md, not CLAUDE.md. Current CLAUDE.md files are 42-66 lines — the problem is they're *too sparse*, not too long.

### KEEP-5: additionalDirectories for Cross-Repo Access (Claude)
**Verdict: KEEP — solves a real problem.**
**Correction**: The V5 mission prompt Fix 7 explicitly mandates "zero hardcoded absolute paths." The proposed config uses `/home/zaks/zakops-backend/` etc. This is a direct conflict. Use `--add-dir` at invocation time or relative paths instead.

### KEEP-6: Contract-Checker Subagent (Claude)
**Verdict: CONDITIONAL KEEP.**
4 agents already exist in `/home/zaks/Zaks-llm/.claude/agents/` (zakops-prime, agent-config-consultant, log-monitor, research-gemini). No one referenced these. New agents should complement, not duplicate.

### KEEP-7: Discovery Step 0.8 — Config Audit (Codex + Claude agree)
**Verdict: STRONG KEEP.** But fix the path: `~/.claude/` not `$MONOREPO_ROOT/.claude/`.

### KEEP-8: CLI Determinism Flags for Automation (Codex)
**Verdict: KEEP for CI/CD pipelines.** `--permission-mode`, `--max-turns`, `--output-format json`.

---

## Section 2: Ideas That Are TRAPS (Reject)

### REJECT-1: PostToolUse Auto-Validate on Every Edit/Write
**Source**: Claude Pass 1, Codex Pass 2 (second review) endorses "PostToolUse trigger make auto-fix"
**Why TRAP**:
- `make validate-all` depends on `validate-live` which requires ALL services running.
- Even `validate-local` takes 5-15 seconds (TypeScript compilation + multiple grep checks).
- Running this after EVERY file edit means: edit 10 files = 50-150 seconds of validation overhead.
- Boris Cherny's pattern is about **giving Claude a way to verify** — meaning validation at task boundaries, not after every keystroke.
**FIX**: Use a `Stop` hook (runs once when Claude finishes responding) instead of PostToolUse. Or scope PostToolUse to contract-adjacent files only with tight matchers.

### REJECT-2: Managed Settings (`/etc/claude-code/managed-settings.json`)
**Source**: Codex (both runs), Claude Pass 1
**Why TRAP**:
- Managed settings enforce org-wide non-overridable policy for TEAMS.
- ZakOps is a single developer. There is no "org" to manage.
- Requires root/admin to modify. Debugging config issues becomes `sudo vim /etc/claude-code/managed-settings.json` instead of editing a local file.
- Zero benefit over project-level settings.json for this use case.
**FIX**: Use `~/.claude/settings.json` (already exists) with deny rules. Skip managed settings entirely.

### REJECT-3: Dynamic Context Script (`context.sh`)
**Source**: Gemini
**Why TRAP**:
- Non-deterministic output (service health, git status change between runs).
- Hooks already exist natively — SessionStart hook can display status without a custom script.
- Adds a maintenance burden for a bash script that replicates built-in Claude Code functionality.
**FIX**: SessionStart hook if dynamic status is needed. Path-scoped rules for static context.

### REJECT-4: DriftOps Auto-Commit Bots
**Source**: Gemini
**Why TRAP**:
- Auto-commits without human review = amplified errors at git speed.
- Git lock contention during concurrent work (user confirmed `zakops-backend-postgres-1` already has restart loop issues — don't add more moving parts).
- Pre-commit hooks BLOCK drift; auto-commit bots HIDE drift.
**FIX**: Keep existing pre-commit hooks + add spec-vs-generated freshness checks.

### REJECT-5: `make auto-fix` Composite Target
**Source**: Gemini, Codex Pass 2 (second review) partially endorses
**Why TRAP**:
- "auto-fix" implies idempotent correction, but `make sync-all-types` can change 7,731+ lines of generated code.
- Hides which sync target actually ran and what changed.
- Developers need to know WHICH surface drifted, not just "everything was auto-fixed."
**FIX**: Keep individual `make sync-*` targets. Add a `make diagnose-drift` that REPORTS which surfaces are stale without auto-fixing.

### REJECT-6: OpenAI Evals Gate
**Source**: Codex (both runs)
**Why TRAP**:
- OpenAI Evals is a separate ecosystem (Python, different API, different auth).
- No concrete eval definition proposed — just "add eval gate."
- The existing gate system (GATE 1-9 in V5) already provides acceptance criteria.
- For a single-developer project, the overhead of maintaining an eval harness exceeds its value.
**FIX**: Keep V5's GATE system. Add `make validate-enforcement` to CI. That IS the eval gate.

### REJECT-7: cc-hooks-ts (TypeScript Hook SDK)
**Source**: Claude Pass 1
**Why TRAP**:
- Adds a TypeScript build step to hook execution.
- Current hooks are 25-28 line bash scripts that work perfectly.
- Type-safety for hooks is solving a problem that doesn't exist at this scale.
**FIX**: Keep bash hooks. They're simple, fast, and debuggable.

### REJECT-8: Two-Tier Persistent Memory (memory-mcp)
**Source**: Claude Pass 1
**Why TRAP**:
- Requires running an MCP server (there is ZERO .mcp.json config currently).
- MEMORY.md already exists at `~/.claude/projects/` and works automatically.
- The "state.json + MCP search" tier adds operational complexity for marginal benefit.
**FIX**: Use existing MEMORY.md. Add PreCompact hook to preserve critical state (this part is fine).

---

## Section 3: Conflicts Between Agents

### CONFLICT-1: Config Location (Critical — blocks ALL implementation)
**Codex**: Proposes `.claude/settings.json` (implies repo-level)
**Claude**: Proposes `.claude/rules/`, `.claude/agents/` (implies repo-level)
**Gemini**: Doesn't address config location
**Reality**: All config is at `~/.claude/` (user-level). No repo has its own `.claude/` directory.

**Resolution**: DECIDE FIRST — either:
- (A) Create repo-level `.claude/` in zakops-agent-api/ (moves config closer to code, versionable in git)
- (B) Keep user-level `~/.claude/` (current state, simpler, works across all repos)
- (C) **RECOMMENDED**: Hybrid — repo-level `.claude/` for repo-specific config (rules, agents) + user-level for global settings (deny rules, hooks). Claude Code merges these hierarchically.

### CONFLICT-2: CLAUDE.md Size — "Too Long" vs "Too Short"
**V5 Mission**: Proposes 300+ line CLAUDE.md (Fix 1 template is ~180 lines of content)
**Pass 1 agents**: "Max 150 lines" / "split into constitution + skills"
**Reality**: Current files are 42-66 lines. They're too SHORT, not too long. The V5 content is needed — it should just live in the right place.

**Resolution**: Write a 120-150 line CLAUDE.md containing: project roots, services, quick-reference commands, pointers to skills/rules for details. Move the 7-surface table and dependency graph into `.claude/rules/contract-surfaces.md` with path-scoped activation. This is the right split, but NOT because of truncation — because of progressive disclosure.

### CONFLICT-3: Validation Strategy — Manual vs Automatic
**V5**: Manual `make validate-*` in Pre/Post Task Protocol
**Codex (v2 Pass 2)**: PostToolUse hook triggers `make auto-fix`
**Claude**: PostToolUse auto-validate on Edit/Write

**Resolution**: THREE TIERS:
1. **Pre-commit hook** (git level): Block commits with stale generated files — ALREADY EXISTS, extend it.
2. **Stop hook** (session level): Run `make validate-local` when Claude finishes responding — catches drift before declaring done.
3. **Manual protocol** (task level): `make validate-live` when services are running — keep from V5.

Do NOT use PostToolUse for validation. It runs on EVERY tool call.

### CONFLICT-4: additionalDirectories vs Portable Paths
**Claude Pass 1**: Proposes `additionalDirectories: ["/home/zaks/zakops-backend/", ...]`
**V5 Fix 7**: "Zero hardcoded absolute paths in Makefile"

**Resolution**: Use `--add-dir` at invocation time (CLI flag) rather than hardcoding in settings.json. Or use `additionalDirectories` with a comment that these must be updated if paths change. The Makefile portability rule is for CI reproducibility; the Claude Code settings are developer-local by definition.

---

## Section 4: Determinism Audit

| Idea | Deterministic? | CI-Safe? | Fix |
|------|---------------|----------|-----|
| `make validate-local` | YES | YES | Keep as CI gate |
| `make validate-live` | NO (requires services) | NO | Dev-only, never in CI |
| `make update-agent-spec` | NO (requires Agent API on 8095) | NO | Dev-only; commit spec artifact |
| PostToolUse auto-validate | NO (depends on service state) | N/A | Replace with Stop hook + validate-local |
| `context.sh` | NO (live state) | NO | Remove; use rules/hooks |
| SessionStart health check | NO (service availability varies) | N/A | OK for dev — display only, no blocking |
| Permission deny rules | YES (settings.json is static) | YES | Keep |
| Path-scoped rules | YES (static .md files) | YES | Keep |
| PreToolUse hook | YES (deterministic script) | YES | Keep |
| Spec freshness (file timestamps) | YES | YES | Keep — compare mtime of spec vs generated |

**Verdict**: All CI gates must use `validate-local` only. `validate-live` and `update-agent-spec` are dev-time-only operations. This distinction is missing from V5 and all Pass 1 proposals.

---

## Section 5: Safety Audit

### 5a: Current Exposure (Verified)
- **Deny rules**: ZERO. Empty array in settings.local.json.
- **Bash allowlisting**: `curl`, `docker`, `docker compose`, `kill`, `pkill`, `rm` (via implicit shell). These are broadly dangerous.
- **Generated file protection**: ZERO. 7,731 lines of generated TypeScript can be hand-edited.
- **.env protection**: ZERO. No deny rule for .env files.
- **DB access**: Through docker compose only (no direct psql exposed).

### 5b: Minimum Viable Safety (implement immediately)
Add to `~/.claude/settings.json`:
```json
{
  "permissions": {
    "deny": [
      "Edit(apps/dashboard/src/lib/api-types.generated.ts)",
      "Edit(apps/dashboard/src/lib/agent-api-types.generated.ts)",
      "Edit(apps/agent-api/app/schemas/backend_models.py)",
      "Edit(zakops-backend/src/schemas/rag_models.py)",
      "Edit(.env)",
      "Edit(.env.*)",
      "Write(apps/dashboard/src/lib/api-types.generated.ts)",
      "Write(apps/dashboard/src/lib/agent-api-types.generated.ts)",
      "Write(apps/agent-api/app/schemas/backend_models.py)",
      "Write(zakops-backend/src/schemas/rag_models.py)"
    ]
  }
}
```

### 5c: Overreach Warnings
- Codex proposes "ALWAYS require PreToolUse hooks for Bash/Write/WebFetch" — this is too broad. Pre-hooking ALL Bash commands adds latency to every shell operation. Hook only dangerous patterns (dropdb, rm -rf, docker rm).
- Codex proposes "NEVER use bypassPermissions in production" — there IS no production for Claude Code. It's a developer tool. This rule has no enforcement surface.
- Claude proposes PostgreSQL MCP for 3 databases — direct DB access from Claude Code without a read-only role is a write-risk. Requires creating read-only DB users first. NEEDS VERIFICATION: do read-only users exist?

### 5d: Secret Paths (must deny)
```
.env, .env.*, .env.local
**/credentials.json
**/secrets/
~/.claude/settings.local.json (contains MCP tokens)
```

---

## Section 6: Missing Pieces (No Agent Mentioned)

### MISSING-1: Config Architecture Decision (BLOCKS EVERYTHING)
Must decide: repo-level vs user-level vs hybrid `.claude/` before implementing ANY proposal. This is the prerequisite for rules, agents, settings, and hooks placement.

### MISSING-2: Existing Agents in Zaks-llm
4 agents exist at `/home/zaks/Zaks-llm/.claude/agents/`: zakops-prime, agent-config-consultant, log-monitor, research-gemini. No Pass 1 agent referenced these. New agents must not duplicate them.

### MISSING-3: Migration Path
No proposal describes HOW to get from current state to proposed state. Need:
1. Backup current config
2. Create new directories
3. Move/split content
4. Verify nothing broke
5. Rollback procedure if hooks/deny rules break workflow

### MISSING-4: CI vs Dev Validation Split
V5 uses `validate-local` vs `validate-live` but doesn't enforce which runs where. The CI workflow (spec-freshness-bot.yml) must ONLY use validate-local. No proposal makes this explicit.

### MISSING-5: Hook Testing
No proposal includes a way to TEST that hooks work correctly. Need:
- `make test-hooks` that simulates an edit to a generated file and verifies it's blocked
- Or: a `.claude/commands/test-hooks.md` that walks through verification

### MISSING-6: Rollback for V5PP Config Changes
If new deny rules or hooks break the developer workflow, there's no documented rollback. Need: snapshot current `~/.claude/` before changes, provide `make restore-claude-config` target.

### MISSING-7: Windows Line Endings (CRLF)
From MEMORY.md: "Windows line endings (CRLF) break bash scripts — always `sed -i 's/\r$//'` after writing." New hook scripts must account for WSL2 environment. No proposal mentions this.

---

## Section 7: Concrete Patch Set (Surgical Edits to V5 Mission Prompt)

### PATCH-A: Add Step 0.8 — Claude Code Config Audit (before ANY changes)
**Insert after Step 0.7 in SECTION 0: DISCOVERY**
```bash
# ════════════════════════════════════════════════════
# STEP 0.8: Claude Code configuration inventory
# ════════════════════════════════════════════════════

echo ""
echo "=== CLAUDE CODE CONFIGURATION ==="

# Check BOTH user-level and repo-level .claude/
for scope in "$HOME/.claude" "$MONOREPO_ROOT/.claude"; do
  echo "--- $scope ---"
  if [ -d "$scope" ]; then
    echo "Commands: $(ls "$scope/commands/"*.md 2>/dev/null | wc -l)"
    echo "Skills: $(ls -d "$scope/skills/"*/ 2>/dev/null | wc -l)"
    echo "Rules: $(ls "$scope/rules/"*.md 2>/dev/null | wc -l)"
    echo "Agents: $(ls "$scope/agents/"*.md 2>/dev/null | wc -l)"
    echo "Hooks: $(ls "$scope/hooks/"* 2>/dev/null | wc -l)"
    [ -f "$scope/settings.json" ] && echo "settings.json: YES" || echo "settings.json: NO"
  else
    echo "DOES NOT EXIST"
  fi
done

# Check deny rules
echo ""
echo "=== PERMISSION DENY RULES ==="
python3 -c "
import json, pathlib
for p in [pathlib.Path.home()/'.claude/settings.json', pathlib.Path.home()/'.claude/settings.local.json']:
    if p.exists():
        d = json.loads(p.read_text())
        deny = d.get('permissions',{}).get('deny',[])
        print(f'{p.name}: {len(deny)} deny rules')
        for r in deny: print(f'  - {r}')
" 2>/dev/null || echo "(python3 not available for settings check)"
```

### PATCH-B: Add Fix 1.5 — Permission Deny Rules (P0, before any code changes)
**Insert after Fix 1 in the VERIFICATION SEQUENCE**
```markdown
## FIX 1.5 (P0): ESTABLISH PERMISSION DENY RULES

Add deny rules to prevent hand-editing generated files. This MUST be done
before any code changes to prevent accidental drift during the mission itself.

### Implementation
Add to ~/.claude/settings.json (merge with existing hooks config):
- Deny Edit/Write to all *.generated.ts files
- Deny Edit/Write to all codegen Python models (*_models.py in schemas/)
- Deny Edit/Write to .env files

### Verification
1. Attempt to edit api-types.generated.ts → must be BLOCKED
2. Attempt to run `make sync-types` → must SUCCEED
3. Attempt to edit .env → must be BLOCKED

GATE 1.5: Generated files protected by deny rules.
          .env files protected by deny rules.
          make sync-* targets still work.
```

### PATCH-C: Add Fix 1.6 — Path-Scoped Rules (P0)
**Insert after Fix 1.5**
```markdown
## FIX 1.6 (P0): CREATE PATH-SCOPED RULES

Create .claude/rules/ directory (at repo level: $MONOREPO_ROOT/.claude/rules/)
with path-scoped markdown files that auto-inject context when working on
matching files.

### Files to Create

1. contract-surfaces.md — paths: packages/contracts/**, *generated*, *_models.py
   Content: The 7-surface table, sync commands, dependency graph

2. backend-api.md — paths: zakops-backend/src/api/**, zakops-backend/src/schemas/**
   Content: Backend conventions, RAG client patterns, migration rules

3. agent-tools.md — paths: apps/agent-api/app/core/langgraph/tools/**
   Content: BackendClient mandate, zero .get() rule, typed SDK patterns

### Verification
1. Work on a file in packages/contracts/ → contract-surfaces.md context loads
2. Work on deal_tools.py → agent-tools.md context loads

GATE 1.6: At least 3 .claude/rules/*.md files with paths frontmatter.
          Rules load when matching files are active.
```

### PATCH-D: Modify Fix 1 — CLAUDE.md Restructure
**Replace the Fix 1 template with**:
```markdown
## FIX 1 (P0): RESTRUCTURE CLAUDE.md — CONSTITUTION + PROGRESSIVE DISCLOSURE

CLAUDE.md should be 120-150 lines containing:
- Project roots (3 repos)
- Service table (ports, health checks)
- Database table (3 databases, schemas, users)
- Essential commands (make sync-*, make validate-*)
- Non-negotiable rules (8 rules)
- Pointers: "For contract surface details → .claude/rules/contract-surfaces.md"
- Pointers: "For codegen pipeline → .claude/skills/codegen-pipeline/"

Move the 7-surface table and full dependency graph into path-scoped rules
(Fix 1.6) and skills. CLAUDE.md is the INDEX, not the ENCYCLOPEDIA.

GATE 1: CLAUDE.md is 120-150 lines.
        Contains project roots, services, databases, commands, rules.
        Points to rules/skills for details.
        A fresh Claude Code instance reading it knows WHERE to find anything.
```

### PATCH-E: Add Validation Tier Split (modify Pre/Post Task Protocol)
**Replace Pre-Task Protocol item 3-4 and Post-Task Protocol with**:
```markdown
## Pre-Task Protocol (MANDATORY)

1. Read CLAUDE.md (you're doing it now)
2. Run: `make infra-snapshot` — generates fresh INFRASTRUCTURE_MANIFEST.md
3. Run: `make infra-check` — verifies DB + migrations + manifest freshness
4. Identify which contract surfaces your change will affect
5. Verify deny rules are active: attempt editing a generated file → must fail

## Post-Task Protocol (MANDATORY)

1. Run the appropriate `make sync-*` targets for affected surfaces
2. Run: `npx tsc --noEmit` (in apps/dashboard) — verify TypeScript compiles
3. Run: `make validate-local` — ALWAYS (offline, CI-safe)
4. ONLY if services are running: `make validate-live` — online validation
5. Verify no regressions in unrelated surfaces

## CI vs Dev Validation (HARD RULE)
- CI pipelines MUST use `make validate-local` only
- `make validate-live` and `make update-agent-spec` are DEV-ONLY
- NEVER put service-dependent targets in CI gates
```

### PATCH-F: Add Stop Hook for Completion Validation
**Add to Fix 6 (Pre-commit hook section)**:
```markdown
### Claude Code Stop Hook (completion gate)

Add a Stop hook that runs `make validate-local` before Claude declares
it has finished. This replaces the PostToolUse pattern (which would run
on every file edit and is too expensive).

In ~/.claude/settings.json:
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tail -20",
        "timeout": 60
      }]
    }]
  }
}

If validate-local fails, Claude sees the output and self-corrects
before stopping. This is Boris Cherny's verification pattern done right.
```

### PATCH-G: Add Migration/Rollback Section (new section)
**Add after AUTONOMY RULES**:
```markdown
## MIGRATION SAFETY

Before implementing V5PP changes:
1. Snapshot current config: `cp -r ~/.claude/ ~/.claude.backup.$(date +%Y%m%d)`
2. Verify backup: `diff -r ~/.claude/ ~/.claude.backup.*/`
3. Implement changes incrementally (deny rules first, then rules, then hooks)
4. After each step: verify `make validate-local` still passes
5. If anything breaks: `rm -rf ~/.claude/ && mv ~/.claude.backup.*/ ~/.claude/`

DO NOT implement all changes at once. The order is:
1. Deny rules (settings.json) — can't break anything
2. Path-scoped rules — additive, can't break anything
3. CLAUDE.md restructure — verify content preserved
4. Hooks changes — most likely to cause issues, do last
5. Subagents — optional, independent
```

---

## Section 8: Recommended "Final Shape" for V5PP

```
V5PP MISSION PROMPT — TABLE OF CONTENTS

SECTION 0: DISCOVERY (Steps 0.1-0.10 from V5 + Step 0.8 config audit)
  └─ Verify filesystem, specs, generated files, bridges, services, AND claude code config

FIX 1: CLAUDE.md RESTRUCTURE (120-150 lines, constitution style)
  └─ Project roots, services, databases, commands, rules, pointers to skills/rules

FIX 1.5: PERMISSION DENY RULES (settings.json, ~15 deny entries)
  └─ Block Edit/Write to generated files, .env, models

FIX 1.6: PATH-SCOPED RULES (3-4 .claude/rules/*.md files)
  └─ contract-surfaces.md, backend-api.md, agent-tools.md

FIX 2: .claude/commands/ (extend existing 12 to 15+)
  └─ after-change.md, diagnose-drift.md, test-hooks.md

FIX 2.5: SUBAGENTS (2-3 .claude/agents/*.md files) [OPTIONAL]
  └─ contract-checker.md, topology-explorer.md
  └─ Must check Zaks-llm/.claude/agents/ for existing agents first

FIX 3: MANIFEST GENERATOR (extend generate-manifest.sh)
  └─ Add contract surfaces, generated files, bridges, SDK status, config audit

FIX 4: CROSS-LAYER VALIDATION (extend validate-*.sh)
  └─ Add freshness checks, bridge enforcement, typed SDK checks

FIX 5: DEPENDENCY GRAPH (in manifest + rules)
  └─ Impact matrix, service→DB mapping, codegen flow diagram

FIX 6: HOOKS (extend pre-edit.sh + add Stop hook)
  └─ Block generated file edits (defense in depth)
  └─ Stop hook: validate-local before completion
  └─ PreCompact: save contract state to memory

FIX 7: MAKEFILE PORTABILITY (verify, no hardcoded paths)
FIX 8: SPEC-FRESHNESS-BOT (extend to all 4 specs)
FIX 9: ENFORCEMENT VALIDATOR (add config audit checks)

VALIDATION TIER SPLIT (new section)
  └─ CI: validate-local ONLY
  └─ Dev: validate-live when services running

MIGRATION SAFETY (new section)
  └─ Backup, incremental implementation, rollback procedure

AUTONOMY RULES (updated from V5)
OUTPUT FORMAT (updated from V5 + config audit fields)
```

### Key Differences from V5:
- **New**: Fix 1.5 (deny rules), Fix 1.6 (path-scoped rules), Fix 2.5 (subagents)
- **Modified**: Fix 1 (constitution split), Fix 6 (Stop hook instead of PostToolUse)
- **New sections**: Validation tier split, Migration safety
- **Removed bloat**: No managed settings, no eval gates, no dynamic context scripts, no auto-fix targets

### Key Differences from Codex Pass 2:
- Rejected: managed settings, eval gates, auto-fix, OWASP section (overkill for single-dev)
- Added: config location decision, migration path, validation tier split, Stop hook pattern
- Grounded: all proposals verified against actual filesystem state

### Key Differences from Codex Pass 2 (second review):
- Agreed: path-scoped rules, deny rules, subagents, reject context.sh and DriftOps
- Disagreed: PostToolUse hook for auto-fix (use Stop hook instead), "wipe legacy CLAUDE.md" (restructure, don't wipe)

---

## Appendix: Cross-Reference Matrix

| Idea | Codex | Gemini | Claude P1 | Codex P2a | Codex P2b | This Review |
|------|-------|--------|-----------|-----------|-----------|-------------|
| Permission deny | KEEP | — | KEEP | KEEP | KEEP | **KEEP** |
| Path-scoped rules | — | — | KEEP | — | KEEP | **KEEP** |
| Managed settings | KEEP | — | KEEP | KEEP | — | **REJECT** |
| PostToolUse auto-validate | — | — | KEEP | KEEP | KEEP | **REJECT** |
| Dynamic context.sh | — | KEEP | — | — | REJECT | **REJECT** |
| DriftOps auto-commit | — | KEEP | — | REJECT | REJECT | **REJECT** |
| make auto-fix | — | KEEP | — | REJECT | partial | **REJECT** |
| Eval gate (OpenAI Evals) | KEEP | — | — | KEEP | — | **REJECT** |
| OWASP section | KEEP | — | — | KEEP | KEEP | **REJECT** (overkill) |
| Subagents | — | — | KEEP | — | KEEP | **CONDITIONAL** |
| CLAUDE.md split | — | — | KEEP | — | KEEP | **KEEP (modified)** |
| Stop hook validation | — | — | — | — | — | **NEW** |
| Validation tier split | — | — | — | — | — | **NEW** |
| Migration/rollback | — | — | — | — | — | **NEW** |
| Config location decision | — | — | — | — | — | **NEW** |

---

*Generated: 2026-02-07T15:00:00Z by Claude (opus46)*
*Pipeline: CLAUDE_CODE_RESET_V5PP, Pass 2 of 3*
*Repo state verified: YES*

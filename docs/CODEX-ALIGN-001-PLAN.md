# CODEX-ALIGN-001: Codex CLI Configuration Alignment Plan

## Context

Claude Code has been configured through 25+ missions into a deeply mature operational environment (V7PP) with 10 hooks, 7 path-scoped rules, 16 slash commands, 8 skills, 14 contract surfaces, boot diagnostics, persistent memory, and a full safety layer. Codex CLI (v0.98.0) currently has only a minimal setup: a 95-line Lab Loop QA instructions file, 5 ad-hoc sandbox rules, 2 profiles, and no AGENTS.md, no MCP servers, no skills, and no session lifecycle management.

If Codex remains unaligned, we risk execution drift, inconsistent reasoning, and uneven output quality between the two agents. This plan brings Codex to operational parity wherever technically feasible, and explicitly documents permanent gaps.

---

## Gap Analysis Summary

| Category | Claude Code | Codex Current | Codex Target | Gap Type |
|----------|-------------|---------------|--------------|----------|
| Instructions | CLAUDE.md (root 64L + monorepo 145L) | CODEX_INSTRUCTIONS.md (95L, Lab Loop only) | AGENTS.md (global ~350L + monorepo ~250L + backend ~100L) | Direct map |
| Hooks (10 scripts) | PreToolUse, PostToolUse, SessionStart, Stop, PreCompact, TaskCompleted | None | Wrapper scripts (boot + stop) + notify handler | Adaptation (major gap) |
| Path-scoped rules (7) | Auto-injected by file path match | None | Embedded in per-project AGENTS.md by heading | Adaptation |
| Slash commands (16) | `.claude/commands/*.md` | None | `.agents/skills/*/SKILL.md` (26 skills) | Direct map |
| Knowledge skills (8) | `.claude/skills/*` | None | `~/.codex/skills/*/SKILL.md` (8 skills) | Direct map |
| Boot diagnostics (6 checks) | session-start.sh + session-boot.sh | None | codex-boot.sh wrapper | Adaptation |
| Deny rules (12) | settings.json deny array + hook enforcement | None | AGENTS.md behavioral rules + sandbox mode | Adaptation |
| Allow patterns (4 make targets) | settings.json allow array | 5 ad-hoc prefix_rules | ~30 structured prefix_rules | Direct map |
| MCP servers (4) | GitHub, Playwright, Gmail, crawl4ai-rag | None | codex mcp add (4 servers) | Direct map |
| Profiles | N/A | 2 (labloop-qa, labloop-qa-debug) | 5 (add builder, review, forensic) | Enhancement |
| config.toml | N/A | Basic (6 settings) | Full (notify, history, shell env, trust) | Enhancement |
| PATH | N/A | Not in PATH | Alias in .bashrc | Fix |
| Persistent memory (MEMORY.md) | 200L with AUTOSYNC sentinels | None | AGENTS.md instruction to read MEMORY.md | **Permanent gap** |
| Sub-agent delegation (3 agents) | contract-guardian, arch-reviewer, test-engineer | N/A | Inlined checklists in AGENTS.md | **Permanent gap** |
| Pre-tool enforcement | Hook exit 2 blocks before execution | N/A | Sandbox mode only | **Permanent gap** |
| Compaction awareness | PreCompact + compact-recovery hooks | N/A | None possible | **Permanent gap** |

---

## Implementation Plan

### Phase 1: Foundation (AGENTS.md + config.toml) — 4 files

#### 1.1 Create `~/.codex/AGENTS.md` (global instructions)

**Path:** `/home/zaks/.codex/AGENTS.md`
**Size target:** ~350 lines (under 15KB, well within 32KB limit)
**Replaces:** `CODEX_INSTRUCTIONS.md` (keep for backward compat with `# Superseded` header)

**Content sections:**
1. **ZakOps Operating Guidelines** — Service map, key paths, golden commands, secrets policy (adapted from `/home/zaks/CLAUDE.md`)
2. **Critical Rules** — Port 8090 decommissioned, evidence-for-every-claim, record changes in CHANGES.md, browser verification
3. **WSL Session Hazards** — CRLF, root ownership, dual tool paths, grep -c exit code (from MEMORY.md)
4. **Infrastructure Awareness Protocol** — Pre-task (`make sync-types`), post-task (`make sync-types && tsc --noEmit`), cross-layer change flow
5. **Deal Integrity Architectural Patterns** — transition_deal_state choke point, Promise.allSettled mandatory, middleware proxy, PIPELINE_STAGES authority, caret-color, ADRs
6. **Contract Surfaces** — 14-surface table with sync commands and generated file mapping
7. **Constraint Registry** — 10 constraints with rule file and search string
8. **Lab Loop Auto-Detection** — Migrated from existing CODEX_INSTRUCTIONS.md (unchanged)
9. **Lab Loop QA Protocol** — Migrated from existing CODEX_INSTRUCTIONS.md (unchanged)
10. **Builder Protocol** — MODE 2 headless builder (from `~/.claude/CLAUDE.md`)
11. **Session Lifecycle** — "At start: read MEMORY.md at `/root/.claude/projects/-home-zaks/memory/MEMORY.md`. At end: record all changes in `/home/zaks/bookkeeping/CHANGES.md`"
12. **General Rules** — Use existing patterns, keep changes minimal, never commit secrets

#### 1.2 Create `/home/zaks/zakops-agent-api/.agents/AGENTS.md` (monorepo project instructions)

**Path:** `/home/zaks/zakops-agent-api/.agents/AGENTS.md`
**Size target:** ~250 lines

**Content sections:**
1. **Read-First Documents** — agent.md, ARCHITECTURE.md, CONSTRAINTS.md, ATOMIC_TASKS.md
2. **Contract Surfaces Detail** — 14 surfaces with full boundary definitions, sync commands, validators
3. **Pre-Task Protocol** — Read CLAUDE.md, run `make infra-check`, identify affected surfaces, run `make sync-all-types`
4. **Post-Task Protocol** — Run `make sync-*`, run `make validate-local`, fix CRLF + ownership, record in CHANGES.md
5. **Path-Scoped Guidance** (inlined from 7 `.claude/rules/*.md` files):
   - Backend API rules (transition_deal_state choke point, ADR-001)
   - Dashboard types rules (bridge imports only, never generated files)
   - Agent tools rules (tool schema consistency)
   - Design system rules (Surface 9: Promise.allSettled, caret-color, console patterns)
   - Contract surfaces rules (sync flow, codegen, drift checking)
   - Backend API conventions, security and data patterns
6. **Agent Procedure Checklists** (inlined since sub-agents unavailable):
   - Contract Guardian checklist (14-surface audit procedure)
   - Architecture Reviewer checklist (design decision evaluation)
   - Test Engineer checklist (test planning and validation)
7. **Non-Negotiable Rules** — Generated file protection, .env protection, port 8090 ban
8. **Essential Make Targets** — Full table from MEMORY.md

#### 1.3 Create `/home/zaks/zakops-backend/.agents/AGENTS.md` (backend project instructions)

**Path:** `/home/zaks/zakops-backend/.agents/AGENTS.md`
**Size target:** ~100 lines

**Content sections:**
1. Backend CLAUDE.md content reference
2. API conventions (route ordering, Pydantic patterns)
3. Database access (zakops schema, NOT public; zakops user, NOT dealengine)
4. transition_deal_state enforcement
5. Test commands (scripts/test.sh, scripts/qa_smoke.sh)
6. OpenAPI contract location

#### 1.4 Update `~/.codex/config.toml`

**Path:** `/home/zaks/.codex/config.toml`

**Changes:**
```toml
# Add notification handler
notify = ["/home/zaks/scripts/codex-notify.sh"]

# Add profiles
[profiles.builder]
model = "gpt-5.3-codex"
sandbox = "workspace-write"
ask_for_approval = "never"

[profiles.review]
model = "gpt-5.3-codex"
sandbox = "read-only"
ask_for_approval = "never"
model_reasoning_effort = "xhigh"

[profiles.forensic]
model = "gpt-5.3-codex"
sandbox = "read-only"
ask_for_approval = "never"
model_reasoning_effort = "xhigh"

# Fix typo and add all project trust entries
[projects."/home/zaks/zakops-agent-api"]
trust_level = "trusted"

[projects."/home/zaks/zakops-backend"]
trust_level = "trusted"

[projects."/home/zaks/bookkeeping"]
trust_level = "trusted"

# Add history config
[history]
persistence = "filesystem"
max_bytes = 10485760

# AGENTS.md discovery
project_doc_max_bytes = 65536
project_doc_fallback_filenames = ["CODEX_INSTRUCTIONS.md"]
```

Remove: `[projects."/home/zaks/bookkeepping/doc"]` (typo, invalid path)

---

### Phase 2: Skills — 26 skill directories

Each skill = directory with `SKILL.md` containing frontmatter (`name`, `description`) + instructions.

#### User-level action skills (`~/.codex/skills/`)

| # | Skill | Source | Description |
|---|-------|--------|-------------|
| S1 | `health-check` | Inline | Check all ZakOps service health |
| S2 | `run-gates` | `/run-gates` command | Run quality gate pipeline |
| S3 | `investigate` | `/investigate` command | Deep investigation workflow |
| S4 | `fix-bug` | `/fix-bug` command | Guided bug fix workflow |
| S5 | `implement-feature` | `/implement-feature` command | Guided feature implementation |
| S6 | `add-endpoint` | `/add-endpoint` command | Guided API endpoint addition |
| S7 | `audit-code` | `/audit-code` command | Code audit checklist |
| S8 | `deploy-backend` | `/deploy-backend` command | Rebuild and restart backend |
| S9 | `deploy-dashboard` | `/deploy-dashboard` command | Restart dashboard |
| S10 | `snapshot` | `/snapshot` command | Bookkeeping state snapshot |
| S11 | `tail-logs` | `/tail` command | Tail all service logs |

#### User-level knowledge skills (`~/.codex/skills/`)

| # | Skill | Source |
|---|-------|--------|
| K1 | `project-context` | `~/.claude/skills/project-context/` |
| K2 | `api-conventions` | `~/.claude/skills/api-conventions/` |
| K3 | `code-style` | `~/.claude/skills/code-style/` |
| K4 | `security-and-data` | `~/.claude/skills/security-and-data/` |
| K5 | `debugging-playbook` | `~/.claude/skills/debugging-playbook/` |
| K6 | `verification-standards` | `~/.claude/skills/verification-standards/` |
| K7 | `atomic-workflow` | `~/.claude/skills/atomic-workflow/` |
| K8 | `frontend-design` | `~/.claude/skills/frontend-design/` |

#### Project-level skills (`/home/zaks/zakops-agent-api/.agents/skills/`)

| # | Skill | Source |
|---|-------|--------|
| P1 | `before-task` | `.claude/commands/before-task.md` |
| P2 | `after-change` | `.claude/commands/after-change.md` |
| P3 | `sync-all` | `.claude/commands/sync-all.md` |
| P4 | `validate` | `.claude/commands/validate.md` |
| P5 | `contract-checker` | `.claude/commands/contract-checker.md` |
| P6 | `infra-check` | `.claude/commands/infra-check.md` |
| P7 | `tripass` | `.claude/commands/tripass.md` |

---

### Phase 3: Sandbox Rules — 1 file

**Path:** `/home/zaks/.codex/rules/default.rules`
**Replaces:** Current 5 ad-hoc rules

**Structured categories (~30 rules):**
- Health checks: `curl -sf localhost:{3003,8091,8095,8052}`, `pg_isready`
- Docker: `docker ps`, `docker logs`, `docker compose ps/up/restart`
- Make targets: `make sync-*`, `make validate-*`, `make infra-*`, `make update-*`
- Tests: `bash scripts/test.sh`, `bash scripts/qa_smoke.sh`, `npx tsc --noEmit`, `npx playwright test`
- Git reads: `git status`, `git diff`, `git log`, `git branch`
- File inspection: `ls`, `cat`, `head`, `tail`, `wc`, `find`
- System: `ss -tlnp`, `lsof -i`, `curl`, `sort`

---

### Phase 4: MCP Servers — 4 commands

**Prerequisites:**
- GitHub auth: Ensure `gh auth login` has been run or `GITHUB_TOKEN` env var is set. The GitHub MCP server requires authentication to access GitHub APIs. After setup, run `codex mcp list` to verify token is not leaked in config output.
- Gmail auth: `@gongrzhe/server-gmail-autoauth-mcp` uses OAuth2 auto-auth flow. First run may prompt browser-based consent.
- crawl4ai-rag: Requires the `docs-rag-mcp` Docker container to be running.

**Source of truth:** Claude Code MCP config lives in two files:
- `settings.json` (project): github, playwright
- `settings.local.json` (user): gmail, crawl4ai-rag, playwright

```bash
/root/.npm-global/bin/codex mcp add github -- npx -y @modelcontextprotocol/server-github
/root/.npm-global/bin/codex mcp add playwright -- /root/.npm-global/bin/playwright-mcp --headless --no-sandbox
/root/.npm-global/bin/codex mcp add gmail -- npx -y @gongrzhe/server-gmail-autoauth-mcp
/root/.npm-global/bin/codex mcp add crawl4ai-rag -- docker exec -i docs-rag-mcp python -m src.mcp_server
```

**Post-setup verification (per server):**
1. `codex mcp list` — confirm all 4 registered
2. Invoke one real tool call per server to verify connectivity:
   - GitHub: list a known repo
   - Playwright: navigate to localhost:3003
   - Gmail: search for a recent email
   - crawl4ai-rag: query available sources
3. Secret scan: verify no tokens appear in `~/.codex/config.toml` or MCP config output

---

### Phase 5: External Wrapper Scripts — 4 files

#### 5.1 `/home/zaks/scripts/codex-boot.sh` (pre-session diagnostics)

Runs the same 6 checks as Claude Code's `session-start.sh`:
1. Memory integrity (MEMORY.md exists, symlink intact)
2. Surface count consistency (4-way: CLAUDE.md, MEMORY.md, validator script header, INFRASTRUCTURE_MANIFEST.md — must all report 14)
3. Sentinel freshness (AUTOSYNC values match filesystem)
4. Generated files exist (4 generated files present and non-empty)
5. Codegen freshness (spec timestamps vs generated files)
6. Constraint registry (10 entries verified)

Output: Verdict (ALL CLEAR / PROCEED WITH CAUTION / HALT). HALT = exit 1 (prevents Codex launch).

**Reuse:** Source the existing `session-start.sh` check functions where possible to avoid duplication.

#### 5.2 `/home/zaks/scripts/codex-stop.sh` (post-session validation)

Runs validation gates:
1. `make validate-local` (offline validation)
2. Report results to stdout
3. Append to health log

#### 5.3 `/home/zaks/scripts/codex-notify.sh` (event handler)

Receives `agent-turn-complete` JSON from Codex notify system. Logs to `/home/zaks/bookkeeping/logs/codex-events.log`.

#### 5.4 `/home/zaks/scripts/codex-wrapper.sh` (unified launcher)

```bash
#!/usr/bin/env bash
# codex-wrapper.sh — Boot, launch, validate
set -euo pipefail

# Emergency bypass: CODEX_FORCE=1 codex-safe ... (logged)
if [[ "${CODEX_FORCE:-}" == "1" ]]; then
  echo "WARNING: Force override — skipping boot diagnostics" | tee -a /home/zaks/bookkeeping/logs/codex-events.log
else
  bash /home/zaks/scripts/codex-boot.sh || { echo "HALT: Fix diagnostics first (use CODEX_FORCE=1 to override)"; exit 1; }
fi

/root/.npm-global/bin/codex "$@"
bash /home/zaks/scripts/codex-stop.sh
```

---

### Phase 6: Shell Integration — 1 modification

**File:** `/home/zaks/.bashrc`

**Add:**
```bash
# Codex CLI
export PATH="/root/.npm-global/bin:$PATH"
alias codex-safe='/home/zaks/scripts/codex-wrapper.sh'
```

---

### Phase 7: Backward Compatibility

**File:** `/home/zaks/.codex/CODEX_INSTRUCTIONS.md`

Add header: `# SUPERSEDED — See ~/.codex/AGENTS.md for current instructions`
Keep existing content intact for any scripts that reference it.

---

## Permanent Capability Gaps (Cannot Be Replicated)

| # | Claude Code Feature | Why Impossible in Codex | Mitigation |
|---|---|---|---|
| 1 | Pre-tool hooks (exit 2 blocks before execution) | Codex has no PreToolUse event. Only `notify` on agent-turn-complete | Rely on `read-only` sandbox default. Behavioral rules in AGENTS.md |
| 2 | Persistent memory with AUTOSYNC sentinels | No memory persistence mechanism between sessions | AGENTS.md instructs "read MEMORY.md first". For `codex exec` mode, caller must prepend context manually — no automatic injection exists |
| 3 | Sub-agent delegation (3 specialized agents) | Codex is single-model, single-session | Inline agent checklists in AGENTS.md |
| 4 | Compaction awareness (PreCompact + recovery) | No compaction hook | No mitigation |
| 5 | Post-edit formatting (async file cleanup) | No PostToolUse hook | No mitigation |
| 6 | Task completion quality gates | No TaskCompleted hook | Manual `codex-stop.sh` invocation |
| 7 | Health log trend detection across sessions | No session history analysis | Manual review of codex-events.log |

---

## Implementation Order

```
Phase 1 (Foundation)  ->  1.1 Global AGENTS.md
                          1.2 Monorepo AGENTS.md
                          1.3 Backend AGENTS.md   (all 3 in parallel)
                          1.4 Update config.toml

Phase 2 (Skills)      ->  2.1 User action skills (S1-S11)
                          2.2 User knowledge skills (K1-K8)    (all in parallel)
                          2.3 Project skills (P1-P7)

Phase 3 (Rules)       ->  3.1 Structured default.rules

Phase 4 (MCP)         ->  4.1 codex mcp add (4 servers)

Phase 5 (Scripts)     ->  5.1 codex-boot.sh
                          5.2 codex-stop.sh        (all in parallel)
                          5.3 codex-notify.sh
                          5.4 codex-wrapper.sh

Phase 6 (Shell)       ->  6.1 .bashrc update

Phase 7 (Compat)      ->  7.1 Supersede CODEX_INSTRUCTIONS.md

Phase 8 (Verify)      ->  Full verification checklist
```

---

## Verification Checklist

### Structural (file existence)
- [ ] `~/.codex/AGENTS.md` exists and < 15KB
- [ ] `/home/zaks/zakops-agent-api/.agents/AGENTS.md` exists
- [ ] `/home/zaks/zakops-backend/.agents/AGENTS.md` exists
- [ ] `~/.codex/config.toml` has notify, 5 profiles, 4 project trust entries
- [ ] 19 user skills exist (`ls -d ~/.codex/skills/*/SKILL.md | wc -l`)
- [ ] 7 project skills exist (`ls -d zakops-agent-api/.agents/skills/*/SKILL.md | wc -l`)
- [ ] `~/.codex/rules/default.rules` has ~30 structured rules
- [ ] 4 MCP servers registered (`codex mcp list`)
- [ ] 4 wrapper scripts exist and are executable
- [ ] `codex` resolves in PATH

### Content (correctness)
- [ ] AGENTS.md mentions port 8090 decommissioned
- [ ] AGENTS.md has service map with all 8 active services
- [ ] AGENTS.md has 14 contract surfaces
- [ ] AGENTS.md has 10 constraint registry entries
- [ ] AGENTS.md has WSL hazards (CRLF, root ownership)
- [ ] AGENTS.md has Deal Integrity patterns
- [ ] config.toml has no typos in project paths
- [ ] Rules file covers make, docker, git, curl, test categories

### Functional (behavior)
- [ ] `codex-boot.sh` runs and reports ALL CLEAR
- [ ] `codex --version` returns 0.98.0
- [ ] `codex mcp list` shows github, playwright, gmail, crawl4ai-rag
- [ ] `codex-stop.sh` runs without errors
- [ ] All file ownership correct (zaks:zaks for /home/zaks/ files)
- [ ] All .sh files have LF line endings (no CRLF)

### AGENTS.md load proof (runtime)
- [ ] Run `codex exec "List the 3 read-first documents for the monorepo" --sandbox read-only` in `/home/zaks/zakops-agent-api/` — must return agent.md, ARCHITECTURE.md, CONSTRAINTS.md (proves project AGENTS.md loaded)
- [ ] Run `codex exec "What database schema does zakops-backend use?" --sandbox read-only` in `/home/zaks/zakops-backend/` — must return "zakops" not "public" (proves backend AGENTS.md loaded)
- [ ] If `.agents/AGENTS.md` is NOT loaded by Codex, fallback: move content to repo-root `AGENTS.md` and re-verify

### MCP behavioral verification (per server)
- [ ] GitHub MCP: `codex exec "Use the GitHub MCP to get info about zakops-agent-api repo"` — must return repo metadata
- [ ] Playwright MCP: `codex exec "Navigate to http://localhost:3003 and take a snapshot"` — must return page content
- [ ] Gmail MCP: `codex exec "Search for the most recent email"` — must return email metadata
- [ ] crawl4ai-rag MCP: `codex exec "List available RAG sources"` — must return source list
- [ ] Secret scan: `grep -ri 'token\|secret\|password' ~/.codex/config.toml` returns no plaintext credentials

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| No pre-tool enforcement in Codex | Default `read-only` sandbox. AGENTS.md explicitly lists protected files. Only `builder` profile enables writes |
| AGENTS.md exceeds 32KB limit | Keep global under 15KB. Use skills for detailed procedures. Monitor with `wc -c` |
| Dual config (root vs user) confusion | Document `/home/zaks/.codex/` as canonical. Root config stays minimal |
| MCP server startup failures | Test each server individually after adding. Document fallback for offline operation |
| Skills not discovered | Verify with `codex exec "List available skills"`. Ensure SKILL.md frontmatter is valid |

---

## Deliverables Summary

| Category | Count | Lines |
|----------|-------|-------|
| AGENTS.md files | 3 | ~700 |
| config.toml update | 1 | ~80 |
| Skill directories | 26 | ~1300 |
| Sandbox rules | 1 | ~30 |
| Wrapper scripts | 4 | ~250 |
| Shell integration | 1 | ~5 |
| Backward compat | 1 | ~3 |
| **Total** | **37 files** | **~2370 lines** |

---

## Bookkeeping

- Record all changes in `/home/zaks/bookkeeping/CHANGES.md`
- Fix CRLF (`sed -i 's/\r$//'`) on all .sh files
- Fix ownership (`chown zaks:zaks`) on all /home/zaks/ files
- Update MEMORY.md with mission completion entry

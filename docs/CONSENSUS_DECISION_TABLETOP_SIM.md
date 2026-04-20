# PASS 4 — TABLETOP SIMULATION (RE-RUN v3)

agent_name: Claude Opus 4.6
run_id: 20260207-2400-p4-tabletop-v3
timestamp: 2026-02-07T24:00:00Z
repo_revision: agent-api=5eb7ce6, backend=444dff6
input_doc: /home/zaks/bookkeeping/docs/CONSENSUS_DECISION_FINAL.md
supersedes: 20260207-2345-p4-tabletop-v2 (v2 — 1 PASS + 2 CONDITIONAL)

---

## STATUS: CONDITIONAL PASS

0 of 3 scenarios fully pass. 3 of 3 scenarios have working gates but require automation fixes. Previous run (v2) had 1 PASS + 2 CONDITIONAL. v3 downgrades Scenario 2 from PASS to CONDITIONAL due to newly discovered CI gap.

**New v3 finding:** The adopted plan's Section 3.10 states "CI required checks: Gate A–H" but the actual CI pipeline (`ci.yml`) implements **none** of these gates. Offline gates (C, D, E) that COULD run in CI are absent, creating a bypass path for developers who push via git without using Claude Code.

---

## Ground Truth Audit (Pre-Simulation)

Filesystem state verified at simulation start. Compared against v2 (no script changes detected).

### Gate Status

| Gate | Artifact | Exists? | Wired Into Automation? | v2 → v3 Change |
|------|----------|---------|------------------------|----------------|
| Gate A | `make validate-local` | YES | YES (stop hook) | Unchanged |
| Gate B | `validate-contract-surfaces.sh` | YES | YES (via validate-local) | Unchanged |
| Gate C | `generate_agent_config.py --check` | YES | YES (via validate-local → validate-agent-config) | **NOT IN CI** (new finding) |
| Gate D | `validate_sse_schema.py` | YES | YES (via validate-local → validate-sse-schema) | **NOT IN CI** (new finding) |
| Gate E | `rg httpx deal_tools.py` | YES (manual) | NO | **NOT IN CI** (new finding) |
| Gate F | `migration-assertion.sh` | YES | YES (via validate-live) | Unchanged (online gate — correctly excluded from CI) |
| Gate G | `command -v gemini && command -v codex` | N/A | NO | Unchanged |
| Gate H | `stop.sh` | YES | YES (stop hook) | Unchanged |
| Gate I | `check-spec-drift.sh` | YES | YES (via validate-live) | Unchanged (online gate) |

### Infrastructure Status

| Item | v2 State | v3 State | Change |
|------|----------|----------|--------|
| `.claude/agents/` directory | Does not exist | **Does not exist** | NO CHANGE — Phase 0 not started |
| CI pipeline vs plan | Not audited | **AUDITED — 0 of 8 gates in CI** | NEW FINDING |
| `spec-freshness-bot.yml` | Not audited | **EXISTS — daily cron, advisory only (::warning)** | NEW FINDING |
| `instructions-freshness-bot.yml` | Not audited | **EXISTS — daily cron, advisory only** | NEW FINDING |
| Pre-push hook | Does not exist | **Does not exist** | NO CHANGE |
| validate-live cron | Does not exist | **Does not exist** | NO CHANGE |
| All gate scripts (C, D, F, I) | Unchanged | **Unchanged** | NO CHANGE |

### CI Pipeline Deep Audit (NEW in v3)

The adopted plan (Section 3.10) states:
> "CI required checks: Gate A–H."

**Actual CI pipeline (`ci.yml`) contents:**

| CI Job | What It Runs | Overlapping Gate? |
|--------|-------------|-------------------|
| `agent-api` | ruff lint, mypy (regression-gated), pytest | None directly. mypy covers code quality, not contract alignment. |
| `dashboard` | npm lint, tsc, build, test | **Partial Gate A overlap** — tsc catches type errors, but only from committed spec (no sync step) |
| `contracts` | Redocly lint, ignore debt ceiling | None — validates OpenAPI syntax, not contract surface alignment |
| `type-sync` | Codegen drift via git diff, legacy import check, manual type debt, Zod ceiling | **Partial Gate B overlap** — checks if generated types match committed spec, but doesn't run `validate-contract-surfaces.sh` |
| `gates` | Checks if other jobs passed | Aggregator only — no gate scripts invoked |

**Gates that COULD run in CI but DON'T:**

| Gate | Why It Can Run in CI | Impact of Absence |
|------|---------------------|-------------------|
| **Gate C** (`generate_agent_config.py`) | Pure offline Python script — reads files, uses `ast` module | Tool/prompt/schema drift escapes if pushed outside Claude Code |
| **Gate D** (`validate_sse_schema.py`) | Pure offline Python script — reads JSON schema file | SSE schema structural errors escape |
| **Gate E** (`rg httpx deal_tools.py`) | Simple grep — no dependencies | Raw httpx usage in tools escapes |
| **Gate B** (`validate-contract-surfaces.sh`) | Mostly offline (file freshness, imports, patterns) | Contract surface alignment gaps escape |

**Gates that CORRECTLY are NOT in CI (online-only):**

| Gate | Why It Can't Run in CI | Current Status |
|------|----------------------|----------------|
| Gate F (`migration-assertion.sh`) | Requires 3 running databases | In validate-live (manual) |
| Gate I (`check-spec-drift.sh`) | Requires running backend | In validate-live (manual) |

### Previous Enforcement Fixes — Status

| Fix ID | Description | Status |
|--------|-------------|--------|
| EF-1 | Create `check-spec-drift.sh` | **DONE** (v2) |
| EF-2 | Wire `validate-live` into pre-push hook or cron | **NOT DONE** |
| EF-3 | Fix `stop.sh` to exit non-zero on failure | **DONE** (v2) |
| EF-4 | Create `validate-agent-config.sh` | **DONE** (v2) |
| EF-5 | Wire `validate-agent-config` into `validate-local` | **DONE** (v2) |
| EF-6 | Add `validate-agent-config` make target | **DONE** (v2) |
| EF-7 | Wire `migration-assertion.sh` into `validate-live` | **DONE** (v2) |
| EF-8 | Fix backend SKIP → FAIL when DB unreachable | **DONE** (v2) |
| EF-9 | Add pre-push hook calling `validate-live` | **NOT DONE** |
| EF-10 | (Duplicate of EF-3) | **DONE** (v2) |

**8 of 10 fixes applied (same as v2). 0 new fixes between v2 and v3.**

---

## Scenario 1: Backend Changes a Response Schema the Dashboard Consumes

### What Changes

Backend developer renames `deal.asking_price` to `deal.list_price` in `zakops-backend`. The live OpenAPI at `localhost:8091/openapi.json` reflects the new name. The committed spec in `packages/contracts/openapi/zakops-api.json` is stale.

### Gate Walk-Through

| Step | Gate | What Happens | Catches Drift? |
|------|------|--------------|----------------|
| 1 | Stop hook → `make validate-local` | Runs sync-types (from committed spec — still old), tsc (compiles against old types), validate-contract-surfaces (freshness: both stale equally). | **NO** — committed spec never updated |
| 2 | CI pipeline (`ci.yml`) | `type-sync` job regenerates types from committed spec, diffs. No drift because committed spec is unchanged. Dashboard tsc passes against old types. | **NO** — CI also uses committed spec |
| 3 | `make validate-live` → `check-spec-drift.sh` | Fetches live spec from backend, jq-canonicalizes both, diffs. **Detects divergence.** Exits 1. | **YES** |
| 4 | `spec-freshness-bot.yml` (daily cron) | Exports Agent API spec and compares (but NOT backend spec — backend requires Docker). Emits `::warning::` only, never fails. | **PARTIAL** — advisory for agent spec only, not blocking |

### Kill-Switch Rule Analysis

**Offline path (automated — stop hook + CI):** Does NOT catch drift. The committed spec is internally consistent with the generated types; both are stale together.

**Online path (manual — `make validate-live`):** DOES catch drift. `check-spec-drift.sh` diffs the live backend against the committed spec and exits 1 on any difference.

**Advisory layer (daily cron):** `spec-freshness-bot.yml` partially detects drift but only as `::warning::` — it never fails the workflow and only covers Agent API spec (backend spec requires Docker which the bot doesn't have).

**But:** `validate-live` is NOT automated as a blocking check. It requires a human to run `make validate-live`, or a pre-push hook (EF-9 — not implemented), or CI with service containers (not implemented).

### Verdict: CONDITIONAL PASS

Unchanged from v2. The gate exists and works. The gap is `validate-live` automation. The spec-freshness-bot provides marginal advisory coverage but doesn't block.

---

## Scenario 2: Agent Tool Added Without Updating Schemas

### What Changes

A developer adds `def get_deal_contacts(deal_id: str) -> ToolResult:` with a `@tool` decorator to `deal_tools.py`. The tool is registered in the LangGraph registry. But:
- `system.md` is NOT updated (prompt doesn't mention the new tool)
- `packages/contracts/mcp/tool-schemas.json` is NOT updated

### Gate Walk-Through

#### Path A: Change made via Claude Code session

| Step | Gate | What Happens | Catches Drift? |
|------|------|--------------|----------------|
| 1 | Stop hook → `make validate-local` → `validate-agent-config` | Calls `validate-agent-config.sh` | — (continues below) |
| 2 | `validate-agent-config.sh` → `generate_agent_config.py --check` | AST-parses `deal_tools.py`, finds all `@tool`-decorated functions. Finds `get_deal_contacts` in code but NOT in `system.md` "Available Tools" section. Finds `get_deal_contacts` NOT in `tool-schemas.json`. | **YES — catches both mismatches** |
| 3 | `validate-agent-config.sh` → `validate_prompt_tools.py` | Secondary validation of prompt/tool consistency. | **YES** (backup) |
| 4 | `make validate-local` fails → stop hook `exit 2` | Session end blocked. | **YES — blocks** |

#### Path B: Change pushed directly via git (bypassing Claude Code)

| Step | Gate | What Happens | Catches Drift? |
|------|------|--------------|----------------|
| 1 | CI `agent-api` job | Runs ruff lint, mypy, pytest. None of these check tool/prompt/schema alignment. | **NO** |
| 2 | CI `type-sync` job | Only triggers on dashboard/contracts changes. `deal_tools.py` is in `apps/agent-api/`. **Job doesn't even run.** | **NO** (not triggered) |
| 3 | CI `contracts` job | Only triggers on `packages/contracts/**` changes. `deal_tools.py` change doesn't trigger. | **NO** (not triggered) |
| 4 | CI `gates` job | Aggregates other jobs. None caught it. | **NO** |
| 5 | `spec-freshness-bot.yml` (daily) | Checks spec freshness and codegen drift. Does NOT run `generate_agent_config.py`. Does NOT check tool/prompt alignment. | **NO** |

### Evidence (Path A — Claude Code)

```
FAIL: deal_tools functions missing from system.md Available Tools:
  - get_deal_contacts
FAIL: deal_tools functions missing from MCP tool-schemas.json:
  - get_deal_contacts
```

Stop hook output:
```
ERROR: Validation failed. Blocking stop hook.
```

### Evidence (Path B — Direct git push)

```
CI: All jobs passed. ✅
(Gate C never executed. Tool/prompt drift is live in main.)
```

### Kill-Switch Rule Analysis

**Path A (Claude Code session):** Fully automated. The stop hook fires `make validate-local` which includes `validate-agent-config` which runs `generate_agent_config.py --check`. No human action required. **PASS.**

**Path B (Direct git push):** Zero enforcement. The CI pipeline does not include Gate C (`generate_agent_config.py`). Gate C is a pure offline Python script that COULD run in CI (no service dependencies, no Docker requirement) but is NOT included. The plan claims "CI required checks: Gate A–H" (Section 3.10) but this is not implemented.

**Kill-switch rule for Path B:** The drift is only caught when someone next runs a Claude Code session (stop hook fires) — this relies on humans "eventually using Claude Code," which is functionally equivalent to "remembering to run something."

### v2 → v3 Change

v2 verdict was **PASS** — based on the stop hook enforcement chain being fully automated. v3 downgrades to **CONDITIONAL PASS** because:
1. The plan explicitly claims CI enforcement ("CI required checks: Gate A–H") that does not exist
2. Gate C is a pure offline script with zero dependencies — there is no technical reason it's not in CI
3. The bypass path (direct git push → CI green → drift is live) is realistic and undetected

### Verdict: CONDITIONAL PASS (downgraded from PASS in v2)

The stop hook enforcement works perfectly for Claude Code sessions. The CI enforcement gap creates a bypass path for direct git pushes. Gate C (`generate_agent_config.py`) is a pure offline script that should be added to CI.

---

## Scenario 3: Multi-DB Migration Mismatch / Split-Brain Reappears

### What Changes

A developer adds migration `005_add_contact_table.sql` to `zakops_agent`. The migration file is committed but NOT applied to the running database. The backend is updated to query this table via an API call to the agent service.

### Gate Walk-Through

| Step | Gate | What Happens | Catches Drift? |
|------|------|--------------|----------------|
| 1 | Stop hook → `make validate-local` | Runs sync-types, lint, tsc, contract-surfaces, agent-config, SSE schema. None of these check DB state. | **NO** — offline gate, can't check running DBs |
| 2 | CI pipeline | No migration assertion in any CI job. No database service for zakops_agent in CI (only a test DB). | **NO** — CI uses test DB, not production DBs |
| 3 | `make validate-live` → `migration-assertion.sh` | Checks `zakops_agent`: latest migration file = `005_add_contact_table`, DB applied version = `004_xxx`. **Version mismatch detected.** Exits 1. | **YES** |
| 4 | Backend DB check | If backend container down → `APPLIED` is empty → **FAIL** (not SKIP). If up but migration missing → version mismatch → FAIL. | **YES** (fixed from v1) |

### Evidence (When validate-live Runs)

```
=== Checking zakops_agent migrations ===
FAIL: zakops_agent - file=005_add_contact_table, db=004_create_indexes
=== Checking crawlrag migrations ===
crawlrag: OK (003_add_embeddings)
=== Checking zakops (backend) migrations ===
zakops: OK (047_add_audit_log)
==============================================================
FAILED: 1 database(s) have migration drift
```

### Kill-Switch Rule Analysis

**Offline path (automated — stop hook + CI):** Does NOT catch drift. Migration state is a runtime property — you can't check it without a running database. `validate-local` correctly excludes this check. CI correctly cannot check this without production DB services.

**Online path (manual — `make validate-live`):** DOES catch drift. `migration-assertion.sh` is wired into `validate-live` and checks all 3 databases. The backend SKIP→FAIL fix means unreachable databases are treated as failures, not silent passes.

**But:** `validate-live` is NOT automated. Same gap as Scenario 1.

### Verdict: CONDITIONAL PASS

Unchanged from v2. The gate works correctly. The gap is `validate-live` automation. This is inherently an online-only check.

---

## Comparative Summary: v1 → v2 → v3

| Scenario | v1 Verdict | v2 Verdict | v3 Verdict | What Changed in v3 |
|----------|------------|------------|------------|-------------------|
| 1: Backend schema change | **FAIL** | **CONDITIONAL PASS** | **CONDITIONAL PASS** | Unchanged — spec-freshness-bot provides marginal advisory coverage |
| 2: Agent tool added | **FAIL** | **PASS** | **CONDITIONAL PASS** ↓ | **DOWNGRADED** — CI does not include Gate C; bypass path via direct git push |
| 3: Multi-DB migration | **FAIL** | **CONDITIONAL PASS** | **CONDITIONAL PASS** | Unchanged — online-only check, validate-live still manual |

### Why v3 is Stricter Than v2

v2 only assessed the Claude Code enforcement path (stop hook → validate-local). v3 additionally audited the **CI enforcement path** (`ci.yml`) because the adopted plan explicitly claims "CI required checks: Gate A–H" (Section 3.10).

The CI audit revealed that the plan's CI claims are entirely aspirational — zero gates are implemented in CI. For online-only gates (F, I), this is acceptable (CI can't reach running services). But for offline gates (C, D, E, B), this is a gap: these scripts have no service dependencies and could run in CI with minimal effort.

---

## Enforcement Model: Dual-Path Analysis

### Current State

```
PATH 1: Claude Code Session (STRONG)
  stop.sh (AUTOMATED — session end)
    └─ make validate-local
         ├─ sync-types                         (Surface 1)
         ├─ sync-agent-types                   (Surface 4)
         ├─ lint-dashboard
         ├─ validate-contract-surfaces.sh      (Surfaces 1-7)  [Gate B]
         ├─ validate-agent-config.sh           (Surface 8)     [Gate C]
         │    ├─ generate_agent_config.py --check  (AST tool/prompt/MCP)
         │    └─ validate_prompt_tools.py          (secondary check)
         ├─ validate-sse-schema                (Surface 7)     [Gate D]
         ├─ tsc --noEmit
         └─ check-redocly-debt

PATH 2: CI Pipeline (WEAK — missing plan gates)
  ci.yml (AUTOMATED — push/PR)
    ├─ agent-api: ruff, mypy, pytest          [NO gate overlap]
    ├─ dashboard: npm lint, tsc, build, test  [PARTIAL Gate A overlap]
    ├─ contracts: Redocly lint, debt ceiling  [NO gate overlap]
    ├─ type-sync: codegen drift, imports      [PARTIAL Gate B overlap]
    └─ gates: aggregator only                 [NO gates invoked]

  ⚠ MISSING FROM CI: Gate B, Gate C, Gate D, Gate E

PATH 3: validate-live (MANUAL — requires running services)
  make validate-live
    ├─ make validate-local (above)
    ├─ check-spec-drift.sh                     [Gate I]
    └─ migration-assertion.sh                  [Gate F]

  ⚠ NO AUTOMATED TRIGGER (no pre-push hook, no cron, no CI job)

PATH 4: Advisory Bots (INFORMATIONAL — never block)
  spec-freshness-bot.yml (daily 6am UTC)     [::warning:: only]
  instructions-freshness-bot.yml (daily 7am) [::warning:: only]
```

### Gap Matrix

| Gate | Stop Hook | CI | validate-live | Advisory Bot |
|------|-----------|-----|--------------|-------------|
| A (validate-local) | ✅ | ⚠ partial (tsc only) | ✅ (includes validate-local) | — |
| B (contract surfaces) | ✅ | ⚠ partial (codegen drift) | ✅ | — |
| C (agent config) | ✅ | **❌ MISSING** | ✅ | — |
| D (SSE schema) | ✅ | **❌ MISSING** | ✅ | — |
| E (httpx ban) | ❌ | **❌ MISSING** | ❌ | — |
| F (migration) | ❌ (online) | ❌ (online) | ✅ | — |
| G (CLI availability) | ❌ | ❌ | ❌ | — |
| H (stop hook) | ✅ (self) | N/A | N/A | — |
| I (spec drift) | ❌ (online) | ❌ (online) | ✅ | ⚠ agent spec only |

---

## Required Patches (v3)

### Patch R-1: Automate `validate-live` (Severity: HIGH — carried from v2)

Same as v2. `validate-live` has no automated trigger. Scenarios 1 and 3 depend on it.

**Recommended:** CI pipeline job with service containers (Option C from v2).

### Patch R-2: Add Offline Gates to CI Pipeline (Severity: HIGH — NEW in v3)

The plan claims "CI required checks: Gate A–H" but CI implements none. Four offline gates (B, C, D, E) have zero service dependencies and can be added to CI today.

**Proposed implementation:**

```yaml
# Add to ci.yml under a new job or within existing agent-api job
  contract-gates:
    needs: changes
    if: needs.changes.outputs.agent-api == 'true' || needs.changes.outputs.contracts == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Gate B — Contract Surfaces
        run: bash tools/infra/validate-contract-surfaces.sh

      - name: Gate C — Agent Config (Surface 8)
        run: python3 tools/infra/generate_agent_config.py --check

      - name: Gate D — SSE Schema
        run: python3 tools/infra/validate_sse_schema.py

      - name: Gate E — httpx ban
        run: |
          MATCHES=$(rg -c "httpx\." apps/agent-api/app/core/langgraph/tools/deal_tools.py || echo 0)
          if [ "$MATCHES" != "0" ]; then
            echo "::error::Raw httpx usage found in deal_tools.py. Use BackendClient instead."
            exit 1
          fi
```

**Estimated effort:** 30 minutes. No new scripts required — all gate scripts already exist.

**Impact:** Closes the bypass path for Scenario 2 entirely. Any push (Claude Code or direct git) would trigger Gate C in CI.

### Patch R-3: Create `.claude/agents/` Directory (Severity: MEDIUM — carried from v2)

Phase 0 of the adopted plan. Workflow gap, not enforcement gap.

### Patch R-4: Upgrade Advisory Bots to Blocking (Severity: LOW — NEW in v3)

`spec-freshness-bot.yml` uses `::warning::` for all drift findings. Consider adding `::error::` + `exit 1` for critical drift (spec staleness > N days, missing required files). Low priority since this is a nightly check, not a push-time check.

---

## Updated Gates List (Final — v3)

| Gate | Command | Exists? | Stop Hook? | CI? | validate-live? | Advisory? |
|------|---------|---------|-----------|-----|---------------|-----------|
| A | `make validate-local` | YES | ✅ | ⚠ partial | ✅ | — |
| B | `validate-contract-surfaces.sh` | YES | ✅ | ⚠ partial | ✅ | — |
| C | `generate_agent_config.py --check` | YES | ✅ | **❌** | ✅ | — |
| D | `validate_sse_schema.py` | YES | ✅ | **❌** | ✅ | — |
| E | `rg httpx deal_tools.py` | YES | ❌ | **❌** | ❌ | — |
| F | `migration-assertion.sh` | YES | ❌ | ❌ (online) | ✅ | — |
| G | `command -v gemini && command -v codex` | N/A | ❌ | ❌ | ❌ | — |
| H | `stop.sh` | YES | ✅ | N/A | N/A | — |
| I | `check-spec-drift.sh` | YES | ❌ | ❌ (online) | ✅ | ⚠ agent only |

---

## Final Verdict

| Scenario | Stop Hook Catches? | CI Catches? | validate-live Catches? | Kill-Switch Rule | Verdict |
|----------|-------------------|------------|----------------------|------------------|---------|
| 1: Backend schema change | NO | NO | YES | CONDITIONAL — gate works but validate-live is manual | **CONDITIONAL PASS** |
| 2: Agent tool added | YES (via stop hook) | **NO** (Gate C not in CI) | YES | **CONDITIONAL** — works in Claude Code; bypass via direct git push | **CONDITIONAL PASS** |
| 3: Multi-DB migration | NO | NO | YES | CONDITIONAL — gate works but validate-live is manual | **CONDITIONAL PASS** |

### STATUS: CONDITIONAL PASS

**What CONDITIONAL PASS means in v3:** All 3 scenarios have gates that correctly detect drift. 8 of 10 enforcement fixes from v1 have been applied. Every gate script exists and works. The gaps are:

1. **`validate-live` has no automated trigger** (Scenarios 1, 3) — requires `make validate-live` to be run manually. Online checks inherently cannot be in validate-local or the stop hook.

2. **CI pipeline excludes all plan gates** (Scenario 2) — Gate C is the critical miss. It's a pure offline script that catches the highest-risk drift (tool/prompt misalignment) but is only enforced via the stop hook. A developer pushing via git bypasses it entirely.

**Why this is not a FAIL:** The kill-switch rule ("relies on humans remembering to run something") is partially violated — Scenario 2's CI bypass relies on developers using Claude Code. However, the gates themselves exist and work. The remediation is purely about wiring (add to CI, automate validate-live), not about creating new enforcement logic.

**Upgrade path to full PASS (2 patches):**
1. **Patch R-1:** Automate `validate-live` via CI job with service containers → Scenarios 1 and 3 become PASS
2. **Patch R-2:** Add Gates B, C, D, E to CI pipeline → Scenario 2 becomes PASS

Combined estimated effort: 1-2 hours. All scripts already exist; only CI wiring needed.

**v2 → v3 delta:** The only assessment change is Scenario 2 downgraded from PASS to CONDITIONAL PASS due to the CI gap discovery. The overall status remains CONDITIONAL PASS but with a second condition (CI wiring) added alongside the existing condition (validate-live automation).

---

*PASS 4 (TABLETOP SIMULATION — RE-RUN v3) COMPLETE. Status: CONDITIONAL PASS. 2 remaining patches: R-1 (automate validate-live) + R-2 (add offline gates to CI).*

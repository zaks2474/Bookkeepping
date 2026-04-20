# Codex Handoff — Generate Phase 0 Reconnaissance Mission (M-00)

**Prepared:** 2026-02-11
**Prepared by:** Claude (Opus 4.6)
**For:** Codex agent
**Priority:** IMMEDIATE — this is the next action in the UI Masterplan pipeline

---

## Your Task

Generate a **mission prompt** for **M-00: Reconnaissance Sprint** — the Phase 0 mission from the FINAL_MASTER strategy document. This is a **recon-only** mission: Playwright captures, console audits, accessibility snapshots, and findings cataloging. **Zero code changes.**

The mission prompt must conform to **Mission Prompt Standard v2.1** and pass the structural validator with **0 FAILs**.

---

## Step-by-Step Procedure

### Step 1: Read These Files (in this order)

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 1 | `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | The authoritative standard (v2.1) — defines every required section | ~873 |
| 2 | `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | 1-page cheat sheet with skeletons | ~68 |
| 3 | `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | THE source document — Phase 0 spec, Gate 0, all 12 findings | 420 |
| 4 | `/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md` | Recent validated+executed v2.1 mission — use as structural reference | 361 |

### Step 2: Extract Phase 0 Requirements from FINAL_MASTER

The FINAL_MASTER contains all the source material you need. Key sections:

- **Lines 265-272** — Phase 0 mission table + deliverables + Playwright tools
- **Lines 336-343** — Gate 0 acceptance criteria (5 pass criteria)
- **Lines 80-89** — F-5: Playwright MCP integration strategy (Phase 0 specifics)
- **Lines 122-137** — F-8: Interaction wiring inventory (required Phase 0 deliverable)
- **Lines 185-191** — F-11: B7 anti-convergence clarification (MUST include in every mission)
- **Lines 396-409** — Risk register (relevant risks: R-1, R-3, R-5, R-7, R-8)
- **Lines 380-392** — Definition of Done (context for what Phase 0 feeds into)

### Step 3: Generate the Mission Prompt

**Output location:** `/home/zaks/bookkeeping/missions/UI-MASTERPLAN-M00-RECON.md`

**Mission ID:** `UI-MASTERPLAN-M00`

Use the v2.1 Execution Mission structure. Here are the specific content requirements:

#### Header (7 fields)
```
# MISSION: UI-MASTERPLAN-M00
## Dashboard Reconnaissance Sprint — Visual Baseline & Findings Catalog
## Date: 2026-02-11
## Classification: Reconnaissance / Audit
## Prerequisite: None — this is Phase 0
## Successor: UI-MASTERPLAN-M01, UI-MASTERPLAN-M02, UI-MASTERPLAN-M03 (Phase 1, parallel-safe, blocked until this passes)
```

#### Mission Objective — Must Include
- This is a **recon-only** mission — zero code changes, zero refactoring
- Purpose: establish the visual baseline and findings catalog that drives all subsequent missions
- The builder uses **Playwright MCP** (22 browser tools) to systematically capture every page
- Deliverables are **artifacts** (screenshots, catalogs, inventories), not code
- Explicit scope: "If you discover a bug, catalog it — do NOT fix it"

#### Context — Must Include
- Reference FINAL_MASTER as source: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`
- The dashboard is a Next.js 15 app at `http://localhost:3003` (12 pages, ~26,600 lines, 120+ components)
- 3 agents (Claude, Gemini, Codex) unanimously chose Strategy C (Hybrid)
- Phase 0 is the evidence-gathering phase that feeds Phase 1-3 mission generation
- Dashboard runs as bare Next.js (NOT Docker) — must be running before mission starts

#### Architectural Constraints — Must Include
- **Playwright MCP tools available:** `browser_navigate`, `browser_resize`, `browser_take_screenshot`, `browser_console_messages`, `browser_snapshot` (plus 17 others)
- **3 breakpoints:** 375px (mobile), 768px (tablet), 1280px (desktop) — per Surface 9 rule
- **No code changes** — this is not a build mission
- **B7 anti-convergence does not apply to this mission** — we are standardizing existing patterns (F-11)
- **Artifact storage:** All screenshots and catalogs go to `/home/zaks/bookkeeping/missions/m00-artifacts/`

#### 12 Pages to Capture (derive from dashboard routes)
The builder must navigate and capture ALL of these:

| # | Page | Route | Tier |
|---|------|-------|------|
| 1 | Dashboard | `/dashboard` | Tier 3 |
| 2 | Deals List | `/deals` | Tier 2 |
| 3 | Deal Workspace | `/deals/[id]` | Tier 1 |
| 4 | Actions | `/actions` | Tier 1 |
| 5 | Chat | `/chat` | Tier 1 |
| 6 | Quarantine | `/quarantine` | Tier 2 |
| 7 | Agent Activity | `/agent-activity` | Tier 2 |
| 8 | Operator HQ | `/hq` | Tier 2 |
| 9 | Settings | `/settings` | Tier 3 |
| 10 | Onboarding | `/onboarding` | Tier 3 |
| 11 | New Deal | `/deals/new` | Tier 3 |
| 12 | Home (redirect) | `/` | Tier 3 |

Note: Deal Workspace (`/deals/[id]`) needs a real deal ID from the database or API. The builder should fetch one first.

#### Phase Structure — Recommended 4 Phases

**Phase 0 — Pre-Flight & Environment Verification**
- Verify dashboard is running at `http://localhost:3003`
- Verify Playwright MCP tools are available (22 tools)
- Create artifact directory `/home/zaks/bookkeeping/missions/m00-artifacts/`
- Gate: Dashboard loads, Playwright responds to `browser_navigate`

**Phase 1 — Systematic Page Capture**
- For each of 12 pages, at each of 3 breakpoints:
  - `browser_navigate` to the page
  - `browser_resize` to breakpoint width
  - `browser_take_screenshot` (save with naming: `{page}-{breakpoint}.png`)
  - `browser_console_messages` (capture any errors/warnings)
  - `browser_snapshot` (accessibility tree)
- Expected artifact count: 36+ screenshots, 12 console logs, 12 accessibility snapshots
- Gate: All 12 pages captured at all 3 breakpoints, files exist in artifacts directory

**Phase 2 — Analysis & Cataloging**
- Review all screenshots and classify findings as cross-cutting vs page-specific
- Build console error catalog (page → errors at each breakpoint)
- Build interaction wiring inventory (F-8): for each page, list every visible control and its wiring status (real endpoint / mock / placeholder / broken)
- Assign severity to each finding (Sev-1 critical, Sev-2 major, Sev-3 minor)
- Gate: Findings catalog complete, interaction inventory complete, all findings have severity

**Phase 3 — Priority Ranking & Report**
- Rank all findings by severity × impact
- Map findings to FINAL_MASTER missions (which finding feeds which M-XX mission)
- Produce final summary report at `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- Gate: Report exists with priority rankings and mission mappings

#### Acceptance Criteria (derive from Gate 0 in FINAL_MASTER)

| AC | Description | Verification |
|----|-------------|-------------|
| AC-1 | All 12 pages captured at 375/768/1280px | 36+ screenshot files exist in artifacts directory |
| AC-2 | Console error catalog complete | Catalog lists errors per page per breakpoint |
| AC-3 | Findings categorized as cross-cutting vs page-specific | Each finding has a category tag |
| AC-4 | Priority ranking assigned to all findings | Each finding has severity + priority rank |
| AC-5 | Interaction wiring inventory for all pages | Every visible control on every page mapped |
| AC-6 | Accessibility tree snapshots captured | 12 snapshot files exist |
| AC-7 | RECON-REPORT.md produced with mission mappings | Report maps findings → M-XX missions |
| AC-8 | No code changes made | `git diff` shows zero changes in application code |
| AC-9 | CHANGES.md updated | Entry recorded in `/home/zaks/bookkeeping/CHANGES.md` |

#### Anti-Pattern Examples — Must Include

```
### WRONG: Fixing a bug during recon
  # Noticed a CSS misalignment — fix it
  Edit: apps/dashboard/src/app/deals/page.tsx  # NO — catalog it, don't fix it

### RIGHT: Cataloging a bug during recon
  # Noticed a CSS misalignment — add to findings catalog
  Finding: F-XX — deals page header misaligned at 375px (Sev-2)
  Mapped to: M-07 (Deals List Polish)

### WRONG: Running tests or validators
  npx playwright test  # NO — this is recon, not QA

### RIGHT: Using Playwright MCP tools for capture
  browser_navigate → browser_resize → browser_take_screenshot → browser_console_messages
```

#### Pre-Mortem — Must Include
- Dashboard not running → Pre-flight check catches it
- Deal workspace needs a real ID → Fetch from API first
- Playwright MCP not responding → Verify tools list in pre-flight
- Console output too verbose → Filter by error level only
- Backend down → Capture graceful degradation state (valuable data point)

#### Guardrails — Must Include
- DO NOT modify any application code (zero `git diff` on app files)
- DO NOT run `make validate-local` or `make sync-*` (no code changes = no validation needed)
- DO NOT fix bugs — catalog them
- DO NOT run E2E tests — this is manual Playwright capture
- ALL artifacts stored in `/home/zaks/bookkeeping/missions/m00-artifacts/`
- B7 anti-convergence does not apply to this mission

#### Self-Check Prompts — Must Include
- [ ] "Am I ONLY capturing and cataloging? I must not change any code."
- [ ] "Did I capture all 12 pages at all 3 breakpoints?"
- [ ] "Does my interaction inventory cover every visible control on every page?"
- [ ] "Did I map each finding to a specific M-XX mission from the FINAL_MASTER?"
- [ ] "Is the backend up? If not, did I capture the graceful degradation state?"
- [ ] "Did I include B7 anti-convergence clarification?"

### Step 4: Validate the Mission Prompt

After generating the file, run the structural validator:

```bash
bash /home/zaks/zakops-agent-api/tools/infra/validate-mission.sh /home/zaks/bookkeeping/missions/UI-MASTERPLAN-M00-RECON.md
```

**Target: 0 FAILs, STRUCTURALLY COMPLETE verdict.**

The validator checks 26 items across 7 groups:
1. **Header** — Mission ID, date, classification, prerequisite, successor
2. **Core Sections** — Objective, context, constraints, phases, ACs, guardrails, stop conditions
3. **Quality Markers** — Anti-patterns, pre-mortem, self-checks
4. **Phase Quality** — Every phase has a gate, complexity labels
5. **Evidence & Discipline** — File paths, rollback procedures
6. **IA Adoption** — Improvement areas from the standard
7. **Gate Count** — At least one formal gate

If FAILs are reported, fix the corresponding section and re-run. Common fixes:
- Missing `## File Paths` section → Add a table of files to create/modify/read
- Missing gate patterns → Name gates as `### Gate P0:`, `### Gate P1:` etc.
- Missing stop conditions → Add `## Stop Conditions` with 3-5 concrete triggers

### Step 5: Post-Generation Checklist

- [ ] File saved to `/home/zaks/bookkeeping/missions/UI-MASTERPLAN-M00-RECON.md`
- [ ] Validator returns 0 FAILs
- [ ] Mission ID is `UI-MASTERPLAN-M00` (consistent with FINAL_MASTER naming)
- [ ] All 12 pages listed with routes
- [ ] Playwright MCP tools referenced (not generic Playwright test runner)
- [ ] B7 clarification included (F-11)
- [ ] Interaction closure inventory included (F-8)
- [ ] Gate 0 criteria from FINAL_MASTER are reflected in ACs
- [ ] No implementation code in the prompt (per standard: "mission prompts never include implementation code")
- [ ] "Reference, don't repeat" principle followed — no copied CLAUDE.md/MEMORY.md content

---

## Key Principles to Follow

### 1. Reference, Don't Repeat
The builder already loads CLAUDE.md, MEMORY.md, hooks, and rules. Say "per Surface 9" — don't copy the rules. Say "per contract surface discipline" — don't re-explain the sync pipeline.

### 2. No Implementation Code
Mission prompts tell the builder WHAT to do and WHERE, not HOW. Include bash commands for verification only. Include anti-pattern examples showing WRONG vs RIGHT.

### 3. Every Phase Needs a Gate
No gateless phases. Each gate must have a concrete pass/fail criterion. Use `make validate-local` where appropriate (but NOT for this recon mission since there are no code changes).

### 4. F-11 B7 Clarification Is Mandatory
Every mission in this UI Masterplan initiative must state: "B7 anti-convergence does not apply to this mission — we are standardizing existing patterns."

### 5. F-8 Interaction Closure
Phase 0 must produce the interaction wiring inventory. This feeds every Phase 2 mission's interaction closure checklist. Map every visible control to: real endpoint / mock / placeholder / broken.

---

## Reference: Validated Mission Example

`/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md` is a recently validated and executed v2.1 mission. Use it as a structural reference for:
- Header format (7 fields)
- Anti-pattern examples format (WRONG/RIGHT blocks)
- Pre-mortem table format
- Phase structure with gates
- Acceptance criteria table format
- Self-check prompts format

---

## Reference: FINAL_MASTER Key Sections Quick Index

| Content | FINAL_MASTER Lines |
|---------|-------------------|
| Phase 0 mission table + deliverables | 265-272 |
| Gate 0 acceptance criteria | 336-343 |
| F-5: Playwright integration by phase | 80-89 |
| F-8: Interaction wiring inventory | 122-137 |
| F-11: B7 anti-convergence | 185-191 |
| Risk register | 396-409 |
| Mission dependency graph | 320-328 |
| Definition of Done | 380-392 |
| Page complexity tiering (F-2) | 32-41 |

---

## After M-00 Is Generated and Validated

The next steps in the pipeline are:
1. **Execute M-00** (the builder runs the recon mission)
2. **Generate M-01, M-02, M-03** (Phase 1 missions, using Phase 0 findings as input)
3. Each subsequent mission uses the same process: read FINAL_MASTER → generate v2.1 prompt → validate → execute

The M-01/M-02/M-03 missions are **parallel-safe** (no dependencies between them) but ALL depend on M-00 completing first (Phase 0 findings feed Phase 1 scope).

---

*Generated by Claude (Opus 4.6) — 2026-02-11*

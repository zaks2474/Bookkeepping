# MISSION: UI-MASTERPLAN-M00
## Dashboard Reconnaissance Sprint - Visual Baseline & Findings Catalog
## Date: 2026-02-11
## Classification: Reconnaissance / Audit
## Prerequisite: None - this is Phase 0
## Successor: UI-MASTERPLAN-M01, UI-MASTERPLAN-M02, UI-MASTERPLAN-M03 (Phase 1, parallel-safe, blocked until this passes)

---

## File Paths Reference

### Files to Modify

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/CHANGES.md` | Record mission execution entry after recon artifacts are complete |

### Files to Create

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/` | Artifact root for all Phase 0 evidence |
| `/home/zaks/bookkeeping/missions/m00-artifacts/screenshots/` | 36+ screenshots (12 pages x 3 breakpoints) |
| `/home/zaks/bookkeeping/missions/m00-artifacts/console/` | Console captures per page per breakpoint |
| `/home/zaks/bookkeeping/missions/m00-artifacts/accessibility/` | Accessibility tree snapshots |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/` | Findings catalog, interaction wiring inventory, rankings |
| `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md` | Final Phase 0 report with mission mappings |

### Files to Read (sources of truth - do NOT modify)

| Path | Why it matters |
|------|----------------|
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Mission Prompt Standard v2.1 structural authority |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Quick structural checklist for execution mission formatting |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 0 requirements, Gate 0 criteria, risk register, dependency graph |
| `/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md` | Validated mission format reference |

---

## Mission Objective

Execute a recon-only baseline sprint for the ZakOps dashboard. This mission captures visual and runtime evidence across all 12 routes at 3 responsive breakpoints using Playwright MCP, then converts that evidence into a findings catalog and prioritized mission map.

This is **not** a build/refactor mission. There are zero application code edits, zero API edits, and zero UI fixes in this mission. If you discover a bug, catalog it with evidence and severity - do not fix it.

Deliverables are artifacts, not code: screenshots, console audits, accessibility snapshots, interaction wiring inventory, prioritized findings, and a final report at `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`.

---

## Context

Source of truth is `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`.

Key context from FINAL_MASTER:
- The dashboard is a Next.js 15 app at `http://localhost:3003` with 12 pages, about 26,600 lines, and 120+ components.
- Claude, Gemini, and Codex unanimously selected Strategy C (Hybrid).
- Phase 0 is the evidence-gathering phase that blocks/unblocks Phase 1 mission generation.
- Phase 0 deliverables (FINAL_MASTER lines 265-272) are baseline artifacts: screenshots, console catalog, accessibility snapshots, findings categories, priority ranking, and interaction wiring inventory.
- Gate 0 (FINAL_MASTER lines 336-343) requires complete coverage and classified findings before moving to Phase 1.
- F-8 requires interaction wiring inventory for every visible control (real endpoint / mock / placeholder / broken).
- F-11 requires explicit clarification in every mission: **B7 anti-convergence does not apply to this mission - we are standardizing existing patterns.**

Runtime context:
- Dashboard must run as bare Next.js at `http://localhost:3003` (not Docker) before execution starts.
- If backend services are degraded or down, capture graceful degradation behavior as evidence instead of treating it as a blocker.

---

## Glossary

| Term | Definition |
|------|------------|
| Playwright MCP | The 22-tool browser-control interface used for interactive navigation, capture, console audit, and accessibility snapshots. |
| Cross-cutting finding | A defect pattern that appears across multiple pages and should map to shared/foundation missions. |
| Page-specific finding | A defect pattern isolated to one route or one local interaction surface. |
| Interaction wiring inventory | Per-page list of visible controls mapped to `real endpoint`, `mock`, `placeholder`, or `broken` state (F-8). |
| Graceful degradation | Expected UI behavior when backend dependencies are unavailable; captured as evidence rather than fixed in Phase 0. |

---

## Architectural Constraints

- **Playwright MCP first-class usage:** Use Playwright MCP browser tools, especially `browser_navigate`, `browser_resize`, `browser_take_screenshot`, `browser_console_messages`, and `browser_snapshot` (plus the rest of the 22-tool set as needed).
- **Surface 9 breakpoint rule:** Every page is captured at `375px`, `768px`, and `1280px` widths.
- **Recon-only scope:** No code changes, no refactors, no dependency updates, no generated file changes.
- **Bug handling rule:** If a defect is found, capture and catalog it; do not patch it in this mission.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission - we are standardizing existing patterns.
- **Artifact location lock:** All screenshots, logs, snapshots, and reports must remain under `/home/zaks/bookkeeping/missions/m00-artifacts/`.
- **Validation command fence:** Do not run `make validate-local`, `make sync-*`, or E2E test suites for this recon mission.
- **No Playwright test runner:** Use interactive Playwright MCP capture flow, not `npx playwright test`.

---

## Route Coverage Matrix (12 Pages)

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

Deal Workspace route requirement:
- Fetch a real deal ID from API or database before capturing `/deals/[id]`.
- Record the chosen ID in artifact metadata for reproducibility.

---

## Anti-Pattern Examples

### WRONG: Fixing a bug during recon
```bash
# Noticed a CSS misalignment - fix it
Edit: apps/dashboard/src/app/deals/page.tsx  # NO - catalog it, do not fix it
```

### RIGHT: Cataloging a bug during recon
```text
# Noticed a CSS misalignment - add to findings catalog
Finding: F-XX - deals page header misaligned at 375px (Sev-2)
Mapped to: M-07 (Deals List Polish)
```

### WRONG: Running tests or validators
```bash
npx playwright test  # NO - this is recon, not QA
make validate-local  # NO - no code changes in this mission
```

### RIGHT: Using Playwright MCP tools for capture
```text
browser_navigate -> browser_resize -> browser_take_screenshot -> browser_console_messages -> browser_snapshot
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Dashboard is not running at mission start | Medium | High | Phase 0 pre-flight verifies `http://localhost:3003` before capture starts |
| 2 | `/deals/[id]` capture fails due to missing real ID | Medium | Medium | Phase 1 includes explicit ID discovery step before route navigation |
| 3 | Playwright MCP tools are unavailable or stale | Low | High | Phase 0 tool response check gates mission start |
| 4 | Console logs become noisy and hard to triage | Medium | Medium | Phase 2 catalog filters and classifies by error severity first |
| 5 | Backend is unavailable during route capture | Medium | Medium | Capture graceful degradation state and classify as evidence, not blocker |

---

## Phase 0 - Pre-Flight & Environment Verification
**Complexity:** S
**Estimated touch points:** 0 code files, 1 artifact directory

**Purpose:** Confirm runtime/tool readiness and establish the artifact workspace before route capture.

### Blast Radius
- **Services affected:** Dashboard runtime at `http://localhost:3003`, Playwright MCP browser tool channel
- **Pages affected:** None (readiness checks only)
- **Downstream consumers:** Phase 1-3 mission generation uses these artifacts as source evidence

### Tasks
- P0-01: **Verify dashboard availability**
  - Evidence: pre-flight note in `/home/zaks/bookkeeping/missions/m00-artifacts/findings/preflight.md`
  - Checkpoint: `http://localhost:3003` returns and renders
- P0-02: **Verify Playwright MCP responsiveness** (`browser_navigate` smoke check)
  - Evidence: tool response log in `/home/zaks/bookkeeping/missions/m00-artifacts/findings/preflight.md`
  - Checkpoint: at least one successful navigate call
- P0-03: **Create artifact directory structure**
  - Evidence: `/home/zaks/bookkeeping/missions/m00-artifacts/` and child folders exist
  - Checkpoint: folder tree created before capture begins

### Decision Tree
- IF dashboard is unreachable -> stop and restore runtime before continuing.
- ELSE IF Playwright MCP does not respond -> restart MCP session/tools and repeat P0-02.
- ELSE -> proceed to Phase 1.

### Rollback Plan
1. Remove incomplete artifact tree if pre-flight setup was incorrect.
2. Re-create clean directory structure and re-run P0-01 through P0-03.

### Gate P0
Pass when dashboard runtime is confirmed, Playwright MCP responds to navigation, and artifact directories exist.

---

## Phase 1 - Systematic Page Capture
**Complexity:** M
**Estimated touch points:** 12 routes x 3 breakpoints x 3 artifact families

**Purpose:** Capture screenshots, console signals, and accessibility snapshots for all required routes.

### Blast Radius
- **Services affected:** Dashboard frontend routes and their API dependencies (read-only observation)
- **Pages affected:** All 12 routes listed in Route Coverage Matrix
- **Downstream consumers:** Findings catalog, interaction inventory, and Phase 1+ mission prompts

### Tasks
- P1-01: **Resolve dynamic route parameter for Deal Workspace**
  - Evidence: selected deal ID recorded in `/home/zaks/bookkeeping/missions/m00-artifacts/findings/preflight.md`
  - Checkpoint: navigable route for `/deals/[id]` confirmed
- P1-02: **Capture screenshot triad per page**
  - Capture sequence per route and breakpoint: `browser_navigate` -> `browser_resize` -> `browser_take_screenshot`
  - Naming convention: `{page-slug}-{breakpoint}.png` under `/home/zaks/bookkeeping/missions/m00-artifacts/screenshots/`
  - Checkpoint: 36+ screenshot files exist
- P1-03: **Capture console output per page**
  - Use `browser_console_messages` and store page/breakpoint log files under `/home/zaks/bookkeeping/missions/m00-artifacts/console/`
  - Checkpoint: catalog contains all pages and all breakpoints
- P1-04: **Capture accessibility tree per page**
  - Use `browser_snapshot` once per page after baseline load
  - Checkpoint: 12 snapshot files exist in `/home/zaks/bookkeeping/missions/m00-artifacts/accessibility/`
- P1-05: **Maintain capture index**
  - Evidence: `/home/zaks/bookkeeping/missions/m00-artifacts/findings/capture-index.md`
  - Checkpoint: index row exists for every page + breakpoint with artifact links

### Decision Tree
- IF a route hard-fails due to backend outage -> capture degraded UI state and log the dependency failure.
- ELSE IF only one breakpoint fails -> retry that breakpoint once, then log as capture defect.
- ELSE -> continue sequentially until all 12 routes are covered.

### Rollback Plan
1. Delete only incomplete artifacts for failed page/breakpoint combinations.
2. Re-run P1-02 through P1-05 for missing combinations.

### Gate P1
Pass when all 12 pages are captured at 375/768/1280 with 36+ screenshots, complete console logs, and 12 accessibility snapshots.

---

## Phase 2 - Analysis & Cataloging
**Complexity:** M
**Estimated touch points:** 3 evidence catalogs + 1 interaction inventory

**Purpose:** Convert raw capture evidence into categorized, severity-tagged findings and complete interaction wiring inventory.

### Blast Radius
- **Services affected:** None (artifact analysis only)
- **Pages affected:** All 12 pages through evidence review
- **Downstream consumers:** M-01 through M-12 mission scoping

### Tasks
- P2-01: **Build findings catalog**
  - Evidence: `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
  - Requirement: every finding tagged as cross-cutting or page-specific with Sev-1/Sev-2/Sev-3
  - Checkpoint: no uncategorized findings remain
- P2-02: **Build console error catalog**
  - Evidence: `/home/zaks/bookkeeping/missions/m00-artifacts/findings/console-error-catalog.md`
  - Requirement: page -> breakpoint -> error/warning map
  - Checkpoint: every page has explicit console status at all breakpoints
- P2-03: **Build interaction wiring inventory (F-8)**
  - Evidence: `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
  - Requirement: every visible control mapped to `real endpoint`, `mock`, `placeholder`, or `broken`
  - Checkpoint: 100% visible controls mapped for all 12 pages
- P2-04: **Assign mission mapping hints**
  - Evidence: mission candidates column in findings catalog
  - Checkpoint: each finding has a likely downstream mission target (M-01 through M-12)

### Decision Tree
- IF evidence is ambiguous -> retain screenshot/log link and mark as "needs confirmation" with provisional severity.
- ELSE IF finding appears on 3+ pages -> classify as cross-cutting.
- ELSE -> classify as page-specific.

### Rollback Plan
1. Rebuild affected catalog from capture index if classification mistakes are found.
2. Keep original raw artifacts unchanged.

### Gate P2
Pass when findings are categorized, all findings have severity, console catalog is complete, and interaction wiring inventory covers all visible controls.

---

## Phase 3 - Priority Ranking & Recon Report
**Complexity:** S
**Estimated touch points:** 1 final report + 1 bookkeeping entry

**Purpose:** Produce actionable ranking and mission mapping output that unblocks Phase 1 execution missions.

### Blast Radius
- **Services affected:** None (documentation output only)
- **Pages affected:** Indirectly all pages via downstream mission planning
- **Downstream consumers:** UI-MASTERPLAN-M01/M02/M03 authors and builders

### Tasks
- P3-01: **Rank findings by severity x impact**
  - Evidence: ranking table in `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
  - Checkpoint: all findings have rank order
- P3-02: **Map findings to mission backlog**
  - Evidence: findings -> mission mapping table in `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
  - Checkpoint: each finding maps to specific M-XX target(s)
- P3-03: **Finalize report narrative**
  - Include route coverage status, console summary, interaction closure summary, and open risk notes (R-1, R-3, R-5, R-7, R-8)
  - Checkpoint: report is complete and readable without external context
- P3-04: **Update bookkeeping log**
  - Evidence: entry in `/home/zaks/bookkeeping/CHANGES.md`
  - Checkpoint: entry references `UI-MASTERPLAN-M00`

### Decision Tree
- IF an Sev-1 finding lacks clear mission mapping -> assign interim owner and flag as blocking in report.
- ELSE -> complete report and mark Phase 0 done.

### Rollback Plan
1. Keep prior report revision as backup in `/home/zaks/bookkeeping/missions/m00-artifacts/`.
2. Re-rank and remap findings without altering raw capture artifacts.

### Gate P3
Pass when `RECON-REPORT.md` exists with priority rankings and mission mappings, and `CHANGES.md` has an entry for `UI-MASTERPLAN-M00`.

---

## Dependency Graph

```text
Phase 0 (Pre-Flight)
  -> Phase 1 (Systematic Capture)
    -> Phase 2 (Analysis & Cataloging)
      -> Phase 3 (Priority Ranking & Report)
```

---

## Acceptance Criteria

| AC | Description | Verification |
|----|-------------|-------------|
| AC-1 | All 12 pages captured at 375/768/1280px | 36+ screenshot files exist in `/home/zaks/bookkeeping/missions/m00-artifacts/screenshots/` |
| AC-2 | Console error catalog complete | `/home/zaks/bookkeeping/missions/m00-artifacts/findings/console-error-catalog.md` lists errors per page per breakpoint |
| AC-3 | Findings categorized as cross-cutting vs page-specific | Every finding in `findings-catalog.md` has category tag |
| AC-4 | Priority ranking assigned to all findings | `RECON-REPORT.md` contains ranked list for all findings |
| AC-5 | Interaction wiring inventory for all pages | `interaction-wiring-inventory.md` maps every visible control on every page |
| AC-6 | Accessibility tree snapshots captured | 12 files exist under `/home/zaks/bookkeeping/missions/m00-artifacts/accessibility/` |
| AC-7 | `RECON-REPORT.md` produced with mission mappings | Report maps findings to specific M-XX missions |
| AC-8 | No code changes made | `git diff` shows zero changes in application code paths |
| AC-9 | CHANGES.md updated | Entry recorded in `/home/zaks/bookkeeping/CHANGES.md` |

---

## Guardrails

1. DO NOT modify any application code (must end with zero `git diff` on app files).
2. DO NOT run `make validate-local` or `make sync-*` (no code-change validation is needed for recon).
3. DO NOT fix bugs during this mission; catalog defects only.
4. DO NOT run E2E test suites (`npx playwright test` is out of scope).
5. ALL artifacts must remain in `/home/zaks/bookkeeping/missions/m00-artifacts/`.
6. B7 anti-convergence does not apply to this mission - we are standardizing existing patterns.
7. Use Playwright MCP browser tooling for capture; do not switch to generic scripted test runners.
8. Preserve evidence integrity: never overwrite a capture file without incrementing filename/version note.
9. If backend is unavailable, capture graceful degradation behavior as valid evidence.

---

## Crash Recovery Protocol (Adopted from IA-2)

If execution is interrupted:
1. Resume from `/home/zaks/bookkeeping/missions/m00-artifacts/findings/capture-index.md` and identify uncaptured page/breakpoint cells.
2. Do not delete successful captures; continue only missing capture units.
3. Re-run the current phase gate before moving to the next phase.

---

## Self-Check Prompts

- [ ] "Am I ONLY capturing and cataloging? I must not change any code."
- [ ] "Did I capture all 12 pages at all 3 breakpoints?"
- [ ] "Does my interaction inventory cover every visible control on every page?"
- [ ] "Did I map each finding to a specific M-XX mission from the FINAL_MASTER?"
- [ ] "Is the backend up? If not, did I capture the graceful degradation state?"
- [ ] "Did I include B7 anti-convergence clarification?"
- [ ] "Did I create ALL files/directories listed in the Files to Create table?"

---

## Stop Condition

Stop when all four gates (P0, P1, P2, P3) pass, AC-1 through AC-9 are satisfied, and the mission produces a complete evidence bundle under `/home/zaks/bookkeeping/missions/m00-artifacts/` plus `RECON-REPORT.md`.

Do not proceed to `UI-MASTERPLAN-M01`, `UI-MASTERPLAN-M02`, or `UI-MASTERPLAN-M03` until this mission is complete and Gate P3 has passed.

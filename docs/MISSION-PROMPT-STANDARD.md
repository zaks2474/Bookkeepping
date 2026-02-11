# ZakOps Mission Prompt Generation Standard — Complete Reference

**Standard Version:** 2.0
**Last Updated:** 2026-02-10
**Change Log:** See [Version History](#version-history) at end of document

---

## Preamble: Builder Operating Environment

The builder (Claude Code) automatically loads `CLAUDE.md`, `MEMORY.md`, path-scoped rules, hooks, and deny rules at session start. **Mission prompts do not repeat that configuration.** They reference it by name and only call out mission-specific deviations.

### What the Builder Already Knows (loaded before reading any mission)

- **CLAUDE.md** — Architectural constraints, sync commands, contract surfaces, guardrails
- **MEMORY.md** — Project map, databases, make targets, key file locations, completed missions
- **7 hooks** — Session lifecycle enforcement (pre-edit blocks generated files, stop runs validation)
- **5 path-scoped rules** — Auto-injected conventions for agent-api, backend, contracts, dashboard, design system
- **12 deny rules** — Tool-level blocks on generated files, `.env`, destructive commands
- **3 delegated agents** — contract-guardian, arch-reviewer, test-engineer
- **9 contract surfaces** — Sync pipelines with `make sync-*` commands
- **15 slash commands** — `/before-task`, `/after-change`, `/sync-all`, `/validate`, etc.

### What Mission Prompts Add (information the builder does NOT already have)

- **Mission-specific objective, scope, and context** — what to build/fix/verify THIS time
- **Mission-specific constraints** — patterns or restrictions unique to this mission beyond the standing rules
- **Phase structure with gates** — the ordered work plan with verification at each step
- **Deviations from standard behavior** — if this mission requires overriding or extending a standing rule, call it out explicitly
- **Acceptance criteria** — the specific definition of DONE for this mission

### Rule for Prompt Authors

**Reference, don't repeat.** Say "Surface 9 applies" — don't copy the design system rules. Say "per contract surface discipline" — don't re-explain the sync pipeline. Only elaborate when the mission DEVIATES from or EXTENDS a standing rule.

---

## Two Mission Types

We produce **two distinct document types**, each with its own anatomy:

1. **Execution Missions** (prefix: `MISSION-`) — Build, fix, or remediate
2. **QA Verification & Remediation Missions** (prefix: `QA-`) — Audit and verify a completed execution mission

### Code Snippet Policy

Mission prompts **never include implementation code** (no TypeScript functions, no Python classes, no "write this exact code"). The executor decides HOW to implement. We tell it WHAT to change and WHERE.

What IS included:
- **Bash search/grep commands** for discovery and verification
- **Bash validation commands** (`make validate-local`, `npx tsc`)
- **Architecture diagrams** in ASCII or plaintext
- **QA evidence-capture commands** with `tee`
- **Anti-pattern examples** showing the WRONG way vs. RIGHT way (see Section 3b)

---

## TYPE 1: EXECUTION MISSION PROMPT

### Document Header (Mandatory, 7 fields)

```
# MISSION: {MISSION-ID}
## {Subtitle — human-readable description}
## Date: {YYYY-MM-DD}
## Classification: {Category — e.g., Infrastructure Remediation, Feature Build, Platform Stabilization}
## Prerequisite: {Mission ID or condition that must be complete first}
## Successor: {What mission is blocked until this one passes}
```

### Section 1: Mission Objective (1–3 paragraphs)

- **What** this mission does, in plain English
- **What it is NOT** (explicit scope boundary — "this is a FIX mission, not a BUILD mission")
- **Source material** with absolute file paths (audit reports, prior mission outputs, forensic findings)
- The objective sets the mental frame for the executor — it knows whether it's building, fixing, or sweeping

### Section 2: Context (Variable length)

Provide the executor with everything it needs to understand the current state:

- **What the source audit/report found** — numbered list of concrete findings with enough detail that each can be independently verified
- **Environment changes since the original work** — if the codebase has evolved, document what's different
- **Prior deliverables that must not be regressed** — name them explicitly with evidence paths

### Section 2b: Glossary (If mission introduces or relies on non-obvious terms)

Define domain-specific terms so a fresh executor session with no memory can understand the mission without guessing.

```
## Glossary

| Term | Definition |
|------|-----------|
| Surface 9 | Component Design System — `.claude/rules/design-system.md`. Governs dashboard UI conventions |
| Bridge file | `apps/dashboard/types/api.ts` — the only file that may import from generated types |
| Choke point | A single function that ALL code paths must use (e.g., `transition_deal_state()`) |
| Hybrid Guardrail | Pattern: OpenAPI spec → codegen → generated file → bridge file → consumer |
| Contract surface | A defined boundary between services with a sync pipeline maintaining type agreement |
```

Only include terms that: (a) are project-specific jargon, (b) appear more than once in the mission, (c) would be ambiguous to a reader without project history.

### Section 3: Architectural Constraints (MANDATORY block)

Non-negotiable patterns the executor must preserve. Listed as bullet points, each with:
- The pattern name in bold
- What it means concretely
- Why it exists

Example patterns from our standard:
- `transition_deal_state()` single choke point
- `Promise.allSettled` mandatory (Promise.all banned)
- Middleware proxy pattern (JSON 502, never HTML 500)
- `PIPELINE_STAGES` from `execution-contracts.ts` as source of truth
- Server-side counts only
- Surface 9 compliance (console.warn for degradation, console.error for unexpected)
- Port 8090 FORBIDDEN
- Contract surface discipline (sync flows, generated files never edited)

### Section 3b: Anti-Pattern Examples (show wrong vs. right)

For each critical constraint, show what a WRONG implementation looks like alongside the CORRECT pattern. This eliminates ambiguity about what "comply with X" actually means in code.

```
## Anti-Pattern Examples

### WRONG: Promise.all for data fetching
  const [deals, stats, alerts] = await Promise.all([
    fetchDeals(), fetchStats(), fetchAlerts()
  ]);
  // If fetchAlerts() fails, the entire page crashes — deals and stats are lost too

### RIGHT: Promise.allSettled with typed fallbacks
  const [dealsResult, statsResult, alertsResult] = await Promise.allSettled([
    fetchDeals(), fetchStats(), fetchAlerts()
  ]);
  const deals = dealsResult.status === 'fulfilled' ? dealsResult.value : { items: [], total: 0 };
  const stats = statsResult.status === 'fulfilled' ? statsResult.value : { pipeline: [] };
  const alerts = alertsResult.status === 'fulfilled' ? alertsResult.value : [];
  // Page renders deals and stats even if alerts fails

### WRONG: console.error for expected degradation
  } catch (err) {
    console.error("Failed to fetch agent activity", err);  // backend is just down — this is expected
    return NextResponse.json({ data: [] });
  }

### RIGHT: console.warn for degradation, console.error for unexpected
  } catch (err) {
    if (err instanceof TypeError || err.code === 'ECONNREFUSED') {
      console.warn("Agent activity unavailable — backend may be down");  // expected degradation
      return NextResponse.json({ data: [] });
    }
    console.error("Unexpected error fetching agent activity", err);  // genuinely unexpected
    throw err;
  }

### WRONG: Client-side deal counting
  <h2>Total Deals: {deals.length}</h2>  // counts only the fetched page, not total

### RIGHT: Server-side count from API
  <h2>Total Deals: {pipelineSummary.total_count}</h2>  // server-computed total
```

Rules for anti-pattern examples:
- Only include for patterns where violations have actually occurred in past missions
- Keep each example to 3–8 lines — just enough to show the pattern, not a full implementation
- Always show WRONG first, then RIGHT — the contrast teaches
- These are NOT implementation instructions — the executor adapts the pattern to its specific context

### Section 3c: Pre-Mortem (anticipate failure modes)

Before execution begins, answer: "Imagine this mission was executed and failed. What are the 3 most likely reasons?"

```
## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Fix is applied to the specific file the audit flagged, but the same anti-pattern exists in 15 other files | HIGH | Mission passes QA for named files but fails full-stack sweep | Phase 0 discovery must grep ALL repos, not just audit-named files |
| 2 | Backfill changes data shape, breaking a downstream view the mission doesn't mention | MEDIUM | Silent data corruption on pages not in scope | Gate requires re-querying v_pipeline_summary post-backfill |
| 3 | CRLF not stripped from new .sh file, causing cron/make failure hours later | MEDIUM | Delayed failure when user runs the script | WSL safety checklist is a mandatory post-task step |
```

Rules for pre-mortem:
- 3–5 failure scenarios per mission
- Each must be specific to THIS mission, not generic ("tests might fail" is too vague)
- Mitigation column traces to a specific phase task, gate, or guardrail
- Drawn from lessons learned in prior missions — check completed mission history for relevant failures

### Section 4: Phases (The Work Itself)

Each phase is a self-contained unit of work:

```
## Phase {N} — {Name}
**Complexity:** {S / M / L / XL}
**Estimated touch points:** {number of files to modify}

**Purpose:** {One sentence — why this phase exists}

### Blast Radius
- **Services affected:** {which services change or are impacted}
- **Pages affected:** {which dashboard pages render differently after this phase}
- **Downstream consumers:** {what reads from files/data this phase changes}

### Tasks
- P{N}-01: **Bold action verb** — specific instruction with exact file paths
  - Evidence: {exact file path where the change happens}
  - **Checkpoint:** After this task, verify {specific condition} before proceeding to P{N}-02
- P{N}-02: ...

### Decision Tree (if applicable)
- **IF** {condition A} → {action A}
- **ELSE IF** {condition B} → {action B}
- **ELSE** → {default action or escalation}

### Rollback Plan
1. {Exact undo step 1}
2. {Exact undo step 2}
3. Verify: `make validate-local` passes after rollback

### Gate P{N}
- {Concrete verification command or condition}
- {Another verification}
- `make validate-local` still passes
```

**Phase characteristics:**
- **Phase 0** is always **Discovery & Baseline** — verify findings are still current, capture baseline validation
- Phases are numbered sequentially and build on each other
- Each task has a unique ID (`P{phase}-{number}`)
- Each task names the exact file(s) to modify with full paths
- Each task explains what to change AND how to verify it
- Each phase ends with a **Gate** — concrete pass/fail criteria including `make validate-local`
- **Complexity signal** — T-shirt size (S/M/L/XL) so the executor can plan its approach and the prompt author knows when to split a phase
- **Blast radius** — which services/pages/consumers are affected by this phase's changes
- **Mid-task checkpoints** — verification points WITHIN the phase, not just at the end gate
- **Decision trees** — if/then branching for common forks the executor will encounter
- **Rollback plan** — exact undo steps if this specific phase needs to be reverted independently

**Complexity sizing guide:**
| Size | Touch Points | Typical Duration | Example |
|------|-------------|-----------------|---------|
| S | 1–2 files | Quick | Fix a port number in Makefile |
| M | 3–5 files | Moderate | Replace Promise.all pattern across 4 routes |
| L | 6–15 files | Substantial | Full settings page redesign with 6 sections |
| XL | 16+ files or cross-service | Major | Full-stack sweep across 4 repos |

**For sweep missions (V2 pattern):** Instead of phases, use **Sweep Categories** (S1–S7), each with:
- Search command (exact grep/find to run)
- Action per hit (classification rules with decision tree)
- Gate per sweep (zero remaining violations + evidence table)

Then wrap sweeps in lightweight phases: Phase 0 (Discovery), Phase 1 (Execute Sweeps), Phase 2 (Final Verification)

**For large platform missions:** Use **Layers** instead of phases (L1–L6), each with full scope, dependencies, exit gates, risk/rollback, and "Never Again" enforcement. Layers have explicit dependency chains.

### Section 4b: Dependency Graph (visual execution flow)

Show the phase execution order, parallel paths, and blocking relationships as a visual diagram:

```
## Dependency Graph

Phase 0 (Discovery)
    │
    ▼
Phase 1 (Port Drift)
    │
    ▼
Phase 2 (Dashboard Fixes) ──────┐
    │                            │ (parallel)
    ▼                            ▼
Phase 3 (Test Remediation)   Phase 4 (Env Hygiene)
    │                            │
    └────────────┬───────────────┘
                 ▼
         Phase 5 (Documentation)
                 │
                 ▼
         Final Verification
```

Rules:
- Always include for missions with 4+ phases or any parallel execution paths
- Show blocking relationships explicitly (arrows)
- Note which phases can run in parallel
- For simple linear missions (3 phases or fewer), a single sentence suffices: "Phases execute sequentially: 0 → 1 → 2 → Final."

### Section 5: Acceptance Criteria (Numbered AC-1 through AC-N)

```
### AC-1: {Short Title}
{One-sentence test that's either true or false after mission completion}

### AC-2: ...
```

Rules:
- Each AC traces directly to one or more phases
- Every AC is independently verifiable
- AC count typically matches phase count + 1–2 cross-cutting criteria (no regressions, bookkeeping)
- Always include:
  - **AC-N-1: No Regressions** — `make validate-local` passes, TypeScript compiles, no test breakage
  - **AC-N: Bookkeeping** — CHANGES.md updated, changes committed

### Section 6: Guardrails (Numbered list, 6–10 items)

Things the executor must NOT do, or must always do:

1. Scope boundary ("Do not implement X — this mission only does Y")
2. Generated file protection ("Do not modify generated files")
3. Migration safety ("Do not modify migration files")
4. Rename prohibition ("Do not rename environment variables — document instead")
5. Skip decorator preservation ("Do not remove @pytest.mark.skip")
6. Surface 9 compliance
7. WSL safety (CRLF + ownership)
8. Pre-task protocol adherence
9. Classification guidance ("err toward leaving as error if uncertain")
10. Repo boundary respect

### Section 7: Executor Self-Check Prompts (challenge-and-response)

Questions the executor asks itself at key checkpoints — the equivalent of a pilot's challenge-and-response checklist. These catch the exact class of mistakes that have occurred in past missions.

```
## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I check ALL 4 repos or just the monorepo?"
- [ ] "Did I verify findings are still current, or did I assume the audit is still accurate?"
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"

### After every code change:
- [ ] "Did I run `make sync-all-types` if I changed an API boundary?"
- [ ] "Is this a degradation path or an unexpected failure?" (for console.warn/error decisions)
- [ ] "Am I fixing the specific instance, or did I sweep for the same pattern elsewhere?"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks, or am I assuming they pass?"
- [ ] "Did I create new .sh files? → CRLF stripped?"
- [ ] "Did I create files under /home/zaks/? → Ownership fixed?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now, not 3 phases ago?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce a completion summary with evidence paths for every AC?"
```

Rules:
- 3–5 questions per checkpoint
- Questions must be specific to common mistakes, not generic ("did I do a good job?")
- Phrased as yes/no or binary — no open-ended questions
- Drawn from actual failures in past missions (V1 fullstack gap, CRLF breakage, forgotten sync)

### Section 8: File Paths Reference (Three tables)

```
### Files to Modify
| File | Phase | Change |
|------|-------|--------|

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
```

This section gives the executor a complete map of its workspace.

### Section 9: Stop Condition (1–2 paragraphs)

Explicitly states when the mission is DONE:
- All AC met
- `make validate-local` passes
- All changes committed
- Completion summary produced with evidence paths
- What NOT to proceed to (explicit scope fence)

### Footer

```
---
*End of Mission Prompt — {MISSION-ID}*
```

---

## TYPE 2: QA VERIFICATION & REMEDIATION MISSION PROMPT

### Document Header (Same 7 fields as execution missions)

### Section 1: Mission Objective

- States this is an **independent verification** of the source mission(s)
- Names the source missions with paths, line counts, AC counts, phase counts
- Names all evidence artifacts the source mission should have produced
- States the QA will **verify, cross-check, stress-test, and remediate**

### Section 2: Pre-Flight (PF-1 through PF-N)

Baseline checks before any verification:

```
### PF-1: Validation Baseline
{bash command with tee to evidence file}
**PASS if:** exit 0. If not, stop — codebase is broken before QA starts.

### PF-2: {Execution Status Check}
### PF-3: TypeScript Compilation
### PF-4: {Evidence Directory Existence}
### PF-5: {Services Running}
```

Each PF has: command block, PASS condition, and what to do if it fails.

Pre-flight adapts to conditions — if services are down, live verification gates become code-only. If the source mission wasn't executed, gates become EXECUTE+VERIFY instead of VERIFY-ONLY.

### Section 3: Verification Families (VF-01 through VF-N)

Each VF maps to one acceptance criterion or phase from the source mission:

```
## Verification Family 01 — {Name} ({Source mission phase/AC reference})

### VF-01.1: {Specific check name}
{bash command with tee to evidence file}
**PASS if:** {concrete criterion}

### VF-01.2: ...

**Gate VF-01:** All N checks pass. {Summary statement}.
```

**VF characteristics:**
- Named with `VF-{family}.{check}` notation
- Every check has an **exact bash command** that captures evidence to a file via `tee`
- Every check has a **concrete PASS/FAIL criterion** — not subjective
- For classification checks (e.g., console.error audit), the action per hit is spelled out with classification rules (CORRECT, VIOLATION, etc.)
- Each VF family ends with a gate that summarizes: "All N checks pass. {What this proves}."
- VF families **cover the full surface** — specific fixes from V1 AND full-stack sweeps from V2

### Section 4: Cross-Consistency Checks (XC-1 through XC-N)

Verify that different artifacts agree with each other:

```
### XC-1: {Documentation vs Codebase Agreement}
### XC-2: {Cross-Reference File vs Example File Agreement}
### XC-3: {Error Shapes Doc vs Normalizer Agreement}
```

Cross-checks catch problems that individual VFs miss — they verify consistency BETWEEN deliverables.

### Section 5: Stress Tests (ST-1 through ST-N)

Edge cases and deeper probing beyond what the source mission specified:

```
### ST-1: {Resilience Config Consistency}
### ST-2: {Timeout Relationship Check}
### ST-3: {Orphaned Config Variables}
```

Stress tests go deeper than VFs — they test assumptions, relationships, and edge cases.

### Section 6: Remediation Protocol

Exact procedure for handling FAIL results:

1. Read the evidence
2. Classify: MISSING_FIX / REGRESSION / SCOPE_GAP / FALSE_POSITIVE / NOT_IMPLEMENTED / PARTIAL / VIOLATION
3. Apply fix following original guardrails
4. Re-run specific gate
5. Re-run `make validate-local`
6. Record in completion report

### Section 7: Enhancement Opportunities (ENH-1 through ENH-N)

Future improvements discovered during QA — **not failures, not blockers**:

```
### ENH-1: {Name}
{Description of what could be added to prevent this class of issue}
```

Typically 8–12 enhancements per QA mission. These become input for future mission planning.

### Section 8: Scorecard Template

Pre-formatted template the executor fills in:

```
QA-{ID} — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  ...

Verification Gates:
  VF-01 ({Name}):  __ / N gates PASS
  ...

Cross-Consistency:
  XC-1 through XC-N: __ / N gates PASS

Stress Tests:
  ST-1 through ST-N: __ / N tests PASS

Total: __ / {total} gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: N (ENH-1 through ENH-N)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

### Section 9: Guardrails (Same pattern as execution missions, plus QA-specific)

QA-specific additions:
- "Do not build new features — this is a QA mission"
- "Remediate, don't redesign"
- "Evidence-based only — every PASS needs tee'd output"
- "P3 items are not failures — mark as INFO/DEFERRED"
- "Services-down accommodation" — live gates become SKIP, not FAIL
- "Preserve prior fixes — remediation must not revert earlier work"

### Section 10: Stop Condition

```
Stop when all {N} verification gates pass (or are justified as
SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and
re-verified, `make validate-local` passes, and the scorecard is complete.
```

---

## WORKFLOW: EXECUTION → QA AND THE INTEGRATED VERIFICATION MODEL

### Current Workflow

The established workflow follows an **execution-first, QA-second** pattern:

```
Audit → Surgical Fix (V1) → Full-Stack Sweep (V2) → QA Verification → Next Build
```

Each link names its predecessor and successor.

### Perspective: Why Separate QA Remains Valuable

After evaluating whether to fold QA into execution, the recommendation is to **keep QA as a separate pass** while **strengthening the verification-during-execution model**. Here's why:

**Arguments for separate QA (why we keep it):**
1. **Independent verification is irreplaceable.** The builder that wrote the code has cognitive bias toward its own work. A fresh session with zero memory of HOW the fix was applied will catch things the builder normalized away.
2. **Evidence integrity.** Execution sessions can exceed context windows, lose track of earlier phases, or silently skip gates under pressure to finish. A QA mission re-runs every gate from scratch with fresh evidence.
3. **Cross-consistency is a QA-native concept.** XC checks (do artifacts agree with each other?) and ST stress tests (do assumptions hold at the edges?) are fundamentally different from "did I implement the thing correctly."
4. **TriPass multi-agent QA** adds perspectives from Gemini and Codex that are architecturally impossible during execution.

**Arguments for tighter integration (what we improve):**
1. **The builder should self-verify during execution, not defer all verification to QA.** Phase gates already enforce this, but we strengthen them.
2. **QA should not be discovering basic failures.** If QA routinely finds that `make validate-local` fails, that's a process failure in execution, not a QA success.
3. **Enhancement opportunities from QA should feed back into the next execution mission automatically.**

### The Integrated Model (V2 Workflow)

```
                    ┌─────────────────────────────────────────────┐
                    │          EXECUTION MISSION                   │
                    │                                              │
                    │  Phase 0: Discovery + Baseline Validation    │
                    │      ↓                                       │
                    │  Phase N: Execute + Self-Verify (gate)       │
                    │      ↓                                       │
                    │  Phase N+1: Execute + Self-Verify (gate)     │
                    │      ↓                                       │
                    │  Final: Full Validation + Self-Audit          │
                    │      ↓                                       │
                    │  Completion Report with evidence paths        │
                    └──────────────────┬──────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────────┐
                    │          QA VERIFICATION MISSION             │
                    │                                              │
                    │  Pre-Flight: Baseline independent of builder │
                    │  VF: Re-verify every AC with fresh evidence  │
                    │  XC: Cross-consistency between deliverables  │
                    │  ST: Stress-test assumptions and edge cases  │
                    │  ENH: Feed improvements → next execution     │
                    └──────────────────┬──────────────────────────┘
                                       │
                           ENH feedback │
                                       ▼
                              Next Execution Mission
```

**Key changes from V1 workflow:**
- Execution missions now include a **Final Self-Audit phase** before completion — the builder verifies its own AC independently before declaring done
- QA missions now include an **ENH feedback loop** — enhancement opportunities are explicitly evaluated when generating the next execution mission
- The workflow is a cycle, not a line: ENH items from QA seed improvements in the next execution mission

### When to Use TriPass QA vs. Standard QA

| Criteria | Standard QA (single Claude session) | TriPass QA (3-agent pipeline) |
|----------|-------------------------------------|-------------------------------|
| Mission scope | Single-domain, < 50 gates | Cross-service, 50+ gates |
| Risk level | Medium — regressions would be caught in next cycle | High — regressions would cause data integrity issues |
| Time budget | Standard | Extended (TriPass takes 3x longer) |
| When to use | Default for most missions | Platform stabilization, data integrity, infrastructure changes |

---

## CROSS-CUTTING STANDARDS (Both Types)

### 1. File Path Discipline
- All file paths are **absolute** (`/home/zaks/zakops-agent-api/...`, not relative)
- Every task/check references the exact file(s) involved

### 2. Evidence Discipline
- Execution missions: completion report per phase in evidence directory
- QA missions: every gate outputs to a `tee`'d evidence file (`/tmp/qa-{id}-{gate}.txt`)
- "I checked and it's fine" is never evidence

### 3. Validation Cadence
- `make validate-local` runs after every phase/sweep/family
- TypeScript compilation (`npx tsc --noEmit`) is an explicit gate
- ESLint is checked at final verification

### 4. WSL Safety (in every mission)
- `sed -i 's/\r$//'` on any new .sh files
- `sudo chown zaks:zaks` on files under `/home/zaks/`

### 5. Architectural Pattern Enforcement
These patterns appear in EVERY mission's constraints section:
- `transition_deal_state()` choke point
- `Promise.allSettled` (Promise.all banned)
- Surface 9 (console.warn/error classification)
- Port 8090 forbidden
- Generated files never edited
- Contract surface discipline
- Middleware proxy pattern (JSON 502)
- PIPELINE_STAGES source of truth
- Server-side counts only

### 6. Scope Fencing
Every mission explicitly states:
- What is IN scope
- What is OUT of scope
- What the successor mission is (blocking relationship)

### 7. Naming Conventions
- Execution: `MISSION-{DOMAIN}-{NUMBER}.md`
- QA: `QA-{ABBREVIATION}-VERIFY-{NUMBER}.md`
- Evidence: `/home/zaks/bookkeeping/qa-verifications/{MISSION-ID}/`
- Changes: `/home/zaks/bookkeeping/CHANGES.md`

### 8. Gate Counting
We track total gate counts and report them in memory:
- Execution: AC count
- QA: VF gates + XC gates + ST gates = total

### 9. Rollback Philosophy
- Every phase has its own rollback plan — not just a mission-wide "git revert"
- Rolling back layer N requires rolling back all layers above N first
- Rollback plans include exact commands, not just "undo the changes"
- Data changes (backfills, migrations) have separate reversibility documentation from code changes

### 10. Decision Tree Philosophy
- Linear instructions are the default for straightforward tasks
- Decision trees are REQUIRED when the executor will encounter a fork with 2+ valid paths
- Common fork points: "file exists vs. doesn't", "service is running vs. down", "grep returns 0 hits vs. many hits", "backend endpoint exists vs. needs creating"
- Decision trees use simple IF/ELSE IF/ELSE format, not flowcharts

### 11. Pre-Mortem Philosophy
- Every mission with 3+ phases includes a pre-mortem section
- Failure scenarios are specific to THIS mission, not generic
- Each scenario traces to a mitigation in the phases, gates, or guardrails
- Pre-mortems are informed by failures from completed missions (check MEMORY.md completed missions list)

### 12. Complexity and Blast Radius Philosophy
- Every phase declares its complexity (S/M/L/XL) and blast radius
- Phases larger than L should be split into sub-phases unless tightly coupled
- Blast radius includes: services affected, pages affected, downstream consumers
- If a phase's blast radius spans all 4 repos, it is automatically classified XL

### 13. Self-Check Philosophy
- Self-check prompts appear at key transitions: after discovery, after every code change, before marking complete
- Questions target mistakes that have ACTUALLY HAPPENED in past missions
- The list evolves — new questions are added after each post-mortem identifies a new failure class
- Self-checks are binary (yes/no), never open-ended

### 14. Reference, Don't Repeat
- The builder loads CLAUDE.md, MEMORY.md, hooks, rules, and deny rules before reading the mission prompt
- Mission prompts reference standing rules by name ("per Surface 9", "per contract surface discipline") — never copy them
- Only elaborate on infrastructure when the mission DEVIATES from or EXTENDS a standing rule
- When a mission modifies contract surfaces, name which `make sync-*` command is required (this IS mission-specific)
- Never instruct the builder to do something a hook will block — route through the correct pipeline instead

---

## IMPROVEMENT AREAS (MANDATORY REVIEW BY BUILDERS)

**Purpose:** This section captures ideas, techniques, and enhancements that are under evaluation or awaiting the right conditions to adopt. When a builder receives this standard and is asked to generate a mission prompt, they MUST:

1. **Read every item** in this section before generating the prompt
2. **Evaluate applicability** — does this specific mission meet the prerequisites for adopting this improvement?
3. **Incorporate mature items** — if the environment has reached the necessary maturity and the improvement applies, weave it into the mission prompt proactively
4. **Note adoption** — when an improvement is incorporated, add a comment in the generated mission: `<!-- Adopted from Improvement Area IA-{N} -->`
5. **Report new ideas** — if the builder discovers a new improvement opportunity during prompt generation, append it here as a new IA item

### IA-1: Context Window Management Strategy
**Status:** Ready to adopt
**Prerequisites:** None — applies to all missions
**Description:** Large missions (500+ lines) risk exceeding the builder's context window. Missions should include a "Context Checkpoint" instruction at the midpoint: "If your context is becoming constrained, summarize progress so far, commit intermediate work, and continue in a fresh continuation."
**When to incorporate:** Any mission with 5+ phases or estimated 500+ lines

### IA-2: Crash Recovery Protocol
**Status:** Ready to adopt
**Prerequisites:** None — applies to all missions
**Description:** If the builder session crashes mid-mission, the next session has no memory of progress. Missions should include a "Recovery Section" near the top: "If resuming after a crash, run these 3 commands to determine current state: (1) git log --oneline -5, (2) make validate-local, (3) check for partial evidence files."
**When to incorporate:** Any mission with 3+ phases

### IA-3: Cost/Token Awareness Signals
**Status:** Under evaluation
**Prerequisites:** Tooling to measure token consumption per phase
**Description:** Mark phases with estimated token cost (LOW/MEDIUM/HIGH) based on the number of file reads, grep operations, and code edits expected. This helps prompt authors identify phases that should be split.
**When to incorporate:** When we have baseline measurements from 3+ missions. Until then, complexity sizing (S/M/L/XL) serves as a proxy.

### IA-4: Template Automation
**Status:** Under evaluation
**Prerequisites:** A template engine or slash command that scaffolds mission prompts
**Description:** Create a `/generate-mission` command that scaffolds a mission prompt skeleton from this standard, pre-filling the header, constraint section, guardrails, and self-check prompts. The builder fills in mission-specific content.
**When to incorporate:** When the standard has been stable for 3+ missions without structural changes. Current pace of evolution suggests this is premature.

### IA-5: Specification-First QA Gates
**Status:** Under evaluation
**Prerequisites:** Mature understanding of which gate types catch the most issues
**Description:** Write QA verification gates BEFORE the execution mission, as a "specification" of what success looks like. The execution mission then targets those gates directly. This is the TDD equivalent for mission prompts. Risk: over-specification may constrain the builder's ability to find the best solution.
**When to incorporate:** Pilot on the next infrastructure remediation mission. Keep for feature builds only if the pilot succeeds.

### IA-6: Execution Session Telemetry
**Status:** Under evaluation
**Prerequisites:** A mechanism to capture builder session metrics (phases completed, gates passed, remediations, context usage)
**Description:** The completion report should include a "Session Metrics" section: total phases, gates passed on first attempt vs. after retry, remediations applied, files touched, estimated token consumption. This data informs future prompt optimization.
**When to incorporate:** When session-log.md and memory-sync.sh are proven stable (they are now live — next mission can pilot this).

### IA-7: Multi-Session Mission Continuity
**Status:** Ready to adopt
**Prerequisites:** None — the JSONL session log already provides the mechanism
**Description:** For XL missions that will span multiple sessions, include a "Continuation Protocol": at the end of each session, the builder writes a structured checkpoint to `/home/zaks/bookkeeping/mission-checkpoints/{MISSION-ID}.md` with: phases completed, phases remaining, current validation state, any open decision trees. The next session reads this checkpoint first.
**When to incorporate:** Any mission estimated at XL complexity or 6+ phases

### IA-8: Graduated Verification Depth
**Status:** Under evaluation
**Prerequisites:** Enough QA history to calibrate risk tiers
**Description:** Not all missions need the same QA depth. Propose three tiers: (1) Self-Audit Only — for S/M missions with low blast radius, the execution mission's final self-audit is sufficient. (2) Standard QA — single Claude session, full VF/XC/ST. (3) TriPass QA — for high-risk, cross-service changes. The mission header declares its required QA tier.
**When to incorporate:** After completing 2 more self-audit-only missions successfully to validate that Tier 1 is reliable.

### IA-9: Prompt Diff Protocol
**Status:** Ready to adopt
**Prerequisites:** None
**Description:** When this standard is updated, the change log should include a "prompt diff" — what specifically changes in generated prompts. Example: "v1.5 → v2.0: All missions now include a Preamble reference. QA missions now require ENH feedback loop section." This helps builders who learned the old standard quickly understand what's different.
**When to incorporate:** Starting with this version (v2.0). Applied retroactively in the version history below.

---

## STANDARD EVOLUTION PROTOCOL

This standard is a **living document**. It evolves alongside the ZakOps platform, Claude Code infrastructure, and lessons learned from each mission cycle.

### Version Numbering
- **Major** (X.0): Structural changes — new sections added, sections removed, workflow changes
- **Minor** (X.Y): Content updates — new improvement areas, updated constraints, new anti-patterns
- Format: `{major}.{minor}` — no patch numbers (this is a prompt standard, not software)

### What Triggers an Update

| Trigger | Example | Update Type |
|---------|---------|-------------|
| New hook, rule, or agent added to Claude Code config | New `pre-commit.sh` hook | Minor — update Preamble |
| Infrastructure change that affects mission execution | New contract surface (Surface 10) | Minor — update Preamble + constraints |
| Structural lesson from a failed or suboptimal mission | QA found that crash recovery was needed | Minor — new Improvement Area |
| Improvement Area promoted to standard practice | IA-1 adopted in 3 consecutive missions | Major — move from IA section to main body |
| Workflow change | Self-audit phase added to execution missions | Major — update workflow section |
| 3+ missions generated without consulting the standard | Drift detected | Review — no change if standard is current |

### Update Procedure

1. **Identify the trigger** — what changed and why
2. **Draft the change** — modify the relevant section
3. **Bump the version** — major or minor per the rules above
4. **Update the Version History** — with date, version, and prompt diff
5. **Run ownership fix** — `sudo chown zaks:zaks /home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`

### Ownership

This standard is maintained by whoever generates mission prompts. When Claude Code (the builder) is asked to generate a mission prompt, it MUST:
1. Read this standard first
2. Follow it completely
3. Review the Improvement Areas section
4. Note any deviations in the generated prompt with justification
5. Propose updates to this standard if it discovers gaps during generation

---

## QUALITY CHECKLIST FOR PROMPT AUTHORS

Before finalizing any mission prompt, the author verifies:

- [ ] **Header complete** — All 7 fields filled (ID, subtitle, date, classification, prerequisite, successor)
- [ ] **Glossary present** — If 3+ project-specific terms are used, glossary section exists
- [ ] **Anti-patterns shown** — For each critical constraint, wrong vs. right examples included
- [ ] **Pre-mortem written** — 3–5 specific failure scenarios with mitigations traced to phases/gates
- [ ] **Every phase has:** complexity, blast radius, tasks with checkpoints, decision trees (if forks exist), rollback plan, gate
- [ ] **Dependency graph present** — For 4+ phases or any parallel paths
- [ ] **Self-check prompts present** — At discovery, mid-mission, and pre-completion checkpoints
- [ ] **Acceptance criteria** — Each AC traces to a phase, includes no-regression and bookkeeping ACs
- [ ] **Guardrails complete** — Scope fence, generated file protection, WSL safety, Surface 9 all present
- [ ] **File paths reference** — Three tables (modify, create, read-only) with absolute paths
- [ ] **Stop condition explicit** — States what DONE means and what NOT to proceed to
- [ ] **All file paths absolute** — Zero relative paths anywhere in the document
- [ ] **Gate counting verified** — Total gate count matches actual gates in document
- [ ] **Improvement Areas reviewed** — Builder has checked each IA and incorporated applicable ones
- [ ] **Builder infrastructure acknowledged** — Preamble constraints are reflected in the mission (no instructions that conflict with hooks/deny rules)
- [ ] **Crash recovery included** — For missions with 3+ phases (per IA-2)
- [ ] **Context checkpoint included** — For missions with 5+ phases or 500+ lines (per IA-1)

---

## VERSION HISTORY

| Version | Date | Type | Change Summary |
|---------|------|------|----------------|
| 1.0 | 2026-02-10 | Major | Initial standard extracted from 7 mission documents (DEAL-INTEGRITY-UNIFIED, SURFACE-REMEDIATION-001/002, DASHBOARD-R4-CONTINUE-001, QA-SR-VERIFY-001, QA-R4C-VERIFY-001, QA-V6GR-VERIFY-001) |
| 1.1 | 2026-02-10 | Minor | Added 10 industry best practices: rollback per phase, decision trees, complexity signals, anti-pattern examples, blast radius maps, pre-mortem, mid-task checkpoints, glossary, dependency graph, executor self-checks |
| 2.0 | 2026-02-10 | Major | **Prompt diff from 1.1:** (1) Added Preamble section — high-level reference to builder infrastructure (CLAUDE.md, MEMORY.md, hooks, rules, agents) with "reference, don't repeat" principle. (2) Replaced simple "Mission Chain" cross-cutting standard with full "Workflow" section including integrated verification model (execution self-audit + QA + ENH feedback loop), TriPass decision matrix, and V2 workflow diagram. (3) Added "Improvement Areas" section (9 items: IA-1 through IA-9) with mandatory builder review protocol. (4) Added "Standard Evolution Protocol" with version numbering, update triggers, update procedure, and ownership rules. (5) Added "Reference, Don't Repeat" as cross-cutting standard #14. (6) Expanded Quality Checklist with 4 new items (IA review, infrastructure acknowledgment, crash recovery, context checkpoint). (7) Added Version History with prompt diffs. |

---

*End of Mission Prompt Generation Standard — Version 2.0*

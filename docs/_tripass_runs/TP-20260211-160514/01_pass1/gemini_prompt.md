# TriPass — Pass 1: Independent Investigation

## Agent Identity
**Agent**: GEMINI
**Run ID**: TP-20260211-160514
**Pipeline Mode**: design
**Timestamp**: 2026-02-11T16:05:18Z

---

## Mission

# TriPass Strategic Mission: Dashboard UI Masterplan

## Mission Type: Strategy / Design
## Date: 2026-02-11
## Requested By: ZakOps Principal

---

## 1. Mission Objective

Produce a **single master strategy** for bringing the ZakOps dashboard to world-class quality. The platform has been built incrementally and now contains visual inconsistencies, unwired interactions, misaligned components, and unpolished flows across multiple pages. We are NOT adding features — we are fixing and perfecting everything that already exists.

---

## 2. Context

### Platform State
- **Stack:** Next.js 15 + shadcn/ui + Tailwind CSS, backend FastAPI (port 8091), Agent API (port 8095)
- **Dashboard:** Located at `/home/zaks/zakops-agent-api/apps/dashboard`, runs on port 3003
- **Pages/Tabs:** Dashboard (pipeline overview), Deal Detail/Workspace, Quarantine, Chat, Agent Activity, Onboarding, Setup, Settings, and potentially others
- **Known issues:** Visual inconsistencies across pages, varying design patterns, components built at different times with different standards, some buttons/interactions not fully wired, responsive breakpoints untested
- **Infrastructure:** 14 contract surfaces, 7 hooks, 8 skills, Playwright MCP (22 browser tools for visual verification), TriPass pipeline, mission prompt standard v2.1

### Architectural Constraints (MANDATORY — do not violate)
- `Promise.allSettled` with typed empty fallbacks for multi-fetch (Promise.all is banned)
- `PIPELINE_STAGES` from `execution-contracts.ts` is the single source of truth for stages
- Server-side deal counts only — no client-side `.length` counting
- All `/api/*` through Next.js middleware proxy, JSON 502 on backend failure
- Import from bridge files (`@/types/api`, `@/types/agent-api`), never from generated files
- `caret-color: transparent` globally with input/textarea override to `auto`
- Design system rule at `.claude/rules/design-system.md` auto-loads for dashboard files

### New Capability: Playwright MCP
We now have 22 Playwright browser tools available as MCP tools within Claude Code:
- `browser_navigate`, `browser_take_screenshot`, `browser_snapshot`
- `browser_resize`, `browser_console_messages`, `browser_click`
- `browser_evaluate`, `browser_network_requests`, `browser_run_code`
- This means Claude Code can now SEE the UI, take screenshots, check console errors, and verify rendering at any breakpoint
- This is a game-changer for quality assurance and should be central to any strategy

---

## 3. The Strategic Question

We need to decide the optimal approach to systematically fix and polish the entire dashboard. Three candidate strategies have been identified:

### Strategy A: Tab-by-Tab (Bottom-Up)
- Pick one page at a time (Dashboard → Detail → Quarantine → Chat → etc.)
- For each page: audit every component, every interaction, every visual element
- Fix everything until that page is perfect, then move to the next
- **Pro:** Focused, delivers complete pages incrementally
- **Risk:** May fix shared components differently per page, causing rework. Cross-cutting issues discovered late.

### Strategy B: Top-Down Blueprint
- First, design a comprehensive UI blueprint: visual system, layout structure, interaction patterns, state management, component behavior rules
- Then restructure everything to match the blueprint
- **Pro:** Ensures consistency from the start
- **Risk:** Abstract, slow, may not account for real-world constraints discovered during implementation. Over-engineering risk.

### Strategy C: Hybrid (Proposed by Claude)
- **Phase 0:** Reconnaissance sprint — Playwright screenshots of every page at 3 breakpoints, full catalog of all findings, categorized as cross-cutting vs page-specific. No code changes.
- **Phase 1:** Cross-cutting foundation — fix shared components, navigation, layout, typography, color, loading/error/empty states first. This prevents inconsistency.
- **Phase 2:** Page-by-page polish — now safe to go tab-by-tab because shared foundation is locked. Each page gets its own mission.
- **Phase 3:** Integration sweep — cross-page flows, full responsive regression, contract compliance across all 14 surfaces.
- **Pro:** Evidence-based, prevents fixing things twice, shared foundation cascades to all pages
- **Risk:** Phase 0 adds upfront time. Total estimated missions: 10-12.

---

## 4. What Each Agent Must Deliver

Each agent must produce a **strategy recommendation** covering:

1. **Chosen approach** (A, B, C, or your own D/E/F) with clear justification
2. **Phase breakdown** — what phases, what order, what each phase delivers
3. **Mission structure** — how many missions, what scope each, what type (recon/build/QA)
4. **Playwright integration** — how and when to use the 22 browser tools for maximum impact
5. **Risk mitigation** — what could go wrong and how each phase prevents it
6. **Regression prevention** — how to ensure fixing one thing doesn't break another
7. **Quality gates** — what criteria must each phase meet before proceeding to the next
8. **Continuous improvement** — how findings from each phase feed into the next
9. **Estimated shape** — rough number of missions, order, dependencies
10. **One thing the other strategies get wrong** — what critical flaw exists in the approaches you didn't choose

---

## 5. Evaluation Criteria

The master strategy will be judged on:
- **Minimizes wasted effort** — no fixing things twice, no over-engineering
- **Maximizes confidence** — evidence-based decisions, not assumptions
- **Ensures long-term stability** — regression prevention built into process
- **Aligns with existing infrastructure** — leverages 14 contracts, mission prompt standard, TriPass, Playwright MCP
- **Actionable** — the strategy should be immediately executable as mission prompts
- **Measurable** — clear definition of "done" for the entire initiative

---

## 6. Codebase Entry Points for Investigation

Agents should examine these to ground their strategy in reality:

- **Dashboard pages:** `apps/dashboard/src/app/` — all route directories
- **Components:** `apps/dashboard/src/components/` — shared and page-specific
- **Styles:** `apps/dashboard/src/styles/` — global CSS, theme tokens
- **Types:** `apps/dashboard/types/` — bridge types, execution contracts
- **E2E tests:** `apps/dashboard/tests/e2e/` — 9 existing test files
- **Design system rule:** `.claude/rules/design-system.md` — current UI standards
- **Frontend skill:** `/home/zaks/.claude/skills/frontend-design/SKILL.md`
- **Backend API spec:** `packages/contracts/openapi/zakops-api.json`

---

## 7. Constraints

- Do NOT produce code. This is a strategy-only mission.
- Do NOT propose adding new features. Only fix and polish what exists.
- Do NOT violate the architectural patterns listed in Section 2.
- The strategy must be executable using our existing mission prompt standard (v2.1).
- Each recommended mission must be scoped to fit a single Claude Code session.
- Playwright MCP integration must be a first-class citizen in the strategy, not an afterthought.

---

## 8. Deliverable Format

Your final output must be a structured strategy document with:
- Executive summary (3-5 sentences)
- Chosen approach with justification
- Phase-by-phase breakdown with clear deliverables
- Mission inventory (numbered list with scope and type)
- Quality gates per phase
- Risk register with mitigations
- How Playwright MCP is used in each phase
- Definition of "done" for the entire initiative

## Scope

As defined in the mission document

## Repository Roots

/home/zaks/zakops-agent-api

## Known Issues or Constraints

V5PP guardrails apply. No production code modifications.

---

## Instructions

You are one of three independent investigators analyzing this mission. Your report will be cross-reviewed by two other agents in Pass 2. No other agent can see your work during this pass.

### Investigation Protocol

1. **Read first, opine second.** Read every relevant file before forming conclusions. Cite file paths and line numbers for every claim.
2. **Stay in scope.** If you discover issues outside the declared mission scope, place them in the ADJACENT OBSERVATIONS section — never mix them with primary findings.
3. **Structure every finding** with these 5 required fields:
   - **(1) Confirmed Root Cause** — What is the actual problem, with file:line evidence?
   - **(2) Permanent Fix Approach** — What specific change resolves it?
   - **(3) Industry Standard / Best Practice** — What standard or pattern does this align with?
   - **(4) Why It Fits This System** — Why is this the right fix for THIS codebase specifically?
   - **(5) Never-Again Enforcement** — What gate, lint rule, hook, or test prevents recurrence?
4. **Be concrete.** "The middleware should validate input" is not a finding. "middleware.ts:47 accepts unsanitized query params — add zod schema validation" is a finding.

### Output Format

Write your report to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/01_pass1/gemini_report.md`

Begin your report with exactly this header:

```
# Pass 1 Report — GEMINI
## Run: TP-20260211-160514 | Mode: design
## Generated: 2026-02-11T16:05:18Z
```

Then organize findings as:

```
## PRIMARY FINDINGS

### Finding 1: [Title]
**Root Cause:** ...
**Fix Approach:** ...
**Industry Standard:** ...
**System Fit:** ...
**Enforcement:** ...

### Finding 2: ...
(repeat for each finding)

## ADJACENT OBSERVATIONS
(out-of-scope items go here, clearly labeled)

## SUMMARY
- Total primary findings: N
- Total adjacent observations: N
- Confidence level: HIGH / MEDIUM / LOW
- Key recommendation: (one sentence)
```

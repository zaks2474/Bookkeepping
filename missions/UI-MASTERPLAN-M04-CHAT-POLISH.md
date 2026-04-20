# MISSION: UI-MASTERPLAN-M04
## Chat Page Polish - Responsive Interaction Closure and Streaming Stability
## Date: 2026-02-11
## Classification: Page-Level UX Hardening (Tier 1)
## Prerequisite: UI-MASTERPLAN-M01, UI-MASTERPLAN-M02, UI-MASTERPLAN-M03 complete
## Successor: UI-MASTERPLAN-M05 and UI-MASTERPLAN-M06 (parallel Tier 1), then M-11 integration sweep

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify artifact continuity in `/home/zaks/bookkeeping/missions/m04-artifacts/` (before/after screenshots, interaction checklist, validation report)

---

## Mission Objective
Close Chat page finding F-22 and complete full interaction closure for `/chat` so all core chat controls remain reachable and truthful across 375px, 768px, and 1280px while streaming behavior remains stable.

This is a chat page polish mission, not a chat architecture rewrite. Improvements should prioritize interaction availability, responsive composition, and reliable degraded behavior semantics.

Out of scope: broad component decomposition for maintainability alone. Extraction is allowed only when directly required to fix responsive/interaction defects.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

M-00 chat-specific evidence:
- F-9 (architectural context): Chat page is the highest-risk surface — 1,772 lines with 9+ inlined concerns (SSE streaming, provider selection, session management, evidence citations, proposal generation, history rail, deal context, timing analytics, error handling). This is why chat receives dedicated Tier 1 treatment.
- F-22 (Sev-2): toolbar overflow at 768px and 375px; essential controls (History, New Chat, Evidence, Debug) clipped or inaccessible on smaller breakpoints.
- Chat interaction inventory includes 10 controls per M-00 inventory (6 real, 3 client-only, 1 static indicator): settings gear, global/deal scope dropdown, deal filter, history, new chat, evidence, debug, ask textbox, send button, provider indicator.

FINAL_MASTER Phase 2 requirements for every page mission apply here:
- Interaction closure checklist (real/degraded/hidden for every visible control)
- Before/after screenshot triad at 375/768/1280
- Console error check (zero untriaged errors)
- Contract compliance preservation (no new client-count anti-patterns, no 500 regression)
- At least 2 new E2E tests for covered page scope

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Interaction closure | Per-control verification that each visible control is either real, explicitly degraded, or hidden intentionally |
| Streaming stability | Chat response flow remains usable during SSE token/progress updates without UI lockups or control loss |
| Responsive triad | 375px (mobile), 768px (tablet), 1280px (desktop) verification set |
| Degraded truthfulness | If backend/provider is unavailable, UI states and responses are explicit and non-misleading |

---

## Architectural Constraints
- **Page scope lock:** Primary target is `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx` and directly related chat UI components.
- **Interaction closure required:** Every visible chat control must be classified `real endpoint`, `explicitly degraded`, or `hidden/removed` with rationale.
- **Responsive first:** Fixes must make controls reachable at 375/768/1280 without horizontal clipping.
- **Streaming integrity:** Do not break SSE handling, token batching, progress display, or session restore.
- **No silent mock success:** Do not present successful execution states for unavailable operations without explicit degraded messaging.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Hide controls at small breakpoints without alternate access
```text
Toolbar overflows at 375px, and History/Evidence/Debug disappear with no fallback menu.
```

### RIGHT: Preserve control accessibility with responsive composition
```text
Controls remain reachable via responsive wrapping, grouped menu, or intentional secondary access pattern.
```

### WRONG: "Success" UI when backend path is unavailable
```text
Proposal/stream interactions appear complete even when route returns degraded/unavailable response.
```

### RIGHT: Explicit degraded semantics
```text
Unavailable backend paths surface clear non-destructive messaging and preserve user context.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Responsive fixes regress desktop chat usability | Medium | High | Require before/after triad and desktop interaction replay in every phase gate |
| 2 | Streaming path breaks while restructuring toolbar/layout | Medium | High | Dedicated streaming replay checks with console capture before and after edits |
| 3 | Controls become visible but non-functional on mobile | High | High | Interaction closure checklist with per-control state and replay proof |
| 4 | Mission drifts into large component refactor | Medium | Medium | Guardrails prohibit decomposition unless directly tied to defect closure |
| 5 | New E2E tests are brittle and non-deterministic | Medium | Medium | Prefer deterministic selectors and awaitable state assertions; no fixed sleep-only gating |

---

## Phase 0 - Baseline Capture and Boundary Snapshot
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Isolate pre-M04 state and capture objective baseline evidence for chat defects.

### Blast Radius
- **Services affected:** Dashboard chat page only (baseline read)
- **Pages affected:** `/chat`
- **Downstream consumers:** M-11 integration and regression suite

### Tasks
- P0-00: Capture M-03 boundary snapshot before chat edits.
  - Preferred: commit/tag boundary for pre-M04 state.
  - Fallback: record changed-file manifest and `git diff --stat` in `/home/zaks/bookkeeping/missions/m04-artifacts/reports/m03-boundary-snapshot.md`.
  - Checkpoint: M-04 can roll back independently from M-03.
- P0-01: Capture before screenshots of `/chat` at 375/768/1280 and a console baseline.
  - Evidence: `/home/zaks/bookkeeping/missions/m04-artifacts/before/`
  - Checkpoint: before-state artifacts exist for all three breakpoints.
- P0-02: Build initial interaction closure matrix from current chat controls.
  - Evidence: `/home/zaks/bookkeeping/missions/m04-artifacts/reports/interaction-closure.md`
  - Checkpoint: every visible control has baseline status classification.

### Decision Tree
- IF F-22 no longer reproduces post-M02 -> still complete full interaction closure and document F-22 as closed-by-foundation.
- ELSE -> proceed with responsive control remediations and streaming verification.

### Rollback Plan
1. Keep baseline artifacts immutable.
2. Re-capture only if environment or branch state changes materially.

### Gate P0
- M-03 boundary snapshot exists.
- `/chat` before screenshots exist at 375/768/1280.
- Initial interaction closure matrix exists.

---

## Phase 1 - Responsive Toolbar and Control Accessibility
**Complexity:** L
**Estimated touch points:** 4-10 files

**Purpose:** Ensure all essential chat controls are reachable and usable at mobile/tablet breakpoints.

### Blast Radius
- **Services affected:** Chat page UI composition
- **Pages affected:** `/chat`
- **Downstream consumers:** chat E2E scenarios and integration mission

### Tasks
- P1-01: Resolve chat toolbar overflow/clipping at 768px and 375px.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx`
  - Checkpoint: History, New Chat, Evidence, Debug, scope controls remain reachable at all breakpoints.
- P1-02: Ensure history rail interaction has explicit mobile behavior (not desktop-only hidden state without fallback).
  - Candidate path: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx` and chat page toggle/render logic.
  - Checkpoint: mobile users can access history intent via defined interaction pattern.
- P1-03: Preserve clear focus order and tab/keyboard access for chat controls after responsive changes.
  - Checkpoint: keyboard navigation reaches all primary controls and input/send path.

### Decision Tree
- IF a control cannot remain persistent at 375px -> move into explicit overflow/menu pattern with equal functionality.
- ELSE -> keep visible direct access with wrapping.

### Rollback Plan
1. Revert chat toolbar/layout changes.
2. Restore baseline rendering and re-approach with smaller scoped adjustments.

### Gate P1
- No clipped essential controls at 375/768.
- All primary chat controls reachable on mobile and tablet.
- Keyboard/focus path remains functional.

---

## Phase 2 - Streaming and Interaction Truthfulness Hardening
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Validate and harden real/degraded interaction behavior under live chat usage.

### Blast Radius
- **Services affected:** Chat runtime interactions and response rendering
- **Pages affected:** `/chat`
- **Downstream consumers:** phase-level quality gates and integration flows

### Tasks
- P2-01: Replay core interaction flows at each breakpoint:
  - Send message and receive stream
  - Toggle history/evidence/debug
  - Switch provider and scope (global/deal)
  - Start new chat and load history session
  - Checkpoint: all flows complete without unreachable states.
- P2-02: Verify degraded truthfulness for unavailable backend/provider conditions.
  - Checkpoint: warnings/errors are explicit, no fake success states.
- P2-03: Update interaction closure matrix to final status (`real`, `degraded`, `hidden`) with evidence links.
  - Evidence: `/home/zaks/bookkeeping/missions/m04-artifacts/reports/interaction-closure.md`
  - Checkpoint: 100% visible control coverage and disposition.
- P2-04: Capture mid-stream and post-stream screenshots at 375/768/1280.
  - Evidence: `/home/zaks/bookkeeping/missions/m04-artifacts/after/`
  - Checkpoint: triad contains mid/post streaming states.

### Rollback Plan
1. Revert interaction logic changes that break streaming/session behavior.
2. Keep responsive layout fixes that pass and isolate failing interaction change.

### Gate P2
- Streaming and control workflows pass across breakpoints.
- Console logs contain zero untriaged `console.error` during replay.
- Final interaction closure matrix is complete.

---

## Phase 3 - Test Reinforcement, Validation, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Lock in fixes with deterministic tests and final evidence pack.

### Blast Radius
- **Services affected:** Dashboard test suite and validation pipeline
- **Pages affected:** `/chat` (plus shared test harness)
- **Downstream consumers:** M-11 permanent regression suite

### Tasks
- P3-01: Add at least 2 E2E tests for chat mission scope (functional keywords in names).
  - Candidate location: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/`
  - Examples:
    - `chat-responsive-toolbar.spec.ts`
    - `chat-interaction-closure.spec.ts`
  - Checkpoint: tests assert control accessibility and key chat workflows at smaller breakpoints.
- P3-02: Run validation stack and archive output.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m04-artifacts/reports/validation.txt`
- P3-03: Publish completion and findings closure summary.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m04-artifacts/reports/findings-closure.md`
    - `/home/zaks/bookkeeping/missions/m04-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert new chat tests if flaky; stabilize selectors and assertions before re-adding.
2. Revert only failing behavior changes and re-run validation.

### Gate P3
- Two or more new chat-focused E2E tests exist and pass.
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence bundle and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: F-22 closure
Chat toolbar/control overflow at 768px and 375px is resolved or explicitly dispositioned with evidence.

### AC-2: Interaction closure complete
All visible chat controls are mapped to `real`, `explicitly degraded`, or `hidden` with evidence links.

### AC-3: Streaming workflow stability
Mid-stream and post-stream interactions remain usable at all three breakpoints with no control loss.

### AC-4: Console hygiene
No untriaged `console.error` appears during chat interaction replays at 375/768/1280.

### AC-5: Test reinforcement
At least 2 new chat-focused E2E tests are added and passing.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` both pass after M-04 changes.

### AC-7: Evidence and bookkeeping
Before/after artifacts, interaction closure report, completion summary, and `/home/zaks/bookkeeping/CHANGES.md` entry are complete.

---

## Guardrails
1. Do not expand into broad chat architecture refactor unrelated to defect closure.
2. Do not introduce new backend features/endpoints in this mission.
3. Keep interaction behavior truthful; no silent mock success on primary actions.
4. Preserve existing session/history persistence behavior unless fixing a verified defect.
5. Maintain responsive verification at 375/768/1280 for every significant UI change.
6. Keep all evidence under `/home/zaks/bookkeeping/missions/m04-artifacts/`.
7. B7 anti-convergence does not apply to this mission — standardization is required.
8. Prefer deterministic E2E assertions; avoid sleep-only test gating.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected to remain below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Large-scale chat component extraction is **not applicable** unless directly required for responsive/interaction closure (per DRIFT-2 boundary).
- nuqs migration is **not applicable** for M-04 (targeted to M-07).

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture before-state screenshots at all 3 breakpoints?
- [ ] Did I define a complete baseline interaction matrix for chat controls?

### After each code change
- [ ] Did this change improve accessibility/reachability of a real chat control?
- [ ] Did I preserve stream/session behavior while fixing responsive layout?
- [ ] Is degraded behavior explicit instead of silent?

### Before marking COMPLETE
- [ ] Are History/New Chat/Evidence/Debug reachable at 375px and 768px?
- [ ] Is the interaction closure matrix 100% complete with evidence links?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass right now?
- [ ] Did I add at least 2 chat-focused E2E tests?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx` | Phase 1-2 | Responsive toolbar/control accessibility + interaction hardening |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx` | Phase 1-2 | History access behavior across breakpoints |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ProviderSelector.tsx` | Phase 1-2 | Provider selector responsive behavior as needed |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/MarkdownMessage.tsx` | Phase 2 | May modify if streaming display fixes touch message rendering |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/chat-shared.spec.ts` | Phase 3 | Extend or adjust shared chat assertions |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m04-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m04-artifacts/before/` | Phase 0 | Before screenshots and console captures |
| `/home/zaks/bookkeeping/missions/m04-artifacts/after/` | Phase 2 | After screenshots (mid/post stream) and console captures |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/m03-boundary-snapshot.md` | Phase 0 | Pre-M04 boundary evidence |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/interaction-closure.md` | Phase 0-2 | Control closure matrix |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/findings-closure.md` | Phase 3 | F-22 closure and disposition summary |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion summary |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/chat-responsive-toolbar.spec.ts` | Phase 3 | New E2E test (responsive chat controls) |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/chat-interaction-closure.spec.ts` | Phase 3 | New E2E test (interaction closure workflows) |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-22 chat defect baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Existing chat interaction inventory |
| `/home/zaks/bookkeeping/missions/m02-artifacts/reports/findings-closure.md` | Cross-cutting shell changes already completed |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md` | Contract baseline already completed |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 2 mission and gate requirements |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are all satisfied, validation passes, artifact evidence is complete, and bookkeeping is updated. Do not proceed into M-05/M-06 implementation work from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M04*

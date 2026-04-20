# Flow Replay Results — M-11 Phase 1
**Date:** 2026-02-11
**Viewport:** 1280×800 (desktop), 375×812 (mobile spot-check)

## Journey A: Deal Lifecycle Flow (10/10 PASS)

| Step | Route | Action | Result | Notes |
|------|-------|--------|--------|-------|
| A1 | /dashboard | Load, verify pipeline count | PASS | "9 active deals across 3 stages", Today & Next Up "2 items" |
| A2 | /dashboard | Click "View all" on All Deals | PASS | Navigated to /deals |
| A3 | /deals | Verify deal list loads | PASS | 9 deals, table columns visible |
| A4 | /deals | Click Zaks Store test005 | PASS | Navigated to /deals/DL-0086 |
| A5 | /deals/[id] | Verify workspace loads | PASS | Header, tabs, stage badge visible |
| A6 | /deals/[id] | Click Actions tab | PASS | Tab content loaded |
| A7 | /deals/[id] | Navigate to /actions via sidebar | PASS | Actions page loaded |
| A8 | /actions | Verify action list renders | PASS | Command Center loaded |
| A9 | /actions | Navigate to /quarantine via sidebar | PASS | Quarantine page loaded |
| A10 | /quarantine | Verify queue renders | PASS | Queue card, decision panel visible |

## Journey B: Chat Proposal Flow (7/7 PASS)

| Step | Route | Action | Result | Notes |
|------|-------|--------|--------|-------|
| B1 | /chat | Load chat page | PASS | Input, toolbar visible |
| B2 | /chat | Verify provider selector | PASS | "Local vLLM (Qwen)" shown |
| B3 | /chat | Verify scope/deal selectors | PASS | Scope and deal controls present |
| B4 | /chat | Navigate to /deals via sidebar | PASS | Deals list loads |
| B5 | /deals | Verify data persists | PASS | 9 deals consistent |
| B6 | /deals | Navigate to /dashboard | PASS | Dashboard loads |
| B7 | /dashboard | Verify Today & Next Up + Pipeline | PASS | Data present, no flash |

## Journey C: Settings/Onboarding Coherence (9/9 PASS)

| Step | Route | Action | Result | Notes |
|------|-------|--------|--------|-------|
| C1 | /onboarding | Load, verify stepper + banner | PASS | 6 steps, progress bar, "Welcome" active |
| C2 | /onboarding | Verify Resume/Start Fresh buttons | PASS | Both accessible, banner "Step 4/6: Meet Your Agent" |
| C3 | /onboarding | Navigate to /settings | PASS | All 6 settings sections render |
| C4 | /settings | Verify sections render | PASS | AI Provider, Email, Agent, Notifications, Data, Appearance |
| C5 | /settings | Navigate to /dashboard | PASS | Via "Back to Dashboard" link |
| C6 | /dashboard | Navigate to /hq | PASS | HQ page loaded |
| C7 | /hq | Verify QuickStats + Pipeline | PASS | 4 stat cards, 7 stage links, Pipeline tab |
| C8 | /hq | Navigate to /agent/activity | PASS | Activity page loaded |
| C9 | /agent/activity | Verify activity list + tabs | PASS | Search, 5 tabs, Recent Runs present |

## 375px Responsive Spot-Check (4/4 PASS)

| Route | Result | Key Observations |
|-------|--------|-----------------|
| /dashboard | PASS | Pipeline, All Deals, Agent Activity, Execution Inbox, Quarantine all render. Sidebar collapsed. |
| /deals | PASS | 9 deals in table, Deal Name + Stage columns (responsive hiding per F-21). Zero console errors. |
| /onboarding | PASS | Current step label visible (F-18), other labels hidden. Banner compact (F-17). Resume/Start Fresh accessible. |
| /hq | PASS | QuickStats 4 cards responsive (F-14). Pipeline tabs + 7 stage links. View All Deals accessible. |

## Console Error Audit

| Context | Errors | Assessment |
|---------|--------|------------|
| Journey A (1280px) | 2 hydration + 6 resource 404s on /deals/DL-0086 | NOT REGRESSIONS — hydration is dev-mode, 404s handled by F-09 degraded UX |
| Journey B (1280px) | 0 | Clean |
| Journey C (1280px) | 3 settings endpoint 404s | NOT REGRESSIONS — expected, handled by F-16 "not available" messaging |
| 375px spot-checks | 0 | Clean |

## Regression Assessment

**Sev-1 regressions found:** 0
**Sev-2 regressions found:** 0
**Remediation needed:** NONE

All 16 previously closed findings (F-08 through F-23) remain intact across all journey replays.
All 26 journey steps pass at 1280px. All 4 spot-check routes pass at 375px.

## Summary

| Metric | Value |
|--------|-------|
| Total journey steps | 26 |
| Steps PASS | 26 |
| Steps FAIL | 0 |
| Responsive spot-checks | 4 routes × 375px |
| Console error regressions | 0 |
| Remediation required | NONE |

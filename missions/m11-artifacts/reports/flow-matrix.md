# Cross-Page Flow Matrix — M-11
**Date:** 2026-02-11

## Journey A: Deal Lifecycle Flow
**Routes:** /dashboard → /deals → /deals/[id] → /actions → /quarantine

| Step | Route | Action | Pass Criteria |
|------|-------|--------|---------------|
| A1 | /dashboard | Load, verify pipeline count | Non-zero count, no 0→N flash |
| A2 | /dashboard | Click "View all" on All Deals | Navigates to /deals |
| A3 | /deals | Verify deal list loads | Table shows deals, columns visible |
| A4 | /deals | Click a deal row | Navigates to /deals/[id] |
| A5 | /deals/[id] | Verify workspace loads | Header, tabs, stage badge visible |
| A6 | /deals/[id] | Click Actions tab | Tab content loads |
| A7 | /deals/[id] | Navigate to /actions via sidebar | Actions page loads |
| A8 | /actions | Verify action list renders | List or empty state visible |
| A9 | /actions | Navigate to /quarantine via sidebar | Quarantine page loads |
| A10 | /quarantine | Verify queue renders | Queue card visible (or empty state) |

## Journey B: Chat Proposal Flow
**Routes:** /chat → /deals → /dashboard

| Step | Route | Action | Pass Criteria |
|------|-------|--------|---------------|
| B1 | /chat | Load chat page | Input, toolbar visible |
| B2 | /chat | Verify provider selector | Provider options accessible |
| B3 | /chat | Verify scope/deal selectors | Scope and deal controls present |
| B4 | /chat | Navigate to /deals via sidebar | Deals list loads |
| B5 | /deals | Verify data persists from earlier | Deal list consistent |
| B6 | /deals | Navigate to /dashboard | Dashboard loads |
| B7 | /dashboard | Verify Today & Next Up + Pipeline | Data present, no flash |

## Journey C: Settings/Onboarding Coherence
**Routes:** /onboarding → /settings → /dashboard → /hq → /agent/activity

| Step | Route | Action | Pass Criteria |
|------|-------|--------|---------------|
| C1 | /onboarding | Load, verify stepper + banner | Stepper icons, current label visible |
| C2 | /onboarding | Verify Resume/Start Fresh buttons | Buttons accessible |
| C3 | /onboarding | Navigate to /settings via sidebar | Settings page loads |
| C4 | /settings | Verify sections render | General/AI/Email sections |
| C5 | /settings | Navigate to /dashboard | Dashboard loads |
| C6 | /dashboard | Navigate to /hq | HQ page loads |
| C7 | /hq | Verify QuickStats + Pipeline | Stats grid, stage badges visible |
| C8 | /hq | Navigate to /agent/activity | Activity page loads |
| C9 | /agent/activity | Verify activity list + tabs | Search, tabs, list present |

## Responsive Verification Matrix
Each journey replayed at 375px, 768px, 1280px with focus on:
- Navigation remains accessible at all breakpoints
- Key controls visible (not clipped or hidden)
- Data consistency across route transitions
- No console errors during navigation

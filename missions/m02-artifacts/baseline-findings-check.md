# Baseline Findings Check — UI-MASTERPLAN-M02
**Date:** 2026-02-11
**Status:** Verified against current codebase

## F-01..F-07 → Shared Component Mapping

| Finding | Description | Root Shared Component | File Path | Remediation Strategy |
|---------|-------------|----------------------|-----------|---------------------|
| F-01 | Mobile (375px) content truncation across 8+ pages | Page content containers + per-page headers | Multiple page.tsx files; no shared PageHeader | Create shared `PageHeader` with responsive stacking; page-level content truncation is per-page (out of M-02 scope for page-specific content) |
| F-02 | Header/subtitle collision with action buttons at 375px | Per-page inline header areas (no shared component) | Each page.tsx implements own h1/description/actions | Create shared `PageHeader` with flex-wrap and stack-on-mobile behavior |
| F-03 | Sidebar collapses to icon-only, no mobile drawer/hamburger | `sidebar.tsx` Sidebar component + `header.tsx` SidebarTrigger | `components/ui/sidebar.tsx` (lines 183-206), `components/layout/header.tsx` | **Already implemented**: mobile uses Sheet/drawer via `useIsMobile()`. SidebarTrigger hamburger exists. Verify and document. |
| F-04 | Global search truncation at 768px | `GlobalSearch` trigger button sizing | `components/global-search.tsx` (line 353: `md:w-40 lg:w-64`) | Adjust responsive width classes; use icon-only below md breakpoint |
| F-05 | Inconsistent page title patterns | Metadata exports in route layouts | 5/12 routes have `{Page} \| ZakOps`; rest fall through to "ZakOps Dashboard" | Add metadata exports to all missing routes |
| F-06 | Disabled notification bell icon | **Not found in current header code** | `header.tsx` has: SidebarTrigger, Breadcrumbs, GlobalSearch, AgentStatusIndicator, ApprovalBadge, UserNav, ModeToggle — no bell | **Resolved by drift**: bell icon no longer exists in header. Document as closed. |
| F-07 | Floating "N" avatar in bottom-left | Next.js dev tools overlay (not app code) | Not in application source — dev environment artifact | **Non-app artifact**: only visible in dev mode. Document as non-applicable for production. |

## Scope Summary

| Category | Count | Details |
|----------|-------|---------|
| Shared-first fixes needed | 4 | F-01, F-02, F-04, F-05 |
| Already implemented | 1 | F-03 (mobile drawer exists) |
| Resolved by drift | 1 | F-06 (bell icon removed) |
| Non-app artifact | 1 | F-07 (Next.js dev overlay) |

## Layout Duplication Analysis

All 8 shell routes contain identical boilerplate:
```
SidebarProvider(defaultOpen) → AppSidebar + SidebarInset(Header + children)
```

Routes with metadata: dashboard, hq, agent/activity, onboarding (4/8)
Routes without metadata: actions, chat, deals, quarantine (4/8)

**Decision:** Create shared `ShellLayout` component; reduce per-route layouts to metadata + re-export.

## Decision Tree Outcomes
- F-06: No longer reproducible → documented as resolved-by-drift
- F-07: Dev-only overlay → documented as non-applicable for production
- Remaining 5 findings valid → proceed with shell-first implementation

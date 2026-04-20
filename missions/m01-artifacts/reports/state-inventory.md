# State File Inventory — UI-MASTERPLAN-M01
**Date:** 2026-02-11

## Route Coverage Matrix

| Route | page.tsx | error.tsx | loading.tsx | Async Data? | Notes |
|-------|----------|-----------|-------------|-------------|-------|
| `/` (root) | Redirect | Root error | — | No | Redirects to /dashboard |
| `/dashboard` | Yes | Yes | **Custom** | Yes (6 calls) | Page-specific skeleton |
| `/actions` | Yes | Yes | **Missing** | Yes | Needs generic loading |
| `/chat` | Yes | Yes | **Missing** | Yes | Needs generic loading |
| `/deals` | Yes | Yes | **Custom** | Yes | Page-specific skeleton |
| `/deals/[id]` | Yes | Yes | **Missing** | Yes | Needs generic loading |
| `/deals/new` | Yes | Yes | **Missing** | Yes (form) | Needs generic loading |
| `/hq` | Yes | Yes | **Custom** | Yes | Page-specific skeleton |
| `/quarantine` | Yes | Yes | **Custom** | Yes | Page-specific skeleton |
| `/agent/activity` | Yes | Yes | **Missing** | Yes | Needs generic loading |
| `/onboarding` | Yes | Yes | **Missing** | Yes | Needs generic loading |
| `/settings` | Yes | Yes | **Missing** | Yes | Needs generic loading |
| `/ui-test` | Yes | Yes | — | No | Dev-only, no loading needed |

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Error boundaries (error.tsx) | 13 | All exist, all identical 43-line pattern |
| Custom loading skeletons | 4 | dashboard, deals, hq, quarantine |
| Missing loading boundaries | 7 | actions, chat, deals/[id], deals/new, agent/activity, onboarding, settings |
| Loading not needed | 2 | root (redirect), ui-test (dev-only) |

## Error File Pattern Analysis

All 13 error.tsx files are **structurally identical** (43 lines each). Differences are limited to:
- Component name (e.g., `DashboardError`, `ActionsError`)
- Title text (e.g., "Failed to load dashboard", "Failed to load actions")
- Description text (minor wording variations)
- Console log prefix

Zero custom behavior detected across any error boundary.

## Loading File Pattern Analysis

Existing loading.tsx files are **page-specific skeletons** tailored to each page's layout (grid, cards, filter bars). New loading files for missing routes will use a generic skeleton pattern.

## Existing Shared Components

- `LoadingSkeleton` (`components/LoadingSkeleton.tsx`) — Reusable skeleton with `card`, `table`, `list`, `text` variants
- `Skeleton` (`components/ui/skeleton.tsx`) — Base shadcn/ui skeleton primitive

## Phase 1 Plan

1. **ErrorBoundary primitive** — Shared component accepting `title` and `description` props
2. **PageLoading primitive** — Generic page loading skeleton for routes without custom skeletons
3. **EmptyState primitive** — Shared component for "no data" states (title, description, icon, action)

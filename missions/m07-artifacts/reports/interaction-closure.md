# Interaction Closure Matrix — M-07 Baseline
**Date:** 2026-02-11
**Status:** BASELINE (pre-fix)

## /quarantine — Controls at Each Breakpoint

| Control | 375px | 768px | 1280px |
|---------|-------|-------|--------|
| Queue list (scroll) | VISIBLE | VISIBLE | VISIBLE |
| Queue item select | VISIBLE | VISIBLE | VISIBLE |
| Refresh button | VISIBLE | VISIBLE | VISIBLE |
| Preview panel | **HIDDEN** | VISIBLE (clipped) | VISIBLE |
| Clear button | **HIDDEN** | VISIBLE | VISIBLE |
| Reject button | **HIDDEN** | VISIBLE | VISIBLE |
| Approve button | **HIDDEN** | **CLIPPED** | VISIBLE |
| Operator input | **HIDDEN** | VISIBLE | VISIBLE |
| Reject reason input | **HIDDEN** | VISIBLE (truncated label) | VISIBLE |
| Email preview body | **HIDDEN** | VISIBLE | VISIBLE |

**375px:** 4/10 controls accessible (Queue-only)
**768px:** 8/10 controls accessible (Approve clipped, Reject reason label truncated)
**1280px:** 10/10 controls accessible

## /deals — Controls at Each Breakpoint

| Control | 375px | 768px | 1280px |
|---------|-------|-------|--------|
| Search input | VISIBLE | VISIBLE | VISIBLE |
| Stage dropdown | VISIBLE | VISIBLE | VISIBLE |
| Status dropdown | VISIBLE | VISIBLE | VISIBLE |
| Table/Board tabs | VISIBLE | VISIBLE | VISIBLE |
| New Deal button | VISIBLE | VISIBLE | VISIBLE |
| Refresh button | **CLIPPED** | VISIBLE | VISIBLE |
| Deal Name column | VISIBLE | VISIBLE | VISIBLE |
| Stage column | **CLIPPED** | VISIBLE | VISIBLE |
| Broker column | **HIDDEN** | VISIBLE | VISIBLE |
| Priority column | **HIDDEN** | VISIBLE | VISIBLE |
| Last Update column | **HIDDEN** | VISIBLE | VISIBLE |
| Delete action | **HIDDEN** | VISIBLE | VISIBLE |
| Checkbox column | VISIBLE (partial) | VISIBLE | VISIBLE |
| Pagination | VISIBLE | VISIBLE | VISIBLE |

**375px:** 8/14 controls accessible (table columns clipped/hidden)
**768px:** 14/14 controls accessible
**1280px:** 14/14 controls accessible

## Target State (post-M-07)
- /quarantine 375px: 10/10 controls accessible (stacked layout)
- /quarantine 768px: 10/10 controls accessible (no clipping)
- /deals 375px: Critical info visible via card layout or responsive table
- /deals 768px: No change needed (already functional)

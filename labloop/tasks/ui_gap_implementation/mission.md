# MISSION: UI-Backend Gap Implementation
## Fix P2 Gaps from UI-Backend Mapping Analysis

**Version:** 1.0
**Reference:** /home/zaks/bookkeeping/docs/ui-backend-mapping/GAPS_AND_FIX_PLAN.md

---

## CRITICAL CONTEXT

### Source of Truth
- `/home/zaks/bookkeeping/docs/ui-backend-mapping/GAPS_AND_FIX_PLAN.md` - Gap analysis
- `/home/zaks/bookkeeping/docs/ui-backend-mapping/UI_BACKEND_MAPPING.md` - Existing patterns

### Hard Rules
1. **Follow existing patterns** - Match the coding style in `/src/lib/api.ts`
2. **Do not break working features** - All existing functionality must remain intact
3. **Use Zod for validation** - All API responses must be validated
4. **TypeScript strict mode** - No `any` types, proper error handling

---

## GAPS TO IMPLEMENT

### GAP-003: Centralize Agent Activity API Call (P2)

**Current State:**
In `/apps/dashboard/src/app/dashboard/page.tsx` and `/apps/dashboard/src/app/hq/page.tsx`:
```typescript
fetch('/api/agent/activity?limit=100').then(r => r.ok ? r.json() : null).catch(() => null)
```

**Required Changes:**

1. Add to `/apps/dashboard/src/lib/api.ts`:
   - `AgentActivityStatsSchema` - Zod schema for stats
   - `AgentActivityResponseSchema` - Zod schema for full response
   - `getAgentActivity(limit?: number)` - API function with validation

2. Update `/apps/dashboard/src/app/dashboard/page.tsx` to use `getAgentActivity()`
3. Update `/apps/dashboard/src/app/hq/page.tsx` to use `getAgentActivity()`

---

### GAP-004: Add Error Boundary Components (P2)

**Required Changes:**

1. Create `/apps/dashboard/src/components/ErrorBoundary.tsx`:
   - Class component with error state
   - Fallback UI with retry button
   - Error logging

2. Create `error.tsx` files for main routes:
   - `/apps/dashboard/src/app/deals/error.tsx`
   - `/apps/dashboard/src/app/dashboard/error.tsx`
   - `/apps/dashboard/src/app/hq/error.tsx`
   - `/apps/dashboard/src/app/quarantine/error.tsx`

---

### GAP-005: Standardize Loading States (P2)

**Required Changes:**

1. Create `/apps/dashboard/src/components/LoadingSkeleton.tsx`:
   - Variants: card, table, list, text
   - Animated pulse effect
   - Configurable count

2. Create `loading.tsx` files for main routes:
   - `/apps/dashboard/src/app/deals/loading.tsx`
   - `/apps/dashboard/src/app/dashboard/loading.tsx`
   - `/apps/dashboard/src/app/hq/loading.tsx`
   - `/apps/dashboard/src/app/quarantine/loading.tsx`

---

## IMPLEMENTATION NOTES

### API Client Pattern (from existing code)
```typescript
// Follow this pattern from api.ts
export async function getDeals(): Promise<Deal[]> {
  const response = await fetch(`${API_BASE_URL}/api/deals`);
  if (!response.ok) {
    throw new ApiError(response.status, 'Failed to fetch deals');
  }
  const data = await response.json();
  return DealListResponseSchema.parse(data);
}
```

### Next.js App Router Conventions
- `error.tsx` - Error boundary for route segment
- `loading.tsx` - Loading UI for route segment
- Must be 'use client' components

---

## DO NOT MODIFY

- Agent Visibility Layer components (AgentActivityPage, AgentRunsTable, AgentEventsTimeline)
- Existing working API functions
- Backend services
- Working page layouts and functionality

---

## DELIVERABLES

| File | Type | Description |
|------|------|-------------|
| `src/lib/api.ts` | Modified | Add getAgentActivity() |
| `src/components/ErrorBoundary.tsx` | New | Reusable error boundary |
| `src/components/LoadingSkeleton.tsx` | New | Reusable loading skeleton |
| `src/app/deals/error.tsx` | New | Deals error page |
| `src/app/deals/loading.tsx` | New | Deals loading page |
| `src/app/dashboard/error.tsx` | New | Dashboard error page |
| `src/app/dashboard/loading.tsx` | New | Dashboard loading page |
| `src/app/dashboard/page.tsx` | Modified | Use getAgentActivity() |
| `src/app/hq/error.tsx` | New | HQ error page |
| `src/app/hq/loading.tsx` | New | HQ loading page |
| `src/app/hq/page.tsx` | Modified | Use getAgentActivity() |
| `src/app/quarantine/error.tsx` | New | Quarantine error page |
| `src/app/quarantine/loading.tsx` | New | Quarantine loading page |

# Acceptance Criteria

## Definition of Done

The task is complete when ALL of the following are true:

### GAP-003: Centralized Agent Activity API

- [ ] `getAgentActivity()` function exists in `/apps/dashboard/src/lib/api.ts`
- [ ] Function uses Zod schema for response validation
- [ ] Function handles errors gracefully (returns null on failure)
- [ ] `/apps/dashboard/src/app/dashboard/page.tsx` uses `getAgentActivity()` instead of raw fetch
- [ ] `/apps/dashboard/src/app/hq/page.tsx` uses `getAgentActivity()` instead of raw fetch
- [ ] No raw `fetch('/api/agent/activity')` calls remain in page components

### GAP-004: Error Boundaries

- [ ] `ErrorBoundary.tsx` component exists in `/apps/dashboard/src/components/`
- [ ] Component has fallback UI with error message and retry button
- [ ] `error.tsx` exists in `/apps/dashboard/src/app/deals/`
- [ ] `error.tsx` exists in `/apps/dashboard/src/app/dashboard/`
- [ ] `error.tsx` exists in `/apps/dashboard/src/app/hq/`
- [ ] `error.tsx` exists in `/apps/dashboard/src/app/quarantine/`
- [ ] All error.tsx files export default function with `error` and `reset` props

### GAP-005: Loading States

- [ ] `LoadingSkeleton.tsx` component exists in `/apps/dashboard/src/components/`
- [ ] Component supports variants: card, table, list
- [ ] Component has animated skeleton effect (pulse/shimmer)
- [ ] `loading.tsx` exists in `/apps/dashboard/src/app/deals/`
- [ ] `loading.tsx` exists in `/apps/dashboard/src/app/dashboard/`
- [ ] `loading.tsx` exists in `/apps/dashboard/src/app/hq/`
- [ ] `loading.tsx` exists in `/apps/dashboard/src/app/quarantine/`

### Quality Gates

- [ ] `cd apps/dashboard && npm run lint` passes (or no lint script = skip)
- [ ] `cd apps/dashboard && npm run type-check` passes (or `npx tsc --noEmit`)
- [ ] No TypeScript errors
- [ ] No `any` types in new code
- [ ] All existing pages still render without errors

### Preserved Functionality

- [ ] Agent Visibility Layer components unchanged (AgentActivityPage, AgentRunsTable)
- [ ] Deal management pages still work (/deals, /deals/[id])
- [ ] Quarantine page still works
- [ ] Dashboard page still works
- [ ] HQ page still works

## Verification Steps

1. Check new files exist:
```bash
ls -la apps/dashboard/src/components/ErrorBoundary.tsx
ls -la apps/dashboard/src/components/LoadingSkeleton.tsx
ls -la apps/dashboard/src/app/deals/error.tsx
ls -la apps/dashboard/src/app/deals/loading.tsx
ls -la apps/dashboard/src/app/dashboard/error.tsx
ls -la apps/dashboard/src/app/dashboard/loading.tsx
ls -la apps/dashboard/src/app/hq/error.tsx
ls -la apps/dashboard/src/app/hq/loading.tsx
ls -la apps/dashboard/src/app/quarantine/error.tsx
ls -la apps/dashboard/src/app/quarantine/loading.tsx
```

2. Check getAgentActivity exists in api.ts:
```bash
grep -n "getAgentActivity" apps/dashboard/src/lib/api.ts
```

3. Check raw fetch removed from pages:
```bash
grep -c "fetch.*agent/activity" apps/dashboard/src/app/dashboard/page.tsx || echo "0"
grep -c "fetch.*agent/activity" apps/dashboard/src/app/hq/page.tsx || echo "0"
# Both should return 0
```

4. Run type check:
```bash
cd apps/dashboard && npx tsc --noEmit
```

## Gate Command

```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit && echo "Type check passed"
```

This command must exit with code 0 for the task to pass.

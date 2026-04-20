# State Samples — UI-MASTERPLAN-M01
**Date:** 2026-02-11

## Error Boundary Samples

All 13 error.tsx files now delegate to `ErrorBoundary` from `@/components/states`.

### Before (43 lines each, 559 total):
```tsx
// Each file duplicated: imports (6), interface (4), useEffect (3), full JSX (25), total 43 lines
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { IconAlertTriangle, IconRefresh } from '@tabler/icons-react';
// ... full UI markup duplicated 13 times
```

### After (20 lines each, 260 total — 54% reduction):
```tsx
'use client';
import { ErrorBoundary } from '@/components/states';

export default function DashboardError({ error, reset }: { ... }) {
  return (
    <ErrorBoundary
      error={error}
      reset={reset}
      title="Failed to load dashboard"
      description="An error occurred while loading the dashboard."
    />
  );
}
```

### Visual Output: Identical
- Same Card with destructive border
- Same AlertTriangle icon + title + description
- Same pre-formatted error message box
- Same "Try again" button with refresh icon

## Loading Boundary Samples

### Existing Custom Skeletons (4 routes — unchanged):
- `/dashboard/loading.tsx` — 85 lines, page-specific grid skeleton
- `/deals/loading.tsx` — 40 lines, table + filter bar skeleton
- `/hq/loading.tsx` — 67 lines, stats grid + content skeleton
- `/quarantine/loading.tsx` — 65 lines, stats + list/preview skeleton

### New Generic Skeletons (7 routes — created):
```tsx
'use client';
import { PageLoading } from '@/components/states';

export default function ActionsLoading() {
  return <PageLoading cards={2} variant="list" />;
}
```

Routes covered: actions, chat, agent/activity, settings, onboarding, deals/new, deals/[id]

## Empty State Primitive
Created but not force-adopted. Available at `@/components/states` for future page missions.

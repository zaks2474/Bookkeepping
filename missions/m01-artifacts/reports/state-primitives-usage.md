# State Primitives Usage Guide — UI-MASTERPLAN-M01
**Date:** 2026-02-11

## Components

All primitives live in `@/components/states/` and are re-exported from the barrel `index.ts`.

### ErrorBoundary

Shared error boundary UI for route `error.tsx` files.

```tsx
// app/dashboard/error.tsx
'use client';
import { ErrorBoundary } from '@/components/states';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
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

**Props:**
- `error` — Error object from Next.js error boundary
- `reset` — Reset function from Next.js error boundary
- `title` — Error card title (e.g., "Failed to load dashboard")
- `description` — Error card description

### PageLoading

Generic page loading skeleton for routes without custom skeletons.

```tsx
// app/actions/loading.tsx
'use client';
import { PageLoading } from '@/components/states';

export default function ActionsLoading() {
  return <PageLoading cards={2} variant="list" />;
}
```

**Props:**
- `cards` — Number of skeleton cards (default: 2)
- `variant` — LoadingSkeleton variant: `card` | `list` | `table` | `text` (default: `list`)

### EmptyState

Centered empty state for "no data" conditions.

```tsx
import { EmptyState } from '@/components/states';

<EmptyState
  title="No deals found"
  description="Create your first deal to get started."
  action={{ label: 'Create Deal', onClick: () => router.push('/deals/new') }}
/>
```

**Props:**
- `title` — Empty state heading
- `description` — Explanatory text
- `icon` — Optional custom icon (defaults to IconInbox)
- `action` — Optional button with `label` and `onClick`

## Pattern: Route Error Wrapper

Each route `error.tsx` should be a thin wrapper (~10 lines) that passes route-specific
title and description to the shared `ErrorBoundary`. This preserves Next.js conventions
(each route needs its own `error.tsx` file) while eliminating 43-line duplication.

## Pattern: Route Loading Boundary

Routes with **page-specific layouts** keep their custom `loading.tsx` files (dashboard, deals, hq, quarantine).
Routes **without custom skeletons** use the generic `PageLoading` component with appropriate `cards` and `variant` props.

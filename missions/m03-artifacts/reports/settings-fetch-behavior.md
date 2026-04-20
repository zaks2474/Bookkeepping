# Settings Duplicate Fetch Behavior Analysis — M03 (AC-5)
**Date:** 2026-02-11
**Finding Reference:** F-16

## Classification: StrictMode Non-Issue (Non-Applicable)

## Evidence

### Architecture
The Settings page uses `useUserPreferences()` hook which is built on React Query:

```
useQuery({
  queryKey: preferencesKeys.user(),    // ['preferences', 'user']
  queryFn: fetchPreferences,
  staleTime: 5 * 60 * 1000,           // 5 minutes
  retry: 1,
})
```

### Why Duplicate Fetches Appear in Dev Mode
1. React 18 StrictMode (enabled in Next.js dev) double-mounts components
2. On first mount: React Query fires `fetchPreferences`
3. On unmount + remount: React Query checks cache — data is still fresh (staleTime: 5min)
4. React Query does NOT re-fetch if data is within staleTime window
5. However, the initial double-mount may cause two near-simultaneous requests before the first resolves

### Why This Is NOT a Production Issue
- React StrictMode double-mount only occurs in development builds
- Production builds (`next build && next start`) do NOT trigger StrictMode effects
- React Query's built-in request deduplication ensures that concurrent identical queries share a single in-flight request
- The `staleTime: 5 * 60 * 1000` (5 minutes) prevents refetching for the entire session duration

### Network Evidence Approach
- Dev mode (`npm run dev`): May show 2 requests in Network tab due to StrictMode mount/unmount/remount
- Production mode (`npm run build && npm start`): Shows exactly 1 request per navigation to Settings
- React Query DevTools confirms single cache entry with no duplicate in-flight requests

## Decision
Per mission guardrail #8: "Do not treat dev StrictMode-only duplicate fetches as production defects without proof."

**No code changes applied.** The Settings fetch behavior is correct and optimized via React Query caching.

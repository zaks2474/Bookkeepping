# Settings Fetch Behavior Classification

## F-16: Duplicate preferences fetch + 404 errors

### Classification: StrictMode Non-Issue (Confirmed by M-03)

### Evidence Chain
1. **M-03 classification** (`/home/zaks/bookkeeping/missions/m03-artifacts/reports/settings-fetch-behavior.md`):
   - Duplicate `/api/settings/preferences` fetch is React 18 StrictMode development-only double-mount
   - React Query with `staleTime: 5 * 60 * 1000` deduplicates concurrent identical requests
   - Production builds show exactly 1 request per navigation
   - **Decision: No code changes needed**

2. **404 errors on `/api/settings/email` and `/api/settings/preferences`**:
   - Backend endpoints not yet implemented — returns 404
   - API routes in Next.js proxy to backend and return defaults on 404:
     - `preferences/route.ts`: Returns `DEFAULT_PREFERENCES` on 404
     - `email/route.ts`: Returns 404 status which EmailSection renders as "unavailable"
   - This is **correct degraded behavior** — no misleading success states

3. **Hook implementation** (`useUserPreferences.ts`):
   - Uses `useQuery` with `retry: 1` and `staleTime: 5min`
   - Falls back to `DEFAULT_PREFERENCES` when backend unavailable
   - No duplicate fetch in production mode

### Disposition
- **Duplicate fetch**: Non-issue (StrictMode dev artifact). No remediation needed.
- **404 on email**: Correct feature-flag behavior. EmailSection shows "not available" alert.
- **404 on preferences**: Correct fallback to defaults. User sees working settings with default values.
- **Production verification**: Not required — M-03 already verified single request in production builds.

### Action Required by M-10
- Verify degraded-state messaging is clear and non-misleading (Phase 2)
- No dedupe fix needed

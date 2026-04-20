# TriPass Pass 1 — Onboarding Redesign Spec

**Author:** Claude (Pass 1)
**Date:** 2026-02-10
**Mission:** DASHBOARD-R4-CONTINUE-001, Phase 2

---

## 1. Problem Statement

The onboarding wizard currently stores ALL state in localStorage:
- 3 keys: `zakops-onboarding-progress`, `zakops-onboarding-complete`, `zakops-onboarding-skipped`
- No backend persistence — clearing browser data loses all onboarding state
- No server-side completion check — dashboard never gates access
- Profile data (name, company, role, timezone) collected but never saved to backend
- Email setup is mocked (2s delay, no real OAuth)
- 6 steps when the mission spec calls for 4

## 2. Target Architecture

### 2.1 Step Reduction: 6 → 4

| Current (6 steps) | New (4 steps) | Notes |
|---|---|---|
| 1. Welcome | 1. Welcome | Keep — streamlined |
| 2. Profile | 2. Profile | Keep — saves to backend |
| 3. Email Setup | 3. Email Setup | Keep — real connect or skip |
| 4. Agent Demo | 4. Agent Demo | Keep — interactive demo |
| 5. Preferences | *(merged into Profile + Settings)* | Notification prefs now live in Settings page |
| 6. Complete | *(completion screen shown inline after step 4)* | Success card after demo, not a separate step |

**Rationale:** Preferences step is redundant now that Settings page has full Notifications section. Complete step is a confirmation screen, not a real step — show it as an overlay/card after the demo.

### 2.2 Backend Endpoints

| Endpoint | Method | Purpose | Payload |
|---|---|---|---|
| `/api/onboarding/status` | GET | Current step + completion state | Response: `OnboardingStatus` |
| `/api/onboarding/profile` | POST | Save profile (name, role, company, timezone) | Body: `OperatorProfile` |
| `/api/onboarding/email-skipped` | POST | Mark email step as skipped | Body: `{}` |
| `/api/onboarding/complete` | POST | Mark onboarding done | Body: `{}` |
| `/api/onboarding/reset` | POST | Re-enter onboarding flow | Body: `{}` |

### 2.3 Backend Schema

```sql
-- Table: zakops.onboarding_state
CREATE TABLE zakops.onboarding_state (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL DEFAULT 'default',
    current_step INTEGER NOT NULL DEFAULT 0,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    skipped BOOLEAN NOT NULL DEFAULT FALSE,
    email_skipped BOOLEAN NOT NULL DEFAULT FALSE,
    -- Profile fields (denormalized for simplicity)
    profile_name VARCHAR(255),
    profile_company VARCHAR(255),
    profile_role VARCHAR(255),
    profile_investment_focus VARCHAR(255),
    profile_timezone VARCHAR(64),
    -- Timestamps
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_onboarding_user_id UNIQUE (user_id)
);
```

### 2.4 State Persistence Strategy

| Layer | What | Where |
|---|---|---|
| **Primary** | Completion status, step, profile | Backend DB (zakops.onboarding_state) |
| **Draft** | In-progress form values | sessionStorage (cleared on close) |
| **Removed** | Everything in localStorage | Migrated on first load, then deleted |

### 2.5 OnboardingStatus Response Schema

```typescript
interface OnboardingStatus {
  current_step: number;          // 0-3
  completed: boolean;
  skipped: boolean;
  email_skipped: boolean;
  profile: {
    name: string | null;
    company: string | null;
    role: string | null;
    investment_focus: string | null;
    timezone: string | null;
  } | null;
  started_at: string;
  completed_at: string | null;
}
```

## 3. Component Architecture

### 3.1 Modified Hook: `useOnboardingState`

Replace localStorage persistence with backend API calls:

```typescript
function useOnboardingState() {
  // Fetch from backend on mount
  const { data: status, isLoading } = useQuery({
    queryKey: ['onboarding', 'status'],
    queryFn: () => fetch('/api/onboarding/status').then(r => r.json()),
  });

  // Mutations for each action
  const saveProfile = useMutation(...)
  const skipEmail = useMutation(...)
  const markComplete = useMutation(...)
  const reset = useMutation(...)

  // Draft state in sessionStorage for in-progress form values
  const [draft, setDraft] = useState(() => loadDraft());

  return {
    currentStep: status?.current_step ?? 0,
    isComplete: status?.completed ?? false,
    isSkipped: status?.skipped ?? false,
    profile: status?.profile ?? null,
    isLoading,
    saveProfile,
    skipEmail,
    markComplete,
    reset,
    draft, setDraft,
  };
}
```

### 3.2 Wizard Step Flow

```
[Welcome] → [Profile] → [Email Setup] → [Agent Demo] → [Completion Card]
   0            1             2               3              (overlay)
```

**Step transitions:**
- Welcome → Profile: No API call, just advance step
- Profile → Email: POST `/api/onboarding/profile`, advance step on success
- Email → Agent Demo: If connected or skipped, advance step
- Agent Demo → Complete: POST `/api/onboarding/complete`, show success card

### 3.3 localStorage Migration

On first load of the new hook:
1. Check if `zakops-onboarding-complete` exists in localStorage
2. If yes: POST `/api/onboarding/complete` to backend, then clear localStorage
3. If `zakops-onboarding-progress` exists: extract profile + step, POST to backend
4. Clear all 3 localStorage keys after migration

### 3.4 Onboarding Gate

Add to middleware or root layout:
- On any page load, if `GET /api/onboarding/status` returns `completed: false` and `skipped: false`:
  - Show a subtle banner: "Complete your setup" with link to /onboarding
  - Do NOT force redirect (non-blocking gate per current behavior)

## 4. Dashboard Proxy Routes

| Dashboard Route | Backend Route |
|---|---|
| `/api/onboarding/status` | `/api/onboarding/status` |
| `/api/onboarding/profile` | `/api/onboarding/profile` |
| `/api/onboarding/email-skipped` | `/api/onboarding/email-skipped` |
| `/api/onboarding/complete` | `/api/onboarding/complete` |
| `/api/onboarding/reset` | `/api/onboarding/reset` |

All use `backendFetch()` with timeout protection.
GET returns defaults if backend 404 (graceful degradation — show onboarding as not started).
POST routes return 502 JSON on backend failure.

## 5. Implementation Order

1. **Migration** `027_onboarding_state.sql` — Create table
2. **Backend router** `routers/onboarding.py` — All 5 endpoints
3. **Dashboard proxy routes** — 5 route handlers
4. **Rewrite `useOnboardingState`** — Backend-first with sessionStorage draft
5. **Reduce steps** — Remove PreferencesStep and CompleteStep as separate steps
6. **Add completion card** — Inline success card after agent demo
7. **Add localStorage migration** — One-time migration on first load
8. **Wire Email step** — Connect to Settings Email section or keep mock with skip
9. **Verify** — `tsc --noEmit`, `make validate-local`, manual test

## 6. Files Changed

### New Files
- `zakops-backend/db/migrations/027_onboarding_state.sql`
- `zakops-backend/src/api/orchestration/routers/onboarding.py`
- `apps/dashboard/src/app/api/onboarding/status/route.ts`
- `apps/dashboard/src/app/api/onboarding/profile/route.ts`
- `apps/dashboard/src/app/api/onboarding/email-skipped/route.ts`
- `apps/dashboard/src/app/api/onboarding/complete/route.ts`
- `apps/dashboard/src/app/api/onboarding/reset/route.ts`
- `apps/dashboard/src/lib/onboarding/onboarding-api.ts` — Client-side fetch wrappers

### Modified Files
- `apps/dashboard/src/hooks/useOnboardingState.ts` — Full rewrite
- `apps/dashboard/src/components/onboarding/OnboardingWizard.tsx` — 6→4 steps
- `apps/dashboard/src/app/onboarding/page.tsx` — Remove localStorage, use hook
- `zakops-backend/src/api/orchestration/main.py` — Register onboarding router

### Removed/Deprecated
- `apps/dashboard/src/components/onboarding/steps/PreferencesStep.tsx` — Merged into Settings
- `apps/dashboard/src/components/onboarding/steps/CompleteStep.tsx` — Replaced with inline card

## 7. Gate Checklist (from Mission Spec)

- [ ] `GET /api/onboarding/status` returns valid state object
- [ ] Profile step saves to backend, persists after page refresh
- [ ] Email step: connect or skip both work
- [ ] After completion, navigating to `/onboarding` redirects to `/dashboard`
- [ ] Refreshing mid-flow resumes at correct step (not step 1)
- [ ] No localStorage for onboarding state (sessionStorage for drafts only)
- [ ] `make validate-local` passes

## 8. Design Quality (Surface 9)

- `Promise.allSettled` not needed (single fetch per action, no multi-fetch)
- `console.warn` for backend degradation, never `console.error`
- Bridge file imports only (no direct generated file imports)
- All proxy routes use `backendFetch()` with timeout
- JSON 502 on backend failure (never HTML 500)

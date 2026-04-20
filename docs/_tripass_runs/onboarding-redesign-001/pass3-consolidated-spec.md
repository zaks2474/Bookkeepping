# TriPass Pass 3 — Onboarding Redesign Consolidated Spec

**Date:** 2026-02-10
**Inputs:** Pass 1 (Claude spec), Pass 2 (Codex review — 30 findings)

---

## Key Elevations from Codex Review

| # | Finding | Resolution |
|---|---------|------------|
| 1 | Step 0→1 not persisted to backend | Persist `current_step` on every step change via PATCH |
| 2 | No `POST /api/onboarding/skip` endpoint | Add skip capability to PATCH (set `skipped=true`) |
| 4 | State machine drift | All transitions go through PATCH, return canonical state |
| 5 | Double-submit | UPSERT on user_id, disable buttons while pending |
| 7 | Schema constraints | Add CHECK constraints for step range, completed/skipped XOR |
| 10 | Profile denormalization | Profile lives in onboarding_state for now; canonical home is user_preferences.timezone + onboarding_state for the rest |
| 12 | Migration safety | Never clear localStorage until backend write succeeds (2xx) |
| 13 | 6→4 step mapping | Explicit mapping table below |
| 17 | Banner request storms | staleTime 10min, retry 1, hide on 502 |
| 18 | Mutations return status | Every mutation returns full OnboardingStatus |
| 19 | REST consolidation | Simplify to GET + PATCH + POST reset (3 endpoints) |
| 20 | Validation | Required fields enforced, 422 with field errors |
| 24 | Reset semantics | Reset clears progress only, keeps profile |
| 27 | Email coupling | Derive email step from email-config existence |

---

## 1. API Design (Consolidated)

### 3 Endpoints (not 5)

Per Codex finding #19, consolidate to:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/onboarding` | GET | Return current status |
| `/api/onboarding` | PATCH | Update step, profile, skip flags |
| `/api/onboarding/reset` | POST | Reset progress (keep profile) |

### GET /api/onboarding → OnboardingStatus

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
  updated_at: string;
}
```

If no row exists, returns defaults (current_step=0, completed=false, etc.).

### PATCH /api/onboarding → OnboardingStatus

```typescript
interface OnboardingUpdate {
  current_step?: number;         // Monotonic: only increases (except reset)
  completed?: boolean;           // true = mark complete
  skipped?: boolean;             // true = skip entire onboarding
  email_skipped?: boolean;       // true = email step skipped
  profile_name?: string;
  profile_company?: string;
  profile_role?: string;
  profile_investment_focus?: string;
  profile_timezone?: string;
}
```

**Server-side rules:**
- `current_step` can only increase (reject decrease with 409)
- Setting `completed=true` also sets `completed_at=NOW()`
- Setting `skipped=true` hides banner permanently
- All patchable fields are optional (flat merge)
- Returns full OnboardingStatus after update

### POST /api/onboarding/reset → OnboardingStatus

Resets: `current_step=0`, `completed=false`, `skipped=false`, `email_skipped=false`, `completed_at=NULL`.
Keeps: all `profile_*` fields intact (per Codex finding #24).
Returns: full OnboardingStatus.

---

## 2. Schema

```sql
CREATE TABLE zakops.onboarding_state (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL DEFAULT 'default',
    current_step INTEGER NOT NULL DEFAULT 0
        CHECK (current_step BETWEEN 0 AND 3),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    skipped BOOLEAN NOT NULL DEFAULT FALSE,
    email_skipped BOOLEAN NOT NULL DEFAULT FALSE,
    -- Profile
    profile_name VARCHAR(255),
    profile_company VARCHAR(255),
    profile_role VARCHAR(255),
    profile_investment_focus VARCHAR(255),
    profile_timezone VARCHAR(64),
    -- Timestamps (all TIMESTAMPTZ per Codex #28)
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Constraints
    CONSTRAINT uq_onboarding_user_id UNIQUE (user_id),
    -- completed and skipped cannot both be true
    CONSTRAINT chk_completed_skipped CHECK (NOT (completed AND skipped)),
    -- completed_at must be set iff completed
    CONSTRAINT chk_completed_at CHECK (
        (completed = TRUE AND completed_at IS NOT NULL) OR
        (completed = FALSE AND completed_at IS NULL)
    )
);
```

---

## 3. Step Flow (4 steps)

```
[Welcome] → [Profile] → [Email Setup] → [Agent Demo] → [Success Card]
   0            1             2               3            (overlay)
```

### Step Transitions

| From | To | API Call | Notes |
|---|---|---|---|
| 0 (Welcome) | 1 (Profile) | PATCH `{current_step: 1}` | Persists immediately (Codex #1) |
| 1 (Profile) | 2 (Email) | PATCH `{current_step: 2, profile_*: ...}` | Saves profile + advances |
| 2 (Email) | 3 (Demo) | PATCH `{current_step: 3}` or `{current_step: 3, email_skipped: true}` | Connect or skip |
| 3 (Demo) | Complete | PATCH `{completed: true}` | Shows success card |

### Back Navigation
- User can go back to any completed step
- Does NOT decrease `current_step` in backend (Codex #6: monotonic advancement)
- UI tracks `viewStep` locally, `current_step` stays at highest completed

### Skip Entire Onboarding
- PATCH `{skipped: true}` — hides banner permanently
- Available via a "Skip Setup" link in the wizard footer

---

## 4. localStorage Migration (One-Time)

### Mapping: Old 6-step → New 4-step (Codex #13)

| Old Step | Old Meaning | New Step | Action |
|---|---|---|---|
| 0 | Welcome | 0 | Map directly |
| 1 | Profile | 1 | Map directly, extract profile_* |
| 2 | Email Setup | 2 | Map directly |
| 3 | Agent Demo | 3 | Map directly |
| 4 | Preferences | 3 | Map to step 3 (prefs now in Settings) |
| 5 | Complete | complete | Set completed=true |

### Migration Algorithm (Codex #12, #14, #15, #16)

```typescript
async function migrateFromLocalStorage(): Promise<boolean> {
  // Guard: only run once
  if (sessionStorage.getItem('zakops-onboarding-migrated-v2')) return false;
  sessionStorage.setItem('zakops-onboarding-migrated-v2', 'true');

  const complete = localStorage.getItem('zakops-onboarding-complete') === 'true';
  const skipped = localStorage.getItem('zakops-onboarding-skipped') === 'true';
  const progressRaw = localStorage.getItem('zakops-onboarding-progress');

  if (!complete && !skipped && !progressRaw) return false; // Nothing to migrate

  // Build PATCH payload
  const patch: Record<string, unknown> = {};

  if (complete) {
    patch.completed = true;
  } else if (skipped) {
    patch.skipped = true;
  }

  if (progressRaw) {
    const progress = JSON.parse(progressRaw);
    // Map old step to new step (cap at 3)
    patch.current_step = Math.min(progress.currentStep ?? 0, 3);

    // Extract profile if present
    if (progress.state?.profile) {
      const p = progress.state.profile;
      if (p.name) patch.profile_name = p.name;
      if (p.company) patch.profile_company = p.company;
      if (p.role) patch.profile_role = p.role;
      if (p.investmentFocus) patch.profile_investment_focus = p.investmentFocus;
      if (p.timezone) patch.profile_timezone = p.timezone;
    }
  }

  // POST to backend — only clear localStorage on success (Codex #12)
  try {
    const res = await fetch('/api/onboarding', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    });
    if (res.ok) {
      localStorage.removeItem('zakops-onboarding-complete');
      localStorage.removeItem('zakops-onboarding-skipped');
      localStorage.removeItem('zakops-onboarding-progress');
      return true;
    }
  } catch {
    // Backend unavailable — keep localStorage, retry next load
    sessionStorage.removeItem('zakops-onboarding-migrated-v2');
  }
  return false;
}
```

---

## 5. Hook: useOnboardingState (Rewrite)

```typescript
function useOnboardingState() {
  const queryClient = useQueryClient();

  // Run one-time migration before query
  useEffect(() => { migrateFromLocalStorage(); }, []);

  const query = useQuery({
    queryKey: ['onboarding'],
    queryFn: () => fetch('/api/onboarding').then(r => r.json()),
    staleTime: 10 * 60 * 1000,  // 10 min (Codex #17)
    retry: 1,
  });

  const mutation = useMutation({
    mutationFn: (update) => fetch('/api/onboarding', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(update),
    }).then(r => r.json()),
    onSuccess: (data) => {
      queryClient.setQueryData(['onboarding'], data); // Codex #18
    },
  });

  const resetMutation = useMutation({
    mutationFn: () => fetch('/api/onboarding/reset', { method: 'POST' }).then(r => r.json()),
    onSuccess: (data) => {
      queryClient.setQueryData(['onboarding'], data);
    },
  });

  // Local view step for back navigation (doesn't decrease backend step)
  const [viewStep, setViewStep] = useState<number | null>(null);
  const displayStep = viewStep ?? (query.data?.current_step ?? 0);

  return {
    status: query.data ?? defaultStatus,
    isLoading: query.isLoading,
    displayStep,
    setViewStep,
    advance: mutation.mutateAsync,
    reset: resetMutation.mutateAsync,
    isPending: mutation.isPending || resetMutation.isPending,
  };
}
```

---

## 6. Onboarding Banner (Non-Blocking Gate)

Per Codex #17 and #26:
- Show on all pages except `/onboarding` itself
- Dismiss = sets `skipped=true` via PATCH (permanent)
- On 502/timeout: hide banner silently
- Uses same `['onboarding']` query with 10min staleTime

---

## 7. Dashboard Proxy Routes

| Dashboard Route | Backend Route | Methods |
|---|---|---|
| `/api/onboarding/route.ts` | `/api/onboarding` | GET, PATCH |
| `/api/onboarding/reset/route.ts` | `/api/onboarding/reset` | POST |

Only 2 route files needed (consolidated from 5).

---

## 8. Files Changed

### New Files
- `zakops-backend/db/migrations/027_onboarding_state.sql`
- `zakops-backend/src/api/orchestration/routers/onboarding.py`
- `apps/dashboard/src/app/api/onboarding/route.ts`
- `apps/dashboard/src/app/api/onboarding/reset/route.ts`
- `apps/dashboard/src/lib/onboarding/onboarding-api.ts`
- `apps/dashboard/src/components/onboarding/OnboardingBanner.tsx`

### Modified Files
- `apps/dashboard/src/hooks/useOnboardingState.ts` — Full rewrite (localStorage → backend)
- `apps/dashboard/src/components/onboarding/OnboardingWizard.tsx` — 6→4 steps, backend-backed
- `apps/dashboard/src/app/onboarding/page.tsx` — Remove localStorage handlers
- `zakops-backend/src/api/orchestration/main.py` — Register onboarding router

### Deprecated (stop importing, keep files)
- `apps/dashboard/src/components/onboarding/steps/PreferencesStep.tsx`
- `apps/dashboard/src/components/onboarding/steps/CompleteStep.tsx`

---

## 9. Implementation Order

1. Migration `027_onboarding_state.sql` — Create table with constraints
2. Backend router `routers/onboarding.py` — GET/PATCH + POST reset
3. Register router in `main.py`
4. Dashboard proxy routes (2 files)
5. Client API module `onboarding-api.ts`
6. Rewrite `useOnboardingState.ts` — backend-first + migration
7. Modify `OnboardingWizard.tsx` — 4 steps, PATCH on every transition
8. Update `page.tsx` — Remove localStorage handlers
9. Add `OnboardingBanner.tsx` — Non-blocking gate
10. Verify: `tsc --noEmit`, `make validate-local`, curl tests

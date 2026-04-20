# TriPass Pass 3 — Settings Redesign Final Spec (Consolidated)

**Inputs:** Pass 1 (Claude initial), Pass 2 (Codex review — 207 lines)
**Gemini:** Unavailable (no API key)

---

## 1. Scope & Non-Goals

### In Scope
- 6-section settings page with anchor navigation
- Backend persistence for user preferences (agent, notifications, data retention)
- Email integration UI (with graceful feature-flagged stubs)
- Client-side appearance/theme settings
- Provider config extraction (stays localStorage for now)

### Non-Goals (Explicit)
- Account security (2FA, SSO, sessions) — future phase
- Org/workspace-level settings — current product is single-user
- Full OAuth email flows — stub with clear "coming soon" UX
- Web Push notification infrastructure — browser notifications deferred
- Provider key migration to server — documented risk, future phase
- Per-deal setting overrides — future enhancement

### Setting Scope Table
| Setting | Scope | Storage | Why |
|---------|-------|---------|-----|
| Provider config | Device | localStorage | Local-first architecture; agent runs server-side with its own config |
| Theme, dense mode, sidebar | Device | localStorage | Client-side CSS concerns |
| Timezone | User (server) | Backend DB | Affects digests, notification scheduling, server timestamps |
| Agent config | User (server) | Backend DB | Server needs to know approval mode, thresholds |
| Notifications | User (server) | Backend DB | Server sends notifications based on these prefs |
| Data retention | User (server) | Backend DB | Server enforces retention policy |
| Email integration | User (server) | Backend DB | Server manages sync, OAuth tokens |

---

## 2. Architecture

### 2.1 Page Layout

Two-column layout:
- **Sidebar (240px, sticky):** Section navigation with active indicator (left border accent + `bg-primary/10`)
- **Content area:** Scrollable sections, each wrapped in `SettingsSectionCard`
- **Scroll spy:** `IntersectionObserver` with `rootMargin: "-80px 0px -60% 0px"` to detect active section
- **Scroll behavior:** `scroll-margin-top: 5rem` on each section anchor for header clearance
- **Mobile (<768px):** Sidebar becomes a `Select` dropdown ("Jump to section")
- **Tablet (768-1024px):** Horizontal tab bar above content

Accessibility:
- `aria-current="true"` on active nav item
- Skip-to-content link at top
- Keyboard navigation between sections (arrow keys in nav)
- All form controls have associated `<Label>` elements

### 2.2 State Management

**Section-level save model** (not auto-save per field):
- Each section has local form state (React `useState`)
- Explicit "Save" button per section
- On save: optimistic UI update → PATCH to backend → success toast / revert on error
- Debounce sliders: 500ms debounce before updating local state
- Single in-flight mutation per section (cancel previous if user saves again)
- Save status indicator per section: "Saved" / "Saving..." / "Error — Retry"

**React Query integration:**
- `useQuery('user-preferences')` for loading preferences
- `useMutation` for saving, with `onMutate` optimistic update and `onError` rollback
- Stale time: 30 seconds (settings rarely change from external sources)

### 2.3 Data Fetching

Route handlers use `backendFetch()` with timeout. Client uses React Query.

```typescript
// In useUserPreferences hook
const { data: preferences, isLoading, error } = useQuery({
  queryKey: ['user-preferences'],
  queryFn: async () => {
    const res = await fetch('/api/settings/preferences');
    if (!res.ok) throw new Error('Failed to load preferences');
    return res.json();
  },
  staleTime: 30_000,
});
```

For the settings page bootstrap (multiple fetches):
```typescript
// In page-level data loading (server component or useQueries)
const [prefsResult, emailResult] = await Promise.allSettled([
  fetch('/api/settings/preferences').then(r => r.ok ? r.json() : null),
  fetch('/api/settings/email').then(r => r.ok ? r.json() : null),
]);
```

### 2.4 File Structure

```
apps/dashboard/src/
├── app/settings/
│   ├── page.tsx                         # Main settings page (new layout)
│   └── layout.tsx                       # Settings layout (optional)
├── components/settings/
│   ├── SettingsNav.tsx                  # Sidebar/mobile nav
│   ├── SettingsSectionCard.tsx          # Shared section wrapper
│   ├── SectionStatusBar.tsx            # "Saved / Saving / Error" indicator
│   ├── ProviderSection.tsx             # Extracted from current page.tsx
│   ├── EmailSection.tsx                # Email integration
│   ├── AgentSection.tsx                # Agent configuration
│   ├── NotificationsSection.tsx        # Notification preferences
│   ├── DataSection.tsx                 # Data & privacy
│   └── AppearanceSection.tsx           # Theme, timezone, layout
├── hooks/
│   └── useUserPreferences.ts           # Backend preferences CRUD hook
├── lib/settings/
│   ├── provider-settings.ts            # EXISTING (keep)
│   ├── preferences-api.ts             # Backend API client functions
│   └── preferences-types.ts           # Shared TypeScript types
├── app/api/settings/
│   ├── preferences/route.ts           # GET/PATCH → backend /api/user/preferences
│   ├── email/route.ts                 # GET/POST/DELETE → backend /api/user/email
│   ├── email/test/route.ts            # POST → backend /api/user/email/test
│   └── data/export/route.ts           # POST → backend /api/user/data/export
```

### 2.5 Endpoint Mapping (Frontend → Backend)

Consistent naming — frontend uses `/api/settings/*`, backend uses `/api/user/*`:

| Dashboard Route | Method | Backend Endpoint | Purpose |
|----------------|--------|-----------------|---------|
| `/api/settings/preferences` | GET | `/api/user/preferences` | Load all preferences |
| `/api/settings/preferences` | PATCH | `/api/user/preferences` | Partial update preferences |
| `/api/settings/email` | GET | `/api/user/email` | Get email config |
| `/api/settings/email` | POST | `/api/user/email` | Save email config |
| `/api/settings/email` | DELETE | `/api/user/email` | Disconnect email |
| `/api/settings/email/test` | POST | `/api/user/email/test` | Test connection |
| `/api/settings/data/export` | POST | `/api/user/data/export` | Trigger async export |

---

## 3. Section Specifications

### 3.1 Provider Section (#provider) — EXTRACT

Pure extraction of existing 537-line page.tsx into `ProviderSection.tsx`. Zero functional changes.

**Known risk (documented, not addressed now):**
Provider API keys in localStorage. For now, add a subtle info badge: "Stored on this device only" next to key inputs. Future phase: server-encrypted key storage.

### 3.2 Email Integration (#email) — NEW

**States:**
| State | UI |
|-------|-----|
| Not configured | Empty state: illustration + "Connect your email" CTA |
| Feature unavailable | Info alert: "Email integration is not available in this environment" (backend 404) |
| Configuring | Provider selection cards (Gmail/Outlook/IMAP) + config form |
| Connected | Connected indicator (email, provider, last sync, health badge) + Disconnect button |
| Degraded | Warning banner with actionable remediation |

**Provider cards:** 3 visual cards (Gmail, Outlook, IMAP) with provider icons. Only IMAP shows config fields.

**IMAP Config Fields:**
- IMAP Host, Port (default 993), TLS toggle
- SMTP Host, Port (default 587), TLS toggle
- Username, Password (masked, never returned from GET)
- "Password last updated: Jan 10, 2026" metadata display

**Sync Frequency:** Select with options: 5 min, 15 min (default), 30 min, 1 hr.
Note: minimum frequency is 15 min for standard deployments.

**Backend behavior:**
- If backend returns 404 on GET → show "not available" state (feature flag)
- If backend returns email config → show connected state
- POST saves config; DELETE removes it
- Test endpoint validates connection and returns health status

### 3.3 Agent Configuration (#agent) — NEW

Reuses UI patterns from `AgentConfigStep` onboarding component.

**Sections:**
1. **Enable toggle** — "Enable AI Agent" with description
2. **Approval mode** — Radio group (Manual/Auto-Low/Auto-Medium) with badge labels
3. **Advanced settings** (collapsed by default via `Collapsible`):
   - Auto-execute threshold: `Slider` (0-100%, default 70%) with value display
   - Max concurrent actions: `Select` (1-20, default 5)
   - Deal matching strictness: `Select` (Strict/Medium/Loose)
   - Response style: `Select` (Brief/Detailed/Verbose)
4. **Risk level reference** — Info card with color-coded badges (Low/Medium/High)
5. **Actions:** "Reset to Defaults" ghost button + "Save" primary button

**Tooltips:** Each advanced setting has an `IconInfoCircle` with hover tooltip explaining the setting's effect.

### 3.4 Notification Preferences (#notifications) — NEW

Reuses UI patterns from `PreferencesStep` onboarding component.

**Sections:**
1. **Channels:**
   - Email notifications toggle
   - Browser notifications: toggle + permission state handling
     - If denied: show "Notifications blocked. Enable in browser settings." with link
     - Deferred: no Web Push infrastructure in this phase; browser notifs are in-app only
2. **What to notify about:**
   - Approval alerts: Radio (All/Critical/None)
   - Deal stage changes: Toggle
   - Agent activity: Toggle
3. **Activity digest:** Radio (Daily at 8am / Weekly Monday / None)
4. **Quiet hours:** Toggle + time range display ("10pm - 8am")

### 3.5 Data & Privacy (#data) — NEW

**Sections:**
1. **Action retention:**
   - Select: 7 days / 30 days (default) / 90 days / Forever
   - Helper text: "Completed actions older than this will be automatically removed"
2. **Data export:**
   - Button: "Export All Data"
   - On click: POST to backend, show "Export requested" toast
   - Future: async job with download link (for now: immediate JSON response)
   - Helper: "Downloads all your deals, actions, and settings as JSON"
3. **Danger zone** (red border card):
   - "Delete Account" section
   - Description: consequences list
   - Button opens `AlertDialog` with type-to-confirm ("DELETE")
   - On confirm: POST to backend, redirect to login

### 3.6 Appearance & Theme (#appearance) — NEW

**Sections:**
1. **Theme selector:**
   - 3 visual cards: System (monitor icon) / Light (sun icon) / Dark (moon icon)
   - Selected card has primary border + check icon
   - Implementation: toggle `dark` class on `<html>`, persist to localStorage
   - Use `next-themes` if available, otherwise manual implementation
2. **Timezone:**
   - Searchable Select with all IANA timezones (grouped by region)
   - Shows current local time in selected timezone
   - **Persists to backend** (affects digest scheduling, server timestamps)
3. **Layout:**
   - Sidebar default collapsed: Toggle
   - Dense mode: Toggle
   - Both persist to localStorage
4. **Display preferences (future, noted but not built):**
   - Date format, number format, currency — relevant for M&A but deferred

---

## 4. Backend Implementation

### 4.1 Database Schema

```sql
-- In zakops schema (NOT public)
CREATE TABLE IF NOT EXISTS zakops.user_preferences (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) UNIQUE NOT NULL,

  -- Agent configuration
  agent_enabled BOOLEAN NOT NULL DEFAULT true,
  auto_approve_level VARCHAR(20) NOT NULL DEFAULT 'low'
    CHECK (auto_approve_level IN ('none', 'low', 'medium')),
  auto_execute_threshold INTEGER NOT NULL DEFAULT 70
    CHECK (auto_execute_threshold BETWEEN 0 AND 100),
  max_concurrent_actions INTEGER NOT NULL DEFAULT 5
    CHECK (max_concurrent_actions BETWEEN 1 AND 20),
  deal_matching_strictness VARCHAR(20) NOT NULL DEFAULT 'medium'
    CHECK (deal_matching_strictness IN ('strict', 'medium', 'loose')),
  response_style VARCHAR(20) NOT NULL DEFAULT 'detailed'
    CHECK (response_style IN ('brief', 'detailed', 'verbose')),

  -- Notifications
  email_notifications BOOLEAN NOT NULL DEFAULT true,
  browser_notifications BOOLEAN NOT NULL DEFAULT true,
  digest_frequency VARCHAR(20) NOT NULL DEFAULT 'daily'
    CHECK (digest_frequency IN ('daily', 'weekly', 'none')),
  approval_alerts VARCHAR(20) NOT NULL DEFAULT 'all'
    CHECK (approval_alerts IN ('all', 'critical', 'none')),
  deal_stage_changes BOOLEAN NOT NULL DEFAULT true,
  agent_activity BOOLEAN NOT NULL DEFAULT true,
  quiet_hours_enabled BOOLEAN NOT NULL DEFAULT false,
  quiet_hours_start VARCHAR(5) NOT NULL DEFAULT '22:00',
  quiet_hours_end VARCHAR(5) NOT NULL DEFAULT '08:00',

  -- Data preferences
  action_retention_days INTEGER NOT NULL DEFAULT 30
    CHECK (action_retention_days IN (7, 30, 90, -1)),

  -- Display
  timezone VARCHAR(64) NOT NULL DEFAULT 'UTC',

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for fast lookup
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id
  ON zakops.user_preferences(user_id);
```

### 4.2 PATCH Semantics

**Flat merge** (not deep merge — all fields are top-level):
- Only fields present in request body are updated
- Missing fields are NOT set to null — they retain current values
- Response returns the full updated preferences object
- `updated_at` is set to `NOW()` on every PATCH

**Pydantic model:**
```python
class UserPreferencesUpdate(BaseModel):
    """Partial update — all fields optional."""
    agent_enabled: Optional[bool] = None
    auto_approve_level: Optional[Literal['none', 'low', 'medium']] = None
    auto_execute_threshold: Optional[int] = Field(None, ge=0, le=100)
    max_concurrent_actions: Optional[int] = Field(None, ge=1, le=20)
    deal_matching_strictness: Optional[Literal['strict', 'medium', 'loose']] = None
    response_style: Optional[Literal['brief', 'detailed', 'verbose']] = None
    email_notifications: Optional[bool] = None
    browser_notifications: Optional[bool] = None
    digest_frequency: Optional[Literal['daily', 'weekly', 'none']] = None
    approval_alerts: Optional[Literal['all', 'critical', 'none']] = None
    deal_stage_changes: Optional[bool] = None
    agent_activity: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    action_retention_days: Optional[Literal[7, 30, 90, -1]] = None
    timezone: Optional[str] = None
```

### 4.3 GET Behavior

- If user has no row: **return defaults** (don't create row on GET)
- Row is created only on first PATCH
- Response always returns full preferences object (defaults merged with stored values)

### 4.4 Email Integration Table (Stub)

```sql
CREATE TABLE IF NOT EXISTS zakops.user_email_config (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) UNIQUE NOT NULL,
  provider VARCHAR(20) NOT NULL CHECK (provider IN ('gmail', 'outlook', 'imap')),
  email_address VARCHAR(255),
  -- IMAP-specific (encrypted at rest)
  imap_host VARCHAR(255),
  imap_port INTEGER DEFAULT 993,
  smtp_host VARCHAR(255),
  smtp_port INTEGER DEFAULT 587,
  username VARCHAR(255),
  encrypted_password BYTEA,  -- encrypted via TOKEN_ENCRYPTION_KEY
  use_tls BOOLEAN DEFAULT true,
  -- Sync
  sync_frequency_minutes INTEGER NOT NULL DEFAULT 15,
  -- Status
  status VARCHAR(20) NOT NULL DEFAULT 'disconnected'
    CHECK (status IN ('connected', 'degraded', 'disconnected')),
  last_sync_at TIMESTAMP WITH TIME ZONE,
  last_error VARCHAR(500),
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

## 5. Component Contracts

### SettingsSectionCard
```typescript
interface SettingsSectionCardProps {
  id: string;              // Anchor ID (e.g., "provider")
  title: string;
  description: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode; // Save/Reset buttons
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error';
  onSave?: () => void;
  onReset?: () => void;
  isDirty?: boolean;       // Show unsaved indicator
}
```

### SettingsNav
```typescript
interface NavSection {
  id: string;
  label: string;
  icon: React.ReactNode;
}

interface SettingsNavProps {
  sections: NavSection[];
  activeSection: string;
  onNavigate: (sectionId: string) => void;
}
```

### SectionStatusBar
```typescript
interface SectionStatusBarProps {
  status: 'idle' | 'saving' | 'saved' | 'error';
  lastSaved?: Date;
  onRetry?: () => void;
}
```

---

## 6. Design Quality

### Visual Direction
- **Aesthetic:** Clean, institutional-grade. Bloomberg meets Linear.
- **Section cards:** `bg-card` with `border`, generous padding (`p-6`)
- **Active nav:** Left border accent (3px primary) + `bg-primary/5` + `text-primary`
- **Danger zone:** `border-destructive/30` + `bg-destructive/5`
- **Info badges:** "Device only" (outline), "Synced" (secondary), "Encrypted" (green outline)

### Micro-interactions
- Smooth anchor scrolling: `scroll-behavior: smooth`
- Nav transition: `transition-all duration-200`
- Save toast: `sonner` toast with check icon
- Status bar: fade transition between states
- Theme switch: immediate class toggle, no flash
- Collapsible advanced settings: animate height

### Copy Style
- M&A-appropriate: precise, professional, no playful microcopy
- Tooltips explain consequences, not just definitions
- Danger zone uses explicit consequences list

---

## 7. Implementation Order

1. **Types & contracts** — `preferences-types.ts` with TypeScript interfaces matching Pydantic models
2. **Scaffold** — File structure, `SettingsSectionCard`, `SettingsNav`, `SectionStatusBar`
3. **Extract Provider** — Move existing code into `ProviderSection.tsx`, verify test connection
4. **Appearance** — Theme toggle + timezone select (localStorage + server for timezone)
5. **Backend** — Alembic migration for `user_preferences` table, GET/PATCH endpoints
6. **Dashboard proxy routes** — `/api/settings/preferences` with `backendFetch()`
7. **useUserPreferences hook** — React Query integration
8. **Agent Config** — Section with save, wired to backend
9. **Notifications** — Section with save, wired to backend
10. **Email Integration** — Section with feature-flag stubs
11. **Data & Privacy** — Retention selector + export + delete dialog
12. **Polish** — Responsive layout, scroll spy, loading skeletons, error boundaries
13. **Validation** — `make validate-local`, Surface 9 check, tsc

---

## 8. Surface 9 Compliance

| Rule | Implementation |
|------|---------------|
| A1: Promise.allSettled | Page bootstrap fetches preferences + email config |
| A2: console.warn for degradation | Backend 404 on email (feature not deployed) |
| A3: CSS architecture | Theme via CSS variables, @layer base |
| A6: Middleware proxy | All new `/api/settings/*` routes use `backendFetch()` |
| A7: Bridge imports | New types in `preferences-types.ts`, not generated files |
| B1-B7: Design quality | Per Section 6 above |

---

## 9. Testing

| Test | Type | Coverage |
|------|------|----------|
| Navigate all 6 sections via sidebar | E2E | Navigation |
| Save agent preferences, reload, verify persistence | E2E | Backend round-trip |
| Theme toggle (system/light/dark) | E2E | Client-side |
| Email section shows feature-unavailable gracefully | E2E | Degradation |
| Timezone saves to backend | E2E | Server persistence |
| useUserPreferences returns defaults when backend down | Unit | Hook resilience |
| Proxy routes return JSON 502 on backend failure | Integration | Error format |
| Section-level save prevents race conditions | Unit | Mutation ordering |
| Keyboard navigation through settings nav | A11y | Accessibility |
| Delete account requires typing "DELETE" | E2E | Security |

---

## 10. Codex Review Items — Disposition

| Codex Finding | Disposition |
|---------------|------------|
| Define user vs org scope | ADOPTED — scope table in Section 1 |
| Provider keys risk | DOCUMENTED — info badge "device only", future phase |
| Section-level save | ADOPTED — replaced auto-save |
| PATCH semantics | ADOPTED — flat merge, explicit in Section 4.2 |
| Route naming mismatch | FIXED — clear mapping table in Section 2.5 |
| Timezone server-side | ADOPTED — persists to backend |
| Browser push defer | ADOPTED — in-app only, noted in non-goals |
| Async data export | PARTIALLY — immediate for now, async noted as future |
| RBAC/CSRF/rate limiting | NOTED — single-user product, defer to security phase |
| Settings search (Cmd+K) | DEFERRED — nice-to-have, not in this phase |
| Audit log in settings | DEFERRED — future enhancement |
| Progressive disclosure | ADOPTED — advanced agent settings in Collapsible |

---

*End of consolidated spec — ready for implementation.*

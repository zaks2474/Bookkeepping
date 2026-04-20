# TriPass Pass 1 — Settings Redesign Spec (Claude)

## 1. Overview

Transform the Settings page from a single AI Provider Configuration card into a comprehensive, anchor-navigated settings hub with 6 sections. The redesign must be full-stack: new React components, new backend API endpoints, new database schema for user preferences, and proper contract surface compliance.

**Current state:** Single `page.tsx` with 537 lines, provider selection + config cards, all localStorage.
**Target state:** Multi-section settings page with sticky sidebar navigation, backend persistence, and 5 new functional areas.

---

## 2. Architecture

### 2.1 Page Layout

```
┌──────────────────────────────────────────────────────┐
│  Settings                                             │
│  Configure your workspace and preferences             │
├─────────────┬────────────────────────────────────────┤
│             │                                        │
│  SIDEBAR    │  CONTENT AREA                          │
│  (sticky)   │                                        │
│             │  ┌──────────────────────────────────┐  │
│  ● Provider │  │  Section Card (scrolls into view)│  │
│  ○ Email    │  │                                  │  │
│  ○ Agent    │  │                                  │  │
│  ○ Notifs   │  └──────────────────────────────────┘  │
│  ○ Data     │                                        │
│  ○ Theme    │  ┌──────────────────────────────────┐  │
│             │  │  Next Section Card               │  │
│             │  │                                  │  │
│             │  └──────────────────────────────────┘  │
│             │                                        │
└─────────────┴────────────────────────────────────────┘
```

- **Layout:** 2-column — sticky sidebar nav (240px) + scrollable content area
- **Navigation:** Anchor-based (`#provider`, `#email`, `#agent`, `#notifications`, `#data`, `#appearance`)
- **Active indicator:** Sidebar highlights current section based on scroll position (IntersectionObserver)
- **Mobile:** Sidebar collapses to horizontal scroll tabs at `md` breakpoint

### 2.2 State Management

```
User Preferences (Backend)
├── Provider settings → localStorage (existing, keep as-is for now)
├── Email integration → backend POST /api/settings/email
├── Agent config → backend PATCH /api/settings/preferences
├── Notifications → backend PATCH /api/settings/preferences
├── Data & privacy → backend endpoints
└── Appearance → localStorage + CSS variables (theme is client-side)
```

**Persistence strategy:**
- Provider config stays in localStorage (existing pattern, works well for local-first architecture)
- All new sections persist to backend via `/api/settings/*` endpoints
- Appearance/theme persists to localStorage (CSS variables are client-side concerns)
- Optimistic updates: save immediately, show success toast, revert on failure

### 2.3 Data Fetching

Per Surface 9 (A1), multi-fetch must use `Promise.allSettled`:

```typescript
// In settings page or a custom hook
const [emailResult, prefsResult] = await Promise.allSettled([
  fetchEmailConfig(),
  fetchUserPreferences(),
]);

const emailConfig = emailResult.status === 'fulfilled' ? emailResult.value : null;
const preferences = prefsResult.status === 'fulfilled' ? prefsResult.value : DEFAULT_PREFERENCES;
```

### 2.4 File Structure

```
apps/dashboard/src/
├── app/settings/
│   ├── page.tsx                    # Main settings page (rewrite)
│   └── layout.tsx                  # Settings layout with sidebar nav
├── components/settings/
│   ├── SettingsNav.tsx             # Sticky sidebar navigation
│   ├── ProviderSection.tsx         # Extract from current page.tsx
│   ├── EmailSection.tsx            # NEW: Email integration
│   ├── AgentSection.tsx            # NEW: Agent configuration
│   ├── NotificationsSection.tsx    # NEW: Notification preferences
│   ├── DataSection.tsx             # NEW: Data & privacy
│   ├── AppearanceSection.tsx       # NEW: Appearance & theme
│   └── SettingsSectionCard.tsx     # Shared section wrapper component
├── hooks/
│   └── useUserPreferences.ts      # NEW: Backend preferences hook
├── lib/settings/
│   ├── provider-settings.ts       # EXISTING: Keep as-is
│   └── preferences-api.ts         # NEW: Backend API client
├── app/api/settings/
│   ├── preferences/route.ts       # NEW: GET/PATCH user preferences
│   ├── email/route.ts             # NEW: Email config CRUD
│   ├── email/test/route.ts        # NEW: Email test connection
│   └── data/export/route.ts       # NEW: Data export
```

---

## 3. Section Specifications

### 3.1 Provider Section (#provider) — REFACTOR

**What changes:** Extract the existing 500-line monolith into a standalone `ProviderSection.tsx` component. No functional changes — pure extraction.

**Component interface:**
```typescript
interface ProviderSectionProps {
  id: string; // "provider" for anchor
}
```

**Behavior:** Identical to current. Provider selection, config cards, test connection. All localStorage.

---

### 3.2 Email Integration (#email) — NEW

**UI Layout:**
```
┌─ Email Integration ──────────────────────────────────┐
│                                                      │
│  Connection Status: ● Connected (zak@company.com)    │
│                     [Disconnect]                     │
│                                                      │
│  ─── OR (if not connected) ───                       │
│                                                      │
│  Connect your email to enable deal-related           │
│  communications and email triage.                    │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Gmail   │  │ Outlook  │  │  IMAP    │          │
│  │  OAuth   │  │  OAuth   │  │  Custom  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
│  (If IMAP selected:)                                 │
│  IMAP Host: [_________________]  Port: [993]         │
│  SMTP Host: [_________________]  Port: [587]         │
│  Username:  [_________________]                      │
│  Password:  [_________________]  🔒                  │
│                                                      │
│  Sync Frequency: [Every 15 minutes ▼]                │
│                                                      │
│  [Test Connection]  [Save & Connect]                 │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Data model:**
```typescript
interface EmailConfig {
  provider: 'gmail' | 'outlook' | 'imap' | null;
  connected: boolean;
  email_address?: string;
  sync_frequency_minutes: 5 | 15 | 30 | 60;
  // IMAP-specific (only when provider === 'imap')
  imap_host?: string;
  imap_port?: number;
  smtp_host?: string;
  smtp_port?: number;
  username?: string;
  // Password never returned from GET, only sent on POST
  last_sync_at?: string; // ISO timestamp
  health_status?: 'healthy' | 'degraded' | 'disconnected';
}
```

**Backend endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/settings/email` | Get current email config (no password) |
| POST | `/api/settings/email` | Connect email (save config) |
| POST | `/api/settings/email/test` | Test email connection |
| DELETE | `/api/settings/email` | Disconnect email |

**Dashboard proxy routes:**
| Method | Path | Proxies to |
|--------|------|-----------|
| GET | `/api/settings/email` | Backend `GET /api/integrations/email` |
| POST | `/api/settings/email` | Backend `POST /api/integrations/email/connect` |
| POST | `/api/settings/email/test` | Backend `POST /api/integrations/email/test` |
| DELETE | `/api/settings/email` | Backend `DELETE /api/integrations/email` |

**Implementation note:** The backend email integration endpoints may not exist yet. If they don't exist, implement graceful stubs that:
1. Return a mock "not configured" state on GET
2. Accept the POST and return success (save to user preferences table)
3. Show a clear "Email integration coming soon" state if backend returns 404

**Surface 9 compliance:**
- `console.warn` if backend returns 404/5xx on GET (expected degradation — feature not deployed)
- `backendFetch()` for all proxy routes (timeout protection)

---

### 3.3 Agent Configuration (#agent) — NEW

**UI Layout:** Reuse the existing `AgentConfigStep` component pattern from onboarding, but adapted for a settings context (no wizard step wrapper, standalone card).

```
┌─ Agent Configuration ────────────────────────────────┐
│                                                      │
│  Enable AI Agent  ──────────────────────── [toggle]  │
│  Let the agent assist with deal analysis              │
│                                                      │
│  ── Approval Mode ──                                  │
│  ○ Manual Everything         [Most Control]           │
│  ● Auto-approve Low Risk     [Recommended]            │
│  ○ Auto-approve Medium Risk  [Faster]                 │
│                                                      │
│  ── Advanced ──                                       │
│  Auto-execute threshold:  ████████░░  70%             │
│  Max concurrent actions:  [5 ▼]                       │
│  Deal matching:           [Medium ▼]                  │
│  Response style:          [Detailed ▼]                │
│                                                      │
│  ── Risk Level Reference ──                           │
│  🟢 Low: Read, search, analyze                        │
│  🟡 Medium: Update profiles, notes, stages            │
│  🔴 High: Send emails, create docs, external          │
│                                                      │
│  [Reset to Defaults]  [Save]                          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Data model:**
```typescript
interface AgentPreferences {
  enabled: boolean;
  auto_approve_level: 'none' | 'low' | 'medium';
  auto_execute_threshold: number; // 0-100
  max_concurrent_actions: number; // 1-20
  deal_matching_strictness: 'strict' | 'medium' | 'loose';
  response_style: 'brief' | 'detailed' | 'verbose';
}
```

**Backend:** Part of unified user preferences endpoint `GET/PATCH /api/settings/preferences`

---

### 3.4 Notification Preferences (#notifications) — NEW

**UI Layout:** Reuse `PreferencesStep` component pattern. Same structure (channels, what-to-notify, digest, quiet hours) but as a settings card rather than onboarding step.

**Data model:** Same as `NotificationPrefs` from onboarding:
```typescript
interface NotificationPreferences {
  email_notifications: boolean;
  browser_notifications: boolean;
  digest_frequency: 'daily' | 'weekly' | 'none';
  approval_alerts: 'all' | 'critical' | 'none';
  deal_stage_changes: boolean;
  agent_activity: boolean;
  quiet_hours: {
    enabled: boolean;
    start: string; // "22:00"
    end: string;   // "08:00"
  };
}
```

**Backend:** Part of unified user preferences endpoint `GET/PATCH /api/settings/preferences`

---

### 3.5 Data & Privacy (#data) — NEW

```
┌─ Data & Privacy ─────────────────────────────────────┐
│                                                      │
│  Completed Action Retention                           │
│  How long to keep completed action records            │
│  [30 days ▼]  (7 days / 30 days / 90 days / Forever) │
│                                                      │
│  ── Data Export ──                                     │
│  Download all your data as a JSON archive             │
│  [Export All Data]                                     │
│                                                      │
│  ── Danger Zone ──                                     │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Delete Account                                  │ │
│  │  Permanently delete your account and all data.  │ │
│  │  This action cannot be undone.                   │ │
│  │                                              [Delete Account] │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Data model:**
```typescript
interface DataPreferences {
  action_retention_days: 7 | 30 | 90 | -1; // -1 = forever
}
```

**Backend endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/settings/data/export` | Trigger data export (returns JSON download) |
| DELETE | `/api/settings/account` | Delete account (requires confirmation) |

**UX:** Delete Account opens an `AlertDialog` requiring the user to type "DELETE" to confirm.

---

### 3.6 Appearance & Theme (#appearance) — NEW

```
┌─ Appearance & Theme ─────────────────────────────────┐
│                                                      │
│  Theme                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  System  │  │  Light   │  │  Dark    │          │
│  │    🖥️   │  │    ☀️   │  │    🌙   │          │
│  │  ● Auto  │  │  ○       │  │  ○       │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
│  Timezone                                             │
│  [America/New_York ▼]                                │
│  Currently: 2:15 PM EST                              │
│                                                      │
│  ── Layout ──                                         │
│  Sidebar default collapsed  ──────────── [toggle]    │
│  Dense mode (compact spacing) ─────────── [toggle]   │
│                                                      │
│  [Save Preferences]                                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Data model:**
```typescript
interface AppearancePreferences {
  theme: 'system' | 'light' | 'dark';
  timezone: string; // IANA timezone
  sidebar_collapsed: boolean;
  dense_mode: boolean;
}
```

**Persistence:** localStorage (theme and layout are client-side concerns).
**Theme implementation:** Use `next-themes` ThemeProvider if installed, or manual class toggle on `<html>` element.

---

## 4. Unified User Preferences API

### 4.1 Backend Schema (New table in zakops database)

```sql
CREATE TABLE IF NOT EXISTS zakops.user_preferences (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) UNIQUE NOT NULL,
  -- Agent config
  agent_enabled BOOLEAN DEFAULT true,
  auto_approve_level VARCHAR(20) DEFAULT 'low',
  auto_execute_threshold INTEGER DEFAULT 70,
  max_concurrent_actions INTEGER DEFAULT 5,
  deal_matching_strictness VARCHAR(20) DEFAULT 'medium',
  response_style VARCHAR(20) DEFAULT 'detailed',
  -- Notifications
  email_notifications BOOLEAN DEFAULT true,
  browser_notifications BOOLEAN DEFAULT true,
  digest_frequency VARCHAR(20) DEFAULT 'daily',
  approval_alerts VARCHAR(20) DEFAULT 'all',
  deal_stage_changes BOOLEAN DEFAULT true,
  agent_activity BOOLEAN DEFAULT true,
  quiet_hours_enabled BOOLEAN DEFAULT false,
  quiet_hours_start VARCHAR(5) DEFAULT '22:00',
  quiet_hours_end VARCHAR(5) DEFAULT '08:00',
  -- Data
  action_retention_days INTEGER DEFAULT 30,
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Backend Endpoints

**GET /api/user/preferences**
- Returns all preferences for authenticated user
- Creates default row if none exists
- Response: `UserPreferencesResponse` Pydantic model

**PATCH /api/user/preferences**
- Partial update — only fields included in body are updated
- Validates enum values
- Returns updated preferences
- Request: `UserPreferencesUpdate` Pydantic model

### 4.3 Dashboard Proxy Routes

```
GET  /api/settings/preferences  →  backendFetch('/api/user/preferences')
PATCH /api/settings/preferences  →  backendFetch('/api/user/preferences', { method: 'PATCH', body })
```

---

## 5. Design Quality (Surface 9 Category B)

### 5.1 Visual Design Direction

**Aesthetic:** Clean, professional, M&A industry-appropriate. Think Bloomberg Terminal meets modern SaaS settings pages (Linear, Vercel, Stripe).

**Color strategy:**
- Section cards use subtle `bg-card` with `border`
- Active nav item uses `bg-primary/10` with `text-primary` and left border accent
- Danger zone uses `border-destructive/20` background
- Status indicators: green (connected/healthy), amber (degraded), red (disconnected/error)

### 5.2 Micro-interactions

- **Section scroll:** Smooth scroll with `scroll-behavior: smooth` and `scroll-margin-top` for header offset
- **Nav highlight:** Sidebar active state transitions with `transition-colors duration-200`
- **Save feedback:** Toast notification on save (success/error) using existing `sonner` toast
- **Toggle animations:** Switch components already have built-in transitions
- **Danger zone:** Delete button requires typing "DELETE" — input border turns red as user types, green when match

### 5.3 Responsive Behavior

- **Desktop (≥1024px):** 2-column layout, sticky sidebar
- **Tablet (768-1023px):** Sidebar collapses to horizontal tabs above content
- **Mobile (<768px):** Full-width sections, dropdown nav or accordion

---

## 6. Component Contracts

### 6.1 SettingsSectionCard (shared wrapper)

```typescript
interface SettingsSectionCardProps {
  id: string;           // Anchor ID
  title: string;        // Section heading
  description: string;  // Subtitle
  icon: React.ReactNode;
  children: React.ReactNode;
  actions?: React.ReactNode; // Footer buttons (Save, Reset, etc.)
}
```

### 6.2 SettingsNav (sidebar)

```typescript
interface SettingsNavProps {
  sections: Array<{
    id: string;
    label: string;
    icon: React.ReactNode;
  }>;
  activeSection: string;
}
```

Uses `IntersectionObserver` to detect which section is in viewport and updates active state.

---

## 7. Implementation Order

1. **Scaffold:** Create file structure, `SettingsSectionCard`, `SettingsNav`, new `page.tsx` layout
2. **Extract Provider:** Move existing provider config into `ProviderSection.tsx` (zero functional change)
3. **Appearance:** Theme toggle + timezone (client-side, no backend needed)
4. **Backend:** Create `user_preferences` table + `GET/PATCH /api/user/preferences` endpoints
5. **Agent Config:** Build section, wire to backend preferences
6. **Notifications:** Build section, wire to backend preferences
7. **Email Integration:** Build section with graceful stubs
8. **Data & Privacy:** Build section with export + delete flows
9. **Polish:** Responsive layout, scroll spy, toasts, loading states

---

## 8. Surface 9 Compliance Checklist

- [ ] `Promise.allSettled` for multi-fetch (loading email config + preferences simultaneously)
- [ ] `console.warn` for expected degradation (backend 404 on email endpoints)
- [ ] Bridge file imports only (`@/types/api`)
- [ ] `backendFetch()` for all new proxy routes
- [ ] Error boundaries around each section (section failure doesn't break page)
- [ ] No hardcoded stage arrays (not applicable here, but verify)
- [ ] Middleware proxy pattern for new `/api/settings/*` routes
- [ ] JSON 502 on backend failure, never HTML 500

---

## 9. Testing Plan

- E2E: Navigate all 6 sections via sidebar
- E2E: Save agent preferences, reload, verify persistence
- E2E: Theme toggle works (system/light/dark)
- E2E: Email section shows "not configured" gracefully
- Unit: `useUserPreferences` hook returns defaults when backend unavailable
- Contract: New proxy routes return proper error format

---

## 10. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Backend preferences endpoint doesn't exist | Graceful fallback to defaults; stub endpoint if needed |
| Email OAuth flow complex | Start with IMAP/stub; OAuth is future enhancement |
| Page becomes too long | Anchor nav + scroll spy keeps UX manageable |
| Theme flicker on load | Use `next-themes` suppressHydrationWarning pattern |
| Breaking existing provider settings | Extract as-is first, verify test connection still works |

# Interaction Wiring Inventory — UI-MASTERPLAN-M00 (F-8)

**Purpose:** Map every visible control to: `real endpoint`, `mock`, `placeholder`, or `broken`.

**Legend:**
- **Real** = Wired to a live backend endpoint that returns real data
- **Mock** = Returns hardcoded/placeholder data but endpoint exists
- **Placeholder** = UI control exists but endpoint returns 404 or is not implemented
- **Broken** = Control fails silently or throws error on interaction
- **Client-only** = Operates purely in the browser (no backend call)

---

## 1. Dashboard (`/dashboard`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Toggle Sidebar | button | Client-only | Collapses/expands sidebar |
| Search deals... (Cmd+K) | button | Client-only | Opens search modal |
| Notification bell | button | Placeholder | Always disabled, no tooltip |
| User avatar | button | Client-only | Opens user menu |
| Toggle theme | button | Client-only | Switches light/dark mode |
| Approvals | button | Real | Filters Today & Next Up to approvals |
| Refresh | button | Real | Re-fetches dashboard data (disabled during load) |
| Today & Next Up deal cards | link | Real | Navigate to `/deals/[id]` |
| Pipeline stage badges | static | Real | Server-side counts from `/api/deals` |
| View all (All Deals) | link | Real | Navigate to `/deals` |
| Ask Agent | button | Real | Opens agent chat interface |
| View All (Agent Activity) | link | Real | Navigate to `/agent/activity` |
| Execution Inbox tabs (All/Approvals/Ready/Failed/Quarantine) | tabs | Real | Filters inbox items |
| Execution Inbox filter comboboxes | combobox | Real | Filters by type/status |
| View all (Quarantine) | link | Real | Navigate to `/quarantine` |

## 2. Deals List (`/deals`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Toggle Sidebar | button | Client-only | |
| Search deals... (Cmd+K) | button | Client-only | |
| Table / Board tabs | tabs | Client-only | Switches view mode |
| New Deal | link | Real | Navigate to `/deals/new` |
| Refresh | button | Real | Re-fetches deals (disabled during load) |
| Search deals (page-level) | textbox | Real | Filters deal list client-side |
| All stages dropdown | combobox | Real | Filters by stage |
| Status dropdown (active) | combobox | Real | Filters by status |
| Deal Name column header | sortable | Real | Client-side sort |
| Deal row | link | Real | Navigate to `/deals/[id]` |
| Delete (trash icon) | button | Real | Deletes deal via API |
| Select all checkbox | checkbox | Client-only | Batch selection |
| Per-row checkbox | checkbox | Client-only | Row selection |
| Last Update sort toggle | button | Client-only | Sort direction |

## 3. Deal Workspace (`/deals/DL-0020`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Back to Deals | button | Client-only | Navigate to `/deals` |
| Add Note | button | Real | Opens note creation dialog |
| Chat | link | Real | Navigate to `/chat?deal_id=DL-0020` |
| Refresh | button | Real | Re-fetches deal data |
| Overview tab | tab | Real | Shows deal info (loaded) |
| Actions tab | tab | Real | Shows deal actions |
| Pipeline tab | tab | Real | Shows pipeline visualization |
| Materials tab | tab | Placeholder | Returns 404 from `/api/deals/DL-0020/materials` |
| Case File tab | tab | Placeholder | Returns 404 from `/api/deals/DL-0020/case-file` |
| Events tab | tab | Real | Shows 9 events |
| Stage Transitions panel | static | Real | Shows "No transitions available (terminal stage)" |
| View All Actions | link | Real | Navigate to `/actions?deal_id=DL-0020` |

## 4. Actions (`/actions`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Clear dropdown | button | Real | Clears completed/failed actions |
| Refresh | button | Real | Re-fetches actions |
| New Action | button | Real | Opens action creation flow |
| Search actions | textbox | Real | Filters action list |
| All types dropdown | combobox | Real | Filters by action type |
| Status filter combobox | combobox | Real | Filters by status |
| Tab bar (All/Pending Approval/Ready/Processing/Completed/Failed) | tabs | Real | Filters by status category |
| Pending Approval stat card | static | Real | Count from API |
| Processing stat card | static | Real | Count from API |
| 24h Success Rate stat card | static | Real | Computed from API |
| Failed (24h) stat card | static | Real | Count from API |

## 5. Chat (`/chat`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Settings gear icon | link | Real | Navigate to `/settings` |
| Global/deal scope dropdown | combobox | Client-only | Filters chat context |
| Deal filter dropdown | combobox | Real | Filters to specific deal |
| History | button | Real | Shows chat history |
| New Chat | button | Client-only | Clears current chat |
| Evidence | button | Real | Shows evidence panel |
| Debug | button | Client-only | Shows debug info |
| Ask a question textbox | textbox | Real | Sends message to RAG/vLLM via `/api/chat` |
| Send button | button | Real | Submits chat message (disabled when empty) |
| Local vLLM (Qwen) indicator | static | Real | Shows connection status (green dot = connected) |

## 6. Quarantine (`/quarantine`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Refresh | button | Real | Re-fetches quarantine queue |
| Queue item list | list | Real | Items from `/api/quarantine` |
| Clear | button | Real | Clears selection (disabled when nothing selected) |
| Reject | button | Real | Rejects quarantine item (disabled when nothing selected) |
| Approve | button | Real | Approves quarantine item → creates deal (disabled when nothing selected) |
| Operator textbox | textbox | Client-only | Sets operator name for action attribution |
| Reject reason textbox | textbox | Client-only | Optional reject reason |

## 7. Agent Activity (`/agent/activity`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Idle status indicator | static | Real | From agent API status |
| Refresh | button | Real | Re-fetches activity |
| Tools Called Today stat | static | Real | Count from API |
| Approvals Processed stat | static | Real | Count from API |
| Deals Analyzed stat | static | Real | Count from API |
| Runs (24h) stat | static | Real | Count from API |
| Search activity | textbox | Real | Filters activity list |
| Tab bar (All Activity/Deals/Documents/Communications/Approvals) | tabs | Real | Filters by category |
| Activity list items | list | Real | Clickable activity entries |
| Recent Runs panel | static | Real | Shows "No runs found" when empty |

## 8. Operator HQ (`/hq`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Refresh | button | Real | Re-fetches HQ data |
| Active Deals stat card | button | Real | Clickable, shows deal count + trend |
| Pending Approvals stat card | button | Real | Clickable |
| Quarantine stat card | button | Real | Clickable |
| Events (24h) stat card | button | Real | Clickable |
| Pipeline / Approvals / Activity tabs | tabs | Real | Switches HQ view |
| Pipeline stage links (Inbound, Screening, etc.) | link | Real | Navigate to `/deals?stage=<stage>` |
| Pipeline Flow bar chart | static | Real | Visualization from API data |
| View All Deals | link | Real | Navigate to `/deals` |
| Review Quarantine | link | Real | Navigate to `/quarantine` |

## 9. Settings (`/settings`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Back to Dashboard | link | Real | Navigate to `/dashboard` |
| Section nav (AI Provider, etc.) | combobox | Client-only | Scrolls to section |
| AI Provider radio group (vLLM/OpenAI/Anthropic/Custom) | radio | Client-only | Selects provider |
| Endpoint URL textbox | textbox | Client-only | Stored in localStorage |
| Model combobox | combobox | Client-only | Selects model |
| Test Connection | button | Real | Tests AI provider endpoint |
| Reset to Defaults (AI) | button | Client-only | Resets to default values |
| Save (AI) | button | Placeholder | Disabled — `/api/settings/preferences` returns 404 |
| Email Integration section | static | Placeholder | Shows "not available" — `/api/settings/email` returns 404 |
| Enable AI Agent switch | switch | Client-only | Toggles agent |
| Approval Mode radio group | radio | Client-only | Sets approval level |
| Advanced Settings | button | Client-only | Expands advanced options |
| Save (Agent) | button | Placeholder | Disabled — backend 404 |
| Email Notifications switch | switch | Client-only | Toggle |
| In-App Notifications switch | switch | Client-only | Toggle |
| Approval Alerts radio group | radio | Client-only | Sets alert level |
| Deal Stage Changes switch | switch | Client-only | Toggle |
| Agent Activity switch | switch | Client-only | Toggle |
| Activity Digest radio group | radio | Client-only | Sets digest frequency |
| Quiet Hours switch | switch | Client-only | Toggle |
| Save (Notifications) | button | Placeholder | Disabled — backend 404 |
| Completed Action Retention combobox | combobox | Client-only | Sets retention period |
| Export All Data | button | Placeholder | No backend endpoint confirmed |
| Delete Account | button | Placeholder | Danger zone — no backend endpoint confirmed |
| Theme buttons (System/Light/Dark) | button | Client-only | Toggles theme |
| Timezone combobox | combobox | Client-only | Sets timezone |
| Sidebar Collapsed switch | switch | Client-only | Layout preference |
| Dense Mode switch | switch | Client-only | Layout preference |
| Save (Appearance) | button | Placeholder | Disabled — backend 404 |

## 10. Onboarding (`/onboarding`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Step indicators (1-6) | button | Client-only | Navigate between onboarding steps |
| Resume | button | Client-only | Resumes from saved step (localStorage) |
| Start Fresh | button | Client-only | Resets onboarding progress |
| Dismiss resume banner (X) | button | Client-only | Closes banner |
| Feature cards (Smart Email Triage, AI-Powered Agent, etc.) | button | Client-only | Shows feature detail |
| Skip Setup | button | Client-only | Skips to dashboard |
| Continue | button | Client-only | Advances to next step |

## 11. New Deal (`/deals/new`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| Back to Deals | button | Client-only | Navigate to `/deals` |
| Deal Name textbox | textbox | Client-only | Required field |
| Display Name textbox | textbox | Client-only | Optional field |
| Initial Stage combobox | combobox | Client-only | Defaults to "inbound" |
| Create Deal | button | Real | POST to `/api/deals` (disabled until name filled) |
| Cancel | button | Client-only | Navigate to `/deals` |

## 12. Home redirect (`/`)

| Control | Type | Wiring Status | Endpoint/Notes |
|---------|------|---------------|----------------|
| (redirect only) | redirect | Real | 307 redirect to `/dashboard` |
| (same as Dashboard) | — | — | See Dashboard inventory above |

---

## Wiring Summary

| Status | Count | Percentage |
|--------|-------|-----------|
| Real endpoint | ~65 | ~52% |
| Client-only | ~48 | ~38% |
| Placeholder | ~10 | ~8% |
| Mock | 0 | 0% |
| Broken | 0 | 0% |

## Key Placeholder Controls (Require Backend Integration)
1. Settings — Save buttons (AI, Agent, Notifications, Appearance) — all disabled due to 404
2. Settings — Email Integration — 404, shows "not available" banner
3. Settings — Export All Data / Delete Account — no confirmed backend
4. Deal Workspace — Materials tab — 404
5. Deal Workspace — Case File tab — 404
6. Global — Notification bell — always disabled

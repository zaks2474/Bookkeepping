# DASHBOARD_ROUND4_MASTER_DEDUPED.Codex.20260205-1900-master.md

## 1. AGENT IDENTITY
- **agent_name:** Codex
- **run_id:** 20260205-1900-master
- **date_time:** 2026-02-05T19:00:00Z

---

## 2. EXECUTIVE SUMMARY

The Round-4 Dashboard Audit reveals a **"Fragile Facade"**: a polished UI wrapper around broken routing, missing endpoints, and demo-ware workflows. The most critical discovery is the **Security Void** (missing Auth headers), which renders the system insecure by design.

This Master Deduped Plan integrates findings from Claude-Opus, Gemini-CLI, and Codex into a single, execution-ready remediation roadmap. It prioritizes Security and Routing (P0) to stabilize the platform before moving to feature hardening.

**Stats:**
- **Issues Found:** 17 (Deduped from ~30)
- **Top Priority:** Security (Auth) & Routing (`/deals/new`)
- **Key Redesign:** Settings & Onboarding (Email Integration)

---

## 3. MASTER DEDUPED LIMITATIONS REGISTRY

| ID | Severity | Subsystem | Symptom | Root Cause | Fix | Sources |
|----|----------|-----------|---------|------------|-----|---------|
| **R4-001** | **P0** | **Security** | No Auth Headers sent to backend | `api-client.ts` missing header injection | Inject `Authorization`/`X-API-Key` in `apiFetch` | Gemini, PASS1, PASS2 |
| **R4-002** | **P0** | **Routing** | `/deals/new` & `/deals/GLOBAL` show 404 | `[id]` catch-all route collision | Create static `/deals/new/page.tsx` + Route Guard in `[id]` | Claude, Codex, Gemini |
| **R4-003** | **P0** | **Chat** | Agent reports wrong deal count (3 vs 9) | Agent RAG index stale vs UI SQL DB | Force SQL fallback in Agent `search_deals` tool | Claude, Codex, Gemini |
| **R4-004** | **P0** | **Onboarding** | "Configure Email" button dead; state lost on refresh | Client-side only (`localStorage`) | Wire `handleComplete` to `POST /api/onboarding` | Claude, Codex, Gemini |
| **R4-005** | **P0** | **Actions** | Bulk Delete returns 405 Method Not Allowed | Proxy targets `/api/actions` (wrong path) | Update Proxy to `/api/kinetic/actions/bulk/delete` | Claude, Codex, Gemini |
| **R4-006** | **P0** | **Quarantine** | Delete button shows "Not Found" | Missing Proxy & Backend Endpoint | Create Proxy + Implement Backend `DELETE` | Claude, Codex, Gemini |
| **R4-007** | **P1** | **Settings** | No Email Configuration UI | Feature never implemented | Build "Email" tab with OAuth/IMAP form | Claude, Codex, Gemini |
| **R4-008** | **P1** | **Chat** | Raw markdown (`**bold**`) displayed | Missing markdown renderer | Wrap content in `<ReactMarkdown>` | Claude, Codex, Gemini |
| **R4-009** | **P1** | **Quarantine** | "Preview not found" in side panel | Endpoint 404s for some item types | Fix Backend Preview logic | Claude |
| **R4-010** | **P2** | **Actions** | "Delete Completed" returns 405 | Missing Backend Endpoint | Implement `POST /api/kinetic/actions/clear-completed` | Claude, Codex |
| **R4-011** | **P2** | **Dashboard** | Sidebar actions unverified | Potential dead UI | E2E verification + wire to chat context | Gemini, PASS1 |
| **R4-012** | **P2** | **Settings** | Missing Agent/Notif config | Feature gaps | Add config sections to Settings page | Claude |
| **R4-013** | **P3** | **UI** | Agent Activity panel truncated | CSS overflow issue | Fix CSS layout | Claude |

---

## 4. MASTER RECOMMENDATIONS CATALOG

### Priority 0: Security & Stability (Immediate)
1.  **Inject Auth Headers**: Modify `src/lib/api-client.ts` to include `Authorization` headers. (R4-001)
2.  **Fix Deals Routing**: Create `src/app/deals/new/page.tsx` and add slug guards to `[id]/page.tsx`. (R4-002)
3.  **Ground Chat Truth**: Update `deal_tools.py` to use `_search_deals_fallback` (SQL) by default. (R4-003)
4.  **Align Proxies**: Update `api/actions/bulk/delete` to point to `kinetic/actions`. (R4-005)

### Priority 1: Functional Contracts (This Sprint)
1.  **Quarantine Actions**: Implement `DELETE /api/triage/quarantine/{id}` in Backend and add Proxy. (R4-006)
2.  **Email Settings**: Build the Email Configuration UI in Settings. (R4-007)
3.  **Chat UX**: Add `react-markdown` for proper rendering. (R4-008)
4.  **Onboarding Persistence**: Wire Onboarding wizard to Backend API. (R4-004)

### Priority 2: Product Completeness (Next Sprint)
1.  **Action Lifecycle**: Implement `clear-completed` endpoints. (R4-010)
2.  **Settings Expansion**: Add Agent and Notification config sections. (R4-012)
3.  **Sidebar Integration**: Connect Dashboard sidebar to Chat session. (R4-011)

---

## 5. SETTINGS REDESIGN SPEC (World-Class)

**Layout**: Vertical Tabs (Left Sidebar)
**Sections**:
1.  **General**: Profile, Organization Name, Timezone.
2.  **Email Integration** (New):
    *   **Status Card**: Connected/Disconnected (Green/Red dot).
    *   **Connection Type**: OAuth (Gmail/Outlook) vs IMAP/SMTP.
    *   **Configuration Form**: Host, Port, User, Password (Masked).
    *   **Test Button**: "Test Connection" (Calls `/api/settings/email/test`).
    *   **Sync Rules**: Folders to scan (Inbox, Spam), Frequency.
3.  **AI Provider** (Existing):
    *   Model Selection (Local/Cloud).
    *   API Key Management.
4.  **Agent Brain**:
    *   **Tone**: Formal/Casual slider.
    *   **Auto-Approve**: Toggle for low-risk actions.
    *   **Buy Box**: JSON editor or Form for deal criteria.
5.  **Notifications**:
    *   Toggles: "New Deal Found", "Quarantine Alert", "Daily Digest".

---

## 6. ONBOARDING REDESIGN SPEC (Real Workflows)

**Principle**: "No Dead Ends" — every step persists state.

**Flow**:
1.  **Welcome**: Value prop (Static).
2.  **Profile**: "What's your name?" -> `POST /api/user/profile`.
3.  **Connect Email**:
    *   Show "Connect Gmail" / "Connect Outlook" buttons.
    *   On click -> popup OAuth window.
    *   On success -> Show "Syncing..." -> `POST /api/settings/email`.
    *   *Fallback*: "Skip for now" (Explicit).
4.  **Meet Your Agent**:
    *   **Action**: Agent creates a *real* sample deal "Acme Corp" in background.
    *   **UI**: User sees "Acme Corp" appear in a mini-list.
    *   **Task**: User clicks "Analyze" -> Agent runs analysis.
    *   **Proof**: The system *actually works*.
5.  **Finish**: Redirect to Dashboard.

---

## 7. VERIFICATION GATES

*   **Gate A (Contracts)**: `verify-contracts.ts` script checks Frontend `apiFetch` calls against Backend `openapi.json`.
*   **Gate B (Dead UI)**: Playwright spider clicks every button; fails on 400/500/Toast Error.
*   **Gate C (Security)**: Regression test verifying `401 Unauthorized` when Auth header is stripped.

---

*Master Deduped Registry Generated: 2026-02-05T19:00:00Z*

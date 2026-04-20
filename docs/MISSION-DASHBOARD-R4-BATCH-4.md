# CLAUDE CODE MISSION: DASHBOARD ROUND 4 — BATCH 4: SETTINGS REDESIGN (FULL SPEC)
## Mission ID: DASHBOARD-R4-BATCH-4
## Codename: "Control Plane"
## Priority: P1
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Build everything, verify everything

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   EXECUTION DIRECTIVE                                                        ║
║                                                                              ║
║   This batch implements the full Settings Redesign spec:                     ║
║   - Email Integration (IMAP/OAuth)                                           ║
║   - Agent Configuration                                                      ║
║   - Notification Preferences                                                 ║
║   - Data & Privacy                                                           ║
║   - Appearance & Theme                                                       ║
║   - Fix provider test connection & persist settings to backend               ║
║                                                                              ║
║   Outcome: Settings becomes a real control plane with persistence.           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## CONTEXT
- Depends on Batch 0 (auth + Playwright), Batch 3 (Test Connection fix if not done).
- Primary source: /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md (Settings Redesign Spec).
- Backend repo is expected at `/home/zaks/zakops-backend`. If missing, locate with:
  ```bash
  find /home/zaks -maxdepth 4 -type d -name "zakops-backend" 2>/dev/null
  ```

---

## SECTION 0: PREFLIGHT VERIFICATION
Evidence directory:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-4/evidence/`

```bash
BASE_EVIDENCE=/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-4/evidence
mkdir -p "$BASE_EVIDENCE/preflight" "$BASE_EVIDENCE/rec-008" "$BASE_EVIDENCE/settings" "$BASE_EVIDENCE/playwright"

# Service health
curl -s http://localhost:8091/health | tee "$BASE_EVIDENCE/preflight/01-backend-health.json"

# Settings page reachable
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003/settings | tee "$BASE_EVIDENCE/preflight/02-settings-status.txt"

# Check if backend has existing settings/preferences endpoints
curl -s http://localhost:8091/openapi.json | jq '.paths | keys[]' | tee "$BASE_EVIDENCE/preflight/03-openapi-paths.txt"

# Confirm API key in dashboard env
rg -n "ZAKOPS_API_KEY" /home/zaks/zakops-agent-api/apps/dashboard/.env.local | tee "$BASE_EVIDENCE/preflight/04-api-key-present.txt"
```

If backend health fails, fix before proceeding.

---

## FIX 1 (P1): REC-008 — Add Email Integration Section
**Source text (verbatim):** “Add Email Configuration section with IMAP/SMTP/OAuth fields”

### Step 1A: Implement Settings UI sections & anchors
File: `apps/dashboard/src/app/settings/page.tsx`
Required anchor layout (verbatim spec):
```
/settings
├── /settings#provider      (AI Provider Configuration) — EXISTING
├── /settings#email         (Email Integration) — NEW
├── /settings#agent         (Agent Configuration) — NEW
├── /settings#notifications (Notification Preferences) — NEW
├── /settings#data          (Data & Privacy) — NEW
└── /settings#appearance    (Appearance & Theme) — NEW
```

Add a left-side section nav (or top tabs) that jumps to each anchor.

### Step 1B: Email Integration fields + actions
Implement the Email Integration form using the spec:
- Connection Type (oauth/imap)
- OAuth Provider (Google/Microsoft)
- IMAP Host/Port, SMTP Host/Port, Username, Password
- Sync Frequency
- Buttons: Connect, Test Connection, Disconnect
- Status table: account email, provider icon, last sync, health status, disconnect

### Step 1C: Hook to backend endpoints
Backend endpoints required:
- `POST /api/integrations/email/connect`
- `POST /api/integrations/email/test`
- `DELETE /api/integrations/email`

If OAuth is not implemented, stub with clear `// STUB:` comment and return `202` + `pending` status.

### Verification
```bash
# Connect (IMAP stub allowed)
curl -i -X POST http://localhost:8091/api/integrations/email/connect \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"connection_type":"imap","imap_host":"imap.gmail.com","imap_port":993,"smtp_host":"smtp.gmail.com","smtp_port":587,"username":"test@example.com","password":"test","sync_frequency":"15min"}' \
  | tee "$BASE_EVIDENCE/rec-008/01-email-connect.txt"

# Test
curl -i -X POST http://localhost:8091/api/integrations/email/test \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"test":true}' | tee "$BASE_EVIDENCE/rec-008/02-email-test.txt"

# Disconnect
curl -i -X DELETE http://localhost:8091/api/integrations/email \
  -H "X-API-Key: $ZAKOPS_API_KEY" | tee "$BASE_EVIDENCE/rec-008/03-email-disconnect.txt"
```

```
GATE 1:
- Email Integration section renders
- Connect/Test/Disconnect return 200/202 (not 404/405)
```

---

## FIX 2 (P1): Agent Configuration + Notification + Data + Appearance Sections
**Source text (verbatim):** “Add Agent Configuration section (core functionality)”

### Step 2A: Implement Agent Configuration UI
Spec fields:
- Auto-execute Threshold (slider)
- Max Concurrent Actions (number)
- Deal Matching Strictness (select)
- Enrichment Sources (multi-select)
- Response Style (select)

### Step 2B: Implement Notification Preferences UI
Spec fields:
- Email Notifications (toggle)
- Browser Notifications (toggle)
- Digest Frequency (select)
- Notify on: New Deals, Pending Approvals, Completed Actions (toggles)

### Step 2C: Implement Data & Privacy UI
Spec fields:
- Completed Action Retention (select)
- Export All Data (button)
- Delete Account (button + confirm)

### Step 2D: Implement Appearance & Theme UI
Spec fields:
- Theme (select)
- Sidebar Collapsed (toggle)
- Dense Mode (toggle)
- Timezone (select)

### Verification
Manual UI review: sections visible, consistent, and field values persist after save.

```
GATE 2:
- All 6 sections render under /settings
- Each section has its specified fields
```

---

## FIX 3 (P1): Backend Preferences Persistence (UserSettings Model)
**Source text (verbatim):**
```python
class UserSettings(BaseModel):
    user_id: str
    email_config: Optional[EmailConfig]  # Encrypted
    agent_preferences: AgentPreferences
    notification_preferences: NotificationPreferences
    data_preferences: DataPreferences
    appearance: AppearancePreferences
    updated_at: datetime
```

### Step 3A: Add backend model + storage
Backend repo (expected): `/home/zaks/zakops-backend/src`

Search for existing settings models:
```bash
rg -n "UserSettings|preferences|settings" /home/zaks/zakops-backend/src | tee "$BASE_EVIDENCE/settings/01-backend-scan.txt"
```

If none exist:
- Create `models/user_settings.py` with `UserSettings` and nested schemas.
- Add DB table `user_settings` with JSONB columns for each preference group.
- Add migrations if backend uses Alembic (or matching system).

### Step 3B: Add backend endpoints
Required endpoints:
- `GET /api/user/preferences` — returns UserSettings
- `PATCH /api/user/preferences` — updates settings

Use X-API-Key auth for writes.

### Step 3C: Add Next API proxy routes
Add in dashboard:
- `apps/dashboard/src/app/api/user/preferences/route.ts`
  - GET: proxy to backend
  - PATCH: proxy to backend (use backendHeaders())

### Verification
```bash
# Read prefs
curl -s http://localhost:8091/api/user/preferences | tee "$BASE_EVIDENCE/settings/02-get-preferences.json"

# Update prefs
curl -i -X PATCH http://localhost:8091/api/user/preferences \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent_preferences":{"auto_execute_threshold":0.7,"max_concurrent_actions":5,"deal_matching_strictness":"medium","enrichment_sources":["web"],"response_style":"detailed"}}' \
  | tee "$BASE_EVIDENCE/settings/03-patch-preferences.txt"
```

```
GATE 3:
- GET /api/user/preferences returns JSON with all sections
- PATCH updates values and persists across refresh
```

---

## FIX 4 (P1): Wire Settings UI to Backend Persistence
**Source text (verbatim):** “Add Email Configuration section with IMAP/SMTP/OAuth fields” (REC-008)

### Step 4A: Replace localStorage-only provider settings
File: `apps/dashboard/src/lib/settings/provider-settings.ts`
- If using localStorage only, add backend sync:
  - On load: fetch `/api/user/preferences` and hydrate UI.
  - On save: PATCH `/api/user/preferences` with updated settings.
- Keep localStorage as fallback only if backend unreachable.

### Step 4B: Ensure Save + Test Connection are consistent
- Save must persist to backend first, then run Test Connection.
- “Test Connection” must not use GET if backend only supports POST.

### Verification
```bash
# Save settings via UI and confirm GET shows new values
curl -s http://localhost:8091/api/user/preferences | tee "$BASE_EVIDENCE/settings/04-preferences-after-save.json"
```

```
GATE 4:
- Settings save persists to backend (refresh page shows same values)
- Test Connection works without 405
```

---

## PLAYWRIGHT VERIFICATION (REQUIRED)
Create Playwright test: `apps/dashboard/tests/e2e/settings.spec.ts`

Test cases:
1. Navigate `/settings` and verify all section anchors exist.
2. Switch to Email Integration and fill IMAP fields; click Connect (expect success toast).
3. Toggle Notification Preferences and save; reload and confirm persisted.

Run:
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard
npx playwright test tests/e2e/settings.spec.ts | tee "$BASE_EVIDENCE/playwright/01-settings.txt"
```

```
GATE 5:
- Playwright settings test passes
```

---

## VERIFICATION SEQUENCE
After all fixes:
```bash
# Gate 1
cat "$BASE_EVIDENCE/rec-008/01-email-connect.txt"
cat "$BASE_EVIDENCE/rec-008/02-email-test.txt"
cat "$BASE_EVIDENCE/rec-008/03-email-disconnect.txt"
# Gate 3
cat "$BASE_EVIDENCE/settings/02-get-preferences.json"
cat "$BASE_EVIDENCE/settings/03-patch-preferences.txt"
# Gate 4
cat "$BASE_EVIDENCE/settings/04-preferences-after-save.json"
# Gate 5
cat "$BASE_EVIDENCE/playwright/01-settings.txt"
```

---

## AUTONOMY RULES
- If backend endpoints are missing, implement them.
- If DB migrations are required, create them and document.
- If OAuth is not implemented, stub with clear `// STUB:` comment and 202 response.
- Do not stop unless infrastructure blocks all fixes.

---

## OUTPUT FORMAT
Save completion report:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-4/completion-report.md`

Template:
```
# DASHBOARD-R4 BATCH 4 — COMPLETION REPORT

## Summary
| Fix | Status | Evidence |
|-----|--------|----------|
| REC-008 Email Integration | PASS/FAIL | path(s) |
| Settings Sections (6) | PASS/FAIL | path(s) |
| Preferences backend | PASS/FAIL | path(s) |
| UI persistence | PASS/FAIL | path(s) |
| Playwright test | PASS/FAIL | path(s) |

## Gates
| Gate | Result | Evidence |
|------|--------|----------|
| Gate 1 | PASS/FAIL | rec-008/* |
| Gate 2 | PASS/FAIL | settings section screenshots |
| Gate 3 | PASS/FAIL | settings/02-03 |
| Gate 4 | PASS/FAIL | settings/04 |
| Gate 5 | PASS/FAIL | playwright/01-settings.txt |

## Blockers
- ...

## Notes
- ...
```

---

## HARD RULES
- All write endpoints must require X-API-Key.
- Any new backend endpoints must appear in OpenAPI.
- No mock-only UI paths in Settings after this batch (unless explicitly marked STUB).
- Evidence artifacts are mandatory.

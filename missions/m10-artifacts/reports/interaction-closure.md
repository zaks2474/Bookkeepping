# M10 Interaction Closure Matrix

## /settings

| Control | 375px | 768px | 1280px | Status |
|---------|-------|-------|--------|--------|
| Back to Dashboard link | visible | visible | visible | real |
| Section nav dropdown | visible, full-width above content | visible, full-width | hidden (sidebar) | real |
| Section nav sidebar | hidden | hidden | visible, sticky | real |
| AI Provider card | visible, full-width | visible | visible | real (localStorage) |
| Provider radio buttons | visible | visible | visible | real (localStorage) |
| Test Connection button | visible | visible | visible | real (localStorage) |
| Email Integration card | visible | visible | visible | degraded (404 → "not available" alert) |
| Agent Configuration card | visible | visible | visible | real (defaults, save echoes on 404) |
| Agent Enable toggle | visible | visible | visible | real |
| Approval mode radios | visible | visible | visible | real |
| Advanced settings collapse | visible | visible | visible | real |
| Notifications card | visible (scroll) | visible (scroll) | visible (scroll) | real (defaults) |
| Data & Privacy card | visible (scroll) | visible (scroll) | visible (scroll) | real |
| Retention selector | visible | visible | visible | real |
| Export Data button | visible | visible | visible | degraded (backend 502) |
| Delete Account button | visible | visible | visible | degraded (backend 502, confirmation dialog works) |
| Appearance card | visible (scroll) | visible (scroll) | visible (scroll) | real (localStorage) |
| Theme selector | visible | visible | visible | real (localStorage) |
| Timezone selector | visible | visible | visible | real |

### F-15 Disposition
Settings uses an intentionally distinct layout (no main sidebar, section-scoped nav). Accepted as deliberate design with mobile stacking fix applied. See `f15-layout-disposition.md`.

### F-16 Disposition
- Duplicate preferences fetch: StrictMode dev artifact (non-issue in production)
- 404 on email: Correct feature-flag behavior → "not available" alert
- 404 on preferences: Correct fallback to defaults
- See `settings-fetch-behavior.md` for full classification

---

## /deals/new

| Control | 375px | 768px | 1280px | Status |
|---------|-------|-------|--------|--------|
| Back (← Deals) button | visible | visible | visible | real |
| Card title "Create New Deal" | visible | visible | visible | real |
| Deal Name input | visible, full-width | visible | visible | real (required) |
| Display Name input | visible, full-width | visible | visible | real (optional) |
| Initial Stage selector | visible | visible | visible | real (defaults to inbound) |
| Create Deal button | visible, disabled when empty | visible | visible | real |
| Cancel button | visible | visible | visible | real (navigates to /deals) |

### Create-Flow Reliability
- Empty name: Submit disabled (client-side validation)
- Valid name: Submit enabled, POST to `/api/deals`, toast success, redirect to deal page
- API error: toast.error with message, form remains editable for retry
- Cancel: navigates to /deals list

---

## Coverage Summary
- **Total controls mapped:** 26
- **Real:** 22
- **Degraded:** 4 (email integration, export, delete account, preferences save persistence)
- **Hidden:** 0
- **Coverage:** 100%

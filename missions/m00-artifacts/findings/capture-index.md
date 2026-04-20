# Capture Index — UI-MASTERPLAN-M00

## Capture Metadata
- **Date:** 2026-02-11
- **Dashboard URL:** http://localhost:3003
- **Deal ID for workspace:** DL-0020 (Seed Deal Alpha, archived)
- **Backend status:** Partially available (DB reachable via Docker, API intermittent)
- **Breakpoints:** 375px (mobile), 768px (tablet), 1280px (desktop)

## Route Coverage Matrix

| # | Page | Route | 1280px | 768px | 375px | Console | A11y |
|---|------|-------|--------|-------|-------|---------|------|
| 1 | Dashboard | `/dashboard` | dashboard-1280.png | dashboard-768.png | dashboard-375.png | dashboard-console.md | dashboard-a11y.md |
| 2 | Deals List | `/deals` | deals-1280.png | deals-768.png | deals-375.png | deals-console.md | deals-a11y.md |
| 3 | Deal Workspace | `/deals/DL-0020` | deal-workspace-1280.png | deal-workspace-768.png | deal-workspace-375.png | deal-workspace-console.md | deal-workspace-a11y.md |
| 4 | Actions | `/actions` | actions-1280.png | actions-768.png | actions-375.png | actions-console.md | actions-a11y.md |
| 5 | Chat | `/chat` | chat-1280.png | chat-768.png | chat-375.png | chat-console.md | chat-a11y.md |
| 6 | Quarantine | `/quarantine` | quarantine-1280.png | quarantine-768.png | quarantine-375.png | quarantine-console.md | quarantine-a11y.md |
| 7 | Agent Activity | `/agent/activity` | agent-activity-1280.png | agent-activity-768.png | agent-activity-375.png | agent-activity-console.md | agent-activity-a11y.md |
| 8 | Operator HQ | `/hq` | hq-1280.png | hq-768.png | hq-375.png | hq-console.md | hq-a11y.md |
| 9 | Settings | `/settings` | settings-1280.png | settings-768.png | settings-375.png | settings-console.md | settings-a11y.md |
| 10 | Onboarding | `/onboarding` | onboarding-1280.png | onboarding-768.png | onboarding-375.png | onboarding-console.md | onboarding-a11y.md |
| 11 | New Deal | `/deals/new` | new-deal-1280.png | new-deal-768.png | new-deal-375.png | new-deal-console.md | new-deal-a11y.md |
| 12 | Home (redirect) | `/` -> `/dashboard` | home-redirect-1280.png | home-redirect-768.png | home-redirect-375.png | home-redirect-console.md | home-redirect-a11y.md |

## Totals
- **Screenshots:** 36 (12 pages x 3 breakpoints)
- **Console logs:** 12
- **Accessibility snapshots:** 12
- **Coverage:** 100%

## Route Discrepancy
- Mission spec lists Agent Activity at `/agent-activity` but actual route is `/agent/activity`

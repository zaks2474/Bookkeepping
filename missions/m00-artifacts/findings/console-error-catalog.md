# Console Error Catalog — UI-MASTERPLAN-M00

## Summary
- **Total pages with errors:** 2 of 12
- **Total unique errors:** 6
- **Pages clean (0 errors):** Dashboard, Deals List, Actions, Chat, Quarantine, Agent Activity, Operator HQ, Onboarding, New Deal, Home (redirect)
- **Global info message:** React DevTools promotion (appears on all pages, harmless)

## Error Detail by Page

### Deal Workspace (`/deals/DL-0020`)
| # | Level | Message | URL | Impact |
|---|-------|---------|-----|--------|
| 1 | ERROR | 404 Not Found | `/api/deals/DL-0020/enrichment` | Enrichment data not loaded; UI degrades gracefully (shows "TBD"/"Unknown" placeholders) |
| 2 | ERROR | 404 Not Found | `/api/deals/DL-0020/case-file` | Case File tab content unavailable |
| 3 | ERROR | 404 Not Found | `/api/deals/DL-0020/materials` | Materials tab content unavailable |

**Debug messages (non-error):**
- Schema validation notes: broker fields (name, email, company, phone) all Required
- Returning partially validated deal data for DL-0020

**Analysis:** These 404s indicate backend API endpoints that are either not implemented or the backend proxy is not routing correctly. The UI handles them gracefully with placeholder values. These are real wiring gaps (F-8 relevant).

### Settings (`/settings`)
| # | Level | Message | URL | Impact |
|---|-------|---------|-----|--------|
| 1 | ERROR | 404 Not Found | `/api/settings/email` | Email integration settings not loadable; UI shows "not available" alert |
| 2 | ERROR | 404 Not Found | `/api/settings/preferences` | Preferences not loadable (called twice — possible duplicate fetch) |
| 3 | ERROR | 404 Not Found | `/api/settings/preferences` | Duplicate of #2 |

**Analysis:** Settings page makes 3 API calls that all 404. The email endpoint failure is handled with a clear "not available" banner. The double `/api/settings/preferences` call suggests a potential `useEffect` dependency issue or `StrictMode` double-render. Save buttons are correctly disabled when backend is unreachable.

## Per-Page Console Status (All Breakpoints)

| Page | Errors | Warnings | Status |
|------|--------|----------|--------|
| Dashboard | 0 | 0 | Clean |
| Deals List | 0 | 0 | Clean |
| Deal Workspace | 3 | 0 | 3x 404 (enrichment, case-file, materials) |
| Actions | 0 | 0 | Clean |
| Chat | 0 | 0 | Clean |
| Quarantine | 0 | 0 | Clean |
| Agent Activity | 0 | 0 | Clean |
| Operator HQ | 0 | 0 | Clean |
| Settings | 3 | 0 | 3x 404 (email, preferences x2) |
| Onboarding | 0 | 0 | Clean |
| New Deal | 0 | 0 | Clean |
| Home (redirect) | 0 | 0 | Clean |

## Cross-Cutting Observations
1. **React DevTools info** appears on every page — this is a standard Next.js development-mode message, not a defect.
2. **No JavaScript runtime errors** were observed on any page — the app is stable.
3. **404 API errors** are confined to Deal Workspace and Settings — both handle failures gracefully.
4. **No CORS errors, no unhandled promise rejections, no deprecation warnings.**

# Accessibility Coverage Matrix

## Date: 2026-02-12
## Mission: UI-MASTERPLAN-M12

## Check Categories

| Category | Code | Description |
|----------|------|-------------|
| Keyboard Navigation | KB | Tab order, Enter/Space activation, Escape handling |
| Focus Management | FM | Focus trap in modals/drawers, focus return on close |
| Landmarks & Structure | LS | `<main>`, `<nav>`, skip-nav link, heading hierarchy |
| Contrast Smoke | CS | Automated baseline contrast ratio check |
| Screen Reader Semantics | SR | aria-labels, aria-live, sr-only text, role attributes |

## Route × Check Matrix

| Route | KB | FM | LS | CS | SR | Priority |
|-------|----|----|----|----|----|---------|
| `/dashboard` | pending | pending | pending | pending | pending | P1 |
| `/deals` | pending | pending | pending | pending | pending | P1 |
| `/deals/[id]` | pending | pending | pending | pending | pending | P1 |
| `/deals/new` | pending | pending | pending | pending | pending | P1 |
| `/actions` | pending | pending | pending | pending | pending | P1 |
| `/quarantine` | pending | pending | pending | pending | pending | P1 |
| `/chat` | pending | pending | pending | pending | pending | P1 |
| `/settings` | pending | pending | pending | pending | pending | P2 |
| `/onboarding` | pending | pending | pending | pending | pending | P2 |
| `/hq` | pending | pending | pending | pending | pending | P2 |
| `/agent/activity` | pending | pending | pending | pending | pending | P2 |

## Cross-Route Components

| Component | KB | FM | LS | CS | SR | Priority |
|-----------|----|----|----|----|----|---------|
| Sidebar nav | pending | N/A | pending | pending | pending | P1 |
| Header | pending | N/A | pending | pending | pending | P1 |
| Global Search (Cmd+K) | pending | pending | N/A | pending | pending | P1 |
| Agent Drawer (Sheet) | pending | pending | N/A | pending | pending | P1 |
| Alert Modal | pending | pending | N/A | pending | pending | P1 |
| Dialogs (Radix) | pending | pending | N/A | pending | pending | P1 |

## Baseline Assessment (from Explore survey)

### Existing Accessibility Infrastructure
- Radix UI primitives provide built-in focus trapping for Dialog/Sheet/AlertDialog
- shadcn/ui form components link labels via htmlFor, errors via aria-describedby
- 21 sr-only patterns across UI components
- focus-visible ring (3px) on all interactive elements
- `lang='en'` on html element
- Sidebar keyboard shortcut (Ctrl/Cmd+B)
- File uploader has role='button', tabIndex={0}, onKeyDown

### Known Gaps (Pre-Sweep)
| Gap | Severity | Components |
|-----|----------|-----------|
| No skip-nav link | High | Root layout |
| No explicit `<main>` landmark | High | Shell layout |
| No explicit `<nav>` on sidebar | High | Shell layout |
| No focus restoration on modal close | Medium | Custom modals |
| No aria-live for loading states | Medium | Dashboard, deals, actions |
| Collapsibles use data-state not aria-expanded | Low | Sidebar nav (Radix handles) |
| No aria-required on required form fields | Low | New Deal form |
| Color-only status indicators | Medium | Badges, status chips |

## Notes
- Radix Dialog/Sheet/AlertDialog handle focus trap automatically — verify, don't reimplement
- `data-state` on Radix collapsibles maps to aria-expanded internally — verify in DOM
- Priority P1 routes are core operational flows; P2 are secondary

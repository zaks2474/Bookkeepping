# Findings Catalog — UI-MASTERPLAN-M00

**B7 Clarification:** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.

## Finding Categories
- **CC** = Cross-Cutting (appears on 3+ pages)
- **PS** = Page-Specific (isolated to one route)

## Severity Scale
- **Sev-1** = Broken functionality or data loss risk
- **Sev-2** = Significant UX degradation, content hidden/truncated
- **Sev-3** = Minor polish issue, cosmetic

---

## Cross-Cutting Findings

### F-01: Mobile (375px) content truncation across multiple pages
- **Category:** CC
- **Severity:** Sev-2
- **Pages affected:** Dashboard, Deals List, Deal Workspace, Actions, Chat, Quarantine, Operator HQ, Agent Activity
- **Description:** At 375px, text labels, card headers, and button labels are frequently truncated or clipped. The "Today & Next Up" cards on Dashboard clip the second card. Deals table columns clip at "Stag...". HQ stat cards show "Activ Deal", "Pend Appr". Pipeline badges show "Int", "Sc", "Qu".
- **Evidence:** dashboard-375.png, deals-375.png, hq-375.png
- **Mission target:** M-02 (Layout/Shell), M-09 (Dashboard)

### F-02: Header/subtitle wrapping collision with action buttons at 375px
- **Category:** CC
- **Severity:** Sev-2
- **Pages affected:** Dashboard, Actions, Chat, Agent Activity, Quarantine
- **Description:** At 375px, page titles and subtitles wrap to multiple lines and collide horizontally with action buttons (Refresh, Approvals, Clear). On Actions page the "New Action" button is cut off. On Chat the toolbar buttons (History, New Chat, Evidence, Debug) overflow.
- **Evidence:** actions-375.png, chat-375.png, dashboard-375.png
- **Mission target:** M-02 (Layout/Shell)

### F-03: Sidebar collapses to icon-only but no mobile drawer/hamburger
- **Category:** CC
- **Severity:** Sev-3
- **Pages affected:** All pages with sidebar (all except Settings)
- **Description:** At 375px the sidebar collapses to a thin icon strip. There is no mobile hamburger menu or slide-out drawer pattern. The icon strip consumes ~48px of horizontal space on mobile, which is significant at 375px. Navigation labels disappear, relying on icon recognition only.
- **Evidence:** dashboard-375.png, deals-375.png
- **Mission target:** M-02 (Layout/Shell)

### F-04: "Search deals..." global search in header at all breakpoints
- **Category:** CC
- **Severity:** Sev-3
- **Pages affected:** All pages with main shell header
- **Description:** The global "Search deals... Cmd+K" button appears in the top header on all pages. At 768px it truncates to "Search dea... Cmd K". At 375px the search field disappears entirely, leaving only icon buttons. This is functional but the truncation at 768px looks unpolished.
- **Evidence:** deals-768.png, actions-768.png
- **Mission target:** M-02 (Layout/Shell)

### F-05: Inconsistent page title patterns
- **Category:** CC
- **Severity:** Sev-3
- **Pages affected:** Multiple
- **Description:** Browser tab titles are inconsistent: some use "Page | ZakOps" pattern (Dashboard, Agent Activity, Operator HQ, Onboarding), others just show "ZakOps Dashboard" (Deals, Actions, Chat, Quarantine, Settings, New Deal). There's no consistent naming scheme.
- **Evidence:** Accessibility snapshots (page titles)
- **Mission target:** M-02 (Layout/Shell)

### F-06: Disabled notification bell icon present on all pages
- **Category:** CC
- **Severity:** Sev-3
- **Pages affected:** All pages with main shell header
- **Description:** A disabled bell/notification button appears in the top-right header on all main pages. It's always disabled with no tooltip explaining why. May confuse users.
- **Evidence:** dashboard-1280.png (top-right area)
- **Mission target:** M-02 (Layout/Shell)

### F-07: Floating "N" avatar in bottom-left corner
- **Category:** CC
- **Severity:** Sev-3
- **Pages affected:** All pages
- **Description:** A dark circular avatar with "N" appears fixed in the bottom-left corner on all pages at all breakpoints. Appears to be a Next.js dev tools button or user avatar. On mobile (375px) it overlaps content.
- **Evidence:** dashboard-375.png, deals-375.png (bottom-left)
- **Mission target:** M-02 (Layout/Shell)

---

## Page-Specific Findings

### F-08: Deal Workspace — values invisible at 375px
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Deal Workspace (`/deals/DL-0020`)
- **Description:** At 375px, the Deal Information card shows only labels (Stage, Status, Created, Updated) but the values (archived, Feb 2 2026, etc.) are not visible — they appear to overflow off-screen right. The Broker and Financials cards have the same issue.
- **Evidence:** deal-workspace-375.png
- **Mission target:** M-05 (Deal Workspace Polish)

### F-09: Deal Workspace — 3 API 404 errors (enrichment, case-file, materials)
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Deal Workspace
- **Description:** Three API endpoints return 404: `/api/deals/DL-0020/enrichment`, `/api/deals/DL-0020/case-file`, `/api/deals/DL-0020/materials`. UI shows placeholders ("TBD", "Unknown") gracefully but the Materials and Case File tabs likely show empty/error state.
- **Evidence:** deal-workspace-console.md
- **Mission target:** M-05 (Deal Workspace Polish), M-03 (API Failure Contract)

### F-10: Deal Workspace — redundant "archived" badges
- **Category:** PS
- **Severity:** Sev-3
- **Page:** Deal Workspace
- **Description:** The deal header shows "archived" twice — once as a dot-label and once as a red badge. Both convey the same information.
- **Evidence:** deal-workspace-1280.png
- **Mission target:** M-05 (Deal Workspace Polish)

### F-11: Actions — detail panel empty when no selection at all breakpoints
- **Category:** PS
- **Severity:** Sev-3
- **Page:** Actions
- **Description:** At 1280px, the right panel shows "Select an action to view details" taking up ~40% of the viewport. At 375px the detail panel disappears entirely. The large empty panel at desktop wastes space.
- **Evidence:** actions-1280.png, actions-375.png
- **Mission target:** M-06 (Actions Command Center Polish)

### F-12: Actions — "New Action" button hidden at 375px
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Actions
- **Description:** At 375px the "New Action" button is cut off / not visible in the viewport. Users on mobile cannot create new actions without scrolling or finding an alternative path.
- **Evidence:** actions-375.png
- **Mission target:** M-06 (Actions Command Center Polish)

### F-13: Quarantine — detail panel cut off at 768px, hidden at 375px
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Quarantine
- **Description:** At 768px the "Approve" button is cut off and the "Reject reason" field is truncated. At 375px the entire detail/review panel disappears, showing only the queue list. Users on mobile cannot approve or reject quarantine items.
- **Evidence:** quarantine-768.png, quarantine-375.png
- **Mission target:** M-07 (Quarantine + Deals List)

### F-14: Operator HQ — pipeline stage badges truncated at 375px
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Operator HQ
- **Description:** At 375px the pipeline stage cards show truncated labels: "Int" for Inbound, "Sc" for Screening, "Qu" for Qualified, "Dil" for Diligence, "Clo" for Closing, "Port" for Portfolio. Stat cards also truncate: "Activ Deal" for "Active Deals".
- **Evidence:** hq-375.png
- **Mission target:** M-08 (Agent Activity + Operator HQ)

### F-15: Settings — uses different layout (no main sidebar)
- **Category:** PS
- **Severity:** Sev-3
- **Page:** Settings
- **Description:** Settings page has its own layout pattern with a "Back to Dashboard" link and left-side section nav (AI Provider, Email, Agent Config, Notifications, Data & Privacy, Appearance). It does not use the standard sidebar shell. This is a deliberate design choice but worth noting for consistency review.
- **Evidence:** settings-1280.png
- **Mission target:** M-10 (Settings + New Deal)

### F-16: Settings — 3 API 404 errors and duplicate preferences fetch
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Settings
- **Description:** Three 404 errors: `/api/settings/email`, `/api/settings/preferences` (called twice). The double preferences call suggests a useEffect dependency issue or StrictMode double-render. Save buttons correctly disabled.
- **Evidence:** settings-console.md
- **Mission target:** M-10 (Settings + New Deal), M-03 (API Failure Contract)

### F-17: Onboarding — resume banner takes excessive vertical space
- **Category:** PS
- **Severity:** Sev-3
- **Page:** Onboarding
- **Description:** The "Welcome back! You were on step 4 of 6" resume banner takes significant vertical space at all breakpoints. At 1280px the text wraps into a narrow column on the left with Resume/Start Fresh buttons. The layout is awkward.
- **Evidence:** onboarding-1280.png
- **Mission target:** M-09 (Dashboard + Onboarding)

### F-18: Onboarding — stepper labels hidden at 375px
- **Category:** PS
- **Severity:** Sev-3
- **Page:** Onboarding
- **Description:** At 375px the stepper shows only icons without labels (Welcome, Your Profile, Connect Email, Meet Your Agent, Preferences, All Set!). Icons alone may not communicate step purpose.
- **Evidence:** onboarding-375.png
- **Mission target:** M-09 (Dashboard + Onboarding)

### F-19: Dashboard — "Today & Next Up" cards clip at 375px
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Dashboard
- **Description:** At 375px, the "Today & Next Up" section shows only the first deal card fully; the second card is clipped at the right edge with only the badge partially visible ("De..."). No horizontal scroll indicator.
- **Evidence:** dashboard-375.png
- **Mission target:** M-09 (Dashboard + Onboarding)

### F-20: Dashboard — "0 active deals across 0 stages" inconsistency
- **Category:** PS
- **Severity:** Sev-3
- **Page:** Dashboard
- **Description:** On initial load the Pipeline card shows "0 active deals across 0 stages" but then updates to "9 active deals across 3 stages" after data loads. The "Today & Next Up" shows "2 items" but the Pipeline shows different counts. This timing/cache inconsistency is visible during navigation.
- **Evidence:** Accessibility snapshot vs screenshot comparison
- **Mission target:** M-09 (Dashboard + Onboarding)

### F-21: Deals List — table horizontal overflow at 375px
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Deals List
- **Description:** At 375px the deals table columns overflow — only "Deal Name" and partial "Stage" columns visible. Broker, Priority, Last Update, and delete columns are clipped. No horizontal scroll indicator.
- **Evidence:** deals-375.png
- **Mission target:** M-07 (Quarantine + Deals List)

### F-22: Chat — toolbar overflow at 768px and 375px
- **Category:** PS
- **Severity:** Sev-2
- **Page:** Chat
- **Description:** At 768px the "Evidence" and "Debug" buttons are clipped. At 375px only "Global" dropdown is visible; History, New Chat, Evidence, and Debug are all hidden/clipped. Essential chat controls are inaccessible on mobile.
- **Evidence:** chat-768.png, chat-375.png
- **Mission target:** M-04 (Chat Page Polish)

### F-23: Agent Activity — stat cards stack vertically at 375px
- **Category:** PS
- **Severity:** Sev-3
- **Page:** Agent Activity
- **Description:** At 375px, the 4 stat cards (Tools Called Today, Approvals Processed, Deals Analyzed, Runs 24h) stack vertically, each taking a full card height. This pushes the activity list and search below the fold. A 2x2 grid or compact display would be more space-efficient.
- **Evidence:** agent-activity-375.png
- **Mission target:** M-08 (Agent Activity + Operator HQ)

---

## Summary Statistics
- **Total findings:** 23
- **Cross-cutting:** 7 (F-01 through F-07)
- **Page-specific:** 16 (F-08 through F-23)
- **Sev-1:** 0
- **Sev-2:** 11 (F-01, F-02, F-08, F-09, F-12, F-13, F-14, F-16, F-19, F-21, F-22)
- **Sev-3:** 12 (F-03, F-04, F-05, F-06, F-07, F-10, F-11, F-15, F-17, F-18, F-20, F-23)

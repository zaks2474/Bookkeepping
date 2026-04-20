# Non-Applicability Notes — DASHBOARD-R5-POLISH-002

## P2-03: Conditional Visibility Fallback — NOT APPLICABLE

**Decision:** Skip P2-03 (change `opacity-0` to `opacity-50` on 3-dot trigger).

**Rationale:** Both P2-01 and P2-02 passed on the fresh runtime build:
- P2-01: Enhanced history metadata (badges, scope icons, message counts, relative times, deal names) all visible. Evidence: `screenshots/p2-chat-history-open.png`
- P2-02: 3-dot trigger is discoverable on hover. Menu opens with all 5 actions (Rename, Pin, Duplicate, Archive, Delete). Evidence: `screenshots/p2-chat-menu-hover.png`

Per mission decision tree (line 268): "IF P2-01 and P2-02 pass on fresh runtime -> skip P2-03 and record non-applicability."

The `opacity-0 group-hover:opacity-100` pattern is standard UX for action menus on list items — it reduces visual noise while maintaining discoverability through the hover affordance. No fallback needed.

**Evidence:** `p2-chat-history-open.png`, `p2-chat-menu-hover.png`

---

## P3-02/P3-03: Settings Internal Subsection Normalization — NOT APPLICABLE

**Decision:** Skip P3-02 (apply unified internal subsection box pattern) and P3-03 (capture before/after).

**Rationale:** The P3-01 audit (`reports/p3-settings-audit.md`) found that all 6 settings sections already follow a consistent internal container pattern:
- **Toggle items:** `p-4 rounded-lg border` (8/9 instances, 1 contextual `p-3`)
- **Selection items:** `border-primary bg-primary/5` active state (all instances)
- **Info boxes:** `bg-muted/50 rounded-lg p-4` (both instances)
- **Outer wrapper:** All use shared `SettingsSectionCard` component

Minor variations (p-3 vs p-4, border vs border-2) are contextually appropriate for visual hierarchy (grid selectors use border-2 for emphasis, nested items use reduced padding).

Per mission decision tree (line 321-322): "ELSE IF inconsistency is acceptable and user does not request redesign -> skip edits and execute P3-04."

**Evidence:** `reports/p3-settings-audit.md`, `screenshots/p3-settings-1280.png`

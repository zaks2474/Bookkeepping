# Phase 2: Quarantine UX Overhaul -- Design Specification

**Version:** 1.0
**Date:** 2026-02-14
**Scope:** Quarantine-centric UX overhaul with holistic shared-component extraction across all dashboard pages
**Surface 9 Compliance:** Required -- all designs adhere to `design-system-manifest.ts` and `.claude/rules/design-system.md`
**Status:** DESIGN ONLY -- no implementation code

---

## Table of Contents

1. [Aesthetic Direction](#1-aesthetic-direction)
2. [Shared Component Plan](#2-shared-component-plan)
3. [Quarantine-Specific Component Designs](#3-quarantine-specific-component-designs)
4. [Feature Parity Matrix](#4-feature-parity-matrix)
5. [Responsive Behavior](#5-responsive-behavior)
6. [Dark Mode](#6-dark-mode)
7. [Accessibility](#7-accessibility)
8. [Implementation Notes](#8-implementation-notes)

---

## 1. Aesthetic Direction

### Design Language: Industrial Utilitarian

The quarantine UX (and by extension all shared components) adopts an **industrial utilitarian** aesthetic. This is not a generic SaaS dashboard. It is a decision-making workstation for a deal operator who triages email signals under time pressure. The visual language must communicate:

- **Authority and clarity** -- the operator is making consequential decisions (approve a deal, reject noise). The UI must not trivialize this with playful decoration.
- **Information density without clutter** -- dense data display is acceptable and expected; wasted space is a design failure. Controlled density beats timid whitespace.
- **Operational tempo** -- the interface should feel like a control room, not a marketing page. Status indicators, queue depths, and confidence scores are primary visual elements.

### Anti-Convergence Declaration

Per Surface 9 rule B7, this design deliberately avoids:

- Purple-gradient-on-white schemes (the existing dark theme uses achromatic oklch values; we stay achromatic with targeted semantic color accents)
- Generic AI dashboard aesthetics (no floating cards with rounded corners on pastel backgrounds, no decorative gradient meshes on the quarantine page)
- Cookie-cutter component layouts -- each page adapts shared components to its domain context rather than looking uniform

### Typography

The dashboard uses Inter (`--font-sans: var(--font-inter)`) as the body font. This is a deliberate neutrality choice for data-heavy screens. No change needed. The `theme-mono` variant (using `--font-mono`) provides an alternative for users who prefer monospaced density. Both remain supported.

### Color System

Color serves a functional role in quarantine:

| Semantic Purpose | Light Mode Token | Dark Mode Token | Usage |
|-----------------|-----------------|-----------------|-------|
| High confidence | `oklch(0.55 0.18 145)` (muted green) | `oklch(0.65 0.18 145)` | Confidence >= 0.8 |
| Medium confidence | `oklch(0.70 0.15 80)` (warm amber) | `oklch(0.75 0.15 80)` | Confidence 0.5-0.79 |
| Low confidence | `oklch(0.60 0.20 25)` (warm red) | `oklch(0.70 0.19 22)` | Confidence < 0.5 |
| Shadow mode | `oklch(0.55 0.15 290)` (violet) | `oklch(0.65 0.15 290)` | LangSmith shadow items |
| Source: email_sync | existing `--muted-foreground` | existing `--muted-foreground` | Default source |
| Destructive action | existing `--destructive` | existing `--destructive` | Delete, reject |
| Approval action | existing `--primary` | existing `--primary` | Approve |

These are defined as CSS custom properties at `@layer base`, consistent with `CSS_CONVENTIONS.globalLayer`.

### Motion

Per Surface 9 rule B4 and C4:

- **List-to-detail transition:** 200ms `opacity` + `transform: translateX()` for the detail panel sliding in. GPU-composited only.
- **Confidence indicator:** 300ms `opacity` fade on confidence badge color change. No layout-triggering animations.
- **Bulk selection bar:** 150ms `transform: translateY()` slide-up from below the toolbar. Wrapped in `@media (prefers-reduced-motion: no-preference)`.
- **Item removal:** 200ms `opacity` fade-out when an item is approved/rejected/deleted, followed by list reflow.

---

## 2. Shared Component Plan

These 4 components are extracted from existing page-specific implementations and generalized for use across ALL dashboard pages. They live in `apps/dashboard/src/components/shared/`.

### 2.1 FilterDropdown

**Problem:** Quarantine uses a native `<select>` element for source type filtering. Deals uses Radix `<Select>` for stage/status filtering. Actions and Agent Activity use `<Tabs>` for status filtering plus Radix `<Select>` for type filtering. This inconsistency breaks user expectations when navigating between pages.

**Solution:** A unified `FilterDropdown` component that wraps Radix `<Select>` with a consistent API, supporting single-select and multi-value display.

#### Props Interface

```
FilterDropdownProps {
  label: string                          // "Source type", "Stage", "Status"
  value: string                          // Current filter value
  onValueChange: (value: string) => void // Change handler
  options: FilterOption[]                // Available options
  allLabel?: string                      // Label for "All" option (default: "All")
  icon?: React.ComponentType             // Optional leading icon (e.g., IconFilter)
  disabled?: boolean
  className?: string
  width?: 'auto' | 'sm' | 'md' | 'lg'   // Predefined widths: sm=120px, md=180px, lg=240px, auto=fit-content
}

FilterOption {
  value: string
  label: string
  icon?: React.ComponentType             // Optional per-option icon
  badge?: string | number                // Optional count badge
  variant?: 'default' | 'muted'         // Visual weight
}
```

#### Visual Description

- Built on Radix `<Select>` (already in the UI library at `components/ui/select.tsx`)
- Trigger shows: optional icon + selected label + chevron
- Dropdown content uses `<SelectItem>` with optional icon and trailing badge (count)
- "All" option always appears first and uses the sentinel value pattern (`__all__`) already established in the deals page
- Trigger height matches existing controls: `h-9`

#### Usage Per Page

| Page | Replaces | Filter Options |
|------|----------|---------------|
| Quarantine | Native `<select>` for source_type | All sources, email_sync, langsmith_shadow, langsmith_live, manual |
| Deals | Existing Radix `<Select>` for stage, status | All stages (from PIPELINE_STAGES), All statuses |
| Actions | Existing Radix `<Select>` for action type | All types (dynamic from capabilities) |
| Agent Activity | N/A (tabs remain for primary nav) | Could add secondary filter for event source |
| HQ | N/A (overview page) | N/A |
| Settings | N/A | N/A |
| Dashboard | N/A (overview page) | N/A |

#### Responsive Behavior

- Desktop (>1280px): Fixed width per `width` prop
- Tablet (768-1280px): Same fixed width, wraps to next line in flex container if needed
- Mobile (<768px): Full width (`w-full`) when inside a stacked layout

---

### 2.2 BulkSelectionBar

**Problem:** Quarantine has select-all checkbox + bulk delete toolbar inline in the card header. Deals has select-all in the table header + bulk delete in a separate section. Actions has select-all above the list + bulk archive/delete in a floating bar. Three different patterns for the same concept.

**Solution:** A unified `BulkSelectionBar` component that handles select-all state, selection count display, and renders action buttons provided by the parent page.

#### Props Interface

```
BulkSelectionBarProps {
  selectedCount: number                        // Number of selected items
  totalCount: number                           // Total visible items
  selectionState: 'none' | 'some' | 'all'     // Drives checkbox visual
  onSelectAll: () => void                      // Toggle select all
  onClearSelection: () => void                 // Clear all selections
  actions: BulkAction[]                        // Page-specific bulk actions
  disabled?: boolean
  className?: string
}

BulkAction {
  label: string                                // "Delete", "Archive", "Approve All"
  icon: React.ComponentType                    // Tabler icon
  onClick: () => void
  variant: 'default' | 'destructive' | 'outline'
  disabled?: boolean
  loading?: boolean
}
```

#### Visual Description

- Horizontal bar with: Checkbox (tri-state) | "N selected" text | spacer | action buttons | "Clear" button
- Background: `bg-muted/50` with `border border-muted-foreground/20 rounded-lg`
- Appears/disappears with a 150ms `translateY` animation (GPU-composited)
- When `selectedCount === 0`, the bar is hidden (not rendered, not `display: none`)
- Checkbox supports three states: unchecked (none), checked (all), indeterminate (some)

#### Usage Per Page

| Page | Bulk Actions |
|------|-------------|
| Quarantine | Delete selected, Approve selected (future), Reject selected (future) |
| Deals | Delete (archive) selected |
| Actions | Archive selected, Delete selected |
| Agent Activity | None currently (extensible for future "Mark read" or "Export") |
| HQ | N/A |
| Settings | N/A |
| Dashboard | N/A |

#### Responsive Behavior

- Desktop: Single row, actions right-aligned
- Tablet: Same layout, action labels hidden (icon-only buttons)
- Mobile: Two rows -- checkbox + count on top, actions below, full-width buttons

---

### 2.3 ListDetailLayout

**Problem:** Quarantine uses a custom split-pane layout (left queue card + right preview card) with `md:w-[340px] lg:w-[420px]` on the list and `flex-1` on the detail. Deals navigates to a separate page (`/deals/[id]`). Actions uses a `grid grid-cols-1 lg:grid-cols-3` pattern with a detail panel on large screens and a fixed bottom sheet on mobile. Three different approaches.

**Solution:** A shared `ListDetailLayout` component that provides a consistent split-pane pattern with responsive collapse behavior.

#### Props Interface

```
ListDetailLayoutProps {
  listContent: React.ReactNode             // The master list (queue, table, card list)
  detailContent: React.ReactNode | null    // The detail panel (null = no selection)
  emptyDetailContent?: React.ReactNode     // Shown when no item is selected
  listWidth?: 'narrow' | 'medium' | 'wide' // narrow=300px, medium=420px, wide=50%
  collapseAt?: 'md' | 'lg'                 // Breakpoint where layout collapses to single-column
  detailPosition?: 'right' | 'bottom'      // Desktop: always right. Mobile: configurable
  mobileDetailMode?: 'sheet' | 'navigate' | 'overlay'  // How detail appears on mobile
  resizable?: boolean                      // Allow drag-to-resize (uses ResizableHandle)
  className?: string
}
```

#### Visual Description

- **Desktop:** Side-by-side horizontal split. List on left with fixed or resizable width. Detail on right fills remaining space. Both wrapped in cards (existing `Card` component).
- **When no item selected:** Detail area shows `emptyDetailContent` (typically a centered icon + "Select an item to review" prompt).
- **Resizable mode:** Uses the existing `ResizablePanelGroup` + `ResizableHandle` from `components/ui/resizable.tsx`. Handle appears as a subtle 1px border with a grip icon on hover.
- **Separator:** Existing `ResizableHandle` with `withHandle` prop.

#### Usage Per Page

| Page | List Width | Collapse At | Mobile Detail Mode | Resizable |
|------|-----------|-------------|-------------------|-----------|
| Quarantine | medium (420px) | md | sheet | Yes |
| Deals | wide (50%) | lg | navigate (`/deals/[id]`) | No |
| Actions | medium (420px) | lg | overlay (existing bottom sheet pattern) | Yes |
| Agent Activity | medium (420px) | lg | sheet | No |
| HQ | N/A (not a list page) | N/A | N/A | N/A |
| Settings | N/A (sidebar nav, not list-detail) | N/A | N/A | N/A |
| Dashboard | N/A (widget grid) | N/A | N/A | N/A |

#### Responsive Behavior

- **Desktop (>1280px):** Full side-by-side, resizable if enabled
- **Tablet (768-1280px):** Side-by-side at `lg` collapse; single-column with detail below at `md` collapse
- **Mobile (<768px):** Single column. Detail appears as:
  - `sheet`: Radix Sheet sliding up from bottom (max 70vh)
  - `navigate`: Router push to detail page
  - `overlay`: Fixed bottom overlay (existing Actions pattern)

---

### 2.4 ConfirmDialog

**Problem:** Quarantine uses `AlertDialog` for delete confirmation. Deals uses the same `AlertDialog` with similar but slightly different copy. Actions uses `Dialog` for clear-completed confirmation. The existing `AlertModal` in `components/modal/alert-modal.tsx` is a fourth pattern with hardcoded text. Four patterns for "are you sure?"

**Solution:** A unified `ConfirmDialog` component with severity levels, customizable text, and consistent behavior.

#### Props Interface

```
ConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string                              // "Delete quarantine item?"
  description: string                        // Explanation of what happens
  severity: 'info' | 'warning' | 'destructive'  // Drives visual treatment
  confirmLabel?: string                      // Default: "Confirm" (or "Delete" for destructive)
  cancelLabel?: string                       // Default: "Cancel"
  onConfirm: () => void | Promise<void>
  loading?: boolean                          // Shows spinner on confirm button, disables both buttons
  itemCount?: number                         // When > 1, title/description can interpolate count
  children?: React.ReactNode                 // Optional additional content between description and buttons
}
```

#### Visual Description

- Built on existing `AlertDialog` primitives (already in UI library)
- **Severity = info:** Default button styling, informational icon
- **Severity = warning:** Amber-tinted description area, warning icon, default button
- **Severity = destructive:** Red-tinted confirm button (`variant='destructive'`), destructive icon, description emphasizes irreversibility
- Confirm button shows a spinner (`IconLoader2 animate-spin`) when `loading` is true
- Both buttons disabled during loading
- Focus trapped inside dialog per Radix default behavior

#### Usage Per Page

| Page | Severity | Use Cases |
|------|----------|-----------|
| Quarantine | destructive | Delete item(s), bulk delete |
| Quarantine | warning | Reject with reason (future) |
| Deals | destructive | Archive/delete deal(s) |
| Actions | info | Archive completed actions |
| Actions | destructive | Delete completed actions, bulk delete |
| Agent Activity | info | Future: export confirmation |
| Settings | warning | Future: reset preferences |

#### Responsive Behavior

- Consistent across all breakpoints (modal overlays full viewport)
- Mobile: Full-width content area with `max-w-[calc(100%-2rem)]` (existing Dialog behavior)
- Footer buttons stack vertically on mobile (`flex-col-reverse` per existing `DialogFooter`)

---

## 3. Quarantine-Specific Component Designs

These components live in `apps/dashboard/src/components/quarantine/` and are used only on the quarantine page. They compose the shared components from Section 2 with quarantine-specific domain logic.

### 3.1 Approval Modal

**Purpose:** Replace the current inline approve/reject controls in the quarantine preview header with a dedicated modal that provides more space for reviewing the decision, editing extracted fields, and adding operator notes.

#### Props Interface

```
ApprovalModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  item: QuarantineItem
  preview: QuarantinePreview
  operatorName: string
  onApprove: (params: ApprovalParams) => Promise<void>
  onReject: (params: RejectParams) => Promise<void>
  loading?: boolean
}

ApprovalParams {
  operatorName: string
  editedFields?: Record<string, string>    // Optional field overrides
  notes?: string                           // Optional operator notes
}

RejectParams {
  operatorName: string
  reason: string                           // Required for reject
  notes?: string
}
```

#### Visual Description

- **Two-column layout inside Dialog:**
  - Left column (60%): Editable extracted fields (company name, broker email, asking price) + operator name input + reject reason input
  - Right column (40%): Read-only evidence summary (confidence indicator, classification, source type, summary bullets)
- **Footer:** Two primary actions: "Reject" (destructive variant, left-aligned) and "Approve" (primary variant, right-aligned). The spatial separation reinforces the decision gravity.
- **Confidence display:** Prominent confidence indicator (see 3.3) at the top of the right column
- **Field editing:** Each extracted field shows the AI-extracted value as the default. The operator can override. Changed fields get a subtle amber left-border to indicate manual edit.
- **Keyboard shortcut hint:** Small text below the buttons: "Ctrl+Enter to approve, Esc to cancel"

#### Responsive Behavior

- Desktop: Two-column layout inside a `max-w-3xl` dialog
- Tablet: Two-column layout, slightly narrower
- Mobile: Single-column layout, evidence summary collapses into an expandable section above the form fields

---

### 3.2 Escalate Flow

**Purpose:** For items that need human review beyond the current operator -- flag for supervisor review, change priority, or add investigation notes without making an approve/reject decision.

#### Props Interface

```
EscalateFlowProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  item: QuarantineItem
  onEscalate: (params: EscalateParams) => Promise<void>
  loading?: boolean
}

EscalateParams {
  priority: 'normal' | 'high' | 'urgent'
  assignTo?: string                        // Operator name or team
  note: string                             // Required escalation note
  reason: 'unclear_classification' | 'needs_domain_expert' | 'suspicious_content' | 'complex_deal' | 'other'
}
```

#### Visual Description

- **Compact dialog** (`max-w-lg`) with:
  - Priority selector: Three radio buttons (normal, high, urgent) displayed horizontally with color-coded labels
  - Reason dropdown: `FilterDropdown` with predefined escalation reasons
  - Note textarea: Required, 3-row minimum, placeholder "Describe why this needs review..."
  - Assign field: Optional text input for target operator/team
- **Priority visual treatment:**
  - Normal: Default border
  - High: Amber left border accent
  - Urgent: Red left border accent with pulsing dot indicator

#### Responsive Behavior

- Desktop/Tablet: Standard dialog positioning
- Mobile: Full-width dialog, priority selector stacks vertically

---

### 3.3 Confidence Indicators

**Purpose:** Visually communicate triage confidence level for each quarantine item. Currently, there are no confidence indicators in the quarantine UI -- items show urgency and classification badges but not the AI's confidence score.

#### Props Interface

```
ConfidenceIndicatorProps {
  score: number                            // 0.0 to 1.0
  size?: 'sm' | 'md' | 'lg'              // sm: inline badge, md: badge with label, lg: detailed with bar
  showLabel?: boolean                      // Show "High", "Medium", "Low" text
  showScore?: boolean                      // Show numeric score (e.g., "0.87")
  className?: string
}
```

#### Visual Description

- **Size = sm:** A colored dot (8px circle) using the confidence color scale (green/amber/red). Suitable for inline use in list items.
- **Size = md:** Colored badge with text label. Example: a badge with background `bg-confidence-high/10` and text `text-confidence-high`, reading "High (0.87)".
- **Size = lg:** Horizontal bar visualization. The bar fills proportionally to the score. Background is `bg-muted`, fill uses the confidence color. Numeric score displayed to the right. Label displayed above.

**Confidence thresholds:**
- High: score >= 0.8 -- green tones
- Medium: score >= 0.5 && score < 0.8 -- amber tones
- Low: score < 0.5 -- red tones

**Anti-convergence note:** The indicator uses a segmented bar (3 discrete segments that fill sequentially) rather than a smooth gradient. This gives it a utilitarian, instrument-panel feel rather than the ubiquitous smooth progress bar.

#### Usage

- **In quarantine list items:** `size="sm"` next to the subject line
- **In quarantine preview header:** `size="lg"` prominently displayed
- **In approval modal:** `size="md"` in the evidence column
- **In triage summary card:** `size="md"`

#### Responsive Behavior

- `sm` and `md` sizes are unchanged across breakpoints
- `lg` size: bar width adapts to container; on mobile, the bar shrinks but remains visible

---

### 3.4 Evidence Panel

**Purpose:** Show the full reasoning chain behind a triage classification -- the source email, why the AI classified it as a deal signal, what patterns matched, and what extracted data supports the decision.

#### Props Interface

```
EvidencePanelProps {
  preview: QuarantinePreview
  item: QuarantineItem
  defaultExpanded?: string[]               // Which sections start expanded
  className?: string
}
```

#### Visual Description

The evidence panel is an accordion (`Collapsible` components, already used in the quarantine page for link groups) with the following sections:

1. **Classification Reasoning** (default: expanded)
   - Classification label with confidence indicator (`size="md"`)
   - Bullet list of reasoning factors (from `preview.summary`)
   - Source type badge

2. **Matched Patterns** (default: expanded)
   - List of patterns that triggered the classification
   - Each pattern shows: pattern name, match location (subject/body/sender), match excerpt with highlighted text

3. **Extracted Fields** (default: expanded)
   - Grid layout showing all extracted fields (company_guess, broker_email, asking_price, etc.)
   - Fields with low extraction confidence get an amber warning icon

4. **Source Email** (default: collapsed)
   - Full email body in a scrollable container with `max-h-[400px]`
   - Headers (From, To, Subject, Date) displayed above the body
   - Expand/collapse toggle (already exists in current quarantine page)

5. **Links & Attachments** (default: collapsed)
   - Reuses the existing link categorization UI from the quarantine page
   - Attachment list with download status

Each section header shows: Chevron (rotation animated) + section title + item count badge.

#### Responsive Behavior

- Desktop: Full width within the detail panel
- Tablet: Same layout, slightly more compact spacing
- Mobile: Full width, all sections default-collapsed except "Classification Reasoning" to save vertical space

---

### 3.5 Filter Controls

**Purpose:** Quarantine-specific filter bar that composes multiple `FilterDropdown` components with additional controls for date range and confidence range.

#### Props Interface

```
QuarantineFilterControlsProps {
  sourceType: string
  onSourceTypeChange: (value: string) => void
  dateRange: DateRange | null
  onDateRangeChange: (range: DateRange | null) => void
  confidenceRange: [number, number]        // [min, max], 0.0-1.0
  onConfidenceRangeChange: (range: [number, number]) => void
  status: string
  onStatusChange: (value: string) => void
  onClear: () => void
  hasActiveFilters: boolean
}

DateRange {
  from: Date
  to: Date
}
```

#### Visual Description

- Horizontal bar of filter controls (wrapping on smaller screens):
  1. **Source type:** `FilterDropdown` with options: All, email_sync, langsmith_shadow, langsmith_live, manual
  2. **Status:** `FilterDropdown` with options: All, PENDING, APPROVED, REJECTED
  3. **Date range:** Button that opens a `Popover` with the existing `Calendar` component for date range selection. Button label shows selected range or "Any date".
  4. **Confidence range:** Dual-handle slider (using the existing `Slider` component) with labels "0%" and "100%". Shows selected range below: "50% - 100%".
  5. **Clear filters:** Ghost button, only visible when `hasActiveFilters` is true

All filter values are URL-persisted via `nuqs` (already used in the deals page), following `STATE_MANAGEMENT_CONVENTIONS.urlState`.

#### Responsive Behavior

- Desktop: All filters in a single row
- Tablet: Filters wrap to two rows
- Mobile: Filters stack vertically, each filter full-width. Confidence slider gets extra padding for touch targets.

---

### 3.6 Triage Summary Card

**Purpose:** Compact card showing key fields for a quarantine item in the list view. Replaces the current inline rendering of item data in the quarantine queue.

#### Props Interface

```
TriageSummaryCardProps {
  item: QuarantineItem
  selected?: boolean
  checked?: boolean
  onSelect: () => void
  onCheck: (checked: boolean) => void
  onDelete?: () => void
  className?: string
}
```

#### Visual Description

- **Layout:** Horizontal card with checkbox on the left, content in the middle, delete button on the right
- **Content area:**
  - Row 1: Subject line (truncated, `font-medium`) + confidence indicator (`size="sm"`)
  - Row 2: Sender (truncated, `text-sm text-muted-foreground`)
  - Row 3: Badge row: urgency badge + classification badge + status badge + source type badge (shadow mode) + timestamp
- **Selected state:** `bg-accent border-accent` (matches current behavior)
- **Hover state:** `hover:bg-accent/50` (matches current behavior)
- **Checkbox click area:** Stops propagation (matches current behavior)
- **Delete button:** Ghost icon button, stops propagation (matches current behavior)

**Differences from current implementation:**
- Adds confidence indicator (currently missing)
- Extracts badge rendering into a reusable sub-component
- Standardizes the `id` resolution pattern (`action_id || id || quarantine_id`) into the card component rather than repeating it in the parent

#### Responsive Behavior

- Desktop/Tablet: Full horizontal layout
- Mobile: Subject and sender lines get more truncation (`max-w-[200px]`); badge row wraps

---

## 4. Feature Parity Matrix

### Dashboard Pages Inventory

| # | Page | Route | Primary Purpose |
|---|------|-------|----------------|
| 1 | Dashboard | `/dashboard` | Overview widgets, morning briefing, pipeline summary |
| 2 | Deals | `/deals` | Deal pipeline management, table + board views |
| 3 | Actions | `/actions` | Kinetic action management, approval workflow |
| 4 | Quarantine | `/quarantine` | Email triage decision queue |
| 5 | Agent Activity | `/agent/activity` | Agent event history and monitoring |
| 6 | Operator HQ | `/hq` | Operational overview, cross-system status |
| 7 | Settings | `/settings` | User preferences, appearance, email config |
| 8 | Chat | `/chat` | Agent conversation interface |
| 9 | Onboarding | `/onboarding` | New user setup flow |

### Feature Parity: Current State vs Target State

#### A. Filter Controls

| Page | Current | Target |
|------|---------|--------|
| Quarantine | Native `<select>` for source_type only | `FilterDropdown` x4 (source, status, date, confidence) + `QuarantineFilterControls` |
| Deals | Radix `Select` x2 (stage, status) + search input | `FilterDropdown` x2 + search input (no change in count, standardized component) |
| Actions | Radix `Select` x1 (type) + search + tabs | `FilterDropdown` x1 + search + tabs (standardized component) |
| Agent Activity | Tabs only (activity type) | Tabs + `FilterDropdown` x1 (event source filter) |
| HQ | None | None (overview page, no filtering needed) |
| Settings | Sidebar nav | No change |
| Dashboard | None | None (overview page) |
| Chat | None | None |
| Onboarding | None | None |

#### B. Select-All / Bulk Selection

| Page | Current | Target |
|------|---------|--------|
| Quarantine | Custom checkbox in CardTitle + inline bulk delete | `BulkSelectionBar` with delete + future approve/reject bulk actions |
| Deals | Checkbox in TableHead + inline bulk delete | `BulkSelectionBar` with archive action |
| Actions | Checkbox above list + inline bulk archive/delete | `BulkSelectionBar` with archive + delete actions |
| Agent Activity | None | `BulkSelectionBar` (extensible, no actions initially) |
| HQ | None | None |
| Settings | None | None |
| Dashboard | None | None |
| Chat | None | None |
| Onboarding | None | None |

#### C. Preview / Detail Panel

| Page | Current | Target |
|------|---------|--------|
| Quarantine | Custom split-pane (Card + Card) | `ListDetailLayout` (medium width, resizable, sheet on mobile) |
| Deals | Navigate to `/deals/[id]` | `ListDetailLayout` (wide, non-resizable, navigate on mobile) -- optional, can keep current pattern |
| Actions | Grid-based split + bottom sheet on mobile | `ListDetailLayout` (medium width, resizable, overlay on mobile) |
| Agent Activity | None | `ListDetailLayout` (medium width, non-resizable, sheet on mobile) -- show event detail on selection |
| HQ | None | None (overview page) |
| Settings | Sidebar + scroll sections | No change (different pattern, not list-detail) |
| Dashboard | None | None |
| Chat | None | None (different interaction model) |
| Onboarding | None | None |

#### D. URL-Persisted State

| Page | Current | Target |
|------|---------|--------|
| Quarantine | `selected` param only (via `useSearchParams`) | `selected`, `source_type`, `status`, `confidence_min`, `confidence_max`, `date_from`, `date_to` (via `nuqs`) |
| Deals | Full nuqs integration (view, stage, status, q, sortBy, sortOrder, page) | No change (already complete) |
| Actions | Manual `useSearchParams` (status, type, deal_id, q, selected) | Migrate to `nuqs` for consistency |
| Agent Activity | Manual `useSearchParams` (tab, search) | Migrate to `nuqs` for consistency |
| HQ | None | None |
| Settings | Section hash via scroll observer | No change |
| Dashboard | None | None |
| Chat | None | None |
| Onboarding | None | None |

#### E. Confirmation Dialogs

| Page | Current | Target |
|------|---------|--------|
| Quarantine | `AlertDialog` for delete | `ConfirmDialog` (destructive) for delete, (warning) for reject with reason |
| Deals | `AlertDialog` for archive | `ConfirmDialog` (destructive) for archive |
| Actions | `Dialog` for clear completed, no dialog for bulk ops | `ConfirmDialog` (info) for archive, (destructive) for delete, for all bulk ops |
| Agent Activity | None | `ConfirmDialog` extensible for future operations |
| HQ | None | None |
| Settings | None | `ConfirmDialog` (warning) for destructive settings changes |
| Dashboard | None | None |
| Chat | None | None |
| Onboarding | None | None |

#### F. Shared Components Adoption Summary

| Page | FilterDropdown | BulkSelectionBar | ListDetailLayout | ConfirmDialog |
|------|---------------|-----------------|-----------------|---------------|
| Quarantine | Yes | Yes | Yes | Yes |
| Deals | Yes (replace) | Yes (replace) | Optional | Yes (replace) |
| Actions | Yes (replace) | Yes (replace) | Yes (replace) | Yes (replace) |
| Agent Activity | Yes (add) | Yes (add, extensible) | Yes (add) | Yes (extensible) |
| HQ | No | No | No | No |
| Settings | No | No | No | Yes (add) |
| Dashboard | No | No | No | No |
| Chat | No | No | No | No |
| Onboarding | No | No | No | No |

---

## 5. Responsive Behavior

### Breakpoint Strategy

Per Surface 9 rule C1, we use Tailwind's default breakpoints:

| Breakpoint | Width | Target Device |
|-----------|-------|---------------|
| Base | <640px | Small mobile |
| `sm` | 640px+ | Large mobile |
| `md` | 768px+ | Tablet portrait |
| `lg` | 1024px+ | Tablet landscape / small laptop |
| `xl` | 1280px+ | Desktop |
| `2xl` | 1536px+ | Large desktop |

### Critical Testing Widths

1. **375px** -- iPhone SE / small mobile
2. **768px** -- iPad portrait / tablet
3. **1280px** -- Standard desktop

### ListDetailLayout Collapse Behavior

#### Desktop (xl+, 1280px+)

```
+------------------+----------------------------+
|  List Panel      |  Detail Panel              |
|  (fixed width    |  (flex-1, fills remaining) |
|   or resizable)  |                            |
|                  |                            |
+------------------+----------------------------+
```

#### Tablet (md to xl, 768px-1279px)

Pages with `collapseAt="lg"` show single-column at this range:

```
+----------------------------------------+
|  List Panel (full width)               |
+----------------------------------------+
|  Detail: Sheet from bottom (70vh max)  |
+----------------------------------------+
```

Pages with `collapseAt="md"` still show split at this range.

#### Mobile (<768px)

All pages collapse to single-column:

```
+---------------------------+
|  List Panel (full width)  |
|  (max-h-[40vh])          |
+---------------------------+
|  Detail: Mode-dependent   |
|  - sheet: bottom sheet    |
|  - overlay: fixed bottom  |
|  - navigate: route push   |
+---------------------------+
```

### Touch Target Requirements

Per WCAG 2.1 Success Criterion 2.5.5:

- Minimum touch target size: 44px x 44px
- Checkbox hit area: Extend padding to meet 44px minimum on mobile
- Delete buttons: Already using `size='icon'` which renders at 36px; increase to 44px on mobile via `sm:size-9 size-11`
- Filter dropdowns: Already `h-9` (36px); acceptable on desktop, increase trigger to `h-11` on mobile
- Slider handles (confidence range): 44px x 44px on mobile

### Spacing Adjustments

- Page padding: `p-4` on mobile, `p-6` on desktop (already implemented: `p-4 md:p-6`)
- Card internal padding: `p-3` on mobile, `p-4` on desktop
- Gap between elements: `gap-3` on mobile, `gap-4` on desktop
- BulkSelectionBar: `px-3 py-2` on mobile, `px-4 py-3` on desktop

---

## 6. Dark Mode

### Current State

The dashboard already has comprehensive dark mode support via CSS custom properties in `globals.css` using oklch color space. The `.dark` class toggles all semantic tokens. Theme variants (default, blue, green, amber, mono) each define their own dark overrides in `theme.css`.

### New CSS Custom Properties for Quarantine

The following custom properties are added at `@layer base` level, consistent with `CSS_CONVENTIONS.globalLayer`:

```
/* Light mode (in :root) */
--confidence-high: oklch(0.55 0.18 145);
--confidence-high-bg: oklch(0.55 0.18 145 / 10%);
--confidence-medium: oklch(0.70 0.15 80);
--confidence-medium-bg: oklch(0.70 0.15 80 / 10%);
--confidence-low: oklch(0.60 0.20 25);
--confidence-low-bg: oklch(0.60 0.20 25 / 10%);
--shadow-mode: oklch(0.55 0.15 290);
--shadow-mode-bg: oklch(0.55 0.15 290 / 10%);
--escalation-urgent: oklch(0.60 0.22 25);
--escalation-high: oklch(0.70 0.15 80);
--evidence-bg: oklch(0.97 0 0);
--evidence-border: oklch(0.90 0 0);

/* Dark mode (in .dark) */
--confidence-high: oklch(0.65 0.18 145);
--confidence-high-bg: oklch(0.65 0.18 145 / 15%);
--confidence-medium: oklch(0.75 0.15 80);
--confidence-medium-bg: oklch(0.75 0.15 80 / 15%);
--confidence-low: oklch(0.70 0.19 22);
--confidence-low-bg: oklch(0.70 0.19 22 / 15%);
--shadow-mode: oklch(0.65 0.15 290);
--shadow-mode-bg: oklch(0.65 0.15 290 / 15%);
--escalation-urgent: oklch(0.70 0.20 25);
--escalation-high: oklch(0.75 0.15 80);
--evidence-bg: oklch(0.22 0 0);
--evidence-border: oklch(0.30 0 0);
```

### Component-Specific Dark Mode Notes

#### Confidence Indicators

- `sm` (dot): Uses `--confidence-{level}` as `background-color`
- `md` (badge): Uses `--confidence-{level}-bg` as background, `--confidence-{level}` as text
- `lg` (bar): Bar track uses `bg-muted`. Fill segments use `--confidence-{level}`. Score text uses `--foreground`.

#### Evidence Panel

- Section backgrounds: `--evidence-bg` (slightly elevated from card background)
- Section borders: `--evidence-border`
- Code/email body container: `bg-muted` (already dark-mode aware)
- Link colors: `text-blue-500` in dark mode (currently hardcoded `text-blue-600` in quarantine -- needs update)

#### Approval Modal

- Field edit indicator (amber left border): Uses `--confidence-medium` which adjusts for dark mode
- Reject reason area: Uses `--destructive` background at 5% opacity

#### BulkSelectionBar

- Background: `bg-muted/50` (already dark-mode aware via `--muted` token)
- Border: `border-muted-foreground/20` (already dark-mode aware)

### Theme Variant Compatibility

All new custom properties use the achromatic/semantic approach. They do not conflict with the themed `--primary` overrides in `theme.css` (default, blue, green, amber, mono). The confidence colors are domain-specific and intentionally independent of the primary theme color.

---

## 7. Accessibility

### ARIA Labels

#### FilterDropdown
- Trigger: `aria-label="{label} filter"` (e.g., "Source type filter")
- Trigger: `aria-expanded` managed by Radix Select
- Options: `role="option"` with `aria-selected` (managed by Radix)

#### BulkSelectionBar
- Select-all checkbox: `aria-label="Select all {totalCount} items"` when unchecked, `aria-label="Deselect all {selectedCount} items"` when checked
- Action buttons: `aria-label="{action} {selectedCount} selected items"` (e.g., "Delete 3 selected items")
- Bar container: `role="toolbar"` with `aria-label="Bulk actions"`

#### ListDetailLayout
- List panel: `role="listbox"` with `aria-label="Item list"`
- Each list item: `role="option"` with `aria-selected={isSelected}`
- Detail panel: `role="region"` with `aria-label="Item detail"` and `aria-live="polite"` (announces when detail content changes)
- Mobile sheet: `role="dialog"` with `aria-label="Item detail"` (managed by Radix Sheet)

#### ConfirmDialog
- Dialog: `role="alertdialog"` (managed by Radix AlertDialog)
- Title: `aria-labelledby` linked to dialog title
- Description: `aria-describedby` linked to dialog description
- Confirm button: `aria-label="{confirmLabel}"` (explicit, not relying on visible text alone when loading spinner replaces text)

#### ConfidenceIndicator
- `sm` (dot): `aria-label="Confidence: {level}"` with `role="img"`
- `md` (badge): Text content is sufficient; no additional ARIA needed
- `lg` (bar): `role="meter"` with `aria-valuenow={score}`, `aria-valuemin={0}`, `aria-valuemax={1}`, `aria-label="Triage confidence"`

#### Evidence Panel
- Accordion sections: `aria-expanded` managed by Radix Collapsible
- Section headers: `aria-controls` linked to section content ID
- Email body container: `aria-label="Source email content"`

#### Approval Modal
- Editable fields: Each input has `<Label htmlFor>` association (already the pattern in quarantine page)
- Changed fields: `aria-description="Field value has been modified from the AI extraction"` on inputs where the operator has overridden the default
- Keyboard shortcut: Visible text hint, no hidden ARIA needed

#### Triage Summary Card
- Card container: `role="option"` with `aria-selected={selected}`
- Checkbox: `aria-label="Select item: {subject}"` (already implemented in current quarantine page)
- Delete button: `aria-label="Delete item: {subject}"`

### Keyboard Navigation

#### Approval Flow

| Key | Action | Context |
|-----|--------|---------|
| `Tab` | Move focus between fields | Within approval modal |
| `Shift+Tab` | Move focus backwards | Within approval modal |
| `Enter` | Submit current field / activate button | On focused button/input |
| `Ctrl+Enter` | Approve (keyboard shortcut) | Anywhere in approval modal |
| `Escape` | Close modal without action | Anywhere in approval modal |

#### List Navigation

| Key | Action | Context |
|-----|--------|---------|
| `ArrowDown` | Select next item in list | When list panel has focus |
| `ArrowUp` | Select previous item in list | When list panel has focus |
| `Space` | Toggle checkbox on focused item | When item has focus |
| `Enter` | Open item detail | When item has focus |
| `Home` | Jump to first item | When list panel has focus |
| `End` | Jump to last item | When list panel has focus |

#### BulkSelectionBar

| Key | Action | Context |
|-----|--------|---------|
| `Tab` | Move between checkbox, action buttons, clear | Within toolbar |
| `Enter` / `Space` | Activate focused control | On focused button/checkbox |

### Screen Reader Support

#### Confidence Indicators

- Screen readers announce: "Triage confidence: high, score 0.87" (via `aria-label`)
- The visual color encoding is supplemented by text labels -- color is never the sole differentiator
- The segmented bar in `size="lg"` uses `role="meter"` which screen readers announce as a value indicator

#### Live Regions

- Detail panel uses `aria-live="polite"` so screen readers announce content changes when a new item is selected
- Toast notifications (via Sonner) already have `role="status"` with `aria-live="polite"`
- BulkSelectionBar appearance/disappearance triggers an `aria-live="assertive"` announcement: "{N} items selected. Bulk actions available."

### Focus Management

#### Modal Open/Close
- When a modal opens (ApprovalModal, EscalateFlow, ConfirmDialog): Focus moves to the first focusable element inside the modal (managed by Radix)
- When a modal closes: Focus returns to the trigger element that opened it (managed by Radix)
- Focus trap is active while modal is open (managed by Radix)

#### List Item Removal
- When an item is approved/rejected/deleted and removed from the list:
  - If the removed item was selected, focus moves to the next item in the list
  - If no next item exists, focus moves to the previous item
  - If the list is now empty, focus moves to the empty state message

#### Mobile Sheet
- When the detail sheet opens on mobile: Focus moves into the sheet
- When the sheet closes: Focus returns to the selected list item

---

## 8. Implementation Notes

### Migration Path

The migration from current components to shared components follows a phased approach that avoids breaking changes.

#### Phase 2A: Extract and Create Shared Components

1. Create `components/shared/FilterDropdown.tsx` -- new component, no existing code changes
2. Create `components/shared/BulkSelectionBar.tsx` -- new component, no existing code changes
3. Create `components/shared/ListDetailLayout.tsx` -- new component, no existing code changes
4. Create `components/shared/ConfirmDialog.tsx` -- new component, no existing code changes
5. Export all from `components/shared/index.ts`

Each component has unit tests before any page adopts it.

#### Phase 2B: Quarantine Page Overhaul

1. Refactor `quarantine/page.tsx` to use `ListDetailLayout`, `FilterDropdown`, `BulkSelectionBar`, `ConfirmDialog`
2. Create quarantine-specific components: `ApprovalModal`, `EscalateFlow`, `ConfidenceIndicator`, `EvidencePanel`, `QuarantineFilterControls`, `TriageSummaryCard`
3. Add new CSS custom properties for confidence colors to `globals.css`
4. Add URL state persistence via `nuqs`

#### Phase 2C: Holistic Adoption (Other Pages)

1. **Deals page:** Replace Radix `Select` with `FilterDropdown`, replace inline bulk delete with `BulkSelectionBar`, replace `AlertDialog` with `ConfirmDialog`
2. **Actions page:** Replace Radix `Select` with `FilterDropdown`, replace inline bulk bar with `BulkSelectionBar`, replace `Dialog`-based confirmation with `ConfirmDialog`, refactor grid layout to `ListDetailLayout`
3. **Agent Activity page:** Add `FilterDropdown` for secondary filtering, add `ListDetailLayout` for event detail view, migrate URL state to `nuqs`
4. **Settings page:** Add `ConfirmDialog` for destructive operations

Each page migration is an independent PR that can be reviewed and merged separately.

### Recommended Implementation Order

1. `ConfirmDialog` -- simplest shared component, immediate value across all pages
2. `FilterDropdown` -- second simplest, standardizes a pattern used on 3 pages
3. `BulkSelectionBar` -- medium complexity, used on 3 pages
4. `ConfidenceIndicator` -- quarantine-specific, standalone
5. `TriageSummaryCard` -- quarantine-specific, depends on ConfidenceIndicator
6. `QuarantineFilterControls` -- quarantine-specific, composes FilterDropdown
7. `EvidencePanel` -- quarantine-specific, standalone
8. `ListDetailLayout` -- highest complexity, most pages affected
9. `ApprovalModal` -- quarantine-specific, depends on ConfidenceIndicator + EvidencePanel
10. `EscalateFlow` -- quarantine-specific, lowest priority

### Testing Considerations

#### Unit Tests (per component)

- **FilterDropdown:** Renders options, fires onChange, handles disabled state, renders "All" option, renders icon and badge
- **BulkSelectionBar:** Renders action buttons, checkbox state matches `selectionState`, fires onSelectAll/onClearSelection, hidden when selectedCount=0
- **ListDetailLayout:** Renders list and detail, shows empty state when detailContent is null, responsive class switching
- **ConfirmDialog:** Opens/closes, fires onConfirm, shows loading state, severity-based styling
- **ConfidenceIndicator:** Renders correct color for each threshold, renders correct size variant, screen reader text
- **TriageSummaryCard:** Renders item data, checkbox interaction, selection highlighting
- **QuarantineFilterControls:** Filter changes fire callbacks, clear button works, all filter types render
- **EvidencePanel:** Sections expand/collapse, renders all data sections, handles missing data gracefully
- **ApprovalModal:** Field editing, approve/reject flows, validation (operator name required), keyboard shortcuts
- **EscalateFlow:** Priority selection, reason dropdown, note required validation

#### E2E Tests (Playwright)

- **Quarantine full flow:** Load page, filter by source type, select item, review evidence, approve, verify toast + navigation
- **Quarantine bulk delete:** Select multiple items, confirm delete, verify items removed
- **Quarantine confidence filter:** Set confidence range, verify filtered results
- **Cross-page consistency:** Verify FilterDropdown looks/behaves the same on quarantine, deals, and actions pages
- **Responsive collapse:** Resize to mobile, verify ListDetailLayout collapses and sheet appears
- **Dark mode:** Toggle theme, verify confidence indicator colors, evidence panel theming

#### Visual Regression Tests

- Screenshot comparison at 375px, 768px, 1280px for quarantine page
- Screenshot comparison of confidence indicators in all three sizes, both themes
- Screenshot comparison of approval modal in light and dark mode

### Performance Implications

#### Lazy Loading

- **Evidence Panel:** The source email body can be large. The "Source Email" section of the evidence panel should lazy-load its content only when expanded. Use React `Suspense` + dynamic import or a simple `useEffect` trigger on collapsible open state.
- **Approval Modal:** Load modal content only when opened. Since it depends on `preview` data that is already loaded, the modal shell renders immediately but evidence summary re-renders on open.

#### Virtualization

- **Quarantine list:** Currently loads up to 200 items and renders all in a `ScrollArea`. For lists exceeding 100 items, implement virtual scrolling using `@tanstack/react-virtual` (already used in some Radix internals). The `TriageSummaryCard` height should be consistent (estimated 80px) for accurate virtual scroll calculations.
- **Evidence Panel links:** The link list already caps at 12 items per category with a "+N more" overflow. This is sufficient; no virtualization needed.

#### Bundle Size

- Shared components should be tree-shakeable via named exports from `components/shared/index.ts`
- No new external dependencies are introduced. All components use existing Radix primitives (Select, AlertDialog, Collapsible, Sheet) and Tabler icons that are already in the bundle.
- The `nuqs` migration for Actions and Agent Activity pages adds no new dependency (already in the bundle from Deals page).

#### Data Fetching

Per `DATA_FETCHING_CONVENTIONS.mandatoryPattern`, all quarantine data fetching continues to use `Promise.allSettled` with typed empty fallbacks. The new filter controls add query parameters to the existing `getQuarantineQueue` API call; they do not introduce additional network requests. Confidence and date filtering should be implemented server-side (backend API) to avoid fetching all 200 items and filtering client-side.

---

## Appendix A: File Location Plan

```
apps/dashboard/src/
  components/
    shared/
      index.ts                    -- barrel export
      FilterDropdown.tsx          -- shared filter component
      BulkSelectionBar.tsx        -- shared bulk selection component
      ListDetailLayout.tsx        -- shared split-pane layout
      ConfirmDialog.tsx           -- shared confirmation dialog
    quarantine/
      ApprovalModal.tsx           -- quarantine approval workflow
      EscalateFlow.tsx            -- quarantine escalation workflow
      ConfidenceIndicator.tsx     -- confidence score display
      EvidencePanel.tsx           -- classification evidence
      QuarantineFilterControls.tsx -- quarantine filter bar
      TriageSummaryCard.tsx       -- quarantine list item card
```

## Appendix B: Existing Component Reuse

| New Component | Builds On (existing) |
|--------------|---------------------|
| FilterDropdown | `ui/select.tsx` (Radix Select) |
| BulkSelectionBar | `ui/checkbox.tsx`, `ui/button.tsx` |
| ListDetailLayout | `ui/resizable.tsx`, `ui/card.tsx`, `ui/sheet.tsx` |
| ConfirmDialog | `ui/alert-dialog.tsx` |
| ApprovalModal | `ui/dialog.tsx`, `ui/input.tsx`, `ui/label.tsx` |
| EscalateFlow | `ui/dialog.tsx`, `ui/radio-group.tsx`, `ui/textarea.tsx` |
| ConfidenceIndicator | `ui/badge.tsx`, `ui/slider.tsx` (for bar variant reference) |
| EvidencePanel | `ui/collapsible.tsx`, `ui/scroll-area.tsx`, `ui/separator.tsx` |
| QuarantineFilterControls | FilterDropdown (shared), `ui/popover.tsx`, `ui/calendar.tsx`, `ui/slider.tsx` |
| TriageSummaryCard | `ui/checkbox.tsx`, `ui/badge.tsx`, `ui/button.tsx`, ConfidenceIndicator |

## Appendix C: Surface 9 Compliance Checklist

| Rule | Status | Notes |
|------|--------|-------|
| A1. Promise.allSettled mandatory | Compliant | No new data fetching patterns introduced; spec mandates server-side filtering |
| A2. console.warn for degradation | Compliant | No new error handling specified |
| A3. CSS at @layer base | Compliant | New custom properties added at @layer base |
| A4. Server-side counts | Compliant | No new client-side counting |
| A5. PIPELINE_STAGES source of truth | N/A | Quarantine does not use pipeline stages |
| A6. API proxy via middleware | Compliant | No new API routes |
| A7. Import from bridge files | Compliant | New components import from @/types/api |
| B1. Design thinking | Compliant | Industrial utilitarian direction defined |
| B2. Typography | Compliant | Uses existing Inter/mono system |
| B3. Color and theme | Compliant | Semantic oklch tokens, not hardcoded hex |
| B4. Motion | Compliant | GPU-composited, <400ms, prefers-reduced-motion |
| B5. Spatial composition | Compliant | Controlled density, purposeful layout |
| B6. Visual depth | Compliant | Card elevation, evidence panel nesting |
| B7. Anti-convergence | Compliant | Industrial utilitarian, segmented confidence bar, no generic dashboard aesthetics |
| C1. Responsive breakpoints | Compliant | Tailwind defaults, 3-width testing |
| C2. Z-index scale | Compliant | Modals at z-40, sheets at z-50 |
| C3. Dark mode | Compliant | CSS variables, semantic naming, both themes tested |
| C4. Animation performance | Compliant | GPU-composited only, prefers-reduced-motion |
| C5. State management | Compliant | URL state via nuqs, server state via API, local state for transient UI |

---

*End of Phase 2 Design Specification*

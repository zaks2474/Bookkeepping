# M10 Findings Closure

## F-15: Settings uses different layout pattern (Sev-3)

**Status:** CLOSED (Accepted Divergence + Mobile Fix)

**Finding:** Settings page uses its own layout with "Back to Dashboard" link and section nav instead of the main sidebar shell.

**Disposition:** The distinct layout is intentional and serves settings UX well (section-scoped anchor navigation vs page navigation). M-10 accepted the divergence and applied a mobile stacking fix.

**Fix Applied:**
- Changed `flex gap-8` → `flex flex-col lg:flex-row gap-6 lg:gap-8` in settings/page.tsx
- At mobile: dropdown nav stacks above content (was side-by-side, squeezing cards)
- At desktop: sidebar layout preserved with no regression
- IMAP form grids: `grid-cols-2` → `grid-cols-1 sm:grid-cols-2` for mobile readability
- Email connected-state: `flex` → `flex flex-col sm:flex-row` for badge/disconnect stacking

**Files Modified:**
- `apps/dashboard/src/app/settings/page.tsx`
- `apps/dashboard/src/components/settings/EmailSection.tsx`

**Evidence:** `f15-layout-disposition.md`, before/after screenshots

---

## F-16: Settings 404 errors and duplicate preferences fetch (Sev-2)

**Status:** CLOSED (Non-App / Correct Degraded Behavior)

**Finding:** Three 404 errors on settings page load + duplicate preferences fetch.

**Classification (confirmed from M-03):**
- **Duplicate fetch:** React 18 StrictMode dev-only double-mount. Production shows 1 request. No code fix needed.
- **404 on `/api/settings/email`:** Backend endpoint not yet implemented. EmailSection shows clear "not available" alert with admin contact guidance.
- **404 on `/api/settings/preferences`:** Backend endpoint not yet implemented. API route returns sensible defaults. User sees working settings page with default values.

**No code changes applied for F-16** — behavior is correct and truthful.

**Evidence:** `settings-fetch-behavior.md`

---

## New Deal Create-Flow (M-10 Scope)

**Status:** HARDENED

**Changes Applied:**
- Card: `max-w-lg` → `w-full max-w-lg` for consistent full-width at mobile
- Button row: `flex gap-2` → `flex flex-wrap gap-2` for overflow safety

**Evidence:** E2E tests verify form controls, validation, and cancel navigation at all breakpoints

---

## Summary

| Finding | Severity | Status | Disposition |
|---------|----------|--------|-------------|
| F-15 | Sev-3 | CLOSED | Accepted divergence + mobile fix |
| F-16 | Sev-2 | CLOSED | Non-app (StrictMode) + correct degraded UX |
| New Deal | — | HARDENED | Responsive + validation improvements |

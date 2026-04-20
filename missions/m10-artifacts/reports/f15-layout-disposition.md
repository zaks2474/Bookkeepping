# F-15 Layout Disposition

## Finding
F-15 (Sev-3): Settings page uses a different layout pattern than the main shell — no shared sidebar, has its own "Back to Dashboard" link and section nav.

## Disposition: ACCEPTED with Partial Convergence

### Rationale
The Settings page intentionally uses a dedicated layout pattern because:
1. **Different navigation model**: Settings uses section-scoped anchor navigation (6 sections via IntersectionObserver), not page navigation like the main sidebar
2. **Configuration density**: A full-width content area serves settings forms better than the main shell's narrower content column
3. **User context**: The "Back to Dashboard" escape hatch makes it clear the user has entered a configuration context, not a standard operational view

### Partial Convergence Applied (M-10)
While accepting the distinct layout, M-10 fixes the responsive stacking issue:
- **Before**: `flex gap-8` kept the mobile dropdown nav beside content at 375px, squeezing cards
- **After**: `flex flex-col lg:flex-row gap-6 lg:gap-8` stacks vertically at mobile, sidebar at desktop
- IMAP form grids changed from `grid-cols-2` to `grid-cols-1 sm:grid-cols-2` for mobile readability
- Email connected-state row stacks vertically at mobile for badge/disconnect accessibility

### Evidence
- Before: `m10-artifacts/before/settings-375.png` — dropdown and content side-by-side, card content squeezed
- After: `m10-artifacts/after/settings-375.png` — dropdown above content, full-width readable cards
- Desktop: `m10-artifacts/after/settings-1280.png` — sidebar layout preserved, no regression

### Decision
F-15 is CLOSED with "accepted divergence + mobile fix" disposition. No further convergence required.

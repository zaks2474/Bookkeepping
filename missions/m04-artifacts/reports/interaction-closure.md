# Interaction Closure Matrix — UI-MASTERPLAN-M04
**Date:** 2026-02-11
**Page:** `/chat`
**Status:** FINAL (Phase 2 complete)

## Chat Controls Inventory (10 controls from M-00)

| # | Control | Type | Wiring | 1280px | 768px | 375px | Disposition |
|---|---------|------|--------|--------|-------|-------|-------------|
| 1 | Settings gear icon | link → /settings | Real | Visible | Visible | Visible | real endpoint |
| 2 | Provider indicator (Local vLLM) | static | Real | Visible | Visible | Visible | real endpoint |
| 3 | Global/deal scope dropdown | combobox | Client-only | Visible | Visible | Visible | client-only |
| 4 | Deal filter dropdown | combobox | Real | Conditional (scope=deal) | Conditional | Conditional | real endpoint |
| 5 | History | button | Client-only (opens rail/sheet) | Visible | Visible (wrapped row) | **Via dropdown** | client-only |
| 6 | New Chat | button | Client-only | Visible | Visible (wrapped row) | **Via dropdown** | client-only |
| 7 | Evidence | button | Client-only (opens panel) | Visible | Visible (wrapped row) | **Via dropdown** | client-only |
| 8 | Debug | button | Client-only (opens panel) | Visible | Visible (wrapped row) | **Via dropdown** | client-only |
| 9 | Ask textbox | textbox | Real → /api/chat | Visible | Visible | Visible | real endpoint |
| 10 | Send button | button | Real → /api/chat | Visible | Visible | Visible | real endpoint |

**100% coverage: All 10 controls classified as `real endpoint` or `client-only`. Zero broken, zero mock, zero placeholder.**

## F-22 Resolution

### At 1280px (desktop)
- No change from baseline — all controls in one clean row
- Evidence: `after/chat-1280-toolbar.png`

### At 768px (tablet)
- Controls row uses `flex-wrap` — toolbar buttons wrap to second row naturally
- All 4 buttons (History, New Chat, Evidence, Debug) fully visible with labels
- No clipping, no title collision
- Evidence: `after/chat-768-toolbar.png`

### At 375px (mobile)
- History/New Chat/Evidence/Debug collapse into DropdownMenu ("..." trigger)
- All 4 actions accessible via dropdown with icons and labels
- History opens as slide-in Sheet (left side) instead of hidden side rail
- Provider + Scope + Dropdown trigger fit in single row
- Evidence: `after/chat-375-toolbar.png`, `after/chat-375-dropdown-open.png`, `after/chat-375-history-sheet.png`

## Interaction Replay Results

| Flow | 1280px | 768px | 375px |
|------|--------|-------|-------|
| Toggle History panel/sheet | PASS | PASS | PASS (Sheet) |
| Toggle Evidence panel | PASS | PASS | PASS (via dropdown) |
| Toggle Debug panel | PASS | PASS | PASS (via dropdown) |
| New Chat | PASS | PASS | PASS (via dropdown) |
| Scope switch (Global/Deal) | PASS | PASS | PASS |
| Input + Send (disabled state) | PASS | PASS | PASS |
| Provider indicator truthful | PASS (green=connected) | PASS | PASS |
| Error display + Retry | N/A (no error triggered) | N/A | N/A |

## Degraded Truthfulness

- **Provider indicator**: Green dot = connected, Red dot = error, Yellow = checking. Real `/api/chat` health check every 30s. Truthful.
- **Evidence panel**: "Evidence will appear here after you send a message" — accurate empty state. No fake data.
- **Debug panel**: Shows "Session: none, Messages: 0" — accurate initial state.
- **Send button**: Disabled when input empty or loading — prevents invalid submissions. Truthful.

## Console Hygiene
- **Errors:** 0 at all breakpoints
- **Warnings:** 2 (Radix aria-describedby for Sheet — fixed with sr-only SheetDescription)

## Fix Implementation Summary
1. Added `flex-wrap` to controls container for natural wrapping at intermediate sizes
2. Toolbar buttons split: `hidden md:flex` (desktop) / `md:hidden` DropdownMenu (mobile)
3. History rail: Sheet component on mobile via `useIsMobile()` hook (existing project pattern)
4. Scope selector width: `w-[110px] md:w-[130px]` for mobile fit
5. Deal selector width: `w-[160px] md:w-[200px]` for mobile fit
6. SheetDescription added for ARIA compliance

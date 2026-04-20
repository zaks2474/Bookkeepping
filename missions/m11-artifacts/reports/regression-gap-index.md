# Regression Gap Index — M-11
**Date:** 2026-02-11

## Existing E2E Coverage (23 spec files)

### Per-Route Coverage

| Route | Dedicated Files | Breakpoint Triad | Finding Coverage | Gap Level |
|-------|----------------|-------------------|------------------|-----------|
| /dashboard | 3 | 375/768/1280 | F-19, F-20 | NONE |
| /deals | 2 | 375/768/1280 | F-21 | NONE |
| /deals/[id] | 3 | 375/768/1280 | F-08, F-09, F-10 | NONE |
| /deals/new | 2 | 375/768/1280 | M-10 | NONE |
| /actions | 2 | 375/768/1280 | F-11, F-12 | NONE |
| /quarantine | 2 | 375/768/1280 | F-13 | NONE |
| /chat | 3 | 375/768/1280 | F-22 | NONE |
| /settings | 1 | 375/768/1280 | F-15, F-16 | NONE |
| /onboarding | 1 | 375/768/1280 | F-17, F-18 | NONE |
| /hq | 1 | 375/768/1280 | F-14 | NONE |
| /agent/activity | 1 | 375/768/1280 | F-23 | MINOR |

### Cross-Cutting Coverage

| Category | Files | Status |
|----------|-------|--------|
| Smoke/load | smoke.spec.ts | EXISTS |
| Dead UI detection | no-dead-ui.spec.ts | EXISTS |
| Graceful degradation | graceful-degradation.spec.ts | EXISTS |
| Backend liveness | backend-up.spec.ts | EXISTS |
| Phase coverage | phase-coverage.spec.ts | EXISTS |

### Identified Gaps for M-11

| Gap | Priority | Resolution |
|-----|----------|------------|
| No cross-page JOURNEY tests | HIGH | Create cross-page-integration-flows.spec.ts |
| No consolidated responsive regression | HIGH | Create responsive-regression.spec.ts (all routes in one file) |
| No visual baseline archive | MEDIUM | Create visual-regression.spec.ts with screenshots |
| /agent/activity limited depth | LOW | Enhance in responsive-regression.spec.ts |

### Permanent Suite Scope (to be created in Phase 2)

1. **responsive-regression.spec.ts**: All 11 routes × 3 breakpoints = 33 test cases
   - Each route: verify page loads, key heading visible, primary controls accessible
   - Focus on preventing recurrence of F-08 through F-23 responsive regressions

2. **visual-regression.spec.ts**: Screenshot baselines for all routes
   - 11 routes × 3 breakpoints = 33 screenshots
   - Deterministic naming: `{route}-{viewport}px.png`
   - Archived in m11-artifacts/after/ for future diffing

3. **cross-page-integration-flows.spec.ts**: Journey A/B/C
   - Sequential navigation with state continuity assertions
   - Console error audit between transitions

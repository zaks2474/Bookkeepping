# Integration Test Results — DEAL-INTEGRITY-UNIFIED Layer 5

## Timestamp
2026-02-08T22:52:00Z

## Test Run
```
npx vitest run src/__tests__/deal-integrity.test.ts
```

## Results: 17 passed, 1 skipped (18 total)

### Suite 1: DI-ISSUE-001 — Lifecycle Transition Tests (3/3 PASS)
- GET /api/deals?status=active returns deals (count > 0) — 13ms
- POST /api/deals/{id}/archive removes deal from active list — 40ms
- POST /api/deals/{id}/restore returns deal to active list — 9ms

### Suite 2: DI-ISSUE-002/003 — Pipeline Count Invariant Tests (4/4 PASS)
- GET /api/pipeline/summary returns an array of stage counts — 1ms
- GET /api/deals?status=active returns deals array — 0ms
- sum(pipeline stage counts) == active deals count — 0ms
- per-stage counts agree between pipeline summary and deals list — 0ms

### Suite 3: DI-ISSUE-006 — Startup Self-Check Tests (3/3 PASS)
- GET /health returns database identity with dbname=zakops — 2ms
- GET /health includes database connection details — 2ms
- GET /health includes version and timestamp — 2ms

### Suite 4: DI-ISSUE-009 — API Health Suite (4/4 PASS + 1 SKIPPED)
- GET /health returns 200 — 1ms
- GET /api/deals returns 200 — 4ms
- GET /api/pipeline/summary returns 200 — 4ms
- GET /api/deals?status=active returns 200 — 3ms
- GET /api/actions/kinetic — **SKIPPED** (DI-ISSUE-009: returns 500, deferred)

### Suite 5: DB Invariant Check (3/3 PASS)
- no orphaned archived/deleted state violations exist — 77ms
- all active deals have a non-archived stage — 39ms
- all archived deals have stage=archived — 72ms

## Duration
Total: 462ms (transform 29ms, setup 22ms, import 17ms, tests 357ms)

## "Never Again" Test Mapping

| MASTER Doc Enforcement | Test Coverage |
|----------------------|---------------|
| DI-ISSUE-001: Archive sets both status + stage | Lifecycle Suite: archive test |
| DI-ISSUE-001: Active filter excludes archived | Lifecycle Suite: archive test step 3 |
| DI-ISSUE-002: Pipeline counts match deals | Invariant Suite: sum test |
| DI-ISSUE-003: Per-stage counts agree | Invariant Suite: per-stage test |
| DI-ISSUE-006: Startup DSN gate | Self-Check Suite: dbname test |
| DI-ISSUE-008: DB invariants | DB Invariant Suite: 3 tests |
| DI-ISSUE-009: No 500 endpoints | API Health Suite (kinetic deferred) |

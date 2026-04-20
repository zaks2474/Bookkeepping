# LANGSMITH-INTAKE-HARDEN-001 — Completion Report

**Date:** 2026-02-13
**Status:** COMPLETE
**Phases:** 7 (0-6), all PASS
**Acceptance Criteria:** 6/6 PASS

---

## Summary

Hardened the email injection pipeline for LangSmith integration safety. Resolved 7 gaps discovered during builder-level forensic investigation of the quarantine intake path. This was a FIX mission — wiring, enforcing, and closing gaps in existing infrastructure.

---

## Acceptance Criteria Results

### AC-1: Canonical Truth — PASS
- **Evidence:** `context_pack.py` — `_get_deal_from_db()` queries `zakops.deals` via asyncpg (replaced `_load_deal_registry()` + `_get_deal_from_registry()`)
- **Evidence:** `actions_runner.py` — `_get_deal_from_db()` queries `zakops.deals` via asyncpg (replaced `registry.get_deal()`)
- **Evidence:** `chat_evidence_builder.py` — `_fetch_registry()` queries `zakops.deals` via asyncpg (replaced JSON file read)
- **Verification:** Grep for `deal_registry.json` in all three files returns 0 truth-read hits

### AC-2: Injection Auth — PASS
- **Evidence:** `apikey.py` — `INJECTION_PATHS = ("/api/quarantine",)` with fail-closed 503 when `ZAKOPS_API_KEY` is unset
- **Verification:** Injection paths return 503 (not silently open) when API key is not configured

### AC-3: Measurement Capability — PASS
- **Evidence:** `main.py` quarantine POST — returns 200 for dedup hits, 201 for new creates (dynamic `response.status_code`)
- **Evidence:** `main.py` quarantine GET — accepts `source_type` query parameter for filtering
- **Evidence:** Dashboard `quarantine/page.tsx` — source_type dropdown filter in header
- **Evidence:** Dashboard `api/actions/quarantine/route.ts` — forwards `source_type` query param to backend
- **Evidence:** Dashboard `lib/api.ts` — `getQuarantineQueue()` accepts `source_type` parameter

### AC-4: Correlation Chain — PASS
- **Evidence:** `main.py` process_quarantine handler — outbox INSERT uses `item.get('correlation_id')` instead of `gen_random_uuid()`
- **Evidence:** Fallback to `str(uuid.uuid4())` when quarantine item has no correlation_id (legacy items)

### AC-5: Flood Protection — PASS
- **Evidence:** `security.py` — `injection_rate_limiter = RateLimiter(requests_per_minute=120)`
- **Evidence:** `main.py` quarantine POST — `check_rate_limit(f"quarantine:{client_ip}", limiter=injection_rate_limiter)` at handler top
- **Verification:** Exceeding 120/min returns HTTP 429 with Retry-After header

### AC-6: Documentation — PASS
- **Evidence:** `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` — covers endpoint, auth, rate limits, response codes, correlation behavior, source_type values

---

## Phase Execution Summary

| Phase | Name | Status | Files Modified |
|-------|------|--------|---------------|
| 0 | Discovery & Baseline | PASS | 0 (read-only) |
| 1 | Canonical Truth Enforcement | PASS | 3 (context_pack.py, actions_runner.py, chat_evidence_builder.py) |
| 2 | Injection Security | PASS | 1 (apikey.py) |
| 3 | Ingest Contract Measurement | PASS | 4 (main.py, quarantine/page.tsx, route.ts, api.ts) |
| 4 | Correlation ID End-to-End | PASS | 1 (main.py) |
| 5 | Flood Protection | PASS | 2 (security.py, main.py) |
| 6 | Documentation & Verification | PASS | 3 (INJECTION-CONTRACT.md, CHANGES.md, this report) |

---

## Validation Results

- `npx tsc --noEmit`: PASS (zero errors)
- `make validate-local`: PASS (all gates green)
- Boot diagnostics: ALL CLEAR (6/6 checks pass)

---

## Files Modified (Complete List)

### Backend (`/home/zaks/zakops-backend/`)
| File | Changes |
|------|---------|
| `src/actions/context/context_pack.py` | Replaced JSON registry reads with PostgreSQL queries via asyncpg |
| `src/workers/actions_runner.py` | Replaced JSON registry deal lookup with PostgreSQL query via asyncpg |
| `src/core/chat_evidence_builder.py` | Replaced JSON registry fetch with PostgreSQL query via asyncpg |
| `src/api/shared/middleware/apikey.py` | Added INJECTION_PATHS fail-closed behavior (503 when key unset) |
| `src/api/shared/security.py` | Added `injection_rate_limiter` (120/min) |
| `src/api/orchestration/main.py` | Quarantine POST: dynamic 200/201, rate limiting, source_type filter on GET, correlation ID forwarding to outbox |
| `docs/INJECTION-CONTRACT.md` | NEW — injection contract documentation |

### Dashboard (`/home/zaks/zakops-agent-api/apps/dashboard/`)
| File | Changes |
|------|---------|
| `src/app/quarantine/page.tsx` | Added source_type filter dropdown UI |
| `src/app/api/actions/quarantine/route.ts` | Forward source_type param to backend, pass source_type in response |
| `src/lib/api.ts` | Added source_type parameter to getQuarantineQueue |

---

## Gaps Closed

| # | Gap | Resolution |
|---|-----|-----------|
| G1 | Split-brain JSON truth | PostgreSQL queries replace all JSON reads (3 files) |
| G2 | Conditional auth | Fail-closed 503 on injection paths when key unset |
| G3 | Same HTTP status for create/dedup | 201 for new, 200 for dedup |
| G4 | Cosmetic-only shadow mode | source_type filter at API + dashboard UI |
| G5 | Correlation ID break at outbox | Original correlation_id forwarded to outbox INSERT |
| G6 | Rate limiter unwired | injection_rate_limiter (120/min) wired to quarantine POST |
| G7 | No retry docs | Documented in INJECTION-CONTRACT.md |

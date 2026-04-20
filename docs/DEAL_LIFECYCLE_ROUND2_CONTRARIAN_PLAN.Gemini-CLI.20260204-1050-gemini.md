# ZAKOPS ROUND-2 CONTRARIAN DESIGN & HARDENING MISSION
## Codename: ROUND2-CONTRARIAN-V2
## Classification: STRATEGIC — Design-Stage Excellence + Execution-Ready Plan

AGENT IDENTITY
- agent_name: Gemini-CLI
- run_id: 20260204-1050-gemini
- date_time: 2026-02-04T10:50:00Z
- repo_revision: unknown (git not active)
- dashboard_zod_errors_checked: true

---

## 1. EXECUTIVE SUMMARY: THE "SOFT PASS" ILLUSION

The previous QA verification (QA-006) marked the system as "PASS". **This is a dangerous illusion.**

While the backend (Layer 3) has improved, the frontend integration (Layer 4) is built on **conflicting, lossy, and hand-duplicated contracts** that are actively hiding data from the user.

**The Smoking Gun:**
The Dashboard maintains **TWO** separate definitions of `DealSchema`:
1.  **The Good Schema** (`src/lib/api-schemas.ts`): Matches the backend, includes `company_info`, `metadata`, and structured `broker`. **UNUSED.**
2.  **The Bad Schema** (`src/lib/api-client.ts`): Actually used by `getDeals()`. **STRIPS DATA.** It flattens `broker` to a string, ignores `company_info` and `metadata`, and expects `priority` at the root (where it doesn't exist).

**Result:** The "PASS" verdict was based on `curl` tests. Real users see a dashboard that is functionally lobotomized, incapable of displaying the rich data the backend is successfully serving.

---

## 2. SCORECARD (CURRENT VS TARGET)

| Layer | Current | Target | Gap Analysis |
|-------|:-------:|:------:|--------------|
| **1. Architecture** | 7 | 9 | Planes are separated, but frontend has internal "split brain" on schemas. |
| **2. Data Integrity** | 8 | 10 | Postgres is SOT. Legacy code still lurks (`sys.path` hacks). |
| **3. API Contracts** | 8 | 10 | Backend Pydantic models are solid. OpenAPI exists. |
| **4. Client Integration** | **3** | 10 | **CRITICAL FAILURE.** Duplicate schemas. `api-client.ts` redefines models poorly. Data loss at UI boundary. |
| **5. Observability** | 6 | 9 | `TraceMiddleware` exists, but client-side tracing is weak. No logs correlation confirmed in UI. |
| **6. Security** | 7 | 9 | Auth middleware exists. RBAC is basic. |
| **7. UX Correctness** | 5 | 9 | "Safe" parsing hides bugs. UI likely shows empty fields where data exists. |
| **8. Email Ingestion** | 8 | 9 | Pipeline is solid, but quarantine integration needs "at-least-once" guarantee. |
| **9. RAG/Knowledge** | 4 | 9 | `search_deals` tool depends on unverified service. No freshness guarantees. |
| **10. Ops Excellence** | 6 | 9 | Deployment is manual. No contract tests in CI. |

---

## 3. CONTRARIAN UPGRADE REGISTER

### **ZK-UPG-0001: Unified Generated Client (Kill the "Bad Schema")**
**Why:** We have two sources of truth in the frontend. One is wrong.
**Current:** `api-client.ts` manually redefines `DealSchema` (poorly). `api-schemas.ts` defines it correctly (unused).
**Target:** **DELETE BOTH.** Generate a TypeScript client (`openapi-typescript-codegen`) directly from the Backend OpenAPI spec.
**Verification:** CI fails if backend changes without client regen.

### **ZK-UPG-0002: Idempotency-Key on Writes**
**Why:** Double-clicking "Create Deal" creates two deals.
**Current:** Backend has `idempotency_key` in *some* docs, but `create_deal` endpoint implementation shows standard `INSERT` without key check.
**Target:** `Idempotency-Key` header enforced on all POST/PUT. Middleware checks `idempotency_store` table.
**Verification:** Replay attack test returns 200 (cached), not 409/500/201 (new).

### **ZK-UPG-0003: Transactional Outbox for Side-Effects**
**Why:** If `record_deal_event` fails, the deal is still created (or vice versa depending on transaction scope), but notifications are lost.
**Current:** Direct DB calls in routers.
**Target:** Write events to `outbox` table in same transaction. Relay worker processes them.

### **ZK-UPG-0004: Frontend Contract Testing**
**Why:** Zod `safeParse` returns `{ success: false }` and we just log it. The UI renders empty tables. This is "silent failure."
**Current:** `console.error` in `api-client.ts`.
**Target:** CI job: `backend` + `frontend` integration test. If `safeParse` fails on *any* fixture, BUILD FAILS.

### **ZK-UPG-0005: RAG Health Circuit Breaker**
**Why:** Agent tool `search_deals` calls port 8052 blind. If down, agent crashes or hallucinates.
**Current:** Direct HTTP call.
**Target:** Circuit breaker wrapper. If RAG down, fallback to SQL `ILIKE` search or fail gracefuly.

---

## 4. ROUND-2 EXECUTION PLAN

### **Phase R2-0: Forensic Baseline (Completed)**
*   Evidence collected: `api-client.ts` vs `main.py` mismatch confirmed.
*   Verdict: **FAIL** (Layer 4).

### **Phase R2-1: The "Schema Unification" Refactor (P0)**
**Objective:** Eradicate duplicate schemas.
1.  **Delete** the manual schema definitions in `api-client.ts`.
2.  **Import** the robust schemas from `api-schemas.ts`.
3.  **Fix** `api-schemas.ts` to match Pydantic exactly (e.g., handle `priority` nesting).
4.  **Update** `api-client.ts` to use `DealsResponseSchema` from `api-schemas.ts`.

### **Phase R2-2: Idempotency Implementation (P1)**
**Objective:** Prevent duplicate deals/actions.
1.  Add `idempotency_keys` table (key, response_body, status, expiry).
2.  Add `IdempotencyMiddleware` to backend.
3.  Update Dashboard `apiFetch` to inject `Idempotency-Key` (UUID v4) on POST.

### **Phase R2-3: Data Visibility Restoration (P1)**
**Objective:** Reveal the hidden data.
1.  Update Dashboard `DealCard` and `DealRow` components to display `company_info.sector`, `metadata.asking_price`, and `broker` details.
2.  Stop coercing `broker` object to string in the API layer; let the UI decide how to render it.

### **Phase R2-4: CI Contract Gate (P2)**
**Objective:** Prevent regression.
1.  Create `tests/contracts/verify_schemas.ts`.
2.  Script: Start backend, hit `/api/deals`, validate response against `api-schemas.ts`.
3.  Add to `github-actions` (or local `make test`).

---

## 5. ADVERSARIAL SCENARIOS (Testing the Plan)

| ID | Scenario | Current Result | Expected (Post-Fix) |
|----|----------|----------------|---------------------|
| **ADV-01** | Backend sends `broker: {name: "John"}` | Client coerces to `"John"` (data loss: email/company) | Client receives full object |
| **ADV-02** | Backend sends `priority` in `metadata` | Client ignores it (expects root) | Client reads `metadata.priority` |
| **ADV-03** | User double-clicks "Create" | 2 Deals created | 1 Deal created, 2nd request returns 200 |
| **ADV-04** | Agent searches deals while RAG down | Exception/Crash | Graceful fallback / "Search unavailable" |

---

## 6. FINAL VERDICT

The system is **functionally correct** in the backend but **integration-broken** in the frontend. The "Soft PASS" on Zod schemas was incorrect; there is significant data loss at the API boundary.

**Recommendation:** Proceed immediately with **Phase R2-1** (Schema Unification).

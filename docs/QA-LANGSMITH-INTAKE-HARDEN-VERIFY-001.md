> **POST-CONSOLIDATION NOTE (2026-02-16):** This document references `/home/zaks/zakops-backend/` paths.
> Backend is now at `/home/zaks/zakops-agent-api/apps/backend/` (MONOREPO-CONSOLIDATION-001).
> See `POST-CONSOLIDATION-PATH-MAPPING.md` for the full path translation table.

# QA MISSION: QA-LANGSMITH-INTAKE-HARDEN-VERIFY-001
## Deep Code-Level Verification — Injection Pipeline Hardening
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: LANGSMITH-INTAKE-HARDEN-001 complete (7 phases, 6 AC)
## Auditor: Claude Code (Opus 4.6)

---

## 1. Mission Objective

This is an **independent, deep code-level verification** of LANGSMITH-INTAKE-HARDEN-001. The completion report claims 7 gaps closed across 10 files. This QA:

1. **Verifies every claim at the source line level** — not just grepping for keywords, but reading the actual code paths to confirm correctness.
2. **Hunts for residual split-brain patterns** — the completion report claims JSON registry reads are eliminated, but preliminary exploration found stale constants and constructor defaults that still reference JSON files.
3. **Validates security properties end-to-end** — fail-closed auth, rate limiting wiring, correlation chain integrity.
4. **Checks dashboard integration completeness** — source_type dropdown, parameter forwarding, API client wiring.

**What this is NOT**: This is not a build mission. No new code is written unless remediating a FAIL gate. Every PASS requires tee'd evidence.

### Source Artifacts

| Artifact | Path | Key Content |
|----------|------|-------------|
| Completion Report | `/home/zaks/bookkeeping/docs/_qa_evidence/LANGSMITH-INTAKE-HARDEN-001-COMPLETION.md` | 7 gaps, 6 AC, 10 files |
| Injection Contract | `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` | Endpoint spec, auth, rate limits, source_type |
| Backend main.py | `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Quarantine POST/GET (2098 lines) |
| API Key Middleware | `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` | INJECTION_PATHS, fail-closed (56 lines) |
| Security Module | `/home/zaks/zakops-backend/src/api/shared/security.py` | Rate limiters (232 lines) |
| Context Pack | `/home/zaks/zakops-backend/src/actions/context/context_pack.py` | Deal lookups (523 lines) |
| Actions Runner | `/home/zaks/zakops-backend/src/workers/actions_runner.py` | Deal lookups (776 lines) |
| Chat Evidence Builder | `/home/zaks/zakops-backend/src/core/chat_evidence_builder.py` | Deal lookups (564 lines) |
| Dashboard Quarantine | `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | Source type filter (823 lines) |
| Dashboard Route | `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts` | Param forwarding (102 lines) |
| Dashboard API | `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | getQuarantineQueue (2416 lines) |

### Evidence Directory

```
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-harden-verify-001
```

All evidence files are written to this directory via `| tee $EVIDENCE_DIR/<gate>.txt`.

---

## 2. Pre-Flight

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-harden-verify-001
mkdir -p "$EVIDENCE_DIR"
```

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee "$EVIDENCE_DIR/PF-1-validate-local.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0. If not, stop.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee "$EVIDENCE_DIR/PF-2-tsc.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0, zero errors.

### PF-3: Backend Container Alive
```bash
curl -sf http://localhost:8091/health 2>&1 | tee "$EVIDENCE_DIR/PF-3-backend-health.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0, JSON healthy. If down, live gates (VF-07, VF-13) become SKIP(services-down).

### PF-4: Source Artifacts Exist
```bash
for f in \
  "/home/zaks/bookkeeping/docs/_qa_evidence/LANGSMITH-INTAKE-HARDEN-001-COMPLETION.md" \
  "/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md"; do
  test -f "$f" && echo "EXISTS: $f" || echo "MISSING: $f"
done 2>&1 | tee "$EVIDENCE_DIR/PF-4-artifacts.txt"
```
**PASS if:** Both files exist.

### PF-5: Evidence Directory Ready
```bash
test -d "$EVIDENCE_DIR" && echo "EVIDENCE_DIR ready" | tee "$EVIDENCE_DIR/PF-5-dir-ready.txt"
ls -la "$EVIDENCE_DIR/" | tee -a "$EVIDENCE_DIR/PF-5-dir-ready.txt"
```
**PASS if:** Directory exists and is writable.

---

## 3. Verification Families

### VF-01 — G1 Canonical Truth: context_pack.py — 4 checks

**Context:** Completion report claims `context_pack.py` replaced `_load_deal_registry()` + `_get_deal_from_registry()` with `_get_deal_from_db()` using asyncpg.

#### VF-01.1: `_get_deal_from_db()` function exists and uses asyncpg
```bash
grep -n "async def _get_deal_from_db\|def _get_deal_from_db\|import asyncpg\|await asyncpg" /home/zaks/zakops-backend/src/actions/context/context_pack.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-1.txt"
```
**PASS if:** Function exists AND asyncpg is imported AND used (await asyncpg.connect).

#### VF-01.2: No `deal_registry.json` or `_load_deal_registry` references
```bash
grep -n "deal_registry.json\|_load_deal_registry\|_get_deal_from_registry\|\.deal-registry" /home/zaks/zakops-backend/src/actions/context/context_pack.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-2.txt"
STALE=$(grep -c "deal_registry.json\|_load_deal_registry\|_get_deal_from_registry\|\.deal-registry" /home/zaks/zakops-backend/src/actions/context/context_pack.py 2>/dev/null) || STALE=0
echo "STALE_REGISTRY_REFS=$STALE" | tee -a "$EVIDENCE_DIR/VF-01-2.txt"
```
**PASS if:** STALE_REGISTRY_REFS is 0.

#### VF-01.3: `_get_deal_from_db()` queries `zakops.deals`
```bash
grep -n -A15 "def _get_deal_from_db" /home/zaks/zakops-backend/src/actions/context/context_pack.py 2>&1 | head -20 | tee "$EVIDENCE_DIR/VF-01-3.txt"
grep -c "zakops\.deals" /home/zaks/zakops-backend/src/actions/context/context_pack.py 2>/dev/null | tee -a "$EVIDENCE_DIR/VF-01-3.txt"
```
**PASS if:** Function body contains `zakops.deals` SQL query. The query must target the canonical PostgreSQL table, not a JSON file.

#### VF-01.4: `_get_deal_from_db()` is actually CALLED in the main code path
```bash
grep -n "_get_deal_from_db\|get_deal_from_db" /home/zaks/zakops-backend/src/actions/context/context_pack.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-4.txt"
```
**PASS if:** Function is called at least once outside its definition (i.e., not just defined but never invoked). Look for call sites in the deal context building flow.

**Gate VF-01:** All 4 checks pass. context_pack.py reads from PostgreSQL, not JSON.

---

### VF-02 — G1 Canonical Truth: actions_runner.py — 5 checks

**Context:** Completion report claims `actions_runner.py` replaced `registry.get_deal()` with `_get_deal_from_db()` using asyncpg.

#### VF-02.1: `_get_deal_from_db()` function exists and uses asyncpg
```bash
grep -n "async def _get_deal_from_db\|def _get_deal_from_db\|import asyncpg\|await asyncpg" /home/zaks/zakops-backend/src/workers/actions_runner.py 2>&1 | tee "$EVIDENCE_DIR/VF-02-1.txt"
```
**PASS if:** Function exists AND asyncpg is imported AND used.

#### VF-02.2: No `registry.get_deal()` calls in active code
```bash
grep -n "registry\.get_deal\|registry\.get(" /home/zaks/zakops-backend/src/workers/actions_runner.py 2>&1 | tee "$EVIDENCE_DIR/VF-02-2.txt"
ACTIVE_REG=$(grep -c "registry\.get_deal\|registry\.get(" /home/zaks/zakops-backend/src/workers/actions_runner.py 2>/dev/null) || ACTIVE_REG=0
echo "ACTIVE_REGISTRY_CALLS=$ACTIVE_REG" | tee -a "$EVIDENCE_DIR/VF-02-2.txt"
```
**PASS if:** ACTIVE_REGISTRY_CALLS is 0.

#### VF-02.3: STALE constants — `REGISTRY_PATH` and `CASE_FILES_DIR` still defined
```bash
grep -n "REGISTRY_PATH\|CASE_FILES_DIR\|deal_registry\.json\|\.deal-registry" /home/zaks/zakops-backend/src/workers/actions_runner.py 2>&1 | tee "$EVIDENCE_DIR/VF-02-3.txt"
STALE_CONST=$(grep -c "REGISTRY_PATH\|CASE_FILES_DIR" /home/zaks/zakops-backend/src/workers/actions_runner.py 2>/dev/null) || STALE_CONST=0
echo "STALE_CONSTANT_COUNT=$STALE_CONST" | tee -a "$EVIDENCE_DIR/VF-02-3.txt"
```
**FAIL if:** STALE_CONSTANT_COUNT > 0. These constants are dead code that reference the JSON file system. They should have been removed as part of the canonical truth migration. Classification: **RESIDUAL_ARTIFACT** — stale constants that create risk of accidental reversion.

#### VF-02.4: `_get_deal_from_db()` queries `zakops.deals`
```bash
grep -n -A15 "def _get_deal_from_db" /home/zaks/zakops-backend/src/workers/actions_runner.py 2>&1 | head -20 | tee "$EVIDENCE_DIR/VF-02-4.txt"
```
**PASS if:** Function body contains `zakops.deals` SQL query.

#### VF-02.5: `_get_deal_from_db()` is called in the action execution path
```bash
grep -n "_get_deal_from_db" /home/zaks/zakops-backend/src/workers/actions_runner.py 2>&1 | tee "$EVIDENCE_DIR/VF-02-5.txt"
```
**PASS if:** Function is called at least once outside its definition.

**Gate VF-02:** Checks 1, 2, 4, 5 must PASS. Check 3 is expected FAIL (stale constants). Gate passes with 1 remediation needed.

---

### VF-03 — G1 Canonical Truth: chat_evidence_builder.py — 5 checks

**Context:** Completion report claims `chat_evidence_builder.py` replaced JSON file reads with `_fetch_registry()` using asyncpg. Preliminary exploration found the constructor STILL accepts a `registry_path` parameter.

#### VF-03.1: `_fetch_registry()` function exists and uses asyncpg
```bash
grep -n "async def _fetch_registry\|def _fetch_registry\|import asyncpg\|await asyncpg" /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>&1 | tee "$EVIDENCE_DIR/VF-03-1.txt"
```
**PASS if:** Function exists AND asyncpg imported AND used.

#### VF-03.2: `_fetch_registry()` queries `zakops.deals`
```bash
grep -n -A15 "def _fetch_registry" /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>&1 | head -25 | tee "$EVIDENCE_DIR/VF-03-2.txt"
```
**PASS if:** Function body contains `zakops.deals` SQL query.

#### VF-03.3: Constructor still accepts `registry_path` parameter (SPLIT-BRAIN BUG)
```bash
grep -n "registry_path\|deal_registry.json\|\.deal-registry" /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>&1 | tee "$EVIDENCE_DIR/VF-03-3.txt"
SPLIT_BRAIN=$(grep -c "registry_path\|deal_registry\.json" /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>/dev/null) || SPLIT_BRAIN=0
echo "SPLIT_BRAIN_REFS=$SPLIT_BRAIN" | tee -a "$EVIDENCE_DIR/VF-03-3.txt"
```
**FAIL if:** SPLIT_BRAIN_REFS > 0. The constructor should not accept a `registry_path` parameter if the canonical truth is PostgreSQL. This creates a code path where a caller could instantiate the class with a JSON file path. Classification: **RESIDUAL_ARTIFACT** — legacy constructor parameter that should have been removed.

#### VF-03.4: Legacy file path attributes (case_files_dir, events_dir, actions_path)
```bash
grep -n "case_files_dir\|events_dir\|actions_path\|self\.registry_path\|DataRoom" /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>&1 | tee "$EVIDENCE_DIR/VF-03-4.txt"
LEGACY_ATTRS=$(grep -c "self\.case_files_dir\|self\.events_dir\|self\.actions_path\|self\.registry_path" /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>/dev/null) || LEGACY_ATTRS=0
echo "LEGACY_ATTR_COUNT=$LEGACY_ATTRS" | tee -a "$EVIDENCE_DIR/VF-03-4.txt"
```
**FAIL if:** LEGACY_ATTR_COUNT > 0 AND those attributes reference `.deal-registry` file paths. Classification: **RESIDUAL_ARTIFACT**.

#### VF-03.5: `_fetch_registry()` is called (not dead code)
```bash
grep -n "_fetch_registry" /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>&1 | tee "$EVIDENCE_DIR/VF-03-5.txt"
```
**PASS if:** Function is called at least once outside its definition.

**Gate VF-03:** Checks 1, 2, 5 must PASS. Checks 3 and 4 are expected FAIL (residual split-brain artifacts).

---

### VF-04 — G1 Global Split-Brain Sweep — 3 checks

**Context:** The completion report claims JSON registry reads are eliminated in 3 files. But are there OTHER files still reading from JSON?

#### VF-04.1: Full repo grep for deal_registry.json active reads
```bash
grep -rn "deal_registry\.json\|\.deal-registry" /home/zaks/zakops-backend/src/ 2>&1 | grep -v "__pycache__\|\.pyc" | tee "$EVIDENCE_DIR/VF-04-1.txt"
TOTAL_REFS=$(grep -rn "deal_registry\.json\|\.deal-registry" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v "__pycache__\|\.pyc" | wc -l) || TOTAL_REFS=0
echo "TOTAL_REGISTRY_REFS=$TOTAL_REFS" | tee -a "$EVIDENCE_DIR/VF-04-1.txt"
```
**INFO:** Count all references. Classify each as: ACTIVE_READ (code path that opens/reads the file), CONSTANT_ONLY (defined but not used for reads), or COMMENT/STRING (documentation).

#### VF-04.2: Identify files that open() or load() JSON registry
```bash
grep -rn "open.*deal_registry\|json\.load.*registry\|Path.*deal_registry\|read_text.*registry\|with open.*registry" /home/zaks/zakops-backend/src/ 2>&1 | grep -v "__pycache__\|\.pyc" | tee "$EVIDENCE_DIR/VF-04-2.txt"
ACTIVE_READS=$(grep -rn "open.*deal_registry\|json\.load.*registry\|read_text.*registry" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v "__pycache__\|\.pyc" | wc -l) || ACTIVE_READS=0
echo "ACTIVE_JSON_READS=$ACTIVE_READS" | tee -a "$EVIDENCE_DIR/VF-04-2.txt"
```
**PASS if:** ACTIVE_JSON_READS is 0 in the 3 claimed files (context_pack, actions_runner, chat_evidence_builder). Other files may still use JSON for non-deal-state purposes.

#### VF-04.3: deal_registry.py itself — is it still used?
```bash
wc -l /home/zaks/zakops-backend/src/core/deal_registry.py 2>&1 | tee "$EVIDENCE_DIR/VF-04-3.txt"
grep -rn "from.*deal_registry import\|import deal_registry" /home/zaks/zakops-backend/src/ 2>&1 | grep -v "__pycache__\|\.pyc" | tee -a "$EVIDENCE_DIR/VF-04-3.txt"
IMPORTS=$(grep -rn "from.*deal_registry import\|import deal_registry" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v "__pycache__\|\.pyc" | wc -l) || IMPORTS=0
echo "DEAL_REGISTRY_IMPORTS=$IMPORTS" | tee -a "$EVIDENCE_DIR/VF-04-3.txt"
```
**INFO:** If deal_registry.py is imported by many files, the split-brain risk is broader than the 3 files claimed. If 0 imports, the module may be dead code.

**Gate VF-04:** Check 2 must show 0 active JSON reads in the 3 target files. Check 1 and 3 are INFO for scope assessment.

---

### VF-05 — G2 Injection Auth (apikey.py) — 4 checks

**Context:** Fail-closed 503 on injection paths when ZAKOPS_API_KEY is unset.

#### VF-05.1: INJECTION_PATHS constant defined
```bash
grep -n "INJECTION_PATHS" /home/zaks/zakops-backend/src/api/shared/middleware/apikey.py 2>&1 | tee "$EVIDENCE_DIR/VF-05-1.txt"
```
**PASS if:** `INJECTION_PATHS = ("/api/quarantine",)` exists.

#### VF-05.2: Fail-closed 503 code path
```bash
grep -n -B3 -A10 "503\|Service Not Configured\|not.*expected_key\|fail.closed" /home/zaks/zakops-backend/src/api/shared/middleware/apikey.py 2>&1 | tee "$EVIDENCE_DIR/VF-05-2.txt"
```
**PASS if:** Code returns 503 when `ZAKOPS_API_KEY` is not set AND request path is in INJECTION_PATHS.

#### VF-05.3: Non-injection paths are NOT blocked by missing key
```bash
cat -n /home/zaks/zakops-backend/src/api/shared/middleware/apikey.py 2>&1 | tee "$EVIDENCE_DIR/VF-05-3.txt"
```
**PASS if:** Reading the full middleware logic confirms that non-injection paths (e.g., `/api/deals`) do NOT receive 503 when key is unset. Only injection paths are fail-closed.

#### VF-05.4: Middleware is registered in the application
```bash
grep -rn "apikey\|ApiKeyMiddleware\|add_middleware.*apikey\|app\.middleware.*apikey" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-05-4.txt"
grep -rn "apikey\|ApiKeyMiddleware" /home/zaks/zakops-backend/src/api/ 2>&1 | grep -v "__pycache__\|\.pyc" | head -10 | tee -a "$EVIDENCE_DIR/VF-05-4.txt"
```
**PASS if:** API key middleware is registered in the FastAPI application (either via `add_middleware()` or imported and called).

**Gate VF-05:** All 4 checks pass. Injection auth is fail-closed and properly wired.

---

### VF-06 — G5 Flood Protection (Rate Limiting) — 4 checks

**Context:** `injection_rate_limiter` at 120/min, wired to quarantine POST.

#### VF-06.1: RateLimiter class exists with `is_allowed()` method
```bash
grep -n "class RateLimiter\|def is_allowed\|def get_remaining" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee "$EVIDENCE_DIR/VF-06-1.txt"
```
**PASS if:** `RateLimiter` class exists with `is_allowed()` method.

#### VF-06.2: injection_rate_limiter instantiated at 120/min
```bash
grep -n "injection_rate_limiter" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee "$EVIDENCE_DIR/VF-06-2.txt"
```
**PASS if:** `injection_rate_limiter = RateLimiter(requests_per_minute=120)` exists.

#### VF-06.3: Rate limiter called in quarantine POST handler
```bash
grep -n "check_rate_limit\|rate_limit\|injection_rate_limiter" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-06-3.txt"
```
**PASS if:** `check_rate_limit(f"quarantine:{client_ip}", limiter=injection_rate_limiter)` is called at the TOP of the quarantine POST handler (before any processing).

#### VF-06.4: 429 response with Retry-After header
```bash
grep -n "429\|Retry-After\|Too Many Requests" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee "$EVIDENCE_DIR/VF-06-4.txt"
grep -n "429\|Retry-After" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -5 | tee -a "$EVIDENCE_DIR/VF-06-4.txt"
```
**PASS if:** Exceeding the rate limit returns 429 with a `Retry-After` header.

**Gate VF-06:** All 4 checks pass. Flood protection is properly wired.

---

### VF-07 — G3 Measurement: Dynamic 200/201 Response — 3 checks

**Context:** Quarantine POST should return 201 for new items, 200 for dedup hits.

#### VF-07.1: Dedup check exists before INSERT
```bash
grep -n -B2 -A15 "existing\|dedup\|already.*exists\|message_id.*exists" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "quarantine" | head -20 | tee "$EVIDENCE_DIR/VF-07-1.txt"
```
**PASS if:** Code checks for existing quarantine item by `message_id` before inserting.

#### VF-07.2: Status code 200 for dedup, 201 for new
```bash
grep -n "status_code.*200\|status_code.*201\|response\.status_code" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-07-2.txt"
```
**PASS if:** Both `response.status_code = 200` (dedup) and `response.status_code = 201` (new) exist in the quarantine POST handler.

#### VF-07.3: Source type captured from body AND header fallback
```bash
grep -n "source_type\|X-Source-Type" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -15 | tee "$EVIDENCE_DIR/VF-07-3.txt"
```
**PASS if:** `source_type` is read from (1) request body, (2) `X-Source-Type` header fallback, (3) default `"email"`. The injection contract specifies this 3-tier priority.

**Gate VF-07:** All 3 checks pass. Measurement capability is complete.

---

### VF-08 — G4 Correlation Chain End-to-End — 4 checks

**Context:** Correlation ID must flow: caller header → quarantine_items → outbox event.

#### VF-08.1: X-Correlation-ID captured from request headers
```bash
grep -n "X-Correlation-ID\|correlation_id.*header\|headers.*correlation" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-08-1.txt"
```
**PASS if:** `request.headers.get("X-Correlation-ID")` exists in the quarantine POST handler.

#### VF-08.2: correlation_id stored in quarantine_items INSERT
```bash
grep -n -A30 "INSERT INTO.*quarantine_items\|INSERT.*quarantine" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "correlation_id" | head -5 | tee "$EVIDENCE_DIR/VF-08-2.txt"
```
**PASS if:** `correlation_id` is included in the INSERT statement for `quarantine_items`.

#### VF-08.3: Outbox event uses ORIGINAL correlation_id from quarantine item
```bash
grep -n -B5 -A15 "outbox.*INSERT\|INSERT.*outbox" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "correlation_id" | tee "$EVIDENCE_DIR/VF-08-3.txt"
```
**PASS if:** Outbox INSERT uses `item.get('correlation_id')` (the ORIGINAL from the quarantine row), NOT `gen_random_uuid()`.

#### VF-08.4: Fallback to UUID for legacy items without correlation_id
```bash
grep -n -A5 "correlation_id.*or\|fallback\|uuid\|gen_random_uuid" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "correlation\|uuid\|fallback" | head -10 | tee "$EVIDENCE_DIR/VF-08-4.txt"
```
**PASS if:** Code has fallback to `str(uuid.uuid4())` or `gen_random_uuid()` when quarantine item has no correlation_id.

**Gate VF-08:** All 4 checks pass. Correlation chain is end-to-end.

---

### VF-09 — G3 Dashboard: Source Type Filter — 5 checks

**Context:** Dashboard quarantine page should have source_type dropdown filter with 5 options.

#### VF-09.1: sourceTypeFilter state in quarantine/page.tsx
```bash
grep -n "sourceTypeFilter\|setSourceTypeFilter\|source.*type.*filter\|source_type" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | head -15 | tee "$EVIDENCE_DIR/VF-09-1.txt"
```
**PASS if:** `useState` for sourceTypeFilter exists.

#### VF-09.2: Dropdown select element with 5 options
```bash
grep -n -A15 "select.*source\|Source.*Type\|sourceType" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | head -30 | tee "$EVIDENCE_DIR/VF-09-2.txt"
```
**PASS if:** `<select>` element renders with options: All sources, email_sync, langsmith_shadow, langsmith_live, manual.

#### VF-09.3: Filter passed to API fetch call
```bash
grep -n -A5 "source_type.*sourceTypeFilter\|sourceTypeFilter.*fetch\|getQuarantineQueue" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | head -15 | tee "$EVIDENCE_DIR/VF-09-3.txt"
```
**PASS if:** sourceTypeFilter value is passed to the API call as `source_type` parameter.

#### VF-09.4: useEffect re-fetches on filter change
```bash
grep -n -B2 -A5 "useEffect.*sourceTypeFilter\|sourceTypeFilter.*useEffect" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | head -15 | tee "$EVIDENCE_DIR/VF-09-4.txt"
```
**PASS if:** `useEffect` includes `sourceTypeFilter` in its dependency array.

#### VF-09.5: 'use client' directive (Surface 9 compliance)
```bash
head -3 /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | tee "$EVIDENCE_DIR/VF-09-5.txt"
```
**PASS if:** First line is `'use client'`.

**Gate VF-09:** All 5 checks pass. Dashboard filter is complete and Surface 9 compliant.

---

### VF-10 — G3 Dashboard: Route Parameter Forwarding — 3 checks

**Context:** Dashboard API route should forward source_type to backend.

#### VF-10.1: source_type extracted from query params
```bash
grep -n "source_type\|sourceType\|searchParams" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts 2>&1 | tee "$EVIDENCE_DIR/VF-10-1.txt"
```
**PASS if:** `searchParams.get('source_type')` extracts the filter value.

#### VF-10.2: Parameter forwarded to backend URL
```bash
cat -n /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts 2>&1 | tee "$EVIDENCE_DIR/VF-10-2.txt"
```
**PASS if:** Reading the full route handler confirms source_type is added to the backend request URL params.

#### VF-10.3: source_type included in response items
```bash
grep -n "source_type" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts 2>&1 | tee "$EVIDENCE_DIR/VF-10-3.txt"
```
**PASS if:** Response mapping includes `source_type: item.source_type`.

**Gate VF-10:** All 3 checks pass.

---

### VF-11 — G3 Dashboard: API Client Function — 3 checks

**Context:** `getQuarantineQueue()` should accept source_type parameter.

#### VF-11.1: Function signature includes source_type
```bash
grep -n -A10 "getQuarantineQueue\|quarantine.*Queue" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | head -20 | tee "$EVIDENCE_DIR/VF-11-1.txt"
```
**PASS if:** Function parameter type includes `source_type?: string`.

#### VF-11.2: source_type added to URL search params
```bash
grep -n -A20 "getQuarantineQueue" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | grep -i "source_type\|searchParams" | tee "$EVIDENCE_DIR/VF-11-2.txt"
```
**PASS if:** `if (params?.source_type) searchParams.set('source_type', params.source_type)` exists.

#### VF-11.3: Endpoint URL is correct
```bash
grep -n "quarantine" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | grep -i "endpoint\|url\|fetch\|/api/" | head -5 | tee "$EVIDENCE_DIR/VF-11-3.txt"
```
**PASS if:** Endpoint targets `/api/actions/quarantine`.

**Gate VF-11:** All 3 checks pass.

---

### VF-12 — G6 Documentation Completeness — 5 checks

**Context:** INJECTION-CONTRACT.md must cover all 6 gaps.

#### VF-12.1: Endpoint and auth documented
```bash
grep -n "POST /api/quarantine\|X-API-Key\|401\|503" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-12-1.txt"
```
**PASS if:** POST endpoint, X-API-Key requirement, 401 and 503 responses documented.

#### VF-12.2: Rate limiting documented
```bash
grep -n "120\|rate.*limit\|429\|Retry-After" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-12-2.txt"
```
**PASS if:** 120/min limit, 429 response, Retry-After header documented.

#### VF-12.3: 200/201 response codes documented
```bash
grep -n "200\|201\|dedup\|Created" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-12-3.txt"
```
**PASS if:** Both 200 (dedup) and 201 (new) documented with meaning.

#### VF-12.4: Correlation ID chain documented
```bash
grep -n "correlation\|X-Correlation-ID\|outbox\|traceability" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-12-4.txt"
```
**PASS if:** Full chain (header → quarantine_items → outbox) documented.

#### VF-12.5: Source type values and priority documented
```bash
grep -n "source_type\|email_sync\|langsmith_shadow\|langsmith_live\|manual\|priority" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-12-5.txt"
```
**PASS if:** All 5 values listed (email_sync, langsmith_shadow, langsmith_live, manual, email) with 3-tier priority (body > header > default).

**Gate VF-12:** All 5 checks pass. Documentation covers all gaps.

---

### VF-13 — G3 GET Endpoint Source Type Filtering — 3 checks

**Context:** GET /api/quarantine should accept source_type query param and filter results.

#### VF-13.1: source_type query parameter accepted
```bash
grep -n -B5 -A15 "def.*get.*quarantine\|GET.*quarantine\|@app\.get.*quarantine\|@.*get.*quarantine" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -30 | tee "$EVIDENCE_DIR/VF-13-1.txt"
```
**PASS if:** GET handler accepts `source_type` as a Query parameter.

#### VF-13.2: SQL WHERE clause includes source_type filter
```bash
grep -n -A30 "SELECT.*quarantine_items\|quarantine.*SELECT" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "source_type\|WHERE" | head -10 | tee "$EVIDENCE_DIR/VF-13-2.txt"
```
**PASS if:** SQL query adds `AND source_type = $n` when the parameter is provided.

#### VF-13.3: source_type included in response items
```bash
grep -n -A3 "source_type" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "response\|return\|dict\|json\|item" | head -10 | tee "$EVIDENCE_DIR/VF-13-3.txt"
```
**PASS if:** Response includes `source_type` field for each quarantine item.

**Gate VF-13:** All 3 checks pass.

---

## 4. Cross-Consistency Checks

### XC-1: Contract Doc Matches Implementation
```bash
echo "=== Contract says 120/min ===" | tee "$EVIDENCE_DIR/XC-1.txt"
grep "120" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee -a "$EVIDENCE_DIR/XC-1.txt"
echo "=== Code says ===" | tee -a "$EVIDENCE_DIR/XC-1.txt"
grep "requests_per_minute.*=.*[0-9]" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | grep injection | tee -a "$EVIDENCE_DIR/XC-1.txt"
```
**PASS if:** Contract rate limit (120/min) matches code (`requests_per_minute=120`).

### XC-2: Source Type Values in Contract vs Dashboard
```bash
echo "=== Contract source types ===" | tee "$EVIDENCE_DIR/XC-2.txt"
grep "email_sync\|langsmith_shadow\|langsmith_live\|manual\|email" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee -a "$EVIDENCE_DIR/XC-2.txt"
echo "=== Dashboard dropdown options ===" | tee -a "$EVIDENCE_DIR/XC-2.txt"
grep "email_sync\|langsmith_shadow\|langsmith_live\|manual" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | tee -a "$EVIDENCE_DIR/XC-2.txt"
```
**PASS if:** All source type values in the contract appear in the dashboard dropdown.

### XC-3: Response Codes in Contract vs Implementation
```bash
echo "=== Contract response codes ===" | tee "$EVIDENCE_DIR/XC-3.txt"
grep -E "^\| \*\*[0-9]{3}" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee -a "$EVIDENCE_DIR/XC-3.txt"
echo "=== Implementation ===" | tee -a "$EVIDENCE_DIR/XC-3.txt"
grep -n "status_code.*=.*[0-9]\|HTTPException.*status_code\|JSONResponse.*status_code" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "quarantine" | head -10 | tee -a "$EVIDENCE_DIR/XC-3.txt"
grep -n "503\|429" /home/zaks/zakops-backend/src/api/shared/middleware/apikey.py /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-3.txt"
```
**PASS if:** All 6 documented response codes (200, 201, 400, 401, 429, 503) have corresponding code paths.

### XC-4: Correlation ID Priority in Contract vs Code
```bash
echo "=== Contract priority ===" | tee "$EVIDENCE_DIR/XC-4.txt"
grep -A5 "Priority\|Correlation" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | grep -i "header\|body\|fallback\|X-Correlation" | tee -a "$EVIDENCE_DIR/XC-4.txt"
echo "=== Code ===" | tee -a "$EVIDENCE_DIR/XC-4.txt"
grep -n "X-Correlation-ID\|correlation_id" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/XC-4.txt"
```
**PASS if:** Contract says header → storage → outbox, and code implements exactly that chain.

### XC-5: All 7 Gaps in Completion Report Have Matching VF Gates
```bash
echo "=== Gap Coverage ===" | tee "$EVIDENCE_DIR/XC-5.txt"
echo "G1 (Split-brain JSON truth) → VF-01, VF-02, VF-03, VF-04" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "G2 (Conditional auth) → VF-05" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "G3 (HTTP status codes) → VF-07" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "G4 (Shadow mode source_type) → VF-09, VF-10, VF-11, VF-13" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "G5 (Correlation ID) → VF-08" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "G6 (Rate limiter) → VF-06" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "G7 (Documentation) → VF-12" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "ALL 7 GAPS COVERED" | tee -a "$EVIDENCE_DIR/XC-5.txt"
```
**PASS if:** Every gap has a corresponding VF family.

---

## 5. Stress Tests

### ST-1: No Promise.all in Dashboard Quarantine Components
```bash
PA_COUNT=$(grep -c "Promise\.all[^S]" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null) || PA_COUNT=0
echo "PROMISE_ALL_COUNT=$PA_COUNT" | tee "$EVIDENCE_DIR/ST-1.txt"
```
**PASS if:** PA_COUNT is 0.

### ST-2: No console.error in Dashboard Quarantine Components (Surface 9)
```bash
CE_COUNT=$(grep -c "console\.error" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null) || CE_COUNT=0
echo "CONSOLE_ERROR_COUNT=$CE_COUNT" | tee "$EVIDENCE_DIR/ST-2.txt"
```
**PASS if:** CE_COUNT is 0.

### ST-3: Rate Limiter Uses Per-IP Key (Not Global)
```bash
grep -n "client_ip\|client.*ip\|request\.client" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "quarantine\|rate" | head -5 | tee "$EVIDENCE_DIR/ST-3.txt"
```
**PASS if:** Rate limiter key includes client IP (e.g., `f"quarantine:{client_ip}"`), not a global counter.

### ST-4: Injection Auth Applies to ALL Quarantine Sub-Paths
```bash
echo "Testing INJECTION_PATHS pattern matching" | tee "$EVIDENCE_DIR/ST-4.txt"
grep -n -A5 "INJECTION_PATHS\|is_injection_path\|startswith" /home/zaks/zakops-backend/src/api/shared/middleware/apikey.py 2>&1 | tee -a "$EVIDENCE_DIR/ST-4.txt"
```
**PASS if:** Path check uses `startswith("/api/quarantine")` which covers `/api/quarantine`, `/api/quarantine/{id}/process`, and any sub-paths. NOT an exact match.

### ST-5: asyncpg Connection String Uses ZAKOPS Database URL (Not Hardcoded)
```bash
grep -n "asyncpg\.connect\|DATABASE_URL\|conn_string\|dsn" /home/zaks/zakops-backend/src/actions/context/context_pack.py /home/zaks/zakops-backend/src/workers/actions_runner.py /home/zaks/zakops-backend/src/core/chat_evidence_builder.py 2>&1 | tee "$EVIDENCE_DIR/ST-5.txt"
```
**PASS if:** asyncpg connections use environment variable (DATABASE_URL or similar), not hardcoded credentials.

---

## 6. Remediation Protocol

When a gate returns FAIL:

1. **Read the evidence file** — understand the exact failure
2. **Classify the failure:**
   - `RESIDUAL_ARTIFACT` — Stale constants, imports, or parameters from pre-migration code that should have been removed
   - `MISSING_FIX` — Claimed fix was not applied
   - `REGRESSION` — A prior fix was reverted or broken
   - `SPLIT_BRAIN` — Code path still reads from JSON file instead of PostgreSQL
   - `WIRING_GAP` — Feature exists but is not connected to the right code path
   - `FALSE_POSITIVE` — Gate logic is wrong, code is correct
3. **Apply minimal fix** following existing patterns
4. **Re-run the specific gate** — capture new evidence
5. **Re-run `make validate-local`** — ensure no regression
6. **Record in completion report** with before/after evidence paths

---

## 7. Enhancement Opportunities

### ENH-1: Remove deal_registry.py Module
If the module is no longer imported, remove it entirely. Dead code is a maintenance burden and confusion source.

### ENH-2: Structured Logging for Rate Limit Events
Log rate limit hits with client_ip, endpoint, and timestamp for security monitoring.

### ENH-3: Correlation ID Propagation to Agent API
Currently the correlation chain ends at the outbox. Extend to agent API SSE events for full end-to-end tracing.

### ENH-4: Integration Test for 200/201 Dedup Behavior
Add a test that submits the same message_id twice and asserts 201 then 200 responses.

### ENH-5: Dashboard Rate Limit Error Handling
If the backend returns 429, the dashboard should show a user-friendly "Too many requests" message, not a generic error.

---

## 8. Scorecard Template

```
QA-LANGSMITH-INTAKE-HARDEN-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: Claude Code (Opus 4.6)

Pre-Flight:
  PF-1 (validate-local):          [ PASS / FAIL ]
  PF-2 (TypeScript):              [ PASS / FAIL ]
  PF-3 (Backend health):          [ PASS / FAIL / SKIP ]
  PF-4 (Source artifacts):        [ PASS / FAIL ]
  PF-5 (Evidence dir):            [ PASS / FAIL ]

Verification Families:
  VF-01 (context_pack.py):        __ / 4  checks PASS
  VF-02 (actions_runner.py):      __ / 5  checks PASS
  VF-03 (chat_evidence_builder):  __ / 5  checks PASS
  VF-04 (Global split-brain):     __ / 3  checks PASS/INFO
  VF-05 (Injection auth):         __ / 4  checks PASS
  VF-06 (Rate limiting):          __ / 4  checks PASS
  VF-07 (Dynamic 200/201):        __ / 3  checks PASS
  VF-08 (Correlation chain):      __ / 4  checks PASS
  VF-09 (Dashboard filter):       __ / 5  checks PASS
  VF-10 (Route forwarding):       __ / 3  checks PASS
  VF-11 (API client):             __ / 3  checks PASS
  VF-12 (Documentation):          __ / 5  checks PASS
  VF-13 (GET source_type):        __ / 3  checks PASS

Cross-Consistency:
  XC-1 (Rate limit match):        [ PASS / FAIL ]
  XC-2 (Source type match):       [ PASS / FAIL ]
  XC-3 (Response code match):     [ PASS / FAIL ]
  XC-4 (Correlation chain):       [ PASS / FAIL ]
  XC-5 (Gap coverage):            [ PASS / FAIL ]

Stress Tests:
  ST-1 (Promise.all ban):         [ PASS / FAIL ]
  ST-2 (console.error ban):       [ PASS / FAIL ]
  ST-3 (Per-IP rate key):         [ PASS / FAIL ]
  ST-4 (Sub-path auth):           [ PASS / FAIL ]
  ST-5 (No hardcoded creds):      [ PASS / FAIL ]

Summary:
  Total gates:          __ / 74
  PASS:                 __
  FAIL:                 __
  INFO:                 __
  SKIP:                 __

  Remediations Applied: __
  Enhancement Opportunities: 5 (ENH-1 through ENH-5)

  Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **QA only** — Do not build new features. If a gate reveals a gap, classify and fix minimally.
2. **Remediate, don't redesign** — Fixes must follow existing patterns.
3. **Evidence-based** — Every PASS needs tee'd output in `$EVIDENCE_DIR`.
4. **Services-down accommodation** — If PF-3 fails, live gates become SKIP(services-down).
5. **Surface 9 compliance** — Dashboard checks include `'use client'` and `console.warn` verification.
6. **Generated files are read-only** — Do not modify `api-types.generated.ts` or `backend_models.py`.
7. **WSL safety** — Strip CRLF and fix ownership on any new files.
8. **Record all changes** in `/home/zaks/bookkeeping/CHANGES.md`.

---

## 10. Stop Condition

Stop when:
- All 74 verification gates pass, are justified (SKIP/INFO), or are remediated (FAIL → fix → re-gate → PASS)
- All remediations are applied and re-verified
- `make validate-local` passes as final check
- The scorecard is complete with evidence paths for every gate
- All changes recorded in CHANGES.md

---

*End of QA Mission Prompt — QA-LANGSMITH-INTAKE-HARDEN-VERIFY-001*

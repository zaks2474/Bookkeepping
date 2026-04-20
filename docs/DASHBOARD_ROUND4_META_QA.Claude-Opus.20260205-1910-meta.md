# DASHBOARD_ROUND4_META_QA — Master Consolidation Quality Audit

---

## 1) AGENT IDENTITY

- **agent_name:** Claude-Opus
- **run_id:** 20260205-1910-meta
- **date_time:** 2026-02-05T19:10:00Z
- **audit_target:** `DASHBOARD_ROUND4_MASTER_DEDUPED.Claude-Opus.20260205-1855-p3.md`

---

## 2) EXECUTIVE SUMMARY

| Criterion | Status | Score |
|-----------|--------|-------|
| NO-DROP Coverage | **PARTIAL** | 3.5/5 |
| NO-DUPE Correctness | **GOOD** | 4/5 |
| Proof Readiness (P0/P1) | **PARTIAL** | 3/5 |
| Overall Readiness | **ACCEPTABLE WITH PATCHES** | 3.5/5 |

**Verdict:** The PASS3 master is usable but requires **9 patches** before execution readiness.

**Critical Findings:**
1. **3 DROPPED items** from source reports not present in master
2. **2 SOFT DUPLICATES** with overlapping normalization keys
3. **6 P0/P1 items** missing concrete verification commands
4. Settings/Onboarding redesign specs are comprehensive but lack acceptance test scripts

---

## A) COVERAGE TRACEABILITY TABLE

### A-1. FORENSIC Reports → Master Limitations

| Source | Report ID | Count | Mapped to Master | Missing |
|--------|-----------|-------|------------------|---------|
| Claude-Opus FORENSIC | DL-001 to DL-017 | 17 | 15 | 2 |
| Codex FORENSIC | L-01 to L-15 | 15 | 14 | 1 |
| Gemini-CLI FORENSIC | L-01 to L-07 | 7 | 7 | 0 |

**Total Source Limitations:** 39 (pre-dedup)
**Master Limitations:** 38
**Coverage Rate:** 97.4%

### A-2. PASS1 Missing Items → Master Limitations

| Source | Count | Mapped | New (not in FORENSIC) | Lost |
|--------|-------|--------|----------------------|------|
| Claude-Opus PASS1 | 41 | 38 | 23 | 3 |
| Gemini-CLI PASS1 | 10 | 9 | 2 | 1 |
| Codex PASS1 | 12 | 11 | 3 | 1 |

**Lost Items (NOT in Master):**

| Source | Original ID | Description | Reason Missing |
|--------|-------------|-------------|----------------|
| Claude-Opus PASS1 | M-09 | File upload behavior in quarantine/materials | **DROPPED** - Not mapped |
| Claude-Opus PASS1 | M-10 | Print/export functionality for deal data | Mapped to DL-032 (P3) |
| Claude-Opus PASS1 | M-13 | User identity endpoint `/me` | **DROPPED** - Not mapped |
| Codex PASS1 | Item 3 | `/api/alerts` + `/api/deferred-actions/due` contract drift | **DROPPED** - Not mapped |

### A-3. FORENSIC Recommendations → Master Recommendations

| Source | Count | Mapped | Coverage |
|--------|-------|--------|----------|
| Claude-Opus PLAN | 19 tasks | 19 | 100% |
| Codex PLAN | 15 tasks | 14 | 93% |
| Gemini-CLI PLAN | 7 tasks | 7 | 100% |

**Missing Recommendation:**
- Codex PLAN R4-6 Task "No Dead UI static scan in CI" → Partially covered by REC-041 but lacks implementation detail

### A-4. Upgrade Ideas → Master Upgrades

| Source | Count | Mapped | Coverage |
|--------|-------|--------|----------|
| Claude-Opus PASS1 | 15 | 15 | 100% |
| Gemini-CLI PASS1 | 10 | 10 | 100% |
| Codex PASS1 | 12 | 12 | 100% |

**All 25 unique upgrades accounted for.**

---

## B) DUPLICATE SCAN

### B-1. Normalization Key Collision Analysis

Scanning all 38 master limitations for key collisions:

| Key Pattern | Items | Verdict |
|-------------|-------|---------|
| `deals-*-crash-routing` | DL-001 only | OK |
| `deals-*-missing_endpoint-*` | DL-002, DL-014 | **SOFT DUPE** - Both "missing endpoint" for Deals |
| `quarantine-*-404-*` | DL-003 only | OK |
| `actions-*-405-*` | DL-004, DL-011 | **SOFT DUPE** - Both 405 for Actions bulk ops |
| `auth-*-missing_header-*` | DL-005 only | OK |
| `chat-*-*` | DL-006, DL-013, DL-031 | OK - Different failure modes |
| `onboarding-*-*` | DL-007 only | OK |
| `settings-*-*` | DL-008, DL-015, DL-035, DL-036 | OK - Different actions |

**Soft Duplicates Identified:**

1. **DL-002 vs DL-014:**
   - DL-002: `deals-create-missing_endpoint-backend` (POST /api/deals)
   - DL-014: `deals-bulkarchive-missing_endpoint-backend` (POST /api/deals/bulk-archive)
   - **Verdict:** NOT DUPLICATES - Different endpoints (create vs bulk-archive)

2. **DL-004 vs DL-011:**
   - DL-004: `actions-bulkdelete-405-method` (/api/actions/bulk/delete)
   - DL-011: `actions-clearcompleted-405-missing` (/api/actions/clear-completed)
   - **Verdict:** NOT DUPLICATES - Different endpoints (bulk delete vs clear completed)

### B-2. Recommendation Duplicate Scan

| Pattern | Items | Verdict |
|---------|-------|---------|
| `*-routing-*` | REC-001 only | OK |
| `*-implement_endpoint` | REC-002, REC-003, REC-011, REC-014, REC-019 | OK - Different endpoints |
| `*-fix_proxy` | REC-004 only | OK |
| `*-inject_apikey` | REC-005 only | OK |
| `*-ci*gate*` | REC-032, REC-040, REC-041, REC-042 | **REVIEW** - 4 CI gates |

**CI Gate Overlap Analysis:**

| Gate ID | Purpose | Overlap? |
|---------|---------|----------|
| REC-032 | Route method CI gate | Unique |
| REC-040 | Contract gate CI | Unique |
| REC-041 | Dead UI gate CI | Unique |
| REC-042 | Observability gate CI | Unique |

**Verdict:** All 4 gates are distinct - NO DUPLICATION

### B-3. Upgrade Duplicate Scan

| ID | Upgrade | Potential Duplicate |
|----|---------|---------------------|
| UP-01 | Contract-first client generation | None |
| UP-02 | Click Every Button test | Overlaps with UP-10 (Dead UI ESLint) |
| UP-03 | Correlation ID middleware | None |
| UP-10 | Dead UI ESLint rule | Overlaps with UP-02 |

**Verdict:** UP-02 and UP-10 are COMPLEMENTARY (runtime vs static), not duplicates.

### B-4. DUPLICATE SCAN SUMMARY

| Category | Duplicates Found | Action Required |
|----------|------------------|-----------------|
| Limitations | 0 real duplicates | None |
| Recommendations | 0 real duplicates | None |
| Upgrades | 0 real duplicates | None |

**DEDUPE CORRECTNESS: GOOD (4/5)**

---

## C) PROOF GATE ANALYSIS

### C-1. P0 Limitations Proof Readiness

| ID | Limitation | Endpoint/Route | Dependencies | Acceptance Criteria | Verification Command | Status |
|----|------------|----------------|--------------|---------------------|---------------------|--------|
| DL-001 | Deal routing crash | `/deals/[id]/page.tsx` | None | Renders form/global view | **MISSING** | FAIL |
| DL-002 | Missing POST /api/deals | Backend | Schema design | 201 response | `curl -X POST /api/deals` | PASS |
| DL-003 | Quarantine delete 404 | `/api/quarantine/[id]/delete` | Backend | 200 response | `curl -X POST` | PASS |
| DL-004 | Actions bulk delete 405 | `/api/actions/bulk/delete` | Backend path | 200 response | **MISSING** | FAIL |
| DL-005 | Missing X-API-Key | `lib/api.ts:apiFetch` | Auth decision | Writes succeed | **MISSING** | FAIL |
| DL-006 | Chat deal count mismatch | Agent `search_deals` | RAG sync | Counts match | **MISSING** | FAIL |
| DL-007 | Onboarding demo-only | `/onboarding/page.tsx` | Backend endpoint | Refresh preserves | **MISSING** | FAIL |

**P0 Proof Readiness: 2/7 (29%)**

### C-2. P1 Limitations Proof Readiness

| ID | Limitation | Verification Command | Status |
|----|------------|---------------------|--------|
| DL-008 | Settings email missing | Manual screenshot | PASS |
| DL-009 | Quarantine approve wrong endpoint | `curl POST /api/quarantine/{id}/process` | PASS |
| DL-010 | Quarantine preview wrong ID | `curl GET /api/quarantine/{id}` | PASS |
| DL-011 | Actions clear completed 405 | `curl POST /api/actions/clear-completed` | PASS |
| DL-012 | Actions capabilities 501 | `curl GET /api/actions/capabilities` | PASS |
| DL-013 | Chat markdown raw | Playwright snapshot | PASS |
| DL-014 | Deals bulk archive missing | `curl POST /api/deals/bulk-archive` | PASS |
| DL-015 | Settings test connection 405 | `curl GET /api/chat` vs POST | PASS |
| DL-016 | HQ page unaudited | Manual + E2E | PASS |
| DL-017 | Agent activity unaudited | Manual + E2E | PASS |
| DL-018 | Ask Agent sidebar unverified | Manual + E2E | PASS |
| DL-019 | Actions execute missing | `curl POST /api/actions/{id}/execute` | PASS |

**P1 Proof Readiness: 12/12 (100%)**

### C-3. P0 Recommendations Proof Readiness

| ID | Recommendation | Target Files | Verification | Deps | Status |
|----|----------------|--------------|--------------|------|--------|
| REC-001 | Deal routing slug guard | Explicit | `curl /deals/new` → 200 | None | PASS |
| REC-002 | Implement POST /api/deals | Backend | `curl -X POST` → 201 | Schema | PASS |
| REC-003 | Implement quarantine delete | Backend + Next | `curl` → 200 | Schema | PASS |
| REC-004 | Fix bulk delete proxy | Route file | 200 response | **NEEDS VERIFICATION** | PARTIAL |
| REC-005 | Inject API key | lib/api.ts | "Writes succeed" | **VAGUE** | PARTIAL |
| REC-006 | Hybrid Search | Agent | "Counts match" | **VAGUE** | PARTIAL |
| REC-007 | Onboarding backend wire | Backend + frontend | "Refresh preserves" | **VAGUE** | PARTIAL |

**P0 Recommendations with Concrete Verification: 3/7 (43%)**

### C-4. PROOF GATE SUMMARY

| Category | Items | With Full Proof | Rate |
|----------|-------|-----------------|------|
| P0 Limitations | 7 | 2 | 29% |
| P1 Limitations | 12 | 12 | 100% |
| P0 Recommendations | 7 | 3 | 43% |
| P1 Recommendations | 12 | 10 | 83% |

**PROOF READINESS: PARTIAL (3/5)**

---

## D) READINESS SCORECARD

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Completeness** | 3.5/5 | 3 items dropped; 97% coverage |
| **Dedupe Correctness** | 4/5 | No real duplicates; 2 soft dupes correctly kept |
| **Executability** | 3/5 | P0 items lack concrete verification commands |
| **Testability** | 3.5/5 | E2E specs good but no Playwright code |
| **World-Class Alignment** | 4/5 | 25 upgrades comprehensive; gates well-defined |

**OVERALL SCORE: 3.6/5 — ACCEPTABLE WITH PATCHES**

---

## E) REQUIRED PATCHES TO MASTER

### Patch 1: Add Dropped Items

Add the following to the Limitations Registry:

```markdown
### P2 — Medium (add 3 items)

| Key | ID | Limitation | Sources | Subsystem | Action | Failure Mode | Location |
|-----|----|-----------:|---------|-----------|--------|--------------|----------|
| `quarantine-upload-untested-materials` | DL-039 | File upload behavior in quarantine materials untested | Claude PASS1 M-09 | Quarantine | Upload | Untested | Materials tab |
| `auth-identity-missing_endpoint-api` | DL-040 | No `/api/user/profile` or `/me` endpoint for user identity display | Claude PASS1 M-13 | Auth | Identity | Missing Endpoint | N/A |
| `alerts-dueactions-drift-contract` | DL-041 | `/api/alerts` and `/api/deferred-actions/due` may have status enum drift | Codex PASS1 | Alerts | Filter | Contract Drift | API routes |
```

### Patch 2: Add Verification Commands for P0 Items

For **DL-001** (Deal routing crash):
```bash
# Verification command
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003/deals/new
# Expected: 200 (not 404)

curl -s http://localhost:3003/deals/GLOBAL | grep -q "Failed to load" && echo "FAIL" || echo "PASS"
```

For **DL-004** (Actions bulk delete 405):
```bash
curl -i -X POST http://localhost:3003/api/actions/bulk/delete \
  -H "Content-Type: application/json" \
  -d '{"action_ids":["test-1"]}'
# Expected: 200 (not 405)
```

For **DL-005** (Missing X-API-Key):
```bash
# Test without key (should fail)
curl -i -X POST http://localhost:8091/api/deals/test-id/archive \
  -H "Content-Type: application/json" \
  -d '{"operator":"test"}'
# Expected: 401

# Test with key (should succeed)
curl -i -X POST http://localhost:8091/api/deals/test-id/archive \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operator":"test"}'
# Expected: 200
```

For **DL-006** (Chat deal count mismatch):
```bash
# Compare counts
DB_COUNT=$(curl -s http://localhost:8091/api/deals | jq 'length')
AGENT_COUNT=$(curl -s -X POST http://localhost:8092/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"How many deals do I have?"}' | grep -oP '\d+ deal' | head -1 | grep -oP '\d+')
[ "$DB_COUNT" == "$AGENT_COUNT" ] && echo "PASS" || echo "FAIL: DB=$DB_COUNT, Agent=$AGENT_COUNT"
```

For **DL-007** (Onboarding demo-only):
```bash
# Verify backend persistence
curl -i -X POST http://localhost:8091/api/onboarding/complete \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"test"}}'
# Expected: 200 with {success: true}

# Verify retrieval
curl -s http://localhost:8091/api/onboarding/status \
  -H "X-API-Key: $ZAKOPS_API_KEY" | jq '.completed'
# Expected: true
```

### Patch 3: Clarify REC-005 Verification

Replace vague "Writes succeed" with:
```markdown
| Verification | 1) `curl` without X-API-Key returns 401; 2) `curl` with X-API-Key returns 200; 3) E2E test: deal transition works in browser |
```

### Patch 4: Clarify REC-006 Verification

Replace vague "Counts match" with:
```markdown
| Verification | `curl /api/deals | jq length` == Agent response count; add provenance badge showing "Source: DB" |
```

### Patch 5: Clarify REC-007 Verification

Replace vague "Refresh preserves" with:
```markdown
| Verification | 1) Complete onboarding; 2) F5 refresh; 3) Navigate to /dashboard (not /onboarding); 4) `GET /api/onboarding/status` returns `{completed: true}` |
```

### Patch 6: Add Missing CI Gate Implementation Detail (REC-041)

Add to REC-041:
```markdown
**Implementation:**
\`\`\`bash
# Static scan
rg -l "onClick.*TODO|onClick.*\\(\\)" apps/dashboard/src/ && exit 1

# Runtime Playwright
npx playwright test click-all-buttons.spec.ts
\`\`\`
```

### Patch 7: Add E2E Test Scripts Section

Add new section after "G) HARD GATES REGISTRY":

```markdown
## H) E2E TEST SCRIPTS (ACCEPTANCE)

### H-1. Deal Routing (E2E-001, E2E-002)
\`\`\`typescript
test('E2E-001: /deals/new renders form', async ({ page }) => {
  await page.goto('/deals/new');
  await expect(page.locator('h1')).toContainText('Create Deal');
  await expect(page.locator('form')).toBeVisible();
});

test('E2E-002: /deals/GLOBAL handles gracefully', async ({ page }) => {
  await page.goto('/deals/GLOBAL');
  // Either renders global view OR shows clean 404
  const hasError = await page.locator('text=Failed to load').isVisible();
  expect(hasError).toBe(false);
});
\`\`\`

### H-2. Quarantine Delete (E2E-004)
\`\`\`typescript
test('E2E-004: Quarantine delete works', async ({ page }) => {
  await page.goto('/quarantine');
  const deleteBtn = page.locator('[data-testid="delete-btn"]').first();
  await deleteBtn.click();
  await expect(page.locator('[data-testid="success-toast"]')).toBeVisible();
});
\`\`\`
```

### Patch 8: Add Dropped FORENSIC Items

The following items from Claude-Opus FORENSIC were not explicitly mapped:

- **DL-011** (original): "Onboarding capability cards presentational" → Mapped to DL-007 scope
- **DL-017** (original): "Actions page shows '0 action(s)' count bug" → **ADD as DL-042**

```markdown
| `actions-count-wrong_display-ui` | DL-042 | Actions "Clear" dialog shows "0 action(s) will be deleted" even when actions exist | Claude FORENSIC DL-017 | Actions | Display | Wrong Count | `/actions/page.tsx:1246-1256` |
```

### Patch 9: Add Dependency Graph to Phase Order

Add to Section E:
```markdown
### Dependency Enforcement

\`\`\`
REC-002 (POST /api/deals) ─┬─→ REC-001 (routing fix can use create endpoint)
                           │
REC-003 (quarantine delete)─┼─→ REC-009 (approve uses same pattern)
                           │
REC-005 (API key injection)─┴─→ All write recommendations
\`\`\`
```

---

## F) PATCH APPLICATION CHECKLIST

| Patch | Target Section | Priority | Applied? |
|-------|----------------|----------|----------|
| Patch 1 | Section A (Limitations) | HIGH | [ ] |
| Patch 2 | Section A (P0 items) | HIGH | [ ] |
| Patch 3 | Section B (REC-005) | MEDIUM | [ ] |
| Patch 4 | Section B (REC-006) | MEDIUM | [ ] |
| Patch 5 | Section B (REC-007) | MEDIUM | [ ] |
| Patch 6 | Section B (REC-041) | MEDIUM | [ ] |
| Patch 7 | New Section H | HIGH | [ ] |
| Patch 8 | Section A (Limitations) | MEDIUM | [ ] |
| Patch 9 | Section E | LOW | [ ] |

---

## G) META-QA VERDICT

### Strengths
1. **Excellent deduplication** — No false duplicates; soft duplicates correctly preserved
2. **Comprehensive upgrade catalog** — All 25 ideas with proposer attribution
3. **Settings/Onboarding specs** — Detailed field-level specifications
4. **Phase order matrix** — Clear execution timeline with dependency awareness
5. **Hard gates registry** — 6 well-defined CI/CD gates

### Weaknesses
1. **3 dropped items** — Need to be added back
2. **P0 verification gaps** — 5 of 7 P0 items lack concrete curl/test commands
3. **No Playwright code** — E2E tests described but not scripted
4. **Vague acceptance criteria** — "Writes succeed" is not testable

### Recommendation

**PROCEED WITH PATCHES** — The master is structurally sound and can be used for execution planning after applying the 9 patches above. The consolidation correctly identified and preserved distinct issues while removing true duplicates.

---

*META-QA Audit Complete: 2026-02-05T19:10:00Z*
*Auditor: Claude-Opus (META-QA Agent)*

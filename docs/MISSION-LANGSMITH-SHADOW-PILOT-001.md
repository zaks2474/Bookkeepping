# MISSION: LANGSMITH-SHADOW-PILOT-001
## One-Week LangSmith Shadow-Mode Pilot — Seed, Measure, Decide
## Date: 2026-02-14
## Classification: Operational Pilot Launch
## Prerequisite: LANGSMITH-SHADOW-PILOT-READY-001 complete (11/11 AC PASS), QA-LANGSMITH-SHADOW-PILOT-VERIFY-001 complete (58 PASS, 2 INFO, 0 FAIL)
## Successor: LANGSMITH-LIVE-PROMOTION-001 (blocked until pilot Go decision)

---

## Crash Recovery
<!-- Adopted from Improvement Area IA-2 -->
If resuming after a crash, run these 3 commands to determine current state:
1. `ls -la /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md` — does the pilot tracker exist?
2. `docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "SELECT source_type, status, COUNT(*) FROM zakops.quarantine_items GROUP BY source_type, status ORDER BY source_type, status;"`
3. `curl -sf http://localhost:8091/health` — is backend alive?

---

## 1. Mission Objective

Launch a clean, measurable, one-week LangSmith shadow-mode pilot. The pilot validates that LangSmith-injected quarantine items flow correctly through the ZakOps pipeline and measures precision against an 80% target before any live promotion decision.

**What this mission does:**
- Cleans the environment of any stale/test artifacts that would distort pilot measurement
- Completes the previously-skipped PF-3 backend health verification
- Runs an end-to-end seed test proving the full injection → quarantine → review loop works
- Creates operator-facing measurement tools (pilot tracker, precision formula, decision packet)

**What this is NOT:**
- This is NOT a live promotion mission — LangSmith remains shadow-only throughout
- This is NOT a code change mission — the intake surface is already hardened (per prerequisite missions)
- This is NOT an auto-promotion system — humans approve every quarantine item; humans make the Go/No-Go decision

**Source material:**
- Completion report: `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md`
- QA scorecard: `/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-shadow-pilot-verify-001/SCORECARD.md`
- Injection contract: `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md`
- Evidence pack: `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E01-E07`

---

## 2. Context

### Current System State

The intake surface has been fully hardened across two missions:

1. **LANGSMITH-INTAKE-HARDEN-001** — Built the injection endpoint with auth, rate limiting, dedup, correlation ID chain, and shadow isolation
2. **LANGSMITH-SHADOW-PILOT-READY-001** — Eliminated source_type drift (`langsmith_production` → `langsmith_live`), added `VALID_SOURCE_TYPES` server-side validation, added startup auth gate

QA verification (QA-LANGSMITH-SHADOW-PILOT-VERIFY-001) scored **58 PASS, 0 FAIL, 2 INFO** across 60 gates. The one exception: **PF-3 (backend health) was SKIP** because services were down at verification time. Backend is now confirmed healthy.

### Database State (as of mission start)

- `zakops.quarantine_items`: 1 row (source_type=email, status=rejected)
- `zakops.deals`: 58 rows across normal stages (inbound: 26, screening: 7, qualified: 2, closing: 1, archived: 22)
- No `langsmith_shadow` or `langsmith_live` rows exist yet — the quarantine surface is clean

### Non-Negotiables

1. **ZakOps is the canonical workflow engine.** LangSmith is an external injector only — it sends items into the quarantine queue. ZakOps owns the pipeline.
2. **Shadow mode first.** No auto-promotion. All quarantine items require human review and approval.
3. **Precision target: ≥ 80%** over the pilot week, with a meaningful sample size (minimum 20 items reviewed).
4. **Markdown-only deliverables.** No JSON files. All tracking and decision documents are Markdown.
5. **Preserve historical artifacts.** Do not overwrite prior mission logs, evidence packs, or QA reports.

---

## 2b. Glossary

| Term | Definition |
|------|-----------|
| Shadow mode | LangSmith injects items with `source_type=langsmith_shadow` — they enter quarantine but are reviewed separately from production email flow |
| Precision | (True Positives) / (True Positives + False Positives) — measures how many LangSmith-suggested items are actually valid deals |
| True Positive (TP) | A `langsmith_shadow` quarantine item that the operator approves as a legitimate deal opportunity |
| False Positive (FP) | A `langsmith_shadow` quarantine item that the operator rejects as not a valid deal |
| Seed test | A synthetic injection to verify the full loop works end-to-end before real pilot data flows |
| Dedup hit | When `POST /api/quarantine` returns 200 (not 201) because an item with the same `message_id` already exists |
| Pilot tracker | A Markdown file the operator updates daily with counts, observations, and precision calculations |
| Go/No-Go | The decision at pilot end: GO LIVE (promote to `langsmith_live`), EXTEND (more data needed), or REFINE (fix issues first) |

---

## 3. Architectural Constraints

Per standing rules in CLAUDE.md and MEMORY.md. Mission-specific emphasis:

- **`source_type=langsmith_shadow` is the ONLY value** used during the pilot. Never inject with `langsmith_live` — that implies promotion.
- **Injection contract governs all injections** — per `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md`. All requests must include `X-API-Key`, valid `source_type`, and `message_id`.
- **Dedup measurement via 201/200** — per E03 evidence. 201 = new item created, 200 = dedup hit. Callers count these to measure injection vs dedup rates.
- **Dashboard `source_type` filter** — per E05 evidence. Operators use the quarantine page dropdown to isolate `langsmith_shadow` items from email items.
- **Port 8090 FORBIDDEN** — per standing rules.
- **Contract surface discipline** — no direct edits to generated files.

---

## 3b. Anti-Pattern Examples

### WRONG: Injecting with langsmith_live during shadow pilot
```
POST /api/quarantine
{"source_type": "langsmith_live", "message_id": "..."}
// This bypasses shadow isolation — live items mix with production flow
```

### RIGHT: All pilot injections use langsmith_shadow
```
POST /api/quarantine
{"source_type": "langsmith_shadow", "message_id": "..."}
// Shadow items are isolated via dashboard dropdown filter
```

### WRONG: Counting precision from database queries only
```sql
SELECT COUNT(*) FROM zakops.quarantine_items WHERE source_type = 'langsmith_shadow' AND status = 'approved';
-- Misses the human judgment aspect — approved != true positive
```

### RIGHT: Operator records TP/FP judgment in the pilot tracker
```markdown
| Day | Reviewed | TP | FP | Precision | Notes |
|-----|----------|----|----|-----------|-------|
| Day 1 | 5 | 4 | 1 | 80% | FP was a duplicate of existing deal |
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Seed test creates quarantine item but operator doesn't know how to filter for it in the dashboard | MEDIUM | Pilot starts with confusion | Phase 2 documents exact UI steps; Phase 3 pilot tracker includes screenshot-equivalent instructions |
| 2 | ZAKOPS_API_KEY not set in backend environment, causing all injections to return 503 | HIGH | No items can be injected at all | Phase 1 Gate verifies health AND auth state explicitly |
| 3 | Pilot tracker precision calculation is ambiguous — operator counts differently than intended | MEDIUM | Measurement is unreliable | Phase 3 defines TP/FP with concrete examples, not just formulas |
| 4 | Seed test item is not cleaned up and distorts Week 1 precision numbers | MEDIUM | Off-by-one in measurements | Phase 2 explicitly marks seed items and Phase 3 tracker excludes them |
| 5 | New .sh files written with CRLF line endings | MEDIUM | Scripts fail silently | WSL safety checklist enforced per standing rules |

---

## Phase 0 — Cleanup
**Complexity:** S
**Estimated touch points:** 0 files (database + filesystem inspection only)

**Purpose:** Verify the environment is clean enough to start pilot measurement without distortion from stale test data.

### Blast Radius
- **Services affected:** None (read-only inspection)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Inspect quarantine_items table** — Query `SELECT source_type, status, COUNT(*) FROM zakops.quarantine_items GROUP BY source_type, status` and document the baseline state.
  - Evidence: Query output saved to evidence directory
  - **Checkpoint:** Confirm no `langsmith_shadow` or `langsmith_production` rows exist. If they do, document them and decide: DELETE (test data) or KEEP (production data) based on `created_at` timestamps.

- P0-02: **Inspect deals table** — Query `SELECT stage, COUNT(*) FROM zakops.deals GROUP BY stage` and document baseline.
  - Evidence: Query output saved to evidence directory
  - **Checkpoint:** Confirm no deals with `langsmith_shadow` source identifiers exist.

- P0-03: **Verify historical artifacts are intact** — Confirm these exist and are not empty:
  - `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md`
  - `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E01-E07`
  - `/home/zaks/bookkeeping/docs/QA-LANGSMITH-SHADOW-PILOT-VERIFY-001.md`
  - `/home/zaks/bookkeeping/CHANGES.md`
  - Evidence: File existence + line count check

### Decision Tree
- **IF** `langsmith_production` rows found in quarantine → UPDATE source_type to `langsmith_live` (per ENH-1 from QA)
- **ELSE IF** `langsmith_shadow` test rows found → DELETE them (test data from prior sessions)
- **ELSE** → No cleanup needed (expected case given current state: 1 row, email/rejected)

### Rollback Plan
1. No destructive changes in this phase (read-only inspection)
2. If any rows are updated/deleted, record the exact SQL in evidence

### Gate P0
- Baseline quarantine state documented
- Baseline deals state documented
- Historical artifacts confirmed intact
- No stale test data that would distort pilot measurement
- Operator can clearly see the system is "clean enough" to start

---

## Phase 1 — Operational Preflight Completion
**Complexity:** S
**Estimated touch points:** 0 files (service verification only)

**Purpose:** Bring services to a known-good state and complete the previously-skipped PF-3 backend health verification from QA-LANGSMITH-SHADOW-PILOT-VERIFY-001.

### Blast Radius
- **Services affected:** Backend API (verification only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P1-01: **Verify backend health** — `curl -sf http://localhost:8091/health` must return JSON healthy response.
  - Evidence: Full health response saved to evidence directory
  - **Checkpoint:** Backend responds with `{"status":"healthy",...}`. This completes the PF-3 that was SKIP in the QA scorecard.

- P1-02: **Verify ZAKOPS_API_KEY state** — Check if the startup gate logged its status. Inspect `app.state.api_key_configured` indirectly by checking the `/health` response or container logs.
  - Evidence: Auth state documentation saved to evidence directory
  - **Checkpoint:** Document whether API key is configured. If not, note that injections will return 503 (fail-closed behavior — this is by design, not a bug).

- P1-03: **Verify quarantine endpoint reachable** — `curl -sf http://localhost:8091/api/quarantine?limit=1` (GET, no auth required for listing).
  - Evidence: Response saved to evidence directory
  - **Checkpoint:** Endpoint returns JSON array (even if empty or with the 1 existing item).

- P1-04: **Verify dashboard quarantine page loads** — Check that the Next.js dashboard is running and the quarantine page is accessible.
  - Evidence: Dashboard status saved to evidence directory

### Decision Tree
- **IF** backend health fails → Check `docker ps` for `zakops-backend-backend-1`, restart with `cd /home/zaks/zakops-backend && docker compose restart backend`
- **IF** dashboard not running → Start with `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run dev`
- **IF** ZAKOPS_API_KEY not set → Document as INFO (fail-closed is the correct behavior; operator sets the key before starting real injections)

### Rollback Plan
1. No changes to revert — this phase is verification only
2. If a service was restarted, it can be stopped with `docker compose stop <service>`

### Gate P1
- Backend health returns `{"status":"healthy"}`
- Quarantine endpoint returns valid JSON
- Dashboard is accessible
- PF-3 is now explicitly PASS (not SKIP)
- Auth state is documented

---

## Phase 2 — Seed Test
**Complexity:** M
**Estimated touch points:** 0 code files (API calls + database verification only)

**Purpose:** Run an end-to-end seed test proving the full injection → quarantine → isolation → review loop works before real pilot data flows.

### Blast Radius
- **Services affected:** Backend API (quarantine POST), PostgreSQL (quarantine_items INSERT)
- **Pages affected:** Dashboard quarantine page (new item visible when filtered)
- **Downstream consumers:** None (seed items are cleaned or marked after test)

### Tasks
- P2-01: **Inject a seed quarantine item** — Use `curl` to POST a synthetic item with `source_type=langsmith_shadow`:
  ```bash
  curl -X POST http://localhost:8091/api/quarantine \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${ZAKOPS_API_KEY}" \
    -H "X-Correlation-ID: seed-test-$(date +%s)" \
    -d '{
      "message_id": "seed-test-langsmith-shadow-001",
      "subject": "[SEED TEST] LangSmith Shadow Pilot Validation",
      "sender": "seed-test@langsmith.internal",
      "body": "This is a seed test item to validate the LangSmith shadow injection pipeline. It should appear in the quarantine queue with source_type=langsmith_shadow. Safe to reject after validation.",
      "source_type": "langsmith_shadow"
    }'
  ```
  - Evidence: Full curl response (expect 201 Created) saved to evidence directory
  - **Checkpoint:** Response is 201 with the created item's ID and `source_type=langsmith_shadow`.

- P2-02: **Verify dedup behavior** — Re-send the SAME curl command from P2-01 (same `message_id`).
  - Evidence: Full curl response (expect 200 OK) saved to evidence directory
  - **Checkpoint:** Response is 200 (dedup hit, not 201). This proves the three-tier dedup is working.

- P2-03: **Verify isolation via API** — Query `GET /api/quarantine?source_type=langsmith_shadow` and confirm the seed item appears, then query `GET /api/quarantine?source_type=email_sync` and confirm it does NOT appear.
  - Evidence: Both responses saved to evidence directory
  - **Checkpoint:** Seed item appears ONLY when filtering by `langsmith_shadow`.

- P2-04: **Verify correlation ID** — Check the database row for the seed item and confirm `correlation_id` matches the `X-Correlation-ID` header sent.
  - Evidence: Database query output saved to evidence directory

- P2-05: **Clean up seed item** — DELETE or mark the seed test item so it does not distort pilot measurements. Document the cleanup method.
  - Evidence: Cleanup SQL or API call saved to evidence directory
  - **Checkpoint:** `SELECT COUNT(*) FROM zakops.quarantine_items WHERE message_id = 'seed-test-langsmith-shadow-001'` returns 0.

### Decision Tree
- **IF** P2-01 returns 503 → ZAKOPS_API_KEY not set. Document as BLOCKED and instruct operator to set the env var.
- **IF** P2-01 returns 401 → API key mismatch. Check the key value.
- **IF** P2-01 returns 400 → source_type validation rejected. Check for typos in the curl command.
- **IF** P2-01 returns 429 → Rate limited (unlikely for a single request). Wait 60 seconds and retry.
- **IF** P2-01 returns 201 → Proceed normally (expected path).

### Rollback Plan
1. DELETE the seed item: `DELETE FROM zakops.quarantine_items WHERE message_id = 'seed-test-langsmith-shadow-001';`
2. Verify: `SELECT COUNT(*) FROM zakops.quarantine_items WHERE message_id LIKE 'seed-test%';` returns 0.

### Gate P2
- Seed injection returns 201 Created with `source_type=langsmith_shadow`
- Dedup re-send returns 200 OK (not 201)
- Isolation filter shows seed item ONLY under `langsmith_shadow`
- Correlation ID preserved in database row
- Seed item cleaned up (not present in quarantine for pilot measurement)
- Clear evidence that the full loop works end-to-end

---

## Phase 3 — One-Week Shadow Mode Pilot Setup
**Complexity:** M
**Estimated touch points:** 2 files to create

**Purpose:** Create operator-facing tools for running and measuring the one-week pilot.

### Blast Radius
- **Services affected:** None (documentation only)
- **Pages affected:** None
- **Downstream consumers:** Operator (human) — uses the tracker daily

### Tasks
- P3-01: **Create pilot tracker** — Write `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md` with:
  - Pilot metadata (start date, end date, target precision, minimum sample size)
  - Daily log table with columns: Day, Date, New Items, Reviewed, TP, FP, Deferred, Daily Precision, Cumulative Precision, Notes
  - Instructions for how to fill in each column
  - How to query the dashboard for shadow items (step-by-step)
  - How to query the database for raw counts (backup verification)
  - Evidence: File exists with all required sections

- P3-02: **Define measurement rules** — Within the pilot tracker, include a "Measurement Rules" section:
  - **True Positive (TP):** Operator reviews the quarantine item, determines it IS a valid deal opportunity, and approves it (status → approved). The key question: "Would I have wanted this in my pipeline if it came from email?"
  - **False Positive (FP):** Operator reviews the quarantine item, determines it is NOT a valid deal opportunity (spam, irrelevant, duplicate of existing deal, wrong context), and rejects it (status → rejected).
  - **Deferred:** Operator cannot make a decision yet (needs more context). Deferred items are excluded from precision calculation until resolved.
  - **Precision formula:** `Precision = TP / (TP + FP)` — deferred items excluded from denominator.
  - **Minimum sample size:** 20 reviewed items (TP + FP ≥ 20) before precision is considered statistically meaningful.
  - **Target:** Precision ≥ 80% (at least 4 out of 5 LangSmith suggestions are valid deals).
  - Evidence: Measurement rules section complete with concrete examples

- P3-03: **Document dashboard workflow** — Within the pilot tracker, include step-by-step instructions:
  1. Navigate to Dashboard → Quarantine page
  2. Select "LangSmith shadow" from the Source Type dropdown
  3. Review each pending item — read subject, sender, body preview
  4. For each item: Approve (TP) or Reject (FP)
  5. Record results in the daily log table
  - Evidence: Instructions complete and reference correct UI elements

- P3-04: **Document database verification queries** — Within the pilot tracker, include SQL queries the operator can use to cross-check dashboard counts:
  ```sql
  -- Total shadow items by status
  SELECT status, COUNT(*) FROM zakops.quarantine_items
  WHERE source_type = 'langsmith_shadow' GROUP BY status;

  -- Daily injection rate (new items per day)
  SELECT DATE(created_at), COUNT(*) FROM zakops.quarantine_items
  WHERE source_type = 'langsmith_shadow' GROUP BY DATE(created_at) ORDER BY 1;

  -- Dedup rate (requires application-level logging or API response tracking)
  ```
  - Evidence: Queries included and syntactically correct

### Rollback Plan
1. Delete the tracker file: `rm /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md`
2. No code changes to revert

### Gate P3
- Pilot tracker file exists at `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md`
- Contains: metadata, daily log table, measurement rules with TP/FP definitions, precision formula, minimum sample size
- Contains: step-by-step dashboard workflow instructions
- Contains: database verification queries
- Operator can run the one-week pilot with minimal friction using only this document

---

## Phase 4 — Go/No-Go Decision Packet
**Complexity:** S
**Estimated touch points:** 1 file to create

**Purpose:** Prepare the decision template the operator completes after the one-week pilot to decide next steps.

### Blast Radius
- **Services affected:** None (documentation only)
- **Pages affected:** None
- **Downstream consumers:** Operator (human) — completes after pilot week

### Tasks
- P4-01: **Create decision packet** — Write `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md` with:
  - **Section 1: Pilot Summary** — Template for: dates, total items, total reviewed, overall precision, target met (Y/N)
  - **Section 2: Precision Analysis** — Table for daily precision trend. Pass/fail against 80% target. Note if sample size met minimum 20.
  - **Section 3: Stability Observations** — Template for: any errors during pilot, dedup rate, correlation ID integrity, dashboard UX issues, injection reliability
  - **Section 4: Decision Matrix** — Three options with criteria:
    - **GO LIVE:** Precision ≥ 80%, sample size ≥ 20, no critical stability issues → Promote `langsmith_shadow` to `langsmith_live`, begin live injection
    - **EXTEND:** Precision borderline (70-80%) OR sample size < 20 → Run one more week with same shadow setup
    - **REFINE:** Precision < 70% OR critical stability issues → Stop injections, diagnose root cause, create a remediation mission
  - **Section 5: Recommended Next Action** — Template line for operator to fill: `Decision: [GO LIVE / EXTEND / REFINE]` with justification
  - **Section 6: Approvals** — Sign-off line for the decision maker
  - Evidence: File exists with all required sections

### Rollback Plan
1. Delete the decision file: `rm /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md`
2. No code changes to revert

### Gate P4
- Decision packet file exists at `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md`
- Contains all 6 sections: summary, precision analysis, stability, decision matrix, recommended action, approvals
- Decision matrix clearly defines GO LIVE / EXTEND / REFINE criteria
- Operator can complete this document after one week to make the final call

---

## Dependency Graph

Phases execute sequentially: 0 → 1 → 2 → 3 → 4 → Final Verification.

No parallel execution paths — each phase depends on the prior phase's gate.

---

## Acceptance Criteria

### AC-1: Environment Cleanup Verified
The quarantine and deals tables are documented at baseline. No stale test data exists that would distort pilot measurement. Gate P0 passes.

### AC-2: Backend Health Confirmed (PF-3 Closure)
Backend health returns `{"status":"healthy"}`. The previously-skipped PF-3 from QA-LANGSMITH-SHADOW-PILOT-VERIFY-001 is now explicitly PASS.

### AC-3: Seed Test — Injection Works
A `langsmith_shadow` quarantine item is successfully injected via `POST /api/quarantine` and returns 201 Created.

### AC-4: Seed Test — Dedup Works
Re-sending the same `message_id` returns 200 OK (dedup hit), not 201.

### AC-5: Seed Test — Isolation Works
The seed item appears when filtering by `source_type=langsmith_shadow` and does NOT appear when filtering by `source_type=email_sync`.

### AC-6: Seed Test — Cleanup Complete
The seed test item is removed from quarantine after validation so it does not distort pilot measurement.

### AC-7: Pilot Tracker Created
`/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md` exists with daily log table, measurement rules (TP/FP definitions, precision formula, 20-item minimum), dashboard workflow, and database queries.

### AC-8: Decision Packet Created
`/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md` exists with precision analysis template, stability observations template, and GO LIVE / EXTEND / REFINE decision matrix with criteria.

### AC-9: No Regressions
`make validate-local` passes. No code was modified in this mission (documentation and operational verification only), but baseline validation confirms the codebase is healthy.

### AC-10: Bookkeeping
CHANGES.md updated. Completion report produced with evidence paths for every AC.

---

## Guardrails

1. **No code changes** — This mission creates documentation and runs verification. The intake surface is already hardened. Do not modify backend or dashboard code.
2. **No live promotion** — All injections use `source_type=langsmith_shadow`. Never use `langsmith_live` during this mission.
3. **Preserve historical artifacts** — Do not overwrite or delete any files in `/home/zaks/bookkeeping/docs/_qa_evidence/` or prior completion reports.
4. **Markdown-only deliverables** — No JSON tracker files. All operator-facing documents are Markdown.
5. **Seed test cleanup mandatory** — Do not leave seed test items in the quarantine table. They distort pilot measurement.
6. **WSL safety** — Strip CRLF and fix ownership on any new files under `/home/zaks/`.
7. **Port 8090 FORBIDDEN** — Per standing rules.
8. **Generated files are read-only** — Per contract surface discipline.
9. **ZAKOPS_API_KEY absence is INFO, not FAIL** — The fail-closed design is intentional. Document the state; do not treat it as a blocker unless real injections are needed immediately.

---

## Executor Self-Check Prompts

### After Phase 0 (Cleanup):
- [ ] "Did I document the baseline quarantine AND deals state, or just one?"
- [ ] "Are there any `langsmith_production` rows that need the ENH-1 migration?"
- [ ] "Did I confirm historical artifacts are intact without modifying them?"

### After Phase 2 (Seed Test):
- [ ] "Did I verify BOTH 201 (creation) AND 200 (dedup) responses?"
- [ ] "Did I test isolation in BOTH directions (appears with shadow filter, absent with email filter)?"
- [ ] "Did I clean up the seed item AND verify it's gone?"
- [ ] "Did I save evidence for every sub-step, not just the final result?"

### Before marking mission COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Do BOTH the pilot tracker AND decision packet exist as files?"
- [ ] "Did I produce a completion report with evidence paths for every AC?"
- [ ] "Did I fix CRLF + ownership on any new files?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/bookkeeping/CHANGES.md` | Final | Add mission entry |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md` | Phase 3 | Daily pilot tracking with measurement rules |
| `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md` | Phase 4 | Go/No-Go decision packet for post-pilot |
| `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.COMPLETION.md` | Final | Completion report |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md` | Prior mission completion |
| `/home/zaks/bookkeeping/docs/QA-LANGSMITH-SHADOW-PILOT-VERIFY-001.md` | QA scorecard (PF-3 was SKIP) |
| `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E01-E07` | Prior evidence files |
| `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` | Injection endpoint specification |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Backend quarantine implementation |

---

## Stop Condition

This mission is DONE when:
- All 10 AC are met
- `make validate-local` passes
- Pilot tracker and decision packet files exist with complete content
- Seed test has been executed AND cleaned up with evidence
- PF-3 backend health is explicitly PASS
- Completion report produced with evidence paths for every AC
- CHANGES.md updated

Do NOT proceed to: actual one-week pilot execution (that's the operator's job using the tracker), live promotion decisions, or `langsmith_live` configuration. Those are out of scope.

---

*End of Mission Prompt — LANGSMITH-SHADOW-PILOT-001*

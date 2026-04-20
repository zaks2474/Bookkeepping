AGENT IDENTITY
- agent_name: Codex
- run_id: 20260204-1728-102efc
- date_time: 2026-02-04T17:28:47Z
- repo_revision: unknown

## Top 25 Failure Modes Still Possible
Each item cites a concrete gap from Round-2 plans or PASS 1.

1) UI shows empty Actions/Deals lists with no visible error
- Symptom: Dashboard tables appear empty after API calls succeed.
- Likely root cause: Zod safeParse failures return [] (Opus Layer 5; Codex Q1-2).
- Detection signal: Browser console shows ZodError; network 200 with empty UI.
- Mitigation: Replace silent failures with user-visible errors; enforce contract gate (Opus ZK-UPG-0004; Codex Phase R2-1/R2-7).
- Rollback: Re-enable `.passthrough()` temporarily with explicit banner to avoid silent empties.

2) Action status appears blank or incorrect in UI
- Symptom: Actions in PROCESSING state render as unknown/empty.
- Likely root cause: ActionStatus enum mismatch RUNNING vs PROCESSING (Opus Layer 4 mismatch).
- Detection signal: Actions API returns PROCESSING; UI expects RUNNING; console schema errors.
- Mitigation: Align enum in backend or Zod schema (Opus ZK-UPG-0001).
- Rollback: Map PROCESSING -> RUNNING in UI adapter.

3) Quarantine approval does not create a deal
- Symptom: Approving quarantine only changes status; no deal created.
- Likely root cause: Round-2 plans do not include ZK-ISSUE-0003 (PASS1 missing list).
- Detection signal: DB shows approved quarantine_items with null deal_id; no new deal row.
- Mitigation: Add atomic approve->create flow (missing issue from PASS1).
- Rollback: Revert to manual create flow with explicit UI warning.

4) Deals created in UI lack DataRoom folders
- Symptom: Deal exists in Postgres but no folder structure in DataRoom.
- Likely root cause: ZK-ISSUE-0004 missing in Round-2 plans (PASS1).
- Detection signal: DB row exists; filesystem path absent.
- Mitigation: Hook folder scaffold on create (missing issue from PASS1).
- Rollback: Disable auto-scaffold, run manual scaffold script.

5) Dashboard still calls wrong quarantine endpoint
- Symptom: 404/405 on approve action.
- Likely root cause: ZK-ISSUE-0006 missing in Round-2 plans (PASS1).
- Detection signal: Network shows /resolve or wrong route.
- Mitigation: Update endpoint path in dashboard (missing issue from PASS1).
- Rollback: Add temporary backend alias.

6) Deal notes endpoint mismatch persists
- Symptom: Add note fails or is silently ignored.
- Likely root cause: ZK-ISSUE-0012 missing in Round-2 plans (PASS1).
- Detection signal: 404 for /notes; UI error logs.
- Mitigation: Add notes endpoint + client alignment (missing issue from PASS1).
- Rollback: Disable notes UI or proxy to correct endpoint.

7) Approval expiry job never runs
- Symptom: Old approvals never expire; stale actions remain pending.
- Likely root cause: ZK-ISSUE-0015 missing in Round-2 plans (PASS1).
- Detection signal: approvals older than TTL still active.
- Mitigation: Add expiry job + TTL check (missing issue from PASS1).
- Rollback: Manual cleanup script with audit log.

8) Retention policy absent; data bloat/PII risk
- Symptom: Archived/junk deals never purged; storage grows.
- Likely root cause: ZK-ISSUE-0017 missing in Round-2 plans (PASS1).
- Detection signal: No policy doc; DB growth; no cleanup job.
- Mitigation: Define policy + job (missing issue from PASS1).
- Rollback: Disable cleanup; document manual review.

9) Executors remain unwired
- Symptom: Action buttons show 501/404 or no effect.
- Likely root cause: ZK-ISSUE-0019 missing in Round-2 plans (PASS1).
- Detection signal: /actions/capabilities empty; executor logs missing.
- Mitigation: Wire executors to workflows (missing issue from PASS1).
- Rollback: Hide executor UI; document as deferred.

10) Scheduling/reminders missing
- Symptom: No reminders for stale deals.
- Likely root cause: ZK-ISSUE-0021 missing in Round-2 plans (PASS1).
- Detection signal: No scheduler logs; no reminder events.
- Mitigation: Add scheduler or cron (missing issue from PASS1).
- Rollback: Manual reminders.

11) Archive/restore endpoints missing
- Symptom: Archive fails or 404s.
- Likely root cause: ZK-ISSUE-0022 missing in Round-2 plans (PASS1).
- Detection signal: 404 on /archive or /restore.
- Mitigation: Implement endpoints (missing issue from PASS1).
- Rollback: Soft-delete in DB manually.

12) SSE still 501 in backend/dashboard
- Symptom: Real-time updates never arrive; UI logs errors.
- Likely root cause: SSE endpoints return 501 (Codex Q1-1 evidence).
- Detection signal: /api/events/stream returns 501; console errors.
- Mitigation: Implement SSE stream or explicitly switch to polling (Codex Phase R2-1/R2-6).
- Rollback: Disable SSE client and use polling.

13) Schema drift recurs between Pydantic and Zod
- Symptom: UI shows empty or incorrect fields after backend change.
- Likely root cause: Multiple schema sources; no CI contract gate (Opus Layer 4; Codex Q1-2; PASS1 consensus item).
- Detection signal: safeParse failures in console; contract diff fails.
- Mitigation: Generate TS client/Zod from OpenAPI + CI gate (Codex R2-7; Gemini R2-4).
- Rollback: Pin backend schema until client regen.

14) Direct fetch bypasses auth/correlation injection
- Symptom: Requests missing API key or correlation ID; logs untraceable.
- Likely root cause: dashboard api-client.ts bypasses middleware injection (Codex Q1-4).
- Detection signal: backend logs missing correlation_id for UI actions.
- Mitigation: unify fetch wrapper; enforce headers in single client (Codex Q1-4).
- Rollback: block direct fetches with lint rule.

15) Split-brain reintroduced via SQLite/JSON defaults
- Symptom: New data written to SQLite/JSON when env missing.
- Likely root cause: adapter defaults to SQLite; legacy paths remain (Codex Q1-5).
- Detection signal: SQLite files updated; JSON hash changes.
- Mitigation: remove/disable legacy adapters; CI guard for legacy patterns (Codex ZK-UPG-0010).
- Rollback: restore env vars; isolate legacy code.

16) Action capabilities/metrics route ambiguity causes 501 in prod
- Symptom: /api/actions/capabilities returns 501 or inconsistent schema.
- Likely root cause: duplicate route definitions (Codex Q1-7).
- Detection signal: endpoint toggles between 200/501; router conflicts.
- Mitigation: consolidate routes to single router; add integration test (Codex Q1-7).
- Rollback: remove main route; keep router.

17) Duplicate deal creation returns 500
- Symptom: create_deal double-click yields server error.
- Likely root cause: idempotency not enforced; unique constraint surfaces as 500 (Codex Q1-3; Gemini UPG-0002).
- Detection signal: 500 in logs; duplicate rows or DB constraint error.
- Mitigation: Idempotency-Key middleware and response cache (Codex R2-2).
- Rollback: return 409 with structured error; disable double-submit in UI.

18) RAG down crashes agent or returns empty results
- Symptom: search_deals tool fails hard or returns nothing.
- Likely root cause: no circuit breaker (Gemini UPG-0005; Codex UPG-0007).
- Detection signal: 5xx from RAG; agent errors.
- Mitigation: circuit breaker + fallback to SQL or explicit error.
- Rollback: disable RAG calls in agent.

19) Stage defaults regress to 'lead' on fresh DB
- Symptom: new deals default to lead; UI stage mismatch.
- Likely root cause: base schema still defaults lead; migration order issues (Codex Q1-6).
- Detection signal: information_schema shows default lead.
- Mitigation: set default in base DDL + migration; add verification gate.
- Rollback: manual update to inbound.

20) Outbox worker not running; side effects lost
- Symptom: deal events not emitted; no downstream effects.
- Likely root cause: outbox exists but processor not running (Codex Q3; UPG-0002).
- Detection signal: health endpoint indicates unprocessed actions; outbox backlog grows.
- Mitigation: enforce outbox worker in deployment + monitoring.
- Rollback: revert to synchronous side effects with explicit error handling.

21) Contract audit not run; drift persists
- Symptom: QA declares pass without browser/Zod validation.
- Likely root cause: CONTRACT-AUDIT-V1 / QA-CA-V1 not executed (Opus; Codex).
- Detection signal: missing evidence pack; no console logs.
- Mitigation: make browser console capture a hard gate (Codex R2-0).
- Rollback: block release until evidence exists.

22) Data loss in UI due to dual DealSchema
- Symptom: broker/company_info/metadata missing in UI.
- Likely root cause: api-client.ts manual schema strips fields (Gemini “Smoking Gun”).
- Detection signal: network shows fields, UI doesn’t render.
- Mitigation: delete manual schema; generate client from OpenAPI (Gemini R2-1, Codex R2-7).
- Rollback: temporarily import correct schema from api-schemas.ts.

23) ActionSource enum missing values
- Symptom: actions with source=agent/api fail validation.
- Likely root cause: ActionSource enum incomplete in backend (Opus ZK-UPG-0005).
- Detection signal: validation error; actions dropped.
- Mitigation: add agent/api to backend enum.
- Rollback: map to system/ui in UI adapter.

24) Legacy 8090 references resurrect dead endpoints
- Symptom: tools/docs point to old port; operators run wrong commands.
- Likely root cause: Makefile/docs still reference 8090 (Codex evidence index).
- Detection signal: rg finds 8090 in repo; operator confusion.
- Mitigation: remove references + add forbidden-pattern CI gate (Codex ZK-UPG-0010).
- Rollback: revert doc updates if wrong; ensure canonical port in SERVICE-CATALOG.

25) Observability gap: no end-to-end trace across UI→backend→agent→DB
- Symptom: cannot debug a single action end-to-end.
- Likely root cause: correlation IDs not consistently propagated; no OTel (Codex Q1-4, UPG-0005).
- Detection signal: missing trace_id in logs; cannot join events.
- Mitigation: enforce correlation header in single client; add OTel spans (Codex R2-6).
- Rollback: add verbose logging with request IDs.

---

## Split-Brain Reintroduction Audit
Potential reintroduction paths (from Round-2 plans + PASS1 gaps):
- SQLite/JSON adapter defaults still present (Codex Q1-5). If env missing, system silently writes to legacy store.
- Legacy registry paths referenced in production code (Codex evidence index).
- Idempotency/duplicate controls absent on create_deal → duplicate deal rows create divergent “truth.”

Required invariants + tests:
- Invariant SOT-1: All deal writes go through Postgres only; no legacy files may be written in production.
  - Test: file hash checks on deal_registry.json/ingest_state.db + rg guard in CI.
- Invariant SOT-2: All mutations require Idempotency-Key and return deterministic responses.
  - Test: replay same key returns identical response body.
- Invariant SOT-3: Folder scaffolding is derived, not a source of truth.
  - Test: folder deletion does not affect deal visibility in UI/agent.

---

## Contract Drift Audit (UI↔Backend↔Agent)
Where drift can recur (Round-2 evidence):
- Multiple schema sources (Pydantic, Zod, TS types) with manual edits (Opus Layer 4; Gemini “two DealSchema”).
- safeParse returning empty arrays hides mismatches (Opus Layer 5; Codex Q1-2).

Single-source-of-truth strategy + CI gates:
- OpenAPI is the authoritative contract.
- Generate TS client and Zod schemas from OpenAPI on every build (Codex ZK-UPG-0001; Gemini UPG-0001).
- CI gate: contract test compares backend responses to generated schema; any safeParse failure fails build.
- Forbidden-pattern gate: reject manual Zod schema files or manual API typings unless explicitly allowed.

---

## Auth & Security Audit
Hidden auth assumptions (from Codex plan):
- Dashboard direct fetch bypasses middleware that injects API key and correlation ID (Codex Q1-4).
- Some endpoints may accept writes without Idempotency-Key (Codex Q1-3; Gemini UPG-0002).

Required explicit flows:
- All UI writes must go through a single apiFetch wrapper that injects auth + correlation headers.
- Enforce API key or service token on all write endpoints.
- Record user_id/actor in audit logs for write actions (NEEDS VERIFICATION: no Round-2 plan explicitly adds this).

---

## Observability Audit
Required trace propagation:
- UI → backend → agent → DB must share correlation_id/trace_id.
- Dashboard: single fetch wrapper injects X-Correlation-ID.
- Backend: logs correlation_id and stores it in deal_events.
- Agent: forwards correlation_id to backend and logs it with tool execution.

Must-have logs/traces:
- API request log: method, path, status, correlation_id, actor_id.
- DB event log: deal_id, event_type, correlation_id, actor_id.
- Agent tool log: tool_name, correlation_id, outcome.

NEEDS VERIFICATION:
- Whether OTel collector is deployed and visible (Codex UPG-0005; not in other plans).

---

## Patch Set (Plan Edits)
Precise edits to upgrade Round-2 plans into execution-ready final plan.

1) Add missing V2 issues to Round-2 scope (PASS1 missing list)
- Add remediation tasks for ZK-ISSUE-0003/0004/0006/0012/0015/0017/0019/0021/0022.
- Place in R2-3 (Deferred Item Closure) or create R2-3b “V2 Coverage Closure.”
- Verification: add explicit acceptance tests per issue (approve→deal, folder scaffold, notes endpoint, archive/restore, retention policy, executors wired, scheduler).

2) Enforce single-source contract generation
- Replace manual schema alignment tasks with: generate TS client + Zod from OpenAPI, delete manual schema files, CI gate for contract drift.
- Apply to R2-1 and R2-7.
- Verification: CI fails on schema mismatch; build requires regen.

3) Idempotency on all write endpoints (not only create_deal)
- Add Idempotency-Key middleware + storage, required on POST/PUT/PATCH.
- Apply to R2-2.
- Verification: replay returns same response; no 500s on duplicates.

4) Remove legacy adapters or isolate behind explicit feature flag
- Explicitly remove SQLite/JSON adapters from production path; add CI guard.
- Apply to R2-3 or R2-9.
- Verification: rg for legacy patterns returns empty; file hashes unchanged.

5) SSE resolution policy
- Choose: implement SSE or document polling. Remove 501 endpoints.
- Apply to R2-1 or new R2-1b.
- Verification: /api/events/stream returns valid SSE frames or UI polling documented.

6) Correlation ID enforcement on all client requests
- Replace direct fetch usage with single wrapper injecting headers.
- Apply to R2-0 baseline and R2-6.
- Verification: correlation_id appears in backend logs and deal_events for every UI action.

7) Add explicit browser console capture gate
- Make browser console zero-ZodErrors a blocking gate (R2-0 + R2-1).
- Verification: saved console log in evidence pack.

8) Add ActionStatus/ActionSource enum alignment task
- Add explicit task in R2-1 for enum alignment and remove .passthrough.
- Verification: Actions status renders correctly; schema parse passes.

9) Add transitional ledger or explicit alternative
- If not implementing deal_transitions table, add rationale + compensating audit logging.
- Apply to R2-5.
- Verification: DB or logs provide immutable transition history.

10) Add QA baseline reference or record absence
- If QA_VERIFICATION_006_REPORT.md is missing, add a placeholder step to locate or generate it.
- Verification: evidence pack contains QA baseline or explicit “NEEDS VERIFICATION” note with path.

---

## Tough Gates Blueprint
MUST-PASS gates for Round-2 convergence.

Gate A: Code Health
- Lint/typecheck/unit tests for backend, agent, dashboard.
- Evidence: ruff/mypy/pytest outputs; npm/pnpm lint+typecheck logs.

Gate B: Contract Tests
- Generated client + Zod from OpenAPI; CI contract tests against live backend.
- Evidence: contract test logs; schema diff report.

Gate C: Integration Tests
- Service-to-service: UI → backend → agent → DB with correlation_id.
- Evidence: curl logs + DB queries showing correlation_id.

Gate D: End-to-End Proof
- Browser flow: email → quarantine → approve → deal → folder → RAG search → agent list.
- Evidence: browser capture + DB logs + filesystem listing.

QA Pass 1: Functional
- Deal CRUD, stage transitions, quarantine approval, actions execution, RAG search.
- Evidence: logs + screenshots.

QA Pass 2: Adversarial
- RAG down, backend down, duplicate POST, SSE down, idempotency replay.
- Evidence: explicit error responses, retry logs, no data corruption.

---

## Output Notes
- QA baseline file was not found at `/home/zaks/bookkeeping/docs/QA_VERIFICATION_006_REPORT.md` or `/mnt/data/QA_VERIFICATION_006_REPORT.md`; treat as NEEDS VERIFICATION and record in evidence pack.


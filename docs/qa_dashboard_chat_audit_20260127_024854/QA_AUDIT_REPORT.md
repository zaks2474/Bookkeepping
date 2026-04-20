# QA AUDIT REPORT — ZakOps Dashboard Deal Display + Chat Agent Fix

- Audit ID: QA-ZAKOPS-DASHBOARD-CHAT-2026-01-27
- Auditor: Codex (QA/Security Verifier)
- Audit timestamp (UTC): 2026-01-27T02:54:15Z
- Run directory: /home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854

## 1) AUDIT VERDICT

**FAIL**

Primary fail conditions (per the provided QA prompt):
- **Port 8090 is alive** and is served by `claude-code-api.service` (forbidden per prompt).
- Chat response path returns **fallback SSE** with warning: `AI agent service is currently unavailable...`.
- Completion packet is missing required chain-of-custody artifacts: `ledger.jsonl`, `evidence_manifest.sha256`, `verification_script.sh`.

## 2) TOP 10 FINDINGS (ranked)

1) **CRITICAL — Forbidden port 8090 is alive (architectural violation under this prompt).**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/02_port_8090_health.json`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/03_listener_8090.txt`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/04_systemctl_claude_code_api.txt`
   - Observed: `GET :8090/health` returned: `{"status":"ok"}`

2) **CRITICAL — The running 8090 service is `claude-code-api.service` (systemd) using Uvicorn on 0.0.0.0:8090.**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/04_systemctl_claude_code_api.txt`

3) **CRITICAL — Chat endpoint returns fallback SSE and includes the banned warning string.**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/08_chat_headers.txt`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/08_chat_body.txt`
   - Observed done payload line: `data: {"citations":[],"proposals":[],"model_used":"fallback","latency_ms":0,"warnings":["AI agent service is currently unavailable. Showing helpful guidance instead."]}`

4) **CRITICAL — Agent API chatbot endpoint rejects unauthenticated calls (401), so dashboard chat cannot use it as implemented.**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/09_agent_chat_headers.txt`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/09_agent_chat_body.txt`
   - Observed: `HTTP/1.1 401 Unauthorized`

5) **MAJOR — Completion packet is missing required proof artifacts (no ledger/manifest/verification script).**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/12_completion_packet_ls.txt`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/13_completion_packet_required_missing.txt`

6) **MAJOR — Builder’s `FIX_SUMMARY.md` claims "Status: COMPLETE" but omits required protocol artifacts (no red-to-green, no browser HAR/console).**
   - Evidence: `/home/zaks/completion_packet/FIX_SUMMARY.md`, `/home/zaks/completion_packet/artifacts/`

7) **PASS (partial) — DB → Backend → Dashboard API counts are consistent.**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/05b_db_deals_count.txt`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/06_backend_api_deals.json`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/07_dashboard_api_deals.json`
   - Observed: DB=3, Backend=3, Dashboard=3

8) **PASS (evidence) — `broker` is JSONB `{}` in DB and backend responses, consistent with the claimed root cause for “0 Deals”.**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/05_db_deals_query.txt`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/06_backend_api_deals.json`

9) **PASS (evidence) — Frontend schema contains `coerceBrokerToString()` and uses `z.preprocess(...)` for `broker` in `DealSchema`.**
   - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/10_api_ts_snippet.txt`

10) **UNVERIFIED — UI claims (AC-1/AC-2) require browser screenshots/HAR/console captures; none provided by Builder and not verifiable via curl alone.**
   - Evidence gap: missing HAR/console/screenshot artifacts in `/home/zaks/completion_packet/`.

## 3) EVIDENCE CONSISTENCY CHECKS

- DB ground truth: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/05_db_deals_query.txt` (count `3`)
- Backend API: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/06_backend_api_deals.json` (length `3`)
- Dashboard API: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/07_dashboard_api_deals.json` (length `3`)
- Consistency verdict: **MATCH** (DB == Backend == Dashboard API)

## 4) ARTIFACT AUTHENTICITY CHECKS

- Completion packet exists: YES
  - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/12_completion_packet_ls.txt`
- Builder-provided hash manifest: **MISSING** (cannot verify integrity of builder artifacts).
- QA artifacts manifest (sha256): present
  - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/audit_artifacts_manifest.sha256`

## 5) INSTRUCTION COMPLIANCE MATRIX

| Requirement | Provided? | Evidence Pointer | Notes |
|---|---:|---|---|
| Completion packet directory exists | YES | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/12_completion_packet_ls.txt` | `/home/zaks/completion_packet/` |
| FIX_SUMMARY.md exists | YES | `/home/zaks/completion_packet/FIX_SUMMARY.md` | Claims "Status: COMPLETE" |
| artifacts/001..005 exist | YES | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/12_completion_packet_ls.txt` | Present |
| ledger.jsonl | NO | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/13_completion_packet_required_missing.txt` | Required by prompt’s protocol mindset |
| evidence_manifest.sha256 | NO | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/13_completion_packet_required_missing.txt` | Missing |
| verification_script.sh | NO | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/13_completion_packet_required_missing.txt` | Missing |
| Browser screenshots | NO | N/A | Missing |
| HAR captures | NO | N/A | Missing |
| Console captures | NO | N/A | Missing |
| Red-to-green proof | NO | N/A | Missing |
| 3-run / 5-run stability evidence (artifacts) | PARTIAL | `artifacts/08_chat_body.txt` | No dedicated run logs |

## 6) FIX VALIDATION MATRIX (per acceptance criterion)

| Acceptance Criterion | Status | Evidence Pointer | Notes |
|---|---|---|---|
| AC-1: Deal Display Fixed | UNPROVEN | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/07_dashboard_api_deals.json`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/05b_db_deals_count.txt` | Data path OK, but no browser proof |
| AC-2: Deals Page Works | UNPROVEN | N/A | Requires browser verification |
| AC-3: Chat Responds | FAILED | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/08_chat_body.txt` | Returns fallback SSE; not real agent response |
| AC-4: No Warning Banner | FAILED | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/08_chat_body.txt` | Warning string present in SSE done payload |
| AC-5: End-to-End Verified | PARTIAL | `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/05_db_deals_query.txt`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/06_backend_api_deals.json`, `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/07_dashboard_api_deals.json` | Missing UI proof + missing chain-of-custody |

## 7) SCOPE & INTEGRITY CHECKS

- Port 8090 listener present: YES → **FAIL per this prompt**
  - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/03_listener_8090.txt`
- Service attribution: `claude-code-api.service` active and bound to port 8090
  - Evidence: `/home/zaks/bookkeeping/docs/qa_dashboard_chat_audit_20260127_024854/artifacts/04_systemctl_claude_code_api.txt`
- Repository change audit: UNVERIFIED (repo is not a git worktree; no full-tree checksum manifest provided by Builder).

## 8) REPRODUCIBILITY CHECK

- Fresh-clone one-command repro instruction: NOT PROVIDED in `/home/zaks/completion_packet/`.
- No `verification_script.sh` exists to rerun deterministically.

## 9) REQUIRED REMEDIATIONS (minimum to reach PASS)

1) Resolve the port 8090 violation under this prompt’s architecture:
   - If 8090 is truly forbidden for ZakOps: stop and quarantine `claude-code-api.service` and ensure dashboard/chat does not depend on it.
   - If 8090 is actually required by your real architecture: update this audit prompt’s “FORBIDDEN Port” section (it currently treats 8090 as forbidden).

2) Fix chat to use the correct Agent API behavior (auth + endpoint):
   - Current behavior: dashboard calls Agent API and receives 401, then falls back.
   - Required: either provision a service-to-service token and send `Authorization: Bearer ...` from the dashboard route, or expose a safe internal endpoint for dashboard use.

3) Produce chain-of-custody artifacts in `/home/zaks/completion_packet/`:
   - `ledger.jsonl` with required fields and output-file pointers
   - `evidence_manifest.sha256`
   - `verification_script.sh` that fails when the fix is reverted

4) Provide dual-channel UI proof for AC-1/AC-2:
   - Screenshots + HAR + console capture showing deals present and no schema validation errors.

5) Provide Red-to-Green:
   - Demonstrate that reverting the schema coercion reproduces “0 deals,” then re-apply and prove fixed.

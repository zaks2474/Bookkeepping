# Email Triage P0 E2E Fix — Verification Report

Date: 2026-01-01

## What was broken (root causes)

1) **`EMAIL_TRIAGE.REVIEW_EMAIL` approval/execution failed**
- Root cause: no executor was registered for `EMAIL_TRIAGE.REVIEW_EMAIL`, so the runner marked approved actions as `FAILED` with `executor_not_found`.

2) **Actions UI ZodError parsing `/api/actions`**
- Root cause: frontend `inputs` schema used `z.record(...).default({})`, which does **not** coerce `null` values; legacy rows or edge cases could surface `inputs: null` and fail parsing.

3) **`COMMUNICATION.DRAFT_EMAIL` failed with `cloud_disabled` even after approval**
- Root cause: executor gated Gemini drafting on global `ALLOW_CLOUD_DEFAULT=true`, instead of using **per-action, approval-gated cloud permission**.
- Additional blocker discovered: the Kinetic capabilities registry could not load due to invalid YAML (unquoted `:` in strings), so any capability-driven policy logic was failing and falling back.

4) **Email triage scope too broad (non-deal emails becoming review actions)**
- Root cause: triage scoring treated some transactional language (e.g., “transaction”) as weak deal evidence and did not consistently label operational emails as non-deal.

---

## What changed (fixes)

### A) E2E: Review action now executes and creates a deal
- Implemented executor `EMAIL_TRIAGE.REVIEW_EMAIL`:
  - Creates an **Inbound** deal workspace under `DataRoom/00-PIPELINE/Inbound/`
  - Registers a **real Deal record** in the existing Deal Registry (`DataRoom/.deal-registry/deal_registry.json`)
  - Persists email artifacts under `07-Correspondence/` and copies quarantined attachments

### B) Frontend contract hardening
- Hardened `zakops-dashboard` Zod schema to treat `inputs: null` as `{}`.

### C) Cloud policy: approval-gated (no global flag required)
- Added capability-level flag `cloud_required: true` for `communication.draft_email.v1`
- Runner passes `cloud_allowed` to executors only when the capability is cloud-required and the action is executing (approved lifecycle)
- `COMMUNICATION.DRAFT_EMAIL` executor now uses `ctx.cloud_allowed` (not `ALLOW_CLOUD_DEFAULT`)
- Fixed invalid capability YAML so the registry loads cleanly

### D) Triage scope tightened
- Removed transactional language from weak deal scoring and added operational hints
- Labeled operational/newsletter emails as `ZakOps/NonDeal`
- Ensures only `DEAL_SIGNAL` emails emit `EMAIL_TRIAGE.REVIEW_EMAIL` actions

---

## Evidence

### Pre-fix failure example (existing failed action)

`curl -s http://localhost:8090/api/actions/ACT-20260101T200807-02978adf | jq '{action_id,status,error}'`

Expected output included:
- `status: "FAILED"`
- `error.code: "executor_not_found"`
- `error.message: "No executor registered for action type: EMAIL_TRIAGE.REVIEW_EMAIL"`

### Capabilities endpoint now loads (was blocked by YAML errors)

`curl -s http://localhost:8090/api/actions/capabilities | jq '.count'`

### Tests (regressions added)

Backend tests:
- `bash /home/zaks/scripts/run_unit_tests.sh`

Triage tests:
- `cd /home/zaks/bookkeeping && make triage-test`

Key new regression coverage:
- `/api/actions` list contract
- `EMAIL_TRIAGE.REVIEW_EMAIL` creates deal + artifacts
- `COMMUNICATION.DRAFT_EMAIL` succeeds with per-action cloud gate (no `ALLOW_CLOUD_DEFAULT`)
- triage logic does not treat transaction alerts as deals

---

## Operational changes applied

Services restarted to pick up code/config changes:
- `systemctl restart kinetic-actions-runner.service`
- Restarted `deal_lifecycle_api.py` on `:8090`

---

## Manual E2E validation checklist (safe, synthetic)

1) Create a synthetic quarantine payload:
```bash
MSG_ID="TEST-EMAIL-$(date +%s)"
QDIR="/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/${MSG_ID}"
mkdir -p "$QDIR"
printf "Hello — this is a test inbound deal email.\n" > "$QDIR/email_body.txt"
printf "fake attachment\n" > "$QDIR/teaser.pdf"
```

2) Create and approve the review action:
```bash
curl -s http://localhost:8090/api/actions -H 'Content-Type: application/json' -d @- | jq '.' <<JSON
{
  "action_type": "EMAIL_TRIAGE.REVIEW_EMAIL",
  "title": "Review inbound deal email: TestCo teaser",
  "summary": "HIGH urgency. Contains deal signals.",
  "deal_id": null,
  "capability_id": "email_triage.review_email.v1",
  "created_by": "operator",
  "source": "ui",
  "risk_level": "medium",
  "requires_human_review": true,
  "inputs": {
    "message_id": "${MSG_ID}",
    "thread_id": "${MSG_ID}",
    "from": "Broker <broker@example.com>",
    "to": "operator@example.com",
    "date": "01 Jan 2026 12:00:00 +0000",
    "subject": "TestCo teaser",
    "company": "TestCo",
    "classification": "DEAL_SIGNAL",
    "urgency": "HIGH",
    "links": [],
    "attachments": [{"filename":"teaser.pdf","mime_type":"application/pdf","size_bytes": 10}],
    "quarantine_dir": "${QDIR}"
  }
}
JSON
```
Then:
```bash
ACTION_ID="(paste action_id)"
curl -s "http://localhost:8090/api/actions/${ACTION_ID}/approve" -H 'Content-Type: application/json' -d '{"approved_by":"operator"}' | jq '.'
curl -s "http://localhost:8090/api/actions/${ACTION_ID}/execute" -H 'Content-Type: application/json' -d '{"requested_by":"operator"}' | jq '.'
```

3) Confirm the runner executed it:
```bash
curl -s "http://localhost:8090/api/actions/${ACTION_ID}" | jq '{status, outputs, error}'
```

4) Confirm deal exists:
```bash
DEAL_ID="$(curl -s \"http://localhost:8090/api/actions/${ACTION_ID}\" | jq -r '.outputs.deal_id')"
curl -s "http://localhost:8090/api/deals/${DEAL_ID}" | jq '{deal_id, canonical_name, folder_path}'
```

---

## Files changed

- `bookkeeping/scripts/email_triage_agent/run_once.py`
- `bookkeeping/scripts/email_triage_agent/triage_logic.py`
- `bookkeeping/scripts/email_triage_agent/tests/test_triage_logic.py`
- `bookkeeping/docs/EMAIL_TRIAGE_P0_E2E_FIX_VERIFICATION_REPORT.md`
- `scripts/actions_runner.py`
- `scripts/actions/capabilities/registry.py`
- `scripts/actions/capabilities/communication.draft_email.v1.yaml`
- `scripts/actions/capabilities/email_triage.review_email.v1.yaml`
- `scripts/actions/capabilities/deal.create_from_email.v1.yaml`
- `scripts/actions/capabilities/deal.extract_email_artifacts.v1.yaml`
- `scripts/actions/executors/base.py`
- `scripts/actions/executors/registry.py`
- `scripts/actions/executors/communication_draft_email.py`
- `scripts/actions/executors/email_triage_review_email.py`
- `scripts/tests/test_actions_list_contract.py`
- `scripts/tests/test_email_triage_review_email_executor.py`
- `scripts/tests/test_draft_email_cloud_gate.py`
- `zakops-dashboard/src/lib/api.ts`


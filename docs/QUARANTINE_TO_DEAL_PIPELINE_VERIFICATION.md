# Verification Report — Quarantine → Deal Pipeline

## Scope Verified
- Deal creation from an approved/quarantined email (deal folder + Deal Registry + copied artifacts)
- Local-only extraction follow-on (summary + entities + doc types)
- Email triage scope tightening (receipts/newsletters no longer become deal review items)

## New / Updated Files
**New**
- `scripts/actions/capabilities/deal.create_from_email.v1.yaml`
- `scripts/actions/capabilities/deal.extract_email_artifacts.v1.yaml`
- `scripts/actions/executors/deal_create_from_email.py`
- `scripts/actions/executors/deal_extract_email_artifacts.py`
- `scripts/tests/test_quarantine_to_deal_pipeline.py`
- `scripts/tests/test_email_triage_scope.py`
- `bookkeeping/docs/QUARANTINE_TO_DEAL_PIPELINE.md`

**Updated**
- `scripts/actions/executors/registry.py`
- `scripts/actions/executors/_artifacts.py`
- `scripts/actions/executors/communication_send_email.py`
- `scripts/actions/executors/email_triage_review_email.py`
- `bookkeeping/scripts/email_triage_agent/triage_logic.py`
- `bookkeeping/scripts/email_triage_agent/run_once.py`
- `scripts/tests/test_chat_orchestrator_proposals.py`

## Commands Run
- Unit tests: `bash /home/zaks/scripts/run_unit_tests.sh` → **OK** (36 tests)

## Evidence (QA Sandbox Run)
This run was executed against an isolated DATAROOM root under `/home/zaks/tmp` (no changes to the real `/home/zaks/DataRoom`):

- `DATAROOM_ROOT=/home/zaks/tmp/qa_quarantine_to_deal_dataroom_1767305220`
- `DEAL.CREATE_FROM_EMAIL` output:
  - `deal_id`: `DEAL-2026-001`
  - `deal_path`: `/home/zaks/tmp/qa_quarantine_to_deal_dataroom_1767305220/00-PIPELINE/Inbound/Acme-Widgets-2026`
  - Copied artifacts include:
    - `.../07-Correspondence/INBOX/msg-demo-0001.md`
    - `.../07-Correspondence/ATTACHMENTS/email_body.txt`
    - `.../07-Correspondence/ATTACHMENTS/signed-nda.pdf`
- `DEAL.EXTRACT_EMAIL_ARTIFACTS` output artifacts:
  - `.../99-ACTIONS/<action_id>/extracted_summary.md`
  - `.../99-ACTIONS/<action_id>/extracted_entities.json`
  - `.../99-ACTIONS/<action_id>/detected_doc_types.json`

## Pass/Fail Checklist
- [x] Create deal folder under pipeline (Inbound)
- [x] Deal Registry record created + email→deal mapping persisted
- [x] Quarantine artifacts copied into deal correspondence area (copy-only)
- [x] Re-run is idempotent (no duplicate deal)
- [x] Extraction action writes 3 outputs under `99-ACTIONS/<action_id>/`
- [x] Email triage: receipt/invoice PDF does **not** classify as `DEAL_SIGNAL`


# Quarantine → Deal Creation Pipeline (Email Triage)

## Overview
This adds the missing “real workflow” pieces so inbound, acquisition-related emails can become real deals:

1) Email triage classifies inbox messages deterministically and only emits review actions for **deal-signal** emails.
2) Operator approves/rejects in the Actions UI (approval gate; no auto-send; no deletes).
3) On approval + execution, the system creates a **Deal workspace folder** + **Deal Registry** entry and copies the quarantined artifacts into the deal.
4) Optional follow-on: run a local-only extraction step to produce a compact summary + doc-type detection + simple entity/number extraction.

## Key Paths / Conventions
- Quarantine root: `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<gmail_message_id>/`
- Deal workspace root: `DataRoom/00-PIPELINE/Inbound/<slug>-<year>[-suffix]/`
- Deal correspondence artifacts (created by the deal-create executor in this track):
  - `07-Correspondence/INBOX/<gmail_message_id>.md`
  - `07-Correspondence/INBOX/<gmail_message_id>.json`
  - `07-Correspondence/ATTACHMENTS/<copied_files>`
- Action artifacts (v1.2 convention):
  - `<deal_path>/99-ACTIONS/<action_id>/...`

## Action Types Added
- `DEAL.CREATE_FROM_EMAIL`
  - Capability: `deal.create_from_email.v1`
  - Creates a new deal folder + Deal Registry entry (idempotent via email→deal mapping).
  - Copies quarantine directory contents into the deal’s correspondence area (copy-only; never deletes quarantine).
- `DEAL.EXTRACT_EMAIL_ARTIFACTS`
  - Capability: `deal.extract_email_artifacts.v1`
  - Local-only extraction over provided `artifact_paths` (best-effort; does not fail on unreadable files).
  - Produces:
    - `extracted_summary.md`
    - `extracted_entities.json`
    - `detected_doc_types.json`
    under `<deal>/99-ACTIONS/<action_id>/`.

## Email Triage Scope Tightening
To avoid flooding Quarantine/Actions with receipts/newsletters:
- Attachment presence alone is **no longer sufficient** to classify as `DEAL_SIGNAL`.
- Deal classification now uses a deterministic score:
  - positive signals: CIM/teaser/NDA/dataroom keywords + known portal link types + deal-ish attachment filenames
  - negative signals: receipt/invoice/order/shipping patterns

## How to Validate Manually
### 1) Run triage once (dry-run)
`python3 /home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py --dry-run --max-per-run 10`

### 2) Synthetic quarantine → deal (local executor)
Create:
- `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<msg_id>/email_body.txt`
- `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<msg_id>/<attachment>.pdf`

Then run the unit test harness (includes idempotency checks):
`bash /home/zaks/scripts/run_unit_tests.sh`

## Notes / Limitations
- `DEAL.EXTRACT_EMAIL_ARTIFACTS` is intentionally “cheap” in v1: it reads previews from `md/txt/csv` and classifies other formats primarily by filename.
- This track does not change UI; it only adds backend/executor capabilities and improves triage classification.


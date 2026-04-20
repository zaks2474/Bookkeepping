# Email Triage Agent — Verification Report

Date: 2026-01-01

## Scope

Verify the localized Gmail triage agent can:
- run a single cycle locally,
- apply labels (write),
- maintain idempotency state (SQLite),
- quarantine attachments (safe types only; deal-signal only),
- emit approval-gated Kinetic Actions (draft-only, never send),
- without enabling LangSmith tracing.

## Environment

- Runner code: `/home/zaks/bookkeeping/scripts/email_triage_agent/`
- Gmail MCP: launched via `npx -y @gongrzhe/server-gmail-autoauth-mcp` (fallback when `/root/...` is not traversable)
- Actions API: `http://localhost:8090/api/actions`
- State DB: `/home/zaks/DataRoom/.deal-registry/email_triage_state.db`
- Quarantine root: `/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE`

## Evidence

### 1) Dry run produces no side effects

Command:
- `cd /home/zaks/bookkeeping/scripts && sudo -u zaks python3 -m email_triage_agent.run_once --dry-run --max-per-run 1`

Observed:
- Runner completed with `processed=1` and `failed=0`.
- No rows were written into `email_triage_state.db` (dry-run is read-only with respect to state and Gmail writes).

### 2) Real run labels + records idempotency state

Command:
- `cd /home/zaks/bookkeeping/scripts && sudo -u zaks python3 -m email_triage_agent.run_once --max-per-run 1`

Observed:
- Runner completed with `processed=1` and `failed=0`.
- A new row was written to `email_triage_state.db` (stores message_id, status, classification/urgency, deal_id if detected, hashes; does not store email body).

### 3) Kinetic Actions API integration + idempotency key

Command (library call):
- `email_triage_agent.kinetic_actions.KineticActionsClient.create_action(...)`

Observed:
- First create returned `created_new=True` and an `ACT-...` action_id in `PENDING_APPROVAL`.
- Repeating the same call with the same `idempotency_key` returned `created_new=False` and the same action_id.

### 4) Safety constraints upheld

Code-level enforcement:
- Runner never calls Gmail “send” or “delete” tools.
- All outbound comms created via actions are `COMMUNICATION.DRAFT_EMAIL` (draft-only capability); no `COMMUNICATION.SEND_EMAIL` actions are emitted by the triage runner.
- URLs persisted to action inputs are scrubbed via `safe_url()` (query/fragment removed).

## Known limits (current)

- Deal linking: only high-confidence `DEAL-YYYY-NNN` IDs are detected deterministically today; other linking patterns remain “review-first”.
- Attachment quarantine: enforced allowlist/denylist; macro-enabled Office formats are blocked.


# n8n Webhooks (Optional, Local-Only)

ZakOps can emit a small set of local webhook events for peripheral automations (notifications, reminders, link follow-ups) without polluting core code paths.

## Safety

- Off by default: requires `N8N_WEBHOOKS_ENABLED=true`
- SSRF-safe: only allows localhost / loopback / RFC1918 webhook targets
- Best-effort: failures never break the primary workflow
- No secrets: event payloads contain only minimal metadata (no raw email bodies, no tokens)

## Enable

1) Start n8n (optional):

```bash
cd /home/zaks/bookkeeping
make n8n-up
```

2) Set env vars for emitters (runner/API services must see these env vars):

```bash
export N8N_WEBHOOKS_ENABLED=true
export ZAKOPS_N8N_WEBHOOK_URL="http://localhost:5678/webhook/zakops-events"
```

3) Import the starter workflows:
- `bookkeeping/docs/n8n_workflows/quarantine_webhook_receiver.json`
- `bookkeeping/docs/n8n_workflows/materials_webhook_receiver.json`

## Payload shape

All events use the same wrapper:

```json
{
  "event": "string",
  "timestamp": "2026-01-10T23:00:00Z",
  "payload": {}
}
```

## Events

### `quarantine.created`

Emitted when triage creates a quarantine/review item.

Payload:
- `message_id`
- `thread_id` (optional)
- `subject` (truncated)
- `sender` (truncated)
- `classification`

### `quarantine.approved`

Emitted when a quarantine item is approved and a deal is created/linked.

Payload:
- `message_id`
- `thread_id` (optional)
- `deal_id`
- `deal_folder`

### `quarantine.rejected`

Emitted when a quarantine item is rejected.

Payload:
- `message_id`
- `thread_id` (optional)
- `reason` (truncated)

### `materials.auth_required_links_detected`

Emitted when materials ingestion detects auth-required links for operator follow-up.

Payload:
- `deal_id`
- `auth_required_links` (count)

## Manual test

```bash
export N8N_WEBHOOKS_ENABLED=true
export ZAKOPS_N8N_WEBHOOK_URL="http://localhost:5678/webhook/zakops-events"

python3 - <<'PY'
from scripts.integrations.n8n_webhook import emit_quarantine_created
emit_quarantine_created(
    message_id="TEST_MESSAGE_ID",
    thread_id="TEST_THREAD_ID",
    subject="Test subject",
    sender="broker@example.com",
    classification="DEAL_SIGNAL",
)
print("ok")
PY
```


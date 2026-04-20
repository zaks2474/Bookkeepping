# Prompt 2 Verification — Actions Reliability + Comms Loop + Controller (P0/P2)

Date: 2026-01-03

This document captures **what was implemented**, **how it was verified**, and **what remains**.

## Non‑Negotiables Confirmed

- No automatic email sending (send is still an approval-gated Kinetic Action).
- No automatic email deletion.
- No LangSmith tracing enabled by this work.
- No secrets committed; configs reference only paths/env names.

## Runtime State (ports / processes)

Timestamp:
```bash
date -Iseconds
```
Output:
```text
2026-01-03T19:26:23-06:00
```

Listening services:
```bash
ss -ltnp | rg -n ":(8090|3003|3000|8080|8000|8052)\\b"
```
Output:
```text
2:LISTEN ... 0.0.0.0:8090 ... users:(("python3",pid=2067359,fd=6))
3:LISTEN ... 0.0.0.0:8080 ... users:(("docker-proxy",pid=1506303,fd=7))
6:LISTEN ... 0.0.0.0:8000 ... users:(("docker-proxy",pid=1501216,fd=7))
9:LISTEN ... 0.0.0.0:8052 ... users:(("docker-proxy",pid=166757,fd=7))
14:LISTEN ... 0.0.0.0:3000 ... users:(("docker-proxy",pid=812470,fd=7))
28:LISTEN ... *:3003 ... users:(("next-server (v1",pid=1463313,fd=19))
```

## Verification — Actions Engine (P0)

### Runner status includes stuck + error breakdown

```bash
curl -sS http://localhost:8090/api/actions/runner-status | jq '{timestamp, runner_alive, queue, stuck_processing, error_breakdown}'
```

Output:
```json
{
  "timestamp": "2026-01-04T01:26:23.818552+00:00",
  "runner_alive": true,
  "queue": {
    "pending_approval": 119,
    "ready": 4,
    "ready_queued": 0,
    "processing": 0
  },
  "stuck_processing": {
    "older_than_seconds": 180,
    "count": 0,
    "action_ids": []
  },
  "error_breakdown": [
    {
      "error": "runner_exception",
      "count": 1
    }
  ]
}
```

### Debug tooling surfaces broken rows (no silent drops)

```bash
curl -sS 'http://localhost:8090/api/actions/debug/missing-executors?limit=10' | jq '{count, missing_types, actions}'
```

Output:
```json
{
  "count": 1,
  "missing_types": [
    "EMAIL_TRIAGE.TEST"
  ],
  "actions": [
    {
      "action_id": "ACT-20260101T073657-a20c6a55",
      "deal_id": null,
      "capability_id": null,
      "type": "EMAIL_TRIAGE.TEST",
      "status": "FAILED",
      "created_at": "2026-01-01T07:36:57Z",
      "updated_at": "2026-01-01T16:29:59Z"
    }
  ]
}
```

### New capability exists: `DEAL.ENRICH_MATERIALS`

```bash
curl -sS 'http://localhost:8090/api/actions/capabilities' | jq '.capabilities[] | select(.action_type=="DEAL.ENRICH_MATERIALS") | {capability_id, action_type, requires_approval, risk_level}'
```

Output:
```json
{
  "capability_id": "deal.enrich_materials.v1",
  "action_type": "DEAL.ENRICH_MATERIALS",
  "requires_approval": false,
  "risk_level": "low"
}
```

## Verification — Quarantine as Action Queue (P0)

### Canonical quarantine endpoint returns triage actions

```bash
curl -sS 'http://localhost:8090/api/actions/quarantine?limit=1' | jq '.items[0] | {action_id, email_subject, sender, urgency, classification, quarantine_reason}'
```

Output:
```json
{
  "action_id": "ACT-20260103T021416-c5f966b5",
  "email_subject": "Welcome to Bitdefender!",
  "sender": "Bitdefender <no-reply@info.bitdefender.com>",
  "urgency": "HIGH",
  "classification": "DEAL_SIGNAL",
  "quarantine_reason": "HIGH urgency. Contains deal-related signals. deal_score=2.00 reasons=weak_keywords=['multiple']; attachments_score=+1.50"
}
```

### Legacy quarantine endpoints now include action-backed quarantine items

```bash
curl -sS http://localhost:8090/api/quarantine/health | jq '.'
curl -sS http://localhost:8090/api/quarantine | jq '.count'
```

Output:
```json
{"status":"attention_needed","pending_items":116,"oldest_pending_days":0}
```
```text
116
```

## Verification — Tests (Regression Coverage)

Unit tests:
```bash
bash /home/zaks/scripts/run_unit_tests.sh
```

Result (tail):
```text
Ran 46 tests in 5.053s

OK
```

New regression coverage added in `scripts/tests/test_prompt2_regressions.py`:
- Create-action validation rejects unknown executors and capability mismatches.
- Debug endpoints work (`missing-executors`).
- Quarantine endpoints return triage actions.
- Runner-status includes new fields.
- `unstick` endpoint transitions PROCESSING → READY.
- `DEAL.ENRICH_MATERIALS` executor is registered.

Additional regression coverage:
- `scripts/tests/test_actions_list_contract.py`: `/api/actions/capabilities` includes `cloud_required` for policy gating.
- `scripts/tests/test_email_triage_scope.py`: denylisted/newsletter patterns do not emit `DEAL_SIGNAL`.

## Verification — Capability Flags (Policy Gating)

Capabilities now expose `cloud_required` and `llm_allowed` so the dashboard/operator can see why an action may be blocked.

```bash
curl -sS 'http://localhost:8090/api/actions/capabilities' | jq '.capabilities[] | select(.capability_id=="communication.draft_email.v1") | {capability_id, cloud_required, llm_allowed}'
```

Expected:
```json
{"capability_id":"communication.draft_email.v1","cloud_required":true,"llm_allowed":true}
```

```bash
curl -sS http://localhost:8090/api/version | jq '.config.gemini_model_pro'
```

Expected:
```json
"gemini-2.5-pro"
```

## What Was Not Done / Remaining

- **No real email was sent** during verification (by design). `COMMUNICATION.SEND_EMAIL` is configured to use ToolGateway + Gmail MCP but should be exercised only with explicit operator approval and a test recipient.
- **Deal Lifecycle Controller**: script exists (`/home/zaks/scripts/deal_lifecycle_controller.py`) but no systemd timer/service was installed/enabled yet.
- **Quarantine backlog**: older triage runs produced some false positives that remain in `PENDING_APPROVAL`; current triage logic is stricter (denylist/newsletter tests added) but existing items may require manual cleanup.

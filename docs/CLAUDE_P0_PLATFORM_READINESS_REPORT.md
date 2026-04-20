# CLAUDE P0 Platform Readiness Report (Baseline Evidence)

- Generated: `2026-01-07T23:33:36-06:00`
- Host: `Zako`

## 0.1 Runtime + service inventory

### Listening ports (expected: 3003, 8090, 8080, 8000)

Command:

```bash
ss -ltnp | egrep ':(3003|8090|8080|8000)\b'
```

Output:

```
LISTEN 0      2048          0.0.0.0:8090       0.0.0.0:*    users:(("python3",pid=2945568,fd=6))         
LISTEN 0      4096          0.0.0.0:8080       0.0.0.0:*    users:(("docker-proxy",pid=1506303,fd=7))    
LISTEN 0      4096          0.0.0.0:8000       0.0.0.0:*    users:(("docker-proxy",pid=1501216,fd=7))    
LISTEN 0      4096             [::]:8080          [::]:*    users:(("docker-proxy",pid=1506310,fd=7))    
LISTEN 0      4096             [::]:8000          [::]:*    users:(("docker-proxy",pid=1501222,fd=7))    
LISTEN 0      511                 *:3003             *:*    users:(("next-server (v1",pid=2954452,fd=19))
```

### Kinetic Actions Runner (systemd)

Command:

```bash
systemctl status kinetic-actions-runner --no-pager
```

Output:

```
● kinetic-actions-runner.service - Kinetic Actions Runner (ZakOps Deal Lifecycle)
     Loaded: loaded (/etc/systemd/system/kinetic-actions-runner.service; enabled; preset: enabled)
     Active: active (running) since Tue 2026-01-06 21:57:53 CST; 1 day 1h ago
       Docs: file:///home/zaks/bookkeeping/docs/ACTIONS-E2E-IMPLEMENTATION-PLAN.md
   Main PID: 2572347 (python3)
      Tasks: 1 (limit: 38126)
     Memory: 96.5M (peak: 96.7M)
        CPU: 1min 31.826s
     CGroup: /system.slice/kinetic-actions-runner.service
             └─2572347 /usr/bin/python3 /home/zaks/scripts/actions_runner.py --runner-name=kinetic_actions --lease-seconds=30 --poll-seconds=2.0 --action-lock-seconds=300

Jan 06 21:57:53 Zako systemd[1]: Started kinetic-actions-runner.service - Kinetic Actions Runner (ZakOps Deal Lifecycle).
Jan 06 21:57:53 Zako kinetic-actions-runner[2572347]: WARNING:root:rapidfuzz not available, fuzzy matching disabled
```

### Email triage timer (systemd)

Command:

```bash
systemctl status zakops-email-triage.timer --no-pager
```

Output:

```
● zakops-email-triage.timer - ZakOps Email Triage (hourly)
     Loaded: loaded (/etc/systemd/system/zakops-email-triage.timer; enabled; preset: enabled)
     Active: active (waiting) since Thu 2026-01-01 10:49:24 CST; 6 days ago
    Trigger: Thu 2026-01-08 00:03:18 CST; 32min left
   Triggers: ● zakops-email-triage.service

Jan 01 10:49:24 Zako systemd[1]: Started zakops-email-triage.timer - ZakOps Email Triage (hourly).
```

### Deal lifecycle controller timer (systemd)

Command:

```bash
systemctl status zakops-deal-lifecycle-controller.timer --no-pager
```

Output:

```
● zakops-deal-lifecycle-controller.timer - ZakOps Deal Lifecycle Controller (hourly)
     Loaded: loaded (/etc/systemd/system/zakops-deal-lifecycle-controller.timer; enabled; preset: enabled)
     Active: active (waiting) since Sat 2026-01-03 20:33:22 CST; 4 days ago
    Trigger: Thu 2026-01-08 00:05:17 CST; 34min left
   Triggers: ● zakops-deal-lifecycle-controller.service

Jan 03 20:33:22 Zako systemd[1]: Started zakops-deal-lifecycle-controller.timer - ZakOps Deal Lifecycle Controller (hourly).
```

### Backend version/config snapshot (8090)

Command:

```bash
curl -s http://localhost:8090/api/version | jq .
```

Output:

```json
{
  "git_commit": "da593b15b7f8",
  "server_pid": 2945568,
  "server_start_time": "2026-01-08T05:01:03.698652Z",
  "config": {
    "openai_api_base": "http://localhost:8000/v1",
    "allow_cloud_default": "false",
    "gemini_model_pro": "gemini-2.5-pro",
    "registry_path": "unknown",
    "case_file_dir": "unknown"
  }
}
```

### Dashboard proxy snapshot (3003 → /api/actions sample)

Command:

```bash
curl -s http://localhost:3003/api/actions | jq '.actions[0]'
```

Output (example action record):

```json
{
  "action_id": "ACT-20260108T052327-516652e8",
  "deal_id": "GLOBAL",
  "type": "EMAIL_TRIAGE.REJECT_EMAIL",
  "title": "Reject email (non-deal)",
  "summary": "Rejected as non-deal",
  "status": "PENDING_APPROVAL",
  "created_at": "2026-01-08T05:23:27Z",
  "updated_at": "2026-01-08T05:23:27Z",
  "created_by": "zaks",
  "source": "ui",
  "risk_level": "low",
  "requires_human_review": true,
  "idempotency_key": "879687e9ea713d08d157429890e99e585dc605fda565830de64426dfc3b37fee",
  "inputs": {
    "message_id": "19b023ef07e81c67",
    "thread_id": "19b023ef07e81c67"
  },
  "outputs": {},
  "retry_count": 0,
  "max_retries": 3,
  "audit_trail": [],
  "artifacts": [],
  "steps": [],
  "action_type": "EMAIL_TRIAGE.REJECT_EMAIL"
}
```

## 0.2 Prove Quarantine E2E (API + preview)

### Quarantine queue sample

Command:

```bash
curl -s 'http://localhost:8090/api/actions/quarantine?limit=5' | jq '{count, first: (.items[0] | {action_id,status,classification,confidence,quarantine_dir,triage_summary_path})}'
```

Output:

```json
{
  "count": 5,
  "first": {
    "action_id": "ACT-20260106T150129-d45f9c03",
    "status": "PENDING_APPROVAL",
    "classification": "DEAL_SIGNAL",
    "confidence": null,
    "quarantine_dir": "/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/19b93d33ea80febc",
    "triage_summary_path": null
  }
}
```

### Preview endpoint shape

Command:

```bash
curl -s 'http://localhost:8090/api/actions/quarantine/ACT-20260106T150129-d45f9c03/preview' | jq 'keys'
```

Output:

```json
[
  "action_id",
  "attachments",
  "created_at",
  "deal_id",
  "email",
  "extracted_fields",
  "from",
  "links",
  "message_id",
  "quarantine_dir",
  "received_at",
  "status",
  "subject",
  "summary",
  "thread_id",
  "thread_resolution",
  "to"
]
```

### UI verification (manual)

- Open: `http://localhost:3003/quarantine`
- Confirm: left list loads, selecting an item loads preview, and **Approve** / **Reject** buttons are present.

## 0.3 Prove Actions lifecycle: Approve → Execute → Completed

### Approve endpoint (PENDING_APPROVAL → READY)

Command:

```bash
curl -s -X POST 'http://localhost:8090/api/actions/ACT-20260106T130122-753d4662/approve' -H 'Content-Type: application/json' -d '{"approved_by":"zaks"}' | jq '{success, action: {action_id: .action.action_id, status: .action.status}}'
```

Output:

```json
{
  "success": true,
  "action": {
    "action_id": "ACT-20260106T130122-753d4662",
    "status": "READY"
  }
}
```

Target action used:

- `action_id`: `ACT-20260106T150129-d45f9c03`
- `type`: `EMAIL_TRIAGE.REVIEW_EMAIL` (local-only filesystem effects; no send/no delete)

### Execute request

Command:

```bash
curl -s -X POST 'http://localhost:8090/api/actions/ACT-20260106T150129-d45f9c03/execute' -H 'Content-Type: application/json' -d '{}' | jq .
```

Key facts from response:
- `success: true`
- audit trail includes `approved` and `execution_requested`

### Poll to terminal

Command:

```bash
for i in {1..30}; do st=$(curl -s 'http://localhost:8090/api/actions/ACT-20260106T150129-d45f9c03' | jq -r '.status'); echo "$i $st"; if [[ "$st" == "COMPLETED" || "$st" == "FAILED" || "$st" == "CANCELLED" ]]; then break; fi; sleep 1; done
```

Output:

```
1 COMPLETED
```

### Terminal state summary

Command:

```bash
curl -s 'http://localhost:8090/api/actions/ACT-20260106T150129-d45f9c03' | jq '{action_id,status,outputs: (.outputs|keys), artifacts_count:(.artifacts|length), error}'
```

Output:

```json
{
  "action_id": "ACT-20260106T150129-d45f9c03",
  "status": "COMPLETED",
  "outputs": [
    "created_new_deal",
    "deal_folder",
    "deal_id",
    "email_artifacts",
    "next_actions"
  ],
  "artifacts_count": 2,
  "error": null
}
```

Deal created by this action:

```
DEAL-2026-090
/home/zaks/DataRoom/00-PIPELINE/Inbound/Biotech-Content-Business-75-Net-Margins-Strong-Growth-with-Untapped-Upside-2026
```

## 0.4 Prove Materials endpoint behavior (no 500s)

Command:

```bash
curl -s 'http://localhost:8090/api/deals/DEAL-2026-090/materials' | jq 'keys'
```

Output:

```json
[
  "aggregate_links",
  "correspondence",
  "deal_id",
  "deal_path",
  "pending_auth"
]
```

Counts:

```json
{
  "deal_id": "DEAL-2026-090",
  "deal_path": "/home/zaks/DataRoom/00-PIPELINE/Inbound/Biotech-Content-Business-75-Net-Margins-Strong-Growth-with-Untapped-Upside-2026",
  "correspondence_count": 1,
  "pending_auth_count": 6,
  "aggregate_links_keys": [
    "links"
  ]
}
```

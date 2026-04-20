# ZakOps Verification Commands (Smoke Checks)

These commands are designed to be copy/pasteable and to produce **hard evidence** of system health.  
Avoid posting outputs externally (may contain deal/email metadata). No secrets are required.

## 1) Runtime inventory (ports + processes)

```bash
ss -ltnp | rg ':(3003|8090|8080|8000|8002|8051|8052|3000|11434)\\b'
docker ps --format 'table {{.Names}}\\t{{.Ports}}\\t{{.Status}}'
ps aux | rg -n 'python3 .*deal_lifecycle_api|python3 .*actions_runner|next-server'
```

## 2) Backend health + runner observability

```bash
curl -sS http://localhost:8090/health | jq .
curl -sS http://localhost:8090/api/version | jq .
curl -sS http://localhost:8090/api/actions/runner-status | jq .
curl -sS http://localhost:8090/api/actions/metrics | jq .
```

If the runner appears dead:
```bash
systemctl show kinetic-actions-runner.service -p ActiveState -p SubState -p MainPID -p ExecStart
sudo systemctl restart kinetic-actions-runner.service
curl -sS http://localhost:8090/api/actions/runner-status | jq .
```

## 3) Frontend → backend proxy correctness

The dashboard proxies `/api/*` → `http://localhost:8090/api/*` by default (`zakops-dashboard/next.config.ts`).

```bash
curl -sS http://localhost:3003/api/actions/capabilities | jq '.count'
curl -sS http://localhost:8090/api/actions/capabilities | jq '.count'
```

Both should return the same capability count and **not** a FastAPI `{"detail":"Not Found"}` 404.

## 4) Kinetic Actions lifecycle (create → approve → execute → artifacts)

This smoke test exercises the **Quarantine → Deal creation** executor (`EMAIL_TRIAGE.REVIEW_EMAIL`) without Gmail access.

### 4.1 Create a synthetic quarantine payload (filesystem)

```bash
SMOKE_ID="SMOKE-MSG-$(date +%s)"
QDIR="/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/$SMOKE_ID"
mkdir -p "$QDIR"
printf '%s\n' "Synthetic email body for smoke test." > "$QDIR/email_body.txt"
printf '%s\n' '{"message_id":"'"$SMOKE_ID"'","thread_id":"","from":"smoke@example.com","to":"zak@example.com","date":"","subject":"Smoke Test Deal"}' > "$QDIR/email.json"
```

### 4.2 Create the action (PENDING_APPROVAL)

```bash
ACTION_ID=$(
  curl -sS http://localhost:8090/api/actions \
    -H 'Content-Type: application/json' \
    -d @- <<JSON | jq -r '.action.action_id'
{
  "deal_id": null,
  "action_type": "EMAIL_TRIAGE.REVIEW_EMAIL",
  "capability_id": "email_triage.review_email.v1",
  "title": "Smoke: Review inbound deal email",
  "summary": "Smoke test",
  "created_by": "smoke",
  "source": "system",
  "risk_level": "medium",
  "requires_human_review": true,
  "idempotency_key": "smoke:email_triage_review_email:'"$SMOKE_ID"'",
  "inputs": {
    "message_id": "'"$SMOKE_ID"'",
    "subject": "Smoke Test Deal",
    "from": "smoke@example.com",
    "to": "zak@example.com",
    "date": "",
    "quarantine_dir": "'"$QDIR"'",
    "links": [],
    "attachments": []
  }
}
JSON
)
echo "$ACTION_ID"
curl -sS "http://localhost:8090/api/actions/$ACTION_ID" | jq '.status,.deal_id,.action_type'
```

### 4.3 Approve (→ READY) and request execute

```bash
curl -sS "http://localhost:8090/api/actions/$ACTION_ID/approve" \
  -H 'Content-Type: application/json' \
  -d '{"approved_by":"smoke"}' | jq '.success,.action.status'

curl -sS "http://localhost:8090/api/actions/$ACTION_ID/execute" \
  -H 'Content-Type: application/json' \
  -d '{"requested_by":"smoke"}' | jq '.success,.action.status'
```

### 4.4 Wait for completion and verify artifacts/download

```bash
for i in $(seq 1 60); do
  STATUS=$(curl -sS "http://localhost:8090/api/actions/$ACTION_ID" | jq -r '.status')
  echo "status=$STATUS"
  if [ "$STATUS" = "COMPLETED" ] || [ "$STATUS" = "FAILED" ] || [ "$STATUS" = "CANCELLED" ]; then
    break
  fi
  sleep 1
done

curl -sS "http://localhost:8090/api/actions/$ACTION_ID" | jq '.status,.outputs,.artifacts'

# download first artifact (if any)
ARTIFACT_ID=$(curl -sS "http://localhost:8090/api/actions/$ACTION_ID" | jq -r '.artifacts[0].artifact_id // empty')
if [ -n "$ARTIFACT_ID" ]; then
  curl -sS -D /tmp/artifact.headers "http://localhost:8090/api/actions/$ACTION_ID/artifact/$ARTIFACT_ID" -o /tmp/artifact.bin
  head -n 20 /tmp/artifact.headers
  ls -la /tmp/artifact.bin
fi
```

If it gets stuck, use:
```bash
curl -sS "http://localhost:8090/api/actions/$ACTION_ID/debug" | jq .
```

## 5) Email triage smoke (safe mode)

This hits Gmail; run in **dry-run** first so it does not label or download.

```bash
cd /home/zaks/bookkeeping/scripts
EMAIL_TRIAGE_DRY_RUN=true python3 -m email_triage_agent.run_once --max-per-run 5
```

Check scheduled runs:
```bash
systemctl status zakops-email-triage.timer
systemctl status zakops-email-triage.service
```

## 6) Unit tests (backend correctness suite)

```bash
bash /home/zaks/scripts/run_unit_tests.sh
```

This suite includes lifecycle/idempotency/lease/tool-gate coverage (see `/home/zaks/scripts/tests/test_*.py`).

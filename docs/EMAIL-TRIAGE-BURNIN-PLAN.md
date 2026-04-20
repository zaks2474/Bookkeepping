# 7-Day Shadow Burn-In Execution Plan

**Service:** ZakOps Email Triage Pipeline
**Phase:** P8-06 (Operational Excellence Gate)
**Created:** 2026-02-15

---

## Objective

Run the Email Triage agent in shadow mode for 7 consecutive days, collecting
precision/recall data to validate classification accuracy before production
graduation.

## Prerequisites

1. All Phase 0-7 gates passed
2. SLOs defined (P8-01)
3. Monitoring configured (P8-02)
4. Backup drill completed (P8-04)
5. Shadow measurement scripts ready (P8-05)

## Production Safety Flags (G8-06)

These flags MUST be set before and during the burn-in:

| Flag | Required Value | Purpose |
|------|---------------|---------|
| `shadow_mode` | `true` (ON) | All items tagged `langsmith_shadow` |
| `auto_route` | `false` (OFF) | No automatic deal routing |
| `delegate_actions` | `false` (OFF) | No agent-initiated actions |
| `send_email_enabled` | `false` (OFF) | No outbound email |
| `email_triage_writes_enabled` | `true` (ON) | Pipeline accepting items |

### Verify Flags
```bash
curl -sf http://localhost:8091/api/admin/flags | python3 -m json.tool
```

### Set Flag (if needed)
```bash
curl -X PUT http://localhost:8091/api/admin/flags/<name> \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## Daily Check Procedure

Run each morning during the 7-day burn-in:

### 1. Health Check
```bash
bash /home/zaks/bookkeeping/scripts/email_triage_health_probe.sh
```

### 2. Volume Check
```sql
-- Items injected in last 24h
SELECT COUNT(*), source_type
FROM zakops.quarantine_items
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY source_type;
```

### 3. Classification Report
```bash
python3 /home/zaks/bookkeeping/scripts/shadow_measurement.py --since 24h
```

### 4. Cumulative Report
```bash
python3 /home/zaks/bookkeeping/scripts/shadow_measurement.py --since 7d \
  --output /home/zaks/bookkeeping/docs/shadow_report_day_N.md
```

### 5. Flag Verification
```bash
curl -sf http://localhost:8091/api/admin/flags | python3 -c "
import sys, json
flags = json.load(sys.stdin)
if isinstance(flags, list):
    for f in flags:
        print(f'{f[\"name\"]}: {\"ON\" if f[\"enabled\"] else \"OFF\"}')"
```

---

## Success Criteria

After 7 days, the system is ready for production graduation when:

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Minimum volume | >= 50 shadow items | Total count query |
| Classification accuracy | >= 85% | Operator review of sample |
| Entity recall (company) | >= 75% | Shadow measurement script |
| Entity recall (broker) | >= 75% | Shadow measurement script |
| Required field NULLs | 0 | Field completeness check |
| Triage summary rate | >= 95% | Shadow measurement script |
| Pipeline uptime | >= 99.5% | Health probe logs |
| Kill switch false trips | 0 | Alert log review |
| Unhandled errors | 0 critical | Alert log review |

---

## Burn-In Schedule

| Day | Activities |
|-----|-----------|
| 1 | Start burn-in. Verify injection flow. Run initial measurement. |
| 2 | Daily check. Review first batch of classifications. |
| 3 | Daily check. Begin operator review of random sample (10 items). |
| 4 | Daily check. Mid-point measurement report. |
| 5 | Daily check. Continue operator review. |
| 6 | Daily check. Run load test profile (P8-03) during burn-in. |
| 7 | Final measurement. Generate graduation report. Flag state audit. |

---

## Graduation Decision

After Day 7:

1. Run final shadow measurement:
   ```bash
   python3 /home/zaks/bookkeeping/scripts/shadow_measurement.py --since 7d \
     --output /home/zaks/bookkeeping/docs/SHADOW-BURNIN-FINAL-REPORT.md
   ```

2. Review all success criteria in table above.

3. If ALL criteria met:
   - Document graduation decision in CHANGES.md
   - Schedule transition: `shadow_mode` OFF, `auto_route` ON (phased)
   - Keep `delegate_actions` and `send_email_enabled` OFF until Phase 9+

4. If ANY criteria NOT met:
   - Document specific failures
   - Extend burn-in or adjust agent configuration
   - Re-run from Day 1

---

## Rollback

If issues arise during burn-in:
1. Activate kill switch: `curl -X PUT .../api/admin/flags/email_triage_writes_enabled -d '{"enabled":false}'`
2. Investigate via health probe logs and alert log
3. Re-enable after fix: `curl -X PUT .../api/admin/flags/email_triage_writes_enabled -d '{"enabled":true}'`

Production flags remain in safe state throughout burn-in — no rollback needed for
`auto_route`, `delegate_actions`, or `send_email_enabled` (already OFF).

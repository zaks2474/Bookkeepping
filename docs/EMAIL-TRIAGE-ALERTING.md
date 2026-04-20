# Email Triage Monitoring & Alerting Configuration

**Service:** ZakOps Email Triage Pipeline
**Phase:** P8-02 (Operational Excellence Gate)
**Created:** 2026-02-15

---

## Health Check Configuration

### Synthetic Probe (every 60 seconds)

```bash
# Crontab entry (add via: crontab -e)
* * * * * /home/zaks/bookkeeping/scripts/email_triage_health_probe.sh >> /home/zaks/bookkeeping/logs/triage_health.log 2>&1
```

### Probe Script

The probe checks 4 endpoints every 60 seconds and logs results:

| Check | Endpoint | Expected | Timeout |
|-------|----------|----------|---------|
| Backend Health | `GET :8091/health` | 200 | 5s |
| Quarantine API | `GET :8091/api/quarantine?limit=1` | 200 | 10s |
| Bridge Health | `GET :8095/health` | 200 | 5s |
| Dashboard | `GET :3003/quarantine` | 200 | 10s |

---

## Alert Rules

### P0: Critical Alerts (page immediately)

#### Kill Switch Activation
- **Trigger:** `email_triage_writes_enabled` flag set to `false`
- **Detection:** Health probe receives 503 on quarantine write test
- **Action:** Log alert, notify operator
- **Severity:** critical

#### Backend Down
- **Trigger:** Backend health check fails for 2 consecutive probes (2 min)
- **Detection:** `GET :8091/health` returns non-200 or timeout
- **Severity:** critical

#### Bridge Down
- **Trigger:** Bridge health check fails for 2 consecutive probes (2 min)
- **Detection:** `GET :8095/health` returns non-200 or timeout
- **Severity:** critical

### P1: Warning Alerts (investigate within 1 hour)

#### Queue Depth High
- **Trigger:** > 20 pending quarantine items for > 30 minutes
- **Detection:** `GET :8091/api/quarantine?status=pending` count > 20
- **Query:** `SELECT COUNT(*) FROM zakops.quarantine_items WHERE status = 'pending'`
- **Severity:** warning

#### Queue Depth Critical
- **Trigger:** > 50 pending quarantine items for > 15 minutes
- **Severity:** critical

#### Escalation Backlog
- **Trigger:** > 5 escalated items unresolved for > 4 hours
- **Detection:** `SELECT COUNT(*) FROM zakops.quarantine_items WHERE status = 'escalated' AND updated_at < NOW() - INTERVAL '4 hours'`
- **Severity:** warning

#### Dead Letter Tasks
- **Trigger:** Any delegated task in `dead_letter` status
- **Detection:** `SELECT COUNT(*) FROM zakops.delegated_tasks WHERE status = 'dead_letter'`
- **Severity:** warning

### P2: Informational (daily digest)

#### Shadow Injection Volume
- **Metric:** Count of items injected in last 24 hours
- **Query:** `SELECT COUNT(*) FROM zakops.quarantine_items WHERE created_at > NOW() - INTERVAL '24 hours'`
- **Expected:** 100-500/day during shadow pilot

#### Classification Distribution
- **Metric:** Breakdown by classification in last 24 hours
- **Query:** `SELECT classification, COUNT(*) FROM zakops.quarantine_items WHERE created_at > NOW() - INTERVAL '24 hours' GROUP BY classification`

#### Operator Activity
- **Metric:** Items processed per operator in last 24 hours
- **Query:** `SELECT processed_by, COUNT(*) FROM zakops.quarantine_items WHERE status IN ('approved','rejected') AND updated_at > NOW() - INTERVAL '24 hours' GROUP BY processed_by`

---

## Monitoring Dashboard Queries

### Real-Time Queue Status
```sql
SELECT
  status,
  COUNT(*) as count,
  MIN(created_at) as oldest,
  AVG(EXTRACT(EPOCH FROM (NOW() - created_at))) as avg_age_seconds
FROM zakops.quarantine_items
GROUP BY status
ORDER BY status;
```

### Injection Rate (hourly)
```sql
SELECT
  date_trunc('hour', created_at) as hour,
  COUNT(*) as injections,
  AVG(confidence) as avg_confidence
FROM zakops.quarantine_items
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY 1
ORDER BY 1;
```

### Processing Throughput
```sql
SELECT
  date_trunc('hour', updated_at) as hour,
  COUNT(*) FILTER (WHERE status = 'approved') as approved,
  COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
  COUNT(*) FILTER (WHERE status = 'escalated') as escalated,
  AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_triage_seconds
FROM zakops.quarantine_items
WHERE updated_at > NOW() - INTERVAL '24 hours'
  AND status IN ('approved', 'rejected', 'escalated')
GROUP BY 1
ORDER BY 1;
```

### Feature Flag Status
```sql
SELECT name, enabled, description, updated_at
FROM zakops.feature_flags
ORDER BY name;
```

---

## Alert Notification Channels

| Channel | Use Case | Configuration |
|---------|----------|--------------|
| Console log | All alerts | `/home/zaks/bookkeeping/logs/triage_health.log` |
| Email | Critical alerts | zaks373631@gmail.com (via Lab Loop notification system) |
| Dashboard | Queue depth | Built-in quarantine page count |

---

## Runbook References

| Alert | Runbook |
|-------|---------|
| Kill Switch Activated | Check `feature_flags` table, verify backend logs for cause |
| Backend Down | `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose restart backend` |
| Bridge Down | `docker compose restart agent-api` in `/home/zaks/zakops-agent-api/apps/agent-api/` |
| Queue Depth High | Check injection rate, verify operators are active, consider bulk processing |
| Dead Letter Tasks | Review task in dashboard, retry or manual resolution |

# Alerting Rules (Prometheus/Grafana)

These are recommended alert rules for ZakOps in a single-operator local lab. Tune thresholds to your volume.

All rules assume Prometheus scrapes `http://localhost:8090/metrics`.

## P0 Alerts (operability)

### Runner down

Trigger when the kinetic actions runner lease is not healthy.

PromQL:
```promql
zakops_runner_alive == 0
```

Suggested:
- `for: 5m`
- severity: `critical`

### Gmail MCP down

PromQL:
```promql
zakops_gmail_mcp_ok == 0
```

Suggested:
- `for: 10m`
- severity: `critical`

### Quarantine backlog high

PromQL:
```promql
zakops_quarantine_pending > 20
```

Suggested:
- `for: 30m`
- severity: `warning`

## P1 Alerts (reliability)

### Stuck PROCESSING actions

PromQL:
```promql
zakops_actions_stuck_processing > 0
```

Suggested:
- `for: 10m`
- severity: `warning`

## Notes

- `false_positive_rate` is evaluated via `bookkeeping/docs/EMAIL_TRIAGE_EVAL_REPORT.md` (operator feedback), not via Prometheus metrics.
- For Temporal health, use the Temporal UI `http://localhost:8233` (or add a dedicated `/api/temporal/status` endpoint later).


=== R2-9: Error Alerting & User Attribution COMPLETE ===

**Status:** PASS
**Date:** 2026-02-04

## Summary
Implemented error alerting infrastructure and enhanced user attribution
for deal events. Added centralized alerting module with rate limiting,
Slack integration, and metrics endpoint for monitoring.

## Implementation

### 1. Alerting Module
Files created:
- `/home/zaks/zakops-backend/src/core/alerting/__init__.py`
- `/home/zaks/zakops-backend/src/core/alerting/alerts.py`

Features:
- `AlertLevel` enum (INFO, WARNING, ERROR, CRITICAL)
- `AlertManager` class with rate limiting to prevent alert storms
- Slack webhook integration (optional)
- `send_alert()` convenience function

```python
class AlertManager:
    # Rate limiting: max 3 alerts per key per 60 seconds
    async def send(self, alert: Alert) -> bool:
        if self._is_rate_limited(key):
            return False
        # Log + send to Slack if configured
```

### 2. Metrics Middleware Enhancement
File: `/home/zaks/zakops-backend/src/api/shared/middleware/metrics.py`

Added:
- Alert triggering for 500 errors
- Metrics recording for aggregation
- `ALERTING_ENABLED` environment variable

```python
if status_code >= 500:
    if ALERTING_ENABLED:
        asyncio.create_task(self._send_error_alert(...))
```

### 3. Metrics Endpoint
File: `/home/zaks/zakops-backend/src/api/shared/routers/health.py`

Added `GET /health/metrics`:
```json
{
  "timestamp": "2026-02-04T20:53:35.208639",
  "metrics": {
    "request_count": 11,
    "error_count": 0,
    "avg_duration_ms": 5.74,
    "error_rate": 0.0
  },
  "config": {
    "slow_request_threshold_ms": 1000.0,
    "metrics_enabled": "true",
    "alerting_enabled": "true"
  }
}
```

### 4. User Attribution Enhancement
File: `/home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py`

Transition endpoint now extracts actor from authenticated operator:
```python
# R2-9: Get actor from authenticated operator if available
actor = transitioned_by
if not actor:
    operator = get_current_operator(request)
    if operator:
        actor = getattr(operator, 'email', None) or ...
```

## Verification Test

```
=== R2-9 Test: Metrics Endpoint ===
GET /health/metrics
{
    "metrics": {
        "request_count": 11,
        "error_count": 0,
        "avg_duration_ms": 5.74,
        "error_rate": 0.0
    }
}

=== R2-9 Test: Alerting Logs ===
[R2-8] Client error: GET /api/nonexistent -> 404 (0ms)
  trace_id: "no-trace"
  method: "GET"
  path: "/api/nonexistent"
  status_code: 404
  duration_ms: 0.42
```

## Gates

- [x] AlertManager with rate limiting implemented
- [x] Slack webhook integration (optional, via SLACK_WEBHOOK_URL)
- [x] 500 errors trigger alerts
- [x] /health/metrics endpoint returns request stats
- [x] User attribution from operator on transitions

## Environment Variables

- `ALERTING_ENABLED` (default: true) - Enable/disable error alerts
- `SLACK_WEBHOOK_URL` (optional) - Slack webhook for alerts

## Files Created/Modified

1. `/home/zaks/zakops-backend/src/core/alerting/__init__.py` (NEW)
2. `/home/zaks/zakops-backend/src/core/alerting/alerts.py` (NEW)
   - AlertLevel enum
   - Alert dataclass
   - AlertManager class
   - send_alert() function

3. `/home/zaks/zakops-backend/src/api/shared/middleware/metrics.py`
   - Added ALERTING_ENABLED config
   - Added _send_error_alert() method
   - Added metrics.record() call

4. `/home/zaks/zakops-backend/src/api/shared/routers/health.py`
   - Added GET /health/metrics endpoint

5. `/home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py`
   - Added operator-based user attribution
   - Import get_current_operator

## Alert Rate Limiting

Prevents alert storms with configurable limits:
- Default: 3 alerts per key per 60 seconds
- Key format: `{level}:{source}:{title}`
- Configurable via AlertManager constructor

## Next Steps

- Configure SLACK_WEBHOOK_URL for production alerts
- Add email alerting channel
- Add PagerDuty integration for critical alerts
- Create Grafana dashboard from /health/metrics data

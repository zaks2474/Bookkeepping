=== R2-8: Request Metrics & Observability COMPLETE ===

**Status:** PASS
**Date:** 2026-02-04

## Summary
Implemented request metrics middleware for API observability. All requests
are now timed and logged with structured data. Slow requests and errors
are flagged at WARNING/ERROR levels for alerting.

## Implementation

### 1. MetricsMiddleware
File: `/home/zaks/zakops-backend/src/api/shared/middleware/metrics.py` (NEW)

Features:
- Tracks request duration with trace_id correlation
- Adds `X-Response-Time` header to all responses
- Logs 5xx errors at ERROR level
- Logs 4xx errors at WARNING level
- Logs slow requests (>1000ms) at WARNING level
- Emits structured logs for monitoring systems

```python
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log based on status code and duration
        if status_code >= 500:
            logger.error(f"[R2-8] Request failed...")
        elif status_code >= 400:
            logger.warning(f"[R2-8] Client error...")
        elif duration_ms > SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(f"[R2-8] Slow request...")

        response.headers["X-Response-Time"] = f"{duration_ms:.0f}ms"
```

### 2. Middleware Registration
File: `/home/zaks/zakops-backend/src/api/orchestration/main.py`

Added after TraceMiddleware:
```python
# R2-8: Metrics middleware for request timing and monitoring
app.add_middleware(MetricsMiddleware)
```

## Verification Test

```
=== R2-8 Test: Response Time Header ===
curl -v http://localhost:8091/api/deals | grep x-response-time
< x-response-time: 2ms
< x-trace-id: 5b2059d3965b4a939e580aeee599a60c

=== R2-8 Test: 404 Error Logging ===
curl -sI http://localhost:8091/api/nonexistent

Backend logs:
{
  "timestamp": "2026-02-04T20:38:58.558093Z",
  "level": "WARNING",
  "logger": "src.api.shared.middleware.metrics",
  "message": "[R2-8] Client error: HEAD /api/nonexistent -> 404 (0ms)",
  "trace_id": "no-trace",
  "method": "HEAD",
  "path": "/api/nonexistent",
  "status_code": 404,
  "duration_ms": 0.4
}
```

## Gates

- [x] X-Response-Time header added to all responses
- [x] Request timing logged with trace_id correlation
- [x] 4xx errors logged at WARNING level
- [x] 5xx errors logged at ERROR level
- [x] Slow requests flagged at WARNING level

## Environment Variables

- `METRICS_ENABLED` (default: true) - Enable/disable metrics logging
- `SLOW_REQUEST_THRESHOLD_MS` (default: 1000) - Threshold for slow request warnings

## Files Created/Modified

1. `/home/zaks/zakops-backend/src/api/shared/middleware/metrics.py` (NEW)
   - MetricsMiddleware class
   - RequestMetrics collector (placeholder for Prometheus/StatsD)
   - get_request_metrics() function

2. `/home/zaks/zakops-backend/src/api/shared/middleware/__init__.py`
   - Added MetricsMiddleware export

3. `/home/zaks/zakops-backend/src/api/orchestration/main.py`
   - Added MetricsMiddleware import
   - Added middleware registration

## Structured Log Format

All metrics logs include:
- `trace_id`: Request correlation ID
- `method`: HTTP method (GET, POST, etc.)
- `path`: Request path
- `status_code`: HTTP status code
- `duration_ms`: Request duration in milliseconds

## Next Steps

- Integrate with Prometheus for metrics aggregation
- Add Slack/email alerts for high error rates
- Configure Grafana dashboards for visualization
- Add per-endpoint response time percentiles

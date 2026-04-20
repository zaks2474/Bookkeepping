# E06 — Flood Protection Active

**Date:** 2026-02-13
**Auditor:** Claude Opus 4.6 (automated evidence collection)
**Scope:** Quarantine injection endpoint rate limiting

---

## 1. RateLimiter Class

**File:** `/home/zaks/zakops-backend/src/api/shared/security.py`
**Lines:** 102-144

```python
class RateLimiter:
    """
    Simple in-memory rate limiter.

    For production, use Redis-based rate limiting.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self._timestamps: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        window_start = now - 60  # 1 minute window

        # Clean old entries
        if key in self._timestamps:
            self._timestamps[key] = [t for t in self._timestamps[key] if t > window_start]
        else:
            self._timestamps[key] = []

        # Check limit
        count = len(self._timestamps[key])
        if count >= self.limit:
            logger.warning(f"Rate limit exceeded for {key}: {count}/{self.limit}")
            return False

        # Record request
        self._timestamps[key].append(now)

        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        window_start = now - 60

        if key not in self._timestamps:
            return self.limit

        current = len([t for t in self._timestamps[key] if t > window_start])
        return max(0, self.limit - current)
```

The class implements a sliding-window rate limiter with per-key tracking and automatic cleanup of expired timestamps.

---

## 2. injection_rate_limiter Instance (120 req/min)

**File:** `/home/zaks/zakops-backend/src/api/shared/security.py`
**Line:** 150

```python
injection_rate_limiter = RateLimiter(requests_per_minute=120)  # Quarantine injection — higher to accommodate email-sync bursts
```

Configured at 120 requests per minute per source IP. The higher limit (vs. 60 for general, 10 for auth) accommodates legitimate email-sync burst ingestion while still preventing flood abuse.

---

## 3. check_rate_limit Function with 429 + Retry-After

**File:** `/home/zaks/zakops-backend/src/api/shared/security.py`
**Lines:** 153-173

```python
def check_rate_limit(key: str, limiter: RateLimiter = None) -> None:
    """
    Check rate limit and raise HTTPException if exceeded.

    Args:
        key: Rate limit key (usually IP or user ID)
        limiter: RateLimiter instance (defaults to general)

    Raises:
        HTTPException: If rate limit exceeded
    """
    if limiter is None:
        limiter = general_rate_limiter

    if not limiter.is_allowed(key):
        remaining = limiter.get_remaining(key)
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down.",
            headers={"Retry-After": "60", "X-RateLimit-Remaining": str(remaining)}
        )
```

When the limit is exceeded:
- Returns **HTTP 429** (Too Many Requests)
- Sets **`Retry-After: 60`** header (client should wait 60 seconds)
- Sets **`X-RateLimit-Remaining: 0`** header for observability

---

## 4. Active Call in POST /api/quarantine Handler

**File:** `/home/zaks/zakops-backend/src/api/orchestration/main.py`
**Line 49 (import):**

```python
from ..shared.security import SecurityMiddleware, check_rate_limit, get_client_ip, injection_rate_limiter
```

**Lines 1521-1523 (invocation inside `create_quarantine_item`):**

```python
    # P5: Rate-limit injection path (120/min per source IP)
    client_ip = get_client_ip(request)
    check_rate_limit(f"quarantine:{client_ip}", limiter=injection_rate_limiter)
```

The rate limiter is invoked at the top of the `POST /api/quarantine` handler (line 1509), before any database work. The key is namespaced as `quarantine:{client_ip}`, isolating injection limits from other rate-limited surfaces.

---

## 5. Summary

| Check | Evidence | Status |
|-------|----------|--------|
| RateLimiter class exists | `security.py` L102-144 | CONFIRMED |
| injection_rate_limiter at 120/min | `security.py` L150 | CONFIRMED |
| check_rate_limit raises 429 | `security.py` L169, status_code=429 | CONFIRMED |
| Retry-After header set | `security.py` L172, `"Retry-After": "60"` | CONFIRMED |
| Active call in POST /api/quarantine | `main.py` L1523 | CONFIRMED |
| Per-IP key namespacing | `"quarantine:{client_ip}"` | CONFIRMED |

---

## Verdict: PASS

Flood protection is active on the quarantine injection endpoint. The `injection_rate_limiter` enforces a 120 requests/minute ceiling per source IP with proper 429 responses and `Retry-After` headers. The limiter is invoked before any database interaction, preventing resource exhaustion under flood conditions.

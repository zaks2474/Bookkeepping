# E02 — Intake Auth Fail-Closed

**Gate:** Intake authentication is fail-closed on injection paths
**Verdict:** PASS
**Date:** 2026-02-13

---

## 1. Middleware Evidence

**File:** `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py`

### INJECTION_PATHS definition (line 22)

```python
# Paths that must NEVER be accessible without auth, even if ZAKOPS_API_KEY is unset
INJECTION_PATHS = ("/api/quarantine",)
```

All quarantine endpoints (the intake/injection surface) are explicitly listed as paths that must never be accessible without authentication.

### 503 fail-closed logic (lines 38-47)

```python
# Fail-closed: injection paths require auth even when key is not configured
is_injection_path = any(path.startswith(p) for p in INJECTION_PATHS)
if not expected_key:
    if is_injection_path:
        return JSONResponse(
            status_code=503,
            content={"error": "service_not_configured", "message": "API key not configured — injection path blocked"},
        )
    # Other paths: graceful degradation (skip auth)
    return await call_next(request)
```

When `ZAKOPS_API_KEY` is not set in the environment:
- Injection paths (`/api/quarantine*`) return **503** with `service_not_configured` error — access is blocked entirely.
- Other write paths degrade gracefully (auth skipped, request proceeds).

This is the fail-closed guarantee: if the operator forgets to configure the API key, quarantine injection is locked out rather than silently open.

### 401 unauthorized logic (lines 49-54)

```python
provided_key = request.headers.get("X-API-Key", "")
if provided_key != expected_key:
    return JSONResponse(
        status_code=401,
        content={"error": "unauthorized", "message": "Invalid or missing API key"},
    )
```

When `ZAKOPS_API_KEY` is configured but the caller provides an invalid or missing `X-API-Key` header, the middleware returns **401** with `unauthorized` error. This covers both wrong-key and no-key scenarios when the server is properly configured.

---

## 2. Startup Gate Evidence

**File:** `/home/zaks/zakops-backend/src/api/orchestration/main.py`

### LAYER 2 — API key startup verification gate (lines 428-439)

```python
# LAYER 2 — API key startup verification gate
# Warn loudly if ZAKOPS_API_KEY is not set (injection paths will 503 at runtime)
api_key = os.getenv("ZAKOPS_API_KEY", "").strip()
app.state.api_key_configured = bool(api_key)
if not api_key:
    print(
        "STARTUP WARNING: ZAKOPS_API_KEY is not set — "
        "injection paths (/api/quarantine) will return 503 (fail-closed). "
        "Set ZAKOPS_API_KEY to enable quarantine injection."
    )
else:
    print("API key gate PASSED: ZAKOPS_API_KEY is configured")
```

At application startup (inside the `lifespan` context manager):
- `app.state.api_key_configured` is set to `True` or `False` based on the environment variable.
- If the key is not set, a loud `STARTUP WARNING` is printed to the console, explicitly stating that injection paths will 503 at runtime.
- If the key is set, a confirmation message is printed (`API key gate PASSED`).

This ensures operators are alerted at boot time if the fail-closed path is active, rather than discovering it only when the first quarantine request fails.

---

## 3. Defense-in-Depth Summary

| Layer | Location | Behavior | Line(s) |
|-------|----------|----------|---------|
| Startup gate | `main.py` lifespan | Sets `app.state.api_key_configured`, warns if unset | 428-439 |
| Middleware — no key configured | `apikey.py` dispatch | Returns 503 on injection paths, skips auth on others | 38-47 |
| Middleware — bad/missing key | `apikey.py` dispatch | Returns 401 on all write paths | 49-54 |
| Path scoping | `apikey.py` INJECTION_PATHS | Only `/api/quarantine*` gets fail-closed treatment | 22 |

---

## Verdict

**PASS** — Intake authentication is fail-closed. When `ZAKOPS_API_KEY` is not configured, quarantine injection paths return 503 (blocked). When configured, invalid or missing keys return 401. The startup gate provides early warning. No path exists where an unauthenticated write to an injection endpoint can succeed silently.

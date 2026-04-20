# Matrix 3: Authentication Matrix

## Service Token Authentication

| Endpoint | No Token | Invalid Token | Valid Token | Status |
|----------|----------|---------------|-------------|--------|
| POST /agent/invoke | 401 | 401 | 200 | ✅ PASS |
| POST /agent/approvals/{id}:approve | 401 | 401 | 200 | ✅ PASS |
| POST /agent/approvals/{id}:reject | 401 | 401 | 200 | ✅ PASS |
| GET /agent/approvals | 401 | 401 | 200 | ✅ PASS |

## Actor Ownership (UF-003)

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| Approve own action (actor_id matches) | Allowed | 200 OK | ✅ PASS |
| Approve other's action (actor_id mismatch) | 403 Forbidden | 403 Insufficient permissions | ✅ PASS |

## Backend API Key (Agent→Backend)

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| No ZAKOPS_API_KEY | 401 Unauthorized | 401 (before fix) | ✅ FIXED |
| Valid ZAKOPS_API_KEY | Tool executes | 200 + deal transitions | ✅ PASS |

## Evidence
- Initial 403 error traced to actor_id mismatch
- ZAKOPS_API_KEY configured in .env files
- X-Service-Token: DASHBOARD_SERVICE_TOKEN

## Verdict: PASS (all auth paths verified)

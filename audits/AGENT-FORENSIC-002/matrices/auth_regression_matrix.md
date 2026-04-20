# Auth Regression Matrix — Phase 2 Embedded Security Tests (Updated)

| Endpoint | No Auth | Wrong Token | JWT on SvcToken EP | SvcToken on JWT EP | Both | Expected | Actual |
|----------|---------|------------|-------------------|-------------------|------|----------|--------|
| POST /agent/invoke | 401 | 401 | 401 | N/A | N/A | 401/401/401 | PASS (Phase2) |
| GET /agent/approvals | 401 | 401 | 401 | N/A | N/A | 401/401/401 | PASS (Phase2) |
| GET /api/v1/sessions | 404 | N/A | N/A | 404 | N/A | 401/401 | FAIL (endpoint mismatch; /api/v1/auth/sessions returns 401/200) |

Note: Phase3 race test used Authorization: Bearer $AGENT_JWT on /agent/approvals and succeeded once (see 3e_concurrent_race.txt), indicating inconsistent auth enforcement or token confusion.

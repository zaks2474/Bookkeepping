# Approval Lifecycle Matrix — AGENT-FORENSIC-002 V2 (Updated)

| Thread | Approval ID | tool_name | Status | Created (UTC) | Expires (UTC) | tool_execution | success | Backend API Stage | Backend SQL Stage | Idempotent | Restart-Survive |
|--------|------------|-----------|--------|---------------|---------------|---------------|---------|------------------|-------------------|------------|----------------|
| f002-hitl-001 | 18f3a017 | transition_deal | pending | 2026-02-03 02:06:45 | 2026-02-03 03:06:45 | NO | N/A | UNVERIFIED (auth blocked) | DL-0020=qualified | N/A | N/A |
| f002-err-002 | 0a8b039c | transition_deal | pending | 2026-02-03 02:08:31 | 2026-02-03 03:08:31 | NO | N/A | UNVERIFIED (auth blocked) | DL-0020=qualified | N/A | N/A |
| f002-path-c-001 | 4b466371 | transition_deal | approved | 2026-02-03 02:09:07 | 2026-02-03 03:09:07 | YES (1 row) | true (phantom) | UNVERIFIED (auth blocked) | DL-0020=qualified | UNVERIFIED | N/A |
| f002-path-e-001 | 8ee0aa7a | transition_deal | rejected | 2026-02-03 02:13:12 | 2026-02-03 03:13:12 | NO | N/A | UNVERIFIED (auth blocked) | DL-0020=qualified | N/A | N/A |
| f002-restart-001 | ea82a675 | transition_deal | approved | 2026-02-03 02:14:41 | 2026-02-03 03:14:41 | YES | true (phantom) | UNVERIFIED (auth blocked) | DL-0037=inbound | N/A | YES |
| f002-race-001 | 1d17d04c | transition_deal | approved | 2026-02-03 02:15:06 | 2026-02-03 03:15:06 | YES | true (phantom) | UNVERIFIED (auth blocked) | DL-0020=qualified | YES (1 success, 1 already claimed) | N/A |

Notes:
- Stage values from backend SQL (3c_reject_sql.txt, 3d_restart_resume.txt).
- API-stage verification was blocked by auth for /agent endpoints.

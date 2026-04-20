# Auth Boundary Matrix

Tested: 2026-02-02 against localhost:8095

## Agent Endpoints (JWT-protected)

| Endpoint | Method | No Auth | Invalid Bearer | Service Token (wrong type) | Expected |
|---|---|---|---|---|---|
| /api/v1/agent/invoke | POST | 401 | 401 | 401 | 401 |
| /api/v1/agent/approvals | GET | 401 | 401 | 401 | 401 |
| /api/v1/agent/approvals/fake-id | GET | 401 | 401 | 401 | 401 |
| /api/v1/agent/approvals/fake-id:approve | POST | 401 | 401 | 401 | 401 |
| /api/v1/agent/approvals/fake-id:reject | POST | 401 | 401 | 401 | 401 |
| /api/v1/agent/threads/fake-id/state | GET | 401 | 401 | 401 | 401 |
| /api/v1/agent/invoke/stream | POST | 401 | 401 | 401 | 401 |

All agent endpoints correctly reject unauthorized requests regardless of auth mode.

## Chatbot Endpoints (session/service-token protected)

| Endpoint | Method | No Auth | Invalid Bearer (wrong type) | Valid Service Token | Expected |
|---|---|---|---|---|---|
| /api/v1/chatbot/chat | POST | 401 | 401 | 422 | 401 / 422 |
| /api/v1/chatbot/chat/stream | POST | 401 | 401 | 422 | 401 / 422 |

- 422 with valid service token indicates auth passed but request body validation failed (expected — minimal test payload).

## Public Endpoints

| Endpoint | Method | No Auth | Expected |
|---|---|---|---|
| /health | GET | 200 | 200 |
| /docs | GET | 200 | 200 |
| /metrics | GET | 200 | 200 |

## Summary

- **All 7 agent endpoints**: Properly return 401 for no-auth, invalid bearer, and service-token (wrong auth type). PASS.
- **Both chatbot endpoints**: Properly return 401 for no-auth and invalid bearer; 422 with valid service token (auth passes, body validation fails). PASS.
- **Public endpoints**: All return 200 with no auth. PASS.
- **No auth bypass detected.**

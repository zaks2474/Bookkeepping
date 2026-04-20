# Endpoint Coverage Matrix
| # | Method | Path | Auth Used | Result (HTTP) | Evidence |
|---|---|---|---|---|---|
| 1 | GET | / | None | 200 | evidence/phase1/11_root_health.txt |
| 2 | GET | /health | None | 200 | evidence/phase1/11_root_health.txt |
| 3 | GET | /api/v1/health | None | 200 | evidence/phase1/15b_openapi_additional_endpoints.txt |
| 4 | POST | /api/v1/auth/register | None (JSON) | 200 (new) / 400 (duplicate) | evidence/phase1/19_multi_user_isolation.txt |
| 5 | POST | /api/v1/auth/login | None (form) | 200 (success) / 401 (bad creds) | evidence/phase1/12_auth_endpoints.txt |
| 6 | POST | /api/v1/auth/session | JWT | 200 | evidence/phase1/13_session_crud.txt |
| 7 | GET | /api/v1/auth/sessions | JWT | 200 | evidence/phase1/13_session_crud.txt |
| 8 | PATCH | /api/v1/auth/session/{session_id}/name | JWT + session token | 404 (not found) | evidence/phase1/13_session_crud.txt |
| 9 | DELETE | /api/v1/auth/session/{session_id} | Session token | 200 | evidence/cleanup/test_data_cleanup.txt |
|10 | POST | /api/v1/chatbot/chat | Session token | 200 | evidence/phase1/14_chat_v1.txt |
|11 | POST | /api/v1/chatbot/chat/stream | Session token | 200 (SSE error payload) | evidence/phase1/14_chat_v1.txt |
|12 | GET | /api/v1/chatbot/messages | Session token | 200 | evidence/phase1/14_chat_v1.txt |
|13 | DELETE | /api/v1/chatbot/messages | Session token | 200 | evidence/phase1/14_chat_v1.txt |
|14 | POST | /agent/invoke | X-Service-Token | 200 (also 200 w/o auth) | evidence/phase1/15_agent_mdv2.txt |
|15 | POST | /agent/invoke/stream | X-Service-Token | 200 | evidence/phase1/21_streaming_validation.txt |
|16 | GET | /agent/approvals | X-Service-Token | 200 | evidence/phase1/15_agent_mdv2.txt |
|17 | GET | /agent/approvals/{approval_id} | X-Service-Token | 404 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|18 | POST | /agent/approvals/{approval_id}:approve | X-Service-Token | 404 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|19 | POST | /agent/approvals/{approval_id}:reject | X-Service-Token | 404 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|20 | GET | /agent/threads/{thread_id}/state | X-Service-Token | 200 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|21 | POST | /api/v1/agent/invoke | None | 200 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|22 | POST | /api/v1/agent/invoke/stream | None | 200 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|23 | GET | /api/v1/agent/approvals | None | 200 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|24 | GET | /api/v1/agent/approvals/{approval_id} | None | 404 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|25 | POST | /api/v1/agent/approvals/{approval_id}:approve | JWT | 404 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|26 | POST | /api/v1/agent/approvals/{approval_id}:reject | JWT | 404 | evidence/phase1/15b_openapi_additional_endpoints.txt |
|27 | GET | /api/v1/agent/threads/{thread_id}/state | None | 200 | evidence/phase1/15b_openapi_additional_endpoints.txt |

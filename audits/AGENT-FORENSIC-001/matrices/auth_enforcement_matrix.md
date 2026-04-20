# Auth Enforcement Matrix
| Endpoint | Expected Auth | No Auth (HTTP) | Bad Auth (HTTP) | Correct Auth (HTTP) | Evidence |
|---|---|---|---|---|---|
| /agent/invoke | X-Service-Token | 200 | 200 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/15_agent_mdv2.txt |
| /agent/approvals (GET) | X-Service-Token | 200 | 200 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/15_agent_mdv2.txt |
| /agent/threads/{thread_id}/state (GET) | X-Service-Token | 200 | 200 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/15b_openapi_additional_endpoints.txt |
| /api/v1/auth/session (POST) | JWT | 401 | 422 | 200 | evidence/phase1/16_auth_enforcement.txt |
| /api/v1/auth/sessions (GET) | JWT | 401 | 422 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/13_session_crud.txt |
| /api/v1/chatbot/chat (POST) | Session token | 401 | 401 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/14_chat_v1.txt |
| /api/v1/chatbot/chat/stream (POST) | Session token | 401 | 401 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/14_chat_v1.txt |
| /api/v1/chatbot/messages (GET) | Session token | 401 | 422 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/14_chat_v1.txt |
| /api/v1/chatbot/messages (DELETE) | Session token | 401 | 422 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/14_chat_v1.txt |
| /api/v1/agent/invoke (POST) | (Should be protected) | 200 | 200 | 200 | evidence/phase1/16_auth_enforcement.txt; evidence/phase1/15b_openapi_additional_endpoints.txt |

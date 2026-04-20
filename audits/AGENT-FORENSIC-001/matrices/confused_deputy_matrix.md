# Confused Deputy Matrix
| Scenario | Endpoint | Expected | Result (HTTP) | Evidence |
|---|---|---|---|---|
| Service token on JWT-only endpoint | /api/v1/auth/sessions | 401/403 | 401 | evidence/phase1/17_confused_deputy.txt |
| JWT on service-token endpoint | /agent/invoke | 401/403 | 200 | evidence/phase1/17_confused_deputy.txt |
| Both headers present | /agent/invoke | Enforce service token only | 200 | evidence/phase1/17_confused_deputy.txt |

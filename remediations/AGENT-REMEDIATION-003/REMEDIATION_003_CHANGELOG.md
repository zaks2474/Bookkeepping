# REMEDIATION-003 Changelog
| Timestamp | File | Change | Before | After |
|-----------|------|--------|--------|-------|
| 2026-02-03T16:50 | graph.py:632-636 | Fix LangGraph resume API | `ainvoke(input=None, interrupt_resume={...})` | `ainvoke(Command(resume={...}))` |
| 2026-02-03T16:50 | graph.py:693-698 | Fix rejection resume API | `ainvoke(input=None, interrupt_resume={...})` | `ainvoke(Command(resume={...}))` |
| 2026-02-03T16:51 | graph.py:638-658 | Extract tool result | Only returned `{"response": text}` | Returns `{"response", "tool_executed", "tool_result"}` |
| 2026-02-03T16:52 | agent.py:396-454 | Use actual tool result | Hardcoded `{"ok": True}` | Uses actual `tool_result` from execution |
| 2026-02-03T16:52 | agent.py:407 | Verify success before marking | Always `execution.success = True` | `execution.success = actual_success` based on tool_executed |
| 2026-02-03T16:55 | deal_tools.py:29-39 | Add backend auth helper | No auth headers | `_get_backend_headers()` with X-API-Key |
| 2026-02-03T16:55 | deal_tools.py:123,156,192,294 | Use auth headers in HTTP calls | `client.get/post(url)` | `client.get/post(url, headers=headers)` |
| 2026-02-03T16:57 | .env.development | Add ZAKOPS_API_KEY | Not present | `ZAKOPS_API_KEY=<key>` |
| 2026-02-03T16:57 | .env | Add ZAKOPS_API_KEY for compose | Not present | `ZAKOPS_API_KEY=<key>` |
| 2026-02-03T16:57 | docker-compose.yml | Pass ZAKOPS_API_KEY to container | Not present | `ZAKOPS_API_KEY=${ZAKOPS_API_KEY:-}` |
| 2026-02-03T17:01 | idempotency.py:37-47 | Fix idempotency key length | `{thread}:{tool}:{hash}` (>64 chars) | Hash only (64 chars) |
| 2026-02-03T17:08 | workflow.py:121-136 | Fix column name in SELECT | `SELECT details` | `SELECT payload` |
| 2026-02-03T17:08 | workflow.py:260-272 | Fix column name in SELECT | `SELECT details` | `SELECT payload` |
| 2026-02-03T17:08 | workflow.py:215-225 | Add idempotency_key to INSERT | Missing column | Added `idempotency_key` to INSERT |

# Tool Wiring Summary Matrix (Updated)

| Tool | HITL | Triggered | Real Data | Cross-Ref | Canary | Injection Blocked | Verdict |
|------|------|-----------|-----------|-----------|--------|------------------|---------|
| get_deal | No | NO (auth blocked) | NO | NO | NO | N/A | FAIL/UNVERIFIED |
| transition_deal | YES | YES (approvals + executions exist) | N/A | FAIL (stage unchanged) | FAIL (auth blocked / no match) | UNVERIFIED (auth blocked) | FAIL (P0 phantom success) |
| search_deals | No | NO (auth blocked) | NO (RAG DB down) | N/A | N/A | N/A | GRACEFUL-FAIL |
| duckduckgo_search | No | NO (auth blocked) | NO | N/A | N/A | N/A | FAIL/UNVERIFIED |

Note: Auth failures on /agent/invoke prevented end-to-end tool triggering for non-HITL tools.

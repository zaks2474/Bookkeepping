# CODEX Chat + Actions Verification Baseline

- Generated: `2026-01-08T04:55:23Z`
- Host: `Zako`

## Ports
```
3:LISTEN 0      2048          0.0.0.0:8090       0.0.0.0:*    users:(("python3",pid=2583788,fd=6))         
4:LISTEN 0      4096          0.0.0.0:8080       0.0.0.0:*    users:(("docker-proxy",pid=1506303,fd=7))    
7:LISTEN 0      4096          0.0.0.0:8000       0.0.0.0:*    users:(("docker-proxy",pid=1501216,fd=7))    
21:LISTEN 0      4096             [::]:8080          [::]:*    users:(("docker-proxy",pid=1506310,fd=7))    
24:LISTEN 0      4096             [::]:8000          [::]:*    users:(("docker-proxy",pid=1501222,fd=7))    
32:LISTEN 0      511                 *:3003             *:*    users:(("next-server (v1",pid=2851041,fd=19))
```

## Versions
- `8090 /api/version`: commit `da593b15b7f8` pid `2583788` allow_cloud_default `false`
- `3003 /api/version` (proxy): commit `da593b15b7f8` pid `2583788`

## LLM Health (shape)
- status: `healthy` primary: `vllm`
  - vllm: `healthy` model `Qwen/Qwen2.5-32B-Instruct-AWQ` latency_ms `43`
  - gemini-flash: `healthy` model `gemini-2.5-flash` latency_ms `564`
  - gemini-pro: `healthy` model `gemini-2.5-pro` latency_ms `2368`

## Chat Contract Snapshots (sanitized)
- `POST /api/chat/complete` hello: {"keys": ["citations", "content", "evidence_summary", "latency_ms", "model_used", "proposals", "warnings"], "content_len": 98, "proposals_count": 0, "proposal_types": [], "citations_count": 2, "model_used": "Qwen/Qwen2.5-32B-Instruct-AWQ", "latency_ms": 1222, "warnings_count": 0}
- `POST /api/chat/complete` draft_email: {"keys": ["citations", "content", "evidence_summary", "latency_ms", "model_used", "proposals", "warnings"], "content_len": 846, "proposals_count": 1, "proposal_types": ["draft_email"], "citations_count": 1, "model_used": "Qwen/Qwen2.5-32B-Instruct-AWQ", "latency_ms": 6628, "warnings_count": 0}
- `POST /api/chat/execute-proposal` invalid id: {"status": 404, "keys": ["error", "reason", "session_id", "success"], "success": false, "reason": "session_not_found", "error": "Session not found"}

## Actions Engine
- capabilities count: `22`
- missing executors: `1`
- capability mismatches: `1`

## Systemd Units
- `kinetic-actions-runner.service` active=`active` enabled=`enabled`
- `zakops-email-triage.timer` active=`active` enabled=`enabled`
- `zakops-deal-lifecycle-controller.timer` active=`active` enabled=`enabled`

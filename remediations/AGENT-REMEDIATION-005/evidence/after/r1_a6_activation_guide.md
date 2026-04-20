# Langfuse Activation Guide

## To Enable Tracing

1. Open `/home/zaks/zakops-agent-api/apps/agent-api/.env`
2. Uncomment and fill these three variables:
   ```
   LANGFUSE_PUBLIC_KEY=pk-lf-your-key-here
   LANGFUSE_SECRET_KEY=sk-lf-your-key-here
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```
3. Restart the agent API:
   ```bash
   cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose restart agent-api
   ```
4. Verify in Langfuse dashboard that traces appear for agent invocations.

## To Disable Tracing

1. Comment out or remove the three LANGFUSE_* variables from `.env`
2. Restart the agent API
3. No errors — tracing silently deactivates

## Instrumentation Points

The following agent lifecycle events are traced (when Langfuse is configured):
- LangGraph agent invocations
- LLM calls (via langchain callbacks)
- Tool executions (with approval correlation)
- Approval decisions
- Backend API calls

## How It Works

The tracing module (`app/core/tracing.py`) uses lazy initialization:
- On first call to `get_langfuse()` or `get_callbacks()`, it checks for env vars
- If all three vars are set and non-empty, Langfuse client is initialized
- If any var is missing, a no-op path is taken (no crashes, no errors)
- The `trace_span()` context manager is always safe to use

## Evidence

Created as part of AGENT-REMEDIATION-005 (F-001 fix).
RT-TRACE-SINK test verifies wiring works without external connection.

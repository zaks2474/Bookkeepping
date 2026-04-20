# LangSmith Safe Tracing (No-Secrets Policy)

This lab can use LangSmith for tracing/evals, but **only in a safe mode** that avoids exfiltrating sensitive content.

## Non-negotiables
- Never trace raw secrets (tokens, cookies, keys, `.env`).
- Never trace raw deal artifacts by default (email bodies, attachments, CIMs, PDFs).
- Prefer tracing **metadata only** (counts, hashes, run IDs, component names).

## What's implemented
- `/home/zaks/Zaks-llm/src/core/tracing.py` enforces **safe defaults** when tracing is enabled:
  - Sets `LANGCHAIN_HIDE_INPUTS=true` and `LANGCHAIN_HIDE_OUTPUTS=true` unless explicitly overridden.
  - Adds safe tags/metadata (component, user_id, correlation IDs).
- `/home/zaks/Zaks-llm/src/agents/systemops.py` uses the tracing helpers for `system_ops` runs.

## Enable tracing (safe mode)

### Option 1: Shell script (for local runs)
```bash
# First, set your API key (do NOT commit this)
export LANGCHAIN_API_KEY=your-key-here

# Then source the activation script
source /home/zaks/scripts/enable_langsmith_tracing.sh
```

### Option 2: Docker Compose overlay (for containerized services)
```bash
# Set API key in environment
export LANGCHAIN_API_KEY=your-key-here

# Deploy with LangSmith tracing enabled
cd /home/zaks/Zaks-llm
docker compose -f docker-compose.yml \
  -f docker-compose.orchestrator.yml \
  -f docker-compose.dfp.yml \
  -f docker-compose.langsmith.yml \
  up -d --force-recreate --no-deps zakops-api
```

### Option 3: Manual environment variables
Do **not** put secrets in git or docs. Set env vars in a secure location (shell profile, systemd env file, etc.).

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
export LANGCHAIN_API_KEY=${LANGSMITH_API_KEY}
export LANGCHAIN_PROJECT=zakops-production

# Safety defaults (recommended)
export LANGCHAIN_HIDE_INPUTS=true
export LANGCHAIN_HIDE_OUTPUTS=true

# Keep unredacted content disabled (recommended)
export ZAKOPS_LANGSMITH_ALLOW_UNREDACTED=0
```

## Correlation IDs (recommended)
To connect traces ↔ run ledger ↔ logs, set:
```bash
export ZAKOPS_CORRELATION_ID="2025-12-25T120000Z_change123"
export ZAKOPS_PARENT_RUN_ID="20251225T120000Z_sharepoint_sync_12345"
```

These values are safe to store in traces and are also supported by run-ledger emitters.

## Disable tracing
```bash
# Shell
unset LANGCHAIN_TRACING_V2

# Docker - just omit the langsmith.yml overlay
docker compose -f docker-compose.yml up -d zakops-api
```

## View traces
Open https://smith.langchain.com and select project `zakops-production`.

## Operational note
LangSmith is a cloud service. Enable tracing only when you explicitly want outbound telemetry and you are confident your redaction rules are correct.


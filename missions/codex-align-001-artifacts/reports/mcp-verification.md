# MCP Verification — CODEX-ALIGN-001
## Date: 2026-02-12

## Registration Status

| Server | Command | Status |
|--------|---------|--------|
| github | `npx -y @modelcontextprotocol/server-github` | enabled |
| playwright | `/root/.npm-global/bin/playwright-mcp --headless --no-sandbox` | enabled |
| gmail | `npx -y @gongrzhe/server-gmail-autoauth-mcp` | enabled |
| crawl4ai-rag | `docker exec -i docs-rag-mcp python -m src.mcp_server` | enabled |

## Secret Scan
- `grep -ri 'token|secret|password|api.key|credential' ~/.codex/config.toml` — **CLEAN** (exit 1, no matches)

## Behavioral Verification
Behavioral verification (per-server tool calls) deferred to Phase 8 runtime checks.
MCP servers require active Codex sessions to invoke tools — cannot be tested from Claude CLI.

## Prerequisites Documented
- **GitHub:** Requires `gh auth login` or `GITHUB_TOKEN` env var
- **Gmail:** OAuth2 auto-auth — first run prompts browser consent
- **crawl4ai-rag:** Requires `docs-rag-mcp` Docker container running
- **Playwright:** Requires chromium browser installed

## Gate P4: PASS (registration complete, behavioral deferred)

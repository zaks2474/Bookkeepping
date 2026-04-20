# Verification Checklist — CODEX-ALIGN-001
## Date: 2026-02-12

## Structural (file existence)
- [ ] `~/.codex/AGENTS.md` exists and < 15KB
- [ ] `/home/zaks/zakops-agent-api/.agents/AGENTS.md` exists
- [ ] `/home/zaks/zakops-backend/.agents/AGENTS.md` exists
- [ ] `~/.codex/config.toml` has notify, 5 profiles, 3 project trust entries
- [ ] 19 user skills exist
- [ ] 7 project skills exist
- [ ] `~/.codex/rules/default.rules` has structured rules
- [ ] 4 MCP servers registered
- [ ] 4 wrapper scripts exist and are executable
- [ ] `codex` resolves in PATH

## Content (correctness)
- [ ] AGENTS.md mentions port 8090 decommissioned
- [ ] AGENTS.md has service map with all active services
- [ ] AGENTS.md has 14 contract surfaces
- [ ] AGENTS.md has 10 constraint registry entries
- [ ] AGENTS.md has WSL hazards (CRLF, root ownership)
- [ ] AGENTS.md has Deal Integrity patterns
- [ ] config.toml has no typos in project paths
- [ ] Rules file covers make, docker, git, curl, test categories

## Functional (behavior)
- [ ] `codex-boot.sh` runs and reports ALL CLEAR
- [ ] `codex --version` returns 0.98.0
- [ ] `codex mcp list` shows 4 servers
- [ ] `codex-stop.sh` runs without errors
- [ ] All file ownership correct (zaks:zaks for /home/zaks/ files)
- [ ] All .sh files have LF line endings (no CRLF)

## AGENTS.md load proof (runtime)
- [ ] Monorepo AGENTS load test
- [ ] Backend AGENTS load test
- [ ] Fallback path tested if needed

## MCP behavioral verification
- [ ] GitHub MCP tool call
- [ ] Playwright MCP tool call
- [ ] Gmail MCP tool call
- [ ] crawl4ai-rag MCP tool call
- [ ] Secret scan clean

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any, Dict, List

from email_triage_agent.gmail_mcp import GmailMcpClient, gmail_mcp_command, gmail_mcp_env
from email_triage_agent.mcp_stdio import McpStdioSession


async def _list_tools(session: McpStdioSession) -> List[str]:
    try:
        resp = await session.request(method="tools/list", params={})
    except Exception:
        return []
    tools = resp.get("tools")
    if not isinstance(tools, list):
        return []
    names: List[str] = []
    for t in tools:
        if isinstance(t, dict) and isinstance(t.get("name"), str) and t["name"].strip():
            names.append(t["name"].strip())
    return names


async def _run(args: argparse.Namespace) -> int:
    cmd = gmail_mcp_command()
    async with McpStdioSession(command=cmd, env=gmail_mcp_env()) as session:
        if args.list_tools:
            tools = await _list_tools(session)
            print(json.dumps({"mcp_command": cmd, "tool_count": len(tools), "tools": tools}, indent=2))
            return 0

        gmail = GmailMcpClient(session)
        hits = await gmail.search_emails(query=args.query, max_results=int(args.max_results))
        # Intentionally avoid printing subjects/senders to keep output low-sensitivity.
        out: Dict[str, Any] = {
            "mcp_command": cmd,
            "query": args.query,
            "hit_count": len(hits),
            "message_ids": [h.message_id for h in hits],
        }
        print(json.dumps(out, indent=2))
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Gmail MCP via stdio (outside Claude Code).")
    parser.add_argument("--list-tools", action="store_true", help="List tools exposed by the MCP server")
    parser.add_argument("--query", default="in:inbox newer_than:1d", help="Gmail search query (read-only)")
    parser.add_argument("--max-results", type=int, default=1, help="Max results to return")
    ns = parser.parse_args()
    return asyncio.run(_run(ns))


if __name__ == "__main__":
    raise SystemExit(main())

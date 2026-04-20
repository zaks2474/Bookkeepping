from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional


class ToolAliasError(RuntimeError):
    pass


CallToolFn = Callable[[str, Dict[str, Any]], Dict[str, Any]]


@dataclass(frozen=True)
class GmailLabel:
    id: str
    name: str


def _first_str(args: Dict[str, Any], keys: Iterable[str]) -> Optional[str]:
    for k in keys:
        v = args.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _first_int(args: Dict[str, Any], keys: Iterable[str]) -> Optional[int]:
    for k in keys:
        v = args.get(k)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.strip().isdigit():
            return int(v.strip())
    return None


def _as_str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        v = value.strip()
        return [v] if v else []
    if isinstance(value, list):
        out: List[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
        return out
    return []


def _extract_text(result: Dict[str, Any]) -> str:
    """
    Gmail MCP server returns: {"content":[{"type":"text","text":"..."}]}
    This helper pulls the first text blob.
    """
    content = result.get("content")
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            text = first.get("text")
            if isinstance(text, str):
                return text
    return ""


_LABEL_ID_RE = re.compile(r"\bID:\s*([A-Za-z0-9_-]+)\b")


def parse_label_id_from_result(result: Dict[str, Any]) -> Optional[str]:
    text = _extract_text(result)
    m = _LABEL_ID_RE.search(text)
    return m.group(1) if m else None


class AgentBuilderToolAliasAdapter:
    """
    Adapter that lets the runtime keep Agent Builder tool names, but execute against
    local Gmail MCP tool names.

    This is intentionally conservative:
    - Blocks send/delete
    - Provides best-effort argument normalization
    """

    BLOCKED_TOOLS = {
        "gmail_send_email",
        "send_email",
        "gmail_delete_email",
        "delete_email",
        "batch_delete_emails",
        "gmail_batch_delete_emails",
    }

    def __init__(self, call_tool: CallToolFn):
        self._call_tool = call_tool

    def call(self, *, tool_name: str, args: Dict[str, Any] | None = None) -> Dict[str, Any]:
        args = args or {}
        if tool_name in self.BLOCKED_TOOLS:
            raise ToolAliasError(f"Blocked tool: {tool_name}")

        if tool_name == "gmail_read_emails":
            query = _first_str(args, ["query", "q"])
            if not query:
                raise ToolAliasError("gmail_read_emails requires query")
            max_results = _first_int(args, ["max_results", "maxResults"]) or 10
            return self._call_tool("search_emails", {"query": query, "maxResults": max_results})

        if tool_name == "gmail_get_thread":
            raise ToolAliasError("gmail_get_thread not supported by local Gmail MCP (no get_thread tool)")

        if tool_name == "gmail_list_labels":
            return self._call_tool("list_email_labels", {})

        if tool_name == "gmail_create_label":
            name = _first_str(args, ["name", "label", "label_name", "labelName"])
            if not name:
                raise ToolAliasError("gmail_create_label requires name")
            # Prefer idempotent creation.
            return self._call_tool("get_or_create_label", {"name": name})

        if tool_name == "gmail_apply_label":
            message_id = _first_str(args, ["messageId", "message_id", "id"])
            label_name = _first_str(args, ["name", "label", "label_name", "labelName"])
            if not message_id or not label_name:
                raise ToolAliasError("gmail_apply_label requires messageId/message_id and label name")
            label_result = self._call_tool("get_or_create_label", {"name": label_name})
            label_id = parse_label_id_from_result(label_result)
            if not label_id:
                raise ToolAliasError("Could not parse label id from get_or_create_label result")
            return self._call_tool("modify_email", {"messageId": message_id, "addLabelIds": [label_id]})

        if tool_name == "gmail_mark_as_read":
            message_id = _first_str(args, ["messageId", "message_id", "id"])
            if not message_id:
                raise ToolAliasError("gmail_mark_as_read requires messageId/message_id")
            return self._call_tool("modify_email", {"messageId": message_id, "removeLabelIds": ["UNREAD"]})

        if tool_name == "gmail_draft_email":
            to = _as_str_list(args.get("to") or args.get("recipients"))
            subject = _first_str(args, ["subject"]) or ""
            body = _first_str(args, ["body", "text"]) or ""
            thread_id = _first_str(args, ["threadId", "thread_id"])
            if not to or not subject or not body:
                raise ToolAliasError("gmail_draft_email requires to[], subject, body")
            payload: Dict[str, Any] = {"to": to, "subject": subject, "body": body}
            if thread_id:
                payload["threadId"] = thread_id
            return self._call_tool("draft_email", payload)

        raise ToolAliasError(f"Unknown Agent Builder tool: {tool_name}")

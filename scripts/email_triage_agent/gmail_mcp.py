from __future__ import annotations

import os
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from email_triage_agent.mcp_stdio import McpStdioSession


@dataclass(frozen=True)
class EmailSearchHit:
    message_id: str
    subject: str
    sender: str
    date: str


@dataclass(frozen=True)
class EmailAttachment:
    attachment_id: str
    filename: str
    mime_type: str
    size_bytes: int

    @property
    def ext_lower(self) -> str:
        return Path(self.filename).suffix.lower().lstrip(".")


@dataclass(frozen=True)
class EmailMessage:
    message_id: str
    thread_id: str
    subject: str
    sender: str
    to: str
    date: str
    body: str
    attachments: List[EmailAttachment]


_ID_LINE_RE = re.compile(r"^ID:\s*(?P<id>.+?)\s*$")
_SUBJECT_LINE_RE = re.compile(r"^Subject:\s*(?P<subject>.*)$")
_FROM_LINE_RE = re.compile(r"^From:\s*(?P<from>.*)$")
_DATE_LINE_RE = re.compile(r"^Date:\s*(?P<date>.*)$")

_THREAD_ID_RE = re.compile(r"^Thread ID:\s*(?P<tid>.*)$")
_TO_RE = re.compile(r"^To:\s*(?P<to>.*)$")

_ATTACHMENT_HEADER_RE = re.compile(r"^Attachments\s*\((?P<count>\d+)\):\s*$")
_ATTACHMENT_LINE_RE = re.compile(
    r"^-\s+(?P<filename>.+?)\s+\((?P<mime>[^,]+),\s*(?P<size_kb>\d+)\s*KB,\s*ID:\s*(?P<id>[^)]+)\)\s*$"
)

_LABEL_ID_RE = re.compile(r"\bID:\s*([A-Za-z0-9_-]+)\b")


def _extract_first_text(result: Dict[str, Any]) -> str:
    content = result.get("content")
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            text = first.get("text")
            if isinstance(text, str):
                return text
    return ""


def parse_search_emails_text(text: str) -> List[EmailSearchHit]:
    hits: List[EmailSearchHit] = []
    current: Dict[str, str] = {}
    for raw in (text or "").splitlines():
        line = raw.strip("\r")
        if not line.strip():
            continue
        m = _ID_LINE_RE.match(line)
        if m:
            if current.get("id"):
                hits.append(
                    EmailSearchHit(
                        message_id=current.get("id", ""),
                        subject=current.get("subject", ""),
                        sender=current.get("from", ""),
                        date=current.get("date", ""),
                    )
                )
            current = {"id": m.group("id").strip()}
            continue
        m = _SUBJECT_LINE_RE.match(line)
        if m:
            current["subject"] = m.group("subject").strip()
            continue
        m = _FROM_LINE_RE.match(line)
        if m:
            current["from"] = m.group("from").strip()
            continue
        m = _DATE_LINE_RE.match(line)
        if m:
            current["date"] = m.group("date").strip()
            continue

    if current.get("id"):
        hits.append(
            EmailSearchHit(
                message_id=current.get("id", ""),
                subject=current.get("subject", ""),
                sender=current.get("from", ""),
                date=current.get("date", ""),
            )
        )
    return hits


def parse_read_email_text(message_id: str, text: str) -> EmailMessage:
    thread_id = ""
    subject = ""
    sender = ""
    to = ""
    date = ""

    lines = (text or "").splitlines()
    i = 0
    # header block
    while i < len(lines):
        line = lines[i].rstrip("\r")
        if not line.strip():
            i += 1
            break
        m = _THREAD_ID_RE.match(line)
        if m:
            thread_id = m.group("tid").strip()
        m = _SUBJECT_LINE_RE.match(line)
        if m:
            subject = m.group("subject").strip()
        m = _FROM_LINE_RE.match(line)
        if m:
            sender = m.group("from").strip()
        m = _TO_RE.match(line)
        if m:
            to = m.group("to").strip()
        m = _DATE_LINE_RE.match(line)
        if m:
            date = m.group("date").strip()
        i += 1

    # body + attachments
    body_lines: List[str] = []
    attachments: List[EmailAttachment] = []
    in_attachments = False
    while i < len(lines):
        line = lines[i].rstrip("\r")
        if _ATTACHMENT_HEADER_RE.match(line.strip()):
            in_attachments = True
            i += 1
            continue
        if in_attachments:
            m = _ATTACHMENT_LINE_RE.match(line.strip())
            if m:
                filename = m.group("filename").strip()
                mime = m.group("mime").strip()
                size_kb = int(m.group("size_kb"))
                aid = m.group("id").strip()
                attachments.append(
                    EmailAttachment(
                        attachment_id=aid,
                        filename=filename,
                        mime_type=mime,
                        size_bytes=size_kb * 1024,
                    )
                )
        else:
            body_lines.append(line)
        i += 1

    body = "\n".join(body_lines).strip()
    return EmailMessage(
        message_id=message_id,
        thread_id=thread_id,
        subject=subject,
        sender=sender,
        to=to,
        date=date,
        body=body,
        attachments=attachments,
    )


def parse_label_id(text: str) -> Optional[str]:
    m = _LABEL_ID_RE.search(text or "")
    return m.group(1) if m else None


class GmailMcpClient:
    def __init__(self, session: McpStdioSession):
        self.session = session
        self._label_cache: Dict[str, str] = {}

    async def search_emails(self, *, query: str, max_results: int = 10) -> List[EmailSearchHit]:
        result = await self.session.call(name="search_emails", arguments={"query": query, "maxResults": int(max_results)})
        text = _extract_first_text(result)
        return parse_search_emails_text(text)

    async def read_email(self, *, message_id: str) -> EmailMessage:
        result = await self.session.call(name="read_email", arguments={"messageId": message_id})
        text = _extract_first_text(result)
        return parse_read_email_text(message_id, text)

    async def get_or_create_label_id(self, *, name: str) -> str:
        name = (name or "").strip()
        if not name:
            raise ValueError("label name required")
        if name in self._label_cache:
            return self._label_cache[name]
        result = await self.session.call(name="get_or_create_label", arguments={"name": name})
        text = _extract_first_text(result)
        label_id = parse_label_id(text)
        if not label_id:
            raise RuntimeError("could_not_parse_label_id")
        self._label_cache[name] = label_id
        return label_id

    async def add_labels(self, *, message_id: str, label_ids: List[str]) -> None:
        label_ids = [l for l in (label_ids or []) if isinstance(l, str) and l.strip()]
        if not label_ids:
            return
        await self.session.call(name="modify_email", arguments={"messageId": message_id, "addLabelIds": label_ids})

    async def remove_labels(self, *, message_id: str, label_ids: List[str]) -> None:
        label_ids = [l for l in (label_ids or []) if isinstance(l, str) and l.strip()]
        if not label_ids:
            return
        await self.session.call(name="modify_email", arguments={"messageId": message_id, "removeLabelIds": label_ids})

    async def mark_as_read(self, *, message_id: str) -> None:
        await self.remove_labels(message_id=message_id, label_ids=["UNREAD"])

    async def download_attachment(self, *, message_id: str, attachment_id: str, save_dir: str, filename: Optional[str] = None) -> str:
        args: Dict[str, Any] = {"messageId": message_id, "attachmentId": attachment_id, "savePath": save_dir}
        if filename:
            args["filename"] = filename
        result = await self.session.call(name="download_attachment", arguments=args)
        return _extract_first_text(result)

    async def draft_email(self, *, to: List[str], subject: str, body: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        args: Dict[str, Any] = {"to": to, "subject": subject, "body": body}
        if thread_id:
            args["threadId"] = thread_id
        result = await self.session.call(name="draft_email", arguments=args)
        return result


def gmail_mcp_command() -> list[str]:
    """
    Command used to launch the local Gmail MCP server in stdio mode.
    Override with env var: GMAIL_MCP_COMMAND (space-separated).
    """
    raw = (os.getenv("GMAIL_MCP_COMMAND") or "").strip()
    if raw:
        # Use shlex to support quoted paths and flags.
        return shlex.split(raw)

    # Fallback: run the published package via npx (works under an unprivileged user).
    return ["npx", "-y", "@gongrzhe/server-gmail-autoauth-mcp"]


def gmail_mcp_env() -> Dict[str, str]:
    """
    Standard env wiring for the Gmail MCP server.

    This keeps triage aligned with ToolGateway/executors, which rely on `GMAIL_MCP_CREDENTIALS_PATH`.
    """
    creds = (os.getenv("GMAIL_MCP_CREDENTIALS_PATH") or "").strip()
    if not creds:
        try:
            creds = str((Path.home() / ".gmail-mcp" / "credentials.json").resolve())
        except Exception:
            creds = str(Path("/home/zaks/.gmail-mcp/credentials.json"))
    # Upstream server uses GMAIL_CREDENTIALS_PATH; keep legacy/internal name too.
    return {"GMAIL_CREDENTIALS_PATH": creds, "GMAIL_MCP_CREDENTIALS_PATH": creds}

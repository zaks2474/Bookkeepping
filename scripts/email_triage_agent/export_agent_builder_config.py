#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


DEEPAGENTS_DEFAULT_BASE_URL = "https://prod-deepagents-agent-build-d4c1479ed8ce53fbb8c3eefc91f0aa7d.us.langgraph.app"


@dataclass(frozen=True)
class ExportConfig:
    base_url: str
    tenant_id: str
    assistant_id: str
    thread_id: str
    output_dir: Path
    history_json: Path | None
    include_tools_dir: bool
    auth_scheme: str


class SecretDetector:
    _patterns: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"\blsv2_pt_[A-Za-z0-9]{16,}_[A-Za-z0-9]{8,}\b"), "langsmith_api_key"),
        (re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"), "openai_key"),
        (re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"), "github_token"),
        (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"), "slack_token"),
        (re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "aws_access_key_id"),
        (re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"), "google_api_key"),
        (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private_key_block"),
        (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}={0,2}\b"), "bearer_token"),
    ]

    @classmethod
    def detect(cls, *, text: str) -> list[str]:
        detections: list[str] = []
        for pattern, name in cls._patterns:
            if pattern.search(text or ""):
                detections.append(name)
        return detections


def _load_langsmith_api_key() -> str:
    env_key = (os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY") or "").strip()
    if env_key:
        return env_key
    fallback = Path("/home/zaks/.langsmith_api")
    if fallback.exists():
        return fallback.read_text(encoding="utf-8").strip()
    raise RuntimeError("Missing LangSmith API key (set LANGSMITH_API_KEY or LANGCHAIN_API_KEY)")


def _fetch_thread_history(cfg: ExportConfig) -> list[dict[str, Any]]:
    url = f"{cfg.base_url.rstrip('/')}/threads/{cfg.thread_id}/history"
    api_key = _load_langsmith_api_key()

    headers = {
        "x-api-key": api_key,
        "X-Tenant-Id": cfg.tenant_id,
        "X-Organization-Id": cfg.tenant_id,
        "x-auth-scheme": cfg.auth_scheme,
    }

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    if not isinstance(data, list):
        raise RuntimeError("Unexpected history payload shape (expected list)")
    return data


def _extract_messages_from_history(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not history:
        raise RuntimeError("Thread history is empty")
    latest = history[-1]
    values = latest.get("values") or {}
    messages = values.get("messages") or []
    if not isinstance(messages, list):
        raise RuntimeError("Unexpected messages payload shape (expected list)")
    out: list[dict[str, Any]] = []
    for m in messages:
        if isinstance(m, dict):
            out.append(m)
    return out


def _tool_call_id_to_file_path(messages: list[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in messages:
        if m.get("type") != "ai":
            continue
        for tc in (m.get("tool_calls") or []):
            if not isinstance(tc, dict):
                continue
            tc_id = tc.get("id")
            args = tc.get("args") or {}
            fp = args.get("file_path")
            if isinstance(tc_id, str) and isinstance(fp, str):
                out[tc_id] = fp
    return out


def _read_file_outputs(messages: list[dict[str, Any]]) -> dict[str, str]:
    """
    Returns the last observed read_file output for each file_path.
    """
    tc_to_fp = _tool_call_id_to_file_path(messages)
    out: dict[str, str] = {}
    for m in messages:
        if m.get("type") != "tool" or m.get("name") != "read_file":
            continue
        tc_id = m.get("tool_call_id")
        fp = tc_to_fp.get(tc_id) if isinstance(tc_id, str) else None
        if not fp:
            continue
        content = m.get("content")
        if isinstance(content, str):
            out[fp] = content
        else:
            out[fp] = json.dumps(content, ensure_ascii=False, indent=2)
    return out


def _iter_tool_calls(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for m in messages:
        if m.get("type") != "ai":
            continue
        for tc in (m.get("tool_calls") or []):
            if isinstance(tc, dict):
                calls.append(tc)
    return calls


def _reconstruct_files(messages: list[dict[str, Any]]) -> dict[str, str]:
    """
    Reconstruct final file content for any file written in the thread using:
    - write_file(file_path, content)
    - edit_file(file_path, old_string, new_string)
    """
    files: dict[str, str] = {}
    tool_calls = _iter_tool_calls(messages)
    for tc in tool_calls:
        name = tc.get("name")
        args = tc.get("args") or {}
        fp = args.get("file_path")
        if not isinstance(fp, str):
            continue

        if name == "write_file":
            content = args.get("content")
            if isinstance(content, str):
                files[fp] = content
            else:
                files[fp] = json.dumps(content, ensure_ascii=False, indent=2)
            continue

        if name == "edit_file":
            old = args.get("old_string")
            new = args.get("new_string")
            if not isinstance(old, str) or not isinstance(new, str):
                continue
            if fp not in files:
                raise RuntimeError(f"edit_file before write_file for {fp}")
            # Mirror typical edit_file behavior: replace all occurrences of old_string.
            files[fp] = files[fp].replace(old, new)
            continue

    return files


def _write_exported_files(*, output_dir: Path, files: dict[str, str], include_tools_dir: bool) -> list[Path]:
    written: list[Path] = []
    for fp, content in sorted(files.items()):
        if fp.startswith("/memories/"):
            rel = fp.lstrip("/")
        elif include_tools_dir and fp.startswith("/tools/"):
            rel = fp.lstrip("/")
        else:
            continue

        dest = output_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)

        detections = SecretDetector.detect(text=content)
        if detections:
            raise RuntimeError(f"Secret-like material detected in {fp}: {', '.join(sorted(set(detections)))}")

        dest.write_text(content, encoding="utf-8")
        written.append(dest)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export LangSmith Agent Builder agent_config (memories/) to local repo")
    parser.add_argument("--base-url", default=DEEPAGENTS_DEFAULT_BASE_URL, help="LangGraph deployment base URL")
    parser.add_argument("--tenant-id", default=os.getenv("LANGSMITH_TENANT_ID", "").strip())
    parser.add_argument("--assistant-id", default=os.getenv("LANGSMITH_ASSISTANT_ID", "").strip())
    parser.add_argument("--thread-id", default=os.getenv("LANGSMITH_THREAD_ID", "").strip())
    parser.add_argument("--auth-scheme", default=os.getenv("LANGSMITH_AUTH_SCHEME", "langsmith-agent").strip())
    parser.add_argument("--history-json", type=Path, help="Use an existing /threads/{id}/history JSON file (offline)")
    parser.add_argument("--output-dir", type=Path, required=True, help="Destination root; will create memories/ subtree")
    parser.add_argument("--include-tools-dir", action="store_true", help="Also export /tools/* files if present in history")
    args = parser.parse_args(argv)

    if not args.tenant_id:
        raise SystemExit("Missing --tenant-id (or LANGSMITH_TENANT_ID)")
    if not args.assistant_id:
        raise SystemExit("Missing --assistant-id (or LANGSMITH_ASSISTANT_ID)")
    if not args.thread_id and not args.history_json:
        raise SystemExit("Missing --thread-id (or LANGSMITH_THREAD_ID) unless --history-json provided")

    cfg = ExportConfig(
        base_url=str(args.base_url),
        tenant_id=str(args.tenant_id),
        assistant_id=str(args.assistant_id),
        thread_id=str(args.thread_id),
        output_dir=Path(args.output_dir),
        history_json=args.history_json,
        include_tools_dir=bool(args.include_tools_dir),
        auth_scheme=str(args.auth_scheme or "langsmith-agent"),
    )

    if cfg.history_json:
        history = json.loads(cfg.history_json.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            raise SystemExit("history-json must be a list")
    else:
        history = _fetch_thread_history(cfg)

    messages = _extract_messages_from_history(history)
    files = _reconstruct_files(messages)

    if not any(fp.startswith("/memories/") for fp in files):
        raise SystemExit("No /memories/* files found in history; cannot export")

    written = _write_exported_files(output_dir=cfg.output_dir, files=files, include_tools_dir=cfg.include_tools_dir)
    print(json.dumps({"written_files": [str(p) for p in written], "count": len(written)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

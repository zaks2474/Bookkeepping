from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple, TypedDict
from urllib.parse import urlparse

from email_triage_agent.llm_triage import (
    LlmTriageConfig,
    LlmTriageResult,
    build_prompt_inputs,
)

from . import llm_triage as llm_triage_mod


_AGENT_SPEC_CACHE: Dict[str, Any] = {"text": None, "mtimes": {}}


def _agent_spec_dir() -> Path:
    # /home/zaks/bookkeeping/scripts/email_triage_agent/langgraph_triage.py
    # -> /home/zaks/bookkeeping
    root = Path(__file__).resolve().parents[2]
    return root / "configs" / "email_triage_agent" / "agent_config" / "memories"


def _read_text(path: Path, max_chars: int = 50_000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    if len(text) > max_chars:
        return text[: max_chars - 1] + "…"
    return text


def _strip_agent_output_contract(agent_md: str) -> str:
    """
    The exported Agent Builder spec includes an Output Contract that conflicts with ZakOps' local
    LlmTriageResult contract. Keep the behavioral guidance, but remove the conflicting schema block.
    """
    text = agent_md or ""
    start = text.find("## Output Contract")
    if start < 0:
        return text
    end = text.find("## Decision Guidance", start)
    if end < 0:
        # If we can't find a clean end marker, just keep the prefix.
        return text[:start].rstrip() + "\n"
    return (text[:start] + text[end:]).strip() + "\n"


def load_agent_builder_memories_text() -> str:
    """
    Best-effort loader for the Agent Builder export. Never raises.
    """
    spec_dir = _agent_spec_dir()
    files = {
        "agent": spec_dir / "agent.md",
        "vendor_patterns": spec_dir / "vendor_patterns.md",
        "brokers": spec_dir / "brokers.md",
        "deals": spec_dir / "deals.md",
        "tools": spec_dir / "tools.json",
    }

    mtimes: Dict[str, float] = {}
    for k, p in files.items():
        try:
            mtimes[k] = p.stat().st_mtime
        except Exception:
            mtimes[k] = -1

    if _AGENT_SPEC_CACHE["text"] is not None and _AGENT_SPEC_CACHE.get("mtimes") == mtimes:
        return str(_AGENT_SPEC_CACHE["text"])

    agent_md = _strip_agent_output_contract(_read_text(files["agent"]))
    vendor_md = _read_text(files["vendor_patterns"])
    brokers_md = _read_text(files["brokers"])
    deals_md = _read_text(files["deals"])
    tools_json = _read_text(files["tools"])

    parts = [
        "=== Agent Builder Memories (Local) ===",
        "",
        agent_md.strip(),
        "",
        "=== Vendor Patterns ===",
        "",
        vendor_md.strip(),
        "",
        "=== Brokers (reference) ===",
        "",
        brokers_md.strip(),
        "",
        "=== Deals (reference) ===",
        "",
        deals_md.strip(),
        "",
        "=== Tools (reference) ===",
        "",
        tools_json.strip(),
        "",
    ]
    text = "\n".join([p for p in parts if p is not None]).strip() + "\n"

    _AGENT_SPEC_CACHE["text"] = text
    _AGENT_SPEC_CACHE["mtimes"] = mtimes
    return text


def _host_is_local(host: str) -> bool:
    host = (host or "").strip()
    if not host:
        return False
    host_l = host.lower()
    if host_l in {"localhost", "127.0.0.1", "::1", "0.0.0.0", "host.docker.internal"}:
        return True
    try:
        ip = ip_address(host_l)
        return bool(ip.is_loopback or ip.is_private)
    except ValueError:
        pass

    try:
        infos = socket.getaddrinfo(host_l, None)
    except Exception:
        return False

    resolved_any = False
    for family, _type, _proto, _canonname, sockaddr in infos:
        if family not in (socket.AF_INET, socket.AF_INET6):
            continue
        resolved_any = True
        ip_str = sockaddr[0]
        try:
            ip = ip_address(ip_str)
        except ValueError:
            return False
        if not (ip.is_loopback or ip.is_private):
            return False
    return resolved_any


def _assert_local_base_url(base_url: str) -> Optional[str]:
    """
    Returns an error string if base_url is not local / RFC1918 / loopback.
    """
    raw = (base_url or "").strip()
    if not raw:
        return "llm_base_url_empty"
    parsed = urlparse(raw)
    host = parsed.hostname or ""
    if not _host_is_local(host):
        return f"llm_base_url_not_local:{raw}"
    return None


def _endpoint_from_base_url(base_url: str) -> str:
    b = (base_url or "").strip().rstrip("/")
    if not b:
        return "http://localhost:8000/v1/chat/completions"
    if b.endswith("/chat/completions"):
        return b
    return f"{b}/chat/completions"


def _call_local_vllm_json(
    *,
    cfg: LlmTriageConfig,
    system_prompt: str,
    user_prompt: str,
) -> Tuple[Optional[str], int, Optional[str]]:
    """
    Returns (model_content, latency_ms, error_reason). Never raises.
    """
    endpoint = _endpoint_from_base_url(cfg.base_url)

    payload: Dict[str, Any] = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": int(cfg.max_tokens),
    }

    started = time.monotonic()
    try:
        req = urllib.request.Request(
            url=endpoint,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=float(cfg.timeout_s)) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        except Exception:
            body = ""
        return None, int((time.monotonic() - started) * 1000), f"llm_http_error:{e.code}:{body[:200]}"
    except Exception as e:
        return None, int((time.monotonic() - started) * 1000), f"llm_request_error:{type(e).__name__}"

    latency_ms = int((time.monotonic() - started) * 1000)
    try:
        data = json.loads(raw)
    except Exception:
        return None, latency_ms, "llm_bad_json"

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        return None, latency_ms, "llm_missing_content"

    return str(content), latency_ms, None


class _TriageState(TypedDict, total=False):
    system_prompt: str
    user_prompt: str
    raw_content: str
    latency_ms: int
    error: str
    result: LlmTriageResult


def call_langgraph_triage(
    *,
    cfg: LlmTriageConfig,
    subject: str,
    sender: str,
    received_at: str,
    body_text: str,
    extracted_urls: Sequence[str],
    attachments: Sequence[Dict[str, Any]],
) -> Tuple[Optional[LlmTriageResult], Optional[str]]:
    """
    LangGraph-backed triage. Returns (result, error_reason). Never raises.

    Safe-by-default:
    - hard-blocks non-local base URLs
    - returns a structured error instead of raising if LangGraph is unavailable
    """
    try:
        from langgraph.graph import END, StateGraph
    except Exception:
        return None, "langgraph_not_installed"

    base_url_err = _assert_local_base_url(cfg.base_url)
    if base_url_err:
        return None, base_url_err

    agent_memories = load_agent_builder_memories_text()

    base_system, user_prompt = build_prompt_inputs(
        subject=subject,
        sender=sender,
        received_at=received_at,
        body_text=body_text,
        extracted_urls=extracted_urls,
        attachments=attachments,
        max_body_chars=cfg.max_body_chars,
    )

    system_prompt = (
        base_system.strip()
        + "\n\n"
        + "Additional guidance (exported Agent Builder memories; behavioral only):\n"
        + agent_memories
    )

    def node_prepare(state: _TriageState) -> _TriageState:
        return {
            **state,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }

    def node_call_llm(state: _TriageState) -> _TriageState:
        content, latency_ms, err = _call_local_vllm_json(
            cfg=cfg, system_prompt=str(state.get("system_prompt") or ""), user_prompt=str(state.get("user_prompt") or "")
        )
        if err or not content:
            return {**state, "error": err or "llm_empty_content", "latency_ms": int(latency_ms)}
        return {**state, "raw_content": content, "latency_ms": int(latency_ms)}

    def node_parse(state: _TriageState) -> _TriageState:
        if state.get("error"):
            return state
        raw = str(state.get("raw_content") or "")
        parsed = llm_triage_mod._parse_json_object(raw)  # noqa: SLF001 - internal helper reused intentionally
        if not parsed:
            return {**state, "error": "llm_output_not_json"}
        latency_ms = int(state.get("latency_ms") or 0)
        result = llm_triage_mod._validate_and_build_result(  # noqa: SLF001 - internal helper reused intentionally
            data=parsed,
            model=cfg.model,
            latency_ms=latency_ms,
        )
        if not result:
            return {**state, "error": "llm_output_schema_invalid"}
        return {**state, "result": result}

    graph = StateGraph(_TriageState)
    graph.add_node("prepare", node_prepare)
    graph.add_node("call_llm", node_call_llm)
    graph.add_node("parse", node_parse)
    graph.set_entry_point("prepare")
    graph.add_edge("prepare", "call_llm")
    graph.add_edge("call_llm", "parse")
    graph.add_edge("parse", END)

    compiled = graph.compile()
    out: _TriageState = compiled.invoke({})
    if out.get("error"):
        return None, str(out.get("error"))
    return out.get("result"), None


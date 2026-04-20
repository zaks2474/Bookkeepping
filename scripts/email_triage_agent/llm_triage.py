from __future__ import annotations

import json
import logging
import os
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from ipaddress import ip_address
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

from email_triage_agent.ma_triage_v1 import (
    SCHEMA_VERSION as MA_TRIAGE_V1_SCHEMA_VERSION,
    safe_url as ma_safe_url,
    to_markdown as ma_triage_v1_to_markdown,
    validate_and_normalize as validate_ma_triage_v1,
)

_log = logging.getLogger(__name__)


ALLOWED_CLASSIFICATIONS = {
    # Legacy labels (kept for backward compatibility)
    "NON_DEAL",
    "RECEIPT",
    # Primary labels (current)
    "DEAL_SIGNAL",
    "OPERATIONAL",
    "NEWSLETTER",
    "SPAM",
    "PORTAL_ACCOUNT",
    "UNCERTAIN",
}
ALLOWED_ATTACHMENT_TYPES = {"NDA", "CIM", "TEASER", "FINANCIALS", "OTHER"}
ALLOWED_LINK_TYPES = {"dataroom", "cim", "nda", "financials", "calendar", "docs", "other"}
ALLOWED_SENDER_ROLES = {"broker", "owner", "friend", "lender", "unknown"}
ALLOWED_MATERIAL_KINDS = {"NDA", "CIM", "FINANCIALS", "TEASER", "DATAROOM", "NONE"}


@dataclass(frozen=True)
class LlmTriageConfig:
    mode: str  # off|assist|full
    base_url: str
    model: str
    timeout_s: float
    max_tokens: int
    max_body_chars: int


@dataclass(frozen=True)
class LlmAttachmentSummary:
    filename: str
    guessed_type: str
    notes: str


@dataclass(frozen=True)
class LlmLinkSummary:
    url: str
    link_type: str
    requires_auth: bool


@dataclass(frozen=True)
class LlmTriageResult:
    classification: str
    confidence: float
    summary_bullets: List[str]
    company_name_guess: str
    broker_name: str
    broker_email: str
    asking_price: str
    key_metrics: Dict[str, Any]
    attachments: List[LlmAttachmentSummary]
    links: List[LlmLinkSummary]
    operator_recommendation: str
    reasons: List[str]
    model: str
    latency_ms: int
    # Optional "Email 3H" deep triage fields (thread-aware mode).
    deal_likelihood_reason: str = ""
    sender_role_guess: str = "unknown"
    materials_detected: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    attachments_assessed: List[Dict[str, Any]] = field(default_factory=list)


_JSON_FENCE_RE = re.compile(r"^```(?:json)?\\s*|```\\s*$", re.IGNORECASE | re.MULTILINE)
_JSON_FENCE_BLOCK_RE = re.compile(r"```(?:json)?\\s*(\\{.*?\\})\\s*```", re.DOTALL | re.IGNORECASE)

_REPAIR_SYSTEM_PROMPT = (
    "You are a JSON repair tool.\n"
    "Rules:\n"
    "- Output JSON ONLY. No markdown, no commentary, no extra text.\n"
    "- Do not add new facts.\n"
    "- Do not add new keys beyond the schema.\n"
    "- If a field is missing, use null (or empty array/object) as appropriate.\n"
    "- Ensure numbers are valid JSON numbers and booleans are true/false.\n"
)

_REPAIR_SCHEMA_V1 = (
    "{\n"
    '  "classification": "DEAL_SIGNAL"|"OPERATIONAL"|"NEWSLETTER"|"SPAM"|"PORTAL_ACCOUNT"|"UNCERTAIN"|"NON_DEAL"|"RECEIPT",\n'
    '  "confidence": number (0..1),\n'
    '  "summary_bullets": string[],\n'
    '  "company_name_guess": string|null,\n'
    '  "broker_name": string,\n'
    '  "broker_email": string,\n'
    '  "asking_price": string,\n'
    '  "key_metrics": object,\n'
    '  "deal_likelihood_reason": string,\n'
    '  "sender_role_guess": "broker"|"owner"|"friend"|"lender"|"unknown",\n'
    '  "materials_detected": {"kind": "NDA"|"CIM"|"FINANCIALS"|"TEASER"|"DATAROOM"|"NONE", "confidence": number (0..1)},\n'
    '  "evidence": [{"message_index": number, "snippet": string, "why_it_matters": string}],\n'
    '  "links": [{"url": string, "link_type": "dataroom"|"cim"|"nda"|"financials"|"teaser"|"calendar"|"docs"|"other", "requires_auth": boolean}],\n'
    '  "attachments": [{"filename": string, "guessed_type": "NDA"|"CIM"|"TEASER"|"FINANCIALS"|"OTHER", "notes": string}],\n'
    '  "attachments_assessed": [{"filename": string, "deal_material": boolean, "why": string}],\n'
    '  "operator_recommendation": string,\n'
    '  "reasons": string[]\n'
    "}\n"
)

_MA_TRIAGE_REPAIR_SCHEMA_V1 = (
    "{\n"
    f'  "schema_version": "{MA_TRIAGE_V1_SCHEMA_VERSION}",\n'
    '  "message_scope": "single"|"thread",\n'
    "\n"
    '  "ma_relevant": boolean,\n'
    '  "routing": "QUARANTINE_REVIEW"|"AUTO_APPEND_EXISTING_DEAL"|"NON_DEAL",\n'
    '  "ma_intent": "NEW_OPPORTUNITY"|"MATERIALS"|"PROCESS"|"SUPPORT"|"UNCLEAR"|"NON_DEAL",\n'
    '  "confidence": number (0..1),\n'
    "\n"
    '  "target_company": {"name": string|null, "name_confidence": number (0..1), "website": string|null, "industry": string|null, "location": string|null},\n'
    '  "actors": {"sender_role_guess": "BROKER"|"OWNER"|"SELLER_REP"|"BUYER_REP"|"LENDER"|"ATTORNEY"|"ACCOUNTANT"|"DILIGENCE"|"VDR_ADMIN"|"OTHER"|"UNKNOWN", "sender_org_guess": string|null},\n'
    '  "deal_signals": {\n'
    '    "stage_hint": "INBOUND"|"NDA"|"CIM"|"IOI"|"LOI"|"DILIGENCE"|"FINANCING"|"LEGAL"|"CLOSING"|"UNKNOWN",\n'
    '    "valuation_terms": {"ask_price": string|null, "revenue": string|null, "ebitda": string|null, "sde": string|null, "multiple": string|null, "currency": string|null},\n'
    '    "timeline_hint": string|null\n'
    "  },\n"
    '  "materials": {\n'
    '    "attachments": [{"filename": string, "detected_type": "CIM"|"TEASER"|"NDA"|"FINANCIALS"|"TAX"|"OPERATIONS"|"LEGAL"|"IMAGE"|"OTHER", "confidence": number (0..1), "notes": string|null}],\n'
    '    "links": [{"url": "https://domain/path", "link_type": "DATAROOM"|"DOCS"|"NDA"|"CIM"|"TEASER"|"FINANCIALS"|"CALENDAR"|"PORTAL"|"OTHER", "auth_required": "YES"|"NO"|"MAYBE", "notes": string|null}]\n'
    "  },\n"
    '  "summary": {"bullets": string[3..8], "operator_recommendation": "APPROVE"|"REJECT"|"NEEDS_REVIEW", "why": string},\n'
    '  "evidence": [{"quote": string (<=240 chars), "source": "SUBJECT"|"BODY"|"THREAD"|"ATTACHMENT"|"LINK", "reason": string, "weight": number (0..1)}],\n'
    '  "safety": {"no_secrets": boolean, "urls_sanitized": boolean},\n'
    '  "debug": {"warnings": string[], "model": string, "latency_ms": number}\n'
    "}\n"
)


def load_llm_config() -> LlmTriageConfig:
    # Email 3H upgrade default: "full" (LLM is primary classifier when deterministic prefilter allows it).
    mode = (os.getenv("EMAIL_TRIAGE_LLM_MODE", "full") or "full").strip().lower()
    if mode not in {"off", "assist", "full"}:
        mode = "full"

    # Prefer explicit triage config, otherwise reuse global vLLM/OpenAI-compatible settings.
    base_url = (
        os.getenv("EMAIL_TRIAGE_LLM_BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or os.getenv("VLLM_ENDPOINT")  # sometimes set to full /chat/completions
        or "http://localhost:8000/v1"
    ).strip()

    model = (
        os.getenv("EMAIL_TRIAGE_LLM_MODEL")
        or os.getenv("VLLM_MODEL")
        or os.getenv("DEFAULT_MODEL")
        or "Qwen/Qwen2.5-32B-Instruct-AWQ"
    ).strip()

    timeout_s = float(os.getenv("EMAIL_TRIAGE_LLM_TIMEOUT_S", "45") or "45")
    max_tokens = int(os.getenv("EMAIL_TRIAGE_LLM_MAX_TOKENS", "1400") or "1400")
    max_body_chars = int(os.getenv("EMAIL_TRIAGE_LLM_MAX_BODY_CHARS", "12000") or "12000")

    return LlmTriageConfig(
        mode=mode,
        base_url=base_url,
        model=model,
        timeout_s=timeout_s,
        max_tokens=max_tokens,
        max_body_chars=max_body_chars,
    )


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
    # If user passed the full endpoint already, keep it.
    if b.endswith("/chat/completions"):
        return b
    return f"{b}/chat/completions"


def _strip_json_fences(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return raw
    return _JSON_FENCE_RE.sub("", raw).strip()


def _parse_json_object(text: str) -> Optional[Dict[str, Any]]:
    raw = (text or "").strip()
    if not raw:
        return None

    # Fast path: strict JSON (optionally fenced).
    candidate = _strip_json_fences(raw)
    if candidate:
        try:
            data = json.loads(candidate)
            return data if isinstance(data, dict) else None
        except Exception:
            pass

    # Fenced JSON block (```json {...} ```).
    m = _JSON_FENCE_BLOCK_RE.search(raw)
    if m:
        try:
            data = json.loads(m.group(1).strip())
            return data if isinstance(data, dict) else None
        except Exception:
            pass

    # Best-effort: first "{" .. last "}".
    start = candidate.find("{") if candidate else raw.find("{")
    end = candidate.rfind("}") if candidate else raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads((candidate if candidate else raw)[start : end + 1])
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    return None


def _repair_prompt_for_output(*, raw_output: str) -> Tuple[str, str]:
    content = (raw_output or "").strip()
    # Avoid sending extremely large malformed outputs back into the model.
    if len(content) > 20_000:
        content = content[:20_000] + "…"
    user = (
        "Fix the following content into VALID JSON ONLY.\n\n"
        "It MUST match exactly this schema:\n\n"
        f"{_REPAIR_SCHEMA_V1}\n"
        "Repair rules:\n"
        "- Keep the same meaning.\n"
        "- If something is unknown, use null / empty arrays.\n"
        "- Ensure confidence is between 0.0 and 1.0.\n\n"
        "CONTENT TO REPAIR:\n"
        "<<<\n"
        f"{content}\n"
        ">>>\n"
    )
    return _REPAIR_SYSTEM_PROMPT, user


def _call_local_vllm_content(
    *,
    cfg: LlmTriageConfig,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
) -> Tuple[Optional[str], int, Optional[str]]:
    """
    Calls the local OpenAI-compatible endpoint (vLLM) and returns (content, latency_ms, error_reason).
    Never raises.
    """
    base_url_err = _assert_local_base_url(cfg.base_url)
    if base_url_err:
        return None, 0, base_url_err

    endpoint = _endpoint_from_base_url(cfg.base_url)
    payload: Dict[str, Any] = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": float(temperature),
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
        # P2: Detect encoding errors (replacement character indicates bad bytes)
        if "\ufffd" in raw:
            latency_ms = int((time.monotonic() - started) * 1000)
            _log.warning("llm_encoding_error replacement_chars_in_response")
            return None, latency_ms, "llm_encoding_error"
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        except Exception:
            body = ""
        latency_ms = int((time.monotonic() - started) * 1000)
        return None, latency_ms, f"llm_http_error:{e.code}:{body[:200]}"
    except Exception:
        latency_ms = int((time.monotonic() - started) * 1000)
        return None, latency_ms, "llm_request_error"

    latency_ms = int((time.monotonic() - started) * 1000)
    try:
        data = json.loads(raw)
    except Exception:
        return None, latency_ms, "llm_bad_json"

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        return None, latency_ms, "llm_missing_content"

    # P1: Detect truncated JSON responses (token limit likely hit)
    content_str = str(content).strip()
    if content_str:
        open_braces = content_str.count("{")
        close_braces = content_str.count("}")
        if open_braces > close_braces or content_str.rstrip().endswith(","):
            _log.warning("llm_incomplete_response open=%d close=%d trailing_comma=%s",
                         open_braces, close_braces, content_str.rstrip().endswith(","))
            return None, latency_ms, "llm_incomplete_response"

    return content_str, latency_ms, None


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "1", "yes", "y"}:
            return True
        if v in {"false", "0", "no", "n"}:
            return False
    return default


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        f = float(value)
    except Exception:
        return default
    if f != f:  # NaN
        return default
    return max(0.0, min(1.0, f))


def _normalize_bullets(value: Any) -> List[str]:
    if isinstance(value, list):
        out = [str(x or "").strip() for x in value if str(x or "").strip()]
    else:
        out = [str(value or "").strip()] if str(value or "").strip() else []
    # Keep it bounded.
    out = out[:8]
    return out


def _normalize_reasons(value: Any) -> List[str]:
    reasons = _normalize_bullets(value)
    return reasons[:8]


def _normalize_attachments(value: Any) -> List[LlmAttachmentSummary]:
    out: List[LlmAttachmentSummary] = []
    if not isinstance(value, list):
        return out
    for item in value[:25]:
        if not isinstance(item, dict):
            continue
        filename = str(item.get("filename") or "").strip()
        guessed = str(item.get("guessed_type") or item.get("type") or "").strip().upper()
        notes = str(item.get("notes") or "").strip()
        if not filename:
            continue
        if guessed not in ALLOWED_ATTACHMENT_TYPES:
            guessed = "OTHER"
        out.append(LlmAttachmentSummary(filename=filename, guessed_type=guessed, notes=notes))
    return out


def _normalize_links(value: Any) -> List[LlmLinkSummary]:
    out: List[LlmLinkSummary] = []
    if not isinstance(value, list):
        return out
    for item in value[:50]:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        link_type = str(item.get("link_type") or item.get("type") or "").strip().lower()
        requires_auth = _coerce_bool(item.get("requires_auth"), default=True)
        if not url:
            continue
        if link_type not in ALLOWED_LINK_TYPES:
            link_type = "other"
        out.append(LlmLinkSummary(url=url, link_type=link_type, requires_auth=requires_auth))
    return out


def _normalize_sender_role(value: Any) -> str:
    role = str(value or "").strip().lower()
    if not role:
        return "unknown"
    return role if role in ALLOWED_SENDER_ROLES else "unknown"


def _normalize_materials_detected(value: Any) -> Dict[str, Any]:
    """
    Accepts either:
      - {"kind": "...", "confidence": 0..1}
      - {"type": "...", "confidence": ...}
      - {"materials_detected": {...}} (already nested)
    Returns a normalized dict with keys: kind, confidence.
    """
    if isinstance(value, dict) and "materials_detected" in value and isinstance(value.get("materials_detected"), dict):
        value = value.get("materials_detected")
    if not isinstance(value, dict):
        return {}
    kind = str(value.get("kind") or value.get("type") or "").strip().upper()
    conf = _coerce_float(value.get("confidence"), default=0.0)
    if kind and kind not in ALLOWED_MATERIAL_KINDS:
        kind = "NONE"
    if not kind:
        kind = "NONE"
    return {"kind": kind, "confidence": conf}


def _normalize_evidence(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in value[:8]:
        if not isinstance(item, dict):
            continue
        try:
            idx = int(item.get("message_index")) if item.get("message_index") is not None else None
        except Exception:
            idx = None
        snippet = str(item.get("snippet") or "").strip()
        why = str(item.get("why_it_matters") or item.get("why") or "").strip()
        out.append(
            {
                "message_index": idx,
                "snippet": snippet[:500],
                "why_it_matters": why[:500],
            }
        )
    return out


def _normalize_attachments_assessed(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in value[:50]:
        if not isinstance(item, dict):
            continue
        filename = str(item.get("filename") or "").strip()
        if not filename:
            continue
        deal_material = _coerce_bool(item.get("deal_material"), default=False)
        why = str(item.get("why") or item.get("notes") or "").strip()
        out.append({"filename": filename, "deal_material": deal_material, "why": why[:500]})
    return out


_EXPECTED_LLM_FIELDS = {
    "classification", "confidence", "summary_bullets",
    "company_name_guess", "broker_name", "broker_email", "asking_price",
    "key_metrics", "attachments", "links",
    "operator_recommendation", "reasons",
    # Optional/extended fields
    "deal_likelihood_reason", "deal_likelihood",  # alias
    "sender_role_guess", "materials_detected", "evidence", "attachments_assessed",
}


def _validate_and_build_result(
    *,
    data: Dict[str, Any],
    model: str,
    latency_ms: int,
) -> Optional[LlmTriageResult]:
    # P0: Detect hallucinated fields (model drift indicator)
    extra_fields = set(data.keys()) - _EXPECTED_LLM_FIELDS
    if extra_fields:
        _log.warning("llm_hallucinated_fields model=%s fields=%s", model, sorted(extra_fields))

    classification = str(data.get("classification") or "").strip().upper()
    if classification not in ALLOWED_CLASSIFICATIONS:
        return None

    confidence = _coerce_float(data.get("confidence"), default=0.0)

    bullets = _normalize_bullets(data.get("summary_bullets"))
    # Require at least 1 bullet to treat as “usable”.
    if not bullets:
        return None

    company = str(data.get("company_name_guess") or "").strip()
    broker_name = str(data.get("broker_name") or "").strip()
    broker_email = str(data.get("broker_email") or "").strip()
    asking_price = str(data.get("asking_price") or "").strip()

    key_metrics = data.get("key_metrics")
    if not isinstance(key_metrics, dict):
        key_metrics = {}

    attachments = _normalize_attachments(data.get("attachments"))
    links = _normalize_links(data.get("links"))

    operator_rec = str(data.get("operator_recommendation") or "").strip()
    reasons = _normalize_reasons(data.get("reasons"))

    return LlmTriageResult(
        classification=classification,
        confidence=confidence,
        summary_bullets=bullets,
        company_name_guess=company,
        broker_name=broker_name,
        broker_email=broker_email,
        asking_price=asking_price,
        key_metrics=key_metrics,
        attachments=attachments,
        links=links,
        operator_recommendation=operator_rec,
        reasons=reasons,
        model=model,
        latency_ms=latency_ms,
        deal_likelihood_reason=str(data.get("deal_likelihood_reason") or data.get("deal_likelihood") or "").strip(),
        sender_role_guess=_normalize_sender_role(data.get("sender_role_guess")),
        materials_detected=_normalize_materials_detected(data.get("materials_detected") or {}),
        evidence=_normalize_evidence(data.get("evidence")),
        attachments_assessed=_normalize_attachments_assessed(data.get("attachments_assessed")),
    )


def build_prompt_inputs(
    *,
    subject: str,
    sender: str,
    received_at: str,
    body_text: str,
    extracted_urls: Sequence[str],
    attachments: Sequence[Dict[str, Any]],
    max_body_chars: int,
) -> Tuple[str, str]:
    """
    Returns (system_prompt, user_prompt). Keep it compact to reduce latency.
    """
    body = (body_text or "").strip()
    if len(body) > max_body_chars:
        body = body[: max_body_chars - 1] + "…"

    urls = [str(u or "").strip() for u in (extracted_urls or []) if str(u or "").strip()]
    urls = urls[:50]

    att_lines: List[str] = []
    for a in attachments[:25]:
        if not isinstance(a, dict):
            continue
        fname = str(a.get("filename") or "").strip()
        size = a.get("size_bytes")
        if fname:
            att_lines.append(f"- {fname} ({size} bytes)" if size is not None else f"- {fname}")

    system = (
        "You are an email triage assistant for an M&A acquisition pipeline.\n"
        "You must output ONLY strict JSON (no markdown) that matches this schema:\n"
        "{\n"
        '  \"classification\": \"DEAL_SIGNAL\"|\"NON_DEAL\"|\"NEWSLETTER\"|\"RECEIPT\"|\"OPERATIONAL\",\n'
        "  \"confidence\": number (0..1),\n"
        "  \"summary_bullets\": string[3..8],\n"
        "  \"company_name_guess\": string,\n"
        "  \"broker_name\": string,\n"
        "  \"broker_email\": string,\n"
        "  \"asking_price\": string,\n"
        "  \"key_metrics\": object,\n"
        "  \"attachments\": [{\"filename\": string, \"guessed_type\": \"NDA\"|\"CIM\"|\"TEASER\"|\"FINANCIALS\"|\"OTHER\", \"notes\": string}],\n"
        "  \"links\": [{\"url\": string, \"link_type\": \"dataroom\"|\"cim\"|\"nda\"|\"financials\"|\"calendar\"|\"docs\"|\"other\", \"requires_auth\": boolean}],\n"
        "  \"operator_recommendation\": string,\n"
        "  \"reasons\": string[]\n"
        "}\n"
        "Rules:\n"
        "- Be conservative: if this is marketing/newsletter/receipt, classify it accordingly.\n"
        "- Do NOT invent numbers; only extract if clearly present.\n"
        "- If links look like portals (ShareFile/Box/Dropbox/DocSend/etc.), mark requires_auth=true.\n"
        "- Keep bullets short and actionable.\n"
    )

    user = (
        f"Subject: {subject}\n"
        f"From: {sender}\n"
        f"Received: {received_at}\n\n"
        "Body:\n"
        f"{body}\n\n"
        "Extracted URLs (may be incomplete):\n"
        + ("\n".join(f"- {u}" for u in urls) if urls else "- (none)")  # noqa: W503
        + "\n\nAttachments:\n"
        + ("\n".join(att_lines) if att_lines else "- (none)")  # noqa: W503
        + "\n"
    )

    return system, user


def build_thread_prompt_inputs(
    *,
    thread_messages: Sequence[Dict[str, Any]],
    max_body_chars: int,
) -> Tuple[str, str]:
    """
    Returns (system_prompt, user_prompt) for thread-aware triage.

    IMPORTANT:
    - The caller should pass messages ordered oldest -> newest.
    - Bodies should already be cleaned (preferably URL-stripped), with URLs provided separately.
    """
    msgs = list(thread_messages or [])
    if len(msgs) > 25:
        # Keep the thread bounded; long threads tend to include lots of repeated quoting.
        msgs = msgs[-25:]

    lines: List[str] = []
    for i, m in enumerate(msgs):
        subject = str(m.get("subject") or "").strip()
        sender = str(m.get("from") or "").strip()
        to = str(m.get("to") or "").strip()
        date = str(m.get("date") or "").strip()
        body = str(m.get("body_text") or "").strip()
        if len(body) > max_body_chars:
            body = body[: max_body_chars - 1] + "…"

        urls = m.get("urls") if isinstance(m.get("urls"), list) else []
        urls = [str(u or "").strip() for u in urls if str(u or "").strip()][:50]

        attachments = m.get("attachments") if isinstance(m.get("attachments"), list) else []
        att_lines = []
        for a in attachments[:25]:
            if not isinstance(a, dict):
                continue
            fname = str(a.get("filename") or "").strip()
            size = a.get("size_bytes")
            if fname:
                att_lines.append(f"- {fname} ({size} bytes)" if size is not None else f"- {fname}")

        lines.extend(
            [
                f"=== MESSAGE {i} (oldest->newest order) ===",
                f"Date: {date}",
                f"From: {sender}",
                f"To: {to}",
                f"Subject: {subject}",
                "",
                "Body (cleaned; URLs removed):",
                body or "(empty)",
                "",
                "Extracted URLs:",
                ("\n".join(f"- {u}" for u in urls) if urls else "- (none)"),
                "",
                "Attachments:",
                ("\n".join(att_lines) if att_lines else "- (none)"),
                "",
            ]
        )

    system = (
        "You are a deep email-thread triage assistant for an M&A acquisition pipeline.\n"
        "You will be given the FULL email thread (multiple messages) in chronological order.\n"
        "\n"
        "You must output ONLY strict JSON (no markdown) that matches this schema:\n"
        "{\n"
        '  \"classification\": \"DEAL_SIGNAL\"|\"OPERATIONAL\"|\"NEWSLETTER\"|\"SPAM\"|\"PORTAL_ACCOUNT\"|\"UNCERTAIN\",\n'
        "  \"confidence\": number (0..1),\n"
        "  \"summary_bullets\": string[3..8],\n"
        "  \"deal_likelihood_reason\": string,\n"
        "  \"evidence\": [{\"message_index\": number, \"snippet\": string, \"why_it_matters\": string}] (2..5),\n"
        "  \"company_name_guess\": string|null,\n"
        "  \"sender_role_guess\": \"broker\"|\"owner\"|\"friend\"|\"lender\"|\"unknown\",\n"
        "  \"materials_detected\": {\"kind\": \"NDA\"|\"CIM\"|\"FINANCIALS\"|\"TEASER\"|\"DATAROOM\"|\"NONE\", \"confidence\": number (0..1)},\n"
        "  \"links\": [{\"url\": string, \"link_type\": \"dataroom\"|\"cim\"|\"nda\"|\"financials\"|\"teaser\"|\"calendar\"|\"docs\"|\"other\", \"requires_auth\": boolean}],\n"
        "  \"attachments_assessed\": [{\"filename\": string, \"deal_material\": boolean, \"why\": string}],\n"
        "  \"operator_recommendation\": string,\n"
        "  \"reasons\": string[]\n"
        "}\n"
        "\n"
        "Rules:\n"
        "- Be conservative. Marketing/newsletters/receipts should not be DEAL_SIGNAL.\n"
        "- Do NOT invent numbers or claims.\n"
        "- Evidence snippets must be short and must reference the provided thread content (by message_index).\n"
        "- If you cannot confidently decide, use classification=UNCERTAIN and explain why.\n"
    )

    user = "\n".join(lines).strip() + "\n"

    # P1: Cap total prompt size to avoid OOM/context overflow (~50K chars ~ 12K tokens)
    MAX_PROMPT_CHARS = 50_000
    if len(user) > MAX_PROMPT_CHARS and len(msgs) > 5:
        _log.warning("llm_prompt_too_large chars=%d msgs=%d, truncating to last 5", len(user), len(msgs))
        # Recursively rebuild with fewer messages
        return build_thread_prompt_inputs(
            thread_messages=msgs[-5:],
            max_body_chars=max_body_chars,
        )

    return system, user


_MA_TRIAGE_SYSTEM_PROMPT = (
    "You are ZakOps Email Triage, an expert M&A analyst.\n"
    "Your job is to decide whether an email (and optionally its thread) is relevant to business acquisition work (M&A).\n"
    "M&A relevance includes:\n"
    "- sourcing opportunities (broker/owner outreach, selling a business)\n"
    "- deal materials (NDA/CIM/teaser/financials/dataroom)\n"
    "- process execution (IOI/LOI/diligence/legal/financing/closing)\n"
    "- deal-support communications (lawyers/lenders/accountants/diligence providers)\n"
    "\n"
    "Hard rules:\n"
    "- Output JSON ONLY (no markdown, no commentary, no extra text).\n"
    "- Do NOT invent facts.\n"
    "- Do NOT include secrets or tokens.\n"
    "- Do NOT include URL query params or fragments. Use only scheme+domain+path.\n"
    "- Evidence quotes must be <=240 chars each.\n"
    "- If uncertain, set ma_intent=UNCLEAR and operator_recommendation=NEEDS_REVIEW with lower confidence.\n"
)


def build_ma_triage_v1_prompt_inputs_single(
    *,
    subject: str,
    sender: str,
    received_at: str,
    body_text: str,
    extracted_urls: Sequence[str],
    attachments: Sequence[Dict[str, Any]],
    max_body_chars: int,
    prefilter_flags: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    body = (body_text or "").strip()
    if len(body) > max_body_chars:
        body = body[: max_body_chars - 1] + "…"

    urls = [ma_safe_url(str(u or "").strip()) for u in (extracted_urls or []) if str(u or "").strip()]
    urls = urls[:50]

    att_lines: List[str] = []
    for a in attachments[:25]:
        if not isinstance(a, dict):
            continue
        fname = str(a.get("filename") or "").strip()
        size = a.get("size_bytes")
        if fname:
            att_lines.append(f"- {fname} ({size} bytes)" if size is not None else f"- {fname}")

    pf = prefilter_flags if isinstance(prefilter_flags, dict) else {}
    pf_lines = []
    for k in sorted(pf.keys()):
        pf_lines.append(f"- {k}: {pf.get(k)!r}")

    user = (
        "Return JSON ONLY matching this schema:\n"
        + _MA_TRIAGE_REPAIR_SCHEMA_V1
        + "\nINPUT:\n"
        + ("\n".join(pf_lines) + "\n\n" if pf_lines else "")
        + "message_scope: single\n"
        + f"Subject: {subject}\n"
        + f"From: {sender}\n"
        + f"Received: {received_at}\n\n"
        + "Body (cleaned):\n"
        + f"{body}\n\n"
        + "Extracted URLs (sanitized):\n"
        + ("\n".join(f"- {u}" for u in urls) if urls else "- (none)")
        + "\n\nAttachments:\n"
        + ("\n".join(att_lines) if att_lines else "- (none)")
        + "\n"
    )

    return _MA_TRIAGE_SYSTEM_PROMPT, user


def build_ma_triage_v1_prompt_inputs_thread(
    *,
    thread_messages: Sequence[Dict[str, Any]],
    max_body_chars: int,
    prefilter_flags: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    msgs = list(thread_messages or [])
    if len(msgs) > 25:
        msgs = msgs[-25:]

    pf = prefilter_flags if isinstance(prefilter_flags, dict) else {}
    pf_lines = []
    for k in sorted(pf.keys()):
        pf_lines.append(f"- {k}: {pf.get(k)!r}")

    lines: List[str] = []
    if pf_lines:
        lines.extend(["prefilter_flags:", *pf_lines, ""])

    lines.append("message_scope: thread")
    lines.append("")

    for i, m in enumerate(msgs):
        subject = str(m.get("subject") or "").strip()
        sender = str(m.get("from") or "").strip()
        to = str(m.get("to") or "").strip()
        date = str(m.get("date") or "").strip()
        body = str(m.get("body_text") or "").strip()
        if len(body) > max_body_chars:
            body = body[: max_body_chars - 1] + "…"

        urls = m.get("urls") if isinstance(m.get("urls"), list) else []
        urls = [ma_safe_url(str(u or "").strip()) for u in urls if str(u or "").strip()][:50]

        attachments = m.get("attachments") if isinstance(m.get("attachments"), list) else []
        att_lines = []
        for a in attachments[:25]:
            if not isinstance(a, dict):
                continue
            fname = str(a.get("filename") or "").strip()
            size = a.get("size_bytes")
            if fname:
                att_lines.append(f"- {fname} ({size} bytes)" if size is not None else f"- {fname}")

        lines.extend(
            [
                f"=== MESSAGE {i} (oldest->newest order) ===",
                f"Date: {date}",
                f"From: {sender}",
                f"To: {to}",
                f"Subject: {subject}",
                "",
                "Body (cleaned):",
                body or "(empty)",
                "",
                "Extracted URLs (sanitized):",
                ("\n".join(f"- {u}" for u in urls) if urls else "- (none)"),
                "",
                "Attachments:",
                ("\n".join(att_lines) if att_lines else "- (none)"),
                "",
            ]
        )

    user = "Return JSON ONLY matching this schema:\n" + _MA_TRIAGE_REPAIR_SCHEMA_V1 + "\nINPUT:\n" + "\n".join(lines).strip() + "\n"
    return _MA_TRIAGE_SYSTEM_PROMPT, user


def _repair_prompt_for_ma_triage_v1(*, raw_output: str) -> Tuple[str, str]:
    content = (raw_output or "").strip()
    if len(content) > 20_000:
        content = content[:20_000] + "…"
    user = (
        "Fix the following content into VALID JSON ONLY.\n\n"
        "It MUST match exactly this schema:\n\n"
        f"{_MA_TRIAGE_REPAIR_SCHEMA_V1}\n"
        "Repair rules:\n"
        "- Keep the same meaning.\n"
        "- If something is unknown, use null / empty arrays.\n"
        "- Ensure confidence is between 0.0 and 1.0.\n"
        "- Evidence quotes must be <=240 chars.\n"
        "- Do NOT include URL query params/fragments.\n\n"
        "CONTENT TO REPAIR:\n"
        "<<<\n"
        f"{content}\n"
        ">>>\n"
    )
    return _REPAIR_SYSTEM_PROMPT, user


def call_local_vllm_ma_triage_v1_single(
    *,
    cfg: LlmTriageConfig,
    subject: str,
    sender: str,
    received_at: str,
    body_text: str,
    extracted_urls: Sequence[str],
    attachments: Sequence[Dict[str, Any]],
    prefilter_flags: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    system_prompt, user_prompt = build_ma_triage_v1_prompt_inputs_single(
        subject=subject,
        sender=sender,
        received_at=received_at,
        body_text=body_text,
        extracted_urls=extracted_urls,
        attachments=attachments,
        max_body_chars=cfg.max_body_chars,
        prefilter_flags=prefilter_flags,
    )
    content, latency_ms, err = _call_local_vllm_content(cfg=cfg, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.1)
    if err or content is None:
        return None, err or "llm_request_error"

    parsed = _parse_json_object(content)
    if parsed:
        normalized = validate_ma_triage_v1(parsed, model=cfg.model, latency_ms=latency_ms, message_scope="single")
        if normalized:
            return normalized, None

    repair_system, repair_user = _repair_prompt_for_ma_triage_v1(raw_output=content)
    repaired_content, repaired_latency_ms, repair_err = _call_local_vllm_content(
        cfg=cfg,
        system_prompt=repair_system,
        user_prompt=repair_user,
        temperature=0.0,
    )
    if repair_err or repaired_content is None:
        return None, f"llm_repair_call_failed:{repair_err or 'unknown'}"

    repaired = _parse_json_object(repaired_content)
    if not repaired:
        return None, "llm_repair_output_not_json"

    normalized = validate_ma_triage_v1(repaired, model=cfg.model, latency_ms=repaired_latency_ms, message_scope="single")
    if not normalized:
        return None, "llm_repair_output_schema_invalid"

    return normalized, None


def call_local_vllm_ma_triage_v1_thread(
    *,
    cfg: LlmTriageConfig,
    thread_messages: Sequence[Dict[str, Any]],
    prefilter_flags: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    system_prompt, user_prompt = build_ma_triage_v1_prompt_inputs_thread(
        thread_messages=thread_messages,
        max_body_chars=int(cfg.max_body_chars),
        prefilter_flags=prefilter_flags,
    )
    content, latency_ms, err = _call_local_vllm_content(cfg=cfg, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.1)
    if err or content is None:
        return None, err or "llm_request_error"

    parsed = _parse_json_object(content)
    if parsed:
        normalized = validate_ma_triage_v1(parsed, model=cfg.model, latency_ms=latency_ms, message_scope="thread")
        if normalized:
            return normalized, None

    repair_system, repair_user = _repair_prompt_for_ma_triage_v1(raw_output=content)
    repaired_content, repaired_latency_ms, repair_err = _call_local_vllm_content(
        cfg=cfg,
        system_prompt=repair_system,
        user_prompt=repair_user,
        temperature=0.0,
    )
    if repair_err or repaired_content is None:
        return None, f"llm_repair_call_failed:{repair_err or 'unknown'}"

    repaired = _parse_json_object(repaired_content)
    if not repaired:
        return None, "llm_repair_output_not_json"

    normalized = validate_ma_triage_v1(repaired, model=cfg.model, latency_ms=repaired_latency_ms, message_scope="thread")
    if not normalized:
        return None, "llm_repair_output_schema_invalid"

    return normalized, None


def call_local_vllm_triage(
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
    Calls the local OpenAI-compatible endpoint (vLLM) and returns (result, error_reason).
    Never raises.
    """
    system_prompt, user_prompt = build_prompt_inputs(
        subject=subject,
        sender=sender,
        received_at=received_at,
        body_text=body_text,
        extracted_urls=extracted_urls,
        attachments=attachments,
        max_body_chars=cfg.max_body_chars,
    )
    content, latency_ms, err = _call_local_vllm_content(cfg=cfg, system_prompt=system_prompt, user_prompt=user_prompt)
    if err or content is None:
        return None, err or "llm_request_error"

    parsed = _parse_json_object(content)
    if parsed:
        result = _validate_and_build_result(data=parsed, model=cfg.model, latency_ms=latency_ms)
        if result:
            return result, None

    # One repair attempt for invalid/malformed JSON outputs.
    repair_system, repair_user = _repair_prompt_for_output(raw_output=content)
    repaired_content, repaired_latency_ms, repair_err = _call_local_vllm_content(
        cfg=cfg,
        system_prompt=repair_system,
        user_prompt=repair_user,
        temperature=0.0,
    )
    if repair_err or repaired_content is None:
        return None, f"llm_repair_call_failed:{repair_err or 'unknown'}"

    repaired = _parse_json_object(repaired_content)
    if not repaired:
        return None, "llm_repair_output_not_json"

    repaired_result = _validate_and_build_result(data=repaired, model=cfg.model, latency_ms=repaired_latency_ms)
    if not repaired_result:
        return None, "llm_repair_output_schema_invalid"

    return repaired_result, None


def triage_result_to_markdown(result: LlmTriageResult) -> str:
    def _safe_url(url: str) -> str:
        """
        Strip query/fragment to avoid persisting access tokens in DataRoom artifacts.
        """
        try:
            from urllib.parse import urlsplit, urlunsplit

            parts = urlsplit(url)
            return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        except Exception:
            return (url or "").split("?", 1)[0].split("#", 1)[0]

    bullets = "\n".join(f"- {b}" for b in result.summary_bullets)
    parts: List[str] = [
        f"Classification: {result.classification} (confidence {result.confidence:.2f})",
        "",
        "Summary:",
        bullets,
    ]

    if result.company_name_guess:
        parts.append("")
        parts.append(f"Company: {result.company_name_guess}")

    if result.broker_email or result.broker_name:
        parts.append("")
        broker = " / ".join([p for p in [result.broker_name, result.broker_email] if p])
        parts.append(f"Broker: {broker}")

    if result.asking_price:
        parts.append("")
        parts.append(f"Asking: {result.asking_price}")

    if result.sender_role_guess and result.sender_role_guess != "unknown":
        parts.append("")
        parts.append(f"Sender role guess: {result.sender_role_guess}")

    if result.materials_detected:
        kind = str(result.materials_detected.get("kind") or "").strip()
        conf = result.materials_detected.get("confidence")
        if kind:
            parts.append("")
            if conf is not None:
                try:
                    conf_f = float(conf)
                except Exception:
                    conf_f = None
                if conf_f is not None:
                    parts.append(f"Materials detected: {kind} (confidence {conf_f:.2f})")
                else:
                    parts.append(f"Materials detected: {kind}")
            else:
                parts.append(f"Materials detected: {kind}")

    if result.links:
        parts.append("")
        parts.append("Links:")
        for l in result.links[:25]:
            auth = "auth" if l.requires_auth else "public"
            parts.append(f"- [{l.link_type}] ({auth}) {_safe_url(l.url)}")

    if result.attachments:
        parts.append("")
        parts.append("Attachments:")
        for a in result.attachments[:25]:
            parts.append(f"- [{a.guessed_type}] {a.filename} {('- ' + a.notes) if a.notes else ''}".rstrip())

    if result.evidence:
        parts.append("")
        parts.append("Evidence (thread):")
        for e in result.evidence[:8]:
            idx = e.get("message_index")
            snippet = str(e.get("snippet") or "").strip()
            why = str(e.get("why_it_matters") or "").strip()
            parts.append(f"- [msg {idx}] {snippet} ({why})".strip())

    if result.operator_recommendation:
        parts.append("")
        parts.append(f"Operator recommendation: {result.operator_recommendation}")

    if result.reasons:
        parts.append("")
        parts.append("Reasons:")
        parts.extend(f"- {r}" for r in result.reasons[:8])

    parts.append("")
    parts.append(f"LLM: {result.model} latency_ms={result.latency_ms}")
    return "\n".join(parts).strip() + "\n"


def call_local_vllm_thread_triage(
    *,
    cfg: LlmTriageConfig,
    thread_messages: Sequence[Dict[str, Any]],
) -> Tuple[Optional[LlmTriageResult], Optional[str]]:
    """
    Calls local vLLM/Qwen with the full thread context and returns (result, error_reason).
    Never raises.
    """
    system_prompt, user_prompt = build_thread_prompt_inputs(
        thread_messages=thread_messages,
        max_body_chars=int(cfg.max_body_chars),
    )
    content, latency_ms, err = _call_local_vllm_content(cfg=cfg, system_prompt=system_prompt, user_prompt=user_prompt)
    if err or content is None:
        return None, err or "llm_request_error"

    parsed = _parse_json_object(content)
    if parsed:
        result = _validate_and_build_result(data=parsed, model=cfg.model, latency_ms=latency_ms)
        if result:
            return result, None

    # One repair attempt for invalid/malformed JSON outputs.
    repair_system, repair_user = _repair_prompt_for_output(raw_output=content)
    repaired_content, repaired_latency_ms, repair_err = _call_local_vllm_content(
        cfg=cfg,
        system_prompt=repair_system,
        user_prompt=repair_user,
        temperature=0.0,
    )
    if repair_err or repaired_content is None:
        return None, f"llm_repair_call_failed:{repair_err or 'unknown'}"

    repaired = _parse_json_object(repaired_content)
    if not repaired:
        return None, "llm_repair_output_not_json"

    repaired_result = _validate_and_build_result(data=repaired, model=cfg.model, latency_ms=repaired_latency_ms)
    if not repaired_result:
        return None, "llm_repair_output_schema_invalid"

    return repaired_result, None

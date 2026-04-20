from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = "zakops.email_triage.v1"

ALLOWED_MESSAGE_SCOPES = {"single", "thread"}
ALLOWED_ROUTING = {"QUARANTINE_REVIEW", "AUTO_APPEND_EXISTING_DEAL", "NON_DEAL"}
ALLOWED_INTENT = {"NEW_OPPORTUNITY", "MATERIALS", "PROCESS", "SUPPORT", "UNCLEAR", "NON_DEAL"}
ALLOWED_SENDER_ROLES = {
    "BROKER",
    "OWNER",
    "SELLER_REP",
    "BUYER_REP",
    "LENDER",
    "ATTORNEY",
    "ACCOUNTANT",
    "DILIGENCE",
    "VDR_ADMIN",
    "OTHER",
    "UNKNOWN",
}
ALLOWED_STAGE_HINT = {"INBOUND", "NDA", "CIM", "IOI", "LOI", "DILIGENCE", "FINANCING", "LEGAL", "CLOSING", "UNKNOWN"}
ALLOWED_ATTACHMENT_TYPES = {"CIM", "TEASER", "NDA", "FINANCIALS", "TAX", "OPERATIONS", "LEGAL", "IMAGE", "OTHER"}
ALLOWED_LINK_TYPES = {"DATAROOM", "DOCS", "NDA", "CIM", "TEASER", "FINANCIALS", "CALENDAR", "PORTAL", "OTHER"}
ALLOWED_AUTH_REQUIRED = {"YES", "NO", "MAYBE"}
ALLOWED_OPERATOR_RECOMMENDATION = {"APPROVE", "REJECT", "NEEDS_REVIEW"}
ALLOWED_EVIDENCE_SOURCES = {"SUBJECT", "BODY", "THREAD", "ATTACHMENT", "LINK"}


def safe_url(url: str) -> str:
    """
    Strip query/fragment to avoid persisting access tokens.
    """
    try:
        from urllib.parse import urlsplit, urlunsplit

        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except Exception:
        return (url or "").split("?", 1)[0].split("#", 1)[0]


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        f = float(value)
    except Exception:
        return float(default)
    if f != f:  # NaN
        return float(default)
    return max(0.0, min(1.0, f))


def _is_str_or_none(value: Any) -> bool:
    return value is None or isinstance(value, str)


def _as_str(value: Any) -> str:
    return str(value) if value is not None else ""


def _maybe_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


_URL_LIKE_RE = re.compile(r"https?://\\S+", re.IGNORECASE)


def _sanitize_quote(text: str) -> str:
    """
    Keep evidence quotes short and avoid leaking URL query params.
    """
    raw = (text or "").strip()
    if not raw:
        return ""
    # If a quote contains a URL, strip query/fragment from it.
    def _repl(match: re.Match[str]) -> str:
        return safe_url(match.group(0))

    raw = _URL_LIKE_RE.sub(_repl, raw)
    if len(raw) > 240:
        raw = raw[:239] + "…"
    return raw


def validate_and_normalize(
    payload: Dict[str, Any],
    *,
    model: str,
    latency_ms: int,
    message_scope: str,
) -> Optional[Dict[str, Any]]:
    """
    Validate + normalize the zakops.email_triage.v1 contract.

    Returns a normalized dict (safe to persist) or None if invalid.
    """
    if not isinstance(payload, dict):
        return None

    # Allow the model to omit schema_version/message_scope, but we enforce them on output.
    schema_version = str(payload.get("schema_version") or "").strip()
    if schema_version and schema_version != SCHEMA_VERSION:
        return None

    scope = (str(payload.get("message_scope") or message_scope) or message_scope).strip().lower()
    if scope not in ALLOWED_MESSAGE_SCOPES:
        scope = message_scope

    ma_relevant = bool(payload.get("ma_relevant", False))
    routing = str(payload.get("routing") or "").strip().upper()
    if routing not in ALLOWED_ROUTING:
        routing = "QUARANTINE_REVIEW" if ma_relevant else "NON_DEAL"

    ma_intent = str(payload.get("ma_intent") or "").strip().upper()
    if ma_intent not in ALLOWED_INTENT:
        ma_intent = "UNCLEAR" if ma_relevant else "NON_DEAL"

    confidence = _clamp01(payload.get("confidence"), default=0.0)

    # target_company
    tc = payload.get("target_company")
    if not isinstance(tc, dict):
        tc = {}
    target_company = {
        "name": _maybe_str(tc.get("name")),
        "name_confidence": _clamp01(tc.get("name_confidence"), default=0.0),
        "website": _maybe_str(tc.get("website")),
        "industry": _maybe_str(tc.get("industry")),
        "location": _maybe_str(tc.get("location")),
    }

    # actors
    actors_in = payload.get("actors")
    if not isinstance(actors_in, dict):
        actors_in = {}
    sender_role_guess = str(actors_in.get("sender_role_guess") or "").strip().upper()
    if sender_role_guess not in ALLOWED_SENDER_ROLES:
        sender_role_guess = "UNKNOWN"
    actors = {"sender_role_guess": sender_role_guess, "sender_org_guess": _maybe_str(actors_in.get("sender_org_guess"))}

    # deal_signals
    ds_in = payload.get("deal_signals")
    if not isinstance(ds_in, dict):
        ds_in = {}
    stage_hint = str(ds_in.get("stage_hint") or "").strip().upper()
    if stage_hint not in ALLOWED_STAGE_HINT:
        stage_hint = "UNKNOWN"
    vt_in = ds_in.get("valuation_terms")
    if not isinstance(vt_in, dict):
        vt_in = {}
    valuation_terms = {
        "ask_price": _maybe_str(vt_in.get("ask_price")),
        "revenue": _maybe_str(vt_in.get("revenue")),
        "ebitda": _maybe_str(vt_in.get("ebitda")),
        "sde": _maybe_str(vt_in.get("sde")),
        "multiple": _maybe_str(vt_in.get("multiple")),
        "currency": _maybe_str(vt_in.get("currency")),
    }
    deal_signals = {
        "stage_hint": stage_hint,
        "valuation_terms": valuation_terms,
        "timeline_hint": _maybe_str(ds_in.get("timeline_hint")),
    }

    # materials
    materials_in = payload.get("materials")
    if not isinstance(materials_in, dict):
        materials_in = {}
    attachments_out: List[Dict[str, Any]] = []
    for item in (materials_in.get("attachments") if isinstance(materials_in.get("attachments"), list) else [])[:50]:
        if not isinstance(item, dict):
            continue
        filename = str(item.get("filename") or "").strip()
        if not filename:
            continue
        detected_type = str(item.get("detected_type") or "").strip().upper()
        if detected_type not in ALLOWED_ATTACHMENT_TYPES:
            detected_type = "OTHER"
        attachments_out.append(
            {
                "filename": filename[:200],
                "detected_type": detected_type,
                "confidence": _clamp01(item.get("confidence"), default=0.0),
                "notes": _maybe_str(item.get("notes")),
            }
        )
    links_out: List[Dict[str, Any]] = []
    for item in (materials_in.get("links") if isinstance(materials_in.get("links"), list) else [])[:100]:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        link_type = str(item.get("link_type") or "").strip().upper()
        if link_type not in ALLOWED_LINK_TYPES:
            link_type = "OTHER"
        auth_required = str(item.get("auth_required") or "").strip().upper()
        if auth_required not in ALLOWED_AUTH_REQUIRED:
            auth_required = "MAYBE"
        links_out.append(
            {
                "url": safe_url(url),
                "link_type": link_type,
                "auth_required": auth_required,
                "notes": _maybe_str(item.get("notes")),
            }
        )
    materials = {"attachments": attachments_out, "links": links_out}

    # summary
    summary_in = payload.get("summary")
    if not isinstance(summary_in, dict):
        summary_in = {}
    bullets_in = summary_in.get("bullets") if isinstance(summary_in.get("bullets"), list) else []
    bullets = [str(b or "").strip() for b in bullets_in if str(b or "").strip()]
    bullets = bullets[:8]
    if len(bullets) < 3:
        why = str(summary_in.get("why") or "").strip()
        if why:
            bullets = (bullets + [why])[:3]
    while len(bullets) < 3:
        bullets.append("")
    operator_recommendation = str(summary_in.get("operator_recommendation") or "").strip().upper()
    if operator_recommendation not in ALLOWED_OPERATOR_RECOMMENDATION:
        operator_recommendation = "NEEDS_REVIEW" if ma_relevant else "REJECT"
    summary = {
        "bullets": bullets,
        "operator_recommendation": operator_recommendation,
        "why": str(summary_in.get("why") or "").strip()[:600],
    }

    # evidence
    evidence_out: List[Dict[str, Any]] = []
    ev_in = payload.get("evidence") if isinstance(payload.get("evidence"), list) else []
    for item in ev_in[:12]:
        if not isinstance(item, dict):
            continue
        quote = _sanitize_quote(str(item.get("quote") or "").strip())
        if not quote:
            continue
        source = str(item.get("source") or "").strip().upper()
        if source not in ALLOWED_EVIDENCE_SOURCES:
            source = "THREAD" if scope == "thread" else "BODY"
        reason = str(item.get("reason") or "").strip()[:600]
        weight = _clamp01(item.get("weight"), default=0.5)
        evidence_out.append({"quote": quote, "source": source, "reason": reason, "weight": weight})

    # safety
    safety_in = payload.get("safety")
    if not isinstance(safety_in, dict):
        safety_in = {}
    safety = {
        "no_secrets": bool(safety_in.get("no_secrets", True)),
        "urls_sanitized": True,  # enforced by safe_url()
    }

    # debug
    debug_in = payload.get("debug")
    if not isinstance(debug_in, dict):
        debug_in = {}
    warnings_in = debug_in.get("warnings") if isinstance(debug_in.get("warnings"), list) else []
    warnings = [str(w or "").strip() for w in warnings_in if str(w or "").strip()][:25]
    debug = {"warnings": warnings, "model": str(model or ""), "latency_ms": int(latency_ms)}

    return {
        "schema_version": SCHEMA_VERSION,
        "message_scope": scope,
        "ma_relevant": bool(ma_relevant),
        "routing": routing,
        "ma_intent": ma_intent,
        "confidence": float(confidence),
        "target_company": target_company,
        "actors": actors,
        "deal_signals": deal_signals,
        "materials": materials,
        "summary": summary,
        "evidence": evidence_out,
        "safety": safety,
        "debug": debug,
    }


def to_markdown(payload: Dict[str, Any]) -> str:
    """
    Human-readable rendering of the v1 triage payload (for Quarantine artifacts).
    """
    tc = payload.get("target_company") if isinstance(payload.get("target_company"), dict) else {}
    actors = payload.get("actors") if isinstance(payload.get("actors"), dict) else {}
    ds = payload.get("deal_signals") if isinstance(payload.get("deal_signals"), dict) else {}
    vt = ds.get("valuation_terms") if isinstance(ds.get("valuation_terms"), dict) else {}
    materials = payload.get("materials") if isinstance(payload.get("materials"), dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    debug = payload.get("debug") if isinstance(payload.get("debug"), dict) else {}

    lines: List[str] = []
    lines.append(f"Schema: {payload.get('schema_version')}")
    lines.append(f"Scope: {payload.get('message_scope')}")
    lines.append("")
    lines.append(f"M&A relevant: {bool(payload.get('ma_relevant'))}  routing={payload.get('routing')}  intent={payload.get('ma_intent')}")
    lines.append(f"Confidence: {float(payload.get('confidence') or 0.0):.2f}")
    lines.append("")

    name = _as_str(tc.get("name")).strip()
    if name:
        lines.append(f"Target company: {name} (confidence {float(tc.get('name_confidence') or 0.0):.2f})")
    role = _as_str(actors.get("sender_role_guess")).strip()
    if role:
        lines.append(f"Sender role: {role}")
    stage = _as_str(ds.get("stage_hint")).strip()
    if stage:
        lines.append(f"Stage hint: {stage}")

    ask = _as_str(vt.get("ask_price")).strip()
    if ask:
        lines.append(f"Asking/price: {ask}")
    ebitda = _as_str(vt.get("ebitda")).strip()
    if ebitda:
        lines.append(f"EBITDA: {ebitda}")
    rev = _as_str(vt.get("revenue")).strip()
    if rev:
        lines.append(f"Revenue: {rev}")
    sde = _as_str(vt.get("sde")).strip()
    if sde:
        lines.append(f"SDE: {sde}")
    multiple = _as_str(vt.get("multiple")).strip()
    if multiple:
        lines.append(f"Multiple: {multiple}")
    currency = _as_str(vt.get("currency")).strip()
    if currency:
        lines.append(f"Currency: {currency}")

    lines.append("")
    lines.append("Summary:")
    for b in (summary.get("bullets") if isinstance(summary.get("bullets"), list) else [])[:8]:
        b_str = str(b or "").strip()
        if b_str:
            lines.append(f"- {b_str}")
    why = str(summary.get("why") or "").strip()
    if why:
        lines.append("")
        lines.append(f"Why: {why}")
    lines.append(f"Operator recommendation: {summary.get('operator_recommendation')}")

    links = materials.get("links") if isinstance(materials.get("links"), list) else []
    atts = materials.get("attachments") if isinstance(materials.get("attachments"), list) else []
    if links:
        lines.append("")
        lines.append("Links:")
        for l in links[:25]:
            if not isinstance(l, dict):
                continue
            lines.append(f"- [{l.get('link_type')}] ({l.get('auth_required')}) {l.get('url')}")
    if atts:
        lines.append("")
        lines.append("Attachments:")
        for a in atts[:25]:
            if not isinstance(a, dict):
                continue
            lines.append(f"- [{a.get('detected_type')}] {a.get('filename')}")

    evidence = payload.get("evidence") if isinstance(payload.get("evidence"), list) else []
    if evidence:
        lines.append("")
        lines.append("Evidence:")
        for e in evidence[:8]:
            if not isinstance(e, dict):
                continue
            lines.append(f"- [{e.get('source')}] {e.get('quote')} ({e.get('reason')})".strip())

    lines.append("")
    lines.append(f"LLM: {debug.get('model')} latency_ms={debug.get('latency_ms')}")
    return "\n".join(lines).strip() + "\n"


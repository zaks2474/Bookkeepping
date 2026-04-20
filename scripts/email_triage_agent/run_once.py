from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from email_triage_agent.gmail_mcp import EmailAttachment, EmailMessage, GmailMcpClient, gmail_mcp_command, gmail_mcp_env
from email_triage_agent.kinetic_actions import KineticActionsClient, extract_deal_id, safe_url
from email_triage_agent.sender_history import SenderHistoryDB
from email_triage_agent.llm_triage import (
    LlmTriageConfig,
    call_local_vllm_ma_triage_v1_single,
    call_local_vllm_ma_triage_v1_thread,
    load_llm_config,
)
from email_triage_agent.ma_triage_v1 import SCHEMA_VERSION as MA_TRIAGE_V1_SCHEMA_VERSION
from email_triage_agent.ma_triage_v1 import to_markdown as ma_triage_v1_to_markdown
from email_triage_agent.ma_triage_v1 import validate_and_normalize as validate_ma_triage_v1
from email_triage_agent.mcp_stdio import McpStdioSession
from email_triage_agent.state_db import EmailTriageStateDB
from email_triage_agent.thread_fetch import GmailThreadFetchConfig, get_thread_message_ids, load_thread_fetch_config
from email_triage_agent.triage_logic import TriageDecision, decide_actions_and_labels, normalize_email_body, sha256_text
from email_triage_agent.vendor_patterns import VendorPattern, load_vendor_patterns_md


DEFAULT_QUERY = "in:inbox -label:ZakOps/Processed newer_than:30d"
DEFAULT_MAX_PER_RUN = 50

DEFAULT_QUARANTINE_ROOT = "/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE"
DEFAULT_STATE_DB = "/home/zaks/DataRoom/.deal-registry/email_triage_state.db"
DEFAULT_SENDER_HISTORY_DB = "/home/zaks/DataRoom/.deal-registry/sender_history.db"
DEFAULT_ACTIONS_BASE_URL = "http://localhost:8090"
DEFAULT_DEAL_REGISTRY_PATH = "/home/zaks/DataRoom/.deal-registry/deal_registry.json"


SAFE_EXTS_DEFAULT = {
    "pdf",
    "doc",
    "docx",
    "rtf",
    "txt",
    "xls",
    "xlsx",
    "csv",
    "ppt",
    "pptx",
    "zip",
}

UNSAFE_EXTS_DEFAULT = {
    "exe",
    "bat",
    "cmd",
    "com",
    "msi",
    "ps1",
    "sh",
    "vbs",
    "js",
    "jar",
    "py",
    "rb",
    "pl",
    "php",
    "xlsm",
    "docm",
    "pptm",
    "iso",
    "img",
    "dmg",
}


def _dataroom_root() -> Path:
    return Path(os.getenv("DATAROOM_ROOT", "/home/zaks/DataRoom")).resolve()


_URL_LIKE_RE = re.compile(r"https?://\\S+", re.IGNORECASE)
_TRAILING_URL_PUNCT = ").,;\"')]>“”"


def _sanitize_urls_in_text(text: str) -> str:
    """
    Remove URL query/fragment from any URLs embedded in text before persisting to disk.
    This avoids leaking access tokens into local artifacts that may later be indexed or logged.
    """
    raw = text or ""
    if not raw:
        return ""

    def _repl(match: re.Match[str]) -> str:
        url = match.group(0)
        suffix = ""
        while url and url[-1] in _TRAILING_URL_PUNCT:
            suffix = url[-1] + suffix
            url = url[:-1]
        return safe_url(url) + suffix

    return _URL_LIKE_RE.sub(_repl, raw)


def _triage_log_path() -> Path:
    override = (os.getenv("EMAIL_TRIAGE_LOG_PATH") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (_dataroom_root() / ".deal-registry" / "logs" / "email_triage_3h.jsonl").resolve()


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Logging must never block triage.
        return


_SENDER_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def _extract_sender_email(sender: str) -> str:
    m = _SENDER_EMAIL_RE.search(sender or "")
    return m.group(1).lower() if m else ""


@dataclass(frozen=True)
class RunnerConfig:
    query: str
    max_per_run: int
    quarantine_root: Path
    state_db_path: Path
    sender_history_db_path: Path
    deal_registry_path: Path
    dry_run: bool
    mark_as_read: bool
    max_attachment_mb: int
    safe_exts: set[str]
    unsafe_exts: set[str]
    vendor_patterns_path: Path
    actions_base_url: str
    enable_actions: bool


def _bool_env(name: str, default: bool) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "y", "on"}


def _int_env(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _csv_env_set(name: str, default: set[str]) -> set[str]:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return set(default)
    out: set[str] = set()
    for part in raw.split(","):
        p = part.strip().lower().lstrip(".")
        if p:
            out.add(p)
    return out or set(default)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _triage_outputs_dir() -> Path:
    return Path(os.getenv("DATAROOM_ROOT", "/home/zaks/DataRoom")).resolve() / ".deal-registry" / "triage_outputs"


def write_triage_output(
    *,
    message: EmailMessage,
    final_classification: str,
    urgency: str,
    deterministic_reason: str,
    llm_backend: str,
    llm_cfg: Optional[LlmTriageConfig],
    llm_result: Optional[object],
    llm_error: Optional[str],
    quarantine_dir: Optional[Path],
    deal_id: Optional[str],
) -> None:
    """
    Best-effort audit trail for triage decisions (no raw email bodies).

    Writes:
      DataRoom/.deal-registry/triage_outputs/<message_id>.json
    """
    try:
        out_dir = _triage_outputs_dir()
        out_dir.mkdir(parents=True, exist_ok=True)

        message_id = (message.message_id or "").strip()
        if not message_id:
            return
        safe_message_id = re.sub(r"[^A-Za-z0-9._-]+", "_", message_id)
        out_path = out_dir / f"{safe_message_id}.json"

        llm_payload: Dict[str, object] = {
            "backend": (llm_backend or "").strip() or None,
            "mode": (llm_cfg.mode if llm_cfg else "off"),
            "model": (llm_cfg.model if llm_cfg else None),
            "max_tokens": (int(llm_cfg.max_tokens) if llm_cfg else None),
            "timeout_s": (float(llm_cfg.timeout_s) if llm_cfg else None),
            "error": (llm_error or None),
            "result": None,
        }

        if llm_result is not None:
            try:
                if isinstance(llm_result, dict):
                    llm_payload["result"] = llm_result
                else:
                    llm_payload["result"] = {
                        "classification": getattr(llm_result, "classification", None),
                        "confidence": float(getattr(llm_result, "confidence", 0.0) or 0.0),
                        "summary_bullets": list(getattr(llm_result, "summary_bullets", []) or []),
                        "company_name_guess": getattr(llm_result, "company_name_guess", None),
                        "broker_name": getattr(llm_result, "broker_name", None),
                        "broker_email": getattr(llm_result, "broker_email", None),
                        "asking_price": getattr(llm_result, "asking_price", None),
                        "key_metrics": getattr(llm_result, "key_metrics", {}) or {},
                        "attachments": [
                            {
                                "filename": getattr(a, "filename", ""),
                                "guessed_type": getattr(a, "guessed_type", ""),
                                "notes": getattr(a, "notes", ""),
                            }
                            for a in (getattr(llm_result, "attachments", None) or [])
                        ],
                        "links": [
                            {
                                "url": safe_url(getattr(l, "url", "")),
                                "link_type": getattr(l, "link_type", ""),
                                "requires_auth": bool(getattr(l, "requires_auth", False)),
                            }
                            for l in (getattr(llm_result, "links", None) or [])
                        ],
                        "operator_recommendation": getattr(llm_result, "operator_recommendation", None),
                        "reasons": list(getattr(llm_result, "reasons", []) or []),
                        "latency_ms": int(getattr(llm_result, "latency_ms", 0) or 0),
                    }
            except Exception:
                llm_payload["result"] = None

        payload: Dict[str, object] = {
            "processed_at": utcnow_iso(),
            "message_id": message_id,
            "thread_id": (message.thread_id or "").strip() or None,
            "from": (message.sender or "").strip()[:200],
            "to": (message.to or "").strip()[:200],
            "date": (message.date or "").strip(),
            "subject": (message.subject or "").strip()[:200],
            "final_classification": (final_classification or "").strip(),
            "urgency": (urgency or "").strip(),
            "deterministic_reason": (deterministic_reason or "").strip()[:500],
            "deal_id": (deal_id or "").strip() or None,
            "quarantine_dir": str(quarantine_dir) if quarantine_dir else None,
            "triage_summary_path": str((quarantine_dir / "triage_summary.json")) if quarantine_dir else None,
            "llm": llm_payload,
        }

        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

        try:
            if os.geteuid() == 0:
                parent_stat = out_dir.stat()
                os.chown(str(out_path), parent_stat.st_uid, parent_stat.st_gid)
                os.chmod(str(out_path), 0o664)
        except Exception:
            pass
    except Exception:
        return


def sanitize_filename(name: str) -> str:
    base = (name or "").strip().split("/")[-1].split("\\")[-1]
    base = re.sub(r"[^A-Za-z0-9._ -]+", "_", base)
    return base[:200] or "attachment"


def is_safe_attachment(att: EmailAttachment, *, safe_exts: set[str], unsafe_exts: set[str], max_bytes: int) -> Tuple[bool, str]:
    ext = att.ext_lower
    if not ext:
        return False, "no_extension"
    if ext in unsafe_exts:
        return False, f"unsafe_ext:{ext}"
    if ext not in safe_exts:
        return False, f"not_allowlisted:{ext}"
    if att.size_bytes and att.size_bytes > max_bytes:
        return False, f"too_large:{att.size_bytes}"
    return True, "ok"


async def download_safe_attachments(
    *,
    gmail: GmailMcpClient,
    message: EmailMessage,
    quarantine_root: Path,
    safe_exts: set[str],
    unsafe_exts: set[str],
    max_attachment_bytes: int,
    dry_run: bool,
) -> Tuple[Optional[Path], bool, List[str]]:
    if not message.attachments:
        return None, False, []
    quarantine_dir = quarantine_root / message.message_id
    attempted: List[str] = []
    quarantine_flag = False

    for att in message.attachments:
        ok, reason = is_safe_attachment(att, safe_exts=safe_exts, unsafe_exts=unsafe_exts, max_bytes=max_attachment_bytes)
        attempted.append(f"{sanitize_filename(att.filename)}:{reason}")
        if not ok:
            quarantine_flag = True
            continue
        if dry_run:
            continue
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        fname = sanitize_filename(att.filename)
        await gmail.download_attachment(
            message_id=message.message_id,
            attachment_id=att.attachment_id,
            save_dir=str(quarantine_dir),
            filename=fname,
        )

    return (quarantine_dir if quarantine_dir.exists() else None), quarantine_flag, attempted


async def ensure_label_ids(gmail: GmailMcpClient, label_names: Sequence[str]) -> Dict[str, str]:
    ids: Dict[str, str] = {}
    for name in label_names:
        ids[name] = await gmail.get_or_create_label_id(name=name)
    return ids


def load_thread_mappings(registry_path: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Load thread_to_deal + thread_to_non_deal mappings from the DealRegistry JSON file.

    This intentionally avoids importing the full DealRegistry module (keeps the triage runner lightweight).
    """
    path = Path(registry_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        return {}, {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}, {}

    thread_to_deal = raw.get("thread_to_deal") if isinstance(raw, dict) else None
    thread_to_non_deal = raw.get("thread_to_non_deal") if isinstance(raw, dict) else None
    if not isinstance(thread_to_deal, dict):
        thread_to_deal = {}
    if not isinstance(thread_to_non_deal, dict):
        thread_to_non_deal = {}
    # Ensure values are strings (defensive)
    thread_to_deal_out = {str(k): str(v) for k, v in thread_to_deal.items() if str(k).strip() and str(v).strip()}
    thread_to_non_deal_out = {str(k): str(v) for k, v in thread_to_non_deal.items() if str(k).strip() and str(v).strip()}
    return thread_to_deal_out, thread_to_non_deal_out


async def process_one_message(
    *,
    gmail: GmailMcpClient,
    state_db: EmailTriageStateDB,
    sender_history_db: SenderHistoryDB,
    vendor_patterns: Iterable[VendorPattern],
    label_ids: Dict[str, str],
    message_id: str,
    cfg: RunnerConfig,
    actions: Optional[KineticActionsClient],
    thread_to_deal: Dict[str, str],
    thread_to_non_deal: Dict[str, str],
    llm_cfg: Optional[LlmTriageConfig] = None,
    thread_fetch_cfg: Optional[GmailThreadFetchConfig] = None,
    thread_message_id_cache: Optional[Dict[str, List[str]]] = None,
    log_path: Optional[Path] = None,
) -> None:
    started = time.monotonic()
    message = await gmail.read_email(message_id=message_id)

    prior = state_db.get(message_id)
    if prior and prior.status == "processed":
        return

    if not cfg.dry_run:
        state_db.mark_started(message_id=message.message_id, thread_id=message.thread_id)

    mapped_deal_id = (thread_to_deal or {}).get(message.thread_id)
    mapped_non_deal_reason = (thread_to_non_deal or {}).get(message.thread_id)

    # Deterministic thread routing (before classification):
    # - If a thread is already mapped to a deal, append materials automatically (no quarantine).
    # - If a thread is marked non-deal, auto-label and skip actions.
    if mapped_deal_id and not mapped_non_deal_reason:
        decision: TriageDecision = decide_actions_and_labels(email=message, vendor_patterns=vendor_patterns)

        quarantine_dir: Optional[Path] = cfg.quarantine_root / message.message_id
        quarantine_flag = False
        max_bytes = cfg.max_attachment_mb * 1024 * 1024

        if not cfg.dry_run:
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            (quarantine_dir / "email_body.txt").write_text(_sanitize_urls_in_text(message.body or ""), encoding="utf-8", errors="replace")
            (quarantine_dir / "email.json").write_text(
                json.dumps(
                    {
                        "message_id": message.message_id,
                        "thread_id": message.thread_id,
                        "from": message.sender,
                        "to": message.to,
                        "date": message.date,
                        "subject": message.subject,
                        "sender_email": decision.sender_email,
                        "company": decision.company,
                        "thread_mapped_deal_id": mapped_deal_id,
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

        downloaded_dir, quarantine_flag, _notes = await download_safe_attachments(
            gmail=gmail,
            message=message,
            quarantine_root=cfg.quarantine_root,
            safe_exts=cfg.safe_exts,
            unsafe_exts=cfg.unsafe_exts,
            max_attachment_bytes=max_bytes,
            dry_run=cfg.dry_run,
        )
        if downloaded_dir is not None:
            quarantine_dir = downloaded_dir

        labels_to_add = list(decision.labels_to_add)
        if "ZakOps/Deal" not in labels_to_add:
            labels_to_add.append("ZakOps/Deal")
        if quarantine_flag and "ZakOps/Quarantine" not in labels_to_add:
            labels_to_add.append("ZakOps/Quarantine")

        created_action_id: Optional[str] = None
        if (not cfg.dry_run) and cfg.enable_actions and actions:
            safe_links = [
                {
                    "type": l.type,
                    "url": safe_url(l.url),
                    "auth_required": bool(l.auth_required),
                    "vendor_hint": l.vendor_hint,
                }
                for l in decision.links
            ]
            attachments = [
                {
                    "filename": sanitize_filename(a.filename),
                    "mime_type": a.mime_type,
                    "size_bytes": int(a.size_bytes or 0),
                }
                for a in decision.attachments
            ]

            create = await asyncio.to_thread(
                actions.create_action,
                action_type="DEAL.APPEND_EMAIL_MATERIALS",
                title=f"Append email materials: {(message.subject or '').strip()[:80]}",
                summary=f"Follow-up email in mapped deal thread ({mapped_deal_id}).",
                deal_id=mapped_deal_id,
                capability_id="deal.append_email_materials.v1",
                risk_level="low",
                requires_human_review=False,
                idempotency_key=f"email_triage:{message.message_id}:append_email_materials",
                inputs={
                    "deal_id": mapped_deal_id,
                    "message_id": message.message_id,
                    "thread_id": message.thread_id,
                    "from": message.sender,
                    "to": message.to,
                    "date": message.date,
                    "subject": message.subject,
                    "company": decision.company,
                    "sender_email": decision.sender_email,
                    "links": safe_links,
                    "attachments": attachments,
                    "quarantine_dir": str(quarantine_dir) if quarantine_dir else None,
                },
            )
            created_action_id = create.action_id
            # Auto-approve + queue for execution (runner performs deterministic append-only work).
            try:
                await asyncio.to_thread(actions.approve_action, action_id=create.action_id, approved_by="email_triage_agent")
            except Exception:
                pass
            try:
                await asyncio.to_thread(actions.execute_action, action_id=create.action_id, requested_by="email_triage_agent")
            except Exception:
                pass

        # Apply labels and mark processed.
        if not cfg.dry_run:
            label_ids_to_add = [label_ids[n] for n in labels_to_add if n in label_ids]
            label_ids_to_add.append(label_ids["ZakOps/Processed"])
            await gmail.add_labels(message_id=message.message_id, label_ids=label_ids_to_add)
            if cfg.mark_as_read:
                await gmail.mark_as_read(message_id=message.message_id)

            body_hash = sha256_text(message.body)
            state_db.mark_processed(
                message_id=message.message_id,
                processed_at=utcnow_iso(),
                classification="DEAL_THREAD",
                urgency=decision.classification.urgency or "LOW",
                deal_id=mapped_deal_id,
                quarantine_dir=str(quarantine_dir) if quarantine_dir else None,
                body_hash=body_hash,
            )
            write_triage_output(
                message=message,
                final_classification="DEAL_THREAD",
                urgency=decision.classification.urgency or "LOW",
                deterministic_reason=decision.classification.reason or "",
                llm_backend=(os.getenv("EMAIL_TRIAGE_LLM_BACKEND", "llm_triage") or "llm_triage").strip().lower(),
                llm_cfg=llm_cfg,
                llm_result=None,
                llm_error=None,
                quarantine_dir=quarantine_dir,
                deal_id=mapped_deal_id,
            )
        _append_jsonl(
            log_path or _triage_log_path(),
            {
                "timestamp": utcnow_iso(),
                "event": "message_processed",
                "dry_run": bool(cfg.dry_run),
                "message_id": message.message_id,
                "thread_id": message.thread_id,
                "sender_email": decision.sender_email,
                "subject": (message.subject or "")[:200],
                "final_classification": "DEAL_THREAD",
                "urgency": decision.classification.urgency or "LOW",
                "eligible_for_llm": bool(decision.eligible_for_llm),
                "actions": {"created": bool(created_action_id), "action_id": created_action_id, "action_type": "DEAL.APPEND_EMAIL_MATERIALS"},
                "duration_ms": int((time.monotonic() - started) * 1000),
            },
        )
        return

    if mapped_non_deal_reason and not mapped_deal_id:
        if not cfg.dry_run:
            label_ids_to_add = [label_ids[n] for n in ("ZakOps/NonDeal", "ZakOps/Processed") if n in label_ids]
            await gmail.add_labels(message_id=message.message_id, label_ids=label_ids_to_add)
            if cfg.mark_as_read:
                await gmail.mark_as_read(message_id=message.message_id)

            body_hash = sha256_text(message.body)
            state_db.mark_processed(
                message_id=message.message_id,
                processed_at=utcnow_iso(),
                classification="NON_DEAL_THREAD",
                urgency="LOW",
                deal_id=None,
                quarantine_dir=None,
                body_hash=body_hash,
            )
            write_triage_output(
                message=message,
                final_classification="NON_DEAL_THREAD",
                urgency="LOW",
                deterministic_reason=mapped_non_deal_reason or "",
                llm_backend=(os.getenv("EMAIL_TRIAGE_LLM_BACKEND", "llm_triage") or "llm_triage").strip().lower(),
                llm_cfg=llm_cfg,
                llm_result=None,
                llm_error=None,
                quarantine_dir=None,
                deal_id=None,
            )
        _append_jsonl(
            log_path or _triage_log_path(),
            {
                "timestamp": utcnow_iso(),
                "event": "message_processed",
                "dry_run": bool(cfg.dry_run),
                "message_id": message.message_id,
                "thread_id": message.thread_id,
                "sender_email": _extract_sender_email(message.sender),
                "subject": (message.subject or "")[:200],
                "final_classification": "NON_DEAL_THREAD",
                "urgency": "LOW",
                "eligible_for_llm": False,
                "actions": {"created": False},
                "duration_ms": int((time.monotonic() - started) * 1000),
            },
        )
        return

    decision: TriageDecision = decide_actions_and_labels(email=message, vendor_patterns=vendor_patterns)

    ma_triage_v1: Optional[Dict[str, Any]] = None
    llm_error = None
    thread_fetch_error = None
    llm_backend = (os.getenv("EMAIL_TRIAGE_LLM_BACKEND", "llm_triage") or "llm_triage").strip().lower()

    # Agentic layer (local-first): use local vLLM/Qwen to produce operator-ready summary/extraction.
    # - assist: only invoked for deterministic DEAL_SIGNAL candidates; may downgrade obvious non-deals.
    # - full: invoked for all messages (classification driven by LLM, with deterministic guardrails).
    if llm_cfg and llm_cfg.mode in {"assist", "full"}:
        if llm_cfg.mode == "assist":
            should_call = decision.classification.classification == "DEAL_SIGNAL"
        else:
            should_call = bool(decision.eligible_for_llm)
    else:
        should_call = False

    if should_call:
        norm_current = normalize_email_body(message.body or "")
        prefilter_flags = {
            "deterministic_classification": decision.classification.classification,
            "deterministic_reason": decision.classification.reason,
            "eligible_for_llm": bool(decision.eligible_for_llm),
            "needs_reply": bool(decision.needs_reply),
            "needs_docs": bool(decision.needs_docs),
            "links_count": len(decision.links),
            "attachments_count": len(decision.attachments),
        }

        # "full" mode is thread-aware: the LLM reads the entire thread, not just the latest message.
        if llm_cfg and llm_cfg.mode == "full":
            thread_id = (message.thread_id or "").strip()
            message_ids_in_thread: List[str] = []
            if thread_id and thread_message_id_cache is not None and thread_id in thread_message_id_cache:
                message_ids_in_thread = list(thread_message_id_cache[thread_id])
            else:
                if thread_fetch_cfg is None:
                    try:
                        thread_fetch_cfg = load_thread_fetch_config()
                    except Exception:
                        thread_fetch_cfg = None
                if thread_fetch_cfg is None or not thread_id:
                    thread_fetch_error = "thread_fetch_unavailable"
                    message_ids_in_thread = [message.message_id]
                else:
                    mids, err = await asyncio.to_thread(get_thread_message_ids, cfg=thread_fetch_cfg, thread_id=thread_id)
                    if err:
                        thread_fetch_error = err
                        message_ids_in_thread = [message.message_id]
                    else:
                        message_ids_in_thread = mids or [message.message_id]
                        if thread_message_id_cache is not None and thread_id:
                            thread_message_id_cache[thread_id] = list(message_ids_in_thread)

            # Fallback: if thread fetch failed/unavailable, approximate the thread via Gmail search.
            # This is best-effort and may return a superset; we cap messages aggressively.
            if (not message_ids_in_thread) or message_ids_in_thread == [message.message_id]:
                sender_email = _extract_sender_email(message.sender) or (decision.sender_email or "")
                subject_norm = re.sub(r"^(re:|fw:|fwd:)\\s*", "", (message.subject or ""), flags=re.I).strip()
                subject_norm = subject_norm.replace('"', " ").replace("\n", " ").strip()
                subject_norm = subject_norm[:120]

                fallback_queries: List[str] = []
                if thread_id:
                    fallback_queries.append(f"threadid:{thread_id}")
                if sender_email and subject_norm:
                    fallback_queries.append(f'from:{sender_email} subject:\"{subject_norm}\" newer_than:730d')
                elif subject_norm:
                    fallback_queries.append(f'subject:\"{subject_norm}\" newer_than:365d')

                for q in fallback_queries:
                    try:
                        hits = await gmail.search_emails(query=q, max_results=25)
                    except Exception:
                        continue
                    mids = [h.message_id for h in hits if getattr(h, "message_id", "").strip()]
                    if not mids:
                        continue
                    if message.message_id and message.message_id not in mids:
                        mids.append(message.message_id)
                    # De-dupe while preserving order.
                    deduped: List[str] = []
                    seen = set()
                    for mid in mids:
                        mid_s = str(mid or "").strip()
                        if mid_s and mid_s not in seen:
                            seen.add(mid_s)
                            deduped.append(mid_s)
                    message_ids_in_thread = deduped
                    if thread_fetch_error:
                        thread_fetch_error = f"{thread_fetch_error};fallback_search_used"
                    else:
                        thread_fetch_error = "fallback_search_used"
                    break

            if message.message_id and message.message_id not in message_ids_in_thread:
                message_ids_in_thread.append(message.message_id)
            if len(message_ids_in_thread) > 25:
                message_ids_in_thread = message_ids_in_thread[-25:]

            thread_messages: List[Dict[str, Any]] = []
            for mid in message_ids_in_thread:
                if mid == message.message_id:
                    msg_obj = message
                else:
                    try:
                        msg_obj = await gmail.read_email(message_id=mid)
                    except Exception:
                        # If one message can't be fetched, keep going; the LLM can still classify from partial context.
                        continue
                norm = normalize_email_body(msg_obj.body or "")
                sort_ts = 0.0
                try:
                    from email.utils import parsedate_to_datetime

                    d = str(msg_obj.date or "").replace("(UTC)", "").strip()
                    dt = parsedate_to_datetime(d) if d else None
                    if dt is not None:
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        sort_ts = float(dt.timestamp())
                except Exception:
                    sort_ts = 0.0
                thread_messages.append(
                    {
                        "message_id": msg_obj.message_id,
                        "thread_id": msg_obj.thread_id,
                        "subject": msg_obj.subject,
                        "from": msg_obj.sender,
                        "to": msg_obj.to,
                        "date": msg_obj.date,
                        "body_text": norm.clean_text_no_urls,
                        "urls": list(norm.urls),
                        "attachments": [
                            {"filename": sanitize_filename(a.filename), "mime_type": a.mime_type, "size_bytes": int(a.size_bytes or 0)}
                            for a in (msg_obj.attachments or [])
                        ],
                        "_sort_ts": sort_ts,
                    }
                )

            thread_messages.sort(key=lambda m: float(m.get("_sort_ts") or 0.0))
            for m in thread_messages:
                m.pop("_sort_ts", None)

            ma_triage_v1, llm_error = await asyncio.to_thread(
                call_local_vllm_ma_triage_v1_thread,
                cfg=llm_cfg,
                thread_messages=thread_messages,
                prefilter_flags=prefilter_flags,
            )
        else:
            # assist-mode remains single-message for speed; use cleaned body (URLs removed) + extracted URL list.
            extracted_urls = [l.url for l in (decision.links or [])] or list(norm_current.urls)
            attachment_dicts = [
                {"filename": sanitize_filename(a.filename), "mime_type": a.mime_type, "size_bytes": int(a.size_bytes or 0)}
                for a in (decision.attachments or [])
            ]
            body_text_for_llm = norm_current.clean_text_no_urls
            # NOTE: legacy EMAIL_TRIAGE_LLM_BACKEND=langgraph is treated as an alias of the local vLLM path for v1.
            ma_triage_v1, llm_error = await asyncio.to_thread(
                call_local_vllm_ma_triage_v1_single,
                cfg=llm_cfg,
                subject=message.subject,
                sender=message.sender,
                received_at=message.date,
                body_text=body_text_for_llm,
                extracted_urls=extracted_urls,
                attachments=attachment_dicts,
                prefilter_flags=prefilter_flags,
            )

    final_classification = decision.classification.classification
    if isinstance(ma_triage_v1, dict) and llm_cfg:
        try:
            llm_confidence = float(ma_triage_v1.get("confidence") or 0.0)
        except Exception:
            llm_confidence = 0.0

        ma_relevant = bool(ma_triage_v1.get("ma_relevant", False))
        ma_intent = str(ma_triage_v1.get("ma_intent") or "").strip().upper()
        op_rec = ""
        summary = ma_triage_v1.get("summary")
        if isinstance(summary, dict):
            op_rec = str(summary.get("operator_recommendation") or "").strip().upper()

        if llm_cfg.mode == "full" and decision.eligible_for_llm:
            if (not ma_relevant) or ma_intent == "NON_DEAL" or op_rec == "REJECT":
                final_classification = "OPERATIONAL"
            elif op_rec == "NEEDS_REVIEW":
                final_classification = "UNCERTAIN"
            else:
                final_classification = "DEAL_SIGNAL"
        elif llm_cfg.mode == "assist":
            # Assist-mode rule: only allow LLM to DOWNGRADE a deal-signal into a non-deal category when confidence is high.
            if (
                final_classification == "DEAL_SIGNAL"
                and ((not ma_relevant) or ma_intent == "NON_DEAL" or op_rec == "REJECT")
                and llm_confidence >= 0.85
            ):
                final_classification = "OPERATIONAL"
            elif ma_relevant and op_rec == "NEEDS_REVIEW":
                final_classification = "UNCERTAIN"

    # Deterministic guardrails: denylisted senders and obvious transactional emails should never become deal-signals.
    if final_classification in {"DEAL_SIGNAL", "UNCERTAIN"} and not decision.eligible_for_llm:
        final_classification = decision.classification.classification

    quarantine_dir = None
    quarantine_flag = False
    max_bytes = cfg.max_attachment_mb * 1024 * 1024

    quarantine_candidate = final_classification in {"DEAL_SIGNAL", "UNCERTAIN"}

    if quarantine_candidate:
        # Always materialize a quarantine directory for deal-signal emails so we can persist
        # the source email content alongside any downloaded attachments.
        quarantine_dir = cfg.quarantine_root / message.message_id
        if not cfg.dry_run:
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            (quarantine_dir / "email_body.txt").write_text(_sanitize_urls_in_text(message.body or ""), encoding="utf-8", errors="replace")
            (quarantine_dir / "email.json").write_text(
                json.dumps(
                    {
                        "message_id": message.message_id,
                        "thread_id": message.thread_id,
                        "from": message.sender,
                        "to": message.to,
                        "date": message.date,
                        "subject": message.subject,
                        "sender_email": decision.sender_email,
                        "company": (
                            (
                                str(((ma_triage_v1.get("target_company") or {}) if isinstance(ma_triage_v1, dict) else {}).get("name") or "").strip()
                                if ma_triage_v1
                                else ""
                            )
                            or decision.company
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            # Persist LLM summary/extraction for Quarantine UX.
            summary_json_path = quarantine_dir / "triage_summary.json"
            summary_md_path = quarantine_dir / "triage_summary.md"
            triage_payload: Optional[Dict[str, Any]] = None
            if isinstance(ma_triage_v1, dict):
                triage_payload = dict(ma_triage_v1)
                if thread_fetch_error:
                    dbg = triage_payload.get("debug")
                    if not isinstance(dbg, dict):
                        dbg = {}
                        triage_payload["debug"] = dbg
                    warnings = dbg.get("warnings")
                    if not isinstance(warnings, list):
                        warnings = []
                        dbg["warnings"] = warnings
                    warnings.append(f"thread_fetch_error:{thread_fetch_error}")
            else:
                raw = {
                    "schema_version": MA_TRIAGE_V1_SCHEMA_VERSION,
                    "message_scope": "single",
                    "ma_relevant": final_classification in {"DEAL_SIGNAL", "UNCERTAIN"},
                    "routing": "QUARANTINE_REVIEW" if final_classification in {"DEAL_SIGNAL", "UNCERTAIN"} else "NON_DEAL",
                    "ma_intent": "UNCLEAR" if final_classification in {"DEAL_SIGNAL", "UNCERTAIN"} else "NON_DEAL",
                    "confidence": 0.0,
                    "target_company": {
                        "name": decision.company,
                        "name_confidence": 0.0,
                        "website": None,
                        "industry": None,
                        "location": None,
                    },
                    "actors": {"sender_role_guess": "UNKNOWN", "sender_org_guess": None},
                    "deal_signals": {
                        "stage_hint": "UNKNOWN",
                        "valuation_terms": {
                            "ask_price": None,
                            "revenue": None,
                            "ebitda": None,
                            "sde": None,
                            "multiple": None,
                            "currency": None,
                        },
                        "timeline_hint": None,
                    },
                    "materials": {
                        "attachments": [
                            {"filename": sanitize_filename(a.filename), "detected_type": "OTHER", "confidence": 0.0, "notes": None}
                            for a in (decision.attachments or [])
                        ],
                        "links": [
                            {
                                "url": safe_url(l.url),
                                "link_type": {
                                    "dataroom": "DATAROOM",
                                    "cim": "CIM",
                                    "teaser": "TEASER",
                                    "nda": "NDA",
                                    "financials": "FINANCIALS",
                                    "calendar": "CALENDAR",
                                    "docs": "DOCS",
                                }.get(l.type, "OTHER"),
                                "auth_required": "YES" if bool(l.auth_required) else "NO",
                                "notes": None,
                            }
                            for l in (decision.links or [])
                        ],
                    },
                    "summary": {
                        "bullets": [
                            f"Subject: {(message.subject or '').strip()[:180]}",
                            f"From: {(message.sender or '').strip()[:180]}",
                            f"Deterministic: {(decision.classification.reason or '').strip()[:240]}",
                        ],
                        "operator_recommendation": "NEEDS_REVIEW" if final_classification in {"DEAL_SIGNAL", "UNCERTAIN"} else "REJECT",
                        "why": (decision.classification.reason or "").strip()[:600],
                    },
                    "evidence": [
                        {"quote": f"Subject: {(message.subject or '').strip()[:200]}", "source": "SUBJECT", "reason": "Email subject", "weight": 0.5},
                    ],
                    "safety": {"no_secrets": True, "urls_sanitized": True},
                    "debug": {
                        "warnings": [f"llm_unavailable:{llm_error}" if llm_error else "llm_unavailable"],
                        "model": "deterministic",
                        "latency_ms": 0,
                    },
                }
                triage_payload = validate_ma_triage_v1(raw, model="deterministic", latency_ms=0, message_scope="single") or raw

            if triage_payload:
                summary_json_path.write_text(json.dumps(triage_payload, indent=2, sort_keys=True), encoding="utf-8")
                summary_md_path.write_text(ma_triage_v1_to_markdown(triage_payload), encoding="utf-8")

        downloaded_dir, quarantine_flag, _notes = await download_safe_attachments(
            gmail=gmail,
            message=message,
            quarantine_root=cfg.quarantine_root,
            safe_exts=cfg.safe_exts,
            unsafe_exts=cfg.unsafe_exts,
            max_attachment_bytes=max_bytes,
            dry_run=cfg.dry_run,
        )
        if downloaded_dir is not None:
            quarantine_dir = downloaded_dir
    else:
        # Do not download attachments for non-deal emails, and do not mark as quarantine
        # solely because attachments exist (receipts/invoices are common).
        quarantine_flag = False

    labels_to_add = list(decision.labels_to_add)
    # Normalize labels based on final classification.
    if final_classification == "DEAL_SIGNAL":
        labels_to_add = [l for l in labels_to_add if l not in {"ZakOps/NonDeal", "ZakOps/Spam-LowValue"}]
        if "ZakOps/Deal" not in labels_to_add:
            labels_to_add.insert(0, "ZakOps/Deal")
    elif final_classification == "UNCERTAIN":
        labels_to_add = [l for l in labels_to_add if l not in {"ZakOps/NonDeal", "ZakOps/Spam-LowValue", "ZakOps/Deal"}]
        if "ZakOps/Needs-Review" not in labels_to_add:
            labels_to_add.insert(0, "ZakOps/Needs-Review")
    elif final_classification == "SPAM":
        labels_to_add = ["ZakOps/Spam-LowValue"]
    else:
        labels_to_add = ["ZakOps/NonDeal"]
    if quarantine_flag and "ZakOps/Quarantine" not in labels_to_add:
        labels_to_add.append("ZakOps/Quarantine")

    deal_id = extract_deal_id(f"{message.subject}\n{message.body}") if final_classification == "DEAL_SIGNAL" else None

    # Emit approval-gated Kinetic Actions (never sends email; draft-only).
    created_review_action_id: Optional[str] = None
    if (
        (not cfg.dry_run)
        and cfg.enable_actions
        and actions
        and quarantine_candidate
    ):
        safe_links = [
            {
                "type": l.type,
                "url": safe_url(l.url),
                "auth_required": bool(l.auth_required),
                "vendor_hint": l.vendor_hint,
            }
            for l in decision.links
        ]
        guessed_type_by_filename: Dict[str, str] = {}
        if isinstance(ma_triage_v1, dict):
            materials = ma_triage_v1.get("materials")
            if isinstance(materials, dict) and isinstance(materials.get("attachments"), list):
                for item in materials["attachments"]:
                    if not isinstance(item, dict):
                        continue
                    fname = sanitize_filename(str(item.get("filename") or "").strip())
                    if not fname:
                        continue
                    detected = str(item.get("detected_type") or "OTHER").strip().upper()
                    guessed_type_by_filename[fname] = detected if detected in {"NDA", "CIM", "TEASER", "FINANCIALS"} else "OTHER"
        attachments = [
            {
                "filename": sanitize_filename(a.filename),
                "mime_type": a.mime_type,
                "size_bytes": int(a.size_bytes or 0),
                **({"guessed_type": guessed_type_by_filename.get(sanitize_filename(a.filename), "OTHER")} if guessed_type_by_filename else {}),
            }
            for a in decision.attachments
        ]

        summary_reason = decision.classification.reason
        if isinstance(ma_triage_v1, dict):
            summary = ma_triage_v1.get("summary")
            if isinstance(summary, dict):
                why = str(summary.get("why") or "").strip()
                if why:
                    summary_reason = why[:500]

        created = await asyncio.to_thread(
            actions.create_action,
            action_type="EMAIL_TRIAGE.REVIEW_EMAIL",
            title=f"Review inbound email ({final_classification}): {(message.subject or '').strip()[:80]}",
            summary=f"{decision.classification.urgency} urgency. {summary_reason}"[:500],
            deal_id=deal_id,
            capability_id="email_triage.review_email.v1",
            risk_level="medium",
            requires_human_review=True,
            idempotency_key=f"email_triage:{message.message_id}:review_email",
            inputs={
                "message_id": message.message_id,
                "thread_id": message.thread_id,
                "from": message.sender,
                "to": message.to,
                "date": message.date,
                "subject": message.subject,
                "company": (
                    (
                        str(((ma_triage_v1.get("target_company") or {}) if isinstance(ma_triage_v1, dict) else {}).get("name") or "").strip()
                        if ma_triage_v1
                        else ""
                    )
                    or decision.company
                ),
                "sender_email": decision.sender_email,
                "needs_reply": bool(decision.needs_reply),
                "needs_docs": bool(decision.needs_docs),
                "classification": final_classification,
                "confidence": (
                    float(ma_triage_v1.get("confidence"))
                    if isinstance(ma_triage_v1, dict) and ma_triage_v1.get("confidence") is not None
                    else None
                ),
                "sender_role_guess": (
                    (ma_triage_v1.get("actors") or {}).get("sender_role_guess")
                    if isinstance(ma_triage_v1, dict) and isinstance(ma_triage_v1.get("actors"), dict)
                    else None
                ),
                "materials_detected": (
                    {
                        "attachments": [
                            a.get("detected_type")
                            for a in ((ma_triage_v1.get("materials") or {}).get("attachments") or [])
                            if isinstance(a, dict)
                        ]
                        if isinstance((ma_triage_v1.get("materials") or {}).get("attachments"), list)
                        else [],
                        "links": [
                            l.get("link_type")
                            for l in ((ma_triage_v1.get("materials") or {}).get("links") or [])
                            if isinstance(l, dict)
                        ]
                        if isinstance((ma_triage_v1.get("materials") or {}).get("links"), list)
                        else [],
                    }
                    if isinstance(ma_triage_v1, dict)
                    else None
                ),
                "deal_likelihood_reason": (
                    (ma_triage_v1.get("summary") or {}).get("why")
                    if isinstance(ma_triage_v1, dict) and isinstance(ma_triage_v1.get("summary"), dict)
                    else None
                ),
                "evidence": (ma_triage_v1.get("evidence") if isinstance(ma_triage_v1, dict) else None),
                "urgency": decision.classification.urgency,
                "links": safe_links,
                "attachments": attachments,
                "quarantine_dir": str(quarantine_dir) if quarantine_dir else None,
                "triage_summary_path": str((quarantine_dir / "triage_summary.json")) if quarantine_dir else None,
            },
        )
        created_review_action_id = created.action_id

    # Apply labels only after we successfully completed processing (incl. downloads).
    if not cfg.dry_run:
        label_ids_to_add = [label_ids[n] for n in labels_to_add if n in label_ids]
        # Always add ZakOps/Processed on successful processing.
        label_ids_to_add.append(label_ids["ZakOps/Processed"])
        await gmail.add_labels(message_id=message.message_id, label_ids=label_ids_to_add)
        if cfg.mark_as_read:
            await gmail.mark_as_read(message_id=message.message_id)

    if not cfg.dry_run:
        body_hash = sha256_text(message.body)
        state_db.mark_processed(
            message_id=message.message_id,
            processed_at=utcnow_iso(),
            classification=final_classification,
            urgency=decision.classification.urgency,
            deal_id=deal_id,
            quarantine_dir=str(quarantine_dir) if quarantine_dir else None,
            body_hash=body_hash,
        )
        write_triage_output(
            message=message,
            final_classification=final_classification,
            urgency=decision.classification.urgency,
            deterministic_reason=decision.classification.reason or "",
            llm_backend=llm_backend,
            llm_cfg=llm_cfg,
            llm_result=ma_triage_v1,
            llm_error=llm_error,
            quarantine_dir=quarantine_dir,
            deal_id=deal_id,
        )
        # Record sender history for improved triage accuracy over time
        sender_role = None
        if isinstance(ma_triage_v1, dict):
            actors = ma_triage_v1.get("actors")
            if isinstance(actors, dict):
                sender_role = actors.get("sender_role_guess")
        sender_history_db.record_email(
            message_id=message.message_id,
            sender=message.sender,
            subject=message.subject or "",
            classification=final_classification,
            confidence=float(ma_triage_v1.get("confidence") or 0.0) if isinstance(ma_triage_v1, dict) else 0.0,
            sender_role_guess=sender_role,
            deal_id=deal_id,
            received_at=message.date,
        )

    _append_jsonl(
        log_path or _triage_log_path(),
        {
            "timestamp": utcnow_iso(),
            "event": "message_processed",
            "dry_run": bool(cfg.dry_run),
            "message_id": message.message_id,
            "thread_id": message.thread_id,
            "sender_email": decision.sender_email,
            "subject": (message.subject or "")[:200],
            "final_classification": final_classification,
            "urgency": decision.classification.urgency,
            "eligible_for_llm": bool(decision.eligible_for_llm),
            "llm": {
                "mode": (llm_cfg.mode if llm_cfg else "off"),
                "used": bool(ma_triage_v1),
                "model": (
                    ((ma_triage_v1.get("debug") or {}).get("model") if isinstance(ma_triage_v1, dict) else None)
                    or (llm_cfg.model if llm_cfg else None)
                ),
                "confidence": (
                    float(ma_triage_v1.get("confidence"))
                    if isinstance(ma_triage_v1, dict) and ma_triage_v1.get("confidence") is not None
                    else None
                ),
                "latency_ms": (
                    int((ma_triage_v1.get("debug") or {}).get("latency_ms") or 0)
                    if isinstance(ma_triage_v1, dict) and isinstance(ma_triage_v1.get("debug"), dict)
                    else None
                ),
                "error": (str(llm_error or "")[:200] if llm_error else None),
                "thread_fetch_error": thread_fetch_error,
            },
            "actions": {
                "created": bool(created_review_action_id),
                "action_id": created_review_action_id,
                "action_type": ("EMAIL_TRIAGE.REVIEW_EMAIL" if created_review_action_id else None),
            },
            "duration_ms": int((time.monotonic() - started) * 1000),
        },
    )


def load_config(args: argparse.Namespace) -> RunnerConfig:
    query = str(args.query or os.getenv("EMAIL_TRIAGE_QUERY") or DEFAULT_QUERY).strip()
    max_per_run = int(args.max_per_run or _int_env("EMAIL_TRIAGE_MAX_PER_RUN", DEFAULT_MAX_PER_RUN))
    quarantine_root = Path(os.getenv("EMAIL_TRIAGE_QUARANTINE_ROOT") or DEFAULT_QUARANTINE_ROOT)
    state_db_path = Path(os.getenv("EMAIL_TRIAGE_STATE_DB") or DEFAULT_STATE_DB)
    sender_history_db_path = Path(os.getenv("EMAIL_TRIAGE_SENDER_HISTORY_DB") or DEFAULT_SENDER_HISTORY_DB)
    deal_registry_path = Path(os.getenv("EMAIL_TRIAGE_DEAL_REGISTRY_PATH") or DEFAULT_DEAL_REGISTRY_PATH)
    vendor_patterns_path = Path(
        os.getenv("EMAIL_TRIAGE_VENDOR_PATTERNS_MD")
        or "/home/zaks/bookkeeping/configs/email_triage_agent/agent_config/memories/vendor_patterns.md"
    )
    dry_run = bool(args.dry_run) or _bool_env("EMAIL_TRIAGE_DRY_RUN", False)
    mark_as_read = bool(args.mark_as_read) or _bool_env("EMAIL_TRIAGE_MARK_AS_READ", False)
    max_attachment_mb = int(args.max_attachment_mb or _int_env("EMAIL_TRIAGE_MAX_ATTACHMENT_MB", 25))
    safe_exts = _csv_env_set("EMAIL_TRIAGE_SAFE_EXTS", SAFE_EXTS_DEFAULT)
    unsafe_exts = _csv_env_set("EMAIL_TRIAGE_UNSAFE_EXTS", UNSAFE_EXTS_DEFAULT)
    actions_base_url = str(os.getenv("EMAIL_TRIAGE_ACTIONS_BASE_URL") or DEFAULT_ACTIONS_BASE_URL).strip()
    enable_actions = _bool_env("EMAIL_TRIAGE_ENABLE_ACTIONS", True)

    return RunnerConfig(
        query=query,
        max_per_run=max(1, max_per_run),
        quarantine_root=quarantine_root,
        state_db_path=state_db_path,
        sender_history_db_path=sender_history_db_path,
        deal_registry_path=deal_registry_path,
        dry_run=dry_run,
        mark_as_read=mark_as_read,
        max_attachment_mb=max(1, max_attachment_mb),
        safe_exts=safe_exts,
        unsafe_exts=unsafe_exts,
        vendor_patterns_path=vendor_patterns_path,
        actions_base_url=actions_base_url,
        enable_actions=enable_actions,
    )


async def run_once(cfg: RunnerConfig) -> int:
    cfg.quarantine_root.mkdir(parents=True, exist_ok=True)
    state_db = EmailTriageStateDB(cfg.state_db_path)
    sender_history_db = SenderHistoryDB(cfg.sender_history_db_path)
    try:
        vendor_patterns = load_vendor_patterns_md(cfg.vendor_patterns_path)
        thread_to_deal, thread_to_non_deal = load_thread_mappings(cfg.deal_registry_path)
        llm_cfg = load_llm_config()
        try:
            thread_fetch_cfg: Optional[GmailThreadFetchConfig] = load_thread_fetch_config()
        except Exception:
            thread_fetch_cfg = None
        thread_message_id_cache: Dict[str, List[str]] = {}
        log_path = _triage_log_path()

        # Safe run header (no secrets): helps confirm local vLLM wiring for Email 3H.
        print(
            "email_triage_config "
            f"llm_mode={llm_cfg.mode} "
            f"llm_base_url={llm_cfg.base_url} "
            f"llm_model={llm_cfg.model} "
            f"llm_timeout_s={llm_cfg.timeout_s} "
            f"llm_max_body_chars={llm_cfg.max_body_chars} "
            f"query={cfg.query!r} "
            f"max_per_run={cfg.max_per_run} "
            f"dry_run={cfg.dry_run}"
        )
        _append_jsonl(
            log_path,
            {
                "timestamp": utcnow_iso(),
                "event": "run_start",
                "query": cfg.query,
                "max_per_run": cfg.max_per_run,
                "dry_run": bool(cfg.dry_run),
                "llm": {
                    "mode": llm_cfg.mode,
                    "base_url": llm_cfg.base_url,
                    "model": llm_cfg.model,
                    "timeout_s": llm_cfg.timeout_s,
                    "max_body_chars": llm_cfg.max_body_chars,
                    "max_tokens": llm_cfg.max_tokens,
                },
            },
        )

        # Always ensure core labels exist.
        label_names = [
            "ZakOps/Processed",
            "ZakOps/Deal",
            "ZakOps/Urgent",
            "ZakOps/Needs-Review",
            "ZakOps/Needs-Reply",
            "ZakOps/Needs-Docs",
            "ZakOps/Quarantine",
            "ZakOps/Spam-LowValue",
            "ZakOps/NonDeal",
            "ZakOps/NotADeal",
        ]

        async with McpStdioSession(command=gmail_mcp_command(), env=gmail_mcp_env()) as session:
            gmail = GmailMcpClient(session)
            label_ids = await ensure_label_ids(gmail, label_names)
            actions = KineticActionsClient(base_url=cfg.actions_base_url) if (cfg.enable_actions and not cfg.dry_run) else None

            hits = await gmail.search_emails(query=cfg.query, max_results=cfg.max_per_run)
            processed = 0
            skipped = 0
            failed = 0

            for hit in hits:
                row = state_db.get(hit.message_id)
                if row and row.status == "processed":
                    skipped += 1
                    continue
                try:
                    await process_one_message(
                        gmail=gmail,
                        state_db=state_db,
                        sender_history_db=sender_history_db,
                        vendor_patterns=vendor_patterns,
                        label_ids=label_ids,
                        message_id=hit.message_id,
                        cfg=cfg,
                        llm_cfg=llm_cfg,
                        actions=actions,
                        thread_to_deal=thread_to_deal,
                        thread_to_non_deal=thread_to_non_deal,
                        thread_fetch_cfg=thread_fetch_cfg,
                        thread_message_id_cache=thread_message_id_cache,
                        log_path=log_path,
                    )
                    processed += 1
                except Exception as e:
                    failed += 1
                    if not cfg.dry_run:
                        state_db.mark_failed(message_id=hit.message_id, error=str(e))
                    _append_jsonl(
                        log_path,
                        {
                            "timestamp": utcnow_iso(),
                            "event": "message_failed",
                            "message_id": hit.message_id,
                            "error": f"{type(e).__name__}:{str(e)[:200]}",
                        },
                    )

            print(f"email_triage_run completed processed={processed} skipped={skipped} failed={failed} query={cfg.query!r}")
            _append_jsonl(
                log_path,
                {
                    "timestamp": utcnow_iso(),
                    "event": "run_complete",
                    "processed": processed,
                    "skipped": skipped,
                    "failed": failed,
                    "query": cfg.query,
                },
            )

            # Persist run stats for /api/diagnostics
            try:
                import json
                from datetime import datetime, timezone
                dataroom_root = Path(os.getenv("DATAROOM_ROOT", "/home/zaks/DataRoom"))
                stats = {
                    "last_run_at": datetime.now(timezone.utc).isoformat(),
                    "processed": processed,
                    "skipped": skipped,
                    "failed": failed,
                    "query": cfg.query,
                    "success": failed == 0,
                }
                try:
                    (dataroom_root / ".triage_stats.json").write_text(json.dumps(stats, indent=2))
                except Exception:
                    fallback = (dataroom_root / ".deal-registry" / "triage_stats.json")
                    fallback.parent.mkdir(parents=True, exist_ok=True)
                    fallback.write_text(json.dumps(stats, indent=2))
            except Exception:
                pass  # Non-critical

            return 0 if failed == 0 else 2
    finally:
        state_db.close()
        sender_history_db.close()


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ZakOps Email Triage Runner (one-shot)")
    parser.add_argument("--query", default=None, help=f"Gmail search query (default: {DEFAULT_QUERY})")
    parser.add_argument("--max-per-run", type=int, default=None, help=f"Max messages per run (default: {DEFAULT_MAX_PER_RUN})")
    parser.add_argument("--dry-run", action="store_true", help="Do not write labels or download attachments")
    parser.add_argument("--mark-as-read", action="store_true", help="Mark processed emails as read")
    parser.add_argument("--max-attachment-mb", type=int, default=None, help="Skip attachments larger than this")
    args = parser.parse_args(argv)

    cfg = load_config(args)
    try:
        return asyncio.run(run_once(cfg))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

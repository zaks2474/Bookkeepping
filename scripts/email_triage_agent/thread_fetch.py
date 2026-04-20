from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


@dataclass(frozen=True)
class GmailThreadFetchConfig:
    credentials_path: Path
    oauth_keys_path: Path
    api_base: str
    timeout_s: float


def load_thread_fetch_config() -> GmailThreadFetchConfig:
    creds = (os.getenv("GMAIL_MCP_CREDENTIALS_PATH") or "").strip()
    if not creds:
        creds = str((Path.home() / ".gmail-mcp" / "credentials.json").resolve())

    keys = (os.getenv("GMAIL_OAUTH_KEYS_PATH") or "").strip()
    if not keys:
        keys = str((Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json").resolve())

    api_base = (os.getenv("GMAIL_API_BASE") or DEFAULT_GMAIL_API_BASE).strip().rstrip("/")
    timeout_s = float(os.getenv("GMAIL_API_TIMEOUT_S", "15") or "15")

    return GmailThreadFetchConfig(
        credentials_path=Path(creds).expanduser().resolve(),
        oauth_keys_path=Path(keys).expanduser().resolve(),
        api_base=api_base,
        timeout_s=timeout_s,
    )


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _now_ms() -> int:
    return int(time.time() * 1000)


def _should_refresh(expiry_date_ms: Optional[int]) -> bool:
    if not expiry_date_ms:
        return True
    # Refresh 60 seconds early.
    return _now_ms() >= int(expiry_date_ms) - 60_000


def _refresh_access_token(
    *,
    refresh_token: str,
    token_uri: str,
    client_id: str,
    client_secret: str,
    timeout_s: float,
) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """
    Returns (access_token, expiry_date_ms, error_reason). Never raises.
    """
    form = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")

    try:
        req = urllib.request.Request(token_uri, data=form, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=float(timeout_s)) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None, None, f"token_refresh_error:{type(e).__name__}"

    try:
        payload = json.loads(raw)
    except Exception:
        return None, None, "token_refresh_bad_json"

    token = str(payload.get("access_token") or "").strip()
    expires_in = payload.get("expires_in")
    if not token:
        return None, None, "token_refresh_missing_access_token"

    expiry_date_ms: Optional[int] = None
    try:
        expiry_date_ms = _now_ms() + int(expires_in) * 1000 if expires_in is not None else None
    except Exception:
        expiry_date_ms = None

    return token, expiry_date_ms, None


def _get_access_token(cfg: GmailThreadFetchConfig) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (access_token, error_reason). Never raises.

    This function reads local OAuth files managed by the Gmail MCP auth flow:
    - credentials.json: access_token, expiry_date, refresh_token
    - gcp-oauth.keys.json: client_id/client_secret/token_uri
    """
    if not cfg.credentials_path.exists():
        return None, "credentials_missing"
    if not cfg.oauth_keys_path.exists():
        return None, "oauth_keys_missing"

    try:
        creds = _load_json(cfg.credentials_path)
        keys = _load_json(cfg.oauth_keys_path)
    except Exception:
        return None, "oauth_files_unreadable"

    access_token = str(creds.get("access_token") or "").strip()
    refresh_token = str(creds.get("refresh_token") or "").strip()
    expiry_date_ms = creds.get("expiry_date")
    try:
        expiry_date_ms_int = int(expiry_date_ms) if expiry_date_ms is not None else None
    except Exception:
        expiry_date_ms_int = None

    installed = keys.get("installed") if isinstance(keys, dict) else None
    if not isinstance(installed, dict):
        return None, "oauth_keys_invalid"

    token_uri = str(installed.get("token_uri") or "").strip()
    client_id = str(installed.get("client_id") or "").strip()
    client_secret = str(installed.get("client_secret") or "").strip()

    if access_token and not _should_refresh(expiry_date_ms_int):
        return access_token, None

    if not (refresh_token and token_uri and client_id and client_secret):
        return None, "oauth_refresh_inputs_missing"

    new_token, new_expiry_ms, err = _refresh_access_token(
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        timeout_s=cfg.timeout_s,
    )
    if err or not new_token:
        return None, err or "oauth_refresh_failed"

    # NOTE: we intentionally do not write back to credentials.json here.
    # The Gmail MCP server manages token persistence; this fetcher uses refresh tokens
    # only for read-only API calls.
    _ = new_expiry_ms
    return new_token, None


def _gmail_get_json(
    *,
    url: str,
    access_token: str,
    timeout_s: float,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {access_token}")
        with urllib.request.urlopen(req, timeout=float(timeout_s)) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if int(getattr(e, "code", 0) or 0) == 401:
            return None, "gmail_unauthorized"
        return None, f"gmail_http_error:{getattr(e,'code',0)}"
    except Exception as e:
        return None, f"gmail_request_error:{type(e).__name__}"

    try:
        payload = json.loads(raw)
    except Exception:
        return None, "gmail_bad_json"

    if not isinstance(payload, dict):
        return None, "gmail_payload_not_object"
    return payload, None


def get_thread_message_ids(
    *,
    cfg: GmailThreadFetchConfig,
    thread_id: str,
) -> Tuple[List[str], Optional[str]]:
    """
    Returns (message_ids_in_thread, error_reason). Never raises.
    """
    tid = (thread_id or "").strip()
    if not tid:
        return [], "thread_id_empty"

    token, err = _get_access_token(cfg)
    if err or not token:
        return [], err or "access_token_unavailable"

    url = f"{cfg.api_base}/users/me/threads/{urllib.parse.quote(tid)}?format=minimal"
    payload, get_err = _gmail_get_json(url=url, access_token=token, timeout_s=cfg.timeout_s)
    if get_err == "gmail_unauthorized":
        # Refresh and retry once.
        token, err = _get_access_token(cfg)
        if err or not token:
            return [], err or "access_token_unavailable"
        payload, get_err = _gmail_get_json(url=url, access_token=token, timeout_s=cfg.timeout_s)

    if get_err or not payload:
        return [], get_err or "gmail_thread_fetch_failed"

    messages = payload.get("messages")
    if not isinstance(messages, list):
        return [], "gmail_thread_missing_messages"

    out: List[Tuple[int, str]] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        mid = str(m.get("id") or "").strip()
        internal_date = m.get("internalDate")
        try:
            ts = int(internal_date) if internal_date is not None else 0
        except Exception:
            ts = 0
        if mid:
            out.append((ts, mid))

    out.sort(key=lambda pair: pair[0])
    return [mid for _ts, mid in out], None


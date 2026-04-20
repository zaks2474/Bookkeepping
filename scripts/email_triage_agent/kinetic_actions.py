from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


_DEAL_ID_RE = re.compile(r"\b(DEAL-\d{4}-\d{3})\b", re.IGNORECASE)


def extract_deal_id(text: str) -> Optional[str]:
    m = _DEAL_ID_RE.search(text or "")
    return m.group(1).upper() if m else None


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


@dataclass(frozen=True)
class CreateActionResult:
    created_new: bool
    action_id: str
    status: str


class KineticActionsClient:
    def __init__(self, *, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _post_json(self, *, path: str, payload: Dict[str, Any], timeout_seconds: int) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url=f"{self.base_url}{path}",
            method="POST",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            raise RuntimeError(f"actions_api_http_error:{e.code}:{raw[:500]}")
        except Exception as e:
            raise RuntimeError(f"actions_api_error:{e}")

        try:
            data = json.loads(raw)
        except Exception:
            raise RuntimeError(f"actions_api_bad_json:{raw[:500]}")

        if not isinstance(data, dict):
            raise RuntimeError("actions_api_invalid_response")
        return data

    def create_action(
        self,
        *,
        action_type: str,
        title: str,
        summary: str = "",
        deal_id: Optional[str] = None,
        capability_id: Optional[str] = None,
        created_by: str = "email_triage_agent",
        source: str = "system",
        risk_level: str = "medium",
        requires_human_review: bool = True,
        idempotency_key: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 15,
    ) -> CreateActionResult:
        payload: Dict[str, Any] = {
            "action_type": action_type,
            "title": title,
            "summary": summary or "",
            "deal_id": deal_id,
            "capability_id": capability_id,
            "created_by": created_by,
            "source": source,
            "risk_level": risk_level,
            "requires_human_review": bool(requires_human_review),
            "idempotency_key": idempotency_key,
            "inputs": inputs or {},
        }
        data = self._post_json(path="/api/actions", payload=payload, timeout_seconds=timeout_seconds)

        action = data.get("action") if isinstance(data, dict) else None
        action_id = ""
        status = ""
        if isinstance(action, dict):
            action_id = str(action.get("action_id") or "")
            status = str(action.get("status") or "")
        created_new = bool(data.get("created_new")) if isinstance(data, dict) else False

        if not action_id:
            raise RuntimeError("actions_api_missing_action_id")
        return CreateActionResult(created_new=created_new, action_id=action_id, status=status)

    def approve_action(self, *, action_id: str, approved_by: str, timeout_seconds: int = 15) -> str:
        payload: Dict[str, Any] = {"approved_by": approved_by}
        data = self._post_json(path=f"/api/actions/{action_id}/approve", payload=payload, timeout_seconds=timeout_seconds)
        action = data.get("action") if isinstance(data, dict) else None
        if isinstance(action, dict):
            return str(action.get("status") or "")
        return ""

    def execute_action(self, *, action_id: str, requested_by: str, timeout_seconds: int = 15) -> str:
        payload: Dict[str, Any] = {"requested_by": requested_by}
        data = self._post_json(path=f"/api/actions/{action_id}/execute", payload=payload, timeout_seconds=timeout_seconds)
        action = data.get("action") if isinstance(data, dict) else None
        if isinstance(action, dict):
            return str(action.get("status") or "")
        return ""

    def cancel_action(self, *, action_id: str, cancelled_by: str, reason: str = "", timeout_seconds: int = 15) -> str:
        payload: Dict[str, Any] = {"cancelled_by": cancelled_by, "reason": reason}
        data = self._post_json(path=f"/api/actions/{action_id}/cancel", payload=payload, timeout_seconds=timeout_seconds)
        action = data.get("action") if isinstance(data, dict) else None
        if isinstance(action, dict):
            return str(action.get("status") or "")
        return ""

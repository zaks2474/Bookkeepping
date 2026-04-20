#!/usr/bin/env python3
"""
Append a standardized JSONL run record to the ZakOps Run Ledger.

Default ledger path (override with ZAKOPS_RUN_LEDGER_PATH or --ledger-path):
  /home/zaks/logs/run-ledger.jsonl

Design goals:
  - Append-only
  - Concurrency-safe (file lock)
  - No secrets: caller must pass sanitized fields only
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import pwd
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fcntl  # type: ignore
except Exception:  # pragma: no cover
    fcntl = None  # type: ignore


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_kv(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"Expected KEY=VALUE, got: {raw!r}")
    key, value = raw.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        raise ValueError(f"Empty KEY in: {raw!r}")
    return key, value


def _coerce_number(value: str) -> Any:
    try:
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            return int(value)
        return float(value)
    except Exception:
        return value


def _default_ledger_path() -> str:
    env_path = os.getenv("ZAKOPS_RUN_LEDGER_PATH", "").strip()
    if env_path:
        return env_path
    return "/home/zaks/logs/run-ledger.jsonl"


def _maybe_fix_owner(path: Path) -> None:
    """
    Ensure the ledger file stays writable by the primary operator user.

    This lab runs some cron jobs as root and others as `zaks`. If root creates the
    ledger file, it can become non-writable for `zaks`, breaking subsequent runs.
    """
    owner_name = os.getenv("ZAKOPS_LEDGER_OWNER", "zaks").strip() or "zaks"
    if os.geteuid() != 0:
        return
    try:
        pw = pwd.getpwnam(owner_name)
    except KeyError:
        return
    try:
        if path.exists():
            st = path.stat()
            if st.st_uid != pw.pw_uid or st.st_gid != pw.pw_gid:
                os.chown(path, pw.pw_uid, pw.pw_gid)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
            os.chown(path, pw.pw_uid, pw.pw_gid)
        os.chmod(path, 0o644)
    except Exception:
        # Best-effort only; never fail the calling automation due to ledger perms.
        return


def _write_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _maybe_fix_owner(path)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with open(path, "a", encoding="utf-8") as fh:
        if fcntl is not None:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            except Exception:
                pass
        fh.write(line + "\n")
        fh.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a JSONL run record to the ZakOps run ledger")
    parser.add_argument("--ledger-path", default="", help="Ledger JSONL path (default via ZAKOPS_RUN_LEDGER_PATH)")
    parser.add_argument("--run-id", required=True, help="Unique run identifier")
    parser.add_argument("--component", required=True, help="Component name (e.g., email_sync, rag_index)")
    parser.add_argument(
        "--status",
        required=True,
        choices=["success", "fail", "partial", "skipped"],
        help="Run status",
    )
    parser.add_argument("--started-at", required=True, help="Start timestamp (ISO8601)")
    parser.add_argument("--ended-at", required=True, help="End timestamp (ISO8601)")
    parser.add_argument("--artifact", action="append", default=[], help="Artifact path (repeatable)")
    parser.add_argument("--error", action="append", default=[], help="Error label/message (repeatable)")
    parser.add_argument("--metric", action="append", default=[], help="Metric KEY=VALUE (repeatable)")
    parser.add_argument("--correlation", action="append", default=[], help="Correlation KEY=VALUE (repeatable)")
    args = parser.parse_args()

    ledger_path = (args.ledger_path or _default_ledger_path()).strip()
    if not ledger_path:
        print("No ledger path resolved", file=sys.stderr)
        return 2

    metrics: dict[str, Any] = {}
    for item in args.metric:
        key, value = _parse_kv(item)
        metrics[key] = _coerce_number(value)

    correlation: dict[str, str] = {}
    for item in args.correlation:
        key, value = _parse_kv(item)
        correlation[key] = value

    record: dict[str, Any] = {
        "run_id": args.run_id,
        "component": args.component,
        "started_at": args.started_at,
        "ended_at": args.ended_at,
        "status": args.status,
        "artifacts": list(args.artifact),
        "metrics": metrics,
        "errors": list(args.error),
        "correlation": correlation,
        "written_at": _now_utc_iso(),
        "host": platform.node(),
        "pid": os.getpid(),
    }

    try:
        _write_jsonl(Path(ledger_path), record)
    except Exception as exc:
        print(f"Failed to write ledger record: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

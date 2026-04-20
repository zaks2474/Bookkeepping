#!/usr/bin/env python3
"""
ZakOps Ops Digest

Generates a daily (or rolling) operational digest from the run ledger.

Default inputs:
  - Ledger: /home/zaks/logs/run-ledger.jsonl
  - Output: /home/zaks/DataRoom/06-KNOWLEDGE-BASE/ops-daily/YYYY-MM-DD.md

Safety:
  - Prints only metadata already present in the run ledger.
  - Does not read raw deal documents.
"""

from __future__ import annotations

import argparse
import json
import os
import pwd
import statistics
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


DEFAULT_LEDGER = "/home/zaks/logs/run-ledger.jsonl"
DEFAULT_OUT_DIR = "/home/zaks/DataRoom/06-KNOWLEDGE-BASE/ops-daily"
DEFAULT_LEDGER_WRITER = "/home/zaks/bookkeeping/scripts/run_ledger.py"


def _parse_iso(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _safe_int(value: Any) -> int | None:
    try:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    except Exception:
        return None
    return None


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    component: str
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    errors: list[str]
    metrics: dict[str, Any]
    artifacts: list[str]

    @property
    def duration_seconds(self) -> int | None:
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            return max(0, int(delta.total_seconds()))
        val = self.metrics.get("duration_seconds")
        return _safe_int(val)


def iter_ledger(path: Path) -> Iterable[RunRecord]:
    if not path.exists():
        return []

    def _iter() -> Iterable[RunRecord]:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue

                yield RunRecord(
                    run_id=str(rec.get("run_id", "")),
                    component=str(rec.get("component", "")),
                    status=str(rec.get("status", "")),
                    started_at=_parse_iso(str(rec.get("started_at", ""))),
                    ended_at=_parse_iso(str(rec.get("ended_at", ""))),
                    errors=list(rec.get("errors", []) or []),
                    metrics=dict(rec.get("metrics", {}) or {}),
                    artifacts=list(rec.get("artifacts", []) or []),
                )

    return _iter()


def format_digest(records: list[RunRecord], *, tz_name: str) -> str:
    tz = ZoneInfo(tz_name) if ZoneInfo else timezone.utc
    now = _now_utc().astimezone(tz)

    by_component: dict[str, list[RunRecord]] = {}
    for r in records:
        by_component.setdefault(r.component or "unknown", []).append(r)

    lines: list[str] = []
    lines.append("# Ops Digest")
    lines.append("")
    lines.append(f"- Generated: `{now.isoformat(timespec='seconds')}` ({tz_name})")
    lines.append(f"- Runs analyzed: `{len(records)}`")
    lines.append("")

    if not records:
        lines.append("No run-ledger records found for the selected time window.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Summary (by component)")
    lines.append("")
    lines.append("| Component | Runs | Success | Partial | Skipped | Fail | P95 Duration (s) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for component in sorted(by_component.keys()):
        runs = by_component[component]
        counts = {"success": 0, "partial": 0, "skipped": 0, "fail": 0}
        durations: list[int] = []
        for r in runs:
            if r.status in counts:
                counts[r.status] += 1
            else:
                counts["fail"] += 1
            d = r.duration_seconds
            if d is not None:
                durations.append(d)
        p95 = ""
        if durations:
            durations_sorted = sorted(durations)
            idx = int(round(0.95 * (len(durations_sorted) - 1)))
            p95 = str(durations_sorted[idx])

        lines.append(
            f"| `{component}` | {len(runs)} | {counts['success']} | {counts['partial']} | {counts['skipped']} | {counts['fail']} | {p95} |"
        )

    lines.append("")

    failures = [r for r in records if r.status not in {"success", "skipped"}]
    if failures:
        lines.append("## Recent Issues")
        lines.append("")
        # newest first by ended_at/written_at proxy
        failures_sorted = sorted(
            failures,
            key=lambda r: (r.ended_at or r.started_at or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )[:15]
        for r in failures_sorted:
            ended = (r.ended_at or r.started_at)
            ended_s = ended.astimezone(tz).isoformat(timespec="seconds") if ended else "unknown"
            dur = r.duration_seconds
            dur_s = f"{dur}s" if dur is not None else "n/a"
            err = ", ".join(r.errors[:5]) if r.errors else "n/a"
            lines.append(f"- `{ended_s}` `{r.component}` `{r.status}` run_id=`{r.run_id}` duration=`{dur_s}` errors=`{err}`")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- This digest is generated from the run ledger (`/home/zaks/logs/run-ledger.jsonl`).")
    lines.append("- If a job is missing here, confirm it writes to the ledger and that the ledger is writable by `zaks`.")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an ops digest from the run ledger")
    parser.add_argument("--ledger", default=os.getenv("ZAKOPS_RUN_LEDGER_PATH", DEFAULT_LEDGER))
    parser.add_argument("--since-hours", type=int, default=24, help="Lookback window in hours (default: 24)")
    parser.add_argument("--tz", default="America/Chicago", help="Timezone for display (default: America/Chicago)")
    parser.add_argument("--out", default="", help="Write digest to this file (default: ops-daily/YYYY-MM-DD.md)")
    parser.add_argument("--no-ledger-record", action="store_true", help="Do not append a run-ledger record")
    args = parser.parse_args()

    started_at = _now_utc()
    start_epoch = time.time()

    ledger_path = Path(args.ledger)
    now = _now_utc()
    since = now - timedelta(hours=max(1, args.since_hours))

    records: list[RunRecord] = []
    for rec in iter_ledger(ledger_path):
        ts = rec.started_at or rec.ended_at
        if ts is None:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if ts >= since:
            records.append(rec)

    digest = format_digest(records, tz_name=args.tz)

    if args.out:
        out_path = Path(args.out)
    else:
        tz = ZoneInfo(args.tz) if ZoneInfo else timezone.utc
        now_local = now.astimezone(tz)
        out_dir = Path(DEFAULT_OUT_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{now_local.strftime('%Y-%m-%d')}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(digest, encoding="utf-8")

    # Best-effort: keep DataRoom outputs owned by `zaks` even when run as root.
    if os.geteuid() == 0:
        try:
            pw = pwd.getpwnam("zaks")
            os.chown(out_path.parent, pw.pw_uid, pw.pw_gid)
            os.chown(out_path, pw.pw_uid, pw.pw_gid)
        except Exception:
            pass

    print(str(out_path))

    if not args.no_ledger_record:
        try:
            writer = os.getenv("ZAKOPS_LEDGER_WRITER", DEFAULT_LEDGER_WRITER).strip() or DEFAULT_LEDGER_WRITER
            if os.path.exists(writer):
                ended_at = _now_utc()
                duration_seconds = max(0, int(time.time() - start_epoch))
                run_ts = ended_at.strftime("%Y%m%dT%H%M%SZ")
                run_id = f"{run_ts}_ops_digest_{os.getpid()}"

                cmd = [
                    "python3",
                    writer,
                    "--ledger-path",
                    str(ledger_path),
                    "--component",
                    "ops_digest",
                    "--run-id",
                    run_id,
                    "--status",
                    "success",
                    "--started-at",
                    started_at.isoformat().replace("+00:00", "Z"),
                    "--ended-at",
                    ended_at.isoformat().replace("+00:00", "Z"),
                    "--artifact",
                    str(out_path),
                    "--metric",
                    f"since_hours={int(args.since_hours)}",
                    "--metric",
                    f"records_analyzed={len(records)}",
                    "--metric",
                    f"duration_seconds={duration_seconds}",
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

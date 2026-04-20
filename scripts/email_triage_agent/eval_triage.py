from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _dataroom_root() -> Path:
    return Path(os.getenv("DATAROOM_ROOT", "/home/zaks/DataRoom")).resolve()


def _feedback_path() -> Path:
    return _dataroom_root() / ".deal-registry" / "triage_feedback.jsonl"


def _parse_ts(ts: str) -> Optional[datetime]:
    t = (ts or "").strip()
    if not t:
        return None
    try:
        if t.endswith("Z"):
            return datetime.fromisoformat(t.replace("Z", "+00:00"))
        return datetime.fromisoformat(t)
    except Exception:
        return None


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []
    out: List[Dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    except Exception:
        return []
    return out


def _count_recent(entries: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    for e in entries:
        ts = _parse_ts(str(e.get("timestamp") or ""))
        if ts and ts >= cutoff:
            out.append(e)
    return out


def _tabulate(entries: List[Dict[str, Any]]) -> Tuple[Counter, Counter, Counter]:
    by_decision: Counter = Counter()
    by_class: Counter = Counter()
    by_pair: Counter = Counter()

    for e in entries:
        decision = str(e.get("decision") or "unknown").strip().lower() or "unknown"
        classification = str(e.get("classification") or "unknown").strip().upper() or "unknown"
        by_decision[decision] += 1
        by_class[classification] += 1
        by_pair[(decision, classification)] += 1
    return by_decision, by_class, by_pair


def _binary_metrics(entries: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Compute binary classification metrics from operator feedback entries.

    Mapping:
    - actual positive: decision == "approve"
    - actual negative: decision == "reject"
    - predicted positive: classification == "DEAL_SIGNAL"

    Notes:
    - This is only computed on rows where decision is approve/reject.
    - Dataset reflects operator-reviewed items, not the full inbox.
    """
    tp = fp = fn = tn = 0
    used = 0
    for e in entries:
        decision = str(e.get("decision") or "").strip().lower()
        if decision not in {"approve", "reject"}:
            continue
        classification = str(e.get("classification") or "").strip().upper()
        actual_pos = decision == "approve"
        pred_pos = classification == "DEAL_SIGNAL"
        used += 1
        if actual_pos and pred_pos:
            tp += 1
        elif (not actual_pos) and pred_pos:
            fp += 1
        elif actual_pos and (not pred_pos):
            fn += 1
        else:
            tn += 1

    precision = (tp / (tp + fp)) if (tp + fp) else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    # Operator-friendly "false positive rate": of predicted deal-signals, what share were rejected?
    false_positive_rate = (fp / (tp + fp)) if (tp + fp) else 0.0
    false_negative_rate = (fn / (tp + fn)) if (tp + fn) else 0.0

    # Classical FPR for completeness (FP / (FP+TN)).
    fpr = (fp / (fp + tn)) if (fp + tn) else 0.0

    return {
        "rows_used": float(used),
        "tp": float(tp),
        "fp": float(fp),
        "fn": float(fn),
        "tn": float(tn),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "false_positive_rate": float(false_positive_rate),
        "false_negative_rate": float(false_negative_rate),
        "false_positive_rate_fpr": float(fpr),
    }


def _render_counter(c: Counter) -> str:
    if not c:
        return "- (none)\n"
    lines = []
    for k, v in c.most_common():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines) + "\n"


def generate_report(entries: List[Dict[str, Any]]) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    recent_7d = _count_recent(entries, 7)
    recent_30d = _count_recent(entries, 30)

    by_decision, by_class, by_pair = _tabulate(entries)
    by_decision_7, _, _ = _tabulate(recent_7d)
    by_decision_30, _, _ = _tabulate(recent_30d)

    metrics_all = _binary_metrics(entries)
    metrics_7d = _binary_metrics(recent_7d)
    metrics_30d = _binary_metrics(recent_30d)

    lines = [
        "# EMAIL TRIAGE EVAL REPORT",
        "",
        f"Generated: {now}",
        "",
        "This report is generated from the operator feedback dataset:",
        f"- `{_feedback_path()}`",
        "",
        "## Totals",
        f"- Total decisions: {len(entries)}",
        f"- rows_used (approve/reject only): {int(metrics_all['rows_used'])}",
        "",
        "## Metrics (operator feedback)",
        f"- precision: {metrics_all['precision']:.1%}",
        f"- recall: {metrics_all['recall']:.1%}",
        f"- f1: {metrics_all['f1']:.1%}",
        f"- false_positive_rate: {metrics_all['false_positive_rate']:.1%}",
        f"- false_negative_rate: {metrics_all['false_negative_rate']:.1%}",
        "",
        "## Metrics (last 7 days)",
        f"- precision: {metrics_7d['precision']:.1%}",
        f"- recall: {metrics_7d['recall']:.1%}",
        f"- f1: {metrics_7d['f1']:.1%}",
        f"- false_positive_rate: {metrics_7d['false_positive_rate']:.1%}",
        "",
        "## Metrics (last 30 days)",
        f"- precision: {metrics_30d['precision']:.1%}",
        f"- recall: {metrics_30d['recall']:.1%}",
        f"- f1: {metrics_30d['f1']:.1%}",
        f"- false_positive_rate: {metrics_30d['false_positive_rate']:.1%}",
        "",
        "## Decisions (all-time)",
        _render_counter(by_decision).rstrip(),
        "",
        "## Decisions (last 7 days)",
        _render_counter(by_decision_7).rstrip(),
        "",
        "## Decisions (last 30 days)",
        _render_counter(by_decision_30).rstrip(),
        "",
        "## Classifications (all-time)",
        _render_counter(by_class).rstrip(),
        "",
        "## Decision × Classification (all-time)",
    ]
    # Render pair counts (sorted).
    if by_pair:
        pairs = sorted(by_pair.items(), key=lambda kv: (-kv[1], str(kv[0])))
        for (decision, classification), count in pairs[:50]:
            lines.append(f"- {decision} × {classification}: {count}")
    else:
        lines.append("- (none)")

    lines.extend(
        [
            "",
            "## Notes",
            "- Dataset is intentionally minimal (no raw email bodies).",
            "- Metrics are computed only on approve/reject rows (operator-reviewed subset).",
            "- `false_positive_rate` is operator-friendly (FP / (TP+FP)); see `false_positive_rate_fpr` in code for classical FPR.",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an email triage evaluation report from triage_feedback.jsonl")
    parser.add_argument("--days", type=int, default=0, help="If set, only include entries from the last N days.")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[2] / "docs" / "EMAIL_TRIAGE_EVAL_REPORT.md"),
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    feedback_path = _feedback_path()
    entries = list(_iter_jsonl(feedback_path))
    if int(args.days or 0) > 0:
        entries = _count_recent(entries, int(args.days))

    report = generate_report(entries)
    out_path = Path(str(args.output)).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

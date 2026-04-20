from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from email_triage_agent.gmail_mcp import EmailAttachment, EmailMessage, GmailMcpClient, gmail_mcp_command, gmail_mcp_env
from email_triage_agent.llm_triage import call_local_vllm_ma_triage_v1_thread, load_llm_config
from email_triage_agent.mcp_stdio import McpStdioSession
from email_triage_agent.thread_fetch import get_thread_message_ids, load_thread_fetch_config
from email_triage_agent.triage_logic import decide_actions_and_labels, normalize_email_body


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dataroom_root() -> Path:
    return Path(os.getenv("DATAROOM_ROOT", "/home/zaks/DataRoom")).resolve()


def _feedback_path() -> Path:
    return _dataroom_root() / ".deal-registry" / "triage_feedback.jsonl"


def _default_samples_dir() -> Path:
    return Path("/home/zaks/bookkeeping/evals/email_3h_samples").resolve()


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []
    out: List[Dict[str, Any]] = []
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
    return out


def _select_recent_feedback(*, limit: int, decisions: Optional[set[str]] = None) -> List[Dict[str, Any]]:
    decisions = {d.strip().lower() for d in (decisions or set()) if d.strip()}
    entries = list(_iter_jsonl(_feedback_path()))
    entries.reverse()  # newest first (file is append-only)
    out: List[Dict[str, Any]] = []
    for e in entries:
        dec = str(e.get("decision") or "").strip().lower()
        if decisions and dec not in decisions:
            continue
        if not str(e.get("message_id") or "").strip():
            continue
        out.append(e)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _safe_filename(text: str) -> str:
    import re

    s = (text or "").strip()
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s[:120] or "sample"


async def export_samples(*, out_dir: Path, limit: int = 20) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    feedback = _select_recent_feedback(limit=limit, decisions={"approve", "reject"})
    if not feedback:
        print(f"No feedback entries found at: {_feedback_path()}")
        return 2

    thread_fetch_cfg = load_thread_fetch_config()
    exported = 0

    async with McpStdioSession(command=gmail_mcp_command(), env=gmail_mcp_env()) as session:
        gmail = GmailMcpClient(session)

        for entry in feedback:
            message_id = str(entry.get("message_id") or "").strip()
            thread_id = str(entry.get("thread_id") or "").strip()
            if not message_id:
                continue

            thread_err: Optional[str] = None
            if thread_id:
                mids, err = get_thread_message_ids(cfg=thread_fetch_cfg, thread_id=thread_id)
                thread_err = err
                message_ids = mids or [message_id]
            else:
                message_ids = [message_id]

            thread_messages: List[Dict[str, Any]] = []
            for mid in message_ids:
                try:
                    msg = await gmail.read_email(message_id=mid)
                except Exception:
                    continue
                norm = normalize_email_body(msg.body or "")
                thread_messages.append(
                    {
                        "message_id": msg.message_id,
                        "thread_id": msg.thread_id,
                        "subject": msg.subject,
                        "from": msg.sender,
                        "to": msg.to,
                        "date": msg.date,
                        "body_text": norm.clean_text_no_urls,
                        "urls": list(norm.urls),
                        "attachments": [
                            {"filename": a.filename, "mime_type": a.mime_type, "size_bytes": int(a.size_bytes or 0)}
                            for a in (msg.attachments or [])
                        ],
                    }
                )

            payload = {
                "exported_at": _now_iso(),
                "source": {
                    "triage_feedback": {
                        "timestamp": entry.get("timestamp"),
                        "decision": entry.get("decision"),
                        "classification": entry.get("classification"),
                        "confidence": entry.get("confidence"),
                        "message_id": message_id,
                        "thread_id": thread_id or None,
                        "action_id": entry.get("action_id"),
                        "deal_id": entry.get("deal_id"),
                    },
                    "thread_fetch_error": thread_err,
                },
                "thread_messages": thread_messages,
            }

            ts = _safe_filename(str(entry.get("timestamp") or ""))
            fname = f"{ts}_{_safe_filename(message_id)}.json"
            (out_dir / fname).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            exported += 1

    print(f"Exported {exported} samples to: {out_dir}")
    return 0


def _decision_to_label(decision: str) -> Optional[bool]:
    d = (decision or "").strip().lower()
    if d == "approve":
        return True
    if d == "reject":
        return False
    return None


def _metrics(tp: int, fp: int, fn: int, tn: int) -> Dict[str, float]:
    precision = (tp / (tp + fp)) if (tp + fp) else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"tp": float(tp), "fp": float(fp), "fn": float(fn), "tn": float(tn), "precision": float(precision), "recall": float(recall), "f1": float(f1)}


def _evaluate_samples(*, samples_dir: Path, with_llm: bool) -> Dict[str, Any]:
    paths = sorted(samples_dir.glob("*.json"))
    if not paths:
        return {"error": f"no_samples:{samples_dir}"}

    llm_cfg = load_llm_config()
    tp = fp = fn = tn = 0
    tp_llm = fp_llm = fn_llm = tn_llm = 0
    used = 0
    examples: Dict[str, List[Dict[str, str]]] = {
        "det_fp": [],
        "det_fn": [],
        "llm_fp": [],
        "llm_fn": [],
    }

    for path in paths:
        sample = json.loads(path.read_text(encoding="utf-8"))
        source = sample.get("source", {}).get("triage_feedback", {}) if isinstance(sample.get("source"), dict) else {}
        actual = _decision_to_label(str(source.get("decision") or ""))
        if actual is None:
            continue

        msgs = sample.get("thread_messages")
        if not isinstance(msgs, list) or not msgs:
            continue
        last = msgs[-1] if isinstance(msgs[-1], dict) else None
        if not isinstance(last, dict):
            continue

        # Deterministic-only baseline uses the last message.
        attachments = []
        for a in last.get("attachments") if isinstance(last.get("attachments"), list) else []:
            if not isinstance(a, dict):
                continue
            attachments.append(
                EmailAttachment(
                    attachment_id="",
                    filename=str(a.get("filename") or ""),
                    mime_type=str(a.get("mime_type") or ""),
                    size_bytes=int(a.get("size_bytes") or 0),
                )
            )

        msg_obj = EmailMessage(
            message_id=str(last.get("message_id") or ""),
            thread_id=str(last.get("thread_id") or ""),
            subject=str(last.get("subject") or ""),
            sender=str(last.get("from") or ""),
            to=str(last.get("to") or ""),
            date=str(last.get("date") or ""),
            body=str(last.get("body_text") or ""),
            attachments=attachments,
        )
        decision = decide_actions_and_labels(email=msg_obj, vendor_patterns=[])
        pred_det = decision.classification.classification == "DEAL_SIGNAL"

        used += 1
        if actual and pred_det:
            tp += 1
        elif (not actual) and pred_det:
            fp += 1
            examples["det_fp"].append({"message_id": msg_obj.message_id, "thread_id": msg_obj.thread_id, "subject": msg_obj.subject})
        elif actual and (not pred_det):
            fn += 1
            examples["det_fn"].append({"message_id": msg_obj.message_id, "thread_id": msg_obj.thread_id, "subject": msg_obj.subject})
        else:
            tn += 1

        if with_llm:
            # LLM full-thread (local vLLM) using the sample thread payload.
            llm_res, llm_err = call_local_vllm_ma_triage_v1_thread(cfg=llm_cfg, thread_messages=msgs)
            pred_llm = bool(
                llm_res
                and bool(llm_res.get("ma_relevant", False))
                and str(llm_res.get("routing") or "").strip().upper() != "NON_DEAL"
            )
            if llm_err:
                pred_llm = False  # conservative
            if actual and pred_llm:
                tp_llm += 1
            elif (not actual) and pred_llm:
                fp_llm += 1
                examples["llm_fp"].append({"message_id": msg_obj.message_id, "thread_id": msg_obj.thread_id, "subject": msg_obj.subject})
            elif actual and (not pred_llm):
                fn_llm += 1
                examples["llm_fn"].append({"message_id": msg_obj.message_id, "thread_id": msg_obj.thread_id, "subject": msg_obj.subject})
            else:
                tn_llm += 1

    return {
        "generated_at": _now_iso(),
        "samples_dir": str(samples_dir),
        "rows_used": int(used),
        "deterministic": _metrics(tp, fp, fn, tn),
        "llm_full_thread": (_metrics(tp_llm, fp_llm, fn_llm, tn_llm) if with_llm else None),
        "examples": examples,
    }


def _render_report_markdown(result: Dict[str, Any]) -> str:
    if "error" in result:
        return f"# EMAIL 3H EVAL REPORT\n\nError: {result['error']}\n"

    det = result.get("deterministic") if isinstance(result.get("deterministic"), dict) else {}
    llm = result.get("llm_full_thread") if isinstance(result.get("llm_full_thread"), dict) else None
    examples = result.get("examples") if isinstance(result.get("examples"), dict) else {}

    lines = [
        "# EMAIL 3H EVAL REPORT",
        "",
        f"Generated: {result.get('generated_at')}",
        f"Samples: `{result.get('samples_dir')}`",
        "",
        "## Deterministic-only",
        f"- rows_used: {result.get('rows_used')}",
        f"- precision: {float(det.get('precision') or 0.0):.1%}",
        f"- recall: {float(det.get('recall') or 0.0):.1%}",
        f"- f1: {float(det.get('f1') or 0.0):.1%}",
        f"- tp/fp/fn/tn: {int(det.get('tp') or 0)}/{int(det.get('fp') or 0)}/{int(det.get('fn') or 0)}/{int(det.get('tn') or 0)}",
        "",
    ]

    if llm is not None:
        lines.extend(
            [
                "## LLM Full-Thread (local vLLM, v1 schema)",
                f"- precision: {float(llm.get('precision') or 0.0):.1%}",
                f"- recall: {float(llm.get('recall') or 0.0):.1%}",
                f"- f1: {float(llm.get('f1') or 0.0):.1%}",
                f"- tp/fp/fn/tn: {int(llm.get('tp') or 0)}/{int(llm.get('fp') or 0)}/{int(llm.get('fn') or 0)}/{int(llm.get('tn') or 0)}",
                "",
            ]
        )

    def _render_examples(title: str, key: str) -> None:
        items = examples.get(key) if isinstance(examples.get(key), list) else []
        lines.append(f"## {title}")
        if not items:
            lines.append("- (none)")
            lines.append("")
            return
        for it in items[:20]:
            if not isinstance(it, dict):
                continue
            mid = str(it.get("message_id") or "").strip()
            tid = str(it.get("thread_id") or "").strip()
            subj = str(it.get("subject") or "").strip()
            lines.append(f"- message_id={mid} thread_id={tid} subject={subj[:140]}")
        lines.append("")

    _render_examples("Deterministic False Positives (rejected but predicted deal)", "det_fp")
    _render_examples("Deterministic False Negatives (approved but predicted non-deal)", "det_fn")
    if llm is not None:
        _render_examples("LLM False Positives (rejected but predicted deal)", "llm_fp")
        _render_examples("LLM False Negatives (approved but predicted non-deal)", "llm_fn")

    lines.append("## Notes")
    lines.append("- Report intentionally excludes raw email bodies; use the sample JSON files for deeper debugging.")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def _score_samples(*, samples_dir: Path, with_llm: bool) -> int:
    result = _evaluate_samples(samples_dir=samples_dir, with_llm=with_llm)
    if "error" in result:
        print(f"Error: {result['error']}")
        return 2

    det = result.get("deterministic") or {}
    print("Deterministic-only:")
    print(f"- rows_used: {result.get('rows_used')}")
    print(f"- precision: {float(det.get('precision') or 0.0):.1%}  recall: {float(det.get('recall') or 0.0):.1%}  f1: {float(det.get('f1') or 0.0):.1%}")

    llm = result.get("llm_full_thread") if isinstance(result.get("llm_full_thread"), dict) else None
    if llm is not None:
        print("LLM-full (local vLLM):")
        print(f"- rows_used: {result.get('rows_used')}")
        print(f"- precision: {float(llm.get('precision') or 0.0):.1%}  recall: {float(llm.get('recall') or 0.0):.1%}  f1: {float(llm.get('f1') or 0.0):.1%}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Email 3H evaluation harness (local-only).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    exp = sub.add_parser("export", help="Export recent (approve/reject) feedback threads into local JSON samples.")
    exp.add_argument("--out", default=str(_default_samples_dir()), help="Output directory (gitignored by default).")
    exp.add_argument("--limit", type=int, default=20, help="Number of feedback entries to export.")

    score = sub.add_parser("score", help="Score exported samples (deterministic vs optional LLM-full).")
    score.add_argument("--in", dest="in_dir", default=str(_default_samples_dir()), help="Samples directory.")
    score.add_argument("--with-llm", action="store_true", help="Also run local vLLM full-thread scoring (slower).")

    rep = sub.add_parser("report", help="Write a Markdown report from exported samples (no raw bodies).")
    rep.add_argument("--in", dest="in_dir", default=str(_default_samples_dir()), help="Samples directory.")
    rep.add_argument("--with-llm", action="store_true", help="Also score local vLLM full-thread (slower).")
    rep.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[2] / "docs" / "EMAIL_3H_EVAL_REPORT.md"),
        help="Output Markdown path.",
    )

    args = parser.parse_args()

    if args.cmd == "export":
        out_dir = Path(str(args.out)).expanduser().resolve()
        return asyncio.run(export_samples(out_dir=out_dir, limit=int(args.limit)))

    if args.cmd == "score":
        in_dir = Path(str(args.in_dir)).expanduser().resolve()
        return _score_samples(samples_dir=in_dir, with_llm=bool(args.with_llm))

    if args.cmd == "report":
        in_dir = Path(str(args.in_dir)).expanduser().resolve()
        result = _evaluate_samples(samples_dir=in_dir, with_llm=bool(args.with_llm))
        report_md = _render_report_markdown(result)
        out_path = Path(str(args.out)).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report_md, encoding="utf-8")
        print(f"Wrote: {out_path}")
        return 0

    return 2


if __name__ == "__main__":
    import asyncio

    raise SystemExit(main())

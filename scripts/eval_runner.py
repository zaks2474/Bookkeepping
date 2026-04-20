#!/usr/bin/env python3
"""
ZakOps Local Eval Runner (offline-first)

Runs simple, deterministic eval checks against sanitized JSONL datasets.

Default target: local vLLM OpenAI-compatible endpoint (no external network).

Safety:
  - Detects secret-like patterns in model output and does not persist raw output
    when detected (stores a redacted placeholder + labels).
  - Writes a run-ledger record with metadata only (no prompts/outputs).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pwd
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


DEFAULT_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:8000/v1").rstrip("/")
DEFAULT_MODEL = os.getenv("ZAKOPS_EVAL_MODEL", "Qwen/Qwen2.5-32B-Instruct-AWQ")
DEFAULT_OUT_DIR = "/home/zaks/DataRoom/06-KNOWLEDGE-BASE/EVALS/runs"
DEFAULT_LEDGER = os.getenv("ZAKOPS_RUN_LEDGER_PATH", "/home/zaks/logs/run-ledger.jsonl")
DEFAULT_LEDGER_WRITER = os.getenv("ZAKOPS_LEDGER_WRITER", "/home/zaks/bookkeeping/scripts/run_ledger.py")
DEFAULT_SECRET_SCAN_MODULE = "/home/zaks/scripts/zakops_secret_scan.py"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso_z(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _load_secret_scanner(path: str) -> Callable[[str], list[str]]:
    """
    Load find_secrets_in_text() from zakops_secret scanner by filesystem path.

    Falls back to a no-op scanner if the module cannot be loaded.
    """
    module_path = Path(path)
    if not module_path.exists():
        return lambda _text: []

    spec = importlib.util.spec_from_file_location("zakops_secret_scan", str(module_path))
    if spec is None or spec.loader is None:
        return lambda _text: []

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
    except Exception:
        return lambda _text: []

    fn = getattr(module, "find_secrets_in_text", None)
    if not callable(fn):
        return lambda _text: []
    return fn  # type: ignore[return-value]


def _iter_dataset_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_file():
            files.append(p)
            continue
        if not p.is_dir():
            continue
        files.extend(sorted(p.rglob("*.jsonl")))
    # stable unique
    return sorted({f.resolve() for f in files})


def _iter_examples(dataset_file: Path) -> Iterable[tuple[str, dict[str, Any]]]:
    with open(dataset_file, "r", encoding="utf-8") as fh:
        for idx, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            example_id = str(rec.get("id") or f"{dataset_file.name}:{idx}")
            yield example_id, rec


def _call_openai_chat(
    *,
    api_base: str,
    model: str,
    messages: list[dict[str, str]],
    timeout_seconds: int,
    temperature: float,
    max_tokens: int,
) -> str:
    url = f"{api_base}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload).encode("utf-8")

    # In some sandboxed environments, Python socket calls may be restricted while
    # `curl` remains usable. Prefer `curl` when available.
    if shutil.which("curl"):
        try:
            proc = subprocess.run(
                [
                    "curl",
                    "-fsS",
                    "--max-time",
                    str(int(max(1, timeout_seconds))),
                    "-H",
                    "Content-Type: application/json",
                    "-H",
                    "Authorization: Bearer dummy",
                    "-d",
                    "@-",
                    url,
                ],
                input=data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if proc.returncode != 0:
                err = (proc.stderr or b"").decode("utf-8", errors="ignore").strip()
                raise RuntimeError(f"curl_exit_{proc.returncode}: {err[:240]}")
            body = (proc.stdout or b"").decode("utf-8", errors="ignore")
        except Exception as exc:
            raise RuntimeError(f"Failed calling {url}: {type(exc).__name__}: {exc}") from exc
    else:
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            raise RuntimeError(f"HTTPError {exc.code} from {url}: {detail[:400]}") from exc
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Failed calling {url}: {type(exc).__name__}: {exc}") from exc

    try:
        parsed = json.loads(body)
        return str(parsed["choices"][0]["message"]["content"] or "")
    except Exception as exc:
        raise RuntimeError(f"Unexpected response from {url}: {body[:400]}") from exc


def _is_bulleted(text: str) -> bool:
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith("- ") or s.startswith("* ") or s.startswith("1) ") or s.startswith("1. "):
            return True
    return False


@dataclass(frozen=True)
class EvalResult:
    example_id: str
    dataset: str
    passed: bool
    failures: list[str]
    secret_labels: list[str]
    response_preview: str


def _evaluate_example(
    *,
    example_id: str,
    dataset_name: str,
    record: dict[str, Any],
    response_text: str,
    find_secrets: Callable[[str], list[str]],
) -> EvalResult:
    expected = dict(record.get("expected", {}) or {})
    includes = list(expected.get("includes", []) or [])
    fmt = str(expected.get("format", "") or "").strip().lower()
    require_no_secrets = bool(expected.get("no_secrets", True))

    failures: list[str] = []

    secret_labels = find_secrets(response_text) if require_no_secrets else []
    if secret_labels:
        failures.append("secret_detected")

    lowered = response_text.lower()
    for item in includes:
        item_s = str(item).strip()
        if not item_s:
            continue
        if item_s.lower() not in lowered:
            failures.append(f"missing_include:{item_s}")

    if fmt == "bulleted" and response_text and not _is_bulleted(response_text):
        failures.append("format_not_bulleted")

    passed = not failures

    if secret_labels:
        preview = "<REDACTED: secret-like output detected>"
    else:
        preview = response_text.strip().replace("\r\n", "\n")[:600]

    return EvalResult(
        example_id=example_id,
        dataset=dataset_name,
        passed=passed,
        failures=failures,
        secret_labels=secret_labels,
        response_preview=preview,
    )


def _write_outputs(
    *,
    out_dir: Path,
    run_id: str,
    started_at: datetime,
    ended_at: datetime,
    results: list[EvalResult],
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / f"{run_id}.results.jsonl"
    summary_path = out_dir / f"{run_id}.summary.md"

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    with open(results_path, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(
                json.dumps(
                    {
                        "example_id": r.example_id,
                        "dataset": r.dataset,
                        "passed": r.passed,
                        "failures": r.failures,
                        "secret_labels": r.secret_labels,
                        "response_preview": r.response_preview,
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )

    lines: list[str] = []
    lines.append("# Local Eval Run")
    lines.append("")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- started_at: `{started_at.isoformat()}`")
    lines.append(f"- ended_at: `{ended_at.isoformat()}`")
    lines.append(f"- examples: `{len(results)}`")
    lines.append(f"- passed: `{passed}`")
    lines.append(f"- failed: `{failed}`")
    lines.append("")

    if failed:
        lines.append("## Failures")
        lines.append("")
        for r in results:
            if r.passed:
                continue
            failures = ", ".join(r.failures) if r.failures else "unknown"
            secrets = ", ".join(r.secret_labels) if r.secret_labels else "none"
            lines.append(f"- `{r.dataset}` `{r.example_id}` failures=`{failures}` secrets=`{secrets}`")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- This runner is offline-first and targets local vLLM by default.")
    lines.append("- Outputs intentionally store only a short preview; secret-like outputs are not persisted.")
    lines.append("")

    summary_path.write_text("\n".join(lines), encoding="utf-8")

    # Best-effort: keep DataRoom outputs owned by `zaks` even when run as root.
    if os.geteuid() == 0:
        try:
            pw = pwd.getpwnam("zaks")
            os.chown(out_dir, pw.pw_uid, pw.pw_gid)
            os.chown(results_path, pw.pw_uid, pw.pw_gid)
            os.chown(summary_path, pw.pw_uid, pw.pw_gid)
        except Exception:
            pass
    return results_path, summary_path


def _append_run_ledger(
    *,
    ledger_writer: str,
    ledger_path: str,
    run_id: str,
    started_at: datetime,
    ended_at: datetime,
    status: str,
    artifacts: list[Path],
    metrics: dict[str, Any],
    errors: list[str],
) -> None:
    if not os.path.exists(ledger_writer):
        return

    cmd = [
        "python3",
        ledger_writer,
        "--ledger-path",
        ledger_path,
        "--component",
        "local_evals",
        "--run-id",
        run_id,
        "--status",
        status,
        "--started-at",
        _iso_z(started_at),
        "--ended-at",
        _iso_z(ended_at),
    ]

    for p in artifacts:
        cmd.extend(["--artifact", str(p)])

    for k, v in metrics.items():
        cmd.extend(["--metric", f"{k}={v}"])

    correlation_id = os.getenv("ZAKOPS_CORRELATION_ID", "").strip()
    if correlation_id:
        cmd.extend(["--correlation", f"correlation_id={correlation_id}"])
    parent_run_id = os.getenv("ZAKOPS_PARENT_RUN_ID", "").strip()
    if parent_run_id:
        cmd.extend(["--correlation", f"parent_run_id={parent_run_id}"])

    for e in errors:
        cmd.extend(["--error", e])

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local eval checks against JSONL datasets")
    parser.add_argument(
        "datasets",
        nargs="+",
        help="Dataset JSONL file(s) or directory(s) containing *.jsonl",
    )
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help=f"OpenAI-compatible API base (default: {DEFAULT_API_BASE})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--timeout-seconds", type=int, default=45, help="HTTP timeout per example")
    parser.add_argument("--temperature", type=float, default=0.0, help="LLM temperature (default: 0)")
    parser.add_argument("--max-tokens", type=int, default=700, help="Max completion tokens per example")
    parser.add_argument("--max-examples", type=int, default=0, help="Limit total examples (0 = no limit)")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help=f"Output directory (default: {DEFAULT_OUT_DIR})")
    parser.add_argument("--run-id", default="", help="Optional run_id override")
    parser.add_argument("--dry-run", action="store_true", help="Parse datasets and write outputs without calling any model")
    parser.add_argument("--no-ledger-record", action="store_true", help="Do not append a run-ledger record")
    args = parser.parse_args()

    started = _now_utc()
    start_epoch = time.time()

    dataset_paths = [Path(p) for p in args.datasets]
    files = _iter_dataset_files(dataset_paths)
    if not files:
        print("No dataset files found.", file=sys.stderr)
        return 2

    find_secrets = _load_secret_scanner(DEFAULT_SECRET_SCAN_MODULE)

    now = datetime.now().astimezone()
    local_day = now.strftime("%Y-%m-%d")
    out_dir = Path(args.out_dir) / local_day
    run_id = args.run_id.strip() or f"{started.strftime('%Y%m%dT%H%M%SZ')}_local_evals_{os.getpid()}"

    results: list[EvalResult] = []
    errors: list[str] = []
    model_call_errors = 0

    try:
        total = 0
        for f in files:
            dataset_name = f.parent.name or f.stem
            for example_id, rec in _iter_examples(f):
                total += 1
                if args.max_examples and total > args.max_examples:
                    break

                question = ""
                try:
                    inp = dict(rec.get("input", {}) or {})
                    question = str(inp.get("question", "") or rec.get("question", "") or "").strip()
                except Exception:
                    question = ""

                if not question:
                    results.append(
                        EvalResult(
                            example_id=example_id,
                            dataset=dataset_name,
                            passed=False,
                            failures=["missing_question"],
                            secret_labels=[],
                            response_preview="",
                        )
                    )
                    continue

                if args.dry_run:
                    response = ""
                else:
                    try:
                        response = _call_openai_chat(
                            api_base=args.api_base,
                            model=args.model,
                            messages=[
                                {"role": "system", "content": "You are a careful ops assistant. Never output secrets."},
                                {"role": "user", "content": question},
                            ],
                            timeout_seconds=args.timeout_seconds,
                            temperature=args.temperature,
                            max_tokens=args.max_tokens,
                        )
                    except Exception as exc:
                        model_call_errors += 1
                        err = f"model_call_error:{type(exc).__name__}"
                        errors.append(err)
                        detail = str(exc).strip().replace("\r", " ").replace("\n", " ")
                        if detail:
                            detail = detail[:220]
                        preview = f"ERROR: {detail}" if detail else "ERROR"
                        # Never persist secret-like content, even in error messages.
                        if find_secrets(preview):
                            preview = "<REDACTED: secret-like error detail detected>"
                        results.append(
                            EvalResult(
                                example_id=example_id,
                                dataset=dataset_name,
                                passed=False,
                                failures=[err],
                                secret_labels=[],
                                response_preview=preview,
                            )
                        )
                        continue

                results.append(
                    _evaluate_example(
                        example_id=example_id,
                        dataset_name=dataset_name,
                        record=rec,
                        response_text=response,
                        find_secrets=find_secrets,
                    )
                )

            if args.max_examples and total >= args.max_examples:
                break
    except Exception as exc:
        errors.append(f"runner_error:{type(exc).__name__}")

    ended = _now_utc()
    duration_seconds = max(0, int(time.time() - start_epoch))

    results_path, summary_path = _write_outputs(
        out_dir=out_dir,
        run_id=run_id,
        started_at=started,
        ended_at=ended,
        results=results,
    )

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    if errors:
        status = "fail"
    elif failed == 0:
        status = "success"
    else:
        status = "partial"

    if not args.no_ledger_record:
        _append_run_ledger(
            ledger_writer=DEFAULT_LEDGER_WRITER,
            ledger_path=DEFAULT_LEDGER,
            run_id=run_id,
            started_at=started,
            ended_at=ended,
            status=status,
            artifacts=[results_path, summary_path],
            metrics={
                "examples_total": len(results),
                "examples_passed": passed,
                "examples_failed": failed,
                "duration_seconds": duration_seconds,
                "datasets": len(files),
                "model_call_errors": model_call_errors,
                "dry_run": int(bool(args.dry_run)),
            },
            errors=errors + ([f"failed_{failed}"] if failed else []),
        )

    print(str(summary_path))
    return 0 if status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

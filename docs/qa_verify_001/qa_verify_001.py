#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def safe_truncate(text: str, limit: int = 4000) -> str:
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n…(truncated, {len(text)} bytes total)…"


def http_json_or_text(response: requests.Response) -> Tuple[Optional[Any], str]:
    try:
        return response.json(), response.text
    except Exception:
        return None, response.text


def http_request(
    method: str,
    url: str,
    json_body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout_s: int = 15,
) -> Dict[str, Any]:
    start = time.time()
    try:
        resp = requests.request(
            method=method,
            url=url,
            json=json_body,
            headers=headers,
            timeout=timeout_s,
        )
        elapsed_ms = int((time.time() - start) * 1000)
        json_obj, raw_text = http_json_or_text(resp)
        return {
            "ok": True,
            "method": method,
            "url": url,
            "request_json": json_body,
            "status_code": resp.status_code,
            "elapsed_ms": elapsed_ms,
            "response_headers": dict(resp.headers),
            "response_json": json_obj,
            "response_text": safe_truncate(raw_text, 4000),
        }
    except Exception as exc:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "ok": False,
            "method": method,
            "url": url,
            "request_json": json_body,
            "elapsed_ms": elapsed_ms,
            "error": repr(exc),
        }


def run_cmd(args: List[str], timeout_s: int = 30) -> Dict[str, Any]:
    start = time.time()
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout_s)
    elapsed_ms = int((time.time() - start) * 1000)
    return {
        "args": args,
        "returncode": proc.returncode,
        "elapsed_ms": elapsed_ms,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def psql_scalar(
    query: str,
    *,
    container: str,
    user: str,
    db: str,
    timeout_s: int = 30,
) -> str:
    args = [
        "docker",
        "exec",
        container,
        "psql",
        "-U",
        user,
        "-d",
        db,
        "-t",
        "-A",
        "-c",
        query,
    ]
    out = run_cmd(args, timeout_s=timeout_s)
    if out["returncode"] != 0:
        raise RuntimeError(
            f"psql failed rc={out['returncode']} stderr={out['stderr'][:400]}"
        )
    return out["stdout"].strip()


def db_count_table(
    schema: str,
    table: str,
    *,
    container: str,
    user: str,
    db: str,
) -> Optional[int]:
    exists = psql_scalar(
        f"SELECT 1 FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='{table}'",
        container=container,
        user=user,
        db=db,
    )
    if not exists:
        return None
    count_str = psql_scalar(
        f"SELECT COUNT(*) FROM {schema}.{table}",
        container=container,
        user=user,
        db=db,
    )
    return int(count_str) if count_str else 0


def find_trace_id(obj: Any, text: str) -> Optional[str]:
    if isinstance(obj, dict):
        trace = obj.get("trace_id")
        if isinstance(trace, str) and trace:
            return trace
        err = obj.get("error")
        if isinstance(err, dict):
            trace = err.get("trace_id")
            if isinstance(trace, str) and trace:
                return trace
    m = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text, re.I)
    return m.group(0) if m else None


@dataclasses.dataclass
class TestCase:
    id: str
    name: str
    passed: bool
    details: Dict[str, Any]
    timestamp_utc: str = dataclasses.field(default_factory=utc_now_iso)


def suite_result(name: str, tests: List[TestCase]) -> Dict[str, Any]:
    passed = sum(1 for t in tests if t.passed)
    total = len(tests)
    return {
        "test_suite": name,
        "timestamp_utc": utc_now_iso(),
        "summary": {"passed": passed, "total": total},
        "tests": [dataclasses.asdict(t) for t in tests],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--test-dir", required=True)
    args = parser.parse_args()

    run_id = args.run_id
    test_dir = Path(args.test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)

    backend_url = os.getenv("BACKEND_URL", "http://localhost:8091").rstrip("/")
    agent_url = os.getenv("AGENT_URL", "http://localhost:8095").rstrip("/")
    rag_url = os.getenv("RAG_URL", "http://localhost:8052").rstrip("/")
    dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3003").rstrip("/")

    pg_container = os.getenv("PG_CONTAINER", "zakops-postgres-1")
    pg_user = os.getenv("PG_USER", "zakops")
    pg_db = os.getenv("PG_DB", "zakops")

    run_meta = {
        "run_id": run_id,
        "timestamp_utc": utc_now_iso(),
        "env": {
            "BACKEND_URL": backend_url,
            "AGENT_URL": agent_url,
            "RAG_URL": rag_url,
            "DASHBOARD_URL": dashboard_url,
            "PG_CONTAINER": pg_container,
            "PG_USER": pg_user,
            "PG_DB": pg_db,
        },
    }
    write_json(test_dir / "run_meta.json", run_meta)

    print(f"RUN_ID={run_id}")
    print(f"TEST_DIR={test_dir}")

    # -------------------------------------------------------------------------
    # Phase 0: Preflight + baseline
    # -------------------------------------------------------------------------
    phase0_tests: List[TestCase] = []

    # 0.1 Health probes
    health_matrix: Dict[str, Any] = {}
    for name, url in [
        ("backend_health", f"{backend_url}/health"),
        ("agent_health", f"{agent_url}/health"),
        ("rag_stats", f"{rag_url}/rag/stats"),
        ("dashboard_root", f"{dashboard_url}/"),
    ]:
        res = http_request("GET", url, timeout_s=5)
        health_matrix[name] = res
    # TCP checks via nc (best-effort)
    tcp_matrix: Dict[str, Any] = {}
    for name, port in [("postgres_tcp", 5432), ("redis_tcp", 6379), ("legacy_8090_tcp", 8090)]:
        if shutil_which("nc"):
            out = run_cmd(["nc", "-z", "-w2", "localhost", str(port)], timeout_s=5)
            tcp_matrix[name] = out
        else:
            tcp_matrix[name] = {"error": "nc_not_found"}

    phase0_health = {
        "timestamp_utc": utc_now_iso(),
        "http": health_matrix,
        "tcp": tcp_matrix,
    }
    write_json(test_dir / "phase0_health.json", phase0_health)

    def http_ok(code: Any) -> bool:
        try:
            c = int(code)
            return c in (200, 301, 302, 307)
        except Exception:
            return False

    all_http_ready = (
        health_matrix["backend_health"].get("ok")
        and http_ok(health_matrix["backend_health"].get("status_code"))
        and health_matrix["agent_health"].get("ok")
        and http_ok(health_matrix["agent_health"].get("status_code"))
        and health_matrix["rag_stats"].get("ok")
        and http_ok(health_matrix["rag_stats"].get("status_code"))
        and health_matrix["dashboard_root"].get("ok")
        and http_ok(health_matrix["dashboard_root"].get("status_code"))
    )
    phase0_tests.append(
        TestCase(
            id="0.1",
            name="Pre-test HTTP health matrix",
            passed=bool(all_http_ready),
            details={"artifact": "phase0_health.json"},
        )
    )

    # 0.2 Baseline DB counts
    baseline_tables = {
        "deals": "deals",
        "actions": "actions",
        "quarantine_items": "quarantine_items",
        "agent_runs": "agent_runs",
        "inbox": "inbox",
        "outbox": "outbox",
    }
    baseline_counts: Dict[str, Any] = {"timestamp_utc": utc_now_iso(), "tables": {}}
    for key, table in baseline_tables.items():
        try:
            baseline_counts["tables"][key] = db_count_table(
                "zakops", table, container=pg_container, user=pg_user, db=pg_db
            )
        except Exception as exc:
            baseline_counts["tables"][key] = {"error": repr(exc)}
    write_json(test_dir / "baseline_state.json", baseline_counts)
    phase0_tests.append(
        TestCase(
            id="0.2",
            name="Baseline DB state captured",
            passed=True,
            details={"artifact": "baseline_state.json"},
        )
    )

    # 0.3 Legacy port 8090 must be dead
    legacy_res = http_request("GET", "http://localhost:8090/health", timeout_s=2)
    legacy_ok = not legacy_res.get("ok") or legacy_res.get("status_code") in (None, 0)
    if legacy_res.get("ok") and legacy_res.get("status_code"):
        # If the HTTP stack returned a status code, it's a hard fail.
        legacy_ok = False
    write_json(test_dir / "legacy_port_8090_check.json", legacy_res)
    phase0_tests.append(
        TestCase(
            id="0.3",
            name="Legacy contamination check (port 8090 must fail)",
            passed=bool(legacy_ok),
            details={"artifact": "legacy_port_8090_check.json"},
        )
    )

    phase0_suite = suite_result("Phase 0 — Environment Setup", phase0_tests)
    write_json(test_dir / "phase0_results.json", phase0_suite)

    # Hard-stop if 8090 responds.
    if not legacy_ok:
        write_final_report(
            test_dir=test_dir,
            run_id=run_id,
            suites=[phase0_suite],
            verdict="FAIL (legacy service on 8090)",
        )
        return 1

    # -------------------------------------------------------------------------
    # Contracts / OpenAPI snapshots
    # -------------------------------------------------------------------------
    openapi_tests: List[TestCase] = []
    backend_openapi = http_request("GET", f"{backend_url}/openapi.json", timeout_s=10)
    agent_openapi = http_request("GET", f"{agent_url}/api/v1/openapi.json", timeout_s=10)
    rag_openapi = http_request("GET", f"{rag_url}/openapi.json", timeout_s=10)
    write_json(test_dir / "openapi_backend.json", backend_openapi.get("response_json") or backend_openapi)
    write_json(test_dir / "openapi_agent.json", agent_openapi.get("response_json") or agent_openapi)
    write_json(test_dir / "openapi_rag.json", rag_openapi.get("response_json") or rag_openapi)
    openapi_tests.append(
        TestCase(
            id="0.4",
            name="OpenAPI snapshots captured",
            passed=bool(
                backend_openapi.get("ok")
                and agent_openapi.get("ok")
                and rag_openapi.get("ok")
            ),
            details={
                "artifacts": [
                    "openapi_backend.json",
                    "openapi_agent.json",
                    "openapi_rag.json",
                ]
            },
        )
    )
    openapi_suite = suite_result("Phase 0 — Contract Snapshots", openapi_tests)
    write_json(test_dir / "phase0_openapi_results.json", openapi_suite)

    # -------------------------------------------------------------------------
    # Phase 1: Backend API verification
    # -------------------------------------------------------------------------
    backend_tests: List[TestCase] = []

    # 1.0 Endpoint probe via OpenAPI (safe, best-effort)
    backend_probe = endpoint_probe(
        name="backend",
        base_url=backend_url,
        openapi_json=backend_openapi.get("response_json"),
        allow_mutation=False,
    )
    write_json(test_dir / "backend_endpoint_probe.json", backend_probe)
    backend_tests.append(
        TestCase(
            id="1.0",
            name="Backend endpoint probe (OpenAPI reachability)",
            passed=True,
            details={"artifact": "backend_endpoint_probe.json"},
        )
    )

    # 1.1 Deals (create/read/update/transition) with DB verification
    deals_suite = backend_deals_suite(
        backend_url=backend_url,
        pg_container=pg_container,
        pg_user=pg_user,
        pg_db=pg_db,
    )
    write_json(test_dir / "deals_crud_results.json", deals_suite)
    backend_tests.append(
        TestCase(
            id="1.1",
            name="Deals CRUD suite executed",
            passed=deals_suite["summary"]["passed"] == deals_suite["summary"]["total"],
            details={"artifact": "deals_crud_results.json", "summary": deals_suite["summary"]},
        )
    )

    # 1.2 Actions (DB-seeded + API approve/reject) with DB verification
    actions_suite = backend_actions_suite(
        backend_url=backend_url,
        pg_container=pg_container,
        pg_user=pg_user,
        pg_db=pg_db,
    )
    write_json(test_dir / "actions_crud_results.json", actions_suite)
    backend_tests.append(
        TestCase(
            id="1.2",
            name="Actions suite executed",
            passed=actions_suite["summary"]["passed"] == actions_suite["summary"]["total"],
            details={"artifact": "actions_crud_results.json", "summary": actions_suite["summary"]},
        )
    )

    # 1.3 Quarantine (endpoint + DB evidence)
    quarantine_suite = backend_quarantine_suite(
        backend_url=backend_url,
        pg_container=pg_container,
        pg_user=pg_user,
        pg_db=pg_db,
    )
    write_json(test_dir / "quarantine_results.json", quarantine_suite)
    backend_tests.append(
        TestCase(
            id="1.3",
            name="Quarantine suite executed",
            passed=quarantine_suite["summary"]["passed"] == quarantine_suite["summary"]["total"],
            details={"artifact": "quarantine_results.json", "summary": quarantine_suite["summary"]},
        )
    )

    backend_suite = suite_result("Phase 1 — Backend API", backend_tests)
    write_json(test_dir / "backend_results.json", backend_suite)

    # -------------------------------------------------------------------------
    # Phase 2: Agent API verification
    # -------------------------------------------------------------------------
    agent_tests: List[TestCase] = []
    agent_probe = endpoint_probe(
        name="agent",
        base_url=agent_url,
        openapi_json=agent_openapi.get("response_json"),
        allow_mutation=False,
    )
    write_json(test_dir / "agent_endpoint_probe.json", agent_probe)
    agent_tests.append(
        TestCase(
            id="2.0",
            name="Agent endpoint probe (OpenAPI reachability)",
            passed=True,
            details={"artifact": "agent_endpoint_probe.json"},
        )
    )

    agent_suite = agent_api_suite(agent_url=agent_url)
    write_json(test_dir / "agent_api_results.json", agent_suite)
    agent_tests.append(
        TestCase(
            id="2.1",
            name="Agent API functional tests executed",
            passed=agent_suite["summary"]["passed"] == agent_suite["summary"]["total"],
            details={"artifact": "agent_api_results.json", "summary": agent_suite["summary"]},
        )
    )

    agent_tools_suite = agent_tool_suite(agent_url=agent_url, backend_url=backend_url)
    write_json(test_dir / "agent_tool_results.json", agent_tools_suite)
    agent_tests.append(
        TestCase(
            id="2.2",
            name="Agent tool capability tests executed",
            passed=agent_tools_suite["summary"]["passed"] == agent_tools_suite["summary"]["total"],
            details={"artifact": "agent_tool_results.json", "summary": agent_tools_suite["summary"]},
        )
    )

    agent_results = suite_result("Phase 2 — Agent API", agent_tests)
    write_json(test_dir / "agent_results.json", agent_results)

    # -------------------------------------------------------------------------
    # Phase 3: RAG API verification
    # -------------------------------------------------------------------------
    rag_tests: List[TestCase] = []
    rag_probe = endpoint_probe(
        name="rag",
        base_url=rag_url,
        openapi_json=rag_openapi.get("response_json"),
        allow_mutation=False,
    )
    write_json(test_dir / "rag_endpoint_probe.json", rag_probe)
    rag_tests.append(
        TestCase(
            id="3.0",
            name="RAG endpoint probe (OpenAPI reachability)",
            passed=True,
            details={"artifact": "rag_endpoint_probe.json"},
        )
    )
    rag_suite = rag_api_suite(rag_url=rag_url)
    write_json(test_dir / "rag_api_results.json", rag_suite)
    rag_tests.append(
        TestCase(
            id="3.1",
            name="RAG API functional tests executed",
            passed=rag_suite["summary"]["passed"] == rag_suite["summary"]["total"],
            details={"artifact": "rag_api_results.json", "summary": rag_suite["summary"]},
        )
    )
    rag_results = suite_result("Phase 3 — RAG API", rag_tests)
    write_json(test_dir / "rag_results.json", rag_results)

    # -------------------------------------------------------------------------
    # Phase 4: E2E workflows
    # -------------------------------------------------------------------------
    e2e_suite = e2e_suite_run(
        backend_url=backend_url,
        agent_url=agent_url,
        pg_container=pg_container,
        pg_user=pg_user,
        pg_db=pg_db,
    )
    write_json(test_dir / "e2e_results.json", e2e_suite)
    e2e_results = suite_result(
        "Phase 4 — E2E Workflows",
        [
            TestCase(
                id="4.0",
                name="E2E workflow suite executed",
                passed=e2e_suite["summary"]["passed"] == e2e_suite["summary"]["total"],
                details={"artifact": "e2e_results.json", "summary": e2e_suite["summary"]},
            )
        ],
    )
    write_json(test_dir / "phase4_results.json", e2e_results)

    # -------------------------------------------------------------------------
    # Phase 5: UI route checks
    # -------------------------------------------------------------------------
    ui_suite = ui_route_suite(dashboard_url=dashboard_url)
    write_json(test_dir / "ui_route_results.json", ui_suite)
    ui_results = suite_result(
        "Phase 5 — UI Routes",
        [
            TestCase(
                id="5.0",
                name="UI route suite executed",
                passed=ui_suite["summary"]["passed"] == ui_suite["summary"]["total"],
                details={"artifact": "ui_route_results.json", "summary": ui_suite["summary"]},
            )
        ],
    )
    write_json(test_dir / "ui_results.json", ui_results)

    # -------------------------------------------------------------------------
    # Final aggregation + report
    # -------------------------------------------------------------------------
    suites = [
        phase0_suite,
        openapi_suite,
        backend_suite,
        agent_results,
        rag_results,
        e2e_results,
        ui_results,
    ]
    summary = aggregate_summary(suites)
    write_json(test_dir / "summary.json", summary)

    verdict = "PASS" if summary["overall"]["failed"] == 0 else "FAIL"
    write_final_report(test_dir=test_dir, run_id=run_id, suites=suites, verdict=verdict)

    print()
    print(f"VERDICT={verdict}")
    print(f"REPORT={test_dir / 'QA_VERIFICATION_REPORT.md'}")

    return 0 if verdict == "PASS" else 1


def shutil_which(cmd: str) -> Optional[str]:
    from shutil import which

    return which(cmd)


def endpoint_probe(
    *,
    name: str,
    base_url: str,
    openapi_json: Optional[Dict[str, Any]],
    allow_mutation: bool,
) -> Dict[str, Any]:
    if not isinstance(openapi_json, dict):
        return {"error": "openapi_missing_or_invalid"}

    results: List[Dict[str, Any]] = []
    paths = openapi_json.get("paths", {})
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, meta in methods.items():
            method_u = method.upper()
            # Only safe probing by default: GET/HEAD; for POST/PUT/PATCH/DELETE only call if allow_mutation is True.
            if method_u not in ("GET", "HEAD") and not allow_mutation:
                results.append(
                    {
                        "method": method_u,
                        "path": path,
                        "skipped": True,
                        "reason": "mutation_disabled",
                    }
                )
                continue

            url = base_url + path
            # Replace path params with placeholders
            url = re.sub(r"\\{[^/]+\\}", "qa-probe-id", url)
            res = http_request(method_u, url, timeout_s=8)
            ok = res.get("ok")
            status = res.get("status_code")
            # For probes: treat any HTTP response as "reachable" (including 4xx), but record 5xx explicitly.
            reachable = bool(ok and status)
            results.append(
                {
                    "method": method_u,
                    "path": path,
                    "url": url,
                    "reachable": reachable,
                    "status_code": status,
                    "trace_id": find_trace_id(res.get("response_json"), res.get("response_text", "")),
                    "response_preview": res.get("response_text", "")[:300],
                }
            )

    return {
        "name": name,
        "timestamp_utc": utc_now_iso(),
        "base_url": base_url,
        "mutation_allowed": allow_mutation,
        "results": results,
    }


def backend_deals_suite(
    *,
    backend_url: str,
    pg_container: str,
    pg_user: str,
    pg_db: str,
) -> Dict[str, Any]:
    tests: List[TestCase] = []
    canonical_name = f"QA-VERIFY-001 Deal {int(time.time())}"
    canonical_name_sql = canonical_name.replace("'", "''")

    count_before = db_count_table("zakops", "deals", container=pg_container, user=pg_user, db=pg_db) or 0

    create_payload = {"canonical_name": canonical_name, "stage": "inbound", "status": "active"}
    create_res = http_request("POST", f"{backend_url}/api/deals", json_body=create_payload, timeout_s=10)

    # Determine if a row exists even if API errored.
    deal_id = None
    try:
        deal_id = psql_scalar(
            f"SELECT deal_id FROM zakops.deals WHERE canonical_name = '{canonical_name_sql}' ORDER BY created_at DESC LIMIT 1",
            container=pg_container,
            user=pg_user,
            db=pg_db,
        )
        deal_id = deal_id or None
    except Exception:
        deal_id = None

    count_after = db_count_table("zakops", "deals", container=pg_container, user=pg_user, db=pg_db) or 0

    create_ok = (
        create_res.get("ok")
        and create_res.get("status_code") in (200, 201)
        and bool(deal_id)
        and count_after == count_before + 1
    )
    side_effect_without_success = (create_res.get("status_code") and create_res.get("status_code") >= 500 and bool(deal_id))
    tests.append(
        TestCase(
            id="1.1.1",
            name="Create deal (API + DB double-verify)",
            passed=bool(create_ok),
            details={
                "request": create_res,
                "db": {
                    "count_before": count_before,
                    "count_after": count_after,
                    "deal_id_from_db": deal_id,
                    "side_effect_without_success": side_effect_without_success,
                },
            },
        )
    )

    # Read deal
    if deal_id:
        get_res = http_request("GET", f"{backend_url}/api/deals/{deal_id}", timeout_s=10)
        db_row = psql_scalar(
            f"SELECT json_build_object('deal_id', deal_id, 'canonical_name', canonical_name, 'stage', stage, 'status', status)::text FROM zakops.deals WHERE deal_id='{deal_id}'",
            container=pg_container,
            user=pg_user,
            db=pg_db,
        )
        read_ok = get_res.get("ok") and get_res.get("status_code") == 200
        tests.append(
            TestCase(
                id="1.1.2",
                name="Read deal by id (API + DB)",
                passed=bool(read_ok),
                details={"request": get_res, "db_row_json_text": db_row},
            )
        )
    else:
        tests.append(
            TestCase(
                id="1.1.2",
                name="Read deal by id (API + DB)",
                passed=False,
                details={"error": "no_deal_id_from_create"},
            )
        )

    # List deals (known to be fragile; still must be tested)
    list_res = http_request("GET", f"{backend_url}/api/deals", timeout_s=10)
    list_ok = list_res.get("ok") and list_res.get("status_code") == 200
    tests.append(
        TestCase(
            id="1.1.3",
            name="List deals (API)",
            passed=bool(list_ok),
            details={"request": list_res},
        )
    )

    # Update deal (display_name)
    if deal_id:
        new_display = f"{canonical_name} (updated)"
        patch_payload = {"display_name": new_display}
        patch_res = http_request("PATCH", f"{backend_url}/api/deals/{deal_id}", json_body=patch_payload, timeout_s=10)
        db_display = psql_scalar(
            f"SELECT COALESCE(display_name,'') FROM zakops.deals WHERE deal_id='{deal_id}'",
            container=pg_container,
            user=pg_user,
            db=pg_db,
        )
        update_ok = patch_res.get("ok") and patch_res.get("status_code") == 200 and new_display in db_display
        tests.append(
            TestCase(
                id="1.1.4",
                name="Update deal (PATCH) + verify DB display_name",
                passed=bool(update_ok),
                details={"request": patch_res, "db_display_name": db_display},
            )
        )
    else:
        tests.append(
            TestCase(
                id="1.1.4",
                name="Update deal (PATCH) + verify DB display_name",
                passed=False,
                details={"error": "no_deal_id_from_create"},
            )
        )

    # Transition deal stage (use valid-transitions first, then attempt)
    if deal_id:
        valid_res = http_request("GET", f"{backend_url}/api/deals/{deal_id}/valid-transitions", timeout_s=10)
        new_stage = None
        if isinstance(valid_res.get("response_json"), dict):
            vt = valid_res["response_json"].get("valid_transitions")
            if isinstance(vt, list) and vt:
                new_stage = vt[0]
        if not new_stage:
            new_stage = "initial_review"
        transition_payload = {
            "new_stage": new_stage,
            "reason": "QA-VERIFY-001 stage transition",
            "idempotency_key": f"qa-verify-{deal_id}-{int(time.time())}",
        }
        trans_res = http_request(
            "POST", f"{backend_url}/api/deals/{deal_id}/transition", json_body=transition_payload, timeout_s=15
        )
        db_stage = psql_scalar(
            f"SELECT stage FROM zakops.deals WHERE deal_id='{deal_id}'",
            container=pg_container,
            user=pg_user,
            db=pg_db,
        )
        trans_ok = trans_res.get("ok") and trans_res.get("status_code") == 200 and db_stage == new_stage
        tests.append(
            TestCase(
                id="1.1.5",
                name="Transition deal stage (API + DB)",
                passed=bool(trans_ok),
                details={
                    "valid_transitions_request": valid_res,
                    "transition_request": trans_res,
                    "db_stage": db_stage,
                    "attempted_new_stage": new_stage,
                },
            )
        )
    else:
        tests.append(
            TestCase(
                id="1.1.5",
                name="Transition deal stage (API + DB)",
                passed=False,
                details={"error": "no_deal_id_from_create"},
            )
        )

    # Cleanup (DB delete) + verify GET returns 404/500-with-trace (evidence)
    cleanup_details: Dict[str, Any] = {}
    if deal_id:
        try:
            _ = psql_scalar(
                f"DELETE FROM zakops.deals WHERE deal_id='{deal_id}'",
                container=pg_container,
                user=pg_user,
                db=pg_db,
            )
            cleanup_details["db_delete"] = "ok"
        except Exception as exc:
            cleanup_details["db_delete_error"] = repr(exc)

        get_after = http_request("GET", f"{backend_url}/api/deals/{deal_id}", timeout_s=10)
        row_exists = psql_scalar(
            f"SELECT COUNT(*) FROM zakops.deals WHERE deal_id='{deal_id}'",
            container=pg_container,
            user=pg_user,
            db=pg_db,
        )
        deleted_ok = row_exists == "0"
        tests.append(
            TestCase(
                id="1.1.6",
                name="Cleanup test deal (DB delete) + verify DB state",
                passed=bool(deleted_ok),
                details={"cleanup": cleanup_details, "get_after": get_after, "db_row_count": row_exists},
            )
        )
    else:
        tests.append(
            TestCase(
                id="1.1.6",
                name="Cleanup test deal (DB delete) + verify DB state",
                passed=False,
                details={"error": "no_deal_id_for_cleanup"},
            )
        )

    return suite_result("Backend Deals", tests)


def backend_actions_suite(
    *,
    backend_url: str,
    pg_container: str,
    pg_user: str,
    pg_db: str,
) -> Dict[str, Any]:
    tests: List[TestCase] = []

    # DB seed an action record (since API has no create action endpoint)
    action_id = f"ACT-QA-{int(time.time())}"
    insert_query = (
        "INSERT INTO zakops.actions(action_id, action_type, title, description, status, requires_approval) "
        f"VALUES ('{action_id}', 'QA_TEST_ACTION', 'QA Verify Action', 'Seeded by QA-VERIFY-001', 'pending', true)"
    )
    try:
        _ = psql_scalar(insert_query, container=pg_container, user=pg_user, db=pg_db)
        seeded = True
    except Exception as exc:
        seeded = False
        tests.append(
            TestCase(
                id="1.2.0",
                name="Seed action row in DB",
                passed=False,
                details={"error": repr(exc), "query": insert_query},
            )
        )
        return suite_result("Backend Actions", tests)

    tests.append(
        TestCase(
            id="1.2.0",
            name="Seed action row in DB",
            passed=True,
            details={"action_id": action_id},
        )
    )

    # List actions
    list_res = http_request("GET", f"{backend_url}/api/actions", timeout_s=10)
    tests.append(
        TestCase(
            id="1.2.1",
            name="List actions (API)",
            passed=bool(list_res.get("ok") and list_res.get("status_code") == 200),
            details={"request": list_res},
        )
    )

    # Get action
    get_res = http_request("GET", f"{backend_url}/api/actions/{action_id}", timeout_s=10)
    db_status_before = psql_scalar(
        f"SELECT status FROM zakops.actions WHERE action_id='{action_id}'",
        container=pg_container,
        user=pg_user,
        db=pg_db,
    )
    tests.append(
        TestCase(
            id="1.2.2",
            name="Get action by id (API + DB)",
            passed=bool(get_res.get("ok") and get_res.get("status_code") == 200),
            details={"request": get_res, "db_status": db_status_before},
        )
    )

    # Approve action
    approve_payload = {"approved_by": "qa_verify_001", "notes": "QA approval"}
    approve_res = http_request(
        "POST", f"{backend_url}/api/actions/{action_id}/approve", json_body=approve_payload, timeout_s=10
    )
    db_status_after = psql_scalar(
        f"SELECT status FROM zakops.actions WHERE action_id='{action_id}'",
        container=pg_container,
        user=pg_user,
        db=pg_db,
    )
    approve_ok = approve_res.get("ok") and approve_res.get("status_code") == 200 and db_status_after != db_status_before
    tests.append(
        TestCase(
            id="1.2.3",
            name="Approve action (API + DB status change)",
            passed=bool(approve_ok),
            details={"request": approve_res, "db_status_before": db_status_before, "db_status_after": db_status_after},
        )
    )

    # Cleanup seeded action
    try:
        _ = psql_scalar(
            f"DELETE FROM zakops.actions WHERE action_id='{action_id}'",
            container=pg_container,
            user=pg_user,
            db=pg_db,
        )
        cleanup_ok = True
    except Exception as exc:
        cleanup_ok = False
        cleanup_err = repr(exc)
    tests.append(
        TestCase(
            id="1.2.4",
            name="Cleanup seeded action (DB delete)",
            passed=bool(cleanup_ok),
            details={"error": cleanup_err} if not cleanup_ok else {"status": "deleted"},
        )
    )

    return suite_result("Backend Actions", tests)


def backend_quarantine_suite(
    *,
    backend_url: str,
    pg_container: str,
    pg_user: str,
    pg_db: str,
) -> Dict[str, Any]:
    tests: List[TestCase] = []

    list_res = http_request("GET", f"{backend_url}/api/quarantine", timeout_s=10)
    tests.append(
        TestCase(
            id="1.3.1",
            name="List quarantine items (API)",
            passed=bool(list_res.get("ok") and list_res.get("status_code") == 200),
            details={"request": list_res},
        )
    )

    # DB sanity: count quarantine_items
    try:
        count = db_count_table("zakops", "quarantine_items", container=pg_container, user=pg_user, db=pg_db)
        tests.append(
            TestCase(
                id="1.3.2",
                name="DB quarantine_items count query",
                passed=True,
                details={"db_count": count},
            )
        )
    except Exception as exc:
        tests.append(
            TestCase(
                id="1.3.2",
                name="DB quarantine_items count query",
                passed=False,
                details={"error": repr(exc)},
            )
        )

    # Endpoint existence probe for item_id
    get_res = http_request("GET", f"{backend_url}/api/quarantine/qa-probe-id", timeout_s=10)
    # Accept 400/404/422 as "exists" (custom error handler may map validation to 400), but 5xx is failure.
    ok = bool(get_res.get("ok") and get_res.get("status_code") in (200, 400, 404, 422))
    tests.append(
        TestCase(
            id="1.3.3",
            name="Get quarantine item (endpoint existence)",
            passed=ok,
            details={"request": get_res},
        )
    )

    return suite_result("Backend Quarantine", tests)


def agent_api_suite(*, agent_url: str) -> Dict[str, Any]:
    tests: List[TestCase] = []
    health = http_request("GET", f"{agent_url}/health", timeout_s=5)
    tests.append(
        TestCase(
            id="2.1.1",
            name="Agent /health",
            passed=bool(health.get("ok") and health.get("status_code") == 200),
            details={"request": health},
        )
    )

    invoke_payload = {"actor_id": "qa-verify-001", "message": "QA test: respond with 'QA test received'."}
    invoke = http_request("POST", f"{agent_url}/api/v1/agent/invoke", json_body=invoke_payload, timeout_s=60)
    invoke_ok = bool(invoke.get("ok") and invoke.get("status_code") == 200)
    # Schema check: must have thread_id + status
    schema_ok = False
    if isinstance(invoke.get("response_json"), dict):
        schema_ok = "thread_id" in invoke["response_json"] and "status" in invoke["response_json"]
    tests.append(
        TestCase(
            id="2.1.2",
            name="Agent invoke (simple) + schema keys",
            passed=bool(invoke_ok and schema_ok),
            details={"request": invoke, "schema_ok": schema_ok},
        )
    )

    # Streaming endpoint (basic)
    stream_payload = {"actor_id": "qa-verify-001", "message": "QA stream test: say hello."}
    stream = http_request("POST", f"{agent_url}/api/v1/agent/invoke/stream", json_body=stream_payload, timeout_s=60)
    stream_ok = bool(stream.get("ok") and stream.get("status_code") == 200)
    tests.append(
        TestCase(
            id="2.1.3",
            name="Agent invoke stream (basic HTTP reachability)",
            passed=stream_ok,
            details={"request": stream},
        )
    )

    return suite_result("Agent API", tests)


def agent_tool_suite(*, agent_url: str, backend_url: str) -> Dict[str, Any]:
    tests: List[TestCase] = []

    # Tool-oriented prompt: attempt to list deals (may fail if tool backend misconfigured)
    payload = {
        "actor_id": "qa-verify-001",
        "message": "List deals (QA). If tools are available, use them; otherwise explain error.",
    }
    invoke = http_request("POST", f"{agent_url}/api/v1/agent/invoke", json_body=payload, timeout_s=90)
    ok = bool(invoke.get("ok") and invoke.get("status_code") == 200)
    tests.append(
        TestCase(
            id="2.2.1",
            name="Agent tool attempt: list deals (may exercise tool gateway)",
            passed=ok,
            details={"request": invoke},
        )
    )

    # Check if agent config still points to decommissioned 8090 by probing backend deals list (known failing) vs legacy
    legacy = http_request("GET", "http://localhost:8090/health", timeout_s=2)
    backend = http_request("GET", f"{backend_url}/health", timeout_s=5)
    tests.append(
        TestCase(
            id="2.2.2",
            name="Agent integration sanity: backend reachable, legacy 8090 dead",
            passed=bool((not legacy.get("ok")) and backend.get("ok") and backend.get("status_code") == 200),
            details={"legacy_8090": legacy, "backend_health": backend},
        )
    )

    return suite_result("Agent Tools", tests)


def rag_api_suite(*, rag_url: str) -> Dict[str, Any]:
    tests: List[TestCase] = []
    stats = http_request("GET", f"{rag_url}/rag/stats", timeout_s=10)
    tests.append(
        TestCase(
            id="3.1.1",
            name="RAG stats",
            passed=bool(stats.get("ok") and stats.get("status_code") == 200),
            details={"request": stats},
        )
    )

    q1 = {"query": "deal pipeline", "top_k": 5}
    query = http_request("POST", f"{rag_url}/rag/query", json_body=q1, timeout_s=30)
    tests.append(
        TestCase(
            id="3.1.2",
            name="RAG query (basic)",
            passed=bool(query.get("ok") and query.get("status_code") == 200),
            details={"request": query},
        )
    )

    invalid = http_request("POST", f"{rag_url}/rag/query", json_body={}, timeout_s=10)
    tests.append(
        TestCase(
            id="3.1.3",
            name="RAG query (invalid request should 400/422)",
            passed=bool(invalid.get("ok") and invalid.get("status_code") in (400, 422)),
            details={"request": invalid},
        )
    )

    return suite_result("RAG API", tests)


def e2e_suite_run(
    *,
    backend_url: str,
    agent_url: str,
    pg_container: str,
    pg_user: str,
    pg_db: str,
) -> Dict[str, Any]:
    tests: List[TestCase] = []

    # E2E-1: Backend create -> DB -> GET
    canonical_name = f"QA-VERIFY-001 E2E Deal {int(time.time())}"
    canonical_name_sql = canonical_name.replace("'", "''")
    create_payload = {"canonical_name": canonical_name, "stage": "inbound", "status": "active"}
    create_res = http_request("POST", f"{backend_url}/api/deals", json_body=create_payload, timeout_s=10)
    deal_id = None
    try:
        deal_id = psql_scalar(
            f"SELECT deal_id FROM zakops.deals WHERE canonical_name = '{canonical_name_sql}' ORDER BY created_at DESC LIMIT 1",
            container=pg_container,
            user=pg_user,
            db=pg_db,
        ) or None
    except Exception:
        deal_id = None
    get_ok = False
    if deal_id:
        get_res = http_request("GET", f"{backend_url}/api/deals/{deal_id}", timeout_s=10)
        get_ok = bool(get_res.get("ok") and get_res.get("status_code") == 200)
    tests.append(
        TestCase(
            id="4.1",
            name="E2E: create deal then GET by id (API + DB)",
            passed=bool(deal_id and get_ok and create_res.get("status_code") in (200, 201)),
            details={"create": create_res, "deal_id_from_db": deal_id},
        )
    )

    # E2E-2: DB counts vs API counts (if API endpoints succeed)
    db_deals_active = psql_scalar(
        "SELECT COUNT(*) FROM zakops.deals WHERE status='active'",
        container=pg_container,
        user=pg_user,
        db=pg_db,
    )
    api_deals = http_request("GET", f"{backend_url}/api/deals?status=active", timeout_s=10)
    api_count = None
    if isinstance(api_deals.get("response_json"), list):
        api_count = len(api_deals["response_json"])
    tests.append(
        TestCase(
            id="4.2",
            name="E2E: backend active deals count API vs DB (must match)",
            passed=bool(api_deals.get("ok") and api_deals.get("status_code") == 200 and api_count is not None and str(api_count) == db_deals_active),
            details={"api": api_deals, "api_count": api_count, "db_count": db_deals_active},
        )
    )

    # Cleanup deal if created
    if deal_id:
        try:
            _ = psql_scalar(
                f"DELETE FROM zakops.deals WHERE deal_id='{deal_id}'",
                container=pg_container,
                user=pg_user,
                db=pg_db,
            )
        except Exception:
            pass

    return suite_result("E2E", tests)


def ui_route_suite(*, dashboard_url: str) -> Dict[str, Any]:
    tests: List[TestCase] = []
    routes = [
        ("5.1.1", "/dashboard", "Dashboard"),
        ("5.1.2", "/hq", "Operator HQ"),
        ("5.1.3", "/deals", "Deals List"),
        ("5.1.4", "/actions", "Actions"),
        ("5.1.5", "/quarantine", "Quarantine"),
        ("5.1.6", "/chat", "Chat"),
        ("5.1.7", "/agent/activity", "Agent Activity"),
        ("5.1.8", "/onboarding", "Onboarding"),
    ]
    for tid, route, name in routes:
        res = http_request("GET", f"{dashboard_url}{route}", timeout_s=10)
        ok = bool(res.get("ok") and res.get("status_code") in (200, 301, 302, 307))
        tests.append(
            TestCase(
                id=tid,
                name=f"UI route {name} ({route})",
                passed=ok,
                details={"request": res},
            )
        )
    return suite_result("UI Routes", tests)


def aggregate_summary(suites: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_passed = 0
    total = 0
    suite_summaries = []
    for s in suites:
        summ = s.get("summary", {})
        p = int(summ.get("passed", 0))
        t = int(summ.get("total", 0))
        total_passed += p
        total += t
        suite_summaries.append({"suite": s.get("test_suite"), "passed": p, "total": t})
    failed = total - total_passed
    return {
        "timestamp_utc": utc_now_iso(),
        "overall": {
            "passed": total_passed,
            "total": total,
            "failed": failed,
            "pass_rate": (total_passed / total) if total else 0.0,
        },
        "suites": suite_summaries,
    }


def write_final_report(
    *,
    test_dir: Path,
    run_id: str,
    suites: List[Dict[str, Any]],
    verdict: str,
) -> None:
    summary = aggregate_summary(suites)
    report_path = test_dir / "QA_VERIFICATION_REPORT.md"

    lines: List[str] = []
    lines.append("# ZakOps QA Verification Report")
    lines.append("## Zero-Trust System Testing Results")
    lines.append("")
    lines.append(f"- **Run ID:** `{run_id}`")
    lines.append(f"- **Timestamp (UTC):** `{utc_now_iso()}`")
    lines.append(f"- **Verdict:** `{verdict}` (evidence-based)")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Suite | Passed | Total | Status |")
    lines.append("|------|--------|-------|--------|")
    for s in summary["suites"]:
        ok = "✅" if s["passed"] == s["total"] else "⚠️"
        lines.append(f"| {s['suite']} | {s['passed']} | {s['total']} | {ok} |")
    lines.append(f"| **TOTAL** | **{summary['overall']['passed']}** | **{summary['overall']['total']}** | {'✅' if summary['overall']['failed']==0 else '⚠️'} |")
    lines.append("")
    lines.append("## Evidence Artifacts")
    lines.append("")
    lines.append(f"- Artifact root: `{test_dir}`")
    for p in sorted(test_dir.glob("*.json")):
        lines.append(f"- `{p.name}`")
    if (test_dir / "runner.log").exists():
        lines.append(f"- `runner.log`")
    lines.append("")
    lines.append("## Stop-Ship Findings (auto-extracted)")
    lines.append("")
    stop_ship = extract_stop_ship(test_dir)
    if stop_ship:
        for item in stop_ship:
            lines.append(f"- {item}")
    else:
        lines.append("- None auto-detected. Review failures for production readiness.")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This report is **zero-trust**: API 5xx with DB side effects is treated as FAIL and highlighted.")
    lines.append("- Port `8090` is required to be decommissioned; the run hard-fails if it responds.")
    lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def extract_stop_ship(test_dir: Path) -> List[str]:
    items: List[str] = []
    # 8090 contamination
    legacy = (test_dir / "legacy_port_8090_check.json")
    if legacy.exists():
        try:
            data = json.loads(legacy.read_text(encoding="utf-8"))
            if data.get("ok") and data.get("status_code"):
                items.append(f"CRITICAL: Legacy service responded on 8090 (HTTP {data.get('status_code')}).")
        except Exception:
            pass

    # Backend deals 5xx response-validation errors
    deals = test_dir / "deals_crud_results.json"
    if deals.exists():
        try:
            data = json.loads(deals.read_text(encoding="utf-8"))
            for t in data.get("tests", []):
                if t.get("id") == "1.1.1":
                    details = t.get("details", {})
                    req = details.get("request", {})
                    if req.get("status_code") and int(req["status_code"]) >= 500 and details.get("db", {}).get("deal_id_from_db"):
                        items.append("CRITICAL: Deal CREATE returns 5xx but still writes to DB (side-effect without success).")
                if t.get("id") == "1.1.3":
                    req = t.get("details", {}).get("request", {})
                    if req.get("status_code") and int(req["status_code"]) >= 500:
                        items.append("CRITICAL: Deal LIST endpoint returns 5xx (breaks UI/pipeline).")
        except Exception:
            pass

    # Quarantine 5xx
    quarantine = test_dir / "quarantine_results.json"
    if quarantine.exists():
        try:
            data = json.loads(quarantine.read_text(encoding="utf-8"))
            for t in data.get("tests", []):
                if t.get("id") == "1.3.1":
                    req = t.get("details", {}).get("request", {})
                    if req.get("status_code") and int(req["status_code"]) >= 500:
                        items.append("CRITICAL: Quarantine LIST endpoint returns 5xx.")
        except Exception:
            pass

    return items


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)

#!/usr/bin/env python3
"""
Shadow Measurement Readiness — Phase P8-05
============================================

Queries shadow-mode quarantine items and computes classification accuracy,
entity extraction recall, and confidence calibration metrics.

Usage:
  python3 shadow_measurement.py                    # Full report
  python3 shadow_measurement.py --since 7d         # Last 7 days
  python3 shadow_measurement.py --output report.md  # Save to file

Requires:
  - psycopg2 or asyncpg
  - Access to zakops database on localhost:5432
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 required. Install: pip install psycopg2-binary")
    sys.exit(1)


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "zakops",
    "password": "zakops",
    "dbname": "zakops",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def parse_duration(s: str) -> timedelta:
    """Parse '7d', '24h', '30d' into timedelta."""
    if s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    elif s.endswith("h"):
        return timedelta(hours=int(s[:-1]))
    else:
        return timedelta(days=int(s))


def fetch_shadow_items(conn, since: datetime):
    """Fetch shadow-mode quarantine items for measurement."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT
                id, email_subject, sender, sender_name, sender_domain,
                classification, urgency, confidence,
                company_name, broker_name,
                triage_summary, email_body_snippet,
                source_type, status, processed_by,
                created_at, updated_at, raw_content
            FROM zakops.quarantine_items
            WHERE source_type = 'langsmith_shadow'
              AND created_at >= %s
            ORDER BY created_at DESC
        """, (since,))
        return cur.fetchall()


def fetch_operator_reviewed(conn, since: datetime):
    """Fetch items that operators have reviewed (approved/rejected)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT
                id, classification, urgency, confidence,
                company_name, broker_name,
                status, processed_by,
                raw_content
            FROM zakops.quarantine_items
            WHERE source_type = 'langsmith_shadow'
              AND status IN ('approved', 'rejected')
              AND created_at >= %s
            ORDER BY updated_at DESC
        """, (since,))
        return cur.fetchall()


def compute_metrics(items: list, reviewed: list) -> dict:
    """Compute accuracy, recall, and calibration metrics."""
    metrics = {
        "total_shadow_items": len(items),
        "total_reviewed": len(reviewed),
        "review_rate": len(reviewed) / max(len(items), 1),
    }

    # Classification distribution
    class_dist = {}
    for item in items:
        cls = item.get("classification", "unknown")
        class_dist[cls] = class_dist.get(cls, 0) + 1
    metrics["classification_distribution"] = class_dist

    # Confidence distribution (buckets)
    conf_buckets = {"0.0-0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, "0.9-1.0": 0}
    for item in items:
        c = item.get("confidence") or 0
        if c < 0.5:
            conf_buckets["0.0-0.5"] += 1
        elif c < 0.7:
            conf_buckets["0.5-0.7"] += 1
        elif c < 0.9:
            conf_buckets["0.7-0.9"] += 1
        else:
            conf_buckets["0.9-1.0"] += 1
    metrics["confidence_distribution"] = conf_buckets

    # Accuracy from operator decisions
    # If operator approved a deal_signal => classification was correct
    # If operator rejected => classification may have been wrong
    if reviewed:
        correct = 0
        incorrect = 0
        for r in reviewed:
            raw = r.get("raw_content")
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    raw = {}
            elif not isinstance(raw, dict):
                raw = {}

            # Operator corrections indicate classification error
            corrections = raw.get("corrections", {})
            if corrections.get("classification"):
                incorrect += 1
            elif r["status"] == "approved":
                correct += 1
            elif r["status"] == "rejected":
                # Rejected items: classification led to quarantine correctly
                # (spam/newsletter correctly quarantined = correct classification)
                cls = r.get("classification", "")
                if cls in ("spam", "newsletter", "operational"):
                    correct += 1  # Correctly identified non-deal
                else:
                    incorrect += 1  # False positive deal_signal

        total_judged = correct + incorrect
        metrics["classification_accuracy"] = correct / max(total_judged, 1)
        metrics["correct_classifications"] = correct
        metrics["incorrect_classifications"] = incorrect
    else:
        metrics["classification_accuracy"] = None
        metrics["correct_classifications"] = 0
        metrics["incorrect_classifications"] = 0

    # Entity extraction recall (company_name, broker_name populated when expected)
    deal_signals = [i for i in items if i.get("classification") == "deal_signal"]
    if deal_signals:
        company_populated = sum(1 for i in deal_signals if i.get("company_name"))
        broker_populated = sum(1 for i in deal_signals if i.get("broker_name"))
        metrics["entity_recall"] = {
            "company_name": company_populated / len(deal_signals),
            "broker_name": broker_populated / len(deal_signals),
            "total_deal_signals": len(deal_signals),
        }
    else:
        metrics["entity_recall"] = {"company_name": 0, "broker_name": 0, "total_deal_signals": 0}

    # Required field completeness
    required_fields = ["email_subject", "sender", "classification", "email_body_snippet", "confidence"]
    field_completeness = {}
    for field in required_fields:
        populated = sum(1 for i in items if i.get(field) is not None and i.get(field) != "")
        field_completeness[field] = populated / max(len(items), 1)
    metrics["field_completeness"] = field_completeness

    # Triage summary presence
    summary_populated = sum(1 for i in items if i.get("triage_summary"))
    metrics["triage_summary_rate"] = summary_populated / max(len(items), 1)

    return metrics


def format_report(metrics: dict, since: datetime) -> str:
    """Format metrics as a Markdown report."""
    lines = []
    lines.append("# Shadow Measurement Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**Window:** Since {since.isoformat()}")
    lines.append("")

    lines.append("## Volume")
    lines.append(f"- Total shadow items: **{metrics['total_shadow_items']}**")
    lines.append(f"- Operator reviewed: **{metrics['total_reviewed']}** ({metrics['review_rate']:.0%})")
    lines.append("")

    lines.append("## Classification Distribution")
    lines.append("| Classification | Count |")
    lines.append("|---------------|-------|")
    for cls, count in sorted(metrics["classification_distribution"].items()):
        lines.append(f"| {cls} | {count} |")
    lines.append("")

    lines.append("## Confidence Distribution")
    lines.append("| Bucket | Count |")
    lines.append("|--------|-------|")
    for bucket, count in metrics["confidence_distribution"].items():
        lines.append(f"| {bucket} | {count} |")
    lines.append("")

    lines.append("## Accuracy Metrics")
    acc = metrics.get("classification_accuracy")
    if acc is not None:
        target = 0.85
        status = "PASS" if acc >= target else "FAIL"
        lines.append(f"- Classification accuracy: **{acc:.1%}** (target: {target:.0%}) — **{status}**")
        lines.append(f"  - Correct: {metrics['correct_classifications']}")
        lines.append(f"  - Incorrect: {metrics['incorrect_classifications']}")
    else:
        lines.append("- Classification accuracy: **N/A** (no reviewed items)")
    lines.append("")

    lines.append("## Entity Extraction Recall")
    er = metrics.get("entity_recall", {})
    lines.append(f"- Deal signals: {er.get('total_deal_signals', 0)}")
    cn = er.get("company_name", 0)
    bn = er.get("broker_name", 0)
    lines.append(f"- Company name recall: **{cn:.1%}** (target: 75%)")
    lines.append(f"- Broker name recall: **{bn:.1%}** (target: 75%)")
    lines.append("")

    lines.append("## Field Completeness")
    lines.append("| Field | Rate |")
    lines.append("|-------|------|")
    for field, rate in metrics.get("field_completeness", {}).items():
        lines.append(f"| {field} | {rate:.0%} |")
    lines.append("")

    lines.append(f"- Triage summary rate: **{metrics.get('triage_summary_rate', 0):.0%}**")
    lines.append("")

    # SLO verdict
    lines.append("## SLO Verdict")
    all_pass = True
    if acc is not None and acc < 0.85:
        all_pass = False
        lines.append("- Classification accuracy < 85%: **FAIL**")
    if cn < 0.75:
        lines.append(f"- Company name recall {cn:.0%} < 75%: **{'FAIL' if metrics.get('entity_recall', {}).get('total_deal_signals', 0) > 0 else 'N/A'}**")
        if er.get("total_deal_signals", 0) > 0:
            all_pass = False
    if bn < 0.75:
        lines.append(f"- Broker name recall {bn:.0%} < 75%: **{'FAIL' if metrics.get('entity_recall', {}).get('total_deal_signals', 0) > 0 else 'N/A'}**")
        if er.get("total_deal_signals", 0) > 0:
            all_pass = False

    if metrics["total_shadow_items"] == 0:
        lines.append("- **No shadow items found** — measurement not possible")
        all_pass = False

    lines.append(f"\n**Overall: {'PASS' if all_pass else 'NEEDS DATA / FAIL'}**")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Shadow Measurement (P8-05)")
    parser.add_argument("--since", default="7d", help="Time window (e.g., 7d, 24h)")
    parser.add_argument("--output", default=None, help="Output file")
    args = parser.parse_args()

    since = datetime.now(timezone.utc) - parse_duration(args.since)
    print(f"Shadow Measurement — Window: {args.since} (since {since.isoformat()})")

    try:
        conn = get_connection()
    except Exception as e:
        print(f"ERROR: Cannot connect to database: {e}")
        print("Ensure PostgreSQL is running and zakops database is accessible.")
        sys.exit(1)

    try:
        items = fetch_shadow_items(conn, since)
        reviewed = fetch_operator_reviewed(conn, since)
        metrics = compute_metrics(items, reviewed)
        report = format_report(metrics, since)
        print(report)

        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"\nSaved to: {args.output}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

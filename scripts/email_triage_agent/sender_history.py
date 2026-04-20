"""
Sender History Database - tracks sender patterns for improved triage accuracy.

This module provides:
1. Persistent storage of sender statistics (email frequency, classifications, roles)
2. Backfill capability from existing triage data
3. Query API for enriching triage decisions with sender context
"""
from __future__ import annotations

import logging
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

_log = logging.getLogger(__name__)

# Default path for sender history database
_DEFAULT_DB_PATH = Path(os.getenv("SENDER_HISTORY_DB_PATH", "/home/zaks/DataRoom/.deal-registry/sender_history.db"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _extract_email(sender: str) -> Optional[str]:
    """Extract email address from sender string like 'Name <email@domain.com>'."""
    raw = (sender or "").strip()
    if not raw:
        return None
    # Try to extract from angle brackets
    m = re.search(r"<([^>]+@[^>]+)>", raw)
    if m:
        return m.group(1).lower().strip()
    # If no brackets, check if it's a bare email
    if "@" in raw and " " not in raw:
        return raw.lower().strip()
    return None


def _extract_domain(email: str) -> Optional[str]:
    """Extract domain from email address."""
    raw = (email or "").strip().lower()
    if "@" not in raw:
        return None
    return raw.split("@")[-1].strip() or None


@dataclass(frozen=True)
class SenderProfile:
    """Aggregated sender statistics."""
    email: str
    domain: str
    first_seen: str
    last_seen: str
    total_emails: int
    deal_signals: int
    non_deals: int
    operational: int
    unknown: int
    most_common_role: Optional[str]
    deal_rate: float  # Percentage of emails classified as DEAL_SIGNAL


@dataclass(frozen=True)
class DomainProfile:
    """Aggregated domain statistics."""
    domain: str
    first_seen: str
    last_seen: str
    unique_senders: int
    total_emails: int
    deal_signals: int
    non_deals: int
    deal_rate: float


class SenderHistoryDB:
    """SQLite-backed sender history store."""

    def __init__(self, path: Optional[str | Path] = None):
        self.path = Path(path) if path else _DEFAULT_DB_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self._init()

    def close(self) -> None:
        self.conn.close()

    def _init(self) -> None:
        cur = self.conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")

        # Per-email sender records
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sender_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                sender_domain TEXT NOT NULL,
                sender_name TEXT,
                subject_prefix TEXT,
                classification TEXT,
                confidence REAL,
                sender_role_guess TEXT,
                deal_id TEXT,
                received_at TEXT,
                recorded_at TEXT NOT NULL,
                UNIQUE(message_id, sender_email)
            );
            """
        )

        # Aggregated sender stats (materialized for fast queries)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sender_profiles (
                sender_email TEXT PRIMARY KEY,
                sender_domain TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                total_emails INTEGER NOT NULL DEFAULT 0,
                deal_signals INTEGER NOT NULL DEFAULT 0,
                non_deals INTEGER NOT NULL DEFAULT 0,
                operational INTEGER NOT NULL DEFAULT 0,
                unknown INTEGER NOT NULL DEFAULT 0,
                most_common_role TEXT,
                updated_at TEXT NOT NULL
            );
            """
        )

        # Aggregated domain stats
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS domain_profiles (
                domain TEXT PRIMARY KEY,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                unique_senders INTEGER NOT NULL DEFAULT 0,
                total_emails INTEGER NOT NULL DEFAULT 0,
                deal_signals INTEGER NOT NULL DEFAULT 0,
                non_deals INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            """
        )

        # Indexes for common queries
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sender_emails_email ON sender_emails(sender_email);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sender_emails_domain ON sender_emails(sender_domain);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sender_emails_classification ON sender_emails(classification);")

        self.conn.commit()

    def record_email(
        self,
        *,
        message_id: str,
        sender: str,
        subject: str,
        classification: str,
        confidence: float,
        sender_role_guess: Optional[str] = None,
        deal_id: Optional[str] = None,
        received_at: Optional[str] = None,
    ) -> bool:
        """
        Record a processed email for sender history tracking.
        Returns True if recorded, False if duplicate or invalid.
        """
        sender_email = _extract_email(sender)
        if not sender_email:
            return False

        sender_domain = _extract_domain(sender_email)
        if not sender_domain:
            return False

        # Extract sender name (part before <email>)
        sender_name = None
        if "<" in sender:
            sender_name = sender.split("<")[0].strip().strip('"').strip("'") or None

        # Truncate subject to prefix (first 100 chars)
        subject_prefix = (subject or "")[:100].strip() or None

        now = _now_iso()
        cur = self.conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO sender_emails (
                    message_id, sender_email, sender_domain, sender_name,
                    subject_prefix, classification, confidence, sender_role_guess,
                    deal_id, received_at, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_id, sender_email) DO UPDATE SET
                    classification=excluded.classification,
                    confidence=excluded.confidence,
                    sender_role_guess=excluded.sender_role_guess,
                    deal_id=excluded.deal_id,
                    recorded_at=excluded.recorded_at
                """,
                (
                    message_id,
                    sender_email,
                    sender_domain,
                    sender_name,
                    subject_prefix,
                    classification,
                    float(confidence),
                    sender_role_guess,
                    deal_id,
                    received_at or now,
                    now,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            _log.warning("sender_history_record_failed email=%s error=%s", sender_email, str(e)[:100])
            return False

    def refresh_sender_profile(self, sender_email: str) -> Optional[SenderProfile]:
        """Recalculate and cache aggregated stats for a sender."""
        sender_email = (sender_email or "").strip().lower()
        if not sender_email:
            return None

        cur = self.conn.cursor()

        # Aggregate from raw email records
        cur.execute(
            """
            SELECT
                sender_email,
                sender_domain,
                MIN(received_at) as first_seen,
                MAX(received_at) as last_seen,
                COUNT(*) as total_emails,
                SUM(CASE WHEN classification = 'DEAL_SIGNAL' THEN 1 ELSE 0 END) as deal_signals,
                SUM(CASE WHEN classification IN ('NON_DEAL', 'NEWSLETTER', 'MARKETING') THEN 1 ELSE 0 END) as non_deals,
                SUM(CASE WHEN classification = 'OPERATIONAL' THEN 1 ELSE 0 END) as operational,
                SUM(CASE WHEN classification IS NULL OR classification = '' THEN 1 ELSE 0 END) as unknown
            FROM sender_emails
            WHERE sender_email = ?
            GROUP BY sender_email, sender_domain
            """,
            (sender_email,),
        )
        row = cur.fetchone()
        if not row:
            return None

        # Find most common role
        cur.execute(
            """
            SELECT sender_role_guess, COUNT(*) as cnt
            FROM sender_emails
            WHERE sender_email = ? AND sender_role_guess IS NOT NULL AND sender_role_guess != ''
            GROUP BY sender_role_guess
            ORDER BY cnt DESC
            LIMIT 1
            """,
            (sender_email,),
        )
        role_row = cur.fetchone()
        most_common_role = role_row["sender_role_guess"] if role_row else None

        now = _now_iso()
        total = int(row["total_emails"])
        deal_signals = int(row["deal_signals"])
        deal_rate = (deal_signals / total) if total > 0 else 0.0

        # Upsert profile
        cur.execute(
            """
            INSERT INTO sender_profiles (
                sender_email, sender_domain, first_seen, last_seen,
                total_emails, deal_signals, non_deals, operational, unknown,
                most_common_role, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sender_email) DO UPDATE SET
                last_seen=excluded.last_seen,
                total_emails=excluded.total_emails,
                deal_signals=excluded.deal_signals,
                non_deals=excluded.non_deals,
                operational=excluded.operational,
                unknown=excluded.unknown,
                most_common_role=excluded.most_common_role,
                updated_at=excluded.updated_at
            """,
            (
                sender_email,
                row["sender_domain"],
                row["first_seen"],
                row["last_seen"],
                total,
                deal_signals,
                int(row["non_deals"]),
                int(row["operational"]),
                int(row["unknown"]),
                most_common_role,
                now,
            ),
        )
        self.conn.commit()

        return SenderProfile(
            email=sender_email,
            domain=row["sender_domain"],
            first_seen=row["first_seen"],
            last_seen=row["last_seen"],
            total_emails=total,
            deal_signals=deal_signals,
            non_deals=int(row["non_deals"]),
            operational=int(row["operational"]),
            unknown=int(row["unknown"]),
            most_common_role=most_common_role,
            deal_rate=deal_rate,
        )

    def refresh_domain_profile(self, domain: str) -> Optional[DomainProfile]:
        """Recalculate and cache aggregated stats for a domain."""
        domain = (domain or "").strip().lower()
        if not domain:
            return None

        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT
                sender_domain,
                MIN(received_at) as first_seen,
                MAX(received_at) as last_seen,
                COUNT(DISTINCT sender_email) as unique_senders,
                COUNT(*) as total_emails,
                SUM(CASE WHEN classification = 'DEAL_SIGNAL' THEN 1 ELSE 0 END) as deal_signals,
                SUM(CASE WHEN classification IN ('NON_DEAL', 'NEWSLETTER', 'MARKETING') THEN 1 ELSE 0 END) as non_deals
            FROM sender_emails
            WHERE sender_domain = ?
            GROUP BY sender_domain
            """,
            (domain,),
        )
        row = cur.fetchone()
        if not row:
            return None

        now = _now_iso()
        total = int(row["total_emails"])
        deal_signals = int(row["deal_signals"])
        deal_rate = (deal_signals / total) if total > 0 else 0.0

        cur.execute(
            """
            INSERT INTO domain_profiles (
                domain, first_seen, last_seen, unique_senders,
                total_emails, deal_signals, non_deals, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(domain) DO UPDATE SET
                last_seen=excluded.last_seen,
                unique_senders=excluded.unique_senders,
                total_emails=excluded.total_emails,
                deal_signals=excluded.deal_signals,
                non_deals=excluded.non_deals,
                updated_at=excluded.updated_at
            """,
            (
                domain,
                row["first_seen"],
                row["last_seen"],
                int(row["unique_senders"]),
                total,
                deal_signals,
                int(row["non_deals"]),
                now,
            ),
        )
        self.conn.commit()

        return DomainProfile(
            domain=domain,
            first_seen=row["first_seen"],
            last_seen=row["last_seen"],
            unique_senders=int(row["unique_senders"]),
            total_emails=total,
            deal_signals=deal_signals,
            non_deals=int(row["non_deals"]),
            deal_rate=deal_rate,
        )

    def get_sender_profile(self, sender_email: str) -> Optional[SenderProfile]:
        """Get cached sender profile (does not refresh)."""
        sender_email = (sender_email or "").strip().lower()
        if not sender_email:
            return None

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM sender_profiles WHERE sender_email = ?", (sender_email,))
        row = cur.fetchone()
        if not row:
            return None

        total = int(row["total_emails"])
        deal_signals = int(row["deal_signals"])

        return SenderProfile(
            email=row["sender_email"],
            domain=row["sender_domain"],
            first_seen=row["first_seen"],
            last_seen=row["last_seen"],
            total_emails=total,
            deal_signals=deal_signals,
            non_deals=int(row["non_deals"]),
            operational=int(row["operational"]),
            unknown=int(row["unknown"]),
            most_common_role=row["most_common_role"],
            deal_rate=(deal_signals / total) if total > 0 else 0.0,
        )

    def get_domain_profile(self, domain: str) -> Optional[DomainProfile]:
        """Get cached domain profile (does not refresh)."""
        domain = (domain or "").strip().lower()
        if not domain:
            return None

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM domain_profiles WHERE domain = ?", (domain,))
        row = cur.fetchone()
        if not row:
            return None

        total = int(row["total_emails"])
        deal_signals = int(row["deal_signals"])

        return DomainProfile(
            domain=row["domain"],
            first_seen=row["first_seen"],
            last_seen=row["last_seen"],
            unique_senders=int(row["unique_senders"]),
            total_emails=total,
            deal_signals=deal_signals,
            non_deals=int(row["non_deals"]),
            deal_rate=(deal_signals / total) if total > 0 else 0.0,
        )

    def get_sender_context(self, sender: str) -> Dict[str, Any]:
        """
        Get sender context for triage enrichment.
        Returns a dict suitable for including in LLM prompts or triage metadata.
        """
        sender_email = _extract_email(sender)
        if not sender_email:
            return {"known_sender": False}

        profile = self.get_sender_profile(sender_email)
        if not profile:
            # Try to refresh from raw data
            profile = self.refresh_sender_profile(sender_email)

        if not profile:
            return {"known_sender": False, "sender_email": sender_email}

        domain_profile = self.get_domain_profile(profile.domain)

        return {
            "known_sender": True,
            "sender_email": profile.email,
            "sender_domain": profile.domain,
            "total_emails_from_sender": profile.total_emails,
            "sender_deal_rate": round(profile.deal_rate, 2),
            "sender_most_common_role": profile.most_common_role,
            "domain_total_emails": domain_profile.total_emails if domain_profile else 0,
            "domain_deal_rate": round(domain_profile.deal_rate, 2) if domain_profile else 0.0,
            "domain_unique_senders": domain_profile.unique_senders if domain_profile else 0,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM sender_emails")
        total_records = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT sender_email) FROM sender_emails")
        unique_senders = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT sender_domain) FROM sender_emails")
        unique_domains = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM sender_emails WHERE classification = 'DEAL_SIGNAL'")
        deal_signals = cur.fetchone()[0]

        return {
            "total_records": total_records,
            "unique_senders": unique_senders,
            "unique_domains": unique_domains,
            "deal_signals": deal_signals,
            "deal_rate": round(deal_signals / total_records, 3) if total_records > 0 else 0.0,
        }

    def list_top_senders(self, *, limit: int = 20, min_emails: int = 2) -> List[SenderProfile]:
        """List top senders by email volume."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM sender_profiles
            WHERE total_emails >= ?
            ORDER BY total_emails DESC
            LIMIT ?
            """,
            (min_emails, limit),
        )
        rows = cur.fetchall()
        results = []
        for row in rows:
            total = int(row["total_emails"])
            deal_signals = int(row["deal_signals"])
            results.append(
                SenderProfile(
                    email=row["sender_email"],
                    domain=row["sender_domain"],
                    first_seen=row["first_seen"],
                    last_seen=row["last_seen"],
                    total_emails=total,
                    deal_signals=deal_signals,
                    non_deals=int(row["non_deals"]),
                    operational=int(row["operational"]),
                    unknown=int(row["unknown"]),
                    most_common_role=row["most_common_role"],
                    deal_rate=(deal_signals / total) if total > 0 else 0.0,
                )
            )
        return results

    def list_top_domains(self, *, limit: int = 20, min_emails: int = 3) -> List[DomainProfile]:
        """List top domains by email volume."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM domain_profiles
            WHERE total_emails >= ?
            ORDER BY total_emails DESC
            LIMIT ?
            """,
            (min_emails, limit),
        )
        rows = cur.fetchall()
        results = []
        for row in rows:
            total = int(row["total_emails"])
            deal_signals = int(row["deal_signals"])
            results.append(
                DomainProfile(
                    domain=row["domain"],
                    first_seen=row["first_seen"],
                    last_seen=row["last_seen"],
                    unique_senders=int(row["unique_senders"]),
                    total_emails=total,
                    deal_signals=deal_signals,
                    non_deals=int(row["non_deals"]),
                    deal_rate=(deal_signals / total) if total > 0 else 0.0,
                )
            )
        return results


def backfill_from_feedback(db: SenderHistoryDB, feedback_path: Path) -> Dict[str, int]:
    """
    Backfill sender history from triage_feedback.jsonl.
    Returns counts of processed/skipped/errors.
    """
    import json

    if not feedback_path.exists():
        return {"processed": 0, "skipped": 0, "errors": 0, "error": "file_not_found"}

    processed = 0
    skipped = 0
    errors = 0

    for line in feedback_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            entry = json.loads(line)
        except Exception:
            errors += 1
            continue

        if not isinstance(entry, dict):
            skipped += 1
            continue

        message_id = str(entry.get("message_id") or "").strip()
        sender = str(entry.get("sender") or "").strip()
        subject = str(entry.get("subject_prefix") or "").strip()
        classification = str(entry.get("classification") or "").strip()
        confidence = float(entry.get("confidence") or 0.0)
        deal_id = str(entry.get("deal_id") or "").strip() or None
        timestamp = str(entry.get("timestamp") or "").strip() or None

        if not message_id or not sender:
            skipped += 1
            continue

        # Map decision to classification if classification is missing
        if not classification:
            decision = str(entry.get("decision") or "").strip().lower()
            if decision == "approve":
                classification = "DEAL_SIGNAL"
            elif decision == "reject":
                classification = "NON_DEAL"

        if db.record_email(
            message_id=message_id,
            sender=sender,
            subject=subject,
            classification=classification,
            confidence=confidence,
            deal_id=deal_id,
            received_at=timestamp,
        ):
            processed += 1
        else:
            skipped += 1

    return {"processed": processed, "skipped": skipped, "errors": errors}


def backfill_from_quarantine(db: SenderHistoryDB, quarantine_root: Path) -> Dict[str, int]:
    """
    Backfill sender history from quarantine directories.
    Each directory should contain a triage_result.json with sender/classification info.
    """
    import json

    if not quarantine_root.exists():
        return {"processed": 0, "skipped": 0, "errors": 0, "error": "dir_not_found"}

    processed = 0
    skipped = 0
    errors = 0

    for qdir in quarantine_root.iterdir():
        if not qdir.is_dir():
            continue

        result_file = qdir / "triage_result.json"
        if not result_file.exists():
            skipped += 1
            continue

        try:
            data = json.loads(result_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            errors += 1
            continue

        if not isinstance(data, dict):
            skipped += 1
            continue

        message_id = str(data.get("message_id") or qdir.name).strip()
        sender = str(data.get("sender") or data.get("from") or "").strip()
        subject = str(data.get("subject") or "").strip()[:100]
        classification = str(data.get("classification") or "").strip()
        confidence = float(data.get("confidence") or 0.0)
        deal_id = str(data.get("deal_id") or "").strip() or None
        received_at = str(data.get("received_at") or data.get("date") or "").strip() or None

        # Try to get sender_role_guess from nested structure
        sender_role = None
        actors = data.get("actors")
        if isinstance(actors, dict):
            sender_role = str(actors.get("sender_role_guess") or "").strip() or None

        if not sender:
            skipped += 1
            continue

        if db.record_email(
            message_id=message_id,
            sender=sender,
            subject=subject,
            classification=classification,
            confidence=confidence,
            sender_role_guess=sender_role,
            deal_id=deal_id,
            received_at=received_at,
        ):
            processed += 1
        else:
            skipped += 1

    return {"processed": processed, "skipped": skipped, "errors": errors}


def refresh_all_profiles(db: SenderHistoryDB) -> Dict[str, int]:
    """Refresh all sender and domain profiles from raw email data."""
    cur = db.conn.cursor()

    # Get all unique senders
    cur.execute("SELECT DISTINCT sender_email FROM sender_emails")
    senders = [row[0] for row in cur.fetchall()]

    # Get all unique domains
    cur.execute("SELECT DISTINCT sender_domain FROM sender_emails")
    domains = [row[0] for row in cur.fetchall()]

    sender_count = 0
    for email in senders:
        if db.refresh_sender_profile(email):
            sender_count += 1

    domain_count = 0
    for domain in domains:
        if db.refresh_domain_profile(domain):
            domain_count += 1

    return {"senders_refreshed": sender_count, "domains_refreshed": domain_count}


def main() -> int:
    """CLI for sender history management."""
    import argparse

    parser = argparse.ArgumentParser(description="Sender History Database Management")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # backfill command
    bf = sub.add_parser("backfill", help="Backfill from feedback and quarantine data")
    bf.add_argument("--feedback", default="/home/zaks/DataRoom/.deal-registry/triage_feedback.jsonl")
    bf.add_argument("--quarantine", default="/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE")
    bf.add_argument("--db", default=str(_DEFAULT_DB_PATH))

    # stats command
    st = sub.add_parser("stats", help="Show database statistics")
    st.add_argument("--db", default=str(_DEFAULT_DB_PATH))

    # top-senders command
    ts = sub.add_parser("top-senders", help="List top senders")
    ts.add_argument("--limit", type=int, default=20)
    ts.add_argument("--min-emails", type=int, default=2)
    ts.add_argument("--db", default=str(_DEFAULT_DB_PATH))

    # top-domains command
    td = sub.add_parser("top-domains", help="List top domains")
    td.add_argument("--limit", type=int, default=20)
    td.add_argument("--min-emails", type=int, default=3)
    td.add_argument("--db", default=str(_DEFAULT_DB_PATH))

    # lookup command
    lk = sub.add_parser("lookup", help="Lookup sender or domain")
    lk.add_argument("query", help="Email address or domain to lookup")
    lk.add_argument("--db", default=str(_DEFAULT_DB_PATH))

    args = parser.parse_args()

    db = SenderHistoryDB(path=args.db)

    try:
        if args.cmd == "backfill":
            print(f"Backfilling from feedback: {args.feedback}")
            fb_result = backfill_from_feedback(db, Path(args.feedback))
            print(f"  Feedback: processed={fb_result['processed']} skipped={fb_result['skipped']} errors={fb_result['errors']}")

            print(f"Backfilling from quarantine: {args.quarantine}")
            q_result = backfill_from_quarantine(db, Path(args.quarantine))
            print(f"  Quarantine: processed={q_result['processed']} skipped={q_result['skipped']} errors={q_result['errors']}")

            print("Refreshing profiles...")
            r_result = refresh_all_profiles(db)
            print(f"  Refreshed: {r_result['senders_refreshed']} senders, {r_result['domains_refreshed']} domains")

            stats = db.get_stats()
            print(f"\nDatabase stats: {stats}")
            return 0

        if args.cmd == "stats":
            stats = db.get_stats()
            print(f"Total records: {stats['total_records']}")
            print(f"Unique senders: {stats['unique_senders']}")
            print(f"Unique domains: {stats['unique_domains']}")
            print(f"Deal signals: {stats['deal_signals']}")
            print(f"Deal rate: {stats['deal_rate']:.1%}")
            return 0

        if args.cmd == "top-senders":
            senders = db.list_top_senders(limit=args.limit, min_emails=args.min_emails)
            print(f"{'Email':<40} {'Total':>6} {'Deals':>6} {'Rate':>6} {'Role':<12}")
            print("-" * 80)
            for s in senders:
                print(f"{s.email:<40} {s.total_emails:>6} {s.deal_signals:>6} {s.deal_rate:>5.0%} {(s.most_common_role or '-'):<12}")
            return 0

        if args.cmd == "top-domains":
            domains = db.list_top_domains(limit=args.limit, min_emails=args.min_emails)
            print(f"{'Domain':<30} {'Senders':>8} {'Total':>6} {'Deals':>6} {'Rate':>6}")
            print("-" * 70)
            for d in domains:
                print(f"{d.domain:<30} {d.unique_senders:>8} {d.total_emails:>6} {d.deal_signals:>6} {d.deal_rate:>5.0%}")
            return 0

        if args.cmd == "lookup":
            query = args.query.strip().lower()
            if "@" in query:
                profile = db.refresh_sender_profile(query)
                if profile:
                    print(f"Sender: {profile.email}")
                    print(f"Domain: {profile.domain}")
                    print(f"First seen: {profile.first_seen}")
                    print(f"Last seen: {profile.last_seen}")
                    print(f"Total emails: {profile.total_emails}")
                    print(f"Deal signals: {profile.deal_signals} ({profile.deal_rate:.0%})")
                    print(f"Non-deals: {profile.non_deals}")
                    print(f"Most common role: {profile.most_common_role or '-'}")
                else:
                    print(f"No data found for sender: {query}")
            else:
                profile = db.refresh_domain_profile(query)
                if profile:
                    print(f"Domain: {profile.domain}")
                    print(f"First seen: {profile.first_seen}")
                    print(f"Last seen: {profile.last_seen}")
                    print(f"Unique senders: {profile.unique_senders}")
                    print(f"Total emails: {profile.total_emails}")
                    print(f"Deal signals: {profile.deal_signals} ({profile.deal_rate:.0%})")
                    print(f"Non-deals: {profile.non_deals}")
                else:
                    print(f"No data found for domain: {query}")
            return 0

    finally:
        db.close()

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

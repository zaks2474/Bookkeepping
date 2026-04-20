from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class EmailStateRow:
    message_id: str
    thread_id: str
    status: str
    attempts: int
    processed_at: Optional[str]
    classification: Optional[str]
    urgency: Optional[str]
    deal_id: Optional[str]
    quarantine_dir: Optional[str]
    last_error: Optional[str]
    body_hash: Optional[str]


class EmailTriageStateDB:
    def __init__(self, path: str | Path):
        self.path = Path(path)
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
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS email_triage_messages (
                message_id TEXT PRIMARY KEY,
                thread_id TEXT,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                processed_at TEXT,
                classification TEXT,
                urgency TEXT,
                deal_id TEXT,
                quarantine_dir TEXT,
                last_error TEXT,
                body_hash TEXT
            );
            """
        )
        self.conn.commit()

    def get(self, message_id: str) -> Optional[EmailStateRow]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM email_triage_messages WHERE message_id=?", (message_id,))
        row = cur.fetchone()
        return EmailStateRow(**dict(row)) if row else None

    def mark_started(self, *, message_id: str, thread_id: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO email_triage_messages (message_id, thread_id, status, attempts)
            VALUES (?, ?, 'processing', 1)
            ON CONFLICT(message_id) DO UPDATE SET
                thread_id=excluded.thread_id,
                status='processing',
                attempts=attempts+1
            """,
            (message_id, thread_id),
        )
        self.conn.commit()

    def mark_processed(
        self,
        *,
        message_id: str,
        processed_at: str,
        classification: str,
        urgency: str,
        deal_id: Optional[str],
        quarantine_dir: Optional[str],
        body_hash: Optional[str],
    ) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE email_triage_messages
            SET status='processed',
                processed_at=?,
                classification=?,
                urgency=?,
                deal_id=?,
                quarantine_dir=?,
                last_error=NULL,
                body_hash=?
            WHERE message_id=?
            """,
            (processed_at, classification, urgency, deal_id, quarantine_dir, body_hash, message_id),
        )
        self.conn.commit()

    def mark_failed(self, *, message_id: str, error: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE email_triage_messages
            SET status='failed',
                last_error=?
            WHERE message_id=?
            """,
            (str(error or "")[:2000], message_id),
        )
        self.conn.commit()


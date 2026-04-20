import tempfile
import unittest
from pathlib import Path

from email_triage_agent.state_db import EmailTriageStateDB


class TestStateDB(unittest.TestCase):
    def test_state_db_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "state.db"
            db = EmailTriageStateDB(db_path)
            try:
                self.assertIsNone(db.get("m1"))
                db.mark_started(message_id="m1", thread_id="t1")
                row = db.get("m1")
                self.assertIsNotNone(row)
                self.assertEqual(row.status, "processing")
                db.mark_processed(
                    message_id="m1",
                    processed_at="2026-01-01T00:00:00+00:00",
                    classification="DEAL_SIGNAL",
                    urgency="HIGH",
                    deal_id="DEAL-2025-001",
                    quarantine_dir="/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/m1",
                    body_hash="deadbeef",
                )
                row2 = db.get("m1")
                self.assertEqual(row2.status, "processed")
                self.assertEqual(row2.deal_id, "DEAL-2025-001")
            finally:
                db.close()


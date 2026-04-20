import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from email_triage_agent.gmail_mcp import EmailAttachment, EmailMessage
from email_triage_agent.run_once import RunnerConfig, process_one_message, utcnow_iso
from email_triage_agent.sender_history import SenderHistoryDB
from email_triage_agent.state_db import EmailTriageStateDB
from email_triage_agent.triage_logic import LinkEntity, TriageClassification, TriageDecision


@dataclass(frozen=True)
class _CreateResult:
    created_new: bool
    action_id: str
    status: str


class _FakeActions:
    def __init__(self) -> None:
        self.created: List[Dict[str, Any]] = []
        self.approved: List[Dict[str, Any]] = []
        self.executed: List[Dict[str, Any]] = []

    def create_action(self, **kwargs: Any) -> _CreateResult:
        self.created.append(dict(kwargs))
        return _CreateResult(created_new=True, action_id="ACTION-1", status="PENDING_APPROVAL")

    def approve_action(self, *, action_id: str, approved_by: str, timeout_seconds: int = 15) -> str:
        self.approved.append({"action_id": action_id, "approved_by": approved_by})
        return "READY"

    def execute_action(self, *, action_id: str, requested_by: str, timeout_seconds: int = 15) -> str:
        self.executed.append({"action_id": action_id, "requested_by": requested_by})
        return "READY"


class _FakeGmail:
    def __init__(self, message: EmailMessage) -> None:
        self._message = message
        self.labels_added: List[Dict[str, Any]] = []
        self.marked_read: List[str] = []
        self.downloaded: List[Dict[str, Any]] = []

    async def read_email(self, *, message_id: str) -> EmailMessage:
        return self._message

    async def add_labels(self, *, message_id: str, label_ids: List[str]) -> None:
        self.labels_added.append({"message_id": message_id, "label_ids": list(label_ids)})

    async def mark_as_read(self, *, message_id: str) -> None:
        self.marked_read.append(message_id)

    async def download_attachment(
        self, *, message_id: str, attachment_id: str, save_dir: str, filename: Optional[str] = None
    ) -> str:
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        name = filename or f"{attachment_id}.bin"
        path = Path(save_dir) / name
        path.write_bytes(b"test")
        self.downloaded.append({"message_id": message_id, "attachment_id": attachment_id, "path": str(path)})
        return str(path)


def _decision_with_links_and_attachments(msg: EmailMessage) -> TriageDecision:
    return TriageDecision(
        classification=TriageClassification(classification="DEAL_SIGNAL", urgency="HIGH", reason="deal-signal"),
        sender_email="broker@example.com",
        company="ExampleCo",
        links=[
            LinkEntity(type="dataroom", url="https://example.com/dataroom?token=abc", auth_required=True, vendor_hint="dataroom"),
        ],
        attachments=list(msg.attachments),
        labels_to_add=["ZakOps/Needs-Review"],
        needs_reply=False,
        needs_docs=False,
        quarantine=False,
        eligible_for_llm=True,
        body_fingerprint="test",
    )


class ThreadRoutingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory(dir="/home/zaks/tmp")
        self.tmp_path = Path(self._tmpdir.name)
        self.quarantine_root = self.tmp_path / "quarantine"
        self.db_path = self.tmp_path / "state.db"

        self.state_db = EmailTriageStateDB(self.db_path)
        self.sender_history_db = SenderHistoryDB(self.tmp_path / "sender_history.db")

        self.cfg = RunnerConfig(
            query="",
            max_per_run=1,
            quarantine_root=self.quarantine_root,
            state_db_path=self.db_path,
            sender_history_db_path=self.tmp_path / "sender_history.db",
            deal_registry_path=self.tmp_path / "deal_registry.json",
            dry_run=False,
            mark_as_read=False,
            max_attachment_mb=25,
            safe_exts={"pdf"},
            unsafe_exts={"exe"},
            vendor_patterns_path=self.tmp_path / "vendor_patterns.md",
            actions_base_url="http://localhost:8090",
            enable_actions=True,
        )

        self.label_ids = {
            "ZakOps/Processed": "Label_Processed",
            "ZakOps/Deal": "Label_Deal",
            "ZakOps/NonDeal": "Label_NonDeal",
            "ZakOps/Needs-Review": "Label_NeedsReview",
        }

    def tearDown(self) -> None:
        self.state_db.close()
        self.sender_history_db.close()
        self._tmpdir.cleanup()

    async def test_known_deal_thread_creates_append_action_and_marks_processed(self) -> None:
        msg = EmailMessage(
            message_id="m1",
            thread_id="t1",
            subject="Re: ExampleCo teaser",
            sender="Broker <broker@example.com>",
            to="me@example.com",
            date=utcnow_iso(),
            body="Follow-up with an attachment.",
            attachments=[EmailAttachment(attachment_id="a1", filename="teaser.pdf", mime_type="application/pdf", size_bytes=123)],
        )
        gmail = _FakeGmail(msg)
        actions = _FakeActions()

        with patch("email_triage_agent.run_once.decide_actions_and_labels", side_effect=lambda **_: _decision_with_links_and_attachments(msg)):
            await process_one_message(
                gmail=gmail,
                state_db=self.state_db,
                sender_history_db=self.sender_history_db,
                vendor_patterns=[],
                label_ids=self.label_ids,
                message_id=msg.message_id,
                cfg=self.cfg,
                actions=actions,  # type: ignore[arg-type]
                thread_to_deal={"t1": "DEAL-2026-001"},
                thread_to_non_deal={},
            )

        self.assertEqual(len(actions.created), 1)
        self.assertEqual(actions.created[0]["action_type"], "DEAL.APPEND_EMAIL_MATERIALS")
        self.assertEqual(actions.created[0]["deal_id"], "DEAL-2026-001")
        self.assertTrue(actions.approved)
        self.assertTrue(actions.executed)

        # quarantine dir should have been materialized for the append executor to copy from
        qdir = self.quarantine_root / msg.message_id
        self.assertTrue((qdir / "email_body.txt").exists())
        self.assertTrue((qdir / "email.json").exists())

        row = self.state_db.get(msg.message_id)
        self.assertIsNotNone(row)
        self.assertEqual(row.status, "processed")
        self.assertEqual(row.classification, "DEAL_THREAD")
        self.assertEqual(row.deal_id, "DEAL-2026-001")

    async def test_rejected_thread_skips_actions_and_labels_non_deal(self) -> None:
        msg = EmailMessage(
            message_id="m2",
            thread_id="t2",
            subject="Costco receipt",
            sender="Costco <noreply@costco.com>",
            to="me@example.com",
            date=utcnow_iso(),
            body="Thanks for your purchase.",
            attachments=[],
        )
        gmail = _FakeGmail(msg)
        actions = _FakeActions()

        await process_one_message(
            gmail=gmail,
            state_db=self.state_db,
            sender_history_db=self.sender_history_db,
            vendor_patterns=[],
            label_ids=self.label_ids,
            message_id=msg.message_id,
            cfg=self.cfg,
            actions=actions,  # type: ignore[arg-type]
            thread_to_deal={},
            thread_to_non_deal={"t2": "not_a_deal"},
        )

        self.assertEqual(actions.created, [])
        self.assertEqual(len(gmail.labels_added), 1)
        applied = gmail.labels_added[0]["label_ids"]
        self.assertIn("Label_NonDeal", applied)
        self.assertIn("Label_Processed", applied)

        row = self.state_db.get(msg.message_id)
        self.assertIsNotNone(row)
        self.assertEqual(row.classification, "NON_DEAL_THREAD")

    async def test_unknown_thread_deal_signal_creates_review_email_action(self) -> None:
        msg = EmailMessage(
            message_id="m3",
            thread_id="t3",
            subject="ExampleCo teaser attached",
            sender="Broker <broker@example.com>",
            to="me@example.com",
            date=utcnow_iso(),
            body="See attached teaser.",
            attachments=[EmailAttachment(attachment_id="a3", filename="teaser.pdf", mime_type="application/pdf", size_bytes=123)],
        )
        gmail = _FakeGmail(msg)
        actions = _FakeActions()

        with patch("email_triage_agent.run_once.decide_actions_and_labels", side_effect=lambda **_: _decision_with_links_and_attachments(msg)):
            await process_one_message(
                gmail=gmail,
                state_db=self.state_db,
                sender_history_db=self.sender_history_db,
                vendor_patterns=[],
                label_ids=self.label_ids,
                message_id=msg.message_id,
                cfg=self.cfg,
                actions=actions,  # type: ignore[arg-type]
                thread_to_deal={},
                thread_to_non_deal={},
            )

        self.assertEqual(len(actions.created), 1)
        self.assertEqual(actions.created[0]["action_type"], "EMAIL_TRIAGE.REVIEW_EMAIL")

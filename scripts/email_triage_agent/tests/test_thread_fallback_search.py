import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from email_triage_agent.gmail_mcp import EmailAttachment, EmailMessage, EmailSearchHit
from email_triage_agent.run_once import RunnerConfig, process_one_message, utcnow_iso
from email_triage_agent.sender_history import SenderHistoryDB
from email_triage_agent.state_db import EmailTriageStateDB
from email_triage_agent.thread_fetch import GmailThreadFetchConfig
from email_triage_agent.triage_logic import LinkEntity, TriageClassification, TriageDecision


@dataclass(frozen=True)
class _CreateResult:
    created_new: bool
    action_id: str
    status: str


class _FakeActions:
    def __init__(self) -> None:
        self.created: List[Dict[str, Any]] = []

    def create_action(self, **kwargs: Any) -> _CreateResult:
        self.created.append(dict(kwargs))
        return _CreateResult(created_new=True, action_id="ACTION-1", status="PENDING_APPROVAL")


class _FakeGmail:
    def __init__(self, messages_by_id: Dict[str, EmailMessage], search_hits_by_query_substr: Dict[str, List[EmailSearchHit]]) -> None:
        self._messages_by_id = dict(messages_by_id)
        self._search_hits_by_query_substr = dict(search_hits_by_query_substr)
        self.search_queries: List[str] = []
        self.labels_added: List[Dict[str, Any]] = []
        self.downloaded: List[Dict[str, Any]] = []

    async def search_emails(self, *, query: str, max_results: int = 10) -> List[EmailSearchHit]:
        self.search_queries.append(query)
        for key, hits in self._search_hits_by_query_substr.items():
            if key in query:
                return hits[: int(max_results)]
        return []

    async def read_email(self, *, message_id: str) -> EmailMessage:
        return self._messages_by_id[message_id]

    async def add_labels(self, *, message_id: str, label_ids: List[str]) -> None:
        self.labels_added.append({"message_id": message_id, "label_ids": list(label_ids)})

    async def mark_as_read(self, *, message_id: str) -> None:
        return

    async def download_attachment(
        self, *, message_id: str, attachment_id: str, save_dir: str, filename: Optional[str] = None
    ) -> str:
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        name = filename or f"{attachment_id}.bin"
        path = Path(save_dir) / name
        path.write_bytes(b"test")
        self.downloaded.append({"message_id": message_id, "attachment_id": attachment_id, "path": str(path)})
        return str(path)


def _decision_deal_signal(msg: EmailMessage) -> TriageDecision:
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


class ThreadSearchFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_full_mode_falls_back_to_search_when_thread_fetch_fails(self) -> None:
        tmp = tempfile.TemporaryDirectory(dir="/home/zaks/tmp")
        tmp_path = Path(tmp.name)
        quarantine_root = tmp_path / "quarantine"
        db_path = tmp_path / "state.db"

        state_db = EmailTriageStateDB(db_path)
        sender_history_db = SenderHistoryDB(tmp_path / "sender_history.db")
        try:
            cfg = RunnerConfig(
                query="",
                max_per_run=1,
                quarantine_root=quarantine_root,
                state_db_path=db_path,
                sender_history_db_path=tmp_path / "sender_history.db",
                deal_registry_path=tmp_path / "deal_registry.json",
                dry_run=False,
                mark_as_read=False,
                max_attachment_mb=25,
                safe_exts={"pdf"},
                unsafe_exts={"exe"},
                vendor_patterns_path=tmp_path / "vendor_patterns.md",
                actions_base_url="http://localhost:8090",
                enable_actions=True,
            )

            older = EmailMessage(
                message_id="m0",
                thread_id="t1",
                subject="Re: ExampleCo teaser",
                sender="Broker <broker@example.com>",
                to="me@example.com",
                date="Thu, 01 Jan 2026 10:00:00 +0000",
                body="Earlier message in thread.",
                attachments=[],
            )
            current = EmailMessage(
                message_id="m1",
                thread_id="t1",
                subject="Re: ExampleCo teaser",
                sender="Broker <broker@example.com>",
                to="me@example.com",
                date=utcnow_iso(),
                body="Latest message in thread.",
                attachments=[EmailAttachment(attachment_id="a1", filename="teaser.pdf", mime_type="application/pdf", size_bytes=123)],
            )

            gmail = _FakeGmail(
                messages_by_id={"m0": older, "m1": current},
                search_hits_by_query_substr={
                    "from:broker@example.com": [
                        EmailSearchHit(message_id="m0", subject=older.subject, sender=older.sender, date=older.date),
                        EmailSearchHit(message_id="m1", subject=current.subject, sender=current.sender, date=current.date),
                    ]
                },
            )
            actions = _FakeActions()

            llm_cfg = type(
                "Cfg",
                (),
                {"mode": "full", "base_url": "http://localhost:8000/v1", "model": "Qwen", "timeout_s": 5.0, "max_tokens": 800, "max_body_chars": 4000},
            )()

            thread_fetch_cfg = GmailThreadFetchConfig(
                credentials_path=tmp_path / "credentials.json",
                oauth_keys_path=tmp_path / "oauth.json",
                api_base="https://gmail.googleapis.com/gmail/v1",
                timeout_s=1.0,
            )

            captured_thread_message_ids: List[str] = []

            def _fake_ma_triage_v1_thread(**kwargs: Any):
                msgs = kwargs.get("thread_messages") or []
                captured_thread_message_ids.extend([m.get("message_id") for m in msgs if isinstance(m, dict)])
                return (
                    {
                        "schema_version": "zakops.email_triage.v1",
                        "message_scope": "thread",
                        "ma_relevant": True,
                        "routing": "QUARANTINE_REVIEW",
                        "ma_intent": "MATERIALS",
                        "confidence": 0.9,
                        "target_company": {"name": "ExampleCo", "name_confidence": 0.6, "website": None, "industry": None, "location": None},
                        "actors": {"sender_role_guess": "BROKER", "sender_org_guess": None},
                        "deal_signals": {
                            "stage_hint": "INBOUND",
                            "valuation_terms": {"ask_price": None, "revenue": None, "ebitda": None, "sde": None, "multiple": None, "currency": None},
                            "timeline_hint": None,
                        },
                        "materials": {"attachments": [], "links": []},
                        "summary": {"bullets": ["Deal signal", "Thread context included", "Recommend review"], "operator_recommendation": "APPROVE", "why": "Deal-related email thread."},
                        "evidence": [{"quote": "Latest message", "source": "THREAD", "reason": "Thread content", "weight": 0.6}],
                        "safety": {"no_secrets": True, "urls_sanitized": True},
                        "debug": {"warnings": [], "model": "Qwen", "latency_ms": 1},
                    },
                    None,
                )

            label_ids = {
                "ZakOps/Processed": "Label_Processed",
                "ZakOps/Deal": "Label_Deal",
                "ZakOps/NonDeal": "Label_NonDeal",
                "ZakOps/Needs-Review": "Label_NeedsReview",
            }

            with patch("email_triage_agent.run_once.decide_actions_and_labels", side_effect=lambda **_: _decision_deal_signal(current)):
                with patch("email_triage_agent.run_once.get_thread_message_ids", return_value=([], "gmail_thread_fetch_failed")):
                    with patch("email_triage_agent.run_once.call_local_vllm_ma_triage_v1_thread", side_effect=_fake_ma_triage_v1_thread):
                        await process_one_message(
                            gmail=gmail,  # type: ignore[arg-type]
                            state_db=state_db,
                            sender_history_db=sender_history_db,
                            vendor_patterns=[],
                            label_ids=label_ids,
                            message_id=current.message_id,
                            cfg=cfg,
                            actions=actions,  # type: ignore[arg-type]
                            thread_to_deal={},
                            thread_to_non_deal={},
                            llm_cfg=llm_cfg,  # type: ignore[arg-type]
                            thread_fetch_cfg=thread_fetch_cfg,
                        )

            # Search fallback was used.
            self.assertTrue(any("from:broker@example.com" in q for q in gmail.search_queries))
            # Thread messages included the fallback hits, not just the current message.
            self.assertIn("m0", captured_thread_message_ids)
            self.assertIn("m1", captured_thread_message_ids)
            # Review action created.
            self.assertEqual(len(actions.created), 1)
            self.assertEqual(actions.created[0]["action_type"], "EMAIL_TRIAGE.REVIEW_EMAIL")
        finally:
            state_db.close()
            sender_history_db.close()
            tmp.cleanup()


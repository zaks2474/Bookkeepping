import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from email_triage_agent.gmail_mcp import EmailAttachment, EmailMessage
from email_triage_agent.llm_triage import (
    LlmLinkSummary,
    LlmTriageConfig,
    LlmTriageResult,
    call_local_vllm_ma_triage_v1_single,
    call_local_vllm_ma_triage_v1_thread,
    call_local_vllm_thread_triage,
    call_local_vllm_triage,
)
from email_triage_agent.run_once import RunnerConfig, process_one_message, utcnow_iso
from email_triage_agent.sender_history import SenderHistoryDB
from email_triage_agent.state_db import EmailTriageStateDB
from email_triage_agent.triage_logic import LinkEntity, TriageClassification, TriageDecision


class _FakeHttpResponse:
    def __init__(self, payload: dict):
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeGmail:
    def __init__(self, msg: EmailMessage):
        self.msg = msg
        self.added_labels = []

    async def read_email(self, *, message_id: str) -> EmailMessage:
        assert message_id == self.msg.message_id
        return self.msg

    async def add_labels(self, *, message_id: str, label_ids):
        self.added_labels.append({"message_id": message_id, "label_ids": list(label_ids)})

    async def mark_as_read(self, *, message_id: str) -> None:
        return

    async def download_attachment(self, *, message_id: str, attachment_id: str, save_dir: str, filename=None) -> str:
        raise AssertionError("download_attachment should not be called in LLM downgrade test")


class _FakeActions:
    def __init__(self):
        self.created = []

    def create_action(self, **kwargs):
        self.created.append(kwargs)
        return {"created_new": True, "action": {"action_id": "ACT-TEST", "status": "PENDING_APPROVAL"}}


def _decision_deal_signal(msg: EmailMessage) -> TriageDecision:
    return TriageDecision(
        classification=TriageClassification(classification="DEAL_SIGNAL", urgency="LOW", reason="deal-signal"),
        sender_email="broker@example.com",
        company=None,
        links=[LinkEntity(type="other", url="https://example.com", auth_required=True, vendor_hint=None)],
        attachments=list(msg.attachments),
        labels_to_add=["ZakOps/Deal"],
        needs_reply=False,
        needs_docs=False,
        quarantine=False,
        eligible_for_llm=True,
        body_fingerprint="test",
    )


class LlmTriageTests(unittest.TestCase):
    def test_call_local_vllm_ma_triage_v1_single_parses_strict_json(self):
        cfg = LlmTriageConfig(mode="assist", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=400, max_body_chars=2000)
        content = {
            "schema_version": "zakops.email_triage.v1",
            "message_scope": "single",
            "ma_relevant": True,
            "routing": "QUARANTINE_REVIEW",
            "ma_intent": "MATERIALS",
            "confidence": 0.9,
            "target_company": {"name": "ExampleCo", "name_confidence": 0.7, "website": None, "industry": None, "location": None},
            "actors": {"sender_role_guess": "BROKER", "sender_org_guess": None},
            "deal_signals": {
                "stage_hint": "INBOUND",
                "valuation_terms": {"ask_price": "$10M", "revenue": None, "ebitda": "2.0M", "sde": None, "multiple": None, "currency": "USD"},
                "timeline_hint": None,
            },
            "materials": {
                "attachments": [{"filename": "CIM.pdf", "detected_type": "CIM", "confidence": 0.8, "notes": None}],
                "links": [{"url": "https://example.com/dataroom?token=abc", "link_type": "DATAROOM", "auth_required": "YES", "notes": None}],
            },
            "summary": {"bullets": ["Inbound teaser/CIM", "Broker outreach", "Recommend review"], "operator_recommendation": "APPROVE", "why": "Broker shared deal materials."},
            "evidence": [{"quote": "Please review the CIM.", "source": "BODY", "reason": "Explicit deal materials", "weight": 0.8}],
            "safety": {"no_secrets": True, "urls_sanitized": True},
            "debug": {"warnings": [], "model": "Qwen", "latency_ms": 12},
        }
        fake = {"choices": [{"message": {"content": json.dumps(content)}}]}

        with patch("urllib.request.urlopen", return_value=_FakeHttpResponse(fake)):
            result, err = call_local_vllm_ma_triage_v1_single(
                cfg=cfg,
                subject="ExampleCo teaser",
                sender="Broker <broker@example.com>",
                received_at="now",
                body_text="Please review the CIM.",
                extracted_urls=["https://example.com/dataroom?token=abc"],
                attachments=[{"filename": "CIM.pdf", "size_bytes": 123}],
            )

        self.assertIsNone(err)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["schema_version"], "zakops.email_triage.v1")
        self.assertTrue(result["ma_relevant"])
        # URL must be sanitized (no query string)
        self.assertEqual(result["materials"]["links"][0]["url"], "https://example.com/dataroom")

    def test_call_local_vllm_ma_triage_v1_thread_repairs_invalid_json(self):
        cfg = LlmTriageConfig(mode="full", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=1200, max_body_chars=4000)

        invalid = {"choices": [{"message": {"content": "{'schema_version': 'zakops.email_triage.v1'}"}}]}
        content = {
            "schema_version": "zakops.email_triage.v1",
            "message_scope": "thread",
            "ma_relevant": False,
            "routing": "NON_DEAL",
            "ma_intent": "NON_DEAL",
            "confidence": 0.95,
            "target_company": {"name": None, "name_confidence": 0.0, "website": None, "industry": None, "location": None},
            "actors": {"sender_role_guess": "UNKNOWN", "sender_org_guess": None},
            "deal_signals": {
                "stage_hint": "UNKNOWN",
                "valuation_terms": {"ask_price": None, "revenue": None, "ebitda": None, "sde": None, "multiple": None, "currency": None},
                "timeline_hint": None,
            },
            "materials": {"attachments": [], "links": []},
            "summary": {"bullets": ["Not M&A-related", "Looks operational/newsletter", "Recommend reject"], "operator_recommendation": "REJECT", "why": "No deal context."},
            "evidence": [{"quote": "unsubscribe", "source": "BODY", "reason": "Newsletter marker", "weight": 0.7}],
            "safety": {"no_secrets": True, "urls_sanitized": True},
            "debug": {"warnings": [], "model": "Qwen", "latency_ms": 25},
        }
        repaired = {"choices": [{"message": {"content": json.dumps(content)}}]}

        with patch("urllib.request.urlopen", side_effect=[_FakeHttpResponse(invalid), _FakeHttpResponse(repaired)]) as mocked:
            result, err = call_local_vllm_ma_triage_v1_thread(
                cfg=cfg,
                thread_messages=[
                    {"subject": "Hello", "from": "Sender <s@example.com>", "to": "me@example.com", "date": "now", "body_text": "unsubscribe", "urls": [], "attachments": []},
                ],
            )

        self.assertIsNone(err)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["routing"], "NON_DEAL")
        self.assertEqual(mocked.call_count, 2)

    def test_call_local_vllm_triage_parses_strict_json(self):
        cfg = LlmTriageConfig(mode="assist", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=200, max_body_chars=2000)
        content = {
            "classification": "DEAL_SIGNAL",
            "confidence": 0.9,
            "summary_bullets": ["Deal teaser received", "Contains NDA link", "Recommend approve"],
            "company_name_guess": "ExampleCo",
            "broker_name": "Jane Broker",
            "broker_email": "broker@example.com",
            "asking_price": "$10M",
            "key_metrics": {"ebitda": "2.0M"},
            "attachments": [{"filename": "CIM.pdf", "guessed_type": "CIM", "notes": ""}],
            "links": [{"url": "https://example.com", "link_type": "dataroom", "requires_auth": True}],
            "operator_recommendation": "Approve and request CIM/financials.",
            "reasons": ["broker sender", "mentions NDA"],
        }
        fake = {"choices": [{"message": {"content": json.dumps(content)}}]}

        with patch("urllib.request.urlopen", return_value=_FakeHttpResponse(fake)):
            result, err = call_local_vllm_triage(
                cfg=cfg,
                subject="ExampleCo teaser",
                sender="Broker <broker@example.com>",
                received_at="now",
                body_text="Please sign NDA.",
                extracted_urls=["https://example.com"],
                attachments=[{"filename": "CIM.pdf", "size_bytes": 123}],
            )

        self.assertIsNone(err)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.classification, "DEAL_SIGNAL")
        self.assertGreaterEqual(result.confidence, 0.8)
        self.assertEqual(result.company_name_guess, "ExampleCo")
        self.assertEqual(result.links[0].link_type, "dataroom")

    def test_call_local_vllm_thread_triage_parses_strict_json(self):
        cfg = LlmTriageConfig(mode="full", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=800, max_body_chars=4000)
        content = {
            "classification": "DEAL_SIGNAL",
            "confidence": 0.88,
            "summary_bullets": [
                "Inbound deal thread with CIM/teaser context",
                "Sender appears to be a broker",
                "Recommend approve and request financials",
            ],
            "deal_likelihood_reason": "Thread references CIM and a dataroom.",
            "evidence": [
                {"message_index": 0, "snippet": "CIM available", "why_it_matters": "Deal materials signal"},
                {"message_index": 1, "snippet": "data room link", "why_it_matters": "Dataroom access indicates active process"},
            ],
            "company_name_guess": "ExampleCo",
            "sender_role_guess": "broker",
            "materials_detected": {"kind": "CIM", "confidence": 0.9},
            "links": [{"url": "https://example.com/room", "link_type": "dataroom", "requires_auth": True}],
            "attachments": [{"filename": "ExampleCo_CIM.pdf", "guessed_type": "CIM", "notes": ""}],
            "attachments_assessed": [{"filename": "ExampleCo_CIM.pdf", "deal_material": True, "why": "CIM doc"}],
            "operator_recommendation": "Approve and request LTM financials.",
            "reasons": ["CIM/dataroom present", "broker sender"],
        }
        fake = {"choices": [{"message": {"content": json.dumps(content)}}]}

        with patch("urllib.request.urlopen", return_value=_FakeHttpResponse(fake)):
            result, err = call_local_vllm_thread_triage(
                cfg=cfg,
                thread_messages=[
                    {"subject": "ExampleCo", "from": "Broker <b@example.com>", "to": "me@example.com", "date": "now", "body_text": "CIM available", "urls": [], "attachments": []},
                    {"subject": "Re: ExampleCo", "from": "Broker <b@example.com>", "to": "me@example.com", "date": "now", "body_text": "See dataroom link", "urls": ["https://example.com/room"], "attachments": []},
                ],
            )

        self.assertIsNone(err)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.classification, "DEAL_SIGNAL")
        self.assertEqual(result.sender_role_guess, "broker")
        self.assertEqual(result.materials_detected.get("kind"), "CIM")
        self.assertGreaterEqual(float(result.materials_detected.get("confidence") or 0.0), 0.5)

    def test_call_local_vllm_thread_triage_repairs_invalid_json(self):
        cfg = LlmTriageConfig(mode="full", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=800, max_body_chars=4000)

        invalid = {"choices": [{"message": {"content": "{'classification': 'DEAL_SIGNAL'}"}}]}

        content = {
            "classification": "DEAL_SIGNAL",
            "confidence": 0.9,
            "summary_bullets": ["Deal signal thread", "Broker outreach", "Recommend approve"],
            "deal_likelihood_reason": "Thread appears to be a broker outreach with materials.",
            "evidence": [{"message_index": 0, "snippet": "CIM", "why_it_matters": "deal materials"}],
            "company_name_guess": "ExampleCo",
            "sender_role_guess": "broker",
            "materials_detected": {"kind": "CIM", "confidence": 0.8},
            "links": [],
            "attachments": [],
            "attachments_assessed": [],
            "operator_recommendation": "Approve.",
            "reasons": ["broker sender"],
        }
        repaired = {"choices": [{"message": {"content": json.dumps(content)}}]}

        with patch("urllib.request.urlopen", side_effect=[_FakeHttpResponse(invalid), _FakeHttpResponse(repaired)]) as mocked:
            result, err = call_local_vllm_thread_triage(
                cfg=cfg,
                thread_messages=[
                    {"subject": "ExampleCo", "from": "Broker <b@example.com>", "to": "me@example.com", "date": "now", "body_text": "CIM available", "urls": [], "attachments": []},
                ],
            )

        self.assertIsNone(err)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.classification, "DEAL_SIGNAL")
        self.assertEqual(mocked.call_count, 2)

    def test_call_local_vllm_triage_repairs_invalid_json(self):
        cfg = LlmTriageConfig(mode="assist", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=200, max_body_chars=2000)

        invalid = {"choices": [{"message": {"content": "not json at all"}}]}
        content = {
            "classification": "NEWSLETTER",
            "confidence": 0.95,
            "summary_bullets": ["Newsletter email", "Not a deal", "Recommend ignore"],
            "company_name_guess": "",
            "broker_name": "",
            "broker_email": "",
            "asking_price": "",
            "key_metrics": {},
            "attachments": [],
            "links": [],
            "operator_recommendation": "Ignore.",
            "reasons": ["marketing content"],
        }
        repaired = {"choices": [{"message": {"content": json.dumps(content)}}]}

        with patch("urllib.request.urlopen", side_effect=[_FakeHttpResponse(invalid), _FakeHttpResponse(repaired)]) as mocked:
            result, err = call_local_vllm_triage(
                cfg=cfg,
                subject="Hello",
                sender="Sender <s@example.com>",
                received_at="now",
                body_text="hi",
                extracted_urls=[],
                attachments=[],
            )

        self.assertIsNone(err)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.classification, "NEWSLETTER")
        self.assertEqual(mocked.call_count, 2)


class LlmRepairDoubleFailureTests(unittest.TestCase):
    """Test double-failure scenarios in the JSON repair loop."""

    def test_repair_call_http_error_returns_structured_error(self):
        """When both initial and repair calls fail, return llm_repair_call_failed."""
        cfg = LlmTriageConfig(mode="assist", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=200, max_body_chars=2000)

        # First call returns invalid JSON
        invalid = {"choices": [{"message": {"content": "not valid json"}}]}

        # Second call (repair) fails with HTTP error
        def side_effect_fn(req, timeout=None):
            if side_effect_fn.call_count == 0:
                side_effect_fn.call_count += 1
                return _FakeHttpResponse(invalid)
            else:
                import urllib.error
                raise urllib.error.HTTPError(url="test", code=500, msg="Server Error", hdrs={}, fp=None)
        side_effect_fn.call_count = 0

        with patch("urllib.request.urlopen", side_effect=side_effect_fn) as mocked:
            result, err = call_local_vllm_triage(
                cfg=cfg,
                subject="Test",
                sender="sender@example.com",
                received_at="now",
                body_text="test body",
                extracted_urls=[],
                attachments=[],
            )

        self.assertIsNone(result)
        self.assertIsNotNone(err)
        self.assertTrue(err.startswith("llm_repair_call_failed:"))

    def test_repair_output_not_json_returns_structured_error(self):
        """When repair output is also not valid JSON, return llm_repair_output_not_json."""
        cfg = LlmTriageConfig(mode="assist", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=200, max_body_chars=2000)

        # First call returns invalid JSON
        invalid = {"choices": [{"message": {"content": "not valid json"}}]}
        # Repair call also returns invalid JSON
        still_invalid = {"choices": [{"message": {"content": "still not valid json either"}}]}

        with patch("urllib.request.urlopen", side_effect=[_FakeHttpResponse(invalid), _FakeHttpResponse(still_invalid)]) as mocked:
            result, err = call_local_vllm_triage(
                cfg=cfg,
                subject="Test",
                sender="sender@example.com",
                received_at="now",
                body_text="test body",
                extracted_urls=[],
                attachments=[],
            )

        self.assertIsNone(result)
        self.assertEqual(err, "llm_repair_output_not_json")
        self.assertEqual(mocked.call_count, 2)

    def test_repair_output_schema_invalid_returns_structured_error(self):
        """When repair output is JSON but fails schema validation, return llm_repair_output_schema_invalid."""
        cfg = LlmTriageConfig(mode="assist", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=200, max_body_chars=2000)

        # First call returns invalid JSON
        invalid = {"choices": [{"message": {"content": "not valid json"}}]}
        # Repair returns valid JSON but wrong schema (missing required fields)
        wrong_schema = {"choices": [{"message": {"content": json.dumps({"random_field": "value"})}}]}

        with patch("urllib.request.urlopen", side_effect=[_FakeHttpResponse(invalid), _FakeHttpResponse(wrong_schema)]) as mocked:
            result, err = call_local_vllm_triage(
                cfg=cfg,
                subject="Test",
                sender="sender@example.com",
                received_at="now",
                body_text="test body",
                extracted_urls=[],
                attachments=[],
            )

        self.assertIsNone(result)
        self.assertEqual(err, "llm_repair_output_schema_invalid")
        self.assertEqual(mocked.call_count, 2)

    def test_ma_triage_v1_repair_call_failure(self):
        """Test ma_triage_v1 repair call failure returns structured error."""
        cfg = LlmTriageConfig(mode="full", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=200, max_body_chars=2000)

        # First call returns invalid JSON
        invalid = {"choices": [{"message": {"content": "not valid json"}}]}

        # Second call (repair) fails with timeout
        def side_effect_fn(req, timeout=None):
            if side_effect_fn.call_count == 0:
                side_effect_fn.call_count += 1
                return _FakeHttpResponse(invalid)
            else:
                import socket
                raise socket.timeout("Connection timed out")
        side_effect_fn.call_count = 0

        with patch("urllib.request.urlopen", side_effect=side_effect_fn):
            result, err = call_local_vllm_ma_triage_v1_single(
                cfg=cfg,
                subject="Test",
                sender="sender@example.com",
                received_at="now",
                body_text="test body",
                extracted_urls=[],
                attachments=[],
            )

        self.assertIsNone(result)
        self.assertIsNotNone(err)
        self.assertTrue(err.startswith("llm_repair_call_failed:"))


class LlmAssistDowngradeTests(unittest.IsolatedAsyncioTestCase):
    async def test_llm_can_downgrade_false_positive_deal_signal(self):
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

            msg = EmailMessage(
                message_id="m1",
                thread_id="t1",
                subject="Welcome to Bitdefender!",
                sender="Bitdefender <noreply@info.bitdefender.com>",
                to="me@example.com",
                date=utcnow_iso(),
                body="Welcome! Here are links to manage your account.",
                attachments=[EmailAttachment(attachment_id="a1", filename="welcome.pdf", mime_type="application/pdf", size_bytes=10)],
            )

            gmail = _FakeGmail(msg)
            actions = _FakeActions()
            label_ids = {"ZakOps/Processed": "P", "ZakOps/NonDeal": "N", "ZakOps/Deal": "D"}

            llm_cfg = LlmTriageConfig(mode="assist", base_url="http://localhost:8000/v1", model="Qwen", timeout_s=5, max_tokens=200, max_body_chars=2000)
            ma_triage = {
                "schema_version": "zakops.email_triage.v1",
                "message_scope": "single",
                "ma_relevant": False,
                "routing": "NON_DEAL",
                "ma_intent": "NON_DEAL",
                "confidence": 0.95,
                "target_company": {"name": None, "name_confidence": 0.0, "website": None, "industry": None, "location": None},
                "actors": {"sender_role_guess": "UNKNOWN", "sender_org_guess": None},
                "deal_signals": {
                    "stage_hint": "UNKNOWN",
                    "valuation_terms": {"ask_price": None, "revenue": None, "ebitda": None, "sde": None, "multiple": None, "currency": None},
                    "timeline_hint": None,
                },
                "materials": {"attachments": [], "links": []},
                "summary": {
                    "bullets": ["Product onboarding email", "Not related to deal flow", "Recommend reject"],
                    "operator_recommendation": "REJECT",
                    "why": "Onboarding/newsletter content with no M&A context.",
                },
                "evidence": [{"quote": "Welcome!", "source": "BODY", "reason": "Onboarding language", "weight": 0.7}],
                "safety": {"no_secrets": True, "urls_sanitized": True},
                "debug": {"warnings": [], "model": "Qwen", "latency_ms": 12},
            }

            with patch("email_triage_agent.run_once.decide_actions_and_labels", side_effect=lambda **_: _decision_deal_signal(msg)):
                with patch("email_triage_agent.run_once.call_local_vllm_ma_triage_v1_single", return_value=(ma_triage, None)):
                    await process_one_message(
                        gmail=gmail,
                        state_db=state_db,
                        sender_history_db=sender_history_db,
                        vendor_patterns=[],
                        label_ids=label_ids,
                        message_id=msg.message_id,
                        cfg=cfg,
                        actions=actions,
                        thread_to_deal={},
                        thread_to_non_deal={},
                        llm_cfg=llm_cfg,
                    )

            # No review action created when downgraded.
            self.assertEqual(len(actions.created), 0)
            # No quarantine directory created.
            self.assertFalse((quarantine_root / msg.message_id).exists())

            # NonDeal + Processed labels applied.
            self.assertEqual(len(gmail.added_labels), 1)
            applied = gmail.added_labels[0]["label_ids"]
            self.assertIn("N", applied)
            self.assertIn("P", applied)

            row = state_db.get(msg.message_id)
            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row.status, "processed")
            self.assertEqual(row.classification, "OPERATIONAL")
        finally:
            state_db.close()
            sender_history_db.close()
            tmp.cleanup()

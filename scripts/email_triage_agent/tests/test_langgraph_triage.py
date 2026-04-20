import json
import unittest
from unittest.mock import patch

from email_triage_agent.llm_triage import LlmTriageConfig


class _FakeHttpResponse:
    def __init__(self, payload: dict):
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _has_langgraph() -> bool:
    try:
        import langgraph  # noqa: F401
    except Exception:
        return False
    return True


class LangGraphTriageTests(unittest.TestCase):
    def test_agent_builder_memories_loads_and_strips_conflicting_output_contract(self):
        from email_triage_agent.langgraph_triage import load_agent_builder_memories_text

        text = load_agent_builder_memories_text()
        self.assertIn("ZakOps Gmail Triage Agent", text)
        # Conflicting section heading should be removed.
        self.assertNotIn("## Output Contract", text)

    def test_langgraph_not_installed_returns_structured_error(self):
        if _has_langgraph():
            self.skipTest("langgraph installed in this environment")

        from email_triage_agent.langgraph_triage import call_langgraph_triage

        cfg = LlmTriageConfig(
            mode="assist",
            base_url="http://localhost:8000/v1",
            model="Qwen",
            timeout_s=5,
            max_tokens=200,
            max_body_chars=2000,
        )
        result, err = call_langgraph_triage(
            cfg=cfg,
            subject="ExampleCo teaser",
            sender="Broker <broker@example.com>",
            received_at="now",
            body_text="Please sign NDA.",
            extracted_urls=["https://example.com"],
            attachments=[{"filename": "CIM.pdf", "size_bytes": 123}],
        )
        self.assertIsNone(result)
        self.assertEqual(err, "langgraph_not_installed")

    def test_langgraph_blocks_non_local_base_url(self):
        if not _has_langgraph():
            self.skipTest("langgraph not installed")

        from email_triage_agent.langgraph_triage import call_langgraph_triage

        cfg = LlmTriageConfig(
            mode="assist",
            base_url="https://api.openai.com/v1",
            model="Qwen",
            timeout_s=5,
            max_tokens=200,
            max_body_chars=2000,
        )
        result, err = call_langgraph_triage(
            cfg=cfg,
            subject="ExampleCo teaser",
            sender="Broker <broker@example.com>",
            received_at="now",
            body_text="Please sign NDA.",
            extracted_urls=["https://example.com"],
            attachments=[],
        )
        self.assertIsNone(result)
        assert err is not None
        self.assertTrue(err.startswith("llm_base_url_not_local:"))

    def test_langgraph_parses_llm_output_into_llmtriageresult(self):
        if not _has_langgraph():
            self.skipTest("langgraph not installed")

        from email_triage_agent.langgraph_triage import call_langgraph_triage

        cfg = LlmTriageConfig(
            mode="assist",
            base_url="http://localhost:8000/v1",
            model="Qwen",
            timeout_s=5,
            max_tokens=200,
            max_body_chars=2000,
        )
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
            result, err = call_langgraph_triage(
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
        self.assertEqual(result.company_name_guess, "ExampleCo")


import unittest

from email_triage_agent.kinetic_actions import extract_deal_id, safe_url


class TestKineticActionsUtils(unittest.TestCase):
    def test_extract_deal_id(self) -> None:
        self.assertEqual(extract_deal_id("re: DEAL-2025-010 materials"), "DEAL-2025-010")
        self.assertIsNone(extract_deal_id("no deal id here"))

    def test_safe_url_strips_query_and_fragment(self) -> None:
        self.assertEqual(safe_url("https://example.com/path?a=1#frag"), "https://example.com/path")


import unittest

from email_triage_agent.gmail_mcp import EmailAttachment, EmailMessage
from email_triage_agent.triage_logic import decide_actions_and_labels, normalize_email_body


class TriageLogicTests(unittest.TestCase):
    def test_url_path_tokens_do_not_create_false_deal_signal(self):
        msg = EmailMessage(
            message_id="m_url",
            thread_id="t_url",
            subject="FYI",
            sender="Sender <sender@example.com>",
            to="operator@example.com",
            date="01 Jan 2026 12:00:00 +0000",
            body="See https://example.com/nda/mandatory for details.",
            attachments=[],
        )
        decision = decide_actions_and_labels(email=msg, vendor_patterns=[])
        self.assertNotEqual(decision.classification.classification, "DEAL_SIGNAL")
        self.assertNotIn("ZakOps/Deal", decision.labels_to_add)

    def test_normalize_email_body_strips_html_and_quotes(self):
        raw = (
            "<html><body><p>Hello</p><p>Unsubscribe</p><br>"
            "On Jan 1, Someone wrote:<br>&gt; quoted line</body></html>"
        )
        norm = normalize_email_body(raw)
        self.assertIn("Hello", norm.clean_text)
        self.assertNotIn("<html", norm.clean_text.lower())
        self.assertNotIn("quoted line", norm.clean_text)
        self.assertTrue(norm.fingerprint)

    def test_transaction_alert_is_not_deal_signal(self):
        msg = EmailMessage(
            message_id="m1",
            thread_id="t1",
            subject="A $16.78 transaction was made on your Costco Anywhere account",
            sender="Citi Alerts <alerts@info6.citi.com>",
            to="operator@example.com",
            date="01 Jan 2026 12:00:00 +0000",
            body="A $16.78 transaction was made on your Costco Anywhere account. If you did not make this purchase, contact us.",
            attachments=[],
        )
        decision = decide_actions_and_labels(email=msg, vendor_patterns=[])
        self.assertEqual(decision.classification.classification, "OPERATIONAL")
        self.assertIn("ZakOps/NonDeal", decision.labels_to_add)
        self.assertNotIn("ZakOps/Deal", decision.labels_to_add)

    def test_cim_attachment_is_deal_signal(self):
        msg = EmailMessage(
            message_id="m2",
            thread_id="t2",
            subject="Project Acme - CIM available",
            sender="Broker <broker@brokerage.com>",
            to="operator@example.com",
            date="01 Jan 2026 12:00:00 +0000",
            body="Please find the CIM attached and let us know if you can sign the NDA.",
            attachments=[
                EmailAttachment(
                    attachment_id="a1",
                    filename="Acme_CIM.pdf",
                    mime_type="application/pdf",
                    size_bytes=1234,
                )
            ],
        )
        decision = decide_actions_and_labels(email=msg, vendor_patterns=[])
        self.assertEqual(decision.classification.classification, "DEAL_SIGNAL")
        self.assertIn("ZakOps/Deal", decision.labels_to_add)
        self.assertNotIn("ZakOps/NonDeal", decision.labels_to_add)

import unittest

from email_triage_agent.gmail_mcp import parse_label_id, parse_read_email_text, parse_search_emails_text


class TestGmailMcpParsing(unittest.TestCase):
    def test_parse_search_emails_text(self) -> None:
        text = (
            "ID: 123abc\n"
            "Subject: Hello\n"
            "From: Someone <a@example.com>\n"
            "Date: Thu, 01 Jan 2026 00:00:00 +0000\n"
            "\n"
            "ID: 456def\n"
            "Subject: World\n"
            "From: Other <b@example.com>\n"
            "Date: Thu, 01 Jan 2026 01:00:00 +0000\n"
        )
        hits = parse_search_emails_text(text)
        self.assertEqual(len(hits), 2)
        self.assertEqual(hits[0].message_id, "123abc")
        self.assertEqual(hits[1].subject, "World")

    def test_parse_read_email_text_with_attachments(self) -> None:
        text = (
            "Thread ID: t_1\n"
            "Subject: Test\n"
            "From: Sender <s@example.com>\n"
            "To: Me <me@example.com>\n"
            "Date: Thu, 01 Jan 2026 00:00:00 +0000\n"
            "\n"
            "Body line 1\n"
            "Body line 2\n"
            "Attachments (2):\n"
            "- CIM.pdf (application/pdf, 12 KB, ID: att_1)\n"
            "- model.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, 34 KB, ID: att_2)\n"
        )
        msg = parse_read_email_text("m_1", text)
        self.assertEqual(msg.message_id, "m_1")
        self.assertEqual(msg.thread_id, "t_1")
        self.assertEqual(msg.subject, "Test")
        self.assertIn("Body line 1", msg.body)
        self.assertEqual(len(msg.attachments), 2)
        self.assertEqual(msg.attachments[0].filename, "CIM.pdf")
        self.assertEqual(msg.attachments[1].attachment_id, "att_2")

    def test_parse_label_id(self) -> None:
        text = "Successfully found existing label:\nID: Label_3\nName: ZakOps/Processed\nType: user"
        self.assertEqual(parse_label_id(text), "Label_3")


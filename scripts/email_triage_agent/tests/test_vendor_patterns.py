import tempfile
import unittest
from pathlib import Path

from email_triage_agent.vendor_patterns import classify_url_vendor, load_vendor_patterns_md


class TestVendorPatterns(unittest.TestCase):
    def test_load_and_match(self) -> None:
        md = (
            "# Vendor URL Patterns\n\n"
            "## Dataroom / Virtual Data Room (VDR) Providers\n\n"
            "| Vendor | URL Patterns | Notes |\n"
            "|--------|--------------|-------|\n"
            "| **Firmex** | `firmex.com`, `app.firmex.com` | |\n"
        )
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "vendor_patterns.md"
            p.write_text(md, encoding="utf-8")
            patterns = load_vendor_patterns_md(p)
            self.assertGreaterEqual(len(patterns), 1)
            hit = classify_url_vendor("https://app.firmex.com/room/abc", patterns)
            self.assertIsNotNone(hit)
            self.assertEqual(hit.category, "dataroom")


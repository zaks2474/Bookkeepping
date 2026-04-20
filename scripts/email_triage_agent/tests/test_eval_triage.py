import os
import tempfile
import unittest
from pathlib import Path

from email_triage_agent import eval_triage


class TestEvalTriage(unittest.TestCase):
    def test_generate_report_includes_binary_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["DATAROOM_ROOT"] = tmpdir
            reg = Path(tmpdir) / ".deal-registry"
            reg.mkdir(parents=True, exist_ok=True)
            feedback = reg / "triage_feedback.jsonl"
            feedback.write_text(
                "\n".join(
                    [
                        '{"timestamp":"2026-01-10T00:00:00Z","decision":"approve","classification":"DEAL_SIGNAL"}',
                        '{"timestamp":"2026-01-10T00:00:01Z","decision":"reject","classification":"DEAL_SIGNAL"}',
                        '{"timestamp":"2026-01-10T00:00:02Z","decision":"approve","classification":"NON_DEAL"}',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            entries = list(eval_triage._iter_jsonl(feedback))
            report = eval_triage.generate_report(entries)

            self.assertIn("## Metrics (operator feedback)", report)
            self.assertIn("false_positive_rate:", report)
            self.assertIn("precision:", report)
            self.assertIn("- precision: 50.0%", report)
            self.assertIn("- recall: 50.0%", report)
            self.assertIn("- false_positive_rate: 50.0%", report)


if __name__ == "__main__":
    unittest.main()


import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from email_triage_agent.thread_fetch import GmailThreadFetchConfig, get_thread_message_ids


class ThreadFetchTests(unittest.TestCase):
    def _make_cfg(self, td: str) -> GmailThreadFetchConfig:
        base = Path(td)
        creds = base / "credentials.json"
        keys = base / "gcp-oauth.keys.json"
        return GmailThreadFetchConfig(credentials_path=creds, oauth_keys_path=keys, api_base="https://example.invalid", timeout_s=1.0)

    def test_get_thread_message_ids_sorts_by_internal_date(self) -> None:
        with tempfile.TemporaryDirectory(dir="/home/zaks/tmp") as td:
            cfg = self._make_cfg(td)
            cfg.credentials_path.write_text('{"access_token":"tok1","expiry_date":9999999999999,"refresh_token":"rt"}', encoding="utf-8")
            cfg.oauth_keys_path.write_text(
                '{"installed":{"token_uri":"https://example.invalid/token","client_id":"cid","client_secret":"csec"}}',
                encoding="utf-8",
            )

            payload = {
                "messages": [
                    {"id": "m3", "internalDate": "300"},
                    {"id": "m1", "internalDate": "100"},
                    {"id": "m2", "internalDate": "200"},
                ]
            }

            used_tokens = []

            def fake_get_json(*, url: str, access_token: str, timeout_s: float):
                used_tokens.append(access_token)
                return payload, None

            with patch("email_triage_agent.thread_fetch._gmail_get_json", side_effect=fake_get_json):
                ids, err = get_thread_message_ids(cfg=cfg, thread_id="t1")

            self.assertIsNone(err)
            self.assertEqual(ids, ["m1", "m2", "m3"])
            self.assertEqual(used_tokens, ["tok1"])

    def test_get_thread_message_ids_refreshes_when_expired(self) -> None:
        with tempfile.TemporaryDirectory(dir="/home/zaks/tmp") as td:
            cfg = self._make_cfg(td)
            cfg.credentials_path.write_text('{"access_token":"old","expiry_date":0,"refresh_token":"rt"}', encoding="utf-8")
            cfg.oauth_keys_path.write_text(
                '{"installed":{"token_uri":"https://example.invalid/token","client_id":"cid","client_secret":"csec"}}',
                encoding="utf-8",
            )

            payload = {"messages": [{"id": "m1", "internalDate": "100"}]}

            with patch("email_triage_agent.thread_fetch._refresh_access_token", return_value=("tok2", 9999999999999, None)):
                with patch("email_triage_agent.thread_fetch._gmail_get_json", return_value=(payload, None)) as get_json:
                    ids, err = get_thread_message_ids(cfg=cfg, thread_id="t1")

            self.assertIsNone(err)
            self.assertEqual(ids, ["m1"])
            # Ensures refreshed token was used for Gmail request
            _kwargs = get_json.call_args.kwargs
            self.assertEqual(_kwargs["access_token"], "tok2")

    def test_get_thread_message_ids_retries_once_on_unauthorized(self) -> None:
        with tempfile.TemporaryDirectory(dir="/home/zaks/tmp") as td:
            cfg = self._make_cfg(td)
            cfg.credentials_path.write_text('{"access_token":"tok1","expiry_date":9999999999999,"refresh_token":"rt"}', encoding="utf-8")
            cfg.oauth_keys_path.write_text(
                '{"installed":{"token_uri":"https://example.invalid/token","client_id":"cid","client_secret":"csec"}}',
                encoding="utf-8",
            )

            payload = {"messages": [{"id": "m1", "internalDate": "100"}]}
            calls = {"n": 0}

            def fake_get_json(*, url: str, access_token: str, timeout_s: float):
                calls["n"] += 1
                if calls["n"] == 1:
                    return None, "gmail_unauthorized"
                return payload, None

            with patch("email_triage_agent.thread_fetch._gmail_get_json", side_effect=fake_get_json):
                ids, err = get_thread_message_ids(cfg=cfg, thread_id="t1")

            self.assertIsNone(err)
            self.assertEqual(ids, ["m1"])
            self.assertEqual(calls["n"], 2)


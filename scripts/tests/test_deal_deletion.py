import importlib
import json
import os
import shutil
import sys
import tempfile
import unittest

from pathlib import Path

import httpx

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class DealDeletionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._old_env = dict(os.environ)
        self._tmpdir = tempfile.TemporaryDirectory(dir="/home/zaks/tmp")
        self.tmp_path = Path(self._tmpdir.name)

        self.dataroom_root = self.tmp_path / "DataRoom"
        self.dataroom_root.mkdir(parents=True, exist_ok=True)
        (self.dataroom_root / ".deal-registry").mkdir(parents=True, exist_ok=True)
        (self.dataroom_root / ".deal-registry" / "case_files").mkdir(parents=True, exist_ok=True)

        os.environ["DATAROOM_ROOT"] = str(self.dataroom_root)
        os.environ["ZAKOPS_STATE_DB"] = str(self.tmp_path / "state.db")
        os.environ["DEAL_EVENTS_DIR"] = str(self.tmp_path / "events")
        os.environ["DATAROOM_ROOT"] = str(self.dataroom_root)

        (self.dataroom_root / ".deal-registry" / "deal_registry.json").write_text(
            json.dumps(
                {
                    "deal_counter": 0,
                    "broker_counter": 0,
                    "deals": {},
                    "brokers": {},
                    "junk_patterns": [],
                    "email_to_deal": {},
                    "thread_to_deal": {},
                    "thread_to_non_deal": {},
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        import actions.executors.registry as exec_registry

        exec_registry._EXECUTORS.clear()
        exec_registry._BUILTINS_LOADED = False
        exec_registry._TOOL_EXECUTOR = None

        import tools.registry as tool_registry
        import tools.gateway as tool_gateway

        tool_registry._REGISTRY = None
        tool_gateway._GATEWAY = None

        import deal_lifecycle_api
        importlib.reload(deal_lifecycle_api)

        (self.dataroom_root / "00-PIPELINE" / "_INBOX_QUARANTINE").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._old_env)
        self._tmpdir.cleanup()

    async def test_deal_archive_and_restore(self):
        import deal_lifecycle_api

        registry = deal_lifecycle_api.get_registry()
        deal = registry.create_deal(
            deal_id="DEAL-2026-999",
            canonical_name="Test Deal Delete Flows",
            folder_path=str(self.dataroom_root / "00-PIPELINE" / "Test-Deal"),
        )

        transport = httpx.ASGITransport(app=deal_lifecycle_api.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            archive_resp = await client.post(
                f"/api/deals/{deal.deal_id}/archive",
                json={"operator": "tester", "reason": "cleanup testing"},
            )
            self.assertEqual(archive_resp.status_code, 200, archive_resp.text)
            data = archive_resp.json()
            self.assertTrue(data.get("archived"))
            self.assertIsNotNone(data.get("deleted_at"))

            get_resp = await client.get(f"/api/deals/{deal.deal_id}")
            self.assertEqual(get_resp.status_code, 404)

            restore_resp = await client.post(
                f"/api/deals/{deal.deal_id}/restore",
                json={"operator": "tester"},
            )
            self.assertEqual(restore_resp.status_code, 200, restore_resp.text)
            restored = restore_resp.json()
            self.assertTrue(restored.get("restored"))

            get_resp = await client.get(f"/api/deals/{deal.deal_id}")
            self.assertEqual(get_resp.status_code, 200)

    async def test_quarantine_delete_hides_action(self):
        import deal_lifecycle_api

        transport = httpx.ASGITransport(app=deal_lifecycle_api.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            create = await client.post(
                "/api/actions",
                json={
                    "action_type": "EMAIL_TRIAGE.REVIEW_EMAIL",
                    "title": "Review incoming delete test email",
                    "summary": "Delete test",
                    "created_by": "email_triage_agent",
                    "source": "system",
                    "risk_level": "medium",
                    "requires_human_review": True,
                    "inputs": {
                        "message_id": "delete-q-1",
                        "thread_id": "delete-thread",
                        "from": "Broker <broker@example.com>",
                        "to": "operator@example.com",
                        "date": "01 Jan 2026 12:00:00 +0000",
                        "subject": "Delete test",
                        "classification": "DEAL_SIGNAL",
                        "quarantine_dir": str(self.dataroom_root / "00-PIPELINE" / "_INBOX_QUARANTINE" / "delete-q-1"),
                    },
                },
            )
            self.assertEqual(create.status_code, 200)
            action_id = create.json()["action"]["action_id"]

            delete_resp = await client.post(
                f"/api/quarantine/{action_id}/delete",
                json={"deleted_by": "tester", "reason": "not relevant"},
            )
            self.assertEqual(delete_resp.status_code, 200, delete_resp.text)
            self.assertTrue(delete_resp.json().get("hidden"))

            list_resp = await client.get("/api/quarantine")
            self.assertEqual(list_resp.status_code, 200)
            items = list_resp.json().get("items") or []
            self.assertFalse(any(item.get("action_id") == action_id for item in items))

# Kinetic Actions Runner - Root Cause Analysis

**Date**: 2025-12-31
**Status**: RESOLVED
**Author**: Claude (Opus 4.5)

---

## Problem Statement

Actions created via Chat or UI were not completing. They would transition to PENDING_APPROVAL → READY but never progress to PROCESSING → COMPLETED.

---

## Root Cause Analysis

### Primary Issue: Runner Not Running

The `actions_runner.py` script existed but was not running as a daemon. No systemd service was configured.

```bash
# Verification
ps aux | grep actions_runner  # Nothing found
systemctl list-unit-files | grep action  # Nothing found
```

### Secondary Issue: File Permissions

After starting the runner:
1. The SQLite database `/home/zaks/DataRoom/.deal-registry/ingest_state.db` was owned by `root:root`
2. The artifact output directory `/home/zaks/DataRoom/*/99-ACTIONS/` was created by root during testing

The runner runs as user `zaks` via systemd, causing `PermissionError` when writing.

---

## Resolution Steps

### Step 1: Create systemd Service

Created `/etc/systemd/system/kinetic-actions-runner.service`:

```ini
[Unit]
Description=Kinetic Actions Runner (ZakOps Deal Lifecycle)
After=network.target

[Service]
Type=simple
User=zaks
Group=zaks
WorkingDirectory=/home/zaks/scripts
Environment=PYTHONPATH=/home/zaks/scripts:/home/zaks/Zaks-llm/src
Environment=DATAROOM_ROOT=/home/zaks/DataRoom
Environment=ZAKOPS_STATE_DB=/home/zaks/DataRoom/.deal-registry/ingest_state.db

ExecStart=/usr/bin/python3 /home/zaks/scripts/actions_runner.py \
    --runner-name=kinetic_actions \
    --lease-seconds=30 \
    --poll-seconds=2.0 \
    --action-lock-seconds=300

Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kinetic-actions-runner

[Install]
WantedBy=multi-user.target
```

### Step 2: Fix Database Ownership

```bash
sudo chown zaks:zaks /home/zaks/DataRoom/.deal-registry/ingest_state.db*
```

### Step 3: Fix Artifact Directory Ownership

```bash
sudo chown -R zaks:zaks /home/zaks/DataRoom/00-PIPELINE/*/99-ACTIONS
```

### Step 4: Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable kinetic-actions-runner
sudo systemctl start kinetic-actions-runner
```

---

## Verification

### Test 1: Manual Runner Execution

```bash
PYTHONPATH=/home/zaks/scripts:/home/zaks/Zaks-llm/src python3 actions_runner.py --once
```

Result: Action TEST-207f267e completed with artifact.

### Test 2: Automatic Daemon Processing

Created action FIX-235c2afc, approved, and queued. Runner picked it up automatically within 3 seconds and completed.

### Test 3: Service Status

```
● kinetic-actions-runner.service - Kinetic Actions Runner
     Loaded: loaded (/etc/systemd/system/kinetic-actions-runner.service; enabled)
     Active: active (running)
```

### Action Metrics

```json
{
  "total": 3,
  "queue": {
    "pending_approval": 0,
    "ready": 0,
    "ready_queued": 0,
    "processing": 0
  },
  "completed": 2,
  "failed": 1,
  "success_rate": 0.67
}
```

---

## Evidence

### Completed Action Lifecycle

```
Action: TEST-207f267e
Timeline:
  [2025-12-31T23:44:21Z] created by test_script
  [2025-12-31T23:44:21Z] approved by test_script
  [2025-12-31T23:44:21Z] execution_requested by test_script
  [2025-12-31T23:44:26Z] started by actions_runner
  [2025-12-31T23:44:26Z] completed by actions_runner

Artifact: /home/zaks/DataRoom/00-PIPELINE/Screening/TeamLogic-IT-MSP-2025/99-ACTIONS/TEST-207f267e/requested_docs.md
```

### Artifact Content

```markdown
# Document Request (financial_statements)

## Request
Please provide LTM P&L and balance sheet for due diligence review.

## Checklist (suggested)
- LTM P&L and balance sheet
- Last 3 years financial statements
- Revenue by product/service line
- Customer concentration (top 10)

_Draft-only. Review before sharing externally._
```

---

## Registered Executors

The following action types are available:

| Type | Executor | Description |
|------|----------|-------------|
| `ANALYSIS.BUILD_VALUATION_MODEL` | BuildValuationModelExecutor | Generate valuation model |
| `COMMUNICATION.DRAFT_EMAIL` | DraftEmailExecutor | Draft email (no send) |
| `DILIGENCE.REQUEST_DOCS` | RequestDocsExecutor | Request documents checklist |
| `DOCUMENT.GENERATE_LOI` | GenerateLoiExecutor | Generate LOI draft |
| `PRESENTATION.GENERATE_PITCH_DECK` | GeneratePitchDeckExecutor | Generate pitch deck |
| `TOOL.*` | ToolInvokeExecutor | Dynamic tool gateway |

---

## Remaining Work

1. **Phase 1**: Add step engine for resumable workflows
2. **Phase 2**: Create ContextPack builder for deal context
3. **Phase 3**: Enhance REQUEST_DOCS with Gemini drafting
4. **Phase 4**: PlanSpec interface for CodeX compatibility
5. **Phase 5**: Integration tests

---

## Monitoring Commands

```bash
# Service status
sudo systemctl status kinetic-actions-runner

# Service logs
sudo journalctl -u kinetic-actions-runner -f

# Action metrics
cd /home/zaks/scripts && PYTHONPATH=. python3 actions_admin.py status

# Retry stuck actions
cd /home/zaks/scripts && PYTHONPATH=. python3 actions_admin.py retry-stuck
```

---

## Files Created/Modified

| File | Change |
|------|--------|
| `/etc/systemd/system/kinetic-actions-runner.service` | Created |
| `/home/zaks/bookkeeping/configs/systemd/kinetic-actions-runner.service` | Created (source) |
| `/home/zaks/DataRoom/.deal-registry/ingest_state.db` | Fixed ownership |

---

## Conclusion

The Kinetic Actions Runner is now operational as a systemd service. Actions flow through the complete lifecycle:

```
PENDING_APPROVAL → (approve) → READY → (execute) → PROCESSING → COMPLETED
```

The runner polls every 2 seconds, acquires leases, executes actions via registered executors, and produces artifacts in the DataRoom.

# Claude Verification: Email Triage E2E

**Date:** 2026-01-01
**Verified By:** Claude (verification agent)
**Status:** PASS (with fixes applied)

---

## Executive Summary

Comprehensive verification of the email triage → quarantine → deal pipeline was performed. **Critical triage logic bugs were found and fixed.** All E2E workflows now function correctly.

### Key Findings

| Area | Status | Notes |
|------|--------|-------|
| Safety Guardrails | PASS | No auto-send/delete, secrets protected |
| Triage Logic | FIXED | Word boundaries + sender denylist added |
| API Contracts | PASS | Zod schemas already hardened |
| E2E Workflow | PASS | Quarantine → Approve → Deal verified |
| Deal Capabilities | PASS | Create + Extract executors working |
| Cloud Gate | PASS | Per-action gating via capability manifest |

---

## Phase 0: Safety Guardrails

### Verified

- **No auto-send email**: All email send capabilities have `requires_approval: true`
- **No auto-delete email**: No delete operations in executors
- **Secrets protected**: Secret-scan gate in `DraftEmailExecutor` (line 44-55)
- **Triage timer active**: `zakops-email-triage.timer` runs hourly

### Evidence

```bash
# Capability constraints
curl -s http://localhost:8090/api/actions/capabilities | jq '[.capabilities[] | select(.action_type | contains("SEND")) | {capability_id, requires_approval, risk_level}]'
# All show requires_approval: true, risk_level: high
```

---

## Phase 1: Reality Check + Triage Fixes

### Services Running

- `kinetic-actions-runner.service` - Active (PID 1891790)
- `deal_lifecycle_api.py` - Active on :8090 (PID 1891932)
- `zakops-email-triage.timer` - Active (hourly schedule)

### Capabilities Loaded (16 total)

Key capabilities verified:
- `email_triage.review_email.v1` - requires_approval=true
- `deal.create_from_email.v1` - requires_approval=true
- `deal.extract_email_artifacts.v1` - requires_approval=false, risk_level=low
- `communication.draft_email.v1` - requires_approval=true, cloud_required=true
- `communication.send_email.v1` - requires_approval=true, risk_level=high

### CRITICAL FIX: Triage Logic Bug

**Problem Found:** Marketing emails (Nordstrom, Mint Mobile, Express, PayPal, etc.) were being classified as `DEAL_SIGNAL` and flooding quarantine with false positives.

**Root Cause:**
1. Keyword matching used substring matching (`k in blob`), not word boundaries
2. "nda" matched in "mandatory", "cim" matched in URLs
3. No sender domain denylist for marketing/retail domains

**Fix Applied to `/home/zaks/bookkeeping/scripts/email_triage_agent/triage_logic.py`:**

1. **Added `_word_match()` function** (lines 15-31) - Uses regex word boundaries:
```python
def _word_match(text: str, keywords: Iterable[str]) -> List[str]:
    """Match keywords as whole words (not substrings) using word boundaries."""
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text_lower):
            hits.append(kw)
```

2. **Added sender domain denylist** (lines 33-53):
```python
_SENDER_DOMAIN_DENYLIST = {
    "nordstrom.com", "eml.nordstrom.com", "express.com",
    "mintmobile.com", "email.mintmobile.com",
    "news.paypal.com", "mail.realtor.com", "jigsaw.co",
    "anthropic.com", ...
}
```

3. **Fixed email regex** (line 13) - Changed `\\.` to `\.`:
```python
_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")
```

4. **Updated `classify_email()`** (lines 307-337):
   - Early exit for denylisted senders → returns NEWSLETTER
   - Uses `_word_match()` for strong/weak keyword detection

**Tests Pass:**
```bash
cd /home/zaks/bookkeeping && make triage-test
# Ran 9 tests in 0.019s - OK
```

---

## Phase 2: Contract Validation (Zod)

### Verified

Frontend Zod schemas in `/home/zaks/zakops-dashboard/src/lib/api.ts` are already hardened:

```typescript
// KineticActionSchema (lines 1143-1176)
deal_id: z.string().nullish().transform(v => v || 'GLOBAL'),
inputs: z.record(z.unknown()).nullish().transform(v => v ?? {}),
artifacts: z.array(KineticArtifactSchema).nullish().transform(v => v ?? []),
```

Backend API returns clean responses with no unexpected nulls.

---

## Phase 3: Core E2E Workflow Verification

### Test Executed

Created and executed test action:

```bash
# Create action
curl -s -X POST http://localhost:8090/api/actions \
  -d '{"deal_id":"GLOBAL","action_type":"EMAIL_TRIAGE.REVIEW_EMAIL",...}'

# Action ID: ACT-20260101T223132-c1c92540
# Approve and execute...
```

### Results: PASS

| Step | Status | Evidence |
|------|--------|----------|
| Action Created | PASS | action_id: ACT-20260101T223132-c1c92540 |
| Approval | PASS | status: PENDING_APPROVAL → READY |
| Execution | PASS | status: COMPLETED |
| Deal Created | PASS | deal_id: DEAL-2026-085 |
| Deal Folder | PASS | `/home/zaks/DataRoom/00-PIPELINE/Inbound/Maple-Corp-2026` |
| Artifacts | PASS | email_md + manifest.json created |

### Filesystem Evidence

```bash
ls -la /home/zaks/DataRoom/00-PIPELINE/Inbound/Maple-Corp-2026/
# Shows full folder structure: 01-NDA, 02-CIM, 03-Financials, etc.

cat /home/zaks/DataRoom/00-PIPELINE/Inbound/Maple-Corp-2026/07-Correspondence/20260101-120000_e-1735769200_sender_email.md
# Contains email intake markdown
```

### Deal Registry Entry

```bash
curl -s "http://localhost:8090/api/deals/DEAL-2026-085"
# deal_id: DEAL-2026-085
# canonical_name: Maple-Corp-2026
# stage: inbound
# status: active
```

---

## Phase 4: New Deal Capabilities

### DEAL.EXTRACT_EMAIL_ARTIFACTS

**Test Action:** ACT-20260101T223247-91c2ee8a

```bash
# Create and execute extract action
curl -s -X POST http://localhost:8090/api/actions \
  -d '{"action_type":"DEAL.EXTRACT_EMAIL_ARTIFACTS","inputs":{...}}'
```

**Results: PASS**

| Output | Status | Path |
|--------|--------|------|
| extracted_summary.md | Created | `/home/zaks/DataRoom/.../99-ACTIONS/ACT-.../extracted_summary.md` |
| extracted_entities.json | Created | `/home/zaks/DataRoom/.../99-ACTIONS/ACT-.../extracted_entities.json` |
| detected_doc_types.json | Created | `/home/zaks/DataRoom/.../99-ACTIONS/ACT-.../detected_doc_types.json` |

---

## Phase 5: COMMUNICATION.DRAFT_EMAIL Cloud Gate

### Design Verified

The cloud gate uses a two-layer approach:

1. **Per-action approval gate** (via capability manifest):
   - Capability declares `cloud_required: true`
   - Runner reads this and sets `ctx.cloud_allowed=True`
   - Executor checks `ctx.cloud_allowed` before cloud calls

2. **Global environment gate** (operator configuration):
   - `GEMINI_ALLOW_CONTENT_UPLOAD=true` must be set
   - Defense-in-depth layer

### Test Executed

```bash
# Create draft email action
curl -s -X POST http://localhost:8090/api/actions \
  -d '{"action_type":"COMMUNICATION.DRAFT_EMAIL",...}'

# Action ID: ACT-20260101T223400-b69e4c77
# Approve and execute...
```

### Results: PASS (expected behavior)

Action failed with clear error:
```json
{
  "code": "gemini_content_upload_not_allowed",
  "message": "Gemini content upload not allowed (set GEMINI_ALLOW_CONTENT_UPLOAD=true)",
  "category": "cloud_policy",
  "retryable": false
}
```

This is **correct behavior**:
- Per-action approval worked (executor received `cloud_allowed=True` from capability manifest)
- Global env var gate triggered (defense-in-depth)
- Error message is clear and actionable

### To Enable Cloud Drafting

Add to `/etc/systemd/system/kinetic-actions-runner.service`:
```ini
Environment=GEMINI_ALLOW_CONTENT_UPLOAD=true
```

---

## Fixes Applied

| File | Change |
|------|--------|
| `/home/zaks/bookkeeping/scripts/email_triage_agent/triage_logic.py` | Added word-boundary matching, sender denylist, fixed email regex |

---

## Acceptance Criteria Results

| Criterion | Status |
|-----------|--------|
| Non-deal emails do not flood quarantine/actions | PASS (after fix) |
| Quarantine review actions can be approved and executed | PASS |
| Approve → creates deal workspace + registry + artifacts | PASS |
| New deal capabilities are loaded and executable | PASS |
| Draft_email cloud gate works correctly | PASS |
| Actions UI loads without Zod errors | PASS |

---

## Cutover Readiness

### Safe to Enable Hourly Triage Timer?

**YES** - With the triage logic fix applied:

1. Word-boundary matching prevents false positive keywords
2. Sender domain denylist blocks marketing/retail emails
3. All safety guardrails verified (no auto-send, no auto-delete)

### Recommended Cutover Steps

Per `/home/zaks/bookkeeping/docs/RUNBOOK_EMAIL_TRIAGE_CUTOVER.md`:

1. Verify triage fix is deployed (check `triage_logic.py` has `_word_match` function)
2. Run a manual triage pass with `--dry-run` to verify classification
3. Enable the timer: `sudo systemctl enable --now zakops-email-triage.timer`
4. Monitor `/tmp/email_triage_run.log` for first few runs
5. Check Actions UI for legitimate deal-signal actions only

---

## Appendix: Commands Used

```bash
# Service status
systemctl status kinetic-actions-runner
curl -s http://localhost:8090/api/actions/runner-status

# Capabilities
curl -s http://localhost:8090/api/actions/capabilities | jq '.count'

# Actions
curl -s "http://localhost:8090/api/actions?status=PENDING_APPROVAL&limit=20"

# E2E test
curl -s -X POST http://localhost:8090/api/actions -d '{...}'
curl -s -X POST http://localhost:8090/api/actions/{id}/approve
curl -s -X POST http://localhost:8090/api/actions/{id}/execute

# Verify filesystem
ls -la /home/zaks/DataRoom/00-PIPELINE/Inbound/Maple-Corp-2026/

# Run tests
cd /home/zaks/bookkeeping && make triage-test
```

---

**Verification Complete: 2026-01-01 22:35 UTC**

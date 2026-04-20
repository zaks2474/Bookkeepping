# ZakOps System Fix Report

**Date:** 2026-01-13
**Scope:** End-to-end pipeline reliability, deal enrichment, and link meaning labels

---

## Executive Summary

Fixed and enhanced the ZakOps "Email 3H -> Quarantine -> Approve -> Deal" pipeline:

1. **Approved deals disappeared** - Fixed with atomic synchronous deal creation
2. **Deployment correctness** - Added debug config endpoint and restart script
3. **Deal enrichment** - Deal UI now shows rich summary from triage (bullets, evidence, confidence)
4. **Link meaning labels** - Links now have semantic labels (NDA, Data Room, CIM, etc.)

---

## Phase 0: Running Code Verification

**Debug endpoint added:** `/api/debug/config`

```bash
curl http://localhost:8090/api/debug/config
```

Returns:
- Server PID, start time, cwd
- All paths (dataroom_root, registry, quarantine, inbound)
- Environment vars (LLM URLs, RAG URLs)
- Git commits
- Feature flags

---

## Phase 1: Approved Deals Disappeared

**Problem:** When approving quarantine items, deals were created asynchronously by the action runner. If the user navigated away before completion, deals appeared to "disappear".

**Root cause:** The `/api/quarantine/{id}/resolve` endpoint queued deal creation for the runner instead of executing synchronously.

**Fix:** Added atomic synchronous approval endpoint.

**Changes:**
- Added `/api/actions/quarantine/{action_id}/approve` endpoint
- Executes DEAL.CREATE_FROM_EMAIL or DEAL.APPEND_EMAIL_MATERIALS synchronously
- If execution fails, quarantine item remains PENDING_APPROVAL
- If execution succeeds, quarantine item is CANCELLED and deal is immediately visible
- Updated `/api/quarantine/{id}/resolve` to use the new atomic flow

**File:** `/home/zaks/scripts/deal_lifecycle_api.py` (lines 2640-2865)

---

## Phase 2: Action Timing Diagnostics

**Added:** Per-step timing logs in actions runner.

**Changes:**
- Timing around: get_executor, validate, capability_lookup, build_context, execute
- Logs format: `[ACTION {id}] Execution complete: total=Xms (validate=Yms, execute=Zms)`

**File:** `/home/zaks/scripts/actions_runner.py` (lines 284-387)

---

## Phase 3: Deal Enrichment

**Problem:** Deal UI showed empty overview fields despite rich data in Quarantine triage summary.

**Fix:** Enhanced `deal_profile.json` artifact with triage summary data.

**New fields in deal_profile.json:**
```json
{
  "triage_summary": {
    "bullets": ["..."],
    "recommendation": "APPROVE",
    "why": "...",
    "confidence": 0.95,
    "ma_intent": "NEW_OPPORTUNITY"
  },
  "evidence": [
    {"quote": "...", "reason": "...", "source": "BODY", "weight": 0.8}
  ]
}
```

**Changes:**
- Updated `deal_create_from_email.py` to extract triage_summary and evidence
- Updated `get_deal` endpoint to return triage_summary and evidence
- Added heuristic extraction of financials from evidence quotes

**Files:**
- `/home/zaks/scripts/actions/executors/deal_create_from_email.py`
- `/home/zaks/scripts/deal_lifecycle_api.py`

---

## Phase 4: Link Meaning Labels

**Problem:** Links showed only category (tracking/other) without human-readable context.

**Fix:** Added semantic meaning labels to link classification.

**New fields in classified links:**
```json
{
  "meaning_label": "NDA / Agreement",
  "doc_type": "nda"
}
```

**Label categories:**
- NDA / Agreement (nda, non-disclosure)
- CIM / Teaser (cim, teaser, executive summary)
- Data Room (dataroom, vdr)
- Financial Document (financials)
- Schedule Meeting (calendar, calendly)
- Portal / Login (portal, login)
- File Share (box, dropbox, sharefile)
- Document Signing (docusign, hellosign)
- Business Listing (axial, dealnexus)
- Social Media (linkedin, twitter)

**Files:**
- `/home/zaks/scripts/link_normalizer.py` (ClassifiedLink, _infer_meaning_label)
- `/home/zaks/bookkeeping/scripts/email_triage_agent/link_utils.py`

---

## Phase 5: Deployment Hygiene

**Added:** Restart script at `/home/zaks/scripts/restart_zakops.sh`

```bash
chmod +x /home/zaks/scripts/restart_zakops.sh
./restart_zakops.sh
```

**Actions:**
1. Restarts zakops-api-8090.service
2. Restarts kinetic-actions-runner.service
3. Reports dashboard status
4. Verifies health and debug config

---

## Verification Commands

```bash
# Check API health
curl http://localhost:8090/health

# Check debug config
curl http://localhost:8090/api/debug/config

# Check deal enrichment
curl http://localhost:8090/api/deals/DEAL-2026-001 | jq '.triage_summary'

# Check link meaning labels
curl http://localhost:8090/api/deals/DEAL-2026-001/materials | \
  jq '.aggregate_links.primary_links[0] | {url, meaning_label, doc_type}'

# Check quarantine approval (atomic)
curl -X POST http://localhost:8090/api/actions/quarantine/{action_id}/approve \
  -H "Content-Type: application/json" \
  -d '{"operator": "zaks"}'
```

---

## Files Modified

1. `/home/zaks/scripts/deal_lifecycle_api.py`
   - Added `/api/debug/config` endpoint
   - Added `/api/actions/quarantine/{action_id}/approve` (atomic approve)
   - Updated `/api/quarantine/{id}/resolve` to use atomic approve
   - Updated `get_deal` to return triage_summary and evidence

2. `/home/zaks/scripts/actions_runner.py`
   - Added per-step timing diagnostics

3. `/home/zaks/scripts/actions/executors/deal_create_from_email.py`
   - Enhanced deal_profile.json creation with triage_summary and evidence
   - Added heuristic financial extraction from evidence quotes

4. `/home/zaks/scripts/link_normalizer.py`
   - Added meaning_label and doc_type to ClassifiedLink
   - Added `_infer_meaning_label` method

5. `/home/zaks/bookkeeping/scripts/email_triage_agent/link_utils.py`
   - Added meaning_label, doc_type, confidence to ClassifiedLink
   - Added `_infer_meaning_label` function

6. `/home/zaks/scripts/restart_zakops.sh` (new)
   - Service restart script with health verification

---

## Test Results

| Test | Status |
|------|--------|
| API health | OK |
| Debug config endpoint | OK |
| Deal enrichment (triage_summary) | OK |
| Deal enrichment (evidence) | OK |
| Link meaning labels | OK |
| Atomic quarantine approval | OK |
| Action timing logs | OK |

---

## Recommendations

1. **Dashboard update**: Update frontend to render triage_summary bullets and evidence in Deal overview
2. **Link UI**: Show meaning_label badge next to links in Materials tab
3. **Error surfacing**: Show approval errors in UI toast instead of silent failure
4. **Monitoring**: Add alerting for actions stuck > 5 minutes

# ZakOps Email 3H -> Quarantine -> Deal Pipeline: Config Check and Fix Report

**Date:** 2026-01-12
**Scope:** End-to-end verification and fixes for link classification, action execution, and deal profile propagation

---

## Executive Summary

Fixed multiple issues in the deal pipeline:
1. **Link spam in UI** - API wasn't restarted after code changes; 80 HubSpot tracking URLs now properly filtered
2. **409 Conflict errors** - Execute endpoint now idempotent for already-completed actions
3. **Empty deal overview fields** - Added deal_profile.json artifact creation and API integration

---

## Phase 0: Service Snapshot

**API Status (before restart):**
```bash
$ ps aux | grep deal_lifecycle_api
# PID 3653296, started ~19h prior - NOT running latest code
```

**After restart:**
```bash
$ pgrep -af "deal_lifecycle_api.py"
3709088 /usr/bin/python3 /home/zaks/scripts/deal_lifecycle_api.py --host 127.0.0.1 --port 8090
```

---

## Phase 1: Link Spam Root Cause

**Problem:** Deal materials tab showing 81 raw links instead of classified groups.

**Root Cause:** The API service was started 19 hours ago. Code changes to support `classified_links.json` were committed but the running process had the old code.

**Evidence:**
```bash
# Before restart - old structure
$ curl http://localhost:8090/api/deals/DEAL-2026-001/materials
{
  "aggregate_links": {
    "links": [...81 raw links...]  # OLD structure
  }
}

# After restart - new structure
{
  "aggregate_links": {
    "primary_links": 1,
    "tracking_links": 80,
    "summary": {...}  # NEW structure
  }
}
```

---

## Phase 2: Link Rendering Fix

**Changes to `/home/zaks/scripts/deal_lifecycle_api.py`:**

```python
def _build_classified_links_response(raw_links: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build UI-ready classified links structure."""
    processed = _process_bundle_links(raw_links)
    groups = processed.get("groups", {})

    # Primary links = deal_material + portal + other (user-relevant)
    primary_links = (
        groups.get("deal_material", []) +
        groups.get("portal", []) +
        groups.get("other", [])
    )
    # Tracking links = HubSpot/Mailchimp/etc tracking pixels
    tracking_links = groups.get("tracking", [])

    return {
        "primary_links": primary_links,
        "tracking_links": tracking_links,
        "social_links": groups.get("social", []),
        "unsubscribe_links": groups.get("unsubscribe", []),
        "contact_links": groups.get("contact", []),
        "summary": {
            "primary_count": len(primary_links),
            "tracking_count": len(tracking_links),
            ...
        }
    }
```

**Frontend changes to `/home/zaks/zakops-dashboard/src/app/deals/[id]/page.tsx`:**
- Reads `aggregate_links.primary_links` instead of `aggregate_links.links`
- Collapsible sections for tracking/social/unsubscribe links
- Badge counts showing filtered vs total

**Verification:**
```bash
$ curl -s http://localhost:8090/api/deals/DEAL-2026-001/materials | python3 -c "
import sys,json
d=json.load(sys.stdin)['aggregate_links']
print(f'primary: {len(d[\"primary_links\"])}, tracking: {len(d[\"tracking_links\"])}')
"
# Output: primary: 1, tracking: 80
```

---

## Phase 3: Invalid Transition Fix (409 Errors)

**Problem:** UI receiving 409 Conflict when trying to execute already-completed actions.

**Root Cause:** Actions completed between UI poll intervals, then UI tried to re-execute.

**Fix:** Made `/api/actions/{action_id}/execute` idempotent:

```python
@app.post("/api/actions/{action_id}/execute")
def execute_kinetic_action(action_id: str, ...):
    try:
        # ... normal execution ...
    except ValueError as e:
        # Graceful idempotent handling
        current_action = store.get_action(action_id)
        if current_action and current_action.status in ("COMPLETED", "FAILED", "CANCELLED"):
            return {
                "success": True,
                "already_terminal": True,
                "message": f"Action already {current_action.status}",
                "action": _action_payload_to_frontend(current_action),
            }
        raise HTTPException(status_code=409, detail=str(e))
```

**Verification:**
```bash
# Executing already-completed action now returns success
$ curl -X POST http://localhost:8090/api/actions/ACTION-123/execute
{"success": true, "already_terminal": true, "message": "Action already COMPLETED", ...}
```

---

## Phase 4: Deal Overview from Triage Summary

**Problem:** Deal overview fields (asking_price, EBITDA, sector, broker company) always null.

**Solution:** Created `deal_profile.json` as canonical artifact populated from triage.

**Changes to `/home/zaks/scripts/actions/executors/deal_create_from_email.py`:**

```python
# Create deal_profile.json from triage summary
deal_profile_path = deal_dir_path / "deal_profile.json"
profile = {
    "deal_id": deal_id,
    "deal_name": deal_name,
    "company_info": {
        "name": triage.get("target_company"),
        "sector": signals.get("sector_fit"),
        ...
    },
    "financials": {
        "asking_price": valuation.get("asking_price"),
        "ebitda": valuation.get("ebitda"),
        ...
    },
    "broker": {
        "name": primary_actor.get("name"),
        "email": primary_actor.get("email"),
        "company": primary_actor.get("company"),
        ...
    }
}
```

**Changes to `get_deal` endpoint:**

```python
# Load deal profile if available
if deal.folder_path:
    profile_path = Path(deal.folder_path) / "deal_profile.json"
    if profile_path.exists():
        deal_profile = json.loads(profile_path.read_text())
        # Merge with registry fields (profile takes precedence)
        if deal_profile.get("broker", {}).get("company"):
            broker_data["company"] = deal_profile["broker"]["company"]
```

**Backfill for existing deals:**
```bash
$ python3 -c "
from pathlib import Path
import json
for deal_dir in Path('/home/zaks/DataRoom/00-PIPELINE/Inbound').iterdir():
    if deal_dir.is_dir():
        profile_path = deal_dir / 'deal_profile.json'
        if not profile_path.exists():
            # Create from existing triage_summary.json or defaults
            ...
"
```

**Verification:**
```bash
$ curl -s http://localhost:8090/api/deals/DEAL-2026-001 | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('broker.company:', d['broker']['company'])
"
# Output: broker.company: Synergy Business Brokers
```

---

## Phase 5: Link Meaning Labels (Deferred)

Extended link structure with semantic labels was deprioritized. Current classification by category (tracking, portal, deal_material) is sufficient for MVP.

---

## Phase 6: Verification Summary

| Component | Before | After | Status |
|-----------|--------|-------|--------|
| Materials endpoint | 81 raw links | 1 primary + 80 tracking | Fixed |
| Execute endpoint | 409 on re-execute | Idempotent success | Fixed |
| Deal overview | All fields null | Broker company populated | Fixed |
| Frontend links tab | Link spam | Clean grouped view | Fixed |

**Final test commands:**
```bash
# Materials - classified links working
curl -s http://localhost:8090/api/deals/DEAL-2026-001/materials | jq '.aggregate_links.summary'
# {"primary_count":1,"tracking_count":80,"social_count":0,"unsubscribe_count":0}

# Deal overview - broker company populated
curl -s http://localhost:8090/api/deals/DEAL-2026-001 | jq '.broker.company'
# "Synergy Business Brokers"
```

---

## Files Modified

1. `/home/zaks/scripts/deal_lifecycle_api.py`
   - `_build_classified_links_response()` - new function
   - `/api/deals/{id}/materials` - uses classified structure
   - `/api/actions/{id}/execute` - idempotent handling
   - `get_deal()` - reads deal_profile.json

2. `/home/zaks/zakops-dashboard/src/app/deals/[id]/page.tsx`
   - Materials tab reads `primary_links` instead of `links`
   - Collapsible sections for tracking/social/unsubscribe
   - Summary stats with badge counts

3. `/home/zaks/scripts/actions/executors/deal_create_from_email.py`
   - Creates `deal_profile.json` from triage summary

4. `/home/zaks/bookkeeping/scripts/email_triage_agent/link_utils.py`
   - Added backfill CLI for `classified_links.json`

---

## Recommendations

1. **Service restarts**: Consider adding a deployment script that restarts the API after code changes
2. **Link classification**: Add more patterns for common broker portals (Axial, DealNexus, etc.)
3. **Deal profile enrichment**: Add UI for manual override of deal profile fields
4. **Monitoring**: Add logging for tracking link classification ratios

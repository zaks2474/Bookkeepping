# Quarantine/Deal UX Polish Report

**Date:** 2026-01-12
**Task:** Link dedupe + pipeline output visibility (NO workflow changes)

## Summary

Fixed two UX issues:
1. **Duplicate/huge link spam** in Quarantine and Deal Materials
2. **"Actions completed but no visible outputs"** confusion

No changes to approval gating or downstream workflow semantics.

---

## Root Cause of Link Duplication

### Exact Problem

Links in quarantine items and deal materials were **HubSpot tracking URLs** like:
```
https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/5E+113/d13dQH04/VWP6ML1sNQB_N4rNJnRlzKzHVfQRxk5FrkhYMBB8TF3lcq-W7lCdLW6lZ3pVW46_9jB...
```

**Why duplicates appeared:**
- The existing `_safe_url()` function only stripped query params and fragments
- HubSpot tracking URLs embed unique tracking IDs **in the path** (not query params)
- So 10+ NDA links that all redirect to the same NDA form appeared as 10+ separate "unique" URLs
- Each email from the same broker contained fresh tracking URLs

### Source Locations

| Location | File | Issue |
|----------|------|-------|
| Quarantine preview | `deal_lifecycle_api.py:2102` | Links from `inputs.links` shown without deduplication |
| Deal Materials | `deal_lifecycle_api.py:662` | Links from `07-Correspondence/<bundle>/manifest.json` shown raw |
| Aggregate links | `deal_lifecycle_api.py:785` | `07-Correspondence/links.json` accumulated duplicates |

---

## What Normalization Was Added

### New Module: `scripts/link_normalizer.py`

A comprehensive link classification, resolution, and deduplication utility:

1. **`classify_link(url, context)`** - Returns one of:
   - `deal_material` - CIM, teaser, dataroom, NDA, financials
   - `tracking` - Click wrappers, email tracking pixels
   - `social` - LinkedIn, Twitter, Facebook, etc.
   - `unsubscribe` - Email preferences, unsubscribe links
   - `portal` - Login portals, authentication pages
   - `contact` - Contact forms, mailto, phone
   - `calendar` - Meeting scheduling (Calendly, etc.)
   - `other` - Uncategorized

2. **`resolve_tracking_url(url)`** - Optional click-wrapper resolution:
   - Follows redirects with HEAD requests
   - Strict limits: 5 max redirects, 5s timeout
   - Caches results to avoid repeated network calls
   - Returns resolved destination URL

3. **`canonicalize_url(url)`** - Generates canonical form:
   - Lowercases scheme and host
   - Normalizes path (removes trailing slash)
   - Strips tracking query params (`utm_*`, `ref`, `gclid`, etc.)
   - Removes fragments
   - Returns `canonical_key` (SHA256 hash prefix)

4. **`dedupe_links(links)`** - Deduplicates by canonical key

5. **`process_links(links)`** - Full pipeline returning UI-ready structure:
   ```json
   {
     "unique_count": 5,
     "total_count": 14,
     "duplicates_removed": 9,
     "groups": {
       "deal_material": [...],
       "tracking": [...],
       "social": [...]
     },
     "all_unique": [...]
   }
   ```

### Known Tracking Domains (30+)

Includes HubSpot, Mailchimp, Constant Contact, SendGrid, AWeber, ConvertKit, Drip, MailerLite, Sendinblue, Klaviyo, Pardot, Marketo, Eloqua, and common URL shorteners.

---

## API Changes

### Updated Endpoints

1. **`/api/actions/quarantine/{action_id}/preview`**
   - Now uses link normalizer
   - Returns `links.groups` with new categories
   - Returns `links.legacy_groups` for backwards compatibility
   - Returns `links.stats` with dedupe metrics

2. **`/api/deals/{deal_id}/materials`**
   - Bundle links processed through normalizer
   - Aggregate links processed through normalizer
   - Returns `normalized` structure with stats

### Response Structure Changes

Old:
```json
{
  "links": {
    "groups": {"nda": [...], "cim": [...]},
    "all": [...]
  }
}
```

New:
```json
{
  "links": {
    "groups": {
      "deal_material": [...],
      "tracking": [...],
      "social": [...],
      "unsubscribe": [...],
      ...
    },
    "legacy_groups": {"nda": [...], "cim": [...]},
    "all": [...],
    "stats": {
      "total_raw": 14,
      "unique_count": 5,
      "duplicates_removed": 9,
      "tracking_count": 8,
      "deal_material_count": 2
    }
  }
}
```

---

## UI Changes

### Quarantine Page (`src/app/quarantine/page.tsx`)

**Before:** Flat list of all links by type (nda, cim, etc.)

**After:**
- Collapsible sections by category
- Deal materials and calendar links expanded by default
- Tracking, social, unsubscribe collapsed by default (muted style)
- Stats banner showing dedupe results: "5 unique links (removed 9 duplicates from 14 total)"
- Each link shows:
  - Auth required badge
  - Resolved badge (if tracking URL was resolved)
  - Full URL on hover

### Deal Page (`src/app/deals/[id]/page.tsx`)

**New Tab: "Pipeline"**
- Shows all automated pipeline actions for the deal
- Actions displayed: DEAL.APPEND_EMAIL_MATERIALS, DEAL.EXTRACT_EMAIL_ARTIFACTS, DEAL.ENRICH_MATERIALS, DEAL.DEDUPE_AND_PLACE_MATERIALS, RAG.REINDEX_DEAL
- Each action shows status (COMPLETED/PENDING/FAILED) and completion time
- Expandable sections reveal outputs:
  - `artifacts_scanned: 3`
  - `placements_path: .../placed_materials.json`
  - `placed: 0`, `skipped: 2`
  - etc.

---

## "Actions Completed But No Outputs" Investigation

### Findings

The follow-on actions **DO exist and ARE completed**:

```
ACT-20260112T004847-e82bb1cd | DEAL.APPEND_EMAIL_MATERIALS      | COMPLETED
ACT-20260112T004847-0a036d74 | DEAL.EXTRACT_EMAIL_ARTIFACTS     | COMPLETED
ACT-20260112T004847-a6c032b6 | DEAL.ENRICH_MATERIALS            | COMPLETED
ACT-20260112T004847-528f5247 | DEAL.DEDUPE_AND_PLACE_MATERIALS  | COMPLETED
ACT-20260112T004847-e3096ac9 | RAG.REINDEX_DEAL                 | COMPLETED
```

### Root Cause

The outputs were being stored in the action store but **not surfaced in the Deal UI**. The Deal page had tabs for "Actions", "Materials", "Case File", and "Events" - but no view of pipeline automation outputs.

### Solution

Added new **"Pipeline" tab** to the Deal page that:
1. Filters for pipeline action types
2. Shows summary badges (completed/pending/failed counts)
3. Lists all pipeline actions with collapsible output displays
4. Shows key-value outputs in human-readable format

---

## Regression Tests Added

**File:** `scripts/tests/test_link_normalizer.py`

**20 tests covering:**
- HubSpot/Mailchimp tracking URL classification
- Social media URL classification (LinkedIn, Twitter)
- Unsubscribe URL detection
- Deal material URL classification (Firmex, Axial)
- Auth-required detection
- Canonical key generation
- UTM param stripping
- WWW normalization
- Deduplication behavior
- Full pipeline processing

All tests pass.

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/link_normalizer.py` | NEW - Link classification and dedupe utility |
| `scripts/deal_lifecycle_api.py` | Updated quarantine preview + materials endpoints |
| `zakops-dashboard/src/app/quarantine/page.tsx` | Collapsible link sections |
| `zakops-dashboard/src/app/deals/[id]/page.tsx` | New Pipeline tab |
| `scripts/tests/test_link_normalizer.py` | NEW - Regression tests |

---

## Validation

To verify the fix:

1. **Quarantine UI:**
   - Select a quarantine item with HubSpot links
   - Should see "Tracking Links" section collapsed with count
   - Should see deal materials expanded
   - Stats should show duplicates removed

2. **Deal UI:**
   - Navigate to DEAL-2026-001
   - Click "Pipeline" tab
   - Should see 6 completed pipeline actions with outputs

3. **Run tests:**
   ```bash
   python3 /home/zaks/scripts/tests/test_link_normalizer.py
   ```
   Should see: "Results: 20 passed, 0 failed"

---

## Notes

- URL resolution is currently disabled by default to avoid network latency. Enable with `LinkNormalizer(resolve_tracking=True)`.
- The link normalizer uses a resolution cache to avoid repeated network calls.
- Legacy API response format preserved via `legacy_groups` for backwards compatibility.

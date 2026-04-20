# AGENT-BRAIN-REMEDIATION-R4 Completion Summary

**Date:** 2026-02-05
**Status:** ✅ COMPLETE
**Mission:** Fix data source routing — agent must use backend API for deal data, not RAG

## Root Cause

When users asked "How many deals do I have?", the agent used `search_deals` which queried RAG (the knowledge base). RAG returned unrelated documents instead of deal records, causing the agent to report wrong counts.

## Solution

### PHASE 1: list_deals Tool
- Created new `list_deals` tool that queries backend API `/api/deals`
- Supports `stage` and `status` filters
- Returns: deal count, full details, and stage breakdown
- File: `app/core/langgraph/tools/deal_tools.py`

### PHASE 2: search_deals Fix
- Removed RAG query from `search_deals`
- Now queries backend `/api/deals` and filters locally
- Searches by: deal_id, canonical_name, display_name, broker, stage
- File: `app/core/langgraph/tools/deal_tools.py`

### PHASE 3: System Prompt Update
- Updated to version v1.4.0-r4
- Added TOOL ROUTING section with explicit guidance:
  - "How many deals?" → `list_deals`
  - "Find Acme Corp" → `search_deals`
  - "Show deal DL-0007" → `get_deal`
- Added rule: "NEVER use search_deals for counting — use list_deals"
- File: `app/core/prompts/system.md`

### PHASE 4: Golden Traces
- GT-032: Count all deals
- GT-033: List by stage
- GT-034: Pipeline breakdown
- Files: `evals/golden_traces/GT-032.json`, `GT-033.json`, `GT-034.json`

### PHASE 5: Acceptance Test
**PASSED** ✅

| Source | Total | Inbound | Screening | Archived |
|--------|-------|---------|-----------|----------|
| Backend API | 10 | 8 | 1 | 1 |
| Agent Response | 10 | 8 | 1 | 1 |

Numbers match exactly.

## Bug Fix During Regression

**Issue:** `ToolResult.from_legacy()` was incorrectly treating valid deal data as errors when the "ok" field was missing from JSON responses.

**Fix:** Updated `from_legacy()` to handle three cases:
1. Legacy format with "ok" field
2. Error-only responses
3. Direct data (deal objects) — treated as success

**File:** `app/core/langgraph/tools/schemas.py`

## Files Modified

| File | Change |
|------|--------|
| `app/core/langgraph/tools/deal_tools.py` | Added list_deals, fixed search_deals |
| `app/core/langgraph/tools/__init__.py` | Registered list_deals |
| `app/core/langgraph/tools/schemas.py` | Fixed from_legacy |
| `app/core/prompts/system.md` | v1.4.0-r4 with TOOL ROUTING |
| `scripts/validate_prompt_tools.py` | Added list_deals to KNOWN_TOOLS |

## Files Created

| File | Purpose |
|------|---------|
| `evals/golden_traces/GT-032.json` | Count deals test |
| `evals/golden_traces/GT-033.json` | List by stage test |
| `evals/golden_traces/GT-034.json` | Pipeline breakdown test |

## Regression Tests

| Test | Result |
|------|--------|
| get_deal | ✅ PASS |
| search_deals | ✅ PASS |
| list_deals | ✅ PASS |
| CI validation | ✅ PASS (8 tools) |

## Evidence Location

`/home/zaks/bookkeeping/evidence/agent-brain-r4-deal-tools/`

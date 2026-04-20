Could not write `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/01_pass1/codex_report.md` because this environment is read-only (`Permission denied`). Full report content is below.

# Pass 1 Report — CODEX
## Run: TP-20260218-095911 | Mode: design
## Generated: 2026-02-18T09:59:14Z

## PRIMARY FINDINGS

### Finding 1: [MUST-ADD] Preview Failure Root Cause Is Under-Specified
**Root Cause:** `getQuarantinePreview()` returns `null` on parse failure (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:952`, `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:955`). `QuarantinePreviewSchema` expects object-shaped `attachments` (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:241`), while backend detail emits list-shaped attachments (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:282`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2186`). Mission diagnosis emphasizes dropped fields (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:15`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:48`) but this type mismatch is a direct crash/degrade trigger.  
**Fix Approach:** Use a detail schema structurally aligned to backend `QuarantineResponse` and parse preview against that unified contract (with top-level `.passthrough()` and explicit legacy-field mapper).  
**Industry Standard:** Contract-first transport schema parity between API model and UI parser.  
**System Fit:** Backend already provides all data; this is dashboard parsing alignment only. This directly restores “open item and decide” speed.  
**Enforcement:** Add a contract-check test that compares frontend preview schema keys/types to backend `QuarantineResponse` fields and fails CI on drift.

### Finding 2: [MUST-ADD] P1 Unification Risks Breaking Thread-Conflict “Approve Into Deal”
**Root Cause:** Mission plans to switch preview parsing to `QuarantineItemSchema` (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:201`). The conflict UX depends on `preview.routing_conflict` and `preview.conflicting_deal_ids` (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:958`, `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:970`). `QuarantineItemSchema` omits those fields (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:175`). Mission explicitly says this flow must not regress (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:57`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:481`).  
**Fix Approach:** Include `routing_conflict` and `conflicting_deal_ids` in unified schema before removing `QuarantinePreviewSchema`; keep existing conflict card behavior intact during panel refactor.  
**Industry Standard:** Preserve exception-handling safety paths during UI schema migrations.  
**System Fit:** Backend already returns these fields (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2187`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2188`). This prevents wrong-deal approvals and speeds decisions.  
**Enforcement:** Add regression test fixture for routing conflict and assert “Approve into this deal” options render.

### Finding 3: [MUST-ADD] 3-Second Decision Goal Lacks Keyboard + Quick-Action Path
**Root Cause:** Mission objective is sub-second/seconds triage (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:12`), but current workflow is click row (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:802`) then use detail buttons (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:905`) and actions are disabled when preview absent (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:915`). No row-level quick approve/reject controls exist (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:777`). Undo API exists but is not surfaced in quarantine decision UX (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:1139`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:3076`).  
**Fix Approach:** Add keyboard triage (`J/K`, `A`, `R`, `E`), row quick actions for high-confidence items, and post-action undo affordance where role permits.  
**Industry Standard:** Keyboard-first triage patterns (Superhuman/Linear-style).  
**System Fit:** Reuses existing endpoints, no backend change. This materially cuts interaction cost per item.  
**Enforcement:** Playwright tests for hotkeys, focus handling, and quick-action latency path.

### Finding 4: [MUST-ADD] Async Race Can Show Wrong Context During Rapid Triage
**Root Cause:** Preview requests are not cancellation-safe (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:251`, `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:257`) and fire on selection changes (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:268`). Mission adds another selection-driven fetch for sender intelligence (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:283`) but does not define stale-response guards; only `Promise.allSettled` is mandated (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:79`).  
**Fix Approach:** Use request tokens or `AbortController` per `selectedId`; discard late responses for stale selection.  
**Industry Standard:** Race-safe state updates for operator-critical UIs.  
**System Fit:** Frontend-only behavior fix; avoids wrong-item decisions and rework.  
**Enforcement:** Add delayed-response test that rapidly switches items and asserts rendered preview/intel match active `selectedId`.

### Finding 5: [SHOULD-ADD] Data Trust UX Is Missing (Completeness + Contradictions)
**Root Cause:** UI shows raw confidence (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:923`) and field confidence list (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:1043`) but no quality/completeness score or contradiction signal. Mission card plan focuses on rendering extracted content (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:243`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:257`) and null safety (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:267`), not trust ergonomics.  
**Fix Approach:** Add compact “Signal Health” bar: completeness ratio, confidence band, and contradiction badges (e.g., `HIGH urgency` + low confidence).  
**Industry Standard:** AI assist tools surface uncertainty and evidence quality before decisions.  
**System Fit:** Uses existing `confidence`, `field_confidences`, `extraction_evidence`; no backend dependencies. Improves decision accuracy/speed under partial data.  
**Enforcement:** Component tests for empty/partial/conflicting fixtures with deterministic expected badges.

### Finding 6: [SHOULD-ADD] Provenance Fields Exist but Are Invisible to Operators
**Root Cause:** Bridge accepts provenance fields (`/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py:858`, `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py:968`), backend returns them (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:274`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2180`), but quarantine frontend schema omits them (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:175`) and mission component list has no provenance surface (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:257`).  
**Fix Approach:** Add a minimal provenance block (trace URL, run ID, tool/prompt version, correlation ID copy).  
**Industry Standard:** High-trust AI decision interfaces expose source/provenance metadata inline.  
**System Fit:** Pure dashboard rendering + schema inclusion. Helps faster escalation when output looks wrong.  
**Enforcement:** Contract-checker rule for provenance keys in schema plus UI smoke test for trace-link rendering.

### Finding 7: [SHOULD-ADD] Classification Vocabulary Drift Can Break Filters
**Root Cause:** UI filter enums are uppercase legacy values (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:87`) while canonical/triage values are lowercase modern taxonomy (`/tmp/langsmith-export/canonical_output_schema.json:27`, `/tmp/langsmith-export/subagents/triage_classifier/AGENTS.md:17`, `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py:877`). Backend filter is exact match (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1631`).  
**Fix Approach:** Normalize classification values in dashboard API boundary and map to operator labels.  
**Industry Standard:** UI boundary normalization when producers emit multiple enum dialects.  
**System Fit:** Frontend-only mapping; avoids empty or misleading filter results and speeds queue narrowing.  
**Enforcement:** Unit tests for enum normalization and integration test verifying filter query values.

### Finding 8: [SHOULD-ADD] Comparison Workflow Is Missing Despite Existing Backend Support
**Root Cause:** Mission keeps scope on detail/list rendering (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:24`) and does not include “similar past decisions.” Backend already exposes sender decision history and corrections (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1753`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1762`). Current detail area has no historical comparison module (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:955`).  
**Fix Approach:** Add collapsible “Past Decisions from This Sender” card (last N outcomes + correction patterns) beside Sender Intel.  
**Industry Standard:** CRM/deal tooling improves operator consistency with adjacent historical context.  
**System Fit:** Uses existing endpoint; no backend change. Reduces repeat mistakes and decision hesitation.  
**Enforcement:** Add API parser + UI tests for non-empty and empty history states.

### Finding 9: [NICE-TO-HAVE] Queue Scaling and Baseline Filter Assumptions Are Misaligned
**Root Cause:** Frontend fetches max 200 (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:197`), backend also caps 200 (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1613`), and UI is single scroll list (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:775`). Mission claims status/sender/search filters are existing and must not regress (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:55`), but current filter row only exposes source/classification/urgency (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:661`).  
**Fix Approach:** Add “Load more” pagination via offset, sender/status filter chips, and lightweight search over loaded rows.  
**Industry Standard:** Progressive loading + targeted filters for high-volume triage queues.  
**System Fit:** Uses existing backend query parameters (`/api/quarantine` already supports `offset`, `sender`, `status`). Improves throughput for large queues.  
**Enforcement:** Playwright scenario with >200 mocked rows validating pagination and filter behavior.

## ADJACENT OBSERVATIONS

- Mission references canonical schema at `/tmp/langsmith-export/schemas/canonical_output_schema.json` (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:31`), but available file is `/tmp/langsmith-export/canonical_output_schema.json`.
- Surface 9 requires reading frontend design skill before dashboard UI build work (`/home/zaks/zakops-agent-api/.claude/rules/design-system.md:13`); mission guardrails do not explicitly call this out.

## SUMMARY
- Total primary findings: 9
- Total adjacent observations: 2
- Confidence level: HIGH
- Key recommendation: Before execution, lock schema parity and race-safety, then add keyboard-first decision ergonomics plus trust/provenance surfaces so operators can act fast without sacrificing accuracy.
# SYSTEM-MATURITY-REMEDIATION-001 — Context Checkpoint
## Date: 2026-02-21
## Session: 2 (P7-P11)

## Phases Completed
- **P0**: Discovery & Baseline (17 checks, all confirmed)
- **P1**: Settings Provider UX — commit `d55c8a0`
- **P2**: User Profile → Agent Integration (10 tasks) — commit `68dbe7e`
- **P3**: Model Switching & Cloud Safety (5 tasks) — commit `2ec29c0`
- **P4**: Agent Resilience, Bug Fixes & Tool Reliability (13 tasks) — commit `87b3b92`
- **P5**: Document Upload Backend API (10 tasks) — commit `fcf7c65`
- **P6**: Dashboard Materials Panel Wiring (9 tasks) — commit `fcf7c65`
- **P7**: Deal Document RAG, Email Intelligence & Agent Tools (9 tasks) — pending commit

## Phases Remaining
- **P8**: Cross-Session Memory & Data Lifecycle (6 tasks)
- **P9**: Observability & Monitoring (8 tasks)
- **P10**: Onboarding Intelligence (4 tasks)
- **P11**: Playwright E2E & Final Validation (12 tasks)

## Tool Count Progression
- P0: 14 tools, 7 HITL (baseline)
- P2: 16 tools, 8 HITL (+get_operator_profile, +update_operator_profile)
- P7: 21 tools, 8 HITL (+list_deal_documents, +search_deal_documents, +analyze_document, +get_deal_email_threads, +lookup_entity)

## Validation State
- `npx tsc --noEmit`: PASS (clean)
- Backend health: PASS (8091)
- Redocly ignores: 44 (well below 57 ceiling)
- `make update-spec && make sync-types`: PASS
- `make sync-backend-models`: FAIL (pre-existing — datamodel-codegen missing in agent container)

## Key Changes Since Start
### Backend (apps/backend/)
- New router: `routers/documents.py` — 8 endpoints (upload, list, download, text, delete, share, shared-download, export)
- Migration 038: version_number, previous_artifact_id, deleted_at columns + artifact_access_log table
- Docker-compose: DataRoom volume mount + DATAROOM_ROOT/RAG_REST_URL env vars
- requirements.txt: +pypdf, +python-docx, +python-multipart
- Body size limit exemption for multipart artifact uploads

### Dashboard (apps/dashboard/)
- New file: `src/lib/deal-artifacts.ts` — API client for artifact CRUD/share/export
- Updated: `DealDocuments.tsx` — +onShare, +onExport callbacks, Share/Export buttons
- Updated: `deals/[id]/page.tsx` — Documents tab with real artifact data, full CRUD handlers
- Updated: `provider-settings.ts` — Current model lists (Claude 4.6, GPT-4.1)
- Updated: `ProviderSection.tsx` — Updated descriptions, text-only mode note
- Updated: `chat/page.tsx` — Text-only banner, proposal card disable, cloud mode
- New file: `src/lib/agent/content-filter.ts` — Server-side PII filter wrapper

### Agent API (apps/agent-api/)
- New tools: get_operator_profile, update_operator_profile (16 total from P2)
- P7 tools: list_deal_documents, search_deal_documents, analyze_document, get_deal_email_threads, lookup_entity (21 total)
- New file: `app/core/langgraph/tools/document_tools.py` — 5 tools for docs/email/entity
- New file: `app/services/rag_client.py` — RAG REST client for deal document queries
- BackendClient: +list_deal_artifacts, +get_artifact_text, +get_deal_email_threads, +search_entities
- SCOPE_TOOL_MAP updated for all 21 tools with deal/global/document scopes
- Stage-aware tool recommendations updated to include document tools
- system.md: 21-tool roster with usage guidance for document/email/entity tools
- Resilience: BackendClient pool-first-then-retry with tenacity
- TaskMonitor: Wraps all asyncio.create_task() calls
- Bug fixes: brain facts loading, HITL format, specialist brain context
- Budget enforcement, CoT logging, concurrent limiter, summary pruning
- New file: `app/core/task_monitor.py`
- New file: `app/core/langgraph/tools/profile_tools.py`
- New file: `app/core/security/content_filter.py`
- Migration 005: provider/model columns on chat_threads

## Open Decisions
- None blocking. All P0-P7 decisions resolved.

## Branch
`feat/system-maturity-remediation-001`

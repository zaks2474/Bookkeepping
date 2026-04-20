─────────────────────────────────────────────────────────────────────────────────╮
│ Plan to implement │
│ │
│ COL-GAP-FULLSTACK-001 — Full-Stack Fix for QA Verification Gaps │
│ │
│ Context │
│ │
│ QA-COL-DEEP-VERIFY-001A/B/C ran 214 gates against the COL design spec (3,276 │
│ lines). │
│ Result: CONDITIONAL PASS — 2 SCOPE_GAP items and 3 PARTIAL items flagged. │
│ │
│ After forensic investigation: │
│ - Proposal FOR UPDATE (VF-07.4): Already correctly implemented │
│ (chat_repository.py:567 uses SELECT ... FOR UPDATE). No fix needed. │
│ - 2 from 001A: Non-issues (raw httpx in RAG = legitimate, injection_guard │
│ module functions = correct design). No fix needed. │
│ │
│ That leaves 2 real gaps requiring full-stack fixes: │
│ ┌────────────┬───────────┬─────────┬──────────┬──────────────────────────────── │
│ ┐ │
│ │ Gap │ VF Codes │ Spec │ Severity │ Problem │
│ │ │
│ ├────────────┼───────────┼─────────┼──────────┼──────────────────────────────── │
│ ┤ │
│ │ Quarantine │ VF-04.1, │ S4, │ │ deal_transitions table missing │
│ │ │
│ │ FSM │ VF-04.2 │ ADR-001 │ MEDIUM │ entirely; quarantine approval │
│ │ │
│ │ │ │ │ │ bypasses FSM ledger │
│ │ │
│ ├────────────┼───────────┼─────────┼──────────┼──────────────────────────────── │
│ ┤ │
│ │ Reflexion │ VF-03.1, │ S8.3 │ MEDIUM │ should_revise flag set but │
│ │ │
│ │ Loop │ VF-03.4 │ │ │ ignored; no refinement loop │
│ │ │
│ └────────────┴───────────┴─────────┴──────────┴──────────────────────────────── │
│ ┘ │
│ Critical Discovery: deal_transitions Table Does Not Exist │
│ │
│ The deal_transitions table is referenced in: │
│ - workflow.py:229-246 (INSERT) — will fail at runtime │
│ - workflow.py router GET /{deal_id}/transitions — queries nonexistent table │
│ - OpenAPI spec already includes the endpoint │
│ │
│ But no CREATE TABLE exists in any migration file. │
│ │
│ --- │
│ Phase 0: Discovery & Baseline │
│ │
│ Purpose: Verify gaps are current, capture baseline. │
│ │
│ - P0-01: make validate-local — baseline PASS │
│ - P0-02: Verify deal_transitions table doesn't exist (SELECT │
│ to_regclass('zakops.deal_transitions') → NULL) │
│ - P0-03: Verify no refine_if_needed in agent-api codebase │
│ - P0-04: Verify no MAX_REFINEMENTS constant exists │
│ │
│ Gate P0: All checks confirm gaps present. │
│ │
│ --- │
│ Phase 1: Database — Create deal_transitions Table │
│ │
│ Files: NEW │
│ /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql + │
│ rollback │
│ │
│ CREATE TABLE IF NOT EXISTS zakops.deal_transitions ( │
│ id UUID PRIMARY KEY DEFAULT gen_random_uuid(), │
│ deal_id VARCHAR(20) NOT NULL REFERENCES zakops.deals(deal_id) ON │
│ DELETE CASCADE, │
│ from_stage VARCHAR(50), -- NULL for initial creation │
│ to_stage VARCHAR(50) NOT NULL, │
│ actor_id VARCHAR(255) NOT NULL DEFAULT 'system', │
│ actor_type VARCHAR(50) NOT NULL DEFAULT 'system', │
│ correlation_id VARCHAR(255), │
│ reason TEXT, │
│ idempotency_key VARCHAR(64), │
│ created_at TIMESTAMPTZ NOT NULL DEFAULT NOW() │
│ ); │
│ CREATE INDEX idx_deal_transitions_deal_id ON zakops.deal_transitions(deal_id); │
│ CREATE INDEX idx_deal_transitions_created_at ON │
│ zakops.deal_transitions(created_at); │
│ │
│ Column names MUST match workflow.py:231-234 exactly. │
│ │
│ Gate P1: Table exists, columns verified against workflow.py INSERT. │
│ │
│ --- │
│ Phase 2: Backend — Quarantine Approval Writes Ledger Entry │
│ │
│ File: @zakops-backend/src/api/orchestration/main.py (~line 1796) │
│ │
│ After the existing INSERT INTO zakops.deals, add: │
│ await conn.execute(""" │
│ INSERT INTO zakops.deal_transitions ( │
│ deal_id, from_stage, to_stage, actor_id, actor_type, │
│ correlation_id, reason │
│ ) VALUES ($1, NULL, 'inbound', $2, 'system', $3, $4) │
│ """, deal_id, process.processed_by or 'system', │
│ str(item.get('correlation_id') or ''), │
│ 'Promoted from quarantine approval') │
│ │
│ from_stage=NULL because this is initial creation, not a transition. │
│ │
│ Also verify: workflow.py:229-246 INSERT already matches the table schema — no │
│ changes needed there (it was always correct, table just didn't exist). │
│ │
│ Gate P2: Quarantine approval writes to deal_transitions. GET │
│ /api/deals/{deal_id}/transitions returns data. │
│ │
│ --- │
│ Phase 3: Dashboard — Display Transitions on Deal Detail │
│ │
│ Files: │
│ - @zakops-agent-api/apps/dashboard/src/lib/api.ts — add │
│ getDealTransitions() │
│ - @zakops-agent-api/apps/dashboard/src/app/deals/**[id]/page.tsx — add │
│ transitions section │
│ - Dashboard API route if needed (proxy to backend) │
│ │
│ The GET /api/deals/{deal_id}/transitions endpoint already exists in workflow.py │
│ router and in the OpenAPI spec. The dashboard just needs to call it and │
│ display it. │
│ │
│ Display: timeline/table showing from_stage → to_stage, actor, reason, │
│ timestamp. Initial creation shows "Created → inbound". │
│ │
│ Gate P3: Deal detail page shows transitions timeline. npx tsc --noEmit passes. │
│ │
│ --- │
│ Phase 4: Agent Service — Reflexion Refinement Loop │
│ │
│ Files: │
│ - @zakops-agent-api/apps/agent-api/app/services/reflexion.py — add │
│ MAX_REFINEMENTS=2 + refine_if_needed() │
│ - @zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py — wire │
│ loop at ~line 1060 │
│ │
│ reflexion.py additions: │
│ │
│ MAX_REFINEMENTS = 2 │
│ │
│ async def refine_if_needed(self, original_response, critique, evidence, │
│ brain_facts): │
│ """Re-generate response incorporating critique feedback. Returns (refined, │
│ new_critique).""" │
│ # Build refinement prompt with critique issues + suggestion │
│ # Call LLM to regenerate │
│ # Re-critique the refined response │
│ # Return (refined_response, new_critique) │
│ │
│ graph.py loop (replaces lines 1060-1092): │
│ │
│ critique = await reflexion_service.critique(response=assistant_message, ...) │
│ refinement_count = 0 │
│ current_response = assistant_message │
│ │
│ while critique.should_revise and refinement_count < MAX_REFINEMENTS: │
│ current_response, critique = await reflexion_service.refine_if_needed( │
│ original_response=current_response, critique=critique, ...) │
│ refinement_count += 1 │
│ │
│ # Store critique with refinement_count + was_refined in snapshot JSONB │
│ │
│ No schema migration needed — critique_result JSONB in turn_snapshots already │
│ accepts arbitrary fields. │
│ │
│ If response was refined, update the assistant message content in the graph │
│ state. │
│ │
│ Gate P4: refine_if_needed() exists, loop wired, snapshot stores │
│ refinement_count + was_refined. │
│ │
│ --- │
│ Phase 5: Dashboard — Refinement Badge in Chat │
│ │
│ Files: │
│ - /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndica │
│ tor.tsx — update RefinedBadge │
│ - @zakops-agent-api/apps/dashboard/src/app/chat/page.tsx — update │
│ ChatMessage type │
│ │
│ Update RefinedBadge to: │
│ - Show "Refined (2x)" when was_refined=true with iteration count │
│ - Show "Critiqued" when critique ran but was_refined=false │
│ - Show nothing when no critique data │
│ │
│ Gate P5: Badge renders correctly. npx tsc --noEmit passes. │
│ │
│ --- │
│ Phase 6: Documentation & Final Verification │
│ │
│ - Run make validate-local — PASS │
│ - Run npx tsc --noEmit — PASS │
│ - Update @bookkeeping/CHANGES.md │
│ - Write completion report │
│ │
│ Gate P6: All validations pass, CHANGES.md updated. │
│ │
│ --- │
│ Dependency Graph │
│ │
│ Phase 0 (Discovery) │
│ │ │
│ ├─────────────────────┐ │
│ ▼ ▼ │
│ Phase 1 (DB Migration) Phase 4 (Reflexion Service) │
│ │ │ │
│ ▼ ▼ │
│ Phase 2 (Backend Ledger) Phase 5 (Chat Badge) │
│ │ │ │
│ ▼ │ │
│ Phase 3 (Deal Detail UI) │ │
│ │ │ │
│ └─────────┬───────────┘ │
│ ▼ │
│ Phase 6 (Docs + Verification) │
│ │
│ Phases 1-3 and 4-5 are independent tracks. │
│ │
│ --- │
│ Acceptance Criteria (10 total) │
│ AC: AC-1 │
│ Description: zakops.deal_transitions table exists with correct schema │
│ ──────────────────────────────────────── │
│ AC: AC-2 │
│ Description: Quarantine approval inserts ledger entry (from_stage=NULL, │
│ to_stage='inbound') │
│ ──────────────────────────────────────── │
│ AC: AC-3 │
│ Description: GET /api/deals/{deal_id}/transitions returns transition history │
│ ──────────────────────────────────────── │
│ AC: AC-4 │
│ Description: Deal detail page shows transitions timeline │
│ ──────────────────────────────────────── │
│ AC: AC-5 │
│ Description: refine_if_needed() method + MAX_REFINEMENTS=2 exist in │
│ reflexion.py │
│ ──────────────────────────────────────── │
│ AC: AC-6 │
│ Description: Graph.py refinement loop iterates up to MAX_REFINEMENTS when │
│ should_revise=True │
│ ──────────────────────────────────────── │
│ AC: AC-7 │
│ Description: Snapshot critique_result JSONB includes refinement_count + │
│ was_refined │
│ ──────────────────────────────────────── │
│ AC: AC-8 │
│ Description: Chat RefinedBadge shows iteration count and distinguishes │
│ critiqued │
│ vs refined │
│ ──────────────────────────────────────── │
│ AC: AC-9 │
│ Description: make validate-local + npx tsc --noEmit pass (no regressions) │
│ ──────────────────────────────────────── │
│ AC: AC-10 │
│ Description: CHANGES.md updated with all modifications │
│ --- │
│ Files Modified Summary │
│ File: db/migrations/031_deal_transitions_ledger.sql │
│ Phase: 1 │
│ Change: NEW — create table + indexes │
│ ──────────────────────────────────────── │
│ File: db/migrations/031_deal_transitions_ledger_rollback.sql │
│ Phase: 1 │
│ Change: NEW — rollback script │
│ ──────────────────────────────────────── │
│ File: src/api/orchestration/main.py │
│ Phase: 2 │
│ Change: Add deal_transitions INSERT after deal creation │
│ ──────────────────────────────────────── │
│ File: apps/dashboard/src/lib/api.ts │
│ Phase: 3 │
│ Change: Add getDealTransitions() │
│ ──────────────────────────────────────── │
│ File: apps/dashboard/src/app/deals/[id]/page.tsx │
│ Phase: 3 │
│ Change: Add transitions timeline section │
│ ──────────────────────────────────────── │
│ File: apps/agent-api/app/services/reflexion.py │
│ Phase: 4 │
│ Change: Add MAX_REFINEMENTS + refine_if_needed() │
│ ──────────────────────────────────────── │
│ File: apps/agent-api/app/core/langgraph/graph.py │
│ Phase: 4 │
│ Change: Wire refinement loop in _post_turn_enrichment() │
│ ──────────────────────────────────────── │
│ File: apps/dashboard/src/components/chat/CitationIndicator.tsx │
│ Phase: 5 │
│ Change: Update RefinedBadge with iteration display │
│ ──────────────────────────────────────── │
│ File: apps/dashboard/src/app/chat/page.tsx │
│ Phase: 5 │
│ Change: Update ChatMessage type with refinement fields │
│ Pre-Mortem Risks │
│ Risk: Migration columns don't match workflow.py INSERT │
│ Mitigation: Checkpoint: character-by-character column comparison │
│ ──────────────────────────────────────── │
│ Risk: Refinement loop degrades response quality │
│ Mitigation: MAX_REFINEMENTS=2 hard cap + bounded LLM call │
│ ──────────────────────────────────────── │
│ Risk: CRLF in .sql files │
│ Mitigation: sed -i 's/$//' on all new files │
│ ──────────────────────────────────────── │
│ Risk: deal_id FK type mismatch │
│ Mitigation: Verify deals.deal_id is VARCHAR(20) before FK │
╰─────────────────────────────────────────────────────────────────────────────────╯
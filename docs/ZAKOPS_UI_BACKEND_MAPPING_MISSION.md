# ZakOps UI-Backend Mapping Mission
## Lab Loop Builder Prompt v2.0

---

## SYSTEM ROLE

You are Claude Code (Builder) working in a Lab Loop environment. Your mission is to make the existing ZakOps Next.js dashboard fully functional end-to-end by mapping every UI feature to concrete backend integrations, implementing any missing wiring, and validating with deterministic tests + artifacts.

**Project Context**: ZakOps is a Deal Lifecycle Management system serving as the foundation for SACS AIOps 3.0. The architecture follows a four-plane design (Agent, Execution, Data, Observability) with execution-first database patterns.

---

## CRITICAL CONSTRAINTS (NON-NEGOTIABLE)

1. **Preserve what already works.** Do NOT refactor "working core" (Docker stack, existing Agent API, working auth/session, working gates, **Agent Visibility Layer components**) unless a change is required to wire a UI feature and is proven safe by tests.

2. **No dead UI**: No placeholder handlers, no TODO buttons, no silent failures. Every user-facing element must have a functional backend integration.

3. **No raw-content leakage**: Do not log plaintext prompts, messages, tool args/results. Use safe logging pattern:
   ```typescript
   // CORRECT: Safe logging
   log.info('agent_action', {
     action_id: hash(action),
     content_length: content.length,
     trace_id: ctx.traceId
   });

   // WRONG: Content leakage
   log.info('agent_action', { prompt: userPrompt, response: agentResponse });
   ```

4. **Canonical contracts**: Do not guess endpoints. The known service topology is:
   - **Deal Lifecycle API**: `localhost:8090` (or via tunnel: `zakops-bridge.zaksops.com`)
   - **RAG REST API**: `localhost:8052`
   - **MCP Server**: `localhost:9100` (transport: `streamable-http`, `stateless_http=True`)
   - **Frontend**: `localhost:3003`

   If any endpoint is uncertain, add/extend a **contract probe** and lock the contract before implementation.

5. **Must be verifiable**: Every change must be covered by Gate + QA evidence (tests + artifacts).

6. **UI → Backend wiring only**: Do NOT do "UI polish" or redesign unless required to make a workflow usable.

7. **Execution-first patterns**: All agent operations must follow the execution-first database design:
   - `agent_runs` table for durable execution tracking
   - `agent_events` table for append-only event logging
   - Standardized response shapes (no freeform JSON chaos)

---

## KNOWN ARCHITECTURE CONTEXT

### Four-Plane Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    AGENT PLANE                          │
│  (LangGraph workflows, tool orchestration, reasoning)   │
├─────────────────────────────────────────────────────────┤
│                   EXECUTION PLANE                       │
│  (Durable execution, checkpoints, queue/worker systems) │
├─────────────────────────────────────────────────────────┤
│                     DATA PLANE                          │
│  (Postgres, agent_runs, agent_events, deal entities)    │
├─────────────────────────────────────────────────────────┤
│                  OBSERVABILITY PLANE                    │
│  (Traces, metrics, safe logging, activity feeds)        │
└─────────────────────────────────────────────────────────┘
```

### Agent Visibility Layer (ALREADY COMPLETED - PRESERVE)
The following components are implemented and working:
- **Dashboard widgets** showing agent activity summaries
- **Header status indicators** for real-time agent state
- **Onboarding demos** for agent interaction patterns
- **Full activity pages** with detailed agent event history
- Consistent visual feedback patterns (hover effects, click destinations, accurate data counts)

### Execution-First Database Schema (Reference)
```sql
-- Core execution tracking
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY,
    workflow_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL, -- 'pending', 'running', 'completed', 'failed', 'awaiting_approval'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    checkpoint_data JSONB,
    deal_id UUID REFERENCES deals(id)
);

CREATE TABLE agent_events (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES agent_runs(id),
    event_type VARCHAR NOT NULL,
    event_data JSONB NOT NULL, -- Standardized shape, NOT freeform
    created_at TIMESTAMP DEFAULT NOW()
);
```

### MCP Tool Naming Convention
Tools exposed via MCP must use explicit naming:
- Format: `ZakOps_{action}_{resource}` (e.g., `ZakOps_check_system_health`, `ZakOps_get_deal_status`)
- This is required for proper tool binding at runtime

---

## WHERE TO WRITE OUTPUT DOCS (REQUIRED)

Create folder structure:
```
/home/zaks/bookkeeping/docs/ui-backend-mapping/
├── UI_INVENTORY.md
├── UI_BACKEND_MAPPING.md
├── UI_BACKEND_MAPPING.json
├── GAPS_AND_FIX_PLAN.md
├── CONTRACT_PROBES.md
├── QA_HANDOFF.md
├── BUILDER_REPORT.md
└── gate_artifacts/
    ├── ui_smoke_test.log
    ├── ui_smoke_results.json
    ├── contract_probe_results.json
    └── screenshots/
```

---

## INPUTS YOU MUST READ FIRST (IN ORDER)

1. `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Implementation-Roadmap-combine.v2.md` - Master roadmap
2. `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md` - Locked architectural decisions
3. `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md` (if present) - HITL implementation status
4. Any existing runbook(s) under `/home/zaks/bookkeeping/docs/` relevant to endpoints/auth
5. Existing contract probes in `scripts/probes/` (if any)

**After reading, summarize key decisions that affect UI wiring in your first output.**

---

## REPO DISCOVERY (DO THIS FIRST)

Locate the Next.js dashboard repo:
```bash
# Search patterns
find /home/zaks -name "next.config.*" -o -name "package.json" 2>/dev/null | head -20
grep -r '"next"' /home/zaks/*/package.json 2>/dev/null
ls -la /home/zaks/zakops-*/
```

Likely paths:
- `/home/zaks/zakops-frontend`
- `/home/zaks/zakops-dashboard`
- `/home/zaks/zakops-web`
- `/home/zaks/zakops-ui`

Once found, define and export:
```bash
export UI_REPO=<absolute path>
export DEAL_API_BASE=http://localhost:8090
export RAG_API_BASE=http://localhost:8052
export MCP_SERVER_BASE=http://localhost:9100
export TUNNEL_BASE=https://zakops-bridge.zaksops.com
```

---

## LAB LOOP EXECUTION MODEL

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  BUILDER │ ──▶ │   GATE   │ ──▶ │    QA    │
│  (You)   │     │ (Scripts)│     │ (Verify) │
└──────────┘     └──────────┘     └──────────┘
     │                                  │
     └──────────── Next Mission ◀───────┘
```

You must generate artifacts so QA can verify without guesswork.

---

## GATES (REQUIRED)

### Gate Script Location
Create or use: `${UI_REPO}/scripts/gates/ui_e2e_gate.sh`

### Gate Script Template
```bash
#!/bin/bash
set -e

ARTIFACT_DIR="/home/zaks/bookkeeping/docs/ui-backend-mapping/gate_artifacts"
mkdir -p "$ARTIFACT_DIR"

echo "=== UI E2E Gate ===" | tee "$ARTIFACT_DIR/ui_smoke_test.log"
echo "Started: $(date -Iseconds)" | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"

# 1. Lint
echo ">> Running lint..." | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"
npm run lint 2>&1 | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"

# 2. Typecheck
echo ">> Running typecheck..." | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"
npm run typecheck 2>&1 | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"

# 3. Unit tests
echo ">> Running unit tests..." | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"
npm test -- --passWithNoTests 2>&1 | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"

# 4. Contract probes (verify backend availability)
echo ">> Running contract probes..." | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"
./scripts/probes/verify_contracts.sh 2>&1 | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"

# 5. Playwright E2E
echo ">> Running Playwright E2E..." | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"
npx playwright test --reporter=json > "$ARTIFACT_DIR/ui_smoke_results.json" 2>&1

echo "=== Gate Complete ===" | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"
echo "Finished: $(date -Iseconds)" | tee -a "$ARTIFACT_DIR/ui_smoke_test.log"
```

### Contract Probe Script Template
Create: `${UI_REPO}/scripts/probes/verify_contracts.sh`
```bash
#!/bin/bash
set -e

RESULTS_FILE="/home/zaks/bookkeeping/docs/ui-backend-mapping/gate_artifacts/contract_probe_results.json"

echo '{"probes": [' > "$RESULTS_FILE"

# Deal API health
DEAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8090/health || echo "000")
echo '{"service": "deal_api", "endpoint": "/health", "status": "'$DEAL_STATUS'"},' >> "$RESULTS_FILE"

# RAG API health
RAG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8052/health || echo "000")
echo '{"service": "rag_api", "endpoint": "/health", "status": "'$RAG_STATUS'"},' >> "$RESULTS_FILE"

# MCP Server health
MCP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9100/health || echo "000")
echo '{"service": "mcp_server", "endpoint": "/health", "status": "'$MCP_STATUS'"}' >> "$RESULTS_FILE"

echo ']}' >> "$RESULTS_FILE"

# Validate all services are up
if [[ "$DEAL_STATUS" != "200" ]] || [[ "$RAG_STATUS" != "200" ]] || [[ "$MCP_STATUS" != "200" ]]; then
    echo "ERROR: One or more services are not healthy"
    cat "$RESULTS_FILE"
    exit 1
fi

echo "All contract probes passed"
```

---

## DELIVERABLES (REQUIRED)

### A) UI INVENTORY (Complete)
**File**: `/home/zaks/bookkeeping/docs/ui-backend-mapping/UI_INVENTORY.md`

Must include:

```markdown
# ZakOps UI Inventory

## Routes/Pages
| Route | File | Description | Auth Required |
|-------|------|-------------|---------------|
| /dashboard | app/dashboard/page.tsx | Main dashboard | Yes |
| /deals | app/deals/page.tsx | Deal list view | Yes |
| /deals/[id] | app/deals/[id]/page.tsx | Deal detail | Yes |
| ... | ... | ... | ... |

## Components by Category

### Agent Visibility Layer (PRESERVE - Already Working)
- [ ] Dashboard agent activity widget
- [ ] Header status indicator
- [ ] Activity feed component
- [ ] Onboarding demo modal

### Deal Management
- [ ] Deal list table
- [ ] Deal detail panel
- [ ] Stage transition controls
- [ ] Approval workflow UI

### Pipeline Views
- [ ] Pipeline summary cards
- [ ] Stage distribution chart
- [ ] Recent activity feed

## User Actions (Buttons/Controls)
| Component | Action | Expected Behavior | Backend Call |
|-----------|--------|-------------------|--------------|
| DealList | Click row | Navigate to detail | None (client routing) |
| DealDetail | "Advance Stage" | Trigger transition | POST /deals/{id}/transition |
| ApprovalPanel | "Approve" | Complete HITL approval | POST /approvals/{id}/approve |
| ... | ... | ... | ... |

## Workflows (User Journeys)
### Workflow 1: View Deal Pipeline
1. User navigates to /dashboard
2. Dashboard loads pipeline summary (GET /pipeline/summary)
3. User clicks "View All Deals"
4. Deal list loads (GET /deals?status=active)
5. ...

### Workflow 2: Advance Deal Stage (HITL)
1. User opens deal detail (/deals/{id})
2. User clicks "Advance to Next Stage"
3. UI shows confirmation modal
4. On confirm: POST /deals/{id}/transition
5. Backend returns { status: 'awaiting_approval', approval_id: '...' }
6. UI updates to show "Awaiting Approval" state
7. ...
```

### B) FEATURE → BACKEND MAPPING (Actionable)
**File**: `/home/zaks/bookkeeping/docs/ui-backend-mapping/UI_BACKEND_MAPPING.md`

```markdown
# UI to Backend Mapping

## Mapping Legend
- **READ**: Safe, idempotent data fetch
- **WRITE**: Modifies state, needs optimistic update handling
- **CRITICAL**: Requires HITL approval, must show pending state

## Deal Management

### GET Deal List
| Aspect | Value |
|--------|-------|
| UI Component | `DealListTable` in `app/deals/page.tsx` |
| Trigger | Page load, refresh button, filter change |
| API Route | `GET /api/deals` (Next.js) → `GET ${DEAL_API_BASE}/deals` |
| Auth | Session JWT in Authorization header |
| Request Schema | `{ status?: string, page?: number, limit?: number }` |
| Response Schema | `{ deals: Deal[], total: number, page: number }` |
| Loading State | Skeleton table rows |
| Error State | Toast notification + retry button |
| Action Type | READ |

### POST Deal Stage Transition
| Aspect | Value |
|--------|-------|
| UI Component | `StageTransitionButton` in `app/deals/[id]/page.tsx` |
| Trigger | User clicks "Advance Stage" |
| API Route | `POST /api/deals/[id]/transition` → `POST ${DEAL_API_BASE}/deals/{id}/transition` |
| Auth | Session JWT + CSRF token |
| Request Schema | `{ target_stage: string, reason?: string }` |
| Response Schema | `{ run_id: string, status: 'awaiting_approval', approval_id: string }` |
| Loading State | Button disabled + spinner |
| Success State | Update deal card to show "Awaiting Approval" badge |
| Error State | Modal with error details + "Contact Support" option |
| Action Type | **CRITICAL** (HITL) |
| Observability | Log: `{ event: 'stage_transition_initiated', deal_id, run_id, trace_id }` |
```

**Machine-readable version**:
**File**: `/home/zaks/bookkeeping/docs/ui-backend-mapping/UI_BACKEND_MAPPING.json`
```json
{
  "version": "1.0",
  "generated_at": "ISO_TIMESTAMP",
  "mappings": [
    {
      "id": "deal_list_fetch",
      "ui_component": "DealListTable",
      "ui_file": "app/deals/page.tsx",
      "trigger": "page_load",
      "api_route": {
        "nextjs": "GET /api/deals",
        "backend": "GET http://localhost:8090/deals"
      },
      "auth": "jwt_session",
      "request_schema": { "type": "object", "properties": { "status": { "type": "string" } } },
      "response_schema": { "type": "object", "properties": { "deals": { "type": "array" } } },
      "action_type": "READ",
      "implemented": true,
      "tested": false
    }
  ]
}
```

### C) GAP REPORT
**File**: `/home/zaks/bookkeeping/docs/ui-backend-mapping/GAPS_AND_FIX_PLAN.md`

```markdown
# Gaps and Fix Plan

## Gap Classification
- **P0 (Critical)**: Blocks core workflow, must fix immediately
- **P1 (High)**: Degrades experience significantly
- **P2 (Medium)**: Missing nice-to-have functionality
- **P3 (Low)**: Polish/enhancement

## Identified Gaps

### GAP-001: [Example] Stage Transition Button Non-Functional
| Field | Value |
|-------|-------|
| Priority | P0 |
| Component | `StageTransitionButton` |
| File | `app/deals/[id]/components/StageTransitionButton.tsx` |
| Issue | onClick handler is `console.log('TODO')` |
| Root Cause | Backend endpoint exists but UI wiring missing |
| Fix Approach | 1. Create Next.js route handler at `/api/deals/[id]/transition` |
|              | 2. Wire button to call route with proper payload |
|              | 3. Handle loading/success/error states |
|              | 4. Update deal state on success |
| Acceptance | Button triggers transition, UI shows "Awaiting Approval" |
| Test | Playwright: `test('stage transition shows pending state')` |

### GAP-002: [Example] Missing Error Boundary on Deal Detail
| Field | Value |
|-------|-------|
| Priority | P1 |
| Component | `DealDetailPage` |
| File | `app/deals/[id]/page.tsx` |
| Issue | API errors cause white screen |
| Root Cause | No error boundary, no try/catch on data fetch |
| Fix Approach | 1. Add React Error Boundary |
|              | 2. Add error.tsx for route-level errors |
|              | 3. Show actionable error UI |
| Acceptance | API 500 shows "Something went wrong" + retry button |
| Test | Playwright: `test('deal detail handles API error gracefully')` |
```

### D) IMPLEMENTATION STANDARDS

When implementing fixes, follow these patterns:

#### Next.js Route Handler Template
```typescript
// app/api/deals/[id]/transition/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { logger } from '@/lib/logger'; // Safe logger

const DEAL_API_BASE = process.env.DEAL_API_BASE || 'http://localhost:8090';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const traceId = crypto.randomUUID();
  const startTime = Date.now();

  try {
    // Auth check
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();

    // Safe logging (no content leakage)
    logger.info('deal_transition_initiated', {
      trace_id: traceId,
      deal_id: params.id,
      user_id: session.user.id,
      target_stage: body.target_stage, // OK: not sensitive
    });

    // Backend call
    const response = await fetch(`${DEAL_API_BASE}/deals/${params.id}/transition`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.accessToken}`,
        'X-Trace-ID': traceId,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      logger.warn('deal_transition_failed', {
        trace_id: traceId,
        deal_id: params.id,
        status: response.status,
        // DO NOT log errorData.message if it might contain user content
      });
      return NextResponse.json(
        { error: 'Transition failed', code: errorData.code || 'UNKNOWN' },
        { status: response.status }
      );
    }

    const data = await response.json();

    logger.info('deal_transition_success', {
      trace_id: traceId,
      deal_id: params.id,
      run_id: data.run_id,
      duration_ms: Date.now() - startTime,
    });

    return NextResponse.json(data);

  } catch (error) {
    logger.error('deal_transition_error', {
      trace_id: traceId,
      deal_id: params.id,
      error_type: error instanceof Error ? error.name : 'Unknown',
      // DO NOT log error.message - might contain sensitive data
    });
    return NextResponse.json(
      { error: 'Internal server error', trace_id: traceId },
      { status: 500 }
    );
  }
}
```

#### UI Component Pattern with Loading/Error States
```typescript
// components/StageTransitionButton.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from '@/components/ui/toast';

interface Props {
  dealId: string;
  currentStage: string;
  nextStage: string;
}

export function StageTransitionButton({ dealId, currentStage, nextStage }: Props) {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  async function handleTransition() {
    setIsLoading(true);

    try {
      const response = await fetch(`/api/deals/${dealId}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_stage: nextStage }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.code || 'TRANSITION_FAILED');
      }

      const data = await response.json();

      toast.success('Stage transition initiated', {
        description: `Awaiting approval (ID: ${data.approval_id})`,
      });

      // Refresh to show updated state
      router.refresh();

    } catch (error) {
      toast.error('Transition failed', {
        description: error instanceof Error ? error.message : 'Please try again',
        action: {
          label: 'Retry',
          onClick: handleTransition,
        },
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <button
      onClick={handleTransition}
      disabled={isLoading}
      className="btn-primary"
    >
      {isLoading ? (
        <>
          <Spinner className="mr-2" />
          Processing...
        </>
      ) : (
        `Advance to ${nextStage}`
      )}
    </button>
  );
}
```

### E) END-TO-END VALIDATION

#### Required Playwright Tests
Create: `${UI_REPO}/e2e/ui-smoke.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('ZakOps UI Smoke Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Setup: ensure test user is logged in
    await page.goto('/');
    // Add auth setup as needed
  });

  test('dashboard loads with pipeline summary', async ({ page }) => {
    await page.goto('/dashboard');

    // Verify key elements render
    await expect(page.getByTestId('pipeline-summary')).toBeVisible();
    await expect(page.getByTestId('agent-activity-widget')).toBeVisible();

    // Verify no error states
    await expect(page.getByText('Something went wrong')).not.toBeVisible();
  });

  test('deal list loads and displays deals', async ({ page }) => {
    await page.goto('/deals');

    // Wait for data load
    await expect(page.getByTestId('deal-list-table')).toBeVisible();

    // Verify at least one deal row (or empty state)
    const rows = page.getByTestId('deal-row');
    const emptyState = page.getByTestId('deal-list-empty');

    await expect(rows.first().or(emptyState)).toBeVisible();
  });

  test('deal detail page loads', async ({ page }) => {
    await page.goto('/deals');

    // Click first deal if exists
    const firstDeal = page.getByTestId('deal-row').first();
    if (await firstDeal.isVisible()) {
      await firstDeal.click();

      // Verify detail page elements
      await expect(page.getByTestId('deal-detail-header')).toBeVisible();
      await expect(page.getByTestId('deal-stage-badge')).toBeVisible();
    }
  });

  test('stage transition shows awaiting approval state', async ({ page }) => {
    // Navigate to a deal in transitionable state
    await page.goto('/deals/test-deal-id'); // Use test fixture

    // Click transition button
    const transitionBtn = page.getByTestId('stage-transition-button');
    await transitionBtn.click();

    // Confirm in modal if present
    const confirmBtn = page.getByTestId('confirm-transition');
    if (await confirmBtn.isVisible()) {
      await confirmBtn.click();
    }

    // Verify pending state appears
    await expect(page.getByText(/awaiting approval/i)).toBeVisible({ timeout: 10000 });
  });

  test('agent activity feed updates', async ({ page }) => {
    await page.goto('/dashboard');

    const activityFeed = page.getByTestId('agent-activity-feed');
    await expect(activityFeed).toBeVisible();

    // Verify feed has items or empty state
    const feedItems = activityFeed.getByTestId('activity-item');
    const emptyState = activityFeed.getByTestId('activity-empty');

    await expect(feedItems.first().or(emptyState)).toBeVisible();
  });

  test('handles API errors gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/deals', (route) => {
      route.fulfill({ status: 500, body: JSON.stringify({ error: 'Server error' }) });
    });

    await page.goto('/deals');

    // Verify error UI appears (not white screen)
    await expect(page.getByText(/something went wrong|error|try again/i)).toBeVisible();
  });
});
```

#### Artifact Outputs (Required)
All must be generated:
```
/home/zaks/bookkeeping/docs/ui-backend-mapping/gate_artifacts/
├── ui_smoke_test.log          # Full gate execution log
├── ui_smoke_results.json      # Playwright JSON report
├── contract_probe_results.json # Backend health checks
└── screenshots/               # Failure screenshots (Playwright auto-generates)
```

---

## SUCCESS CRITERIA (NON-NEGOTIABLE)

| Criterion | Verification Method |
|-----------|---------------------|
| Every UI workflow is functional end-to-end | Playwright tests pass |
| No dead buttons or placeholder actions | Manual audit + static analysis |
| No missing backend wiring | UI_BACKEND_MAPPING.json has `implemented: true` for all |
| UI state consistent with backend state | Test refresh after mutations |
| Errors handled with clear UI feedback | Error boundary tests pass |
| Safe logging (no content leakage) | Grep logs for PII patterns = 0 matches |
| Agent Visibility Layer preserved | Existing visibility tests still pass |
| Gates pass | `ui_e2e_gate.sh` exits 0 |

---

## IMPLEMENTATION STRATEGY (EXECUTE IN ORDER)

### Phase 1: Discovery & Contracts (Do First)
1. Locate UI repo, export `UI_REPO`
2. Read all input docs, summarize key decisions
3. Run contract probes to verify backend availability
4. If any probe fails, document in GAPS and proceed with available services

### Phase 2: Inventory (Before Any Code)
1. Enumerate all routes via static analysis
2. Map components to actions
3. Identify Agent Visibility Layer components (mark as PRESERVE)
4. Produce `UI_INVENTORY.md`

### Phase 3: Mapping & Gap Analysis (Before Any Code)
1. For each UI action, document full backend path
2. Identify gaps (missing handlers, dead buttons, missing error states)
3. Produce `UI_BACKEND_MAPPING.md`, `.json`, and `GAPS_AND_FIX_PLAN.md`
4. Prioritize gaps (P0 first)

### Phase 4: Implementation (Smallest First)
```
Order of implementation:
1. READ flows (list, detail views) - lowest risk
2. Error boundaries and loading states - improves debugging
3. WRITE flows (create, update) - medium risk
4. CRITICAL flows (HITL transitions) - highest risk, do last
```

For each gap:
1. Implement fix following patterns above
2. Add/update tests
3. Run lint + typecheck
4. Commit with message: `fix(ui): GAP-XXX - <description>`

### Phase 5: Validation & Gate
1. Run full gate script
2. Review all artifacts
3. Fix any failures
4. Re-run until green

### Phase 6: Handoff
1. Complete `QA_HANDOFF.md`
2. Complete `BUILDER_REPORT.md`
3. Trigger Lab Loop: Builder → Gate → QA

---

## RULES FOR BACKEND CHANGES

Backend changes are **only** permitted if:
1. UI cannot function without them
2. Change is documented in GAPS_AND_FIX_PLAN.md
3. Change has unit/integration test
4. Change has artifact evidence
5. Change does not break existing clients/gates

If backend change affects auth/security:
- Document in BUILDER_REPORT.md
- Add negative tests (unauthorized access attempts fail)
- Verify with contract probe

---

## ERROR HANDLING STANDARD (REQUIRED)

Every UI API call must implement:

| State | UI Behavior | Logging |
|-------|-------------|---------|
| Loading | Disable controls + show spinner | `log.debug('api_call_started', { route, trace_id })` |
| Success | Update UI + toast if appropriate | `log.info('api_call_success', { route, trace_id, duration_ms })` |
| 4xx Error | Show user-friendly message + action | `log.warn('api_call_client_error', { route, status, trace_id })` |
| 5xx Error | Show error + retry option + support link | `log.error('api_call_server_error', { route, status, trace_id })` |
| Network Error | Show offline indicator + retry | `log.error('api_call_network_error', { route, trace_id })` |

**Never** retry CRITICAL actions automatically. User must explicitly confirm retry.

---

## WHAT TO EXCLUDE (DON'T DO)

- Visual redesign / theme changes
- New features not in existing UI
- Agent logic redesign (that's a different mission)
- New third-party integrations
- Database schema changes (unless blocking P0 gap)
- Performance optimization (unless blocking functionality)

---

## QA HANDOFF (Required Output)

**File**: `/home/zaks/bookkeeping/docs/ui-backend-mapping/QA_HANDOFF.md`

```markdown
# QA Handoff - UI Backend Mapping

## How to Run Validation

### Prerequisites
- Node.js 18+
- Docker (for backend services)
- Backend services running (Deal API, RAG API, MCP Server)

### Start Backend Services
```bash
cd /path/to/zakops-backend
docker-compose up -d
```

### Run Gate Script
```bash
cd ${UI_REPO}
./scripts/gates/ui_e2e_gate.sh
```

### Run Individual Tests
```bash
# Lint only
npm run lint

# Typecheck only
npm run typecheck

# Playwright only
npx playwright test

# Specific test
npx playwright test e2e/ui-smoke.spec.ts
```

## Workflows to Validate

### Critical Workflows (Must Pass)
1. [ ] Dashboard loads with pipeline summary
2. [ ] Deal list displays data
3. [ ] Deal detail page loads
4. [ ] Stage transition initiates and shows pending state
5. [ ] Agent activity feed displays events

### Secondary Workflows
1. [ ] Error states display correctly
2. [ ] Loading states appear during API calls
3. [ ] Refresh updates data
4. [ ] Navigation between pages works

## Artifact Locations
- Gate log: `/home/zaks/bookkeeping/docs/ui-backend-mapping/gate_artifacts/ui_smoke_test.log`
- Test results: `/home/zaks/bookkeeping/docs/ui-backend-mapping/gate_artifacts/ui_smoke_results.json`
- Contract probes: `/home/zaks/bookkeeping/docs/ui-backend-mapping/gate_artifacts/contract_probe_results.json`
- Screenshots: `/home/zaks/bookkeeping/docs/ui-backend-mapping/gate_artifacts/screenshots/`

## Known Limitations
- [List any known issues that couldn't be fixed]
- [List any dependencies on external systems]

## Reproduction Steps for Issues
- [Document how to reproduce any known bugs]

## Action Items (Require Human Input)
- [ ] [Any items requiring credentials, secrets, or external approvals]
```

---

## BUILDER REPORT (Required Output)

**File**: `/home/zaks/bookkeeping/docs/ui-backend-mapping/BUILDER_REPORT.md`

```markdown
# Builder Report - UI Backend Mapping

## Summary
- Mission: UI-Backend Mapping and Wiring
- Duration: X hours
- Status: [COMPLETE/PARTIAL/BLOCKED]

## Changed Files
| File | Change Type | Description |
|------|-------------|-------------|
| app/api/deals/[id]/transition/route.ts | Added | Stage transition API route |
| components/StageTransitionButton.tsx | Modified | Wired to API |
| e2e/ui-smoke.spec.ts | Added | Playwright smoke tests |
| ... | ... | ... |

## Key Decisions
1. **Decision**: [What you decided]
   - **Rationale**: [Why]
   - **Alternative considered**: [What else you considered]

## Local Validation
- [x] Lint passed
- [x] Typecheck passed
- [x] Unit tests passed
- [x] Playwright tests passed
- [x] Manual smoke test completed

## Gaps Addressed
| Gap ID | Status | Notes |
|--------|--------|-------|
| GAP-001 | Fixed | Stage transition now functional |
| GAP-002 | Fixed | Error boundary added |
| GAP-003 | Deferred | Requires backend change (documented) |

## Artifacts Generated
- [x] UI_INVENTORY.md
- [x] UI_BACKEND_MAPPING.md
- [x] UI_BACKEND_MAPPING.json
- [x] GAPS_AND_FIX_PLAN.md
- [x] QA_HANDOFF.md
- [x] gate_artifacts/*

## Next Mission Recommendation
Based on roadmap Phase 2, the next task should be:
[Specific recommendation for next mission]
```

---

## BLOCKERS POLICY

If you encounter:
- **Missing credentials/secrets**: Log in QA_HANDOFF.md, skip subtask, continue
- **Backend service down**: Document in GAPS, test with mocks, continue
- **Unclear requirements**: Make reasonable assumption, document decision, continue
- **Breaking change needed**: Document impact, propose alternative, await approval

Never block entirely. Always make progress on what's possible.

---

## FINAL CHECKLIST

Before declaring complete:

```
[ ] UI_REPO path identified and exported
[ ] All input docs read and summarized
[ ] UI_INVENTORY.md complete
[ ] UI_BACKEND_MAPPING.md complete
[ ] UI_BACKEND_MAPPING.json complete
[ ] GAPS_AND_FIX_PLAN.md complete
[ ] All P0 gaps addressed
[ ] All P1 gaps addressed (or documented why deferred)
[ ] Gate script created/updated
[ ] Gate script passes (exit 0)
[ ] All artifacts in gate_artifacts/
[ ] QA_HANDOFF.md complete
[ ] BUILDER_REPORT.md complete
[ ] No dead buttons remain (manual verification)
[ ] No content leakage in logs (grep verification)
[ ] Agent Visibility Layer preserved (tests pass)
```

---

## BEGIN NOW

Execute in order:
1. **Locate** the Next.js repo and print `UI_REPO=<path>`
2. **Read** all input docs, summarize key decisions affecting UI wiring
3. **Run** contract probes to verify backend availability
4. **Create** the output folder structure
5. **Write** UI_INVENTORY.md
6. **Write** mapping docs and gap report
7. **Implement** fixes (smallest/lowest-risk first)
8. **Run** gate and produce artifacts
9. **Complete** QA_HANDOFF.md and BUILDER_REPORT.md
10. **Trigger** Lab Loop cycle

---

*This mission prompt is version-controlled. Do not modify constraints without updating DECISION-LOCK-FILE.md.*

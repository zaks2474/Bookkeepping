# ZakOps UI-Backend Verification & Completion Mission

## MISSION CLASSIFICATION: VERIFICATION & HARDENING

**Trust Level**: ZERO — Assume nothing works until proven with evidence.

You are the Builder LLM. Your mission is to **verify and complete** the UI-Backend integration for the ZakOps dashboard. Previous work has been done, but **you must not trust it**. Every claim of "complete" must be independently verified with live testing and evidence artifacts.

**This is not a "check the boxes" mission. This is a "prove it works" mission.**

---

## CRITICAL MINDSET

```
ASSUMPTION: Previous work is INCOMPLETE until PROVEN otherwise.

• "Mapping exists" ≠ "Integration works"
• "File present" ≠ "Feature functional"
• "No errors" ≠ "Correct behavior"
• "Gate passed" ≠ "Production ready"
```

---

## HARD CONSTRAINTS (NON-NEGOTIABLE)

1. **Evidence-Based Verification Only**
   - Every "PASS" requires a concrete artifact: screenshot, response JSON, timing data, or test output
   - "I checked and it works" is NOT acceptable — show the proof
   - If you cannot produce evidence, the item is marked UNVERIFIED

2. **Live Testing Required**
   - Static code analysis is INSUFFICIENT
   - Every endpoint must be hit with real HTTP requests
   - Response bodies must be validated against expected schemas

3. **Double Verification Protocol**
   - Pass 1: Automated verification (scripts, tests, probes)
   - Pass 2: Manual spot-check verification (different approach)
   - Both passes must agree for PASS status

4. **Strict Gate — No Soft Passes**
   - Gate exit code: 0 = ALL checks pass, non-zero = ANY failure
   - No "warnings", no "acceptable failures", no "known issues"

5. **Regression Awareness**
   - New fixes must not break existing functionality
   - Every fix requires re-running affected workflow tests

---

## SERVICE TOPOLOGY (Verify These Are Running)

| Service | Port | Health Endpoint | Required Status |
|---------|------|-----------------|-----------------|
| Deal Lifecycle API | 8090 | `GET /health` | 200 OK |
| RAG REST API | 8052 | `GET /health` | 200 OK |
| MCP Server | 9100 | `GET /health` | 200 OK or 307 |
| Orchestration API | 9200 | `GET /health` | 200 OK |
| Frontend Dashboard | 3003 | `GET /` | 200 OK |
| Postgres | 5432 | `pg_isready` | Ready |
| Redis | 6379 | `redis-cli ping` | PONG |

**GATE RULE**: If ANY service is down, gate FAILS immediately.

---

## INPUT DOCUMENTS (Read and Cross-Reference)

```
/home/zaks/bookkeeping/docs/ui-backend-mapping/
├── UI_INVENTORY.md           # Claims about routes/components
├── UI_BACKEND_MAPPING.md     # Claims about integrations
├── UI_BACKEND_MAPPING.json   # Machine-readable mappings
├── GAPS_AND_FIX_PLAN.md      # Claims about what was fixed
├── QA_HANDOFF.md             # Claims about validation
└── gate_artifacts/
    └── contract_probe_results.json
```

---

## VERIFICATION PHASES

### Phase 1: Service Health Verification (BLOCKING)
Create `tools/gates/verify_services.sh` to check all services are alive.

### Phase 2: Mapping Completeness Audit
Create `tools/verification/audit_mappings.py` to verify every documented mapping with live requests.

### Phase 3: Workflow End-to-End Verification
Create `e2e/workflow_verification.spec.ts` Playwright tests for:
- W1: Dashboard Load
- W2: Deal List
- W3: Deal Detail
- W4: Stage Transition
- W5: Agent Activity
- W6: Error Recovery

### Phase 4: Gap Closure Verification
Create `tools/verification/verify_gaps_closed.py` to verify claimed fixes.

### Phase 5: Double Verification (Second Pass)
Create `tools/verification/double_check.sh` using curl-based verification.

### Phase 6: Master Gate Script
Create `tools/gates/ui_backend_verification_gate.sh` that runs all phases in sequence.

---

## DELIVERABLES

| Artifact | Purpose |
|----------|---------|
| `gate_artifacts/contract_probe_results.json` | Service health evidence |
| `gate_artifacts/mapping_audit_results.json` | Endpoint verification evidence |
| `gate_artifacts/playwright_results.json` | Workflow test results |
| `gate_artifacts/gap_closure_verification.json` | Fix verification evidence |
| `gate_artifacts/double_check_results.json` | Second pass evidence |
| `gate_artifacts/gate_final_report.json` | Master summary |
| `gate_artifacts/w1_*.png` through `w6_*.png` | Visual evidence |

---

## FIX PRIORITY ORDER

1. Service health issues (blocking)
2. Endpoint 404s/500s (critical)
3. Schema mismatches (high)
4. Workflow failures (high)
5. Gap verification issues (medium)
6. Cross-reference disagreements (investigate)

---

**Do not declare success until the gate passes with zero failures.**

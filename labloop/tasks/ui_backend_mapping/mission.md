# MISSION: ZakOps UI-Backend Mapping
## Wire the Next.js Dashboard to Backend Services

**Version:** 2.0
**Reference:** /home/zaks/bookkeeping/docs/ZAKOPS_UI_BACKEND_MAPPING_MISSION.md

---

## CRITICAL CONTEXT

### What This Mission Produces

| Deliverable | Description | Output Location |
|-------------|-------------|-----------------|
| **UI Inventory** | Complete list of routes, components, actions | UI_INVENTORY.md |
| **Backend Mapping** | Feature → API endpoint mapping | UI_BACKEND_MAPPING.md/json |
| **Gap Report** | Missing wiring, dead buttons, fixes | GAPS_AND_FIX_PLAN.md |
| **Implementation** | Fixed gaps, wired features | UI repo changes |
| **E2E Tests** | Playwright smoke tests | e2e/ui-smoke.spec.ts |
| **QA Handoff** | Validation instructions | QA_HANDOFF.md |

### Hard Rules

1. **Preserve what works** - Do NOT break Agent Visibility Layer, auth, or Docker stack
2. **No dead UI** - Every button must have a functional backend integration
3. **No raw-content leakage** - Safe logging patterns only
4. **Canonical contracts** - Use contract probes, don't guess endpoints
5. **Verifiable** - Every change covered by Gate + QA evidence

---

## REPO DISCOVERY (DO THIS FIRST)

Locate the Next.js dashboard repo:
```bash
find /home/zaks -name "next.config.*" 2>/dev/null | head -20
grep -r '"next"' /home/zaks/*/package.json 2>/dev/null
ls -la /home/zaks/zakops-*/
```

Likely paths:
- `/home/zaks/zakops-frontend`
- `/home/zaks/zakops-dashboard`
- `/home/zaks/zakops-web`
- `/home/zaks/zakops-ui`

Once found, export: `UI_REPO=<path>`

---

## KNOWN SERVICE TOPOLOGY

| Service | Port | Health Endpoint |
|---------|------|-----------------|
| Deal Lifecycle API | 8090 | /health |
| RAG REST API | 8052 | /health |
| MCP Server | 9100 | /health |
| Frontend | 3003 | - |

---

## IMPLEMENTATION STRATEGY

### Phase 1: Discovery & Contracts
1. Locate UI repo
2. Read input docs (roadmap, decision-lock, etc.)
3. Run contract probes
4. Create output directory structure

### Phase 2: Inventory
1. Enumerate all routes
2. Map components to actions
3. Identify Agent Visibility Layer (mark PRESERVE)
4. Write UI_INVENTORY.md

### Phase 3: Mapping & Gap Analysis
1. Document each UI action → backend path
2. Identify gaps
3. Prioritize (P0 > P1 > P2 > P3)
4. Write UI_BACKEND_MAPPING.md/json, GAPS_AND_FIX_PLAN.md

### Phase 4: Implementation
Order: READ flows → Error boundaries → WRITE flows → CRITICAL flows

### Phase 5: Validation
1. Create/update gate script
2. Run gate
3. Fix failures
4. Re-run until green

### Phase 6: Handoff
1. Complete QA_HANDOFF.md
2. Complete BUILDER_REPORT.md

---

## OUTPUT DIRECTORY STRUCTURE

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

## REFERENCE

Full implementation details and patterns in:
`/home/zaks/bookkeeping/docs/ZAKOPS_UI_BACKEND_MAPPING_MISSION.md`

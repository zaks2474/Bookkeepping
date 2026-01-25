# Acceptance Criteria

## Definition of Done

The task is complete when ALL of the following are true:

### Documentation Deliverables
- [ ] `UI_INVENTORY.md` exists in `/home/zaks/bookkeeping/docs/ui-backend-mapping/`
  - [ ] Contains Routes/Pages table
  - [ ] Contains Components by Category section
  - [ ] Contains User Actions table
  - [ ] Contains Workflows section
- [ ] `UI_BACKEND_MAPPING.md` exists with all UI actions mapped to backend endpoints
- [ ] `UI_BACKEND_MAPPING.json` exists and is valid JSON
  - [ ] Contains `version` field
  - [ ] Contains `mappings` array with at least 1 mapping
- [ ] `GAPS_AND_FIX_PLAN.md` exists with prioritized gap list
- [ ] `QA_HANDOFF.md` exists with validation instructions
- [ ] `BUILDER_REPORT.md` exists with implementation summary

### Gap Resolution
- [ ] All P0 (Critical) gaps addressed or documented as blocked
- [ ] All P1 (High) gaps addressed or documented with reason for deferral
- [ ] No dead buttons in UI (buttons without handlers)
- [ ] All API calls have loading and error states

### Quality Gates
- [ ] Gate script exists and is executable
- [ ] Gate script passes (exit code 0)
- [ ] Contract probes validate backend availability
- [ ] No raw content leakage in logging (safe logging patterns used)

### Preservation Requirements
- [ ] Agent Visibility Layer components still work
- [ ] Existing auth/session flow intact
- [ ] Docker stack unchanged (unless required for wiring)

## Verification Steps

1. Check all required files exist:
   ```bash
   ls -la /home/zaks/bookkeeping/docs/ui-backend-mapping/
   ```

2. Validate JSON files:
   ```bash
   python3 -c "import json; json.load(open('/home/zaks/bookkeeping/docs/ui-backend-mapping/UI_BACKEND_MAPPING.json'))"
   ```

3. Run gate script:
   ```bash
   bash /home/zaks/bookkeeping/labloop/tasks/ui_backend_mapping/gate.sh
   ```

4. Verify artifact outputs in `gate_artifacts/`

## Gate Command

```bash
bash /home/zaks/bookkeeping/labloop/tasks/ui_backend_mapping/gate.sh
```

This command must exit with code 0 for the task to pass.

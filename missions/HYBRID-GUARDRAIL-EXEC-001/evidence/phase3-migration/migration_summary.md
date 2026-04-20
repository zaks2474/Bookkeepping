# Phase 3 Migration Summary

## What was migrated

### types/api.ts (429 → 371 lines)
- **Before:** 100% hand-written TypeScript interfaces
- **After:** Hybrid — imports from generated types where possible, manual refinements where needed

### Types now derived from generated file:
- DealCreate → components['schemas']['DealCreate']
- DealUpdate → components['schemas']['DealUpdate']
- DealEvent → components['schemas']['DealEvent']
- QuarantineItem → components['schemas']['QuarantineResponse']
- QuarantineProcess → components['schemas']['QuarantineProcess']
- EventResponse → components['schemas']['EventResponse']
- AgentRun → components['schemas']['AgentRunResponse']
- StageTransitionRequest → components['schemas']['TransitionRequest']
- StageTransitionResponse → components['schemas']['TransitionResponse']
- Deal → extends GeneratedDeal with manual nested type overrides
- Action → extends GeneratedAction with manual refinements

### Types kept as manual refinements:
- String literal unions: DealStage, DealStatus, Priority, ActionStatus, RiskLevel, etc.
  (Generated types have these as plain 'string')
- Nested object interfaces: DealIdentifiers, CompanyInfo, BrokerInfo, DealMetadata
  (Generated types have these as {[key: string]: unknown})
- Types without generated equivalent: DealAlias, SenderProfile, PipelineStats, etc.
- Request/response types: ListParams, DealListParams, HealthResponse, etc.

### Dead code removed:
- api-schemas.ts (500 lines) — had ZERO imports. Moved to evidence directory.

### Compilation issues found and fixed:
- ActionReject: generated type has rejected_by as required, but components don't pass it
  (backend provides default). Fixed by keeping manual interface with optional rejected_by.

## Verification
- tsc --noEmit: PASS (exit 0)
- make sync-types: PASS (exit 0)
- curl /api/deals: PASS
- Dashboard accessible: PASS

## Note on api.ts Zod schemas
api.ts (the API client) has its OWN Zod schemas (13 safeParse usages) separate from
api-schemas.ts. These are the "thin manual Zod wrappers" mentioned in the strategy —
they handle runtime validation with custom coercion (coerceToNumber, coerceBrokerToString).
These are kept as-is and are the legitimate manual Zod wrappers.

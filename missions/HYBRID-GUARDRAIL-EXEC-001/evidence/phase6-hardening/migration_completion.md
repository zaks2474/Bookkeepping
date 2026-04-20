# Migration Completion Report

## Legacy Status
- api-schemas.ts: DELETED (was 500 lines, zero imports — dead code)
- Remaining legacy imports: 0
- Legacy api-schemas file: no longer exists

## Generated Types
- api-types.generated.ts: 5,502 lines (openapi-typescript v7.10.1)
- Generated from: 83 OpenAPI paths, 56 schemas

## Migrated Entities (types/api.ts → generated)
1. DealCreate → components['schemas']['DealCreate']
2. DealUpdate → components['schemas']['DealUpdate']
3. DealEvent → components['schemas']['DealEvent']
4. QuarantineItem → components['schemas']['QuarantineResponse']
5. QuarantineProcess → components['schemas']['QuarantineProcess']
6. EventResponse → components['schemas']['EventResponse']
7. AgentRun → components['schemas']['AgentRunResponse']
8. StageTransitionRequest → components['schemas']['TransitionRequest']
9. StageTransitionResponse → components['schemas']['TransitionResponse']
10. Deal → extends GeneratedDeal (hybrid: generated base + manual nested overrides)
11. Action → extends GeneratedAction (hybrid: generated base + manual refinements)

## Manual Refinements Kept (with rationale)
- String literal unions (DealStage, ActionStatus, etc.) — generated types have plain 'string'
- Nested object interfaces (DealIdentifiers, CompanyInfo, BrokerInfo, DealMetadata) — generated has {[key: string]: unknown}
- ActionApprove/ActionReject — generated has required fields client doesn't pass
- Types without generated equivalent (DealAlias, SenderProfile, PipelineStats, etc.)
- Runtime Zod wrappers in api.ts (13 safeParse usages) — coercion at API boundary

## Manual Zod Wrapper Count
- Post-migration z.object count: 46 (set as CI ceiling in type-sync.yml)
- All are runtime validation wrappers, not type definitions

## POST Endpoints Without response_model
- 0 POST endpoints (all 13 without response schema are GET admin/diagnostic endpoints)
- DEFERRED — adding response_model is a backend change

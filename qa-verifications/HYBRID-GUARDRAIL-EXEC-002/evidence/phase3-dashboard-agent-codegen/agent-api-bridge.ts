/**
 * ZakOps Agent API Types (Bridge File)
 *
 * HYBRID GUARDRAIL EXEC-002: Types derived from Agent API OpenAPI spec.
 * Source of truth: components['schemas'] from agent-api-types.generated.ts
 *
 * This bridge file provides:
 * 1. Type aliases for cleaner imports
 * 2. Single import point (enforced by ESLint)
 */

import type { components } from '../lib/agent-api-types.generated';

// =============================================================================
// GENERATED TYPE ALIASES
// These come directly from the Agent API OpenAPI-generated types.
// =============================================================================

// Activity types
/** Generated: components['schemas']['ActivityEvent'] */
export type ActivityEvent = components['schemas']['ActivityEvent'];

/** Generated: components['schemas']['ActivityResponse'] */
export type ActivityResponse = components['schemas']['ActivityResponse'];

/** Generated: components['schemas']['ActivityStats'] */
export type ActivityStats = components['schemas']['ActivityStats'];

// Agent invocation types
/** Generated: components['schemas']['AgentInvokeRequest'] */
export type AgentInvokeRequest = components['schemas']['AgentInvokeRequest'];

/** Generated: components['schemas']['AgentInvokeResponse'] */
export type AgentInvokeResponse = components['schemas']['AgentInvokeResponse'];

/** Generated: components['schemas']['ActionTaken'] */
export type ActionTaken = components['schemas']['ActionTaken'];

// Approval types
/** Generated: components['schemas']['ApprovalActionRequest'] */
export type ApprovalActionRequest = components['schemas']['ApprovalActionRequest'];

/** Generated: components['schemas']['ApprovalListResponse'] */
export type ApprovalListResponse = components['schemas']['ApprovalListResponse'];

/** Generated: components['schemas']['PendingApproval'] */
export type PendingApproval = components['schemas']['PendingApproval'];

// Thread types
/** Generated: components['schemas']['ThreadStateResponse'] */
export type ThreadStateResponse = components['schemas']['ThreadStateResponse'];

// Chat types
/** Generated: components['schemas']['ChatRequest'] */
export type ChatRequest = components['schemas']['ChatRequest'];

/** Generated: components['schemas']['ChatResponse'] */
export type ChatResponse = components['schemas']['ChatResponse'];

/** Generated: components['schemas']['Message'] */
export type Message = components['schemas']['Message'];

// Auth types
/** Generated: components['schemas']['SessionResponse'] */
export type SessionResponse = components['schemas']['SessionResponse'];

/** Generated: components['schemas']['Token'] */
export type Token = components['schemas']['Token'];

/** Generated: components['schemas']['TokenResponse'] */
export type TokenResponse = components['schemas']['TokenResponse'];

/** Generated: components['schemas']['UserCreate'] */
export type UserCreate = components['schemas']['UserCreate'];

/** Generated: components['schemas']['UserResponse'] */
export type UserResponse = components['schemas']['UserResponse'];

// Error types
/** Generated: components['schemas']['HTTPValidationError'] */
export type HTTPValidationError = components['schemas']['HTTPValidationError'];

/** Generated: components['schemas']['ValidationError'] */
export type ValidationError = components['schemas']['ValidationError'];

// =============================================================================
// RE-EXPORT BASE TYPES
// For advanced usage (typed fetch clients, etc.)
// =============================================================================

export type { paths, components, operations } from '../lib/agent-api-types.generated';

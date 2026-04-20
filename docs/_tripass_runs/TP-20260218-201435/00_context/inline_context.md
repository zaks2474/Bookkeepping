
---
## PRE-LOADED FILE: /home/zaks/zakops-agent-api/apps/backend/db/init/001_base_tables.sql
```
-- Base Tables for ZakOps
-- Creates the core tables that other migrations depend on
-- Must run BEFORE other migrations

-- Ensure schema exists
CREATE SCHEMA IF NOT EXISTS zakops;

-- ============================================================================
-- DEAL ID SEQUENCE
-- ============================================================================

CREATE SEQUENCE IF NOT EXISTS zakops.deal_id_seq START 1;

-- Function to generate deal IDs like DL-0001
CREATE OR REPLACE FUNCTION zakops.next_deal_id()
RETURNS VARCHAR(20) AS $$
DECLARE
    next_val INTEGER;
BEGIN
    next_val := nextval('zakops.deal_id_seq');
    RETURN 'DL-' || LPAD(next_val::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DEALS TABLE (Core entity)
-- ============================================================================

CREATE TABLE IF NOT EXISTS zakops.deals (
    deal_id VARCHAR(20) PRIMARY KEY,
    canonical_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    folder_path VARCHAR(1024),

    -- Deal stage and status
    stage VARCHAR(50) DEFAULT 'inbound',
    status VARCHAR(50) DEFAULT 'active',

    -- Structured data
    identifiers JSONB DEFAULT '{}',
    company_info JSONB DEFAULT '{}',
    broker JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',

    -- Soft delete
    deleted BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deals_canonical_name ON zakops.deals(canonical_name);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON zakops.deals(stage);
CREATE INDEX IF NOT EXISTS idx_deals_status ON zakops.deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON zakops.deals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_deals_updated_at ON zakops.deals(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_deals_cursor_pagination ON zakops.deals (updated_at DESC, deal_id DESC);

-- ============================================================================
-- ACTIONS TABLE (Tasks/workflows associated with deals)
-- ============================================================================

CREATE TABLE IF NOT EXISTS zakops.actions (
    action_id VARCHAR(50) PRIMARY KEY,
    deal_id VARCHAR(20) REFERENCES zakops.deals(deal_id) ON DELETE SET NULL,
    correlation_id UUID,

    -- Action details
    action_type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    description TEXT,

    -- State
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,

    -- Agent info
    agent_type VARCHAR(100),
    agent_config JSONB DEFAULT '{}',

    -- Results
    result JSONB DEFAULT '{}',
    error_message TEXT,

    -- HITL
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID,
    approved_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_actions_deal_id ON zakops.actions(deal_id);
CREATE INDEX IF NOT EXISTS idx_actions_status ON zakops.actions(status);
CREATE INDEX IF NOT EXISTS idx_actions_action_type ON zakops.actions(action_type);
CREATE INDEX IF NOT EXISTS idx_actions_correlation_id ON zakops.actions(correlation_id);

-- ============================================================================
-- DEAL EVENTS TABLE (Event history)
-- ============================================================================

CREATE TABLE IF NOT EXISTS zakops.deal_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id VARCHAR(20) REFERENCES zakops.deals(deal_id) ON DELETE CASCADE,

    event_type VARCHAR(100) NOT NULL,
    event_source VARCHAR(100),
    actor VARCHAR(255),

    payload JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deal_events_deal_id ON zakops.deal_events(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_events_event_type ON zakops.deal_events(event_type);
CREATE INDEX IF NOT EXISTS idx_deal_events_created_at ON zakops.deal_events(created_at DESC);

-- Function to record deal events
CREATE OR REPLACE FUNCTION zakops.record_deal_event(
    p_deal_id VARCHAR(20),
    p_event_type VARCHAR(100),
    p_event_source VARCHAR(100),
    p_actor VARCHAR(255),
    p_payload JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    event_id UUID;
BEGIN
    INSERT INTO zakops.deal_events (deal_id, event_type, event_source, actor, payload)
    VALUES (p_deal_id, p_event_type, p_event_source, p_actor, p_payload)
    RETURNING id INTO event_id;

    RETURN event_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- UPDATE TIMESTAMP TRIGGER
-- ============================================================================

CREATE OR REPLACE FUNCTION zakops.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to deals
DROP TRIGGER IF EXISTS deals_updated_at ON zakops.deals;
CREATE TRIGGER deals_updated_at
    BEFORE UPDATE ON zakops.deals
    FOR EACH ROW
    EXECUTE FUNCTION zakops.update_timestamp();

-- Apply trigger to actions
DROP TRIGGER IF EXISTS actions_updated_at ON zakops.actions;
CREATE TRIGGER actions_updated_at
    BEFORE UPDATE ON zakops.actions
    FOR EACH ROW
    EXECUTE FUNCTION zakops.update_timestamp();

-- ============================================================================
-- DEAL ALIASES TABLE (Alternative identifiers for deals)
-- ============================================================================

CREATE TABLE IF NOT EXISTS zakops.deal_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id VARCHAR(20) REFERENCES zakops.deals(deal_id) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL,
    alias_type VARCHAR(50) DEFAULT 'general',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deal_aliases_deal_id ON zakops.deal_aliases(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_aliases_alias ON zakops.deal_aliases(alias);

-- ============================================================================
-- SENDER PROFILES TABLE (Email sender tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS zakops.sender_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    domain VARCHAR(255),
    reputation VARCHAR(50) DEFAULT 'unknown',
    classification VARCHAR(50),
    total_emails INTEGER DEFAULT 0,
    last_seen_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sender_profiles_email ON zakops.sender_profiles(email);
CREATE INDEX IF NOT EXISTS idx_sender_profiles_domain ON zakops.sender_profiles(domain);

-- ============================================================================
-- QUARANTINE ITEMS TABLE (Email quarantine)
-- ============================================================================

CREATE TABLE IF NOT EXISTS zakops.quarantine_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id VARCHAR(20) REFERENCES zakops.deals(deal_id) ON DELETE SET NULL,

    -- Email info
    sender VARCHAR(255),
    subject VARCHAR(500),
    message_id VARCHAR(500),

    -- Content
    body_preview TEXT,
    raw_content JSONB DEFAULT '{}',

    -- Classification
    reason VARCHAR(100),
    confidence FLOAT,

    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    reviewed_by UUID,
    reviewed_at TIMESTAMPTZ,

    -- Timestamps
    received_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quarantine_items_status ON zakops.quarantine_items(status);
CREATE INDEX IF NOT EXISTS idx_quarantine_items_sender ON zakops.quarantine_items(sender);
CREATE INDEX IF NOT EXISTS idx_quarantine_items_deal_id ON zakops.quarantine_items(deal_id);

-- ============================================================================
-- AGENT TOOL CALLS TABLE (Agent execution tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS zakops.agent_tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id VARCHAR(50) REFERENCES zakops.actions(action_id) ON DELETE CASCADE,
    run_id UUID,

    -- Tool info
    tool_name VARCHAR(100) NOT NULL,
    tool_input JSONB DEFAULT '{}',
    tool_output JSONB DEFAULT '{}',

    -- Execution
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,

    -- HITL
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID,
    approved_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agent_tool_calls_action_id ON zakops.agent_tool_calls(action_id);
CREATE INDEX IF NOT EXISTS idx_agent_tool_calls_status ON zakops.agent_tool_calls(status);
CREATE INDEX IF NOT EXISTS idx_agent_tool_calls_run_id ON zakops.agent_tool_calls(run_id);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Pipeline Summary View (matches migration 023_stage_check_constraint.sql)
CREATE OR REPLACE VIEW zakops.v_pipeline_summary AS
SELECT stage,
       count(*) AS count,
       round(avg(EXTRACT(DAY FROM NOW() - updated_at))::numeric, 1) AS avg_days_in_stage
FROM zakops.deals
WHERE deleted = false AND status = 'active'
GROUP BY stage
ORDER BY (CASE stage
    WHEN 'inbound' THEN 1 WHEN 'screening' THEN 2 WHEN 'qualified' THEN 3
    WHEN 'loi' THEN 4 WHEN 'diligence' THEN 5 WHEN 'closing' THEN 6
    WHEN 'portfolio' THEN 7 WHEN 'junk' THEN 8 WHEN 'archived' THEN 9
    ELSE 99 END);

-- Pending Tool Approvals View
CREATE OR REPLACE VIEW zakops.v_pending_tool_approvals AS
SELECT
    tc.id,
    tc.action_id,
    tc.tool_name,
    tc.tool_input,
    tc.created_at,
    a.deal_id,
    a.action_type,
    d.canonical_name AS deal_name
FROM zakops.agent_tool_calls tc
JOIN zakops.actions a ON tc.action_id = a.action_id
LEFT JOIN zakops.deals d ON a.deal_id = d.deal_id
WHERE tc.requires_approval = TRUE
  AND tc.status = 'pending'
ORDER BY tc.created_at;
```
---

---
## PRE-LOADED FILE: /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts
```
/**
 * ZakOps API Client
 *
 * Centralized API client with Zod validation and response normalization.
 * All API calls MUST go through this module - no direct fetch in components.
 *
 * The frontend uses Next.js rewrites to proxy /api/* to the backend,
 * so we always call relative paths.
 */

import { z } from 'zod';
import { normalizeError } from './error-normalizer';

/**
 * Check if a response payload is an error shape rather than valid data.
 * Catches backend error payloads that pass HTTP 200 (partial availability).
 */
function isErrorPayload(data: unknown): boolean {
  if (!data || typeof data !== 'object' || Array.isArray(data)) return false;
  const d = data as Record<string, unknown>;
  return ('error' in d || 'detail' in d);
}

// ============================================================================
// Zod Schemas - Define expected response shapes
// ============================================================================

/**
 * Coerce a value to number, handling strings with currency symbols, commas, etc.
 * Returns null/undefined if the value cannot be parsed.
 * Logs warnings (not errors) for type coercions to aid debugging without alarming.
 */
function coerceToNumber(val: unknown): number | null | undefined {
  if (val === null) return null;
  if (val === undefined) return undefined;
  if (typeof val === 'number') return isNaN(val) ? null : val;
  if (typeof val === 'string') {
    // Remove currency symbols, commas, whitespace
    const cleaned = val.replace(/[$,\s]/g, '').trim();
    if (cleaned === '' || cleaned === '-' || cleaned.toLowerCase() === 'tbd') {
      // Expected non-numeric values - don't log
      return null;
    }
    const num = parseFloat(cleaned);
    if (isNaN(num)) {
      // Unexpected string that couldn't be parsed - log as debug info
      if (process.env.NODE_ENV === 'development') {
        console.debug(`[API] Coerced non-numeric string to null: "${val}"`);
      }
      return null;
    }
    return num;
  }
  return null;
}

// Schema for numeric fields that might arrive as strings
const coercedNumber = z.preprocess(coerceToNumber, z.number().nullable().optional());

/**
 * Coerce broker field to string. Backend may return:
 * - string: broker name directly
 * - object: { name?: string, email?: string, ... }
 * - null/undefined
 * We extract the name for display purposes.
 */
function coerceBrokerToString(val: unknown): string | null {
  if (val === null || val === undefined) return null;
  if (typeof val === 'string') return val || null;
  if (typeof val === 'object' && val !== null) {
    const obj = val as Record<string, unknown>;
    // Extract name from broker object
    if (typeof obj.name === 'string' && obj.name) {
      return obj.name;
    }
    // Empty object {} returns null
    return null;
  }
  return null;
}

// Deal schema
export const DealSchema = z.object({
  deal_id: z.string(),
  canonical_name: z.string().nullable(),
  display_name: z.string().optional().nullable(),
  stage: z.string(),
  status: z.string(),
  broker: z.preprocess(coerceBrokerToString, z.string().nullable().optional()),
  priority: z.string().nullable().optional(),
  updated_at: z.string().nullable().optional(),
  created_at: z.string().nullable().optional(),
  days_since_update: z.preprocess(coerceToNumber, z.number().optional()),
  folder_path: z.string().optional().nullable(),
  identifiers: z.record(z.unknown()).optional().nullable(),
});

export type Deal = z.infer<typeof DealSchema>;

// Deal detail schema (expanded)
export const DealDetailSchema = z.object({
  deal_id: z.string(),
  canonical_name: z.string().nullable(),
  display_name: z.string().nullable().optional(),
  folder_path: z.string().nullable().optional(),
  stage: z.string(),
  status: z.string(),
  broker: z.object({
    name: z.string().nullable(),
    email: z.string().nullable(),
    company: z.string().nullable(),
    phone: z.string().nullable(),
  }).passthrough().nullable().optional(),
  company_info: z.object({
    sector: z.string().nullable().optional(),
    location: z.any().nullable().optional(),
  }).passthrough().nullable().optional(),
  metadata: z.object({
    priority: z.string().nullable().optional(),
    asking_price: coercedNumber,
    ebitda: coercedNumber,
    revenue: coercedNumber,
    multiple: coercedNumber,
    nda_status: z.string().nullable().optional(),
    cim_received: z.boolean().nullable().optional(),
  }).passthrough().nullable().optional(),
  state_machine: z.object({
    current_stage: z.string(),
    is_terminal: z.boolean(),
    allowed_transitions: z.array(z.string()),
    advisory_context: z.string().nullable().optional(),
  }).nullable().optional(),
  identifiers: z.record(z.unknown()).optional().nullable(),
  case_file: z.any().nullable().optional(),
  event_count: z.number().optional(),
  pending_actions: z.number().optional(),
  created_at: z.string().nullable().optional(),
  updated_at: z.string().nullable().optional(),
});

export type DealDetail = z.infer<typeof DealDetailSchema>;

// Deferred action schema
// FIX: Changed to .nullable().optional() to handle backend null values
export const ActionSchema = z.object({
  action_id: z.string(),
  deal_id: z.string().nullable().optional(),
  action_type: z.string(),
  scheduled_for: z.string().nullable().optional(),
  status: z.string(),
  priority: z.string().nullable().optional(),
  is_due: z.boolean().nullable().optional(),
  data: z.any().nullable().optional(),
});

export type Action = z.infer<typeof ActionSchema>;

// Event schema — matches backend deal_events response
// FIX: Changed to .nullable().optional() to handle backend null values
export const EventSchema = z.object({
  id: z.string(),
  deal_id: z.string().nullable().optional(),
  event_type: z.string(),
  source: z.string().nullable().optional(),
  actor: z.string().nullable().optional(),
  details: z.record(z.any()).nullable().optional(),
  created_at: z.string(),
});

export type DealEvent = z.infer<typeof EventSchema>;

// Structured extraction_evidence schema — contract between agent and dashboard
// QI-001 P1: Defines the JSONB shape for triage intelligence
const ExtractionEvidenceFinancialsSchema = z.object({
  asking_price: z.union([z.string(), z.number()]).nullable().optional(),
  revenue: z.union([z.string(), z.number()]).nullable().optional(),
  ebitda: z.union([z.string(), z.number()]).nullable().optional(),
  sde: z.union([z.string(), z.number()]).nullable().optional(),
  multiple: z.number().nullable().optional(),
  revenue_range: z.string().nullable().optional(),
  valuation_notes: z.string().nullable().optional(),
}).passthrough();

const ExtractionEvidenceBrokerSchema = z.object({
  name: z.string().nullable().optional(),
  email: z.string().nullable().optional(),
  title: z.string().nullable().optional(),
  firm: z.string().nullable().optional(),
  firm_type: z.string().nullable().optional(),
  phone: z.string().nullable().optional(),
}).passthrough();

const ExtractionEvidenceEntitySchema = z.object({
  name: z.string(),
  role: z.string().nullable().optional(),
  organization: z.string().nullable().optional(),
  evidence_snippet: z.string().nullable().optional(),
  confidence: z.number().nullable().optional(),
}).passthrough();

const ExtractionEvidenceTypedLinkSchema = z.object({
  url: z.string(),
  link_type: z.string(),
  vendor: z.string().nullable().optional(),
  auth_required: z.boolean().nullable().optional(),
  label: z.string().nullable().optional(),
}).passthrough();

export const ExtractionEvidenceSchema = z.object({
  reasons: z.array(z.string()).nullable().optional(),
  urgency_signals: z.array(z.string()).nullable().optional(),
  urgency_rationale: z.string().nullable().optional(),
  financials: ExtractionEvidenceFinancialsSchema.nullable().optional(),
  broker: ExtractionEvidenceBrokerSchema.nullable().optional(),
  entities: z.object({
    companies: z.array(ExtractionEvidenceEntitySchema).nullable().optional(),
    people: z.array(ExtractionEvidenceEntitySchema).nullable().optional(),
  }).passthrough().nullable().optional(),
  typed_links: z.array(ExtractionEvidenceTypedLinkSchema).nullable().optional(),
  deal_stage_hint: z.string().nullable().optional(),
  timeline_signals: z.array(z.string()).nullable().optional(),
  deal_match_confidence: z.number().nullable().optional(),
  match_factors: z.array(z.string()).nullable().optional(),
}).passthrough();

export type ExtractionEvidence = z.infer<typeof ExtractionEvidenceSchema>;

// Quarantine item schema
// FIX: Changed all .optional() to .nullable().optional() to handle backend null values
// P2: Extended with confidence, version, display_subject, sender_name for operational UX
// QI-001 P1: Added extraction_evidence typed schema, provenance, routing conflict fields
export const QuarantineItemSchema = z.object({
  id: z.string().nullable().optional(),
  quarantine_id: z.string().nullable().optional(),
  action_id: z.string().nullable().optional(),
  email_subject: z.string().nullable().optional(),
  subject: z.string().nullable().optional(),
  display_subject: z.string().nullable().optional(),
  sender: z.string().nullable().optional(),
  sender_name: z.string().nullable().optional(),
  sender_domain: z.string().nullable().optional(),
  sender_company: z.string().nullable().optional(),
  from: z.string().nullable().optional(),
  received_at: z.string().nullable().optional(),
  timestamp: z.string().nullable().optional(),
  quarantine_reason: z.string().nullable().optional(),
  reason: z.string().nullable().optional(),
  status: z.string().nullable().optional(),
  classification: z.string().nullable().optional(),
  urgency: z.string().nullable().optional(),
  confidence: z.number().nullable().optional(),
  version: z.number().nullable().optional(),
  company: z.string().nullable().optional(),
  company_name: z.string().nullable().optional(),
  broker_name: z.string().nullable().optional(),
  is_broker: z.boolean().nullable().optional(),
  email_body_snippet: z.string().nullable().optional(),
  triage_summary: z.string().nullable().optional(),
  source_thread_id: z.string().nullable().optional(),
  schema_version: z.string().nullable().optional(),
  links: z.array(z.record(z.any())).nullable().optional(),
  attachments: z.any().nullable().optional(),
  quarantine_dir: z.string().nullable().optional(),
  capability_id: z.string().nullable().optional(),
  source_type: z.string().nullable().optional(),
  correlation_id: z.string().nullable().optional(),
  extraction_evidence: ExtractionEvidenceSchema.nullable().optional(),
  field_confidences: z.record(z.number()).nullable().optional(),
  routing_reason: z.string().nullable().optional(),
  // QI-001 P1: Routing conflict fields (F-1) — needed for "Approve into deal" flow
  routing_conflict: z.boolean().nullable().optional(),
  conflicting_deal_ids: z.array(z.string()).nullable().optional(),
  // QI-001 P1: LangSmith provenance fields (F-5) — agent trace + version metadata
  langsmith_run_id: z.string().nullable().optional(),
  langsmith_trace_url: z.string().nullable().optional(),
  tool_version: z.string().nullable().optional(),
  prompt_version: z.string().nullable().optional(),
}).passthrough();

export type QuarantineItem = z.infer<typeof QuarantineItemSchema>;

// Quarantine health schema
export const QuarantineHealthSchema = z.object({
  status: z.string(),
  pending_items: z.number(),
  oldest_pending_days: z.number().optional(),
});

export type QuarantineHealth = z.infer<typeof QuarantineHealthSchema>;

// Quarantine preview schema (right-side panel)
// FIX: Changed all .optional() to .nullable().optional() to handle backend null values
export const QuarantinePreviewSchema = z.object({
  action_id: z.string().nullable().optional(),
  status: z.string().nullable().optional(),
  created_at: z.string().nullable().optional(),
  deal_id: z.string().nullable().optional(),
  message_id: z.string().nullable().optional(),
  thread_id: z.string().nullable().optional(),
  from: z.string().nullable().optional(),
  to: z.string().nullable().optional(),
  received_at: z.string().nullable().optional(),
  subject: z.string().nullable().optional(),
  summary: z.array(z.string()).nullable().optional().default([]),
  extracted_fields: z.record(z.any()).nullable().optional(),
  attachments: z.record(z.any()).nullable().optional(),
  links: z.record(z.any()).nullable().optional(),
  email: z.record(z.any()).nullable().optional(),
  quarantine_dir: z.string().nullable().optional(),
  thread_resolution: z
    .object({
      thread_to_deal: z.string().nullable().optional(),
      thread_to_non_deal: z.string().nullable().optional(),
    })
    .nullable().optional(),
  // P5: Routing metadata
  routing_reason: z.string().nullable().optional(),
  routing_conflict: z.boolean().nullable().optional(),
  conflicting_deal_ids: z.array(z.string()).nullable().optional(),
  source_thread_id: z.string().nullable().optional(),
});

export type QuarantinePreview = z.infer<typeof QuarantinePreviewSchema>;

// Deal materials (filesystem-backed correspondence bundles)
// FIX: deal_path can be null for deals without folder_path
export const DealMaterialsSchema = z.object({
  deal_id: z.string(),
  deal_path: z.string().nullable().optional(),
  correspondence: z.array(z.record(z.any())).nullable().optional().default([]),
  aggregate_links: z.record(z.any()).nullable().optional(),
  pending_auth: z.array(z.record(z.any())).nullable().optional().default([]),
});

export type DealMaterials = z.infer<typeof DealMaterialsSchema>;

// Alert schema
// FIX: Changed to .nullable().optional() to handle backend null values
export const AlertSchema = z.object({
  type: z.string(),
  severity: z.string(),
  message: z.string(),
  deal_id: z.string().nullable().optional(),
  count: z.number().nullable().optional(),
  actions: z.array(z.string()).nullable().optional(),
});

export type Alert = z.infer<typeof AlertSchema>;

// Classification metrics schema
export const ClassificationMetricsSchema = z.object({
  decisions_24h: z.number().nullable().optional(),
  local_24h: z.number().nullable().optional(),
  cloud_24h: z.number().nullable().optional(),
  heuristic_24h: z.number().nullable().optional(),
  quarantine_rate: z.number().optional(),
});

export type ClassificationMetrics = z.infer<typeof ClassificationMetricsSchema>;

// Checkpoint schema
export const CheckpointSchema = z.object({
  id: z.string(),
  operation_type: z.string(),
  status: z.string(),
  progress: z.number().optional(),
});

export type Checkpoint = z.infer<typeof CheckpointSchema>;

// Pipeline stage schema
export const PipelineStageSchema = z.object({
  count: z.number(),
  deals: z.array(z.object({
    deal_id: z.string(),
    canonical_name: z.string().nullable(),
    days_in_stage: z.number(),
  })),
  avg_age: z.number(),
});

export type PipelineStage = z.infer<typeof PipelineStageSchema>;

// ============================================================================
// API Response Wrappers - Handle both wrapped and unwrapped responses
// ============================================================================

// Generic wrapper for paginated/counted responses
const DealsResponseSchema = z.object({
  count: z.number().optional(),
  total_count: z.number().optional(),
  deals: z.array(DealSchema),
}).or(z.array(DealSchema));

const ActionsResponseSchema = z.object({
  count: z.number().optional(),
  actions: z.array(ActionSchema),
}).or(z.array(ActionSchema));

const EventsResponseSchema = z.object({
  deal_id: z.string().optional(),
  count: z.number().optional(),
  events: z.array(EventSchema),
}).or(z.array(EventSchema));

const QuarantineResponseSchema = z.object({
  count: z.number().optional(),
  items: z.array(QuarantineItemSchema),
}).or(z.array(QuarantineItemSchema));

const AlertsResponseSchema = z.object({
  alert_count: z.number().optional(),
  alerts: z.array(AlertSchema),
}).or(z.array(AlertSchema));

const CheckpointsResponseSchema = z.array(CheckpointSchema);

const PipelineResponseSchema = z.object({
  total_active: z.number(),
  stages: z.record(PipelineStageSchema),
});

// ============================================================================
// API Error Handling
// ============================================================================

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public endpoint: string
  ) {
    super(message);
    this.name = 'ApiError';
  }

  /** User-friendly error message */
  get userMessage(): string {
    if (this.status === 0) {
      return `Network error connecting to API. Check if the backend is running.`;
    }
    if (this.status === 404) {
      return `Resource not found: ${this.endpoint}`;
    }
    if (this.status >= 500) {
      return `Server error (${this.status}). The API is having problems.`;
    }
    if (this.status === 401 || this.status === 403) {
      return `Access denied (${this.status}). You may not have permission.`;
    }
    return `API error ${this.status}: ${this.message}`;
  }
}

// ============================================================================
// Core Fetch Function
// ============================================================================

async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  // REC-029: Correlation ID for cross-service tracing
  // R2-2.3: Add Idempotency-Key header for write operations
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Correlation-ID': crypto.randomUUID(),
    ...options.headers,
  };

  // Auto-generate idempotency key for write methods
  const method = options.method?.toUpperCase() || 'GET';
  const isWrite = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    // Only add if not already provided
    const existingHeaders = options.headers as Record<string, string> | undefined;
    if (!existingHeaders?.['Idempotency-Key'] && !existingHeaders?.['idempotency-key']) {
      (headers as Record<string, string>)['Idempotency-Key'] = crypto.randomUUID();
    }
  }

  // REC-005: Add X-API-Key for write operations on server side only
  // This avoids leaking secrets to client-side bundles
  if (isWrite && typeof window === 'undefined' && process.env.ZAKOPS_API_KEY) {
    (headers as Record<string, string>)['X-API-Key'] = process.env.ZAKOPS_API_KEY;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorBody = await response.text();
      let errorMsg = errorBody;
      try {
        const parsed = JSON.parse(errorBody);
        const normalized = normalizeError(parsed, response.status);
        errorMsg = normalized.message;
      } catch { /* use raw text */ }
      throw new ApiError(
        `API request failed: ${errorMsg}`,
        response.status,
        endpoint
      );
    }

    const data = await response.json();

    // Intercept error payloads that sneak through as HTTP 200 (partial availability)
    if (isErrorPayload(data)) {
      const normalized = normalizeError(data, response.status);
      throw new ApiError(
        `API returned error payload: ${normalized.message}`,
        response.status || 502,
        endpoint
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      0,
      endpoint
    );
  }
}

// ============================================================================
// Normalized API Functions - Always return arrays where expected
// ============================================================================

/**
 * Fetch all deals - returns {deals, totalCount}
 */
export async function getDeals(params?: {
  stage?: string;
  status?: string;
  broker?: string;
}): Promise<{ deals: Deal[]; totalCount: number }> {
  const searchParams = new URLSearchParams();
  if (params?.stage) searchParams.set('stage', params.stage);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.broker) searchParams.set('broker', params.broker);

  const query = searchParams.toString();
  const endpoint = `/api/deals${query ? `?${query}` : ''}`;

  try {
    const data = await apiFetch<unknown>(endpoint);
    const parsed = DealsResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid deals response:', parsed.error);
      return { deals: [], totalCount: 0 };
    }

    // Normalize: extract array from wrapper or return as-is
    if (Array.isArray(parsed.data)) {
      return { deals: parsed.data, totalCount: parsed.data.length };
    }
    return { deals: parsed.data.deals, totalCount: parsed.data.total_count ?? parsed.data.count ?? parsed.data.deals.length };
  } catch (error) {
    console.warn('Failed to fetch deals:', error);
    return { deals: [], totalCount: 0 };
  }
}

/**
 * Create a new deal.
 */
export async function createDeal(params: {
  canonical_name: string;
  display_name?: string;
  stage?: string;
  status?: string;
}): Promise<{ deal_id: string }> {
  return apiFetch('/api/deals', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Soft-delete (archive) a deal.
 * This is a UI-level delete only (keeps registry/events/materials intact).
 */
export async function archiveDeal(
  dealId: string,
  params?: { operator?: string; reason?: string }
): Promise<{ archived: boolean; deal_id: string }> {
  return apiFetch(`/api/deals/${encodeURIComponent(dealId)}/archive`, {
    method: 'POST',
    body: JSON.stringify({
      operator: params?.operator || 'operator',
      reason: params?.reason,
    }),
  });
}

/**
 * Soft-delete (archive) multiple deals.
 */
export async function bulkArchiveDeals(
  dealIds: string[],
  params?: { operator?: string; reason?: string }
): Promise<{ archived: string[]; skipped: string[] }> {
  return apiFetch(`/api/deals/bulk-archive`, {
    method: 'POST',
    body: JSON.stringify({
      deal_ids: dealIds,
      operator: params?.operator || 'operator',
      reason: params?.reason,
    }),
  });
}

/**
 * Fetch single deal detail
 * Returns partial data on validation errors (degrades gracefully)
 */
export async function getDeal(dealId: string): Promise<DealDetail | null> {
  try {
    const data = await apiFetch<unknown>(`/api/deals/${dealId}`);
    const parsed = DealDetailSchema.safeParse(data);

    if (!parsed.success) {
      // Log validation issues as debug info (not errors - this is expected behavior)
      if (process.env.NODE_ENV === 'development') {
        console.debug('[API] Deal schema validation notes:', parsed.error.issues.map(i => `${i.path.join('.')}: ${i.message}`).join(', '));
      }

      // Try to return partial data - the API returned something, just not perfectly shaped
      // Use a more permissive schema as fallback
      const rawData = data as Record<string, unknown>;
      if (rawData && typeof rawData === 'object' && rawData.deal_id) {
        console.debug('[API] Returning partially validated deal data for:', rawData.deal_id);
        return {
          deal_id: String(rawData.deal_id),
          canonical_name: rawData.canonical_name ? String(rawData.canonical_name) : null,
          display_name: rawData.display_name ? String(rawData.display_name) : null,
          folder_path: rawData.folder_path ? String(rawData.folder_path) : null,
          stage: String(rawData.stage || 'unknown'),
          status: String(rawData.status || 'unknown'),
          broker: rawData.broker as DealDetail['broker'] || null,
          company_info: rawData.company_info as DealDetail['company_info'] || null,
          metadata: rawData.metadata as DealDetail['metadata'] || null,
          state_machine: rawData.state_machine as DealDetail['state_machine'] || null,
          case_file: rawData.case_file || null,
          event_count: typeof rawData.event_count === 'number' ? rawData.event_count : undefined,
          pending_actions: typeof rawData.pending_actions === 'number' ? rawData.pending_actions : undefined,
          created_at: rawData.created_at ? String(rawData.created_at) : null,
          updated_at: rawData.updated_at ? String(rawData.updated_at) : null,
        };
      }
      return null;
    }

    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

/**
 * Fetch deal events - ALWAYS returns an array
 */
export async function getDealEvents(
  dealId: string,
  limit?: number
): Promise<DealEvent[]> {
  try {
    const query = limit ? `?limit=${limit}` : '';
    const data = await apiFetch<unknown>(`/api/deals/${dealId}/events${query}`);
    const parsed = EventsResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid events response:', parsed.error);
      return [];
    }

    if (Array.isArray(parsed.data)) {
      return parsed.data;
    }
    return parsed.data.events;
  } catch (error) {
    console.warn('Failed to fetch deal events:', error);
    return [];
  }
}

// ============================================================================
// Deal Transitions (FSM Audit Ledger)
// ============================================================================

export interface DealTransition {
  id: string;
  from_stage: string | null;
  to_stage: string;
  actor_id: string;
  actor_type: string;
  correlation_id: string | null;
  reason: string | null;
  timestamp: string | null;
}

/**
 * Fetch deal transitions (FSM audit ledger) - ALWAYS returns an array
 */
export async function getDealTransitions(dealId: string): Promise<DealTransition[]> {
  try {
    const data = await apiFetch<{ transitions?: DealTransition[] }>(`/api/deals/${dealId}/transitions`);
    return data?.transitions ?? [];
  } catch (error) {
    console.warn('Failed to fetch deal transitions:', error);
    return [];
  }
}

/**
 * Fetch deal case file
 */
const CaseFileEnvelopeSchema = z.object({
  deal_id: z.string(),
  version: z.string(),
  generated_at: z.string(),
  data: z.record(z.unknown()),
});

export type CaseFileEnvelope = z.infer<typeof CaseFileEnvelopeSchema>;

export async function getDealCaseFile(dealId: string): Promise<CaseFileEnvelope | null> {
  try {
    const data = await apiFetch<unknown>(`/api/deals/${dealId}/case-file`);
    const parsed = CaseFileEnvelopeSchema.safeParse(data);
    if (!parsed.success) {
      console.warn('Invalid case-file response:', parsed.error.message);
      return null;
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

// ============================================================================
// Enrichment Types and Functions
// ============================================================================

export interface MaterialLink {
  url: string;
  normalized_url: string;
  link_type: string;
  label?: string;
  source_email_id?: string;
  source_timestamp?: string;
  requires_auth: boolean;
  vendor_hint?: string;
  status: string;
  context_text?: string;
  classification_confidence: number;
}

const DealEnrichmentSchema = z.object({
  deal_id: z.string(),
  display_name: z.string().nullable().optional(),
  target_company_name: z.string().nullable().optional(),
  broker: z.object({
    name: z.string().nullable().optional(),
    email: z.string().nullable().optional(),
    company: z.string().nullable().optional(),
    phone: z.string().nullable().optional(),
    domain: z.string().nullable().optional(),
  }).optional(),
  last_email_at: z.string().nullable().optional(),
  enrichment_confidence: z.number().optional(),
  enriched_at: z.string().nullable().optional(),
  materials: z.object({
    total: z.number(),
    by_type: z.record(z.array(z.any())),
    auth_required_count: z.number(),
  }),
  aliases: z.array(z.object({
    alias: z.string(),
    alias_type: z.string(),
    confidence: z.number(),
  })),
});

export type DealEnrichment = z.infer<typeof DealEnrichmentSchema>;

export interface MaterialLink {
  url: string;
  normalized_url: string;
  link_type: string;
  label?: string;
  source_email_id?: string;
  source_timestamp?: string;
  requires_auth: boolean;
  vendor_hint?: string;
  status: string;
  context_text?: string;
  classification_confidence: number;
}

/**
 * Fetch deal enrichment data (materials, resolved names, etc.)
 */
export async function getDealEnrichment(dealId: string): Promise<DealEnrichment | null> {
  try {
    const data = await apiFetch<unknown>(`/api/deals/${dealId}/enrichment`);
    const parsed = DealEnrichmentSchema.safeParse(data);
    if (!parsed.success) {
      console.warn('Invalid enrichment response:', parsed.error.message);
      return null;
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

/**
 * Fetch all deferred actions - ALWAYS returns an array
 */
export async function getActions(params?: {
  deal_id?: string;
  status?: string;
}): Promise<Action[]> {
  try {
    const searchParams = new URLSearchParams();
    if (params?.deal_id) searchParams.set('deal_id', params.deal_id);
    if (params?.status) searchParams.set('status', params.status);

    const query = searchParams.toString();
    const endpoint = `/api/deferred-actions${query ? `?${query}` : ''}`;

    const data = await apiFetch<unknown>(endpoint);
    const parsed = ActionsResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid actions response:', parsed.error);
      return [];
    }

    if (Array.isArray(parsed.data)) {
      return parsed.data;
    }
    return parsed.data.actions;
  } catch (error) {
    console.warn('Failed to fetch actions:', error);
    return [];
  }
}

/**
 * Fetch due actions - ALWAYS returns an array
 */
export async function getDueActions(): Promise<Action[]> {
  try {
    const data = await apiFetch<unknown>('/api/deferred-actions/due');
    const parsed = ActionsResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid due actions response:', parsed.error);
      return [];
    }

    if (Array.isArray(parsed.data)) {
      return parsed.data;
    }
    return parsed.data.actions;
  } catch (error) {
    console.warn('Failed to fetch due actions:', error);
    return [];
  }
}

/**
 * Fetch quarantine items - ALWAYS returns an array
 */
export async function getQuarantineItems(): Promise<QuarantineItem[]> {
  try {
    const data = await apiFetch<unknown>('/api/quarantine');
    const parsed = QuarantineResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid quarantine response:', parsed.error);
      return [];
    }

    if (Array.isArray(parsed.data)) {
      return parsed.data;
    }
    return parsed.data.items;
  } catch (error) {
    console.warn('Failed to fetch quarantine items:', error);
    return [];
  }
}

/**
 * Fetch quarantine health status
 */
export async function getQuarantineHealth(): Promise<QuarantineHealth | null> {
  try {
    const data = await apiFetch<unknown>('/api/quarantine/health');
    const parsed = QuarantineHealthSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid quarantine health response:', parsed.error);
      return null;
    }

    return parsed.data;
  } catch (error) {
    console.warn('Failed to fetch quarantine health:', error);
    return null;
  }
}

/**
 * Resolve quarantine item
 */
export async function resolveQuarantineItem(
  itemId: string,
  resolution: 'link_to_deal' | 'create_new_deal' | 'discard',
  dealId?: string
): Promise<{ success: boolean; deal_id?: string }> {
  // Map frontend resolution actions to backend action values
  const actionMap: Record<string, string> = {
    'link_to_deal': 'approve',
    'create_new_deal': 'approve',
    'discard': 'reject',
  };
  return apiFetch('/api/quarantine/' + itemId + '/process', {
    method: 'POST',
    body: JSON.stringify({
      action: actionMap[resolution],
      deal_id: dealId,
      processed_by: 'operator',
    }),
  });
}

/**
 * Canonical quarantine queue with P2 filter/sort support
 */
export async function getQuarantineQueue(params?: {
  limit?: number;
  offset?: number;
  source_type?: string;
  status?: string;
  classification?: string;
  urgency?: string;
  confidence_min?: number;
  confidence_max?: number;
  sort_by?: string;
  sort_order?: string;
}): Promise<QuarantineItem[]> {
  try {
    const searchParams = new URLSearchParams();
    if (params?.limit != null) searchParams.set('limit', String(params.limit));
    if (params?.offset != null) searchParams.set('offset', String(params.offset));
    if (params?.source_type) searchParams.set('source_type', params.source_type);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.classification) searchParams.set('classification', params.classification);
    if (params?.urgency) searchParams.set('urgency', params.urgency);
    if (params?.confidence_min != null) searchParams.set('confidence_min', String(params.confidence_min));
    if (params?.confidence_max != null) searchParams.set('confidence_max', String(params.confidence_max));
    if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params?.sort_order) searchParams.set('sort_order', params.sort_order);
    const query = searchParams.toString();
    const endpoint = `/api/quarantine${query ? `?${query}` : ''}`;

    const data = await apiFetch<unknown>(endpoint);
    const parsed = QuarantineResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid quarantine queue response:', parsed.error);
      return [];
    }

    if (Array.isArray(parsed.data)) {
      return parsed.data;
    }
    return parsed.data.items;
  } catch (error) {
    console.warn('Failed to fetch quarantine queue:', error);
    return [];
  }
}

/**
 * Quarantine detail payload (right-side panel).
 * QI-001 P1: Unified to parse against QuarantineItemSchema (not legacy QuarantinePreviewSchema).
 * Falls back to raw data on parse failure — never returns null for valid API responses (F-4).
 */
export async function getQuarantinePreview(itemId: string): Promise<QuarantineItem | null> {
  try {
    const data = await apiFetch<unknown>(`/api/quarantine/${encodeURIComponent(itemId)}`);
    const parsed = QuarantineItemSchema.safeParse(data);
    if (!parsed.success) {
      // Graceful degradation: return raw data cast as QuarantineItem (F-4)
      // Schema has .passthrough() so unknown fields are preserved
      console.warn('[Quarantine] Schema drift detected — rendering available data:', parsed.error.issues?.length, 'issues');
      // Try to return raw data if it's at least an object
      if (data && typeof data === 'object') {
        return data as QuarantineItem;
      }
      return null;
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

/**
 * Approve a quarantine item via POST /api/quarantine/{id}/process.
 * P2-03: Supports optimistic locking via expectedVersion.
 * P2-05: Supports approve-with-edits via corrections.
 */
export async function approveQuarantineItem(
  itemId: string,
  approvedBy: string,
  options?: {
    dealId?: string;
    corrections?: Record<string, string>;
    expectedVersion?: number;
    notes?: string;
  }
): Promise<{ success: boolean; deal_id?: string; deal_created?: boolean; error?: string; conflict?: boolean }> {
  try {
    const response = await apiFetch<{
      status: string;
      item_id: string;
      deal_id?: string;
      deal_created?: boolean;
    }>(`/api/quarantine/${encodeURIComponent(itemId)}/process`, {
      method: 'POST',
      body: JSON.stringify({
        action: 'approve',
        processed_by: approvedBy,
        deal_id: options?.dealId,
        corrections: options?.corrections,
        expected_version: options?.expectedVersion,
        notes: options?.notes,
      }),
    });
    return { success: true, deal_id: response.deal_id, deal_created: response.deal_created };
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 409) {
        return { success: false, error: error.message, conflict: true };
      }
      return { success: false, error: error.message };
    }
    return { success: false, error: error instanceof Error ? error.message : 'Failed to approve' };
  }
}

/**
 * Reject a quarantine item via POST /api/quarantine/{id}/process.
 * P2-06: Reason is now required.
 * P2-03: Supports optimistic locking.
 */
export async function rejectQuarantineItem(params: {
  itemId: string;
  rejectedBy: string;
  reason: string;
  expectedVersion?: number;
}): Promise<{ success: boolean; error?: string; conflict?: boolean }> {
  try {
    await apiFetch<{
      status: string;
      item_id: string;
    }>(`/api/quarantine/${encodeURIComponent(params.itemId)}/process`, {
      method: 'POST',
      body: JSON.stringify({
        action: 'reject',
        processed_by: params.rejectedBy,
        reason: params.reason,
        expected_version: params.expectedVersion,
      }),
    });
    return { success: true };
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 409) {
        return { success: false, error: error.message, conflict: true };
      }
      return { success: false, error: error.message };
    }
    return { success: false, error: error instanceof Error ? error.message : 'Reject failed' };
  }
}

/**
 * P2-04: Escalate a quarantine item for supervisor review.
 */
export async function escalateQuarantineItem(params: {
  itemId: string;
  escalatedBy: string;
  priority: 'normal' | 'high' | 'urgent';
  reason: string;
  note: string;
  expectedVersion?: number;
}): Promise<{ success: boolean; error?: string; conflict?: boolean }> {
  try {
    await apiFetch<{ status: string; item_id: string }>(
      `/api/quarantine/${encodeURIComponent(params.itemId)}/process`,
      {
        method: 'POST',
        body: JSON.stringify({
          action: 'escalate',
          processed_by: params.escalatedBy,
          escalation_priority: params.priority,
          escalation_reason: params.reason,
          notes: params.note,
          expected_version: params.expectedVersion,
        }),
      }
    );
    return { success: true };
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 409) return { success: false, error: error.message, conflict: true };
      return { success: false, error: error.message };
    }
    return { success: false, error: error instanceof Error ? error.message : 'Escalate failed' };
  }
}

/**
 * P2-08: Bulk approve/reject quarantine items with per-item validation.
 */
export async function bulkProcessQuarantineItems(params: {
  itemIds: string[];
  action: 'approve' | 'reject';
  processedBy: string;
  reason?: string;
}): Promise<{
  results: Array<{ item_id: string; success: boolean; status?: string; deal_id?: string; error?: string }>;
  succeeded: number;
  failed: number;
}> {
  return apiFetch('/api/quarantine/bulk-process', {
    method: 'POST',
    body: JSON.stringify({
      item_ids: params.itemIds,
      action: params.action,
      processed_by: params.processedBy,
      reason: params.reason,
    }),
  });
}

/**
 * Delete (hide) a quarantine item from the decision queue.
 * This does NOT approve/reject, does NOT cancel the action, and does NOT touch Gmail.
 */
export async function deleteQuarantineItem(
  quarantineId: string,
  params?: { deletedBy?: string; reason?: string }
): Promise<{ hidden: boolean; quarantine_id: string }> {
  return apiFetch(`/api/quarantine/${encodeURIComponent(quarantineId)}/delete`, {
    method: 'POST',
    body: JSON.stringify({
      deleted_by: params?.deletedBy || 'operator',
      reason: params?.reason,
    }),
  });
}

/**
 * Bulk delete (hide) quarantine items from the decision queue.
 */
export async function bulkDeleteQuarantineItems(
  actionIds: string[],
  params?: { deletedBy?: string; reason?: string }
): Promise<{ hidden: string[]; missing: string[]; already_hidden: string[] }> {
  return apiFetch(`/api/quarantine/bulk-delete`, {
    method: 'POST',
    body: JSON.stringify({
      action_ids: actionIds,
      deleted_by: params?.deletedBy || 'operator',
      reason: params?.reason,
    }),
  });
}

// P4-04: Undo quarantine approval (admin-only)
export async function undoQuarantineApproval(
  itemId: string,
  params: { adminUser: string; reason: string }
): Promise<{ status: string; item_id: string; deal_archived: string | null; restored_to: string }> {
  return apiFetch(`/api/quarantine/${itemId}/undo-approve`, {
    method: 'POST',
    body: JSON.stringify({
      admin_user: params.adminUser,
      reason: params.reason,
    }),
  });
}

// QI-001 P1: Sender intelligence schema — matches GET /api/quarantine/sender-intelligence
export const SenderIntelligenceSchema = z.object({
  sender_email: z.string(),
  rollup: z.object({
    messages_seen: z.number(),
    quarantine_injected: z.number(),
    approved_to_deals: z.number(),
    rejected: z.number(),
    pending: z.number(),
    approval_rate: z.number().nullable().optional(),
    avg_time_to_decision_hours: z.number().nullable().optional(),
    avg_time_to_approval_hours: z.number().nullable().optional(),
    first_seen_ts: z.string().nullable().optional(),
    last_seen_ts: z.string().nullable().optional(),
  }),
  deal_associations: z.array(z.object({
    deal_id: z.string(),
    count: z.number(),
    last_ts: z.string().nullable().optional(),
    stage: z.string().nullable().optional(),
  })),
  signals: z.object({
    is_known_broker: z.boolean(),
    likely_broker_score: z.number(),
    common_domains: z.array(z.string()),
    notes: z.string().nullable().optional(),
  }),
  as_of_ts: z.string(),
}).passthrough();

export type SenderIntelligence = z.infer<typeof SenderIntelligenceSchema>;

/**
 * Fetch sender intelligence for a given email address.
 * QI-001 P1: Returns null on 404/parse failure (F-6 null safety handled by caller).
 */
export async function getSenderIntelligence(senderEmail: string): Promise<SenderIntelligence | null> {
  try {
    const data = await apiFetch<unknown>(
      `/api/quarantine/sender-intelligence?sender_email=${encodeURIComponent(senderEmail)}`
    );
    const parsed = SenderIntelligenceSchema.safeParse(data);
    if (!parsed.success) {
      console.warn('[Quarantine] Sender intelligence parse failure:', parsed.error.issues?.length, 'issues');
      return null;
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 400)) return null;
    console.warn('[Quarantine] Sender intelligence fetch degraded:', error);
    return null;
  }
}

// QI-001 P1: Triage feedback schema — matches GET /api/quarantine/feedback (F-13)
export const TriageFeedbackSchema = z.object({
  sender_email: z.string(),
  summary: z.object({
    total_quarantine_items: z.number(),
    approved_count: z.number(),
    rejected_count: z.number(),
    pending_count: z.number(),
    approval_rate: z.number().nullable().optional(),
    last_seen_ts: z.string().nullable().optional(),
    typical_outcome: z.string(),
  }),
  recent_items: z.array(z.object({
    message_id: z.string().nullable().optional(),
    thread_id: z.string().nullable().optional(),
    created_ts: z.string().nullable().optional(),
    decision: z.string(),
    deal_id: z.string().nullable().optional(),
    deal_stage: z.string().nullable().optional(),
    operator_notes: z.string().nullable().optional(),
    operator_reasons: z.array(z.string()).optional(),
  })),
  corrections: z.object({
    routing_overrides: z.array(z.object({
      message_id: z.string().nullable().optional(),
      from_deal_id: z.string().nullable().optional(),
      to_deal_id: z.string().nullable().optional(),
      ts: z.string().nullable().optional(),
      reason: z.string().nullable().optional(),
    })),
    classification_overrides: z.array(z.any()),
  }),
}).passthrough();

export type TriageFeedback = z.infer<typeof TriageFeedbackSchema>;

/**
 * Fetch per-sender triage feedback (past decisions).
 * QI-001 P1 (F-13): Returns null on any failure.
 */
export async function getTriageFeedback(senderEmail: string): Promise<TriageFeedback | null> {
  try {
    const data = await apiFetch<unknown>(
      `/api/quarantine/feedback?sender_email=${encodeURIComponent(senderEmail)}&include_corrections=true`
    );
    const parsed = TriageFeedbackSchema.safeParse(data);
    if (!parsed.success) {
      console.warn('[Quarantine] Triage feedback parse failure:', parsed.error.issues?.length, 'issues');
      return null;
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 400)) return null;
    console.warn('[Quarantine] Triage feedback fetch degraded:', error);
    return null;
  }
}

// P5-03: Deal thread management
export interface DealThread {
  id: string;
  deal_id: string;
  thread_id: string;
  subject: string | null;
  provider: string;
  created_at: string;
}

export async function getDealThreads(dealId: string): Promise<{ threads: DealThread[]; count: number }> {
  return apiFetch(`/api/deals/${encodeURIComponent(dealId)}/threads`);
}

export async function addDealThread(dealId: string, threadId: string, subject?: string): Promise<{ success: boolean }> {
  return apiFetch(`/api/deals/${encodeURIComponent(dealId)}/threads`, {
    method: 'POST',
    body: JSON.stringify({ thread_id: threadId, subject }),
  });
}

export async function removeDealThread(dealId: string, threadId: string): Promise<{ success: boolean }> {
  return apiFetch(`/api/deals/${encodeURIComponent(dealId)}/threads/${encodeURIComponent(threadId)}`, {
    method: 'DELETE',
  });
}

export async function moveDealThread(
  fromDealId: string,
  threadId: string,
  targetDealId: string
): Promise<{ success: boolean }> {
  return apiFetch(`/api/deals/${encodeURIComponent(fromDealId)}/threads/${encodeURIComponent(threadId)}/move`, {
    method: 'POST',
    body: JSON.stringify({ target_deal_id: targetDealId }),
  });
}

// =============================================================================
// Delegated Tasks (P6 — Collaboration Contract)
// =============================================================================

const DelegatedTaskSchema = z.object({
  id: z.string(),
  deal_id: z.string().nullable(),
  task_type: z.string(),
  status: z.enum(['pending', 'queued', 'executing', 'completed', 'failed', 'dead_letter']),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  title: z.string(),
  description: z.string().nullable(),
  context: z.record(z.unknown()),
  result: z.record(z.unknown()).nullable(),
  feedback: z.string().nullable(),
  assigned_to: z.string(),
  created_by: z.string(),
  correlation_id: z.string().nullable(),
  max_attempts: z.number(),
  attempt_count: z.number(),
  last_error: z.string().nullable(),
  requires_confirmation: z.boolean(),
  confirmed_by: z.string().nullable(),
  confirmed_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
  queued_at: z.string().nullable(),
  started_at: z.string().nullable(),
  resolved_at: z.string().nullable(),
});

export type DelegatedTask = z.infer<typeof DelegatedTaskSchema>;

const DealTasksResponseSchema = z.object({
  tasks: z.array(DelegatedTaskSchema),
  count: z.number(),
});

export async function getDealTasks(dealId: string): Promise<{ tasks: DelegatedTask[]; count: number }> {
  try {
    const data = await apiFetch<unknown>(`/api/deals/${encodeURIComponent(dealId)}/tasks`);
    const parsed = DealTasksResponseSchema.safeParse(data);
    if (!parsed.success) {
      console.warn('Invalid tasks response:', parsed.error.message);
      return { tasks: [], count: 0 };
    }
    return parsed.data;
  } catch {
    return { tasks: [], count: 0 };
  }
}

export async function retryDelegatedTask(taskId: string): Promise<{ success: boolean; message?: string }> {
  return apiFetch(`/api/tasks/${encodeURIComponent(taskId)}/retry`, { method: 'POST' });
}

export async function confirmDelegatedTask(
  taskId: string,
  confirmedBy: string,
): Promise<{ success: boolean; message?: string }> {
  return apiFetch(`/api/tasks/${encodeURIComponent(taskId)}/confirm`, {
    method: 'POST',
    body: JSON.stringify({ confirmed_by: confirmedBy }),
  });
}

// ============================================================================
// Delegation API (Phase 2 Integration)
// ============================================================================

export type DelegationType = {
  lease_seconds: number;
  category: string;
  requires_deal: boolean;
  description: string;
};

export class DelegationDisabledError extends Error {
  constructor(message = 'Delegation is disabled by administrator') {
    super(message);
    this.name = 'DelegationDisabledError';
  }
}

export async function getDelegationTypes(): Promise<Record<string, DelegationType>> {
  try {
    const data = await apiFetch<{ types: Record<string, DelegationType> }>('/api/delegation/types');
    return data.types ?? {};
  } catch (err) {
    if (err instanceof ApiError && err.status === 503) {
      throw new DelegationDisabledError('Delegation is disabled by administrator');
    }
    console.warn('[API] Delegation types unavailable:', err);
    return {};
  }
}

export async function createDelegatedTask(params: {
  task_type: string;
  title: string;
  deal_id?: string;
  description?: string;
  context?: Record<string, unknown>;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  assigned_to?: string;
}): Promise<{ task_id: string; status: string } | null> {
  try {
    return await apiFetch('/api/delegation/tasks', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 503) {
      throw new DelegationDisabledError('Delegation is disabled by administrator');
    }
    console.warn('[API] Failed to create delegated task:', err);
    return null;
  }
}

export async function sendTaskMessage(taskId: string, text: string, role = 'operator'): Promise<{ task_id: string; message_count: number } | null> {
  try {
    return await apiFetch(`/api/tasks/${taskId}/message`, {
      method: 'POST',
      body: JSON.stringify({ text, role }),
    });
  } catch (err) {
    console.warn('[API] Failed to send task message:', err);
    return null;
  }
}

export async function listDelegatedTasks(params?: {
  status?: string;
  assigned_to?: string;
  task_type?: string;
  claimable_only?: boolean;
  limit?: number;
}): Promise<{ tasks: DelegatedTask[]; count: number }> {
  try {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.assigned_to) query.set('assigned_to', params.assigned_to);
    if (params?.task_type) query.set('task_type', params.task_type);
    if (params?.claimable_only) query.set('claimable_only', 'true');
    if (params?.limit) query.set('limit', String(params.limit));
    const qs = query.toString();
    const data = await apiFetch<unknown>(`/api/delegation/tasks${qs ? `?${qs}` : ''}`);
    const parsed = DealTasksResponseSchema.safeParse(data);
    if (!parsed.success) return { tasks: [], count: 0 };
    return parsed.data;
  } catch {
    return { tasks: [], count: 0 };
  }
}

/**
 * Filesystem-backed deal materials view (correspondence bundles + links)
 */
export async function getDealMaterials(dealId: string): Promise<DealMaterials | null> {
  try {
    const data = await apiFetch<unknown>(`/api/deals/${dealId}/materials`);
    const parsed = DealMaterialsSchema.safeParse(data);
    if (!parsed.success) {
      console.warn('Invalid deal materials response:', parsed.error);
      return null;
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

/**
 * Fetch alerts - ALWAYS returns an array
 */
export async function getAlerts(): Promise<Alert[]> {
  try {
    const data = await apiFetch<unknown>('/api/alerts');
    const parsed = AlertsResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid alerts response:', parsed.error);
      return [];
    }

    if (Array.isArray(parsed.data)) {
      return parsed.data;
    }
    return parsed.data.alerts;
  } catch (error) {
    console.warn('Failed to fetch alerts:', error);
    return [];
  }
}

/**
 * Fetch classification metrics
 */
export async function getClassificationMetrics(): Promise<ClassificationMetrics | null> {
  try {
    const data = await apiFetch<unknown>('/api/metrics/classification');
    const parsed = ClassificationMetricsSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid classification metrics response:', parsed.error);
      return null;
    }

    return parsed.data;
  } catch (error) {
    console.warn('Failed to fetch classification metrics:', error);
    return null;
  }
}

/**
 * Fetch checkpoints - ALWAYS returns an array
 */
export async function getCheckpoints(): Promise<Checkpoint[]> {
  try {
    const data = await apiFetch<unknown>('/api/checkpoints');
    const parsed = CheckpointsResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid checkpoints response:', parsed.error);
      return [];
    }

    return parsed.data;
  } catch (error) {
    console.warn('Failed to fetch checkpoints:', error);
    return [];
  }
}

/**
 * Fetch pipeline summary
 */
export async function getPipeline(): Promise<{
  total_active: number;
  stages: Record<string, PipelineStage>;
} | null> {
  try {
    const data = await apiFetch<unknown>('/api/pipeline');
    const parsed = PipelineResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid pipeline response:', parsed.error);
      return null;
    }

    return parsed.data;
  } catch (error) {
    console.warn('Failed to fetch pipeline:', error);
    return null;
  }
}

/**
 * Transition deal to new stage
 */
export async function transitionDeal(
  dealId: string,
  toStage: string,
  reason: string,
  approvedBy: string
): Promise<{ success: boolean; message?: string }> {
  const params = new URLSearchParams();
  if (approvedBy) params.set('transitioned_by', approvedBy);
  const qs = params.toString();

  return apiFetch(`/api/deals/${dealId}/transition${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    body: JSON.stringify({
      new_stage: toStage,
      reason,
    }),
  });
}

/**
 * Add note to deal
 */
export async function addDealNote(
  dealId: string,
  content: string,
  category?: string
): Promise<{ success: boolean; event_id?: string }> {
  return apiFetch(`/api/deals/${dealId}/notes`, {
    method: 'POST',
    body: JSON.stringify({
      content,
      category: category || 'general',
    }),
  });
}

// ============================================================================
// Chat API
// ============================================================================

export interface ChatScope {
  type: 'global' | 'deal' | 'document';
  deal_id?: string;
  doc?: {
    url?: string;
    title?: string;
  };
}

export interface ChatCitation {
  id: string;
  source: string;
  url?: string;
  snippet: string;
  chunk?: number;
  similarity?: number;
  event_id?: string;
  event_type?: string;
  timestamp?: string;
}

export interface ChatProposal {
  proposal_id: string;
  type: ChatProposalType;
  deal_id?: string;
  params?: Record<string, unknown>;
  reason?: string;
  status: 'pending_approval' | 'executed' | 'rejected' | 'failed';
  result?: unknown;
  error?: string;
  rejected_by?: string;
  rejected_at?: string;
  reject_reason?: string;
}

export const CHAT_PROPOSAL_TYPES = [
  'add_note',
  'draft_email',
  'create_task',
  'stage_transition',
  'request_docs',
  'correct_brain_summary',
  'search_web',
  'mark_complete',
  'add_document',
] as const;

export type ChatProposalType = (typeof CHAT_PROPOSAL_TYPES)[number];

export function normalizeChatProposalType(type: string | null | undefined): ChatProposalType | null {
  const raw = (type || '').trim().toLowerCase();
  if (!raw) return null;

  const normalized = raw.replace(/[\s-]+/g, '_');
  const aliasMap: Record<string, ChatProposalType> = {
    schedule_action: 'create_task',
    schedule_task: 'create_task',
    scheduleaction: 'create_task',
  };

  const aliased = aliasMap[normalized] || (normalized as ChatProposalType);
  return CHAT_PROPOSAL_TYPES.includes(aliased) ? aliased : null;
}

export interface ChatEvidenceSummary {
  sources_queried: string[];
  rag: {
    query: string;
    results_found: number;
    top_similarity: number;
  };
  events: {
    window: string;
    count: number;
    types: string[];
  };
  case_file: {
    loaded: boolean;
    sections_used: string[];
  };
  registry: {
    loaded: boolean;
    stage: string | null;
  };
  actions: {
    count: number;
  };
  total_evidence_size: number;
}

export interface ChatResponse {
  content: string;
  citations: ChatCitation[];
  proposals: ChatProposal[];
  evidence_summary: ChatEvidenceSummary | null;
  model_used: string;
  latency_ms: number;
  warnings: string[];
}

export interface ChatStreamEvent {
  type: 'token' | 'evidence' | 'done' | 'error' | 'progress';
  data: {
    token?: string;
    citations?: ChatCitation[];
    proposals?: ChatProposal[];
    model_used?: string;
    latency_ms?: number;
    session_id?: string;
    message?: string;
    step?: string;
  } | ChatEvidenceSummary;
}

/**
 * Send a chat message (non-streaming)
 */
export async function sendChatMessage(
  query: string,
  scope: ChatScope,
  sessionId?: string,
  options?: Record<string, unknown>
): Promise<ChatResponse> {
  return apiFetch('/api/chat/complete', {
    method: 'POST',
    body: JSON.stringify({
      query,
      scope,
      session_id: sessionId,
      options,
    }),
  });
}

/**
 * Send a chat message with SSE streaming.
 * REC-031: Includes automatic retry with exponential backoff on network errors.
 * Returns an async generator that yields events.
 */
export async function* streamChatMessage(
  query: string,
  scope: ChatScope,
  sessionId?: string,
  options?: Record<string, unknown>
): AsyncGenerator<ChatStreamEvent, void, unknown> {
  const MAX_RETRIES = 2;
  const BASE_DELAY_MS = 1000;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          scope,
          session_id: sessionId,
          options,
        }),
      });

      if (!response.ok) {
        let errorBody = '';
        try {
          errorBody = await response.text();
          if (errorBody.length > 200) {
            errorBody = errorBody.slice(0, 200) + '...';
          }
        } catch {
          errorBody = response.statusText;
        }
        // Don't retry HTTP errors (4xx/5xx) — only network failures
        throw new ApiError(
          `Chat request failed: ${errorBody}`,
          response.status,
          '/api/chat'
        );
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let receivedDone = false;

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE events from buffer
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          let currentEvent = '';
          let currentData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              currentData = line.slice(6);
            } else if (line === '' && currentEvent && currentData) {
              try {
                const parsedData = JSON.parse(currentData);
                if (currentEvent === 'done') receivedDone = true;
                yield {
                  type: currentEvent as ChatStreamEvent['type'],
                  data: parsedData,
                };
              } catch {
                console.debug('[Chat] Failed to parse SSE data:', currentData);
              }
              currentEvent = '';
              currentData = '';
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      // Stream completed — if we got a done event, no retry needed
      if (receivedDone) return;

      // Stream ended without done event — treat as premature close
      if (attempt < MAX_RETRIES) {
        console.warn(`[Chat] Stream ended without done event, retrying (attempt ${attempt + 1}/${MAX_RETRIES})...`);
        yield { type: 'progress' as ChatStreamEvent['type'], data: { step: 'Reconnecting...' } };
        await new Promise((r) => setTimeout(r, BASE_DELAY_MS * (attempt + 1)));
        continue;
      }
      // Exhausted retries — exit normally (consumer sees incomplete response)
      return;

    } catch (err) {
      // ApiError = HTTP error, don't retry
      if (err instanceof ApiError) throw err;

      // Network error — retry if attempts remain
      if (attempt < MAX_RETRIES) {
        console.warn(`[Chat] Network error, retrying (attempt ${attempt + 1}/${MAX_RETRIES}):`, err);
        yield { type: 'progress' as ChatStreamEvent['type'], data: { step: 'Reconnecting...' } };
        await new Promise((r) => setTimeout(r, BASE_DELAY_MS * (attempt + 1)));
        continue;
      }
      throw err;
    }
  }
}

/**
 * Execute a chat proposal (requires approval)
 */
export async function executeChatProposal(
  proposalId: string,
  sessionId: string,
  approvedBy: string,
  action: 'approve' | 'reject' = 'approve',
  rejectReason?: string
): Promise<{
  success: boolean;
  result?: unknown;
  proposal?: ChatProposal;
  proposal_type?: string;
  error?: string;
  reason?: string;
  current_status?: string;
}> {
  return apiFetch('/api/chat/execute-proposal', {
    method: 'POST',
    body: JSON.stringify({
      proposal_id: proposalId,
      session_id: sessionId,
      approved_by: approvedBy,
      action,
      reject_reason: rejectReason,
    }),
  });
}

/**
 * Get chat session history (with full message data from SQLite backend)
 */
export async function getChatSession(sessionId: string): Promise<{
  session_id: string;
  scope: ChatScope;
  created_at: string;
  last_activity: string;
  messages: Array<{
    role: string;
    content: string;
    timestamp: string;
    citations?: ChatCitation[];
    proposals?: ChatProposal[];
    timings?: Record<string, unknown>;
    warnings?: string[];
    provider_used?: string;
    cache_hit?: boolean;
  }>;
} | null> {
  try {
    return await apiFetch(`/api/chat/session/${sessionId}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

// ============================================================================
// Kinetic Actions API (Action Engine v1.2)
// ============================================================================

/**
 * Kinetic Action statuses (state machine)
 * R2-1.3 FIX: Aligned with backend lowercase status values
 */
export const KINETIC_ACTION_STATUSES = [
  'pending',
  'pending_approval',
  'queued',
  'ready',
  'running',
  'completed',
  'failed',
  'cancelled',
  'rejected',
] as const;

export type KineticActionStatus = (typeof KINETIC_ACTION_STATUSES)[number];

/**
 * Schema property for dynamic form generation
 */
export interface SchemaProperty {
  type: string;
  description?: string;
  required?: boolean;
  enum?: string[];
  default?: unknown;
  format?: string;
  items?: SchemaProperty;
  properties?: Record<string, SchemaProperty>;
  minLength?: number;
  maxLength?: number;
  minimum?: number;
  maximum?: number;
}

/**
 * Input schema for capabilities (JSON Schema-like)
 */
export interface InputSchema {
  type: string;
  properties: Record<string, SchemaProperty>;
  required?: string[];
}

/**
 * Output artifact definition
 */
export interface OutputArtifact {
  type: string;
  description: string;
  mime_type: string;
}

/**
 * Capability manifest from backend
 */
export interface Capability {
  capability_id: string;
  version: string;
  title: string;
  description: string;
  action_type: string;
  input_schema: InputSchema;
  output_artifacts: OutputArtifact[];
  risk_level: 'low' | 'medium' | 'high';
  requires_approval: boolean;
  cloud_required?: boolean;
  llm_allowed?: boolean;
  constraints?: string[];
  examples?: Array<{
    description: string;
    inputs: Record<string, unknown>;
  }>;
  tags: string[];
}

/**
 * Artifact attached to a completed action
 */
export interface KineticArtifact {
  artifact_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  created_at: string;
  download_url: string;
}

/**
 * Kinetic Action (from Action Engine v1.2)
 */
export interface KineticAction {
  action_id: string;
  deal_id: string;
  action_type: string;
  capability_id?: string;
  title: string;
  summary?: string;
  status: KineticActionStatus;
  inputs: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  artifacts: KineticArtifact[];
  error?: {
    message: string;
    code?: string;
    category?: string;
    retryable?: boolean;
    details?: string;
  };
  created_at: string;
  updated_at: string;
  approved_at?: string;
  approved_by?: string;
  started_at?: string;
  completed_at?: string;
  retry_count: number;
  max_retries: number;
  created_by?: string;
  progress?: number;
  progress_message?: string;
}

/**
 * Action metrics from /api/actions/metrics
 * Aligned with backend response structure (SCHEMA-ALIGN-001)
 */
export interface ActionMetrics {
  total_actions: number;
  pending_approval: number;
  completed_today: number;
  failed_today: number;
  avg_approval_time_seconds?: number | null;
  avg_execution_time_seconds?: number | null;
  by_capability?: Record<string, unknown>;
  version?: string;
}

// Zod schemas for Kinetic Actions API
const KineticArtifactSchema = z.object({
  artifact_id: z.string(),
  filename: z.string(),
  mime_type: z.string(),
  size_bytes: z.number(),
  created_at: z.string(),
  download_url: z.string(),
});

// KineticActionSchema: Hardened to handle null values from backend
// Uses .nullish() (null | undefined) for optional fields to handle legacy data
const KineticActionSchema = z.object({
  action_id: z.string(),
  // deal_id: Backend should send "GLOBAL" for non-deal actions, but handle null gracefully
  deal_id: z.string().nullish().transform(v => v || 'GLOBAL'),
  action_type: z.string(),
  // capability_id: May be null for legacy actions
  capability_id: z.string().nullish().transform(v => v ?? undefined),
  title: z.string(),
  summary: z.string().nullish().transform(v => v ?? undefined),
  status: z.enum(KINETIC_ACTION_STATUSES),
  // inputs: Some legacy rows may store null; coerce to {} (Zod .default does not apply to null)
  inputs: z.record(z.any()).nullish().transform(v => v ?? {}),
  outputs: z.record(z.any()).nullish().transform(v => v ?? undefined),
  artifacts: z.array(KineticArtifactSchema).nullish().transform(v => v ?? []),
  // error: May be null when no error, or object when failed
  error: z.object({
    message: z.string(),
    code: z.string().nullish().transform(v => v ?? undefined),
    category: z.string().nullish().transform(v => v ?? undefined),
    retryable: z.boolean().nullish().transform(v => v ?? undefined),
    details: z.string().nullish().transform(v => v ?? undefined),
  }).nullish().transform(v => v ?? undefined),
  created_at: z.string(),
  updated_at: z.string(),
  approved_at: z.string().nullish().transform(v => v ?? undefined),
  approved_by: z.string().nullish().transform(v => v ?? undefined),
  started_at: z.string().nullish().transform(v => v ?? undefined),
  completed_at: z.string().nullish().transform(v => v ?? undefined),
  retry_count: z.number().nullish().transform(v => v ?? 0),
  max_retries: z.number().nullish().transform(v => v ?? 3),
  created_by: z.string().nullish().transform(v => v ?? undefined),
  progress: z.number().nullish().transform(v => v ?? undefined),
  progress_message: z.string().nullish().transform(v => v ?? undefined),
});

const KineticActionsResponseSchema = z.object({
  count: z.number().optional(),
  actions: z.array(KineticActionSchema),
}).or(z.array(KineticActionSchema));

const CapabilitySchema = z.object({
  capability_id: z.string(),
  version: z.string(),
  title: z.string(),
  description: z.string(),
  action_type: z.string(),
  input_schema: z.object({
    type: z.string(),
    properties: z.record(z.any()),
    required: z.array(z.string()).optional(),
  }),
  output_artifacts: z.array(z.object({
    type: z.string(),
    description: z.string(),
    mime_type: z.string(),
  })),
  risk_level: z.enum(['low', 'medium', 'high']),
  requires_approval: z.boolean(),
  cloud_required: z.boolean().optional(),
  llm_allowed: z.boolean().optional(),
  constraints: z.array(z.string()).optional(),
  examples: z.array(z.object({
    description: z.string(),
    inputs: z.record(z.any()),
  })).optional(),
  tags: z.array(z.string()),
});

const CapabilitiesResponseSchema = z.object({
  capabilities: z.array(CapabilitySchema),
  count: z.number(),
});

// ActionMetricsSchema: Aligned with backend /api/actions/metrics response
// Backend returns: {total_actions, pending_approval, completed_today, failed_today, ...}
const ActionMetricsSchema = z.object({
  total_actions: z.number(),
  pending_approval: z.number(),
  completed_today: z.number(),
  failed_today: z.number(),
  avg_approval_time_seconds: z.number().nullable().optional(),
  avg_execution_time_seconds: z.number().nullable().optional(),
  by_capability: z.record(z.any()).optional(),
  version: z.string().optional(),
});

/**
 * Check if Kinetic Actions API is available (mock mode detection)
 */
let _kineticApiAvailable: boolean | null = null;

async function isKineticApiAvailable(): Promise<boolean> {
  if (_kineticApiAvailable !== null) return _kineticApiAvailable;

  try {
    const response = await fetch('/api/actions/capabilities');
    _kineticApiAvailable = response.ok;
  } catch {
    _kineticApiAvailable = false;
  }
  return _kineticApiAvailable;
}

/**
 * Fetch all Kinetic Actions - ALWAYS returns an array
 * Falls back to legacy deferred-actions endpoint if Kinetic API unavailable
 */
export async function getKineticActions(params?: {
  deal_id?: string;
  status?: KineticActionStatus;
  type?: string;
  limit?: number;
  offset?: number;
}): Promise<KineticAction[]> {
  const searchParams = new URLSearchParams();
  if (params?.deal_id) searchParams.set('deal_id', params.deal_id);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.type) searchParams.set('type', params.type);
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));

  const query = searchParams.toString();

  try {
    // Try Kinetic API first
    if (await isKineticApiAvailable()) {
      const endpoint = `/api/actions${query ? `?${query}` : ''}`;
      const data = await apiFetch<unknown>(endpoint);
      const parsed = KineticActionsResponseSchema.safeParse(data);

      if (!parsed.success) {
        console.warn('Invalid Kinetic actions response:', parsed.error);
        return [];
      }

      if (Array.isArray(parsed.data)) {
        return parsed.data;
      }
      return parsed.data.actions;
    }

    // Fallback: convert legacy actions to Kinetic format
    // R2-1.3 FIX: Use lowercase status values
    const legacyActions = await getActions({
      deal_id: params?.deal_id,
      status: params?.status === 'completed' ? 'completed' : params?.status === 'pending_approval' ? 'pending' : undefined,
    });

    return legacyActions.map(a => ({
      action_id: a.action_id,
      deal_id: a.deal_id ?? '',
      action_type: a.action_type,
      title: a.action_type,
      status: (a.status === 'completed' ? 'completed' : 'pending') as KineticActionStatus,
      inputs: a.data || {},
      artifacts: [],
      created_at: a.scheduled_for ?? new Date().toISOString(),
      updated_at: a.scheduled_for ?? new Date().toISOString(),
      retry_count: 0,
      max_retries: 3,
    }));
  } catch (error) {
    console.warn('Failed to fetch kinetic actions:', error);
    return [];
  }
}

/**
 * Fetch single Kinetic Action
 */
export async function getKineticAction(actionId: string): Promise<KineticAction | null> {
  if (!await isKineticApiAvailable()) {
    return null;
  }

  try {
    const data = await apiFetch<unknown>(`/api/actions/${actionId}`);
    const parsed = KineticActionSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid Kinetic action response:', parsed.error);
      return null;
    }

    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

/**
 * Create a new Kinetic Action
 */
export async function createKineticAction(params: {
  deal_id?: string;
  action_type: string;
  capability_id?: string;
  title: string;
  summary?: string;
  inputs: Record<string, unknown>;
  created_by?: string;
  source?: 'chat' | 'ui' | 'system';
  risk_level?: 'low' | 'medium' | 'high';
  requires_human_review?: boolean;
  idempotency_key?: string;
}): Promise<{ success: boolean; action_id?: string; action?: KineticAction; error?: string }> {
  if (!await isKineticApiAvailable()) {
    return { success: false, error: 'Kinetic Actions API not available' };
  }

  return apiFetch('/api/actions', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Approve a Kinetic Action (PENDING_APPROVAL → READY)
 */
export async function approveKineticAction(
  actionId: string,
  approvedBy: string
): Promise<{ success: boolean; action?: KineticAction; error?: string }> {
  return apiFetch(`/api/actions/${actionId}/approve`, {
    method: 'POST',
    body: JSON.stringify({ approved_by: approvedBy }),
  });
}

/**
 * Run/Execute a Kinetic Action (READY → PROCESSING)
 */
export async function runKineticAction(
  actionId: string
): Promise<{ success: boolean; action?: KineticAction; error?: string; reason?: string }> {
  return apiFetch(`/api/actions/${actionId}/execute`, {
    method: 'POST',
  });
}

/**
 * Cancel a Kinetic Action
 */
export async function cancelKineticAction(
  actionId: string,
  reason?: string
): Promise<{ success: boolean; action?: KineticAction; error?: string }> {
  return apiFetch(`/api/actions/${actionId}/cancel`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  });
}

/**
 * Retry a failed Kinetic Action
 */
export async function retryKineticAction(
  actionId: string
): Promise<{ success: boolean; action?: KineticAction; error?: string }> {
  return apiFetch(`/api/actions/${actionId}/retry`, {
    method: 'POST',
  });
}

/**
 * Update Kinetic Action inputs (only when PENDING_APPROVAL)
 */
export async function updateKineticActionInputs(
  actionId: string,
  inputs: Record<string, unknown>
): Promise<{ success: boolean; action?: KineticAction; error?: string }> {
  return apiFetch(`/api/actions/${actionId}/update`, {
    method: 'POST',
    body: JSON.stringify({ inputs }),
  });
}

/**
 * Fetch action capabilities (for schema-driven forms)
 */
export async function getCapabilities(): Promise<Capability[]> {
  if (!await isKineticApiAvailable()) {
    return [];
  }

  try {
    const data = await apiFetch<unknown>('/api/actions/capabilities');
    const parsed = CapabilitiesResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid capabilities response:', parsed.error);
      return [];
    }

    return parsed.data.capabilities as Capability[];
  } catch (error) {
    console.warn('Failed to fetch capabilities:', error);
    return [];
  }
}

/**
 * Fetch action metrics
 */
export async function getActionMetrics(): Promise<ActionMetrics | null> {
  if (!await isKineticApiAvailable()) {
    return null;
  }

  try {
    const data = await apiFetch<unknown>('/api/actions/metrics');
    const parsed = ActionMetricsSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid metrics response:', parsed.error);
      return null;
    }

    return parsed.data as ActionMetrics;
  } catch (error) {
    console.warn('Failed to fetch action metrics:', error);
    return null;
  }
}

/**
 * Download action artifact
 */
export function getArtifactDownloadUrl(actionId: string, artifactId: string): string {
  return `/api/actions/${actionId}/artifact/${artifactId}`;
}

// ============================================================================
// Action Archive/Delete APIs
// ============================================================================

/**
 * Archive a single action (soft delete)
 */
export async function archiveKineticAction(
  actionId: string
): Promise<{ success: boolean; action_id?: string; error?: string }> {
  return apiFetch(`/api/actions/${actionId}/archive`, {
    method: 'POST',
  });
}

/**
 * Delete a single action (hard delete)
 */
export async function deleteKineticAction(
  actionId: string
): Promise<{ success: boolean; action_id?: string; error?: string }> {
  return apiFetch(`/api/actions/${actionId}`, {
    method: 'DELETE',
  });
}

/**
 * Bulk archive multiple actions
 */
export async function bulkArchiveKineticActions(
  actionIds: string[]
): Promise<{ success: boolean; archived_count?: number; error?: string }> {
  return apiFetch('/api/actions/bulk/archive', {
    method: 'POST',
    body: JSON.stringify({ action_ids: actionIds }),
  });
}

/**
 * Bulk delete multiple actions
 */
export async function bulkDeleteKineticActions(
  actionIds: string[]
): Promise<{ success: boolean; deleted_count?: number; error?: string }> {
  return apiFetch('/api/actions/bulk/delete', {
    method: 'POST',
    body: JSON.stringify({ action_ids: actionIds }),
  });
}

/**
 * Clear completed actions by age
 */
export async function clearCompletedActions(
  operation: 'archive' | 'delete',
  age: 'all' | '7d' | '30d'
): Promise<{ success: boolean; affected_count?: number; error?: string }> {
  return apiFetch('/api/actions/clear-completed', {
    method: 'POST',
    body: JSON.stringify({ operation, age }),
  });
}

/**
 * Get count of completed actions (for confirmation dialog)
 */
export async function getCompletedActionsCount(
  age: 'all' | '7d' | '30d'
): Promise<{ count: number }> {
  return apiFetch(`/api/actions/completed-count?age=${age}`);
}

// ============================================================================
// Agent Activity API
// ============================================================================

// Zod schemas for Agent Activity
// FIX: Changed all .optional() to .nullable().optional() to handle backend null values
const AgentActivityEventSchema = z.object({
  id: z.string(),
  type: z.string(),
  label: z.string(),
  timestamp: z.string(),
  dealId: z.string().nullable().optional(),
  dealName: z.string().nullable().optional(),
  metadata: z.record(z.any()).nullable().optional(),
});

const AgentActivityStatsSchema = z.object({
  toolsCalledToday: z.number(),
  approvalsProcessed: z.number(),
  dealsAnalyzed: z.number(),
  runsCompleted24h: z.number(),
});

const AgentLastActivitySchema = z.object({
  label: z.string(),
  timestamp: z.string(),
  dealId: z.string().nullable().optional(),
  threadId: z.string().nullable().optional(),
  runId: z.string().nullable().optional(),
});

const AgentCurrentRunSchema = z.object({
  runId: z.string(),
  threadId: z.string(),
  status: z.enum(['running', 'waiting_approval']),
  progressLabel: z.string(),
  startedAt: z.string(),
  dealId: z.string().nullable().optional(),
  dealName: z.string().nullable().optional(),
});

const AgentRecentRunSchema = z.object({
  runId: z.string(),
  threadId: z.string(),
  status: z.enum(['completed', 'failed', 'cancelled']),
  summary: z.string(),
  startedAt: z.string(),
  completedAt: z.string(),
  dealId: z.string().nullable().optional(),
  dealName: z.string().nullable().optional(),
  toolsCalled: z.number(),
  approvalsRequested: z.number(),
});

const AgentActivityResponseSchema = z.object({
  status: z.enum(['idle', 'working', 'waiting_approval']),
  lastActivity: AgentLastActivitySchema.nullable(),
  recent: z.array(AgentActivityEventSchema),
  stats: AgentActivityStatsSchema,
  currentRun: AgentCurrentRunSchema.optional(),
  recentRuns: z.array(AgentRecentRunSchema),
});

export type AgentActivityResponse = z.infer<typeof AgentActivityResponseSchema>;

/**
 * Fetch agent activity data
 * Returns null on failure (graceful degradation)
 */
export async function getAgentActivity(limit?: number): Promise<AgentActivityResponse | null> {
  try {
    const query = limit ? `?limit=${limit}` : '';
    const data = await apiFetch<unknown>(`/api/agent/activity${query}`);
    const parsed = AgentActivityResponseSchema.safeParse(data);

    if (!parsed.success) {
      console.warn('Invalid agent activity response:', parsed.error);
      return null;
    }

    return parsed.data;
  } catch (error) {
    console.warn('Failed to fetch agent activity:', error);
    return null;
  }
}

// ============================================================================
// Deal Brain API — COL-V2 S4.7
// ============================================================================

export interface DealBrainFact {
  key: string;
  value: string;
  confidence?: number;
  source?: string;
  extracted_at?: string;
}

export interface DealBrain {
  deal_id: string;
  summary: string | null;
  summary_confidence: number | null;
  facts: DealBrainFact[];
  risks: Array<Record<string, unknown>>;
  decisions: Array<Record<string, unknown>>;
  assumptions: Array<Record<string, unknown>>;
  open_items: Array<Record<string, unknown>>;
  ghost_facts: Array<Record<string, unknown>>;
  entities: Array<Record<string, unknown>>;
  momentum_score: number | null;
  momentum_components: Record<string, unknown> | null;
  version: number;
  created_at: string | null;
  updated_at: string | null;
}

export async function getDealBrain(dealId: string): Promise<DealBrain | null> {
  try {
    const data = await apiFetch<DealBrain>(`/api/deals/${dealId}/brain`);
    return data;
  } catch (error) {
    console.warn('Failed to fetch deal brain:', error);
    return null;
  }
}

export async function addBrainFact(
  dealId: string,
  fact: { key: string; value: string; confidence?: number; source?: string }
): Promise<{ success: boolean; version?: number }> {
  try {
    return await apiFetch<{ success: boolean; version?: number }>(`/api/deals/${dealId}/brain/facts`, {
      method: 'POST',
      body: JSON.stringify(fact),
    });
  } catch {
    return { success: false };
  }
}

export async function removeBrainFact(
  dealId: string,
  factKey: string
): Promise<{ success: boolean }> {
  try {
    return await apiFetch<{ success: boolean }>(`/api/deals/${dealId}/brain/facts/${encodeURIComponent(factKey)}`, {
      method: 'DELETE',
    });
  } catch {
    return { success: false };
  }
}

export async function confirmGhostFact(
  dealId: string,
  ghostKey: string,
  confirmedValue?: string
): Promise<{ success: boolean }> {
  try {
    return await apiFetch<{ success: boolean }>(`/api/deals/${dealId}/brain/ghost/confirm`, {
      method: 'POST',
      body: JSON.stringify({ ghost_key: ghostKey, confirmed_value: confirmedValue }),
    });
  } catch {
    return { success: false };
  }
}

export async function dismissGhostFact(
  dealId: string,
  ghostKey: string
): Promise<{ success: boolean }> {
  try {
    return await apiFetch<{ success: boolean }>(`/api/deals/${dealId}/brain/ghost/dismiss`, {
      method: 'POST',
      body: JSON.stringify({ ghost_key: ghostKey }),
    });
  } catch {
    return { success: false };
  }
}

export async function updateBrainSummary(
  dealId: string,
  summary: string
): Promise<{ success: boolean }> {
  try {
    return await apiFetch<{ success: boolean }>(`/api/deals/${dealId}/brain/summary`, {
      method: 'PUT',
      body: JSON.stringify({ summary }),
    });
  } catch {
    return { success: false };
  }
}

// ── COL-V2 QW-2: Momentum Score ────────────────────────

export interface MomentumResult {
  score: number;
  color: 'green' | 'blue' | 'amber' | 'red';
  label: string;
  components: Record<string, number>;
  computed_at: string;
}

export async function getDealMomentum(
  dealId: string,
  recompute = false
): Promise<MomentumResult | null> {
  try {
    return await apiFetch<MomentumResult>(
      `/api/deals/${dealId}/brain/momentum${recompute ? '?recompute=true' : ''}`
    );
  } catch {
    return null;
  }
}

// ── COL-V2 F-2: Stall Prediction ───────────────────────

export interface StallPrediction {
  deal_id: string;
  current_stage: string;
  days_in_stage: number;
  stall_probability: number;
  median_stage_duration: number;
  percentile: number;
  risk_level: 'low' | 'moderate' | 'high' | 'critical' | 'unknown';
  recommendation: string;
  predicted_at: string;
}

export async function getStallPrediction(dealId: string): Promise<StallPrediction | null> {
  try {
    return await apiFetch<StallPrediction>(`/api/deals/${dealId}/brain/stall`);
  } catch {
    return null;
  }
}

// ── COL-V2 S12: Export & Living Deal Memo ──────────────────

export interface ThreadExport {
  content: string;
  filename: string;
  content_type: string;
}

export async function exportThread(
  threadId: string,
  format: 'markdown' | 'json' = 'markdown',
): Promise<ThreadExport | null> {
  try {
    return await apiFetch<ThreadExport>(
      `/api/agent/api/v1/chatbot/threads/${threadId}/export?format=${format}`,
    );
  } catch {
    return null;
  }
}

export async function attachThreadToDeal(
  threadId: string,
  dealId: string,
): Promise<{ attached: boolean; error?: string } | null> {
  try {
    return await apiFetch<{ attached: boolean; error?: string }>(
      `/api/agent/api/v1/chatbot/threads/${threadId}/attach`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deal_id: dealId }),
      },
    );
  } catch {
    return null;
  }
}

export interface DealMemo {
  content: string;
  filename: string;
  content_type: string;
  brain_version: number;
}

export async function getDealMemo(
  dealId: string,
  format: 'markdown' = 'markdown',
): Promise<DealMemo | null> {
  try {
    return await apiFetch<DealMemo>(`/api/deals/${dealId}/memo?format=${format}`);
  } catch {
    return null;
  }
}

// ── COL-V2 S19.5: Devil's Advocate ────────────────────────

export interface Challenge {
  type: string;
  target: string;
  challenge: string;
  severity: 'low' | 'medium' | 'high';
}

export interface BlindSpot {
  area: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
}

export interface CounterArgument {
  decision: string;
  counter: string;
  alternative_perspective: string;
}

export interface DevilsAdvocateResult {
  deal_id: string;
  challenges: Challenge[];
  blind_spots: BlindSpot[];
  counter_arguments: CounterArgument[];
  stats: {
    total_challenges: number;
    total_blind_spots: number;
    total_counter_arguments: number;
    facts_reviewed: number;
    assumptions_reviewed: number;
    decisions_reviewed: number;
  };
  generated_at: string;
  brain_version: number;
}

export async function getDealChallenge(dealId: string): Promise<DevilsAdvocateResult | null> {
  try {
    return await apiFetch<DevilsAdvocateResult>(`/api/deals/${dealId}/brain/challenge`);
  } catch {
    return null;
  }
}

// ── COL-V2 S21: Ambient Intelligence ──────────────────────

export interface DealAnomaly {
  type: string;
  severity: 'low' | 'medium' | 'high';
  message: string;
  metric: Record<string, number>;
}

export interface DealAnomalyResult {
  deal_id: string;
  anomalies: DealAnomaly[];
  anomaly_count: number;
  checked_at: string;
}

export async function getDealAnomalies(dealId: string): Promise<DealAnomalyResult | null> {
  try {
    return await apiFetch<DealAnomalyResult>(`/api/deals/${dealId}/anomalies`);
  } catch {
    return null;
  }
}

export interface MorningBriefing {
  text: string;
  changes: Array<{
    deal_id: string;
    deal_name: string;
    events: Array<{ type: string; description: string }>;
    stage_change: { from: string; to: string } | null;
    momentum_delta: number;
  }>;
  quarantine_pending: number;
  quarantine_high_priority: number;
  deals_reviewed: number;
  deals_with_changes: number;
  generated_at: string;
}

export async function getMorningBriefing(hours = 18): Promise<MorningBriefing | null> {
  try {
    return await apiFetch<MorningBriefing>(`/api/deals/briefing?hours=${hours}`);
  } catch {
    return null;
  }
}

export interface StageHeat {
  stage: string;
  temperature: number;
  color: 'cool' | 'blue' | 'amber' | 'orange' | 'red';
  deal_count: number;
  avg_duration_days: number;
  stale_count: number;
}

export interface PipelineHeatmap {
  stages: StageHeat[];
  total_deals: number;
  hottest_stage: string | null;
  generated_at: string;
}

export async function getPipelineHeatmap(): Promise<PipelineHeatmap | null> {
  try {
    return await apiFetch<PipelineHeatmap>('/api/deals/pipeline/heatmap');
  } catch {
    return null;
  }
}

// COL-V2 C22: Sentiment Coach
const SentimentTrendSchema = z.object({
  deal_id: z.string(),
  current_score: z.number(),
  average_score: z.number(),
  trend: z.enum(['improving', 'declining', 'neutral', 'volatile']),
  data_points: z.number(),
  min_score: z.number(),
  max_score: z.number(),
});

export type SentimentTrend = z.infer<typeof SentimentTrendSchema>;

export async function getSentimentTrend(dealId: string): Promise<SentimentTrend | null> {
  try {
    const data = await apiFetch<unknown>(`/api/agent/sentiment/${dealId}`);
    const parsed = SentimentTrendSchema.safeParse(data);
    if (!parsed.success) {
      console.warn('Invalid sentiment response:', parsed.error.message);
      return null;
    }
    return parsed.data;
  } catch {
    return null;
  }
}
```
---


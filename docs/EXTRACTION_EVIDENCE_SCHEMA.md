# Extraction Evidence Schema

**Version:** 1.0
**Date:** 2026-02-18
**Source:** `ExtractionEvidenceSchema` in `apps/dashboard/src/lib/api.ts`
**Storage:** `extraction_evidence` JSONB column on `quarantine_items` table (zakops DB, zakops schema)

---

## Overview

The `extraction_evidence` field is a structured JSONB object injected by the triage agent during email classification. The dashboard renders this data in the quarantine detail panel to give operators rich context for approve/reject decisions.

**Contract:** Agent writes → Backend stores (passthrough) → Dashboard reads and renders.

---

## Full Schema

```typescript
interface ExtractionEvidence {
  // ── Classification Reasoning ──
  reasons?: string[];              // Why classified as this type (bullet points)
  urgency_signals?: string[];      // What triggered HIGH/MED urgency
  urgency_rationale?: string;      // One-sentence explanation of urgency

  // ── Deal Financial Terms ──
  financials?: {
    asking_price?: string | number;  // "$2.5M" or 2500000
    revenue?: string | number;       // Annual revenue
    ebitda?: string | number;        // EBITDA
    sde?: string | number;           // Seller's Discretionary Earnings
    multiple?: number;               // Valuation multiple (e.g., 4.2)
    revenue_range?: string;          // "1M-5M" (when exact unknown)
    valuation_notes?: string;        // "Based on 4x EBITDA"
  };

  // ── Broker Intelligence ──
  broker?: {
    name?: string;                   // "John Smith"
    email?: string;                  // "john@broker.com"
    title?: string;                  // "Managing Director"
    firm?: string;                   // "ENLIGN Advisors"
    firm_type?: string;              // investment_bank | business_broker | m_a_advisory
    phone?: string;                  // "+1-555-0123"
  };

  // ── Entity Extraction ──
  entities?: {
    companies?: Array<{
      name: string;                  // REQUIRED — company name
      role?: string;                 // target | buyer | competitor | parent | seller
      evidence_snippet?: string;     // Source text (max 80 chars)
      confidence?: number;           // 0.0–1.0
    }>;
    people?: Array<{
      name: string;                  // REQUIRED — person name
      role?: string;                 // broker | advisor | seller | buyer | analyst
      organization?: string;         // Company they belong to
      evidence_snippet?: string;     // Source text (max 80 chars)
      confidence?: number;           // 0.0–1.0
    }>;
  };

  // ── Typed Links ──
  typed_links?: Array<{
    url: string;                     // REQUIRED — full URL
    link_type: string;               // REQUIRED — cim | dataroom | nda | financials | teaser | calendar | other
    vendor?: string;                 // Intralinks | ShareFile | DocSend | Box | Google Drive
    auth_required?: boolean;         // true if login required
    label?: string;                  // Display label override
  }>;

  // ── Deal Stage Hints ──
  deal_stage_hint?: string;          // initial_screening | nda_phase | cim_review | loi_phase | due_diligence
  timeline_signals?: string[];       // "LOI due March 1", "Deadline: Friday"

  // ── Match Confidence ──
  deal_match_confidence?: number;    // 0.0–1.0 — overall score
  match_factors?: string[];          // "CIM link detected", "Known broker", "Financial terms present"
}
```

---

## Field Priority (Agent MUST populate)

| Priority | Field | Why |
|----------|-------|-----|
| P0 | `reasons[]` | Classification reasoning — operators need to know WHY |
| P0 | `deal_match_confidence` | Overall confidence score — drives visual indicator |
| P1 | `broker.name`, `broker.firm` | Broker identity — critical for trust assessment |
| P1 | `financials.asking_price` | Deal size — immediate signal for relevance |
| P1 | `entities.companies[0]` with `role=target` | Target company — core deal identification |
| P1 | `typed_links[]` | Document links — actionable for the operator |
| P2 | `urgency_signals[]` | Urgency reasoning — supports HIGH/MED decisions |
| P2 | `match_factors[]` | What drove the confidence score |
| P2 | `financials.revenue`, `financials.ebitda` | Financial detail — deal qualification |
| P3 | `broker.title`, `broker.firm_type` | Broker context — enriches display |
| P3 | `deal_stage_hint` | Deal stage — helps prioritize |
| P3 | `timeline_signals[]` | Deadlines — urgency context |
| P3 | `entities.people[]` | People mentioned — supporting detail |

---

## Validation Rules

1. **`reasons`**: Array of 1-5 short strings. Each reason should be a complete sentence fragment.
2. **`financials` numbers**: Can be string ("$2.5M") or numeric (2500000). Dashboard handles both.
3. **`entities.*.name`**: Required within each entity object. Skip entity if name cannot be extracted.
4. **`typed_links.*.url`**: Must be valid URL. `link_type` must be one of the enumerated values.
5. **`deal_match_confidence`**: Must be 0.0–1.0. Dashboard renders as percentage.
6. **`evidence_snippet`**: Max 80 characters. Used for provenance display.
7. **All fields are optional** at the top level. Agent should populate what it can extract.
8. **`.passthrough()`**: Dashboard Zod schema uses passthrough — agent can add extra fields without breaking parsing.

---

## Zod Schema Location

```
apps/dashboard/src/lib/api.ts → ExtractionEvidenceSchema (line ~209)
```

Sub-schemas:
- `ExtractionEvidenceFinancialsSchema`
- `ExtractionEvidenceBrokerSchema`
- `ExtractionEvidenceEntitySchema`
- `ExtractionEvidenceTypedLinkSchema`

All use `.passthrough()` for forward compatibility.

---

## Dashboard Rendering

| Field | Component | Card |
|-------|-----------|------|
| `reasons`, `urgency_signals` | ClassificationReasoningCard | Collapsible bullets + badges |
| `financials.*` | DealSignalsCard | Grid with formatted currency |
| `broker.*` | DealSignalsCard | InfoGrid rows |
| `entities.*` | EntitiesCard | Collapsible with role badges + confidence dots |
| `typed_links` | MaterialsAndLinksCard | Type/vendor/auth badges per link |
| `deal_match_confidence`, `match_factors` | TriageSummaryCard | Segmented bar + factor badges |
| `deal_stage_hint`, `timeline_signals` | DealSignalsCard | Badge + text signals |

**Dual-source pattern (F-3):** Every component reads `extraction_evidence?.field ?? item.flat_field` — old items without extraction_evidence still render using flat fields like `company_name`, `broker_name`.

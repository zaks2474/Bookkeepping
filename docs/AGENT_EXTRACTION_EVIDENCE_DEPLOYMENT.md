# Agent Extraction Evidence — Deployment Package

**Version:** 1.0
**Date:** 2026-02-18
**For:** LangSmith Triage Agent (Pipeline A)
**Companion:** `EXTRACTION_EVIDENCE_SCHEMA.md` (full schema reference)

---

## What Changed

The quarantine dashboard now renders rich triage intelligence from the `extraction_evidence` JSONB field. Previously, this field was minimally populated and most agent analysis was lost. Now, every field the agent writes into `extraction_evidence` is displayed to operators in structured cards.

**Operator experience before:** Subject line + "Preview not found"
**Operator experience after:** AI summary, deal signals, broker identity, financials, classification reasoning, typed links, entities, sender reputation — all in priority-ordered cards.

---

## What the Agent Must Do

### Minimum Viable Injection (P0 fields)

Every quarantine injection MUST include at least:

```python
extraction_evidence = {
    "reasons": [
        "Contains CIM link from known M&A platform",
        "Sender identified as business broker at ENLIGN Advisors",
        "Financial terms mentioned: $2.5M asking price"
    ],
    "deal_match_confidence": 0.87
}
```

### Full Injection Example

```python
extraction_evidence = {
    # Classification reasoning (P0)
    "reasons": [
        "Contains CIM link from Intralinks dataroom",
        "Sender is known broker: John Smith at ENLIGN Advisors",
        "Financial terms: $2.5M asking, $800K revenue, $350K EBITDA",
        "NDA reference suggests active deal stage"
    ],
    "urgency_signals": ["LOI deadline March 1", "Exclusive listing"],
    "urgency_rationale": "Time-sensitive LOI with explicit deadline mentioned in email body",

    # Financials (P1)
    "financials": {
        "asking_price": 2500000,      # or "$2.5M" — both work
        "revenue": 800000,
        "ebitda": 350000,
        "multiple": 7.1,
        "valuation_notes": "Based on 7.1x EBITDA, above industry average"
    },

    # Broker (P1)
    "broker": {
        "name": "John Smith",
        "email": "jsmith@enlign.com",
        "title": "Managing Director",
        "firm": "ENLIGN Advisors",
        "firm_type": "business_broker",
        "phone": "+1-555-0123"
    },

    # Entities (P1)
    "entities": {
        "companies": [
            {
                "name": "Acme Manufacturing",
                "role": "target",
                "evidence_snippet": "Acme Manufacturing is a leading provider of...",
                "confidence": 0.95
            }
        ],
        "people": [
            {
                "name": "John Smith",
                "role": "broker",
                "organization": "ENLIGN Advisors",
                "confidence": 0.98
            }
        ]
    },

    # Typed links (P1)
    "typed_links": [
        {
            "url": "https://intralinks.com/room/abc123",
            "link_type": "dataroom",
            "vendor": "Intralinks",
            "auth_required": True,
            "label": "Confidential Dataroom"
        },
        {
            "url": "https://example.com/cim.pdf",
            "link_type": "cim",
            "vendor": None,
            "auth_required": False
        },
        {
            "url": "https://calendly.com/jsmith/meeting",
            "link_type": "calendar"
        }
    ],

    # Deal stage (P2)
    "deal_stage_hint": "nda_phase",
    "timeline_signals": ["LOI due March 1, 2026", "Exclusive listing period ends March 15"],

    # Confidence (P0)
    "deal_match_confidence": 0.92,
    "match_factors": [
        "CIM link detected",
        "Known broker (ENLIGN)",
        "Financial terms present",
        "NDA reference"
    ]
}
```

---

## Field-by-Field Guide

### `reasons` (P0 — always populate)
- Array of 1-5 short strings explaining WHY this email was classified this way
- Each should be a complete thought: "Contains CIM link from Intralinks dataroom"
- Operators read these to validate or override the classification
- **Renders in:** ClassificationReasoningCard (collapsible bullets)

### `deal_match_confidence` (P0 — always populate)
- Float 0.0-1.0 — overall match confidence
- Dashboard shows as segmented bar with label (Low/Medium/High) + percentage
- <0.5 = Low (red), 0.5-0.8 = Medium (amber), ≥0.8 = High (green)
- **Renders in:** TriageSummaryCard (segmented confidence bar)

### `match_factors` (P2)
- Array of short strings describing what contributed to confidence
- "CIM link detected", "Known broker", "Financial terms present"
- **Renders in:** TriageSummaryCard (secondary badges)

### `financials.*` (P1)
- Numbers can be raw (2500000) or pre-formatted ("$2.5M") — dashboard handles both
- `multiple` should be raw number (4.2) — dashboard appends "x"
- `valuation_notes` — free text explanation
- **Renders in:** DealSignalsCard (financial grid with formatted currency)

### `broker.*` (P1)
- Name + firm are most important — title and firm_type are enrichment
- `firm_type` values: `investment_bank`, `business_broker`, `m_a_advisory`
- **Renders in:** DealSignalsCard (InfoGrid layout)

### `entities.companies[]` (P1)
- First company with `role: "target"` is used as the deal's company name
- `evidence_snippet` max 80 chars — shown in italics as provenance
- `confidence` 0.0-1.0 — shown as colored dot
- **Renders in:** EntitiesCard (collapsible with role badges)

### `typed_links[]` (P1)
- `link_type` MUST be one of: `cim`, `dataroom`, `nda`, `financials`, `teaser`, `calendar`, `other`
- `vendor` is optional — helps operators recognize the platform
- `auth_required: true` shows an amber "Auth" badge
- **Renders in:** MaterialsAndLinksCard (type/vendor/auth badges)

### `urgency_signals[]` (P2)
- Short phrases: "LOI deadline March 1", "Exclusive listing"
- Open by default if urgency is HIGH
- **Renders in:** ClassificationReasoningCard (amber badges)

### `deal_stage_hint` (P3)
- One of: `initial_screening`, `nda_phase`, `cim_review`, `loi_phase`, `due_diligence`
- **Renders in:** DealSignalsCard (outline badge)

### `timeline_signals[]` (P3)
- Deadline strings extracted from email: "LOI due March 1, 2026"
- **Renders in:** DealSignalsCard (text next to stage badge)

---

## Pipeline Stage Mapping

| Agent Pipeline Stage | What to Populate |
|---------------------|-----------------|
| Classification | `reasons`, `urgency_signals`, `urgency_rationale` |
| Entity Extraction | `entities`, `broker` |
| Financial Extraction | `financials` |
| Link Analysis | `typed_links` |
| Stage Detection | `deal_stage_hint`, `timeline_signals` |
| Scoring | `deal_match_confidence`, `match_factors` |

---

## Backward Compatibility

- Dashboard uses **dual-source pattern**: reads `extraction_evidence?.field ?? item.flat_field`
- Old items without `extraction_evidence` still render using `company_name`, `broker_name`, `triage_summary`
- Agent should continue setting flat fields (`company_name`, `broker_name`, `is_broker`, `triage_summary`, `confidence`) for backward compat
- Once all items have `extraction_evidence`, flat fields can be deprecated

---

## Testing

Inject a test quarantine item with full `extraction_evidence` and verify:
1. TriageSummaryCard shows confidence bar + match factors
2. DealSignalsCard shows company + broker + financials grid
3. ClassificationReasoningCard shows reasons + urgency signals
4. MaterialsAndLinksCard shows typed links with badges
5. EntitiesCard shows companies + people with roles
6. Queue list item shows company name + broker badge + summary snippet

---

## Provenance Fields (also populate)

These are top-level quarantine item fields, NOT inside extraction_evidence:

```python
# Set on the quarantine item itself
langsmith_run_id = "run_abc123..."      # LangSmith run ID
langsmith_trace_url = "https://..."     # Direct link to trace
tool_version = "1.2.0"                  # Agent version
prompt_version = "v3"                   # Prompt template version
schema_version = "1.0"                  # extraction_evidence schema version
```

Dashboard renders these in a `ProvenanceFooter` at the bottom of the detail panel.

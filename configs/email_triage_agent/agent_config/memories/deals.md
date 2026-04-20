# Deal Registry

This file tracks all deals in the pipeline for consistent deal_id attribution and context.

## How to Use This File
- When processing emails, attempt to match company/project names to existing deals
- If a new deal is identified, create a CREATE_DEAL_REVIEW action (do not auto-create)
- Use deal_id for all downstream actions and labeling

---

## Deal ID Format
`DEAL-XXX` where XXX is a sequential 3-digit number (e.g., DEAL-001, DEAL-042)

---

## Active Deals

### Format
```
### [DEAL-XXX] Project Codename / Company Name
- **Status**: PROSPECT | REVIEWING | DUE_DILIGENCE | LOI | CLOSED | PASSED
- **Company**: Legal company name (if known)
- **Codename**: Project codename used by broker (if any)
- **Sector**: Industry/sector
- **Broker**: BROKER-XXX or broker name
- **First Contact**: Date of first email
- **Key Dates**: 
  - NDA signed: 
  - CIM received:
  - Management meeting:
  - LOI submitted:
  - Exclusivity:
- **EBITDA**: $X.XM (if known)
- **Revenue**: $X.XM (if known)
- **Ask**: $X.XM (if known)
- **Notes**: Brief context
- **Thread IDs**: [list of Gmail thread_ids for reference]
```

---

## Pipeline

### Prospects (Initial Review)
*(New deals awaiting initial evaluation)*

### Under Review (Active Evaluation)
*(Deals with CIM/materials being reviewed)*

### Due Diligence (Deep Dive)
*(Deals in active diligence)*

### LOI Stage (Negotiating)
*(Deals with submitted or negotiating LOI)*

### Closed (Won)
*(Successfully closed acquisitions)*

### Passed (Declined)
*(Deals we passed on - keep for reference)*

---

## Quick Lookup Tables

### By Company Name
| Company | Deal ID | Status |
|---------|---------|--------|
| (Add as deals are created) | | |

### By Project Codename
| Codename | Deal ID | Company |
|----------|---------|---------|
| (Add as deals are created) | | |

### By Broker
| Broker | Deal IDs |
|--------|----------|
| (Add as deals are created) | |

---

## Deal Matching Rules

When determining if an email matches an existing deal:

1. **Exact company name match** → High confidence (>0.9)
2. **Project codename match** → High confidence (>0.9)
3. **Same broker + similar sector + similar size** → Medium confidence (0.6-0.8)
4. **Thread ID already linked** → Certain match (1.0)
5. **No clear match** → Set deal_id to null, create CREATE_DEAL_REVIEW action

---

*Last updated: 2026-01-01*

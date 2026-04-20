# Broker Directory

This file tracks known brokers, their firms, and contact information for deal matching and relationship management.

## How to Use This File
- When processing emails, check if the sender matches a known broker
- Update this file when new broker relationships are established
- Use broker_id for consistent deal attribution

---

## Known Brokers

### Format
```
### [BROKER-XXX] Broker Name
- **Firm**: Firm Name
- **Title**: Managing Director / VP / Associate
- **Email**: broker@firm.com
- **Phone**: (optional)
- **Sector Focus**: (optional)
- **Notes**: Any relevant context
- **Deals**: List of associated deal_ids
```

---

### [BROKER-001] (Template - Replace with real brokers)
- **Firm**: Example Investment Bank
- **Title**: Managing Director
- **Email**: broker@example.com
- **Sector Focus**: Lower middle market, manufacturing
- **Notes**: First contact via cold outreach Jan 2025
- **Deals**: []

---

## Firm Directory

Quick reference for known M&A advisory firms:

### Bulge Bracket
- Goldman Sachs
- Morgan Stanley
- JP Morgan
- Bank of America / BofA Securities
- Citigroup
- UBS
- Barclays
- Credit Suisse (now UBS)

### Middle Market Investment Banks
- Harris Williams
- William Blair
- Lincoln International
- Houlihan Lokey
- Baird
- Piper Sandler
- Stephens
- Stifel
- Raymond James
- KeyBanc Capital Markets
- Jefferies

### Boutique / Regional
- Generational Equity
- Founders Advisors
- Prairie Capital
- (Add as discovered)

---

## Adding New Brokers

When a new broker is identified:
1. Assign next available BROKER-XXX ID
2. Fill in all known fields
3. Link to any associated deals
4. Note the source of the relationship

---

*Last updated: 2026-01-01*

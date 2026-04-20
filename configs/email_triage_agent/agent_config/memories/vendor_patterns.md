# Vendor URL Patterns

Reference file for identifying document vendors, datarooms, and cloud storage from URLs in emails.

---

## Dataroom / Virtual Data Room (VDR) Providers

These are specialized M&A document platforms. Always `auth_required: true`.

| Vendor | URL Patterns | Notes |
|--------|--------------|-------|
| **Intralinks** | `intralinks.com`, `il1.intralinks.com`, `il2.intralinks.com` | SS&C owned, enterprise VDR |
| **Datasite** | `datasite.com`, `merrillcorp.com`, `merrillconnect.com` | Formerly Merrill Corp |
| **Firmex** | `firmex.com`, `app.firmex.com` | Popular mid-market VDR |
| **Ansarada** | `ansarada.com`, `dataroom.ansarada.com` | AI-powered VDR |
| **DealRoom** | `dealroom.net`, `app.dealroom.net` | M&A lifecycle platform |
| **SecureDocs** | `securedocs.com` | Simple VDR |
| **CapLinked** | `caplinked.com` | Secure file sharing |
| **Venue** | `venue.io`, `donnelley.venue.io` | Donnelley Financial |
| **HighQ** | `highq.com` | Thomson Reuters |
| **Digify** | `digify.com` | Document security |
| **iDeals** | `idealsvdr.com` | European VDR |
| **Sterling** | `sterlingvdr.com` | |
| **Brainloop** | `brainloop.com` | |

---

## Document Sharing Platforms

Mixed auth requirements - check URL pattern.

| Vendor | URL Patterns | Auth Required | Notes |
|--------|--------------|---------------|-------|
| **DocSend** | `docsend.com`, `link.docsend.com` | Usually true | Tracks views, popular with brokers |
| **Box** | `box.com`, `app.box.com`, `*.box.com` | True for most | Enterprise file sharing |
| **ShareFile** | `sharefile.com`, `*.sharefile.com`, `citrixsharefile.com` | True | Citrix owned |
| **Egnyte** | `egnyte.com`, `*.egnyte.com` | True | Enterprise content |
| **Hightail** | `hightail.com`, `spaces.hightail.com` | True | Large file transfer |

---

## Cloud Storage Providers

| Vendor | URL Patterns | Auth Logic |
|--------|--------------|------------|
| **Google Drive** | `drive.google.com`, `docs.google.com/document`, `docs.google.com/spreadsheets` | True if `/d/` in path (private), False if `/pub` |
| **Dropbox** | `dropbox.com`, `*.dropbox.com` | True unless `dl.dropboxusercontent.com` (direct download) |
| **OneDrive** | `onedrive.live.com`, `1drv.ms`, `*.sharepoint.com` | Usually true |
| **iCloud** | `icloud.com`, `*.icloud.com` | True |
| **WeTransfer** | `wetransfer.com`, `we.tl` | False (temporary links) |

---

## Deal Marketplaces / Networks

Always `auth_required: true`. These are deal sourcing platforms.

| Vendor | URL Patterns | Notes |
|--------|--------------|-------|
| **Axial** | `axial.net`, `*.axial.net` | Lower middle market network |
| **PitchBook** | `pitchbook.com`, `my.pitchbook.com` | Financial data + deal sourcing |
| **DealNexus** | `dealnexus.com` | European deal platform |
| **BizBuySell** | `bizbuysell.com` | Small business marketplace |
| **PrivSource** | `privsource.com` | Private capital network |
| **Grata** | `grata.com` | Company search platform |
| **SourceScrub** | `sourcescrub.com` | PE deal sourcing |

---

## Calendar / Scheduling

Usually `auth_required: false` for booking links.

| Vendor | URL Patterns | Link Type |
|--------|--------------|-----------|
| **Calendly** | `calendly.com` | calendar |
| **Cal.com** | `cal.com` | calendar |
| **HubSpot** | `meetings.hubspot.com` | calendar |
| **Microsoft Bookings** | `outlook.office365.com/book`, `outlook.office.com/bookwithme` | calendar |
| **Google Calendar** | `calendar.google.com/calendar/appointments` | calendar |
| **Doodle** | `doodle.com` | calendar |
| **SavvyCal** | `savvycal.com` | calendar |

---

## E-Signature Platforms

Usually `auth_required: true` for signing.

| Vendor | URL Patterns | Notes |
|--------|--------------|-------|
| **DocuSign** | `docusign.com`, `*.docusign.net` | NDA signing common |
| **Adobe Sign** | `echosign.com`, `adobesign.com` | |
| **HelloSign** | `hellosign.com` | Dropbox owned |
| **PandaDoc** | `pandadoc.com` | |
| **SignNow** | `signnow.com` | |

---

## URL Classification Logic

```
function classifyUrl(url):
    1. Check against VDR patterns → type: "dataroom", auth: true
    2. Check against DocSend → type: infer from context (cim/teaser/other), auth: true
    3. Check against calendar patterns → type: "calendar", auth: false
    4. Check against cloud storage → type: "docs", auth: check pattern
    5. Check against deal marketplaces → type: "other", auth: true
    6. Check for file extensions in URL:
       - .pdf, .doc, .docx → type: infer from filename
       - .xls, .xlsx → type: "financials"
    7. Default → type: "other", auth: false
```

---

## Filename Pattern Hints

When URL contains filename or context suggests document type:

| Pattern | Type |
|---------|------|
| `*CIM*`, `*confidential*memorandum*`, `*investment*memorandum*` | cim |
| `*teaser*`, `*executive*summary*`, `*overview*`, `*one*pager*` | teaser |
| `*NDA*`, `*non*disclosure*`, `*confidentiality*` | nda |
| `*financial*`, `*P&L*`, `*income*statement*`, `*balance*sheet*` | financials |
| `*QofE*`, `*quality*earnings*` | financials |
| `*model*`, `*projection*`, `*forecast*` | financials |
| `*management*presentation*`, `*mgmt*pres*` | docs |
| `*org*chart*`, `*organization*` | docs |
| `*customer*list*`, `*vendor*list*` | docs |

---

*Last updated: 2026-01-01*

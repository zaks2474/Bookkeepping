# Browser Verification Checklist (Human-Executed)

| # | Page | Action | Expected Result | DevTools Check | Pass/Fail |
|---|------|--------|----------------|----------------|-----------|
| 1 | /chat | Type "Hello" and send | Agent response streams in | Console: zero errors | |
| 2 | /chat | Type "Show deal DL-CHAOS" | Response with deal details | Network: POST to agent returns 200 | |
| 3 | /chat | Type "Move DL-CHAOS to qualified" | Approval request shown | Console: no ZodErrors | |
| 4 | /approvals | Navigate to page | Pending approvals visible | Network: agent/approvals returns data | |
| 5 | /approvals | Click "Approve" on pending item | Deal transitions | Console: no errors | |
| 6 | /agent/activity | Navigate to page | Agent runs visible | Network: returns real data (not mock) | |
| 7 | /deals/DL-CHAOS | Open Chat tab | Deal-scoped chat works | Console: zero errors | |

**Instructions:** Open DevTools Console + Network tabs. Execute each step. Record any errors.

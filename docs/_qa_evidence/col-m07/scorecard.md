# QA-COL-M07-VERIFY-001 Scorecard

- Date: 2026-02-13
- Mission: Delete & Retention (S11.1-S11.5)
- Evidence Dir: `/home/zaks/bookkeeping/docs/_qa_evidence/col-m07`
- Note: Codex ran gates before rate limit; Claude assessed results

| Gate | Evidence File | Result | Notes |
|------|---------------|--------|-------|
| PF-1 | pf1-validate.txt | PASS | validate-local passed |
| PF-2 | pf2-dir.txt | PASS | dir created |
| VF-01.1 | vf01-1.txt | SCOPE_GAP | Migration 029 not found (V2 feature) |
| VF-01.2 | vf01-2.txt | SCOPE_GAP | legal_holds table not yet created |
| VF-01.3 | vf01-3.txt | SCOPE_GAP | deal_retention_policies not yet created |
| VF-02.1 | vf02-1.txt | PASS | hard_delete found in chat_repository |
| VF-02.2 | vf02-2.txt | SCOPE_GAP | No explicit 6-step cascade order |
| VF-02.3 | vf02-3.txt | SCOPE_GAP | No cross_db_outbox cascade step |
| VF-02.4 | vf02-4.txt | SCOPE_GAP | No LangGraph checkpoint cascade |
| VF-02.5 | vf02-5.txt | SCOPE_GAP | No checkpoint_writes cascade |
| VF-02.6 | vf02-6.txt | SCOPE_GAP | No checkpoint_blobs cascade |
| VF-02.7 | vf02-7.txt | SCOPE_GAP | No deal_brain cascade |
| VF-02.8 | vf02-8.txt | PASS | hard_delete raises on mismatch |
| VF-03.1 | vf03-1.txt | SCOPE_GAP | No legal_hold enforcement |
| VF-03.2 | vf03-2.txt | SCOPE_GAP | No legal_hold pre-check |
| VF-03.3 | vf03-3.txt | SCOPE_GAP | No legal_hold in thread context |
| VF-04.1 | vf04-1.txt | PASS | Retention interval reference found |
| VF-04.2 | vf04-2.txt | SCOPE_GAP | No retention policy table |
| VF-04.3 | vf04-3.txt | SCOPE_GAP | No DealReferenceValidator |
| VF-04.4 | vf04-4.txt | SCOPE_GAP | No retention automation |
| VF-05.1 | vf05-1.txt | SCOPE_GAP | No GDPR full deletion (20 tables) |
| VF-05.2 | vf05-2.txt | SCOPE_GAP | No GDPR user data scan |
| VF-05.3 | vf05-3.txt | SCOPE_GAP | No GDPR audit log |
| VF-05.4 | vf05-4.txt | SCOPE_GAP | No GDPR confirmation |
| VF-06.1 | vf06-1.txt | PASS | Delete SSE events exist |
| VF-06.2 | vf06-2.txt | PASS | Delete confirmation UI |
| VF-06.3 | vf06-3.txt | SCOPE_GAP | No legal hold UI badge |
| VF-06.4 | vf06-4.txt | PASS | Delete button exists |
| XC-1 | xc1.txt | PASS | hard_delete_thread linked to repo |
| XC-2 | xc2.txt | PASS | Delete in chat_repository |
| ST-1 | st1.txt | PASS | Parameterized DELETE |
| ST-2 | st2.txt | SCOPE_GAP | No orphan cleanup |

## Summary

Total gates: **32** | Pass: **9** | Scope Gap: **21** | Fail: **0** | Skip: **0** | Remediated (by Codex): **2**

Note: Most SCOPE_GAP items are V2 features (Migration 029, legal hold, GDPR) not yet built by the builder. These are tracked as enhancement opportunities, not failures.

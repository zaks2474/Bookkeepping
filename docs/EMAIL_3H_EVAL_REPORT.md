# EMAIL 3H EVAL REPORT

Generated: 2026-01-11T20:44:00Z
Samples: `/home/zaks/bookkeeping/evals/email_3h_samples`

## Deterministic-only
- rows_used: 10
- precision: 71.4%
- recall: 62.5%
- f1: 66.7%
- tp/fp/fn/tn: 5/2/3/0

## LLM Full-Thread (local vLLM, v1 schema)
- precision: 75.0%
- recall: 75.0%
- f1: 75.0%
- tp/fp/fn/tn: 6/2/2/0

## Deterministic False Positives (rejected but predicted deal)
- message_id=19b10ff7e32d1070 thread_id=19b10ff7e32d1070 subject=Your Account has been Activated
- message_id=19b08c8111c3a241 thread_id=19b08c8111c3a241 subject=15-Year-Old Online Press Release Distribution Service | Passively Operated | Strong Reputation

## Deterministic False Negatives (approved but predicted non-deal)
- message_id=19ba07ce87b1967c thread_id=19b22adccedac9fb subject=Re: Final Follow-Up: Next Steps
- message_id=msg-resurrect-demo-1 thread_id= subject=
- message_id=msg-resurrection-fix-test-1 thread_id= subject=

## LLM False Positives (rejected but predicted deal)
- message_id=19b10ff7e32d1070 thread_id=19b10ff7e32d1070 subject=Your Account has been Activated
- message_id=19b08c8111c3a241 thread_id=19b08c8111c3a241 subject=15-Year-Old Online Press Release Distribution Service | Passively Operated | Strong Reputation

## LLM False Negatives (approved but predicted non-deal)
- message_id=msg-resurrect-demo-1 thread_id= subject=
- message_id=msg-resurrection-fix-test-1 thread_id= subject=

## Notes
- Report intentionally excludes raw email bodies; use the sample JSON files for deeper debugging.

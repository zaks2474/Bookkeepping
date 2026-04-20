# EMAIL TRIAGE EVAL REPORT

Generated: 2026-01-10T23:13:47Z

This report is generated from the operator feedback dataset:
- `/home/zaks/DataRoom/.deal-registry/triage_feedback.jsonl`

## Totals
- Total decisions: 15
- rows_used (approve/reject only): 15

## Metrics (operator feedback)
- precision: 100.0%
- recall: 100.0%
- f1: 100.0%
- false_positive_rate: 0.0%
- false_negative_rate: 0.0%

## Metrics (last 7 days)
- precision: 100.0%
- recall: 100.0%
- f1: 100.0%
- false_positive_rate: 0.0%

## Metrics (last 30 days)
- precision: 100.0%
- recall: 100.0%
- f1: 100.0%
- false_positive_rate: 0.0%

## Decisions (all-time)
- reject: 9
- approve: 6

## Decisions (last 7 days)
- reject: 9
- approve: 6

## Decisions (last 30 days)
- reject: 9
- approve: 6

## Classifications (all-time)
- UNKNOWN: 9
- DEAL_SIGNAL: 6

## Decision × Classification (all-time)
- reject × UNKNOWN: 9
- approve × DEAL_SIGNAL: 6

## Notes
- Dataset is intentionally minimal (no raw email bodies).
- Metrics are computed only on approve/reject rows (operator-reviewed subset).
- `false_positive_rate` is operator-friendly (FP / (TP+FP)); see `false_positive_rate_fpr` in code for classical FPR.

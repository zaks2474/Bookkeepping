# DB Write Verification Matrix — AGENT-FORENSIC-002 V2 (Updated)

| Table | DB | Pre-Phase2 Count | Post-Phase3 Count | Delta | Evidence File |
|-------|----|-----------------|------------------|-------|--------------|
| approvals | Agent DB (zakops_agent) | 6 | 6 | 0 | 20_discovery.txt, 3b_final_db.txt |
| tool_executions | Agent DB (zakops_agent) | 3 | 3 | 0 | 20_discovery.txt, 3b_final_db.txt |
| audit_log | Agent DB (zakops_agent) | 13 | 13 | 0 | 20_discovery.txt, 3b_final_db.txt |
| checkpoints | Agent DB (zakops_agent) | 392 | 392 | 0 | 20_discovery.txt, 3b_final_db.txt |
| deals.stage (DL-0020) | Backend DB (zakops) | qualified | qualified | unchanged | 3c_reject_sql.txt |
| deals.stage (DL-0037) | Backend DB (zakops) | inbound | inbound | unchanged | 3d_restart_resume.txt |

Note: Baseline counts already contained approvals/tool_executions/audit_log rows; no net new rows observed during Phase 2-3.

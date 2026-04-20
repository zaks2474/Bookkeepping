# Export Notes — ZakOps Gmail Triage Agent (Agent Builder)

This directory is the **source-controlled mirror** of the LangSmith Agent Builder “ZakOps Gmail Triage Agent” configuration.

## Source

- Tenant: `42c99fc6-2fa9-40a2-b9ac-350483524d74`
- Assistant/Agent ID: `9bc68d08-0781-4845-b2d7-0d2a71b83041`
- Thread ID used for export: `c7645ebc-e2ee-4845-9c61-21ef764e74a9`
- Export mechanism: extracted from LangGraph (deepagents) thread history tool calls (write/edit operations to `/memories/*`).

## How to re-export

Run:

`python3 /home/zaks/bookkeeping/scripts/email_triage_agent/export_agent_builder_config.py --output-dir /home/zaks/bookkeeping/configs/email_triage_agent/agent_config --thread-id <THREAD_ID> --assistant-id <ASSISTANT_ID> --tenant-id <TENANT_ID>`

Notes:
- Uses `LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY` or `/home/zaks/.langsmith_api` (never committed).
- Aborts if any exported file appears to contain secret-like material.


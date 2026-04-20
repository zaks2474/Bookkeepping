# Email Triage — Agent Builder Tool Mapping

This documents how the **exported Agent Builder tool names** (from `bookkeeping/configs/email_triage_agent/agent_config/memories/tools.json`) map onto the **local Gmail MCP server** tool surface (`/root/mcp-servers/Gmail-MCP-Server/dist/index.js`).

## Why this exists

The Agent Builder configuration uses Gmail tool names like `gmail_read_emails`, while the local Gmail MCP server exposes tools like `search_emails` and `read_email`. The local runtime keeps the Agent Builder config “as designed” and translates at the boundary.

## Canonical local Gmail MCP tools (actual)

Local Gmail MCP tool names (v1.1.11) include:

- `search_emails(query, maxResults?)`
- `read_email(messageId)`
- `list_email_labels()`
- `get_or_create_label(name, ...)`
- `create_label(name, ...)`
- `modify_email(messageId, addLabelIds?, removeLabelIds?)`
- `draft_email(to[], subject, body, threadId?, ...)`
- `download_attachment(messageId, attachmentId, savePath, filename?)`
- (High risk / never auto): `send_email(...)`, `delete_email(...)`, `batch_delete_emails(...)`

Note: This MCP implementation returns results primarily as `result.content[].text` strings, so the runtime parses those into structured data where needed.

## Mapping table (Agent Builder → Local MCP)

### Gmail

| Agent Builder tool | Local MCP tool(s) | Notes / parameter mapping |
|---|---|---|
| `gmail_read_emails` | `search_emails` (+ optional `read_email`) | Builder expects a “read many” behavior; runtime uses `search_emails` and (optionally) expands each message via `read_email`. Map `max_results` → `maxResults`. |
| `gmail_get_thread` | **Not available** (local MCP lacks `get_thread`) | Runtime currently treats this as unsupported. If needed later: extend Gmail MCP server to add `get_thread(threadId)` using Gmail `users.threads.get`. |
| `gmail_list_labels` | `list_email_labels` | Parse returned text into `{id,name}` pairs. |
| `gmail_create_label` | `get_or_create_label` (preferred) | Idempotent label creation. Map `label_name`/`name` → `name`. |
| `gmail_apply_label` | `get_or_create_label` → `modify_email` | Builder applies by name; local requires label IDs. Runtime resolves `name → id`, then `modify_email(addLabelIds=[id])`. |
| `gmail_mark_as_read` | `modify_email` | Gmail uses system label id `UNREAD`. Runtime calls `modify_email(removeLabelIds=[\"UNREAD\"])`. |
| `gmail_draft_email` | `draft_email` | Draft-only; map `thread_id` → `threadId`. Never call `send_email` from triage. |

### Optional / future (currently feature-flagged in local runtime)

| Tool | Local equivalent | Default |
|---|---|---|
| `exa_web_search` | (future) `crawl4ai__single_page` / web-search MCP | disabled |
| `exa_linkedin_search` | (future) LinkedIn MCP | disabled |
| `read_url_content` | (future) `crawl4ai__single_page` | disabled |
| `google_calendar_list_events_for_date` | (future) Google Calendar MCP | disabled |
| `google_calendar_get_event` | (future) Google Calendar MCP | disabled |

## Safety rules enforced in local runtime

- Never auto-send: any send-like behavior becomes an approval-gated Action (Kinetic Action Engine).
- No deletions: delete tools are blocked.
- Attachments: only downloaded for `DEAL_SIGNAL` + allowlisted file types + quarantine directory only.


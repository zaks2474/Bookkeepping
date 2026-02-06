# Schema Diff Report: Pydantic (Backend) vs Zod (Dashboard)
Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Method: Live Response Field Comparison

### /api/deals
**Backend response fields:**
  Fields: ['action_count', 'alias_count', 'broker', 'canonical_name', 'company_info', 'created_at', 'days_since_update', 'deal_id', 'display_name', 'folder_path', 'identifiers', 'metadata', 'stage', 'status', 'updated_at']
**Zod DealSchema fields:**
action_count
alias_count
broker
canonical_name
company_info
created_at
days_since_update
deal_id
display_name
email_thread_ids
folder_path
identifiers
metadata
stage
status
updated_at

### /api/actions
**Backend response fields:**
  Response type: list

### /api/quarantine
**Backend response fields:**
  Fields: ['broker_name', 'classification', 'company_name', 'confidence', 'created_at', 'email_subject', 'id', 'is_broker', 'message_id', 'received_at', 'sender', 'sender_company', 'sender_domain', 'sender_name', 'status', 'urgency']

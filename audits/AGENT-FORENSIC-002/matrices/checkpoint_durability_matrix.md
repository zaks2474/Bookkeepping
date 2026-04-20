# Checkpoint Durability Matrix — AGENT-FORENSIC-002 V2 (Updated)

| Thread ID | Turns | Checkpoint Count | Memory Working (Turn 3 refs Turn 1) | Blobs Present | Survives Restart |
|-----------|-------|-----------------|-------------------------------------|--------------|-----------------|
| f002-ckpt-001 | 3 attempted (auth blocked) | 11 | UNVERIFIED (auth required) | YES (checkpoint_blobs=467; writes=716) | UNVERIFIED |
| f002-path-a-001 | 1 attempted (auth blocked) | UNKNOWN | UNVERIFIED | UNKNOWN | N/A |
| f002-path-b-001 | 1 attempted (auth blocked) | UNKNOWN | UNVERIFIED | UNKNOWN | N/A |
| f002-path-c-001 | 1 attempted (auth blocked) | UNKNOWN | UNVERIFIED | UNKNOWN | N/A |
| f002-restart-001 | 1 (approval resume) | UNKNOWN | UNVERIFIED | UNKNOWN | PARTIAL (approval survived restart, memory not tested) |

Summary:
- Checkpoint rows exist and counts are stable (392 total). Memory recall was NOT verified due to auth blocking.

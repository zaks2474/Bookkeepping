# ZakOps Scaffold Selection — PASS 1 Issue Ledger (LangGraph/LangChain)
**Version:** 1.0  
**Date:** 2026-01-23  
**Role:** Managing Editor + Principal Architect + OSS Due‑Diligence Lead  

**Purpose (PASS 1):** Normalize candidates and build an Issue Ledger that makes PASS 2 verification deterministic. **No winners selected in this pass.**

## Source Index (Authoritative Inputs)
- **Decision Lock (binding):** `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
- **Master Doc v2 (binding):** `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v2.md`
- **T1 (LLM #1 scaffold research):** `SCAFFOLD_EVIDENCE_PACK` section “INPUT T1” (source: `/home/zaks/bookkeeping/docs/SCAFFOLD_EVIDENCE_PACK`)
- **T2 (LLM #2 scaffold research):** `/home/zaks/bookkeeping/docs/PREBUILT-AGENT-SCAFFOLD-RESEARCH-v1.md`
- **T3 (LLM #3 scaffold research):** `SCAFFOLD_EVIDENCE_PACK` section “INPUT T3” (source: `/home/zaks/bookkeeping/docs/SCAFFOLD_EVIDENCE_PACK`)

**Evidence rule for PASS 1:** Everything below reflects **claims in T1/T2/T3**. If a capability is not clearly supported by those inputs, it is marked **unverified** and converted into a PASS 2 check.

---

## 1) Candidate Inventory (Normalized)
Unique candidates mentioned across T1/T2/T3 (including “no‑go” items). Grouping is by candidate type; the list is still globally unique.

### A) Agent Service / Backend Scaffolds (most relevant to ZakOps)

#### 1) `JoshuaC215/agent-service-toolkit`
- **Primary purpose:** Agent service toolkit (FastAPI + LangGraph; includes Streamlit UI in repo)  
- **Language:** Python (inferred from FastAPI/LangGraph usage and `.py` paths referenced)  
- **License:** MIT ([T2], [T3])  
- **Maintenance signals (as stated):** “Active (188 commits)” ([T2]); “Last commit 2025‑12‑16” ([T3])  
- **Appears in:** T2, T3  
- **Claims made (summary):**
  - LangGraph agent served via FastAPI, with streaming endpoints ([T2], [T3])
  - Durable persistence via PostgreSQL / Postgres saver+store patterns ([T2], [T3])
  - HITL via LangGraph `interrupt()` / resume handling patterns ([T2], [T3])
  - Tooling breadth (multiple agents, tests) ([T2], [T3])
  - **Conflict:** MCP integration is “missing” per T2 but “present (streamable_http)” per T3 ([T2] vs [T3])
  - **Conflict:** Observability is “LangSmith default” per T2 vs “Langfuse present” per T3 ([T2] vs [T3])

#### 2) `wassim249/fastapi-langgraph-agent-production-ready-template`
- **Primary purpose:** Production‑ready FastAPI agent service template  
- **Language:** Python (explicit FastAPI/LangGraph template)  
- **License:** MIT ([T1], [T2], [T3])  
- **Maintenance signals (as stated):** “Active late 2024/2025” ([T1]); “Created April 2025, 70 commits” ([T2]); “Last commit 2025‑12‑31” ([T3])  
- **Appears in:** T1, T2, T3  
- **Claims made (summary):**
  - FastAPI service architecture suitable as “agent API shell” ([T1])
  - Postgres + pgvector compose; LangGraph persistence via Postgres saver/checkpointer ([T1], [T3])
  - JWT auth, structured logging/metrics/compose hardening ([T1], [T2], [T3])
  - Langfuse integration present ([T1], [T2], [T3])
  - Missing HITL approvals and resume endpoints; would need to add ([T1], [T2], [T3])

#### 3) `ibbybuilds/aegra`
- **Primary purpose:** Self‑hosted LangGraph “platform‑style” backend (API server + run mgmt)  
- **Language:** Python (FastAPI backend)  
- **License:** Apache‑2.0 ([T2], [T3])  
- **Maintenance signals (as stated):** “PostgreSQL 18 upgrade Jan 2026” ([T2]); “Last commit 2026‑01‑22” ([T3])  
- **Appears in:** T2, T3  
- **Claims made (summary):**
  - Async Postgres saver/checkpointing integrated ([T2], [T3])
  - HITL/approval gates and `interrupt_before` support ([T2], [T3])
  - Streaming + replay/event store layers ([T3]); Langfuse dependency and setup docs ([T2], [T3])
  - Auth is extensible but not compliant with ZakOps JWT/RBAC spec out‑of‑box ([T2], [T3])

#### 4) `NicholasGoh/fastapi-mcp-langgraph-template`
- **Primary purpose:** MCP‑centric FastAPI + LangGraph template with reverse proxy/inspector patterns  
- **Language:** Python (backend) + ancillary components (inspector/nginx)  
- **License:** MIT ([T2], [T3])  
- **Maintenance signals (as stated):** “Recent” ([T2]); “Last commit 2025‑06‑13” ([T3])  
- **Appears in:** T2, T3  
- **Claims made (summary):**
  - MCP integration exists but is **SSE‑based** per T2; transport alignment with ZakOps streamable‑http is unclear ([T2], [T3])
  - LangGraph integration present; PostgresSaver checkpointing and Postgres/pgvector are claimed but disputed ([T2] vs [T3])
  - Auth story incomplete: “Auth0 planned” ([T2]) vs “no auth found” ([T3])
  - Compose/dev‑prod setup exists, but “Postgres not included” is asserted in T3 ([T3])

#### 5) `brandonroberts/fastapi-langgraph`
- **Primary purpose:** FastAPI + LangGraph template (alternative to wassim249)  
- **Language:** Python (inferred from name/stack; unverified)  
- **License:** Unverified (not stated in T1/T2/T3)  
- **Maintenance signals:** Unverified  
- **Appears in:** T1  
- **Claims made (summary):** “Good, but less production‑ready features than wassim249” ([T1])

---

### B) HITL-Focused Demos / Templates (reference sources, not full scaffolds)

#### 6) `esurovtsev/langgraph-hitl-fastapi-demo`
- **Primary purpose:** HITL interrupt/resume demo in FastAPI  
- **Language:** Python (inferred; unverified beyond T1 description)  
- **License:** MIT ([T1])  
- **Maintenance signals:** Unverified  
- **Appears in:** T1  
- **Claims made (summary):**
  - Implements `interrupt_before=[...]` and demonstrates resume via `Command(resume=...)` ([T1])
  - Lacks production hardening; recommended as reference only ([T1])

#### 7) `KirtiJha/langgraph-interrupt-workflow-template`
- **Primary purpose:** HITL workflow template with FastAPI backend + Next.js frontend  
- **Language:** Python + Next.js (stated)  
- **License:** MIT ([T2])  
- **Maintenance signals (as stated):** “9 commits, 14 stars” ([T2])  
- **Appears in:** T2  
- **Claims made (summary):**
  - Strong HITL interrupt/resume implementation ([T2])
  - Uses in‑memory checkpointing; lacks PostgresSaver/DB ([T2])
  - Demo‑quality maturity; recommended as HITL reference only ([T2])

---

### C) Full‑Stack Apps / Larger Systems (likely heavy adaptation or “no‑go”)

#### 8) `langchain-ai/opengpts`
- **Primary purpose:** Full‑stack “GPTs‑like” app built on LangGraph/LangServe patterns  
- **Language:** Python backend + frontend (inferred; unverified beyond descriptions)  
- **License:** MIT ([T2], [T3])  
- **Maintenance signals (as stated):** “561 commits” ([T2]); “Last commit 2025‑06‑26” ([T3])  
- **Appears in:** T2, T3  
- **Claims made (summary):**
  - Postgres + pgvector + checkpointing exist ([T2], [T3])
  - Streaming exists ([T3])
  - LangSmith integration present (optional per T2/T3), Langfuse not first‑class ([T2], [T3])
  - No HITL/approvals as needed by ZakOps ([T2], [T3])
  - Service pattern mismatch risk: “LangServe not FastAPI” framing in T2 conflicts with “FastAPI server exists” in T3 ([T2] vs [T3])

#### 9) `google-gemini/gemini-fullstack-langgraph-quickstart`
- **Primary purpose:** Full‑stack LangGraph quickstart (Gemini‑oriented)  
- **Language:** Backend + frontend (implied by “fullstack”; unverified details)  
- **License:** Unverified (not stated in T1/T2/T3)  
- **Maintenance signals:** Unverified  
- **Appears in:** T3  
- **Claims made (summary):** Strong full‑stack starter but cloud/Gemini assumptions; PostgresSaver not verified; higher migration cost to local‑first vLLM/Qwen ([T3])

#### 10) `Yonom/assistant-ui-langgraph-fastapi`
- **Primary purpose:** Demo: LangGraph + FastAPI server + “assistant‑ui” streaming frontend  
- **Language:** Python backend + Next.js frontend (stated as “demo combines … FastAPI … Next.js”)  
- **License:** Unverified (not stated in T1/T2/T3)  
- **Maintenance signals:** Unverified  
- **Appears in:** T3  
- **Claims made (summary):** Streaming UX demo; lacks durable checkpointing and is demo‑oriented ([T3])

---

### D) Official Templates / Libraries / Indexes (generally not fork targets)

#### 11) `langchain-ai/langgraph-example`
- **Primary purpose:** Official example/reference for graph logic  
- **Language:** Unverified (likely Python; not asserted as such in inputs)  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T1  
- **Claims made (summary):** “Pure reference,” too minimalist to productize (no auth, docker, pooling) ([T1])

#### 12) `langchain-ai/react-agent`
- **Primary purpose:** Official LangGraph template for a simple ReAct agent  
- **Language:** Unverified  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T3  
- **Claims made (summary):** Graph template, not an agent service scaffold; lacks FastAPI boundary and PostgresSaver wiring ([T3])

#### 13) `langchain-ai/retrieval-agent-template`
- **Primary purpose:** Official retrieval agent template  
- **Language:** Unverified  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T3  
- **Claims made (summary):** Template is graph‑level, not a service scaffold (no FastAPI boundary / no PostgresSaver wiring) ([T3])

#### 14) `langchain-ai/langserve`
- **Primary purpose:** Library to serve LangChain runnables/graphs via generated API routes  
- **Language:** Unverified (library)  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T1  
- **Claims made (summary):** Powerful but conflicts with custom service boundary needs (RBAC + interrupt/resume endpoints) ([T1])

#### 15) `langchain-ai/deepagents`
- **Primary purpose:** Library (not a service scaffold)  
- **Language:** Unverified  
- **License:** MIT (stated) ([T2])  
- **Maintenance signals:** Unverified  
- **Appears in:** T2  
- **Claims made (summary):** Rejected because it is a library without FastAPI service boundary/deploy config ([T2])

#### 16) `langchain-ai/langgraph-fullstack-python`
- **Primary purpose:** Demo/tutorial fullstack project (targets LangGraph Platform)  
- **Language:** Unverified  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T2  
- **Claims made (summary):** Rejected: no persistence/auth/HITL; demo‑quality only ([T2])

#### 17) `langchain-ai/agents-from-scratch`
- **Primary purpose:** Tutorial/notebooks  
- **Language:** Unverified  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T2  
- **Claims made (summary):** Rejected: educational content, not deployable scaffold ([T2])

#### 18) `langchain-ai/open-agent-platform`
- **Primary purpose:** Frontend‑only platform components (requires external backend)  
- **Language:** Unverified  
- **License:** MIT (stated) ([T2])  
- **Maintenance signals:** Unverified  
- **Appears in:** T2  
- **Claims made (summary):** Rejected: requires LangGraph Platform backend; not standalone agent service ([T2])

#### 19) `sieveLau/openwebui-langgraph`
- **Primary purpose:** OpenWebUI‑specific integration  
- **Language:** Unverified  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T2  
- **Claims made (summary):** Rejected: OpenWebUI coupling; does not match ZakOps service boundary ([T2])

#### 20) `docker/compose-for-agents`
- **Primary purpose:** Compose examples for agent stacks (reference)  
- **Language:** Multi (examples) (unverified)  
- **License:** Apache‑2.0 + MIT (stated) ([T3])  
- **Maintenance signals:** Unverified  
- **Appears in:** T3  
- **Claims made (summary):** Useful reference; not an agent service scaffold to fork ([T3])

#### 21) `von-development/awesome-LangGraph`
- **Primary purpose:** Ecosystem index (discovery aid)  
- **Language:** N/A  
- **License:** Unverified in T1/T2/T3 (T2 links it only)  
- **Maintenance signals:** Unverified  
- **Appears in:** T2  
- **Claims made (summary):** Discovery index; not a scaffold ([T2])

#### 22) `langchain-ai/langgraph`
- **Primary purpose:** Framework/library (not a scaffold)  
- **Language:** N/A  
- **License:** Unverified in T1/T2/T3 (T2 links it only)  
- **Maintenance signals:** Unverified  
- **Appears in:** T2  
- **Claims made (summary):** Framework under evaluation; not a fork target ([T2])

#### 23) `langserve-assistant-ui` (canonical repo name unresolved)
- **Primary purpose:** LangServe + “assistant UI” pattern (exact repo unclear)  
- **Language:** Unverified  
- **License:** Unverified  
- **Maintenance signals:** Unverified  
- **Appears in:** T2 (no‑go list)  
- **Claims made (summary):** Rejected: LangServe pattern doesn’t match ZakOps FastAPI service boundary ([T2])

---

## 2) Coverage Map (ZakOps Requirements → Candidate Coverage)

### MUST‑HAVE Capability Set (derived from Decision Lock + Master Doc v2)
These are the **PASS 2 gating axes**; anything missing becomes required adaptation work:
1. LangGraph orchestration (Python service‑side)  
2. Durable checkpointing (PostgresSaver/AsyncPostgresSaver; crash recovery)  
3. HITL interrupt/resume pattern compatible with approvals (`interrupt_before=["approval_gate"]` + resume endpoints)  
4. Streaming to UI (SSE/WS acceptable; must integrate with ZakOps Next.js)  
5. Tool calling with schema validation / strict args (Pydantic/JSON Schema; no “freeform” tool args)  
6. Tool separation: READ vs WRITE vs CRITICAL (policy‑enforceable)  
7. Idempotency friendliness for writes (claim‑first pattern support)  
8. Observability hooks compatible with Langfuse + OpenTelemetry (no LangSmith hosting dependency)  
9. Local‑first dev ergonomics (docker‑compose; works without constant internet)  
10. Security baseline (JWT + RBAC; optional API key)  
11. Clean service boundary (Agent API separate from existing Deal API)  

### Scoring rubric (0–5)
- **5:** Present + aligned with ZakOps constraints as described in inputs  
- **3:** Present but requires meaningful adaptation / has caveats  
- **1:** Mentioned only / partial patterns / likely rework  
- **0:** Not supported / wrong shape for ZakOps  

### 2.1 Quick Score Matrix (0–5)
Abbrev columns: `LG` LangGraph, `CP` checkpointing, `HITL`, `STR` streaming, `TV` tool validation, `RW/C` permission tiers, `IDEM`, `OBS` observability, `DEV` compose/local‑first, `SEC` auth/RBAC, `BND` service boundary.

| Candidate | LG | CP | HITL | STR | TV | RW/C | IDEM | OBS | DEV | SEC | BND |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| JoshuaC215/agent-service-toolkit | 5 | 4 | 4 | 5 | 4 | 1 | 1 | 3 | 5 | 2 | 5 |
| ibbybuilds/aegra | 5 | 5 | 4 | 4 | 3 | 1 | 1 | 4 | 5 | 2 | 3 |
| wassim249/fastapi-langgraph-agent-production-ready-template | 5 | 5 | 1 | 4 | 4 | 1 | 1 | 4 | 5 | 4 | 5 |
| NicholasGoh/fastapi-mcp-langgraph-template | 4 | 2 | 1 | 4 | 3 | 1 | 1 | 3 | 3 | 1 | 4 |
| brandonroberts/fastapi-langgraph | 3 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 3 |
| esurovtsev/langgraph-hitl-fastapi-demo | 3 | 1 | 5 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 3 |
| KirtiJha/langgraph-interrupt-workflow-template | 3 | 0 | 5 | 3 | 1 | 0 | 0 | 1 | 3 | 1 | 2 |
| langchain-ai/opengpts | 4 | 4 | 0 | 3 | 3 | 0 | 0 | 1 | 4 | 3 | 2 |
| google-gemini/gemini-fullstack-langgraph-quickstart | 2 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 2 | 0 | 1 |
| Yonom/assistant-ui-langgraph-fastapi | 2 | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 2 | 0 | 2 |
| langchain-ai/langgraph-example | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| langchain-ai/react-agent | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| langchain-ai/retrieval-agent-template | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| langchain-ai/langserve | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| langchain-ai/deepagents | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| langchain-ai/langgraph-fullstack-python | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| langchain-ai/agents-from-scratch | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| langchain-ai/open-agent-platform | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sieveLau/openwebui-langgraph | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| docker/compose-for-agents | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| von-development/awesome-LangGraph | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| langchain-ai/langgraph | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| langserve-assistant-ui (unresolved) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### 2.2 One‑Sentence Justifications (per requirement, per candidate)
Notes: “unverified” indicates T1/T2/T3 did not clearly prove the feature; PASS 2 must inspect code.

#### JoshuaC215/agent-service-toolkit
- LG=5 — Described as LangGraph agent served by FastAPI. ([T2], [T3])
- CP=4 — Claims PostgreSQL persistence via compose; exact PostgresSaver wiring requires validation. ([T2])
- HITL=4 — Claims `interrupt()` + resume handling exist, but ZakOps approval endpoints must be added. ([T2], [T3])
- STR=5 — Claims streaming endpoints are present (token/message). ([T2], [T3])
- TV=4 — Claims tool calling + Pydantic‑style schemas are used; strictness unverified. ([T2])
- RW/C=1 — Permission tiers (READ/WRITE/CRITICAL) are stated as missing. ([T2])
- IDEM=1 — Idempotency layer is stated as missing. ([T2])
- OBS=3 — LangSmith↔Langfuse story conflicts (optional vs missing); must verify, but observability hooks exist. ([T2] vs [T3])
- DEV=5 — Claims full docker-compose + hot reload (`docker compose watch`). ([T2])
- SEC=2 — Header auth only is stated; JWT/RBAC must be implemented. ([T2], [T3])
- BND=5 — Clean FastAPI agent service boundary is explicit. ([T2], [T3])

#### ibbybuilds/aegra
- LG=5 — Presented as LangGraph backend platform with FastAPI. ([T2], [T3])
- CP=5 — Claims built‑in Postgres saver/checkpointing. ([T2], [T3])
- HITL=4 — Claims approval gates / `interrupt_before` support; mapping to ZakOps approval endpoints is unverified. ([T2], [T3])
- STR=4 — Claims SSE streaming (and replay/event store in T3). ([T3])
- TV=3 — Tool system exists but schema‑strict tool contracts are not proven. ([T2])
- RW/C=1 — Permission tiers are stated as missing. ([T2])
- IDEM=1 — Idempotency layer is stated as missing. ([T2])
- OBS=4 — Langfuse is stated as integrated; OTel/no‑raw‑content policy is unverified. ([T2], [T3])
- DEV=5 — Docker compose exists (Redis optional). ([T2])
- SEC=2 — Auth is extensible but not ZakOps JWT/RBAC spec out‑of‑box. ([T2], [T3])
- BND=3 — Platform/run API shape may not match ZakOps `/agent/*` contract cleanly. ([T3])

#### wassim249/fastapi-langgraph-agent-production-ready-template
- LG=5 — Native LangGraph integration in a FastAPI service template. ([T1], [T2], [T3])
- CP=5 — Claims Postgres persistence / AsyncPostgresSaver usage and pgvector compose. ([T1], [T3])
- HITL=1 — Explicitly stated missing; must add approval gate + resume endpoints. ([T1], [T2], [T3])
- STR=4 — Streaming is stated as present, but not aligned to ZakOps `/agent/invoke` contract out‑of‑box. ([T1], [T3])
- TV=4 — Tool validation via Pydantic is claimed; strictness unverified. ([T1], [T2])
- RW/C=1 — Permission tiers are not present; must implement. ([T2], [T3])
- IDEM=1 — Idempotency is not present; must implement. ([T2], [T3])
- OBS=4 — Langfuse integration is claimed; “no raw content” policy enforcement is unverified. ([T1], [T2], [T3])
- DEV=5 — Docker compose described as “compose ready” with DB/monitoring. ([T1], [T2])
- SEC=4 — JWT authentication is claimed as implemented; claim‑validation specifics must be checked in PASS 2. ([T1], [T2], [T3])
- BND=5 — Explicitly “server model” template aligned with service boundary needs. ([T1])

#### NicholasGoh/fastapi-mcp-langgraph-template
- LG=4 — FastAPI + LangGraph are claimed; exact graph structure unverified. ([T2], [T3])
- CP=2 — PostgresSaver checkpointing is “not explicit” in T2 and disputed in T3. ([T2], [T3])
- HITL=1 — HITL not explicit; would require new approval nodes/endpoints. ([T2], [T3])
- STR=4 — SSE streaming for graph events is claimed. ([T3])
- TV=3 — Tool schema validation is not clearly proven; MCP tool structure exists. ([T2])
- RW/C=1 — Permission tiers not present. ([T2], [T3])
- IDEM=1 — Idempotency not present. ([T2], [T3])
- OBS=3 — Langfuse integration is claimed but deployability/policy alignment is disputed. ([T2], [T3])
- DEV=3 — Compose exists but Postgres inclusion is disputed; needs PASS 2 validation. ([T2] vs [T3])
- SEC=1 — Auth story is incomplete (planned vs missing). ([T2], [T3])
- BND=4 — FastAPI service boundary exists, but may be MCP/inspector‑shaped vs ZakOps `/agent/*`. ([T2])

#### brandonroberts/fastapi-langgraph
- LG=3 — Mentioned as “good FastAPI+LangGraph option,” but details unverified. ([T1])
- CP=1 — No checkpointing details provided. ([T1])
- HITL=0 — No HITL claims. ([T1])
- STR=1 — No streaming claims. ([T1])
- TV=1 — No tool validation claims. ([T1])
- RW/C=0 — No permission tier claims. ([T1])
- IDEM=0 — No idempotency claims. ([T1])
- OBS=0 — No Langfuse/OTel claims. ([T1])
- DEV=1 — No compose claims. ([T1])
- SEC=0 — No JWT claims. ([T1])
- BND=3 — Likely FastAPI‑service shaped, but unverified. ([T1])

#### esurovtsev/langgraph-hitl-fastapi-demo
- LG=3 — “Simple FastAPI file” showing interrupt pattern; full LangGraph architecture unverified. ([T1])
- CP=1 — Persistence is not described as Postgres‑durable. ([T1])
- HITL=5 — Explicitly recommended as best HITL interrupt/resume reference. ([T1])
- STR=1 — No streaming claims. ([T1])
- TV=1 — No tool schema validation claims. ([T1])
- RW/C=0 — No permission tiers. ([T1])
- IDEM=0 — No idempotency. ([T1])
- OBS=0 — No observability. ([T1])
- DEV=1 — “Manual” setup implied; no production compose asserted. ([T1])
- SEC=0 — No auth. ([T1])
- BND=3 — FastAPI exists but not a production service boundary. ([T1])

#### KirtiJha/langgraph-interrupt-workflow-template
- LG=3 — HITL template implies LangGraph, but not proven as production LangGraph orchestration. ([T2])
- CP=0 — Explicitly stated to use in‑memory checkpointing (no PostgresSaver). ([T2])
- HITL=5 — “Full HITL implementation” is claimed. ([T2])
- STR=3 — Fullstack implies UI streaming; exact mechanism unverified. ([T2])
- TV=1 — Tool schema validation not described. ([T2])
- RW/C=0 — No permission tiers. ([T2])
- IDEM=0 — No idempotency. ([T2])
- OBS=1 — No Langfuse; only “LangChain optional” tracing noted. ([T2])
- DEV=3 — Docker compose is claimed included. ([T2])
- SEC=1 — JWT/auth is stated as env‑vars only. ([T2])
- BND=2 — Fullstack template may not align with “agent service only” preference. ([T2])

#### langchain-ai/opengpts
- LG=4 — Uses LangGraph (MessageGraph pattern). ([T2], [T3])
- CP=4 — Postgres+pgvector and checkpointing are claimed. ([T2], [T3])
- HITL=0 — Explicitly stated “no HITL” / “no approvals.” ([T2], [T3])
- STR=3 — Streaming exists, but shape may not match ZakOps `/agent/*`. ([T3])
- TV=3 — “Custom actions/OpenAPI” suggests structured tools; strict arg validation unverified. ([T2])
- RW/C=0 — No permission tiers. ([T2])
- IDEM=0 — No idempotency. ([T2])
- OBS=1 — LangSmith‑oriented; Langfuse/OTel compatibility not established. ([T2], [T3])
- DEV=4 — Docker compose exists, but heavyweight. ([T2], [T3])
- SEC=3 — JWT/auth options are claimed but need PASS 2 validation for ZakOps claim requirements. ([T2], [T3])
- BND=2 — Fullstack + LangServe patterns increase boundary mismatch risk. ([T2], [T3])

#### google-gemini/gemini-fullstack-langgraph-quickstart
- LG=2 — LangGraph is implied by name; implementation details not provided. ([T3])
- CP=0 — PostgresSaver not verified. ([T3])
- HITL=0 — No HITL claims. ([T3])
- STR=2 — Fullstack implies interactive streaming, but unverified. ([T3])
- TV=1 — Tool schema validation unverified. ([T3])
- RW/C=0 — No permission tiers. ([T3])
- IDEM=0 — No idempotency. ([T3])
- OBS=0 — No Langfuse/OTel claims. ([T3])
- DEV=2 — Compose likely exists, but cloud‑first assumptions violate local‑first constraints. ([T3])
- SEC=0 — No JWT/RBAC claims. ([T3])
- BND=1 — Fullstack starter is not aligned to “agent service drop‑in.” ([T3])

#### Yonom/assistant-ui-langgraph-fastapi
- LG=2 — LangGraph usage is implied (demo), not proven durable. ([T3])
- CP=0 — Explicitly noted “no durable checkpointing.” ([T3])
- HITL=0 — No HITL claims. ([T3])
- STR=4 — Streaming to frontend is the core claim. ([T3])
- TV=1 — Tool schema validation not described. ([T3])
- RW/C=0 — No permission tiers. ([T3])
- IDEM=0 — No idempotency. ([T3])
- OBS=0 — No Langfuse/OTel claims. ([T3])
- DEV=2 — Demo suggests runnable, but production compose not claimed. ([T3])
- SEC=0 — No auth claims. ([T3])
- BND=2 — Includes frontend; not a clean agent‑server scaffold. ([T3])

#### langchain-ai/langgraph-example / react-agent / retrieval-agent-template
- All are treated as **graph templates/examples** rather than agent service scaffolds; service boundary, checkpointing, auth, and ops are not present in inputs. ([T1], [T3])

#### langchain-ai/langserve / deepagents / langgraph-fullstack-python / agents-from-scratch / open-agent-platform / sieveLau/openwebui-langgraph / docker/compose-for-agents / awesome-LangGraph / langgraph / langserve-assistant-ui
- All are **non‑scaffold** (library/tutorial/index/demo) or explicitly rejected patterns; they do not satisfy ZakOps must‑have service shape without major rebuild. ([T1], [T2], [T3])

---

## 3) Contradiction Register
Conflicts across T1/T2/T3 that must be resolved in PASS 2 by inspecting code and running minimal bring‑up tests.

### C‑01 — “Which scaffold should be forked first?”
- **Claim A:** Fork `wassim249/fastapi-langgraph-agent-production-ready-template` as primary chassis. ([T1])
- **Claim B:** Fork `JoshuaC215/agent-service-toolkit` first (best HITL completeness + maturity). ([T2])
- **Claim C:** `wassim249` is #1, with `agent-service-toolkit` as #2. ([T3])
- **Impact:** Changes baseline architecture, deletion/pruning strategy, and delta workload ordering.
- **Missing evidence:** Uniform PASS‑2 gate results (license, checkpointing durability, HITL semantics, auth delta, observability).
- **Resolution approach (PASS 2):** Run the same verification checklist on top 3 (wassim249, agent-service-toolkit, aegra) and compare against Decision Lock acceptance tests.

### C‑02 — MCP support in `agent-service-toolkit`
- **Claim A:** MCP integration is missing. ([T2])
- **Claim B:** MCP integration exists and uses streamable-http. ([T3])
- **Impact:** Determines whether we reuse its MCP adapter layer vs implementing from scratch for ZakOps MCP `:9100`.
- **Missing evidence:** Inspect MCP client code and transport config; confirm it can target `localhost:9100` streamable-http.
- **Resolution approach (PASS 2):** Locate MCP client modules; verify transport type; run conformance test: initialize → tools/list → tools/call against ZakOps MCP server.

### C‑03 — Observability in `agent-service-toolkit` (LangSmith vs Langfuse)
- **Claim A:** Uses LangSmith by default; Langfuse integration missing but swappable. ([T2])
- **Claim B:** Langfuse is already present/used (optional). ([T3])
- **Impact:** Determines whether the scaffold violates “no LangSmith hosting dependency” and how much refactor is needed.
- **Missing evidence:** Confirm which tracing SDK is wired into request path; ensure LangSmith is optional and can be disabled without code edits.
- **Resolution approach (PASS 2):** Identify tracing config flags and callback handlers; run with LangSmith disabled and verify Langfuse trace emission is possible.

### C‑04 — `fastapi-mcp-langgraph-template`: Postgres/pgvector + PostgresSaver checkpointing + compose completeness
- **Claim A:** Has Postgres/pgvector, Langfuse, and compose (dev+prod). ([T2])
- **Claim B:** Core compose lacks Postgres; checkpointing not clear; auth missing. ([T3])
- **Impact:** Risk of choosing a scaffold that cannot meet durable state requirements without heavy surgery.
- **Missing evidence:** Inspect compose files and graph compilation for `AsyncPostgresSaver`; check whether Postgres is actually part of stack.
- **Resolution approach (PASS 2):** Verify `docker compose up` yields Postgres + API; grep for `AsyncPostgresSaver` and `compile(checkpointer=...)`.

### C‑05 — wassim249 delta sizing (“Medium” vs “Large”)
- **Claim A:** Medium delta; use as chassis and graft HITL logic. ([T1])
- **Claim B:** Large delta because HITL is missing and must be implemented. ([T2])
- **Claim C:** Medium delta (replace LLM/memory/tools; add approval endpoints). ([T3])
- **Impact:** Affects schedule/risk and whether we prefer a HITL-complete base.
- **Missing evidence:** Actual time‑boxed spike implementing `/agent/invoke` + approvals + checkpointing + one CRITICAL tool flow.
- **Resolution approach (PASS 2):** Implement the “Transition Deal with Approval Gate” scenario in a fork branch and measure integration complexity qualitatively (S/M/L).

### C‑06 — OpenGPTs service boundary characterization
- **Claim A:** “LangServe not FastAPI” and mismatch risk is primary rejection reason. ([T2])
- **Claim B:** FastAPI server exists and can be adapted, but it’s LangSmith‑oriented and heavyweight. ([T3])
- **Impact:** If misunderstood, may incorrectly reject/accept as a fork base.
- **Missing evidence:** Confirm whether OpenGPTs can expose custom endpoints matching `/agent/invoke` and approvals without fighting framework auto‑routes.
- **Resolution approach (PASS 2):** Inspect backend server entrypoint and routing; attempt to add a custom router matching MDv2 contract as a small spike.

### C‑07 — Port conventions drift (Langfuse :3000 vs :3001)
- **Claim A:** T1 references trace in Langfuse at `:3000`. ([T1])
- **Constraint:** Decision Lock binds Langfuse to `:3001`. (Decision Lock)
- **Impact:** Port collisions (OpenWebUI uses :3000 in current environment); drift risk in scaffolds.
- **Resolution approach (PASS 2):** Standardize compose ports to Decision Lock and reject candidates that hard‑code conflicting ports without easy override.

---

## 4) Missing Pieces / Blind Spots (PASS 2 Check Definitions)
Items none of T1/T2/T3 establish with enough certainty to safely fork without verification.

### B‑01 — Durable checkpointing is “claimed” but not proven end‑to‑end
- **Risk:** Repo uses Postgres for other reasons but not LangGraph PostgresSaver checkpointing, or uses it incorrectly (no crash recovery).
- **PASS 2 checks (deterministic):**
  - Find `AsyncPostgresSaver` / `PostgresSaver` usage and confirm graph compilation uses `compile(checkpointer=...)`.
  - Run: start service → invoke graph with thread_id → hard kill process → restart → resume same thread_id → verify state persists.

### B‑02 — HITL semantics vs ZakOps approval contract
- **Risk:** Repo uses interrupts for “ask user a question” but not approval gating with durable resume; no `/agent/approvals/{id}` API.
- **PASS 2 checks:**
  - Locate interrupt nodes and resume mechanism (`interrupt_before` vs `interrupt()` vs `Command(resume=...)`).
  - Confirm we can implement MDv2 endpoints:
    - `POST /agent/invoke`
    - `POST /agent/approvals/{approval_id}:approve|reject`
  - E2E: CRITICAL tool proposal → returns `awaiting_approval` → approve → resumes and executes once.

### B‑03 — Tool contract strictness (schema validation + “no hallucinated args”)
- **Risk:** Tools are bound loosely (dict passthrough), increasing hallucinated parameter risk.
- **PASS 2 checks:**
  - Confirm tool definitions are typed (Pydantic models or JSON Schema) and validated before execution.
  - Add negative tests: malformed args → tool call rejected with 4xx or structured error, not executed.

### B‑04 — READ/WRITE/CRITICAL policy enforcement
- **Risk:** Candidate has tools but no permission taxonomy, making approvals and governance non-deterministic.
- **PASS 2 checks:**
  - Identify existing tool registry abstraction (if any).
  - Verify how to add permission tiers and enforce:
    - READ: no approval
    - WRITE: policy‑dependent
    - CRITICAL: always approval

### B‑05 — Idempotency for WRITE/CRITICAL tools (claim‑first)
- **Risk:** Duplicate side effects under retries/restarts (contradicts Decision Lock).
- **PASS 2 checks:**
  - Confirm there is (or can be added) a tool execution log table and claim‑first insert.
  - Concurrency test: N parallel calls with same idempotency key → exactly one external side effect.

### B‑06 — Observability compliance: Langfuse + OTel with “no raw content”
- **Risk:** Candidate logs raw prompts/responses into traces or logs, violating Decision Lock.
- **PASS 2 checks:**
  - Inspect tracing integration points: what is sent to Langfuse (prompt/response raw vs hash/length).
  - Run a PII canary prompt and confirm canary strings do not appear in traces/logs by default.

### B‑07 — Local‑first reality (no hard cloud dependency)
- **Risk:** Required cloud keys (Gemini/OpenAI) for basic startup; violates “works without constant internet.”
- **PASS 2 checks:**
  - Inspect `.env.example` / settings for required cloud keys and whether they are optional.
  - Bring up scaffold using only local vLLM base URL (`http://localhost:8000/v1`) and no internet.

### B‑08 — Port and boundary compatibility with existing ZakOps services
- **Risk:** Candidate hard‑codes ports (especially `:8000`) or conflates “agent” with “deal API.”
- **PASS 2 checks:**
  - Confirm agent service can run on `:8095` with Cloudflare routing to `:8095` (not `:8090`).
  - Confirm outbound calls to Deal API target `http://localhost:8090`.
  - Confirm retrieval path is single (pgvector or RAG REST `:8052`) per Decision Lock.

### B‑09 — MCP transport alignment
- **Risk:** Candidate MCP client assumes SSE, while ZakOps MCP server is streamable‑http (`:9100`).
- **PASS 2 checks:**
  - Verify client transport options and whether it supports streamable-http.
  - Run deterministic conformance: initialize → tools/list → tools/call on ZakOps MCP server.

---

## 5) Decision Queue (Top 20)
Decisions required to make PASS 2 deterministic and avoid scope drift. Each item includes what must be verified to raise confidence.

1) **Choose the base fork scaffold for ZakOps Agent API (:8095).**  
   - Options: `wassim249/...`, `JoshuaC215/...`, `ibbybuilds/aegra`, (others as non‑recommended)  
   - Recommendation: **Open Decision** (PASS 2 gating)  
   - Confidence: Low  
   - Required verification: PASS 2 gate checklist on top 3 + E2E approval‑gated deal transition demo.

2) **Service shape: “agent service scaffold” vs “platform/run API server” baseline.**  
   - Options: agent-service-toolkit / wassim249 (agent service) vs aegra (platform‑style)  
   - Recommendation: Open Decision  
   - Confidence: Low  
   - Required verification: effort to implement MDv2 `/agent/*` contract cleanly in each.

3) **HITL mechanism: `interrupt_before` vs `interrupt()` usage style (internals).**  
   - Options: prefer `interrupt_before=["approval_gate"]` (Decision Lock) vs implement via `interrupt()` nodes  
   - Recommendation: **Use Decision Lock pattern; allow `interrupt()` internally if it maps cleanly**  
   - Confidence: Medium  
   - Required verification: demonstrate pause/resume with approval endpoints and PostgresSaver checkpoints.

4) **Approval API shape: adopt scaffold’s existing endpoints vs enforce ZakOps canonical endpoints.**  
   - Options: keep scaffold endpoints, add adapter; or implement `/agent/invoke` + `/agent/approvals/...` as primary  
   - Recommendation: Enforce canonical endpoints (avoid drift)  
   - Confidence: High  
   - Required verification: add contract tests + update any scaffold clients accordingly.

5) **Checkpointing integration approach (pooling strategy).**  
   - Options: reuse SQLAlchemy pool vs separate psycopg/async pool for `AsyncPostgresSaver`  
   - Recommendation: Open Decision  
   - Confidence: Medium  
   - Required verification: stability under load; crash recovery works; no connection starvation.

6) **Tool integration: hybrid MCP + direct tools (locked) — decide the adapter interface.**  
   - Options: MCP wrapper around Deal API vs direct HTTP client for Deal API + MCP for external tools  
   - Recommendation: Direct tools for Deal API/RAG; MCP for external/optional tools (per Decision Lock)  
   - Confidence: High  
   - Required verification: tool registry supports both kinds with one permission/idempotency layer.

7) **MCP transport: confirm streamable‑http client viability in chosen scaffold.**  
   - Options: reuse existing MCP client (if any) vs implement minimal client for streamable‑http  
   - Recommendation: Open Decision  
   - Confidence: Low  
   - Required verification: PASS 2 MCP conformance test against ZakOps MCP `:9100`.

8) **Observability stack integration: Langfuse direct vs OTel collector pipeline.**  
   - Options: Langfuse callback only; or OTel spans → collector → Langfuse  
   - Recommendation: Open Decision (Decision Lock requires Langfuse + OTel compatibility)  
   - Confidence: Medium  
   - Required verification: traces visible; no raw content; graceful degradation when Langfuse down.

9) **LangSmith presence: tolerate optional LangSmith libs or remove entirely?**  
   - Options: keep optional (disabled) vs remove dependency surface  
   - Recommendation: Keep optional only if fully disabled by default and no runtime dependency  
   - Confidence: Medium  
   - Required verification: run without LangSmith env/config; no errors; no egress.

10) **Authentication baseline: implement ZakOps JWT+RBAC in scaffold vs adapt existing.**  
   - Options: scaffold JWT (wassim249) vs add JWT to toolkit/aegra  
   - Recommendation: Open Decision  
   - Confidence: Medium  
   - Required verification: JWT claim validation per Decision Lock; role enforcement on CRITICAL approvals.

11) **API key fallback: support `X-API-Key` (Decision Lock) in addition to JWT.**  
   - Options: add; or postpone  
   - Recommendation: Add in Phase 1 (small and reduces integration friction)  
   - Confidence: High  
   - Required verification: revoked keys rejected; audit log records auth attempts.

12) **Retrieval integration: single path selection (Decision Lock).**  
   - Options: call RAG REST `:8052` vs direct pgvector in Agent DB  
   - Recommendation: Open Decision (but must be single path)  
   - Confidence: Medium  
   - Required verification: end‑to‑end doc retrieval works; access controls honored; no split‑brain.

13) **Embedding pipeline: where does BGE‑M3 run and how is it called?**  
   - Options: in‑process embeddings vs separate embeddings worker/service  
   - Recommendation: Open Decision  
   - Confidence: Low  
   - Required verification: can generate/store 1024‑dim vectors; performance acceptable locally.

14) **Queue: Postgres SKIP LOCKED implementation location.**  
   - Options: build into agent service vs separate workers service  
   - Recommendation: Open Decision  
   - Confidence: Medium  
   - Required verification: concurrent claims; retries/backoff; DLQ tables.

15) **Idempotency boundary: tool‑level only vs API endpoint idempotency too.**  
   - Options: tool gateway only vs both  
   - Recommendation: Implement in tool gateway first; add API-level idempotency for write endpoints as needed  
   - Confidence: Medium  
   - Required verification: duplicate approval execution prevented under retries.

16) **Streaming protocol to ZakOps Next.js UI: SSE vs WebSocket.**  
   - Options: SSE (simpler) vs WS (bi‑directional)  
   - Recommendation: Open Decision  
   - Confidence: Medium  
   - Required verification: can stream token/message updates without breaking approval interrupts.

17) **Port collision strategy for local dev (OpenWebUI at :3000).**  
   - Options: keep Langfuse at :3001 (Decision Lock) and move other dashboards off :3000  
   - Recommendation: Follow Decision Lock ports; avoid :3000 collisions  
   - Confidence: High  
   - Required verification: `docker compose up` works without conflicts.

18) **Graph organization: single “deal lifecycle graph” vs multi-graph modules.**  
   - Options: one graph with router nodes; or separate graphs per workflow type  
   - Recommendation: Open Decision  
   - Confidence: Medium  
   - Required verification: checkpointing and approvals consistent across workflow types.

19) **Event/audit logging substrate alignment with MDv2 event types.**  
   - Options: adopt scaffold logs/traces; or implement explicit event table + schema validation  
   - Recommendation: Implement explicit event taxonomy per MDv2 to prevent drift  
   - Confidence: High  
   - Required verification: schema validation + required event emission tests.

20) **“Minimal fork” pruning strategy.**  
   - Options: fork and delete non‑ZakOps modules immediately vs keep temporarily  
   - Recommendation: Keep temporarily only if it reduces risk; otherwise delete early to prevent drift  
   - Confidence: Medium  
   - Required verification: clear migration plan and first E2E scenario defined and tested.

---

## 6) Shortlist Criteria (Gate Checklist for PASS 2)
PASS 2 should apply these as **fail‑fast gates** to each plausible scaffold (at minimum: wassim249, agent-service-toolkit, aegra; optionally fastapi-mcp-langgraph-template).

### Gate 1 — License acceptance
- **PASS:** MIT or Apache‑2.0 explicitly present and acceptable for commercial use.
- **FAIL FAST:** Missing license file or copyleft license (GPL/AGPL) unless explicitly approved.

### Gate 2 — Service boundary compatibility
- **PASS:** A clean Agent API server can run on `:8095` and call Deal API on `:8090`.
- **FAIL FAST:** Repo architecture couples agent runtime into UI or requires a platform backend we don’t run.

### Gate 3 — Durable checkpointing (must be real, not aspirational)
- **PASS:** LangGraph graph compiles with `PostgresSaver/AsyncPostgresSaver` and survives restart with same `thread_id`.
- **FAIL FAST:** Only in‑memory checkpoints or persistence is “planned” without working PostgresSaver wiring.

### Gate 4 — HITL approvals support (or minimal addability)
- **PASS:** Either already has interrupt/resume semantics or can add approvals without rewriting the framework.
- **FAIL FAST:** HITL depends on console/manual steps or cannot resume deterministically.

### Gate 5 — Tool abstraction cleanliness
- **PASS:** Clear tool registry layer exists (or can be added) to enforce READ/WRITE/CRITICAL + validation + idempotency.
- **FAIL FAST:** Tool execution is scattered without a single gateway point (high drift risk).

### Gate 6 — Observability + privacy compliance
- **PASS:** Can integrate Langfuse and/or OTel with **no raw prompt/response** logged by default.
- **FAIL FAST:** Traces/logs capture raw deal documents by default and cannot be disabled.

### Gate 7 — Local‑first operability
- **PASS:** Can run with local vLLM OpenAI‑compatible API (`:8000`) and no mandatory cloud keys.
- **FAIL FAST:** Requires Gemini/OpenAI/cloud keys for basic startup or core workflows.

### Gate 8 — Maintenance risk
- **PASS:** Either actively maintained or sufficiently minimal/stable with low churn risk.
- **FAIL FAST:** Extremely immature templates (e.g., “9 commits”) unless used strictly as reference modules.

---

**PASS 1 Deliverable Complete:** This ledger defines the normalized candidate set, the coverage gaps, the contradictions, and the exact PASS 2 checks needed to make a deterministic fork decision.


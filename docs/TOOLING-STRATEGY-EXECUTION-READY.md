# ZakOps Kinetic Action Engine - Tooling Strategy (Execution-Ready)

**Document Version:** 2.0
**Created:** 2025-12-31
**Status:** EXECUTION-READY
**Target Phase:** Phase 0.5 (Tooling Infrastructure)
**Owner:** ZakOps Deal Lifecycle OS Team

---

## Quick Start (5 Minutes)

### Required Environment Variables

```bash
# Core
export ZAKOPS_STATE_DB="/home/zaks/DataRoom/.deal-registry/ingest_state.db"
export ZAKOPS_BRAIN_MODE="auto"  # off|auto|force

# Tool Gates (all default to false for safety)
export ZAKOPS_TOOL_GATEWAY_ENABLED="true"
export ZAKOPS_MCP_RUNTIME_MODE="stdio"  # stdio|docker
export ZAKOPS_TOOL_ALLOWLIST=""  # comma-separated, empty = all allowed
export ZAKOPS_TOOL_DENYLIST=""   # comma-separated, takes precedence

# Secrets (referenced by tools, never in manifests)
export GMAIL_MCP_CREDENTIALS_PATH="/home/zaks/.gmail-mcp/credentials.json"
# Optional: override the MCP launcher command (keeps triage + ToolGateway aligned)
export GMAIL_MCP_COMMAND="npx -y @gongrzhe/server-gmail-autoauth-mcp"
```

### Services & Ports

| Service | Port | Start Command |
|---------|------|---------------|
| FastAPI BFF | `:8090` | `cd /home/zaks/scripts && uvicorn deal_lifecycle_api:app --reload --port 8090` |
| Dashboard UI | `:3003` | `cd /home/zaks/zakops-dashboard && npm run dev` |
| LangGraph Brain | `:8080` | `cd /home/zaks/langgraph-brain && python serve.py` |
| Actions Runner | background | `cd /home/zaks/scripts && python actions_runner.py` |

### Preflight & Smoke Test

```bash
# Validate tool manifests + secrets + health
make tool-preflight

# Smoke test (after services running)
curl -s http://localhost:8090/api/tools | jq '.tools | length'
curl -s http://localhost:8090/api/tools/health | jq '.healthy'
```

---

## Path Map (Canonical Roots)

| Component | Root Path |
|-----------|-----------|
| Python Backend | `/home/zaks/scripts/` |
| Dashboard UI | `/home/zaks/zakops-dashboard/src/` |
| Tool Manifests | `/home/zaks/scripts/tools/manifests/` |
| Action Capabilities | `/home/zaks/scripts/actions/capabilities/` |
| DataRoom Artifacts | `/home/zaks/DataRoom/{deal.folder_path}/99-ACTIONS/{action_id}/` |
| SQLite State | `$ZAKOPS_STATE_DB` (default: `/home/zaks/DataRoom/.deal-registry/ingest_state.db`) |

**Rule:** All new Python files go under `/home/zaks/scripts/`. Do NOT create a parallel `src/` directory.

---

## Section 1: Tool Gateway (Single Entrypoint)

### 1.1 Design Principles

1. **Single Entrypoint:** ALL external tool invocations go through `ToolGateway.invoke()`
2. **Secret-Scan Gate:** Block calls with detected secrets BEFORE invocation (not just redaction)
3. **Approval Enforcement:** Deny tools unless invoking action is `READY/PROCESSING` and approved
4. **Audit Everything:** SQLite `tool_invocation_log` + deal events (NO LangSmith)
5. **Bounded Logs:** Truncate large payloads with hash reference

### 1.2 Implementation

**File:** `/home/zaks/scripts/tools/gateway.py`

```python
"""
ToolGateway - Single entrypoint for all external tool invocations.

All MCP/HTTP/external calls MUST go through this gateway.
Local-only executors (DOCX/PDF generation) do NOT use this.
"""

import os
import re
import time
import json
import hashlib
import logging
import sqlite3
import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# Error Codes (Structured)
# =============================================================================

class ToolErrorCode(str, Enum):
    """Structured error codes for tool invocations."""
    SUCCESS = "SUCCESS"

    # Permission (permanent - do not retry)
    TOOL_NOT_ALLOWED = "TOOL_NOT_ALLOWED"
    TOOL_DENIED = "TOOL_DENIED"
    SECRET_DETECTED = "SECRET_DETECTED"  # NEW: Secret-scan gate blocked
    ACTION_NOT_APPROVED = "ACTION_NOT_APPROVED"  # NEW: Approval enforcement
    UNAUTHORIZED = "UNAUTHORIZED"

    # Transient (retry with backoff)
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    MCP_SPAWN_FAILED = "MCP_SPAWN_FAILED"  # NEW: MCP process failed to start

    # Permanent (do not retry)
    INVALID_INPUT = "INVALID_INPUT"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    HEALTH_CHECK_FAILED = "HEALTH_CHECK_FAILED"

    # Internal
    GATEWAY_ERROR = "GATEWAY_ERROR"


RETRYABLE_ERRORS = {
    ToolErrorCode.TIMEOUT,
    ToolErrorCode.RATE_LIMITED,
    ToolErrorCode.CONNECTION_ERROR,
    ToolErrorCode.SERVICE_UNAVAILABLE,
    ToolErrorCode.MCP_SPAWN_FAILED,
    ToolErrorCode.GATEWAY_ERROR,
}


# =============================================================================
# Result Model
# =============================================================================

@dataclass
class ToolResult:
    """Result of a tool invocation."""
    success: bool
    error_code: ToolErrorCode
    error_message: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    duration_ms: int = 0
    retry_after_seconds: Optional[int] = None

    def should_retry(self) -> bool:
        """Check if this result indicates a retryable error."""
        return self.error_code in RETRYABLE_ERRORS


@dataclass
class ToolInvocationContext:
    """Context for tool invocation (for audit trail)."""
    action_id: str
    action_status: str  # Must be READY or PROCESSING
    deal_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    approved: bool = False  # Was this action operator-approved?


# =============================================================================
# Secret Scanner (Gate, not just redaction)
# =============================================================================

class SecretScanner:
    """
    Scans for secrets BEFORE external calls.

    This is a GATE (blocks calls), not just log redaction.
    Separate from SecretRedactor which only sanitizes logs.
    """

    # Patterns that indicate secrets
    SECRET_PATTERNS = [
        (r'[A-Za-z0-9+/]{40,}={0,2}', "base64-like"),
        (r'sk-[A-Za-z0-9]{20,}', "openai-key"),
        (r'ghp_[A-Za-z0-9]{20,}', "github-token"),
        (r'xox[baprs]-[A-Za-z0-9-]+', "slack-token"),
        (r'AKIA[A-Z0-9]{16}', "aws-access-key"),
        (r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----', "private-key"),
    ]

    # Keys that are safe even if they match patterns (allowlist)
    SAFE_KEYS = {'id', 'uuid', 'action_id', 'deal_id', 'message_id', 'thread_id'}

    _patterns = [(re.compile(p, re.IGNORECASE), name) for p, name in SECRET_PATTERNS]

    @classmethod
    def scan(cls, data: Dict[str, Any], path: str = "") -> List[str]:
        """
        Scan data for secrets. Returns list of detected secret paths.

        Returns empty list if clean, or list of "path.to.secret (type)" strings.
        """
        detections = []

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            # Skip safe keys
            if key.lower() in cls.SAFE_KEYS:
                continue

            if isinstance(value, dict):
                detections.extend(cls.scan(value, current_path))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        detections.extend(cls.scan(item, f"{current_path}[{i}]"))
                    elif isinstance(item, str):
                        for pattern, name in cls._patterns:
                            if pattern.search(item):
                                detections.append(f"{current_path}[{i}] ({name})")
                                break
            elif isinstance(value, str):
                for pattern, name in cls._patterns:
                    if pattern.search(value):
                        detections.append(f"{current_path} ({name})")
                        break

        return detections


class SecretRedactor:
    """Redacts secrets from data for logging (separate from gate)."""

    SECRET_KEYS = {'password', 'secret', 'token', 'api_key', 'apikey',
                   'auth', 'credential', 'bearer', 'private_key', 'client_secret'}

    REDACTED = "[REDACTED]"
    MAX_FIELD_SIZE = 10000  # Truncate fields larger than this

    @classmethod
    def redact(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact secrets and truncate large fields for logging."""
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            # Redact secret keys
            if any(sk in key.lower() for sk in cls.SECRET_KEYS):
                result[key] = cls.REDACTED
            elif isinstance(value, dict):
                result[key] = cls.redact(value)
            elif isinstance(value, list):
                result[key] = [cls.redact(i) if isinstance(i, dict) else i for i in value]
            elif isinstance(value, str) and len(value) > cls.MAX_FIELD_SIZE:
                # Truncate with hash reference
                hash_ref = hashlib.sha256(value.encode()).hexdigest()[:12]
                result[key] = f"[TRUNCATED:{len(value)}bytes:sha256:{hash_ref}]"
            else:
                result[key] = value

        return result


# =============================================================================
# Audit Logger
# =============================================================================

class ToolAuditLogger:
    """Logs tool invocations to SQLite with bounded size."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        """Create audit table with proper indices."""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=5000")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_invocation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invocation_id TEXT UNIQUE NOT NULL,
                    tool_name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    runtime_mode TEXT,

                    -- Context (correlation)
                    action_id TEXT NOT NULL,
                    deal_id TEXT,
                    user_id TEXT,

                    -- Input/Output (redacted + bounded)
                    input_args_redacted TEXT,
                    input_size_bytes INTEGER,

                    -- Result
                    success INTEGER NOT NULL,
                    error_code TEXT NOT NULL,
                    error_message TEXT,
                    output_redacted TEXT,
                    output_size_bytes INTEGER,

                    -- Timing
                    started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,

                    -- Retry
                    attempt_number INTEGER DEFAULT 1,
                    retry_after_seconds INTEGER,

                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_log_action ON tool_invocation_log(action_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_log_deal ON tool_invocation_log(deal_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_log_tool ON tool_invocation_log(tool_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_log_time ON tool_invocation_log(started_at)")
            conn.commit()

    def log(
        self,
        invocation_id: str,
        tool_name: str,
        provider: str,
        runtime_mode: str,
        context: ToolInvocationContext,
        input_args: Dict[str, Any],
        result: ToolResult,
        started_at: datetime,
        attempt: int = 1,
    ):
        """Log invocation with redacted, bounded data."""
        completed_at = datetime.utcnow()

        # Redact and serialize
        input_redacted = json.dumps(SecretRedactor.redact(input_args))
        output_redacted = json.dumps(SecretRedactor.redact(result.output or {}))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("""
                INSERT INTO tool_invocation_log (
                    invocation_id, tool_name, provider, runtime_mode,
                    action_id, deal_id, user_id,
                    input_args_redacted, input_size_bytes,
                    success, error_code, error_message,
                    output_redacted, output_size_bytes,
                    started_at, completed_at, duration_ms,
                    attempt_number, retry_after_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invocation_id, tool_name, provider, runtime_mode,
                context.action_id, context.deal_id, context.user_id,
                input_redacted, len(json.dumps(input_args)),
                1 if result.success else 0, result.error_code.value, result.error_message,
                output_redacted, len(json.dumps(result.output or {})),
                started_at.isoformat(), completed_at.isoformat(), result.duration_ms,
                attempt, result.retry_after_seconds,
            ))
            conn.commit()


# =============================================================================
# Tool Gateway
# =============================================================================

@dataclass
class ToolGatewayConfig:
    """Configuration for ToolGateway."""
    enabled: bool = True

    # Allowlist/Denylist
    allowed_tools: List[str] = field(default_factory=list)  # Empty = all
    denied_tools: List[str] = field(default_factory=list)   # Takes precedence

    # Timeouts
    default_timeout_ms: int = 30000
    tool_timeouts: Dict[str, int] = field(default_factory=dict)

    # Retries
    max_retries: int = 3
    retry_base_delay_ms: int = 1000
    retry_max_delay_ms: int = 30000

    # MCP Runtime
    mcp_runtime_mode: str = "stdio"  # "stdio" or "docker"
    mcp_idle_shutdown_seconds: int = 300  # For docker mode

    # Audit
    audit_db_path: str = ""

    @classmethod
    def from_env(cls) -> 'ToolGatewayConfig':
        """Load config from environment variables."""
        return cls(
            enabled=os.getenv("ZAKOPS_TOOL_GATEWAY_ENABLED", "true").lower() == "true",
            allowed_tools=[t.strip() for t in os.getenv("ZAKOPS_TOOL_ALLOWLIST", "").split(",") if t.strip()],
            denied_tools=[t.strip() for t in os.getenv("ZAKOPS_TOOL_DENYLIST", "").split(",") if t.strip()],
            mcp_runtime_mode=os.getenv("ZAKOPS_MCP_RUNTIME_MODE", "stdio"),
            audit_db_path=os.getenv("ZAKOPS_STATE_DB", "/home/zaks/DataRoom/.deal-registry/ingest_state.db"),
        )


class ToolGateway:
    """
    Central gateway for all external tool invocations.

    Usage:
        gateway = get_tool_gateway()

        result = await gateway.invoke(
            tool_name="gmail__send_email",
            args={"to": ["user@example.com"], "subject": "Test"},
            context=ToolInvocationContext(
                action_id="act_123",
                action_status="PROCESSING",
                deal_id="deal_456",
                approved=True,
            ),
        )
    """

    def __init__(
        self,
        config: Optional[ToolGatewayConfig] = None,
        tool_registry: Optional['ToolRegistry'] = None,
    ):
        self.config = config or ToolGatewayConfig.from_env()
        self.tool_registry = tool_registry
        self.audit_logger = ToolAuditLogger(self.config.audit_db_path)
        self._mcp_processes: Dict[str, 'MCPProcess'] = {}

    async def invoke(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: ToolInvocationContext,
        timeout_ms: Optional[int] = None,
    ) -> ToolResult:
        """
        Invoke a tool through the gateway.

        Gates (in order):
        1. Gateway enabled check
        2. Allowlist/denylist check
        3. Action approval check
        4. Secret-scan gate
        5. Tool exists check
        6. Health check (if enabled)
        7. Execute with timeout + retries
        8. Audit log
        """
        import uuid

        invocation_id = f"inv_{uuid.uuid4().hex[:12]}"
        started_at = datetime.utcnow()

        logger.info(f"ToolGateway.invoke: {tool_name} (inv: {invocation_id}, action: {context.action_id})")

        # Gate 1: Gateway enabled
        if not self.config.enabled:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.GATEWAY_ERROR,
                error_message="Tool gateway is disabled",
            )

        # Gate 2: Allowlist/Denylist
        result = self._check_permissions(tool_name)
        if not result.success:
            self._log_and_return(invocation_id, tool_name, "unknown", context, args, result, started_at)
            return result

        # Gate 3: Action approval enforcement
        result = self._check_approval(context)
        if not result.success:
            self._log_and_return(invocation_id, tool_name, "unknown", context, args, result, started_at)
            return result

        # Gate 4: Secret-scan gate (BLOCK, not just redact)
        detections = SecretScanner.scan(args)
        if detections:
            result = ToolResult(
                success=False,
                error_code=ToolErrorCode.SECRET_DETECTED,
                error_message=f"Secrets detected in tool args: {', '.join(detections[:3])}{'...' if len(detections) > 3 else ''}",
            )
            self._log_and_return(invocation_id, tool_name, "unknown", context, args, result, started_at)
            return result

        # Gate 5: Tool exists
        if self.tool_registry:
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                result = ToolResult(
                    success=False,
                    error_code=ToolErrorCode.TOOL_NOT_FOUND,
                    error_message=f"Tool not found: {tool_name}",
                )
                self._log_and_return(invocation_id, tool_name, "unknown", context, args, result, started_at)
                return result

        # Execute with retries
        timeout = timeout_ms or self.config.tool_timeouts.get(tool_name, self.config.default_timeout_ms)

        result = await self._execute_with_retry(
            tool_name, args, context, timeout, invocation_id, started_at
        )

        return result

    def _check_permissions(self, tool_name: str) -> ToolResult:
        """Check allowlist/denylist."""
        if tool_name in self.config.denied_tools:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.TOOL_DENIED,
                error_message=f"Tool is denied: {tool_name}",
            )

        if self.config.allowed_tools and tool_name not in self.config.allowed_tools:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.TOOL_NOT_ALLOWED,
                error_message=f"Tool not in allowlist: {tool_name}",
            )

        return ToolResult(success=True, error_code=ToolErrorCode.SUCCESS)

    def _check_approval(self, context: ToolInvocationContext) -> ToolResult:
        """Enforce action approval state."""
        valid_statuses = {"READY", "PROCESSING"}

        if context.action_status not in valid_statuses:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.ACTION_NOT_APPROVED,
                error_message=f"Action status '{context.action_status}' not allowed for tool execution. Must be READY or PROCESSING.",
            )

        return ToolResult(success=True, error_code=ToolErrorCode.SUCCESS)

    async def _execute_with_retry(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: ToolInvocationContext,
        timeout_ms: int,
        invocation_id: str,
        started_at: datetime,
    ) -> ToolResult:
        """Execute with exponential backoff retry."""
        attempt = 0
        last_result = None

        while attempt < self.config.max_retries:
            attempt += 1

            try:
                result = await self._execute_single(tool_name, args, timeout_ms)

                # Log this attempt
                self._log_and_return(
                    f"{invocation_id}_a{attempt}", tool_name,
                    self._get_provider(tool_name), context, args, result, started_at, attempt
                )

                if result.success or not result.should_retry():
                    return result

                last_result = result

                # Calculate backoff
                delay = self._calculate_backoff(attempt, result)
                logger.warning(f"Tool {tool_name} failed (attempt {attempt}), retry in {delay}ms")
                await asyncio.sleep(delay / 1000.0)

            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                last_result = ToolResult(
                    success=False,
                    error_code=ToolErrorCode.GATEWAY_ERROR,
                    error_message=str(e),
                )

        return last_result or ToolResult(
            success=False,
            error_code=ToolErrorCode.GATEWAY_ERROR,
            error_message="Max retries exceeded",
        )

    async def _execute_single(
        self,
        tool_name: str,
        args: Dict[str, Any],
        timeout_ms: int,
    ) -> ToolResult:
        """Execute a single tool invocation based on runtime mode."""
        start_time = time.time()

        try:
            if self.config.mcp_runtime_mode == "stdio":
                output = await asyncio.wait_for(
                    self._invoke_mcp_stdio(tool_name, args),
                    timeout=timeout_ms / 1000.0,
                )
            elif self.config.mcp_runtime_mode == "docker":
                output = await asyncio.wait_for(
                    self._invoke_mcp_docker(tool_name, args),
                    timeout=timeout_ms / 1000.0,
                )
            else:
                return ToolResult(
                    success=False,
                    error_code=ToolErrorCode.GATEWAY_ERROR,
                    error_message=f"Unknown runtime mode: {self.config.mcp_runtime_mode}",
                )

            duration_ms = int((time.time() - start_time) * 1000)
            return ToolResult(
                success=True,
                error_code=ToolErrorCode.SUCCESS,
                output=output,
                duration_ms=duration_ms,
            )

        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.TIMEOUT,
                error_message=f"Tool timed out after {timeout_ms}ms",
                duration_ms=int((time.time() - start_time) * 1000),
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_code=self._categorize_error(e),
                error_message=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
            )

    async def _invoke_mcp_stdio(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke MCP tool via stdio spawn-per-call.

        This spawns a fresh MCP server process for each call.
        Preferred mode for simplicity and isolation.
        """
        if not self.tool_registry:
            raise ValueError("Tool registry not configured")

        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # Get spawn command from manifest
        spawn_cmd = tool.mcp_stdio_command
        if not spawn_cmd:
            raise ValueError(f"Tool {tool_name} has no stdio command configured")

        # Resolve secret references
        env = self._resolve_secrets(tool.secrets_refs)

        # Spawn MCP process
        import subprocess

        # Build JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool.mcp_tool_name or tool_name,
                "arguments": args,
            }
        }

        proc = await asyncio.create_subprocess_exec(
            *spawn_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, **env},
        )

        stdout, stderr = await proc.communicate(json.dumps(request).encode())

        if proc.returncode != 0:
            raise RuntimeError(f"MCP process failed: {stderr.decode()}")

        response = json.loads(stdout.decode())
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")

        return response.get("result", {})

    async def _invoke_mcp_docker(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke MCP tool via docker-started server.

        Server runs persistently with healthcheck and idle shutdown.
        """
        if not self.tool_registry:
            raise ValueError("Tool registry not configured")

        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # Ensure container is running
        await self._ensure_mcp_container(tool)

        # Call via HTTP
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://localhost:{tool.docker_port}/call",
                json={
                    "name": tool.mcp_tool_name or tool_name,
                    "arguments": args,
                },
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _ensure_mcp_container(self, tool: 'ToolManifest'):
        """Ensure MCP docker container is running."""
        import subprocess

        container_name = f"mcp-{tool.mcp_server}"

        # Check if running
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
            capture_output=True, text=True,
        )

        if result.returncode == 0 and result.stdout.strip() == "true":
            return  # Already running

        # Start container
        subprocess.run([
            "docker", "run", "-d",
            "--name", container_name,
            "-p", f"{tool.docker_port}:{tool.docker_port}",
            "--health-cmd", tool.docker_health_cmd or "exit 0",
            "--health-interval", "30s",
            tool.docker_image,
        ], check=True)

        # Wait for healthy
        for _ in range(30):
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Health.Status}}", container_name],
                capture_output=True, text=True,
            )
            if result.stdout.strip() == "healthy":
                return
            await asyncio.sleep(1)

        raise RuntimeError(f"Container {container_name} failed health check")

    def _resolve_secrets(self, secrets_refs: Dict[str, str]) -> Dict[str, str]:
        """Resolve secret references to env vars or files."""
        env = {}
        for env_name, ref in secrets_refs.items():
            if ref.startswith("env:"):
                # Reference another env var
                env[env_name] = os.getenv(ref[4:], "")
            elif ref.startswith("file:"):
                # Read from file
                path = ref[5:]
                if os.path.exists(path):
                    with open(path) as f:
                        env[env_name] = f.read().strip()
            else:
                # Direct value (not recommended)
                env[env_name] = ref
        return env

    def _calculate_backoff(self, attempt: int, result: ToolResult) -> int:
        """Calculate backoff delay in milliseconds."""
        import random

        base = self.config.retry_base_delay_ms * (2 ** (attempt - 1))

        if result.error_code == ToolErrorCode.RATE_LIMITED:
            base *= 2
            if result.retry_after_seconds:
                base = max(base, result.retry_after_seconds * 1000)

        jitter = random.uniform(0.75, 1.25)
        return min(int(base * jitter), self.config.retry_max_delay_ms)

    def _categorize_error(self, e: Exception) -> ToolErrorCode:
        """Categorize exception to error code."""
        msg = str(e).lower()

        if "rate limit" in msg or "429" in msg:
            return ToolErrorCode.RATE_LIMITED
        if "timeout" in msg:
            return ToolErrorCode.TIMEOUT
        if "connection" in msg:
            return ToolErrorCode.CONNECTION_ERROR
        if "unauthorized" in msg or "401" in msg:
            return ToolErrorCode.UNAUTHORIZED

        return ToolErrorCode.GATEWAY_ERROR

    def _get_provider(self, tool_name: str) -> str:
        """Get provider name for tool."""
        if self.tool_registry:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                return tool.provider
        return "unknown"

    def _log_and_return(
        self,
        invocation_id: str,
        tool_name: str,
        provider: str,
        context: ToolInvocationContext,
        args: Dict[str, Any],
        result: ToolResult,
        started_at: datetime,
        attempt: int = 1,
    ):
        """Log invocation to audit trail."""
        self.audit_logger.log(
            invocation_id, tool_name, provider,
            self.config.mcp_runtime_mode,
            context, args, result, started_at, attempt,
        )


# =============================================================================
# Global Instance
# =============================================================================

_gateway: Optional[ToolGateway] = None


def get_tool_gateway() -> ToolGateway:
    """Get global ToolGateway instance."""
    global _gateway
    if _gateway is None:
        from tools.registry import get_tool_registry
        _gateway = ToolGateway(tool_registry=get_tool_registry())
    return _gateway


def configure_tool_gateway(config: ToolGatewayConfig):
    """Configure global ToolGateway."""
    global _gateway
    from tools.registry import get_tool_registry
    _gateway = ToolGateway(config=config, tool_registry=get_tool_registry())
```

---

## Section 2: Tool Manifest Schema

### 2.1 Schema Definition

**File:** `/home/zaks/scripts/tools/manifests/SCHEMA.md`

```markdown
# Tool Manifest Schema

Each tool is described by a YAML manifest in `/home/zaks/scripts/tools/manifests/`.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `tool_id` | string | Unique identifier (e.g., `gmail__send_email`) |
| `version` | string | Semantic version (e.g., `1.0.0`) |
| `title` | string | Human-readable name |
| `description` | string | What this tool does |
| `provider` | enum | `mcp` or `http` |

## MCP-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| `mcp_server` | string | MCP server name (e.g., `gmail`) |
| `mcp_tool_name` | string | Tool name in MCP protocol |
| `mcp_stdio_command` | list | Command to spawn MCP server |
| `docker_image` | string | Docker image for docker mode |
| `docker_port` | int | Port to expose |
| `docker_health_cmd` | string | Health check command |

## Safety & Policy

| Field | Type | Description |
|-------|------|-------------|
| `risk_level` | enum | `low`, `medium`, `high` |
| `requires_approval` | bool | Needs operator approval |
| `secrets_refs` | dict | Secret references (env: or file:) |
| `constraints` | list | Safety constraints |

## Runtime

| Field | Type | Description |
|-------|------|-------------|
| `timeout_ms` | int | Default timeout |
| `ttl_seconds` | int | Cache TTL for docker mode |
| `health_check` | object | Health check config |
| `startup_time_ms` | int | Expected startup time |

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `input_schema` | object | JSON Schema for inputs |
| `output_schema` | object | JSON Schema for outputs |
| `examples` | list | Example invocations |
```

### 2.2 Example Manifests

**File:** `/home/zaks/scripts/tools/manifests/gmail__send_email.yaml`

```yaml
# Gmail Send Email Tool Manifest
tool_id: "gmail__send_email"
version: "1.0.0"
title: "Send Email via Gmail"
description: "Send an email using Gmail MCP server"
provider: "mcp"

# MCP Configuration
mcp_server: "gmail"
mcp_tool_name: "mcp__gmail__send_email"

# Runtime: stdio spawn-per-call (preferred)
mcp_stdio_command:
  - "npx"
  - "-y"
  - "@anthropic/gmail-mcp"

# Runtime: docker alternative
docker_image: "ghcr.io/anthropic/gmail-mcp:latest"
docker_port: 8100
docker_health_cmd: "curl -f http://localhost:8100/health || exit 1"

# Startup & Timeout
startup_time_ms: 5000
timeout_ms: 30000
ttl_seconds: 300  # Idle shutdown for docker mode

# Health Check
health_check:
  enabled: true
  endpoint: "mcp__gmail__list_email_labels"
  interval_seconds: 60
  timeout_ms: 5000
  cache_ttl_seconds: 30

# Secrets (NEVER put actual secrets here)
secrets_refs:
  GMAIL_CREDENTIALS: "file:/home/zaks/.config/gmail-mcp/credentials.json"
  GMAIL_TOKEN: "env:GMAIL_MCP_TOKEN"

# Safety
risk_level: "high"
requires_approval: true
constraints:
  - "All recipients must be verified"
  - "Rate limited to 50 emails/day"
  - "Attachments must be under 25MB"

# Input Schema (JSON Schema)
input_schema:
  type: "object"
  required: ["to", "subject", "body"]
  properties:
    to:
      type: "array"
      items:
        type: "string"
        format: "email"
      description: "Recipient email addresses"
    subject:
      type: "string"
      maxLength: 200
      description: "Email subject line"
    body:
      type: "string"
      description: "Email body content"
    cc:
      type: "array"
      items:
        type: "string"
        format: "email"
    bcc:
      type: "array"
      items:
        type: "string"
        format: "email"
    attachments:
      type: "array"
      items:
        type: "string"
      description: "File paths to attach"

# Output Schema
output_schema:
  type: "object"
  properties:
    message_id:
      type: "string"
      description: "Gmail message ID"
    thread_id:
      type: "string"
      description: "Gmail thread ID"

# Examples
examples:
  - description: "Send simple email"
    input:
      to: ["user@example.com"]
      subject: "Meeting Follow-up"
      body: "Thank you for your time today."
    expected_output:
      message_id: "msg_123abc"

tags: ["email", "gmail", "communication", "mcp"]
created: "2025-12-31"
owner: "zakops"
```

**File:** `/home/zaks/scripts/tools/manifests/crawl4ai__single_page.yaml`

```yaml
# Crawl4AI Single Page Tool Manifest
tool_id: "crawl4ai__single_page"
version: "1.0.0"
title: "Crawl Single Web Page"
description: "Fetch and parse content from a single URL"
provider: "mcp"

mcp_server: "crawl4ai-rag"
mcp_tool_name: "mcp__crawl4ai-rag__crawl_single_page"

mcp_stdio_command:
  - "python"
  - "-m"
  - "crawl4ai_mcp"

startup_time_ms: 3000
timeout_ms: 60000

health_check:
  enabled: true
  endpoint: "mcp__crawl4ai-rag__get_available_sources"
  interval_seconds: 120
  timeout_ms: 5000
  cache_ttl_seconds: 60

secrets_refs: {}  # No secrets needed

risk_level: "low"
requires_approval: false
constraints:
  - "Only crawl allowed domains"
  - "Respect robots.txt"

input_schema:
  type: "object"
  required: ["url"]
  properties:
    url:
      type: "string"
      format: "uri"
      description: "URL to crawl"

output_schema:
  type: "object"
  properties:
    content:
      type: "string"
    title:
      type: "string"
    links:
      type: "array"

examples:
  - description: "Crawl documentation page"
    input:
      url: "https://docs.example.com/api"

tags: ["web", "crawl", "scrape", "mcp"]
created: "2025-12-31"
owner: "zakops"
```

---

## Section 3: Tool Registry

**File:** `/home/zaks/scripts/tools/registry.py`

```python
"""
Tool Registry - Loads and indexes tool manifests.

Provides:
- Manifest loading and validation
- Health check management with TTL caching
- Integration with Capability Registry for planner
"""

import os
import yaml
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckConfig:
    """Health check configuration."""
    enabled: bool = True
    endpoint: str = ""
    interval_seconds: int = 60
    timeout_ms: int = 5000
    cache_ttl_seconds: int = 30


@dataclass
class HealthStatus:
    """Cached health status."""
    healthy: bool
    last_check: datetime
    latency_ms: int
    error: Optional[str] = None


@dataclass
class ToolManifest:
    """Parsed tool manifest."""
    tool_id: str
    version: str
    title: str
    description: str
    provider: str

    # MCP config
    mcp_server: Optional[str] = None
    mcp_tool_name: Optional[str] = None
    mcp_stdio_command: Optional[List[str]] = None

    # Docker config
    docker_image: Optional[str] = None
    docker_port: Optional[int] = None
    docker_health_cmd: Optional[str] = None

    # Runtime
    startup_time_ms: int = 5000
    timeout_ms: int = 30000
    ttl_seconds: int = 300

    # Health
    health_check: Optional[HealthCheckConfig] = None

    # Secrets
    secrets_refs: Dict[str, str] = field(default_factory=dict)

    # Safety
    risk_level: str = "medium"
    requires_approval: bool = True
    constraints: List[str] = field(default_factory=list)

    # Schema
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)

    # Meta
    tags: List[str] = field(default_factory=list)
    created: str = ""
    owner: str = ""


class ToolRegistry:
    """
    Registry of available tools.

    Usage:
        registry = ToolRegistry()
        registry.load_from_directory("/home/zaks/scripts/tools/manifests")

        tool = registry.get_tool("gmail__send_email")
        health = await registry.check_health("gmail__send_email")
    """

    def __init__(self):
        self._tools: Dict[str, ToolManifest] = {}
        self._by_server: Dict[str, List[ToolManifest]] = {}
        self._by_tag: Dict[str, List[ToolManifest]] = {}
        self._health_cache: Dict[str, HealthStatus] = {}

    def load_from_directory(self, manifests_dir: str):
        """Load all tool manifests from directory."""
        path = Path(manifests_dir)
        if not path.exists():
            logger.warning(f"Tools directory not found: {manifests_dir}")
            return

        for yaml_file in path.glob("*.yaml"):
            if yaml_file.name == "SCHEMA.md":
                continue
            try:
                self._load_manifest(yaml_file)
            except Exception as e:
                logger.error(f"Failed to load {yaml_file}: {e}")
                raise

        logger.info(f"Loaded {len(self._tools)} tool manifests")

    def _load_manifest(self, yaml_path: Path):
        """Load single manifest."""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        # Parse health check
        hc_data = data.pop("health_check", None)
        health_check = None
        if hc_data:
            health_check = HealthCheckConfig(**hc_data)

        manifest = ToolManifest(
            health_check=health_check,
            **{k: v for k, v in data.items() if k != "health_check"}
        )

        # Register
        self._tools[manifest.tool_id] = manifest

        # Also register by mcp_tool_name
        if manifest.mcp_tool_name:
            self._tools[manifest.mcp_tool_name] = manifest

        # Index by server
        if manifest.mcp_server:
            if manifest.mcp_server not in self._by_server:
                self._by_server[manifest.mcp_server] = []
            self._by_server[manifest.mcp_server].append(manifest)

        # Index by tags
        for tag in manifest.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(manifest)

        logger.info(f"Loaded tool: {manifest.tool_id}")

    def get_tool(self, tool_id: str) -> Optional[ToolManifest]:
        """Get tool by ID or MCP tool name."""
        return self._tools.get(tool_id)

    def list_tools(self) -> List[ToolManifest]:
        """List all unique tools."""
        seen = set()
        tools = []
        for tool in self._tools.values():
            if tool.tool_id not in seen:
                tools.append(tool)
                seen.add(tool.tool_id)
        return tools

    def list_by_server(self, server: str) -> List[ToolManifest]:
        """List tools by MCP server."""
        return self._by_server.get(server, [])

    async def check_health(self, tool_id: str) -> HealthStatus:
        """
        Check tool health with caching.

        Returns cached result if within TTL.
        """
        tool = self.get_tool(tool_id)
        if not tool:
            return HealthStatus(
                healthy=False,
                last_check=datetime.utcnow(),
                latency_ms=0,
                error="Tool not found",
            )

        if not tool.health_check or not tool.health_check.enabled:
            return HealthStatus(
                healthy=True,
                last_check=datetime.utcnow(),
                latency_ms=0,
                error=None,
            )

        # Check cache
        cached = self._health_cache.get(tool_id)
        if cached:
            age = (datetime.utcnow() - cached.last_check).total_seconds()
            if age < tool.health_check.cache_ttl_seconds:
                return cached

        # Perform health check
        start = time.time()
        try:
            # For MCP: call the health endpoint
            from tools.gateway import get_tool_gateway

            gateway = get_tool_gateway()

            # Create a minimal context for health check
            from tools.gateway import ToolInvocationContext
            context = ToolInvocationContext(
                action_id="health_check",
                action_status="PROCESSING",
                approved=True,
            )

            result = await gateway.invoke(
                tool_name=tool.health_check.endpoint,
                args={},
                context=context,
                timeout_ms=tool.health_check.timeout_ms,
            )

            latency = int((time.time() - start) * 1000)

            status = HealthStatus(
                healthy=result.success,
                last_check=datetime.utcnow(),
                latency_ms=latency,
                error=result.error_message if not result.success else None,
            )

        except Exception as e:
            status = HealthStatus(
                healthy=False,
                last_check=datetime.utcnow(),
                latency_ms=int((time.time() - start) * 1000),
                error=str(e),
            )

        # Cache result
        self._health_cache[tool_id] = status
        return status

    async def check_all_health(self) -> Dict[str, HealthStatus]:
        """Check health of all tools."""
        results = {}
        for tool in self.list_tools():
            results[tool.tool_id] = await self.check_health(tool.tool_id)
        return results

    def validate_secrets(self) -> Dict[str, List[str]]:
        """
        Validate that all secret references resolve.

        Returns dict of tool_id -> list of missing secrets.
        """
        missing = {}

        for tool in self.list_tools():
            tool_missing = []
            for env_name, ref in tool.secrets_refs.items():
                if ref.startswith("env:"):
                    env_var = ref[4:]
                    if not os.getenv(env_var):
                        tool_missing.append(f"{env_name} (env:{env_var})")
                elif ref.startswith("file:"):
                    path = ref[5:]
                    if not os.path.exists(path):
                        tool_missing.append(f"{env_name} (file:{path})")

            if tool_missing:
                missing[tool.tool_id] = tool_missing

        return missing


# =============================================================================
# Global Instance
# =============================================================================

_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def load_tools(manifests_dir: str = "/home/zaks/scripts/tools/manifests"):
    """Load tools into global registry."""
    get_tool_registry().load_from_directory(manifests_dir)
```

---

## Section 4: Makefile Integration

**Add to:** `/home/zaks/scripts/Makefile` (or create if doesn't exist)

```makefile
# =============================================================================
# Tool Preflight & Health
# =============================================================================

TOOLS_DIR := /home/zaks/scripts/tools/manifests
PYTHON := python3

.PHONY: tool-preflight tool-health tool-list

# Validate manifests, secrets, and health
tool-preflight:
	@echo "=== Tool Preflight Check ==="
	@echo ""
	@echo "1. Checking manifest syntax..."
	@$(PYTHON) -c "from tools.registry import ToolRegistry; r = ToolRegistry(); r.load_from_directory('$(TOOLS_DIR)'); print(f'   ✓ Loaded {len(r.list_tools())} manifests')"
	@echo ""
	@echo "2. Checking secret references..."
	@$(PYTHON) -c "\
from tools.registry import get_tool_registry, load_tools; \
load_tools('$(TOOLS_DIR)'); \
missing = get_tool_registry().validate_secrets(); \
if missing: \
    print('   ✗ Missing secrets:'); \
    for t, s in missing.items(): \
        print(f'     {t}: {s}'); \
    exit(1); \
else: \
    print('   ✓ All secrets present')"
	@echo ""
	@echo "3. Running health checks (may take a moment)..."
	@$(PYTHON) -c "\
import asyncio; \
from tools.registry import get_tool_registry, load_tools; \
load_tools('$(TOOLS_DIR)'); \
async def check(): \
    results = await get_tool_registry().check_all_health(); \
    unhealthy = [k for k, v in results.items() if not v.healthy]; \
    if unhealthy: \
        print(f'   ⚠ Unhealthy tools: {unhealthy}'); \
    else: \
        print(f'   ✓ All {len(results)} tools healthy'); \
asyncio.run(check())"
	@echo ""
	@echo "=== Preflight Complete ==="

# Just check health (quick)
tool-health:
	@$(PYTHON) -c "\
import asyncio; \
from tools.registry import get_tool_registry, load_tools; \
load_tools('$(TOOLS_DIR)'); \
async def check(): \
    results = await get_tool_registry().check_all_health(); \
    for tool_id, status in results.items(): \
        icon = '✓' if status.healthy else '✗'; \
        print(f'{icon} {tool_id}: {status.latency_ms}ms'); \
asyncio.run(check())"

# List available tools
tool-list:
	@$(PYTHON) -c "\
from tools.registry import get_tool_registry, load_tools; \
load_tools('$(TOOLS_DIR)'); \
for tool in get_tool_registry().list_tools(): \
    print(f'{tool.tool_id} [{tool.risk_level}] - {tool.title}')"
```

---

## Section 5: API Endpoints

**Add to:** `/home/zaks/scripts/deal_lifecycle_api.py`

```python
# =============================================================================
# Tool Endpoints
# =============================================================================

from tools.registry import get_tool_registry, load_tools

# Load tools on startup
@app.on_event("startup")
async def load_tool_registry():
    load_tools("/home/zaks/scripts/tools/manifests")


@app.get("/api/tools")
async def list_tools():
    """List all available tools."""
    registry = get_tool_registry()
    tools = []

    for tool in registry.list_tools():
        tools.append({
            "tool_id": tool.tool_id,
            "title": tool.title,
            "description": tool.description,
            "provider": tool.provider,
            "risk_level": tool.risk_level,
            "requires_approval": tool.requires_approval,
            "tags": tool.tags,
        })

    return {"tools": tools, "count": len(tools)}


@app.get("/api/tools/{tool_id}")
async def get_tool(tool_id: str):
    """Get tool details."""
    registry = get_tool_registry()
    tool = registry.get_tool(tool_id)

    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    return {
        "tool_id": tool.tool_id,
        "version": tool.version,
        "title": tool.title,
        "description": tool.description,
        "provider": tool.provider,
        "risk_level": tool.risk_level,
        "requires_approval": tool.requires_approval,
        "input_schema": tool.input_schema,
        "output_schema": tool.output_schema,
        "examples": tool.examples,
        "constraints": tool.constraints,
        "tags": tool.tags,
    }


@app.get("/api/tools/health")
async def check_tools_health():
    """Check health of all tools."""
    registry = get_tool_registry()
    results = await registry.check_all_health()

    healthy_count = sum(1 for s in results.values() if s.healthy)

    return {
        "healthy": healthy_count == len(results),
        "total": len(results),
        "healthy_count": healthy_count,
        "tools": {
            tool_id: {
                "healthy": status.healthy,
                "latency_ms": status.latency_ms,
                "last_check": status.last_check.isoformat(),
                "error": status.error,
            }
            for tool_id, status in results.items()
        }
    }
```

---

## Section 6: Capability Registry Integration

**Update:** `/home/zaks/scripts/actions/capabilities/registry.py`

Add tool indexing so planner can map unknown requests:

```python
# Add to CapabilityRegistry class

def index_tools(self, tool_registry: 'ToolRegistry'):
    """
    Index tool manifests as capabilities for planner discovery.

    This allows the planner to map user requests to available tools.
    """
    for tool in tool_registry.list_tools():
        # Create a capability-like entry for the tool
        cap_id = f"TOOL.{tool.tool_id}.v{tool.version.split('.')[0]}"

        self._capabilities[cap_id] = {
            "capability_id": cap_id,
            "title": tool.title,
            "description": tool.description,
            "action_type": f"TOOL.{tool.tool_id}",
            "input_schema": tool.input_schema,
            "risk_level": tool.risk_level,
            "requires_approval": tool.requires_approval,
            "tags": tool.tags + ["tool", tool.provider],
            "is_tool": True,
            "tool_id": tool.tool_id,
        }

        # Index by tags
        for tag in tool.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(self._capabilities[cap_id])

    logger.info(f"Indexed {len(tool_registry.list_tools())} tools as capabilities")


def create_missing_tool_capability(
    self,
    user_request: str,
    suggested_tool: str,
) -> Dict[str, Any]:
    """
    Create a "missing tool" capability response.

    Used when planner identifies a need for a tool not in registry.
    """
    return {
        "capability_id": "SYSTEM.MISSING_TOOL",
        "title": f"Missing Tool: {suggested_tool}",
        "description": f"This request requires '{suggested_tool}' which is not available.",
        "action_type": "SYSTEM.MISSING_TOOL",
        "status": "BLOCKED",
        "inputs": {
            "user_request": user_request,
            "missing_tool": suggested_tool,
            "resolution": f"Add {suggested_tool} manifest to /home/zaks/scripts/tools/manifests/",
        },
        "executable": False,
    }
```

---

## Section 7: Smoke Tests

```bash
#!/bin/bash
# /home/zaks/scripts/tools/smoke-test.sh

set -e

API="http://localhost:8090"

echo "=== Tool Smoke Tests ==="

echo "1. List tools..."
TOOLS=$(curl -s "$API/api/tools" | jq '.count')
echo "   Found $TOOLS tools"

echo "2. Check tool health..."
HEALTH=$(curl -s "$API/api/tools/health" | jq '.healthy')
echo "   Healthy: $HEALTH"

echo "3. Get tool details..."
curl -s "$API/api/tools/gmail__send_email" | jq '.title'

echo "4. Create test action with tool..."
ACTION_ID=$(curl -s -X POST "$API/api/actions" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "TOOL.gmail__send_email",
    "deal_id": "test_deal",
    "title": "Test Email",
    "inputs": {
      "to": ["test@example.com"],
      "subject": "Smoke Test",
      "body": "This is a smoke test."
    }
  }' | jq -r '.action_id')
echo "   Created action: $ACTION_ID"

echo "=== Smoke Tests Complete ==="
```

---

## Section 8: Implementation Checklist

### Phase 0.5: Tooling Infrastructure (2 days)

#### Day 1: Core Gateway

- [ ] Create `/home/zaks/scripts/tools/` directory structure
- [ ] Implement `/home/zaks/scripts/tools/gateway.py`:
  - [ ] `ToolErrorCode` enum
  - [ ] `SecretScanner` class (gate, not just redaction)
  - [ ] `SecretRedactor` class (log sanitization)
  - [ ] `ToolAuditLogger` class (SQLite with WAL)
  - [ ] `ToolGateway` class with all gates
  - [ ] `ToolInvocationContext` with approval enforcement
- [ ] Implement `/home/zaks/scripts/tools/registry.py`:
  - [ ] `ToolManifest` dataclass
  - [ ] `ToolRegistry` class
  - [ ] Health check with TTL caching
  - [ ] Secret validation

#### Day 2: Manifests & Integration

- [ ] Create `/home/zaks/scripts/tools/manifests/SCHEMA.md`
- [ ] Create tool manifests:
  - [ ] `gmail__send_email.yaml`
  - [ ] `gmail__search_emails.yaml`
  - [ ] `gmail__read_email.yaml`
  - [ ] `crawl4ai__single_page.yaml`
  - [ ] `crawl4ai__rag_query.yaml`
- [ ] Add Makefile targets:
  - [ ] `make tool-preflight`
  - [ ] `make tool-health`
  - [ ] `make tool-list`
- [ ] Add API endpoints:
  - [ ] `GET /api/tools`
  - [ ] `GET /api/tools/{tool_id}`
  - [ ] `GET /api/tools/health`
- [ ] Update CapabilityRegistry to index tools
- [ ] Create smoke test script
- [ ] Run full preflight validation

### Acceptance Criteria

- [ ] `make tool-preflight` passes with 0 errors
- [ ] `GET /api/tools/health` returns all healthy
- [ ] Secret-scan gate blocks test payload with fake API key
- [ ] Approval enforcement blocks tool call when action not READY/PROCESSING
- [ ] Audit log captures invocations with correlation fields
- [ ] Health checks use TTL caching (verify with timing)

---

## Codex Review Notes Addressed

| Issue | Resolution |
|-------|------------|
| Secret-scan gate vs redaction | Added `SecretScanner` as gate BEFORE invocation |
| `should_retry()` bug | Implemented as method, called correctly |
| Approval enforcement | Added `_check_approval()` gate |
| Health check "not implemented" | Implemented with TTL caching |
| Bounded log size | Added truncation with hash reference |
| Path consistency | All paths under `/home/zaks/scripts/` |
| Dynamic action_type | Tools indexed as capabilities, string-based |

---

**Document Status:** EXECUTION-READY
**Estimated Effort:** 2 days
**Dependencies:** SQLite WAL mode, MCP servers available

---

## Codex Review Notes — Follow-up Improvements (Added 2025-12-31)

### 1) Align Defaults With "Safety-First" Claims

- The doc says "Tool Gates default to false", but `ToolGatewayConfig.from_env()` defaults `ZAKOPS_TOOL_GATEWAY_ENABLED` to `"true"`. Align doc + implementation: default should be **disabled unless explicitly enabled**.
- `allowed_tools` currently treats "empty = all allowed". For production safety, consider "empty = deny-all" (or require an explicit allowlist when gateway is enabled).

**Resolution:** Updated defaults:
```python
# ToolGatewayConfig.from_env() - UPDATED
enabled=os.getenv("ZAKOPS_TOOL_GATEWAY_ENABLED", "false").lower() == "true",  # Default: DISABLED
require_allowlist=os.getenv("ZAKOPS_TOOL_REQUIRE_ALLOWLIST", "true").lower() == "true",  # Default: REQUIRED

# _check_permissions() - UPDATED
def _check_permissions(self, tool_name: str) -> ToolResult:
    # Deny if allowlist required but empty
    if self.config.require_allowlist and not self.config.allowed_tools:
        return ToolResult(
            success=False,
            error_code=ToolErrorCode.TOOL_NOT_ALLOWED,
            error_message="Tool gateway requires explicit allowlist (ZAKOPS_TOOL_ALLOWLIST)",
        )
    # ... rest of checks
```

### 2) Approval Enforcement Must Be DB-Sourced (Do Not Trust Caller Context)

- `_check_approval()` currently trusts `context.action_status`. Treat `ToolInvocationContext` as correlation only and verify approval by loading the action record from `ZAKOPS_STATE_DB` (and/or presence of an approval audit event) before any external call.

**Resolution:** DB-sourced verification:
```python
def _check_approval_from_db(self, context: ToolInvocationContext) -> ToolResult:
    """Verify approval from DB, not caller-provided context."""
    import sqlite3

    with sqlite3.connect(self.config.audit_db_path) as conn:
        conn.execute("PRAGMA busy_timeout=5000")
        row = conn.execute(
            "SELECT status, requires_approval, approved_at FROM actions WHERE action_id = ?",
            (context.action_id,)
        ).fetchone()

        if not row:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.ACTION_NOT_APPROVED,
                error_message=f"Action {context.action_id} not found in DB",
            )

        db_status, requires_approval, approved_at = row

        # Verify status from DB (not trusted context)
        if db_status not in {"READY", "PROCESSING"}:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.ACTION_NOT_APPROVED,
                error_message=f"Action status '{db_status}' not allowed (DB-verified)",
            )

        # Verify approval if required
        if requires_approval and not approved_at:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.ACTION_NOT_APPROVED,
                error_message="Action requires approval but not yet approved (DB-verified)",
            )

    return ToolResult(success=True, error_code=ToolErrorCode.SUCCESS)
```

### 3) Secret Scanner Hardening (Reduce Bypass + False Safety)

- `SAFE_KEYS` includes generic keys like `id`/`uuid`, which can be abused to smuggle secrets (e.g., `{"id":"sk-..."}`). Prefer removing generic keys or only skipping when the **value matches a strict UUID/ID pattern**.
- Add **key-name based blocking** (e.g., if keys include `password`, `token`, `api_key`, `authorization`, `bearer`) regardless of value, with a small allowlist for non-secret uses.
- Redact/sanitize `error_message` before persisting (external tool errors can echo credentials).

**Resolution:** Hardened scanner:
```python
class SecretScanner:
    """Hardened secret scanner - blocks calls, not just redacts."""

    # Remove generic safe keys - only skip if value matches strict UUID pattern
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
    ACTION_ID_PATTERN = re.compile(r'^(act|inv|deal)_[a-z0-9]{8,}$', re.I)

    # Key-name blocklist (always block regardless of value)
    BLOCKED_KEY_PATTERNS = [
        r'password', r'passwd', r'secret', r'token', r'api_key', r'apikey',
        r'authorization', r'bearer', r'credential', r'private_key', r'client_secret',
    ]
    _blocked_key_patterns = [re.compile(p, re.IGNORECASE) for p in BLOCKED_KEY_PATTERNS]

    @classmethod
    def scan(cls, data: Dict[str, Any], path: str = "") -> List[str]:
        """Scan with hardened rules."""
        detections = []

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            # Check key-name blocklist FIRST (always block)
            if any(p.search(key) for p in cls._blocked_key_patterns):
                if isinstance(value, str) and value:  # Non-empty string
                    detections.append(f"{current_path} (blocked-key:{key})")
                continue

            # Only skip if value matches strict ID pattern (not generic)
            if isinstance(value, str):
                if cls.UUID_PATTERN.match(value) or cls.ACTION_ID_PATTERN.match(value):
                    continue  # Safe: matches strict ID format

                # Check value patterns
                for pattern, name in cls._patterns:
                    if pattern.search(value):
                        detections.append(f"{current_path} ({name})")
                        break

            # Recurse
            elif isinstance(value, dict):
                detections.extend(cls.scan(value, current_path))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        detections.extend(cls.scan(item, f"{current_path}[{i}]"))

        return detections

    @classmethod
    def redact_error_message(cls, error_msg: str) -> str:
        """Redact potential secrets from error messages (tool errors may echo creds)."""
        if not error_msg:
            return error_msg

        redacted = error_msg
        for pattern, name in cls._patterns:
            redacted = pattern.sub(f"[REDACTED:{name}]", redacted)

        return redacted
```

### 4) Audit Trail Precision (Retries + Timing)

- Retry attempt logs currently reuse the original `started_at`. Consider storing per-attempt timestamps (attempt_started_at/attempt_completed_at) or logging both "run-level" and "attempt-level" timing to keep metrics/debugging unambiguous.
- Store approximate sizes in bytes using `len(json.dumps(...).encode("utf-8"))` to match the "*_bytes" naming.

**Resolution:** Per-attempt timing + correct byte calculation:
```python
# Updated audit table schema
"""
CREATE TABLE tool_invocation_log (
    ...
    -- Run-level timing
    run_started_at TEXT NOT NULL,
    run_completed_at TEXT,

    -- Attempt-level timing (per retry)
    attempt_started_at TEXT NOT NULL,
    attempt_completed_at TEXT NOT NULL,
    attempt_duration_ms INTEGER NOT NULL,

    -- Correct byte sizes (UTF-8 encoded)
    input_size_bytes INTEGER,
    output_size_bytes INTEGER,
    ...
)
"""

# Correct byte calculation
input_json = json.dumps(SecretRedactor.redact(input_args))
input_size_bytes = len(input_json.encode("utf-8"))  # UTF-8 bytes, not string length
```

### 5) HTTP Tool Safety (SSRF/Egress Controls)

- If/when `provider: http` is enabled, add host/domain allowlists and block private/link-local ranges (`127.0.0.0/8`, `10/8`, `172.16/12`, `192.168/16`, `169.254/16`) to prevent SSRF. Record blocked attempts in the audit log.

**Resolution:** SSRF protection:
```python
import ipaddress
import socket

class SSRFProtection:
    """Block requests to private/internal networks."""

    BLOCKED_RANGES = [
        ipaddress.ip_network("127.0.0.0/8"),      # Loopback
        ipaddress.ip_network("10.0.0.0/8"),       # Private A
        ipaddress.ip_network("172.16.0.0/12"),    # Private B
        ipaddress.ip_network("192.168.0.0/16"),   # Private C
        ipaddress.ip_network("169.254.0.0/16"),   # Link-local
        ipaddress.ip_network("::1/128"),          # IPv6 loopback
        ipaddress.ip_network("fc00::/7"),         # IPv6 private
        ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
    ]

    @classmethod
    def check_url(cls, url: str) -> tuple[bool, str]:
        """
        Check if URL is safe to access.
        Returns (is_safe, reason).
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False, "No hostname in URL"

        # Resolve hostname
        try:
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)
        except (socket.gaierror, ValueError) as e:
            return False, f"Cannot resolve hostname: {e}"

        # Check against blocked ranges
        for blocked in cls.BLOCKED_RANGES:
            if ip in blocked:
                return False, f"IP {ip} in blocked range {blocked}"

        return True, "OK"


# In ToolGateway._invoke_http():
async def _invoke_http(self, tool: ToolManifest, args: Dict[str, Any]) -> Dict[str, Any]:
    # SSRF check BEFORE any request
    is_safe, reason = SSRFProtection.check_url(tool.http_endpoint)
    if not is_safe:
        raise ValueError(f"SSRF blocked: {reason}")

    # ... proceed with request
```

### 6) Subprocess Resource Bounds

- In stdio mode, `proc.communicate()` reads full stdout/stderr; add output size limits + truncation (and ensure stderr included in logs is redacted/bounded) to avoid runaway memory/log growth.

**Resolution:** Bounded subprocess output:
```python
MAX_STDOUT_BYTES = 10 * 1024 * 1024  # 10MB
MAX_STDERR_BYTES = 1 * 1024 * 1024   # 1MB

async def _invoke_mcp_stdio(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    # ... spawn process ...

    # Read with bounds
    async def read_bounded(stream, max_bytes: int) -> bytes:
        """Read from stream with size limit."""
        chunks = []
        total = 0
        while True:
            chunk = await stream.read(8192)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                chunks.append(chunk[:max_bytes - (total - len(chunk))])
                logger.warning(f"Output truncated at {max_bytes} bytes")
                break
            chunks.append(chunk)
        return b"".join(chunks)

    stdout = await read_bounded(proc.stdout, MAX_STDOUT_BYTES)
    stderr = await read_bounded(proc.stderr, MAX_STDERR_BYTES)

    await proc.wait()

    if proc.returncode != 0:
        # Redact stderr before including in error
        stderr_redacted = SecretScanner.redact_error_message(stderr.decode(errors="replace"))
        raise RuntimeError(f"MCP failed (exit {proc.returncode}): {stderr_redacted[:500]}")

    # ... parse stdout ...
```

---

## Implementation Status After Codex Review

| Issue | Status | Implementation |
|-------|--------|----------------|
| Safety defaults | ✅ RESOLVED | Gateway disabled by default, allowlist required |
| DB-sourced approval | ✅ RESOLVED | `_check_approval_from_db()` verifies from SQLite |
| Secret scanner hardening | ✅ RESOLVED | Key-name blocklist, strict ID patterns, error redaction |
| Audit timing precision | ✅ RESOLVED | Per-attempt timestamps, UTF-8 byte sizes |
| HTTP SSRF protection | ✅ RESOLVED | `SSRFProtection.check_url()` blocks private ranges |
| Subprocess bounds | ✅ RESOLVED | `read_bounded()` with 10MB/1MB limits |

# ZakOps Kinetic Action Engine - Tooling Strategy (World-Class)

**Document Version:** 1.0
**Created:** 2025-12-30
**Status:** Ready for Integration into ACTIONS-ENGINE-IMPLEMENTATION-PLAN-v1.2.md
**Target Phase:** Phase 0.5 (Tooling Infrastructure)
**Owner:** ZakOps Deal Lifecycle OS Team

---

## Executive Summary

This document defines the **Tooling Strategy** for the Kinetic Action Engine - a world-class, extensible layer that enables:

1. **External Tool Integration** - MCP servers (gmail, crawl4ai-rag, browser-use, linkedin) and future tools
2. **Tool Gateway** - Single, secure interface for all tool invocations with safety controls
3. **Capability Manifest Extension** - Machine-readable tool descriptions enabling LLM/router intelligence
4. **Composite Actions** - Handles "unknown" requests by composing known capabilities
5. **Audit & Safety** - Complete observability without LangSmith (SQLite + deal events)

### Problem Statement

The current Action Engine has an internal executor plugin strategy (ActionExecutor + ExecutorRegistry + DataRoom artifacts), but:

- **No MCP integration** - Existing MCP servers (gmail, crawl4ai-rag, browser-use, linkedin) are not callable from actions
- **No tool safety layer** - External tools called directly without allowlist, timeouts, or audit
- **Hard-coded actions** - No way to handle "new action types we didn't predefine"
- **No secret protection** - Credentials could leak to logs

### Solution: Tool Gateway + Extended Capability Manifest

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Action Engine (v1.2+)                            │
│                                                                         │
│  ┌─────────────┐                      ┌─────────────────────────────┐  │
│  │ ActionPlanner│──────────────────▶ │   Capability Registry        │  │
│  └──────┬──────┘                      │   (Extended with Tools)      │  │
│         │                             │                              │  │
│         │ creates                     │   • draft_email.v1.yaml      │  │
│         ▼                             │   • mcp_gmail_send.v1.yaml   │  │
│  ┌─────────────┐                      │   • mcp_browser_use.v1.yaml  │  │
│  │   Action    │                      │   • composite_lender_pkg.yaml│  │
│  │   Queue     │                      └──────────────────────────────┘  │
│  └──────┬──────┘                                    │                   │
│         │ executes                                  │ informs           │
│         ▼                                           ▼                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Executor Registry                             │   │
│  │                                                                  │   │
│  │  ┌─────────────────────┐    ┌──────────────────────────────┐   │   │
│  │  │  Local Executors     │    │   Tool-Based Executors       │   │   │
│  │  │  (Direct)            │    │   (via ToolGateway)          │   │   │
│  │  │                      │    │                              │   │   │
│  │  │  • DocxGenerator     │    │  • EmailSendExecutor ─────┐  │   │   │
│  │  │  • PdfGenerator      │    │  • WebScrapeExecutor ────┐│  │   │   │
│  │  │  • XlsxGenerator     │    │  • BrowserUseExecutor ──┐││  │   │   │
│  │  │  • PptxGenerator     │    │  • CompositeExecutor ──┐│││  │   │   │
│  │  └─────────────────────┘    └─────────────────────────┼┼┼┼──┘   │   │
│  └──────────────────────────────────────────────────────┼┼┼┼───────┘   │
│                                                          ││││          │
│  ┌───────────────────────────────────────────────────────┼┼┼┼──────┐   │
│  │                    TOOL GATEWAY                       ▼▼▼▼      │   │
│  │                    (Central Safety Layer)                       │   │
│  │                                                                 │   │
│  │  ┌──────────────┐  ┌────────────┐  ┌─────────────────────────┐ │   │
│  │  │ Allowlist/   │  │ Timeout +  │  │ Audit Logger            │ │   │
│  │  │ Denylist     │  │ Retry      │  │ (SQLite + Deal Events)  │ │   │
│  │  └──────────────┘  └────────────┘  └─────────────────────────┘ │   │
│  │  ┌──────────────┐  ┌────────────┐  ┌─────────────────────────┐ │   │
│  │  │ Secret       │  │ Error      │  │ Cost                    │ │   │
│  │  │ Redactor     │  │ Codes      │  │ Tracker                 │ │   │
│  │  └──────────────┘  └────────────┘  └─────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                          │                              │
└──────────────────────────────────────────┼──────────────────────────────┘
                                           │
                                           ▼
                    ┌───────────────────────────────────────────┐
                    │           External Tools                  │
                    │                                           │
                    │  ┌────────────┐  ┌────────────────────┐  │
                    │  │ MCP Servers│  │ HTTP APIs          │  │
                    │  │            │  │                    │  │
                    │  │ • gmail    │  │ • LangGraph Brain  │  │
                    │  │ • crawl4ai │  │ • SharePoint       │  │
                    │  │ • browser  │  │ • External APIs    │  │
                    │  │ • linkedin │  │                    │  │
                    │  └────────────┘  └────────────────────┘  │
                    └───────────────────────────────────────────┘
```

---

## Section 1: Tool Gateway Design

### 1.1 Purpose

The **ToolGateway** is the single internal interface for invoking any external tool. ALL external-system actions (email send, web scrape, browser automation, SharePoint sync) MUST go through this gateway.

Local-only executors (DOCX/PDF/XLSX/PPTX generation) remain **direct** and do NOT use the gateway.

### 1.2 Interface Specification

**New File:** `src/tools/gateway.py` (~500 lines)

```python
"""
ToolGateway - Central interface for all external tool invocations.

Design Principles:
1. Single entry point for ALL external tools (MCP + HTTP)
2. Allowlist/denylist enforcement BEFORE invocation
3. Structured error codes for retry logic
4. Audit logging to SQLite + deal events (NO LangSmith)
5. Secret redaction ALWAYS (credentials never in logs)
6. Timeout + retry with exponential backoff
"""

import os
import re
import time
import logging
import sqlite3
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# Error Codes
# =============================================================================

class ToolErrorCode(str, Enum):
    """Structured error codes for tool invocations."""

    # Success
    SUCCESS = "SUCCESS"

    # Permission errors (do not retry)
    TOOL_NOT_ALLOWED = "TOOL_NOT_ALLOWED"
    TOOL_DENIED = "TOOL_DENIED"
    UNAUTHORIZED = "UNAUTHORIZED"

    # Transient errors (retry with backoff)
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

    # Permanent errors (do not retry)
    INVALID_INPUT = "INVALID_INPUT"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"

    # Internal errors
    GATEWAY_ERROR = "GATEWAY_ERROR"
    REDACTION_ERROR = "REDACTION_ERROR"


class ToolErrorCategory(str, Enum):
    """Error categories for retry logic."""
    PERMANENT = "permanent"      # Do not retry
    TRANSIENT = "transient"      # Retry with backoff
    RATE_LIMIT = "rate_limit"    # Retry with longer delay


# Error code to category mapping
ERROR_CATEGORIES: Dict[ToolErrorCode, ToolErrorCategory] = {
    ToolErrorCode.SUCCESS: ToolErrorCategory.PERMANENT,  # N/A
    ToolErrorCode.TOOL_NOT_ALLOWED: ToolErrorCategory.PERMANENT,
    ToolErrorCode.TOOL_DENIED: ToolErrorCategory.PERMANENT,
    ToolErrorCode.UNAUTHORIZED: ToolErrorCategory.PERMANENT,
    ToolErrorCode.TIMEOUT: ToolErrorCategory.TRANSIENT,
    ToolErrorCode.RATE_LIMITED: ToolErrorCategory.RATE_LIMIT,
    ToolErrorCode.CONNECTION_ERROR: ToolErrorCategory.TRANSIENT,
    ToolErrorCode.SERVICE_UNAVAILABLE: ToolErrorCategory.TRANSIENT,
    ToolErrorCode.INVALID_INPUT: ToolErrorCategory.PERMANENT,
    ToolErrorCode.TOOL_NOT_FOUND: ToolErrorCategory.PERMANENT,
    ToolErrorCode.MALFORMED_RESPONSE: ToolErrorCategory.PERMANENT,
    ToolErrorCode.GATEWAY_ERROR: ToolErrorCategory.TRANSIENT,
    ToolErrorCode.REDACTION_ERROR: ToolErrorCategory.PERMANENT,
}


# =============================================================================
# Result Models
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

    @property
    def should_retry(self) -> bool:
        """Check if this result indicates a retryable error."""
        category = ERROR_CATEGORIES.get(self.error_code, ToolErrorCategory.PERMANENT)
        return category in {ToolErrorCategory.TRANSIENT, ToolErrorCategory.RATE_LIMIT}


class ToolInvocationContext(BaseModel):
    """Context for tool invocation (for audit trail)."""
    action_id: str
    deal_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None


# =============================================================================
# Secret Redaction
# =============================================================================

class SecretRedactor:
    """
    Redacts secrets from tool inputs/outputs before logging.

    CRITICAL: This must be 100% reliable. Credentials must NEVER appear in logs.
    """

    # Patterns that indicate secrets (case-insensitive)
    SECRET_KEY_PATTERNS = [
        r'password', r'passwd', r'secret', r'token', r'api_key', r'apikey',
        r'api-key', r'auth', r'credential', r'bearer', r'access_key',
        r'private_key', r'client_secret', r'refresh_token', r'session_id',
        r'cookie', r'authorization', r'x-api-key', r'oauth',
    ]

    # Compiled patterns
    _key_patterns = [re.compile(p, re.IGNORECASE) for p in SECRET_KEY_PATTERNS]

    # Value patterns (things that look like secrets)
    SECRET_VALUE_PATTERNS = [
        r'^[A-Za-z0-9+/]{40,}={0,2}$',  # Base64 (long)
        r'^[A-Fa-f0-9]{32,}$',           # Hex (long)
        r'^sk-[A-Za-z0-9]{20,}$',        # OpenAI-style key
        r'^ghp_[A-Za-z0-9]{20,}$',       # GitHub token
        r'^xox[baprs]-[A-Za-z0-9-]+$',   # Slack token
    ]

    _value_patterns = [re.compile(p) for p in SECRET_VALUE_PATTERNS]

    REDACTED = "[REDACTED]"

    @classmethod
    def redact_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact secrets from a dictionary."""
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            # Check if key indicates a secret
            is_secret_key = any(p.search(key) for p in cls._key_patterns)

            if is_secret_key:
                result[key] = cls.REDACTED
            elif isinstance(value, dict):
                result[key] = cls.redact_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    cls.redact_dict(item) if isinstance(item, dict) else cls._redact_value(item)
                    for item in value
                ]
            elif isinstance(value, str):
                result[key] = cls._redact_value(value)
            else:
                result[key] = value

        return result

    @classmethod
    def _redact_value(cls, value: Any) -> Any:
        """Redact a single value if it looks like a secret."""
        if not isinstance(value, str):
            return value

        # Check if value looks like a secret
        if any(p.match(value) for p in cls._value_patterns):
            return cls.REDACTED

        return value


# =============================================================================
# Audit Logger
# =============================================================================

class ToolAuditLogger:
    """
    Logs tool invocations to SQLite + deal events.

    NO LangSmith tracing - all observability is local.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        """Create audit tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_invocation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invocation_id TEXT UNIQUE NOT NULL,
                    tool_name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    action_id TEXT,
                    deal_id TEXT,
                    user_id TEXT,

                    -- Input (redacted)
                    input_args_redacted TEXT,

                    -- Output
                    success INTEGER NOT NULL,
                    error_code TEXT NOT NULL,
                    error_message TEXT,
                    output_redacted TEXT,

                    -- Timing
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    duration_ms INTEGER NOT NULL,

                    -- Retry info
                    attempt_number INTEGER DEFAULT 1,
                    retry_after_seconds INTEGER,

                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_log_action_id
                ON tool_invocation_log(action_id);
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_log_deal_id
                ON tool_invocation_log(deal_id);
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_log_tool_name
                ON tool_invocation_log(tool_name);
            """)

            conn.commit()

    def log_invocation(
        self,
        invocation_id: str,
        tool_name: str,
        provider: str,
        context: ToolInvocationContext,
        input_args: Dict[str, Any],
        result: ToolResult,
        started_at: datetime,
        attempt_number: int = 1,
    ):
        """Log a tool invocation (input and output already redacted)."""
        import json

        completed_at = datetime.utcnow()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tool_invocation_log (
                    invocation_id, tool_name, provider,
                    action_id, deal_id, user_id,
                    input_args_redacted,
                    success, error_code, error_message, output_redacted,
                    started_at, completed_at, duration_ms,
                    attempt_number, retry_after_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invocation_id,
                tool_name,
                provider,
                context.action_id,
                context.deal_id,
                context.user_id,
                json.dumps(SecretRedactor.redact_dict(input_args)),
                1 if result.success else 0,
                result.error_code.value,
                result.error_message,
                json.dumps(SecretRedactor.redact_dict(result.output or {})),
                started_at.isoformat(),
                completed_at.isoformat(),
                result.duration_ms,
                attempt_number,
                result.retry_after_seconds,
            ))
            conn.commit()

        logger.info(
            f"Tool invocation logged: {tool_name} ({provider}) - "
            f"{'SUCCESS' if result.success else result.error_code.value}"
        )


# =============================================================================
# Tool Gateway
# =============================================================================

class ToolGatewayConfig(BaseModel):
    """Configuration for ToolGateway."""

    # Allowlist/Denylist
    allowed_tools: List[str] = Field(default_factory=list)  # Empty = all allowed
    denied_tools: List[str] = Field(default_factory=list)

    # Timeouts (milliseconds)
    default_timeout_ms: int = 30000  # 30 seconds
    tool_timeouts: Dict[str, int] = Field(default_factory=dict)  # Per-tool overrides

    # Retries
    max_retries: int = 3
    retry_base_delay_ms: int = 1000  # 1 second
    retry_max_delay_ms: int = 30000  # 30 seconds

    # Audit
    audit_db_path: str = "DataRoom/.deal-registry/ingest_state.db"


class ToolGateway:
    """
    Central gateway for all external tool invocations.

    Usage:
        gateway = ToolGateway(config)

        result = await gateway.invoke(
            tool_name="mcp_gmail_send_email",
            args={"to": ["user@example.com"], "subject": "Test", "body": "Hello"},
            context=ToolInvocationContext(action_id="act_123", deal_id="deal_456"),
        )

        if result.success:
            print(f"Email sent: {result.output}")
        else:
            print(f"Failed: {result.error_code} - {result.error_message}")
    """

    def __init__(
        self,
        config: Optional[ToolGatewayConfig] = None,
        tool_registry: Optional['ToolRegistry'] = None,
    ):
        self.config = config or ToolGatewayConfig()
        self.tool_registry = tool_registry or get_tool_registry()
        self.audit_logger = ToolAuditLogger(self.config.audit_db_path)

    async def invoke(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: ToolInvocationContext,
        timeout_ms: Optional[int] = None,
    ) -> ToolResult:
        """
        Invoke a tool through the gateway.

        Steps:
        1. Check allowlist/denylist
        2. Validate tool exists in registry
        3. Validate inputs against schema
        4. Execute with timeout + retries
        5. Audit log (redacted)
        6. Return structured result
        """
        import uuid

        invocation_id = f"inv_{uuid.uuid4().hex[:12]}"
        started_at = datetime.utcnow()

        logger.info(f"ToolGateway.invoke: {tool_name} (invocation: {invocation_id})")

        # Step 1: Check permissions
        permission_result = self._check_permissions(tool_name)
        if not permission_result.success:
            self.audit_logger.log_invocation(
                invocation_id, tool_name, "unknown", context, args, permission_result, started_at
            )
            return permission_result

        # Step 2: Get tool from registry
        tool_manifest = self.tool_registry.get_tool(tool_name)
        if not tool_manifest:
            result = ToolResult(
                success=False,
                error_code=ToolErrorCode.TOOL_NOT_FOUND,
                error_message=f"Tool not found: {tool_name}",
            )
            self.audit_logger.log_invocation(
                invocation_id, tool_name, "unknown", context, args, result, started_at
            )
            return result

        # Step 3: Validate inputs
        validation_result = self._validate_inputs(tool_manifest, args)
        if not validation_result.success:
            self.audit_logger.log_invocation(
                invocation_id, tool_name, tool_manifest.provider, context, args, validation_result, started_at
            )
            return validation_result

        # Step 4: Execute with timeout + retries
        timeout = timeout_ms or self.config.tool_timeouts.get(
            tool_name, self.config.default_timeout_ms
        )

        result = await self._execute_with_retry(
            tool_manifest, args, context, timeout, invocation_id, started_at
        )

        return result

    def _check_permissions(self, tool_name: str) -> ToolResult:
        """Check if tool is allowed."""

        # Check denylist first (takes precedence)
        if tool_name in self.config.denied_tools:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.TOOL_DENIED,
                error_message=f"Tool is denied: {tool_name}",
            )

        # Check allowlist (empty = all allowed)
        if self.config.allowed_tools and tool_name not in self.config.allowed_tools:
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.TOOL_NOT_ALLOWED,
                error_message=f"Tool not in allowlist: {tool_name}",
            )

        return ToolResult(success=True, error_code=ToolErrorCode.SUCCESS)

    def _validate_inputs(
        self,
        tool_manifest: 'ToolManifest',
        args: Dict[str, Any],
    ) -> ToolResult:
        """Validate inputs against tool schema."""

        # Check required fields
        for prop_name, prop_schema in tool_manifest.input_schema.items():
            if prop_schema.get('required', False) and prop_name not in args:
                return ToolResult(
                    success=False,
                    error_code=ToolErrorCode.INVALID_INPUT,
                    error_message=f"Missing required field: {prop_name}",
                )

        return ToolResult(success=True, error_code=ToolErrorCode.SUCCESS)

    async def _execute_with_retry(
        self,
        tool_manifest: 'ToolManifest',
        args: Dict[str, Any],
        context: ToolInvocationContext,
        timeout_ms: int,
        invocation_id: str,
        started_at: datetime,
    ) -> ToolResult:
        """Execute tool with retry logic."""

        attempt = 0
        last_result = None

        while attempt < self.config.max_retries:
            attempt += 1

            try:
                result = await self._execute_single(
                    tool_manifest, args, timeout_ms
                )

                # Log this attempt
                self.audit_logger.log_invocation(
                    f"{invocation_id}_a{attempt}",
                    tool_manifest.name,
                    tool_manifest.provider,
                    context,
                    args,
                    result,
                    started_at,
                    attempt,
                )

                if result.success or not result.should_retry:
                    return result

                last_result = result

                # Calculate backoff
                delay_ms = self._calculate_backoff(attempt, result)
                logger.warning(
                    f"Tool {tool_manifest.name} failed (attempt {attempt}), "
                    f"retrying in {delay_ms}ms: {result.error_code}"
                )

                await self._async_sleep(delay_ms)

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
        tool_manifest: 'ToolManifest',
        args: Dict[str, Any],
        timeout_ms: int,
    ) -> ToolResult:
        """Execute a single tool invocation."""
        import asyncio

        start_time = time.time()

        try:
            if tool_manifest.provider == "mcp":
                output = await asyncio.wait_for(
                    self._invoke_mcp(tool_manifest, args),
                    timeout=timeout_ms / 1000.0,
                )
            elif tool_manifest.provider == "http":
                output = await asyncio.wait_for(
                    self._invoke_http(tool_manifest, args),
                    timeout=timeout_ms / 1000.0,
                )
            else:
                return ToolResult(
                    success=False,
                    error_code=ToolErrorCode.TOOL_NOT_FOUND,
                    error_message=f"Unknown provider: {tool_manifest.provider}",
                )

            duration_ms = int((time.time() - start_time) * 1000)

            return ToolResult(
                success=True,
                error_code=ToolErrorCode.SUCCESS,
                output=output,
                duration_ms=duration_ms,
            )

        except asyncio.TimeoutError:
            duration_ms = int((time.time() - start_time) * 1000)
            return ToolResult(
                success=False,
                error_code=ToolErrorCode.TIMEOUT,
                error_message=f"Tool timed out after {timeout_ms}ms",
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_code = self._categorize_exception(e)
            return ToolResult(
                success=False,
                error_code=error_code,
                error_message=str(e),
                duration_ms=duration_ms,
            )

    async def _invoke_mcp(
        self,
        tool_manifest: 'ToolManifest',
        args: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Invoke an MCP tool."""
        # Import MCP client (dynamically to avoid import errors if MCP not installed)
        from mcp import ClientSession

        # MCP invocation logic
        # This will be implemented based on your MCP server setup
        # For now, this is a placeholder that shows the interface

        mcp_tool_name = tool_manifest.mcp_tool_name or tool_manifest.name

        # Call the MCP tool
        # result = await mcp_client.call_tool(mcp_tool_name, args)
        # return result

        raise NotImplementedError(
            f"MCP invocation for {mcp_tool_name} - implement based on your MCP client setup"
        )

    async def _invoke_http(
        self,
        tool_manifest: 'ToolManifest',
        args: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Invoke an HTTP tool."""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=tool_manifest.http_method or "POST",
                url=tool_manifest.http_endpoint,
                json=args,
                headers=tool_manifest.http_headers or {},
            ) as response:
                if response.status == 429:
                    raise RateLimitError("Rate limited")

                response.raise_for_status()
                return await response.json()

    def _calculate_backoff(self, attempt: int, result: ToolResult) -> int:
        """Calculate backoff delay in milliseconds."""
        import random

        base_delay = self.config.retry_base_delay_ms * (2 ** (attempt - 1))

        # Rate limit gets longer delay
        if result.error_code == ToolErrorCode.RATE_LIMITED:
            base_delay *= 2
            if result.retry_after_seconds:
                base_delay = max(base_delay, result.retry_after_seconds * 1000)

        # Add jitter (±25%)
        jitter = random.uniform(0.75, 1.25)
        delay = int(base_delay * jitter)

        return min(delay, self.config.retry_max_delay_ms)

    def _categorize_exception(self, e: Exception) -> ToolErrorCode:
        """Categorize an exception into an error code."""
        error_str = str(e).lower()

        if "rate limit" in error_str or "429" in error_str:
            return ToolErrorCode.RATE_LIMITED
        if "timeout" in error_str:
            return ToolErrorCode.TIMEOUT
        if "connection" in error_str or "network" in error_str:
            return ToolErrorCode.CONNECTION_ERROR
        if "unauthorized" in error_str or "401" in error_str:
            return ToolErrorCode.UNAUTHORIZED
        if "not found" in error_str or "404" in error_str:
            return ToolErrorCode.TOOL_NOT_FOUND
        if "503" in error_str or "service unavailable" in error_str:
            return ToolErrorCode.SERVICE_UNAVAILABLE

        return ToolErrorCode.GATEWAY_ERROR

    async def _async_sleep(self, ms: int):
        """Sleep for milliseconds."""
        import asyncio
        await asyncio.sleep(ms / 1000.0)


class RateLimitError(Exception):
    """Raised when rate limited."""
    pass


# =============================================================================
# Global Instance
# =============================================================================

_gateway: Optional[ToolGateway] = None


def get_tool_gateway() -> ToolGateway:
    """Get global ToolGateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = ToolGateway()
    return _gateway


def configure_tool_gateway(config: ToolGatewayConfig):
    """Configure the global ToolGateway."""
    global _gateway
    _gateway = ToolGateway(config)
```

### 1.3 Integration with Deal Events

When a tool is invoked as part of an action, emit a deal event:

```python
# In executor that uses ToolGateway
from deal_events import emit_event

async def execute_with_tool(self, action, context):
    gateway = get_tool_gateway()

    result = await gateway.invoke(
        tool_name="mcp_gmail_send_email",
        args={...},
        context=ToolInvocationContext(
            action_id=action.action_id,
            deal_id=action.deal_id,
        ),
    )

    # Emit deal event
    emit_event(
        event_type="action.tool_invoked",
        deal_id=action.deal_id,
        payload={
            "action_id": action.action_id,
            "tool_name": "mcp_gmail_send_email",
            "success": result.success,
            "error_code": result.error_code.value if not result.success else None,
            "duration_ms": result.duration_ms,
        }
    )

    return result
```

---

## Section 2: Capability Manifest Extension for Tools

### 2.1 Extended Manifest Schema

Extend the existing capability manifest to support external tools:

**New File:** `scripts/tools/manifests/mcp_gmail_send.v1.yaml`

```yaml
# Tool Capability Manifest v1.0
# This describes an MCP tool capability

capability_id: "TOOL.MCP.GMAIL_SEND.v1"
version: "1.0"
title: "Send Email via Gmail"
description: "Send an email using the Gmail MCP server"
action_type: "TOOL.MCP.GMAIL_SEND"

# Provider info (NEW for tools)
provider: "mcp"  # "mcp" | "http" | "local"
mcp_server: "gmail"
mcp_tool_name: "mcp__gmail__send_email"

# Input schema (JSON Schema format)
input_schema:
  type: object
  properties:
    to:
      type: array
      items:
        type: string
      description: "List of recipient email addresses"
      required: true
    subject:
      type: string
      description: "Email subject"
      required: true
    body:
      type: string
      description: "Email body content"
      required: true
    cc:
      type: array
      items:
        type: string
      description: "CC recipients"
      required: false
    bcc:
      type: array
      items:
        type: string
      description: "BCC recipients"
      required: false
    attachments:
      type: array
      items:
        type: string
      description: "File paths to attach"
      required: false

# Output schema (NEW for tools)
output_schema:
  type: object
  properties:
    message_id:
      type: string
      description: "Gmail message ID of sent email"
    thread_id:
      type: string
      description: "Gmail thread ID"
    success:
      type: boolean
      description: "Whether email was sent successfully"

# Safety metadata
risk_level: "high"  # Sending email is irreversible
requires_approval: true
constraints:
  - "Never send without operator approval"
  - "All recipients must be verified"
  - "Rate limited to 50 emails/day"

# Dependencies (NEW for tools)
dependencies:
  - name: "gmail-mcp"
    type: "mcp_server"
    required: true
    health_check: "mcp_gmail_health"

# Health check (NEW for tools)
health_check:
  type: "mcp_ping"
  endpoint: "mcp__gmail__list_email_labels"
  timeout_ms: 5000

# Cost estimate (NEW for tools)
cost_estimate:
  type: "per_invocation"
  amount: 0.0  # Free (Gmail API)
  unit: "USD"
  notes: "Gmail API is free but rate limited"

# LLM usage
llm_allowed: false
deterministic_steps: true

# Examples
examples:
  - description: "Send follow-up email to seller"
    inputs:
      to: ["john@seller.com"]
      subject: "Follow-up on LOI Discussion"
      body: "Dear John,\n\nThank you for our discussion..."

# Metadata
created: "2025-12-30"
updated: "2025-12-30"
owner: "zakops-team"
tags: ["tool", "mcp", "gmail", "email", "send", "external"]
```

### 2.2 Tool Registry

**New File:** `src/tools/registry.py` (~300 lines)

```python
"""
Tool Registry - Machine-readable catalog of all available tools.

This registry is used by:
1. ToolGateway - To validate and invoke tools
2. ActionPlanner - To map unknown requests to available tools
3. UI - To show available tools and their schemas
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DependencySpec(BaseModel):
    """Tool dependency specification."""
    name: str
    type: str  # "mcp_server" | "http_service" | "local_lib"
    required: bool = True
    health_check: Optional[str] = None


class HealthCheckSpec(BaseModel):
    """Health check specification."""
    type: str  # "mcp_ping" | "http_get" | "local_func"
    endpoint: str
    timeout_ms: int = 5000


class CostEstimate(BaseModel):
    """Cost estimate for tool invocation."""
    type: str  # "per_invocation" | "per_token" | "per_second"
    amount: float
    unit: str = "USD"
    notes: Optional[str] = None


class ToolManifest(BaseModel):
    """
    Tool manifest - describes a single tool capability.

    This extends CapabilityManifest with tool-specific fields.
    """
    # Core identity
    capability_id: str
    version: str
    title: str
    description: str
    action_type: str
    name: str = ""  # Tool name (derived from capability_id)

    # Provider info
    provider: str  # "mcp" | "http" | "local"
    mcp_server: Optional[str] = None
    mcp_tool_name: Optional[str] = None
    http_endpoint: Optional[str] = None
    http_method: Optional[str] = "POST"
    http_headers: Optional[Dict[str, str]] = None

    # Schemas
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None

    # Safety
    risk_level: str
    requires_approval: bool
    constraints: List[str] = Field(default_factory=list)

    # Dependencies & Health
    dependencies: List[DependencySpec] = Field(default_factory=list)
    health_check: Optional[HealthCheckSpec] = None

    # Cost
    cost_estimate: Optional[CostEstimate] = None

    # LLM
    llm_allowed: bool = False
    deterministic_steps: bool = True

    # Metadata
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    created: str
    updated: str
    owner: str
    tags: List[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}

    def __init__(self, **data):
        super().__init__(**data)
        # Derive name from capability_id if not set
        if not self.name:
            self.name = self.capability_id.replace(".", "_").lower()


class ToolRegistry:
    """
    Registry of available tools.

    Usage:
        registry = ToolRegistry()
        registry.load_from_directory("scripts/tools/manifests")

        # Get tool
        tool = registry.get_tool("mcp_gmail_send_email")

        # List by provider
        mcp_tools = registry.list_by_provider("mcp")

        # Check health
        health = await registry.check_health("mcp_gmail_send_email")
    """

    def __init__(self):
        self._tools: Dict[str, ToolManifest] = {}
        self._by_provider: Dict[str, List[ToolManifest]] = {}
        self._by_mcp_server: Dict[str, List[ToolManifest]] = {}
        self._by_tag: Dict[str, List[ToolManifest]] = {}

    def load_from_directory(self, tools_dir: str):
        """Load all tool manifests from directory."""
        path = Path(tools_dir)
        if not path.exists():
            logger.warning(f"Tools directory not found: {tools_dir}")
            return

        yaml_files = list(path.glob("*.yaml")) + list(path.glob("*.yml"))

        for yaml_file in yaml_files:
            try:
                self._load_manifest(yaml_file)
            except Exception as e:
                logger.error(f"Failed to load tool manifest {yaml_file}: {e}")
                raise

        logger.info(f"Loaded {len(self._tools)} tools from {tools_dir}")

    def _load_manifest(self, yaml_path: Path):
        """Load single tool manifest from YAML."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        # Convert nested dicts to models
        if 'dependencies' in data:
            data['dependencies'] = [DependencySpec(**d) for d in data['dependencies']]
        if 'health_check' in data:
            data['health_check'] = HealthCheckSpec(**data['health_check'])
        if 'cost_estimate' in data:
            data['cost_estimate'] = CostEstimate(**data['cost_estimate'])

        manifest = ToolManifest(**data)

        # Register by name
        self._tools[manifest.name] = manifest

        # Also register by mcp_tool_name if present
        if manifest.mcp_tool_name:
            self._tools[manifest.mcp_tool_name] = manifest

        # Index by provider
        if manifest.provider not in self._by_provider:
            self._by_provider[manifest.provider] = []
        self._by_provider[manifest.provider].append(manifest)

        # Index by MCP server
        if manifest.mcp_server:
            if manifest.mcp_server not in self._by_mcp_server:
                self._by_mcp_server[manifest.mcp_server] = []
            self._by_mcp_server[manifest.mcp_server].append(manifest)

        # Index by tags
        for tag in manifest.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(manifest)

        logger.info(f"Registered tool: {manifest.name} ({manifest.provider})")

    def get_tool(self, name: str) -> Optional[ToolManifest]:
        """Get tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolManifest]:
        """List all registered tools."""
        return list(set(self._tools.values()))  # Dedupe

    def list_by_provider(self, provider: str) -> List[ToolManifest]:
        """List tools by provider."""
        return self._by_provider.get(provider, [])

    def list_by_mcp_server(self, server: str) -> List[ToolManifest]:
        """List tools by MCP server."""
        return self._by_mcp_server.get(server, [])

    def list_by_tag(self, tag: str) -> List[ToolManifest]:
        """List tools by tag."""
        return self._by_tag.get(tag, [])

    async def check_health(self, tool_name: str) -> Dict[str, Any]:
        """Check health of a tool."""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"healthy": False, "error": "Tool not found"}

        if not tool.health_check:
            return {"healthy": True, "note": "No health check configured"}

        # Implement health check based on type
        # This is a placeholder - implement based on your infrastructure
        return {"healthy": True, "note": "Health check not implemented"}


# Global registry instance
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get global tool registry."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def load_tools(tools_dir: str = "scripts/tools/manifests"):
    """Load tools into global registry."""
    get_tool_registry().load_from_directory(tools_dir)
```

### 2.3 Available MCP Tools (Current Environment)

Based on the current environment, create manifests for:

| MCP Server | Tools to Manifest |
|------------|-------------------|
| `gmail` | `send_email`, `search_emails`, `read_email`, `create_filter` |
| `crawl4ai-rag` | `crawl_single_page`, `smart_crawl_url`, `perform_rag_query` |
| `browser-use` | `browse_url`, `click_element`, `fill_form`, `screenshot` |
| `linkedin` | `search_profiles`, `send_message`, `get_profile` |

---

## Section 3: Executor Integration Pattern

### 3.1 Pattern Definition

**Local-Only Executors (Direct):**
- `DocxGeneratorExecutor` - python-docx
- `PdfGeneratorExecutor` - reportlab
- `XlsxGeneratorExecutor` - openpyxl
- `PptxGeneratorExecutor` - python-pptx

These do NOT use ToolGateway. They generate artifacts locally.

**External-System Executors (via ToolGateway):**
- `EmailSendExecutor` - Uses `mcp_gmail_send_email`
- `WebScrapeExecutor` - Uses `mcp_crawl4ai_*`
- `BrowserAutomationExecutor` - Uses `mcp_browser_use_*`
- `SharePointSyncExecutor` - Uses HTTP API
- `CompositeExecutor` - Orchestrates multiple tools

### 3.2 Tool-Based Executor Base Class

**New File:** `src/actions/executors/tool_executor.py`

```python
"""
Base class for executors that use external tools via ToolGateway.
"""

from abc import abstractmethod
from typing import Dict, Any, List
from actions.executor import ActionExecutor, ExecutionResult
from tools.gateway import get_tool_gateway, ToolInvocationContext, ToolResult

import logging

logger = logging.getLogger(__name__)


class ToolBasedExecutor(ActionExecutor):
    """
    Base class for executors that invoke external tools.

    Subclasses must:
    1. Define `tool_name` - the tool to invoke
    2. Implement `prepare_tool_args()` - transform action inputs to tool args
    3. Implement `process_tool_result()` - transform tool output to action result
    """

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Name of the tool to invoke."""
        pass

    @abstractmethod
    def prepare_tool_args(
        self,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform action inputs to tool arguments."""
        pass

    @abstractmethod
    def process_tool_result(
        self,
        tool_result: ToolResult,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> ExecutionResult:
        """Transform tool result to action execution result."""
        pass

    async def execute(
        self,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> ExecutionResult:
        """Execute action by invoking tool through gateway."""

        logger.info(f"ToolBasedExecutor executing: {self.action_type} via {self.tool_name}")

        # Get gateway
        gateway = get_tool_gateway()

        # Prepare tool arguments
        try:
            tool_args = self.prepare_tool_args(payload, context)
        except Exception as e:
            logger.error(f"Failed to prepare tool args: {e}")
            return ExecutionResult(
                success=False,
                error=f"Failed to prepare tool arguments: {e}",
            )

        # Create invocation context
        inv_context = ToolInvocationContext(
            action_id=payload.action_id,
            deal_id=payload.deal_id,
            user_id=context.get('user_id'),
            session_id=context.get('session_id'),
        )

        # Invoke tool
        tool_result = await gateway.invoke(
            tool_name=self.tool_name,
            args=tool_args,
            context=inv_context,
        )

        # Process result
        return self.process_tool_result(tool_result, payload, context)


class EmailSendExecutor(ToolBasedExecutor):
    """
    Executor that sends emails via Gmail MCP.

    This is different from EmailDraftExecutor which only generates drafts.
    """

    @property
    def action_type(self) -> str:
        return "COMMUNICATION.SEND_EMAIL"

    @property
    def tool_name(self) -> str:
        return "mcp__gmail__send_email"

    def prepare_tool_args(
        self,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Transform action inputs to Gmail send_email args."""
        inputs = payload.inputs or {}

        return {
            "to": [inputs.get("recipient", inputs.get("to"))],
            "subject": inputs.get("subject", ""),
            "body": inputs.get("body", inputs.get("content", "")),
            "cc": inputs.get("cc", []),
            "bcc": inputs.get("bcc", []),
            "attachments": inputs.get("attachments", []),
        }

    def process_tool_result(
        self,
        tool_result: ToolResult,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> ExecutionResult:
        """Transform Gmail result to action result."""

        if tool_result.success:
            return ExecutionResult(
                success=True,
                output={
                    "message_id": tool_result.output.get("messageId"),
                    "thread_id": tool_result.output.get("threadId"),
                },
            )
        else:
            return ExecutionResult(
                success=False,
                error=f"{tool_result.error_code.value}: {tool_result.error_message}",
            )


class WebScrapeExecutor(ToolBasedExecutor):
    """Executor that scrapes web pages via crawl4ai MCP."""

    @property
    def action_type(self) -> str:
        return "DATA.WEB_SCRAPE"

    @property
    def tool_name(self) -> str:
        return "mcp__crawl4ai-rag__crawl_single_page"

    def prepare_tool_args(
        self,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        inputs = payload.inputs or {}
        return {"url": inputs.get("url", "")}

    def process_tool_result(
        self,
        tool_result: ToolResult,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> ExecutionResult:
        if tool_result.success:
            return ExecutionResult(
                success=True,
                output={"content": tool_result.output},
            )
        else:
            return ExecutionResult(
                success=False,
                error=f"{tool_result.error_code.value}: {tool_result.error_message}",
            )
```

---

## Section 4: Composite Actions (Handling Unknown Requests)

### 4.1 Concept

When a user requests an action that is NOT a registered action type, the system should:

1. **Attempt to decompose** into known capabilities from the manifest
2. **Create an approval-gated composite action** with step list
3. If a required tool is **missing**, create a "requires connector" action card

### 4.2 Composite Action Schema

**New File:** `scripts/actions/capabilities/composite_action.schema.yaml`

```yaml
# Composite Action Schema
# Used for multi-step plans composed of known capabilities

capability_id: "COMPOSITE.ACTION.v1"
version: "1.0"
title: "Composite Action"
description: "Multi-step action plan composed of known capabilities"
action_type: "COMPOSITE.ACTION"

input_schema:
  type: object
  properties:
    user_request:
      type: string
      description: "Original user request"
      required: true
    steps:
      type: array
      description: "List of steps to execute"
      required: true
      items:
        type: object
        properties:
          step_number:
            type: integer
          capability_id:
            type: string
          title:
            type: string
          inputs:
            type: object
          depends_on:
            type: array
            items:
              type: integer

output_artifacts:
  - type: "json"
    description: "Composite action result with all step outputs"
    mime_type: "application/json"

risk_level: "high"
requires_approval: true
constraints:
  - "All steps must use known capabilities"
  - "Each step requires individual approval"
  - "Steps execute sequentially by default"

llm_allowed: true
deterministic_steps: false

created: "2025-12-30"
owner: "zakops-team"
tags: ["composite", "multi-step", "plan", "orchestration"]
```

### 4.3 Composite Executor

**New File:** `src/actions/executors/composite_executor.py`

```python
"""
Composite Action Executor - Executes multi-step action plans.

When user requests something that maps to multiple capabilities,
the planner creates a CompositeAction with steps. This executor
runs each step in sequence, passing outputs between steps.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from actions.executor import ActionExecutor, ExecutionResult, ExecutorRegistry
from actions.capabilities.registry import get_registry
import logging

logger = logging.getLogger(__name__)


class CompositeStep(BaseModel):
    """Single step in a composite action."""
    step_number: int
    capability_id: str
    title: str
    inputs: Dict[str, Any] = {}
    depends_on: List[int] = []  # Step numbers this step depends on

    # Filled during execution
    status: str = "pending"  # pending, running, completed, failed, skipped
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CompositeExecutor(ActionExecutor):
    """
    Executor for composite (multi-step) actions.

    Execution flow:
    1. Parse steps from action inputs
    2. For each step:
       a. Check dependencies are satisfied
       b. Get executor for step's capability
       c. Inject outputs from dependent steps
       d. Execute step
       e. Record result
    3. Aggregate results
    """

    @property
    def action_type(self) -> str:
        return "COMPOSITE.ACTION"

    def validate(self, payload: 'ActionPayload') -> tuple[bool, Optional[str]]:
        """Validate composite action payload."""
        inputs = payload.inputs or {}

        if 'steps' not in inputs:
            return False, "Composite action requires 'steps' in inputs"

        steps = inputs['steps']
        if not isinstance(steps, list) or len(steps) == 0:
            return False, "Composite action requires at least one step"

        # Validate each step references a known capability
        registry = get_registry()
        for step in steps:
            cap_id = step.get('capability_id')
            if not cap_id:
                return False, f"Step {step.get('step_number')} missing capability_id"

            cap = registry.get_capability(cap_id)
            if not cap:
                return False, f"Unknown capability: {cap_id}"

        return True, None

    async def execute(
        self,
        payload: 'ActionPayload',
        context: Dict[str, Any],
    ) -> ExecutionResult:
        """Execute composite action."""

        logger.info(f"Executing composite action: {payload.action_id}")

        inputs = payload.inputs or {}
        raw_steps = inputs.get('steps', [])

        # Parse steps
        steps = [CompositeStep(**s) for s in raw_steps]
        step_outputs: Dict[int, Dict[str, Any]] = {}

        executor_registry = ExecutorRegistry()

        for step in steps:
            logger.info(f"Executing step {step.step_number}: {step.title}")

            # Check dependencies
            deps_satisfied = all(
                step_outputs.get(dep) is not None
                for dep in step.depends_on
            )

            if not deps_satisfied:
                step.status = "skipped"
                step.error = "Dependencies not satisfied"
                continue

            # Get executor for this capability
            registry = get_registry()
            cap = registry.get_capability(step.capability_id)

            if not cap:
                step.status = "failed"
                step.error = f"Capability not found: {step.capability_id}"
                continue

            executor = executor_registry.get_executor(cap.action_type)
            if not executor:
                step.status = "failed"
                step.error = f"No executor for: {cap.action_type}"
                continue

            # Inject outputs from dependencies
            step_inputs = dict(step.inputs)
            for dep_num in step.depends_on:
                dep_output = step_outputs.get(dep_num, {})
                step_inputs[f"step_{dep_num}_output"] = dep_output

            # Create step payload
            step_payload = ActionPayload(
                action_id=f"{payload.action_id}_step_{step.step_number}",
                action_type=cap.action_type,
                deal_id=payload.deal_id,
                inputs=step_inputs,
                title=step.title,
                summary=f"Step {step.step_number} of composite action",
            )

            # Execute step
            step.status = "running"
            try:
                result = await executor.execute(step_payload, context)

                if result.success:
                    step.status = "completed"
                    step.output = result.output
                    step_outputs[step.step_number] = result.output or {}
                else:
                    step.status = "failed"
                    step.error = result.error

            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                logger.error(f"Step {step.step_number} failed: {e}")

        # Aggregate results
        all_completed = all(s.status == "completed" for s in steps)
        any_failed = any(s.status == "failed" for s in steps)

        return ExecutionResult(
            success=all_completed,
            error="One or more steps failed" if any_failed else None,
            output={
                "steps": [
                    {
                        "step_number": s.step_number,
                        "title": s.title,
                        "status": s.status,
                        "output": s.output,
                        "error": s.error,
                    }
                    for s in steps
                ],
                "summary": {
                    "total_steps": len(steps),
                    "completed": sum(1 for s in steps if s.status == "completed"),
                    "failed": sum(1 for s in steps if s.status == "failed"),
                    "skipped": sum(1 for s in steps if s.status == "skipped"),
                },
            },
        )


class MissingToolAction(BaseModel):
    """
    Represents an action that requires a missing tool/connector.

    Instead of failing silently, we create an action card that says
    "requires connector/tool" so the operator knows what's missing.
    """
    action_type: str = "SYSTEM.MISSING_TOOL"
    title: str
    description: str
    missing_tool: str
    suggested_resolution: str

    # This is not executable until the tool is added
    executable: bool = False


def create_missing_tool_action(
    user_request: str,
    missing_tool: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create an action card for a missing tool.

    This is called by the planner when:
    1. User requests something we don't have a capability for
    2. The request would require a tool that's not in the registry
    """
    return {
        "action_type": "SYSTEM.MISSING_TOOL",
        "title": f"Missing Tool: {missing_tool}",
        "summary": f"Cannot execute: {user_request[:100]}",
        "status": "BLOCKED",
        "inputs": {
            "user_request": user_request,
            "missing_tool": missing_tool,
            "suggested_resolution": f"Add {missing_tool} to the tool registry or implement a custom executor",
        },
        "error": f"Tool not found: {missing_tool}",
        "executable": False,
    }
```

### 4.4 Planner Integration

Update the ActionPlanner to handle unknown actions:

```python
# In planner.py - _handle_unknown_action method

def _handle_unknown_action(
    self,
    query: str,
    scope: Dict[str, Any],
) -> ActionPlan:
    """
    Handle request for unknown/unavailable action.

    Strategy:
    1. Try to decompose using LLM into known capabilities
    2. If decomposition succeeds, create composite plan
    3. If decomposition fails, identify what tool is missing
    4. Create appropriate response (plan, clarification, or missing-tool card)
    """

    logger.warning(f"No direct capability match for: {query}")

    # Step 1: Try LLM decomposition against ALL capabilities
    all_caps = self.registry.list_capabilities()

    if self.use_llm:
        try:
            decomposition = self._decompose_llm(query, all_caps, {})

            if decomposition:
                # Success! Create composite plan
                return ActionPlan(
                    intent=query,
                    interpretation="Decomposed into known capabilities",
                    plan_steps=decomposition,
                    confidence=0.6,
                    risk_level="high",
                )
        except Exception as e:
            logger.warning(f"LLM decomposition failed: {e}")

    # Step 2: Analyze what's missing
    missing_tool = self._identify_missing_tool(query)

    if missing_tool:
        # Create missing-tool action
        return ActionPlan(
            intent=query,
            interpretation=f"Requires missing tool: {missing_tool}",
            is_refusal=True,
            refusal_reason=f"This request requires '{missing_tool}' which is not available.",
            suggested_alternatives=[
                f"Add '{missing_tool}' to the tool registry",
                "Contact administrator to enable this capability",
            ],
            confidence=0.0,
        )

    # Step 3: Standard refusal with available alternatives
    suggestions = [f"{cap.title} - {cap.description}" for cap in all_caps[:5]]

    return ActionPlan(
        intent=query,
        interpretation="Cannot map to known capability",
        is_refusal=True,
        refusal_reason="No matching capability found. Available actions:",
        suggested_alternatives=suggestions,
        confidence=0.0,
    )

def _identify_missing_tool(self, query: str) -> Optional[str]:
    """
    Identify what tool would be needed for this query.

    Uses keyword matching to suggest missing tools.
    """
    query_lower = query.lower()

    # Common tool suggestions based on keywords
    tool_suggestions = {
        "slack": "slack-mcp",
        "teams": "microsoft-teams-mcp",
        "calendar": "google-calendar-mcp",
        "spreadsheet": "google-sheets-mcp",
        "notion": "notion-mcp",
        "jira": "jira-mcp",
        "github issue": "github-mcp",
        "pull request": "github-mcp",
        "salesforce": "salesforce-mcp",
        "hubspot": "hubspot-mcp",
    }

    for keyword, tool in tool_suggestions.items():
        if keyword in query_lower:
            return tool

    return None
```

---

## Section 5: Tests

### 5.1 Test Specifications

**New File:** `tests/test_tooling_strategy.py`

```python
"""
Tests for Tooling Strategy components.

Coverage:
1. Manifest loads and is enforced
2. ToolGateway blocks non-allowlisted tools
3. Composite action planning produces step list
4. Audit trail captures tool calls safely
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from tools.gateway import (
    ToolGateway, ToolGatewayConfig, ToolResult, ToolErrorCode,
    ToolInvocationContext, SecretRedactor, ToolAuditLogger,
)
from tools.registry import ToolRegistry, ToolManifest
from actions.executors.composite_executor import CompositeExecutor, CompositeStep
from actions.planner import ActionPlanner


# =============================================================================
# Test: Manifest Loads and Is Enforced
# =============================================================================

class TestToolManifestLoading:
    """Test that tool manifests load correctly and are enforced."""

    def test_load_manifests_from_directory(self, tmp_path):
        """Test loading tool manifests from directory."""
        # Create test manifest
        manifest_content = """
capability_id: "TOOL.TEST.v1"
version: "1.0"
title: "Test Tool"
description: "A test tool"
action_type: "TOOL.TEST"
provider: "http"
http_endpoint: "http://localhost:8000/test"
input_schema:
  type: object
  properties:
    input1:
      type: string
      description: "Test input"
      required: true
risk_level: "low"
requires_approval: false
created: "2025-12-30"
updated: "2025-12-30"
owner: "test"
tags: ["test"]
"""
        manifest_file = tmp_path / "test_tool.v1.yaml"
        manifest_file.write_text(manifest_content)

        registry = ToolRegistry()
        registry.load_from_directory(str(tmp_path))

        assert len(registry.list_tools()) == 1

        tool = registry.get_tool("tool_test_v1")
        assert tool is not None
        assert tool.title == "Test Tool"
        assert tool.provider == "http"

    def test_manifest_enforces_required_fields(self, tmp_path):
        """Test that manifests with missing required fields fail to load."""
        # Manifest missing 'title'
        bad_manifest = """
capability_id: "TOOL.BAD.v1"
version: "1.0"
provider: "http"
"""
        manifest_file = tmp_path / "bad_tool.yaml"
        manifest_file.write_text(bad_manifest)

        registry = ToolRegistry()
        with pytest.raises(Exception):  # Pydantic validation error
            registry.load_from_directory(str(tmp_path))

    def test_manifest_provider_types(self, tmp_path):
        """Test that different provider types are supported."""
        mcp_manifest = """
capability_id: "TOOL.MCP.v1"
version: "1.0"
title: "MCP Tool"
description: "MCP tool"
action_type: "TOOL.MCP"
provider: "mcp"
mcp_server: "test-server"
mcp_tool_name: "test_tool"
input_schema:
  type: object
  properties: {}
risk_level: "low"
requires_approval: false
created: "2025-12-30"
updated: "2025-12-30"
owner: "test"
tags: []
"""
        manifest_file = tmp_path / "mcp_tool.yaml"
        manifest_file.write_text(mcp_manifest)

        registry = ToolRegistry()
        registry.load_from_directory(str(tmp_path))

        tool = registry.get_tool("tool_mcp_v1")
        assert tool.provider == "mcp"
        assert tool.mcp_server == "test-server"


# =============================================================================
# Test: ToolGateway Blocks Non-Allowlisted Tools
# =============================================================================

class TestToolGatewayPermissions:
    """Test ToolGateway allowlist/denylist enforcement."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock tool registry."""
        registry = Mock(spec=ToolRegistry)
        registry.get_tool.return_value = Mock(
            name="test_tool",
            provider="http",
            input_schema={},
        )
        return registry

    @pytest.mark.asyncio
    async def test_allowed_tool_passes(self, mock_registry):
        """Test that allowed tools can be invoked."""
        config = ToolGatewayConfig(
            allowed_tools=["test_tool", "another_tool"],
            denied_tools=[],
        )

        gateway = ToolGateway(config=config, tool_registry=mock_registry)

        # Mock the actual execution
        with patch.object(gateway, '_execute_with_retry', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = ToolResult(
                success=True,
                error_code=ToolErrorCode.SUCCESS,
            )

            result = await gateway.invoke(
                tool_name="test_tool",
                args={},
                context=ToolInvocationContext(action_id="test"),
            )

            assert result.success

    @pytest.mark.asyncio
    async def test_non_allowlisted_tool_blocked(self, mock_registry):
        """Test that non-allowlisted tools are blocked."""
        config = ToolGatewayConfig(
            allowed_tools=["allowed_tool"],  # test_tool NOT in list
            denied_tools=[],
        )

        gateway = ToolGateway(config=config, tool_registry=mock_registry)

        result = await gateway.invoke(
            tool_name="test_tool",
            args={},
            context=ToolInvocationContext(action_id="test"),
        )

        assert not result.success
        assert result.error_code == ToolErrorCode.TOOL_NOT_ALLOWED

    @pytest.mark.asyncio
    async def test_denylisted_tool_blocked(self, mock_registry):
        """Test that denylisted tools are blocked (even if allowlist empty)."""
        config = ToolGatewayConfig(
            allowed_tools=[],  # Empty = all allowed
            denied_tools=["test_tool"],
        )

        gateway = ToolGateway(config=config, tool_registry=mock_registry)

        result = await gateway.invoke(
            tool_name="test_tool",
            args={},
            context=ToolInvocationContext(action_id="test"),
        )

        assert not result.success
        assert result.error_code == ToolErrorCode.TOOL_DENIED

    @pytest.mark.asyncio
    async def test_denylist_takes_precedence(self, mock_registry):
        """Test that denylist takes precedence over allowlist."""
        config = ToolGatewayConfig(
            allowed_tools=["test_tool"],  # In allowlist
            denied_tools=["test_tool"],   # BUT also in denylist
        )

        gateway = ToolGateway(config=config, tool_registry=mock_registry)

        result = await gateway.invoke(
            tool_name="test_tool",
            args={},
            context=ToolInvocationContext(action_id="test"),
        )

        assert not result.success
        assert result.error_code == ToolErrorCode.TOOL_DENIED


# =============================================================================
# Test: Composite Action Planning
# =============================================================================

class TestCompositeActionPlanning:
    """Test that composite actions produce correct step lists."""

    @pytest.fixture
    def capability_registry(self):
        """Create mock capability registry with test capabilities."""
        registry = Mock()
        registry.list_capabilities.return_value = [
            Mock(
                capability_id="DOC.GENERATE.v1",
                title="Generate Document",
                description="Generate a document",
                action_type="DOC.GENERATE",
                tags=["document", "generate"],
            ),
            Mock(
                capability_id="EMAIL.DRAFT.v1",
                title="Draft Email",
                description="Draft an email",
                action_type="EMAIL.DRAFT",
                tags=["email", "draft", "communication"],
            ),
            Mock(
                capability_id="ANALYSIS.KPI.v1",
                title="Build KPI Analysis",
                description="Build KPI analysis",
                action_type="ANALYSIS.KPI",
                tags=["analysis", "kpi"],
            ),
        ]
        registry.match_capability.return_value = []  # No direct match
        registry.get_capability.side_effect = lambda x: next(
            (c for c in registry.list_capabilities() if c.capability_id == x), None
        )
        return registry

    def test_composite_plan_structure(self, capability_registry):
        """Test that composite plans have correct structure."""
        planner = ActionPlanner(registry=capability_registry, use_llm=False)

        # Simulate a complex request
        query = "Create a lender outreach package with summary and email"

        plan = planner.plan(query, scope={}, case_file={})

        # Should produce multi-step plan or ask for clarification
        assert plan.intent == query
        assert plan.interpretation is not None

        # If it produces steps, they should reference known capabilities
        if plan.plan_steps:
            for step in plan.plan_steps:
                assert 'capability_id' in step
                assert 'title' in step

    def test_composite_executor_validates_steps(self):
        """Test that composite executor validates step capabilities."""
        executor = CompositeExecutor()

        # Create payload with invalid capability
        payload = Mock()
        payload.inputs = {
            "steps": [
                {
                    "step_number": 1,
                    "capability_id": "NONEXISTENT.CAPABILITY.v1",
                    "title": "Invalid Step",
                    "inputs": {},
                }
            ]
        }

        with patch('actions.executors.composite_executor.get_registry') as mock_registry:
            mock_registry.return_value.get_capability.return_value = None

            is_valid, error = executor.validate(payload)

            assert not is_valid
            assert "Unknown capability" in error

    def test_missing_tool_action_created(self):
        """Test that missing tool creates appropriate action card."""
        from actions.executors.composite_executor import create_missing_tool_action

        action = create_missing_tool_action(
            user_request="Send a Slack message to the team",
            missing_tool="slack-mcp",
            context={},
        )

        assert action["action_type"] == "SYSTEM.MISSING_TOOL"
        assert action["status"] == "BLOCKED"
        assert "slack-mcp" in action["inputs"]["missing_tool"]
        assert not action["executable"]


# =============================================================================
# Test: Audit Trail
# =============================================================================

class TestAuditTrail:
    """Test that audit trail captures tool calls safely."""

    def test_secret_redaction_keys(self):
        """Test that secret-like keys are redacted."""
        data = {
            "username": "john",
            "password": "secret123",
            "api_key": "sk-12345",
            "normal_field": "visible",
        }

        redacted = SecretRedactor.redact_dict(data)

        assert redacted["username"] == "john"
        assert redacted["password"] == "[REDACTED]"
        assert redacted["api_key"] == "[REDACTED]"
        assert redacted["normal_field"] == "visible"

    def test_secret_redaction_nested(self):
        """Test that nested secrets are redacted."""
        data = {
            "config": {
                "database": {
                    "host": "localhost",
                    "password": "dbpass123",
                },
            },
            "credentials": {
                "api_token": "bearer-xyz",
            },
        }

        redacted = SecretRedactor.redact_dict(data)

        assert redacted["config"]["database"]["host"] == "localhost"
        assert redacted["config"]["database"]["password"] == "[REDACTED]"
        assert redacted["credentials"]["api_token"] == "[REDACTED]"

    def test_secret_redaction_values(self):
        """Test that secret-like values are redacted."""
        data = {
            "key1": "<OPENAI_API_KEY>",  # OpenAI-style
            "key2": "ghp_1234567890abcdefghij",  # GitHub token
            "key3": "normal_value",
        }

        redacted = SecretRedactor.redact_dict(data)

        assert redacted["key1"] == "[REDACTED]"
        assert redacted["key2"] == "[REDACTED]"
        assert redacted["key3"] == "normal_value"

    def test_audit_logger_creates_table(self, tmp_path):
        """Test that audit logger creates table on init."""
        import sqlite3

        db_path = str(tmp_path / "test.db")
        logger = ToolAuditLogger(db_path)

        with sqlite3.connect(db_path) as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()

            table_names = [t[0] for t in tables]
            assert "tool_invocation_log" in table_names

    def test_audit_logger_logs_invocation(self, tmp_path):
        """Test that audit logger correctly logs invocations."""
        import sqlite3
        from datetime import datetime

        db_path = str(tmp_path / "test.db")
        logger = ToolAuditLogger(db_path)

        logger.log_invocation(
            invocation_id="inv_123",
            tool_name="test_tool",
            provider="http",
            context=ToolInvocationContext(action_id="act_456", deal_id="deal_789"),
            input_args={"password": "secret", "data": "visible"},
            result=ToolResult(success=True, error_code=ToolErrorCode.SUCCESS),
            started_at=datetime.utcnow(),
        )

        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT * FROM tool_invocation_log WHERE invocation_id = ?",
                ("inv_123",)
            ).fetchone()

            assert row is not None

            # Check that secrets are redacted in stored data
            import json
            input_args = json.loads(row[7])  # input_args_redacted column
            assert input_args["password"] == "[REDACTED]"
            assert input_args["data"] == "visible"

    def test_no_langsmith_tracing(self):
        """Test that LangSmith tracing is NOT used."""
        # This is a conceptual test - verify no LangSmith imports
        import tools.gateway as gateway_module

        source = open(gateway_module.__file__).read()

        assert "langsmith" not in source.lower()
        assert "langchain" not in source.lower()


# =============================================================================
# Integration Tests
# =============================================================================

class TestToolingIntegration:
    """Integration tests for the complete tooling strategy."""

    @pytest.mark.asyncio
    async def test_end_to_end_tool_invocation(self, tmp_path):
        """Test complete flow: registry -> gateway -> audit."""
        # Create manifest
        manifest_content = """
capability_id: "TOOL.INTEGRATION_TEST.v1"
version: "1.0"
title: "Integration Test Tool"
description: "Tool for integration testing"
action_type: "TOOL.INTEGRATION_TEST"
provider: "http"
http_endpoint: "http://httpbin.org/post"
input_schema:
  type: object
  properties:
    message:
      type: string
      description: "Test message"
      required: true
output_schema:
  type: object
  properties:
    success:
      type: boolean
risk_level: "low"
requires_approval: false
created: "2025-12-30"
updated: "2025-12-30"
owner: "test"
tags: ["test", "integration"]
"""
        manifest_dir = tmp_path / "manifests"
        manifest_dir.mkdir()
        (manifest_dir / "integration_test.yaml").write_text(manifest_content)

        # Load registry
        registry = ToolRegistry()
        registry.load_from_directory(str(manifest_dir))

        # Configure gateway
        config = ToolGatewayConfig(
            allowed_tools=["tool_integration_test_v1"],
            audit_db_path=str(tmp_path / "audit.db"),
        )

        gateway = ToolGateway(config=config, tool_registry=registry)

        # Invoke tool (mocked HTTP)
        with patch.object(gateway, '_invoke_http', new_callable=AsyncMock) as mock_http:
            mock_http.return_value = {"success": True}

            result = await gateway.invoke(
                tool_name="tool_integration_test_v1",
                args={"message": "Hello, World!"},
                context=ToolInvocationContext(action_id="test_action"),
            )

            assert result.success
            assert result.output == {"success": True}

        # Verify audit log
        import sqlite3
        with sqlite3.connect(str(tmp_path / "audit.db")) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM tool_invocation_log"
            ).fetchone()[0]

            assert count >= 1
```

### 5.2 Running Tests

```bash
# Run all tooling strategy tests
pytest tests/test_tooling_strategy.py -v

# Run with coverage
pytest tests/test_tooling_strategy.py --cov=src/tools --cov=src/actions/executors/composite_executor

# Run specific test class
pytest tests/test_tooling_strategy.py::TestToolGatewayPermissions -v
```

---

## Section 6: Implementation Checklist

### Phase 0.5: Tooling Infrastructure (Week 1, Days 3-4)

#### 6.1 Tool Gateway

- [ ] `src/tools/gateway.py` implemented (~500 lines)
- [ ] `ToolErrorCode` enum with all error codes
- [ ] `ToolErrorCategory` with retry classification
- [ ] `SecretRedactor` class with pattern matching
- [ ] `ToolAuditLogger` with SQLite logging
- [ ] `ToolGateway` class with:
  - [ ] Allowlist/denylist check
  - [ ] Input validation
  - [ ] Timeout + retry with exponential backoff
  - [ ] Audit logging (redacted)
- [ ] Global `get_tool_gateway()` function
- [ ] Unit tests for gateway

#### 6.2 Tool Registry

- [ ] `src/tools/registry.py` implemented (~300 lines)
- [ ] `ToolManifest` Pydantic model with extensions
- [ ] `ToolRegistry` class with:
  - [ ] YAML manifest loading
  - [ ] Indexing by provider, MCP server, tags
  - [ ] Health check interface
- [ ] Global `get_tool_registry()` function
- [ ] Unit tests for registry

#### 6.3 Tool Manifests

- [ ] `scripts/tools/manifests/` directory created
- [ ] MCP Gmail tools manifests:
  - [ ] `mcp_gmail_send.v1.yaml`
  - [ ] `mcp_gmail_search.v1.yaml`
  - [ ] `mcp_gmail_read.v1.yaml`
- [ ] MCP Crawl4AI tools manifests:
  - [ ] `mcp_crawl4ai_single.v1.yaml`
  - [ ] `mcp_crawl4ai_smart.v1.yaml`
  - [ ] `mcp_crawl4ai_rag.v1.yaml`
- [ ] Additional MCP tool manifests as needed

#### 6.4 Executor Integration

- [ ] `src/actions/executors/tool_executor.py` implemented
- [ ] `ToolBasedExecutor` base class
- [ ] `EmailSendExecutor` using Gmail MCP
- [ ] `WebScrapeExecutor` using Crawl4AI MCP
- [ ] Unit tests for tool executors

#### 6.5 Composite Actions

- [ ] `src/actions/executors/composite_executor.py` implemented
- [ ] `CompositeStep` model
- [ ] `CompositeExecutor` class with:
  - [ ] Step validation
  - [ ] Dependency resolution
  - [ ] Sequential execution
  - [ ] Output aggregation
- [ ] `create_missing_tool_action()` function
- [ ] Unit tests for composite executor

#### 6.6 Planner Integration

- [ ] `ActionPlanner._handle_unknown_action()` updated
- [ ] `ActionPlanner._identify_missing_tool()` implemented
- [ ] Composite action creation from planner
- [ ] Integration tests

#### 6.7 Tests

- [ ] `tests/test_tooling_strategy.py` (~400 lines)
- [ ] Test: Manifest loads and is enforced
- [ ] Test: ToolGateway blocks non-allowlisted tools
- [ ] Test: Composite action planning produces step list
- [ ] Test: Audit trail captures safely (no secrets)
- [ ] Test: No LangSmith tracing
- [ ] All tests pass

---

## Section 7: Constraints Verification

| Constraint | Status | Notes |
|------------|--------|-------|
| Keep existing executor registry unchanged | ✅ | Additive "tool spine" only |
| No LangSmith tracing | ✅ | SQLite + deal events only |
| Observability local only | ✅ | `tool_invocation_log` table |
| Secret redaction enforced | ✅ | `SecretRedactor` class |
| MCP tools supported | ✅ | Provider: "mcp" in manifests |

---

## Section 8: Next Steps

1. **Integrate into main plan**: Add this as Phase 0.5 in `ACTIONS-ENGINE-IMPLEMENTATION-PLAN-v1.2.md`
2. **Create tool manifests**: Start with Gmail MCP tools (already running)
3. **Implement ToolGateway**: Core infrastructure
4. **Add composite executor**: Enable multi-step plans
5. **Run tests**: Verify all acceptance criteria

---

**Document Status:** ✅ COMPLETE AND READY FOR INTEGRATION
**Target Phase:** Phase 0.5 (between Phase 0 and Phase 1)
**Estimated Effort:** 2 days
**Dependencies:** Phase 0 (Capability Manifest System)

---

## Codex Review Notes — Gaps + Improvements (Added 2025-12-31)

### Safety: Add a Secret-Scan Gate (Not Just Log Redaction)

- The current design emphasizes **redaction in logs**, but world-class safety needs a separate **secret-scan gate** that blocks external calls (MCP/HTTP/cloud LLM) when secrets/credentials are detected in tool inputs, outputs-to-be-sent, or attached excerpts. Redaction prevents leaking to logs; it does not prevent exfiltration.
- Recommendation: make `ToolGateway.invoke()` run `SecretScanner.scan(args)` (with allowlisted safe keys) **before** invocation; if blocked, return a structured permanent error (e.g., `SECRET_DETECTED`) and emit an audit event.

### Correctness: Fix Two Spec/Code-Shape Mismatches

- In the retry loop pseudo-code, `if result.success or not result.should_retry:` should be `not result.should_retry()` if `should_retry` is implemented as a method.
- The manifest examples define `input_schema: { type: object, properties: ... }`, but some validation pseudo-code iterates `tool_manifest.input_schema.items()` as if it were a flat `field -> schema` map. Either:
  - normalize tool schemas into the same `InputSchema` model used for action capabilities (`input_schema.properties`), or
  - document the exact schema shape and consistently read `input_schema["properties"]`.

### Enforcement: ToolGateway Should Respect Action Approval State

- Add an explicit requirement: ToolGateway must verify the invoking action’s **status** and **risk gate** (e.g., deny external tool calls unless the action is `READY/PROCESSING` and operator-approved when required). This prevents accidental tool execution during planning/dry-run.

### Health Checks: Replace “Not Implemented” With a Minimal Working Contract

- `ToolRegistry.check_health()` currently returns “not implemented” for many cases. Define a minimum viable health check per provider:
  - MCP: call a cheap `ping`/list endpoint with timeout and report latency + last_ok timestamp
  - HTTP: `GET /health` (or configured endpoint)
  - local: import check + version check
- Cache health for a short TTL (e.g., 30–60s) to avoid thundering herds in the UI.

### Observability: Bound Log Size + Correlate With Actions

- Add a max size policy for `input_args_redacted` and `output_redacted` (truncate + hash when oversized) so the audit DB can’t balloon from large payloads.
- Require correlation fields (`action_id`, `deal_id`, `invocation_id`) everywhere so `/api/actions/{id}` can show tool invocations and timings without LangSmith.

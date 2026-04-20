from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


class McpError(RuntimeError):
    pass


@dataclass
class McpResponse:
    raw: Dict[str, Any]

    @property
    def result(self) -> Dict[str, Any]:
        r = self.raw.get("result")
        return r if isinstance(r, dict) else {"result": r}


class McpStdioSession:
    """
    Minimal JSON-RPC (MCP stdio) session that keeps a single server process alive.
    """

    def __init__(
        self,
        *,
        command: list[str],
        env: Optional[Dict[str, str]] = None,
        protocol_version: str = "2024-11-05",
        client_name: str = "zakops-email-triage",
        client_version: str = "0.1.0",
    ):
        self.command = list(command)
        self.env = env or {}
        self.protocol_version = protocol_version
        self.client_name = client_name
        self.client_version = client_version
        self._proc: Optional[asyncio.subprocess.Process] = None
        self._stderr_task: Optional[asyncio.Task] = None
        self._stdout_buf = bytearray()
        self._next_id = 1
        self._initialized = False

    async def __aenter__(self) -> "McpStdioSession":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()

    async def start(self) -> None:
        if self._proc:
            return
        self._proc = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, **self.env},
        )
        assert self._proc.stdout and self._proc.stdin and self._proc.stderr
        self._stderr_task = asyncio.create_task(self._drain_stderr(self._proc.stderr))
        await self._initialize()

    async def _initialize(self) -> None:
        if self._initialized:
            return
        params = {
            "protocolVersion": self.protocol_version,
            "capabilities": {},
            "clientInfo": {"name": self.client_name, "version": self.client_version},
        }
        await self.request(method="initialize", params=params)
        self._initialized = True

    async def stop(self) -> None:
        if not self._proc:
            return
        proc = self._proc
        self._proc = None
        self._stdout_buf = bytearray()

        try:
            if proc.stdin:
                proc.stdin.close()
        except Exception:
            pass

        try:
            proc.terminate()
        except Exception:
            pass

        try:
            await asyncio.wait_for(proc.wait(), timeout=5.0)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

        if self._stderr_task:
            self._stderr_task.cancel()
            self._stderr_task = None

    async def _drain_stderr(self, stderr: asyncio.StreamReader) -> None:
        try:
            while True:
                line = await stderr.readline()
                if not line:
                    return
        except asyncio.CancelledError:
            return

    async def _read_stdout_line(self, *, max_bytes: int = 10 * 1024 * 1024) -> bytes:
        """
        Read a single \\n-terminated line from MCP stdout without asyncio's default 64KiB
        StreamReader line limit.
        """
        if not self._proc or not self._proc.stdout:
            raise McpError("MCP process not started")
        while True:
            idx = self._stdout_buf.find(b"\n")
            if idx != -1:
                line = bytes(self._stdout_buf[: idx + 1])
                del self._stdout_buf[: idx + 1]
                return line
            chunk = await self._proc.stdout.read(4096)
            if not chunk:
                return b""
            self._stdout_buf.extend(chunk)
            if len(self._stdout_buf) > max_bytes:
                raise McpError("mcp_stdout_line_too_large")

    async def request(self, *, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self._proc or not self._proc.stdin or not self._proc.stdout:
            raise McpError("MCP process not started")

        request_id = self._next_id
        self._next_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        payload = json.dumps(req, ensure_ascii=False)
        self._proc.stdin.write((payload + "\n").encode("utf-8"))
        await self._proc.stdin.drain()

        while True:
            line = await self._read_stdout_line()
            if not line:
                raise McpError("MCP process closed stdout")
            try:
                msg = json.loads(line.decode("utf-8", errors="replace"))
            except Exception:
                continue
            if not isinstance(msg, dict):
                continue
            if msg.get("id") != request_id:
                continue
            if "error" in msg:
                raise McpError(f"mcp_error:{msg['error']}")
            resp = McpResponse(raw=msg)
            return resp.result

    async def call(self, *, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request(method="tools/call", params={"name": name, "arguments": arguments or {}})

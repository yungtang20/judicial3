"""Live MCP client boundary for taiwan-law tools.

This is the deterministic bridge that lets the application actually call the
configured MCP sources instead of always failing closed:

- ``JUDICIAL3_MCP_REMOTE`` (default ``https://legaltech.org.tw/mcp``) — live HTTP
  JSON-RPC to the remote Taiwan legal MCP server. Public statute/judgment lookup
  only; no case content is ever sent.
- ``JUDICIAL3_MCP_LOCAL`` — optional path to a local ``mcp-taiwan-legal-db`` checkout
  (its own venv runs ``-m mcp_server.server`` over stdio JSON-RPC). Used when the
  app should prefer an offline/local snapshot first.

All network/process failures degrade gracefully: an unavailable or broken MCP
source yields ``MCP_UNAVAILABLE`` verification records and empty records — never
invented statute text, never substituted model memory.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from typing import Any

from .mcp_verification import VerificationStatus, build_record, classify_mcp_result


REMOTE_DEFAULT = "https://legaltech.org.tw/mcp"
HTTP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


def remote_call_tool(name: str, arguments: dict[str, Any], *, timeout: int = 60) -> Any:
    """Call one tool on the remote Taiwan legal MCP via plain HTTP JSON-RPC."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": name, "arguments": arguments}}
    req = urllib.request.Request(
        os.environ.get("JUDICIAL3_MCP_REMOTE", REMOTE_DEFAULT),
        data=json.dumps(payload).encode("utf-8"),
        headers=HTTP_HEADERS,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    stripped = raw.lstrip()
    if stripped.startswith("{") and ("jsonrpc" in raw[:40] or '"result"' in raw[:40]):
        return json.loads(raw)
    for line in raw.splitlines():
        if line.startswith("data:"):
            body = line[len("data:"):].strip()
            if body:
                return json.loads(body)
    raise ValueError(f"unrecognized MCP response: {raw[:200]!r}")


def _remote_text(name: str, arguments: dict[str, Any], *, timeout: int = 60) -> str | None:
    result = remote_call_tool(name, arguments, timeout=timeout)
    content = result.get("result", {}).get("content") or []
    for block in content:
        if block.get("type") == "text":
            text = block.get("text", "")
            try:
                return json.loads(text)
            except (ValueError, TypeError):
                return text
    return None


class _LocalMcpClient:
    """Singleton stdio JSON-RPC client to the local mcp-taiwan-legal-db server.

    Created lazily once per process (only when ``JUDICIAL3_MCP_LOCAL`` is set
    and the venv python exists). Any startup failure degrades to unavailable.
    """

    def __init__(self, python: str, cwd: str, init_timeout: int = 30) -> None:
        self.proc = subprocess.Popen(
            [python, "-m", "mcp_server.server"],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self._lock = threading.Lock()
        self._pending: dict[int, Any] = {}
        self._id_counter = 0
        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()
        self._raw_call({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "judicial3-local-mcp", "version": "1.0"},
        }}, init_timeout)
        self._raw_call({"jsonrpc": "2.0", "method": "notifications/initialized"}, 5)

    def _next_id(self) -> int:
        with self._lock:
            self._id_counter += 1
            return self._id_counter

    def _raw_call(self, obj: dict[str, Any], timeout: int) -> Any:
        rid = self._next_id()
        obj["id"] = rid
        with self._lock:
            assert self.proc.stdin is not None
            self.proc.stdin.write(json.dumps(obj) + "\n")
            self.proc.stdin.flush()
        return self._wait(rid, timeout)

    def _read(self) -> None:
        assert self.proc.stdout is not None
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            rid = msg.get("id")
            if rid is None:
                continue
            with self._lock:
                self._pending[rid] = msg

    def _wait(self, rid: int, timeout: int) -> Any:
        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError(f"local MCP call id {rid} timed out")
            with self._lock:
                msg = self._pending.pop(rid, None)
            if msg is not None:
                if msg.get("error"):
                    raise ValueError(msg["error"].get("message", "local MCP error"))
                return msg.get("result")
            time.sleep(min(0.05, remaining))

    def call_tool(self, name: str, arguments: dict[str, Any], *, timeout: int = 60) -> Any:
        return self._raw_call({"jsonrpc": "2.0", "method": "tools/call",
                               "params": {"name": name, "arguments": arguments}}, timeout)

    def list_tools(self, *, timeout: int = 20) -> list[dict[str, Any]]:
        result = self._raw_call({"jsonrpc": "2.0", "method": "tools/list",
                                 "params": {}}, timeout)
        return result.get("result", {}).get("tools", [])

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self.proc.terminate()
                self.proc.wait(timeout=5)
        except Exception:
            pass


_local_client: _LocalMcpClient | None = None
_local_client_lock = threading.Lock()


def local_call_tool(name: str, arguments: dict[str, Any], *, timeout: int = 60) -> Any:
    """Call one tool on the local mcp-taiwan-legal-db server (opt-in via env)."""
    global _local_client
    local_dir = os.environ.get("JUDICIAL3_MCP_LOCAL")
    if not local_dir:
        raise RuntimeError("local MCP not configured (JUDICIAL3_MCP_LOCAL)")
    py = os.path.join(local_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(py):
        py = os.path.join(local_dir, ".venv", "bin", "python")
    if not os.path.exists(py):
        raise RuntimeError(f"local MCP venv python not found under {local_dir}")
    with _local_client_lock:
        if _local_client is None or _local_client.proc.poll() is not None:
            _local_client = _LocalMcpClient(py, local_dir)
    return _local_client.call_tool(name, arguments, timeout=timeout)


def local_list_tools() -> list[dict[str, Any]] | None:
    try:
        with _local_client_lock:
            if _local_client is None:
                return None
            return _local_client.list_tools()
    except Exception:
        return None


def local_server_available() -> bool:
    try:
        local_call_tool("tools/list", {}, timeout=10)
        return True
    except Exception:
        return False


def remote_available() -> bool:
    try:
        remote_call_tool("tools/list", {}, timeout=15)
        return True
    except Exception:
        return False


def probe() -> dict[str, Any]:
    """Cheap readiness report used by /api/mcp/status. Never blocks long."""
    return {
        "remote_configured": bool(os.environ.get("JUDICIAL3_MCP_REMOTE", REMOTE_DEFAULT)),
        "remote_available": remote_available(),
        "local_configured": bool(os.environ.get("JUDICIAL3_MCP_LOCAL")),
        "local_available": local_server_available(),
    }

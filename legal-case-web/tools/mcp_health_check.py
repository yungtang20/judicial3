"""Check if mcp-taiwan-legal-db is installed and functional.

The local MCP server (stdio JSON-RPC) is opt-in via ``JUDICIAL3_MCP_LOCAL``. This
check reports the *actual* tool set instead of asserting a stale hardcoded count.
"""

from __future__ import annotations

import asyncio
import sys

EXPECTED_TOOLS = [
    "search_judgments",
    "get_judgment",
    "query_regulation",
    "get_pcode",
    "search_regulations",
    "get_interpretation",
    "search_interpretations",
    "get_citations",
]

try:
    import mcp_server  # noqa: F401
except ImportError as e:
    print(f"SKIP: mcp_server package not importable: {e}")
    print("Set JUDICIAL3_MCP_LOCAL to <mcp-taiwan-legal-db dir> to use local MCP.")
    sys.exit(0)

from mcp_server.server import mcp


async def check_tools():
    tools = await mcp.list_tools()
    names = [getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None) for t in tools]
    print(f"PASS: {len(names)} tools available: {', '.join(str(n) for n in names)}")
    missing = [t for t in EXPECTED_TOOLS if t not in names]
    if missing:
        print(f"WARN: expected tools missing: {missing}")
        sys.exit(1)
    print("ALL CHECKS PASSED")


asyncio.run(check_tools())

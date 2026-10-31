"""Check if mcp-taiwan-legal-db is installed and functional."""
import asyncio
import sys

# Test 1: Check if the package is installed
try:
    import mcp_server
    print("PASS: mcp_server package imported")
except ImportError as e:
    print(f"FAIL: Cannot import mcp_server: {e}")
    sys.exit(1)

# Test 2: Check tool count
from mcp_server.server import mcp

async def check_tools():
    tools = await mcp.list_tools()
    print(f"PASS: {len(tools)} tools available")
    return len(tools)

count = asyncio.run(check_tools())
assert count == 26, f"Expected 26 tools, got {count}"
print("ALL CHECKS PASSED")
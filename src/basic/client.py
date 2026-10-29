"""MCP CLIENT: holds the connection to the server and fetches its tools.

Run this file directly to check the connection and list the server's tools.
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


# --------------------------------------------------------
# Each entry is its own 1:1 client-server connection.
# Add more servers here to give the host more tools.
# ---------------------------------------------------------
def build_client() -> MultiServerMCPClient:
    
    return MultiServerMCPClient(
        {"weather": {"transport": "streamable_http", "url": MCP_SERVER_URL}}
    )


async def load_tools():
    """Connect, handshake, and discover the server's tools (tools/list)."""
    return await build_client().get_tools()


#--------------------------------------------------
#   This is to test locally
#--------------------------------------------------
async def test_mcp_client():
    tools = await load_tools()
    print(f"Connected. {len(tools)} tools found:")
    for t in tools:
        print(f"  - {t.name}: {t.description}")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())

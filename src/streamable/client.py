
"""MCP CLIENT: connects to the weather server and receives progress."""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def on_progress(
    progress: float,
    total: float | None,
    message: str | None,
    context,
) -> None:
    percentage = (
        f"{progress / total * 100:.0f}%"
        if total
        else f"{progress} completed"
    )

    print(
        f"\n[MCP PROGRESS] "
        f"[{context.server_name}] "
        f"{percentage} - {message or ''}",
        flush=True,
    )


def build_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": MCP_SERVER_URL,
            }
        },
        callbacks=Callbacks(on_progress=on_progress),
    )


async def load_tools():
    """Connect to the MCP server and discover its tools."""
    return await build_client().get_tools()

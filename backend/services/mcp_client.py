"""Each role has its own cached tool set and stdio MCP subprocess."""

import asyncio
import os
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
_tool_cache = {}
_lock = asyncio.Lock()


async def load_mcp_tools(role):
    if role in _tool_cache:
        return _tool_cache[role]

    async with _lock:
        if role in _tool_cache:
            return _tool_cache[role]

        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND_DIR)
        env["STOREBRIDGE_MCP_ROLE"] = role

        client = MultiServerMCPClient({
            "storebridge": {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-m", "mcp_server.server"],
                "env": env,
                "cwd": str(BACKEND_DIR),
            }
        })

        tools = await client.get_tools()
        _tool_cache[role] = tools

        return tools

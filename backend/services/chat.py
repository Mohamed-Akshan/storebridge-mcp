
import json

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)

from agents.graph import build_graph
from guardrails.output_guard import check_answer
from services.mcp_client import load_mcp_tools
from services.observability import graph_config


_graphs = {}


async def get_graph(role):
    """Load the correct tool-enabled graph for each role."""

    if role not in _graphs:

        tools = await load_mcp_tools(role)

        _graphs[role] = build_graph(
            tools=tools,
            role=role,
        )

    return _graphs[role]


def get_payload(message):
    """Read structured data returned by an MCP tool."""

    content = message.content

    try:
        if isinstance(content, str):
            content = json.loads(content)

        if isinstance(content, dict):
            if "content" in content:
                content = content["content"]

            else:
                return content

        if isinstance(content, list):

            for block in content:

                if isinstance(block, dict):
                    text = block.get("text")

                    if text:
                        parsed = json.loads(text)

                        if isinstance(parsed, dict):
                            return parsed

        return content

    except (ValueError, TypeError):
        return None


async def respond(history, role):
    """Run the conversation and return a clean response."""

    graph = await get_graph(role)

    messages = []

    for item in history:

        if item.role == "user":
            messages.append(
                HumanMessage(content=item.content)
            )

        elif item.role == "assistant":
            messages.append(
                AIMessage(content=item.content)
            )

    config = {
        "recursion_limit": 10,
        **graph_config(),
    }

    state = await graph.ainvoke(
        {
            "messages": messages,
            "routing": "",
        },
        config=config,
    )

    tools_used = []
    chart = None
    data_table = None

    for message in state["messages"]:

        if not isinstance(message, ToolMessage):
            continue

        if message.name:
            tools_used.append(message.name)

        payload = get_payload(message)

        if not isinstance(payload, dict):
            continue

        if payload.get("chart"):
            chart = payload["chart"]

        for key in (
            "branches",
            "products",
            "matches",
            "ranking",
            "rows",
        ):

            rows = payload.get(key)

            if isinstance(rows, list) and rows:
                data_table = rows[:15]
                break

    answer = ""

    for message in reversed(state["messages"]):

        if not isinstance(message, AIMessage):
            continue

        if message.tool_calls:
            continue

        answer = check_answer(message.content)

        break

    answer = check_answer(answer)

    return {
        "answer": answer,
        "chart": chart,
        "table": data_table,
        "tools_used": list(dict.fromkeys(tools_used)),
    }

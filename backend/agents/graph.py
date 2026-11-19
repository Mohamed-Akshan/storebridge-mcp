from typing import Annotated, NotRequired, TypedDict

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
)

from langgraph.graph import (
    START,
    END,
    StateGraph,
)

from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode

from agents.supervisor import supervisor_node

from agents.business_agent import make_business_node


class RetailState(TypedDict):
    """Shared conversation state."""

    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]

    routing: str

    scope: NotRequired[str]


def route_question(state):
    """Route based on the supervisor's decision."""

    intent = state.get("scope", "business")

    if intent == "unrelated":
        return "out_of_scope"

    if intent == "modification":
        return "read_only"

    return "business_agent"


def next_step(state):
    """Run MCP tools when the business agent requests them."""

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage):

        if last_message.tool_calls:
            return "tools"

    return END


def out_of_scope_node(state):
    """Handle unrelated questions politely."""

    answer = (
        "I'm here to assist with Walk & Talk's "
        "mobile retail operations, including "
        "product availability, stock levels, "
        "selling prices and purchase costs "
        "across our three branches.\n\n"
        "I can also help with sales, revenue "
        "and business performance reports "
        "when your account has access.\n\n"
        "Is there anything related to "
        "Walk & Talk I can help you with?"
    )

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }


def read_only_node(state):
    """Refuse requests that modify business records."""

    answer = (
        "I'm sorry, but Walk & Talk Assistant "
        "provides read-only access to "
        "business information.\n\n"
        "I can't create, update or delete "
        "inventory, prices, sales or "
        "financial records through this chat.\n\n"
        "Please use your authorized inventory "
        "management system for those changes. "
        "I'd be happy to help you review "
        "the existing information instead."
    )

    return {
        "messages": [
            AIMessage(content=answer)
        ]
    }


def build_graph(tools, role):
    """Create the complete LangGraph workflow."""

    graph = StateGraph(RetailState)


    graph.add_node(
        "supervisor",
        supervisor_node,
    )


    graph.add_node(
        "business_agent",
        make_business_node(
            tools,
            role,
        ),
    )


    graph.add_node(
        "tools",
        ToolNode(
            tools,
            handle_tool_errors=True,
        ),
    )

    # Register guardrail response nodes.

    graph.add_node(
        "out_of_scope",
        out_of_scope_node,
    )

    graph.add_node(
        "read_only",
        read_only_node,
    )

    # tart with the supervisor.

    graph.add_edge(
        START,
        "supervisor",
    )

    # Route based on classified intent.

    graph.add_conditional_edges(
        "supervisor",
        route_question,
        {
            "business_agent": "business_agent",
            "out_of_scope": "out_of_scope",
            "read_only": "read_only",
        },
    )

    #Check whether the business agent needs tools.

    graph.add_conditional_edges(
        "business_agent",
        next_step,
        {
            "tools": "tools",
            END: END,
        },
    )

    # Send MCP results back to the business agent.

    graph.add_edge(
        "tools",
        "business_agent",
    )

    # Finish guardrail responses.

    graph.add_edge(
        "out_of_scope",
        END,
    )

    graph.add_edge(
        "read_only",
        END,
    )

    return graph.compile()

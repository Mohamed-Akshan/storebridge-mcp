from langchain_core.messages import SystemMessage

from core.llm import invoke_with_fallback
from prompts.business_prompt import business_prompt


def make_business_node(tools, role):

    async def business_node(state):
        instructions = business_prompt(role, state.get("routing", ""))

        response = await invoke_with_fallback(
            [SystemMessage(content=instructions), *state["messages"]],
            tools=tools,
        )

        return {"messages": [response]}

    return business_node

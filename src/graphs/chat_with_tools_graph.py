import os
import sys
import json
from typing import TypedDict, Annotated, Literal

from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_node import ToolNode

from AetherMind.utils.langchain_utils import wrap_ad_hoc_tool_agent

def add_messages(left: list, right: list):
    """Add-don't-overwrite."""
    return left + right

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        print("Assistant state:", state, flush=True)
        result = self.runnable.invoke(state)
        return {"messages": [result]}

# Define the function that determines whether to continue or not
def should_continue(state: State) -> Literal["action", "__end__"]:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "action"
    # Otherwise, we stop (reply to the user)
    return "__end__"

def get_chat_with_tools_graph(llm, tools, memory, use_ad_hoc_tool_agent=False):

    # Define a new graph
    graph = StateGraph(State)

    if use_ad_hoc_tool_agent:
        llm = wrap_ad_hoc_tool_agent(llm, tools)
    else:
        if len(tools) > 0:
            llm = llm.bind_tools(tools)
        llm = ChatPromptTemplate.from_messages([("placeholder", "{messages}")]) | llm
    
    graph.add_node("agent", Assistant(llm))
    graph.add_node("action", ToolNode(tools))

    graph.set_entry_point("agent")

    # Conditional agent -> action OR agent -> END
    graph.add_conditional_edges(
        "agent",
        should_continue,
    )

    # Always transition `action` -> `agent`
    graph.add_edge("action", "agent")

    return graph.compile(checkpointer=memory)
from typing import Iterable, List, Dict, Any
import json
import secrets

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AIMessage, AIMessageChunk


class ToolCall(BaseModel):
    name: str = Field(description="tool name")
    arguments: Dict[str, Any] = Field(description="tool arguments")

class ToolCallMessage(BaseModel):
    tool_calls: List[ToolCall] = Field(description="list of tool calls")

json_parser = JsonOutputParser(pydantic_object=ToolCallMessage)

def ad_hoc_tool_parser(ai_message: AIMessage) -> AIMessage:
    """Parse the AI message to the format of a tool call, if possible."""
    try:
        json_content = json_parser.parse(ai_message.content)
        for tool_call in json_content['tool_calls']:
            tool_call['id'] = "call_" + secrets.token_hex(12)
        # parse to a valid tool call response
        response_metadata = ai_message.response_metadata
        response_metadata['finish_reason'] = "tool_calls"
        ai_message.response_metadata = response_metadata
        ai_message.additional_kwargs = {
            'tool_calls': [
                {
                    "function": tool_call,
                    "id": tool_call['id'],
                    "type": "function"
                } for tool_call in json_content['tool_calls']
            ]
        }
        ai_message.tool_calls = [
            {
                "name": tool_call['name'],
                "args": tool_call['arguments'],
                "id": tool_call['id']
            } for tool_call in json_content['tool_calls']
        ]
        return ai_message
    except Exception as e:
        return ai_message

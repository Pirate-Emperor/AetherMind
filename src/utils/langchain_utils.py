import os
import sys

from langchain_core.tools import render_text_description
from langchain_core.prompts import ChatPromptTemplate

from AetherMind.parsers.ad_hoc_tool_parser import ad_hoc_tool_parser

def get_messages_from_checkpoint_tuple(checkpoint_tuple):
    if checkpoint_tuple is None:
        return []
    return checkpoint_tuple.checkpoint['channel_values']['messages']

def wrap_ad_hoc_tool_agent(llm_with_tools, tools):
    """
    llm_with_tools: a language model already bound with tools
    """
    
    AD_HOC_TOOL_SYSTEM_PROMPT = """\
You are an assistant that has access to the following set of tools. 
Here are the names and descriptions for each tool:

{tool_desc}

Given the user input, do the following thinking:

1. Determine if the user input requires you to use a tool.

2. If so, return and ONLY return a JSON blob in the following format:

```json
{{\"tool_calls\": [{{\"name\": \"<tool_name>\", \"arguments\": {{<argument_name>: <argument_value>}}}}]}}
```

As you can see, `tool_calls` is a list with the name and argument inputs of the tools you devided to use. 
The `arguments` should be a dictionary, with keys corresponding 
to the argument names and the values corresponding to the requested values.

3. If no tool is required, just return however you like.

Please note again: IF YOU DECIDE TO USE A TOOL, you should only return a JSON blob, any other character is not needed;
OTHERWISE, just use your own words.

Also, after the tool returns, you should just render the tool's output by means you see fit, DON'T RECALL THE TOOL BY ANOTHER JSON.
"""
    system_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", AD_HOC_TOOL_SYSTEM_PROMPT),
            ("placeholder", "{messages}"),
        ]
    ).partial(tool_desc=render_text_description(tools))
    return system_prompt | llm_with_tools | ad_hoc_tool_parser
    
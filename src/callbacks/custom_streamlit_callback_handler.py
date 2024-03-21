from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional

from langchain_community.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler, LLMThought
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult

from AetherMind.utils.streamlit_utils import write_token_usage

class CustomStreamlitCallbackHandler(StreamlitCallbackHandler):
    
    def __init__(self, *args, **kwargs):
        self.streaming = True
        super().__init__(*args, **kwargs)
        
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        print('LLM END RESPOSNE', response, kwargs, flush=True)
        if not self.streaming:
            # if streaming mode is off, write result here
            super().on_llm_new_token(response.generations[0][0].message.content, **kwargs)
        super().on_llm_end(response, **kwargs)
        # self._require_current_thought().on_llm_end(response, **kwargs)
        # self._prune_old_thought_containers()
        write_token_usage(self._require_current_thought().container, response.generations[0][0].message)
        if self._current_thought is not None:
            self._current_thought.complete(
                self._thought_labeler.get_final_agent_thought_label()
            )
            self._current_thought = None
        
    # def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
    #     print('CHAIN END OUTPUTS', outputs, kwargs)
    #     super().on_chain_end(outputs, **kwargs)
        
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # print('LLM NEW TOKEN', token, kwargs)
        super().on_llm_new_token(token, **kwargs)
        
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        print('LLM START SERIALIZED', serialized, prompts, kwargs, flush=True)
        # if self._current_thought is None:
        #     self._current_thought = LLMThought(
        #         parent_container=self._parent_container,
        #         expanded=self._expand_new_thoughts,
        #         collapse_on_complete=self._collapse_completed_thoughts,
        #         labeler=self._thought_labeler,
        #     )
        super().on_llm_start(serialized, prompts, **kwargs)
        # detect whether streaming mode is on
        self.streaming = serialized.get('kwargs', {}).get('streaming', False)
        # use this place holder to show the thinking container immediately
        self._require_current_thought().container.markdown('')
        
    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        print('AGENT FINISH', finish, color, kwargs)
        super().on_agent_finish(finish, color, **kwargs)
        # if self._current_thought is not None:
        #     self._current_thought.complete(
        #         self._thought_labeler.get_final_agent_thought_label()
        #     )
        #     self._current_thought = None
        
    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        print('TOOL START', serialized, input_str, kwargs)
        if self._current_thought is None:
            self._current_thought = LLMThought(
                parent_container=self._parent_container,
                expanded=self._expand_new_thoughts,
                collapse_on_complete=self._collapse_completed_thoughts,
                labeler=self._thought_labeler,
            )
        super().on_tool_start(serialized, input_str, **kwargs)
        # use this place holder to show the thinking container immediately
        self._require_current_thought().container.markdown('')
    
    def on_tool_end(
        self,
        output: Any,
        color: Optional[str] = None,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        print('TOOL END', output, color, observation_prefix, llm_prefix, kwargs)
        # super().on_tool_end(output, color, observation_prefix, llm_prefix, **kwargs)
        output = str(output)
        self._require_current_thought().container.markdown(output)
        self._complete_current_thought()
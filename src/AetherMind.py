import os
import sys
import streamlit as st
import numpy as np
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages.chat import ChatMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.tool import ToolMessage
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_community.callbacks import StreamlitCallbackHandler
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint import MemorySaver
from langchain_community.callbacks.streamlit.streamlit_callback_handler import LLMThoughtLabeler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AetherMind.configs.models import available_models
from AetherMind.tools.bolosophy import BolosophyTool
from AetherMind.tools.draw import DrawTool
from AetherMind.utils.streamlit_utils import get_streamlit_cb, write_token_usage
from AetherMind.utils.langchain_utils import get_messages_from_checkpoint_tuple
from AetherMind.utils.llm_utils import get_model_price
from AetherMind.utils.router import render_toc_with_expander
from AetherMind.graphs.chat_with_tools_graph import get_chat_with_tools_graph
from AetherMind.callbacks.custom_streamlit_callback_handler import CustomStreamlitCallbackHandler

OPEN_ROUTER_API_BASE = 'https://openrouter.ai/api/v1'
OPEN_ROUTER_API_LINK = 'https://openrouter.ai/keys'

MODEL_NAME_AVATAR_MAP = {}

for model_group in available_models:
    for model in model_group['models']:
        MODEL_NAME_AVATAR_MAP[model['api_name']] = model_group['icon']
        # MODEL_NAME_AVATAR_MAP[f"{model_group['open_router_prefix']}/{model['api_name']}"] = model_group['icon']

st.set_page_config(
    page_title='AetherMind', 
    page_icon='🎭'
)

def clear_history():
    # st.session_state.messages = []
    st.session_state.checkpoint_tuple = None

# Initialize chat history
if "checkpoint_tuple" not in st.session_state:
    st.session_state.checkpoint_tuple = None
    
# sidebar
with st.sidebar:
    # new chat
    # st.markdown('---')
    render_toc_with_expander()
    st.title('🎭AetherChat')
    # st.markdown('A chatbot assistant designed by Aether.')
    st.button('New chat', on_click=clear_history)
    # model selection
    with st.popover('Switch model'):
        model_group = st.selectbox('Select model group', available_models, format_func=lambda x: x['group'], index=3)
        model = st.selectbox('Select model', model_group['models'], 
                            format_func=lambda x: ('[FREE!] ' if x['is_free'] else '') + x['display_name'])
    if model['is_free']:
        st.caption(' 🎉 Free model at your service!')
    else:
        st.caption('❗Why not try a free model?')
    
    st.markdown('---')
    
    # current_model_container = st.container()
    # current_model_container.subheader('✨ Using model')
    st.markdown(f'<img src="{model_group["icon"]}" alt="{model["display_name"]}" height="28px">&nbsp;&nbsp;&nbsp;**{model["display_name"]}**', unsafe_allow_html=True)
    
    # select api provider
    ambi_api_support = model_group['supports_official_api'] and model_group['supports_open_router']
    if ambi_api_support:
        api_provider = st.radio('Which provider to use', 
                                horizontal=True, 
                                options=['Official API', 'OpenRouter'],
                                help='OpenRouter is an LLM router service. One key for all major LLMs. [learn more](https://openrouter.ai/)')
    elif model_group['supports_official_api']:
        api_provider = 'Official API'
    elif model_group['supports_open_router']:
        api_provider = 'OpenRouter'
    else:
        api_provider = None
        st.error(f'No API provider available for {model_group["group"]}.')
    # get model price
    model_price = get_model_price(f'{model_group["open_router_prefix"]}/{model["api_name"]}', 
                                    api_provider if api_provider == 'OpenRouter' else model_group["group"])   
    if model_price:
        detail_str = ', '.join([f'{k} {v}' for k, v in model_price.items()])
        # st.caption(detail_str)
        st.caption(f'💸 {detail_str}')
    # api key
    use_free_key = False
    if api_provider == 'Official API':
        api_key = st.text_input(f'{model_group["group"]} API Key', type='password',
                                help=f'Get your API key from [link]({model_group["official_api_link"]})')
        api_base = model_group['official_api_base']
        model_name = model['api_name']
    elif api_provider == 'OpenRouter':
        if model['is_free']:
            use_free_key = st.checkbox('Fancy free trial?', value=True, help='Check this box to use a free trial key provided by us.')
        if use_free_key:
            api_key = st.secrets['free_open_router_key']
        else:
            api_key = st.text_input('OpenRouter API Key', type='password',
                                    help=f'Get your API key from [link]({OPEN_ROUTER_API_LINK})')
        api_base = OPEN_ROUTER_API_BASE
        model_name = f"{model_group['open_router_prefix']}/{model['api_name']}"
    else:
        api_key = None
        api_base = None
        model_name = None
    if not use_free_key: 
        st.caption('🔒 Your API key is safe with us. We won\'t store it or use it outside the scope of your actions on this site.')
    
    
    # tools
    st.markdown('---')
    st.subheader('🛠️ Use tools')
    available_tools = [
        BolosophyTool(), 
        DrawTool()
    ]
    if not model['native_tool_support']:
        st.caption('🚨 :red[No native tool support for this model!]',
            help='''Tools will be used in an ad-hoc manner by means of system message.
                The performance may be less optimal and is prone to errors. More tokens are also expected.
            ''')
    # else:
    #     st.caption('✅ Native tool support available!')
    tools = []
    for tool in available_tools:
        use_cur_tool = st.checkbox(f'{tool.emoji} {tool.name}', help=tool.description)
        if use_cur_tool:
            tools.append(tool)
            with st.container(border=True):
                tool.st_config()
        
    # parameters
    st.markdown('---')
    st.subheader('🎰 Parameters')
    with st.container(height=250):
        temprature = st.slider('temprature', 
                                min_value=0.,
                                max_value=2.,
                                step=0.1,
                                value=1.,
                                format='%.1f',
                                help='''What sampling temperature to use, between 0 and 2. 
                                Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. 
                                We generally recommend altering this or `top_p` but not both. 
                                Default to 1.''')
        top_p = st.slider('top_p', 
                            min_value=0.,
                            max_value=1.,
                            step=0.1,
                            value=0.999,
                            format='%.1f',
                            help='''An alternative to sampling with temperature, called nucleus sampling, 
                            where the model considers the results of the tokens with top_p probability mass. 
                            So 0.1 means only the tokens comprising the top 10% probability mass are considered. 
                            We generally recommend altering this or `temperature` but not both. 
                            Default to 1.''')
        frequency_penalty = st.slider('frequency_penalty', 
                                        min_value=-2.,
                                        max_value=2.,
                                        step=0.1,
                                        value=0.,
                                        format='%.1f',
                                        help='''Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, 
                                        decreasing the model's likelihood to repeat the same line verbatim.''')
        presence_penalty = st.slider('presence_penalty', 
                                        min_value=-2.,
                                        max_value=2.,
                                        step=0.1,
                                        value=0.,
                                        format='%.1f',
                                        help='''Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, 
                                        increasing the model's likelihood to talk about new topics.''')
        max_tokens = st.number_input('max_tokens', 
                                        min_value=1,
                                        value=None,
                                        placeholder='No limit',
                                        help='''The maximum number of tokens that can be generated in the chat completion. 
                                        The total length of input tokens and generated tokens is limited by the model's context length.''')
        # currently unusable
        # logprobs = st.checkbox('Return log probabilities', 
        #                                 value=False,
        #                                 help='''Whether to return log probabilities of the output tokens or not. If true, returns the log probabilities of each output token returned.''')
        # if logprobs:
        #     top_logprobs = st.number_input('top_logprobs', 
        #                                 min_value=0,
        #                                 max_value=20,
        #                                 value=0,
        #                                 placeholder='Don\'t return',
        #                                 help='''An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability. `logprobs` must be set to `true` if this parameter is used.''')
        # else:
        #     top_logprobs = None
        
main_placeholder = st.empty()
main_container = main_placeholder.container()
if st.session_state.checkpoint_tuple is None or len(get_messages_from_checkpoint_tuple(st.session_state.checkpoint_tuple)) == 0:
    # Display welcome message
    with main_container:
        st.title('📎Welcome to AetherMind!')
        st.markdown("Ask me anything!")
else:
    # Display chat messages from history on app rerun
    with main_container:
        msg_container = None
        messages = get_messages_from_checkpoint_tuple(st.session_state.checkpoint_tuple)
        for idx, message in enumerate(messages):
            expanded = (idx == len(messages)-1)
            if isinstance(message, AIMessage):
                role = 'assistant'
                avatar = None
                msg_model_name = message.response_metadata.get('model_name', 'Bot')
                if msg_model_name:
                    avatar = MODEL_NAME_AVATAR_MAP.get(msg_model_name.split('/')[-1], None)
                # if has tool calls
                # tool_calls = message.tool_calls
                if msg_container is None:
                    msg_container = st.chat_message(role, avatar=avatar)
                with msg_container:
                    expander = st.expander(f'✅ **{msg_model_name}**', expanded=expanded)
                    expander.write(message.content)
                    if message.tool_calls:
                        for tool_call in message.tool_calls:
                            expander.caption(f"🛠️ Tool call: `{tool_call['name']}` with arguments ```{tool_call['args']}```")
                    write_token_usage(expander, message)
            elif isinstance(message, HumanMessage):
                role = 'user'
                msg_container = st.chat_message(role)
                with msg_container:
                    st.write(message.content)
                # revert msg_container as well
                msg_container = None
            elif isinstance(message, ToolMessage):
                # append intermediate step info to the current container
                with msg_container:
                    with st.expander(f'🛠️ **{message.name}**', expanded=expanded):
                        st.write(message.content)
        
# React to user input
if prompt := st.chat_input("What is up?"):
    # For first message, empty the main placeholder
    if len(get_messages_from_checkpoint_tuple(st.session_state.checkpoint_tuple)) == 0:
        main_placeholder.empty()
        main_container = main_placeholder.container()
    # Display user message in chat message container
    with main_container:
        with st.chat_message("user"):
            st.write(prompt)
    
    if not api_key:
        st.error("Please add your API key to continue.")
        st.stop()
    
    # generate response
    with main_container:
        with st.chat_message("assistant", avatar=MODEL_NAME_AVATAR_MAP.get(model_name.split('/')[-1], None)):
            msg_container = st.container()
            # stream_handler = StreamHandler(msg_container)
            stream_handler = get_streamlit_cb(CustomStreamlitCallbackHandler, 
                                              parent_container=msg_container, 
                                              expand_new_thoughts=True, 
                                              collapse_completed_thoughts=False,)
            config = {
                "configurable": {"thread_id": "thread-1"},
                "callbacks": [stream_handler],
            }
            streaming = True
            if model_group['group'] == 'Qwen' and len(tools):
                # qwen doesn't support streaming when using tools
                streaming = False
            model_kwargs = {
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                # "logprobs": logprobs,
                # "top_logprobs": top_logprobs,
            }
            if streaming:
                model_kwargs['stream_options'] = {
                    "include_usage": True,
                }
            llm = ChatOpenAI(openai_api_base=api_base,
                            openai_api_key=api_key, 
                            model_name=model_name,
                            max_tokens=max_tokens,
                            temperature=temprature,
                            model_kwargs=model_kwargs,
                            streaming=streaming, 
                            # callbacks=[stream_handler],
                        )
            # if logprobs:
            #     llm = llm.bind(logprobs=True)
            # if len(tools):
            #     llm = llm.bind_tools(tools)
            # set memory from session
            memory = MemorySaver()
            if st.session_state.get('checkpoint_tuple', None):
                memory.put(config=st.session_state.checkpoint_tuple.config,
                           checkpoint=st.session_state.checkpoint_tuple.checkpoint,
                           metadata=st.session_state.checkpoint_tuple.metadata)
            # get graph
            graph = get_chat_with_tools_graph(llm, tools, memory, 
                                              use_ad_hoc_tool_agent=len(tools) and not model['native_tool_support'])
            
            # interrupt button
            interrupt_placeholder = st.empty()
            with interrupt_placeholder:
                st.button('Stop', help='Stop the current conversation.', type="primary",)

            for s in graph.stream({'messages': [HumanMessage(role="user", content=prompt)]}, config, stream_mode="values"):
                message = s['messages'][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
                # print(message)
                # add model name to response metadata
                message.response_metadata['model_name'] = model_name
                # if chat response content is empty, replace it with a space
                # this is to bypass the bug that a None might be sent to llm
                # and cause an error
                if not message.content or message.content == '':
                    message.content = ' '
            # write last message when all intermedite nodes are done
            # msg_container.write(message.content)
            # write_token_usage(message)
            # update chat history
            checkpoint_tuple = memory.get_tuple(config)
            st.session_state.checkpoint_tuple = checkpoint_tuple
            
            # clear interrupt button
            interrupt_placeholder.empty()

# additional informations

@st.experimental_dialog("Raw messages", width='large')
def show_raw_messages():
    with st.container(height=450):
        st.json(st.session_state.checkpoint_tuple.checkpoint)
    
if len(get_messages_from_checkpoint_tuple(st.session_state.checkpoint_tuple)):
    if st.button('Show raw messages'):
        show_raw_messages()

from typing import Optional, Type
import requests
import json

from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_milvus.vectorstores import Zilliz
import streamlit as st

from AetherMind.utils.embedding_utils import (
    get_zilliz_vectorstore, get_embeddings, similarity_search
)
                                        
class BolosophyInput(BaseModel):
    query: str = Field(description="search query string")


class BolosophyTool(BaseTool):
    name = "Bolosophy"
    description = "A local knowledge base constructed by Aether, containing book notes, personal thoughts, etc. Useful for when asked to search Aether\'s knowledge base or to answer questions about some professional topics an LLM have no knowledge of."
    args_schema: Type[BaseModel] = BolosophyInput
    return_direct: bool = False
    
    emoji: str = "📚"
    vectorstore: Zilliz = None
    embeddings: HuggingFaceEndpointEmbeddings = None
    num_entries: int = 5
    
    def __init__(self):
        super().__init__()
        self.vectorstore = get_zilliz_vectorstore()
        self.embeddings = get_embeddings()

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        print('Bolosophy test with query:', query)
        docs = similarity_search(self.embeddings, self.vectorstore, query, self.num_entries)
        print(f'{len(docs)} results retrieved')
        print(docs)
        if len(docs):
            result = 'Following are the results from this query: \n\n' + '\n'.join([f"- {doc.text}" for doc in docs])
        else:
            result = 'No results found for this query'
        return result
    
    def st_config(self):
        """config setting in streamlit"""
        self.num_entries = st.slider('Number of entries', 
                            min_value=1,
                            max_value=10,
                            step=1,
                            value=5,
                            help='''Maximum number of knowledge base entries to return.''')

if __name__ == '__main__':
    tool = BolosophyTool()
    print(tool.name)
    print(tool.description)
    print(tool.args)
    print(tool.return_direct)

    print(tool.invoke({"query": '商鞅与管仲对商人阶层的区别', "num_entries": 5}))
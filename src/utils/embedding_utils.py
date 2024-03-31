from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from pymilvus import (connections, Collection, AnnSearchRequest, RRFRanker)
import streamlit as st
from AetherMind.configs import embedding as embedding_config

_zilliz_vectorstore = None

def get_embeddings():
    return HuggingFaceEndpointEmbeddings(
        model= embedding_config.model_name,
        task="feature-extraction",
        huggingfacehub_api_token=st.secrets['huggingface_key'],
        model_kwargs={}
    )
    
def get_zilliz_vectorstore():
    global _zilliz_vectorstore
    if _zilliz_vectorstore is None:
        connections.connect(
            uri=st.secrets['zilliz_uri'],
            token=st.secrets['zilliz_key'],
        )
        _zilliz_vectorstore = Collection(name=embedding_config.collection_name)
        _zilliz_vectorstore.load()
    return _zilliz_vectorstore

def similarity_search(embeddings, vectorstore, query, top_k=5):
    # Instruct required by multilingual-e5-large-instruct, see https://huggingface.co/intfloat/multilingual-e5-large-instruct#faq
    instruct = f'Instruct: Given a keyword, retrieve documents most relevant to it.\nQuery: {query}'
    # print(instruct, flush=True)
    query_embedding = embeddings.embed_query(instruct)
    # hybrid search
    summary_req = AnnSearchRequest(
        [query_embedding], "text_vector", {"metric_type": "COSINE"}, limit=top_k
    )
    content_req = AnnSearchRequest(
        [query_embedding], "text_vector", {"metric_type": "COSINE"}, limit=top_k
    )
    docs = vectorstore.hybrid_search(
        [summary_req, content_req], rerank=RRFRanker(),
        limit=top_k, 
        output_fields=["text", "summary", "source", "chapter", "note_idx", "is_thought"]
    )[0]
    return docs


import os
import sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from AetherMind.utils.router import render_toc
from AetherMind.utils.embedding_utils import (
    get_zilliz_vectorstore, get_embeddings, similarity_search
)

st.set_page_config(
    page_title='Retriever #42 | AetherMind', 
    page_icon='👓'
)

with st.sidebar:
    render_toc()
    
def retrieve(query, top_k=5):
    vectorstore = get_zilliz_vectorstore()
    embeddings = get_embeddings()
    docs = similarity_search(embeddings, vectorstore, query, top_k)
    return docs

st.title('👓Retriever #42')

st.write('Retrieves knowledge from Aether\'s knowledge base.')

with st.form('query_form'):
    query = st.text_input('Query', placeholder='Your ultimate question...')
    top_k = st.slider('Top K', value=10, min_value=1, max_value=20)
    # score_threshold = st.slider('Score Threshold', value=0.5, min_value=0.0, max_value=1.0, step=0.01)
    st.form_submit_button('Submit')

if query:
    with st.spinner('Retrieving results...'):
        docs = retrieve(query, top_k=top_k)
    st.write(f'{len(docs)} results retrieved')
    for idx, doc in enumerate(docs):
        with st.container(border=True):
            st.write(f'**#{idx+1} {doc.summary}**')
            st.write(doc.text)
            st.caption(f"《{doc.source}》 {doc.chapter}")
            st.caption(f"Relevance score: {doc.score:.4f}")
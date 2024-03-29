import os
import sys
import argparse
import json
import time

# from langchain.indexes import SQLRecordManager
# from langchain_core.indexing.api import index
from langchain_openai.chat_models.base import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from AetherMind.document_loaders.weread_loader import WeReadLoader
from AetherMind.utils.langchain_utils import get_zilliz_vectorstore, get_embeddings
from AetherMind.configs.embedding import (collection_name, summarizer_model_name, 
                                        summarizer_template, summarizer_api_base)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--file_path', type=str, required=True, help='Path to the file')
    parser.add_argument('--book_name', type=str, required=True, help='Name of the book')
    parser.add_argument('--booknote_type', type=str, choices=['weread'], default='weread', help='Type of the booknote')
    parser.add_argument('--language', type=str, choices=['en', 'cn'], default='cn', help='Language of the book')
    # parser.add_argument('--embedding_model', type=str, default="BAAI/bge-m3", help='Model for embedding')
    parser.add_argument('--embedding_batch_size', type=int, default=64, help='Batch size for embedding')
    # parser.add_argument('--force_update', action='store_true', default=False, help='Force update')
    
    args = parser.parse_args()
    
    # summarizer
    summarizer = ChatOpenAI(openai_api_base=summarizer_api_base[args.language],
                    openai_api_key=st.secrets['summarizer_key'], 
                    model_name=summarizer_model_name[args.language],
                    temperature=1,
                    streaming=False, 
                )
    summarizer = ChatPromptTemplate.from_template(summarizer_template[args.language]) | summarizer
    
    # get loader
    if args.booknote_type == 'weread':
        loader = WeReadLoader(args.file_path, args.book_name, summarizer=summarizer)
    else:
        raise ValueError(f"Unsupported booknote type: {args.booknote_type}")
    
    # get embeddings
    # embeddings = get_embeddings()
    
    # connect to zilliz
    vectorstore = get_zilliz_vectorstore()
    
    # test embedding
    embeddings = get_embeddings()
    embedding_sample = embeddings.embed_query('说点smart的话')
    print('embedding dimension', len(embedding_sample))
    # vectorstore.add_texts(["test"], metadatas=[{"source": "test"}])
    
    # load documents
    # docs = loader.load()
    # print('number of documents:', len(docs))
    # with open('data/output.json', 'w', encoding='utf-8') as f:
    #     json.dump([doc.dict() for doc in docs], f, ensure_ascii=False, indent=4)
    
    with open('data/output.json', 'r', encoding='utf-8') as f:
        docs = json.load(f)
        
    # embedding and write into vectorstore
    batch = []
    batch_num = 0
    for idx, doc in enumerate(docs):
        batch.append(doc)
        if (idx + 1) % args.embedding_batch_size == 0 or idx == len(docs) - 1:
            # Process the batch here
            batch_num += 1
            print(f'Processing batch {batch_num}...')
            # Embed
            content_batch = [doc['page_content'] for doc in batch]
            summary_batch = [doc['metadata']['summary'] for doc in batch]
            content_embeddings = embeddings.embed_documents(content_batch)  # replace with your embedding function
            time.sleep(1)
            summary_embeddings = embeddings.embed_documents(summary_batch)  # replace with your embedding function
            # Write into vectorstore
            vectorstore.insert(data=[
                {
                    "text": doc['page_content'],
                    "summary": doc['metadata']['summary'][:100],
                    "source": doc['metadata']['source'],
                    "chapter": doc['metadata']['chapter'],
                    "note_idx": doc['metadata']['note_idx'],
                    "text_vector": content_embeddings[i],
                    "summary_vector": summary_embeddings[i],
                } for i, doc in enumerate(batch)
            ], collection_name=collection_name)
            batch.clear()
            
    
if __name__ == "__main__":
    main()
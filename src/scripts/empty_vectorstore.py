import os
import sys
import argparse

from langchain.indexes import SQLRecordManager
from langchain_core.indexing.api import index

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from AetherMind.document_loaders.weread_loader import WeReadLoader
from AetherMind.utils.langchain_utils import get_zilliz_vectorstore
from AetherMind.configs.embedding import collection_name

# NOT WORKING CURRENTLY SOMEHOW

def main():
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('--file_path', type=str, required=True, help='Path to the file')
    # parser.add_argument('--book_name', type=str, required=True, help='Name of the book')
    # parser.add_argument('--booknote_type', type=str, choices=['weread'], default='weread', help='Type of the booknote')
    # # parser.add_argument('--embedding_model', type=str, default="BAAI/bge-m3", help='Model for embedding')
    # parser.add_argument('--embedding_batch_size', type=int, default=64, help='Batch size for embedding')
    # parser.add_argument('--force_update', action='store_true', default=False, help='Force update')
    
    # args = parser.parse_args()
    
    # connect to zilliz
    vectorstore = get_zilliz_vectorstore()
    
    # set record manager
    namespace = f"zilliz/{collection_name}"
    record_manager = SQLRecordManager(
        namespace, db_url="sqlite:///record_manager_cache.sql"
    )
    record_manager.create_schema()
    
    result = index([], record_manager, vectorstore, cleanup="full", source_id_key="source")
    
    print('empty result')

if __name__ == "__main__":
    main()
import os
import sys
import streamlit as st
import traceback
import time
import json
import math
from io import StringIO
from langchain_openai.chat_models.base import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import or_

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from AetherMind.database.session import get_session
from AetherMind.models.book import Book
from AetherMind.utils.router import render_toc
from AetherMind.configs import embedding as embedding_config
from AetherMind.document_loaders.weread_loader import WeReadLoader
from AetherMind.utils.embedding_utils import get_zilliz_vectorstore, get_embeddings
from AetherMind.utils.book_utils import (get_book_cover_from_douban, upload_image_to_imgur,
                                get_image_from_url, parse_epub_to_txt)

st.set_page_config(
    page_title='Book Manager | AetherMind', 
    page_icon='📚'
)

with st.sidebar:
    render_toc()
    
st.title('📚 Book Manager')

PAGE_LIMIT = 10
BOOK_LIST_COLUMNS = 2
EMBEDDING_BATCH_SIZE = 64
DEFAULT_COVER_URL = 'https://hatscripts.github.io/circle-flags/flags/xx.svg'

vectorstore = get_zilliz_vectorstore()

def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ''

# dialogs
@st.dialog('Add a book', width='large')
def add_book(title, authors, source_type, language, book_notes_file):
    if book_notes_file is None:
        raise ValueError('Please upload a book notes file')
    
    # Check file extension and get string value
    file_extension = book_notes_file.name.split('.')[-1].lower()
    
    if file_extension == 'txt':
        book_content = book_notes_file.getvalue().decode("utf-8")
    elif file_extension == 'epub':
        # Create directory if it doesn't exist
        epub_upload_dir = './static/epub_uploads'
        os.makedirs(epub_upload_dir, exist_ok=True)
        # Save the uploaded epub file
        epub_path = os.path.join(epub_upload_dir, book_notes_file.name)
        with open(epub_path, 'wb') as f:
            f.write(book_notes_file.getvalue())
        
        book_content = parse_epub_to_txt(epub_path)
        # Remove the temporary epub file
        os.remove(epub_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    # ensure no title conflict
    with get_session() as session:
        if session.query(Book).filter(Book.name == title).first():
            raise ValueError('Book already exists')
    
    embedding_model = embedding_config.model_name
    summary_model = embedding_config.summarizer_model_name[language]
    new_book = Book(
                name=title,
                authors=authors,  # Assuming authors are comma-separated
                source_type=1 if source_type == 'WeRead' else 2,
                language=1 if language == 'cn' else 2,
                embedding_model=embedding_model,
                summary_model=summary_model
            )
    st_display_book_details(new_book, is_adding_new_book=True, raw_book_notes=book_content)
    
    # summarizer
    summarizer = ChatOpenAI(openai_api_base=embedding_config.summarizer_api_base[language],
                    openai_api_key=st.secrets['summarizer_key'], 
                    model_name=summary_model,
                    temperature=1,
                    streaming=False, 
                )
    summarizer = ChatPromptTemplate.from_template(embedding_config.summarizer_template[language]) | summarizer
    
    if source_type in ['WeRead', 'iReader']:
        Loader = WeReadLoader
    else:
        raise ValueError(f"Unsupported book source type: {source_type}")
    
    book_notes_file_source = StringIO(book_content)
    
    parsed_cache_file = f'static/parsed_cache/{title}.json'
    parsed_done_file = f'static/parsed_done/{title}.json'
    if not os.path.exists(os.path.dirname(parsed_cache_file)):
        os.makedirs(os.path.dirname(parsed_cache_file))
    if not os.path.exists(os.path.dirname(parsed_done_file)):
        os.makedirs(os.path.dirname(parsed_done_file))
    if os.path.exists(parsed_cache_file):
        read_cache = st.toggle('Read from cache', value=True)
    else:
        read_cache = False
    
    close_on_finish = st.toggle('Close on finish', value=False)
        
    placeholder = st.empty()
    confirm_btn = placeholder.button('Confirm', icon=':material/check:')
    if confirm_btn:
        with placeholder.container():
            if read_cache:
                with open(parsed_cache_file, 'r', encoding='utf-8') as f:
                    docs = json.load(f)
                    new_book.num_notes = docs[-1]['metadata']['note_idx']
                    new_book.num_entries = len(docs)
            else:   
                with st.status('Parsing notes...', state='running', expanded=True) as status:
                    try:
                        load_ctn = st.container(height=200)
                        loader = Loader(book_notes_file_source, title, summarizer=summarizer, st_container=load_ctn, chunk_size=embedding_config.chunk_size[language])
                        docs = loader.load()
                        new_book.num_notes = loader.note_idx
                        new_book.num_entries = len(docs)
                        status.update(label=f'{len(docs)} notes parsed, {new_book.num_entries} entries', state='complete', expanded=False)
                    except Exception as e:
                        status.update(label='Error parsing notes', state='error')
                        st.write(f":red[An error occurred while parsing notes: {str(e)}]")
                        with st.container(height=200):
                            st.code(traceback.format_exc(), language='python')
                        st.stop()

                # write cache
                with open(parsed_cache_file, 'w', encoding='utf-8') as f:
                    json.dump([doc.dict() for doc in docs], f, ensure_ascii=False, indent=4)
            
            with st.status('Writing to database...', state='running', expanded=True) as status:
                try:
                    with get_session() as session:
                        session.add(new_book)
                        session.commit()
                    status.update(label='Database written', state='complete', expanded=False)
                    st.write(f"Book '{title}' has been added to the database.")
                except Exception as e:
                    status.update(label='Error writing to database', state='error')
                    st.write(f":red[An error occurred while writing to database: {str(e)}]")
                    with st.container(height=200):
                        st.code(traceback.format_exc(), language='python')
                    st.stop()

            vectorstore = get_zilliz_vectorstore()
            embeddings = get_embeddings()
            num_entries = len(docs)
            with st.status('Writing to vector store...', state='running', expanded=True) as status:
                try:
                    # progress_bar = st.progress(0, text=f'Progressing... {0}/{num_entries}')
                    batch_idx = 0
                    batch_count = math.ceil(len(docs) / EMBEDDING_BATCH_SIZE)
                    for i in range(0, len(docs), EMBEDDING_BATCH_SIZE):
                        batch_idx += 1
                        st.write(f'Progressing batch #{batch_idx} of {batch_count}...')
                        batch = docs[i:i+EMBEDDING_BATCH_SIZE]
                        # parse to dict, because cached docs are dicts
                        if not isinstance(batch[0], dict):
                            batch = [doc.dict() for doc in batch]
                        content_batch = [doc["page_content"] for doc in batch]
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
                                "is_thought": doc['metadata']['is_thought'],
                                "text_vector": content_embeddings[j],
                                "summary_vector": summary_embeddings[j],
                            } for j, doc in enumerate(batch)
                        ])
                        # progress_bar.progress((i + 1) / num_entries, text=f'Progressing... {i + 1}/{num_entries}')
                    status.update(label='Vector store written', state='complete', expanded=False)
                    st.write(f'{len(docs)} entries written')
                except Exception as e:
                    status.update(label='Error writing to vector store', state='error')
                    st.write(f":red[An error occurred while writing to vector store: {str(e)}]")
                    with st.container(height=200):
                        st.code(traceback.format_exc(), language='python')
                    st.stop()
                    
        st.toast(f'Book {title} added!', icon='🍾')
        # delete cache
        os.rename(parsed_cache_file, parsed_done_file)
        # get books
        st.session_state.page = 0
        st.session_state.search_query = ''
        if close_on_finish:
            time.sleep(1)
            st.rerun()

@st.dialog('Book details', width='large')
def show_book_details(book_id):
    with get_session() as session:
        book = session.get(Book, book_id)
        st_display_book_details(book)
        update_btn = st.button('Update Book', icon=":material/edit_note:")
        if update_btn:
            with st.status('Updating database...', state='running', expanded=True) as status:
                try:
                    session.commit()
                    session.refresh(book)
                    status.update(label='Database updated', state='complete', expanded=False)
                    st.write(f"Book '{book.name}' has been updated in database.")
                except Exception as e:
                    status.update(label='Error updating database', state='error')
                    st.write(f":red[An error occurred while updating database: {str(e)}]")
                    with st.container(height=200):
                        st.code(traceback.format_exc(), language='python')
    
        del_placeholder = st.empty()
        del_btn = del_placeholder.button('Delete Book', type='primary', icon=':material/delete:')
        if del_btn:
            with del_placeholder.container():
                with st.status('Deleting from vector store...', state='running', expanded=True) as status:
                    try:
                        vectorstore = get_zilliz_vectorstore()
                        del_result = vectorstore.delete(f'source == "{book.name}"')
                        status.update(label='Deleted from vector store', state='complete', expanded=False)
                        st.write(f'{del_result.delete_count} entries deleted')
                        st.write(f"Book '{book.name}' has been deleted from vector store.")
                    except Exception as e:
                        status.update(label='Error deleting from vector store', state='error')
                        st.write(f":red[An error occurred while deleting from vector store: {str(e)}]")
                        with st.container(height=200):
                            st.code(traceback.format_exc(), language='python')
                        st.stop()
                        
                with st.status('Deleting from database...', state='running', expanded=True) as status:
                    try:
                        session.delete(book)
                        session.commit()
                        status.update(label='Deleted from database', state='complete', expanded=False)
                        st.write(f"Book '{book.name}' has been deleted from database.")
                    except Exception as e:
                        status.update(label='Error deleting from database', state='error')
                        st.write(f":red[An error occurred while deleting from database: {str(e)}]")
                        with st.container(height=200):
                            st.code(traceback.format_exc(), language='python')
                        st.stop()
            
            st.toast('Book deleted!', icon='🗑️')
            time.sleep(1)
            st.rerun()

# db operations
def get_books():
    page = st.session_state.page or 0
    page_limit = PAGE_LIMIT
    search_query = st.session_state.search_query or ''
    with get_session() as session:
        query = session.query(Book).filter(
            or_(
                Book.name.ilike(f'%{search_query}%'),
                Book.authors.ilike(f'%{search_query}%')
            )
        )
        
        # Get total count
        total_count = query.count()
        
        # Get books for current page
        books = query.order_by(Book.id.desc()).offset(page * page_limit).limit(page_limit).all()
        
        return {
            "count": total_count,
            "data": books
        }
    
def get_chapters_by_book(book: Book):
    results = vectorstore.query(
        expr=f'source == "{book.name}"',
        output_fields=['chapter', 'note_idx']
    )
    sorted_results = sorted(results, key=lambda x: x['note_idx'])
    chapters = []
    for result in sorted_results:
        chapter = result['chapter']
        if chapter not in chapters:
            chapters.append(chapter)
    return chapters

def get_notes_by_chapter(book: Book, chapter: str):
    results = vectorstore.query(
        expr=f'source == "{book.name}" and chapter == "{chapter}"',
        output_fields=['note_idx', 'text', 'summary']
    )
    results = sorted(results, key=lambda x: x['note_idx'])
    return results
    
@st.fragment
def st_display_notes(book: Book):
    chapters = get_chapters_by_book(book)
    sel_chapter = st.selectbox('Select a chapter', chapters)
    notes = get_notes_by_chapter(book, sel_chapter)
    with st.container(border=True, height=500):
        st.write(notes)
    
def st_display_book_details(book: Book, is_adding_new_book=False, raw_book_notes=None):
    columns = st.columns([1, 2])
    with columns[0]:
        with st.spinner('Loading book info...'):
            cover_placeholder = st.empty()
            if not book.cover_url:
                book.cover_url = get_book_cover_from_douban(book.name)
            if book.cover_url:
                cover_placeholder.image(get_image_from_url(book.cover_url),
                                        use_column_width=True)
            else:
                cover_placeholder.image(DEFAULT_COVER_URL, use_column_width=True)
        uploaded_cover = st.file_uploader('Upload Cover', type=['jpg', 'png', 'jpeg', 'gif'])
        if uploaded_cover:
            book.cover_url = upload_image_to_imgur(uploaded_cover, book.name, f'Cover of {book.name}')
            cover_placeholder.image(get_image_from_url(book.cover_url),
                                    use_column_width=True)
    with columns[1]:
        st.write(f'**{book.name}** by {book.authors.replace(",", ", ")}')
        source_type = 'WeRead' if book.source_type == 1 else 'iReader'
        language = '中文' if book.language == 1 else 'English'
        st.write(f'`{source_type}` `{language}`')
        st.write(f'Embedding Model: `{book.embedding_model}`')
        st.write(f'Summary Model: `{book.summary_model}`')
        if not is_adding_new_book:
            st.write(f'Notes: {book.num_notes} | Entries: {book.num_entries}')
            st_display_notes(book)
        if raw_book_notes:
            # with st.container(border=True, height=500):
            st.text_area('Preview (readonly)', value=raw_book_notes, height=500,
                         disabled=True)

@st.fragment
def st_display_booklist():
    # Add a search input field
    search_query = st.text_input("Search query", value=st.session_state.search_query,
                                 placeholder="Search books by title or author", label_visibility='collapsed')

    if search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
        st.session_state.page = 0  # Reset to first page when search query changes
        st.rerun()

    books_data = get_books()
    total_count = books_data["count"]
    books = books_data["data"]

    st.write(f"Page {st.session_state.page + 1} of {math.ceil(total_count / PAGE_LIMIT)}, total {total_count} books")

    if not books:
        st.info('No books found. Please add a book or try a different search query.')
    else:
        for i in range(0, len(books), BOOK_LIST_COLUMNS):
            columns = st.columns(BOOK_LIST_COLUMNS)
            for j in range(BOOK_LIST_COLUMNS):
                if i + j < len(books):
                    book = books[i + j]
                    with columns[j]:
                        with st.container(border=True, height=200):
                            inner_columns = st.columns([1, 2])
                            with inner_columns[0]:
                                cover_url = book.cover_url or DEFAULT_COVER_URL
                                st.image(get_image_from_url(cover_url), use_column_width=True)
                            with inner_columns[1]:
                                st.markdown(f"**{book.name}**\n\n{book.authors.replace(',', ', ')}")
                                st.caption(f"Notes: {book.num_notes} | Entries: {book.num_entries}")
                                st.button('Details', on_click=show_book_details, args=(book.id,), 
                                          key=f'more_{book.id}', use_container_width=True,
                                          icon=':material/book:')
   
    # Add pagination controls
    prev_page_col, next_page_col = st.columns([1, 1])
    with prev_page_col:
        if st.button("Prev", icon=":material/chevron_left:", 
                     disabled=st.session_state.page == 0,
                     use_container_width=True):
            st.session_state.page -= 1
            st.rerun()
    with next_page_col:
        if st.button("Next", icon=":material/chevron_right:", 
                     disabled=st.session_state.page == math.ceil(total_count / PAGE_LIMIT) - 1,
                     use_container_width=True):
            st.session_state.page += 1
            st.rerun()

    st.button('Refresh', icon=':material/refresh:')


# Add a book
st.subheader('Add a book')

with st.form('add_book_form', clear_on_submit=True):
    title = st.text_input('Title')
    authors = st.text_input('Authors', help='Separate authors with commas')
    source_type = st.radio('Source Type', ['WeRead', 'iReader'],
                           horizontal=True,
                        #    format_func=lambda x: 'WeRead' if x == 'weread' else 'iReader'
                           )
    language = st.radio('Language', ['cn', 'en'],
                        horizontal=True,
                        format_func=lambda x: '中文' if x == 'cn' else 'English'
                        )
    book_notes_file = st.file_uploader('Book Notes File', type=['txt', 'epub'])
    
    submitted = st.form_submit_button('Add Book', icon=":material/add:")
    if submitted:
        add_book(title, authors, source_type, language, book_notes_file)

# Book list
st.subheader('Book List')
init_session_state()
st_display_booklist()

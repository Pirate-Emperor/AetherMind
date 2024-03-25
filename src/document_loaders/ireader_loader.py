from typing import AsyncIterator, Iterator, Union
import re
from io import StringIO

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from AetherMind.document_loaders.summarize_loader import SummarizeLoader



class IReaderLoader(SummarizeLoader):
    """
    [DEPRECATED] Use WeReadLoader instead.
    
    A loader for book notes from iReader.
    """
    
    def __init__(self, file_source: Union[str, StringIO], book_name: str, summarizer=None, st_container=None, chunk_size=500):
        super().__init__(file_source, book_name, summarizer, st_container, chunk_size)
        
    def _yield_accu_text(self, accu_text, chapter_name) -> Iterator[Document]:
        if accu_text:
            self.note_idx += 1
            # is_thought = re.match(self.thought_regex, accu_text) is not None
            doc = Document(page_content=accu_text, 
                            metadata={
                                "source": self.book_name, 
                                "chapter": chapter_name,
                                'note_idx': self.note_idx,  
                                'is_thought': False,
                            })
            if self.note_idx % 100 == 0:
                self._log_progress(f'Adding note No.{self.note_idx}...')
            yield from self._split_and_summarize(doc)

                 
    def lazy_load(self) -> Iterator[Document]:
        if isinstance(self.file_source, str):
            # If file_source is a string, treat it as a file path
            with open(self.file_source, encoding="utf-8") as f:
                yield from self._process_file(f)
        elif isinstance(self.file_source, StringIO):
            # If file_source is a StringIO object, use it directly
            yield from self._process_file(self.file_source)
        else:
            raise ValueError("file_source must be either a file path string or a StringIO object")

    def _process_file(self, file_obj) -> Iterator[Document]:
        accu_text = ''
        chapter_name = ''
        empty_lines_count = 0
        is_first_line = True

        for line in file_obj:
            line = line.strip()

            if not line:
                empty_lines_count += 1
                continue

            if is_first_line or empty_lines_count >= 4:
                # This is a chapter name
                if accu_text:
                    yield from self._yield_accu_text(accu_text, chapter_name)
                chapter_name = line
                accu_text = ''
            elif empty_lines_count >= 2:
                # This is a book note
                if accu_text:
                    yield from self._yield_accu_text(accu_text, chapter_name)
                accu_text = line
            else:
                # This is a continuation of the previous text
                accu_text += '\n' + line if accu_text else line

            empty_lines_count = 0
            is_first_line = False

        # Yield any remaining text
        if accu_text:
            yield from self._yield_accu_text(accu_text, chapter_name)

    def load(self):
        return list(self.lazy_load())
    

from typing import AsyncIterator, Iterator, Union
import re
from io import StringIO

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from AetherMind.document_loaders.summarize_loader import SummarizeLoader


class WeReadLoader(SummarizeLoader):
    """A loader for book notes with WeRead format."""
    
    # regex for chapter name
    chapter_name_regex = r"^(?:第[一二三四五六七八九十百千万亿]+章|Chapter)\s*"
    thought_regex = r"^\d{4}/\d{2}/\d{2}(发表想法| 认为)"
    
    def __init__(self, file_source: Union[str, StringIO], book_name: str, summarizer=None, st_container=None, chunk_size=500):
        super().__init__(file_source, book_name, summarizer, st_container, chunk_size)
        
    def _yield_accu_text(self, accu_text, chapter_name) -> Iterator[Document]:
        if accu_text:
            self.note_idx += 1
            is_thought = re.match(self.thought_regex, accu_text) is not None
            doc = Document(page_content=accu_text, 
                            metadata={
                                "source": self.book_name, 
                                "chapter": chapter_name,
                                'note_idx': self.note_idx,  
                                'is_thought': is_thought,
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
        continued_empty_lines = 0 # 2 empty lines will lead to a new chapter
        for idx, line in enumerate(file_obj):
            # Skip metadata lines
            if idx < 5: 
                continue
            line = line.strip()
            line = line.replace('\ufffc', '')
            # Skip empty lines
            if len(line) == 0:
                continued_empty_lines += 1
                continue
            # skip useless lines
            if line in ['-- 来自微信读书']:
                continue
            # Locate chapter name
            # When a new chapter starts, yield the accumulated text
            if line == '点评':
                yield from self._yield_accu_text(accu_text, chapter_name)
                accu_text = ''
                chapter_name = line
            elif continued_empty_lines >= 2 and not line.startswith('◆ '):
                yield from self._yield_accu_text(accu_text, chapter_name)
                accu_text = ''
                chapter_name = line
            elif line.startswith('◆ '):
                # A new book note starts
                yield from self._yield_accu_text(accu_text, chapter_name)
                accu_text = line[2:] # Skip '◆ '
            elif chapter_name == '':
                chapter_name = line
            else:
                accu_text += '\n' + line
            continued_empty_lines = 0
        # Yield any remaining text
        yield from self._yield_accu_text(accu_text, chapter_name)

    def load(self):
        return list(self.lazy_load())
    
if __name__ == '__main__':
    # Example usage with file path
    loader = WeReadLoader(file_source='../data/booknotes/haodang2000.txt', book_name='浩荡两千年：中国企业公元前7世纪~1869年')
    for idx, doc in enumerate(loader.load()):
        if idx < 20:
            print(doc)

    # Example usage with StringIO
    from io import StringIO
    sample_text = "... (sample WeRead notes content) ..."
    string_io = StringIO(sample_text)
    loader = WeReadLoader(file_source=string_io, book_name='Sample Book')
    for idx, doc in enumerate(loader.load()):
        if idx < 20:
            print(doc)
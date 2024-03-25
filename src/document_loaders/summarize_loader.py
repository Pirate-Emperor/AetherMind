from typing import Iterator, Union
from io import StringIO

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class SummarizeLoader(BaseLoader):
    """A base loader with summarization capabilities."""
    
    separators = [
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",
    ]
    
    def __init__(self, file_source: Union[str, StringIO], book_name: str, summarizer=None, st_container=None, chunk_size=500):
        self.file_source = file_source
        self.book_name = book_name
        self.note_idx = 0
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=self.separators,
            chunk_size=chunk_size, 
            chunk_overlap=20,
        )
        self.summarizer = summarizer
        self.st_container = st_container

    def _split_and_summarize(self, doc: Document) -> Iterator[Document]:
        for split_doc in self.text_splitter.split_documents([doc]):
            if self.summarizer is not None:
                summary = self.summarizer.invoke({'context': split_doc.page_content})
                summary = summary.content.strip().split('\n')[0]
                if summary.startswith("标题："):
                    summary = summary[3:]
                # remove quotation marks at the beginning and end
                while summary[0] in ['“', '‘', '"', '\'', '《', '"']:
                    summary = summary[1:]
                while summary[-1] in ['”', '’', '"', '\'', '》', '"']:
                    summary = summary[:-1]
                summary = summary.strip()
                # remove "标题：" again
                if summary.startswith("标题："):
                    summary = summary[3:]
                self._log_progress(f'Summary for note No.{self.note_idx}: {summary} ({split_doc.metadata["chapter"]})')
                split_doc.metadata['summary'] = summary
            yield split_doc

    def _log_progress(self, message: str):
        if self.st_container is not None:
            self.st_container.write(message)
        else:
            print(message)

    def lazy_load(self) -> Iterator[Document]:
        raise NotImplementedError("Subclasses must implement this method")

    def load(self):
        return list(self.lazy_load())

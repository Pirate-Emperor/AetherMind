# src/models/data_source.py
from sqlalchemy import Column, String, Integer, ARRAY, ForeignKey
from AetherMind.database.base import BaseModel

class Book(BaseModel):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment='Name of the book')
    authors = Column(String(100), nullable=False, comment='Authors of the book (comma-separated)')
    source_type = Column(Integer, default=1, comment='Source type of the book, 1-weread, 2-ireader')
    language = Column(Integer, default=1, comment='Language of the book, 1-cn, 2-en')
    embedding_model = Column(String(100), nullable=False, comment='Embedding model used for the book')
    num_notes = Column(Integer, default=0, comment='Number of notes in the book')
    num_entries = Column(Integer, default=0, comment='Number of embedded entries in the book')
    summary_model = Column(String(100), nullable=False, comment='Summary model used for the book')
    cover_url = Column(String(100), nullable=True, comment='Cover url of the book')
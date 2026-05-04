from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    book_title: str = Field(max_length=255)
    book_author: str = Field(max_length=255)
    book_isbn: str = Field(max_length=32)
    book_genre: str = Field(max_length=100)
    book_publication_year: int = Field(ge=0, le=9999)
    book_language: str = Field(max_length=50)
    book_status: str = Field(max_length=50)
    shelf_id: int


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookRead(BookBase):
    book_id: int
    created_at: datetime
    updated_at: datetime


class BookWithLocation(BookRead):
    room_id: int

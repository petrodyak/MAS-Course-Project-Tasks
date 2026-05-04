from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    book_title: str = Field(min_length=1, max_length=500)
    isbn: str = Field(min_length=1, max_length=32)
    author: str = Field(min_length=1, max_length=255)
    shelf_id: int
    published_date: Optional[datetime] = None
    book_description: Optional[str] = Field(default=None, max_length=2000)
    is_available: bool


class BookRead(BaseModel):
    book_id: int
    book_title: str
    isbn: str
    author: str
    shelf_id: int
    published_date: Optional[datetime]
    book_description: Optional[str]
    is_available: bool
    created_at: datetime
    updated_at: datetime


class BookLocationRead(BaseModel):
    book_id: int
    book_title: str
    shelf_id: int
    shelf_name: str
    room_id: int
    room_name: str

from __future__ import annotations

import sqlite3
from fastapi import APIRouter, HTTPException, Request

from app.schemas.book import BookCreate, BookLocationRead, BookRead
from app.services.books import BooksService

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", status_code=201, response_model=BookRead)
async def create_book(payload: BookCreate, request: Request):
    service = BooksService(request.app.state.db_path)
    try:
        return service.create(payload)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=404, detail="Referenced shelf not found")


@router.get("/{book_id}/location", response_model=BookLocationRead)
async def get_book_location(book_id: int, request: Request):
    service = BooksService(request.app.state.db_path)
    row = service.get_location(book_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return row

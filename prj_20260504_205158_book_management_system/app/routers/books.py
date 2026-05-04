from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models.book import Book
from app.models.shelf import Shelf
from app.schemas.book import BookCreate, BookRead, BookUpdate, BookWithLocation

router = APIRouter(prefix="/books", tags=["books"])


@router.get("")
def list_books(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    books = db.query(Book).order_by(Book.book_id.asc()).all()
    items = [BookRead.model_validate(b, from_attributes=True).model_dump() for b in books]
    return {"items": items}


@router.post("", status_code=201, response_model=BookRead)
def create_book(
    payload: BookCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    shelf = db.get(Shelf, payload.shelf_id)
    if not shelf:
        raise HTTPException(status_code=400, detail="Invalid shelf_id")

    book = Book(
        book_title=payload.book_title,
        book_author=payload.book_author,
        book_isbn=payload.book_isbn,
        book_genre=payload.book_genre,
        book_publication_year=payload.book_publication_year,
        book_language=payload.book_language,
        book_status=payload.book_status,
        shelf_id=payload.shelf_id,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/{book_id}", response_model=BookWithLocation)
def get_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    from app.services.book import get_book_with_location

    try:
        data = get_book_with_location(db, book_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Book not found")
    return data


@router.put("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    payload: BookUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    shelf = db.get(Shelf, payload.shelf_id)
    if not shelf:
        raise HTTPException(status_code=400, detail="Invalid shelf_id")

    book.book_title = payload.book_title
    book.book_author = payload.book_author
    book.book_isbn = payload.book_isbn
    book.book_genre = payload.book_genre
    book.book_publication_year = payload.book_publication_year
    book.book_language = payload.book_language
    book.book_status = payload.book_status
    book.shelf_id = payload.shelf_id

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return None

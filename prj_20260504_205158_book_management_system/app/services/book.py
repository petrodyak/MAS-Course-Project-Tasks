from __future__ import annotations
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_book_with_location(db: Session, book_id: int) -> dict:
    row = db.execute(
        text(
            "SELECT b.book_id, b.book_title, b.book_author, b.book_isbn, b.book_genre,"
            " b.book_publication_year, b.book_language, b.book_status, b.shelf_id,"
            " r.room_id, b.created_at, b.updated_at"
            " FROM books b"
            " JOIN shelves s ON s.shelf_id = b.shelf_id"
            " JOIN rooms r ON r.room_id = s.room_id"
            " WHERE b.book_id = :book_id"
        ),
        {"book_id": book_id},
    ).mappings().first()
    if not row:
        raise KeyError("Book not found")
    return dict(row)

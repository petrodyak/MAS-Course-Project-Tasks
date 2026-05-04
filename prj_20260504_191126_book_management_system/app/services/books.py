from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.db import connect
from app.schemas.book import BookCreate


@dataclass(frozen=True)
class BooksService:
    db_path: str

    def create(self, payload: BookCreate) -> dict[str, Any]:
        with connect(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO books (
                    book_title, isbn, author, shelf_id,
                    published_date, book_description, is_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.book_title,
                    payload.isbn,
                    payload.author,
                    payload.shelf_id,
                    payload.published_date,
                    payload.book_description,
                    int(payload.is_available),
                ),
            )
            book_id = cur.lastrowid
            row = conn.execute(
                "SELECT book_id, book_title, isbn, author, shelf_id, published_date, book_description, is_available, created_at, updated_at FROM books WHERE book_id = ?",
                (book_id,),
            ).fetchone()
            return {
                "book_id": row[0],
                "book_title": row[1],
                "isbn": row[2],
                "author": row[3],
                "shelf_id": row[4],
                "published_date": row[5],
                "book_description": row[6],
                "is_available": bool(row[7]),
                "created_at": row[8],
                "updated_at": row[9],
            }

    def get_location(self, book_id: int) -> dict[str, Any] | None:
        with connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT b.book_id, b.book_title,
                       b.shelf_id, s.shelf_name,
                       s.room_id, r.room_name
                FROM books b
                JOIN shelves s ON s.shelf_id = b.shelf_id
                JOIN rooms r ON r.room_id = s.room_id
                WHERE b.book_id = ?
                """,
                (book_id,),
            ).fetchone()
            if row is None:
                return None
            return {
                "book_id": row[0],
                "book_title": row[1],
                "shelf_id": row[2],
                "shelf_name": row[3],
                "room_id": row[4],
                "room_name": row[5],
            }

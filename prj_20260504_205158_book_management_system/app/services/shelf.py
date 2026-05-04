from __future__ import annotations
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.shelf import Shelf


def delete_shelf(db: Session, shelf_id: int) -> None:
    books_count = db.execute(
        text("SELECT COUNT(1) FROM books WHERE shelf_id = :shelf_id"),
        {"shelf_id": shelf_id},
    ).scalar_one()
    if books_count:
        raise ValueError("Deletion rejected due to existing books")
    shelf = db.get(Shelf, shelf_id)
    if not shelf:
        raise KeyError("Shelf not found")
    db.delete(shelf)

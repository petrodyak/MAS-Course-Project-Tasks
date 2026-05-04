from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    book_title: Mapped[str] = mapped_column(String(255), nullable=False)
    book_author: Mapped[str] = mapped_column(String(255), nullable=False)
    book_isbn: Mapped[str] = mapped_column(String(32), nullable=False)
    book_genre: Mapped[str] = mapped_column(String(100), nullable=False)
    book_publication_year: Mapped[int] = mapped_column(Integer, nullable=False)
    book_language: Mapped[str] = mapped_column(String(50), nullable=False)
    book_status: Mapped[str] = mapped_column(String(50), nullable=False)

    shelf_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shelves.shelf_id"), nullable=False
    )
    shelf = relationship("Shelf")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False,
        server_default=func.current_timestamp(),
    )

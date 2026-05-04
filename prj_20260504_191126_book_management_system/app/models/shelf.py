from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

from app.models.room import Base


class Shelf(Base):
    __tablename__ = "shelves"

    shelf_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shelf_name: Mapped[str] = mapped_column(String(255), nullable=False)
    room_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    shelf_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp(),
    )

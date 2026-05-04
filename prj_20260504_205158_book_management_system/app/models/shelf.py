from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Shelf(Base):
    __tablename__ = "shelves"

    shelf_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    shelf_name: Mapped[str] = mapped_column(String(255), nullable=False)
    shelf_code: Mapped[str] = mapped_column(String(255), nullable=False)
    shelf_description: Mapped[str] = mapped_column(Text, nullable=False)

    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.room_id"), nullable=False
    )
    room = relationship("Room")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False,
        server_default=func.current_timestamp(),
    )

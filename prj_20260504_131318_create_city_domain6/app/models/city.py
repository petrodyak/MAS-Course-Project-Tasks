from __future__ import annotations

import datetime as dt

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "city"

    city_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )

    city_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city_old_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city_size_km2: Mapped[float | None] = mapped_column(Float, nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    established_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow
    )
